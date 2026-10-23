"""Conversão das respostas do DRE para o modelo do acervo (sem rede)."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from leis_portugal.domain.document_types import DocumentTypeRegistry
from leis_portugal.domain.identifiers import clean_date, pt_record_id
from leis_portugal.domain.record import (
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
    merge_relationships,
    utc_now,
)
from leis_portugal.domain.structure import article_structure
from leis_portugal.errors import NoSourceText
from leis_portugal.sources.content import SourceContent, SourceDocument
from leis_portugal.sources.dre.client import ASSOCIATION_CORRECTIONS, ASSOCIATION_MODIFICATIONS, dre_id_from_ref, split_sitemap_ref
from leis_portugal.sources.dre.constants import DRE_ATTRIBUTION, DRE_BASE_URL, DRE_LICENCE_URL, DRE_REUSE_NOTES
from leis_portugal.sources.dre.html import DreHtmlConverter


SOURCE_ID = "dre"
SOURCE_NAME = "Diário da República Eletrónico"
METADATA_ONLY_NOTE = "o DRE não tem texto eletrónico nem PDF deste diploma; o registo tem só os metadados"

# O DRE guarda também o catálogo do Jornal Oficial dos Açores (`TipoConteudo`
# "DiplomaLegacor"): legislação regional com a publicação de origem em
# `DiplomaLegacor.FonteRegional`, p. ex. "JORNAL OFICIAL DOS AÇORES - 1.ª SÉRIE, Nº 101,
# de 2020-07-06, Pág. 2755 - 2757".
AZORES_CATALOGUE = "DiplomaLegacor"
_ROMAN = {"1": "I", "2": "II", "3": "III", "4": "IV"}


def legal_status_from_dre(vigencia: str | None) -> str:
    """Mapeia o campo Vigencia do DRE para o vocabulário do esquema."""
    return {
        "VIGENTE": "in_force",
        "VIGENCIA_CONDICIONADA": "partially_in_force",
        "NAO_VIGENTE": "not_in_force",
        "CADUCADO": "not_in_force",
        "REVOGADO": "repealed",
    }.get((vigencia or "").strip().upper(), "unknown")


def dre_reuse() -> Reuse:
    return Reuse(status="permitted", attribution=DRE_ATTRIBUTION, reference=DRE_LICENCE_URL, notes=DRE_REUSE_NOTES)


def regional_publication(source: str | None) -> dict[str, str | None]:
    """Território, série, número e páginas de uma referência ao Jornal Oficial regional."""
    text = re.sub(r"\s+", " ", source or "").strip()
    series = re.search(r"([0-9])\s*\.?\s*ª\s*S[ÉE]RIE", text, re.IGNORECASE)
    number = re.search(r"\bN\.?\s*[º°o]\s*([0-9][0-9A-Za-z/-]*)", text)
    pages = re.search(r"P[ÁA]GS?\.?\s*([0-9]+(?:\s*-\s*[0-9]+)?)", text, re.IGNORECASE)
    return {
        "territory": "madeira" if "MADEIRA" in text.upper() else "acores",
        "series": _ROMAN.get(series.group(1)) if series else None,
        "number": number.group(1) if number else None,
        "pages": re.sub(r"\s+", "", pages.group(1)) if pages else None,
        "reference": text or None,
    }


def _relation_type(text: str, *, inverse: bool, corrections: bool) -> str:
    if corrections:
        return "corrected_by" if inverse else "corrects"
    if re.match(r"^\s*Revog", text or "", re.IGNORECASE):
        return "repealed_by" if inverse else "repeals"
    if re.match(r"^\s*Republica", text or "", re.IGNORECASE):
        return "republished_by" if inverse else "republishes"
    return "amended_by" if inverse else "amends"


class DreMapper:
    def __init__(self, types: DocumentTypeRegistry) -> None:
        self.types = types
        self.converter = DreHtmlConverter()

    def relationships(self, associations: dict[str, dict[str, Any]]) -> list[Relationship]:
        """Relações da análise jurídica, por tipo de associação (162 alterações, 165 retificações)."""
        relationships: list[Relationship] = []
        for association_id in (ASSOCIATION_MODIFICATIONS, ASSOCIATION_CORRECTIONS):
            data = associations.get(association_id) or {}
            corrections = association_id == ASSOCIATION_CORRECTIONS
            for row in (data.get("InversasList") or {}).get("List") or []:
                target = str(row.get("DiplomaLegisId") or "0")
                link = (row.get("LinkSitemapAnaliseJuridica") or "").strip()
                if target == "0" and link:
                    target = link.rsplit("-", 1)[-1]
                if not target.isdigit() or target == "0":
                    continue
                text = re.sub(r"\s+", " ", row.get("Texto") or "").strip()
                relationships.append(
                    Relationship(
                        type=_relation_type(text, inverse=True, corrections=corrections),
                        target=pt_record_id(target),
                        label=text or (row.get("Diploma") or "").strip() or None,
                        source=f"{DRE_BASE_URL}{link}" if link else None,
                        date=clean_date(row.get("Data")),
                    )
                )
            for row in (data.get("DiretasList") or {}).get("List") or []:
                text = re.sub(r"\s+", " ", row.get("Texto") or "").strip()
                linked = str(row.get("DiplomaLinkId") or "0")
                # O DRE raramente preenche DiplomaLinkId; o diploma alterado vem no texto.
                target = pt_record_id(linked) if linked.isdigit() and linked != "0" else self.types.textual_reference(text)
                if not target:
                    continue
                relationships.append(
                    Relationship(
                        type=_relation_type(text, inverse=False, corrections=corrections),
                        target=target,
                        label=text or None,
                        date=clean_date(row.get("Data")),
                    )
                )
        return relationships

    def published(
        self,
        detail: dict[str, Any],
        *,
        ref: str,
        associations: dict[str, dict[str, Any]] | None = None,
        subjects: list[str] | None = None,
    ) -> SourceDocument:
        """Um diploma tal como publicado no Diário da República (ou no Jornal Oficial dos
        Açores, pelo catálogo que o DRE guarda).

        Sem texto e sem PDF, o registo é montado só com os metadados e vem dentro de
        `NoSourceText`: quem grava decide se o usa (não substitui um texto já existente)."""
        ref = (detail.get("LinkSitemap") or ref).strip()
        tipo, _ = split_sitemap_ref(ref)
        dre_id = str(detail.get("Id") or dre_id_from_ref(ref))
        document_type = self.types.resolve(tipo)
        official_number = (detail.get("Numero") or "").strip() or None
        regional = (
            regional_publication((detail.get("DiplomaLegacor") or {}).get("FonteRegional"))
            if (detail.get("TipoConteudo") or "") == AZORES_CATALOGUE
            else None
        )
        if regional:
            issuers = [
                re.sub(r"\s+", " ", name).strip()
                for name in (((detail.get("DiplomaLegacor") or {}).get("EntidadeEmitente_AJ") or {}).get("List") or [])
                if (name or "").strip()
            ]
            territory = regional["territory"]
        else:
            issuers = [name for name in [(detail.get("Emissor") or "").strip()] if name]
            territory = self.types.territory_for(document_type=tipo, official_number=official_number, issuer=issuers[0] if issuers else None)
        pdf_url = (detail.get("URL_PDF") or "").strip() or None
        html = detail.get("TextoFormatado") or ""
        warnings: list[str] = []
        has_text = True

        conversion = self.converter.convert(html) if html.strip() else None
        title = re.sub(r"\s+", " ", detail.get("Titulo") or "").strip() or f"{document_type.label} n.º {official_number}"
        if conversion and conversion.markdown:
            body = conversion.markdown if conversion.markdown.startswith("# ") else f"# {title}\n\n{conversion.markdown}"
        else:
            plain = (detail.get("Texto") or "").replace("\x00", "").strip()
            if plain:
                body = f"# {title}\n\n{plain}"
                warnings.append("Sem TextoFormatado; usado o texto simples do DRE.")
            elif pdf_url:
                body = f"# {title}\n\n> O texto deste diploma não está disponível em formato eletrónico. [Ver documento original]({pdf_url})"
                warnings.append("Sem texto eletrónico no DRE; o registo liga apenas ao PDF oficial.")
            else:
                has_text = False
                body = f"# {title}\n\n> O DRE não tem o texto deste diploma nem o PDF; este registo tem só os metadados."
                warnings.append("Sem texto e sem PDF no DRE; registo só com os metadados.")

        relationships = [
            Relationship(type="cites", target=pt_record_id(cited))
            for cited in (conversion.cited_dre_ids if conversion else [])
            if cited != dre_id
        ]
        relationships.extend(self.relationships(associations or {}))

        content_bytes = (html or detail.get("Texto") or "").encode("utf-8")
        if not has_text:
            # Sem texto, o conteúdo oficial que fica identificado são os próprios metadados.
            content_bytes = json.dumps(detail, ensure_ascii=False, sort_keys=True).encode("utf-8")
        sha256 = hashlib.sha256(content_bytes).hexdigest()
        official_url = f"{DRE_BASE_URL}{ref}"
        eli = (detail.get("ELI") or "").strip() or None
        reference = regional["reference"] if regional else (detail.get("Publicacao") or "").strip() or None
        now = utc_now()
        identifier = pt_record_id(dre_id)
        record = LegalRecord(
            id=identifier,
            title=title,
            summary=re.sub(r"<[^>]+>", "", detail.get("Sumario") or (detail.get("Resumo") if regional else "") or "").strip() or None,
            jurisdiction="regional" if territory else "portugal",
            territory=territory,
            document_type=document_type.slug,
            document_type_label=document_type.label,
            issuing_authority=issuers,
            proposing_entity=((detail.get("DiplomaLegis") or {}).get("EntidadeProponente") or "").strip() or None,
            official_number=official_number,
            official_date=clean_date(detail.get("DataAssinatura")),
            publication_date=clean_date(detail.get("DataPublicacao"))
            or clean_date(detail.get("DataDistribuicao"))
            or clean_date(detail.get("DataDisponibilizacao")),
            publication=Publication(
                gazette="Jornal Oficial dos Açores" if regional else (reference.split(" n.º", 1)[0] if reference and " n.º" in reference else None),
                reference=reference,
                number=regional["number"] if regional else ((detail.get("DiarioRepublica") or {}).get("Numero") or "").strip() or None,
                series=regional["series"] if regional else (detail.get("Serie") or "").strip() or None,
                supplement=None if regional else (detail.get("Suplemento") or "").strip() or None,
                pages=regional["pages"] if regional else (detail.get("Pagina") or "").strip() or None,
                pdf_url=pdf_url,
            ),
            legal_status=legal_status_from_dre(detail.get("Vigencia")),
            notes=[note for note in [re.sub(r"<[^>]+>", "", detail.get("Notas") or "").strip()] if note],
            version=Version(
                kind="original",
                label="Texto publicado no Jornal Oficial dos Açores" if regional else "Texto publicado no Diário da República",
                language="por",
            ),
            identifiers=Identifiers(eli=eli, dre=dre_id, dre_path=ref, internal=identifier),
            source=Source(
                id=SOURCE_ID,
                name=SOURCE_NAME,
                official_url=official_url,
                metadata_url=eli,
                content_url=official_url,
                retrieved_at=now,
                retrieval_method=(
                    "Endpoints screenservices (OutSystems) da aplicação web do DRE; não é uma API pública documentada"
                    + ("; catálogo do Jornal Oficial dos Açores guardado pelo DRE" if regional else "")
                ),
            ),
            integrity=Integrity(source_sha256=sha256),
            provenance=Provenance(collector="leis-portugal DRE", generated_by="leis-portugal collect dre", generated_at=now),
            reuse=dre_reuse(),
            subjects=subjects or [],
            relationships=merge_relationships(relationships),
            article_structure=article_structure(body, method="Classes de parágrafo do TextoFormatado do DRE"),
            derived_material=DerivedMaterial(
                notes="Markdown convertido do HTML TextoFormatado do DRE; o conteúdo-fonte é identificado pelo URL e SHA-256."
                if has_text
                else "Sem texto na fonte: o SHA-256 identifica a resposta de metadados do DRE (JSON, chaves ordenadas)."
            ),
            validation=Validation(checked_at=now, warnings=warnings),
        )
        media_type = "text/html" if has_text else "application/json"
        content = SourceContent(url=official_url, content=content_bytes, media_type=media_type, sha256=sha256)
        document = SourceDocument(record=record, body=body, content=content, warnings=warnings)
        if not has_text:
            record.note_source_gap(METADATA_ONLY_NOTE, checked=now[:10])
            raise NoSourceText(f"{ref}: sem texto e sem PDF no DRE.", record_id=identifier, document=document)
        return document
