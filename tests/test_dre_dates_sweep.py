"""Varredura por datas: listagem em paralelo e recolha só do que falta."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from leis_portugal.cli import main
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.dre import DreIngestion
from leis_portugal.sources.dre.client import DreApiError, DreClient
from leis_portugal.sources.dre.source import DreSource
from test_dre_source import FakeSession


class FlakySession(FakeSession):
    """O DRE não lista o dia 2026-10-21; os outros dias listam o DL 202/2026."""

    def call(self, action: str, variables: dict[str, Any]) -> dict[str, Any]:
        if action == "documents_by_date" and variables.get("DataSelecionada") == "2026-10-21":
            raise DreApiError("documents_by_date(2026-10-21) sem DiarioByDiaList")
        return super().call(action, variables)


def _service(acervo: Acervo) -> DreIngestion:
    return DreIngestion(acervo, source_factory=lambda: DreSource(acervo.types, DreClient(FlakySession())), with_subjects=False)


def test_listing_in_parallel_keeps_order_dedupes_and_records_unlisted_days(repo_root: Path):
    refs, failures = _service(Acervo(repo_root)).list_dates(date(2026, 10, 20), date(2026, 10, 22), workers=3)
    assert refs == ["/dr/detalhe/decreto-lei/202-2026-1183482554"]
    assert [(item["ref"], item["motivo"]) for item in failures] == [("dia 2026-10-21", "erro_de_acesso")]


def test_only_missing_skips_what_the_acervo_already_has(repo_root: Path):
    acervo = Acervo(repo_root)
    first = _service(acervo).ingest_dates_parallel(date(2026, 10, 20), date(2026, 10, 20), workers=2, only_missing=True)
    assert [result.action for result in first.documents] == ["written"]

    messages: list[str] = []
    again = _service(Acervo(repo_root)).ingest_dates_parallel(
        date(2026, 10, 20), date(2026, 10, 22), workers=2, only_missing=True, progress=messages.append
    )
    assert again.documents == []
    assert "1 diploma(s) listados; 0 ainda não estão no acervo" in messages


def test_cli_only_missing(repo_root: Path, monkeypatch, capsys):
    monkeypatch.setattr("leis_portugal.cli.collect.DreIngestion", lambda acervo, **options: _service(acervo))
    arguments = ["--root", str(repo_root), "collect", "dre", "--from", "2026-10-20", "--to", "2026-10-20", "--only-missing"]
    assert main(arguments) == 0
    assert "written: data/portugal/decretos-leis/2026/decreto-lei-202-2026.md" in capsys.readouterr().out
    assert main(arguments) == 0
    assert "0 ainda não estão no acervo" in capsys.readouterr().err
