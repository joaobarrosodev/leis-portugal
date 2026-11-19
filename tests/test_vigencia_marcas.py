"""Marcas de vigência por regra (`consolidacao/vigencia.py`)."""

import sys
from pathlib import Path

import pytest


PASTA = Path(__file__).resolve().parents[1] / "consolidacao"
if not (PASTA / "vigencia.py").exists():
    pytest.skip("consolidacao/ não está nesta cópia", allow_module_level=True)
sys.path.insert(0, str(PASTA))

import vigencia  # noqa: E402


def test_ultramar_so_territorio_e_sem_regimes_pessoais():
    assert vigencia.motivo_ultramar("Decreto n.º 572/72", "Aprova o Estatuto da Polícia de Segurança Pública de Moçambique").startswith("é um diploma para os territórios")
    assert "Macau" in vigencia.motivo_ultramar("Decreto-Lei n.º 411/70", "Regula o exercício das funções de crédito na província de Macau")
    assert vigencia.motivo_ultramar("Decreto n.º 52/75", "Harmoniza os regimes da aposentação dos servidores civis do Estado em serviço nos territórios ultramarinos") is None
    assert vigencia.motivo_ultramar("Portaria n.º 22869", "Torna extensivo às províncias ultramarinas o novo Código Civil") is None
    assert vigencia.motivo_ultramar("Decreto-Lei n.º 1/70", "Regula o arrendamento urbano") is None


def test_revogacao_registada_noutro_registo():
    p = vigencia.padrao_revogacao("Decreto-Lei n.º 158/96", "decreto-lei")
    assert p.search("Revogado o Decreto-Lei n.º 158/96, de 3 de Setembro, na redacção do presente diploma, pelo DEC LEI.47/2005.24.02.2005.MFAP")
    assert p.search("Revogado o Dec Lei 158/96, de 3-Set, pelo DEC LEI.47/2005")
    assert not p.search("Revogado o art. 24.º do Decreto-Lei n.º 158/96, pelo DEC LEI.1/2000")
    assert not p.search("Revogado o Decreto-Lei n.º 158/97, pelo DEC LEI.1/2000")
    q = vigencia.padrao_revogacao("Portaria n.º 132/2009", "portaria")
    assert q.search("Revogada, a partir de 29.04.2013, a Port 132/2009, de 30 de janeiro, com as alterações introduzidas pelo presente")


def test_diploma_que_revoga():
    assert vigencia._pelo("Revogada pelo(a) Portaria n.º 207/2017 - Diário da República n.º 132/2017, Série I") == "Portaria n.º 207/2017"
    assert vigencia._pelo("Revogada a concessão atribuída pelo presente diploma, pela PORT.188/99.1999.03.20.MECO, DR.IS-B [67]") == "PORT.188/99.1999.03.20.MECO"
    assert vigencia._pelo("Revogado, com as alterações introduzidas pelo DR 1/2002 de 03-Jan, pelo DEC LEI.39/2008.07.03.2008.MEI") == "DEC LEI.39/2008.07.03.2008.MEI"
