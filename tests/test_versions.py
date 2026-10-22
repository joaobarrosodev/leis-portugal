from __future__ import annotations

from pathlib import Path
from typing import Any

from conftest import record_dict
from leis_portugal.infrastructure.markdown import read_markdown_record, render_markdown
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.validation import validate_repository
from leis_portugal.services.versions import apply_history, collect_history, render_version, version_at
from leis_portugal.sources.dre.consolidated import ConsolidatedEntry, parse_sitemap, render_fragment


def _fragment(version_id: str, fragment_id: str, type_id: int, title: str, epigraph: str, text: str, changes: list[str] | None = None) -> dict[str, Any]:
    return {
        "ConsolidacaoFragmento": {"Id": "1", "Name": title},
        "FragmentoVersao": {
            "Id": version_id, "FragmentoId": fragment_id, "TipoFragmentoId": type_id, "Tituo": title,
            "Epigrafe": epigraph, "Texto": text, "DataEntradaVigor": "1900-01-01T00:00:00",
        },
        "Nota": {"List": []},
        "AlteracoesList": {"List": changes or []},
    }


PREAMBLE = _fragment("100", "10", 15, "Diploma", "", "Decreto-Lei n.º 140/2009\rde 15 de Junho\rPreâmbulo.")
CHAPTER = _fragment("101", "11", 1, "Capítulo I", "Disposições gerais", "")
ART1 = _fragment("102", "12", 11, "Artigo 1.º", "Objeto", "O presente decreto-lei estabelece o regime.")
ART2_OLD = _fragment("103", "13", 11, "Artigo 2.º", "Definições", "a) Primeira;\rb) Segunda.")
ART2_NEW = _fragment(
    "203", "13", 11, "Artigo 2.º", "Definições", "a) Primeira, alterada;\nb) Segunda.",
    ['Alterado pelo/a Artigo 2.º do/a [L]<a href="/dr/detalhe/decreto-lei/90-2024-897548401">Decreto-Lei n.º 90/2024</a>[/L], em vigor a partir de 2024-11-23'],
)
ART2A = _fragment("204", "14", 11, "Artigo 2.º-A", "Novo", "Artigo aditado.")


class FakeClient:
    def __init__(self) -> None:
        self.dates: list[str] = []

    def consolidated_header(self, tipo: str, ano: int, frag_id: str) -> dict[str, Any]:
        return {"ConsolidadaConteudoDetalhe": {"DiplomaLegis": {
            "Id": "494543", "LinkSitemap": "/dr/detalhe/decreto-lei/140-2009-494543", "DataPublicacao": "2009-06-15T00:00:00Z",
        }}}

    def consolidated_timeline(self, legis_id: str, frag_id: str) -> list[dict[str, Any]]:
        return [
            {"IsDiplomaOriginal": False, "DiplomaLegisId": "897548401", "Title": "Decreto-Lei n.º 90/2024 - 1.ª Série",
             "DataPublicacao": "2024-11-22", "LinkSitemap": "/dr/detalhe/decreto-lei/90-2024-897548401",
             "ModificacaoList": {"List": [
                 {"DataEntradaVigor": "2024-11-23", "TipoModificacao": "Altera", "FragmentoDestinoModificacao": "Artigo 2.º"},
                 {"DataEntradaVigor": "2024-11-23", "TipoModificacao": "Adita", "FragmentoDestinoModificacao": "Artigo 2.º-A"},
             ]}},
            {"IsDiplomaOriginal": False, "DiplomaLegisId": "207272800", "Title": "Decreto-Lei n.º 11/2023 - 1.ª Série",
             "DataPublicacao": "2023-02-10", "ModificacaoList": {"List": [
                 {"DataEntradaVigor": "2023-02-11", "TipoModificacao": "Altera", "FragmentoDestinoModificacao": "Artigo 1.º"},
             ]}},
            {"IsDiplomaOriginal": True, "Title": "Decreto-Lei n.º 140/2009 - 1.ª Série", "ModificacaoList": {"List": []}},
        ]

    def consolidated_snapshot(self, tipo: str, ano: int, frag_id: str, legis_id: str, when: str, header: dict) -> list[dict[str, Any]]:
        self.dates.append(when)
        if when < "2024-11-23":
            # 2023-02-11: alteração sem mudança visível no texto (só efeitos).
            return [PREAMBLE, CHAPTER, ART1, ART2_OLD]
        return [PREAMBLE, CHAPTER, ART1, ART2_NEW, ART2A]


ENTRY = ConsolidatedEntry(
    url="https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2009-207631928",
    tipo="decreto-lei", ano=2009, frag_id="207631928", lastmod="2024-11-22",
)


def test_render_fragment_headings_text_and_changes():
    article = render_fragment(ART2_NEW)
    assert article["markdown"].startswith("###### Artigo 2.º — Definições\n\na) Primeira, alterada;\n\nb) Segunda.")
    assert "> Alterado pelo/a Artigo 2.º do/a [Decreto-Lei n.º 90/2024](https://diariodarepublica.pt/dr/detalhe/decreto-lei/90-2024-897548401)" in article["markdown"]
    assert render_fragment(CHAPTER)["markdown"] == "### Capítulo I — Disposições gerais"
    assert render_fragment(PREAMBLE)["markdown"].startswith("Decreto-Lei n.º 140/2009\n\nde 15 de Junho")


