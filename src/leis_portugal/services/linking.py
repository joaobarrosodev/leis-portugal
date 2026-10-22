"""Ligações entre a legislação portuguesa e os atos da UE presentes no acervo."""

from __future__ import annotations

import os
import re
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from leis_portugal.domain.record import Relationship, merge_relationships
from leis_portugal.infrastructure.markdown import read_record_id, render_markdown, write_if_changed
from leis_portugal.infrastructure.repository import PORTUGUESE_SCOPES, Acervo


_EU_RELATION = re.compile(r"^- type: (\w+)\n  target: celex:(\S+)$", re.MULTILINE)
_LEGISLATION = re.compile(r"^3[0-9]{4}[RLD][0-9]{4}$")
# Relação no diploma português -> relação inversa no ato da UE.
INVERSE = {"transposes": "transposed_by", "cites": "cited_by", "implements": "implemented_by"}
_PRIORITY = {"cites": 0, "implements": 1, "transposes": 2}


def _scan(path: str) -> tuple[str | None, list[tuple[str, str]]]:
    """(id, [(tipo, CELEX)]) lendo só o front matter, sem interpretar o YAML."""
    text = Path(path).read_text(encoding="utf-8")
    end = text.find("\n---\n", 4)
    front = text[: end if end > 0 else len(text)]
    return read_record_id(path), _EU_RELATION.findall(front)


def scan_portuguese_references(acervo: Acervo, *, workers: int | None = None) -> dict[str, list[tuple[str, str]]]:
    """CELEX -> [(id do diploma português, tipo de relação)]."""
    paths = [str(path) for path in acervo.paths(PORTUGUESE_SCOPES)]
    references: dict[str, list[tuple[str, str]]] = defaultdict(list)
    with ProcessPoolExecutor(max_workers=workers or max(1, (os.cpu_count() or 2) - 1)) as pool:
        for record_id, relations in pool.map(_scan, paths, chunksize=512):
            if record_id:
                for kind, celex in relations:
                    if kind in INVERSE:
                        references[celex].append((record_id, kind))
    return references


def missing_referenced_acts(references: dict[str, list[tuple[str, str]]], present: dict[str, Path], *, minimum: int = 1) -> list[str]:
    """Atos legislativos da UE referidos e ainda sem registo, os mais referidos primeiro."""
    counts = {
        celex: len({record for record, _ in items})
        for celex, items in references.items()
        if _LEGISLATION.match(celex) and celex not in present
    }
    return [celex for celex, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])) if count >= minimum]


@dataclass
class LinkSummary:
    eu_records: int = 0
    updated: int = 0
    relations: int = 0
    changed_paths: list[Path] = field(default_factory=list)


def link_eu_records(acervo: Acervo, *, workers: int | None = None) -> LinkSummary:
    """Escreve em cada ato da UE as relações inversas vindas dos diplomas portugueses
    (`transposed_by`, `cited_by`); as ligações antigas a `pt:` são recalculadas."""
    references = scan_portuguese_references(acervo, workers=workers)
    present = acervo.eu_records()
    summary = LinkSummary(eu_records=len(present))
    for celex, path in sorted(present.items()):
        record, body = acervo.read(path)
        kept = [item for item in record.relationships if not item.target.startswith("pt:")]
        # Um diploma que transpõe e também cita o mesmo ato fica só como transposição.
        strongest: dict[str, str] = {}
        for record_id, kind in references.get(celex, []):
            if _PRIORITY[kind] > _PRIORITY.get(strongest.get(record_id, ""), -1):
                strongest[record_id] = kind
        inverse = [Relationship(type=INVERSE[kind], target=record_id) for record_id, kind in sorted(strongest.items())]
        record.relationships = merge_relationships(kept, inverse)
        summary.relations += len(inverse)
        if write_if_changed(path, render_markdown(record.to_dict(), body)):
            summary.updated += 1
            summary.changed_paths.append(path)
    return summary
