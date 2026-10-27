"""Cópia local dos sitemaps do DRE (`.cache/dre-sitemaps/`, fora do git).

O índice é sempre pedido ao DRE (é pequeno) e diz a data de alteração de cada
ficheiro. Um ficheiro só é descarregado de novo quando essa data muda; sem data no
índice, a cópia serve durante um dia. Para forçar tudo de novo, basta apagar a pasta.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Protocol

from leis_portugal.infrastructure.markdown import write_if_changed
from leis_portugal.sources.dre.sitemap import parse_index


ONE_DAY = 24 * 3600


class SitemapSource(Protocol):
    def sitemap_index(self) -> bytes: ...

    def sitemap(self, url: str) -> bytes: ...


class CachedSitemapClient:
    """Mesma interface que o cliente do DRE (`sitemap_index`, `sitemap`), com cópia local."""

    def __init__(self, client: SitemapSource, directory: Path, *, max_age: float = ONE_DAY, clock=time.time) -> None:
        self.client = client
        self.directory = Path(directory)
        self.max_age = max_age
        self.clock = clock
        self._lastmod: dict[str, str | None] = {}
        self.downloaded = 0
        self.reused = 0

    def sitemap_index(self) -> bytes:
        xml = self.client.sitemap_index()
        self._lastmod = {item.url: item.lastmod for item in parse_index(xml)}
        return xml

    def _paths(self, url: str) -> tuple[Path, Path]:
        name = url.rstrip("/").rsplit("/", 1)[-1]
        return self.directory / name, self.directory / f"{name}.lastmod"

    def _fresh(self, content: Path, stamp: Path, lastmod: str | None) -> bool:
        if not content.exists():
            return False
        if lastmod:
            return stamp.exists() and stamp.read_text(encoding="utf-8").strip() == lastmod
        return self.clock() - content.stat().st_mtime < self.max_age

    def sitemap(self, url: str) -> bytes:
        content, stamp = self._paths(url)
        lastmod = self._lastmod.get(url)
        if self._fresh(content, stamp, lastmod):
            self.reused += 1
            return content.read_bytes()
        xml = self.client.sitemap(url)
        self.directory.mkdir(parents=True, exist_ok=True)
        content.write_bytes(xml)
        write_if_changed(stamp, (lastmod or "") + "\n")
        self.downloaded += 1
        return xml
