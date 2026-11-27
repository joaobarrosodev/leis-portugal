"""O servidor MCP (`mcp/servidor.py`): o protocolo sem índice, e as ferramentas no índice quando ele existe."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import pytest


RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("servidor_mcp", RAIZ / "mcp" / "servidor.py")
servidor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(servidor)  # type: ignore[union-attr]


def chamar(nome, **argumentos):
    r = servidor.responder({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": nome, "arguments": argumentos}})
    return r["result"]["isError"], json.loads(r["result"]["content"][0]["text"])


def test_protocolo():
    r = servidor.responder({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert r["result"]["protocolVersion"] and r["result"]["capabilities"] == {"tools": {}}
    assert servidor.responder({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    nomes = [t["name"] for t in servidor.responder({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]]
    assert nomes == ["pesquisar", "ler_artigo", "diploma", "relacoes", "contar_prazo"]
    assert servidor.responder({"jsonrpc": "2.0", "id": 3, "method": "nada"})["error"]["code"] == -32601
    assert servidor.responder({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "nada"}})["error"]["code"] == -32602


def test_contar_prazo_sem_indice():
    erro, dados = chamar("contar_prazo", inicio="2026-10-31", quantidade=60, regime="civil_em_juizo", data_referencia="2026-11-26")
    assert not erro and dados["fim"] == "2027-01-04" and dados["ja_passou"] is False
    erro, dados = chamar("contar_prazo", inicio="31/10/2026", quantidade=60, regime="civil")
    assert erro and "inválida" in dados["erro"]
    erro, dados = chamar("contar_prazo", inicio="2026-10-31")
    assert erro and "Argumentos inválidos" in dados["erro"]


INDICE = Path(os.environ.get("RAG_INDICE", RAIZ / "rag" / "indice")) / "indice.sqlite"


@pytest.mark.skipif(not INDICE.exists(), reason="sem o índice de pesquisa")
def test_ferramentas_no_indice(monkeypatch):
    monkeypatch.setenv("RAG_RERANKER", "0")
    erro, dados = chamar("diploma", referencia="Lei n.º 7/2009")
    assert not erro and dados["diplomas"][0]["id"] == "pt:dre:602073:por"
    erro, dados = chamar("ler_artigo", documento="pt:dre:602073:por", artigo="351.º")
    assert not erro and "justa causa" in dados["redacoes"][0]["texto"].lower()
    erro, dados = chamar("pesquisar", pergunta="prazo para impugnar o despedimento Código do Trabalho", k=3)
    assert not erro and len(dados["artigos"]) == 3
