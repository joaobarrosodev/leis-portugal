"""O fluxo completo pelo CLI, sem rede: importar, ligar, validar, relatar, consultar versões."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import record_dict
from leis_portugal.cli import main
from leis_portugal.infrastructure.markdown import read_markdown_record, render_markdown
from leis_portugal.services.eurlex import EurLexIngestion
from leis_portugal.sources.eurlex.source import EurLexSource
from test_eurlex import FakeCellar


def run(root: Path, *args: str) -> int:
    return main(["--root", str(root), *args])


def test_link_validate_report(repo_root: Path, capsys):
    citing = repo_root / "data/portugal/decretos-leis/2009/decreto-lei-140-2009.md"
    citing.parent.mkdir(parents=True)
    citing.write_text(render_markdown(record_dict("pt:dre:494543:por", relationships=[
        {"type": "cites", "target": "celex:32016L0798", "label": None, "source": None},
    ]), "# Decreto-Lei"), encoding="utf-8")
    regional = repo_root / "data/regional/madeira/decretos-regulamentares-regionais/2020/decreto-regulamentar-regional-1-2020-m.md"
    regional.parent.mkdir(parents=True)
    regional.write_text(render_markdown(record_dict("pt:dre:127657050:por", jurisdiction="regional", territory="madeira"), "# Regional"), encoding="utf-8")
    eu = repo_root / "data/european_union/directives/2016/diretiva-ue-2016-798.md"
    eu.parent.mkdir(parents=True)
    eu.write_text(render_markdown(record_dict("eu:celex:32016L0798:por", identifiers={"celex": "32016L0798"}), "# Diretiva"), encoding="utf-8")

    assert run(repo_root, "link") == 0
    assert "ligações a diplomas portugueses: 1" in capsys.readouterr().out
    metadata, _ = read_markdown_record(eu)
    assert {"type": "cited_by", "target": "pt:dre:494543:por", "label": None, "source": None} in metadata["relationships"]

    assert run(repo_root, "validate") == 0
    assert run(repo_root, "reports") == 0
    coverage = json.loads((repo_root / "reports/coverage.json").read_text(encoding="utf-8"))
    assert coverage["totals"]["documents"] == 3
    assert coverage["by_jurisdiction"] == {"european_union": 1, "portugal": 1, "regional": 1}
    assert (repo_root / "reports/failures.jsonl").read_text(encoding="utf-8") == ""


def test_version_at_lists_and_renders(repo_root: Path, capsys):
    record = repo_root / "data/portugal/leis/2020/lei-1-2020.md"
    record.parent.mkdir(parents=True)
    record.write_text(render_markdown(record_dict("pt:dre:1:por", title="Lei n.º 1/2020"), "# Lei n.º 1/2020"), encoding="utf-8")
    history = {
        "versions": [
            {"date": "2020-01-01", "acts": [], "changes": [], "fragments": ["a"]},
            {"date": "2024-01-01", "acts": [{"title": "Lei n.º 5/2024"}], "changes": ["Altera Artigo 1.º"], "fragments": ["b"]},
        ],
        "fragments": {"a": {"markdown": "###### Artigo 1.º\n\nOriginal."}, "b": {"markdown": "###### Artigo 1.º\n\nAlterado."}},
    }
    record.with_name("lei-1-2020.versoes.json").write_text(json.dumps(history), encoding="utf-8")

    assert run(repo_root, "version-at", "pt:dre:1:por", "--list") == 0
    assert "2024-01-01  Lei n.º 5/2024  (1 modificação(ões))" in capsys.readouterr().out
    assert run(repo_root, "version-at", str(record), "--date", "2021-06-01") == 0
    assert capsys.readouterr().out == "# Lei n.º 1/2020\n\n###### Artigo 1.º\n\nOriginal.\n"
    assert run(repo_root, "version-at", "pt:dre:1:por", "--date", "2019-01-01") == 1
    assert run(repo_root, "version-at", "pt:dre:404:por") == 1


def test_collect_eurlex_by_celex(repo_root: Path, monkeypatch, capsys):
    monkeypatch.setattr(
        "leis_portugal.cli.collect.EurLexIngestion",
        lambda acervo, **options: EurLexIngestion(acervo, source_factory=lambda: EurLexSource(FakeCellar()), **options),
    )
    assert run(repo_root, "collect", "eurlex", "--celex", "32022L2555") == 0
    assert "Registo atualizado: data/european_union/directives/2022/diretiva-ue-2022-2555.md" in capsys.readouterr().out


def test_invalid_input_is_a_clean_error(repo_root: Path, capsys):
    assert run(repo_root, "collect", "eurlex", "--celex", "isto-nao-e-celex") == 1
    assert "Erro: Identificador CELEX inválido" in capsys.readouterr().err


def test_sources_lists_registry(repo_root: Path, capsys):
    assert run(repo_root, "sources") == 0
    assert "dre: operational" in capsys.readouterr().out


@pytest.mark.parametrize("command", [["collect"], ["import"], []])
def test_incomplete_commands_show_usage(repo_root: Path, command):
    with pytest.raises(SystemExit):
        run(repo_root, *command)
