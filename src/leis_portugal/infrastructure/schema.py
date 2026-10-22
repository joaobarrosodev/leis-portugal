"""Validação JSON Schema dos registos e do registo de fontes."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


@lru_cache(maxsize=8)
def _validator(schema_path: str) -> Draft202012Validator:
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


class SchemaValidator:
    """Valida dicionários contra os esquemas em `schemas/`."""

    def __init__(self, root: str | Path) -> None:
        schemas = Path(root).resolve() / "schemas"
        self._record_schema = str(schemas / "legal_document.schema.json")
        self._source_schema = str(schemas / "source_record.schema.json")

    @staticmethod
    def _errors(validator: Draft202012Validator, data: Any) -> list[str]:
        messages = []
        for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path)
            messages.append(f"{location}: {error.message}" if location else error.message)
        return messages

    def record_errors(self, data: dict[str, Any]) -> list[str]:
        return self._errors(_validator(self._record_schema), data)

    def source_errors(self, data: dict[str, Any]) -> list[str]:
        return self._errors(_validator(self._source_schema), data)
