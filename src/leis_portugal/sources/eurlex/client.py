"""Transporte do EUR-Lex/CELLAR: consultas SPARQL e ficheiros das expressões."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date
from typing import Any

from leis_portugal.domain.identifiers import normalize_celex
from leis_portugal.errors import FetchError, MetadataError
from leis_portugal.infrastructure.http import HttpClient
from leis_portugal.sources.content import SourceContent


CDM = "http://publications.europa.eu/ontology/cdm#"
SPARQL_ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"
_PREFIXES = f"""PREFIX cdm: <{CDM}>
PREFIX cmr: <http://publications.europa.eu/ontology/cdm/cmr#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""
_TEXT_MEDIA_TYPES = {"application/xhtml+xml", "text/html", "application/xml"}

# Predicados CDM das relações, nos dois sentidos (o mapeamento para tipos está no mapper).
OUTGOING_PREDICATES = (
    "resource_legal_amends_resource_legal",
    "resource_legal_repeals_resource_legal",
    "resource_legal_implicitly_repeals_resource_legal",
    "resource_legal_based_on_resource_legal",
    "resource_legal_corrects_resource_legal",
    "work_cites_work",
)
INCOMING_PREDICATES = (
    "resource_legal_amends_resource_legal",
    "resource_legal_repeals_resource_legal",
    "resource_legal_implicitly_repeals_resource_legal",
    "resource_legal_corrects_resource_legal",
    "case-law_interpretes_resource_legal",
)


@dataclass(frozen=True)
class Expression:
    """Expressão linguística de um ato e os seus ficheiros."""

    uri: str | None
    title: str
    short_title: str | None
    last_modified: str | None
    text_items: list[str]
    pdf_url: str | None


@dataclass(frozen=True)
class GraphRelation:
    direction: str  # "out": este ato é o sujeito; "in": outro ato aponta para este
    predicate: str
    target_uri: str | None
    target_celex: str
    date: str | None


def _doc_order(url: str) -> tuple[int, str]:
    match = re.search(r"DOC_(\d+)$", url)
    return (int(match.group(1)) if match else 0, url)


