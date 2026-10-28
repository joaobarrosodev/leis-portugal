"""Segundo travão: um segundo modelo verifica, às cegas, se a resposta escrita se aguenta nos artigos.

    PYTHONPATH=src python -m rag.travao exportar --nome reais
    # uma sessão do Claude lê rag/resultados/privado/llm/<nome>/travao-NN.jsonl e escreve travao-saida-NN.jsonl
    PYTHONPATH=src python -m rag.travao importar --nome reais

Parte de um passo do LLM já feito (`rag.passo_llm`: `entrada-NN.jsonl`, `saida-NN.jsonl`) e de
`rag/resultados/privado/<nome>-llm-detalhe.jsonl`. O verificador recebe a pergunta, os artigos e a
resposta, nunca a resposta certa, e devolve por `id`:

    {"id", "apoiada": true|false, "responde": true|false}

`apoiada`: cada afirmação da resposta está escrita num dos artigos dados (e a citação é de um
deles). `responde`: a resposta responde à pergunta feita. O travão recusa (passa a "não sei")
quando uma das duas é falsa. `importar` mede o que isso custa e rende: quantas respostas certas
perde, quantas erradas apanha, e a fiabilidade e o "não sei" depois do travão.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict

from rag.fontes import RAIZ


PASTA = RAIZ / "rag" / "resultados" / "privado" / "llm"
RESULTADOS = RAIZ / "rag" / "resultados"

INSTRUCOES = """És um verificador de respostas jurídicas. Recebes a mensagem que foi dada a um assistente (data de referência,
artigos numerados e pergunta) e a resposta que ele escreveu. Não sabes qual é a resposta certa; julgas só se a resposta se aguenta.
- "apoiada": true só se cada afirmação da resposta está escrita num dos artigos dados, tal como está em vigor na data de referência,
  e os artigos citados dizem o que a resposta lhes atribui. Se a resposta acrescenta números, prazos, exceções ou condições que não estão nos artigos, false.
- "responde": true só se a resposta responde à pergunta feita (e não a outra parecida, nem a um caso especial quando a pergunta é geral).
Responde só com um objeto JSON por linha: {"id": ..., "apoiada": true|false, "responde": true|false}."""


def _ler(ficheiro) -> list[dict]:
    return [json.loads(x) for x in ficheiro.read_text(encoding="utf-8").splitlines() if x.strip()]


def exportar(nome: str, por_lote: int) -> None:
    pasta = PASTA / nome
    mensagens = {d["id"]: d["mensagem"] for f in sorted(pasta.glob("entrada-*.jsonl")) for d in _ler(f)}
    linhas = [
        {"id": d["id"], "mensagem": mensagens[d["id"]], "resposta": d["resposta"], "citacoes": d["citacoes"]}
        for f in sorted(pasta.glob("saida-*.jsonl"))
        for d in _ler(f)
        if d.get("responde") and d["id"] in mensagens
    ]
    for f in pasta.glob("travao-*.jsonl"):
        f.unlink()
    for i in range(0, len(linhas), por_lote):
        ficheiro = pasta / f"travao-{i // por_lote + 1:02d}.jsonl"
        ficheiro.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in linhas[i : i + por_lote]), encoding="utf-8")
    (pasta / "TRAVAO-INSTRUCOES.md").write_text(INSTRUCOES + "\n", encoding="utf-8")
    print(f"{len(linhas)} respostas para verificar em {-(-len(linhas) // por_lote)} lotes.")


def importar(nome: str) -> None:
    pasta = PASTA / nome
    veredictos = {d["id"]: d for f in sorted(pasta.glob("travao-saida-*.jsonl")) for d in _ler(f)}
    detalhe = [json.loads(x) for x in (RESULTADOS / "privado" / f"{nome}-llm-detalhe.jsonl").read_text(encoding="utf-8").splitlines()]
    por_tipo: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    sem_veredicto = 0
    for x in detalhe:
        r = por_tipo[x["tipo"]]
        r["n"] += 1
        if not x["responde"]:
            r["nao_sei"] += 1
            continue
        v = veredictos.get(x["id"])
        if v is None:
            sem_veredicto += 1
            continue
        recusa = not (v.get("apoiada") and v.get("responde"))
        if x["tipo"] == "sem_resposta":
            r["respondidas_antes"] += 1
            r["apanhadas"] += recusa
            continue
        r["respondidas_antes"] += 1
        r["certas_antes"] += bool(x["certa"])
        if recusa:
            r["recusadas"] += 1
            r["certas_perdidas"] += bool(x["certa"])
            r["erradas_apanhadas"] += not x["certa"]
        else:
            r["respondidas_depois"] += 1
            r["certas_depois"] += bool(x["certa"])
    linhas = ["| Tipo | n | respondidas | certas antes | recusadas pelo travão | certas perdidas | erradas apanhadas | certas/respondidas depois |",
              "|---|--:|--:|--:|--:|--:|--:|--:|"]
    resumo = {}
    for tipo, r in por_tipo.items():
        resumo[tipo] = dict(r)
        if tipo == "sem_resposta":
            linhas.append(f"| {tipo} | {r['n']} | {r['respondidas_antes']} | — | {r['apanhadas']} | — | {r['apanhadas']} | — |")
            continue
        depois = f"{100 * r['certas_depois'] / r['respondidas_depois']:.0f}% ({r['certas_depois']}/{r['respondidas_depois']})" if r["respondidas_depois"] else "—"
        linhas.append(f"| {tipo} | {r['n']} | {r['respondidas_antes']} | {r['certas_antes']} | {r['recusadas']} | {r['certas_perdidas']} | {r['erradas_apanhadas']} | {depois} |")
    (RESULTADOS / f"{nome}-travao.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(linhas))
    if sem_veredicto:
        print(f"\n{sem_veredicto} respostas sem veredicto ficaram de fora.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("acao", choices=("exportar", "importar"))
    parser.add_argument("--nome", required=True)
    parser.add_argument("--lote", type=int, default=15)
    args = parser.parse_args(argv)
    exportar(args.nome, args.lote) if args.acao == "exportar" else importar(args.nome)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
