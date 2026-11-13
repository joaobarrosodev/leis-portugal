"""A página local (rag.web): os pedidos HTTP tratados sem abrir uma porta."""

import io
import json

import pytest
from rag import definicoes, provedores, referencias, web
from rag.pesquisa import Consulta, Resultado
from rag.resposta import Resposta


CODIGO = "codigo-de-teste"
PORTA = 8765


class _Ligacao:
    def __init__(self, bruto: bytes):
        self._entrada = io.BytesIO(bruto)
        self.saida = io.BytesIO()

    def makefile(self, modo, *args, **kwargs):
        return self._entrada if "r" in modo else self.saida

    def sendall(self, dados):
        self.saida.write(dados)


class _Servidor:
    server_address = ("127.0.0.1", PORTA)


def pedir(servico, metodo, caminho, corpo=None, *, host=f"127.0.0.1:{PORTA}", codigo=CODIGO):
    dados = json.dumps(corpo).encode() if corpo is not None else b""
    cabecalhos = [f"{metodo} {caminho} HTTP/1.1", f"Host: {host}", f"Content-Length: {len(dados)}"]
    if codigo:
        cabecalhos.append(f"X-Codigo: {codigo}")
    bruto = ("\r\n".join(cabecalhos) + "\r\n\r\n").encode() + dados
    ligacao = _Ligacao(bruto)
    web.criar_tratador(servico, CODIGO)(ligacao, ("127.0.0.1", 50000), _Servidor())
    resposta = ligacao.saida.getvalue()
    cabeca, _, corpo_resposta = resposta.partition(b"\r\n\r\n")
    estado = int(cabeca.split(b" ")[1])
    try:
        return estado, json.loads(corpo_resposta)
    except ValueError:
        return estado, corpo_resposta


def _artigo(n):
    return Resultado(n, "pt:doc", "Lei n.º 1/2020", "", f"{n}.º", "", f"{n}.º", f"Lei n.º 1/2020 › Artigo {n}.º", "O prazo é de 30 dias.", "", None, None)


class PesquisaFalsa:
    def pesquisar(self, pergunta, data, k=10):
        return Consulta(pergunta, data, referencias.extrair(pergunta), [_artigo(1), _artigo(2)])

    def julgamentos(self, r):
        return []


