"""Cobertura pelos sitemaps do DRE e recolha dos documentos em falta."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import record_dict
from leis_portugal.cli import main
from leis_portugal.infrastructure.markdown import render_markdown
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.coverage import sitemap_coverage
from leis_portugal.services.dre import DreIngestion
from leis_portugal.sources.dre.client import DreClient
from leis_portugal.sources.dre.sitemap import parse_documents, parse_index
from leis_portugal.sources.dre.source import DreSource
from test_dre_source import FakeSession


BASE = "https://files.diariodarepublica.pt/sitemap"
INDEX = f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<sitemap><loc>{BASE}/decreto-lei-sitemap-1.xml</loc><lastmod>2026-10-20</lastmod></sitemap>
<sitemap><loc>{BASE}/decreto-lei-sitemap-2.xml</loc></sitemap>
<sitemap><loc>{BASE}/despacho-sitemap-1.xml</loc></sitemap>
<sitemap><loc>{BASE}/ato-societario-sitemap-1.xml</loc></sitemap>
<sitemap><loc>{BASE}/geral-sitemap-sitemap-1.xml</loc></sitemap>
</sitemapindex>""".encode()


def _urlset(*paths: str) -> bytes:
    rows = "".join(f"<url><loc>https://diariodarepublica.pt{path}</loc></url>\n" for path in paths)
    return f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}</urlset>'.encode()


SITEMAPS = {
    f"{BASE}/decreto-lei-sitemap-1.xml": _urlset(
        "/dr/detalhe/decreto-lei/202-2026-1183482554",
        "/dr/detalhe/decreto-lei/31838-1942-138871",
        "/dr/detalhe/decreto-lei/140-2009-494543",
        "/dr/geral/avisos-legais",
    ),
    # Repete um documento do primeiro ficheiro e traz uma linha em Latin-1.
    f"{BASE}/decreto-lei-sitemap-2.xml": _urlset("/dr/detalhe/decreto-lei/140-2009-494543")
    + "<url><loc>https://diariodarepublica.pt/dr/detalhe/decreto-lei/1-n.ª-1940-138000</loc></url>\n".encode("latin-1"),
    f"{BASE}/despacho-sitemap-1.xml": _urlset("/dr/detalhe/despacho/1977-138169", "/dr/detalhe/despacho/15-2020-555"),
    f"{BASE}/ato-societario-sitemap-1.xml": _urlset("/dr/detalhe/ato-societario/4430972"),
}


class SitemapClient(DreClient):
    """Cliente DRE com sitemaps gravados (e o detalhe do DL 202/2026 da FakeSession)."""

    def __init__(self) -> None:
        super().__init__(FakeSession())
        self.requested: list[str] = []

    def sitemap_index(self) -> bytes:
        return INDEX

    def sitemap(self, url: str) -> bytes:
        self.requested.append(url)
        return SITEMAPS.get(url, _urlset())  # p. ex. `geral-sitemap`, sem páginas de detalhe


def _with_record(root: Path, dre_id: str) -> None:
    path = root / "data" / "portugal" / "decretos-leis" / "2009" / "decreto-lei-140-2009.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    record = record_dict(f"pt:dre:{dre_id}:por", identifiers={"dre": dre_id, "internal": f"pt:dre:{dre_id}:por"})
    path.write_text(render_markdown(record, "# Decreto-Lei n.º 140/2009"), encoding="utf-8")


def test_parse_index_and_documents():
    files = parse_index(INDEX)
    assert [item.family for item in files] == ["decreto-lei", "decreto-lei", "despacho", "ato-societario", "geral-sitemap"]
    documents = parse_documents(SITEMAPS[f"{BASE}/decreto-lei-sitemap-2.xml"])
    assert [(item.tipo, item.dre_id) for item in documents] == [("decreto-lei", "494543"), ("decreto-lei", "138000")]
    assert documents[1].ref == "/dr/detalhe/decreto-lei/1-n.ª-1940-138000"
    # Caminho sem número nem ano; páginas que não são de detalhe ficam de fora.
    assert [item.dre_id for item in parse_documents(_urlset("/dr/detalhe/acordao/29942863", "/dr/geral/x"))] == ["29942863"]


