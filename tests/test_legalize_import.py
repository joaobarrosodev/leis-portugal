from __future__ import annotations

from pathlib import Path

from leis_portugal.infrastructure.markdown import read_markdown_record
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.legalize_import import import_legalize
from leis_portugal.services.validation import validate_repository


def test_import_converts_to_repository_structure(repo_root: Path, legalize_repo: Path):
    summary = import_legalize(Acervo(repo_root), legalize_repo, workers=1)
    assert summary.total == 6
    assert summary.written == 5
    assert [failure["path"] for failure in summary.failures] == ["pt/2009/DRE-2009-x-1.md"]
    assert validate_repository(Acervo(repo_root)) == []

    consolidated, body = read_markdown_record(repo_root / "data/portugal/decretos-leis/2009/decreto-lei-140-2009.md")
    assert consolidated["id"] == "pt:dre:494543:por"
    assert consolidated["title"] == "Decreto-Lei n.º 140/2009"
    assert consolidated["version"]["kind"] == "consolidated"
    assert consolidated["version"]["consolidation_date"] == "2024-11-22"
    assert consolidated["subjects"] == ["Património Cultural", "Vistoria"]
    targets = {(item["type"], item["target"]) for item in consolidated["relationships"]}
    assert ("cites", "celex:32016L0798") in targets
    assert ("amended_by", "pt:dre:897548401:por") in targets
    assert body.lstrip().startswith("# Decreto-Lei n.º 140/2009\n\nDecreto-Lei n.º 140/2009\n\nde 15 de Junho\n\nPreâmbulo.")

    portaria, portaria_body = read_markdown_record(repo_root / "data/portugal/portarias/2009/portaria-1-2009.md")
    assert portaria["id"] == "pt:dre:396946:por"
    assert "This is the law as enacted" not in portaria_body
    assert "| A | B |\n| --- | --- |\n| 1 | 2 |" in portaria_body
    # Mesmo número na 2.ª Série: pasta própria. Mesmo número e série: sufixo com o id DRE.
    assert (repo_root / "data/portugal/serie-ii/portarias/2009/portaria-1-2009.md").exists()
    assert (repo_root / "data/portugal/portarias/2009/portaria-1-2009-2000000.md").exists()

    regional, _ = read_markdown_record(
        repo_root / "data/regional/madeira/decretos-regulamentares-regionais/2020/decreto-regulamentar-regional-1-2020-m.md"
    )
    assert regional["jurisdiction"] == "regional"
    assert regional["territory"] == "madeira"
    assert regional["legal_status"] == "repealed"


def test_import_is_idempotent(repo_root: Path, legalize_repo: Path):
    import_legalize(Acervo(repo_root), legalize_repo, workers=1)
    again = import_legalize(Acervo(repo_root), legalize_repo, workers=1)
    assert again.written == 0
    assert again.unchanged == 5


def test_imported_records_cite_the_dre_not_legalize(repo_root: Path, legalize_repo: Path):
    import_legalize(Acervo(repo_root), legalize_repo, workers=1)
    metadata, _ = read_markdown_record(repo_root / "data/portugal/portarias/2009/portaria-1-2009.md")
    assert metadata["source"]["id"] == "dre"
    assert metadata["source"]["official_url"] == "https://diariodarepublica.pt/dr/detalhe/portaria/1-2009-396946"
    assert "github.com" not in metadata["source"]["content_url"]
    assert metadata["integrity"]["source_sha256_scope"] == "imported_derived_markdown"
    assert "legalize-pt" in metadata["provenance"]["notes"]
    assert "legalize" not in metadata["reuse"]["attribution"]
