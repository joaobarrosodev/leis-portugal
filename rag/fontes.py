"""Onde estão os dados e como se leem os artigos de um registo.

A leitura dos artigos fica toda em `ler_artigos`: hoje usa `avaliacao/comum.py`; quando o
parser da fase 3 estiver pronto, troca-se só esta função.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any


RAIZ = Path(__file__).resolve().parents[1]
PASTA_INDICE = Path(os.environ.get("RAG_INDICE", RAIZ / "rag" / "indice"))

_spec = importlib.util.spec_from_file_location("avaliacao_comum", RAIZ / "avaliacao" / "comum.py")
comum = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = comum
_spec.loader.exec_module(comum)  # type: ignore[union-attr]

Artigo = comum.Artigo
corpo = comum.corpo
normalizar = comum.normalizar


def ler_artigos(texto: str) -> list[Artigo]:
    """Os artigos do corpo de um registo (sem o cabeçalho YAML), pela ordem do texto."""
    return comum.artigos(texto)


def export_sqlite() -> Path:
    """O `exports/leis-portugal.sqlite`: na raiz, ou na pasta principal quando se corre numa worktree."""
    if os.environ.get("RAG_EXPORT"):
        return Path(os.environ["RAG_EXPORT"])
    for pasta in (RAIZ, *RAIZ.parents):
        candidato = pasta / "exports" / "leis-portugal.sqlite"
        if candidato.exists():
            return candidato
    raise FileNotFoundError("exports/leis-portugal.sqlite não encontrado; corre `leis-portugal export` ou define RAG_EXPORT")


def ler_historico(caminho_md: Path) -> dict[str, Any] | None:
    """O `.versoes.json` de um registo, com os fragmentos dos blocos quando está dividido."""
    caminho = caminho_md.with_suffix(".versoes.json")
    if not caminho.exists():
        return None
    historico = json.loads(caminho.read_text(encoding="utf-8"))
    if "fragment_blocks" in historico:
        fragmentos: dict[str, Any] = {}
        for nome in historico.pop("fragment_blocks"):
            fragmentos.update(json.loads((caminho.parent / nome).read_text(encoding="utf-8"))["fragments"])
        historico["fragments"] = fragmentos
    return historico


def texto_da_versao(historico: dict[str, Any], versao: dict[str, Any]) -> str:
    """O corpo de uma versão: a concatenação dos seus fragmentos (como `render_version`, sem título)."""
    fragmentos = historico["fragments"]
    return "\n\n".join(fragmentos[chave]["markdown"] for chave in versao["fragments"] if fragmentos[chave]["markdown"])
