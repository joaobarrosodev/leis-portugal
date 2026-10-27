"""Entrada da verificação às cegas do piloto: `consolidacao/verificacao/entrada-piloto.jsonl`.

Uma linha por diploma consolidado (estado "aplicado por regra" em `resultados.jsonl`), com o
texto original, o texto do diploma que altera e o texto consolidado, e nada sobre como foi
feito: sem os registos de alterações, sem as regras e sem as notas "> Alterado pelo/a …" que o
piloto acrescenta aos artigos (quem verifica tem de encontrar sozinho o que mudou).

Quando o diploma que altera passa de 60 mil caracteres (orçamentos, diplomas com muitos
anexos), vão só os artigos dele que mencionam o original, com `alterador_completo: false`.
As regras da verificação estão em `consolidacao/README.md`.

Uso: `python consolidacao/cegas.py`.
"""

from __future__ import annotations

import json
import re

from texto import RAIZ, artigos_alteradores, corpo

PASTA = RAIZ / "consolidacao"
SAIDA = PASTA / "verificacao" / "entrada-piloto.jsonl"
LIMITE = 60_000
_NOTA_PILOTO = re.compile(r"^> (?:Alterado|Aditado|Revogado|Retificado) pelo/a .*, publicado em \d{4}-\d{2}-\d{2}\.\n\n?", re.M)


def main() -> int:
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao.jsonl").read_text(encoding="utf-8").splitlines())}
    resultados = [json.loads(l) for l in (PASTA / "resultados.jsonl").read_text(encoding="utf-8").splitlines()]
    SAIDA.parent.mkdir(exist_ok=True)
    n = 0
    with SAIDA.open("w", encoding="utf-8") as f:
        for r in resultados:
            if r["estado"] != "aplicado por regra":
                continue
            registo = selecao[r["id"]]
            alterador = registo["alterador"]
            texto_alterador = corpo((RAIZ / alterador["path"]).read_text(encoding="utf-8"))
            completo = len(texto_alterador) <= LIMITE
            if not completo:
                texto_alterador = "\n\n".join(
                    "\n".join(a.linhas).strip() for a in artigos_alteradores(texto_alterador, registo["title"])
                )
            consolidado = corpo((RAIZ / r["consolidado"]).read_text(encoding="utf-8"))
            f.write(json.dumps({
                "id": r["id"],
                "titulo": registo["title"],
                "alterador": alterador["title"],
                "alterador_completo": completo,
                "texto_original": corpo((RAIZ / registo["path"]).read_text(encoding="utf-8")),
                "texto_alterador": texto_alterador,
                "texto_consolidado": _NOTA_PILOTO.sub("", consolidado),
            }, ensure_ascii=False) + "\n")
            n += 1
    print(f"{n} diplomas em {SAIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
