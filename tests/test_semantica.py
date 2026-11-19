"""rag.semantica: que pedaços se vetorizam, a recusa de vetores de outro índice e os candidatos a mais no reranker.

O modelo verdadeiro (240 MB) não está no CI: um modelo falso dá a cada texto um vetor pelas palavras."""

import sqlite3
import zlib

import pytest


np = pytest.importorskip("numpy")  # o CI dos testes não instala o extra `rag`

from rag import semantica  # noqa: E402
from rag.pesquisa import Pesquisa  # noqa: E402

from test_dados import _artigos, _construir  # noqa: E402


DIM = 64


class ModeloFalso:
    def embed(self, textos, batch_size=None):
        for texto in textos:
            v = np.zeros(DIM, dtype=np.float32)
            for palavra in texto.lower().split():
                v[zlib.crc32(palavra.encode()) % DIM] += 1
            yield v + 1e-3


@pytest.fixture
def indice(tmp_path, monkeypatch):
    monkeypatch.setattr(semantica, "_modelo", lambda fios=None: ModeloFalso())
    caminho = _construir(tmp_path / "i.sqlite", {
        "pt:con": ("Lei consolidada", "despedimentos", _artigos(3, "despedimento"), []),
        "pt:ant": ("Lei antiga", "baldios", _artigos(3, "baldio"), []),
        "pt:ref": ("Regulamento municipal", "despedimentos", _artigos(3, "despedimento"), []),
        **{f"pt:e{n:02}": (f"Portaria {n}", "estradas", _artigos(2, f"estrada{n}"), []) for n in range(10)},
    })
    con = sqlite3.connect(caminho)
    con.execute("UPDATE documentos SET com_historico = 1 WHERE id IN ('pt:con', 'pt:ref')")
    con.execute("UPDATE pedacos SET ate = '2021-01-01' WHERE documento = 'pt:con' AND numero = '3.º'")  # redação antiga
    con.execute("CREATE TABLE so_referencia (id TEXT PRIMARY KEY)")
    con.execute("INSERT INTO so_referencia VALUES ('pt:ref')")
    con.commit()
    con.close()
    return caminho


def test_vetoriza_so_os_consolidados_em_vigor_fora_da_2a_serie(indice, tmp_path):
    assert semantica.construir(indice, tmp_path / "s.npz") == 2
    dados = np.load(tmp_path / "s.npz")
    con = sqlite3.connect(indice)
    documentos = {con.execute("SELECT documento, numero FROM pedacos WHERE id = ?", (int(i),)).fetchone() for i in dados["ids"]}
    assert documentos == {("pt:con", "1.º"), ("pt:con", "2.º")}
    assert not (tmp_path / "s.partes").exists()


def test_recusa_vetores_de_outro_indice(indice, tmp_path):
    semantica.construir(indice, tmp_path / "s.npz")
    with sqlite3.connect(indice) as con:
        con.execute("INSERT INTO meta VALUES ('outra', 'coisa')")  # o índice mudou
    import os

    os.utime(indice, (1, 1))
    with pytest.raises(RuntimeError, match="outro índice"):
        semantica.Semantica(indice, tmp_path / "s.npz")


def test_os_candidatos_semanticos_vao_ao_reranker(indice, tmp_path):
    semantica.construir(indice, tmp_path / "s.npz")
    sem = semantica.Semantica(indice, tmp_path / "s.npz")
    assert sem.pesquisar("despedimento prazo", k=1)

    class Reranker:
        maximo = 1
        lidos: list[str] = []

        def pontuar(self, pergunta, textos):
            self.lidos.extend(textos)
            return [0.0] * len(textos)

    r = Reranker()
    # Uma pergunta sem palavras do diploma consolidado: o BM25 não o traz, a semântica sim.
    Pesquisa(indice, reranker=r, codigos_candidatos=0, semantica=sem).pesquisar("estrada1 prazo despedimento", "2026-01-01")
    assert any("Lei consolidada" in t for t in r.lidos)
    r.lidos.clear()
    Pesquisa(indice, reranker=r, codigos_candidatos=0).pesquisar("estrada1 prazo despedimento", "2026-01-01")
    assert not any("Lei consolidada" in t for t in r.lidos)
