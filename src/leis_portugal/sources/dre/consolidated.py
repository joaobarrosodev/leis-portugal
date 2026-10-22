"""Legislação consolidada do DRE: sitemap e conversão de fragmentos para Markdown.

O texto consolidado vem dividido em fragmentos (artigos, capítulos, anexos...).
Cada fragmento tem uma identidade estável (`FragmentoId`) e cada versão dele um id
próprio (`FragmentoVersao.Id`), o que permite guardar cada versão uma só vez.
"""

from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass
from typing import Any

from leis_portugal.domain.identifiers import clean_date
from leis_portugal.sources.dre.client import DreApiError
from leis_portugal.sources.dre.constants import DRE_BASE_URL
from leis_portugal.sources.dre.html import DreHtmlConverter


_CONSOLIDATED_REF = re.compile(r"/dr/legislacao-consolidada/([^/]+)/(\d{4})-(\d+)")
_TAG = re.compile(r"<[^>]+>")
_LINK = re.compile(r"<a\b[^>]*href=\"?([^\"\s>]+)\"?[^>]*>(.*?)</a>", re.IGNORECASE | re.DOTALL)

# TipoFragmentoId do DRE -> nível de cabeçalho Markdown (None: corpo de texto).
FRAGMENT_LEVELS: dict[int, int | None] = {
    4: 2, 12: 2, 13: 2, 5: 2, 14: 2,  # Parte, Livro, Título, Subtítulo, Anexo
    1: 3, 10: 3,  # Capítulo, Subcapítulo
    8: 4,  # Secção
    3: 5, 9: 5, 6: 5,  # Subsecção, Divisão, Subdivisão
    11: 6, 2: 6,  # Artigo, Base
    15: None, 7: None, 16: None, 17: None, 18: None, 0: None,  # preâmbulo, assinatura, números, alíneas
}
ARTICLE_TYPES = {11, 2}
DIVISION_LEVELS = {2, 3, 4, 5}


@dataclass(frozen=True)
class ConsolidatedEntry:
    url: str
    tipo: str
    ano: int
    frag_id: str
    lastmod: str | None = None


def parse_consolidated_ref(url: str) -> tuple[str, int, str]:
    """`…/dr/legislacao-consolidada/decreto-lei/2009-207631928` -> (`decreto-lei`, 2009, `207631928`)."""
    match = _CONSOLIDATED_REF.search(url or "")
    if not match:
        raise DreApiError(f"Ligação de legislação consolidada inválida: {url!r}")
    return match.group(1), int(match.group(2)), match.group(3)


def consolidated_entry(url: str, lastmod: str | None = None) -> ConsolidatedEntry:
    tipo, ano, frag_id = parse_consolidated_ref(url)
    return ConsolidatedEntry(url=url, tipo=tipo, ano=ano, frag_id=frag_id, lastmod=lastmod)


def parse_sitemap(xml_bytes: bytes) -> list[ConsolidatedEntry]:
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    entries = []
    for node in ElementTree.fromstring(xml_bytes).findall("s:url", namespace):
        url = (node.findtext("s:loc", default="", namespaces=namespace) or "").strip()
        lastmod = (node.findtext("s:lastmod", default="", namespaces=namespace) or "").strip()[:10] or None
        if _CONSOLIDATED_REF.search(url):
            entries.append(consolidated_entry(url, lastmod))
    return entries


def _plain(value: str | None) -> str:
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub("", value or ""))).strip()


def _markdown_links(value: str) -> str:
    """HTML inline do DRE (com marcadores [L]…[/L]) -> Markdown com ligações absolutas."""
    text = (value or "").replace("[L]", "").replace("[/L]", "")
    text = _LINK.sub(
        lambda m: f"[{_plain(m.group(2))}]({DRE_BASE_URL + m.group(1) if m.group(1).startswith('/') else m.group(1)})", text
    )
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub("", text))).strip()


def _body_text(value: str) -> str:
    text = (value or "").replace("\x00", "")
    if not text.strip():
        return ""
    if re.search(r"<(p|table|br|div|ul|ol)\b", text, re.IGNORECASE):
        return DreHtmlConverter().convert(text).markdown
    lines = [html.unescape(line).strip() for line in re.split(r"\r\n|\r|\n", text)]
    return "\n\n".join(line for line in lines if line)


def render_fragment(entry: dict[str, Any]) -> dict[str, Any]:
    """Uma entrada de `LegConsBase` -> versão de fragmento com Markdown pronto."""
    version = entry.get("FragmentoVersao") or {}
    fragment = entry.get("ConsolidacaoFragmento") or {}
    type_id = int(version.get("TipoFragmentoId") or 0)
    level = FRAGMENT_LEVELS.get(type_id)
    title = _plain(version.get("Tituo") or fragment.get("Name"))
    epigraph = _plain(version.get("Epigrafe"))
    heading = f"{title} — {epigraph}" if title and epigraph else title
    parts: list[str] = []
    if level and heading:
        parts.append(f"{'#' * level} {heading}")
    body = _body_text(version.get("Texto") or "")
    if body:
        parts.append(body)
    for note in (entry.get("Nota") or {}).get("List") or []:
        text = _markdown_links(note if isinstance(note, str) else json.dumps(note, ensure_ascii=False))
        if text:
            parts.append(f"> Nota: {text}")
    changes = []
    for change in (entry.get("AlteracoesList") or {}).get("List") or []:
        text = _markdown_links(change if isinstance(change, str) else json.dumps(change, ensure_ascii=False))
        if text:
            changes.append(text)
            parts.append(f"> {text}")
    return {
        "fragment_id": str(version.get("FragmentoId") or fragment.get("Id") or ""),
        "type": type_id,
        "heading": heading or None,
        "in_force_from": clean_date(version.get("DataEntradaVigor")),
        "changed_by": changes,
        "markdown": "\n\n".join(parts),
    }
