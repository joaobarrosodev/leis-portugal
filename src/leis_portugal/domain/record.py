"""Modelo tipado de um registo do acervo (diploma português ou ato da UE).

A ordem dos campos é a ordem de serialização no front matter YAML: alterá-la muda
todos os ficheiros do acervo. `from_dict`/`to_dict` fazem a ida e volta exata do
formato em disco, validado por `schemas/legal_document.schema.json`.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, replace
from datetime import UTC, datetime
from typing import Any

from leis_portugal import __version__


SCHEMA_VERSION = "1.0"

# Precedência entre registos do mesmo diploma: um texto consolidado prevalece sobre o
# texto publicado e, no mesmo tipo de versão, a recolha direta na fonte prevalece sobre
# o texto da importação inicial (bytes convertidos, `imported_derived_markdown`).
_KIND_RANK = {"original": 0, "corrigendum": 0, "republication": 1, "consolidated": 2}
IMPORTED_SCOPE = "imported_derived_markdown"
SOURCE_GAP_PREFIX = "Fonte sem texto:"


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


class _Block:
    """Ida e volta dict <-> dataclass, na ordem dos campos."""

    _optional_keys: frozenset[str] = frozenset()

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None):
        data = data or {}
        known = {item.name for item in fields(cls)}
        return cls(**{key: value for key, value in data.items() if key in known})

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for item in fields(self):
            value = getattr(self, item.name)
            if value is None and item.name in self._optional_keys:
                continue
            result[item.name] = list(value) if isinstance(value, list) else value
        return result


@dataclass(frozen=True)
class Relationship(_Block):
    """Relação com outro documento. `date` só é serializada quando existe."""

    type: str
    target: str
    label: str | None = None
    source: str | None = None
    date: str | None = None

    _optional_keys = frozenset({"date"})

    @property
    def key(self) -> tuple[str, str, str | None]:
        return self.type, self.target, self.date


def merge_relationships(*groups: list[Relationship] | None) -> list[Relationship]:
    """Une listas de relações sem duplicados (tipo, alvo, data), por ordem estável.

    Entre duplicados prevalece a primeira com etiqueta."""
    merged: dict[tuple[str, str, str | None], Relationship] = {}
    for group in groups:
        for relation in group or []:
            if relation.key not in merged or (relation.label and not merged[relation.key].label):
                merged[relation.key] = relation
    return sorted(merged.values(), key=lambda item: (item.type, item.date or "", item.target))


@dataclass
class Publication(_Block):
    gazette: str | None = None
    reference: str | None = None
    number: str | None = None
    series: str | None = None
    supplement: str | None = None
    pages: str | None = None
    pdf_url: str | None = None


@dataclass
class Version(_Block):
    kind: str = "original"
    label: str = "Texto original"
    language: str = "por"
    consolidation_date: str | None = None


@dataclass
class VersionHistoryEntry(_Block):
    date: str
    amending: str | None = None
    amending_title: str | None = None
    changes: list[str] = field(default_factory=list)


@dataclass
class VersionHistory(_Block):
    file: str
    count: int
    source_lastmod: str | None = None
    versions: list[VersionHistoryEntry] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> VersionHistory | None:
        if not data:
            return None
        return cls(
            file=data["file"],
            count=data["count"],
            source_lastmod=data.get("source_lastmod"),
            versions=[VersionHistoryEntry.from_dict(item) for item in data.get("versions") or []],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "count": self.count,
            "source_lastmod": self.source_lastmod,
            "versions": [item.to_dict() for item in self.versions],
        }


@dataclass
class Identifiers(_Block):
    celex: str | None = None
    eli: str | None = None
    oj: str | None = None
    dre: str | None = None
    dre_path: str | None = None
    internal: str | None = None

    # O esquema exige texto em `internal`: sem valor, o campo não é escrito.
    _optional_keys = frozenset({"internal"})


@dataclass
class Source(_Block):
    id: str
    name: str
    official_url: str
    metadata_url: str | None = None
    content_url: str | None = None
    consolidated_url: str | None = None
    retrieved_at: str = field(default_factory=utc_now)
    retrieval_method: str = ""
    source_modified_at: str | None = None


@dataclass
class Integrity(_Block):
    source_sha256: str
    source_sha256_scope: str = "official_source_content_bytes"


@dataclass
class Provenance(_Block):
    collector: str
    generated_by: str
    collector_version: str = __version__
    generated_at: str = field(default_factory=utc_now)
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        # Ordem histórica em disco: collector, collector_version, generated_by, generated_at, notes.
        return {
            "collector": self.collector,
            "collector_version": self.collector_version,
            "generated_by": self.generated_by,
            "generated_at": self.generated_at,
            "notes": self.notes,
        }


@dataclass
class Reuse(_Block):
    status: str
    attribution: str
    reference: str | None = None
    notes: str | None = None


@dataclass
class ArticleStructure(_Block):
    article_count: int | None = None
    section_count: int | None = None
    extraction_method: str | None = None


@dataclass
class DerivedMaterial(_Block):
    machine_generated: bool = True
    notes: str | None = None


@dataclass
class Validation(_Block):
    status: str = "pending_review"
    checked_at: str = field(default_factory=utc_now)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class LegalRecord:
    """Um documento do acervo: metadados normalizados de um diploma ou ato."""

    id: str
    title: str
    jurisdiction: str
    document_type: str
    source: Source
    integrity: Integrity
    provenance: Provenance
    reuse: Reuse
    schema_version: str = SCHEMA_VERSION
    short_title: str | None = None
    summary: str | None = None
    territory: str | None = None
    document_type_label: str | None = None
    issuing_authority: list[str] = field(default_factory=list)
    proposing_entity: str | None = None
    official_number: str | None = None
    official_date: str | None = None
    publication_date: str | None = None
    publication: Publication | None = None
    entry_into_force_dates: list[str] = field(default_factory=list)
    # Entrada em vigor lida no texto (`leis-portugal structure`): data, regra, método…
    entry_into_force: dict[str, Any] | None = None
    end_of_validity_date: str | None = None
    legal_status: str = "unknown"
    # Proveniência de `legal_status` quando não vem do DRE, com as provas.
    legal_status_basis: dict[str, Any] | None = None
    notes: list[str] = field(default_factory=list)
    language: str = "por"
    version: Version = field(default_factory=Version)
    version_history: VersionHistory | None = None
    identifiers: Identifiers = field(default_factory=Identifiers)
    subjects: list[str] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    article_structure: ArticleStructure | None = None
    derived_material: DerivedMaterial = field(default_factory=DerivedMaterial)
    validation: Validation = field(default_factory=Validation)

    # Ordem de serialização (a do formato em disco).
    _ORDER = (
        "schema_version", "id", "title", "short_title", "summary", "jurisdiction", "territory",
        "document_type", "document_type_label", "issuing_authority", "proposing_entity",
        "official_number", "official_date", "publication_date", "publication",
        "entry_into_force_dates", "entry_into_force", "end_of_validity_date", "legal_status", "legal_status_basis", "notes", "language",
        "version", "version_history", "identifiers", "source", "integrity", "provenance", "reuse",
        "subjects", "relationships", "article_structure", "derived_material", "validation",
    )
    # Campos que só se gravam quando existem (os registos sem eles ficam como estão).
    _OMIT_WHEN_NONE = frozenset({"version_history", "entry_into_force", "legal_status_basis"})
    _BLOCKS = {
        "publication": Publication, "version": Version, "identifiers": Identifiers, "source": Source,
        "integrity": Integrity, "provenance": Provenance, "reuse": Reuse,
        "article_structure": ArticleStructure, "derived_material": DerivedMaterial, "validation": Validation,
    }

    # ------------------------------------------------------------------ serialização

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LegalRecord:
        values: dict[str, Any] = {}
        for name in cls._ORDER:
            if name not in data:
                continue
            value = data[name]
            if name in cls._BLOCKS:
                value = None if value is None else cls._BLOCKS[name].from_dict(value)
            elif name == "version_history":
                value = VersionHistory.from_dict(value)
            elif name == "relationships":
                value = [Relationship.from_dict(item) for item in value or []]
            elif isinstance(value, list):
                value = list(value)
            values[name] = value
        return cls(**values)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for name in self._ORDER:
            value = getattr(self, name)
            if name in self._OMIT_WHEN_NONE and value is None:
                continue
            if name == "relationships":
                value = [item.to_dict() for item in value]
            elif hasattr(value, "to_dict"):
                value = value.to_dict()
            elif isinstance(value, list):
                value = list(value)
            result[name] = value
        return result

    # ---------------------------------------------------------------------- regras

    @property
    def imported(self) -> bool:
        """Texto da importação inicial, ainda não recolhido diretamente da fonte."""
        return self.integrity.source_sha256_scope == IMPORTED_SCOPE

    @property
    def precedence(self) -> tuple[int, int]:
        return _KIND_RANK.get(self.version.kind, 0), 0 if self.imported else 1

    def same_document(self, other_id: str | None) -> bool:
        """O mesmo documento, aceitando o formato antigo `eu:celex:<CELEX>:<língua>:original`."""
        return bool(other_id) and (other_id == self.id or other_id.startswith(self.id + ":"))

    def note_source_gap(self, text: str, *, checked: str) -> bool:
        """Regista que a fonte não tem o texto. Devolve False se a nota já existia
        (a data da primeira verificação mantém-se, para não gerar alterações a cada recolha)."""
        if any(note.startswith(f"{SOURCE_GAP_PREFIX} {text}") for note in self.notes):
            return False
        self.notes = [note for note in self.notes if not note.startswith(SOURCE_GAP_PREFIX)]
        self.notes.append(f"{SOURCE_GAP_PREFIX} {text} (verificado em {checked}).")
        return True

    def add_relationships(self, *groups: list[Relationship] | None) -> None:
        self.relationships = merge_relationships(self.relationships, *groups)

    def copy(self, **changes: Any) -> LegalRecord:
        return replace(self, **changes)
