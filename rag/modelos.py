"""Reranking dos candidatos com modelos multilingues locais (fastembed, ONNX, CPU).

- `cruzado`: cross-encoder BAAI/bge-reranker-v2-m3 (int8), que lê a pergunta e o artigo juntos;
- `denso`: semelhança de cosseno entre embeddings (paraphrase-multilingual-MiniLM-L12-v2).

Os embeddings do acervo inteiro (1,35 milhões de pedaços) levariam ~5 h neste CPU, por isso
os modelos só reordenam os candidatos que a pesquisa por referência e o BM25 já trouxeram.
Os modelos descarregam-se do Hugging Face na primeira utilização para `rag/indice/modelos/`.
"""

from __future__ import annotations

import os
import re

from rag.fontes import PASTA_INDICE
from rag.texto import termos


MODELO_CRUZADO = "BAAI/bge-reranker-v2-m3-int8"
MODELO_DENSO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CARACTERES = 1200
# Com `passagens` (desligado por omissão): quantos textos o reranker lê de um artigo comprido, contando
# o início, e quantas passagens a mais lê por pergunta, somando todos os artigos.
PASSAGENS_ARTIGO = 4
PASSAGENS_PERGUNTA = 40
MINIMO_PASSAGEM = 300  # caracteres do artigo numa passagem, por comprido que seja o cabeçalho
CORPO_REPETIDO = 300  # caracteres do corpo de um número («Estão isentas:») repetidos antes das alíneas
# Onde começa um número do artigo: «1 - », «1.», «1. », «1.º », «§ 1.º» (as alíneas «a)» não contam).
_NUMERO = re.compile(r"\d+ ?[-–] |\d+\.[º°]? |\d+\.[º°]?$|§ ?\d+")
_SEPARADOR = re.compile(r"\n\s*\n")


def _paragrafos(texto: str) -> list[tuple[int, str]]:
    """(onde começa, parágrafo) de cada parágrafo do texto."""
    saida, inicio = [], 0
    for separador in [*_SEPARADOR.finditer(texto), None]:
        fim = separador.start() if separador else len(texto)
        if texto[inicio:fim].strip():
            saida.append((inicio, texto[inicio:fim]))
        inicio = separador.end() if separador else fim
    return saida


