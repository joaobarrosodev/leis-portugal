"""O passo do LLM sem chave da API: uma sessão do Claude lê os artigos e responde, em lotes.

    PYTHONPATH=src python -m rag.passo_llm exportar --nome reais --tipos real,sem_resposta
    # uma sessão do Claude lê rag/resultados/privado/llm/<nome>/entrada-NN.jsonl e escreve saida-NN.jsonl
    PYTHONPATH=src python -m rag.passo_llm importar --nome reais

`exportar` faz a pesquisa (com o reranker e o limiar da avaliação), deixa de fora as perguntas a
que as regras já respondem "não sei" e escreve, por lote, a pergunta, a data e os artigos
numerados, tal como o `resposta.py` os daria ao LLM, mais o `INSTRUCOES.md` com as instruções.
Cada linha de `saida-NN.jsonl` é `{"id", "responde", "resposta", "citacoes"}`, o mesmo objeto
JSON que o `resposta.py` pede à API. `importar` junta as respostas à pesquisa, pontua-as como o
`rag.avaliar` com LLM (cita o artigo certo e tem o mesmo sentido) e escreve
`rag/resultados/<nome>-llm.json` (só números) e o detalhe em `privado/`.

A sessão que responde não pode ver as respostas certas: só recebe `entrada-NN.jsonl`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rag import avaliar
from rag.fontes import RAIZ
from rag.pesquisa import Pesquisa
from rag.resposta import INSTRUCOES, LIMIAR_PADRAO, Resposta, contexto, interpretar, mensagem, nao_sei_antes


PASTA = RAIZ / "rag" / "resultados" / "privado" / "llm"


def exportar(nome: str, tipos: set[str], por_lote: int, limiar: float, indice: Path | None) -> None:
    from rag.modelos import Reranker

    pesquisa = Pesquisa(indice, reranker=Reranker("cruzado"))
    perguntas = [p for p in avaliar.ler_perguntas() if p["tipo"] in tipos]
    pasta = PASTA / nome
    pasta.mkdir(parents=True, exist_ok=True)
    for f in pasta.glob("entrada-*.jsonl"):
        f.unlink()
    entradas, regras = [], 0
    for n, p in enumerate(perguntas, 1):
        consulta = pesquisa.pesquisar(p["pergunta"], p["data_referencia"], k=max(avaliar.KS))
        if nao_sei_antes(consulta, limiar):
            regras += 1
            continue
        texto, _ = contexto(consulta)
        entradas.append({"id": p["id"], "mensagem": mensagem(consulta, texto)})
        if n % 25 == 0:
            print(f"{n}/{len(perguntas)}", file=sys.stderr, flush=True)
    for i in range(0, len(entradas), por_lote):
        ficheiro = pasta / f"entrada-{i // por_lote + 1:02d}.jsonl"
        ficheiro.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entradas[i : i + por_lote]), encoding="utf-8")
    (pasta / "INSTRUCOES.md").write_text(
        INSTRUCOES + "\n\nCada linha de entrada-NN.jsonl tem `id` e `mensagem` (a data, os artigos numerados e a pergunta)."
        " Escreve em saida-NN.jsonl, uma linha por `id`, o objeto JSON pedido acima mais o campo `id`.\n",
        encoding="utf-8",
    )
    print(f"{len(entradas)} perguntas para o LLM em {-(-len(entradas) // por_lote)} lotes; {regras} já são 'não sei' pelas regras.")


def importar(nome: str, tipos: set[str], limiar: float, indice: Path | None) -> None:
    from rag.modelos import Reranker

    respostas: dict[str, dict] = {}
    for f in sorted((PASTA / nome).glob("saida-*.jsonl")):
        for linha in f.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                d = json.loads(linha)
                respostas[d["id"]] = d
    pesquisa = Pesquisa(indice, reranker=Reranker("cruzado"))
    linhas, em_falta = [], 0
    for p in (p for p in avaliar.ler_perguntas() if p["tipo"] in tipos):
        consulta = pesquisa.pesquisar(p["pergunta"], p["data_referencia"], k=max(avaliar.KS))
        motivo = nao_sei_antes(consulta, limiar)
        if motivo:
            resposta = Resposta(False, "Não sei.", motivo=motivo)
        elif p["id"] in respostas:
            resposta = interpretar(respostas[p["id"]], consulta.resultados[:8])
        else:
            em_falta += 1
            continue
        linhas.append(avaliar.pontuar(p, consulta, resposta))
    resumo = avaliar.guardar(f"{nome}-llm", {"reranker": "cruzado", "limiar": limiar, "llm": "sessão do Claude"}, linhas)
    print(avaliar.tabela(resumo))
    if em_falta:
        print(f"\n{em_falta} perguntas sem resposta do LLM ficaram de fora.", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("acao", choices=("exportar", "importar"))
    parser.add_argument("--nome", required=True)
    parser.add_argument("--tipos", default="real,sem_resposta", help="Tipos de pergunta, separados por vírgulas.")
    parser.add_argument("--lote", type=int, default=10)
    parser.add_argument("--limiar", type=float, default=LIMIAR_PADRAO)
    parser.add_argument("--indice", type=Path)
    args = parser.parse_args(argv)
    tipos = set(args.tipos.split(","))
    if args.acao == "exportar":
        exportar(args.nome, tipos, args.lote, args.limiar, args.indice)
    else:
        importar(args.nome, tipos, args.limiar, args.indice)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
