"""Entrada da verificação às cegas do piloto: `consolidacao/verificacao/entrada-piloto.jsonl`.

Uma linha por diploma consolidado (estado "aplicado por regra" em `resultados.jsonl` ou
"aplicado com LLM" em `llm/juntados.jsonl`, sem dizer qual), com o
texto original, o texto do diploma que altera e o texto consolidado, e nada sobre como foi
feito: sem os registos de alterações, sem as regras e sem as notas "> Alterado pelo/a …" que o
piloto acrescenta aos artigos (quem verifica tem de encontrar sozinho o que mudou).

Quando o diploma que altera passa de 60 mil caracteres (orçamentos, diplomas com muitos
anexos), vão só os artigos dele que mencionam o original, com `alterador_completo: false`.
Quando os títulos dos artigos do original foram normalizados (artigos em texto corrido, ver
`texto.com_titulos`), a linha diz `titulos_normalizados: true` e traz também o original com os
títulos, `texto_original_com_titulos`. As regras da verificação estão em `consolidacao/README.md`.

Rondas: `--ronda 1` escreve `entrada-piloto.jsonl` com todos os aplicados por regra; `--ronda N`
escreve `entrada-piloto-N.jsonl` só com os que não estão nas rondas anteriores ou cujo
consolidado mudou desde a última em que estiveram (as rondas anteriores já foram verificadas e
não se reescrevem).

Uso: `python consolidacao/cegas.py [--ronda N]`.
"""

from __future__ import annotations

import argparse
import json
import re

from texto import RAIZ, artigos_alteradores, com_titulos, corpo, publicado

PASTA = RAIZ / "consolidacao"


def entrada(ronda: int):
    return PASTA / "verificacao" / ("entrada-piloto.jsonl" if ronda == 1 else f"entrada-piloto-{ronda}.jsonl")
LIMITE = 60_000
_NOTA_PILOTO = re.compile(r"^> (?:Alterado|Aditado|Revogado|Retificado) pelo/a .*, publicado em \d{4}-\d{2}-\d{2}\.\n\n?", re.M)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ronda", type=int, default=1)
    args = parser.parse_args()
    saida = entrada(args.ronda)
    anteriores = {}
    for ronda in range(1, args.ronda):
        anteriores |= {d["id"]: d["texto_consolidado"] for d in map(json.loads, entrada(ronda).read_text(encoding="utf-8").splitlines())}
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao.jsonl").read_text(encoding="utf-8").splitlines())}
    resultados = [json.loads(l) for l in (PASTA / "resultados.jsonl").read_text(encoding="utf-8").splitlines()]
    juntados = PASTA / "llm" / "juntados.jsonl"
    if juntados.exists():
        resultados += [j for j in map(json.loads, juntados.read_text(encoding="utf-8").splitlines()) if j["estado"] == "aplicado com LLM"]
    saida.parent.mkdir(exist_ok=True)
    n = 0
    with saida.open("w", encoding="utf-8") as f:
        for r in resultados:
            if r["estado"] not in ("aplicado por regra", "aplicado com LLM"):
                continue
            registo = selecao[r["id"]]
            consolidado = _NOTA_PILOTO.sub("", corpo((RAIZ / r["consolidado"]).read_text(encoding="utf-8")))
            if anteriores.get(r["id"]) == consolidado:
                continue
            alterador = registo["alterador"]
            texto_alterador = publicado(RAIZ / alterador["path"])
            completo = len(texto_alterador) <= LIMITE
            if not completo:
                texto_alterador = "\n\n".join(
                    "\n".join(a.linhas).strip() for a in artigos_alteradores(texto_alterador, registo["title"])
                )
            original = publicado(RAIZ / registo["path"])
            linha = {
                "id": r["id"],
                "titulo": registo["title"],
                "alterador": alterador["title"],
                "alterador_completo": completo,
                "texto_original": original,
                "texto_alterador": texto_alterador,
                "texto_consolidado": consolidado,
            }
            if r.get("titulos_normalizados"):
                linha |= {"titulos_normalizados": True, "texto_original_com_titulos": com_titulos(original)}
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")
            n += 1
    print(f"{n} diplomas em {saida.relative_to(RAIZ)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
