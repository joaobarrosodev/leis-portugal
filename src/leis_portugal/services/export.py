"""Exportação do acervo para pesquisa: índice de relações e tabelas de metadados.

Ficheiros em `exports/` (gerados, fora do git):

- `relationships.jsonl`: uma relação por linha (origem, tipo, alvo, alvo resolvido);
- `leis-portugal.sqlite`: tabelas `documentos` e `relacoes`, com índices para pesquisar
  nos dois sentidos ("o que altera este diploma?", "o que é que este diploma transpõe?");
- `documentos.parquet` e `relacoes.parquet`: as mesmas tabelas (precisa de `pyarrow`).

O alvo de cada relação fica como está no registo (`target`) e, ao lado, o id do
documento no acervo quando é possível resolvê-lo (`target_id`): ids `pt:dre:`/`eu:celex:`
presentes, `celex:` de atos da UE recolhidos, ELI e referências por número.
"""

from __future__ import annotations

import json
import os
import sqlite3
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from leis_portugal.domain.relations import DiplomaIndex, EliIndex, celex_from_eu_eli, diploma_key
from leis_portugal.infrastructure.markdown import read_markdown_record
from leis_portugal.infrastructure.repository import Acervo


METADATA_ONLY = "o registo tem só os metadados"
PDF_ONLY = "não está disponível em formato eletrónico"

# Colunas da tabela `documentos`, pela ordem de exportação. As listas ficam como JSON no SQLite.
DOCUMENT_COLUMNS = (
    "id", "title", "summary", "jurisdiction", "territory", "document_type", "document_type_label",
    "official_number", "official_date", "publication_date", "legal_status", "language",
    "version_kind", "consolidation_date", "version_count", "text_quality", "article_count",
    "eli", "dre", "celex", "gazette", "publication_reference", "series", "pdf_url", "official_url",
    "issuing_authority", "subjects", "retrieved_at", "path",
)
LIST_COLUMNS = frozenset({"issuing_authority", "subjects"})
INTEGER_COLUMNS = frozenset({"version_count", "article_count"})
RELATION_COLUMNS = ("source_id", "type", "target", "target_id", "date", "label")


PDF_ONLY_WARNING = "o registo liga apenas ao PDF oficial"


def text_quality(metadata: dict[str, Any], body: str = "") -> str:
    """`texto`, `pdf` (só a ligação ao PDF oficial) ou `metadados` (a fonte não tem texto nem PDF).

    Sem o corpo, o aviso da recolha (`validation.warnings`) identifica os registos só com PDF."""
    if any(METADATA_ONLY in note for note in metadata.get("notes") or []):
        return "metadados"
    warnings = (metadata.get("validation") or {}).get("warnings") or []
    if PDF_ONLY in body or any(PDF_ONLY_WARNING in warning for warning in warnings):
        return "pdf"
    return "texto"


def _row(path: str, root: str) -> tuple[dict[str, Any], list[dict[str, Any]]] | None:
    try:
        metadata, body = read_markdown_record(path)
    except (OSError, ValueError):
        return None
    identifiers = metadata.get("identifiers") or {}
    publication = metadata.get("publication") or {}
    version = metadata.get("version") or {}
    source = metadata.get("source") or {}
    document = {
        "id": metadata.get("id"),
        "title": metadata.get("title"),
        "summary": metadata.get("summary"),
        "jurisdiction": metadata.get("jurisdiction"),
        "territory": metadata.get("territory"),
        "document_type": metadata.get("document_type"),
        "document_type_label": metadata.get("document_type_label"),
        "official_number": metadata.get("official_number"),
        "official_date": metadata.get("official_date"),
        "publication_date": metadata.get("publication_date"),
        "legal_status": metadata.get("legal_status"),
        "language": metadata.get("language"),
        "version_kind": version.get("kind"),
        "consolidation_date": version.get("consolidation_date"),
        "version_count": (metadata.get("version_history") or {}).get("count"),
        "text_quality": text_quality(metadata, body),
        "article_count": (metadata.get("article_structure") or {}).get("article_count"),
        "eli": identifiers.get("eli"),
        "dre": identifiers.get("dre"),
        "celex": identifiers.get("celex"),
        "gazette": publication.get("gazette"),
        "publication_reference": publication.get("reference"),
        "series": publication.get("series"),
        "pdf_url": publication.get("pdf_url"),
        "official_url": source.get("official_url"),
        "issuing_authority": list(metadata.get("issuing_authority") or []),
        "subjects": list(metadata.get("subjects") or []),
        "retrieved_at": source.get("retrieved_at"),
        "path": os.path.relpath(path, root),
    }
    relations = [
        {
            "source_id": document["id"],
            "type": relation.get("type"),
            "target": relation.get("target"),
            "date": relation.get("date"),
            "label": relation.get("label"),
        }
        for relation in metadata.get("relationships") or []
    ]
    return document, relations


class TargetResolver:
    """Alvo de uma relação -> id de um documento do acervo (ou None)."""

    def __init__(self, documents: list[dict[str, Any]], eli_codes: dict[str, str] | None = None) -> None:
        self.ids = {document["id"] for document in documents}
        self.by_eli = EliIndex([(document["id"], document["eli"]) for document in documents if document.get("eli")])
        self.by_celex = {document["celex"]: document["id"] for document in documents if document.get("celex")}
        self.diplomas = DiplomaIndex(eli_codes)
        for document in documents:
            if document.get("jurisdiction") in ("portugal", "regional"):
                key = diploma_key(
                    document.get("document_type"), document.get("official_number"),
                    publication_date=document.get("publication_date"), territory=document.get("territory"),
                )
                self.diplomas.add(document["id"], key, publication_date=document.get("publication_date"), series=document.get("series"))

    def __call__(self, target: str | None) -> str | None:
        if not target:
            return None
        if target in self.ids:
            return target
        if target.startswith("celex:"):
            return self.by_celex.get(target.removeprefix("celex:"))
        if target.startswith("eli:"):
            eu = celex_from_eu_eli(target)
            if eu:
                return self.by_celex.get(eu)
            return self.by_eli.get(target) or self.diplomas.from_eli(target)
        if target.startswith("pt:numero:"):
            return self.diplomas.from_number(target)
        return None


