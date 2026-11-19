"""Onde estão os dados e como se leem os artigos de um registo.

A leitura dos artigos fica toda em `ler_artigos`: hoje usa `avaliacao/comum.py`; quando o
parser da fase 3 estiver pronto, troca-se só esta função.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
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


_REVOGADO = re.compile(r"^\(?\s*revogad[oa]", re.I)


_PUBLICADO_EM = re.compile(r"Série [^,\]]*?de (\d{4}-\d{2}-\d{2})")
_EM_VIGOR_DESDE = re.compile(r"em vigor a partir de (\d{4}-\d{2}-\d{2})")


def revogado(texto: str, notas: str) -> bool:
    """O artigo está revogado: o texto é "(Revogado.)" ou uma nota diz "Revogado pelo/a …".

    Nos consolidados do DRE, um artigo revogado fica muitas vezes com o texto antigo e só ganha a
    nota (p. ex. os do Código do Trabalho de 2003, revogados pela Lei n.º 7/2009). Conta a nota de
    revogação mais recente: se uma nota com data posterior o altera (o artigo foi reposto, como os
    do arrendamento do Código Civil, revogados em 1975 e repostos pela Lei n.º 6/2006), já não está."""
    if _REVOGADO.match(texto.strip()):
        return True
    linhas = [n.strip() for n in notas.splitlines() if n.strip()]
    revogacoes = [n for n in linhas if _REVOGADO.match(n)]
    if not revogacoes:
        return False
    def data(nota: str) -> str | None:
        # A data de publicação do diploma que altera ou revoga ("… Série I de 2013-12-31"); a de entrada em
        # vigor engana às vezes (uma revogação de 2013 "em vigor a partir de 2004-01-01"). Sem ela, a de
        # entrada em vigor. Uma data impossível (1079-01-01, gralha do DRE por 1979) conta como sem data.
        m = _PUBLICADO_EM.search(nota) or _EM_VIGOR_DESDE.search(nota)
        return m.group(1) if m and m.group(1) >= "1800" else None

    datas_revogacao = [data(n) for n in revogacoes]
    if None in datas_revogacao:
        return True  # sem data não se sabe a ordem: fica revogado, como antes
    ultima_revogacao = max(datas_revogacao)
    return not any((d := data(n)) and d > ultima_revogacao for n in linhas if not _REVOGADO.match(n))


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
