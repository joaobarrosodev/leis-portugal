"""Recolha de atos da União Europeia (EUR-Lex/CELLAR)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date

from leis_portugal.errors import LeisPortugalError
from leis_portugal.infrastructure.repository import Acervo, WriteResult
from leis_portugal.services.common import EU_POLICY, Progress, failure, run_parallel, silent
from leis_portugal.sources.eurlex.source import EurLexSource


@dataclass
class EurLexRunSummary:
    results: list[WriteResult] = field(default_factory=list)
    failures: list[dict[str, str]] = field(default_factory=list)

    @property
    def changed(self) -> int:
        return sum(1 for result in self.results if result.changed)


class EurLexIngestion:
    def __init__(
        self,
        acervo: Acervo,
        *,
        source_factory: Callable[[], EurLexSource] = EurLexSource,
        language: str = "por",
        consolidated: bool = True,
    ) -> None:
        self.acervo = acervo
        self.source_factory = source_factory
        self.language = language
        self.consolidated = consolidated

    def ingest(self, celex: str, source: EurLexSource | None = None) -> WriteResult:
        document = (source or self.source_factory()).collect(celex, language=self.language, consolidated=self.consolidated)
        record, body = document.record, document.body
        path = self.acervo.path_for(record)
        if path.exists():
            existing, existing_body = self.acervo.read(path)
            if existing.version_history and self.acervo.read_history(path) is not None:
                # Com histórico de versões, o texto e a versão vêm do histórico
                # (`collect eurlex-consolidated`); aqui só se atualizam os metadados.
                record.version = existing.version
                record.version_history = existing.version_history
                record.article_structure = existing.article_structure
                record.integrity = existing.integrity
                record.source.consolidated_url = existing.source.consolidated_url
                body = existing_body
        return self.acervo.save(record, body, policy=EU_POLICY)

    def ingest_many(self, celex_list: list[str], *, workers: int = 1, progress: Progress = silent) -> EurLexRunSummary:
        """Vários CELEX em paralelo (uma sessão CELLAR por thread); uma falha não
        interrompe os restantes."""
        summary = EurLexRunSummary()

        def work(celex: str, source: EurLexSource) -> str:
            try:
                result = self.ingest(celex, source)
            except LeisPortugalError as exc:
                summary.failures.append(failure("celex", celex, exc))
                return f"{celex}: falha: {exc}"
            summary.results.append(result)
            return f"{celex}: {'atualizado' if result.changed else 'inalterado'}"

        run_parallel(celex_list, work, context=self.source_factory, workers=workers, progress=progress)
        return summary

    def ingest_dates(self, start: date, end: date, *, types: str = "RLD", workers: int = 1, progress: Progress = silent) -> EurLexRunSummary:
        """Atos publicados no Jornal Oficial entre duas datas (inclusive)."""
        discovered = self.source_factory().discover(start, end, types=types)
        progress(f"{start.isoformat()} a {end.isoformat()}: {len(discovered)} ato(s) no Jornal Oficial")
        return self.ingest_many(discovered, workers=workers, progress=progress)

    def ingest_existing(self, *, workers: int = 1, progress: Progress = silent) -> EurLexRunSummary:
        present = sorted(self.acervo.eu_records())
        progress(f"{len(present)} ato(s) da UE no acervo a atualizar")
        return self.ingest_many(present, workers=workers, progress=progress)
