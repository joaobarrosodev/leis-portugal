"""Juízes estritos: dois juízes independentes, às cegas, julgam cada resposta escrita contra a resposta de referência.

    PYTHONPATH=src python -m rag.juiz exportar --nome reais2
    # duas sessões do Claude (juiz A e juiz B, sem ver o trabalho uma da outra) lêem
    # rag/resultados/privado/llm/<nome>/juiz-NN.jsonl e escrevem juiz-a-saida-NN.jsonl / juiz-b-saida-NN.jsonl
    PYTHONPATH=src python -m rag.juiz importar --nome reais2

Substitui o critério brando das 80% de palavras. Quatro papéis, cada um uma sessão sem ver as outras:
`a` e `b` (rigorosos, com a referência), `c` (cético: procura ativamente o erro, com a referência) e `s` (sem a
referência: só a pergunta, os artigos e a resposta, em `juiz-sr-NN.jsonl`). Uma resposta só conta como certa se TODOS
a dão como "correta" e "fundamentada". Qualquer discordância conta como não certa (critério conservador). `importar`
mostra a fiabilidade com o intervalo de confiança de Wilson a 95%; o número a citar é o limite inferior.
"""

from __future__ import annotations

import argparse
import json
from math import sqrt

from rag.fontes import RAIZ


