"""Cobertura do acervo face aos sitemaps do DRE: o que o DRE lista e o acervo não tem.

A recolha por datas só garante o que foi publicado desde que começou a correr; os
sitemaps listam tudo o que o DRE tem, desde 1820. Só entram os tipos do vocabulário
(`config/document_types.yml`); os documentos repetidos entre ficheiros contam uma vez.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from leis_portugal.domain.identifiers import pt_record_id
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.common import Progress, silent
from leis_portugal.sources.dre.sitemap import parse_documents, parse_index


class SitemapClient(Protocol):
    def sitemap_index(self) -> bytes: ...

    def sitemap(self, url: str) -> bytes: ...


@dataclass
class TypeCoverage:
    slug: str
    label: str
    optional: bool = False
    listed: int = 0
    present: int = 0
    missing: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "type": self.slug,
            "label": self.label,
            "optional": self.optional,
            "listed": self.listed,
            "present": self.present,
            "missing": len(self.missing),
        }


def sitemap_coverage(
    acervo: Acervo,
    client: SitemapClient,
    *,
    types: set[str] | None = None,
    progress: Progress = silent,
) -> list[TypeCoverage]:
    """Por tipo: quantos documentos o DRE lista, quantos o acervo tem e os caminhos em falta.

    `types` limita a contagem a esses tipos canónicos. A lista sai pela ordem do
    vocabulário (leis antes de portarias, portarias antes de avisos)."""
    registry = acervo.types
    files = [item for item in parse_index(client.sitemap_index()) if registry.resolve(item.family).known]
    if types is not None:
        files = [item for item in files if registry.resolve(item.family).slug in types]
    present = acervo.index()
    seen: set[str] = set()
    coverage: dict[str, TypeCoverage] = {}
    for number, item in enumerate(files, start=1):
        documents = parse_documents(client.sitemap(item.url))
        progress(f"sitemap {number}/{len(files)}: {item.family} ({len(documents)} documento(s))")
        for document in documents:
            document_type = registry.resolve(document.tipo)
            if not document_type.known or document.dre_id in seen or (types is not None and document_type.slug not in types):
                continue
            seen.add(document.dre_id)
            entry = coverage.setdefault(
                document_type.slug,
                TypeCoverage(document_type.slug, document_type.label, optional=document_type.slug in registry.sitemap_optional),
            )
            entry.listed += 1
            if pt_record_id(document.dre_id) in present:
                entry.present += 1
            else:
                entry.missing.append(document.ref)
    return sorted(coverage.values(), key=lambda entry: (registry.order(entry.slug), entry.slug))


def write_coverage(path: Path, coverage: list[TypeCoverage], *, checked: str) -> None:
    """Contagens por tipo em `reports/` (sem a lista de caminhos, que pode ter centenas de milhares)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "checked": checked,
        "listed": sum(entry.listed for entry in coverage),
        "present": sum(entry.present for entry in coverage),
        "missing": sum(len(entry.missing) for entry in coverage),
        "types": [entry.as_dict() for entry in coverage],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
