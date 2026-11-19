"""Vigência revista: diplomas que o DRE dá como em vigor mas que já não vigoram (ou cujo regime mudou).

A marca vem de `consolidacao/auditoria/vigencia-revista.jsonl` (`consolidacao/vigencia.py`), uma
linha por diploma:

- `marca`: `nao_vigora` (revogado, caducado ou substituído, com prova) ou `regime_anterior`
  (cursos e graus anteriores ao DL 74/2006, sem se afirmar que caducaram);
- `motivo`: a frase do aviso;
- `prova` e `fonte`: de onde vem (uma relação do DRE, um diploma do acervo, uma leitura).

A pesquisa (`rag.pesquisa`) junta o aviso aos resultados destes diplomas. Baixar-lhes a posição
fica atrás de `RAG_VIGENCIA_PRIOR` (desligado por omissão), para se medir antes.

O ficheiro lê-se da pasta do índice (`RAG_INDICE`/vigencia-revista.jsonl) ou, se lá não estiver,
do repositório; sem nenhum dos dois, não há marcas. Não muda o índice.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from rag.fontes import PASTA_INDICE, RAIZ


NOME = "vigencia-revista.jsonl"
NO_REPOSITORIO = RAIZ / "consolidacao" / "auditoria" / NOME
# Peso no prior da pesquisa em todo o acervo para `nao_vigora`, só com RAG_VIGENCIA_PRIOR=1.
PRIOR_NAO_VIGORA = 0.6


def caminho() -> Path | None:
    for candidato in (PASTA_INDICE / NOME, NO_REPOSITORIO):
        if candidato.exists():
            return candidato
    return None


@lru_cache(maxsize=4)
def _carregar(texto: str) -> dict[str, dict]:
    marcas = {}
    for linha in texto.splitlines():
        if linha.strip():
            m = json.loads(linha)
            marcas[m["id"]] = m
    return marcas


def marcas(ficheiro: Path | None = None) -> dict[str, dict]:
    ficheiro = ficheiro or caminho()
    return _carregar(ficheiro.read_text(encoding="utf-8")) if ficheiro else {}


def aviso(marca: dict) -> str:
    if marca["marca"] == "regime_anterior":
        return f"Regime anterior ao Decreto-Lei n.º 74/2006 (Bolonha): {marca['motivo']}"
    return f"O DRE dá-o como em vigor, mas {marca['motivo']}"


def prior_ligado() -> bool:
    return os.environ.get("RAG_VIGENCIA_PRIOR", "").strip().lower() in ("1", "true", "sim", "yes")