PASTA = RAIZ / "rag" / "resultados" / "privado" / "llm"
RESULTADOS = RAIZ / "rag" / "resultados"
PERGUNTAS = (
    RAIZ / "avaliacao" / "perguntas.jsonl",
    RAIZ / "avaliacao" / "privado" / "perguntas-reais.jsonl",
    RAIZ / "avaliacao" / "privado" / "perguntas-coloquiais.jsonl",
)
PAPEIS = ("a", "b", "c", "s")

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
Não procures nada fora destas linhas.
- Se a linha traz "premissa", a pergunta contém uma premissa que pode estar errada: a resposta só é "correta" se corrige a premissa como a referência faz.
- Papel "cético": parte do princípio de que há um erro e procura-o (número trocado, exceção ou condição em falta, norma de outra data, caso especial tomado por regra geral); só dá "correta" se não o encontra.
- Papel "sem referência": não recebes a resposta de referência; julga só se a resposta responde à pergunta e se cada afirmação está nos artigos vistos ("correta" = responde e está toda fundamentada)."""


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


def _referencias() -> dict[str, dict]:
    return {d["id"]: d for f in PERGUNTAS if f.exists() for d in _ler(f)}


def exportar(nome: str, por_lote: int) -> None:
    pasta = PASTA / nome
    ref = _referencias()
    entradas = [d for f in sorted(pasta.glob("entrada-*.jsonl")) for d in _ler(f)]
    artigos = {d["id"]: d["mensagem"].split("Artigos:", 1)[1].rsplit("Pergunta:", 1)[0].strip() for d in entradas}
    perguntas = {d["id"]: d["mensagem"].rsplit("Pergunta:", 1)[1].strip() for d in entradas}
    linhas = []
    for f in sorted(pasta.glob("saida-*.jsonl")):
        for d in _ler(f):
            r = ref.get(d["id"])
            if not d.get("responde") or r is None or r["tipo"] == "sem_resposta":
                continue
            x = {"id": d["id"], "pergunta": perguntas[d["id"]], "referencia": r["resposta"], "artigos": artigos[d["id"]], "resposta_do_sistema": d["resposta"]}
            if r.get("premissa"):
                x["premissa"] = r["premissa"]
            linhas.append(x)
    for f in pasta.glob("juiz-*.jsonl"):
        f.unlink()
    for i in range(0, len(linhas), por_lote):
        lote = linhas[i : i + por_lote]
        n = f"{i // por_lote + 1:02d}"
        escrever = lambda ficheiro, itens: ficheiro.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in itens), encoding="utf-8")  # noqa: E731
        escrever(pasta / f"juiz-{n}.jsonl", lote)
        escrever(pasta / f"juiz-sr-{n}.jsonl", [{k: v for k, v in x.items() if k != "referencia"} for x in lote])
    (pasta / "JUIZ-INSTRUCOES.md").write_text(INSTRUCOES + "\n", encoding="utf-8")
    print(f"{len(linhas)} respostas para julgar em {-(-len(linhas) // por_lote)} lotes (cada uma por {len(PAPEIS)} juízes).")


def importar(nome: str) -> None:
    pasta = PASTA / nome
    juizes = {j: {d["id"]: d for f in sorted(pasta.glob(f"juiz-{j}-saida-*.jsonl")) for d in _ler(f)} for j in PAPEIS}
    juizes = {j: v for j, v in juizes.items() if v}  # só os papéis que julgaram
    detalhe = [json.loads(x) for x in (RESULTADOS / "privado" / f"{nome}-llm-detalhe.jsonl").read_text(encoding="utf-8").splitlines()]

    def ok(v):
        return v["veredicto"] == "correta" and v.get("fundamentada") is True

    por_tipo: dict[str, dict] = {}
    for x in detalhe:
        r = por_tipo.setdefault(x["tipo"], {"n": 0, "respondidas": 0, "certas_brando": 0, "certas": 0, "incompletas": 0, "erradas": 0, "sem_fundamento": 0, "discordam": 0, "sem_julgamento": 0, "ids_nao_certos": []})
        r["n"] += 1
        if not x["responde"]:
            continue
        r["respondidas"] += 1
        r["certas_brando"] += bool(x["certa"])
        if x["tipo"] == "sem_resposta":
            continue  # respondeu sem haver resposta: errada por definição
        vs = [juizes[j].get(x["id"]) for j in juizes]
        if not all(vs):
            r["sem_julgamento"] += 1
            r["ids_nao_certos"].append(x["id"])
            continue
        if all(ok(v) for v in vs):
            r["certas"] += 1
            continue
        r["ids_nao_certos"].append(x["id"])
        r["discordam"] += any(ok(v) for v in vs)
        r["incompletas"] += any(v["veredicto"] == "incompleta" for v in vs)
        r["erradas"] += any(v["veredicto"] == "errada" for v in vs)
        r["sem_fundamento"] += any(not v.get("fundamentada") for v in vs)
    total = {k: sum(r[k] for t, r in por_tipo.items() if t != "sem_resposta") for k in ("n", "respondidas", "certas_brando", "certas")}
    linhas = [f"Juízes: {', '.join(juizes)} (certa = todos dizem correta e fundamentada).", "",
              '| Tipo | n | respondidas | "não sei" | certas (brando) | certas (juízes) | fiabilidade | limite inferior 95% |', "|---|--:|--:|--:|--:|--:|--:|--:|"]
    for t, r in [*por_tipo.items(), ("total", total)]:
        if t == "sem_resposta":
            linhas.append(f"| sem_resposta | {r['n']} | {r['respondidas']} | {100 * (r['n'] - r['respondidas']) / r['n']:.0f}% | — | — | recusou {r['n'] - r['respondidas']}/{r['n']} | — |")
            continue
        c, d = (r["certas"], r["respondidas"])
        linhas.append(f"| {t} | {r['n']} | {d} | {100 * (r['n'] - d) / r['n']:.0f}% | {r['certas_brando']} | {c} | {100 * c / max(d, 1):.0f}% ({c}/{d}) | {100 * wilson_inferior(c, d):.0f}% |")
    por_tipo["total"] = total | {"fiabilidade": round(total["certas"] / max(total["respondidas"], 1), 3), "limite_inferior_95": round(wilson_inferior(total["certas"], total["respondidas"]), 3)}
    (RESULTADOS / f"{nome}-juizes.json").write_text(json.dumps({"juizes": list(juizes), "por_tipo": por_tipo}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(linhas))


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
