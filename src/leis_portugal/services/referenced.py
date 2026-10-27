"""Documentos referidos pelo acervo que o acervo ainda não tem.

Cada relação cujo alvo não resolve para um registo aponta para um documento em falta:

- `pt:dre:<id>:por` sem registo — um diploma do DRE pelo id;
- um ELI do DRE ou `pt:numero:…` por resolver — um diploma pela numeração;
- `celex:` (ou um ELI da UE) de um regulamento, diretiva ou decisão sem registo.

Os diplomas do DRE encontram-se nos sitemaps (o caminho de cada documento traz o tipo,
o número, o ano e o id); os atos da UE recolhem-se pelo CELEX.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from leis_portugal.domain.relations import DiplomaKey, celex_from_eu_eli, eli_key
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.common import Progress, silent
from leis_portugal.services.coverage import SitemapClient, read_sitemaps
from leis_portugal.services.linking import ReferenceResolver, scan_entries
from leis_portugal.sources.dre.sitemap import NON_DOCUMENT_FAMILIES, parse_index


_DRE_ID = re.compile(r"^pt:dre:([0-9]+):por$")
_EU_LEGISLATION = re.compile(r"^3[0-9]{4}[RLD][0-9]{4}$")
# Chave do caminho DRE: `13-a-2010-138807` -> número `13-a`, ano 2010 (o id é o último bloco).
_REF_NUMBER = re.compile(r"^(?P<number>.+?)-(?P<year>[0-9]{4})-[0-9]+$")


@dataclass
class MissingReferences:
    dre_ids: Counter = field(default_factory=Counter)  # id do DRE -> nº de documentos que o referem
    diplomas: Counter = field(default_factory=Counter)  # DiplomaKey -> nº de documentos que o referem
    celex: Counter = field(default_factory=Counter)  # CELEX -> nº de documentos que o referem


def missing_references(acervo: Acervo, *, workers: int | None = None) -> MissingReferences:
    """O que o acervo refere e não tem, contado por documento que refere."""
    entries = scan_entries(acervo, workers=workers)
    ids = {entry.record_id for entry in entries if entry.record_id}
    present_celex = {record_id.split(":")[2] for record_id in ids if record_id.startswith("eu:celex:")}
    resolver = ReferenceResolver(entries, acervo.types.eli_codes)
    missing = MissingReferences()
    for entry in entries:
        dre_ids: set[str] = set()
        diplomas: set[DiplomaKey] = set()
        celex: set[str] = set()
        for target in entry.targets:
            if target in ids:
                continue
            if match := _DRE_ID.match(target):
                dre_ids.add(match.group(1))
            elif target.startswith("eli:"):
                eu = celex_from_eu_eli(target)
                if eu:
                    celex.add(eu)
                elif eli_key(target).startswith("data.dre.pt/") and not resolver.eli(target):
                    found = resolver.diplomas.key_from_eli(target)
                    if found:
                        diplomas.add(found[0])
            elif target.startswith("pt:numero:") and not resolver.diplomas.from_number(target):
                key = resolver.diplomas.key_from_number(target)
                if key:
                    diplomas.add(key)
            elif target.startswith("celex:"):
                celex.add(target.removeprefix("celex:"))
        missing.dre_ids.update(dre_ids)
        missing.diplomas.update(diplomas)
        missing.celex.update(item for item in celex if _EU_LEGISLATION.match(item) and item not in present_celex)
    return missing


def _ref_keys(document_type: str, ref: str) -> list[DiplomaKey]:
    """Chaves possíveis de um caminho DRE (o caminho não diz a região: as três servem)."""
    match = _REF_NUMBER.match(ref.rstrip("/").rsplit("/", 1)[-1].lower())
    if not match:
        return []
    return [DiplomaKey(document_type, match["number"], match["year"], region) for region in ("p", "a", "m")]


@dataclass
class ReferencedRefs:
    refs: list[str] = field(default_factory=list)
    found_ids: int = 0
    found_diplomas: int = 0


def referenced_refs(acervo: Acervo, client: SitemapClient, missing: MissingReferences, *, progress: Progress = silent) -> ReferencedRefs:
    """Caminhos DRE dos diplomas em falta, procurados em todos os sitemaps do DRE.

    Os ids procuram-se em todos os ficheiros (um diploma citado pode ser de um tipo fora do
    vocabulário, que fica em `outros/`); a numeração só nos tipos do vocabulário. Uma
    referência por numeração sem região pode corresponder a mais de um caminho (p. ex. o
    mesmo número nos Açores e na Madeira): recolhem-se todos e o `link` escolhe."""
    registry = acervo.types
    files = [item for item in parse_index(client.sitemap_index()) if item.family not in NON_DOCUMENT_FAMILIES]
    wanted_ids = set(missing.dre_ids)
    wanted_diplomas = set(missing.diplomas)
    found: dict[str, str] = {}
    matched_ids: set[str] = set()
    matched_diplomas: set[DiplomaKey] = set()
    for documents in read_sitemaps(client, files, progress=progress):
        for document in documents:
            if document.dre_id in wanted_ids:
                found[document.dre_id] = document.ref
                matched_ids.add(document.dre_id)
                continue
            document_type = registry.resolve(document.tipo)
            if not document_type.known:
                continue
            keys = [key for key in _ref_keys(document_type.slug, document.ref) if key in wanted_diplomas]
            if keys:
                found.setdefault(document.dre_id, document.ref)
                matched_diplomas.update(keys)
    present = acervo.index()
    refs = [ref for dre_id, ref in found.items() if f"pt:dre:{int(dre_id)}:por" not in present]
    # Os mais referidos primeiro.
    weight = {ref: missing.dre_ids.get(dre_id, 0) for dre_id, ref in found.items()}
    refs.sort(key=lambda ref: -weight.get(ref, 0))
    return ReferencedRefs(refs=refs, found_ids=len(matched_ids), found_diplomas=len(matched_diplomas))
