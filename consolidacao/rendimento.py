"""Quantos diplomas passaram às cegas: numa ronda, ou nos de um ficheiro de ids (um bloco).

Um diploma passa se todos os artigos são `certo`, nada em `instrucoes_em_falta`, `artigos_em_falta`
nem `artigos_a_mais`, e `fora_dos_artigos` começa por "sem alter". Conta a última ronda em que o
diploma esteve.

Uso:
    python consolidacao/rendimento.py RONDA [RONDA …] [--ids FICHEIRO]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from texto import RAIZ

VERIFICACAO = RAIZ / "consolidacao" / "verificacao"


def passaram(rondas: list[int]) -> dict[str, bool]:
    estado: dict[str, bool] = {}
    for ronda in rondas:
        for f in sorted(VERIFICACAO.glob(f"saida-piloto-{ronda}-lote-*.jsonl")):
            veredictos: dict[str, list[str]] = {}
            for linha in f.read_text(encoding="utf-8").splitlines():
                d = json.loads(linha)
                if "veredicto" in d:
                    veredictos.setdefault(d["id"], []).append(d["veredicto"])
                    continue
                estado[d["id"]] = (
                    all(v == "certo" for v in veredictos.get(d["id"], [])) and not d["instrucoes_em_falta"]
                    and not d["artigos_em_falta"] and not d["artigos_a_mais"]
                    and str(d["fora_dos_artigos"]).lower().startswith("sem alter")
                )
    return estado


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("rondas", type=int, nargs="+")
    parser.add_argument("--ids", type=Path, help="o bloco: um id por linha")
    args = parser.parse_args()
    estado = passaram(args.rondas)
    ids = set(args.ids.read_text(encoding="utf-8").split()) if args.ids else set(estado)
    verificados = [i for i in ids if i in estado]
    bons = sum(estado[i] for i in verificados)
    print(f"{len(ids)} diplomas, {len(verificados)} verificados, {bons} sem reparos: {bons / max(len(ids), 1):.0%} do bloco, {bons / max(len(verificados), 1):.0%} dos verificados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
