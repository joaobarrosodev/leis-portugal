"""Repositório do acervo: onde e como os registos vivem em disco.

Concentra a estrutura de pastas, o índice id -> ficheiro, a leitura e a escrita
(com validação, colisões, precedência entre fontes e preservação de datas) e os
ficheiros de histórico de versões. Os serviços não tocam no sistema de ficheiros
diretamente.
"""

from __future__ import annotations

import json
import os
import threading
from collections.abc import Callable, Iterator
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from leis_portugal.domain.document_types import DocumentTypeRegistry
from leis_portugal.domain.identifiers import parse_celex, slugify
from leis_portugal.domain.record import LegalRecord, Relationship, merge_relationships
from leis_portugal.errors import InvalidRecord, StorageError
from leis_portugal.infrastructure.config import load_document_types
from leis_portugal.infrastructure.markdown import read_markdown_record, read_record_id, render_markdown, write_if_changed
from leis_portugal.infrastructure.schema import SchemaValidator


HISTORY_SUFFIX = ".versoes.json"
PORTUGUESE_SCOPES = ("portugal", "regional")
EU_SCOPE = "european_union"
_EU_DIRECTORIES = {"regulation": "regulations", "directive": "directives", "decision": "decisions", "treaty": "treaties"}


@dataclass(frozen=True)
class WriteResult:
    path: Path
    action: str  # "written", "unchanged", "kept_existing"
    warnings: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return self.action == "written"


@dataclass(frozen=True)
class SavePolicy:
    """Como juntar um registo novo com o que já está em disco.

    - `keep_relationship`: que relações do registo existente se mantêm;
    - `respect_precedence`: se um registo existente com mais precedência (p. ex.
      texto consolidado) se mantém, recebendo só relações e descritores novos;
    - `enrich`: ajuste final sobre o registo e o texto que ficam (p. ex. relações
      detetadas no texto).
    """

    keep_relationship: Callable[[Relationship], bool] = lambda _relation: True
    respect_precedence: bool = True
    enrich: Callable[[LegalRecord, str], None] | None = None


DEFAULT_POLICY = SavePolicy()


def _scan_id(path: str) -> tuple[str | None, str]:
    return read_record_id(path), path


