"""Termos para o BM25: minúsculas, sem palavras vazias, radical (Snowball português) e sem acentos.

O índice e as perguntas têm de passar pela mesma função; o nome do método fica gravado no
índice (`metodo_termos`) e a pesquisa recusa um índice feito com outro.
"""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache


try:
    from py_rust_stemmers import SnowballStemmer

    _stemmer = SnowballStemmer("portuguese")
    METODO = "snowball-pt"
except ImportError:  # pragma: no cover - sem o extra `rag`
    _stemmer = None
    METODO = "sufixos-leves"

_PALAVRA = re.compile(r"\w+", re.UNICODE)

VAZIAS = frozenset(
    """
    a à ao aos as às o os um uma uns umas de do da dos das dum duma em no na nos nas num numa
    por pelo pela pelos pelas para pra com sem sob sobre entre até após ante e ou nem mas que se
    é são ser foi era há tem têm ter sua seu suas seus sua lhe lhes ele ela eles elas isto isso
    aquilo este esta estes estas esse essa esses essas aquele aquela aqueles aquelas qual quais
    quando onde como quem cujo cuja mais menos muito muita já não sim também só pode podem deve
    devem segundo nº n º ª
    """.split()
)


def sem_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def _leve(palavra: str) -> str:
    for sufixo, troca in (("ções", "ção"), ("ões", "ão"), ("ais", "al"), ("eis", "el"), ("res", "r"), ("es", "e"), ("s", "")):
        if palavra.endswith(sufixo) and len(palavra) > len(sufixo) + 2:
            return palavra[: -len(sufixo)] + troca
    return palavra


@lru_cache(maxsize=2_000_000)
def radical(palavra: str) -> str:
    if palavra.isdigit():
        return palavra
    base = _stemmer.stem_word(palavra) if _stemmer is not None else _leve(palavra)
    return sem_acentos(base)


def termos(texto: str) -> list[str]:
    """Os termos de um texto, pela ordem, já normalizados."""
    return [radical(p) for p in _PALAVRA.findall(texto.lower()) if p not in VAZIAS and len(p) < 40]
