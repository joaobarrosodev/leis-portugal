"""Reranking dos candidatos com modelos multilingues locais (fastembed, ONNX, CPU).

- `cruzado`: cross-encoder BAAI/bge-reranker-v2-m3 (int8), que lê a pergunta e o artigo juntos;
- `denso`: semelhança de cosseno entre embeddings (paraphrase-multilingual-MiniLM-L12-v2).

Os embeddings do acervo inteiro (1,35 milhões de pedaços) levariam ~5 h neste CPU, por isso
os modelos só reordenam os candidatos que a pesquisa por referência e o BM25 já trouxeram.
Os modelos descarregam-se do Hugging Face na primeira utilização para `rag/indice/modelos/`.
"""

from __future__ import annotations

import os

from rag.fontes import PASTA_INDICE


MODELO_CRUZADO = "BAAI/bge-reranker-v2-m3-int8"
MODELO_DENSO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CARACTERES = 1200


class Reranker:
    """Reordena os candidatos com um modelo multilingue.

    O `cruzado` é int8 com quantização dinâmica: a escala depende do lote, por isso a nota de um
    texto muda com os outros textos do mesmo lote (até 0,6 medido a 19/11/2026; `rag/README.md`,
    «Candidatos ao reranker e pesquisa semântica»). Com `estavel=True` cada texto é pontuado
    sozinho: a mesma pergunta e o mesmo texto dão sempre a mesma nota, que se pode guardar em
    `notas` e reutilizar entre medições. Por omissão fica o lote de 16, o da aplicação 0.1.1.
    """

    def __init__(self, tipo: str = "cruzado", *, maximo: int = 30, fios: int | None = None, estavel: bool = False):
        os.environ.setdefault("HF_HOME", str(PASTA_INDICE / "hf"))
        os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
        pasta = str(PASTA_INDICE / "modelos")
        # Depois da primeira descarga, carrega só da cache: sem rede, o fastembed fica preso a tentar o Hugging Face.
        local = any((PASTA_INDICE / "modelos").glob("models--*"))
        self.tipo = tipo
        self.maximo = maximo
        self.estavel = estavel
        self.notas: dict[tuple[str, str], float] = {}  # só com `estavel`: (pergunta, texto) → nota
        if tipo == "cruzado":
            from fastembed.rerank.cross_encoder import TextCrossEncoder

            self.modelo = TextCrossEncoder(MODELO_CRUZADO, cache_dir=pasta, local_files_only=local, threads=fios)
        elif tipo == "denso":
            from fastembed import TextEmbedding

            self.modelo = TextEmbedding(MODELO_DENSO, cache_dir=pasta, local_files_only=local, threads=fios)
        else:
            raise ValueError(f"reranker desconhecido: {tipo}")

    def pontuar(self, pergunta: str, textos: list[str]) -> list[float]:
        textos = [t[:CARACTERES] for t in textos]
        if not textos:
            return []
        if self.tipo == "cruzado":
            if not self.estavel:
                return [float(s) for s in self.modelo.rerank(pergunta, textos, batch_size=16)]
            falta = [t for t in dict.fromkeys(textos) if (pergunta, t) not in self.notas]
            if falta:
                # batch_size=1: cada texto num lote só dele, e a nota não depende dos vizinhos.
                novas = [float(s) for s in self.modelo.rerank(pergunta, falta, batch_size=1)]
                self.notas.update(((pergunta, t), n) for t, n in zip(falta, novas, strict=True))
            return [self.notas[(pergunta, t)] for t in textos]
        import numpy as np

        vetores = np.array(list(self.modelo.embed([pergunta, *textos], batch_size=32)))
        vetores /= np.linalg.norm(vetores, axis=1, keepdims=True)
        return [float(s) for s in vetores[1:] @ vetores[0]]
