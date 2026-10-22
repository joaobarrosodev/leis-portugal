"""Conversão do HTML `TextoFormatado` do Diário da República para Markdown.

O DRE marca a estrutura apenas com classes de parágrafo (`paragraph-center`,
`paragraph-bold-center-14px`, ...). As divisões e os artigos são reconhecidos pelo
texto e a epígrafe que os segue é unida ao cabeçalho, no formato
`###### Artigo 1.º — Objeto`, igual ao dos registos importados do legalize-pt.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urljoin

from bs4 import BeautifulSoup, NavigableString, Tag

from leis_portugal.sources.dre.constants import DRE_BASE_URL


_ARTICLE = re.compile(r"^Artigo\s+\S+", re.IGNORECASE)
_DIVISIONS = (
    (re.compile(r"^(PARTE|LIVRO|T[ÍI]TULO|ANEXO)\b", re.IGNORECASE), "##"),
    (re.compile(r"^CAP[ÍI]TULO\b", re.IGNORECASE), "###"),
    (re.compile(r"^SEC[ÇC][ÃA]O\b", re.IGNORECASE), "####"),
    (re.compile(r"^(SUBSEC[ÇC][ÃA]O|DIVIS[ÃA]O)\b", re.IGNORECASE), "#####"),
)
_HEADING_CLASSES = {"paragraph-center", "paragraph-bold-center", "paragraph-bold-center-14px"}
_EPIGRAPH_CLASSES = {"paragraph-bold-center-14px", "paragraph-bold-center"}
_TITLE_CLASS = "paragraph-title-bold-center-18px"
_DRE_DOCUMENT_LINK = re.compile(r"/dr/detalhe/[^/]+/[^/?#]*?-([0-9]+)(?:[/?#]|$)")
_BLOCK_TAGS = {"p", "table", "ul", "ol", "img", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre"}


@dataclass
class Conversion:
    markdown: str
    cited_dre_ids: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _classes(tag: Tag) -> set[str]:
    return set(tag.get("class") or [])


def _escape_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", "<br>").strip()


class DreHtmlConverter:
    def __init__(self, base_url: str = DRE_BASE_URL) -> None:
        self.base_url = base_url

    def convert(self, html: str) -> Conversion:
        soup = BeautifulSoup(html or "", "html.parser")
        self._cited: list[str] = []
        blocks = [block for block in self._blocks(soup) if block[1].strip()]
        lines: list[str] = []
        index = 0
        # Profundidade de citação «…»: artigos transcritos num ato de alteração
        # não são artigos do próprio diploma.
        quote_depth = 0
        while index < len(blocks):
            kind, text, classes = blocks[index]
            if kind == "p" and _TITLE_CLASS in classes and not lines:
                lines.append(f"# {text.strip()}")
                index += 1
                continue
            quoted = quote_depth > 0 or text.lstrip().startswith("«")
            heading = (
                self._heading_prefix(text) if kind == "p" and classes & _HEADING_CLASSES and not quoted else None
            )
            quote_depth = max(0, quote_depth + text.count("«") - text.count("»"))
            if heading:
                title = re.sub(r"\s+", " ", text).strip()
                following = blocks[index + 1] if index + 1 < len(blocks) else None
                if (
                    following
                    and following[0] == "p"
                    and following[2] & _EPIGRAPH_CLASSES
                    and not self._heading_prefix(following[1])
                ):
                    epigraph = re.sub(r"\s+", " ", following[1]).strip()
                    title = f"{title} — {epigraph}"
                    index += 1
                lines.append(f"{heading} {title}")
            else:
                lines.append(text.strip())
            index += 1
        markdown = "\n\n".join(lines)
        markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()
        return Conversion(markdown=markdown, cited_dre_ids=list(dict.fromkeys(self._cited)))

    @staticmethod
    def _heading_prefix(text: str) -> str | None:
        stripped = text.strip()
        if _ARTICLE.match(stripped) and len(stripped) < 40:
            return "######"
        for pattern, prefix in _DIVISIONS:
            if pattern.match(stripped) and len(stripped) < 80:
                return prefix
        return None

    def _blocks(self, node: Tag):
        """Percorre o documento e devolve (tipo, texto Markdown, classes) por bloco."""
        for child in node.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    yield ("text", text, set())
                continue
            if not isinstance(child, Tag):
                continue
            name = child.name.lower()
            if name == "table":
                yield ("table", self._table(child), set())
            elif name in {"ul", "ol"}:
                items = [self._inline(item).strip() for item in child.find_all("li", recursive=False)]
                marker = "1." if name == "ol" else "-"
                yield ("list", "\n".join(f"{marker} {item}" for item in items if item), set())
            elif name == "img":
                yield ("img", self._image(child), set())
            elif name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                yield ("p", self._inline(child), {"paragraph-center"})
            elif name == "p" or not any(isinstance(item, Tag) and item.name in _BLOCK_TAGS for item in child.descendants):
                yield ("p", self._inline(child), _classes(child))
            else:
                yield from self._blocks(child)

    def _image(self, tag: Tag) -> str:
        src = (tag.get("src") or "").strip()
        if not src:
            return ""
        return f"![{(tag.get('alt') or '').strip()}]({urljoin(self.base_url + '/', src)})"

    def _inline(self, node: Tag) -> str:
        parts: list[str] = []
        for child in node.children:
            if isinstance(child, NavigableString):
                parts.append(re.sub(r"[ \t\r\n]+", " ", str(child)))
                continue
            if not isinstance(child, Tag):
                continue
            name = child.name.lower()
            if name == "br":
                parts.append("\n")
            elif name == "a":
                text = self._inline(child).strip()
                href = (child.get("href") or "").strip()
                match = _DRE_DOCUMENT_LINK.search(href)
                if match:
                    self._cited.append(match.group(1))
                if href and text and not href.startswith(("javascript:", "#")):
                    parts.append(f"[{text}]({urljoin(self.base_url + '/', href)})")
                else:
                    parts.append(text)
            elif name in {"b", "strong"}:
                text = self._inline(child).strip()
                parts.append(f"**{text}**" if text else "")
            elif name in {"i", "em"}:
                text = self._inline(child).strip()
                parts.append(f"*{text}*" if text else "")
            elif name == "img":
                parts.append(self._image(child))
            elif name == "table":
                parts.append("\n\n" + self._table(child) + "\n\n")
            else:
                parts.append(self._inline(child))
        text = "".join(parts)
        text = re.sub(r" *\n *", "\n", text)
        return text.strip()

    def _table(self, table: Tag) -> str:
        rows: list[list[str]] = []
        for row in table.find_all("tr"):
            cells = [_escape_cell(self._inline(cell)) for cell in row.find_all(["td", "th"], recursive=False)]
            if cells:
                rows.append(cells)
        if not rows:
            return ""
        width = max(len(row) for row in rows)
        rows = [row + [""] * (width - len(row)) for row in rows]
        header = "| " + " | ".join(rows[0]) + " |"
        separator = "| " + " | ".join(["---"] * width) + " |"
        body = ["| " + " | ".join(row) + " |" for row in rows[1:]]
        return "\n".join([header, separator, *body])
