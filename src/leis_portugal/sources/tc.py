"""Acórdãos do Tribunal Constitucional (www.tribunalconstitucional.pt).

As listagens anuais estão em blocos de 100 números (`/tc/acordaos/AAAA0001-0100.html`),
com o processo, a formação, a espécie, a data e o relator; cada acórdão tem uma página
HTML (`/tc/acordaos/AAAANNNN.html`) gerada a partir do Word. Não há API.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
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
from leis_portugal.errors import FetchError, MetadataError, NoSourceText
from leis_portugal.infrastructure.http import HttpClient
from leis_portugal.sources.content import SourceContent, SourceDocument
from leis_portugal.sources.decisions import sha256


BASE_URL = "https://www.tribunalconstitucional.pt/tc/acordaos/"
SOURCE_ID = "tribunal-constitucional"
SOURCE_NAME = "Tribunal Constitucional"
FIRST_YEAR = 1983
DOCUMENT_TYPE = "acordao-tribunal-constitucional"
RETRIEVAL_METHOD = "Listagens anuais e páginas HTML dos acórdãos no site do Tribunal Constitucional; não é uma API"
REUSE = Reuse(
    status="restricted",
    attribution="Tribunal Constitucional (www.tribunalconstitucional.pt) — todos os direitos reservados",
    reference="https://www.tribunalconstitucional.pt/tc/home.html",
    notes=(
        "O site autoriza a reprodução para fins privados, com citação da fonte e da natureza não autêntica do texto; "
        "declara todos os direitos reservados. A jurisprudência publicada no site não tem carácter autêntico: a versão "
        "oficial é a dos arquivos do Tribunal (e, quando publicada, a do Diário da República)."
    ),
)


@dataclass(frozen=True)
class Listed:
    number: int
    year: int
    href: str
    process: str | None
    formation: str | None
    kind: str | None
    decided: str | None  # AAAA-MM-DD
    rapporteur: str | None

    @property
    def official_number(self) -> str:
        return f"{self.number}/{self.year}"

    @property
    def url(self) -> str:
        return urljoin(BASE_URL, self.href)


def decode(content: bytes) -> str:
    """As páginas declaram ISO-8859-1, mas as recentes são UTF-8 e as antigas Windows-1252."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("cp1252", "replace")


def block_url(year: int, start: int) -> str:
    return f"{BASE_URL}{year}{start:04d}-{start + 99:04d}.html"


def _date(value: str | None) -> str | None:
    match = re.fullmatch(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", (value or "").strip())
    if not match:
        return None
    try:
        return date(int(match.group(3)), int(match.group(2)), int(match.group(1))).isoformat()
    except ValueError:
        return None


def parse_listing(page: str, year: int) -> list[Listed]:
    soup = BeautifulSoup(page, "html.parser")
    items: list[Listed] = []
    for row in soup.select("table.ilistashtmlminimal_in tr"):
        link = row.select_one("a[href]")
        if not link:
            continue
        match = re.fullmatch(rf"{year}(\d{{4}})\.html", link["href"].strip())
        if not match:
            continue

        def cell(name: str, row=row) -> str | None:
            node = row.select_one(f"td.{name}")
            value = re.sub(r"\s+", " ", node.get_text(" ", strip=True)) if node else ""
            return value or None

        items.append(
            Listed(
                number=int(match.group(1)),
                year=year,
                href=link["href"].strip(),
                process=cell("processo"),
                formation=cell("seccao"),
                kind=cell("especie"),
                decided=_date(cell("data")),
                rapporteur=cell("relator"),
            )
        )
    return items


_SECTION = re.compile(r"^(?:Word)?Section\d+$")


def judgment_markdown(page: str) -> str:
    """O texto do acórdão (as secções Word da página), em parágrafos.

    As páginas recentes têm `div.WordSection1`; as anteriores a 2013, `div.Section1`; algumas,
    só o documento dentro de `div#acimport`."""
    soup = BeautifulSoup(page, "html.parser")
    sections = soup.find_all("div", class_=_SECTION)
    if not sections:
        # Algumas páginas trazem o documento Word inteiro dentro de #acimport, sem secções.
        sections = [node for node in soup.select("#acimport") if node.find("p")]
    if not sections:
        raise NoSourceText("Página sem o texto do acórdão (sem secções WordSection nem Section).")
    paragraphs: list[str] = []
    for section in sections:
        blocks = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"]
        for block in section.find_all(blocks):
            if block.find_parent(blocks) is not None:
                continue
            text = re.sub(r"\s+", " ", block.get_text("")).strip()
            if text:
                paragraphs.append(text)
    if not paragraphs:
        raise NoSourceText("Página do acórdão sem texto.")
    return "\n\n".join(paragraphs)


class TcClient:
    def __init__(self, http: HttpClient | None = None) -> None:
        self.http = http or HttpClient(min_interval=1.0)

    def listing(self, year: int) -> list[Listed]:
        """Todos os acórdãos de um ano, bloco a bloco, até ao primeiro bloco vazio ou inexistente."""
        items: dict[int, Listed] = {}
        start = 1
        while True:
            try:
                response = self.http.get(block_url(year, start))
            except FetchError as exc:
                if "HTTP 404" in str(exc) and start > 1:
                    break
                raise
            block = parse_listing(decode(response.content), year)
            if not block:
                break
            items.update((item.number, item) for item in block)
            start += 100
        if not items:
            raise MetadataError(f"Tribunal Constitucional {year}: listagem sem acórdãos")
        return [items[number] for number in sorted(items)]

    def page(self, item: Listed) -> SourceContent:
        response = self.http.get(item.url)
        return SourceContent(url=item.url, content=response.content, media_type="text/html", sha256=sha256(response.content))


def record_id(item: Listed) -> str:
    return f"pt:tc:acordao:{item.year}:{item.number}"


def to_document(item: Listed, content: SourceContent, *, dre_id: str | None = None) -> SourceDocument:
    title = f"Acórdão do Tribunal Constitucional n.º {item.official_number}"
    text = judgment_markdown(decode(content.content))
    notes = [
        f"{label}: {value}"
        for label, value in (
            ("Processo", item.process),
            ("Formação", item.formation),
            ("Espécie", item.kind),
            ("Relator", item.rapporteur),
        )
        if value
    ]
    record = LegalRecord(
        id=record_id(item),
        title=title,
        jurisdiction="portugal",
        document_type=DOCUMENT_TYPE,
        document_type_label="Acórdão do Tribunal Constitucional",
        issuing_authority=[SOURCE_NAME],
        official_number=item.official_number,
        official_date=item.decided,
        notes=notes,
        version=Version(kind="original", label="Texto publicado no site do Tribunal Constitucional (sem carácter autêntico)", language="por"),
        identifiers=Identifiers(dre=dre_id, internal=record_id(item)),
        source=Source(
            id=SOURCE_ID,
            name=SOURCE_NAME,
            official_url=item.url,
            metadata_url=block_url(item.year, ((item.number - 1) // 100) * 100 + 1),
            content_url=item.url,
            retrieval_method=RETRIEVAL_METHOD,
        ),
        integrity=Integrity(source_sha256=content.sha256),
        provenance=Provenance(collector="leis-portugal Tribunal Constitucional", generated_by="leis-portugal collect tc"),
        reuse=REUSE,
    )
    return SourceDocument(record=record, body=f"# {title}\n\n{text}", content=content)
