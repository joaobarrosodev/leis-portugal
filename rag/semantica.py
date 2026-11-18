"""Pesquisa semântica (embeddings) nos diplomas consolidados e nos códigos principais.

O BM25 só encontra um artigo se a pergunta usar as palavras dele. Numa pergunta de leigo ("posso
ser despedido por estar doente?") o artigo certo muitas vezes nem chega aos candidatos que o
reranker lê. Aqui, a pergunta e os artigos passam a vetores (paraphrase-multilingual-MiniLM-L12-v2,
o modelo `denso` de `rag.modelos`, já descarregado), e os artigos mais próximos da pergunta
juntam-se aos candidatos do reranker, como os do BM25 nos códigos principais.

Só os pedaços em vigor (`ate IS NULL`) dos diplomas com histórico de versões (o texto consolidado
pelo DRE) e dos códigos principais: 252 mil pedaços no índice de 17/11, cerca de 1 h neste CPU.
O acervo inteiro levaria umas 5 h e é sobretudo texto antigo, que estes candidatos não ajudam.

    PYTHONPATH=src:. python -m rag.semantica construir [--indice rag/indice/indice.sqlite]

Os vetores ficam em `rag/indice/semantica.npz`, ao lado do índice e fora dele: o formato do índice
que a aplicação descarrega não muda. O ficheiro guarda o tamanho e a data do índice com que foi
feito, e a pesquisa recusa-o se o índice for outro (os ids dos pedaços mudam a cada reconstrução).
A construção grava por partes em `semantica.partes/` e retoma depois de um corte.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np

from rag.fontes import PASTA_INDICE
from rag.modelos import CARACTERES, MODELO_DENSO


FICHEIRO = PASTA_INDICE / "semantica.npz"
PARTE = 20_000  # pedaços por parte gravada
CANDIDATOS = 20  # quantos pedaços a pesquisa semântica junta aos candidatos do reranker


def _modelo(fios: int | None = None):
    os.environ.setdefault("HF_HOME", str(PASTA_INDICE / "hf"))
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    from fastembed import TextEmbedding

    pasta = PASTA_INDICE / "modelos"
    local = any(pasta.glob("models--*"))
    return TextEmbedding(MODELO_DENSO, cache_dir=str(pasta), local_files_only=local, threads=fios)


def assinatura(indice: Path) -> str:
    """O índice com que os vetores foram feitos: tamanho e data de modificação."""
    estado = indice.stat()
    return f"{estado.st_size}:{int(estado.st_mtime)}"


def pedacos(con: sqlite3.Connection, principais: list[str], so_referencia: set[str]) -> list[tuple[int, str]]:
    """(id, texto a vetorizar) dos pedaços em vigor dos consolidados e dos códigos principais, por id.

    Os diplomas só pela referência (a 2.ª Série) ficam de fora, como no BM25 em todo o acervo."""
    for tabela, valores in (("principais", principais), ("so_referencia_ids", so_referencia)):
        con.execute(f"CREATE TEMP TABLE IF NOT EXISTS {tabela} (id TEXT PRIMARY KEY)")
        con.execute(f"DELETE FROM {tabela}")
        con.executemany(f"INSERT INTO {tabela} VALUES (?)", [(d,) for d in valores])
    linhas = con.execute(
        """SELECT p.id, p.rotulo, p.texto FROM pedacos p JOIN documentos d ON d.id = p.documento
           WHERE p.ate IS NULL AND (d.com_historico = 1 OR d.id IN (SELECT id FROM principais))
             AND d.id NOT IN (SELECT id FROM so_referencia_ids)
           ORDER BY p.id"""
    ).fetchall()
    return [(i, texto_do_pedaco(rotulo, texto)) for i, rotulo, texto in linhas]


def texto_do_pedaco(rotulo: str | None, texto: str | None) -> str:
    """O caminho (diploma › artigo — epígrafe) e o início do texto: o modelo só lê ~128 tokens."""
    return f"{rotulo or ''}\n{texto or ''}"[:CARACTERES]


def construir(indice: Path, saida: Path, *, fios: int | None = None, lote: int = 64) -> int:
    from rag.pesquisa import Pesquisa

    pesquisa = Pesquisa(indice)
    principais = pesquisa.codigos_principais()
    con = sqlite3.connect(f"file:{indice}?mode=ro", uri=True)
    todos = pedacos(con, principais, pesquisa.so_referencia)
    con.close()
    print(f"{len(todos)} pedaços; {len(principais)} códigos principais", file=sys.stderr, flush=True)

    partes = saida.with_suffix(".partes")
    partes.mkdir(parents=True, exist_ok=True)
    marca = partes / "assinatura.txt"
    if marca.exists() and marca.read_text() != assinatura(indice):
        for f in partes.glob("*.npy"):
            f.unlink()  # de outro índice: os ids não servem
    marca.write_text(assinatura(indice))

    modelo = _modelo(fios)
    inicio = time.time()
    for n in range(0, len(todos), PARTE):
        caminho = partes / f"{n // PARTE:04d}.npy"
        if caminho.exists():
            continue
        bloco = todos[n : n + PARTE]
        vetores = np.array(list(modelo.embed([t for _, t in bloco], batch_size=lote)), dtype=np.float32)
        vetores /= np.linalg.norm(vetores, axis=1, keepdims=True) + 1e-12
        temporario = caminho.with_suffix(".tmp.npy")
        np.save(temporario, vetores.astype(np.float16))
        temporario.replace(caminho)
        print(f"{n + len(bloco)}/{len(todos)} ({time.time() - inicio:.0f} s)", file=sys.stderr, flush=True)

    vetores = np.concatenate([np.load(partes / f"{n // PARTE:04d}.npy") for n in range(0, len(todos), PARTE)])
    ids = np.array([i for i, _ in todos], dtype=np.int64)
    assert len(ids) == len(vetores)
    temporario = saida.with_name(saida.name + ".tmp.npz")
    np.savez(temporario, ids=ids, vetores=vetores, assinatura=np.array(assinatura(indice)), modelo=np.array(MODELO_DENSO))
    temporario.replace(saida)
    for f in partes.glob("*"):
        f.unlink()
    partes.rmdir()
    return len(ids)


class Semantica:
    """Os vetores do acervo em memória (~190 MB em float16) e o modelo para vetorizar a pergunta."""

    def __init__(self, indice: Path | None = None, caminho: Path = FICHEIRO, *, fios: int | None = None):
        indice = indice or PASTA_INDICE / "indice.sqlite"
        dados = np.load(caminho)
        if str(dados["assinatura"]) != assinatura(indice):
            raise RuntimeError(f"{caminho} foi feito com outro índice; refaz com `python -m rag.semantica construir`.")
        self.ids = dados["ids"]
        self.vetores = dados["vetores"]
        self.modelo = _modelo(fios)

    def pesquisar(self, pergunta: str, k: int = CANDIDATOS, *, excluir: set[int] | None = None) -> list[tuple[int, float]]:
        """Os k pedaços mais próximos da pergunta (cosseno), sem os de `excluir`."""
        v = np.array(next(iter(self.modelo.embed([pergunta]))), dtype=np.float32)
        v /= np.linalg.norm(v) + 1e-12
        semelhanca = self.vetores @ v.astype(np.float16)
        quantos = min(len(semelhanca), k + len(excluir or ()))
        melhores = np.argpartition(-semelhanca, quantos - 1)[:quantos]
        melhores = melhores[np.argsort(-semelhanca[melhores])]
        resultado = [(int(self.ids[j]), float(semelhanca[j])) for j in melhores if not excluir or int(self.ids[j]) not in excluir]
        return resultado[:k]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="comando", required=True)
    c = sub.add_parser("construir", help="Vetorizar os pedaços em vigor dos consolidados e dos códigos principais.")
    c.add_argument("--indice", type=Path, default=PASTA_INDICE / "indice.sqlite")
    c.add_argument("--saida", type=Path, default=FICHEIRO)
    c.add_argument("--fios", type=int)
    args = parser.parse_args(argv)
    n = construir(args.indice, args.saida, fios=args.fios)
    print(f"{n} vetores em {args.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
