"""Publicar o índice e descarregá-lo como a aplicação faz (rag.dados), sem rede."""

import json
import sqlite3

import pytest
from rag import dados


def _indice(caminho, texto="artigo"):
    with sqlite3.connect(caminho) as con:
        con.execute("CREATE TABLE meta (chave TEXT, valor TEXT)")
        con.execute("INSERT INTO meta VALUES ('metodo_termos', 'teste')")
        con.execute("CREATE TABLE pedacos (texto TEXT)")
        con.executemany("INSERT INTO pedacos VALUES (?)", [(f"{texto} {i}",) for i in range(2000)])
    return caminho


class _Resposta:
    def __init__(self, corpo: bytes, estado: int):
        self.corpo, self.status_code = corpo, estado

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)

    def iter_content(self, tamanho):
        for i in range(0, len(self.corpo), 1000):
            yield self.corpo[i : i + 1000]

    def json(self):
        return json.loads(self.corpo)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


@pytest.fixture
def publicado(tmp_path, monkeypatch):
    """Um índice publicado em tmp_path/pub e um `requests.get` que o serve, com Range."""
    pub = tmp_path / "pub"
    manifesto = dados.publicar(_indice(tmp_path / "indice.sqlite"), pub, "https://exemplo.pt/dados", "2026-11-12")
    pedidos = []

    def get(url, headers=None, stream=False, timeout=None):
        ficheiro = pub / url.rsplit("/", 1)[1]
        corpo = ficheiro.read_bytes()
        pedidos.append(headers or {})
        if headers and "Range" in headers:
            inicio = int(headers["Range"].split("=")[1].rstrip("-"))
            return _Resposta(corpo[inicio:], 206)
        return _Resposta(corpo, 200)

    import requests

    monkeypatch.setattr(requests, "get", get)
    monkeypatch.setenv("RAG_DADOS_URL", "https://exemplo.pt/dados/versao.json")
    return manifesto, pedidos


def test_publicar_e_descarregar_da_o_mesmo_indice(tmp_path, publicado):
    manifesto, _ = publicado
    f = manifesto["ficheiros"][0]
    assert f["url"] == "https://exemplo.pt/dados/indice.sqlite.gz" and f["bytes"] < f["bytes_descomprimido"]
    destino = tmp_path / "app"
    progresso = dados.Progresso()
    dados.descarregar(destino, progresso)
    assert progresso.fase == "pronto" and progresso.feito == f["bytes"]
    assert (destino / "indice.sqlite").read_bytes() == (tmp_path / "indice.sqlite").read_bytes()
    assert dados.versao_local(destino)["versao"] == "2026-11-12"
    assert not list(destino.glob("*.parte")) and not list(destino.glob("*.novo"))


def test_retoma_onde_parou(tmp_path, publicado):
    manifesto, pedidos = publicado
    destino = tmp_path / "app"
    destino.mkdir()
    metade = (tmp_path / "pub" / "indice.sqlite.gz").read_bytes()[: manifesto["ficheiros"][0]["bytes"] // 2]
    (destino / "indice.sqlite.gz.parte").write_bytes(metade)
    dados.descarregar(destino)
    assert pedidos[-1] == {"Range": f"bytes={len(metade)}-"}
    assert (destino / "indice.sqlite").read_bytes() == (tmp_path / "indice.sqlite").read_bytes()


def test_ficheiro_corrompido_nao_substitui_o_indice(tmp_path, publicado, monkeypatch):
    manifesto, _ = publicado
    destino = tmp_path / "app"
    destino.mkdir()
    (destino / "indice.sqlite").write_bytes(b"antigo")
    manifesto = json.loads(json.dumps(manifesto))
    manifesto["ficheiros"][0]["sha256"] = "0" * 64
    with pytest.raises(RuntimeError, match="corrompido"):
        dados.descarregar(destino, manifesto=manifesto)
    assert (destino / "indice.sqlite").read_bytes() == b"antigo"


def test_atualizacao_so_quando_ha_versao_nova(tmp_path, publicado):
    destino = tmp_path / "app"
    assert dados.ha_atualizacao(destino)["versao"] == "2026-11-12"
    dados.descarregar(destino)
    assert dados.ha_atualizacao(destino) is None


def test_antes_de_trocar_e_chamado(tmp_path, publicado):
    chamadas = []
    dados.descarregar(tmp_path / "app", antes_de_trocar=lambda: chamadas.append(1))
    assert chamadas == [1]


def test_sem_espaco_nao_comeca(tmp_path, publicado, monkeypatch):
    import shutil
    from collections import namedtuple

    monkeypatch.setattr(shutil, "disk_usage", lambda p: namedtuple("U", "total used free")(10, 10, 10))
    with pytest.raises(RuntimeError, match="espaço"):
        dados.descarregar(tmp_path / "app")
