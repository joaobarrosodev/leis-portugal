"""collect dre | eurlex | dre-consolidated"""

from __future__ import annotations

import sys
from datetime import date

from leis_portugal.cli.output import acervo, progress, write_failures
from leis_portugal.services.coverage import TypeCoverage, sitemap_coverage, write_coverage
from leis_portugal.services.dre import DreIngestion, imported_references
from leis_portugal.services.eu_versions import collect_eu_versions
from leis_portugal.services.eurlex import EurLexIngestion
from leis_portugal.services.linking import missing_referenced_acts, scan_portuguese_references
from leis_portugal.services.versions import collect_versions
from leis_portugal.sources.dre.consolidated import consolidated_entry


def register(commands) -> None:
    collect = commands.add_parser("collect", help="Recolher documentos de uma fonte oficial.")
    sources = collect.add_subparsers(dest="source", required=True)

    dre = sources.add_parser("dre", help="Recolher diplomas do Diário da República (por data, por caminho ou os que faltam no acervo).")
    target = dre.add_mutually_exclusive_group(required=True)
    target.add_argument("--date", type=date.fromisoformat, help="Data de publicação (AAAA-MM-DD).")
    target.add_argument("--from", dest="date_from", type=date.fromisoformat, help="Início do intervalo (AAAA-MM-DD); usar com --to.")
    target.add_argument("--ref", help="Caminho DRE de um diploma, por exemplo /dr/detalhe/lei/29-2026-1135578391.")
    target.add_argument("--imported", action="store_true", help="Recolher de novo do DRE os registos que ainda têm o texto da importação inicial.")
    target.add_argument("--missing", action="store_true", help="Comparar o acervo com os sitemaps do DRE e recolher os documentos em falta.")
    dre.add_argument("--to", dest="date_to", type=date.fromisoformat, help="Fim do intervalo (inclusive; por omissão: hoje).")
    dre.add_argument("--no-relations", action="store_true", help="Não recolher alterações e retificações (análise jurídica).")
    dre.add_argument("--no-subjects", action="store_true", help="Não recolher os descritores temáticos.")
    dre.add_argument("--workers", type=int, default=1, help="Sessões DRE em paralelo (por omissão: 1).")
    dre.add_argument("--limit", type=int, default=None, help="Com --imported ou --missing: recolher no máximo N diplomas.")
    dre.add_argument("--types", default=None, help="Com --missing: só estes tipos, separados por vírgulas (p. ex. lei,decreto-lei).")
    dre.add_argument("--all", action="store_true", help="Com --missing: recolher também os tipos sobretudo da 2.ª Série (despachos, avisos...).")
    dre.add_argument("--dry-run", action="store_true", help="Com --missing: só contar, sem recolher.")
    dre.set_defaults(handler=collect_dre)

    eurlex = sources.add_parser("eurlex", help="Recolher atos da UE via EUR-Lex/CELLAR.")
    eu_target = eurlex.add_mutually_exclusive_group(required=True)
    eu_target.add_argument("--celex", help="Identificador CELEX, por exemplo 32016R0679.")
    eu_target.add_argument("--from", dest="date_from", type=date.fromisoformat, help="Atos publicados no JO a partir desta data (AAAA-MM-DD).")
    eu_target.add_argument("--date", type=date.fromisoformat, help="Atos publicados no JO numa data (AAAA-MM-DD).")
    eu_target.add_argument("--referenced", action="store_true", help="Atos da UE referidos pela legislação portuguesa e ainda em falta.")
    eu_target.add_argument("--existing", action="store_true", help="Voltar a recolher todos os atos da UE já presentes no acervo.")
    eurlex.add_argument("--to", dest="date_to", type=date.fromisoformat, help="Fim do intervalo (inclusive; por omissão: hoje).")
    eurlex.add_argument("--types", default="RLD", help="Tipos CELEX: R (regulamentos), L (diretivas), D (decisões). Por omissão: RLD.")
    eurlex.add_argument("--limit", type=int, default=None, help="Com --referenced: recolher no máximo N atos (os mais referidos primeiro).")
    eurlex.add_argument("--min-references", type=int, default=1, help="Com --referenced: só atos referidos por pelo menos N diplomas.")
    eurlex.add_argument("--workers", type=int, default=1, help="Recolhas em paralelo (por omissão: 1; recomendado no máximo 4).")
    eurlex.add_argument("--no-consolidated", action="store_true", help="Usar sempre o texto do JO, mesmo que exista versão consolidada.")
    eurlex.add_argument("--language", default="por", help="Língua da expressão CELLAR (por omissão: por).")
    eurlex.set_defaults(handler=collect_eurlex)

    eu_history = sources.add_parser(
        "eurlex-consolidated", help="Histórico de versões consolidadas dos atos da UE já presentes no acervo (EUR-Lex)."
    )
    eu_history.add_argument("--celex", action="append", default=None, help="CELEX de um ato (repetível); por omissão, todos os atos da UE do acervo.")
    eu_history.add_argument("--limit", type=int, default=None, help="Verificar no máximo N atos.")
    eu_history.add_argument("--workers", type=int, default=4, help="Sessões CELLAR em paralelo (por omissão: 4).")
    eu_history.set_defaults(handler=collect_eurlex_consolidated)

    consolidated = sources.add_parser(
        "dre-consolidated", help="Histórico de versões consolidadas do DRE (uma versão por data de entrada em vigor)."
    )
    consolidated.add_argument("--url", action="append", default=None, help="Ligação de legislação consolidada (repetível); por omissão, todo o sitemap do DRE.")
    consolidated.add_argument("--stale", action="store_true", help="Só os diplomas cuja data de atualização no sitemap mudou.")
    consolidated.add_argument("--limit", type=int, default=None, help="Recolher no máximo N diplomas.")
    consolidated.add_argument("--workers", type=int, default=2, help="Sessões DRE em paralelo (por omissão: 2).")
    consolidated.set_defaults(handler=collect_consolidated)


