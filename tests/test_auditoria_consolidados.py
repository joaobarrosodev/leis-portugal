"""Auditoria dos consolidados: retificações fora da cadeia e classes de vigência (`consolidacao/auditoria.py`)."""

import sys
from pathlib import Path

import pytest


PASTA = Path(__file__).resolve().parents[1] / "consolidacao"
if not (PASTA / "auditoria.py").exists():
    pytest.skip("consolidacao/ não está nesta cópia", allow_module_level=True)
sys.path.insert(0, str(PASTA))

import auditoria  # noqa: E402
from texto import normalizar  # noqa: E402


RETIFICACAO = """Declara-se que o Decreto Regulamentar n.º 84-A/2007, publicado no suplemento ao Diário da República,
saiu com uma inexactidão, que assim se rectifica:

No n.º 2 do artigo 52.º, onde se lê:

«O disposto no número anterior aplica-se às candidaturas apresentadas até 31 de Janeiro de 2008.»

deve ler-se:

«O disposto no número anterior aplica-se às candidaturas apresentadas até 31 de Março de 2008.»
"""


def test_pares_em_paragrafos_seguidos():
    pares = auditoria.pares(RETIFICACAO)
    assert len(pares) == 1
    assert pares[0]["antes"].endswith("31 de Janeiro de 2008.")
    assert pares[0]["depois"].endswith("31 de Março de 2008.")


def test_reticencias_saem_das_pontas():
    pares = auditoria.pares("No artigo 38.º, onde se lê: «... e coplementado, conforme ...», deve ler-se: «... e complementado, conforme ...»")
    assert [(p["antes"], p["depois"]) for p in pares] == [("e coplementado, conforme", "e complementado, conforme")]
    assert pares[0]["localizador"].strip() == "No artigo 38.º,"


def test_classes_da_retificacao():
    em_vigor = normalizar("Artigo 52.º 2 - O disposto no número anterior aplica-se às candidaturas apresentadas até 31 de Janeiro de 2008.")
    titulo = "Decreto Regulamentar n.º 84-A/2007"
    assert auditoria.classificar_retificacao(RETIFICACAO, titulo, em_vigor, em_vigor, titulo)["classe"] == "por_regra"
    ja = em_vigor.replace("Janeiro", "Março")
    assert auditoria.classificar_retificacao(RETIFICACAO, titulo, ja, em_vigor, titulo)["classe"] == "ja_no_texto"
    reescrito = normalizar("Artigo 52.º 2 - (Revogado.)")
    assert auditoria.classificar_retificacao(RETIFICACAO, titulo, reescrito, em_vigor, titulo)["classe"] == "substituida"
    # O DRE liga a retificação a um diploma que ela não menciona.
    assert auditoria.classificar_retificacao(RETIFICACAO, "Decreto Regulamentar n.º 85/2007", em_vigor, em_vigor, "")["classe"] == "outro_diploma"
    mapa = "O Decreto-Lei n.º 436/73 saiu com inexactidão no mapa, pelo que se procede de novo à sua publicação: (ver documento original)"
    assert auditoria.classificar_retificacao(mapa, "Decreto-Lei n.º 436/73", em_vigor, em_vigor, "")["classe"] == "imagem_ou_republicacao"


def test_mencao_so_pelo_numero():
    assert auditoria.menciona("o despacho n.º 10 910/2009, do Secretário de Estado", "Despacho n.º 10910/2009")
    assert auditoria.menciona("o Decreto-Lei n.º 317/75, de 27 de Junho", "Decreto n.º 317/75")
    assert auditoria.menciona("a Portaria n.º 667-X3/1993", "Portaria n.º 667-X3/93")
    assert not auditoria.menciona("no Decreto-Lei n.º 677/76, de 1 de Setembro", "Decreto n.º 678/76")


