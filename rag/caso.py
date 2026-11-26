"""Análise de um caso narrado por um advogado: partir o caso, pesquisar por partes, analisar (experimental).

Um advogado escreve «o contexto é este, aconteceu isto ao meu cliente, estou a pensar usar estas leis». Numa consulta
só, a pesquisa encontra o código certo mas não o artigo. O fluxo de caso tem três passos:

1. `partir`: um LLM escreve 3 a 6 consultas curtas, uma por questão jurídica, no vocabulário da lei e com o nome do
   código, e os artigos que acha decisivos («o 394.º do Código do Trabalho»), com as regras de `rag/CASO-PARTIR.md`;
2. `pesquisar`: uma pesquisa por artigo provável (conta o 1.º resultado) e uma por consulta, intercaladas (o 1.º de
   cada, depois o 2.º de cada, …, cada artigo uma vez); o LLM recebe os 16 primeiros;
3. `analisar`: um LLM analisa o caso só com esses artigos, com as regras de `rag/CASO-ANALISE.md`, numa estrutura fixa
   (questões, leis pensadas, o que fazer, prazos, resultado previsível, o que depende de prova), com cada afirmação
   presa a um artigo.

Medido nos 39 casos de `avaliacao/casos/` (26/11/2026, Opus em todos os passos, sem jurista): com o texto inteiro, 33
de 161 artigos essenciais nos 8 primeiros e 5 de 39 análises certas para os dois juízes; partindo o caso, 127 de 161
e 31 de 39. Não é número para dizer em público.

Não está na aplicação: as instruções da app recusam casos concretos, e falta confirmar se um parecer sobre um caso
concreto é ato próprio dos advogados. Não há limiar: é o LLM que diz se os artigos chegam. Sem a chave de uma IA
(`rag.provedores`), ou se o passo de partir falhar, a pesquisa é a do texto inteiro, como a app faz hoje.

    PYTHONPATH=src python -m rag.caso pedido.txt [--data 2026-11-26] [--indice PASTA]
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from rag import provedores
from rag.fontes import RAIZ
from rag.pesquisa import Resultado
from rag.resposta import CARACTERES_POR_ARTIGO, extrair_json, llm_disponivel


FICHEIRO_PARTIR = RAIZ / "rag" / "CASO-PARTIR.md"
FICHEIRO_ANALISE = RAIZ / "rag" / "CASO-ANALISE.md"
ARTIGOS_NO_CONTEXTO = 16
K_POR_CONSULTA = 30
K_POR_ARTIGO = 3
MAXIMO_CONSULTAS = 8
MAXIMO_ARTIGOS = 10
MAXIMO_CARACTERES_CONSULTA = 400
SECCOES = ("questoes", "leis_pensadas", "o_que_fazer", "prazos", "resultado_previsivel", "depende_de_prova")
TITULOS = {
    "questoes": "Questões", "leis_pensadas": "As leis que pensa usar", "o_que_fazer": "O que fazer", "prazos": "Prazos",
    "resultado_previsivel": "Resultado previsível", "depende_de_prova": "O que depende de prova",
}
# As linhas que só servem às sessões do Claude que fazem estes passos por lotes, nas medições.
_LINHA_DOS_FICHEIROS = re.compile(r"^.*(?:entrada|saida)-NN\.jsonl.*\n\n?", re.M)
_CITACAO_NO_TEXTO = re.compile(r"\[(\d{1,3})\]")


def _sem_ficheiros(ficheiro: Path) -> str:
    return _LINHA_DOS_FICHEIROS.sub("", ficheiro.read_text(encoding="utf-8")).rstrip()


def instrucoes_partir() -> str:
    return _sem_ficheiros(FICHEIRO_PARTIR) + (
        '\n\nResponde só com um objeto JSON: {"consultas": ["…", "…"], "artigos_provaveis": ["…"]}'
    )


def instrucoes_analise() -> str:
    return _sem_ficheiros(FICHEIRO_ANALISE) + "\n\nResponde só com esse objeto JSON."


@dataclass
class Decomposicao:
    consultas: list[str]
    artigos_provaveis: list[str] = field(default_factory=list)


def _textos(valor, maximo: int) -> list[str]:
    if not isinstance(valor, list):
        return []
    saida: list[str] = []
    for t in valor:
        if isinstance(t, str):
            t = " ".join(t.split())[:MAXIMO_CARACTERES_CONSULTA]
            if t and t not in saida:
                saida.append(t)
    return saida[:maximo]


def decomposicao(dados: dict) -> Decomposicao | None:
    """O JSON do passo de partir ({"consultas", "artigos_provaveis"}) limpo; `None` se não traz nenhuma consulta."""
    consultas = _textos(dados.get("consultas"), MAXIMO_CONSULTAS)
    return Decomposicao(consultas, _textos(dados.get("artigos_provaveis"), MAXIMO_ARTIGOS)) if consultas else None


def partir(pedido: str) -> Decomposicao | None:
    """As consultas e os artigos prováveis para o pedido; `None` sem LLM ou se a chamada falhar."""
    if not llm_disponivel():
        return None
    try:
        escrita = provedores.escrever(instrucoes_partir(), pedido, max_tokens=4000, esforco="medium")
    except provedores.ErroIA:
        return None
    return None if escrita.recusou else decomposicao(extrair_json(escrita.texto))


def intercalar(listas: list[list[Resultado]]) -> list[Resultado]:
    """O 1.º de cada lista, depois o 2.º de cada, …; cada artigo uma vez. Cada consulta tem lugar nos primeiros."""
    vistos, saida = set(), []
    for i in range(max((len(l) for l in listas), default=0)):
        for l in listas:
            if i < len(l) and (l[i].documento, l[i].chave) not in vistos:
                vistos.add((l[i].documento, l[i].chave))
                saida.append(l[i])
    return saida


def pesquisar(pesquisa, pedido: str, data: str, decomposto: Decomposicao | None, *, n: int | None = ARTIGOS_NO_CONTEXTO) -> list[Resultado]:
    """Os artigos para o caso: os das consultas e dos artigos prováveis, intercalados (primeiro os artigos prováveis);
    sem decomposição, os do texto inteiro. `n=None` devolve a lista toda (para medir posições)."""
    if decomposto is None:
        resultados = pesquisa.pesquisar(pedido, data, k=max(n or 0, K_POR_CONSULTA)).resultados
    else:
        por_artigo = [pesquisa.pesquisar(a, data, k=K_POR_ARTIGO).resultados[:1] for a in decomposto.artigos_provaveis]
        por_consulta = [pesquisa.pesquisar(q, data, k=K_POR_CONSULTA).resultados for q in decomposto.consultas]
        resultados = intercalar(por_artigo + por_consulta)
    return resultados if n is None else resultados[:n]


def contexto(artigos: list[Resultado]) -> str:
    """Os artigos numerados com os avisos, no formato de `rag.resposta.contexto`."""
    return "\n\n".join(
        f"[{n}] {r.rotulo}" + "".join(f"\nAviso: {a}" for a in r.avisos) + f"\n{r.texto[:CARACTERES_POR_ARTIGO]}"
        for n, r in enumerate(artigos, 1)
    )


def mensagem(pedido: str, data: str, artigos: list[Resultado]) -> str:
    return f"Data de referência: {data}\n\nArtigos:\n\n{contexto(artigos)}\n\nPedido do advogado:\n{pedido}"


@dataclass
class Analise:
    responde: bool
    seccoes: dict[str, str] = field(default_factory=dict)
    citacoes: list[Resultado] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    artigos: list[Resultado] = field(default_factory=list)  # os que o LLM recebeu
    decomposicao: Decomposicao | None = None
    motivo: str | None = None
    modelo: str = ""
    aviso_modelo: str | None = None
    erro: str | None = None


def interpretar(dados: dict, artigos: list[Resultado]) -> Analise:
    """A resposta do LLM como `Analise`. Conta como citado cada número válido em `citacoes` ou escrito [n] no texto;
    sem nenhuma citação de um artigo dado, a análise não conta («não sei»)."""
    if not dados.get("responde"):
        return Analise(False, artigos=artigos, motivo="o modelo diz que os artigos não chegam para analisar o caso")
    bruto = dados.get("analise") if isinstance(dados.get("analise"), dict) else {}
    seccoes = {s: " ".join(str(bruto.get(s) or "").split()) for s in SECCOES if bruto.get(s)}
    numeros = [n for n in dados.get("citacoes") or [] if isinstance(n, int)]
    numeros += [int(m) for t in seccoes.values() for m in _CITACAO_NO_TEXTO.findall(t)]
    validos = list(dict.fromkeys(n for n in numeros if 1 <= n <= len(artigos)))
    citacoes = [artigos[n - 1] for n in sorted(validos)]
    if not seccoes or not citacoes:
        return Analise(False, artigos=artigos, motivo="análise sem citação de um artigo dado")
    avisos = list(dict.fromkeys(a for r in citacoes for a in r.avisos))
    return Analise(True, seccoes, citacoes, avisos, artigos)


def analisar(pesquisa, pedido: str, data: str, *, decomposto: Decomposicao | None = None) -> Analise:
    """O fluxo todo: partir (se não vier já a decomposição), pesquisar e analisar com o LLM."""
    if not llm_disponivel():
        return Analise(False, motivo="a análise de caso precisa da chave de uma IA (rag.provedores)")
    quem, aviso = provedores.descricao(), provedores.aviso_medicao()
    decomposto = decomposto or partir(pedido)
    artigos = pesquisar(pesquisa, pedido, data, decomposto)
    if not artigos:
        return Analise(False, decomposicao=decomposto, motivo="a pesquisa não encontrou artigos", modelo=quem, aviso_modelo=aviso)
    try:
        escrita = provedores.escrever(instrucoes_analise(), mensagem(pedido, data, artigos), max_tokens=16000, esforco="medium")
    except provedores.ErroIA as e:
        return Analise(False, artigos=artigos, decomposicao=decomposto, motivo=str(e), modelo=quem, aviso_modelo=aviso, erro=str(e))
    analise = Analise(False, artigos=artigos, motivo="o modelo recusou") if escrita.recusou else interpretar(extrair_json(escrita.texto), artigos)
    analise.decomposicao, analise.modelo, analise.aviso_modelo = decomposto, quem, aviso
    return analise


def mostrar(analise: Analise) -> str:
    linhas = []
    if analise.decomposicao:
        linhas += ["Consultas:"] + [f"  - {q}" for q in analise.decomposicao.consultas]
        if analise.decomposicao.artigos_provaveis:
            linhas += ["Artigos prováveis: " + "; ".join(analise.decomposicao.artigos_provaveis)]
        linhas.append("")
    if not analise.responde:
        linhas.append(f"Não sei. ({analise.motivo})")
    for s, texto in analise.seccoes.items():
        linhas += [f"{TITULOS[s]}:", f"  {texto}", ""]
    if analise.artigos:
        linhas.append("Artigos dados ao modelo:")
        citados = {id(r) for r in analise.citacoes}
        linhas += [f"  [{n}] {'*' if id(r) in citados else ' '} {r.rotulo}" for n, r in enumerate(analise.artigos, 1)]
    linhas += [f"Aviso: {a}" for a in analise.avisos]
    if analise.aviso_modelo:
        linhas.append(analise.aviso_modelo)
    return "\n".join(linhas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pedido", type=Path, help="Ficheiro de texto com o pedido do advogado ('-' lê da entrada).")
    parser.add_argument("--data", default=date.today().isoformat(), help="Data de referência (AAAA-MM-DD).")
    parser.add_argument("--indice", type=Path)
    args = parser.parse_args(argv)
    pedido = sys.stdin.read() if str(args.pedido) == "-" else args.pedido.read_text(encoding="utf-8")
    from rag.modelos import Reranker
    from rag.pesquisa import Pesquisa

    pesquisa = Pesquisa(args.indice, reranker=Reranker("cruzado"))
    print(mostrar(analisar(pesquisa, pedido.strip(), args.data)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