def test_coverage_counts_present_missing_and_optional_types(repo_root: Path):
    _with_record(repo_root, "494543")
    client = SitemapClient()
    coverage = sitemap_coverage(Acervo(repo_root), client)
    by_type = {entry.slug: entry for entry in coverage}
    assert list(by_type) == ["decreto-lei", "despacho"]  # ordem do vocabulário
    decree_laws = by_type["decreto-lei"]
    assert (decree_laws.listed, decree_laws.present) == (4, 1)
    assert decree_laws.missing == [
        "/dr/detalhe/decreto-lei/202-2026-1183482554",
        "/dr/detalhe/decreto-lei/31838-1942-138871",
        "/dr/detalhe/decreto-lei/1-n.ª-1940-138000",
    ]
    assert by_type["despacho"].optional and len(by_type["despacho"].missing) == 2
    # Os atos societários não são do vocabulário: o ficheiro nem é pedido.
    assert f"{BASE}/ato-societario-sitemap-1.xml" not in client.requested


def test_coverage_limited_to_types(repo_root: Path):
    client = SitemapClient()
    coverage = sitemap_coverage(Acervo(repo_root), client, types={"despacho"})
    assert [entry.slug for entry in coverage] == ["despacho"]
    assert client.requested == [f"{BASE}/despacho-sitemap-1.xml"]


def _fake_service(monkeypatch) -> None:
    monkeypatch.setattr(
        "leis_portugal.cli.collect.DreIngestion",
        lambda acervo, **options: DreIngestion(acervo, source_factory=lambda: DreSource(acervo.types, SitemapClient()), **options),
    )


def test_cli_missing_dry_run_counts_and_writes_report(repo_root: Path, monkeypatch, capsys):
    _fake_service(monkeypatch)
    _with_record(repo_root, "494543")
    assert main(["--root", str(repo_root), "collect", "dre", "--missing", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "Decreto-Lei" in out and "Despacho *" in out
    assert "A recolher: 3" in out  # os despachos só com --all
    report = json.loads((repo_root / "reports" / "dre_sitemap_coverage.json").read_text(encoding="utf-8"))
    assert (report["listed"], report["present"], report["missing"]) == (6, 1, 5)
    assert not (repo_root / "data" / "portugal" / "decretos-leis" / "2026").exists()

    assert main(["--root", str(repo_root), "collect", "dre", "--missing", "--dry-run", "--all"]) == 0
    assert "A recolher: 5" in capsys.readouterr().out


def test_cli_missing_collects_listed_documents(repo_root: Path, monkeypatch, capsys):
    _fake_service(monkeypatch)
    assert main(["--root", str(repo_root), "collect", "dre", "--missing", "--types", "decreto-lei", "--limit", "1", "--no-subjects"]) == 0
    out = capsys.readouterr().out
    assert "A recolher: 1" in out and "gravados: 1" in out
    assert (repo_root / "data" / "portugal" / "decretos-leis" / "2026" / "decreto-lei-202-2026.md").exists()
    assert (repo_root / "reports" / "dre_missing_failures.jsonl").read_text(encoding="utf-8") == ""


def test_cli_missing_rejects_unknown_types(repo_root: Path, monkeypatch, capsys):
    _fake_service(monkeypatch)
    assert main(["--root", str(repo_root), "collect", "dre", "--missing", "--types", "ato-societario"]) != 0
    assert "fora do vocabulário" in capsys.readouterr().err


@pytest.mark.parametrize("slug, expected", [("decreto-lei", False), ("despacho-extracto", True), ("declaracao", True)])
def test_optional_types_come_from_the_vocabulary(repo_root: Path, slug: str, expected: bool):
    types = Acervo(repo_root).types
    assert (types.resolve(slug).slug in types.sitemap_optional) is expected