def test_classes_de_vigencia():
    caca = auditoria.classe_vigencia("Portaria n.º 705/91", "Sujeita ao regime cinegético especial vários prédios rústicos sitos nas freguesias de Alfeizerão", "portaria", "1991-07-15")
    assert caca == ("caca", "alta")
    taxas = auditoria.classe_vigencia("Portaria n.º 1241/90", "Define as condições e o montante das taxas a pagar pelos concessionários de zonas de caça turística", "portaria", "1990-12-31")
    assert taxas == ("caca", "incerta")
    mestrado = auditoria.classe_vigencia("Portaria n.º 176/98", "Autoriza o Instituto Superior de Matemática e Gestão de Lisboa a conceder o grau de mestre", "portaria", "1998-03-17")
    assert mestrado == ("cursos_pre_bolonha", "alta")
    depois = auditoria.classe_vigencia("Portaria n.º 1/2010", "Autoriza a Universidade X a conceder o grau de mestre", "portaria", "2010-01-01")
    assert depois == (None, None)
    prova = auditoria.classe_vigencia("Portaria n.º 1171/91", "Regulamenta a inscrição na prova geral de acesso ao ensino superior de 1992", "portaria", "1991-11-15")
    assert prova == ("um_so_ano", "alta")
    # Um número de diploma não é um ano.
    lei = auditoria.classe_vigencia("Decreto-Lei n.º 1/2001", "Regulamenta a Lei n.º 3/2000, de 20 de Março", "decreto-lei", "2001-01-01")
    assert lei == (None, None)
    organica = auditoria.classe_vigencia("Decreto Regulamentar n.º 8/93", "Define a orgânica da Direcção-Geral da Indústria", "decreto-regulamentar", "1993-01-01")
    assert organica == ("organicas", "alta")
    assert auditoria.classe_vigencia("Lei n.º 3/85", "Estatuto dos Deputados", "lei", "1985-01-01") == (None, None)


def test_revogacao_inteira():
    assert auditoria.revogacao_inteira("Revogada pela PORT.219/72.1972.04.21.MMAR DG.IS [94]\x00\x00")
    assert auditoria.revogacao_inteira("Revogada a concessão atribuída pelo presente diploma pela PORT.1/2000")
    assert auditoria.revogacao_inteira("Decreto-Lei n.º 42978: revogação total pelo Decreto-Lei n.º 1/80")
    assert not auditoria.revogacao_inteira("Revogado o art. 2º pelo DEC LEI.161/89.13.05.1989.MF")
    assert not auditoria.revogacao_inteira("Revogado o presente diploma, com excepção do art. 3.º, pelo DL 1/90")
    assert not auditoria.revogacao_inteira("Alterado o n.º 5 pela PORT.321/2002")
    assert not auditoria.revogacao_inteira("Revogado, à excepção do seu artigo 4º, pelo DEC LEI.73/99")
    assert not auditoria.revogacao_inteira("Revogado, relativamente à província de Moçambique, o art. 2º do presente diploma, pelo DEC LEI.76/72")
    assert not auditoria.revogacao_inteira("Revogado pelo DEC LEI.35/2003 com excep&#231;&#227;o dos arts 1&#186; e 14&#186;")
    assert not auditoria.revogacao_inteira("REVOGADO O NUMERO 6 PELA PORTARIA NUMERO 537/80")
    assert not auditoria.revogacao_inteira("Revogada a sec VII do cap V, pelo DEC LEI.322/90")
    assert auditoria.revogacao_inteira("Revogada pelo(a) Portaria n.º 207/2017 - Diário da República n.º 132/2017, nos termos do seu art. 5.º")


def test_prazo_da_concessao():
    assert auditoria.prazo_concessao("é concessionada, pelo período de 12 anos, ao Clube") == 12
    assert auditoria.prazo_concessao("renovada por um período de doze anos e, depois, pelo período de seis anos") == 12
    assert auditoria.prazo_concessao("por tempo indeterminado") is None
    assert auditoria.fim_estimado("1991-07-15", 21) == "2012-07-15"
