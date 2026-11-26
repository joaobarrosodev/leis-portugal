"""Prepara os lotes dos juízes e conta o resultado da medição experimental dos casos.

    python avaliacao/casos/juizes.py preparar PASTA_LLM PASTA_JUIZ     # junta caso de referência + análise do sistema
    python avaliacao/casos/juizes.py contar PASTA_LLM PASTA_JUIZ [--nome X] # junta os veredictos e escreve rag/resultados/X.json

Com `--casos FICHEIRO`, usa outro conjunto de casos (por omissão, `avaliacao/casos/casos.jsonl`).

PASTA_LLM tem `entrada-NN.jsonl` (com `chaves`, os artigos dados) e `saida-NN.jsonl` (as respostas).
PASTA_JUIZ recebe `lote-NN.jsonl` e, de cada juiz, `juiz-<letra>-NN.jsonl`.
Uma análise conta como certa só se todos os juízes lhe dão `certa`.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[2]
CASOS = RAIZ / "avaliacao" / "casos" / "casos.jsonl"


def _jsonl(f: Path) -> list[dict]:
    return [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]


def _respostas(pasta: Path) -> dict[str, dict]:
    entradas = {e["id"]: e for f in sorted(pasta.glob("entrada-*.jsonl")) for e in _jsonl(f)}
    saidas = {s["id"]: s for f in sorted(pasta.glob("saida-*.jsonl")) for s in _jsonl(f)}
    juntas = {}
    for id_, e in entradas.items():
        s = saidas.get(id_, {"responde": False, "analise": {}, "citacoes": []})
        cit = [n for n in s.get("citacoes") or [] if isinstance(n, int) and 1 <= n <= len(e["chaves"])]
        juntas[id_] = {"entrada": e, "saida": s, "citadas": [tuple(e["chaves"][n - 1]) for n in cit],
                       "rotulos_citados": [(e.get("rotulos") or [None] * len(e["chaves"]))[n - 1] or f"{e['chaves'][n - 1][1]}" for n in cit]}
    return juntas


def preparar(pasta_llm: Path, pasta_juiz: Path, ficheiro: Path = CASOS) -> None:
    casos = _jsonl(ficheiro)
    respostas = _respostas(pasta_llm)
    pasta_juiz.mkdir(parents=True, exist_ok=True)
    linhas = []
    for c in casos:
        r = respostas[c["id"]]
        linhas.append({"caso": c, "sistema": {"responde": r["saida"].get("responde"), "analise": r["saida"].get("analise"),
                                               "artigos_citados": r["rotulos_citados"]}})
    for i in range(0, len(linhas), 10):
        (pasta_juiz / f"lote-{i // 10 + 1:02d}.jsonl").write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas[i:i + 10]), encoding="utf-8")
    print(f"{len(linhas)} casos em {pasta_juiz}")


def contar(pasta_llm: Path, pasta_juiz: Path, nome: str | None, ficheiro: Path = CASOS) -> None:
    casos = _jsonl(ficheiro)
    respostas = _respostas(pasta_llm)
    juizes: dict[str, dict[str, dict]] = {}
    for f in sorted(pasta_juiz.glob("juiz-*-*.jsonl")):
        letra = f.stem.split("-")[1]
        for v in _jsonl(f):
            juizes.setdefault(letra, {})[v["id"]] = v
    letras = sorted(juizes)
    por_caso = []
    for c in casos:
        ess = [(e["documento"], e["artigo"]) for e in c["resposta"]["artigos_essenciais"]]
        r = respostas[c["id"]]
        dados = {tuple(x) for x in r["entrada"]["chaves"]}
        vs = {l: juizes[l].get(c["id"]) for l in letras}
        verds = [v["veredicto"] if v else "sem_juiz" for v in vs.values()]
        por_caso.append({
            "id": c["id"], "area": c["area"], "dificuldade": c["dificuldade"],
            "essenciais": len(ess), "essenciais_dados": sum(e in dados for e in ess), "essenciais_citados": sum(e in set(r["citadas"]) for e in ess),
            "veredictos": dict(zip(letras, verds, strict=False)),
            "certa": bool(verds) and all(v == "certa" for v in verds),
            "errada_algum": any(v == "errada" for v in verds),
            "leis_pensadas": {l: (vs[l] or {}).get("leis_pensadas") for l in letras},
            "prazos": {l: (vs[l] or {}).get("prazos") for l in letras},
        })
    n = len(por_caso)
    resumo = {
        "casos": n, "juizes": letras,
        "certas_todos_os_juizes": sum(p["certa"] for p in por_caso),
        "errada_para_algum_juiz": sum(p["errada_algum"] for p in por_caso),
        "veredictos_por_juiz": {l: dict(Counter(p["veredictos"][l] for p in por_caso)) for l in letras},
        "essenciais": sum(p["essenciais"] for p in por_caso),
        "essenciais_dados": sum(p["essenciais_dados"] for p in por_caso),
        "essenciais_citados": sum(p["essenciais_citados"] for p in por_caso),
        "casos_com_todos_os_essenciais_dados": sum(p["essenciais_dados"] == p["essenciais"] for p in por_caso),
        "leis_pensadas_por_juiz": {l: [sum((p["leis_pensadas"][l] or {}).get(k, 0) for p in por_caso) for k in ("acertou", "total")] for l in letras},
        "prazos_por_juiz": {l: dict(Counter(p["prazos"][l] for p in por_caso)) for l in letras},
    }
    print(json.dumps(resumo, ensure_ascii=False, indent=1))
    if nome:
        (RAIZ / "rag" / "resultados" / f"{nome}.json").write_text(
            json.dumps({"resumo": resumo, "casos": por_caso}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("acao", choices=("preparar", "contar"))
    parser.add_argument("pasta_llm", type=Path)
    parser.add_argument("pasta_juiz", type=Path)
    parser.add_argument("--nome")
    parser.add_argument("--casos", type=Path, default=CASOS)
    args = parser.parse_args()
    if args.acao == "preparar":
        preparar(args.pasta_llm, args.pasta_juiz, args.casos)
    else:
        contar(args.pasta_llm, args.pasta_juiz, args.nome, args.casos)
