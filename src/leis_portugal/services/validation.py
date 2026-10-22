"""Validação do acervo: esquema de cada registo, ids únicos e registo de fontes."""

from __future__ import annotations

from dataclasses import dataclass

import yaml

from leis_portugal.errors import StorageError
from leis_portugal.infrastructure.config import load_source_registry
from leis_portugal.infrastructure.markdown import read_markdown_record
from leis_portugal.infrastructure.repository import Acervo


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str


def validate_source_registry(acervo: Acervo) -> list[ValidationIssue]:
    registry_path = acervo.root / "config" / "sources.yml"
    try:
        sources = load_source_registry(acervo.root)
    except (OSError, yaml.YAMLError) as exc:
        return [ValidationIssue(str(registry_path), str(exc))]
    issues: list[ValidationIssue] = []
    seen: set[str] = set()
    for index, source in enumerate(sources):
        source_id = source.get("id", f"#{index}") if isinstance(source, dict) else f"#{index}"
        if source_id in seen:
            issues.append(ValidationIssue(str(registry_path), f"Fonte duplicada: {source_id}"))
        seen.add(source_id)
        issues.extend(ValidationIssue(str(registry_path), f"{source_id}: {message}") for message in acervo.schema.source_errors(source))
    return issues


def validate_repository(acervo: Acervo) -> list[ValidationIssue]:
    """Todos os registos em data/ e o registo de fontes."""
    issues = validate_source_registry(acervo)
    seen_ids: dict[str, str] = {}
    for path in acervo.paths():
        relative = acervo.relative(path)
        try:
            metadata, body = read_markdown_record(path)
        except (OSError, UnicodeError, StorageError, yaml.YAMLError) as exc:
            issues.append(ValidationIssue(relative, str(exc)))
            continue
        issues.extend(ValidationIssue(relative, message) for message in acervo.schema.record_errors(metadata))
        record_id = metadata.get("id")
        if isinstance(record_id, str):
            if record_id in seen_ids:
                issues.append(ValidationIssue(relative, f"ID duplicado; já usado em {seen_ids[record_id]}"))
            else:
                seen_ids[record_id] = relative
        if not body.strip():
            issues.append(ValidationIssue(relative, "O corpo Markdown está vazio."))
        if metadata.get("validation", {}).get("status") == "validation_failed":
            issues.append(ValidationIssue(relative, "O registo está marcado como validation_failed."))
    return issues
