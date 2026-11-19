"""Anexos, mapas e quadros de alteradores triados «sem alteração textual» (`consolidacao/anexos_alteradores.py`)."""

import sys
from pathlib import Path

import pytest


PASTA = Path(__file__).resolve().parents[1] / "consolidacao"
if not (PASTA / "anexos_alteradores.py").exists():
    pytest.skip("consolidacao/ não está nesta cópia", allow_module_level=True)
sys.path.insert(0, str(PASTA))

import anexos_alteradores as aa  # noqa: E402


def test_rotulo_de_um_anexo_alterado():
    assert aa.ROTULO.search("Alterado o quadro de pessoal pela PORT.168/88.19.03.1988.MF")
    assert aa.ROTULO.search("Substituido o anexo II pela PORT.257/90.07.04.1990.MF")
    assert aa.ROTULO.search("ALTERADO O NUM1 E SUBSTITUÍDA A PLANTA ANEXA PELA PORT 892/94")
    assert not aa.ROTULO.search("Alterado o n.º 2 do artigo 5.º pelo DL 10/90")


def test_nota_de_alteracao():
    meta = {"title": "Portaria n.º 168/88", "publication_date": "1988-03-19", "identifiers": {"dre_path": "/dr/detalhe/portaria/168-1988-1"}}
    assert aa._nota(meta) == "> Alterado pelo/a [Portaria n.º 168/88](https://diariodarepublica.pt/dr/detalhe/portaria/168-1988-1), publicado em 1988-03-19."
