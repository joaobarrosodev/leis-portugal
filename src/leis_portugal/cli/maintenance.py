"""link | validate | reports | sources"""

from __future__ import annotations

import sys

from leis_portugal.cli.output import acervo
from leis_portugal.infrastructure.config import load_source_registry
from leis_portugal.services.linking import link_eu_records
from leis_portugal.services.reporting import generate_reports
from leis_portugal.services.validation import validate_repository


def register(commands) -> None:
    commands.add_parser("link", help="Ligar os atos da UE aos diplomas portugueses que os transpõem ou citam.").set_defaults(handler=link)
    commands.add_parser("validate", help="Validar o registo de fontes e todos os documentos em data/.").set_defaults(handler=validate)
    commands.add_parser("reports", help="Gerar relatórios a partir dos registos existentes.").set_defaults(handler=reports)
    commands.add_parser("sources", help="Listar o estado registado das fontes.").set_defaults(handler=sources)


def link(args) -> int:
    summary = link_eu_records(acervo(args))
    print(f"Atos da UE no acervo: {summary.eu_records}; atualizados: {summary.updated}; ligações a diplomas portugueses: {summary.relations}")
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
