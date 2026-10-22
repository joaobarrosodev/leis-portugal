"""Conversão dos dados do CELLAR para o modelo do acervo (sem rede)."""

from __future__ import annotations

import re
from datetime import date, datetime
from urllib.parse import quote

from leis_portugal.domain.identifiers import eu_record_id, normalize_celex, parse_celex
from leis_portugal.domain.record import (
    ArticleStructure,
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
    utc_now,
)
from leis_portugal.sources.content import SourceContent, SourceDocument
from leis_portugal.sources.eurlex.client import Expression, GraphRelation
from leis_portugal.sources.eurlex.xhtml import CellarXhtmlMarkdownConverter


SOURCE_ID = "eurlex-cellar"
SOURCE_NAME = "EUR-Lex / CELLAR"
LEGAL_NOTICE_URL = "https://eur-lex.europa.eu/content/legal-notice/legal-notice.html"

DOCUMENT_TYPES = {"R": ("regulation", "Regulamento"), "L": ("directive", "Diretiva"), "D": ("decision", "Decisão"), "E": ("treaty", "Tratado")}
# Subtipo a partir do ELI (`reg_del`, `dir_impl`, ...).
ELI_SUBTYPES = {"del": "Delegado", "impl": "de Execução"}
OUTGOING_TYPES = {
    "resource_legal_amends_resource_legal": "amends",
    "resource_legal_repeals_resource_legal": "repeals",
    "resource_legal_implicitly_repeals_resource_legal": "implicitly_repeals",
    "resource_legal_based_on_resource_legal": "based_on",
    "resource_legal_corrects_resource_legal": "corrects",
    "work_cites_work": "cites",
}
INCOMING_TYPES = {
    "resource_legal_amends_resource_legal": "amended_by",
    "resource_legal_repeals_resource_legal": "repealed_by",
    "resource_legal_implicitly_repeals_resource_legal": "repealed_by",
    "resource_legal_corrects_resource_legal": "corrected_by",
    "case-law_interpretes_resource_legal": "interpreted_by",
}
AUTHORS = {
    "EP": "Parlamento Europeu",
    "CONSIL": "Conselho da União Europeia",
    "COM": "Comissão Europeia",
    "ECB": "Banco Central Europeu",
    "EUCO": "Conselho Europeu",
}


def citation_title(title: str) -> tuple[str, str | None]:
    """Divide o título oficial em designação de citação e sumário.

    "Regulamento (UE) 2016/679 do Parlamento Europeu e do Conselho, de 27 de abril
    de 2016, relativo à proteção…" -> ("Regulamento (UE) 2016/679 do Parlamento
    Europeu e do Conselho, de 27 de abril de 2016", título completo).
    """
    match = re.match(r"^(.*?\bde \d{1,2}\.?º? de [A-Za-zçÇ]+ de \d{4})", title)
    if match and len(match.group(1)) < len(title):
        return match.group(1).rstrip(" ,"), title
    return title, None


def oj_series(oj_id: str | None) -> str | None:
    """`oj:JOL_2016_119_R` -> `L`; `oj:L_202602343` -> `L`."""
    match = re.match(r"^oj:(?:JO)?([LC])_", oj_id or "")
    return match.group(1) if match else None


def latest_consolidation(candidates: list[str], celex: str, *, today: date | None = None) -> str | None:
    """CELEX da versão consolidada mais recente já aplicável (`0AAAATNNNN-AAAAMMDD`).

    Só aceita consolidações do próprio ato: um ato revogado pode "consolidar" no grafo
    o ato que o revogou (a consolidação da Diretiva 95/46 aponta para o RGPD)."""
    prefix = "0" + normalize_celex(celex)[1:] + "-"
    dated = [(match.group(1), item) for item in candidates if item.startswith(prefix) and (match := re.search(r"-([0-9]{8})$", item))]
    if not dated:
        return None
    limit = (today or date.today()).strftime("%Y%m%d")
    applicable = [item for item in dated if item[0] <= limit] or dated
    return max(applicable)[1]


