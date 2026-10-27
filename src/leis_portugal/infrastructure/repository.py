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
from leis_portugal.domain.history import FRAGMENT_BLOCK_BYTES, FRAGMENT_BLOCK_SCHEMA, HISTORY_MAX_BYTES, fragment_sizes, split_fragments
from leis_portugal.domain.identifiers import parse_celex, slugify
from leis_portugal.domain.record import LegalRecord, Relationship, merge_relationships
from leis_portugal.errors import InvalidRecord, StorageError
from leis_portugal.infrastructure.config import load_document_types
from leis_portugal.infrastructure.markdown import read_markdown_record, read_record_id, render_markdown, write_if_changed
from leis_portugal.infrastructure.schema import SchemaValidator


HISTORY_SUFFIX = ".versoes.json"
HISTORY_BLOCKS_SUFFIX = ".versoes"
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

    def locate(self, record: LegalRecord) -> Path:
        """Onde gravar um registo: o ficheiro onde já está (mesmo que o caminho canónico
        tenha mudado, p. ex. numeração escrita de outra forma) ou um caminho novo."""
        preferred = self.path_for(record)
        if preferred.exists() and record.same_document(read_record_id(preferred)):
            return preferred
        known = self.index().get(record.id)
        if known is not None and known.exists():
            return known
        return self.resolve_target(record)

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
        target = target or self.locate(record)

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
                _preserve_derived(record, existing)
                _preserve_timestamps(record, existing)

        if policy.enrich:
            policy.enrich(record, body)
        changed = write_if_changed(target, render_markdown(record.to_dict(), body))
        self.remember(record.id, target)
        if action == "written" and not changed:
            action = "unchanged"
        return WriteResult(path=target, action=action, warnings=list(record.validation.warnings))

    # ------------------------------------------------------------ histórico de versões

    def history_blocks_path(self, record_path: Path) -> Path:
        return record_path.with_name(record_path.stem + HISTORY_BLOCKS_SUFFIX)

    def read_history(self, record_path: Path) -> dict[str, Any] | None:
        """O histórico completo, com os fragmentos dos blocos quando está dividido."""
        path = self.history_path(record_path)
        if not path.exists():
            return None
        history = json.loads(path.read_text(encoding="utf-8"))
        if "fragment_blocks" not in history:
            return history
        fragments: dict[str, Any] = {}
        for name in history["fragment_blocks"]:
            fragments.update(json.loads((path.parent / name).read_text(encoding="utf-8"))["fragments"])
        return _rename_key(history, "fragment_blocks", "fragments", fragments)

    @staticmethod
    def render_history(history: dict[str, Any]) -> str:
        return json.dumps(history, ensure_ascii=False, indent=1) + "\n"

    def write_history(self, record_path: Path, history: dict[str, Any]) -> bool:
        """Grava o histórico num só ficheiro ou, se passar de `HISTORY_MAX_BYTES`, num
        índice e em blocos de fragmentos (ver `leis_portugal.domain.history`)."""
        path = self.history_path(record_path)
        blocks_dir = self.history_blocks_path(record_path)
        fragments = history.get("fragments") or {}
        sizes = fragment_sizes(fragments)
        index_bytes = len(self.render_history({key: value for key, value in history.items() if key != "fragments"}).encode("utf-8"))
        if index_bytes + sum(sizes.values()) <= HISTORY_MAX_BYTES:
            changed = write_if_changed(path, self.render_history(history))
            names: list[str] = []
        else:
            names = []
            changed = False
            for number, block in enumerate(split_fragments(fragments, sizes, FRAGMENT_BLOCK_BYTES), start=1):
                names.append(f"{blocks_dir.name}/{number:03d}.json")
                content = {"schema": FRAGMENT_BLOCK_SCHEMA, "id": history.get("id"), "fragments": block}
                changed |= write_if_changed(path.parent / names[-1], self.render_history(content))
            # Os blocos primeiro e o índice no fim: o índice nunca aponta para um bloco por gravar.
            changed |= write_if_changed(path, self.render_history(_rename_key(history, "fragments", "fragment_blocks", names)))
        # Blocos que deixaram de ser usados (menos blocos, ou o histórico voltou a caber num ficheiro).
        if blocks_dir.is_dir():
            for stale in sorted(blocks_dir.glob("*.json")):
                if f"{blocks_dir.name}/{stale.name}" not in names:
                    stale.unlink()
                    changed = True
            if not any(blocks_dir.iterdir()):
                blocks_dir.rmdir()
        return changed

    def histories(self) -> Iterator[tuple[Path, dict[str, Any]]]:
        """Cada ficheiro de histórico como está gravado: num histórico dividido em blocos,
        só o índice (sem os fragmentos)."""
        for path in sorted(self.data.rglob(f"*{HISTORY_SUFFIX}")):
            try:
                yield path, json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue


def _rename_key(data: dict[str, Any], old: str, new: str, value: Any) -> dict[str, Any]:
    """Cópia de `data` com `old` trocado por `new` (e `value`) na mesma posição."""
    return {new if key == old else key: value if key == old else item for key, item in data.items()}


def _preserve_derived(new: LegalRecord, existing: LegalRecord) -> None:
    """O que `leis-portugal structure` tirou do texto e a fonte não traz: a entrada em vigor
    e o estado de vigência provado, enquanto a fonte não indicar outro estado."""
    if new.entry_into_force is None and existing.entry_into_force is not None:
        new.entry_into_force = existing.entry_into_force
        if not new.entry_into_force_dates:
            new.entry_into_force_dates = list(existing.entry_into_force_dates)
    if new.legal_status == "unknown" and existing.legal_status_basis:
        new.legal_status, new.legal_status_basis = existing.legal_status, existing.legal_status_basis


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
