"""Os deltas no índice inteiro: aplicar um delta dá o mesmo que construir de raiz?

    RAG_INDICE=… PYTHONPATH=src:. python -m rag.navegador.equivalencia --trabalho /tmp/eq

1. B é o índice verdadeiro (só lido).
2. A é uma cópia de B sem uma amostra de diplomas: os que aparecem nos resultados das 50 perguntas
   de `consultas.jsonl` e mais 2000 ao acaso. Tiram-se com o próprio `aplicar_delta`.
3. Gera-se o delta de A para B, aplica-se a uma cópia de A (A') e compara-se A' com B:
   a impressão digital de cada diploma (`rag.dados.impressoes`), o BM25 das 50 perguntas e o
   resultado da pesquisa sem reranker (os 10 primeiros, por diploma e artigo).
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sqlite3
import time
from pathlib import Path

from rag import dados
from rag.fontes import PASTA_INDICE
from rag.pesquisa import Pesquisa


PASTA = Path(__file__).resolve().parent / "resultados"


def _delta_que_tira(ids: list[str], saida: Path, metodo: str) -> None:
    saida.unlink(missing_ok=True)
    with sqlite3.connect(saida) as s:
        s.execute("CREATE TABLE meta (chave TEXT PRIMARY KEY, valor TEXT)")
        s.execute("CREATE TABLE removidos (id TEXT PRIMARY KEY)")
        s.execute("CREATE TABLE documentos (id)")
        s.execute(f"CREATE TABLE pedacos ({dados._COLUNAS_PEDACO})")
        s.execute("CREATE TABLE relacoes (documento, tipo, alvo, alvo_titulo, data)")
        s.executemany("INSERT INTO meta VALUES (?, ?)", [("de", "B"), ("para", "A"), ("metodo_termos", metodo)])
        s.executemany("INSERT INTO removidos VALUES (?)", [(i,) for i in ids])


def _resultados(indice: Path, perguntas: list[dict]) -> tuple[list, list]:
    p = Pesquisa(indice)
    chave = {}

    def nome(i):
        if i not in chave:
            chave[i] = p.con.execute("SELECT documento, chave FROM pedacos WHERE id = ?", (i,)).fetchone()
        return chave[i]

    bm25 = [[(nome(i), round(s, 6)) for i, s in p.bm25(q["pergunta"], q["data"], limite=100)] for q in perguntas]
    pesquisa = [[(r.documento, r.chave) for r in p.pesquisar(q["pergunta"], q["data"], k=10).resultados] for q in perguntas]
    return bm25, pesquisa


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--trabalho", type=Path, required=True, help="Pasta com espaço para duas cópias do índice.")
    ap.add_argument("--ao-acaso", type=int, default=2000)
    args = ap.parse_args()
    args.trabalho.mkdir(parents=True, exist_ok=True)
    b = PASTA_INDICE / "indice.sqlite"
    perguntas = [json.loads(linha) for linha in (PASTA / "consultas.jsonl").open(encoding="utf-8")]
    t = time.time()

    with sqlite3.connect(f"file:{b}?mode=ro", uri=True) as con:
        metodo = dict(con.execute("SELECT chave, valor FROM meta"))["metodo_termos"]
        todos = [r[0] for r in con.execute("SELECT id FROM documentos")]
        dos_resultados = {r[0] for q in perguntas for r in con.execute(
            f"SELECT DISTINCT documento FROM pedacos WHERE id IN ({','.join('?' * len(q['resultado']))})", q["resultado"]) if q["resultado"]}
    amostra = sorted(dos_resultados | set(random.Random(7).sample(todos, args.ao_acaso)))
    print(f"amostra: {len(amostra)} diplomas ({len(dos_resultados)} dos resultados das {len(perguntas)} perguntas)", flush=True)

    a = args.trabalho / "a.sqlite"
    shutil.copyfile(b, a)
    _delta_que_tira(amostra, args.trabalho / "tira.sqlite", metodo)
    print("tirar:", dados.aplicar_delta(a, args.trabalho / "tira.sqlite"), f"{time.time() - t:.0f} s", flush=True)

    delta = args.trabalho / "delta.sqlite"
    print("delta:", dados.gerar_delta(a, b, delta, "A", "B"), f"{time.time() - t:.0f} s", flush=True)
    comprimido = delta.with_name("delta.sqlite.gz")
    dados._gzip(delta, comprimido)
    a2 = args.trabalho / "a2.sqlite"
    shutil.copyfile(a, a2)
    print("aplicar:", dados.aplicar_delta(a2, delta), f"{time.time() - t:.0f} s", flush=True)

    with sqlite3.connect(f"file:{b}?mode=ro", uri=True) as cb, sqlite3.connect(f"file:{a2}?mode=ro", uri=True) as ca:
        ib, ia = dados.impressoes(cb), dados.impressoes(ca)
    diferentes = [d for d in ib if ia.get(d) != ib[d]] + [d for d in ia if d not in ib]
    rb, ra = _resultados(b, perguntas), _resultados(a2, perguntas)
    bm25_iguais = sum(x == y for x, y in zip(rb[0], ra[0], strict=True))
    pesquisa_iguais = sum(x == y for x, y in zip(rb[1], ra[1], strict=True))
    resumo = {
        "amostra": len(amostra),
        "delta_mb": round(delta.stat().st_size / 1e6, 1),
        "delta_gz_mb": round(comprimido.stat().st_size / 1e6, 1),
        "diplomas_diferentes": len(diferentes),
        "bm25_iguais": f"{bm25_iguais}/{len(perguntas)}",
        "pesquisa_igual": f"{pesquisa_iguais}/{len(perguntas)}",
        "segundos": round(time.time() - t),
    }
    (PASTA / "equivalencia.json").write_text(json.dumps(resumo, indent=1), encoding="utf-8")
    print(json.dumps(resumo, indent=1))


if __name__ == "__main__":
    main()
