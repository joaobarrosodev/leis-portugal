"""Sitemaps do DRE: a lista pública de todos os documentos publicados, por tipo.

O índice (`sitemap.xml`) aponta para ficheiros `<família>-sitemap-<n>.xml`; cada um
lista até 50 000 páginas `/dr/detalhe/<tipo>/<chave>`, das duas séries. A família
nem sempre é o tipo (p. ex. `contrato-publico` lista anúncios), por isso o tipo de
cada documento lê-se no próprio caminho.

Alguns ficheiros misturam UTF-8 e Latin-1 (`n.ª` em Latin-1): cada linha que não é
UTF-8 válido é lida como Latin-1.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


SITEMAP_INDEX = "https://files.diariodarepublica.pt/sitemap/sitemap.xml"

_FILE = re.compile(r"<loc>\s*(https://[^<\s]+/([a-z0-9-]+?)-sitemap-[0-9]+\.xml)\s*</loc>")
_DOCUMENT = re.compile(r"<loc>\s*https://diariodarepublica\.pt(/dr/detalhe/([a-z0-9-]+)/(?:[^<\s]*?[-/])?([0-9]+))\s*</loc>")


@dataclass(frozen=True)
class SitemapFile:
    url: str
    family: str


@dataclass(frozen=True)
class SitemapDocument:
    ref: str
    tipo: str
    dre_id: str


def _text(xml: bytes) -> str:
    try:
        return xml.decode("utf-8")
    except UnicodeDecodeError:
        lines = []
        for line in xml.split(b"\n"):
            try:
                lines.append(line.decode("utf-8"))
            except UnicodeDecodeError:
                lines.append(line.decode("latin-1"))
        return "\n".join(lines)


def parse_index(xml: bytes) -> list[SitemapFile]:
    """Ficheiros de sitemap listados no índice."""
    return [SitemapFile(url=url, family=family) for url, family in _FILE.findall(_text(xml))]


def parse_documents(xml: bytes) -> list[SitemapDocument]:
    """Páginas de detalhe de um ficheiro de sitemap (as outras páginas são ignoradas)."""
    return [SitemapDocument(ref=ref, tipo=tipo, dre_id=dre_id) for ref, tipo, dre_id in _DOCUMENT.findall(_text(xml))]
