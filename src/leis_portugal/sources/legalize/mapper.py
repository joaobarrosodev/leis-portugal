"""Importação inicial a partir do legalize-pt (texto do DRE já convertido).

O legalize-pt (https://github.com/legalize-dev/legalize-pt) tem o texto do Diário da
República desde 1960 já convertido; foi usado só para arrancar o acervo mais depressa.
A fonte de cada registo é o DRE (`source`); a importação fica registada em
`provenance` e em `integrity` (`imported_derived_markdown`), e o registo é substituído
quando o diploma é recolhido diretamente do DRE.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from leis_portugal.domain.document_types import DocumentTypeRegistry
from leis_portugal.domain.identifiers import clean_date, pt_record_id
from leis_portugal.domain.record import (
    IMPORTED_SCOPE,
    DerivedMaterial,
    Identifiers,
    Integrity,
    LegalRecord,
    Provenance,
    Publication,
    Relationship,
    Reuse,
    Source,
    Validation,
    Version,
)
from leis_portugal.domain.relations import citation_target
from leis_portugal.domain.structure import article_structure
from leis_portugal.errors import MetadataError
from leis_portugal.infrastructure.markdown import split_front_matter
from leis_portugal.sources.content import SourceDocument
from leis_portugal.sources.dre.constants import DRE_ATTRIBUTION, DRE_BASE_URL, DRE_LICENCE_URL, DRE_REUSE_NOTES
from leis_portugal.sources.dre.mapper import SOURCE_ID as DRE_SOURCE_ID
from leis_portugal.sources.dre.mapper import SOURCE_NAME as DRE_SOURCE_NAME
from leis_portugal.sources.dre.mapper import legal_status_from_dre
from leis_portugal.sources.legalize.snapshot import LegalizeSnapshot, territory_hint


REPOSITORY_URL = "https://github.com/legalize-dev/legalize-pt"

_BANNER = re.compile(
    r"^> \*\*This is the law as enacted\..*?\n> .*?history\.\*\*\n",
    re.MULTILINE,
)
_FIRST_H1 = re.compile(r"^# .*$", re.MULTILINE)
_CONSOLIDATION_DATE = re.compile(r"/cons/([0-9]{4})([0-9]{2})([0-9]{2})/")
_NO_ELECTRONIC_TEXT = "não se encontra disponível em formato eletrónico"
_STATUS = {
    "in_force": "in_force",
    "repealed": "repealed",
    "partially_repealed": "partially_in_force",
    "expired": "not_in_force",
}


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _split_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(";") if item.strip()]



def _title(front: dict[str, Any]) -> str:
    title = _text(front.get("title")) or ""
    # O legalize-pt junta "<tipo> n.º <número> — <sumário truncado…>".
    head = title.split(" — ", 1)[0].strip()
    return head if len(head) >= 3 else title


def _gazette(reference: str | None) -> str | None:
    if not reference:
        return None
    match = re.match(r"^(.*?)\s+n\.º", reference)
    return match.group(1).strip() if match else None


def _consolidation_date(front: dict[str, Any]) -> str | None:
    match = _CONSOLIDATION_DATE.search(str(front.get("source") or front.get("eli") or ""))
    if match:
        return "-".join(match.groups())
    return clean_date(front.get("last_updated"))


def _separate_paragraphs(body: str) -> str:
    """As consolidações do legalize-pt separam parágrafos com uma só quebra de linha,
    que em Markdown os junta num único parágrafo. As linhas de tabela ficam juntas."""
    lines = body.split("\n")
    output: list[str] = []
    for line in lines:
        previous = output[-1] if output else ""
        if line.strip() and previous.strip() and not (line.startswith("|") and previous.startswith("|")):
            output.append("")
        output.append(line)
    return "\n".join(output)


def _relationships(front: dict[str, Any]) -> list[Relationship]:
    relationships = []
    for url in _split_list(front.get("cites")) + _split_list(front.get("cites_eu")):
        relationships.append(Relationship(type="cites", target=citation_target(url), source=url))
    last_amendment = _text(front.get("last_amendment"))
    if last_amendment:
        # "DRE-2023-346-B-224139032": o último segmento é o id do DRE.
        dre_id = last_amendment.rsplit("-", 1)[-1]
        if dre_id.isdigit():
            relationships.append(
                Relationship(type="amended_by", target=pt_record_id(dre_id), label="Última alteração registada pelo legalize-pt")
            )
    return relationships


class LegalizeMapper:
    """Converte ficheiros do legalize-pt para o modelo do acervo."""

    def __init__(self, types: DocumentTypeRegistry, snapshot: LegalizeSnapshot) -> None:
        self.types = types
        self.snapshot = snapshot

    def convert(self, raw: bytes, relative: Path) -> SourceDocument:
        front, body = split_front_matter(raw.decode("utf-8"))
        dre_id = _text(front.get("dre_id"))
        if not dre_id or not dre_id.isdigit():
            raise MetadataError(f"{relative}: dre_id em falta ou inválido ({dre_id!r}).")
        rank = _text(front.get("rank")) or "desconhecido"
        document_type = self.types.resolve(rank)
        official_number = _text(front.get("official_number"))
        territory = self.types.territory_for(
            document_type=_text(front.get("rank")) or "",
            official_number=official_number,
            issuer=_text(front.get("department")),
            hint=territory_hint(relative),
        )
        title = _title(front)
        consolidated = front.get("surface") == "cons" or front.get("text_state") == "consolidated"
        dre_path = _text(front.get("dre_link"))
        official_url = f"{DRE_BASE_URL}{dre_path}" if dre_path else _text(front.get("source"))
        if not official_url:
            raise MetadataError(f"{relative}: sem ligação ao DRE.")

        body = _BANNER.sub("", body, count=1)
        body = _FIRST_H1.sub(lambda _: f"# {title}", body, count=1)
        body = _separate_paragraphs(body)
        body = re.sub(r"\n{3,}", "\n\n", body).strip()

        status = _STATUS.get(str(front.get("status") or ""), legal_status_from_dre(_text(front.get("in_force_raw"))))
        warnings: list[str] = []
        if _NO_ELECTRONIC_TEXT in body:
            warnings.append("Sem texto eletrónico no DRE; o registo liga apenas ao PDF oficial.")

        snapshot = self.snapshot
        identifier = pt_record_id(dre_id)
        reference = _text(front.get("gazette_reference"))
        eli = _text(front.get("eli"))
        last_updated = clean_date(front.get("last_updated"))
        record = LegalRecord(
            id=identifier,
            title=title,
            summary=_text(front.get("summary")) or _text(front.get("designation")),
            jurisdiction="regional" if territory else "portugal",
            territory=territory,
            document_type=document_type.slug,
            document_type_label=document_type.label,
            issuing_authority=[item for item in [_text(front.get("department"))] if item],
            proposing_entity=_text(front.get("proposing_entity")),
            official_number=official_number,
            publication_date=clean_date(front.get("publication_date")),
            publication=Publication(
                gazette=_gazette(reference),
                reference=reference,
                number=_text(front.get("gazette_number")),
                series=_text(front.get("series")),
                supplement=_text(front.get("supplement")),
                pages=_text(front.get("pages")),
                pdf_url=_text(front.get("pdf_url")),
            ),
            legal_status=status,
            notes=[note for note in [_text(front.get("note"))] if note],
            version=Version(
                kind="consolidated" if consolidated else "original",
                label="Versão consolidada pelo DRE" if consolidated else "Texto publicado no Diário da República",
                language="por",
                consolidation_date=_consolidation_date(front) if consolidated else None,
            ),
            identifiers=Identifiers(eli=eli, dre=dre_id, dre_path=dre_path, internal=identifier),
            # A fonte é o Diário da República; o legalize-pt foi só o meio da importação
            # inicial e fica registado na proveniência.
            source=Source(
                id=DRE_SOURCE_ID,
                name=DRE_SOURCE_NAME,
                official_url=official_url,
                metadata_url=eli,
                content_url=official_url,
                consolidated_url=_text(front.get("consolidated_url")),
                retrieved_at=snapshot.committed_at,
                retrieval_method="Importação inicial do texto do DRE; substituído pela recolha direta quando o diploma é recolhido de novo",
                source_modified_at=f"{last_updated}T00:00:00Z" if last_updated else None,
            ),
            integrity=Integrity(source_sha256=hashlib.sha256(raw).hexdigest(), source_sha256_scope=IMPORTED_SCOPE),
            provenance=Provenance(
                collector="leis-portugal importador legalize-pt",
                generated_by="leis-portugal import legalize",
                generated_at=snapshot.committed_at,
                notes=(
                    f"Importação inicial: texto do DRE convertido pelo projeto legalize-pt ({REPOSITORY_URL}/blob/"
                    f"{snapshot.commit}/{relative.as_posix()})."
                ),
            ),
            reuse=Reuse(
                status="permitted",
                attribution=DRE_ATTRIBUTION,
                reference=DRE_LICENCE_URL,
                notes=DRE_REUSE_NOTES,
            ),
            subjects=list(dict.fromkeys(_split_list(front.get("subjects")))),
            relationships=_relationships(front),
            article_structure=article_structure(body, method="Cabeçalhos Markdown '###### Artigo' do legalize-pt"),
            derived_material=DerivedMaterial(
                notes="Markdown convertido pelo legalize-pt a partir do DRE e normalizado pelo leis-portugal; confirmar na fonte oficial."
            ),
            validation=Validation(checked_at=snapshot.committed_at, warnings=warnings),
        )
        return SourceDocument(record=record, body=body, warnings=warnings)
