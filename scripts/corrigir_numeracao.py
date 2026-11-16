"""Corrige no acervo as gralhas de numeração dos títulos de artigo (`domain/numbering.py`).

A recolha do DRE já corrige as gralhas isoladas dos registos novos (`sources/dre/mapper.py` e
`services/versions.py`). Este script aplica a mesma regra aos registos que já estão em `data/`,
com uma nota em `notes` por correção. Com `--repetidos`, corrige também os números repetidos
(2.º, 2.º, 4.º), que foram lidos um a um a 16/11/2026. A recolha não os corrige.

Não mexe na UE (`data/european_union`): os títulos vêm do EUR-Lex.

Uso: `python scripts/corrigir_numeracao.py [--repetidos] [--escrever] > corrigidos.jsonl`
(sem `--escrever` só lista).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from leis_portugal.domain.numbering import find_number_fixes, fix_article_numbers
from leis_portugal.infrastructure.repository import PORTUGUESE_SCOPES, Acervo


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raiz", type=Path, default=Path("."))
    parser.add_argument("--repetidos", action="store_true")
    parser.add_argument("--escrever", action="store_true")
    args = parser.parse_args()
    acervo = Acervo(args.raiz)
    total = 0
    for path in acervo.paths(PORTUGUESE_SCOPES):
        text = path.read_text(encoding="utf-8")
        if "###### Art" not in text:
            continue
        record, body = acervo.read(path)
        fixes = find_number_fixes(body, repeated=args.repetidos)
        if not fixes:
            continue
        fixed, notes = fix_article_numbers(body, repeated=args.repetidos)
        lines = body.split("\n")
        for fix in fixes:
            total += 1
            print(json.dumps({
                "path": str(path.relative_to(acervo.root)), "id": record.id, "lido": fix.written, "corrigido": fix.fixed,
                "antes": fix.before, "depois": fix.after, "tipo": "repetido" if fix.repeated else "gralha",
                "titulo": lines[fix.line],
            }, ensure_ascii=False))
        if args.escrever:
            record.notes.extend(note for note in notes if note not in record.notes)
            acervo.write(record, fixed, path)
    print(f"{total} correção(ões)" + (" gravadas" if args.escrever else " por gravar"), file=sys.stderr)


if __name__ == "__main__":
    main()
