"""Leitura da configuração do repositório (`config/`)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from leis_portugal.domain.document_types import DocumentTypeRegistry


@lru_cache(maxsize=4)
def _document_types(path: str) -> DocumentTypeRegistry:
    return DocumentTypeRegistry(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def load_document_types(root: str | Path) -> DocumentTypeRegistry:
    return _document_types(str(Path(root).resolve() / "config" / "document_types.yml"))


def load_source_registry(root: str | Path) -> list[dict[str, Any]]:
    registry = yaml.safe_load((Path(root) / "config" / "sources.yml").read_text(encoding="utf-8"))
    return registry.get("sources", []) if isinstance(registry, dict) else []
