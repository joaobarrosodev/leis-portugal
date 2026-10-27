from __future__ import annotations

import hashlib
from pathlib import Path

from leis_portugal.cli import main
from leis_portugal.domain.history import render_version, version_at
from leis_portugal.errors import MetadataError
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.eu_versions import apply_eu_history, collect_eu_history, consolidation_dates
from leis_portugal.services.eurlex import EurLexIngestion
from leis_portugal.sources.content import SourceContent
from leis_portugal.sources.eurlex.client import Expression
from leis_portugal.sources.eurlex.source import EurLexSource
from leis_portugal.sources.eurlex.xhtml import consolidation_modifiers
from test_eurlex import FakeCellar


def _consolidated(article_2: str, modifiers: list[tuple[str, str]], stamp: str) -> bytes:
    rows = "".join(
        f'<tr><td><p class="arrow"><a href="http://publications.europa.eu/resource/celex/{celex}">►M{index}</a></p></td>'
        f'<td><p class="title-fam-member">{title}</p></td></tr>'
        for index, (celex, title) in enumerate(modifiers, start=1)
    )
    header = f'<p class="hd-modifiers">Alterado por:</p><table>{rows}</table>' if modifiers else ""
    return f"""<html><body>
<p class="reference">02022L2555 — PT — {stamp}</p>
<p class="disclaimer">Este texto constitui um instrumento de documentação.</p>
{header}
<div class="eli-container"><div class="eli-main-title"><p class="title-doc-first">DIRETIVA (UE) 2022/2555</p></div>
<p class="title-article-norm">Artigo 1.<span class="superscript">o</span></p>
<div class="eli-title"><p class="stitle-article-norm">Objeto</p></div>
<p class="norm">Texto do artigo 1.</p>
<p class="title-article-norm">Artigo 2.<span class="superscript">o</span></p>
<div class="eli-title"><p class="stitle-article-norm">Âmbito</p></div>
<p class="norm">{article_2}</p>
</div></body></html>""".encode()


M1 = ("32024L0001", "Diretiva (UE) 2024/1")
M2 = ("32025R0002", "Regulamento (UE) 2025/2")
TEXTS = {
    "02022L2555-20230116": _consolidated("Âmbito original.", [], "16.1.2023"),
    "02022L2555-20240101": _consolidated("Âmbito alterado.", [M1], "1.1.2024"),
    "02022L2555-20250101": _consolidated("Âmbito alterado.", [M1, M2], "1.1.2025"),
    "02022L2555-29991231": _consolidated("Âmbito futuro.", [M1, M2], "31.12.2999"),
}


class ConsolidatedCellar(FakeCellar):
    """CELLAR simulado com várias versões consolidadas do mesmo ato."""

    def consolidations(self, work_uri: str) -> list[str]:
        return [*TEXTS, "01995L0046-20180525"]

    def expression(self, celex: str, *, language: str = "por") -> Expression:
        if celex.startswith("0") and celex not in TEXTS:
            raise MetadataError("sem expressão")
        return Expression(uri=None, title="Diretiva (UE) 2022/2555 do Parlamento Europeu e do Conselho, de 14 de dezembro de 2022, relativa a x",
                          short_title=None, last_modified=None, text_items=[celex], pdf_url=None)

    def fetch_text(self, expression: Expression) -> SourceContent:
        celex = expression.text_items[0]
        from test_eurlex import ORIGINAL_XHTML

        content = TEXTS.get(celex, ORIGINAL_XHTML)
        return SourceContent(url=celex, content=content, media_type="application/xhtml+xml", sha256=hashlib.sha256(content).hexdigest())


def test_consolidation_dates_keep_only_own_versions():
    assert consolidation_dates(["01995L0046-20180525", "02022L2555-20240101", "02022L2555-20230116"], "32022L2555") == [
        ("2023-01-16", "02022L2555-20230116"),
        ("2024-01-01", "02022L2555-20240101"),
    ]


def test_modifiers_are_read_from_the_consolidation_header():
    assert consolidation_modifiers(TEXTS["02022L2555-20250101"]) == [M1, M2]
    assert consolidation_modifiers(TEXTS["02022L2555-20230116"]) == []


