"""Recolha de diplomas da 1.ª Série do Diário da República."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta

from leis_portugal.errors import LeisPortugalError, SkipDocument
from leis_portugal.infrastructure.repository import Acervo, WriteResult
from leis_portugal.services.common import PORTUGUESE_POLICY, Progress, silent
from leis_portugal.sources.dre.source import DreSource


@dataclass
class DreRunSummary:
    documents: list[WriteResult] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failures: list[dict[str, str]] = field(default_factory=list)


class DreIngestion:
    def __init__(self, acervo: Acervo, source: DreSource | None = None, *, with_relations: bool = True, with_subjects: bool = True) -> None:
        self.acervo = acervo
        self.source = source or DreSource(acervo.types)
        self.with_relations = with_relations
        self.with_subjects = with_subjects

    def ingest(self, ref: str) -> WriteResult:
        document = self.source.collect(ref, with_relations=self.with_relations, with_subjects=self.with_subjects)
        return self.acervo.save(document.record, document.body, policy=PORTUGUESE_POLICY)

    def ingest_dates(self, start: date, end: date, *, progress: Progress = silent) -> DreRunSummary:
        """Todos os diplomas publicados entre duas datas (inclusive).

        Uma mudança no DRE ao listar um dia interrompe a recolha (`DreApiError`): não
        se grava um dia vazio por engano."""
        summary = DreRunSummary()
        day = start
        while day <= end:
            listed = self.source.documents_by_date(day.isoformat())
            progress(f"{day.isoformat()}: {len(listed)} documento(s)")
            for item in listed:
                ref = (item.get("LinkSitemap") or "").strip()
                if not ref:
                    summary.failures.append({"ref": json.dumps(item, ensure_ascii=False)[:200], "error": "Sem LinkSitemap"})
                    continue
                try:
                    summary.documents.append(self.ingest(ref))
                except SkipDocument as exc:
                    summary.skipped.append(str(exc))
                except LeisPortugalError as exc:
                    summary.failures.append({"ref": ref, "error": str(exc)})
            day += timedelta(days=1)
        return summary