def collect_dre(args) -> int:
    repository = acervo(args)
    service = DreIngestion(repository, with_relations=not args.no_relations, with_subjects=not args.no_subjects)
    if args.ref:
        result = service.ingest(args.ref)
        print(f"{result.action}: {repository.relative(result.path)}")
        return 0
    if args.imported:
        refs = imported_references(repository)
        progress(f"{len(refs)} registo(s) com o texto da importação inicial")
        summary = service.ingest_many(refs[: args.limit] if args.limit else refs, workers=args.workers, progress=progress)
        write_failures(repository.root / "reports" / "dre_imported_failures.jsonl", summary.failures)
        changed = sum(1 for result in summary.documents if result.changed)
        print(f"Diplomas: {len(summary.documents)}; atualizados: {changed}; ignorados: {len(summary.skipped)}; falhas: {len(summary.failures)}")
        return 1 if summary.failures and not summary.documents else 0
    if args.missing:
        return collect_missing(args, repository, service)
    start = args.date or args.date_from
    end = args.date or args.date_to or date.today()
    if args.workers > 1:
        summary = service.ingest_dates_parallel(start, end, workers=args.workers, progress=progress)
        write_failures(repository.root / "reports" / "dre_dates_failures.jsonl", summary.failures)
    else:
        summary = service.ingest_dates(start, end, progress=progress)
    for result in summary.documents:
        print(f"{result.action}: {repository.relative(result.path)}")
    for skipped in summary.skipped:
        print(f"Ignorado: {skipped}", file=sys.stderr)
    for failure in summary.failures:
        print(f"Falha: {failure['ref']}: {failure['error']}", file=sys.stderr)
    return 1 if summary.failures else 0


def _coverage_table(coverage: list[TypeCoverage]) -> None:
    print(f"{'Tipo':<48} {'No DRE':>9} {'No acervo':>10} {'Em falta':>9}")
    for entry in coverage:
        label = f"{entry.label} *" if entry.optional else entry.label
        print(f"{label:<48} {entry.listed:>9} {entry.present:>10} {len(entry.missing):>9}")
    print(
        f"{'Total':<48} {sum(entry.listed for entry in coverage):>9} {sum(entry.present for entry in coverage):>10} "
        f"{sum(len(entry.missing) for entry in coverage):>9}"
    )
    if any(entry.optional for entry in coverage):
        print("* sobretudo 2.ª Série: só recolhidos com --all ou --types.")


