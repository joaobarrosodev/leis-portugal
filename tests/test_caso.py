"""O fluxo de caso (`rag.caso`) sem índice nem IA: uma pesquisa falsa e um provedor falso."""

from __future__ import annotations

import json

from rag import caso, provedores, referencias
from rag.pesquisa import Consulta, Resultado


def _r(doc: str, chave: str, aviso: str | None = None) -> Resultado:
    return Resultado(0, doc, doc, "", chave, "", chave, f"{doc}, art. {chave}", f"texto {chave}", "", None, None,
                     avisos=[aviso] if aviso else [])


class Pesquisa:
    def __init__(self, por_consulta: dict[str, list[Resultado]]):
        self.por_consulta = por_consulta
        self.pedidas: list[tuple[str, int]] = []

    def pesquisar(self, pergunta, data, k):
        self.pedidas.append((pergunta, k))
        return Consulta(pergunta, data, referencias.extrair(pergunta), self.por_consulta.get(pergunta, [])[:k])


def test_instrucoes_sem_as_linhas_dos_ficheiros():
    for texto in (caso.instrucoes_partir(), caso.instrucoes_analise()):
        assert "entrada-NN" not in texto and "saida-NN" not in texto
        assert texto.rstrip().startswith("# ") and "JSON" in texto.splitlines()[-1]
    assert "3 a 6 consultas" in caso.instrucoes_partir()
    assert "Usa só os artigos dados" in caso.instrucoes_analise()


def test_decomposicao_limpa_o_que_vem_do_llm():
    d = caso.decomposicao({"consultas": ["  despedimento   com justa causa ", "", 3, "despedimento com justa causa", "prazo"],
                           "artigos_provaveis": "o 351.º"})
    assert d.consultas == ["despedimento com justa causa", "prazo"] and d.artigos_provaveis == []
    assert caso.decomposicao({"consultas": []}) is None
    assert len(caso.decomposicao({"consultas": [f"q{i}" for i in range(20)]}).consultas) == caso.MAXIMO_CONSULTAS


def test_pesquisar_intercala_primeiro_os_artigos_provaveis():
    a, b, c, d = _r("CT", "351.º"), _r("CT", "357.º"), _r("CT", "387.º"), _r("CC", "483.º")
    pesquisa = Pesquisa({"o 351.º do Código do Trabalho": [a, d], "q1": [b, a], "q2": [c, b, d]})
    decomposto = caso.Decomposicao(["q1", "q2"], ["o 351.º do Código do Trabalho"])
    lista = caso.pesquisar(pesquisa, "pedido", "2026-11-26", decomposto, n=None)
    # do artigo provável só conta o 1.º; depois o 1.º de cada consulta, o 2.º de cada, …, sem repetidos
    assert [(r.documento, r.chave) for r in lista] == [("CT", "351.º"), ("CT", "357.º"), ("CT", "387.º"), ("CC", "483.º")]
    assert ("o 351.º do Código do Trabalho", caso.K_POR_ARTIGO) in pesquisa.pedidas and ("q1", caso.K_POR_CONSULTA) in pesquisa.pedidas
    assert len(caso.pesquisar(pesquisa, "pedido", "2026-11-26", decomposto, n=2)) == 2


def test_sem_decomposicao_pesquisa_o_texto_inteiro():
    pesquisa = Pesquisa({"pedido": [_r("CT", "1.º")]})
    assert [r.chave for r in caso.pesquisar(pesquisa, "pedido", "2026-11-26", None)] == ["1.º"]


def test_interpretar_conta_as_citacoes_do_texto_e_exige_uma():
    artigos = [_r("CT", "351.º", "Revogado por X"), _r("CT", "357.º"), _r("CT", "387.º")]
    a = caso.interpretar({"responde": True, "analise": {"questoes": "Justa causa [1].", "prazos": "60 dias [3] e [9]."},
                          "citacoes": [2, 0, "x"]}, artigos)
    assert a.responde and [r.chave for r in a.citacoes] == ["351.º", "357.º", "387.º"]
    assert a.avisos == ["Revogado por X"] and set(a.seccoes) == {"questoes", "prazos"}
    assert not caso.interpretar({"responde": True, "analise": {"questoes": "Sem artigos."}, "citacoes": [7]}, artigos).responde
    assert not caso.interpretar({"responde": False}, artigos).responde