def relationships(relations: list[GraphRelation]) -> list[Relationship]:
    result: list[Relationship] = []
    seen: set[tuple[str, str]] = set()
    for relation in relations:
        mapping = OUTGOING_TYPES if relation.direction == "out" else INCOMING_TYPES
        relation_type = mapping.get(relation.predicate)
        if not relation_type or not relation.target_celex:
            continue
        try:
            target = f"celex:{normalize_celex(relation.target_celex)}"
        except ValueError:
            continue
        if (relation_type, target) in seen:
            continue
        seen.add((relation_type, target))
        result.append(
            Relationship(
                type=relation_type,
                target=target,
                source=relation.target_uri,
                date=relation.date if relation_type != "cites" else None,
            )
        )
    return result


def _authors(uris: list[str]) -> list[str]:
    """Autores numa ordem fixa (o SPARQL não garante a ordem das linhas)."""
    codes = {uri.rsplit("/", 1)[-1] for uri in uris}
    ordered = [code for code in AUTHORS if code in codes] + sorted(codes - set(AUTHORS))
    return [AUTHORS.get(code, code) for code in ordered]


def _first(values: dict[str, list[str]], name: str) -> str | None:
    found = values.get(name) or []
    return found[0] if found else None


class EurLexMapper:
    def __init__(self) -> None:
        self.converter = CellarXhtmlMarkdownConverter()

    def document(
        self,
        celex: str,
        *,
        language: str,
        expression: Expression,
        work: dict[str, list[str]],
        relations: list[Relationship],
        subjects: list[str],
        content: SourceContent,
        consolidated_celex: str | None,
        warnings: list[str],
    ) -> SourceDocument:
        normalized = normalize_celex(celex)
        parts = parse_celex(normalized)
        eli = _first(work, "eli")
        year = int(_first(work, "year") or parts.year)
        number = int(_first(work, "number") or parts.number)
        oj_id = _first(work, "oj_id")
        # Data do número do JO (antigos) ou do ato (desde 2023); a data "legacy" é a de distribuição.
        published = (_first(work, "oj_date") or _first(work, "act_date") or _first(work, "published") or "")[:10] or None
        in_force = _first(work, "in_force")
        if in_force in {"1", "true"}:
            legal_status = "in_force"
        elif in_force is not None:
            legal_status = "repealed" if any(item.type == "repealed_by" for item in relations) else "not_in_force"
        else:
            legal_status = "unknown"

        type_code = _first(work, "type_code") or parts.document_type_code
        document_type, label = DOCUMENT_TYPES.get(type_code, (f"eu_{type_code.lower()}", None))
        subtype = re.search(r"/eli/[a-z]+_([a-z]+)/", eli or "")
        if label and subtype and subtype.group(1) in ELI_SUBTYPES:
            label = f"{label} {ELI_SUBTYPES[subtype.group(1)]}"
        title, summary = citation_title(re.sub(r"\s+", " ", expression.title).strip())

        series = oj_series(oj_id)
        reference = None
        if published:
            day = datetime.strptime(published, "%Y-%m-%d").date()
            when = f"{day.day}.{day.month}.{day.year}"
            if _first(work, "oj_act_number"):
                reference = f"JO {series or 'L'}, {year}/{_first(work, 'oj_act_number')}, {when}"
            elif _first(work, "oj_number"):
                reference = f"JO {series or 'L'} {_first(work, 'oj_number')} de {when}"

        body, structure, date_hint = self._body(content, title=title, warnings=warnings)
        published = published or date_hint
        lang_code = "PT" if language == "por" else language.upper()
        consolidation_date = None
        if consolidated_celex:
            stamp = consolidated_celex.rsplit("-", 1)[-1]
            consolidation_date = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}"
        identifier = eu_record_id(normalized, language)
        now = utc_now()
        record = LegalRecord(
            id=identifier,
            title=title,
            short_title=expression.short_title,
            summary=summary,
            jurisdiction="european_union",
            document_type=document_type,
            document_type_label=label,
            issuing_authority=_authors(work.get("author", [])),
            official_number=f"{year}/{number}",
            official_date=_first(work, "signature_date"),
            publication_date=published,
            publication=Publication(
                gazette="Jornal Oficial da União Europeia",
                reference=reference,
                number=_first(work, "oj_act_number") or _first(work, "oj_number"),
                series=series,
                pdf_url=expression.pdf_url,
            ),
            entry_into_force_dates=sorted(work.get("entry_date", [])),
            end_of_validity_date=_first(work, "end_date"),
            legal_status=legal_status,
            language=language,
            version=Version(
                kind="consolidated" if consolidated_celex else "original",
                label="Versão consolidada (EUR-Lex), sem valor jurídico" if consolidated_celex else "Texto original publicado no Jornal Oficial",
                language=language,
                consolidation_date=consolidation_date,
            ),
            identifiers=Identifiers(celex=normalized, eli=eli, oj=oj_id, internal=identifier),
            source=Source(
                id=SOURCE_ID,
                name=SOURCE_NAME,
                official_url=f"https://eur-lex.europa.eu/legal-content/{lang_code}/TXT/?uri=CELEX%3A{normalized}",
                metadata_url=expression.uri,
                content_url=content.url,
                consolidated_url=(
                    f"https://eur-lex.europa.eu/legal-content/{lang_code}/TXT/?uri=CELEX%3A{quote(consolidated_celex)}"
                    if consolidated_celex
                    else None
                ),
                retrieved_at=now,
                retrieval_method="CELLAR RDF + SPARQL + negociação de conteúdo XHTML",
                source_modified_at=expression.last_modified,
            ),
            integrity=Integrity(source_sha256=content.sha256),
            provenance=Provenance(
                collector="leis-portugal EUR-Lex/CELLAR",
                generated_by="leis-portugal collect eurlex",
                generated_at=now,
                notes=f"Texto consolidado {consolidated_celex}." if consolidated_celex else None,
            ),
            reuse=Reuse(
                status="permitted_with_conditions",
                attribution="União Europeia, EUR-Lex / Publicações da União Europeia",
                reference=LEGAL_NOTICE_URL,
                notes="Verificar o aviso jurídico aplicável; só o texto publicado no Jornal Oficial faz fé (as consolidações são instrumentos de documentação).",
            ),
            subjects=subjects,
            relationships=relations,
            article_structure=structure,
            derived_material=DerivedMaterial(
                notes="O Markdown é uma conversão derivada do XHTML do CELLAR; o conteúdo-fonte é identificado pelo URL e SHA-256."
            ),
            validation=Validation(checked_at=now, warnings=list(warnings)),
        )
        return SourceDocument(record=record, body=body, content=content, warnings=record.validation.warnings)

    def _body(self, content: SourceContent, *, title: str, warnings: list[str]) -> tuple[str, ArticleStructure, str | None]:
        """Markdown, estrutura e data de publicação indicada no próprio texto (se houver)."""
        if content.media_type == "application/pdf":
            body = (
                f"# {title}\n\n> O texto deste ato não está disponível em formato eletrónico no CELLAR. "
                f"[Ver documento original]({content.url})"
            )
            return body, ArticleStructure(article_count=0, section_count=0, extraction_method="Sem texto eletrónico (só PDF)"), None
        conversion = self.converter.convert(content.content, source_url=content.url)
        warnings.extend(conversion.warnings)
        markdown = conversion.markdown.strip()
        if not markdown.startswith("# "):
            # Texto consolidado: começa pelas notas do EUR-Lex; o título do ato passa a H1.
            markdown = re.sub(r"^# ", "## ", markdown, flags=re.MULTILINE)
            markdown = f"# {title}\n\n{markdown}"
        return markdown, ArticleStructure(
            article_count=conversion.article_count,
            section_count=conversion.section_count,
            extraction_method="Classes XHTML do CELLAR (oj-ti-art / title-article-norm)",
        ), conversion.publication_date_hint
