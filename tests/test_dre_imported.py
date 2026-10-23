"""Recolha direta dos registos que ainda têm o texto da importação inicial."""

from __future__ import annotations

from pathlib import Path

from conftest import record_dict
from leis_portugal.cli import main
from leis_portugal.infrastructure.markdown import read_markdown_record, render_markdown
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.dre import DreIngestion, imported_references
from leis_portugal.sources.dre.client import DreClient
from leis_portugal.sources.dre.source import DreSource
from test_dre_source import FakeSession


REF = "/dr/detalhe/decreto-lei/202-2026-1183482554"


def _imported(repo_root: Path, relative: str) -> Path:
    path = repo_root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(record_dict(
        "pt:dre:1183482554:por",
        title="Decreto-Lei n.º 202/2026",
        official_number="202/2026",
        publication_date="2026-10-20",
        identifiers={"dre": "1183482554", "dre_path": REF, "internal": "pt:dre:1183482554:por"},
        integrity={"source_sha256": "1" * 64, "source_sha256_scope": "imported_derived_markdown"},
        subjects=["Descritor antigo"],
    ), "# Texto importado"), encoding="utf-8")
    return path


def _service(acervo: Acervo) -> DreIngestion:
    return DreIngestion(acervo, source_factory=lambda: DreSource(acervo.types, DreClient(FakeSession())))


def test_imported_references_lists_only_imported_records(repo_root: Path):
    _imported(repo_root, "data/portugal/decretos-leis/2026/decreto-lei-202-2026.md")
    direct = repo_root / "data/portugal/leis/2020/lei-1-2020.md"
    direct.parent.mkdir(parents=True)
    direct.write_text(render_markdown(record_dict("pt:dre:1:por", identifiers={"dre_path": "/dr/detalhe/lei/1-2020-1"}), "# x"), encoding="utf-8")
    assert imported_references(Acervo(repo_root), workers=1) == [REF]


def test_recollection_replaces_import_in_the_same_file(repo_root: Path):
    # O registo importado está num caminho diferente do canónico: a recolha grava no mesmo ficheiro.
    path = _imported(repo_root, "data/portugal/decretos-leis/2026/decreto-lei-202-2026-1183482554.md")
    acervo = Acervo(repo_root)
    summary = _service(acervo).ingest_many([REF], workers=2)
    assert [result.action for result in summary.documents] == ["written"]
    assert summary.documents[0].path == path.resolve()
    assert not (repo_root / "data/portugal/decretos-leis/2026/decreto-lei-202-2026.md").exists()
    metadata, body = read_markdown_record(path)
    assert metadata["integrity"]["source_sha256_scope"] == "official_source_content_bytes"
    assert metadata["source"]["id"] == "dre"
    assert "Texto importado" not in body
    assert imported_references(Acervo(repo_root), workers=1) == []


def test_cli_recollects_imported_records(repo_root: Path, monkeypatch, capsys):
    _imported(repo_root, "data/portugal/decretos-leis/2026/decreto-lei-202-2026.md")
    monkeypatch.setattr(
        "leis_portugal.cli.collect.DreIngestion",
        lambda acervo, **options: DreIngestion(acervo, source_factory=lambda: DreSource(acervo.types, DreClient(FakeSession())), **options),
    )
    assert main(["--root", str(repo_root), "collect", "dre", "--imported", "--workers", "2"]) == 0
    out = capsys.readouterr()
    assert "1 registo(s) com o texto da importação inicial" in out.err
    assert "Diplomas: 1; atualizados: 1" in out.out


def test_cli_imported_limited_to_types(repo_root: Path, monkeypatch, capsys):
    _imported(repo_root, "data/portugal/decretos-leis/2026/decreto-lei-202-2026.md")
    monkeypatch.setattr(
        "leis_portugal.cli.collect.DreIngestion",
        lambda acervo, **options: DreIngestion(acervo, source_factory=lambda: DreSource(acervo.types, DreClient(FakeSession())), **options),
    )
    assert main(["--root", str(repo_root), "collect", "dre", "--imported", "--types", "lei,portaria"]) == 0
    assert "0 registo(s) com o texto da importação inicial" in capsys.readouterr().err
    assert main(["--root", str(repo_root), "collect", "dre", "--imported", "--types", "decreto-lei"]) == 0
    assert "Diplomas: 1; atualizados: 1" in capsys.readouterr().out
