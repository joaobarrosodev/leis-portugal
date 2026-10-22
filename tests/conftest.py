from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


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


CONSOLIDATED = '''---
title: "Decreto-Lei n.º 140/2009 — Estabelece o regime jurídico dos estudos…"
identifier: "DRE-2009-140-494543"
country: "pt"
rank: "decreto-lei"
publication_date: "2009-06-15"
last_updated: "2024-11-23"
status: "in_force"
source: "https://data.dre.pt/eli/dec-lei/140/2009/p/cons/20241122/pt/html"
department: "Ministério da Cultura"
pdf_url: "https://files.diariodarepublica.pt/1s/2009/06/11300/0365303659.pdf"
subjects: ["Património Cultural", "Vistoria", "Vistoria"]
summary: "Estabelece o regime jurídico dos estudos"
official_number: "140/2009"
eli: "https://data.dre.pt/eli/dec-lei/140/2009/p/cons/20241122/pt/html"
surface: "cons"
series: "I"
year: "2009"
gazette_reference: "Diário da República n.º 113/2009, Série I de 2009-06-15"
gazette_number: "113"
pages: "3653 - 3659"
in_force_raw: "VIGENTE"
dre_id: "494543"
dre_link: "/dr/detalhe/decreto-lei/140-2009-494543"
consolidated_url: "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2009-207631928"
cites: "http://data.dre.pt/eli/lei/107/2001/09/08/p/dre"
cites_eu: "http://data.europa.eu/eli/dir/2016/798/oj"
last_amendment: "DRE-2024-90-897548401"
---
# Decreto-Lei n.º 140/2009 — Estabelece o regime jurídico dos estudos…

Decreto-Lei n.º 140/2009
de 15 de Junho
Preâmbulo.

###### Artigo 1.º — Objecto

Texto.
'''

ENACTED = '''---
title: "Portaria n.º 1/2009 — Atualiza o apoio…"
rank: "portaria"
publication_date: "2009-01-02"
status: "in_force"
source: "https://data.dre.pt/eli/port/1/2009/01/02/p/dre/pt/html"
text_state: "as_enacted"
summary: "Atualiza o apoio"
official_number: "1/2009"
surface: "pub"
series: "{series}"
gazette_reference: "Diário da República n.º 1/2009, Série {series} de 2009-01-02"
dre_id: "{dre_id}"
dre_link: "/dr/detalhe/portaria/1-2009-{dre_id}"
---
# Portaria n.º 1/2009 — Atualiza o apoio…

> **This is the law as enacted. Amendments are not incorporated below — each one is
> a separate file in this repository and a commit in this file's history.**

de 2 de Janeiro

| A | B |
| --- | --- |
| 1 | 2 |
'''

REGIONAL = '''---
title: "Decreto Regulamentar Regional n.º 1/2020/M — Estrutura orgânica"
rank: "decreto-regulamentar-regional"
publication_date: "2020-01-02"
status: "repealed"
source: "https://data.dre.pt/eli/decregulreg/1/2020/m/pub/pt/html"
official_number: "1/2020/M"
surface: "pub"
series: "I"
dre_id: "127657050"
dre_link: "/dr/detalhe/decreto-regulamentar-regional/1-2020-127657050"
department: "Região Autónoma da Madeira - Presidência do Governo"
---
# Decreto Regulamentar Regional n.º 1/2020/M — Estrutura orgânica

Texto regional.
'''


@pytest.fixture
def legalize_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "legalize-pt"
    files = {
        "pt/2009/DRE-2009-140-494543.md": CONSOLIDATED,
        "pt/2009/DRE-2009-1-396946.md": ENACTED.format(series="I", dre_id="396946"),
        "pt/2009/DRE-2009-1-1956122.md": ENACTED.format(series="II", dre_id="1956122"),
        "pt/2009/DRE-2009-1-2000000.md": ENACTED.format(series="I", dre_id="2000000"),
        "pt-30/2020/DRE-2020-1-127657050.md": REGIONAL,
        "pt/2009/DRE-2009-x-1.md": "---\ntitle: \"Sem id\"\n---\nCorpo\n",
    }
    for relative, content in files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    git = ["git", "-C", str(repo), "-c", "user.email=t@example.com", "-c", "user.name=t"]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "add", "."], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "fixture", "--date", "2026-10-21T00:00:00Z"], check=True,
                   env={**os.environ, "GIT_COMMITTER_DATE": "2026-10-21T00:00:00Z"})
    return repo
