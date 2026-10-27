"""Conversão determinística de XHTML do CELLAR para Markdown."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup, NavigableString, Tag


@dataclass(frozen=True)
class MarkdownConversionResult:
    """Resultado da conversão de um XHTML oficial."""

    markdown: str
    title_hint: str | None
    publication_date_hint: str | None
    article_count: int
    section_count: int
    warnings: list[str] = field(default_factory=list)


class CellarXhtmlMarkdownConverter:
    """Converte o XHTML do CELLAR: texto do Jornal Oficial (classes `oj-*`) e
    texto consolidado (classes `title-article-norm`, `norm`, ...)."""

    heading_classes = {
        "oj-ti-section-1": 2,
        "oj-ti-section-2": 3,
        "title-division-1": 2,
        "title-division-2": 3,
        "title-annex-1": 2,
        "title-annex-2": 3,
        "title-gr-seq-level-1": 3,
        "title-gr-seq-level-2": 4,
    }
    article_classes = {"oj-ti-art", "title-article-norm"}
    article_subtitle_classes = {"oj-sti-art", "stitle-article-norm"}
    paragraph_classes = {"oj-normal", "norm", "title-doc-last", "title-doc-oj-reference"}
    note_classes = {"oj-note", "footnote"}
    # Marcadores ▼M1/►B do texto consolidado e cabeçalhos do índice de alterações.
    dropped_classes = {"modref", "arrow", "hd-toc-1", "hd-toc-2", "hd-toc-3", "separator", "separator-short"}

    def convert(self, content: bytes, *, source_url: str | None = None) -> MarkdownConversionResult:
        soup = BeautifulSoup(content, "html.parser")
        for unwanted in soup.find_all(["script", "style", "noscript"]):
            unwanted.decompose()

        publication_date_hint = self._publication_date_hint(soup)
        container = soup.select_one("div.eli-container") or soup.body or soup
        if soup.find("p", class_="reference") is not None:
            # Consolidado: a referência, o aviso e a lista "Alterado por" ficam fora do eli-container.
            container = soup.body or soup
        lines: list[str] = []
        warnings: list[str] = []
        skip_ids: set[int] = set()
        notes_started = False
        article_count = 0
        section_count = 0
        title_hint: str | None = None

        def emit(text: str = "") -> None:
            lines.append(text.rstrip())

        def process_element(element: Tag) -> None:
            nonlocal notes_started, article_count, section_count, title_hint
            if id(element) in skip_ids:
                return

            classes = set(element.get("class", []))
            if classes & self.dropped_classes:
                return
            if element.name == "p" and "title-doc-first" in classes:
                text = self._normalize_block_text(self._inline_text(element, source_url))
                if text and not title_hint:
                    title_hint = text
                    emit(f"# {text}")
                elif text:
                    emit(text)
                emit()
                return
            if element.name == "p" and classes & {"reference", "disclaimer"}:
                text = self._normalize_block_text(self._inline_text(element, source_url))
                if text:
                    emit(f"> {text}")
                    emit()
                return
            if element.name == "p" and "hd-modifiers" in classes:
                # "Alterado por:" / "Retificado por:" seguido de uma tabela de atos.
                text = self._normalize_block_text(self._inline_text(element, source_url))
                if text:
                    emit(f"**{text}**")
                    emit()
                table = next((item for item in element.next_siblings if isinstance(item, Tag)), None)
                if isinstance(table, Tag) and table.name == "table":
                    skip_ids.add(id(table))
                    for row in table.find_all("tr"):
                        cells = [
                            self._normalize_block_text(self._inline_text(cell, source_url))
                            for cell in row.find_all("td", recursive=False)
                            if not set(sum((p.get("class", []) for p in cell.find_all("p")), [])) & {"hd-toc-1", "hd-toc-2", "hd-toc-3"}
                        ]
                        cells = [cell for cell in cells if cell]
                        if cells:
                            emit("- " + " — ".join(cells))
                    emit()
                return
            if element.name == "div" and "eli-main-title" in classes:
                title_lines = [
                    self._normalize_block_text(self._inline_text(p, source_url))
                    for p in element.select("p.oj-doc-ti, p.title-doc-first, p.title-doc-last")
                ]
                title_lines = [line for line in title_lines if line]
                if title_lines:
                    title_hint = title_lines[0]
                    emit(f"# {title_lines[0]}")
                    emit()
                    for title_line in title_lines[1:]:
                        emit(title_line)
                        emit()
                return

            if element.name == "p" and classes & self.article_classes:
                number = self._heading_text(self._inline_text(element, source_url))
                title = ""
                sibling = next((item for item in element.next_siblings if isinstance(item, Tag)), None)
                while isinstance(sibling, Tag) and not sibling.get_text(strip=True):
                    sibling = next((item for item in sibling.next_siblings if isinstance(item, Tag)), None)
                if isinstance(sibling, Tag) and sibling.name == "div" and "eli-title" in set(sibling.get("class", [])):
                    # Consolidado: a epígrafe vem dentro de <div class="eli-title">.
                    inner = sibling.find("p", class_=lambda value: value in self.article_subtitle_classes)
                    if inner is not None:
                        title = self._heading_text(self._inline_text(inner, source_url))
                        skip_ids.add(id(sibling))
                elif isinstance(sibling, Tag) and self.article_subtitle_classes & set(sibling.get("class", [])):
                    title = self._heading_text(self._inline_text(sibling, source_url))
                    skip_ids.add(id(sibling))
                heading = f"###### {number}"
                if title:
                    heading = f"{heading} — {title}"
                emit(heading)
                emit()
                article_count += 1
                return

            if element.name == "p" and classes & self.article_subtitle_classes:
                text = self._normalize_block_text(self._inline_text(element, source_url))
                if text:
                    emit(f"##### {text}")
                    emit()
                return

            if element.name == "p" and classes.intersection(self.heading_classes):
                level = next(self.heading_classes[item] for item in classes if item in self.heading_classes)
                text = self._heading_text(self._inline_text(element, source_url))
                if text:
                    emit(f"{'#' * level} {text}")
                    emit()
                    section_count += 1
                return

            if element.name == "p" and classes & self.note_classes:
                text = self._normalize_block_text(self._inline_text(element, source_url))
                if not text:
                    return
                if not notes_started:
                    emit("---")
                    emit()
                    emit("## Notas")
                    emit()
                    notes_started = True
                note = self._format_note(text)
                emit(note)
                emit()
                return

            if element.name == "p" and classes & self.paragraph_classes:
                text = self._normalize_block_text(self._inline_text(element, source_url))
                if text:
                    emit(text)
                    emit()
                return

            if element.name == "p" and "oj-signatory" in classes:
                text = self._normalize_block_text(self._inline_text(element, source_url))
                if text:
                    emit(f"**{text}**")
                    emit()
                return

            if element.name == "div" and "grid-container" in classes:
                # Alínea do consolidado: marcador "a)" numa coluna e o texto noutra.
                marker_div = element.find("div", class_="grid-list-column-1")
                body_div = element.find("div", class_="grid-list-column-2")
                marker = self._normalize_block_text(marker_div.get_text(" ")) if marker_div else ""
                blocks = [child for child in (body_div.children if body_div else []) if isinstance(child, Tag)]
                if blocks and not self._has_block_children(blocks[0]):
                    text = self._normalize_block_text(self._inline_text(blocks[0], source_url))
                    emit(f"{marker} {text}".strip())
                    emit()
                    blocks = blocks[1:]
                elif marker:
                    emit(marker)
                    emit()
                for child in blocks:
                    process_element(child)
                return

            if element.name == "div" and "norm" in classes:
                # Número do consolidado: <span class="no-parag">1. </span> + texto, com
                # possíveis alíneas aninhadas.
                pending: list[str] = []

                def flush() -> None:
                    text = self._normalize_block_text("".join(pending))
                    if text:
                        emit(text)
                        emit()
                    pending.clear()

                for child in element.children:
                    if isinstance(child, Tag) and (child.name in {"p", "table"} or self._has_block_children(child) or "grid-container" in set(child.get("class", []))):
                        flush()
                        process_element(child)
                    else:
                        pending.append(self._inline_text(child, source_url))
                flush()
                return

            if element.name == "table":
                if element.find("p", class_="arrow") and element.find("p", class_="title-doc-first"):
                    # Cabeçalho "►B" do consolidado: repete o título que vem a seguir.
                    return
                for paragraph in self._table_to_markdown(element, source_url):
                    emit(paragraph)
                    emit()
                return

            if element.name == "hr" and "oj-note" in classes:
                return

            for child in element.children:
                if isinstance(child, Tag):
                    process_element(child)

        for child in container.children:
            if isinstance(child, Tag):
                process_element(child)

        if article_count == 0:
            # HTML simples dos atos antigos do JO: sem classes, artigos reconhecidos pelo texto.
            plain_lines, plain_articles, plain_sections, plain_title = self._plain_html(soup, source_url)
            if plain_articles:
                lines, article_count, section_count = plain_lines, plain_articles, plain_sections
                title_hint = title_hint or plain_title
        markdown = self._compact_blank_lines(lines).strip() + "\n"
        if article_count == 0:
            warnings.append("Não foram detetados artigos com as classes XHTML esperadas.")
        if not title_hint:
            warnings.append("Não foi detetado o título principal no XHTML.")
        return MarkdownConversionResult(
            markdown=markdown,
            title_hint=title_hint,
            publication_date_hint=publication_date_hint,
            article_count=article_count,
            section_count=section_count,
            warnings=warnings,
        )

    def _inline_text(self, node: Tag | NavigableString, source_url: str | None) -> str:
        if isinstance(node, NavigableString):
            return str(node).replace("\xa0", " ")
        classes = set(node.get("class", []))
        if "oj-note-tag" in classes:
            value = self._normalize_block_text(node.get_text(" ", strip=True))
            return f"[^{value}]" if value else ""
        if classes & {"oj-super", "superscript"}:
            value = self._normalize_block_text(node.get_text(" ", strip=True)).lower()
            if value == "o":
                return "º"
            if value == "a":
                return "ª"
            return f"^{value}^" if value else ""
        if node.name == "br":
            return " "

        content = "".join(self._inline_text(child, source_url) for child in node.children)
        if node.name == "a":
            text = self._normalize_block_text(content)
            href = node.get("href")
            if href and text:
                return f"[{text}]({urljoin(source_url or '', href)})"
            return text
        if node.name in {"strong", "b"} or classes & {"oj-bold", "boldface"}:
            text = self._normalize_block_text(content)
            return f"**{text}**" if text else ""
        if node.name in {"em", "i"} or classes & {"oj-italic", "italics"}:
            text = self._normalize_block_text(content)
            return f"*{text}*" if text else ""
        return content

    _PLAIN_ARTICLE = re.compile(r"^Artigo\s+\S+$", re.IGNORECASE)
    _PLAIN_DIVISIONS = (
        (re.compile(r"^(PARTE|LIVRO|T[ÍI]TULO|ANEXO)\b", re.IGNORECASE), "##"),
        (re.compile(r"^CAP[ÍI]TULO\b", re.IGNORECASE), "###"),
        (re.compile(r"^SEC[ÇC][ÃA]O\b", re.IGNORECASE), "####"),
    )

    def _plain_html(self, soup: BeautifulSoup, source_url: str | None) -> tuple[list[str], int, int, str | None]:
        """Conversão por texto para o HTML sem classes dos atos antigos do JO."""
        body = soup.body or soup
        blocks: list[tuple[str, str]] = []
        for element in body.find_all(["p", "table"]):
            # O HTML antigo aninha <p> dentro de <p>: conta só os parágrafos-folha.
            if element.find_parent("table") or (element.name == "p" and element.find("p")):
                continue
            if element.name == "table":
                for paragraph in self._table_to_markdown(element, source_url):
                    blocks.append(("table", paragraph))
                continue
            text = self._normalize_block_text(self._inline_text(element, source_url))
            if text and "legal_notice" not in text:
                blocks.append(("p", text))
        lines: list[str] = []
        articles = sections = 0
        title = None
        index = 0
        while index < len(blocks):
            kind, text = blocks[index]
            heading = None
            if kind == "p" and len(text) < 30 and self._PLAIN_ARTICLE.match(text):
                heading = "######"
                articles += 1
            elif kind == "p" and len(text) < 80:
                heading = next((prefix for pattern, prefix in self._PLAIN_DIVISIONS if pattern.match(text)), None)
                if heading:
                    sections += 1
            if heading:
                text = re.sub(r"(\d)\.o\b", r"\1.º", text)
                following = blocks[index + 1][1] if index + 1 < len(blocks) and blocks[index + 1][0] == "p" else ""
                if following and len(following) < 150 and not re.search(r"[.;:]$", following) and not re.match(r"^[\d(«]", following):
                    text = f"{text} — {following}"
                    index += 1
                lines.extend([f"{heading} {text}", ""])
            else:
                lines.extend([text, ""])
            index += 1
        return lines, articles, sections, title

    @staticmethod
    def _has_block_children(node: Tag) -> bool:
        return any(isinstance(child, Tag) and child.name in {"p", "div", "table"} for child in node.children)

    def _heading_text(self, text: str) -> str:
        return re.sub(r"\*+", "", self._normalize_block_text(text)).strip()

    @staticmethod
    def _normalize_block_text(text: str) -> str:
        text = text.replace("\xa0", " ")
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"\.\s+([ºª])", r".\1", text)
        text = re.sub(r"\(\s+(\[\^\d+\])\s+\)", r"(\1)", text)
        text = re.sub(r"\s+([,.;:!?])", r"\1", text)
        return text

    def _table_to_markdown(self, table: Tag, source_url: str | None) -> list[str]:
        rows: list[list[str]] = []
        for row in table.find_all("tr"):
            cells = [self._normalize_block_text(self._inline_text(cell, source_url)) for cell in row.find_all(["td", "th"], recursive=False)]
            if any(cells):
                rows.append(cells)
        if not rows:
            return []

        if all(len(row) == 2 for row in rows):
            paragraphs = []
            for first, second in rows:
                if first and second:
                    paragraphs.append(f"{first} {second}")
                elif first or second:
                    paragraphs.append(first or second)
            return paragraphs

        escaped_rows = [[cell.replace("|", "\\|") for cell in row] for row in rows]
        width = max(len(row) for row in escaped_rows)
        normalized = [row + [""] * (width - len(row)) for row in escaped_rows]
        markdown = ["| " + " | ".join(normalized[0]) + " |", "| " + " | ".join(["---"] * width) + " |"]
        markdown.extend("| " + " | ".join(row) + " |" for row in normalized[1:])
        return ["\n".join(markdown)]

    @staticmethod
    def _format_note(text: str) -> str:
        match = re.match(r"^\(\s*(\d+)\s*\)\s*(.*)$", text)
        if match:
            number, body = match.groups()
            return f"[^{number}]: {body}"
        return f"> {text}"

    @staticmethod
    def _compact_blank_lines(lines: Iterable[str]) -> str:
        result: list[str] = []
        previous_blank = True
        for line in lines:
            blank = not line.strip()
            if blank and previous_blank:
                continue
            result.append("" if blank else line)
            previous_blank = blank
        return "\n".join(result)

    @staticmethod
    def _publication_date_hint(soup: BeautifulSoup) -> str | None:
        element = soup.select_one("p.oj-hd-date")
        if not element:
            return None
        value = element.get_text(" ", strip=True).replace("\xa0", " ").strip()
        try:
            return datetime.strptime(value, "%d.%m.%Y").date().isoformat()
        except ValueError:
            return None


_CELEX_IN_URL = re.compile(r"/celex/([0-9A-Z()%]+)", re.IGNORECASE)


def consolidation_modifiers(content: bytes) -> list[tuple[str, str]]:
    """(CELEX, título) dos atos da lista "Alterado por" de um texto consolidado."""
    soup = BeautifulSoup(content, "html.parser")
    found: list[tuple[str, str]] = []
    for marker in soup.find_all("p", class_="hd-modifiers"):
        if not marker.get_text(strip=True).lower().startswith("alterad"):
            continue
        table = next((item for item in marker.next_siblings if isinstance(item, Tag)), None)
        if not isinstance(table, Tag) or table.name != "table":
            continue
        for row in table.find_all("tr"):
            link = row.find("a", href=_CELEX_IN_URL)
            if link is None:
                continue
            celex = _CELEX_IN_URL.search(link["href"]).group(1).replace("%28", "(").replace("%29", ")")
            # O título está numa das outras ligações/células da linha (a primeira é "►M1").
            candidates = [row.find("p", class_="title-fam-member")] + [
                anchor for anchor in row.find_all("a") if not anchor.get_text(strip=True).startswith(("►", "▼"))
            ]
            title_cell = next((item for item in candidates if item is not None and item.get_text(strip=True)), link)
            title = re.sub(r"\s+", " ", title_cell.get_text(" ", strip=True)).strip()
            if (celex, title) not in found:
                found.append((celex, title))
    return found
