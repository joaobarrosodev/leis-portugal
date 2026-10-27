from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from sem_processos import sem_processos  # noqa: F401  (fixture autouse: threads em vez de processos)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    """Raiz de repositório isolada, com a configuração e os esquemas reais."""
    root = tmp_path / "acervo"
    root.mkdir()
    shutil.copytree(REPOSITORY_ROOT / "config", root / "config")
    shutil.copytree(REPOSITORY_ROOT / "schemas", root / "schemas")
    return root


def record_dict(record_id: str, **overrides) -> dict:
    """Metadados mínimos e válidos de um registo, para fixtures de testes."""
    base = {
        "schema_version": "1.0",
        "id": record_id,
        "title": "Registo de teste",
        "jurisdiction": "european_union" if record_id.startswith("eu:") else "portugal",
        "document_type": "directive" if record_id.startswith("eu:") else "decreto-lei",
        "language": "por",
        "version": {"kind": "original", "label": "Texto original", "language": "por", "consolidation_date": None},
        "source": {"id": "teste", "name": "Teste", "official_url": "https://example.org/", "retrieved_at": "2026-10-21T00:00:00Z", "retrieval_method": "teste"},
        "integrity": {"source_sha256": "0" * 64, "source_sha256_scope": "official_source_content_bytes"},
        "provenance": {"collector": "teste", "collector_version": "0", "generated_by": "teste", "generated_at": "2026-10-21T00:00:00Z"},
        "reuse": {"status": "permitted", "attribution": "Teste", "reference": None},
        "validation": {"status": "validated", "checked_at": "2026-10-21T00:00:00Z"},
    }
    base.update(overrides)
    return base
