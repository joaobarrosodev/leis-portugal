"""Saída comum dos comandos."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from leis_portugal.infrastructure.repository import Acervo


def acervo(args) -> Acervo:
    return Acervo(args.root)


def progress(message: str) -> None:
    print(message, file=sys.stderr)


def write_failures(path: Path, failures: list[dict[str, Any]], *, sort_key: str | None = None) -> None:
    """Relatório JSONL de falhas (vazio quando não há falhas)."""
    items = sorted(failures, key=lambda item: item[sort_key]) if sort_key else failures
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in items), encoding="utf-8")