def collect_missing(args, repository, service: DreIngestion) -> int:
    """Documentos que os sitemaps do DRE listam e o acervo não tem."""
    types = None
    if args.types:
        requested = [repository.types.resolve(item.strip()) for item in args.types.split(",") if item.strip()]
        unknown = [item.slug for item in requested if not item.known]
        if unknown:
            raise ValueError(f"Tipo(s) fora do vocabulário (config/document_types.yml): {', '.join(unknown)}")
        types = {item.slug for item in requested}
    coverage = sitemap_coverage(repository, service.source.client, types=types, progress=progress)
    write_coverage(repository.root / "reports" / "dre_sitemap_coverage.json", coverage, checked=date.today().isoformat())
    _coverage_table(coverage)
    refs = [ref for entry in coverage if args.all or types is not None or not entry.optional for ref in entry.missing]
    if args.limit:
        refs = refs[: args.limit]
    print(f"A recolher: {len(refs)}")
    if args.dry_run or not refs:
        return 0
    summary = service.ingest_many(refs, workers=args.workers, progress=progress)
    write_failures(repository.root / "reports" / "dre_missing_failures.jsonl", summary.failures)
    changed = sum(1 for result in summary.documents if result.changed)
    print(f"Diplomas: {len(summary.documents)}; gravados: {changed}; ignorados: {len(summary.skipped)}; falhas: {len(summary.failures)}")
    return 1 if summary.failures and not summary.documents else 0


def collect_eurlex(args) -> int:
    repository = acervo(args)
    service = EurLexIngestion(repository, language=args.language, consolidated=not args.no_consolidated)
    if args.celex:
        result = service.ingest(args.celex)
        print(f"Registo {'atualizado' if result.changed else 'inalterado'}: {repository.relative(result.path)}")
        for warning in result.warnings:
            print(f"Aviso: {warning}", file=sys.stderr)
        return 0
    if args.existing:
        summary = service.ingest_existing(workers=args.workers, progress=progress)
    elif args.referenced:
        missing = missing_referenced_acts(scan_portuguese_references(repository), repository.eu_records(), minimum=args.min_references)
        missing = [celex for celex in missing if celex[5] in args.types.upper()]
        progress(f"{len(missing)} ato(s) da UE referidos pela legislação portuguesa ainda sem registo")
        summary = service.ingest_many(missing[: args.limit] if args.limit else missing, workers=args.workers, progress=progress)
        # Atos referidos que não puderam ser recolhidos (p. ex. sem versão portuguesa).
        write_failures(repository.root / "reports" / "eurlex_referenced_failures.jsonl", summary.failures, sort_key="celex")
    else:
        start = args.date or args.date_from
        summary = service.ingest_dates(start, args.date or args.date_to or date.today(), types=args.types, workers=args.workers, progress=progress)
    print(f"Atos recolhidos: {len(summary.results)}; alterados: {summary.changed}; falhas: {len(summary.failures)}")
    for failure in summary.failures:
        print(f"Falha: {failure['celex']}: {failure['error']}", file=sys.stderr)
    return 1 if summary.failures and not summary.results else 0


def collect_consolidated(args) -> int:
    repository = acervo(args)
    entries = [consolidated_entry(url) for url in args.url] if args.url else None
    summary = collect_versions(repository, entries=entries, stale_only=args.stale, limit=args.limit, workers=args.workers, progress=progress)
    write_failures(repository.root / "reports" / "dre_consolidated_failures.jsonl", summary.failures)
    print(
        f"Diplomas: {summary.total}; atualizados: {summary.written}; novos: {summary.created}; "
        f"inalterados: {summary.unchanged}; falhas: {len(summary.failures)}"
    )
    return 1 if summary.failures and not (summary.written or summary.created or summary.unchanged) else 0


def collect_eurlex_consolidated(args) -> int:
    repository = acervo(args)
    summary = collect_eu_versions(repository, celex_list=args.celex, limit=args.limit, workers=args.workers, progress=progress)
    write_failures(repository.root / "reports" / "eurlex_consolidated_failures.jsonl", summary.failures, sort_key="celex")
    print(
        f"Atos: {summary.total}; atualizados: {summary.written}; inalterados: {summary.unchanged}; "
        f"sem consolidações: {summary.skipped}; falhas: {len(summary.failures)}"
    )
    return 1 if summary.failures and not (summary.written or summary.unchanged) else 0
