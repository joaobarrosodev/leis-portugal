"""link | validate | reports | sources | export"""

from __future__ import annotations

import sys
from pathlib import Path

from leis_portugal.cli.output import acervo
from leis_portugal.infrastructure.config import load_source_registry
from leis_portugal.services.export import export_acervo
from leis_portugal.services.linking import link_eu_records, link_republications, resolve_references, scan_entries
from leis_portugal.services.reporting import generate_reports
from leis_portugal.services.validation import validate_repository


def register(commands) -> None:
    commands.add_parser(
        "link", help="Ligar os atos da UE aos diplomas portugueses e resolver as referências por ELI para ids do acervo."
    ).set_defaults(handler=link)
    commands.add_parser("validate", help="Validar o registo de fontes e todos os documentos em data/.").set_defaults(handler=validate)
    commands.add_parser("reports", help="Gerar relatórios a partir dos registos existentes.").set_defaults(handler=reports)
    commands.add_parser("sources", help="Listar o estado registado das fontes.").set_defaults(handler=sources)
    export = commands.add_parser("export", help="Exportar o índice de relações e os metadados (JSONL, SQLite, Parquet).")
    export.add_argument("--output", default="exports", help="Pasta de destino, relativa à raiz do repositório (por omissão: exports).")
    export.add_argument(
        "--format", dest="formats", action="append", choices=("jsonl", "sqlite", "parquet"),
        help="Formato a gerar (repetível); por omissão, todos os disponíveis.",
    )
    export.set_defaults(handler=export_command)


def link(args) -> int:
    repository = acervo(args)
    summary = link_eu_records(repository)
    print(f"Atos da UE no acervo: {summary.eu_records}; atualizados: {summary.updated}; ligações a diplomas portugueses: {summary.relations}")
    entries = scan_entries(repository)
    resolved = resolve_references(repository, entries=entries)
    print(
        f"Referências por ELI: {resolved.checked} registo(s) verificados; resolvidas: {resolved.resolved}; "
        f"\"sem diploma\" passadas a número: {resolved.by_number}; ligações partidas removidas: {resolved.removed}; "
        f"registos atualizados: {resolved.updated}"
    )
    republished = link_republications(repository, entries=entries)
    print(
        f"Consolidados sobre republicações: {republished.consolidated}; ligados ao diploma original: {republished.linked}; "
        f"registos atualizados: {republished.updated}"
    )
    for item in republished.unresolved:
        print(f"  diploma original não encontrado: {item}")
    return 0


def validate(args) -> int:
    issues = validate_repository(acervo(args))
    for issue in issues:
        print(f"{issue.path}: {issue.message}", file=sys.stderr)
    if issues:
        return 1
    print("Validação concluída sem erros.")
    return 0


def reports(args) -> int:
    repository = acervo(args)
    for name, path in generate_reports(repository).items():
        print(f"{name}: {repository.relative(path)}")
    return 0


def sources(args) -> int:
    for source in load_source_registry(args.root):
        print(f"{source.get('id')}: {source.get('status', {}).get('operational', 'desconhecido')}; reutilização={source.get('reuse', {}).get('status', 'desconhecido')}")
    return 0


def export_command(args) -> int:
    repository = acervo(args)
    output = Path(args.output) if Path(args.output).is_absolute() else repository.root / args.output
    summary = export_acervo(repository, output, formats=tuple(args.formats or ("jsonl", "sqlite", "parquet")))
    share = summary.resolved / summary.relations if summary.relations else 0
    print(f"Documentos: {summary.documents}; relações: {summary.relations}; com alvo no acervo: {summary.resolved} ({share:.0%})")
    kinds = sorted({kind for kind, _ in summary.by_target})
    for kind in kinds:
        print(f"  {kind:<10} resolvidas {summary.by_target[(kind, True)]:>8}   por resolver {summary.by_target[(kind, False)]:>8}")
    for path in summary.files:
        print(f"Escrito: {repository.relative(path)}")
    for skipped in summary.skipped:
        print(f"Não gerado: {skipped}", file=sys.stderr)
    return 1 if args.formats and summary.skipped else 0
