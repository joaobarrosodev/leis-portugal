"""Medição pequena e emparelhada do reranker por passagens (`Reranker(passagens=True)`).

Para cada pergunta pedida, corre a pesquisa quatro vezes com o mesmo reranker em modo `estavel` (cada
texto pontuado sozinho e a nota guardada):

- `base`: como a aplicação 0.1.1, mas com `estavel`;
- `passagens`: o reranker lê também as passagens dos artigos compridos;
- `perguntas`: o reranker lê as perguntas por artigo (`reranker_com_perguntas`);
- `perguntas+passagens`: as duas coisas.

Como as notas se guardam, o início de cada artigo só é pontuado uma vez, e a diferença entre os braços
não tem ruído de lote: vem só das passagens. Regista, por braço, a posição do artigo certo, a nota do
1.º, se responde com o limiar, quantos textos novos o reranker leu e quanto tempo levou.

    RAG_INDICE=... PYTHONPATH=src:. python scripts/medir_passagens.py --indice rag/indice/indice-final.sqlite \
        --perguntas avaliacao/privado/perguntas-reais.jsonl --ids real-001,real-003 \
        --saida rag/resultados/privado/passagens-pequena.jsonl

A saída tem ids e números, sem o texto das perguntas; mesmo assim fica em `rag/resultados/privado/`.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from rag.avaliar import pontuar
from rag.modelos import PASSAGENS_ARTIGO, PASSAGENS_PERGUNTA, Reranker
from rag.pesquisa import Pesquisa
from rag.resposta import responder


BRACOS = ("base", "passagens", "perguntas", "perguntas+passagens")


def medir(pesquisas: dict[bool, Pesquisa], reranker: Reranker, p: dict, limiar: float) -> dict:
    linha = {"id": p["id"], "tipo": p["tipo"]}
    reranker.notas.clear()
    for braco in BRACOS:
        reranker.passagens = "passagens" in braco
        antes, inicio = len(reranker.notas), time.time()
        consulta = pesquisas["perguntas" in braco].pesquisar(p["pergunta"], p["data_referencia"], k=10)
        segundos = time.time() - inicio
        x = pontuar(p, consulta, responder(consulta, limiar=limiar, usar_llm=False))
        fonte = p.get("fonte") or {}
        certo = next((r for r in consulta.resultados if r.documento == fonte.get("documento") and r.chave == fonte.get("artigo")), None)
        linha[braco] = {
            "posicao_artigo": x["posicao_artigo"], "posicao_texto": x["posicao_texto"], "topo": x["topo"], "topo_reranker": x["topo_reranker"],
            "responde": x["responde"], "certa": x["certa"], "nota_certo": certo.reranker if certo else None,
            "certo_por_passagem": bool(certo and certo.passagem), "topo_por_passagem": bool(consulta.resultados and consulta.resultados[0].passagem),
            "textos_novos": len(reranker.notas) - antes, "segundos": round(segundos, 1),
        }
    return linha


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--indice", type=Path, required=True)
    parser.add_argument("--perguntas", type=Path, action="append", required=True)
    parser.add_argument("--ids", required=True, help="Ids separados por vírgulas, ou um ficheiro com um id por linha.")
    parser.add_argument("--saida", type=Path, required=True)
    parser.add_argument("--limiar", type=float, default=3.0)
    parser.add_argument("--fios", type=int, default=3)
    parser.add_argument("--passagens-artigo", type=int, default=PASSAGENS_ARTIGO)
    parser.add_argument("--passagens-pergunta", type=int, default=PASSAGENS_PERGUNTA)
    args = parser.parse_args(argv)

    perguntas = {}
    for ficheiro in args.perguntas:
        for linha in ficheiro.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                x = json.loads(linha)
                perguntas[x["id"]] = x
    ids = Path(args.ids).read_text(encoding="utf-8").split() if Path(args.ids).exists() else args.ids.split(",")
    feitas = set()
    if args.saida.exists():
        feitas = {json.loads(linha)["id"] for linha in args.saida.read_text(encoding="utf-8").splitlines() if linha.strip()}

    reranker = Reranker(
        "cruzado", fios=args.fios, estavel=True, passagens_artigo=args.passagens_artigo, passagens_pergunta=args.passagens_pergunta,
    )
    pesquisas = {False: Pesquisa(args.indice, reranker=reranker), True: Pesquisa(args.indice, reranker=reranker, reranker_com_perguntas=True)}
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    inicio = time.time()
    with args.saida.open("a", encoding="utf-8") as f:
        for n, i in enumerate(ids, 1):
            if i in feitas or i not in perguntas:
                continue
            linha = medir(pesquisas, reranker, perguntas[i], args.limiar)
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")
            f.flush()
            print(f"{n}/{len(ids)} {i} ({time.time() - inicio:.0f} s) " + " ".join(
                f"{b}: {linha[b]['posicao_artigo']} ({linha[b]['textos_novos']} textos, {linha[b]['segundos']} s)" for b in BRACOS
            ), file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
