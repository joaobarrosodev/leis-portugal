"""Histórico de versões consolidadas, recolhido diretamente do DRE.

Para cada diploma consolidado pede-se o texto em cada data de entrada em vigor de
uma alteração e guarda-se, ao lado do registo, `<diploma>.versoes.json` com:

- `versions`: cada versão, com os atos que a produziram, as modificações
  (Altera/Adita/Revoga …) e a lista ordenada dos fragmentos em vigor nessa data;
- `fragments`: cada versão de cada fragmento uma única vez, já em Markdown.

O texto de qualquer versão é a concatenação dos fragmentos da lista
(`render_version`). O registo `.md` fica com o texto em vigor hoje e um resumo do
histórico em `version_history`.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from leis_portugal.domain.history import HISTORY_SCHEMA, render_version, summarize, version_at
from leis_portugal.domain.identifiers import clean_date, pt_record_id
from leis_portugal.domain.record import (
    ArticleStructure,
    DerivedMaterial,
    Integrity,
    Provenance,
    Relationship,
    Source,
    Validation,
    Version,
    utc_now,
)
from leis_portugal.domain.relations import eu_relationships
from leis_portugal.errors import LeisPortugalError, NoSourceText
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.common import Progress, failure, note_source_gap, run_parallel, silent
from leis_portugal.sources.dre.client import DreClient
from leis_portugal.sources.dre.consolidated import (
    ARTICLE_TYPES,
    DIVISION_LEVELS,
    FRAGMENT_LEVELS,
    ConsolidatedEntry,
    parse_sitemap,
    render_fragment,
)
from leis_portugal.sources.dre.constants import DRE_BASE_URL
from leis_portugal.sources.dre.source import DreSource


# ------------------------------------------------------------------------- recolha


@dataclass
class HistoryResult:
    history: dict[str, Any]
    latest_raw: bytes


def _act(act: dict[str, Any]) -> dict[str, Any]:
    legis_id = str(act.get("DiplomaLegisId") or "")
    return {
        "id": pt_record_id(legis_id) if legis_id.isdigit() and legis_id != "0" else None,
        "title": re.sub(r"\s*-\s*1\.ª Série$", "", (act.get("Title") or "").strip()) or None,
        "published": clean_date(act.get("DataPublicacao")),
        "dre_path": (act.get("LinkSitemap") or "").strip() or None,
    }


def collect_history(entry: ConsolidatedEntry, client: DreClient, *, today: str | None = None) -> HistoryResult:
    """Pede ao DRE o texto em cada data de entrada em vigor e monta o histórico."""
    today = today or date.today().isoformat()
    header = client.consolidated_header(entry.tipo, entry.ano, entry.frag_id)
    diploma = header["ConsolidadaConteudoDetalhe"]["DiplomaLegis"]
    legis_id = str(diploma.get("Id") or "0")

    acts_by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    changes_by_date: dict[str, list[str]] = defaultdict(list)
    for act in client.consolidated_timeline(legis_id, entry.frag_id):
        if act.get("IsDiplomaOriginal"):
            continue
        info = _act(act)
        for modification in (act.get("ModificacaoList") or {}).get("List") or []:
            when = clean_date(modification.get("DataEntradaVigor"))
            if not when:
                continue
            if info not in acts_by_date[when]:
                acts_by_date[when].append(info)
            label = " ".join(
                part
                for part in ((modification.get("TipoModificacao") or "").strip(), (modification.get("FragmentoDestinoModificacao") or "").strip())
                if part
            )
            if label and label not in changes_by_date[when]:
                changes_by_date[when].append(label)

    original = clean_date(diploma.get("DataPublicacao"))
    dates = sorted(set(acts_by_date) | ({original} if original else set())) or [today]

    fragments: dict[str, dict[str, Any]] = {}
    versions: list[dict[str, Any]] = []
    unavailable: list[str] = []
    latest_raw = b""
    for when in dates:
        snapshot = client.consolidated_snapshot(entry.tipo, entry.ano, entry.frag_id, legis_id, when, header)
        if not snapshot:
            # O DRE às vezes não tem texto para uma das datas (p. ex. a original, ou uma
            # alteração ainda por consolidar): salta-se essa data e fica registada.
            unavailable.append(when)
            continue
        keys: list[str] = []
        for item in snapshot:
            version_id = str((item.get("FragmentoVersao") or {}).get("Id") or "")
            if not version_id:
                continue
            if version_id not in fragments:
                fragments[version_id] = render_fragment(item)
            keys.append(version_id)
        if versions and versions[-1]["fragments"] == keys:
            # Nada mudou no texto nesta data (p. ex. alteração só de efeitos): o ato fica
            # registado, mas não é apresentado como autor da versão anterior.
            versions[-1].setdefault("acts_without_text_change", []).extend({**act, "date": when} for act in acts_by_date.get(when, []))
            continue
        versions.append(
            {"date": when, "future": when > today, "acts": list(acts_by_date.get(when, [])), "changes": changes_by_date.get(when, []), "fragments": keys}
        )
        if when <= today or not latest_raw:
            latest_raw = json.dumps(
                [[(item.get("FragmentoVersao") or {}).get("Id"), (item.get("FragmentoVersao") or {}).get("Texto")] for item in snapshot],
                ensure_ascii=False,
            ).encode("utf-8")
    if not versions:
        raise NoSourceText(
            f"{entry.url}: texto consolidado vazio em todas as datas ({', '.join(unavailable)})", record_id=pt_record_id(diploma["Id"])
        )

    used = dict.fromkeys(key for version in versions for key in version["fragments"])
    history = {
        "schema": HISTORY_SCHEMA,
        "id": pt_record_id(diploma["Id"]),
        "consolidated_url": entry.url,
        "dre_path": (diploma.get("LinkSitemap") or "").strip() or None,
        "source_lastmod": entry.lastmod,
        "versions": versions,
        "fragments": {key: fragments[key] for key in used},
    }
    if unavailable:
        history["unavailable_dates"] = unavailable
    return HistoryResult(history=history, latest_raw=latest_raw)


# --------------------------------------------------------------------------- gravação


def apply_history(result: HistoryResult, *, acervo: Acervo, dre_source: DreSource | None, today: str | None = None) -> tuple[Path, str]:
    """Grava o ficheiro de versões e atualiza (ou cria) o registo do diploma."""
    history = result.history
    today = today or date.today().isoformat()
    path = acervo.index().get(history["id"])
    created = path is None
    if created:
        if dre_source is None:
            raise LeisPortugalError(f"{history['id']} não está no acervo e não há fonte DRE para o criar.")
        document = dre_source.collect(history["dre_path"])
        record = document.record
        path = acervo.resolve_target(record)
    else:
        record, _ = acervo.read(path)

    history_file = acervo.history_path(path)
    current = version_at(history, today) or history["versions"][0]
    body = render_version(history, current, title=record.title)
    summary = summarize(history, history_file.name)
    if not created and record.version_history == summary and acervo.read_history(path) == json.loads(acervo.render_history(history)):
        return path, "unchanged"

    now = utc_now()
    fragments = history["fragments"]
    current_types = [fragments[key]["type"] for key in current["fragments"]]
    amended_by = [
        Relationship(
            type="amended_by",
            target=act["id"],
            label="; ".join(version["changes"][:20]) or None,
            source=f"{DRE_BASE_URL}{act['dre_path']}" if act.get("dre_path") else None,
            date=act.get("published"),
        )
        for version in history["versions"]
        for act in version["acts"] + version.get("acts_without_text_change", [])
        if act.get("id")
    ]
    dre_path = history.get("dre_path") or record.identifiers.dre_path
    record.version = Version(kind="consolidated", label="Versão consolidada pelo DRE", language="por", consolidation_date=current["date"])
    record.version_history = summary
    record.source = Source(
        id="dre",
        name="Diário da República Eletrónico",
        official_url=f"{DRE_BASE_URL}{dre_path}" if dre_path else history["consolidated_url"],
        metadata_url=record.identifiers.eli,
        content_url=history["consolidated_url"],
        consolidated_url=history["consolidated_url"],
        retrieved_at=now,
        retrieval_method="Legislação consolidada do DRE (LegCons_Detalhe): texto em cada data de entrada em vigor; endpoints internos da aplicação web",
        source_modified_at=f"{history['source_lastmod']}T00:00:00Z" if history.get("source_lastmod") else None,
    )
    record.integrity = Integrity(source_sha256=hashlib.sha256(result.latest_raw).hexdigest())
    record.provenance = Provenance(
        collector="leis-portugal DRE consolidado",
        generated_by="leis-portugal collect dre-consolidated",
        generated_at=now,
        notes=f"{len(history['versions'])} versão(ões); histórico completo em {history_file.name}.",
    )
    record.article_structure = ArticleStructure(
        article_count=sum(1 for kind in current_types if kind in ARTICLE_TYPES),
        section_count=sum(1 for kind in current_types if FRAGMENT_LEVELS.get(kind) in DIVISION_LEVELS),
        extraction_method="Fragmentos da legislação consolidada do DRE (TipoFragmentoId)",
    )
    record.add_relationships(amended_by, eu_relationships(body))
    record.derived_material = DerivedMaterial(
        notes="Markdown gerado a partir dos fragmentos consolidados do DRE; as versões anteriores estão no ficheiro de versões."
    )
    record.validation = Validation(checked_at=now)
    acervo.validate(record)
    acervo.write_history(path, history)
    acervo.write(record, body, path)
    return path, "created" if created else "written"


# ----------------------------------------------------------------------- orquestração


@dataclass
class VersionsSummary:
    total: int = 0
    written: int = 0
    created: int = 0
    unchanged: int = 0
    failures: list[dict[str, str]] = field(default_factory=list)


@dataclass
class _Context:
    client: DreClient
    source: DreSource


def stale_entries(acervo: Acervo, entries: list[ConsolidatedEntry]) -> list[ConsolidatedEntry]:
    """Só os diplomas cuja data no sitemap mudou desde a última recolha (ou novos)."""
    stored: dict[str, str | None] = {}
    for _path, content in acervo.histories():
        url = content.get("consolidated_url")
        if url:
            stored[url.rsplit("-", 1)[-1]] = content.get("source_lastmod")
    return [entry for entry in entries if entry.frag_id not in stored or not entry.lastmod or stored[entry.frag_id] != entry.lastmod]


def collect_versions(
    acervo: Acervo,
    *,
    entries: list[ConsolidatedEntry] | None = None,
    stale_only: bool = False,
    limit: int | None = None,
    workers: int = 2,
    client_factory: Callable[[], DreClient] = DreClient,
    progress: Progress = silent,
) -> VersionsSummary:
    """Recolhe o histórico de versões dos diplomas consolidados do DRE."""
    if entries is None:
        entries = parse_sitemap(client_factory().consolidated_sitemap())
    progress(f"{len(entries)} diploma(s) consolidado(s) no DRE")
    if stale_only:
        before = len(entries)
        entries = stale_entries(acervo, entries)
        progress(f"{before - len(entries)} sem alterações desde a última recolha; {len(entries)} a atualizar")
    if limit:
        entries = entries[:limit]
    acervo.index()  # uma leitura do índice antes de abrir as threads
    summary = VersionsSummary(total=len(entries))

    def context() -> _Context:
        client = client_factory()
        return _Context(client=client, source=DreSource(acervo.types, client))

    def work(entry: ConsolidatedEntry, ctx: _Context) -> str:
        try:
            result = collect_history(entry, ctx.client)
            path, action = apply_history(result, acervo=acervo, dre_source=ctx.source)
        except NoSourceText as exc:
            note_source_gap(acervo, exc, "o DRE lista este diploma como consolidado mas não tem texto consolidado em nenhuma data")
            summary.failures.append(failure("url", entry.url, exc))
            return f"sem texto na fonte: {entry.url}"
        except (LeisPortugalError, KeyError, TypeError, ValueError) as exc:
            # KeyError/TypeError/ValueError: resposta do DRE com um formato inesperado
            # para este diploma; fica registada e a recolha continua.
            summary.failures.append(failure("url", entry.url, exc))
            return f"falha: {entry.url}: {exc}"
        setattr(summary, action, getattr(summary, action) + 1)
        return f"{action}: {acervo.relative(path)} ({len(result.history['versions'])} versões)"

    run_parallel(entries, work, context=context, workers=workers, progress=progress)
    return summary