class CellarClient:
    """Pedidos ao CELLAR. Uma instância por thread."""

    def __init__(self, http: HttpClient | None = None) -> None:
        self.http = http or HttpClient(timeout=120, min_interval=0.2, max_retries=4)

    # ---------------------------------------------------------------------- SPARQL

    def sparql(self, query: str) -> list[dict[str, str]]:
        """Executa uma consulta e devolve as linhas como dicionários de valores."""
        try:
            response = self.http.get(
                SPARQL_ENDPOINT,
                params={"query": _PREFIXES + query},
                headers={"Accept": "application/sparql-results+json"},
            )
        except FetchError as exc:
            raise FetchError(f"Falha no SPARQL do CELLAR: {exc}") from exc
        try:
            bindings = response.json().get("results", {}).get("bindings", [])
        except ValueError as exc:
            raise FetchError("O SPARQL do CELLAR não devolveu JSON válido.") from exc
        return [{key: value.get("value") for key, value in row.items()} for row in bindings]

    def discover(self, start: date, end: date, *, types: str = "RLD") -> list[tuple[str, str]]:
        """(CELEX, data) dos atos legislativos publicados no JO entre duas datas.

        `work_date_creation_legacy` existe tanto nos números antigos do JO como na
        publicação ato a ato (desde outubro de 2023)."""
        type_filter = "".join(sorted(set(types.upper()) & set("RLD"))) or "RLD"
        rows = self.sparql(f"""
SELECT DISTINCT ?celex ?published WHERE {{
  ?work cdm:work_date_creation_legacy ?published .
  FILTER(?published >= "{start.isoformat()}"^^xsd:date && ?published <= "{end.isoformat()}"^^xsd:date)
  ?work cdm:resource_legal_id_celex ?celex .
  FILTER(REGEX(STR(?celex), "^3[0-9]{{4}}[{type_filter}][0-9]{{4}}$"))
}} ORDER BY ?published ?celex""")
        found: dict[str, str] = {}
        for row in rows:
            if row.get("celex") and row["celex"] not in found:
                found[row["celex"]] = (row.get("published") or "")[:10]
        return list(found.items())

    def expression(self, celex: str, *, language: str = "por") -> Expression:
        """Expressão linguística e ficheiros (XHTML/HTML/PDF), para qualquer período.

        O CELEX é procurado como literal tipado: um FILTER(STR(...)) percorre o grafo
        inteiro (dezenas de segundos)."""
        normalized = normalize_celex(celex)
        rows = self.sparql(f"""
SELECT ?expr ?title ?short ?modified ?mtype ?item WHERE {{
  ?work cdm:resource_legal_id_celex "{normalized}"^^xsd:string .
  ?expr cdm:expression_belongs_to_work ?work ;
        cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/{language.upper()}> .
  OPTIONAL {{ ?expr cdm:expression_title ?title }}
  OPTIONAL {{ ?expr cdm:expression_title_short ?short }}
  OPTIONAL {{ ?expr cmr:lastModificationDate ?modified }}
  OPTIONAL {{ ?manifestation cdm:manifestation_manifests_expression ?expr ;
                             cdm:manifestation_type ?mtype .
             ?item cdm:item_belongs_to_manifestation ?manifestation . }}
}}""")
        if not rows:
            raise MetadataError(f"Sem expressão na língua {language} para CELEX {normalized}.")

        def first(name: str) -> str | None:
            return next((row[name] for row in rows if row.get(name)), None)

        items: dict[str, list[str]] = {}
        for row in rows:
            if row.get("mtype") and row.get("item"):
                items.setdefault(row["mtype"].lower(), []).append(row["item"])
        pdf_type = next((name for name in ("pdfa2a", "pdfa1a", "pdfa2b", "pdfa1b", "pdf", "pdfx") if items.get(name)), None) or next(
            (name for name in sorted(items) if name.startswith("pdf")), None
        )
        title = first("title")
        if not title:
            raise MetadataError(f"A expressão {language} de {normalized} não tem título.")
        return Expression(
            uri=first("expr"),
            title=re.sub(r"\s+", " ", title).strip(),
            short_title=first("short"),
            last_modified=first("modified"),
            # Atos antigos do JO só têm HTML simples (sem classes oj-*).
            text_items=sorted(set(items.get("xhtml") or items.get("html") or []), key=_doc_order),
            pdf_url=sorted(set(items[pdf_type]), key=_doc_order)[0] if pdf_type else None,
        )

    def work(self, celex: str) -> dict[str, Any]:
        """Metadados do ato (work), em bruto: cada campo com todos os valores encontrados."""
        normalized = normalize_celex(celex)
        rows = self.sparql(f"""
SELECT ?work ?eli ?signature_date ?entry_date ?end_date ?in_force ?type_code ?year ?number
       ?published ?oj_date ?act_date ?oj_id ?oj_number ?oj_act_number ?author WHERE {{
  VALUES ?celex {{ "{normalized}"^^xsd:string }}
  ?work cdm:resource_legal_id_celex ?celex .
  OPTIONAL {{ ?work cdm:resource_legal_eli ?eli . }}
  OPTIONAL {{ ?work cdm:resource_legal_date_signature ?signature_date . }}
  OPTIONAL {{ ?work cdm:resource_legal_date_entry-into-force ?entry_date . }}
  OPTIONAL {{ ?work cdm:resource_legal_date_end-of-validity ?end_date . }}
  OPTIONAL {{ ?work cdm:resource_legal_in-force ?in_force . }}
  OPTIONAL {{ ?work cdm:resource_legal_type ?type_code . }}
  OPTIONAL {{ ?work cdm:resource_legal_year ?year . }}
  OPTIONAL {{ ?work cdm:resource_legal_number_natural ?number . }}
  OPTIONAL {{ ?work cdm:work_date_creation_legacy ?published . }}
  OPTIONAL {{ ?work cdm:official-journal-act_number ?oj_act_number . }}
  OPTIONAL {{ ?work cdm:official-journal-act_date_publication ?act_date . }}
  OPTIONAL {{ ?work cdm:work_id_document ?oj_id . FILTER(STRSTARTS(STR(?oj_id), "oj:")) }}
  OPTIONAL {{ ?work cdm:resource_legal_published_in_official-journal ?oj .
             OPTIONAL {{ ?oj cdm:publication_general_date_publication ?oj_date . }}
             OPTIONAL {{ ?oj cdm:official-journal_number ?oj_number . }} }}
  OPTIONAL {{ ?work cdm:work_created_by_agent ?author . }}
}} ORDER BY ?work ?signature_date ?entry_date""")
        if not rows:
            raise MetadataError(f"O SPARQL do CELLAR não devolveu metadados para CELEX {normalized}.")
        values: dict[str, list[str]] = {}
        for row in rows:
            for key, value in row.items():
                if value and value not in values.setdefault(key, []):
                    values[key].append(value)
        return values

    def relations(self, work_uri: str) -> list[GraphRelation]:
        outgoing = " ".join(f"cdm:{name}" for name in OUTGOING_PREDICATES)
        incoming = " ".join(f"cdm:{name}" for name in INCOMING_PREDICATES)
        rows = self.sparql(f"""
SELECT ?direction ?relation ?target ?celex ?date WHERE {{
  {{
    VALUES ?relation {{ {outgoing} }}
    <{work_uri}> ?relation ?target .
    BIND("out" AS ?direction)
  }} UNION {{
    VALUES ?relation {{ {incoming} }}
    ?target ?relation <{work_uri}> .
    BIND("in" AS ?direction)
  }}
  ?target cdm:resource_legal_id_celex ?celex .
  OPTIONAL {{ ?target cdm:work_date_creation_legacy ?date . }}
}} ORDER BY ?direction ?relation ?celex""")
        return [
            GraphRelation(
                direction=row.get("direction") or "",
                predicate=(row.get("relation") or "").rsplit("#", 1)[-1],
                target_uri=row.get("target"),
                target_celex=row.get("celex") or "",
                date=(row.get("date") or "")[:10] or None,
            )
            for row in rows
        ]

    def eurovoc(self, work_uri: str, *, language: str = "pt") -> list[str]:
        rows = self.sparql(f"""
SELECT DISTINCT ?label WHERE {{
  <{work_uri}> cdm:work_is_about_concept_eurovoc ?concept .
  ?concept skos:prefLabel ?label .
  FILTER(LANG(?label) = "{language}")
}} ORDER BY ?label""")
        return [label for label in ((row.get("label") or "").strip() for row in rows) if label]

    def consolidations(self, work_uri: str) -> list[str]:
        """CELEX de todas as versões consolidadas ligadas ao ato no grafo."""
        rows = self.sparql(f"""
SELECT DISTINCT ?celex WHERE {{
  ?consolidated cdm:act_consolidated_consolidates_resource_legal <{work_uri}> ;
                cdm:resource_legal_id_celex ?celex .
}}""")
        return [row["celex"] for row in rows if row.get("celex")]

    # -------------------------------------------------------------------- ficheiros

    def fetch_text(self, expression: Expression) -> SourceContent:
        """XHTML/HTML da expressão; vários itens são concatenados."""
        if not expression.text_items:
            raise MetadataError("A expressão não tem manifestação XHTML nem HTML.")
        parts = []
        for item in expression.text_items:
            response = self.http.get(item, headers={"Accept": "application/xhtml+xml, application/xml;q=0.9, */*;q=0.1"})
            media_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            if media_type not in _TEXT_MEDIA_TYPES:
                raise FetchError(f"Tipo de conteúdo inesperado para o XHTML: {media_type or 'desconhecido'}")
            if not response.content:
                raise FetchError(f"Resposta vazia para {item}")
            parts.append((response.url, response.content, media_type))
        content = b"\n".join(part[1] for part in parts)
        return SourceContent(url=parts[0][0], content=content, media_type=parts[0][2], sha256=_sha256(content))

    def fetch_pdf(self, url: str) -> SourceContent:
        response = self.http.get(url, headers={"Accept": "application/pdf, */*;q=0.1"})
        if not response.content:
            raise FetchError(f"Resposta vazia para {url}")
        return SourceContent(url=url, content=response.content, media_type="application/pdf", sha256=_sha256(response.content))


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
