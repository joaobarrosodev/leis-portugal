"""Fazer perguntas ao protótipo, uma a uma, e anotar as que falham.

O mais simples é `./perguntar` na raiz do repositório (instala o que falta e constrói o índice
na primeira vez). Diretamente:

    PYTHONPATH=src python -m rag.perguntar                      # modo interativo
    PYTHONPATH=src python -m rag.perguntar "Quantos dias de férias tem um trabalhador?"

Mostra a resposta (sem chave da API, o artigo mais provável) com os avisos (revogado, texto
original de um diploma alterado, redação antiga…) e os outros artigos encontrados. Usa o
reranker quando o extra `rag` está instalado, com o limiar medido (3). No modo interativo
pergunta se a resposta está certa e, se não estiver, que artigo se esperava.

Cada pergunta fica em `rag/resultados/privado/perguntas-testadas.jsonl` (fora do git), com a
resposta, os artigos e a anotação, para as que falham entrarem no conjunto de avaliação.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import textwrap
from datetime import date, datetime
from pathlib import Path

from rag.fontes import RAIZ
from rag.pesquisa import Consulta, Pesquisa
from rag.resposta import llm_disponivel, responder


REGISTO = RAIZ / "rag" / "resultados" / "privado" / "perguntas-testadas.jsonl"
LIMIAR = 3.0  # medido com o conjunto de avaliação (rag/README.md)
LARGURA = 100


def _paragrafos(texto: str, maximo: int) -> str:
    texto = textwrap.shorten(" ".join(texto.split()), maximo, placeholder=" …")
    return textwrap.fill(texto, LARGURA, initial_indent="   ", subsequent_indent="   ")


def mostrar(consulta: Consulta, resposta, k: int) -> None:
    print()
    if not resposta.responde:
        print(f"→ Não sei. ({resposta.motivo})")
    elif resposta.com_llm:
        print("→ " + textwrap.fill(resposta.texto.strip(), LARGURA, subsequent_indent="  "))
        for r in resposta.citacoes:
            print(f"   Fonte: {r.rotulo}")
    else:
        topo = resposta.citacoes[0]
        print(f"→ {topo.rotulo}")
        print(_paragrafos(topo.texto, 600))
    for aviso in resposta.avisos:
        print(f"   ⚠ {aviso}")
    if consulta.diplomas_em_falta:
        print(f"   ⚠ Não está no acervo: {', '.join(consulta.diplomas_em_falta)}")
    citados = {r.id for r in resposta.citacoes}
    outros = [r for r in consulta.resultados[:k] if r.id not in citados]
    if outros:
        print("\n   Outros artigos encontrados:")
        for r in outros:
            print(f"   · {r.rotulo}")
    print()


def registar(consulta: Consulta, resposta, anotacao: dict) -> None:
    REGISTO.parent.mkdir(parents=True, exist_ok=True)
    linha = {
        "quando": datetime.now().isoformat(timespec="seconds"),
        "pergunta": consulta.pergunta,
        "data_referencia": consulta.data,
        "responde": resposta.responde,
        "com_llm": resposta.com_llm,
        "resposta": resposta.texto,
        "motivo": resposta.motivo,
        "artigos": [{"documento": r.documento, "artigo": r.chave, "rotulo": r.rotulo, "reranker": r.reranker} for r in consulta.resultados[:10]],
        **anotacao,
    }
    with REGISTO.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")


def anotar() -> dict:
    try:
        certo = input("Está certo? (s/n, Enter salta) ").strip().lower()
        if certo.startswith("s"):
            return {"certo": True}
        if certo.startswith("n"):
            return {"certo": False, "esperado": input("O que esperavas? (artigo e lei, se souberes) ").strip()}
    except EOFError:
        pass
    return {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pergunta", nargs="?", help="Sem pergunta, abre o modo interativo.")
    parser.add_argument("--data", default=date.today().isoformat(), help="Data de referência (AAAA-MM-DD; por omissão: hoje).")
    parser.add_argument("--indice", type=Path)
    parser.add_argument("--reranker", choices=("cruzado", "denso", "nenhum"), help="Por omissão, cruzado se o extra `rag` estiver instalado.")
    parser.add_argument("--limiar", type=float, help=f"'Não sei' abaixo desta pontuação do reranker (por omissão: {LIMIAR:g}).")
    parser.add_argument("-k", type=int, default=4, help="Quantos artigos mostrar.")
    parser.add_argument("--sem-llm", action="store_true")
    args = parser.parse_args(argv)

    tipo = args.reranker or ("cruzado" if importlib.util.find_spec("fastembed") else "nenhum")
    reranker = None
    if tipo != "nenhum":
        from rag.modelos import Reranker

        print("A carregar o modelo…", file=sys.stderr, flush=True)
        reranker = Reranker(tipo)
    limiar = args.limiar if args.limiar is not None else (LIMIAR if tipo == "cruzado" else None)
    pesquisa = Pesquisa(args.indice, reranker=reranker)
    usar_llm = llm_disponivel() and not args.sem_llm

    def uma(pergunta: str, interativo: bool) -> None:
        consulta = pesquisa.pesquisar(pergunta, args.data, k=max(args.k, 10))
        resposta = responder(consulta, limiar=limiar, usar_llm=usar_llm)
        mostrar(consulta, resposta, args.k)
        registar(consulta, resposta, anotar() if interativo else {})

    if args.pergunta:
        uma(args.pergunta, interativo=False)
        return 0
    print(
        "\nProtótipo: dá o artigo mais provável, não uma resposta escrita"
        + (" (com LLM)." if usar_llm else " (sem LLM).")
        + "\nEscreve a pergunta e carrega Enter. Enter numa linha vazia para sair.\n",
        file=sys.stderr,
    )
    while True:
        try:
            pergunta = input("Pergunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(file=sys.stderr)
            break
        if not pergunta:
            break
        uma(pergunta, interativo=True)
    print(f"Obrigado! As perguntas ficaram em {REGISTO.relative_to(RAIZ)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