def test_analisar_sem_chave_nao_inventa(monkeypatch):
    monkeypatch.setattr(caso, "llm_disponivel", lambda: False)
    a = caso.analisar(Pesquisa({}), "pedido", "2026-11-26")
    assert not a.responde and "chave" in a.motivo
    assert caso.partir("pedido") is None


def test_analisar_com_um_provedor_falso(monkeypatch):
    monkeypatch.setattr(caso, "llm_disponivel", lambda: True)
    monkeypatch.setattr(provedores, "descricao", lambda: "falso")
    monkeypatch.setattr(provedores, "aviso_medicao", lambda: None)
    pedidos = []

    def escrever(sistema, mensagem, *, max_tokens, esforco):
        pedidos.append(sistema)
        if sistema == caso.instrucoes_partir():
            return provedores.Escrita(json.dumps({"consultas": ["q1"], "artigos_provaveis": []}))
        assert "[1] CT, art. 351.º" in mensagem and mensagem.rstrip().endswith("pedido")
        return provedores.Escrita('Aqui vai: {"responde": true, "analise": {"o_que_fazer": "Resolver [1]."}, "citacoes": [1]}')

    monkeypatch.setattr(provedores, "escrever", escrever)
    a = caso.analisar(Pesquisa({"q1": [_r("CT", "351.º")]}), "pedido", "2026-11-26")
    assert a.responde and a.decomposicao.consultas == ["q1"] and a.seccoes == {"o_que_fazer": "Resolver [1]."}
    assert len(pedidos) == 2 and "O que fazer" in caso.mostrar(a)


def test_completar_traz_so_artigos_novos():
    a, b, c, d = _r("CT", "351.º"), _r("CT", "387.º"), _r("CC", "498.º"), _r("CC", "279.º")
    pesquisa = Pesquisa({"prazo da ação de impugnação": [a, b, d], "prescrição da indemnização": [c, d, b]})
    novos = caso.completar(pesquisa, {("CT", "351.º")}, ["prazo da ação de impugnação", "prescrição da indemnização"], "2026-11-26")
    assert [r.chave for r in novos] == ["387.º", "498.º", "279.º"]
    assert caso.completar(pesquisa, {("CT", "351.º")}, [], "2026-11-26") == []


def test_analisar_faz_segunda_volta_com_o_que_falta(monkeypatch):
    monkeypatch.setattr(caso, "llm_disponivel", lambda: True)
    monkeypatch.setattr(provedores, "descricao", lambda: "falso")
    monkeypatch.setattr(provedores, "aviso_medicao", lambda: None)
    mensagens = []

    def escrever(sistema, mensagem, *, max_tokens, esforco):
        if sistema == caso.instrucoes_partir():
            return provedores.Escrita(json.dumps({"consultas": ["q1"]}))
        mensagens.append(mensagem)
        if len(mensagens) == 1:
            return provedores.Escrita(json.dumps({"responde": True, "analise": {"prazos": "Não encontrei o prazo [1]."},
                                                  "citacoes": [1], "falta": ["prazo da ação de impugnação"]}))
        assert "[2] CT, art. 387.º" in mensagem
        return provedores.Escrita(json.dumps({"responde": True, "analise": {"prazos": "60 dias [2]."}, "citacoes": [2]}))

    monkeypatch.setattr(provedores, "escrever", escrever)
    pesquisa = Pesquisa({"q1": [_r("CT", "351.º")], "prazo da ação de impugnação": [_r("CT", "351.º"), _r("CT", "387.º")]})
    a = caso.analisar(pesquisa, "pedido", "2026-11-26")
    assert len(mensagens) == 2 and a.completada and a.falta == ["prazo da ação de impugnação"]
    assert [r.chave for r in a.citacoes] == ["387.º"] and len(a.artigos) == 2
    mensagens.clear()
    sem = caso.analisar(pesquisa, "pedido", "2026-11-26", completar_falta=False)
    assert not sem.completada and len(sem.artigos) == 1
