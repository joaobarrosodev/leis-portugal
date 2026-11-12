"""Recolha de decisões fora da legislação: CNPD e acórdãos do Tribunal Constitucional.

Retoma onde parou: um documento já gravado (pelo id) não é descarregado de novo, salvo
com `refresh`. As falhas não interrompem a recolha e ficam em `reports/`.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

from leis_portugal.domain.record import Relationship
from leis_portugal.errors import LeisPortugalError
from leis_portugal.infrastructure.markdown import read_record_id
from leis_portugal.infrastructure.repository import CASE_LAW_SCOPE, ENTITIES_SCOPE, Acervo, SavePolicy, WriteResult
from leis_portugal.services.common import Progress, failure, silent
from leis_portugal.sources import cnpd, tc


# A fonte é a única a escrever estes registos: não há precedência a respeitar.
DECISION_POLICY = SavePolicy(respect_precedence=False)


@dataclass
class DecisionRunSummary:
    listed: int = 0
    skipped: int = 0
    results: list[WriteResult] = field(default_factory=list)
    failures: list[dict[str, str]] = field(default_factory=list)

    @property
    def changed(self) -> int:
        return sum(1 for result in self.results if result.changed)

    @property
    def without_text(self) -> int:
        return sum(1 for result in self.results if result.warnings)


def existing_ids(directory: Path) -> set[str]:
    return {record_id for path in directory.rglob("*.md") if (record_id := read_record_id(path))}


_MISSING_TEXT = ("\n- 'Fonte sem texto:", "\n- 'Texto incompleto:", "\n- Fonte sem texto:", "\n- Texto incompleto:")


def ids_without_text(directory: Path) -> set[str]:
    """Registos cujo PDF não deu texto (ou deu texto incompleto): os candidatos a OCR."""
    found: set[str] = set()
    for path in directory.rglob("*.md"):
        head = path.read_text(encoding="utf-8")[:6000]
        if any(marker in head for marker in _MISSING_TEXT) and (record_id := read_record_id(path)):
            found.add(record_id)
    return found


class _Ingestion:
    def __init__(
        self, acervo: Acervo, *, refresh: bool = False, only: set[str] | None = None, failures_path: Path | None = None
    ) -> None:
        self.acervo = acervo
        self.refresh = refresh
        # Com `only`, só estes ids são (re)descarregados; os outros são ignorados.
        self.only = only
        self.failures_path = failures_path

    def _save(self, document) -> WriteResult:
        record = document.record
        return self.acervo.save(record, document.body, target=self.acervo.resolve_target(record), policy=DECISION_POLICY)

    def _flush(self, summary: DecisionRunSummary) -> None:
        if self.failures_path is None:
            return
        import json

        self.failures_path.parent.mkdir(parents=True, exist_ok=True)
        self.failures_path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in summary.failures), encoding="utf-8")

    def _run(
        self,
        items: Iterable,
        *,
        key: Callable[[object], str],
        collect: Callable[[object], WriteResult],
        known: set[str],
        summary: DecisionRunSummary,
        progress: Progress,
        label: str,
        limit: int | None,
    ) -> None:
        items = list(items)
        summary.listed += len(items)
        done = 0
        for item in items:
            record_id = key(item)
            if self.only is not None:
                if record_id not in self.only:
                    continue
            elif record_id in known and not self.refresh:
                summary.skipped += 1
                continue
            if limit is not None and done >= limit:
                break
            done += 1
            try:
                result = collect(item)
            except LeisPortugalError as exc:
                summary.failures.append(failure("id", record_id, exc))
                progress(f"{label} {record_id}: falha: {exc}")
                continue
            summary.results.append(result)
            known.add(record_id)
            if done % 50 == 0:
                progress(f"{label}: {done} recolhidos neste lote ({record_id})")
                self._flush(summary)
        self._flush(summary)


class CnpdIngestion(_Ingestion):
    def __init__(self, acervo: Acervo, *, client_factory: Callable[[], cnpd.CnpdClient] = cnpd.CnpdClient, **kwargs) -> None:
        super().__init__(acervo, **kwargs)
        self.client = client_factory()

    def ingest(
        self,
        *,
        types: list[str],
        years: list[int],
        limit: int | None = None,
        progress: Progress = silent,
    ) -> DecisionRunSummary:
        summary = DecisionRunSummary()
        known = existing_ids(self.acervo.data / ENTITIES_SCOPE / "cnpd")
        for slug in types:
            decision_type = cnpd.TYPES[slug]
            for year in years:
                try:
                    listed = self.client.listing(decision_type, year)
                except LeisPortugalError as exc:
                    summary.failures.append(failure("listagem", f"{slug}:{year}", exc))
                    progress(f"CNPD {decision_type.label} {year}: falha na listagem: {exc}")
                    continue
                if not listed:
                    continue
                progress(f"CNPD {decision_type.label} {year}: {len(listed)} na listagem")

                def collect(item: cnpd.Listed) -> WriteResult:
                    return self._save(cnpd.to_document(item, self.client.download(item)))

                remaining = None if limit is None else max(0, limit - len(summary.results) - len(summary.failures))
                if remaining == 0:
                    return summary
                self._run(
                    listed, key=cnpd.record_id, collect=collect, known=known, summary=summary,
                    progress=progress, label=f"CNPD {decision_type.label} {year}", limit=remaining,
                )
        return summary


_DRE_FILE = re.compile(r"acordao-tribunal-constitucional-(\d+)-(\d{4})(?:-\d+)?$")


def dre_judgments(acervo: Acervo) -> dict[str, tuple[str, str | None]]:
    """N.º/ano -> (id do registo, id DRE) dos acórdãos do TC publicados no Diário da República."""
    found: dict[str, tuple[str, str | None]] = {}
    for path in sorted((acervo.data / "portugal" / tc.DOCUMENT_TYPE.replace("acordao", "acordaos")).rglob("*.md")):
        match = _DRE_FILE.match(path.stem)
        record_id = read_record_id(path) if match else None
        if match and record_id:
            dre = record_id.split(":")[2] if record_id.startswith("pt:dre:") else None
            found.setdefault(f"{int(match.group(1))}/{match.group(2)}", (record_id, dre))
    return found


class TcIngestion(_Ingestion):
    def __init__(self, acervo: Acervo, *, client_factory: Callable[[], tc.TcClient] = tc.TcClient, **kwargs) -> None:
        super().__init__(acervo, **kwargs)
        self.client = client_factory()

    def ingest(self, *, years: list[int], limit: int | None = None, progress: Progress = silent) -> DecisionRunSummary:
        summary = DecisionRunSummary()
        known = existing_ids(self.acervo.data / CASE_LAW_SCOPE / "tribunal-constitucional")
        published = dre_judgments(self.acervo)
        for year in years:
            try:
                listed = self.client.listing(year)
            except LeisPortugalError as exc:
                summary.failures.append(failure("listagem", str(year), exc))
                progress(f"TC {year}: falha na listagem: {exc}")
                continue
            progress(f"TC {year}: {len(listed)} acórdão(s) na listagem")

            def collect(item: tc.Listed) -> WriteResult:
                record_id, dre = published.get(item.official_number, (None, None))
                document = tc.to_document(item, self.client.page(item), dre_id=dre)
                if record_id:
                    document.record.add_relationships(
                        [Relationship(type="published_in", target=record_id, label="Publicado no Diário da República")]
                    )
                return self._save(document)

            remaining = None if limit is None else max(0, limit - len(summary.results) - len(summary.failures))
            if remaining == 0:
                return summary
            self._run(
                listed, key=tc.record_id, collect=collect, known=known, summary=summary,
                progress=progress, label=f"TC {year}", limit=remaining,
            )
        return summary
