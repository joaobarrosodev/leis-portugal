from __future__ import annotations

from conftest import REPOSITORY_ROOT
from leis_portugal.domain.identifiers import clean_date
from leis_portugal.domain.record import LegalRecord, Relationship, merge_relationships
from leis_portugal.domain.relations import celex_from_eu_eli, citation_target
from leis_portugal.infrastructure.config import load_document_types
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.sources.dre.mapper import legal_status_from_dre


ROOT = REPOSITORY_ROOT
TYPES = load_document_types(ROOT)


def path_for(metadata, *, disambiguate=False):
    record = LegalRecord.from_dict({
        "id": "pt:dre:1:por", "title": "x", "jurisdiction": "regional" if metadata.get("territory") else "portugal",
        "source": {"id": "dre", "name": "x", "official_url": "https://x"}, "integrity": {"source_sha256": "0" * 64},
        "provenance": {"collector": "x", "generated_by": "x"}, "reuse": {"status": "permitted", "attribution": "x"},
        **metadata,
    })
    acervo = Acervo(ROOT)
    return acervo.path_for(record, disambiguate=disambiguate).relative_to(acervo.root)


def test_aliases_normalize_spelling_variants():
    assert TYPES.resolve("declaracao-rectificacao").slug == "declaracao-retificacao"
    assert TYPES.resolve("declaracao-retificacao").slug == "declaracao-retificacao"
    assert TYPES.resolve("acordo-colectivo-trabalho").slug == "acordo-coletivo-trabalho"
    regional = TYPES.resolve("resolucao-assembleia-legislativa-regiao-autonoma-acores")
    assert regional.slug == "resolucao-assembleia-legislativa-regional"


def test_unknown_type_goes_to_outros():
    unknown = TYPES.resolve("tipo-inexistente")
    assert unknown.path == "outros/tipo-inexistente"
    assert not unknown.known


def test_territory_detection():
    assert TYPES.territory_for(document_type="decreto-legislativo-regional", official_number="1/2020/M") == "madeira"
    assert (
        TYPES.territory_for(
            document_type="resolucao",
            official_number="36/2026",
            issuer="Região Autónoma dos Açores - Assembleia Legislativa",
        )
        == "acores"
    )
    assert TYPES.territory_for(document_type="lei", official_number="29/2026", issuer="Assembleia da República") is None


def test_eu_eli_to_celex():
    assert celex_from_eu_eli("http://data.europa.eu/eli/reg/2013/1408/oj") == "32013R1408"
    assert celex_from_eu_eli("http://data.europa.eu/eli/dir/2016/798/oj") == "32016L0798"
    assert citation_target("http://data.dre.pt/eli/lei/107/2001/09/08/p/dre").startswith("eli:")


def test_textual_reference():
    text = "Altera os artigos 10.º e 11.º do Decreto-Lei n.º 40-A/2026, de 13 de fevereiro"
    assert TYPES.textual_reference(text) == "pt:numero:decreto-lei:40-A/2026"
    assert TYPES.textual_reference("Rectifica a Declaração de Rectificação n.º 5/2009") == (
        "pt:numero:declaracao-retificacao:5/2009"
    )
    assert TYPES.textual_reference("sem referências") is None


def test_paths_separate_series_and_regions():
    base = {
        "document_type": "portaria",
        "official_number": "1/2009",
        "publication_date": "2009-01-02",
        "identifiers": {"dre": "396946"},
    }
    assert path_for(base).as_posix() == "data/portugal/portarias/2009/portaria-1-2009.md"
    serie_ii = {**base, "publication": {"series": "II"}}
    assert path_for(serie_ii).as_posix() == "data/portugal/serie-ii/portarias/2009/portaria-1-2009.md"
    regional = {**base, "document_type": "decreto-legislativo-regional", "official_number": "1/2020/M", "territory": "madeira"}
    assert path_for(regional).as_posix().startswith(
        "data/regional/madeira/decretos-legislativos-regionais/2009/"
    )
    assert path_for(base, disambiguate=True).name == "portaria-1-2009-396946.md"


def test_dates_and_status():
    assert clean_date("1900-01-01") is None
    assert clean_date("2026-10-20T00:00:00") == "2026-10-20"
    assert legal_status_from_dre("VIGENTE") == "in_force"
    assert legal_status_from_dre("NAO_VIGENTE") == "not_in_force"
    assert legal_status_from_dre("") == "unknown"


def test_merge_relationships_is_stable_and_deduplicated():
    a = [Relationship(type="cites", target="pt:dre:2:por")]
    b = [
        Relationship(type="cites", target="pt:dre:2:por", label="com etiqueta"),
        Relationship(type="amended_by", target="pt:dre:9:por", date="2020-01-01"),
    ]
    merged = merge_relationships(a, b)
    assert [item.type for item in merged] == ["amended_by", "cites"]
    assert merged[1].label == "com etiqueta"
    assert merge_relationships(b, a) == merged
