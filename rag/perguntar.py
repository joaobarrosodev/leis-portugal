"""Fazer perguntas ao protótipo, uma a uma, e anotar as que falham.

    PYTHONPATH=src python -m rag.perguntar "Qual é a coima por não usar cinto de segurança?"
    PYTHONPATH=src python -m rag.perguntar --reranker cruzado        # modo interativo

Mostra a resposta (sem chave da API, o primeiro artigo encontrado) e os artigos encontrados,
com os avisos (revogado, texto original de um diploma alterado, redação antiga…). No modo
interativo pergunta se a resposta está certa e, se não estiver, que artigo se esperava.

Cada pergunta fica em `rag/resultados/privado/perguntas-testadas.jsonl` (fora do git), com a
resposta, os artigos e a anotação, para as que falham entrarem no conjunto de avaliação.
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from datetime import date, datetime
from pathlib import Path

from rag.fontes import RAIZ
from rag.pesquisa import Consulta, Pesquisa
from rag.resposta import llm_disponivel, responder


REGISTO = RAIZ / "rag" / "resultados" / "privado" / "perguntas-testadas.jsonl"


def mostrar(consulta: Consulta, resposta, k: int) -> None:
    print()
    if resposta.responde:
        print("Resposta" + (" (LLM)" if resposta.com_llm else " (sem LLM: o primeiro artigo encontrado)") + ":")
        print(textwrap.indent(resposta.texto.strip(), "  "))
    else:
        print(f"Não sei ({resposta.motivo}).")
    for aviso in resposta.avisos:
        print(f"  ! {aviso}")
    if consulta.diplomas_em_falta:
        print(f"  ! Citados e não encontrados no acervo: {', '.join(consulta.diplomas_em_falta)}")
    print(f"\nArtigos encontrados (data {consulta.data}):")
    for n, r in enumerate(consulta.resultados[:k], 1):
        pontos = f" [reranker {r.reranker:.1f}]" if r.reranker is not None else ""
        print(f"  {n}. {r.rotulo}{pontos}")
        for aviso in r.avisos:
            print(f"     ! {aviso}")
        print(textwrap.indent(textwrap.shorten(r.texto, 240, placeholder=" …"), "     "))
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
        certo = input("Certo? [s/n, Enter para saltar] ").strip().lower()
    except EOFError:
        return {}
    if certo.startswith("s"):
        return {"certo": True}
    if certo.startswith("n"):
        esperado = input("Que artigo e diploma esperavas? (p. ex. art. 238.º do Código do Trabalho) ").strip()
        return {"certo": False, "esperado": esperado}
    return {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pergunta", nargs="?", help="Sem pergunta, abre o modo interativo.")
    parser.add_argument("--data", default=date.today().isoformat(), help="Data de referência (AAAA-MM-DD; por omissão: hoje).")
    parser.add_argument("--indice", type=Path)
    parser.add_argument("--reranker", choices=("cruzado", "denso"), help="Reordena os candidatos com um modelo multilingue (extra `rag`).")
    parser.add_argument("--limiar", type=float, default=None, help="'Não sei' quando o reranker dá ao melhor artigo menos do que isto (medido: 3).")
    parser.add_argument("-k", type=int, default=5, help="Quantos artigos mostrar.")
    parser.add_argument("--sem-llm", action="store_true")
    args = parser.parse_args(argv)

    reranker = None
    if args.reranker:
        from rag.modelos import Reranker

        reranker = Reranker(args.reranker)
    pesquisa = Pesquisa(args.indice, reranker=reranker)
    usar_llm = llm_disponivel() and not args.sem_llm

    def uma(pergunta: str, interativo: bool) -> None:
        consulta = pesquisa.pesquisar(pergunta, args.data, k=max(args.k, 10))
        resposta = responder(consulta, limiar=args.limiar, usar_llm=usar_llm)
        mostrar(consulta, resposta, args.k)
        registar(consulta, resposta, anotar() if interativo else {})

    if args.pergunta:
        uma(args.pergunta, interativo=False)
        return 0
    print(f"LLM: {'sim' if usar_llm else 'não'}; reranker: {args.reranker or 'não'}. Linha vazia ou Ctrl-D para sair.", file=sys.stderr)
    while True:
        try:
            pergunta = input("Pergunta: ").strip()
        except EOFError:
            break
        if not pergunta:
            break
        uma(pergunta, interativo=True)
    print(f"Perguntas guardadas em {REGISTO.relative_to(RAIZ)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
