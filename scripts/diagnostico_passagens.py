"""Diagnóstico: simula a posição do artigo certo no BM25 se os artigos compridos entrassem por passagens.

Parte da saída de `scripts/diagnostico_pesquisa.py`. O índice não muda: o BM25 do FTS5 é recalculado à
mão (`Sim`, que dá a mesma pontuação que o `bm25()` do SQLite para os pedaços que existem) para cada
passagem dos 1000 melhores pedaços de cada pergunta. Um artigo até 1200 caracteres é uma passagem só; um
maior parte-se pelos números («1 - …»), e um número maior do que isso em grupos de alíneas com o corpo
do número repetido. Diz a posição do artigo certo pela melhor passagem dele e a posição da passagem que
tem o excerto, em todo o acervo e nos códigos principais.

É uma estimativa: o comprimento médio dos pedaços fica o do índice atual, e os artigos fora dos 1000
melhores não entram na simulação.

    RAG_INDICE=... PYTHONPATH=src:. python scripts/diagnostico_passagens.py ENTRADA.jsonl SAIDA.json INDICE.sqlite
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

from rag import texto as termos_mod
from rag.fontes import normalizar, revogado
from rag.pesquisa import PESOS_BM25, Pesquisa


NUMERO = re.compile(r"\d+ ?[-–.] ")
LIMITE = 1200  # caracteres de uma passagem (o que o reranker lê de cada texto)


def _varints(blob: bytes) -> list[int]:
    valores, v = [], 0
    for byte in blob:
        v = (v << 7) | (byte & 0x7F)
        if not byte & 0x80:
            valores.append(v)
            v = 0
    return valores


class Sim:
    """O BM25 do FTS5 (k1 = 1,2; b = 0,75; pesos por coluna) calculado à mão, para textos que não estão no índice."""

    def __init__(self, con):
        self.con = con
        self._idf: dict[str, float] = {}
        con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS temp.vocab USING fts5vocab(main, pedacos_fts, 'row')")
        # O registo 1 de `pedacos_fts_data` tem o número de linhas e o total de termos por coluna.
        valores = _varints(con.execute("SELECT block FROM pedacos_fts_data WHERE id = 1").fetchone()[0])
        self.linhas = valores[0]
        self.media = sum(valores[1:]) / self.linhas

    def idf(self, termo: str) -> float:
        if termo not in self._idf:
            n = (self.con.execute("SELECT doc FROM vocab WHERE term = ?", (termo,)).fetchone() or (0,))[0]
            valor = math.log((self.linhas - n + 0.5) / (n + 0.5))
            self._idf[termo] = valor if valor > 0 else 1e-6
        return self._idf[termo]

    def pontuar(self, uteis: list[str], cabecalho: list[str], texto: list[str]) -> float:
        tamanho = len(cabecalho) + len(texto)
        total = 0.0
        for termo in uteis:
            f = PESOS_BM25[0] * cabecalho.count(termo) + PESOS_BM25[1] * texto.count(termo)
            if f:
                total += self.idf(termo) * f * 2.2 / (f + 1.2 * (0.25 + 0.75 * tamanho / self.media))
        return total


def passagens(texto: str) -> list[str]:
    """As passagens de um artigo: inteiro se for curto; senão por números, e os números compridos por grupos de alíneas."""
    if len(texto) <= LIMITE:
        return [texto]
    unidades: list[list[str]] = []
    for paragrafo in (p for p in re.split(r"\n\s*\n", texto) if p.strip()):
        if NUMERO.match(paragrafo.lstrip()) or not unidades:
            unidades.append([paragrafo])
        else:
            unidades[-1].append(paragrafo)
    saida = []
    for unidade in unidades:
        inteira = "\n\n".join(unidade)
        if len(inteira) <= LIMITE:
            saida.append(inteira)
            continue
        corpo = unidade[0][:300]
        atual: list[str] = []
        tamanho = 0
        for paragrafo in unidade[1:] or [unidade[0]]:
            if atual and tamanho + len(paragrafo) > 1000:
                saida.append(corpo + "\n\n" + "\n\n".join(atual))
                atual, tamanho = [], 0
            atual.append(paragrafo[:LIMITE])
            tamanho += len(paragrafo)
        if atual:
            saida.append(corpo + "\n\n" + "\n\n".join(atual))
    return saida


def simular(pesquisa: Pesquisa, sim: Sim, perguntas_artigo: dict, x: dict, lista: list[tuple[int, float]], *, com_prior: bool):
    """(posição do artigo certo pela melhor passagem, posição da passagem com o excerto) entre os pedaços de `lista`."""
    certo = (x["fonte"]["documento"], x["fonte"]["artigo"])
    uteis = x["termos"]["uteis"]
    excerto = normalizar(x["excerto"] or "")
    ids = [i for i, _ in lista]
    linhas = {}
    for n in range(0, len(ids), 900):
        lote = ids[n : n + 900]
        sql = (
            "SELECT p.id, p.documento, p.chave, p.parte, p.epigrafe, p.texto, p.notas, p.ate, d.titulo, d.sumario "
            f"FROM pedacos p JOIN documentos d ON d.id = p.documento WHERE p.id IN ({','.join('?' * len(lote))})"
        )
        for linha in pesquisa.con.execute(sql, lote):
            linhas[linha[0]] = linha
    artigos, todas = [], []
    for i in ids:
        _, documento, chave, parte, epigrafe, texto, notas, ate, titulo, sumario = linhas[i]
        cabecalho = termos_mod.termos(f"{titulo} {(sumario or '')[:300]} {parte or ''} {epigrafe or ''}")
        das_perguntas = termos_mod.termos(perguntas_artigo.get((documento, chave), "")) if ate is None else []
        prior = pesquisa._prior(documento, parte or "", revogado(texto[:40], notas or ""), pergunta=x["pergunta"]) if com_prior else 1.0
        melhor = 0.0
        for passagem in passagens(texto or ""):
            nota = sim.pontuar(uteis, cabecalho, termos_mod.termos(passagem) + das_perguntas) * prior
            melhor = max(melhor, nota)
            todas.append((nota, (documento, chave) == certo and bool(excerto) and excerto[:80] in normalizar(passagem)))
        artigos.append((documento, chave, melhor))
    artigos.sort(key=lambda t: -t[2])
    todas.sort(key=lambda t: -t[0])
    do_artigo = next((n for n, t in enumerate(artigos, 1) if (t[0], t[1]) == certo), None)
    do_excerto = next((n for n, t in enumerate(todas, 1) if t[1]), None)
    return do_artigo, do_excerto


class SemModelo:
    maximo = 30

    def pontuar(self, pergunta: str, textos: list[str]) -> list[float]:
        return [0.0] * len(textos)


def main(entrada: str, saida: str, indice: str) -> None:
    pesquisa = Pesquisa(Path(indice), reranker=SemModelo())
    sim = Sim(pesquisa.con)
    perguntas_artigo = {(d, c): p for d, c, p in pesquisa.con.execute("SELECT documento, chave, perguntas FROM perguntas_artigo")}
    resultado = {}
    for linha in Path(entrada).read_text(encoding="utf-8").splitlines():
        x = json.loads(linha)
        globais = pesquisa.bm25(x["pergunta"], x["data"], limite=1000)
        codigos = pesquisa.bm25(x["pergunta"], x["data"], documentos=pesquisa.codigos_principais(), limite=200)
        artigo_g, excerto_g = simular(pesquisa, sim, perguntas_artigo, x, globais, com_prior=True)
        artigo_c, excerto_c = simular(pesquisa, sim, perguntas_artigo, x, codigos, com_prior=False)
        resultado[x["id"]] = {
            "global_artigo": artigo_g, "global_passagem_excerto": excerto_g, "codigos_artigo": artigo_c, "codigos_passagem_excerto": excerto_c,
        }
        print(x["id"], x["bm25"]["global_fundo"], "→ artigo", artigo_g, "passagem", excerto_g,
              "| códigos", x["bm25"]["codigos"], "→ artigo", artigo_c, "passagem", excerto_c, flush=True)
    Path(saida).write_text(json.dumps(resultado), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
