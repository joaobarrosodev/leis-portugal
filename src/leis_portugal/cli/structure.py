"""structure"""

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

from leis_portugal.cli.output import acervo, progress
from leis_portugal.services.structure import run, write_report


def register(commands) -> None:
    parser = commands.add_parser(
        "structure",
        help="Artigos com id estável, datas de entrada em vigor e vigência: relatório de cobertura (sem alterar registos).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Só medir e escrever o relatório; obrigatório enquanto a escrita nos registos não existir.",
    )
    parser.add_argument("--output", default="reports", help="Pasta do relatório, relativa à raiz (por omissão: reports).")
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1), help="Processos paralelos (1: sem paralelismo).")
    parser.add_argument("--validation-sample", type=int, default=300, help="Consolidados a comparar com os fragmentos do DRE (0: não validar).")
    parser.add_argument("--today", type=date.fromisoformat, default=date.today(), help="Data de referência (AAAA-MM-DD; por omissão: hoje).")
    parser.add_argument("--limit", type=int, default=None, help="Ler só os primeiros N registos (para testes).")
    parser.set_defaults(handler=structure_command)


def structure_command(args) -> int:
    if not args.dry_run:
        print("Por agora só existe o relatório: use `leis-portugal structure --dry-run`.", file=sys.stderr)
        return 2
    repository = acervo(args)
    output = Path(args.output) if Path(args.output).is_absolute() else repository.root / args.output
    report = run(
        repository, workers=args.workers, today=args.today.isoformat(), validation_sample=args.validation_sample,
        limit=args.limit, progress=progress,
    )
    articles, entry, validity = report.summary["artigos"], report.summary["entrada_em_vigor"], report.summary["vigencia"]
    print(f"Diplomas com texto: {articles['com_texto']}; com artigos: {articles['com_artigos']}; só com números: {articles['por_unidade'].get('numeros', 0)}")
    print(
        f"Entrada em vigor: {entry['calculadas_do_texto']} calculadas; {entry['so_regra']} só com a regra; "
        f"{entry['supletivas']} pela regra supletiva; {entry['sem_clausula']} sem cláusula"
    )
    print(f"Vigência desconhecida: {validity['desconhecidos']}; com estado proposto: {validity['resolvidos']}")
    if report.validation:
        current = report.validation.get("atual", {})
        print(f"Validação: {current.get('tudo_igual', 0)} de {current.get('diplomas', 0)} consolidados com os mesmos artigos e epígrafes")
    for path in write_report(report, output):
        print(f"Escrito: {repository.relative(path) if path.is_relative_to(repository.root) else path}")
    return 0