@dataclass
class ExportSummary:
    documents: int = 0
    relations: int = 0
    resolved: int = 0
    by_target: Counter = field(default_factory=Counter)
    files: list[Path] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


def _target_kind(target: str) -> str:
    for prefix in ("pt:dre:", "eu:celex:", "celex:", "eli:", "pt:numero:"):
        if target.startswith(prefix):
            return prefix.rstrip(":")
    return "outro"


def read_acervo(acervo: Acervo, *, workers: int | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    paths = [str(path) for path in acervo.paths()]
    root = str(acervo.root)
    documents: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=workers or max(1, (os.cpu_count() or 2) - 1)) as pool:
        for row in pool.map(_row, paths, [root] * len(paths), chunksize=256):
            if row:
                documents.append(row[0])
                relations.extend(row[1])
    return documents, relations


def _write_jsonl(path: Path, relations: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for relation in relations:
            handle.write(json.dumps(relation, ensure_ascii=False) + "\n")


def _sql_value(column: str, value: Any) -> Any:
    return json.dumps(value, ensure_ascii=False) if column in LIST_COLUMNS else value


def _write_sqlite(path: Path, documents: list[dict[str, Any]], relations: list[dict[str, Any]]) -> None:
    path.unlink(missing_ok=True)
    with sqlite3.connect(path) as connection:
        columns = ", ".join(f"{column} {'INTEGER' if column in INTEGER_COLUMNS else 'TEXT'}" for column in DOCUMENT_COLUMNS)
        connection.execute(f"CREATE TABLE documentos ({columns}, PRIMARY KEY (id))")
        connection.execute(f"CREATE TABLE relacoes ({', '.join(f'{column} TEXT' for column in RELATION_COLUMNS)})")
        connection.executemany(
            f"INSERT INTO documentos VALUES ({', '.join('?' for _ in DOCUMENT_COLUMNS)})",
            ([_sql_value(column, document.get(column)) for column in DOCUMENT_COLUMNS] for document in documents),
        )
        connection.executemany(
            f"INSERT INTO relacoes VALUES ({', '.join('?' for _ in RELATION_COLUMNS)})",
            ([relation.get(column) for column in RELATION_COLUMNS] for relation in relations),
        )
        for name, table, column in (
            ("relacoes_origem", "relacoes", "source_id"),
            ("relacoes_alvo", "relacoes", "target_id"),
            ("relacoes_tipo", "relacoes", "type"),
            ("documentos_tipo", "documentos", "document_type"),
            ("documentos_publicacao", "documentos", "publication_date"),
        ):
            connection.execute(f"CREATE INDEX {name} ON {table} ({column})")


def _write_parquet(directory: Path, documents: list[dict[str, Any]], relations: list[dict[str, Any]]) -> list[Path]:
    import pyarrow as pa
    import pyarrow.parquet as pq

    written = []
    for name, rows, columns in (("documentos", documents, DOCUMENT_COLUMNS), ("relacoes", relations, RELATION_COLUMNS)):
        table = pa.Table.from_pylist([{column: row.get(column) for column in columns} for row in rows])
        path = directory / f"{name}.parquet"
        pq.write_table(table, path, compression="zstd")
        written.append(path)
    return written


def parquet_available() -> bool:
    try:
        import pyarrow.parquet  # noqa: F401
    except ImportError:
        return False
    return True


def export_acervo(
    acervo: Acervo,
    output: Path,
    *,
    formats: tuple[str, ...] = ("jsonl", "sqlite", "parquet"),
    workers: int | None = None,
) -> ExportSummary:
    """Lê todos os registos e escreve o índice de relações e as tabelas pedidas."""
    documents, relations = read_acervo(acervo, workers=workers)
    resolve = TargetResolver(documents, acervo.types.eli_codes)
    for relation in relations:
        relation["target_id"] = resolve(relation["target"])
    documents.sort(key=lambda document: document["id"] or "")
    relations.sort(key=lambda relation: (relation["source_id"] or "", relation["type"] or "", relation["target"] or ""))
    relations = [{column: relation.get(column) for column in RELATION_COLUMNS} for relation in relations]

    summary = ExportSummary(documents=len(documents), relations=len(relations))
    summary.resolved = sum(1 for relation in relations if relation["target_id"])
    summary.by_target = Counter((_target_kind(relation["target"] or ""), bool(relation["target_id"])) for relation in relations)
    output.mkdir(parents=True, exist_ok=True)
    if "jsonl" in formats:
        _write_jsonl(output / "relationships.jsonl", relations)
        summary.files.append(output / "relationships.jsonl")
    if "sqlite" in formats:
        _write_sqlite(output / "leis-portugal.sqlite", documents, relations)
        summary.files.append(output / "leis-portugal.sqlite")
    if "parquet" in formats:
        if parquet_available():
            summary.files.extend(_write_parquet(output, documents, relations))
        else:
            summary.skipped.append("parquet (instalar com: pip install -e '.[export]')")
    return summary
