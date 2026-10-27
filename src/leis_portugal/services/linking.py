"""Ligações entre documentos do acervo.

- os atos da UE recebem as relações inversas vindas dos diplomas portugueses;
- as referências por ELI (herdadas da importação inicial) passam a apontar para o id
  do documento no acervo, quando ele existe, e as ligações partidas são removidas;
- um código consolidado pelo DRE sob o diploma que o republicou (o Código do IRS sob a
  Lei n.º 82-E/2014, não sob o Decreto-Lei n.º 442-A/88) fica ligado ao diploma que o
  aprovou: `republished_by` no original, `republishes` no consolidado.
"""

from __future__ import annotations

import os
import re
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field, replace
from pathlib import Path

from leis_portugal.domain.record import Relationship, merge_relationships
from leis_portugal.domain.relations import DiplomaIndex, EliIndex, acting_reference, diploma_key, placeholder_source, valid_target
from leis_portugal.infrastructure.markdown import read_record_id, render_markdown, write_if_changed
from leis_portugal.infrastructure.repository import PORTUGUESE_SCOPES, Acervo


_TARGET = re.compile(r"^  target: '?(.*?)'?$", re.MULTILINE)
_ELI = re.compile(r"^  eli: '?(.*?)'?$", re.MULTILINE)
_FIELDS = {
    name: re.compile(rf"^{indent}{name}: '?(.*?)'?$", re.MULTILINE)
    for name, indent in (("document_type", ""), ("official_number", ""), ("publication_date", ""), ("territory", ""), ("series", "  "))
}
_EU_RELATION = re.compile(r"^- type: (\w+)\n  target: celex:(\S+)$", re.MULTILINE)
# Nota do DRE num consolidado que assenta na republicação de outro diploma: "Esta versão
# consolidada tem por base a republicação, em anexo à Lei 82-E/2014, …, do Código do IRS,
# aprovado pelo Decreto-Lei n.º 442-A/88, de 30 de novembro." (às vezes sem "n.º").
_REPUBLICATION_NOTE = re.compile(
    r"tem por base a republicação.*?aprovad[oa]s? pel[oa]s? (?P<kind>Decreto Legislativo Regional|Decreto Regulamentar Regional|"
    r"Decreto Regulamentar|Decreto-Lei|Decreto|Lei Orgânica|Lei|Portaria) (?:n\.?\s*º\s*)?"
    r"(?P<number>[0-9]+(?:-[A-Z])?)/(?P<year>[0-9]{2,4})(?:/(?P<region>[AM]))?",
)
_NOTE_KINDS = {
    "Decreto Legislativo Regional": "decreto-legislativo-regional", "Decreto Regulamentar Regional": "decreto-regulamentar-regional",
    "Decreto Regulamentar": "decreto-regulamentar", "Decreto-Lei": "decreto-lei", "Decreto": "decreto",
    "Lei Orgânica": "lei-organica", "Lei": "lei", "Portaria": "portaria",
}
REPUBLICATION_LABEL = "Texto em vigor: versão consolidada pelo DRE com base na republicação deste diploma"
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


def _front(path: str) -> str:
    text = Path(path).read_text(encoding="utf-8")
    end = text.find("\n---\n", 4)
    return text[: end if end > 0 else len(text)]


@dataclass(frozen=True)
class Entry:
    """O que interessa de um registo para ligar referências (lido sem interpretar o YAML)."""

    path: str
    record_id: str | None
    eli: str | None
    pending: bool
    fields: dict[str, str | None]
    targets: tuple[str, ...] = ()
    # Diploma cuja republicação é a base deste consolidado (`pt:numero:…`), pela nota do DRE.
    republication: str | None = None


def _value(front: str, name: str) -> str | None:
    match = _FIELDS[name].search(front)
    return match.group(1) if match and match.group(1) not in ("", "null") else None


def republication_reference(front: str) -> str | None:
    """`pt:numero:…` do diploma que aprovou o texto republicado em que assenta o consolidado."""
    match = _REPUBLICATION_NOTE.search(" ".join(re.sub(r"<[^>]+>", " ", front).split()))
    if not match:
        return None
    region = f"/{match['region']}" if match["region"] else ""
    return f"pt:numero:{_NOTE_KINDS[match['kind']]}:{match['number']}/{match['year']}{region}"


def _references(path: str) -> Entry:
    """O id, o ELI, a numeração e os alvos das relações do documento."""
    front = _front(path)
    eli = _ELI.search(front)
    targets = tuple(_TARGET.findall(front))
    pending = "/sem-diploma/" in front or any(target.startswith("eli:") or not valid_target(target) for target in targets)
    return Entry(
        path, read_record_id(path), eli.group(1) if eli else None, pending, {name: _value(front, name) for name in _FIELDS}, targets,
        republication_reference(front),
    )


