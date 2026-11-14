from __future__ import annotations

import json
from datetime import date
from typing import Any

from leis_portugal.infrastructure.markdown import read_markdown_record
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services import eu_translation
from leis_portugal.services.validation import validate_repository
from leis_portugal.sources.eurlex.source import EurLexSource
from test_eurlex import FakeCellar, _ingestion


class EnglishOnlyCellar(FakeCellar):
    """Como o FakeCellar, mas sem expressão portuguesa (como os atos anteriores à adesão)."""

    def sparql(self, query: str) -> list[dict[str, Any]]:
        if "expression_belongs_to_work" in query and "language/POR" in query:
            self.queries.append(query)
            return []
        return super().sparql(query)


TRANSLATION = """título: Diretiva (UE) 2022/2555 do Parlamento Europeu e do Conselho, de 14 de dezembro de 2022
resumo: relativa a medidas de cibersegurança
---
# Diretiva (UE) 2022/2555

###### Artigo 1.º — Objeto

1. A presente diretiva estabelece medidas.
"""


def _prepare(repo_root) -> dict:
    cache = repo_root / eu_translation.CACHE
    summary = eu_translation.prepare(["32022L2555"], cache, source_factory=lambda: EurLexSource(EnglishOnlyCellar(consolidated=None)))
    assert (summary.prepared, summary.failures) == ({"eng": 1}, [])
    return json.loads((cache / "32022L2555.json").read_text(encoding="utf-8"))


def test_prepare_falls_back_to_english_and_keeps_the_eurlex_link(repo_root):
    data = _prepare(repo_root)
    assert data["language"] == "eng"
    assert data["original_url"] == "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32022L2555"
    assert data["record"]["id"] == "eu:celex:32022L2555:eng"
    # Já preparado: não se volta a descarregar.
    again = eu_translation.prepare(["32022L2555"], repo_root / eu_translation.CACHE, source_factory=lambda: EurLexSource(EnglishOnlyCellar()))
    assert again.skipped == 1


def test_assemble_writes_a_marked_translation_with_the_english_source(repo_root):
    _prepare(repo_root)
    cache = repo_root / eu_translation.CACHE
    (cache / "32022L2555.pt.md").write_text(TRANSLATION, encoding="utf-8")
    acervo = Acervo(repo_root)
    summary = eu_translation.assemble(acervo, cache, translator="Claude (teste)", today=date(2026, 11, 14))
    assert (summary.written, summary.failures, summary.missing) == (1, [], [])
    [path] = (repo_root / "data" / "european_union").rglob("*.md")
    metadata, body = read_markdown_record(path)
    assert metadata["id"] == "eu:celex:32022L2555:por"
    assert metadata["language"] == "por"
    assert metadata["title"].startswith("Diretiva (UE) 2022/2555 do Parlamento Europeu")
    assert metadata["version"] == {
        "kind": "translation",
        "label": "Tradução não oficial para português europeu do texto em inglês (EUR-Lex); sem valor jurídico",
        "language": "por",
        "consolidation_date": None,
    }
    url = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32022L2555"
    assert metadata["source"]["official_url"] == url
    assert metadata["notes"][0] == f"Traduzido do texto em inglês publicado no EUR-Lex: {url}"
    assert "Tradução automática por Claude (teste), em 2026-11-14" in metadata["notes"][2]
    assert body.strip().startswith("# Diretiva (UE) 2022/2555\n\n> Tradução não oficial para português europeu do texto em inglês.")
    assert f"[32022L2555]({url})" in body
    assert "###### Artigo 1.º — Objeto" in body
    assert validate_repository(acervo) == []


def test_official_portuguese_text_replaces_the_translation(repo_root):
    _prepare(repo_root)
    cache = repo_root / eu_translation.CACHE
    (cache / "32022L2555.pt.md").write_text(TRANSLATION, encoding="utf-8")
    eu_translation.assemble(Acervo(repo_root), cache, translator="Claude (teste)")
    result = _ingestion(repo_root, consolidated=False).ingest("32022L2555")
    metadata, _body = read_markdown_record(result.path)
    assert metadata["version"]["kind"] == "original"


def test_translation_without_header_is_refused(repo_root):
    _prepare(repo_root)
    cache = repo_root / eu_translation.CACHE
    (cache / "32022L2555.pt.md").write_text("# Só o corpo\n", encoding="utf-8")
    summary = eu_translation.assemble(Acervo(repo_root), cache, translator="Claude (teste)")
    assert summary.written == 0 and summary.failures[0]["celex"] == "32022L2555"


def test_pending_celex_reads_only_the_acts_without_portuguese(repo_root):
    path = repo_root / "reports" / "eurlex_em_vigor_failures.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '{"celex": "31983D0245", "motivo": "sem_texto_na_fonte"}\n{"celex": "31990R0001", "motivo": "armazenamento"}\n', encoding="utf-8"
    )
    assert eu_translation.pending_celex(repo_root) == ["31983D0245"]
