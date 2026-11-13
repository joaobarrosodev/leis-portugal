import json

import pytest
from rag import provedores, referencias, resposta
from rag.pesquisa import Consulta, Resultado


def _artigo(n: int, avisos=None) -> Resultado:
    r = Resultado(n, "pt:doc", "Lei n.º 1/2020", "", f"{n}.º", "", f"{n}.º", f"Lei n.º 1/2020 › Artigo {n}.º", "texto", "", None, None)
    r.avisos = list(avisos or [])
    return r


def _consulta() -> Consulta:
    return Consulta("Qual o prazo?", "2026-11-12", referencias.extrair("Qual o prazo?"), [_artigo(1), _artigo(2)])


@pytest.fixture
def ia(monkeypatch):
    """Um provedor falso: grava o que lhe pedem e devolve `ia.texto`."""

    class Falsa:
        texto = json.dumps({"responde": True, "resposta": "30 dias [2]", "citacoes": [2]})
        pedidos: list = []
        erro: Exception | None = None

    def escrever(sistema, mensagem, max_tokens, esforco):
        Falsa.pedidos.append((sistema, mensagem, max_tokens))
        if Falsa.erro:
            raise Falsa.erro
        return provedores.Escrita(Falsa.texto)

    for nome in provedores.PROVEDORES:
        monkeypatch.setitem(provedores._ESCREVER, nome, escrever)
    for nome in ("RAG_PROVEDOR", "RAG_MODELO"):
        monkeypatch.delenv(nome, raising=False)
    Falsa.pedidos = []
    return Falsa


def test_por_omissao_e_o_claude_medido(monkeypatch):
    monkeypatch.delenv("RAG_PROVEDOR", raising=False)
    monkeypatch.delenv("RAG_MODELO", raising=False)
    assert (provedores.provedor(), provedores.modelo()) == provedores.MEDIDO
    assert provedores.aviso_medicao() is None


@pytest.mark.parametrize("nome", ["openai", "gemini"])
def test_outra_ia_avisa_que_nao_foi_medida(monkeypatch, nome):
    monkeypatch.setenv("RAG_PROVEDOR", nome)
    monkeypatch.delenv("RAG_MODELO", raising=False)
    aviso = provedores.aviso_medicao()
    assert "medidos com o Claude Opus 5.5" in aviso and provedores.PROVEDORES[nome]["nome"] in aviso


def test_outro_modelo_do_claude_tambem_avisa(monkeypatch):
    monkeypatch.setenv("RAG_PROVEDOR", "claude")
    monkeypatch.setenv("RAG_MODELO", "claude-sonnet-5-5")
    assert "não foi medida" in provedores.aviso_medicao()


def test_disponivel_precisa_da_chave_do_provedor_escolhido(monkeypatch):
    monkeypatch.setenv("RAG_PROVEDOR", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-x")
    assert not provedores.disponivel()


@pytest.mark.parametrize("nome", ["claude", "openai", "gemini"])
def test_a_mesma_resposta_json_da_o_mesmo_resultado_nas_tres(monkeypatch, ia, nome):
    monkeypatch.setenv("RAG_PROVEDOR", nome)
    r = resposta._com_llm(_consulta())
    assert r.responde and r.texto == "30 dias [2]" and [c.numero for c in r.citacoes] == ["2.º"]
    assert r.modelo.startswith(provedores.PROVEDORES[nome]["nome"])
    assert (r.aviso_modelo is None) == (nome == "claude")
    sistema, mensagem, _ = ia.pedidos[-1]
    assert sistema == resposta.INSTRUCOES and "Pergunta: Qual o prazo?" in mensagem


def test_modo_estrito_vale_para_todas(monkeypatch, ia):
    monkeypatch.setenv("RAG_PROVEDOR", "openai")
    consulta = Consulta("Qual o prazo?", "2026-11-12", referencias.extrair("x"), [_artigo(1), _artigo(2, ["Texto original; alterado por Lei 2/2021"])])
    r = resposta._com_llm(consulta)
    assert not r.responde and "texto original" in r.motivo


def test_erro_da_ia_nao_se_confunde_com_nao_sei(monkeypatch, ia):
    monkeypatch.setenv("RAG_PROVEDOR", "gemini")
    ia.erro = provedores.ErroIA("A conta da Gemini (Google) não tem créditos.")
    r = resposta._com_llm(_consulta())
    assert not r.responde and r.erro == "A conta da Gemini (Google) não tem créditos."
    ia.erro = None


def test_reescrita_usa_a_ia_escolhida_e_falha_para_a_pergunta(monkeypatch, ia):
    from rag import reescrita

    monkeypatch.setenv("RAG_PROVEDOR", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-x")
    monkeypatch.setattr(provedores.importlib.util, "find_spec", lambda nome: object())
    ia.texto = "prazo de pagamento da coima"
    assert reescrita.reescrever("quanto tempo tenho pra pagar a multa") == "prazo de pagamento da coima"
    ia.erro = provedores.ErroIA("sem rede")
    assert reescrita.reescrever("quanto tempo tenho pra pagar a multa") == "quanto tempo tenho pra pagar a multa"
    ia.erro = None


def test_mensagens_de_erro_simples():
    class Erro(Exception):
        status_code = 401

    assert "não é válida" in provedores._mensagem_de_erro("openai", Erro("Incorrect API key provided"))
    assert "créditos" in provedores._mensagem_de_erro("claude", Exception("Your credit balance is too low"))
