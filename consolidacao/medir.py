"""Números do piloto: `consolidacao/medicao.json`, a partir de `resultados.jsonl`.

Quantos diplomas ficaram aplicados por regra, quantos ficam para o LLM, quantos não têm
alteração textual a aplicar e porquê, quantas alterações por regra, as comparações com as
republicações e a estimativa do que custa o LLM (pedidos e tokens).

Uso: `python consolidacao/medir.py`.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict

from llm import estimar
from texto import RAIZ

PASTA = RAIZ / "consolidacao"


def main() -> int:
    resultados = [json.loads(l) for l in (PASTA / "resultados.jsonl").read_text(encoding="utf-8").splitlines()]
    pendentes = [json.loads(l) for l in (PASTA / "pendentes.jsonl").read_text(encoding="utf-8").splitlines()]
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao.jsonl").read_text(encoding="utf-8").splitlines())}

    estados: dict[str, Counter] = defaultdict(Counter)
    for r in resultados:
        estados[r["estado"]][r["motivo"] or "—"] += 1
    regras = Counter()
    for r in resultados:
        if r["estado"] == "aplicado por regra":
            regras.update(r.get("regras", {}))
    republicacoes = [
        {"title": r["title"], "estado": r["estado"], **r["republicacao"]}
        for r in resultados if r.get("republicacao")
    ]
    for rep in republicacoes:
        rep.pop("so_na_republicacao", None)
    medicao = {
        "diplomas": len(resultados),
        "por_estado": {e: {"total": sum(c.values()), "motivos": dict(c.most_common())} for e, c in
                       sorted(estados.items(), key=lambda kv: -sum(kv[1].values()))},
        "alteracoes_aplicadas_por_regra": dict(regras.most_common()),
        "comparacao_com_republicacoes": republicacoes,
        "titulos_pelo_parser_da_fase_3": dict(Counter(r["estado"] for r in resultados if r.get("titulos_normalizados"))),
        "llm": {"pedidos_feitos": 0, "tokens_usados": 0,
                "motivo": "sem ANTHROPIC_API_KEY no ambiente do piloto; a entrada para uma sessão do Claude está em llm/entrada-sessao.jsonl",
                "estimativa_para_os_pendentes": estimar(pendentes, selecao)},
    }
    (PASTA / "medicao.json").write_text(json.dumps(medicao, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for estado, dados in medicao["por_estado"].items():
        print(f"{dados['total']:4d}  {estado}")
        for motivo, n in dados["motivos"].items():
            print(f"        {n:4d}  {motivo}")
    print("Alterações por regra:", medicao["alteracoes_aplicadas_por_regra"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