def _fatias(paragrafo: str, tamanho: int) -> list[str]:
    """Um parágrafo maior do que `tamanho`, cortado em fatias (no último espaço, se houver)."""
    fatias = []
    while len(paragrafo) > tamanho:
        corte = paragrafo.rfind(" ", tamanho // 2, tamanho)
        corte = corte if corte > 0 else tamanho
        fatias.append(paragrafo[:corte])
        paragrafo = paragrafo[corte:].lstrip()
    return [*fatias, paragrafo] if paragrafo else fatias


def passagens_do_artigo(texto: str, tamanho: int) -> list[str]:
    """As passagens de um artigo para lá dos primeiros `tamanho` caracteres, que o reranker já lê.

    O artigo parte-se pelos números («1 - …», com as alíneas de cada um). Os números que se leem inteiros
    no início ficam de fora. Números seguidos juntam-se enquanto couberem em `tamanho`. Um número maior
    do que isso parte-se pelas alíneas, e o corpo do número, quando as introduz (acaba em «:»), repete-se
    à frente de cada grupo. Um artigo que cabe em `tamanho` não tem passagens."""
    if len(texto) <= tamanho:
        return []
    unidades: list[list[tuple[int, str]]] = []
    for inicio, paragrafo in _paragrafos(texto):
        if not unidades or _NUMERO.match(paragrafo.lstrip()):
            unidades.append([(inicio, paragrafo)])
        else:
            unidades[-1].append((inicio, paragrafo))
    saida: list[str] = []
    atual: list[str] = []

    def junto(partes: list[str]) -> int:
        return sum(len(p) for p in partes) + 2 * max(len(partes) - 1, 0)

    def fechar() -> None:
        if atual:
            saida.append("\n\n".join(atual))
            atual.clear()

    for unidade in unidades:
        resto = [p for inicio, p in unidade if inicio + len(p) > tamanho]  # o que não se lê inteiro no início
        if not resto:
            continue
        corpo = unidade[0][1]
        cabeca = [corpo[:CORPO_REPETIDO]] if resto[0] is not corpo and corpo.rstrip().endswith(":") else []
        if junto([*atual, *cabeca, *resto]) <= tamanho:
            atual += [*cabeca, *resto]
            continue
        fechar()
        if junto([*cabeca, *resto]) <= tamanho:
            atual += [*cabeca, *resto]
            continue
        grupo = list(cabeca)
        for paragrafo in resto:
            for fatia in _fatias(paragrafo, max(tamanho - junto(cabeca) - 2, MINIMO_PASSAGEM // 2)):
                if len(grupo) > len(cabeca) and junto([*grupo, fatia]) > tamanho:
                    saida.append("\n\n".join(grupo))
                    grupo = list(cabeca)
                grupo.append(fatia)
        if len(grupo) > len(cabeca):
            saida.append("\n\n".join(grupo))
    fechar()
    return saida


class Reranker:
    """Reordena os candidatos com um modelo multilingue.

    O `cruzado` é int8 com quantização dinâmica: a escala depende do lote, por isso a nota de um
    texto muda com os outros textos do mesmo lote (até 0,6 medido a 19/11/2026; `rag/README.md`,
    «Candidatos ao reranker e pesquisa semântica»). Com `estavel=True` cada texto é pontuado
    sozinho: a mesma pergunta e o mesmo texto dão sempre a mesma nota, que se pode guardar em
    `notas` e reutilizar entre medições. Por omissão fica o lote de 16, o da aplicação 0.1.1.

    Com `passagens=True` (`pontuar_artigos`), um artigo comprido deixa de valer só pelo início: o
    reranker lê também as passagens seguintes e o artigo fica com a melhor nota. Diagnóstico de
    19/11/2026 (`reports/diagnostico-reais-nao-encontradas.md`): em 10 das 41 reais em que a pesquisa
    falhava, a resposta estava para lá dos 1200 caracteres que o reranker lê. Para limitar o custo, lê
    no máximo `passagens_artigo` textos por artigo e `passagens_pergunta` passagens a mais por pergunta,
    escolhidas pelos termos que partilham com a pergunta.
    """

    # Valores de classe: um `Reranker` criado sem `__init__` (os testes) fica com o comportamento de sempre.
    estavel = False
    passagens = False
    passagens_artigo = PASSAGENS_ARTIGO
    passagens_pergunta = PASSAGENS_PERGUNTA

    def __init__(
        self, tipo: str = "cruzado", *, maximo: int = 30, fios: int | None = None, estavel: bool = False,
        passagens: bool = False, passagens_artigo: int = PASSAGENS_ARTIGO, passagens_pergunta: int = PASSAGENS_PERGUNTA,
    ):
        os.environ.setdefault("HF_HOME", str(PASTA_INDICE / "hf"))
        os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
        pasta = str(PASTA_INDICE / "modelos")
        # Depois da primeira descarga, carrega só da cache: sem rede, o fastembed fica preso a tentar o Hugging Face.
        local = any((PASTA_INDICE / "modelos").glob("models--*"))
        self.tipo = tipo
        self.maximo = maximo
        self.estavel = estavel
        self.passagens = passagens
        self.passagens_artigo = passagens_artigo
        self.passagens_pergunta = passagens_pergunta
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

    def pontuar_artigos(self, pergunta: str, artigos: list[tuple[str, str]]) -> list[tuple[float, str | None]]:
        """A nota de cada artigo (`cabeçalho`, `texto`) e, com `passagens`, a passagem que a deu.

        Sem `passagens` é o `pontuar` de sempre sobre «cabeçalho + texto», e a passagem é `None`. Com
        `passagens`, cada artigo comprido leva também as suas passagens (cada uma com o cabeçalho à
        frente) e fica com a melhor nota; a passagem só vem preenchida quando ganhou ao início do artigo.
        O início entra sempre, por isso a nota de um artigo nunca desce por causa das passagens (a menos
        do ruído do lote, sem `estavel`)."""
        inteiros = [f"{cabecalho}\n{texto}" for cabecalho, texto in artigos]
        if not self.passagens:
            return [(nota, None) for nota in self.pontuar(pergunta, inteiros)]
        da_pergunta = set(termos(pergunta))
        candidatas: list[tuple[int, int, int, str]] = []  # (−termos em comum, artigo, passagem, texto)
        for n, (cabecalho, texto) in enumerate(artigos):
            tamanho = max(CARACTERES - len(cabecalho) - 1, MINIMO_PASSAGEM)
            do_artigo = [(-len(da_pergunta & set(termos(p))), n, k, p) for k, p in enumerate(passagens_do_artigo(texto, tamanho))]
            candidatas += sorted(do_artigo)[: max(self.passagens_artigo - 1, 0)]
        candidatas = sorted(candidatas)[: max(self.passagens_pergunta, 0)]
        notas = self.pontuar(pergunta, inteiros + [f"{artigos[n][0]}\n{p}" for _, n, _, p in candidatas])
        melhores: list[tuple[float, str | None]] = [(nota, None) for nota in notas[: len(artigos)]]
        for (_, n, _, passagem), nota in zip(candidatas, notas[len(artigos) :], strict=True):
            if nota > melhores[n][0]:
                melhores[n] = (nota, passagem)
        return melhores