def test_history_versions_acts_and_changes():
    result = collect_eu_history("32022L2555", ConsolidatedCellar(), publication_date="2022-12-27", today="2026-10-22")
    history = result.history
    assert [(version["date"], version["future"]) for version in history["versions"]] == [
        ("2022-12-27", False), ("2023-01-16", False), ("2024-01-01", False), ("2999-12-31", True),
    ]
    by_date = {version["date"]: version for version in history["versions"]}
    assert [act["celex"] for act in by_date["2024-01-01"]["acts"]] == ["32024L0001"]
    assert by_date["2024-01-01"]["acts"][0]["id"] == "eu:celex:32024L0001:por"
    # 2025: só entrou um ato novo, sem mudança de texto.
    assert [(act["celex"], act["date"]) for act in by_date["2024-01-01"]["acts_without_text_change"]] == [("32025R0002", "2025-01-01")]
    assert by_date["2024-01-01"]["changes"] == ["Altera Artigo 2.º — Âmbito"]
    assert history["source_lastmod"] == "2999-12-31"
    # O Artigo 1.º não muda entre as 3 consolidações: fica guardado uma vez, mais a
    # redação do texto original do JO (diferente na fixture) — 2 e não 4.
    article_1 = [key for key, fragment in history["fragments"].items() if fragment["fragment_id"] == "Artigo 1.º — Objeto"]
    assert len(article_1) == 2
    text = render_version(history, version_at(history, "2024-06-01"), title="Diretiva (UE) 2022/2555")
    assert "Âmbito alterado." in text and "Este texto constitui" not in text and "►M1" not in text


def test_apply_history_and_refresh_keep_versions(repo_root: Path):
    acervo = Acervo(repo_root)
    ingestion = EurLexIngestion(acervo, source_factory=lambda: EurLexSource(ConsolidatedCellar()))
    path = ingestion.ingest("32022L2555").path
    record, _ = acervo.read(path)
    result = collect_eu_history("32022L2555", ConsolidatedCellar(), publication_date=record.publication_date, today="2026-10-22")
    assert apply_eu_history(result, acervo=acervo, path=path, today="2026-10-22") == "written"
    record, body = acervo.read(path)
    assert record.version.kind == "consolidated"
    assert record.version.consolidation_date == "2024-01-01"
    assert record.version_history.count == 4
    assert "Âmbito alterado." in body
    assert apply_eu_history(result, acervo=acervo, path=path, today="2026-10-22") == "unchanged"

    # Uma recolha normal atualiza metadados mas mantém texto e histórico.
    ingestion.ingest("32022L2555")
    refreshed, refreshed_body = acervo.read(path)
    assert refreshed.version_history == record.version_history
    assert refreshed_body == body


def test_split_history_is_unchanged_on_refresh(repo_root: Path, monkeypatch):
    monkeypatch.setattr("leis_portugal.infrastructure.repository.HISTORY_MAX_BYTES", 1_000)
    monkeypatch.setattr("leis_portugal.infrastructure.repository.FRAGMENT_BLOCK_BYTES", 500)
    acervo = Acervo(repo_root)
    path = EurLexIngestion(acervo, source_factory=lambda: EurLexSource(ConsolidatedCellar())).ingest("32022L2555").path
    record, _ = acervo.read(path)
    result = collect_eu_history("32022L2555", ConsolidatedCellar(), publication_date=record.publication_date, today="2026-10-22")
    assert apply_eu_history(result, acervo=acervo, path=path, today="2026-10-22") == "written"
    assert acervo.history_blocks_path(path).is_dir()
    assert acervo.read_history(path) == result.history
    assert apply_eu_history(result, acervo=acervo, path=path, today="2026-10-22") == "unchanged"


def test_cli_collects_eu_history_and_version_at(repo_root: Path, monkeypatch, capsys):
    acervo = Acervo(repo_root)
    EurLexIngestion(acervo, source_factory=lambda: EurLexSource(ConsolidatedCellar())).ingest("32022L2555")
    monkeypatch.setattr("leis_portugal.services.eu_versions.CellarClient", ConsolidatedCellar)
    import leis_portugal.cli.collect as collect_cli
    from leis_portugal.services import eu_versions

    monkeypatch.setattr(collect_cli, "collect_eu_versions", lambda *args, **kwargs: eu_versions.collect_eu_versions(*args, **{**kwargs, "client_factory": ConsolidatedCellar}))
    assert main(["--root", str(repo_root), "collect", "eurlex-consolidated", "--workers", "1"]) == 0
    assert "Atos: 1; atualizados: 1" in capsys.readouterr().out
    assert main(["--root", str(repo_root), "version-at", "eu:celex:32022L2555:por", "--date", "2023-06-01"]) == 0
    assert "Âmbito original." in capsys.readouterr().out


def test_malformed_modifier_celex_is_kept_without_id():
    from leis_portugal.services.eu_versions import _act_id

    assert _act_id("397L0062") is None
    assert _act_id("32024L0001") == "eu:celex:32024L0001:por"
    assert _act_id("52020PC0001") is None
