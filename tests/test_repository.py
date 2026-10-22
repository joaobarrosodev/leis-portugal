from __future__ import annotations

from pathlib import Path

import pytest

from conftest import record_dict
from leis_portugal.domain.record import LegalRecord, Relationship
from leis_portugal.errors import InvalidRecord, StorageError
from leis_portugal.infrastructure.markdown import render_markdown
from leis_portugal.infrastructure.repository import Acervo, SavePolicy


def _record(record_id: str = "pt:dre:100:por", **overrides) -> LegalRecord:
    data = record_dict(
        record_id,
        title="Decreto-Lei n.º 1/2020",
        official_number="1/2020",
        publication_date="2020-01-02",
        identifiers={"dre": record_id.split(":")[2], "internal": record_id},
    )
    data.update(overrides)
    return LegalRecord.from_dict(data)


def test_round_trip_keeps_field_order_and_omits_empty_optionals():
    data = record_dict("pt:dre:1:por", relationships=[{"type": "cites", "target": "pt:dre:2:por", "label": None, "source": None}])
    record = LegalRecord.from_dict(data)
    out = record.to_dict()
    assert list(out)[:3] == ["schema_version", "id", "title"]
    assert "version_history" not in out
    assert out["relationships"] == [{"type": "cites", "target": "pt:dre:2:por", "label": None, "source": None}]
    assert LegalRecord.from_dict(out).to_dict() == out


def test_save_writes_validated_record_and_detects_no_change(repo_root: Path):
    acervo = Acervo(repo_root)
    first = acervo.save(_record(), "# Texto")
    assert first.action == "written"
    assert first.path == acervo.root / "data/portugal/decretos-leis/2020/decreto-lei-1-2020.md"
    assert acervo.save(_record(), "# Texto").action == "unchanged"
    assert acervo.find("pt:dre:100:por") == first.path


def test_invalid_record_is_refused(repo_root: Path):
    acervo = Acervo(repo_root)
    with pytest.raises(InvalidRecord):
        acervo.save(_record(legal_status="talvez"), "# Texto")


def test_existing_consolidated_text_wins_over_published_text(repo_root: Path):
    acervo = Acervo(repo_root)
    consolidated = _record(version={"kind": "consolidated", "label": "Consolidado", "language": "por", "consolidation_date": "2024-01-01"})
    acervo.save(consolidated, "# Consolidado")
    published = _record(subjects=["Novo"], relationships=[{"type": "amended_by", "target": "pt:dre:9:por", "label": None, "source": None}])
    result = acervo.save(published, "# Publicado")
    assert result.action == "kept_existing"
    record, body = acervo.read(result.path)
    assert body.strip() == "# Consolidado"
    assert record.subjects == ["Novo"]
    assert [item.target for item in record.relationships] == ["pt:dre:9:por"]


def test_policy_can_replace_source_relations_but_keep_local_links(repo_root: Path):
    acervo = Acervo(repo_root)
    acervo.save(_record(relationships=[
        {"type": "cites", "target": "celex:1", "label": None, "source": None},
        {"type": "cited_by", "target": "pt:dre:5:por", "label": None, "source": None},
    ]), "# Texto")
    policy = SavePolicy(keep_relationship=lambda relation: relation.target.startswith("pt:"), respect_precedence=False)
    result = acervo.save(_record(relationships=[{"type": "cites", "target": "celex:2", "label": None, "source": None}]), "# Texto", policy=policy)
    record, _ = acervo.read(result.path)
    assert {item.target for item in record.relationships} == {"celex:2", "pt:dre:5:por"}


def test_unchanged_source_bytes_keep_previous_timestamps(repo_root: Path):
    acervo = Acervo(repo_root)
    acervo.save(_record(), "# Texto")
    again = _record(source={**record_dict("x")["source"], "retrieved_at": "2030-01-01T00:00:00Z"})
    assert acervo.save(again, "# Texto").action == "unchanged"
    record, _ = acervo.read(acervo.find("pt:dre:100:por"))
    assert record.source.retrieved_at == "2026-10-21T00:00:00Z"


def test_path_collision_disambiguates_with_dre_id(repo_root: Path):
    acervo = Acervo(repo_root)
    first = acervo.save(_record("pt:dre:100:por"), "# A")
    second = acervo.save(_record("pt:dre:200:por"), "# B")
    assert first.path.name == "decreto-lei-1-2020.md"
    assert second.path.name == "decreto-lei-1-2020-200.md"


def test_explicit_target_with_other_document_is_a_collision(repo_root: Path):
    acervo = Acervo(repo_root)
    first = acervo.save(_record("pt:dre:100:por"), "# A")
    with pytest.raises(StorageError, match="Colisão"):
        acervo.save(_record("pt:dre:200:por"), "# B", target=first.path)


def test_eu_paths_use_celex_year_and_base_type(repo_root: Path):
    acervo = Acervo(repo_root)
    record = LegalRecord.from_dict(record_dict(
        "eu:celex:32024R1689:por",
        document_type="regulation",
        document_type_label="Regulamento Delegado",
        official_number="2024/1689",
        identifiers={"celex": "32024R1689"},
    ))
    assert acervo.relative(acervo.path_for(record)) == "data/european_union/regulations/2024/regulamento-ue-2024-1689.md"


def test_history_files_live_next_to_the_record(repo_root: Path):
    acervo = Acervo(repo_root)
    result = acervo.save(_record(), "# Texto")
    assert acervo.read_history(result.path) is None
    assert acervo.write_history(result.path, {"consolidated_url": "https://x/dr/legislacao-consolidada/lei/2020-5", "versions": []})
    assert acervo.history_path(result.path).name == "decreto-lei-1-2020.versoes.json"
    assert [content["consolidated_url"] for _, content in acervo.histories()] == ["https://x/dr/legislacao-consolidada/lei/2020-5"]


def test_merge_prefers_labelled_duplicates():
    record = _record()
    record.add_relationships([Relationship(type="cites", target="pt:dre:2:por")], [Relationship(type="cites", target="pt:dre:2:por", label="com etiqueta")])
    assert [(item.target, item.label) for item in record.relationships] == [("pt:dre:2:por", "com etiqueta")]


def test_index_reads_ids_without_parsing_yaml(repo_root: Path):
    path = repo_root / "data/portugal/leis/2020/lei-1-2020.md"
    path.parent.mkdir(parents=True)
    path.write_text(render_markdown(record_dict("pt:dre:7:por"), "# x"), encoding="utf-8")
    assert Acervo(repo_root).index() == {"pt:dre:7:por": path.resolve()}


def test_direct_collection_replaces_import_but_never_the_reverse(repo_root: Path):
    acervo = Acervo(repo_root)
    imported = {"source_sha256": "1" * 64, "source_sha256_scope": "imported_derived_markdown"}
    acervo.save(_record(integrity=imported), "# Importado")
    direct = acervo.save(_record(integrity={"source_sha256": "2" * 64, "source_sha256_scope": "official_source_content_bytes"}), "# Direto")
    assert direct.action == "written"
    again = acervo.save(_record(integrity=imported), "# Importado")
    assert again.action == "kept_existing"
    _, body = acervo.read(again.path)
    assert body.strip() == "# Direto"
