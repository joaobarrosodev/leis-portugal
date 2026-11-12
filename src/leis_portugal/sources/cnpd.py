"""Decisões da Comissão Nacional de Proteção de Dados (www.cnpd.pt).

O histórico de decisões do site (`/decisoes/historico-de-decisoes/?year=AAAA&type=N`)
lista, por ano e tipo, cartões com o número, a entidade e o início do assunto; cada
cartão liga a um PDF (`/umbraco/surface/cnpdDecision/download/<id>`). Não há API.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from leis_portugal.domain.record import (
    Identifiers,
    Integrity,
    LegalRecord,
    Provenance,
    Reuse,
    Source,
    Version,
)
from leis_portugal.errors import FetchError, MetadataError
from leis_portugal.infrastructure.http import HttpClient
from leis_portugal.sources.content import SourceContent, SourceDocument
from leis_portugal.sources.decisions import reflow, sha256, signature_date
from leis_portugal.sources.pdftext import extract


BASE_URL = "https://www.cnpd.pt"
HISTORY_URL = f"{BASE_URL}/decisoes/historico-de-decisoes/"
SOURCE_ID = "cnpd"
SOURCE_NAME = "Comissão Nacional de Proteção de Dados"
FIRST_YEAR = 1994
RETRIEVAL_METHOD = "Histórico de decisões do site da CNPD (páginas HTML) e descarga do PDF de cada decisão; não é uma API"
REUSE = Reuse(
    status="permitted_with_conditions",
    attribution="Comissão Nacional de Proteção de Dados (www.cnpd.pt) — todos os direitos reservados",
    reference="https://www.cnpd.pt/avisos-legais-e-outras-informacoes/",
    notes=(
        "Reprodução total ou parcial permitida com distribuição gratuita, integridade dos documentos e citação "
        "expressa do site com a menção de direitos reservados; uso pessoal, associativo ou profissional, sem fins "
        "comerciais ou publicitários. Só a cópia certificada tem valor legal."
    ),
)


@dataclass(frozen=True)
class DecisionType:
    code: str  # valor do filtro `type` do site
    slug: str  # "parecer"
    label: str  # "Parecer"
    directory: str  # "pareceres"


TYPES = {
    item.slug: item
    for item in (
        DecisionType("4", "parecer", "Parecer", "pareceres"),
        DecisionType("2", "deliberacao", "Deliberação", "deliberacoes"),
        DecisionType("5", "diretriz", "Diretriz", "diretrizes"),
        DecisionType("6", "regulamento", "Regulamento", "regulamentos"),
        DecisionType("3", "registo", "Registo", "registos"),
        DecisionType("1", "autorizacao", "Autorização", "autorizacoes"),
    )
}


@dataclass(frozen=True)
class Listed:
    """Um cartão do histórico de decisões."""

    download_id: str
    decision_type: DecisionType
    year: int
    heading: str  # "Parecer 71/2026"
    entity: str | None
    subject: str | None

    @property
    def number(self) -> str | None:
        match = re.search(r"(\d+)\s*/\s*(\d{4})", self.heading)
        return f"{int(match.group(1))}/{match.group(2)}" if match else None

    @property
    def url(self) -> str:
        return f"{BASE_URL}/umbraco/surface/cnpdDecision/download/{self.download_id}"


def parse_listing(page: str, decision_type: DecisionType, year: int) -> tuple[int | None, list[Listed]]:
    """O total anunciado ("N registos encontrados") e os cartões de uma página."""
    soup = BeautifulSoup(page, "html.parser")
    count = soup.select_one(".search-count")
    total = int(count.get_text(strip=True)) if count and count.get_text(strip=True).isdigit() else None
    items: list[Listed] = []
    for link in soup.select("a[href*='cnpdDecision/download/']"):
        match = re.search(r"download/(\d+)", link["href"])
        if not match:
            continue

        def text(selector: str, link=link) -> str | None:
            node = link.select_one(selector)
            value = html.unescape(node.get_text(" ", strip=True)) if node else ""
            return re.sub(r"\s+", " ", value).strip() or None

        items.append(
            Listed(
                download_id=match.group(1),
                decision_type=decision_type,
                year=year,
                heading=text(".c-card-header-medium") or "",
                entity=text(".c-card-header"),
                subject=text(".c-card-text"),
            )
        )
    return total, items


class CnpdClient:
    def __init__(self, http: HttpClient | None = None) -> None:
        self.http = http or HttpClient(min_interval=1.0)

    def listing(self, decision_type: DecisionType, year: int) -> list[Listed]:
        """Todos os cartões de um ano e tipo (50 por página). Falha se o total não bate."""
        found: dict[str, Listed] = {}
        total: int | None = None
        page = 1
        while True:
            params = {"year": str(year), "type": decision_type.code}
            if page > 1:
                params["pgd"] = str(page)
            response = self.http.get(HISTORY_URL, params=params)
            announced, items = parse_listing(response.content.decode("utf-8", "replace"), decision_type, year)
            total = announced if total is None else total
            new = [item for item in items if item.download_id not in found]
            found.update((item.download_id, item) for item in new)
            if not new or (total is not None and len(found) >= total):
                break
            page += 1
        if total is not None and len(found) != total:
            raise MetadataError(f"CNPD {decision_type.label} {year}: o site anuncia {total} e a listagem tem {len(found)}")
        return list(found.values())

    def download(self, item: Listed) -> SourceContent:
        response = self.http.get(item.url, headers={"Accept": "application/pdf, */*;q=0.1"})
        media_type = (response.headers.get("Content-Type") or "").split(";")[0].strip() or "application/octet-stream"
        if not response.content:
            raise FetchError(f"{item.url}: resposta vazia")
        return SourceContent(url=item.url, content=response.content, media_type=media_type, sha256=sha256(response.content))


def record_id(item: Listed) -> str:
    return f"pt:cnpd:{item.download_id}"


def summary_of(item: Listed) -> str | None:
    """Entidade e início do assunto, como o site os mostra (o assunto vem cortado a 100 carateres)."""
    subject = item.subject
    if subject and len(subject) >= 99 and not subject.endswith((".", "…")):
        subject += "…"
    parts = [part for part in (item.entity, subject) if part]
    return " — ".join(parts) or None


def to_document(item: Listed, content: SourceContent) -> SourceDocument:
    decision_type = item.decision_type
    number = item.number
    title = f"{decision_type.label} da CNPD n.º {number}" if number else f"{decision_type.label} da CNPD ({item.heading or item.download_id})"
    is_pdf = content.media_type == "application/pdf" or content.content[:4] == b"%PDF"
    extracted = extract(content.content) if is_pdf else None
    text = extracted.text if extracted else None
    notes: list[str] = []
    warnings: list[str] = []
    if item.entity:
        notes.append(f"Entidade: {item.entity}")
    if extracted and extracted.ocr_pages:
        notes.append(
            f"Texto obtido por OCR em {extracted.ocr_pages} de {extracted.pages} página(s) (digitalização): pode ter erros de reconhecimento."
        )
    if extracted and extracted.empty_pages:
        notes.append(f"Texto incompleto: {extracted.empty_pages} de {extracted.pages} página(s) do PDF sem texto (digitalização sem OCR).")
        warnings.append("Texto incompleto: páginas digitalizadas sem OCR.")
    if text:
        body = f"# {title}\n\n{reflow(text)}"
        official_date = signature_date(text, year=item.year)
    else:
        body = f"# {title}\n\nO texto não foi extraído do PDF oficial: [{item.url}]({item.url})."
        official_date = None
        notes.append("Fonte sem texto: o PDF da CNPD não tem camada de texto (digitalização); falta OCR.")
        warnings.append("Sem texto extraído do PDF.")
    record = LegalRecord(
        id=record_id(item),
        title=title,
        summary=summary_of(item),
        jurisdiction="regulator",
        document_type=f"{decision_type.slug}-cnpd",
        document_type_label=f"{decision_type.label} da Comissão Nacional de Proteção de Dados",
        issuing_authority=[SOURCE_NAME],
        official_number=number,
        official_date=official_date,
        notes=notes,
        version=Version(kind="original", label="Texto da decisão publicada no site da CNPD", language="por"),
        identifiers=Identifiers(internal=record_id(item)),
        source=Source(
            id=SOURCE_ID,
            name=SOURCE_NAME,
            official_url=item.url,
            metadata_url=urljoin(HISTORY_URL, f"?year={item.year}&type={decision_type.code}"),
            content_url=item.url,
            retrieval_method=RETRIEVAL_METHOD,
        ),
        integrity=Integrity(source_sha256=content.sha256),
        provenance=Provenance(collector="leis-portugal CNPD", generated_by="leis-portugal collect cnpd"),
        reuse=REUSE,
    )
    record.validation.warnings = warnings
    return SourceDocument(record=record, body=body, content=content, warnings=warnings)
