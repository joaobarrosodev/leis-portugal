"""A segunda volta do fluxo de caso, por lotes: junta ao contexto os artigos que a 1.ª análise disse que faltavam.

    RAG_INDICE=<pasta do índice> python avaliacao/casos/completar.py PASTA_1 PASTA_2 [--indice X] [--nome casos-completar]

PASTA_1 tem `entrada-NN.jsonl` (com `chaves`) e `saida-NN.jsonl` (a 1.ª análise, com `falta` e `contas`). Para cada caso
com `falta`, `rag.caso.completar` pesquisa cada consulta e junta até 8 artigos novos, numerados depois dos que já lá
estavam; as `contas` válidas fazem-se com `rag.prazos` e vão no campo `contas`. PASTA_2 recebe `entrada-NN.jsonl` só com
os casos que ganharam artigos ou contas (é a esses que se volta a analisar) e `iguais.json` com os outros. Escreve em `rag/resultados/<nome>.json` quantos essenciais estavam no contexto antes e depois.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from rag import caso as caso_mod  # noqa: E402
from rag import prazos as prazos_mod  # noqa: E402
from rag.pesquisa import Pesquisa  # noqa: E402


def _jsonl(f: Path) -> list[dict]:
    return [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pasta_1", type=Path)
    parser.add_argument("pasta_2", type=Path)
    parser.add_argument("--indice", type=Path)
    parser.add_argument("--nome", default="casos-completar")
    parser.add_argument("--casos", type=Path, default=RAIZ / "avaliacao" / "casos" / "casos.jsonl")
    args = parser.parse_args(argv)
    from rag.modelos import Reranker

    casos = {c["id"]: c for c in _jsonl(args.casos)}
    entradas = {e["id"]: e for f in sorted(args.pasta_1.glob("entrada-*.jsonl")) for e in _jsonl(f)}
    saidas = {s["id"]: s for f in sorted(args.pasta_1.glob("saida-*.jsonl")) for s in _jsonl(f)}
    pesquisa = Pesquisa(args.indice, reranker=Reranker("cruzado", maximo=30))
    novas, iguais, linhas = [], [], []
    for n, (id_, e) in enumerate(entradas.items(), 1):
        falta = caso_mod._textos(saidas.get(id_, {}).get("falta"), caso_mod.MAXIMO_FALTA)
        ja = [tuple(c) for c in e["chaves"]]
        novos = caso_mod.completar(pesquisa, set(ja), falta, e["data_referencia"]) if falta else []
        saida = saidas.get(id_, {})
        pedidas = [c for c in map(prazos_mod.de_json, saida.get("contas") or [] if isinstance(saida.get("contas"), list) else []) if c]
        contas = caso_mod.contas_feitas(pedidas[: caso_mod.MAXIMO_CONTAS], e["data_referencia"])
        ess = [(x["documento"], x["artigo"]) for x in casos[id_]["resposta"]["artigos_essenciais"]]
        depois = ja + [(r.documento, r.chave) for r in novos]
        linhas.append({"id": id_, "falta": falta, "acrescentados": [r.rotulo for r in novos], "contas_pedidas": len(pedidas),
                       "contas": contas,
                       "essenciais": len(ess), "antes": sum(x in ja for x in ess), "depois": sum(x in depois for x in ess)})
        if novos or contas:
            extra = "\n\n" + caso_mod.contexto(novos, inicio=len(ja) + 1) if novos else ""
            novas.append(e | {"artigos": e["artigos"] + extra,
                              "rotulos": e.get("rotulos", []) + [r.rotulo for r in novos],
                              "chaves": e["chaves"] + [[r.documento, r.chave] for r in novos]} | ({"contas": contas} if contas else {}))
        else:
            iguais.append(id_)
        print(f"[{n}/{len(entradas)}] {id_} falta {len(falta)} +{len(novos)} essenciais {linhas[-1]['antes']}→{linhas[-1]['depois']}/{len(ess)}",
              file=sys.stderr, flush=True)
    args.pasta_2.mkdir(parents=True, exist_ok=True)
    for i in range(0, len(novas), 10):
        (args.pasta_2 / f"entrada-{i // 10 + 1:02d}.jsonl").write_text(
            "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in novas[i:i + 10]), encoding="utf-8")
    (args.pasta_2 / "iguais.json").write_text(json.dumps(iguais, ensure_ascii=False) + "\n", encoding="utf-8")
    resumo = {"casos": len(linhas), "com_falta": sum(bool(l["falta"]) for l in linhas), "completados": len(novas),
              "consultas_em_falta": sum(len(l["falta"]) for l in linhas), "artigos_acrescentados": sum(len(l["acrescentados"]) for l in linhas),
              "contas_pedidas": sum(l["contas_pedidas"] for l in linhas), "casos_com_contas": sum(bool(l["contas"]) for l in linhas),
              "essenciais": sum(l["essenciais"] for l in linhas), "essenciais_antes": sum(l["antes"] for l in linhas),
              "essenciais_depois": sum(l["depois"] for l in linhas),
              "casos_com_todos_antes": sum(l["antes"] == l["essenciais"] for l in linhas),
              "casos_com_todos_depois": sum(l["depois"] == l["essenciais"] for l in linhas)}
    (RAIZ / "rag" / "resultados" / f"{args.nome}.json").write_text(
        json.dumps({"resumo": resumo, "casos": linhas}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
