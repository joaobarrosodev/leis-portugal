"""import legalize"""

from __future__ import annotations

import sys
from pathlib import Path

from leis_portugal.cli.output import acervo, progress, write_failures
from leis_portugal.services.legalize_import import import_legalize


def register(commands) -> None:
    importer = commands.add_parser("import", help="Importar acervos de terceiros para a estrutura do repositório.")
    sources = importer.add_subparsers(dest="source", required=True)
    legalize = sources.add_parser("legalize", help="Converter um clone local do legalize-pt.")
    legalize.add_argument("--path", type=Path, required=True, help="Pasta do clone do legalize-pt.")
    legalize.add_argument("--workers", type=int, default=None, help="Número de processos (por omissão: CPUs - 1).")
    legalize.add_argument("--limit", type=int, default=None, help="Converter apenas os primeiros N ficheiros (testes).")
    legalize.add_argument("--years", default=None, help="Lista de anos separados por vírgulas, por exemplo 2023,2024.")
    legalize.set_defaults(handler=import_legalize_command)


def import_legalize_command(args) -> int:
    repository = acervo(args)
    years = {item.strip() for item in args.years.split(",")} if args.years else None
    summary = import_legalize(repository, args.path, workers=args.workers, limit=args.limit, years=years, progress=progress)
    failures_path = repository.root / "reports" / "import_legalize_failures.jsonl"
    write_failures(failures_path, summary.failures)
    print(
        f"Ficheiros: {summary.total}; escritos: {summary.written}; inalterados: {summary.unchanged}; "
        f"mantidos (versão existente prevalece): {summary.kept_existing}; falhas: {len(summary.failures)}"
    )
    if summary.failures:
        print(f"Falhas registadas em {repository.relative(failures_path)}", file=sys.stderr)
    return 1 if summary.failures else 0