class Acervo:
    """O acervo em disco, a partir da raiz do repositório."""

    def __init__(self, root: str | Path, *, types: DocumentTypeRegistry | None = None) -> None:
        self.root = Path(root).resolve()
        self.data = self.root / "data"
        self.types = types or load_document_types(self.root)
        self.schema = SchemaValidator(self.root)
        self._index: dict[str, Path] | None = None
        self._lock = threading.Lock()

    # --------------------------------------------------------------------- caminhos

    def relative(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()

    def path_for(self, record: LegalRecord, *, disambiguate: bool = False) -> Path:
        """Caminho canónico de um registo."""
        if record.jurisdiction == EU_SCOPE:
            year = parse_celex(record.identifiers.celex).year if record.identifiers.celex else int((record.official_date or "0")[:4])
            directory = _EU_DIRECTORIES.get(record.document_type, "other")
            # O nome usa o tipo base ("Regulamento"), não o subtipo ("Regulamento Delegado"),
            # para se manter estável entre recolhas.
            label = (record.document_type_label or record.document_type).split(" ")[0]
            slug = slugify(f"{label} UE {record.official_number or 'sem-numero'}")
            return self.data / EU_SCOPE / directory / str(year) / f"{slug}.md"

        document_type = self.types.resolve(record.document_type)
        year = (record.publication_date or record.official_date or "0000")[:4]
        dre_id = record.identifiers.dre
        if record.official_number:
            stem = slugify(f"{document_type.slug} {record.official_number}")
        else:
            stem = slugify(f"{document_type.slug} {record.publication_date or 'sem-data'} {dre_id}")
        if disambiguate and dre_id and not stem.endswith(str(dre_id)):
            stem = f"{stem}-{dre_id}"
        base = self.data / "regional" / record.territory if record.territory else self.data / "portugal"
        # A 2.ª Série tem numeração própria (Portaria n.º 1/2009 existe nas duas séries).
        series = str((record.publication.series if record.publication else None) or "I").strip().upper()
        if series not in {"", "I"}:
            base = base / f"serie-{slugify(series)}"
        return base / document_type.path / year / f"{stem}.md"

    def resolve_target(self, record: LegalRecord) -> Path:
        """Caminho onde gravar; desambigua com o id do DRE se outro diploma já o ocupa."""
        preferred = self.path_for(record)
        occupant = read_record_id(preferred) if preferred.exists() else None
        if occupant is None or record.same_document(occupant) or record.jurisdiction == EU_SCOPE:
            return preferred
        alternative = self.path_for(record, disambiguate=True)
        occupant = read_record_id(alternative) if alternative.exists() else None
        if occupant is not None and not record.same_document(occupant):
            raise StorageError(f"Colisão de caminho: {alternative} já contém {occupant}")
        return alternative

    def history_path(self, record_path: Path) -> Path:
        return record_path.with_name(record_path.stem + HISTORY_SUFFIX)

    # ---------------------------------------------------------------------- leitura

    def read(self, path: Path) -> tuple[LegalRecord, str]:
        metadata, body = read_markdown_record(path)
        return LegalRecord.from_dict(metadata), body

    def paths(self, scopes: tuple[str, ...] = (*PORTUGUESE_SCOPES, EU_SCOPE)) -> list[Path]:
        return sorted(path for scope in scopes for path in (self.data / scope).rglob("*.md"))

    def index(self, *, workers: int | None = None) -> dict[str, Path]:
        """id -> ficheiro de todos os registos (lido uma vez por instância)."""
        with self._lock:
            if self._index is None:
                paths = [str(path) for path in self.paths()]
                index: dict[str, Path] = {}
                with ProcessPoolExecutor(max_workers=workers or max(1, (os.cpu_count() or 2) - 1)) as pool:
                    for record_id, path in pool.map(_scan_id, paths, chunksize=512):
                        if record_id:
                            index[record_id] = Path(path)
                self._index = index
            return self._index

    def remember(self, record_id: str, path: Path) -> None:
        with self._lock:
            if self._index is not None:
                self._index[record_id] = path

    def find(self, reference: str) -> Path | None:
        """Um registo por caminho ou por id (`pt:dre:<id>:por`, `eu:celex:<CELEX>:por`)."""
        candidate = Path(reference)
        if not candidate.is_absolute():
            candidate = self.root / candidate
        if candidate.exists():
            return candidate
        return self.index().get(reference)

    def eu_records(self) -> dict[str, Path]:
        """CELEX -> ficheiro, para os atos da UE presentes."""
        records: dict[str, Path] = {}
        for path in self.paths((EU_SCOPE,)):
            record, _ = self.read(path)
            if record.identifiers.celex:
                records[record.identifiers.celex] = path
        return records

    def iter_front_matter(self, scopes: tuple[str, ...] = (*PORTUGUESE_SCOPES, EU_SCOPE)) -> Iterator[tuple[Path, dict[str, Any]]]:
        for path in self.paths(scopes):
            metadata, _ = read_markdown_record(path)
            yield path, metadata

    # ---------------------------------------------------------------------- escrita

    def validate(self, record: LegalRecord) -> None:
        record.validation.errors = []
        errors = self.schema.record_errors(record.to_dict())
        if errors:
            raise InvalidRecord(f"{record.id}: metadados inválidos: " + "; ".join(errors))
        record.validation.status = "validated"

    def write(self, record: LegalRecord, body: str, path: Path) -> bool:
        """Valida e grava tal como está (sem juntar com o existente)."""
        self.validate(record)
        changed = write_if_changed(path, render_markdown(record.to_dict(), body))
        self.remember(record.id, path)
        return changed

    def save(self, record: LegalRecord, body: str, *, target: Path | None = None, policy: SavePolicy = DEFAULT_POLICY) -> WriteResult:
        """Grava um registo, juntando-o com o que já existe no mesmo caminho."""
        record.add_relationships()
        self.validate(record)
        target = target or self.resolve_target(record)

        action = "written"
        if target.exists():
            existing, existing_body = self.read(target)
            if not record.same_document(existing.id):
                raise StorageError(f"Colisão de caminho: {target} já contém {existing.id}")
            kept = [relation for relation in existing.relationships if policy.keep_relationship(relation)]
            if policy.respect_precedence and existing.precedence > record.precedence:
                # Ex.: o texto consolidado já está gravado e a fonte só tem o texto publicado.
                existing.add_relationships(record.relationships)
                if record.subjects and not existing.subjects:
                    existing.subjects = record.subjects
                record, body, action = existing, existing_body, "kept_existing"
            else:
                record.relationships = merge_relationships(kept, record.relationships)
                if existing.subjects and not record.subjects:
                    record.subjects = existing.subjects
                _preserve_timestamps(record, existing)

        if policy.enrich:
            policy.enrich(record, body)
        changed = write_if_changed(target, render_markdown(record.to_dict(), body))
        self.remember(record.id, target)
        if action == "written" and not changed:
            action = "unchanged"
        return WriteResult(path=target, action=action, warnings=list(record.validation.warnings))

    # ------------------------------------------------------------ histórico de versões

    def read_history(self, record_path: Path) -> dict[str, Any] | None:
        path = self.history_path(record_path)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def render_history(history: dict[str, Any]) -> str:
        return json.dumps(history, ensure_ascii=False, indent=1) + "\n"

    def write_history(self, record_path: Path, history: dict[str, Any]) -> bool:
        return write_if_changed(self.history_path(record_path), self.render_history(history))

    def histories(self) -> Iterator[tuple[Path, dict[str, Any]]]:
        for path in sorted(self.data.rglob(f"*{HISTORY_SUFFIX}")):
            try:
                yield path, json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue


def _preserve_timestamps(new: LegalRecord, existing: LegalRecord) -> None:
    """Sem mudança nos bytes da fonte, uma nova recolha não gera diffs só de datas."""
    if (
        existing.integrity.source_sha256 != new.integrity.source_sha256
        or existing.source.id != new.source.id
        or existing.source.source_modified_at != new.source.source_modified_at
    ):
        return
    new.source.retrieved_at = existing.source.retrieved_at
    new.provenance.generated_at = existing.provenance.generated_at
    new.validation.checked_at = existing.validation.checked_at
