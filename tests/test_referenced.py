"""Documentos referidos pelo acervo e ainda sem registo."""

from __future__ import annotations

from pathlib import Path

from conftest import record_dict
from leis_portugal.cli import main
from leis_portugal.domain.relations import DiplomaKey
from leis_portugal.infrastructure.markdown import render_markdown
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.dre import DreIngestion
from leis_portugal.services.export import TargetResolver
from leis_portugal.services.referenced import missing_references, referenced_refs
from leis_portugal.sources.dre.source import DreSource
from test_dre_sitemap import SitemapClient


def _citing(root: Path) -> None:
    path = root / "data/portugal/leis/2020/lei-1-2020.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(record_dict("pt:dre:1:por", relationships=[
        {"type": "cites", "target": "pt:dre:1183482554:por", "label": None, "source": None},
        {"type": "cites", "target": "eli:http://data.dre.pt/eli/dec-lei/31838/1942/06/01/p/dre", "label": None, "source": None},
        {"type": "based_on", "target": "pt:numero:decreto-lei:999/2000", "label": None, "source": None},
        {"type": "cites", "target": "celex:32016R0679", "label": None, "source": None},
        {"type": "cites", "target": "eli:http://data.europa.eu/eli/reg/2016/679/oj", "label": None, "source": None},
        {"type": "cites", "target": "celex:11957E100", "label": None, "source": None},
    ]), "# Lei"), encoding="utf-8")


def test_missing_references_by_id_numbering_and_celex(repo_root: Path):
    _citing(repo_root)
    missing = missing_references(Acervo(repo_root), workers=1)
    assert dict(missing.dre_ids) == {"1183482554": 1}
    assert set(missing.diplomas) == {DiplomaKey("decreto-lei", "31838", "1942", "p"), DiplomaKey("decreto-lei", "999", "2000", "p")}
    # O mesmo regulamento por CELEX e por ELI conta uma vez; artigos dos tratados ficam de fora.
    assert dict(missing.celex) == {"32016R0679": 1}


def test_referenced_refs_are_found_in_the_sitemaps(repo_root: Path):
    _citing(repo_root)
    acervo = Acervo(repo_root)
    found = referenced_refs(acervo, SitemapClient(), missing_references(acervo, workers=1))
    assert (found.found_ids, found.found_diplomas) == (1, 1)  # o DL 999/2000 não está nos sitemaps
    assert sorted(found.refs) == ["/dr/detalhe/decreto-lei/202-2026-1183482554", "/dr/detalhe/decreto-lei/31838-1942-138871"]


def test_cli_collects_referenced_diplomas(repo_root: Path, monkeypatch, capsys):
    _citing(repo_root)
    monkeypatch.setattr(
        "leis_portugal.cli.collect.DreIngestion",
        lambda acervo, **options: DreIngestion(acervo, source_factory=lambda: DreSource(acervo.types, SitemapClient()), **options),
    )
    arguments = ["--root", str(repo_root), "collect", "dre", "--referenced", "--no-subjects"]
    assert main([*arguments, "--dry-run"]) == 0
    assert "1 de 1 pelo id e 1 de 2 pela numeração. A recolher: 2" in capsys.readouterr().out
    assert main([*arguments, "--limit", "1"]) == 0
    assert "gravados: 1" in capsys.readouterr().out
    assert (repo_root / "data/portugal/decretos-leis/2026/decreto-lei-202-2026.md").exists()
    assert (repo_root / "reports/dre_referenced_failures.jsonl").read_text(encoding="utf-8") == ""


def test_export_resolves_eu_eli_through_celex():
    resolve = TargetResolver([{"id": "eu:celex:32016R0679:por", "celex": "32016R0679", "eli": None, "jurisdiction": "european_union"}])
    assert resolve("eli:http://data.europa.eu/eli/reg/2016/679/oj") == "eu:celex:32016R0679:por"
    assert resolve("eli:http://data.europa.eu/eli/dir/2019/1/oj") is None


def test_referenced_ids_are_searched_in_every_sitemap(repo_root: Path):
    # Um id citado de um tipo fora do vocabulário (aqui, um ato societário) também é encontrado.
    path = repo_root / "data/portugal/leis/2021/lei-2-2021.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(record_dict("pt:dre:2:por", relationships=[
        {"type": "cites", "target": "pt:dre:4430972:por", "label": None, "source": None},
    ]), "# Lei"), encoding="utf-8")
    acervo = Acervo(repo_root)
    found = referenced_refs(acervo, SitemapClient(), missing_references(acervo, workers=1))
    assert found.refs == ["/dr/detalhe/ato-societario/4430972"]


def test_a_sitemap_the_dre_refuses_is_skipped(repo_root: Path):
    from leis_portugal.errors import FetchError
    from test_dre_sitemap import BASE

    class Refusing(SitemapClient):
        def sitemap(self, url: str) -> bytes:
            if url.endswith("/decreto-lei-sitemap-2.xml"):
                raise FetchError(f"HTTP 403 para {url}")
            return super().sitemap(url)

    _citing(repo_root)
    acervo = Acervo(repo_root)
    client = Refusing()
    messages: list[str] = []
    found = referenced_refs(acervo, client, missing_references(acervo, workers=1), progress=messages.append)
    assert "/dr/detalhe/decreto-lei/202-2026-1183482554" in found.refs
    assert any("decreto-lei ignorado (HTTP 403" in message for message in messages)
    # As páginas gerais nem são pedidas.
    assert f"{BASE}/geral-sitemap-sitemap-1.xml" not in client.requested
