"""Leitura e escrita de ficheiros Markdown com front matter YAML."""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from typing import Any

import yaml

from leis_portugal.errors import StorageError


# O acervo tem centenas de milhares de registos: usar o parser em C quando existe.
_YamlLoader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


class FrontMatterError(StorageError):
    """O ficheiro não contém front matter YAML válido."""


def render_markdown(metadata: dict[str, Any], body: str) -> str:
    """Renderiza um documento Markdown determinístico."""
    front_matter = yaml.safe_dump(
        metadata,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=120,
    )
    return f"---\n{front_matter}---\n\n{body.strip()}\n"


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """Separa metadados YAML do corpo Markdown."""
    if not text.startswith("---\n"):
        raise FrontMatterError("O ficheiro não começa com front matter YAML.")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise FrontMatterError("Não foi encontrado o terminador do front matter YAML.")
    raw_metadata = text[4:end]
    body = text[end + 5 :]
    metadata = yaml.load(raw_metadata, Loader=_YamlLoader)
    if not isinstance(metadata, dict):
        raise FrontMatterError("O front matter YAML não contém um objeto.")
    return metadata, body


def read_markdown_record(path: str | Path) -> tuple[dict[str, Any], str]:
    """Lê um registo Markdown e devolve metadados e corpo."""
    return split_front_matter(Path(path).read_text(encoding="utf-8"))


_ID_LINE = re.compile(r"^id: '?([^'\n]+?)'?$", re.MULTILINE)


def read_record_id(path: str | Path) -> str | None:
    """Lê só o `id` do front matter (as primeiras linhas), sem interpretar o YAML."""
    try:
        with open(path, encoding="utf-8") as handle:
            head = handle.read(4096)
    except OSError:
        return None
    match = _ID_LINE.search(head)
    return match.group(1) if match else None


def write_if_changed(path: str | Path, content: str) -> bool:
    """Escrita atómica; devolve True só quando o conteúdo muda."""
    target = Path(path)
    if target.exists() and target.read_text(encoding="utf-8") == content:
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    # Temporário único na mesma pasta: escritas concorrentes não partilham o ficheiro.
    handle, temporary = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        os.chmod(temporary, 0o644)
        os.replace(temporary, target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
    return True