def scan_entries(acervo: Acervo, *, workers: int | None = None) -> list[Entry]:
    """Lê de todos os registos o que é preciso para resolver referências."""
    paths = [str(path) for path in acervo.paths()]
    with ProcessPoolExecutor(max_workers=workers or max(1, (os.cpu_count() or 2) - 1)) as pool:
        return list(pool.map(_references, paths, chunksize=512))


class ReferenceResolver:
    """ELI -> id do documento no acervo: o ELI exato, o mesmo diploma noutra versão
    (publicado/consolidado) e, para registos sem ELI, a numeração (tipo, número, ano,
    região e data)."""

    def __init__(self, entries: list[Entry], eli_codes: dict[str, str]) -> None:
        self.by_eli = EliIndex([(entry.record_id, entry.eli) for entry in entries if entry.record_id and entry.eli])
        self.diplomas = DiplomaIndex(eli_codes)
        for entry in entries:
            if entry.record_id:
                fields = entry.fields
                key = diploma_key(
                    fields["document_type"], fields["official_number"], publication_date=fields["publication_date"], territory=fields["territory"]
                )
                self.diplomas.add(entry.record_id, key, publication_date=fields["publication_date"], series=fields["series"])

    def eli(self, target: str) -> str | None:
        return self.by_eli.get(target) or self.diplomas.from_eli(target)


@dataclass
class ResolveSummary:
    checked: int = 0
    updated: int = 0
    resolved: int = 0
    removed: int = 0
    by_number: int = 0
    changed_paths: list[Path] = field(default_factory=list)


def resolve_references(acervo: Acervo, *, workers: int | None = None, entries: list[Entry] | None = None) -> ResolveSummary:
    """Troca os alvos `eli:` pelo id do documento no acervo e remove os alvos partidos.

    O URL original fica em `source`. Um ELI de um documento que o acervo ainda não tem
    mantém-se como está (passa a ser resolvido quando o documento for recolhido).

    As ligações ao marcador "sem diploma" da análise jurídica do DRE passam a referência
    por número quando a nota diz qual é o ato (`pt:numero:decreto-lei:189/90`) e são
    removidas quando não diz."""
    entries = entries if entries is not None else scan_entries(acervo, workers=workers)
    resolver = ReferenceResolver(entries, acervo.types.eli_codes)
    summary = ResolveSummary()
    for entry in entries:
        if not entry.pending:
            continue
        path = entry.path
        summary.checked += 1
        record, body = acervo.read(Path(path))
        relationships = []
        for relation in record.relationships:
            if placeholder_source(relation.source):
                label = " ".join((relation.label or "").replace("\x00", " ").split()) or None
                target = acting_reference(label)
                if not target:
                    summary.removed += 1
                    continue
                relation = replace(relation, target=target, label=label, source=None)
                summary.by_number += 1
            if not valid_target(relation.target):
                summary.removed += 1
                continue
            if relation.target.startswith("eli:"):
                target = resolver.eli(relation.target)
                if target and target != record.id:
                    relation = replace(relation, target=target, source=relation.source or relation.target.removeprefix("eli:"))
                    summary.resolved += 1
            relationships.append(relation)
        record.relationships = merge_relationships(relationships)
        if write_if_changed(path, render_markdown(record.to_dict(), body)):
            summary.updated += 1
            summary.changed_paths.append(Path(path))
    return summary


@dataclass
class RepublicationSummary:
    consolidated: int = 0
    linked: int = 0
    unresolved: list[str] = field(default_factory=list)
    updated: int = 0
    changed_paths: list[Path] = field(default_factory=list)


def link_republications(acervo: Acervo, *, workers: int | None = None, entries: list[Entry] | None = None) -> RepublicationSummary:
    """Liga cada diploma ao consolidado que tem o seu texto em vigor quando o DRE o consolida
    sob o diploma que o republicou: `republished_by` no original (com a etiqueta que o diz)
    e `republishes` no consolidado. Um diploma da nota que o acervo não tenha fica em
    `unresolved`."""
    entries = entries if entries is not None else scan_entries(acervo, workers=workers)
    resolver = ReferenceResolver(entries, acervo.types.eli_codes)
    paths = {entry.record_id: Path(entry.path) for entry in entries if entry.record_id}
    additions: dict[str, list[Relationship]] = defaultdict(list)
    summary = RepublicationSummary()
    for entry in entries:
        if not entry.republication or not entry.record_id:
            continue
        summary.consolidated += 1
        original = resolver.diplomas.from_number(entry.republication)
        if not original or original == entry.record_id:
            summary.unresolved.append(f"{entry.record_id}: {entry.republication}")
            continue
        additions[original].append(Relationship(type="republished_by", target=entry.record_id, label=REPUBLICATION_LABEL))
        additions[entry.record_id].append(Relationship(type="republishes", target=original))
        summary.linked += 1
    for record_id, relations in sorted(additions.items()):
        path = paths[record_id]
        record, body = acervo.read(path)
        record.relationships = merge_relationships(record.relationships, relations)
        if write_if_changed(path, render_markdown(record.to_dict(), body)):
            summary.updated += 1
            summary.changed_paths.append(path)
    return summary