@pytest.fixture
def servico(monkeypatch, tmp_path):
    monkeypatch.setenv("LEIS_PORTUGAL_PASTA", str(tmp_path))
    for v in ("RAG_PROVEDOR", "RAG_MODELO", "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.delenv(v, raising=False)
    monkeypatch.setattr(definicoes, "_keyring", lambda: None)  # nada no cofre verdadeiro durante os testes
    definicoes._em_memoria.clear()
    registo = tmp_path / "perguntas.jsonl"
    from rag import perguntar

    monkeypatch.setattr(perguntar, "REGISTO", registo)
    s = web.Servico(reranker="nenhum")
    s.pesquisa, s.estado = PesquisaFalsa(), "pronto"
    s.registo = registo
    return s


def test_pagina_leva_o_codigo(servico):
    estado, corpo = pedir(servico, "GET", "/", codigo=None)
    assert estado == 200 and CODIGO.encode() in corpo and b"__CODIGO__" not in corpo


def test_api_sem_codigo_ou_com_outro_host_e_recusada(servico):
    assert pedir(servico, "GET", "/api/estado", codigo=None)[0] == 403
    assert pedir(servico, "POST", "/api/perguntar", {"pergunta": "x"}, codigo="errado")[0] == 403
    assert pedir(servico, "POST", "/api/perguntar", {"pergunta": "x"}, host="mau.exemplo:8765")[0] == 403
    assert pedir(servico, "GET", "/", host="mau.exemplo")[0] == 403


def test_ficheiros_fora_da_pagina_nao_saem(servico):
    assert pedir(servico, "GET", "/../web.py")[0] == 404
    assert pedir(servico, "GET", "/estilo.css")[0] == 200


def test_estado_sem_chave_pede_o_assistente(servico):
    estado, corpo = pedir(servico, "GET", "/api/estado")
    assert estado == 200 and corpo["configurado"] is False and corpo["com_chave"] is False
    assert set(corpo["provedores"]) == {"claude", "openai", "gemini"}
    assert corpo["medido"] == {"provedor": "claude", "modelo": "claude-opus-5-5"}


def test_perguntar_sem_ia_da_o_artigo_e_a_avaliacao_fica_gravada(servico):
    estado, r = pedir(servico, "POST", "/api/perguntar", {"pergunta": "Qual o prazo?", "data": "2026-11-12"})
    assert estado == 200 and r["responde"] and not r["com_llm"]
    assert r["citacoes"][0]["rotulo"] == "Lei n.º 1/2020 › Artigo 1.º"
    assert [o["rotulo"] for o in r["outros"]] == ["Lei n.º 1/2020 › Artigo 2.º"]
    assert pedir(servico, "POST", "/api/avaliar", {"id": r["id"], "certo": False, "esperado": "artigo 2.º"})[1] == {"gravado": True}
    linha = json.loads(servico.registo.read_text(encoding="utf-8"))
    assert linha["pergunta"] == "Qual o prazo?" and linha["certo"] is False and linha["esperado"] == "artigo 2.º"
    assert pedir(servico, "POST", "/api/avaliar", {"id": r["id"], "certo": True})[1] == {"gravado": False}


def test_pergunta_vazia(servico):
    assert pedir(servico, "POST", "/api/perguntar", {"pergunta": "  "})[0] == 400


def test_sem_dados_responde_503(servico):
    servico.pesquisa, servico.estado, servico.erro = None, "sem dados", "sem índice"
    estado, corpo = pedir(servico, "POST", "/api/perguntar", {"pergunta": "Qual o prazo?"})
    assert estado == 503 and "sem índice" in corpo["erro"]


def test_configurar_so_guarda_chave_valida(servico, monkeypatch):
    monkeypatch.setattr(provedores, "validar", lambda nome, chave, modelo: (chave == "boa", "ok" if chave == "boa" else "A chave não é válida."))
    estado, r = pedir(servico, "POST", "/api/configurar", {"provedor": "gemini", "modelo": "gemini-4-carbon", "chave": "má"})
    assert r["ok"] is False and definicoes.ler() == {}
    estado, r = pedir(servico, "POST", "/api/configurar", {"provedor": "gemini", "modelo": "gemini-4-carbon", "chave": "boa"})
    assert r["ok"] is True and "cofre" in r["mensagem"]  # sem cofre nos testes: avisa que fica só até fechar
    assert definicoes.ler() == {"provedor": "gemini", "modelo": "gemini-4-carbon"}
    assert r["estado"]["com_chave"] is provedores._instalado("google.genai")
    assert "não foi medida" in r["estado"]["aviso_medicao"]
    assert pedir(servico, "POST", "/api/esquecer", {"provedor": "gemini"})[1]["ok"]
    assert definicoes.ler_chave("gemini") is None


def test_erro_da_ia_aparece_como_erro(servico, monkeypatch):
    monkeypatch.setattr(web, "llm_disponivel", lambda: True)
    monkeypatch.setattr(web.reescrita, "pesquisar", lambda p, pergunta, data, k: p.pesquisar(pergunta, data, k))
    monkeypatch.setattr(web, "responder", lambda *a, **k: Resposta(False, "Não sei.", motivo="sem créditos", com_llm=True, erro="A conta da OpenAI não tem créditos."))
    r = pedir(servico, "POST", "/api/perguntar", {"pergunta": "Qual o prazo?"})[1]
    assert r["erro"] == "A conta da OpenAI não tem créditos."


def test_aplicar_poe_a_escolha_no_ambiente(servico, monkeypatch):
    import os

    definicoes.gravar({"provedor": "openai", "modelo": "gpt-6.1-sol"})
    definicoes._em_memoria["openai"] = "sk-x"
    definicoes.aplicar()
    assert (os.environ["RAG_PROVEDOR"], os.environ["RAG_MODELO"], os.environ["OPENAI_API_KEY"]) == ("openai", "gpt-6.1-sol", "sk-x")
