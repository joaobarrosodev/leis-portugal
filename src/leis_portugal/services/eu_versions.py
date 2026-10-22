"""Histórico de versões consolidadas dos atos da UE (EUR-Lex), no formato comum.

O EUR-Lex publica cada versão consolidada de um ato com um CELEX próprio
(`0AAAATNNNN-AAAAMMDD`, a data de aplicação). Cada versão vem como texto inteiro;
divide-se por cabeçalhos (artigos, títulos, capítulos, anexos) e cada fragmento
fica guardado uma só vez, identificado pelo conteúdo. Os atos que produziram uma
versão são os que entram de novo na lista "Alterado por" (►M1, ►M2…) dessa versão.

O texto original do Jornal Oficial entra como primeira versão quando nenhuma
consolidação começa na data de publicação.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import quote

from leis_portugal.domain.history import HISTORY_SCHEMA, render_version, summarize, version_at
from leis_portugal.domain.identifiers import eu_record_id, normalize_celex
from leis_portugal.domain.record import ArticleStructure, Integrity, LegalRecord, Provenance, Version, utc_now
from leis_portugal.domain.structure import split_fragments
from leis_portugal.errors import FetchError, LeisPortugalError, MetadataError, SkipDocument, SourceError
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.common import Progress, run_parallel, silent
from leis_portugal.sources.eurlex.client import CellarClient
from leis_portugal.sources.eurlex.xhtml import CellarXhtmlMarkdownConverter, consolidation_modifiers


_STAMP = re.compile(r"-([0-9]{4})([0-9]{2})([0-9]{2})$")
_ARTICLE = re.compile(r"^Artigo\b", re.IGNORECASE)


def consolidation_dates(candidates: list[str], celex: str) -> list[tuple[str, str]]:
    """(data, CELEX) das consolidações do próprio ato, por data."""
    prefix = "0" + normalize_celex(celex)[1:] + "-"
    dated = []
    for item in set(candidates):
        match = _STAMP.search(item)
        if item.startswith(prefix) and match:
            dated.append(("-".join(match.groups()), item))
    return sorted(dated)


def eurlex_url(celex: str) -> str:
    return f"https://eur-lex.europa.eu/legal-content/PT/TXT/?uri=CELEX%3A{quote(celex)}"


@dataclass
class EuHistoryResult:
    history: dict[str, Any]
    current_sha256: str
    warnings: list[str] = field(default_factory=list)


def _fragment(item: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    markdown = str(item["markdown"])
    key = hashlib.sha1(markdown.encode("utf-8")).hexdigest()[:16]
    heading = item["heading"]
    return key, {
        "fragment_id": heading or "preambulo",
        "type": "artigo" if heading and _ARTICLE.match(str(heading)) else ("divisao" if heading else "preambulo"),
        "heading": heading,
        "in_force_from": None,
        "changed_by": [],
        "markdown": markdown,
    }


def _normalized(text: str) -> str:
    """Texto só com letras e números: o texto do JO e o consolidado vêm de HTML
    diferente, e a formatação não deve contar como modificação."""
    return re.sub(r"[\W_]+", "", text.replace("º", "o").replace("ª", "a")).lower()


def _act_id(celex: str) -> str | None:
    """Id do ato modificador; o EUR-Lex tem ligações com CELEX mal escritos (p. ex.
    `397L0062`): nesse caso o ato fica registado só com o título."""
    if not celex.startswith("3"):
        return None
    try:
        return eu_record_id(celex)
    except ValueError:
        return None


def _changes(previous: dict[str, str], current: dict[str, str]) -> list[str]:
    """Modificações entre duas versões, por cabeçalho: Adita / Altera / Suprime."""
    changes = [f"Altera {heading}" for heading, key in current.items() if heading in previous and previous[heading] != key]
    changes += [f"Adita {heading}" for heading in current if heading not in previous]
    changes += [f"Suprime {heading}" for heading in previous if heading not in current]
    return changes


def collect_eu_history(celex: str, client: CellarClient, *, publication_date: str | None, today: str | None = None) -> EuHistoryResult:
    """Pede ao CELLAR cada versão consolidada de um ato e monta o histórico."""
    normalized = normalize_celex(celex)
    today = today or date.today().isoformat()
    work_uri = client.work(normalized)["work"][0]
    consolidations = consolidation_dates(client.consolidations(work_uri), normalized)
    if not consolidations:
        raise SkipDocument(f"{normalized}: sem versões consolidadas no EUR-Lex")

    planned: list[tuple[str, str]] = []
    if publication_date and consolidations[0][0] > publication_date:
        planned.append((publication_date, normalized))  # texto original do JO
    planned.extend(consolidations)

    converter = CellarXhtmlMarkdownConverter()
    fragments: dict[str, dict[str, Any]] = {}
    versions: list[dict[str, Any]] = []
    warnings: list[str] = []
    previous_headings: dict[str, str] = {}
    previous_modifiers: set[str] = set()
    current_sha = ""
    for when, version_celex in planned:
        try:
            content = client.fetch_text(client.expression(version_celex))
        except (FetchError, MetadataError) as exc:
            warnings.append(f"{version_celex}: versão indisponível ({exc})")
            continue
        keys: list[str] = []
        headings: dict[str, str] = {}
        markdown = converter.convert(content.content, source_url=content.url).markdown
        # O cabeçalho da consolidação (referência, aviso, "Alterado por") vem antes do
        # título e muda em todas as versões: os atos dele vão para `acts`.
        title_line = re.search(r"^# ", markdown, re.MULTILINE)
        if title_line:
            markdown = markdown[title_line.start():]
        for item in split_fragments(markdown):
            key, fragment = _fragment(item)
            fragments.setdefault(key, fragment)
            keys.append(key)
            headings.setdefault(fragment["fragment_id"], _normalized(fragment["markdown"]))
        modifiers = consolidation_modifiers(content.content)
        new_acts = [
            {"id": _act_id(item_celex), "title": title, "published": None, "celex": item_celex}
            for item_celex, title in modifiers
            if item_celex not in previous_modifiers
        ]
        previous_modifiers |= {item_celex for item_celex, _ in modifiers}
        if versions and versions[-1]["fragments"] == keys:
            if new_acts:
                versions[-1].setdefault("acts_without_text_change", []).extend({**act, "date": when} for act in new_acts)
            continue
        versions.append(
            {
                "date": when,
                "future": when > today,
                "celex": version_celex,
                "acts": new_acts if versions else [],
                "changes": _changes(previous_headings, headings) if versions else [],
                "fragments": keys,
            }
        )
        previous_headings = headings
        if when <= today or not current_sha:
            current_sha = content.sha256
    if not versions:
        raise SourceError(f"{normalized}: nenhuma versão consolidada disponível em português")

    used = dict.fromkeys(key for version in versions for key in version["fragments"])
    history = {
        "schema": HISTORY_SCHEMA,
        "id": eu_record_id(normalized),
        "consolidated_url": eurlex_url(consolidations[-1][1]),
        "dre_path": None,
        "source_lastmod": consolidations[-1][0],
        "versions": versions,
        "fragments": {key: fragments[key] for key in used},
    }
    return EuHistoryResult(history=history, current_sha256=current_sha, warnings=warnings)


def apply_eu_history(result: EuHistoryResult, *, acervo: Acervo, path: Path, today: str | None = None) -> str:
    """Grava o histórico e atualiza o registo do ato com o texto em vigor hoje."""
    history = result.history
    today = today or date.today().isoformat()
    record, _ = acervo.read(path)
    current = version_at(history, today) or history["versions"][0]
    summary = summarize(history, acervo.history_path(path).name)
    if record.version_history == summary and acervo.read_history(path) == history:
        return "unchanged"

    body = render_version(history, current, title=record.title)
    consolidated = current["celex"] != record.identifiers.celex
    now = utc_now()
    record.version = Version(
        kind="consolidated" if consolidated else "original",
        label="Versão consolidada (EUR-Lex), sem valor jurídico" if consolidated else "Texto original publicado no Jornal Oficial",
        language=record.language,
        consolidation_date=current["date"] if consolidated else None,
    )
    record.version_history = summary
    record.source.consolidated_url = eurlex_url(current["celex"]) if consolidated else None
    record.source.retrieved_at = now
    record.integrity = Integrity(source_sha256=result.current_sha256 or record.integrity.source_sha256)
    record.provenance = Provenance(
        collector="leis-portugal EUR-Lex/CELLAR",
        generated_by="leis-portugal collect eurlex-consolidated",
        generated_at=now,
        notes=f"{len(history['versions'])} versão(ões); histórico completo em {acervo.history_path(path).name}.",
    )
    fragments = history["fragments"]
    current_types = [fragments[key]["type"] for key in current["fragments"]]
    record.article_structure = ArticleStructure(
        article_count=current_types.count("artigo"),
        section_count=current_types.count("divisao"),
        extraction_method="Fragmentos por cabeçalho do texto consolidado do EUR-Lex",
    )
    record.validation.checked_at = now
    record.validation.warnings = list(result.warnings)
    acervo.validate(record)
    acervo.write_history(path, history)
    acervo.write(record, body, path)
    return "written"


@dataclass
class EuVersionsSummary:
    total: int = 0
    written: int = 0
    unchanged: int = 0
    skipped: int = 0
    failures: list[dict[str, str]] = field(default_factory=list)


def collect_eu_versions(
    acervo: Acervo,
    *,
    celex_list: list[str] | None = None,
    limit: int | None = None,
    workers: int = 4,
    client_factory: Callable[[], CellarClient] = CellarClient,
    progress: Progress = silent,
) -> EuVersionsSummary:
    """Histórico de versões dos atos da UE presentes no acervo (ou dos indicados)."""
    present = acervo.eu_records()
    targets = [normalize_celex(item) for item in celex_list] if celex_list else sorted(present)
    if limit:
        targets = targets[:limit]
    progress(f"{len(targets)} ato(s) da UE a verificar")
    summary = EuVersionsSummary(total=len(targets))

    def work(celex: str, client: CellarClient) -> str:
        path = present.get(celex)
        if path is None:
            summary.failures.append({"celex": celex, "error": "Ato não está no acervo (recolher primeiro com collect eurlex)."})
            return f"{celex}: não está no acervo"
        try:
            record: LegalRecord = acervo.read(path)[0]
            result = collect_eu_history(celex, client, publication_date=record.publication_date)
            action = apply_eu_history(result, acervo=acervo, path=path)
        except SkipDocument:
            summary.skipped += 1
            return f"{celex}: sem versões consolidadas"
        except (LeisPortugalError, KeyError, TypeError, ValueError) as exc:
            summary.failures.append({"celex": celex, "error": f"{type(exc).__name__}: {exc}"})
            return f"{celex}: falha: {exc}"
        setattr(summary, action, getattr(summary, action) + 1)
        return f"{action}: {acervo.relative(path)} ({len(result.history['versions'])} versões)"

    run_parallel(targets, work, context=client_factory, workers=workers, progress=progress)
    return summary
