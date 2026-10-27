"""Pesquisa por diploma com embeddings: um vetor por diploma (título, sumário, nomes dos anexos e,
sem sumário, o início do texto), um por anexo com nome ("Anexo — CÓDIGO DO TRABALHO") e, nos
diplomas com artigos, um por cada 25 epígrafes (o sumário de um código não diz do que tratam os
artigos; "Duração do período de férias" diz).

As perguntas reais usam palavras do dia a dia e quase nunca citam o diploma; o BM25 por artigo
traz diplomas do mesmo tema mas errados. Aqui procura-se primeiro o diploma mais próximo da
pergunta e depois o artigo só dentro dele (como já se faz com os diplomas citados).

    PYTHONPATH=src python -m rag.diplomas            # constrói rag/indice/diplomas.npy (+ .json), ~30 min em CPU

O modelo denso é o de `rag.modelos` (paraphrase-multilingual-MiniLM-L12-v2, 384 dimensões); os
223 mil vetores (~350 MB) procuram-se por produto interno com o numpy, sem índice aproximado.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

from rag.fontes import PASTA_INDICE


CARACTERES_SUMARIO = 400
CARACTERES_TEXTO = 300
MAX_ANEXOS = 4
EPIGRAFES_POR_VETOR = 25
ESTADOS = ("in_force", "partially_in_force", "unknown")  # os revogados ficam de fora: as perguntas reais são sobre a lei atual


def textos_dos_diplomas(con: sqlite3.Connection) -> list[tuple[str, str, str]]:
    """(documento, parte, texto a embeber): um por diploma em vigor (parte ""), um por anexo com nome e um por 25 epígrafes."""
    anexos: dict[str, list[str]] = {}
    for documento, parte in con.execute("SELECT DISTINCT documento, parte FROM pedacos WHERE parte != '' ORDER BY documento, parte"):
        anexos.setdefault(documento, []).append(parte)
    inicios = dict(con.execute("SELECT documento, substr(texto, 1, ?) FROM pedacos WHERE ordem = 0", (CARACTERES_TEXTO,)))
    epigrafes: dict[tuple[str, str], list[str]] = {}
    for documento, parte, epigrafe in con.execute(
        "SELECT documento, parte, epigrafe FROM pedacos WHERE epigrafe != '' AND ate IS NULL ORDER BY documento, ordem"
    ):
        lista = epigrafes.setdefault((documento, parte), [])
        if epigrafe not in lista[-3:]:
            lista.append(epigrafe)
    entradas = []
    sql = f"SELECT id, titulo, sumario FROM documentos WHERE legal_status IN ({','.join('?' * len(ESTADOS))}) ORDER BY id"
    for id_, titulo, sumario in con.execute(sql, ESTADOS):
        partes = [f"{titulo}. {sumario[:CARACTERES_SUMARIO]}" if sumario else f"{titulo}. {inicios.get(id_, '')}"]
        partes += anexos.get(id_, [])[:MAX_ANEXOS]
        entradas.append((id_, "", " ".join(partes)))
        for parte in anexos.get(id_, []):
            if "—" in parte or ":" in parte:  # anexos com nome, não "Anexo I"
                entradas.append((id_, parte, f"{parte}. {titulo}"))
        for parte in ["", *anexos.get(id_, [])]:
            lista = epigrafes.get((id_, parte), [])
            for n in range(0, len(lista), EPIGRAFES_POR_VETOR):
                entradas.append((id_, f"{parte}#{n // EPIGRAFES_POR_VETOR}", "; ".join(lista[n : n + EPIGRAFES_POR_VETOR])))
    return entradas


def construir(saida: Path = PASTA_INDICE / "diplomas", caminho_indice: Path | None = None, *, lote: int = 256) -> None:
    import numpy as np

    from rag.modelos import Reranker

    con = sqlite3.connect(f"file:{caminho_indice or PASTA_INDICE / 'indice.sqlite'}?mode=ro", uri=True)
    entradas = textos_dos_diplomas(con)
    modelo = Reranker("denso").modelo
    print(f"{len(entradas)} textos a embeber", file=sys.stderr, flush=True)
    vetores = []
    inicio = time.time()
    for n in range(0, len(entradas), lote):
        vetores.extend(modelo.embed([t for _, _, t in entradas[n : n + lote]], batch_size=64))
        if (n // lote) % 20 == 0:
            print(f"{min(n + lote, len(entradas))}/{len(entradas)} ({(time.time() - inicio) / 60:.1f} min)", file=sys.stderr, flush=True)
    matriz = np.asarray(vetores, dtype=np.float32)
    matriz /= np.linalg.norm(matriz, axis=1, keepdims=True)
    np.save(saida.with_suffix(".npy"), matriz)
    saida.with_suffix(".json").write_text(json.dumps([[d, p] for d, p, _ in entradas], ensure_ascii=False), encoding="utf-8")
    print(f"{matriz.shape} em {saida}.npy ({(time.time() - inicio) / 60:.1f} min)", file=sys.stderr)


class IndiceDiplomas:
    def __init__(self, caminho: Path = PASTA_INDICE / "diplomas", modelo=None):
        import numpy as np

        self.matriz = np.load(caminho.with_suffix(".npy"))
        self.entradas: list[tuple[str, str]] = [tuple(x) for x in json.loads(caminho.with_suffix(".json").read_text(encoding="utf-8"))]
        if modelo is None:
            from rag.modelos import Reranker

            modelo = Reranker("denso").modelo
        self.modelo = modelo

    def vetor(self, pergunta: str):
        import numpy as np

        v = np.asarray(next(iter(self.modelo.embed([pergunta]))), dtype=np.float32)
        return v / np.linalg.norm(v)

    def procurar(self, pergunta: str, k: int = 20, *, peso=None) -> list[tuple[str, float]]:
        """Os k diplomas mais próximos, (documento, semelhança × peso); cada diploma uma vez, pela melhor entrada."""
        import numpy as np

        semelhancas = self.matriz @ self.vetor(pergunta)
        candidatos = np.argpartition(-semelhancas, min(k * 4, len(semelhancas) - 1))[: k * 4]
        melhores: dict[str, float] = {}
        for i in sorted(candidatos, key=lambda i: -semelhancas[i]):
            documento = self.entradas[i][0]
            s = float(semelhancas[i]) * (peso(documento) if peso else 1.0)
            if documento not in melhores or s > melhores[documento]:
                melhores[documento] = s
        return sorted(melhores.items(), key=lambda x: -x[1])[:k]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--saida", type=Path, default=PASTA_INDICE / "diplomas")
    parser.add_argument("--indice", type=Path)
    args = parser.parse_args(argv)
    construir(args.saida, args.indice)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
