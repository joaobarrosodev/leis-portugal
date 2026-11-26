"""Medição de base dos casos de advogado: só a pesquisa, como a app 0.1.1 (BM25 + reranker cruzado, limiar 3).

Duas formas de pesquisar cada caso:
- `inteiro`: o texto que o advogado escreveria na app (narrativa, leis que pensa usar e perguntas), numa consulta só.
  É o que o sistema faz hoje.
- `por_questao`: uma consulta por questão jurídica, com as questões que o autor do caso escreveu à mão. Mostra o
  teto de um fluxo que separe o caso em questões; é otimista, porque as questões já vêm bem formuladas.

Conta-se cada artigo essencial pela melhor posição em que aparece (no `por_questao`, em qualquer das consultas,
na lista juntada pela ordem das notas). Um caso fica «coberto em k» quando todos os essenciais estão nos k primeiros.

Com `--decomposicao PASTA` mede, em vez daquelas duas, as consultas que um LLM escreveu para cada caso
(`decomposto`) e essas mais os artigos que ele achou prováveis (`decomposto_com_artigos`), intercaladas.

    RAG_INDICE=<pasta do índice> python avaliacao/casos/medir.py [--indice X] [--nome casos-base] [--decomposicao avaliacao/casos/decomposicao]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from rag.pesquisa import Pesquisa  # noqa: E402

KS = (1, 3, 8, 10, 30)


def texto_inteiro(caso: dict) -> str:
    leis = "; ".join(lp["como_cita"] for lp in caso.get("leis_pensadas", []))
    perguntas = " ".join(caso["questoes"])
    return f"{caso['narrativa']}\n\nEstou a pensar usar: {leis}.\n\n{perguntas}"


def posicoes(resultados, essenciais: list[dict]) -> list[int | None]:
    pos: list[int | None] = []
    for e in essenciais:
        p = next((n for n, r in enumerate(resultados, 1) if r.documento == e["documento"] and r.chave == e["artigo"]), None)
        pos.append(p)
    return pos


def juntar(consultas) -> list:
    """Os resultados de várias consultas numa lista só, cada artigo uma vez, pela melhor nota do reranker."""
    melhor: dict[tuple[str, str], object] = {}
    for c in consultas:
        for r in c.resultados:
            chave = (r.documento, r.chave)
            nota = r.reranker if r.reranker is not None else float("-inf")
            atual = melhor.get(chave)
            if atual is None or nota > (atual.reranker if atual.reranker is not None else float("-inf")):
                melhor[chave] = r
    return sorted(melhor.values(), key=lambda r: -(r.reranker if r.reranker is not None else float("-inf")))


def intercalar(listas: list[list]) -> list:
    """O 1.º de cada lista, depois o 2.º de cada, …; cada artigo uma vez. Cada consulta tem lugar nos primeiros."""
    vistos, saida = set(), []
    for i in range(max((len(l) for l in listas), default=0)):
        for l in listas:
            if i < len(l) and (l[i].documento, l[i].chave) not in vistos:
                vistos.add((l[i].documento, l[i].chave))
                saida.append(l[i])
    return saida


def formatar(resultados) -> str:
    """Os artigos numerados como o `rag.resposta.contexto` os dá ao LLM."""
    from rag.resposta import CARACTERES_POR_ARTIGO

    return "\n\n".join(f"[{n}] {r.rotulo}" + "".join(f"\nAviso: {a}" for a in r.avisos) + f"\n{r.texto[:CARACTERES_POR_ARTIGO]}"
                       for n, r in enumerate(resultados, 1))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--casos", type=Path, default=RAIZ / "avaliacao" / "casos" / "casos.jsonl")
    parser.add_argument("--indice", type=Path)
    parser.add_argument("--nome", default="casos-base")
    parser.add_argument("--exportar", type=Path, help="Pasta onde escrever, por lotes de 10, o pedido e os artigos da 1.ª estratégia (para um LLM responder).")
    parser.add_argument("--contexto", type=int, default=16, help="Com --exportar: quantos artigos vão por caso.")
    parser.add_argument(
        "--decomposicao", type=Path,
        help="Pasta com saida-*.jsonl ({id, consultas, artigos_provaveis}): mede só `decomposto` (uma pesquisa por consulta, "
             "intercaladas) e `decomposto_com_artigos` (o mesmo, mais uma pesquisa por artigo provável).",
    )
    args = parser.parse_args(argv)
    from rag.modelos import Reranker

    decomposicao = None
    if args.decomposicao:
        decomposicao = {d["id"]: d for f in sorted(args.decomposicao.glob("saida-*.jsonl"))
                        for d in map(json.loads, filter(str.strip, f.read_text(encoding="utf-8").splitlines()))}
    estrategias = ("decomposto", "decomposto_com_artigos") if decomposicao else ("inteiro", "por_questao")
    exportados: list[dict] = []
    pesquisa = Pesquisa(args.indice, reranker=Reranker("cruzado", maximo=30))
    casos = [json.loads(l) for l in args.casos.read_text(encoding="utf-8").splitlines() if l.strip()]
    linhas = []
    inicio = time.time()
    for n, caso in enumerate(casos, 1):
        essenciais = caso["resposta"]["artigos_essenciais"]
        data = caso["data_referencia"]
        if decomposicao:
            d = decomposicao[caso["id"]]
            por_consulta = [pesquisa.pesquisar(q, data, k=max(KS)) for q in d["consultas"]]
            por_artigo = [pesquisa.pesquisar(a, data, k=3) for a in d.get("artigos_provaveis") or []]
            listas = {"decomposto": intercalar([c.resultados for c in por_consulta]),
                      "decomposto_com_artigos": intercalar([c.resultados[:1] for c in por_artigo] + [c.resultados for c in por_consulta])}
        else:
            inteiro = pesquisa.pesquisar(texto_inteiro(caso), data, k=max(KS))
            listas = {"inteiro": inteiro.resultados, "por_questao": juntar([pesquisa.pesquisar(q, data, k=max(KS)) for q in caso["questoes"]])}
        linha = {"id": caso["id"], "area": caso["area"], "essenciais": [f"{e['titulo']} › {e['artigo']}" for e in essenciais]}
        for nome, resultados in listas.items():
            linha[nome] = {"posicoes": posicoes(resultados, essenciais), "topo": [f"{r.rotulo}" for r in resultados[:5]],
                           "nota_topo": resultados[0].reranker if resultados else None}
        linhas.append(linha)
        if args.exportar:
            lista = listas[estrategias[-1] if decomposicao else estrategias[0]][: args.contexto]
            exportados.append({"id": caso["id"], "data_referencia": data, "pedido": texto_inteiro(caso), "artigos": formatar(lista),
                               "rotulos": [r.rotulo for r in lista], "chaves": [[r.documento, r.chave] for r in lista]})
        print(f"[{n}/{len(casos)}] {caso['id']} " + " ".join(f"{e} {linha[e]['posicoes']}" for e in estrategias)
              + f" ({time.time() - inicio:.0f}s)", file=sys.stderr)

    resumo: dict[str, dict] = {}
    for nome in estrategias:
        todas = [p for l in linhas for p in l[nome]["posicoes"]]
        resumo[nome] = {
            "casos": len(linhas),
            "artigos_essenciais": len(todas),
            **{f"artigos_top{k}": sum(1 for p in todas if p is not None and p <= k) for k in KS},
            **{f"casos_cobertos_top{k}": sum(1 for l in linhas if all(p is not None and p <= k for p in l[nome]["posicoes"])) for k in KS},
            "casos_algum_top8": sum(1 for l in linhas if any(p is not None and p <= 8 for p in l[nome]["posicoes"])),
        }
    por_area: dict[str, dict] = {}
    for l in linhas:
        a = por_area.setdefault(l["area"], {"casos": 0, **{f"cobertos_top8_{e}": 0 for e in estrategias}})
        a["casos"] += 1
        for nome in estrategias:
            a[f"cobertos_top8_{nome}"] += all(p is not None and p <= 8 for p in l[nome]["posicoes"])
    saida = RAIZ / "rag" / "resultados" / f"{args.nome}.json"
    saida.write_text(json.dumps({"configuracao": {"reranker": "cruzado", "maximo": 30, "llm": False, "indice": str(args.indice) if args.indice else None},
                                 "resumo": resumo, "por_area": por_area, "casos": linhas}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"resumo": resumo, "por_area": por_area}, ensure_ascii=False, indent=1))
    print(f"Gravado em {saida}", file=sys.stderr)
    if args.exportar:
        args.exportar.mkdir(parents=True, exist_ok=True)
        for i in range(0, len(exportados), 10):
            lote = args.exportar / f"entrada-{i // 10 + 1:02d}.jsonl"
            lote.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in exportados[i:i + 10]), encoding="utf-8")
        print(f"Exportados {len(exportados)} casos para {args.exportar}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
