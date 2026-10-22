"""Estrutura de um texto em Markdown: artigos e divisões."""

from __future__ import annotations

import re

from leis_portugal.domain.record import ArticleStructure


_ARTICLE_HEADING = re.compile(r"^#{1,6}\s+Artigo\b", re.MULTILINE)
_DIVISION_HEADING = re.compile(
    r"^#{2,5}\s+(?:LIVRO|PARTE|T[ÍI]TULO|CAP[ÍI]TULO|SEC[ÇC][ÃA]O|SUBSEC[ÇC][ÃA]O|DIVIS[ÃA]O)\b",
    re.MULTILINE | re.IGNORECASE,
)


def article_structure(markdown: str, *, method: str) -> ArticleStructure:
    return ArticleStructure(
        article_count=len(_ARTICLE_HEADING.findall(markdown)),
        section_count=len(_DIVISION_HEADING.findall(markdown)),
        extraction_method=method,
    )


_HEADING = re.compile(r"^(#{2,6})\s+(.+)$")


def split_fragments(markdown: str) -> list[dict[str, str | int | None]]:
    """Divide um texto em fragmentos: um por cabeçalho (## a ######), mais o texto
    antes do primeiro cabeçalho. O título `# …` não faz parte dos fragmentos."""
    fragments: list[dict[str, str | int | None]] = []
    current: list[str] = []
    heading: str | None = None
    level: int | None = None

    def flush() -> None:
        text = "\n".join(current).strip()
        if text:
            fragments.append({"heading": heading, "level": level, "markdown": text})

    for line in markdown.splitlines():
        if line.startswith("# "):
            continue
        match = _HEADING.match(line)
        if match:
            flush()
            current, heading, level = [line], match.group(2).strip(), len(match.group(1))
        else:
            current.append(line)
    flush()
    return fragments