def test_collect_history_deduplicates_versions_and_fragments():
    client = FakeClient()
    result = collect_history(ENTRY, client, today="2026-10-22")
    history = result.history
    assert client.dates == ["2009-06-15", "2023-02-11", "2024-11-23"]
    assert [version["date"] for version in history["versions"]] == ["2009-06-15", "2024-11-23"]
    # A alteração de 2023 não mudou o texto: o ato fica associado à versão anterior.
    assert history["versions"][0]["acts"] == []
    assert [(act["title"], act["date"]) for act in history["versions"][0]["acts_without_text_change"]] == [("Decreto-Lei n.º 11/2023", "2023-02-11")]
    assert history["versions"][1]["changes"] == ["Altera Artigo 2.º", "Adita Artigo 2.º-A"]
    assert set(history["fragments"]) == {"100", "101", "102", "103", "203", "204"}
    original = render_version(history, version_at(history, "2010-01-01"), title="Decreto-Lei n.º 140/2009")
    current = render_version(history, version_at(history, "2026-10-22"), title="Decreto-Lei n.º 140/2009")
    assert "a) Primeira;" in original and "Artigo 2.º-A" not in original
    assert "a) Primeira, alterada;" in current and "###### Artigo 2.º-A — Novo" in current
    assert version_at(history, "2000-01-01") is None


def test_apply_history_updates_record_and_writes_versions(repo_root: Path):
    record = repo_root / "data/portugal/decretos-leis/2009/decreto-lei-140-2009.md"
    record.parent.mkdir(parents=True)
    metadata = record_dict(
        "pt:dre:494543:por",
        title="Decreto-Lei n.º 140/2009",
        official_number="140/2009",
        publication_date="2009-06-15",
        identifiers={"dre": "494543", "dre_path": "/dr/detalhe/decreto-lei/140-2009-494543", "eli": None},
        version={"kind": "consolidated", "label": "x", "language": "por", "consolidation_date": "2024-11-22"},
        source={"id": "dre", "name": "Diário da República Eletrónico", "official_url": "https://diariodarepublica.pt/x", "retrieved_at": "2026-10-21T00:00:00Z", "retrieval_method": "x"},
        integrity={"source_sha256": "0" * 64, "source_sha256_scope": "imported_derived_markdown"},
        subjects=["Património Cultural"],
        relationships=[{"type": "cites", "target": "eli:http://data.dre.pt/eli/lei/107/2001/09/08/p/dre", "label": None}],
    )
    record.write_text(render_markdown(metadata, "# Texto antigo"), encoding="utf-8")
    acervo = Acervo(repo_root)

    result = collect_history(ENTRY, FakeClient(), today="2026-10-22")
    path, action = apply_history(result, acervo=acervo, dre_source=None, today="2026-10-22")
    assert (path.resolve(), action) == (record.resolve(), "written")
    updated, body = read_markdown_record(record)
    assert updated["source"]["id"] == "dre"
    assert updated["version"]["consolidation_date"] == "2024-11-23"
    assert updated["version_history"]["count"] == 2
    assert updated["version_history"]["versions"][1]["amending"] == "pt:dre:897548401:por"
    assert updated["subjects"] == ["Património Cultural"]
    relations = {(item["type"], item["target"]) for item in updated["relationships"]}
    assert ("amended_by", "pt:dre:897548401:por") in relations
    assert ("cites", "eli:http://data.dre.pt/eli/lei/107/2001/09/08/p/dre") in relations
    assert updated["article_structure"]["article_count"] == 3
    assert "a) Primeira, alterada;" in body
    stored = acervo.read_history(record)
    assert stored["source_lastmod"] == "2024-11-22"
    assert validate_repository(acervo) == []

    again = apply_history(collect_history(ENTRY, FakeClient(), today="2026-10-22"), acervo=acervo, dre_source=None, today="2026-10-22")
    assert again[1] == "unchanged"


def test_parse_sitemap():
    xml = b"""<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>https://diariodarepublica.pt/dr/legislacao-consolidada/lei/2009-34546475</loc><lastmod>2026-05-01</lastmod></url>
    <url><loc>https://diariodarepublica.pt/dr/outra-coisa</loc></url></urlset>"""
    assert parse_sitemap(xml) == [
        ConsolidatedEntry(url="https://diariodarepublica.pt/dr/legislacao-consolidada/lei/2009-34546475", tipo="lei", ano=2009, frag_id="34546475", lastmod="2026-05-01")
    ]


def test_empty_snapshot_on_one_date_is_skipped_not_fatal():
    class GapClient(FakeClient):
        def consolidated_snapshot(self, tipo, ano, frag_id, legis_id, when, header):
            return [] if when == "2023-02-11" else super().consolidated_snapshot(tipo, ano, frag_id, legis_id, when, header)

    history = collect_history(ENTRY, GapClient(), today="2026-10-22").history
    assert [version["date"] for version in history["versions"]] == ["2009-06-15", "2024-11-23"]
    assert history["unavailable_dates"] == ["2023-02-11"]


def test_no_text_on_any_date_is_a_failure():
    import pytest

    from leis_portugal.errors import SourceError

    class EmptyClient(FakeClient):
        def consolidated_snapshot(self, *args):
            return []

    with pytest.raises(SourceError, match="vazio em todas as datas"):
        collect_history(ENTRY, EmptyClient(), today="2026-10-22")
