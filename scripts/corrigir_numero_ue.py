"""Corrige no acervo o número oficial dos atos da UE que o CELLAR dá errado (`official_number` no mapper).

A recolha do EUR-Lex já grava o número certo nos registos novos e nos recolhidos outra vez. Este script
aplica a mesma regra aos registos que já estão em `data/european_union`, com uma nota em `notes`. O
ficheiro não muda de sítio: o caminho é só o nome, e o repositório encontra o registo pelo id (CELEX).

Uso: `python scripts/corrigir_numero_ue.py [--escrever] > corrigidos.jsonl` (sem `--escrever` só lista).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from leis_portugal.domain.identifiers import parse_celex
from leis_portugal.infrastructure.repository import EU_SCOPE, Acervo
from leis_portugal.sources.eurlex.mapper import official_number


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raiz", type=Path, default=Path("."))
    parser.add_argument("--escrever", action="store_true")
    args = parser.parse_args()
    acervo = Acervo(args.raiz)
    total = 0
    for path in acervo.paths((EU_SCOPE,)):
        record, body = acervo.read(path)
        written = record.official_number or ""
        if not record.identifiers.celex or "/" not in written:
            continue
        year, number = written.split("/", 1)
        if not (year.isdigit() and number.isdigit()):
            continue
        celex = parse_celex(record.identifiers.celex)
        fixed, note = official_number(
            (int(year), int(number)), celex=(celex.year, celex.number), title=record.title,
            publication_year=int(record.publication_date[:4]) if record.publication_date else None,
            authors=record.issuing_authority,
        )
        if note is None:
            continue
        total += 1
        print(json.dumps({
            "path": str(path.relative_to(acervo.root)), "id": record.id, "celex": record.identifiers.celex,
            "cellar": written, "corrigido": fixed, "titulo": record.title, "nota": note,
        }, ensure_ascii=False))
        if args.escrever:
            record.official_number = fixed
            if note not in record.notes:
                record.notes.append(note)
            acervo.write(record, body, path)
    print(f"{total} correção(ões)" + (" gravadas" if args.escrever else " por gravar"), file=sys.stderr)


if __name__ == "__main__":
    main()
