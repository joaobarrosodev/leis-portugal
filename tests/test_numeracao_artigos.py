"""Títulos de artigo fora de sequência (`scripts/numeracao_artigos.py`)."""

import sys
from pathlib import Path

import pytest


PASTA = Path(__file__).resolve().parents[1] / "scripts"
if not (PASTA / "numeracao_artigos.py").exists():
    pytest.skip("scripts/ não está nesta cópia", allow_module_level=True)
sys.path.insert(0, str(PASTA))

from numeracao_artigos import suspeitas  # noqa: E402


def test_gralha_entre_dois_vizinhos():
    # DRR 2/2005/M: o DRE escreve «Artigo 212.º» entre o 20.º e o 22.º.
    assert suspeitas([19, 20, 212, 22, 23]) == [
        {"posicao": 2, "antes": 20, "lido": 212, "depois": 22, "provavel": 21, "tipo": "gralha"}
    ]


def test_numero_repetido():
    assert [s["tipo"] for s in suspeitas([1, 2, 2, 4])] == ["repetido"]


def test_numeros_trocados():
    achadas = suspeitas([80, 82, 81, 84, 83, 85])
    assert achadas and {s["tipo"] for s in achadas} == {"troca"}


def test_sequencia_certa_e_recomeco_nos_anexos():
    assert suspeitas([1, 2, 3, 4]) == []
    assert suspeitas([1, 2, 3, 1, 2, 3]) == []
