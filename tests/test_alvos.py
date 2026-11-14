"""Verificação dos alvos das respostas do LLM (`consolidacao/llm_completo.py`, `verificar_alvos`)."""

import sys
from pathlib import Path

import pytest


PASTA = Path(__file__).resolve().parents[1] / "consolidacao"
if not (PASTA / "llm_completo.py").exists():
    pytest.skip("consolidacao/ não está nesta cópia", allow_module_level=True)
sys.path.insert(0, str(PASTA))

import llm_completo as lc  # noqa: E402


REGISTO = {"id": "pt:dre:1:por", "title": "Decreto-Lei n.º 10/90", "path": "x.md",
           "alteradores": [{"id": "a", "title": "Decreto-Lei n.º 5/95", "path": "a.md", "text_quality": "texto"}]}


@pytest.fixture
def alterador(monkeypatch):
    textos = {}
    monkeypatch.setattr(lc, "_alteradores", lambda registo: registo["alteradores"])
    monkeypatch.setattr(lc, "_texto_alterador", lambda path, titulo: (textos["a.md"], True))
    monkeypatch.setattr(lc, "_ultimos_do_original", lambda registo: {"20.º"})

    def definir(texto, rotulos=()):
        textos["a.md"] = texto
        REGISTO["alteradores"][0]["rotulos_dre"] = list(rotulos)
    return definir


def _resposta(*artigos, nao_aplicavel=None):
    return {"artigos": [{"chave": c, "texto": t, "alterador": 1} for c, t in artigos], "removidos": [], "nao_aplicavel": nao_aplicavel}


def test_artigo_que_nenhum_alterador_menciona(alterador):
    alterador("###### Artigo 1.º\n\nO artigo 5.º do Decreto-Lei n.º 10/90 passa a ter a seguinte redação: «Texto novo.»")
    v = lc.verificar_alvos(_resposta(("5.º", "Texto novo."), ("7.º", "Texto antigo.")), REGISTO)
    assert v["sem_instrucao"] == ["7.º: nenhum alterador menciona o artigo 7.º"]


def test_intervalo_aditado_sem_grau_e_ultimo_artigo(alterador):
    alterador("São revogados os artigos 3.º a 7.º do Decreto-Lei n.º 10/90.\n\nArt. 45-A - É aditado ao Decreto-Lei n.º 10/90 …")
    resposta = _resposta(("5.º", "(Revogado.)"), ("45.º-A", "Texto."), ("20.º", "Publique-se."))
    assert lc.verificar_alvos(resposta, REGISTO)["sem_instrucao"] == []
    # "45.º" não é "45.º-A", nem "5.º" é "15.º"
    assert lc.verificar_alvos(_resposta(("45.º", "Texto."), ("15.º", "(Revogado.)")), REGISTO)["sem_instrucao"] == [
        "45.º: nenhum alterador menciona o artigo 45.º", "15.º: nenhum alterador menciona o artigo 15.º"]


def test_revogacao_do_diploma_inteiro(alterador):
    alterador("São revogados:\n\na) O Decreto-Lei n.º 10/90, de 2 de janeiro, com excepção do artigo 9.º;")
    assert lc.verificar_alvos(_resposta(("4.º", "(Revogado.)")), REGISTO)["sem_instrucao"] == []
    # a revogação não autoriza outra redação
    assert lc.verificar_alvos(_resposta(("4.º", "Outro texto.")), REGISTO)["sem_instrucao"] != []
    # revogar um artigo não é revogar o diploma
    alterador("É revogado o artigo 2.º do Decreto-Lei n.º 10/90.")
    assert lc.verificar_alvos(_resposta(("4.º", "(Revogado.)")), REGISTO)["sem_instrucao"] != []


def test_renumeracao_dispensa_a_mencao(alterador):
    alterador("Art. 2.º É revogado o artigo 18.º do Decreto-Lei n.º 10/90, passando o artigo 19.º a 18.º e "
              "acompanhando os restantes artigos esta alteração de ordem numérica.")
    assert lc.verificar_alvos(_resposta(("25.º", "Texto do antigo 26.º.")), REGISTO)["sem_instrucao"] == []


def test_rotulo_do_dre_por_aplicar(alterador):
    alterador("Os artigos 16.º e 17.º do Decreto-Lei n.º 10/90 passam a ter a seguinte redação: «…»",
              ["Alterados os artigos 16.º e 17.º, pelo DEC LEI.5/95"])
    resposta = _resposta(("16.º", "Novo."))
    assert [x.split(":")[0] for x in lc.verificar_alvos(resposta, REGISTO)["rotulo_por_aplicar"]] == ["17.º"]
    assert lc.verificar_alvos(resposta, REGISTO, tocados={"17.º"})["rotulo_por_aplicar"] == []
    resposta["nao_aplicavel"] = "O artigo 17.º só muda o mapa, que vem em imagem."
    assert lc.verificar_alvos(resposta, REGISTO)["rotulo_por_aplicar"] == []


def test_numeros_do_rotulo():
    assert lc.numeros_do_rotulo("Alterados os artigos 16.º e 17.º, pelo DEC LEI.220/80") == ["16.º", "17.º"]
    assert lc.numeros_do_rotulo("Aditado um art. 48º-A pela PORT.1270/2009") == ["48.º-A"]
    assert lc.numeros_do_rotulo("Alterado o art 89.º do Código dos IEC, aprovado pelo Dec Lei 73/2010") == []
    assert lc.numeros_do_rotulo("Revogado o presente diploma, com excepção do art. 45º") == []
    assert lc.numeros_do_rotulo("Última alteração registada na importação inicial") == []
    # os artigos de outro diploma que o original altera
    assert lc.numeros_do_rotulo("Alterados os arts. 21.º, 26.º e 28.º do Dec Lei 225/85, de 04-Jul") == []
    assert lc.numeros_do_rotulo("Alterados os arts. 2º, 82º e 85º do presente diploma, na redacção do Dec Lei 167/89") == ["2.º", "82.º", "85.º"]
