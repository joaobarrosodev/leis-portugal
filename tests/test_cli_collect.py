"""Comandos `collect` pelo CLI, com as fontes substituídas por respostas gravadas."""

from __future__ import annotations

import json
from functools import partial
from pathlib import Path

from conftest import record_dict
from leis_portugal.cli import main
from leis_portugal.infrastructure.http import HttpClient
from leis_portugal.infrastructure.markdown import render_markdown
from leis_portugal.services import versions as versions_service
from leis_portugal.services.dre import DreIngestion
from leis_portugal.services.eurlex import EurLexIngestion
from leis_portugal.sources.dre.client import DreClient
from leis_portugal.sources.dre.source import DreSource
from leis_portugal.sources.eurlex.client import CellarClient
from leis_portugal.sources.eurlex.source import EurLexSource
from test_dre_source import FakeSession
from test_eurlex import FakeCellar
from test_http_and_dre_session import FakeResponse
from test_http_and_dre_session import FakeSession as FakeHttpSession
from test_versions import ENTRY, FakeClient


def run(root: Path, *args: str) -> int:
    return main(["--root", str(root), *args])


def _fake_eurlex(monkeypatch) -> None:
    monkeypatch.setattr(
        "leis_portugal.cli.collect.EurLexIngestion",
        lambda acervo, **options: EurLexIngestion(acervo, source_factory=lambda: EurLexSource(FakeCellar()), **options),
    )


def test_collect_dre_by_date_and_ref(repo_root: Path, monkeypatch, capsys):
    monkeypatch.setattr(
        "leis_portugal.cli.collect.DreIngestion",
        lambda acervo, **options: DreIngestion(acervo, DreSource(acervo.types, DreClient(FakeSession())), **options),
    )
    assert run(repo_root, "collect", "dre", "--date", "2026-10-20") == 0
    out = capsys.readouterr()
    assert "written: data/portugal/decretos-leis/2026/decreto-lei-202-2026.md" in out.out
    assert "2026-10-20: 1 documento(s)" in out.err
    assert run(repo_root, "collect", "dre", "--ref", "/dr/detalhe/decreto-lei/202-2026-1183482554", "--no-subjects") == 0
    assert "decreto-lei-202-2026.md" in capsys.readouterr().out


def test_collect_eurlex_by_dates_and_existing(repo_root: Path, monkeypatch, capsys):
    _fake_eurlex(monkeypatch)
    assert run(repo_root, "collect", "eurlex", "--date", "2022-12-27", "--types", "L", "--workers", "2") == 0
    assert "Atos recolhidos: 2" in capsys.readouterr().out
    assert run(repo_root, "collect", "eurlex", "--existing") == 0
    assert "1 ato(s) da UE no acervo a atualizar" in capsys.readouterr().err


def test_collect_eurlex_referenced_by_portuguese_law(repo_root: Path, monkeypatch, capsys):
    _fake_eurlex(monkeypatch)
    citing = repo_root / "data/portugal/leis/2020/lei-1-2020.md"
    citing.parent.mkdir(parents=True)
    citing.write_text(render_markdown(record_dict("pt:dre:1:por", relationships=[
        {"type": "transposes", "target": "celex:32022L2555", "label": None, "source": None},
        {"type": "cites", "target": "celex:12012E016", "label": None, "source": None},
    ]), "# Lei"), encoding="utf-8")
    assert run(repo_root, "collect", "eurlex", "--referenced", "--limit", "5") == 0
    assert "1 ato(s) da UE referidos pela legislação portuguesa ainda sem registo" in capsys.readouterr().err
    assert (repo_root / "reports/eurlex_referenced_failures.jsonl").read_text(encoding="utf-8") == ""


def test_collect_consolidated_history_and_stale_skip(repo_root: Path, monkeypatch, capsys):
    record = repo_root / "data/portugal/decretos-leis/2009/decreto-lei-140-2009.md"
    record.parent.mkdir(parents=True)
    record.write_text(
        render_markdown(record_dict("pt:dre:494543:por", title="Decreto-Lei n.º 140/2009", identifiers={"dre": "494543", "internal": "pt:dre:494543:por"}), "# x"),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "leis_portugal.cli.collect.collect_versions",
        partial(versions_service.collect_versions, client_factory=FakeClient),
    )
    assert run(repo_root, "collect", "dre-consolidated", "--url", ENTRY.url, "--workers", "1") == 0
    assert "Diplomas: 1; atualizados: 1" in capsys.readouterr().out
    history = json.loads(record.with_name("decreto-lei-140-2009.versoes.json").read_text(encoding="utf-8"))
    assert [version["date"] for version in history["versions"]] == ["2009-06-15", "2024-11-23"]

    # Sem data no sitemap, o diploma volta a ser verificado e não muda.
    assert run(repo_root, "collect", "dre-consolidated", "--url", ENTRY.url, "--stale") == 0
    assert "inalterados: 1" in capsys.readouterr().out


def test_cellar_client_parses_sparql_rows_and_concatenates_text_items():
    session = FakeHttpSession([
        FakeResponse(body={"results": {"bindings": [{"celex": {"value": "32016R0679"}, "published": {"value": "2016-05-04"}}]}}),
        FakeResponse(text="<html>1</html>", content_type="application/xhtml+xml"),
        FakeResponse(text="<html>2</html>", content_type="application/xhtml+xml"),
    ])
    client = CellarClient(HttpClient(session=session, sleep=lambda _seconds: None))
    from datetime import date

    assert client.discover(date(2016, 5, 4), date(2016, 5, 4)) == [("32016R0679", "2016-05-04")]
    assert "PREFIX cdm:" in session.requests[0][2]["params"]["query"]
    from leis_portugal.sources.eurlex.client import Expression

    content = client.fetch_text(Expression(uri=None, title="t", short_title=None, last_modified=None, text_items=["u/DOC_1", "u/DOC_2"], pdf_url=None))
    assert content.content == b"<html>1</html>\n<html>2</html>"
