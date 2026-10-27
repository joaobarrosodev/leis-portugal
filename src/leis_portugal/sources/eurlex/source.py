"""Recolha de um ato da UE: pedidos ao CELLAR + conversão para o modelo do acervo."""

from __future__ import annotations

from datetime import date

from leis_portugal.domain.identifiers import normalize_celex
from leis_portugal.errors import FetchError, MetadataError
from leis_portugal.sources.content import SourceDocument
from leis_portugal.sources.eurlex import mapper
from leis_portugal.sources.eurlex.client import CellarClient


class EurLexSource:
    def __init__(self, client: CellarClient | None = None) -> None:
        self.client = client or CellarClient()
        self.mapper = mapper.EurLexMapper()

    def discover(self, start: date, end: date, *, types: str = "RLD") -> list[str]:
        return [celex for celex, _published in self.client.discover(start, end, types=types)]

    def collect(self, celex: str, *, language: str = "por", consolidated: bool = True, today: date | None = None) -> SourceDocument:
        """Um ato pelo CELEX. Com `consolidated`, usa o texto consolidado mais recente
        quando existe (como nos diplomas portugueses consolidados pelo DRE)."""
        normalized = normalize_celex(celex)
        language = language.lower()
        expression = self.client.expression(normalized, language=language)
        work = self.client.work(normalized)
        work_uri = work["work"][0]
        relations = mapper.relationships(self.client.relations(work_uri))
        subjects = self.client.eurovoc(work_uri)
        warnings: list[str] = []

        content = None
        consolidated_celex = (
            mapper.latest_consolidation(self.client.consolidations(work_uri), normalized, today=today) if consolidated else None
        )
        if consolidated_celex:
            try:
                content = self.client.fetch_text(self.client.expression(consolidated_celex, language=language))
            except (FetchError, MetadataError) as exc:
                warnings.append(f"Versão consolidada {consolidated_celex} indisponível ({exc}); usado o texto do JO.")
                consolidated_celex = None
        if content is None:
            try:
                content = self.client.fetch_text(expression)
            except (FetchError, MetadataError) as exc:
                if not expression.pdf_url:
                    raise
                # Só existe o PDF (ou uma digitalização): regista-se o ato com os metadados
                # e a ligação ao PDF oficial, como nos diplomas portugueses digitalizados.
                content = self.client.fetch_pdf(expression.pdf_url)
                warnings.append(f"Sem texto eletrónico no CELLAR ({exc}); o registo liga apenas ao PDF oficial.")

        return self.mapper.document(
            normalized,
            language=language,
            expression=expression,
            work=work,
            relations=relations,
            subjects=subjects,
            content=content,
            consolidated_celex=consolidated_celex,
            warnings=warnings,
        )
