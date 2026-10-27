"""Recolha de diplomas do Diário da República (e do catálogo do Jornal Oficial dos Açores que o DRE guarda)."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from leis_portugal.domain.identifiers import pt_record_id
from leis_portugal.errors import LeisPortugalError, NoSourceText, SkipDocument
from leis_portugal.infrastructure.repository import PORTUGUESE_SCOPES, Acervo, WriteResult
from leis_portugal.services.common import PORTUGUESE_POLICY, Progress, failure, note_source_gap, run_parallel, silent
from leis_portugal.sources.dre.client import dre_id_from_ref
from leis_portugal.sources.dre.source import DreSource


@dataclass
class DreRunSummary:
    documents: list[WriteResult] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failures: list[dict[str, str]] = field(default_factory=list)


NO_TEXT_NOTE = "o DRE não tem texto eletrónico nem PDF deste diploma; mantém-se o texto anterior"
_IMPORTED = "source_sha256_scope: imported_derived_markdown"
_DRE_PATH = re.compile(r"^  dre_path: '?(/dr/[^'\n]+)'?$", re.MULTILINE)


def _imported_ref(path: str) -> str | None:
    with open(path, encoding="utf-8") as handle:
        head = handle.read(12000)
    if _IMPORTED not in head:
        return None
    match = _DRE_PATH.search(head)
    return match.group(1) if match else None


def _present(ref: str, present: dict[str, object]) -> bool:
    try:
        return pt_record_id(dre_id_from_ref(ref)) in present
    except (LeisPortugalError, ValueError):
        return False


def imported_references(acervo: Acervo, *, workers: int | None = None) -> list[str]:
    """Caminhos DRE dos registos que ainda têm o texto da importação inicial."""
    paths = [str(path) for path in acervo.paths(PORTUGUESE_SCOPES)]
    with ProcessPoolExecutor(max_workers=workers or max(1, (os.cpu_count() or 2) - 1)) as pool:
        return [ref for ref in pool.map(_imported_ref, paths, chunksize=512) if ref]


class DreIngestion:
    def __init__(
        self,
        acervo: Acervo,
        source: DreSource | None = None,
        *,
        with_relations: bool = True,
        with_subjects: bool = True,
        source_factory: Callable[[], DreSource] | None = None,
    ) -> None:
        self.acervo = acervo
        self.source_factory = source_factory or (lambda: DreSource(acervo.types))
        self.source = source or self.source_factory()
        self.with_relations = with_relations
        self.with_subjects = with_subjects

    def ingest(self, ref: str, source: DreSource | None = None) -> WriteResult:
        document = (source or self.source).collect(ref, with_relations=self.with_relations, with_subjects=self.with_subjects)
        return self.acervo.save(document.record, document.body, policy=PORTUGUESE_POLICY)

    def keep_without_text(self, exc: NoSourceText) -> WriteResult | None:
        """A fonte não tem o texto. Um registo que já existe mantém o seu texto e ganha uma
        nota; se não existe, grava-se o registo só com os metadados (quando a fonte os tem)."""
        path = self.acervo.index().get(exc.record_id) if exc.record_id else None
        if path is not None and path.exists():
            note_source_gap(self.acervo, exc, NO_TEXT_NOTE, path=path)
            return None
        if exc.document is None:
            return None
        return self.acervo.save(exc.document.record, exc.document.body, policy=PORTUGUESE_POLICY)

    def ingest_many(self, refs: list[str], *, workers: int = 1, progress: Progress = silent) -> DreRunSummary:
        """Vários diplomas em paralelo (uma sessão DRE por thread)."""
        summary = DreRunSummary()
        self.acervo.index()  # uma leitura do índice antes de abrir as threads

        def work(ref: str, source: DreSource) -> str:
            try:
                result = self.ingest(ref, source)
            except SkipDocument as exc:
                summary.skipped.append(str(exc))
                return f"ignorado: {ref}"
            except NoSourceText as exc:
                saved = self.keep_without_text(exc)
                summary.failures.append(failure("ref", ref, exc))
                if saved is None:
                    return f"sem texto na fonte: {ref}"
                summary.documents.append(saved)
                return f"sem texto na fonte, só metadados: {self.acervo.relative(saved.path)}"
            except (LeisPortugalError, KeyError, TypeError, ValueError) as exc:
                # KeyError/TypeError/ValueError: resposta com formato inesperado para este diploma.
                summary.failures.append(failure("ref", ref, exc))
                return f"falha: {ref}: {exc}"
            summary.documents.append(result)
            return f"{result.action}: {self.acervo.relative(result.path)}"

        run_parallel(refs, work, context=self.source_factory, workers=workers, progress=progress)
        return summary

    def list_dates(
        self, start: date, end: date, *, workers: int = 1, progress: Progress = silent
    ) -> tuple[list[str], list[dict[str, str]]]:
        """Caminhos DRE dos diplomas publicados entre duas datas (e as falhas: entradas sem
        caminho e dias que o DRE não listou). Com `workers`, vários dias em paralelo; os
        caminhos saem pela ordem das datas."""
        days = [start + timedelta(days=offset) for offset in range((end - start).days + 1)]
        listed_by_day: dict[date, list[dict[str, Any]]] = {}
        failures: list[dict[str, str]] = []

        def work(day: date, source: DreSource) -> str:
            try:
                listed_by_day[day] = source.documents_by_date(day.isoformat())
            except LeisPortugalError as exc:
                # Um dia por listar fica registado como falha, nunca como dia sem diplomas.
                failures.append(failure("ref", f"dia {day.isoformat()}", exc))
                return f"{day.isoformat()}: falha: {exc}"
            return f"{day.isoformat()}: {len(listed_by_day[day])} documento(s)"

        if workers > 1:
            run_parallel(days, work, context=self.source_factory, workers=workers, progress=progress)
        else:
            for day in days:
                progress(work(day, self.source))
        refs: list[str] = []
        for day in days:
            for item in listed_by_day.get(day, []):
                ref = (item.get("LinkSitemap") or "").strip()
                if ref:
                    refs.append(ref)
                else:
                    failures.append({"ref": json.dumps(item, ensure_ascii=False)[:200], "motivo": "metadados_em_falta", "error": "Sem LinkSitemap"})
        return list(dict.fromkeys(refs)), failures

    def ingest_dates_parallel(
        self, start: date, end: date, *, workers: int, only_missing: bool = False, progress: Progress = silent
    ) -> DreRunSummary:
        """Como `ingest_dates`, mas lista os dias e recolhe os diplomas em paralelo.

        Com `only_missing`, só recolhe os diplomas que ainda não estão no acervo (para
        varrer décadas de Diário da República sem voltar a recolher o que já existe)."""
        refs, missing = self.list_dates(start, end, workers=workers, progress=progress)
        if only_missing:
            present = self.acervo.index()
            listed = len(refs)
            refs = [ref for ref in refs if not _present(ref, present)]
            progress(f"{listed} diploma(s) listados; {len(refs)} ainda não estão no acervo")
        summary = self.ingest_many(refs, workers=workers, progress=progress)
        summary.failures.extend(missing)
        return summary

    def ingest_dates(self, start: date, end: date, *, progress: Progress = silent) -> DreRunSummary:
        """Todos os diplomas publicados entre duas datas (inclusive).

        Uma mudança no DRE ao listar um dia interrompe a recolha (`DreApiError`): não
        se grava um dia vazio por engano."""
        summary = DreRunSummary()
        day = start
        while day <= end:
            listed = self.source.documents_by_date(day.isoformat())
            progress(f"{day.isoformat()}: {len(listed)} documento(s)")
            for item in listed:
                ref = (item.get("LinkSitemap") or "").strip()
                if not ref:
                    summary.failures.append({"ref": json.dumps(item, ensure_ascii=False)[:200], "error": "Sem LinkSitemap"})
                    continue
                try:
                    summary.documents.append(self.ingest(ref))
                except SkipDocument as exc:
                    summary.skipped.append(str(exc))
                except NoSourceText as exc:
                    saved = self.keep_without_text(exc)
                    if saved is not None:
                        summary.documents.append(saved)
                    summary.failures.append(failure("ref", ref, exc))
                except LeisPortugalError as exc:
                    summary.failures.append(failure("ref", ref, exc))
            day += timedelta(days=1)
        return summary
