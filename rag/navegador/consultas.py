"""Regista as consultas SQL que a pesquisa faz, para as medir fora do Python (prova de conceito no browser).

    RAG_INDICE=… python -m rag.navegador.consultas --n 50

Grava em `rag/navegador/resultados/` (fora do git):
- `consultas.jsonl`: por pergunta, as consultas (SQL e parâmetros), o tempo local e os ids do resultado;
- `arranque.jsonl`: as consultas feitas uma só vez (códigos, códigos principais), que no browser
  viriam num ficheiro pequeno já preparado;
- `candidatos.jsonl`: a pergunta e os textos que o reranker leria (até 30 + os dos códigos), para medir
  o reranker no browser com os mesmos dados.

Usa um reranker falso (pontuação 0), para a pesquisa seguir o mesmo caminho que com o reranker
(também o BM25 nos códigos principais) sem gastar tempo com o modelo.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from rag.modelos import CARACTERES
from rag.pesquisa import Pesquisa


RAIZ = Path(__file__).resolve().parents[2]
SAIDA = Path(__file__).resolve().parent / "resultados"


class Gravadora:
    """Embrulha a ligação SQLite e regista cada `execute`."""

    def __init__(self, con):
        self._con = con
        self.registo: list[dict] = []

    def execute(self, sql, parametros=()):
        inicio = time.perf_counter()
        cursor = self._con.execute(sql, parametros)
        linhas = cursor.fetchall()
        self.registo.append({"sql": sql, "parametros": list(parametros), "ms": round((time.perf_counter() - inicio) * 1000, 2), "linhas": len(linhas)})
        return _Linhas(linhas)

    def __getattr__(self, nome):
        return getattr(self._con, nome)


class _Linhas(list):
    def fetchone(self):
        return self[0] if self else None

    def fetchall(self):
        return list(self)


class RerankerFalso:
    maximo = 30

    def __init__(self):
        self.ultimos: list[str] = []

    def pontuar(self, pergunta, textos):
        self.ultimos = [t[:CARACTERES] for t in textos]
        return [0.0] * len(textos)


def perguntas(n: int) -> list[dict]:
    todas = [json.loads(linha) for linha in (RAIZ / "avaliacao" / "perguntas.jsonl").open(encoding="utf-8")]
    passo = max(1, len(todas) // n)
    return todas[::passo][:n]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--indice", type=Path, default=None)
    args = ap.parse_args()
    SAIDA.mkdir(exist_ok=True)

    reranker = RerankerFalso()
    pesquisa = Pesquisa(args.indice, reranker=reranker)
    gravadora = Gravadora(pesquisa.con)
    pesquisa.con = gravadora

    inicio = time.perf_counter()
    pesquisa.codigos_principais()
    arranque_ms = (time.perf_counter() - inicio) * 1000
    with (SAIDA / "arranque.jsonl").open("w", encoding="utf-8") as f:
        for r in gravadora.registo:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"arranque: {len(gravadora.registo)} consultas, {arranque_ms:.0f} ms")

    with (SAIDA / "consultas.jsonl").open("w", encoding="utf-8") as fc, (SAIDA / "candidatos.jsonl").open("w", encoding="utf-8") as fr:
        for p in perguntas(args.n):
            gravadora.registo = []
            inicio = time.perf_counter()
            consulta = pesquisa.pesquisar(p["pergunta"], p.get("data_referencia"))
            ms = (time.perf_counter() - inicio) * 1000
            registo = {
                "id": p["id"],
                "tipo": p.get("tipo"),
                "pergunta": p["pergunta"],
                "data": p.get("data_referencia"),
                "ms": round(ms, 1),
                "resultado": [r.id for r in consulta.resultados],
                "consultas": gravadora.registo,
            }
            fc.write(json.dumps(registo, ensure_ascii=False) + "\n")
            fr.write(json.dumps({"id": p["id"], "pergunta": p["pergunta"], "textos": reranker.ultimos}, ensure_ascii=False) + "\n")
            print(f"{p['id']:>10}  {len(gravadora.registo):>4} consultas  {ms:7.0f} ms")


if __name__ == "__main__":
    main()
