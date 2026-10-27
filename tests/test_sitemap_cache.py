"""Cópia local dos sitemaps do DRE."""

from __future__ import annotations

from pathlib import Path

from leis_portugal.infrastructure.sitemap_cache import CachedSitemapClient
from leis_portugal.sources.dre.sitemap import parse_index


BASE = "https://files.diariodarepublica.pt/sitemap"


def _index(lastmod: str | None) -> bytes:
    stamp = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
    return f"<sitemapindex><sitemap><loc>{BASE}/lei-sitemap-1.xml</loc>{stamp}</sitemap></sitemapindex>".encode()


class Remote:
    def __init__(self) -> None:
        self.index = _index("2026-10-20")
        self.requests: list[str] = []

    def sitemap_index(self) -> bytes:
        return self.index

    def sitemap(self, url: str) -> bytes:
        self.requests.append(url)
        return f"<urlset>{len(self.requests)}</urlset>".encode()


def test_index_lastmod_is_read():
    assert [(item.family, item.lastmod) for item in parse_index(_index("2026-10-20"))] == [("lei", "2026-10-20")]
    assert parse_index(_index(None))[0].lastmod is None


def test_sitemaps_are_downloaded_again_only_when_the_index_date_changes(tmp_path: Path):
    remote = Remote()
    url = f"{BASE}/lei-sitemap-1.xml"

    first = CachedSitemapClient(remote, tmp_path)
    first.sitemap_index()
    assert first.sitemap(url) == b"<urlset>1</urlset>"
    assert (first.downloaded, first.reused) == (1, 0)

    # Outra execução, mesma data no índice: lê a cópia local.
    second = CachedSitemapClient(remote, tmp_path)
    second.sitemap_index()
    assert second.sitemap(url) == b"<urlset>1</urlset>"
    assert (second.downloaded, second.reused, len(remote.requests)) == (0, 1, 1)

    # O DRE alterou o ficheiro: descarrega de novo.
    remote.index = _index("2026-10-26")
    third = CachedSitemapClient(remote, tmp_path)
    third.sitemap_index()
    assert third.sitemap(url) == b"<urlset>2</urlset>"
    assert third.downloaded == 1


def test_without_index_date_the_copy_lasts_one_day(tmp_path: Path):
    remote = Remote()
    remote.index = _index(None)
    url = f"{BASE}/lei-sitemap-1.xml"
    now = [1_000_000.0]
    CachedSitemapClient(remote, tmp_path, clock=lambda: now[0]).sitemap(url)
    cached = (tmp_path / "lei-sitemap-1.xml").stat().st_mtime
    now[0] = cached + 3600
    assert CachedSitemapClient(remote, tmp_path, clock=lambda: now[0]).sitemap(url) == b"<urlset>1</urlset>"
    now[0] = cached + 2 * 24 * 3600
    assert CachedSitemapClient(remote, tmp_path, clock=lambda: now[0]).sitemap(url) == b"<urlset>2</urlset>"
