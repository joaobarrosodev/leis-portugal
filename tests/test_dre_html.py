from __future__ import annotations

import json

from conftest import FIXTURES
from leis_portugal.sources.dre.html import DreHtmlConverter


def _converted():
    detail = json.loads((FIXTURES / "dre" / "detail_decreto_lei.json").read_text(encoding="utf-8"))
    return DreHtmlConverter().convert(detail["TextoFormatado"])


def test_title_divisions_and_articles_with_epigraphs():
    markdown = _converted().markdown
    assert markdown.startswith("# Decreto-Lei n.º 202/2026\n\nde 20 de outubro")
    assert "### CAPÍTULO I — Disposições gerais" in markdown
    assert "###### Artigo 1.º — Objeto" in markdown
    assert "###### Artigo 3.º — Entrada em vigor" in markdown


def test_quoted_articles_are_not_headings():
    markdown = _converted().markdown
    assert "###### Artigo 10.º" not in markdown
    assert "###### Artigo 11.º" not in markdown
    assert "«Artigo 10.º" in markdown
    assert markdown.count("###### Artigo") == 3


def test_links_become_absolute_and_are_recorded_as_citations():
    conversion = _converted()
    assert "[Decreto-Lei n.º 40-A/2026](https://diariodarepublica.pt/dr/detalhe/decreto-lei/40-a-2026-1050874165)" in conversion.markdown
    assert conversion.cited_dre_ids == ["1050874165"]


def test_tables_are_converted_and_pipes_escaped():
    markdown = _converted().markdown
    assert "| Coluna A | Coluna B |\n| --- | --- |\n| 1 | 2 \\| 3 |" in markdown
