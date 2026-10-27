"""version-at"""

from __future__ import annotations

import sys
from datetime import date

from leis_portugal.cli.output import acervo
from leis_portugal.domain.history import render_version, version_at


def register(commands) -> None:
    parser = commands.add_parser("version-at", help="Texto de um diploma consolidado numa data.")
    parser.add_argument("diploma", help="Caminho do registo .md ou id (pt:dre:<id>:por).")
    parser.add_argument("--date", type=date.fromisoformat, default=date.today(), help="Data (AAAA-MM-DD; por omissão: hoje).")
    parser.add_argument("--list", action="store_true", help="Listar as versões em vez de mostrar o texto.")
    parser.set_defaults(handler=version_at_command)


def version_at_command(args) -> int:
    repository = acervo(args)
    path = repository.find(args.diploma)
    if path is None:
        print(f"Diploma não encontrado: {args.diploma}", file=sys.stderr)
        return 1
    record, _ = repository.read(path)
    history = repository.read_history(path)
    if history is None:
        print(f"{repository.relative(path)} não tem histórico de versões.", file=sys.stderr)
        return 1
    if args.list:
        for item in history["versions"]:
            acts = "; ".join(act["title"] for act in item["acts"] if act.get("title")) or "texto original"
            print(f"{item['date']}  {acts}  ({len(item['changes'])} modificação(ões))")
        return 0
    version = version_at(history, args.date.isoformat())
    if version is None:
        print(f"Não há versão em vigor em {args.date.isoformat()}.", file=sys.stderr)
        return 1
    print(render_version(history, version, title=record.title), end="")
    return 0
