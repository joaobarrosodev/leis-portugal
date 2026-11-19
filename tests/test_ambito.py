"""O âmbito de um diploma (rag.ambito) e o seu peso na ordenação sem IA (rag.pesquisa)."""

from types import SimpleNamespace

from rag import ambito
from rag.pesquisa import RERANKER_ANTIGO, RERANKER_SETOR, Pesquisa


LTFP = {"titulo": "Lei n.º 35/2014", "sumario": "Lei Geral do Trabalho em Funções Públicas", "tipo": "lei", "numero": "35/2014",
        "data": "2014-06-20", "com_historico": 1}
CT = {"titulo": "Lei n.º 7/2009", "sumario": "Aprova a revisão do Código do Trabalho", "tipo": "lei", "numero": "7/2009",
      "data": "2009-02-12", "com_historico": 1}
PORTARIA_1979 = {"titulo": "Portaria n.º 193/79", "sumario": "Actualiza as condições de trabalho dos trabalhadores das instituições de previdência",
                 "tipo": "portaria", "numero": "193/79", "data": "1979-04-21", "com_historico": 0}


def test_rotulo_do_ambito():
    assert ambito.rotulo(LTFP, "Anexo — Lei Geral do Trabalho em Funções Públicas") == "Função pública"
    assert ambito.rotulo(CT, "Anexo — CÓDIGO DO TRABALHO") == "Regime geral"
    assert ambito.rotulo(PORTARIA_1979, "") == "Regulamento de 1979, sem versão consolidada"
    assert ambito.rotulo({"tipo": "decreto-legislativo-regional", "numero": "16/2012/A"}, "") == "Só Açores"
    assert ambito.rotulo({"tipo": "regulation", "numero": "2016/679"}, "") == "Direito da UE"
    assert ambito.rotulo({"tipo": "decreto-lei", "numero": "84/2021", "data": "2021-10-18"}, "") == ""


def test_pergunta_que_fala_do_setor():
    assert ambito.pergunta_fala_do_setor("Quantos dias de férias tem um funcionário público?", "Função pública")
    assert ambito.pergunta_fala_do_setor("férias na Administração Pública", "Função pública")
    assert not ambito.pergunta_fala_do_setor("Quantos dias de férias tem um trabalhador por ano?", "Função pública")


def _pesquisa(docs):
    return SimpleNamespace(documento=lambda i: docs[i], so_referencia=set())


def test_prior_poe_atras_o_setor_e_os_regulamentos_antigos():
    p = _pesquisa({"ltfp": LTFP, "ct": CT, "port": PORTARIA_1979})
    geral = "Quantos dias de férias tem um trabalhador por ano?"
    ct = Pesquisa._prior(p, "ct", "Anexo — CÓDIGO DO TRABALHO", False, pergunta=geral)
    ltfp = Pesquisa._prior(p, "ltfp", "Anexo — Lei Geral do Trabalho em Funções Públicas", False, pergunta=geral)
    assert ltfp < ct
    # Quando a pergunta fala da função pública, a LTFP pesa como o CT.
    publico = "Quantos dias de férias tem um trabalhador em funções públicas?"
    assert Pesquisa._prior(p, "ltfp", "Anexo — Lei Geral do Trabalho em Funções Públicas", False, pergunta=publico) == ct
    assert Pesquisa._prior(p, "port", "", False, pergunta=geral) == 0.75  # PRIOR_ANTIGO (em vigor, sem histórico)


def test_desconto_do_reranker_so_nos_artigos_que_a_pergunta_nao_cita():
    p = _pesquisa({"ltfp": LTFP, "port": PORTARIA_1979})
    geral = "Quantos dias de férias tem um trabalhador por ano?"
    r = SimpleNamespace(documento="ltfp", parte="Anexo — Lei Geral do Trabalho em Funções Públicas", nivel=1)
    assert Pesquisa._desconto_reranker(p, r, geral) == RERANKER_SETOR
    assert Pesquisa._desconto_reranker(p, SimpleNamespace(documento="port", parte="", nivel=1), geral) == RERANKER_ANTIGO
    # Citado na pergunta (nível 2 ou 3): sem desconto.
    assert Pesquisa._desconto_reranker(p, SimpleNamespace(documento="ltfp", parte=r.parte, nivel=3), geral) == 0.0
