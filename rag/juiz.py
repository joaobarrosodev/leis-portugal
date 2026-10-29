"""Juízes estritos: dois juízes independentes, às cegas, julgam cada resposta escrita contra a resposta de referência.

    PYTHONPATH=src python -m rag.juiz exportar --nome reais2
    # duas sessões do Claude (juiz A e juiz B, sem ver o trabalho uma da outra) lêem
    # rag/resultados/privado/llm/<nome>/juiz-NN.jsonl e escrevem juiz-a-saida-NN.jsonl / juiz-b-saida-NN.jsonl
    PYTHONPATH=src python -m rag.juiz importar --nome reais2

Substitui o critério brando das 80% de palavras. Uma resposta só conta como certa se os DOIS juízes a dão
como "correta" e "fundamentada". Qualquer discordância conta como não certa (critério conservador). `importar`
mostra a fiabilidade com o intervalo de confiança de Wilson a 95%; o número a citar é o limite inferior.
"""

from __future__ import annotations

import argparse
import json
from math import sqrt

from rag.fontes import RAIZ


PASTA = RAIZ / "rag" / "resultados" / "privado" / "llm"
RESULTADOS = RAIZ / "rag" / "resultados"
PERGUNTAS = RAIZ / "avaliacao" / "privado" / "perguntas-reais.jsonl"

INSTRUCOES = """És um juiz rigoroso de respostas jurídicas. Para cada linha recebes: a pergunta, a resposta de referência
(escrita por uma pessoa a partir da fonte oficial), os artigos que o sistema viu e a resposta que o sistema escreveu.
Não conheces o autor da resposta. Sê exigente: um erro que levasse alguém a agir mal conta como erro.
Devolve por id um objeto JSON numa linha: {"id", "veredicto", "fundamentada", "nota"}.
- "veredicto":
  - "correta": diz o mesmo que a referência no essencial (números, prazos, condições, exceções) e não afirma nada falso;
  - "incompleta": nada falso, mas falta algo essencial que a referência diz;
  - "errada": contradiz a referência, responde a outra pergunta, ou afirma algo falso ou que mudaria a conclusão.
- "fundamentada": true só se cada afirmação da resposta está escrita nos artigos que o sistema viu (e não é invenção ou conhecimento externo).
- "nota": uma frase a dizer porquê, só se não for "correta" ou não for fundamentada.
Não procures nada fora destas linhas."""


def _ler(f) -> list[dict]:
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]


def wilson_inferior(k: int, n: int, z: float = 1.96) -> float:
    if n == 0:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - m) / d


def exportar(nome: str, por_lote: int) -> None:
    pasta = PASTA / nome
    ref = {d["id"]: d for d in _ler(PERGUNTAS)}
    artigos = {d["id"]: d["mensagem"].split("Artigos:", 1)[1].rsplit("Pergunta:", 1)[0].strip() for f in sorted(pasta.glob("entrada-*.jsonl")) for d in _ler(f)}
    perguntas = {d["id"]: d["mensagem"].rsplit("Pergunta:", 1)[1].strip() for f in sorted(pasta.glob("entrada-*.jsonl")) for d in _ler(f)}
    linhas = [
        {"id": d["id"], "pergunta": perguntas[d["id"]], "referencia": ref[d["id"]]["resposta"], "artigos": artigos[d["id"]], "resposta_do_sistema": d["resposta"]}
        for f in sorted(pasta.glob("saida-*.jsonl"))
        for d in _ler(f)
        if d.get("responde") and d["id"] in ref
    ]
    for f in pasta.glob("juiz-*.jsonl"):
        f.unlink()
    for i in range(0, len(linhas), por_lote):
        (pasta / f"juiz-{i // por_lote + 1:02d}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in linhas[i : i + por_lote]), encoding="utf-8")
    (pasta / "JUIZ-INSTRUCOES.md").write_text(INSTRUCOES + "\n", encoding="utf-8")
    print(f"{len(linhas)} respostas para julgar em {-(-len(linhas) // por_lote)} lotes (cada uma por 2 juízes).")


def importar(nome: str) -> None:
    pasta = PASTA / nome
    juizes = {j: {d["id"]: d for f in sorted(pasta.glob(f"juiz-{j}-saida-*.jsonl")) for d in _ler(f)} for j in "ab"}
    detalhe = [json.loads(x) for x in (RESULTADOS / "privado" / f"{nome}-llm-detalhe.jsonl").read_text(encoding="utf-8").splitlines()]
    n_tipo = {"real": 0}
    respondidas = certas = incompletas = erradas = sem_fundamento = discordam = so_um = 0
    brandas_certas = 0
    ids_nao_certos = []
    for x in detalhe:
        if x["tipo"] != "real":
            continue
        n_tipo["real"] += 1
        if not x["responde"]:
            continue
        respondidas += 1
        brandas_certas += bool(x["certa"])
        a, b = juizes["a"].get(x["id"]), juizes["b"].get(x["id"])
        if not a or not b:
            so_um += 1
            ids_nao_certos.append(x["id"])
            continue
        ok = lambda v: v["veredicto"] == "correta" and v.get("fundamentada") is True  # noqa: E731
        if ok(a) and ok(b):
            certas += 1
            continue
        ids_nao_certos.append(x["id"])
        discordam += ok(a) != ok(b)
        incompletas += a["veredicto"] == "incompleta" or b["veredicto"] == "incompleta"
        erradas += a["veredicto"] == "errada" or b["veredicto"] == "errada"
        sem_fundamento += not (a.get("fundamentada") and b.get("fundamentada"))
    n = n_tipo["real"]
    inf = wilson_inferior(certas, respondidas)
    resumo = {
        "perguntas": n, "respondidas": respondidas, "nao_sei": n - respondidas,
        "certas_criterio_brando": brandas_certas, "certas_juizes": certas,
        "fiabilidade_juizes": round(certas / respondidas, 3) if respondidas else None,
        "fiabilidade_limite_inferior_95": round(inf, 3),
        "nao_certas": {"juizes_discordam": discordam, "incompletas": incompletas, "erradas": erradas, "sem_fundamento": sem_fundamento, "sem_julgamento": so_um},
        "ids_nao_certos": ids_nao_certos,
    }
    (RESULTADOS / f"{nome}-juizes.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Reais: {n}; respondidas {respondidas} ({n - respondidas} 'não sei').")
    print(f"Certas (critério brando, 80% das palavras): {brandas_certas}/{respondidas} = {100 * brandas_certas / max(respondidas, 1):.0f}%")
    print(f"Certas (os dois juízes: correta e fundamentada): {certas}/{respondidas} = {100 * certas / max(respondidas, 1):.0f}%  | limite inferior 95%: {100 * inf:.0f}%")
    print(f"Não certas: incompletas {incompletas}, erradas {erradas}, sem fundamento {sem_fundamento}, juízes discordam {discordam}, sem julgamento {so_um}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("acao", choices=("exportar", "importar"))
    p.add_argument("--nome", required=True)
    p.add_argument("--lote", type=int, default=10)
    a = p.parse_args(argv)
    exportar(a.nome, a.lote) if a.acao == "exportar" else importar(a.nome)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
