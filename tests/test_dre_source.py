from __future__ import annotations

import json
from datetime import date
from typing import Any

import pytest

from conftest import FIXTURES
from leis_portugal.infrastructure.markdown import read_markdown_record, render_markdown
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.dre import DreIngestion
from leis_portugal.services.validation import validate_repository
from leis_portugal.sources.dre.client import DreApiError, DreClient, split_sitemap_ref
from leis_portugal.sources.dre.source import DreSource


def _fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / "dre" / name).read_text(encoding="utf-8"))


class FakeSession:
    """Substitui a sessão HTTP: devolve respostas gravadas por ação."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def call(self, action: str, variables: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((action, variables))
        if action == "published_detail":
            return {"DetalheConteudo": _fixture("detail_decreto_lei.json")}
        if action == "associations":
            return _fixture(f"associations_{variables['TipoAssociacaoId']}.json")
        if action == "aj_element_type":
            return {"IsNullElementType": False, "DiplomaLegisIdOut": "1183482554"}
        if action == "aj_data":
            return _fixture("aj_data.json")
        if action == "documents_by_date":
            return _fixture("documents_by_date.json")
        raise AssertionError(action)


REF = "/dr/detalhe/decreto-lei/202-2026-1183482554"


def _service(repo_root, session: FakeSession | None = None) -> DreIngestion:
    acervo = Acervo(repo_root)
    return DreIngestion(acervo, DreSource(acervo.types, DreClient(session or FakeSession())))


def test_split_sitemap_ref():
    assert split_sitemap_ref(REF) == ("decreto-lei", "202-2026-1183482554")
    with pytest.raises(DreApiError):
        split_sitemap_ref("/dr/pesquisa")


def test_collect_maps_metadata_and_relationships(repo_root):
    acervo = Acervo(repo_root)
    document = DreSource(acervo.types, DreClient(FakeSession())).collect(REF)
    metadata, body = document.record.to_dict(), document.body
    assert metadata["id"] == "pt:dre:1183482554:por"
    assert metadata["title"] == "Decreto-Lei n.º 202/2026"
    assert metadata["summary"] == "Altera o Decreto-Lei n.º 40-A/2026, de 13 de fevereiro."
    assert metadata["official_date"] == "2026-10-09"
    assert metadata["publication"]["number"] == "203"
    assert metadata["subjects"] == ["Fundos CE", "Portugal 2030"]
    assert metadata["article_structure"]["article_count"] == 3
    relations = {(item["type"], item["target"]) for item in metadata["relationships"]}
    assert ("amended_by", "pt:dre:1190000001:por") in relations
    assert ("amends", "pt:numero:decreto-lei:40-A/2026") in relations
    assert ("repeals", "pt:numero:portaria:15/2026") in relations
    assert ("corrected_by", "pt:dre:1190000002:por") in relations
    assert ("cites", "pt:dre:1050874165:por") in relations
    assert body.startswith("# Decreto-Lei n.º 202/2026")


def test_ingest_writes_valid_record_and_is_stable(repo_root):
    service = _service(repo_root)
    first = service.ingest(REF)
    assert first.action == "written"
    assert first.path == repo_root.resolve() / "data/portugal/decretos-leis/2026/decreto-lei-202-2026.md"
    assert validate_repository(Acervo(repo_root)) == []
    second = service.ingest(REF)
    assert second.action == "unchanged"


def test_consolidated_text_is_kept_but_relations_are_merged(repo_root):
    service = _service(repo_root)
    result = service.ingest(REF)
    metadata, _ = read_markdown_record(result.path)
    metadata["version"] = {**metadata["version"], "kind": "consolidated", "consolidation_date": "2026-11-02"}
    metadata["source"]["id"] = "legalize-pt"
    metadata["relationships"] = [{"type": "cites", "target": "eli:http://data.dre.pt/eli/lei/1/2000", "label": None}]
    result.path.write_text(render_markdown(metadata, "# Texto consolidado"), encoding="utf-8")

    again = _service(repo_root).ingest(REF)
    assert again.action == "kept_existing"
    kept, body = read_markdown_record(again.path)
    assert body.strip() == "# Texto consolidado"
    targets = {item["target"] for item in kept["relationships"]}
    assert "eli:http://data.dre.pt/eli/lei/1/2000" in targets
    assert "pt:dre:1190000001:por" in targets


def test_ingest_dates_walks_each_day(repo_root):
    session = FakeSession()
    summary = _service(repo_root, session).ingest_dates(date(2026, 10, 20), date(2026, 10, 21))
    assert [call for call, _ in session.calls].count("documents_by_date") == 2
    assert len(summary.documents) == 2
    assert summary.failures == []
