from __future__ import annotations

import hashlib
from datetime import date
from typing import Any

from leis_portugal.domain.identifiers import eu_record_id, normalize_celex, parse_celex
from leis_portugal.infrastructure.markdown import read_markdown_record, render_markdown
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.eurlex import EurLexIngestion
from leis_portugal.services.validation import validate_repository
from leis_portugal.sources.content import SourceContent
from leis_portugal.sources.eurlex.client import CellarClient, Expression
from leis_portugal.sources.eurlex.mapper import citation_title, latest_consolidation, oj_series
from leis_portugal.sources.eurlex.source import EurLexSource


ORIGINAL_XHTML = b"""<html><body><div class="eli-container">
<div class="eli-main-title"><p class="oj-doc-ti">DIRETIVA (UE) 2022/2555 DO PARLAMENTO EUROPEU E DO CONSELHO</p>
<p class="oj-doc-ti">de 14 de dezembro de 2022</p></div>
<p class="oj-normal">Considerando o seguinte:</p>
<p class="oj-ti-art">Artigo 1.<span class="oj-super">o</span></p>
<p class="oj-sti-art">Objeto</p>
<p class="oj-normal">1. A presente diretiva estabelece medidas.</p>
</div></body></html>"""

CONSOLIDATED_XHTML = """<html><body>
<p class="reference">02022L2555 — PT — 01.01.2026 — 001.001</p>
<p class="disclaimer">Este texto constitui um instrumento de documentação e não tem qualquer efeito jurídico.</p>
<table><tr><td><p class="arrow"><a href="x">►B</a></p></td><td><p class="title-doc-first">DIRETIVA (UE) 2022/2555</p></td></tr></table>
<p class="hd-modifiers">Alterado por:</p>
<table><tr><td><p class="hd-toc-1">Jornal Oficial</p></td></tr>
<tr><td><p class="arrow"><a href="http://publications.europa.eu/resource/celex/32025L0001">►M1</a></p></td>
<td><p class="title-fam-member">Diretiva (UE) 2025/1</p></td></tr></table>
<div class="eli-container">
<div class="eli-main-title"><p class="title-doc-first">DIRETIVA (UE) 2022/2555 DO PARLAMENTO EUROPEU E DO CONSELHO</p></div>
<div id="cpt_I"><p class="title-division-1"><span class="italics">CAPÍTULO I</span></p>
<p class="title-division-2"><span class="boldface">Disposições gerais</span></p>
<div class="eli-subdivision" id="art_1">
<p class="title-article-norm">Artigo 1.<span class="superscript">o</span></p>
<div class="eli-title"><p class="stitle-article-norm">Objeto</p></div>
<p class="modref"><a href="x">▼M1</a></p>
<div class="norm"><span class="no-parag">1. </span><div class="norm inline-element">A presente diretiva estabelece medidas:</div>
<div class="grid-container grid-list"><div class="list grid-list-column-1"><span>a) </span></div>
<div class="grid-list-column-2"><p class="norm">Primeira alínea;</p></div></div>
</div></div></div></div></body></html>""".encode()


def _content(url: str, content: bytes, media_type: str = "application/xhtml+xml") -> SourceContent:
    return SourceContent(url=url, content=content, media_type=media_type, sha256=hashlib.sha256(content).hexdigest())


class FakeCellar(CellarClient):
    """Respostas SPARQL e ficheiros gravados, sem rede."""

    def __init__(self, *, consolidated: str | None = "02022L2555-20260101", in_force: str = "1", text: bool = True) -> None:
        super().__init__()
        self.consolidated_celex = consolidated
        self.in_force = in_force
        self.text = text
        self.queries: list[str] = []

    def sparql(self, query: str) -> list[dict[str, Any]]:
        self.queries.append(query)
        if "work_date_creation_legacy ?published ." in query and "SELECT DISTINCT ?celex ?published" in query:
            return [
                {"celex": "32022L2555", "published": "2022-12-27"},
                {"celex": "32022L2555", "published": "2022-12-27"},
                {"celex": "32022R2554", "published": "2022-12-27"},
            ]
        if "expression_belongs_to_work" in query:
            celex = "02022L2555-20260101" if "02022L2555" in query else "32022L2555"
            title = (
                "Diretiva (UE) 2022/2555 do Parlamento Europeu e do Conselho, de 14 de dezembro de 2022, "
                "relativa a medidas destinadas a garantir um elevado nível comum de cibersegurança"
            )
            rows = [{"expr": f"http://cellar/{celex}.0019", "title": title, "mtype": "pdfa2a", "item": f"http://cellar/{celex}/DOC_2"}]
            if self.text:
                rows.append({"expr": f"http://cellar/{celex}.0019", "title": title, "mtype": "xhtml", "item": f"http://cellar/{celex}/DOC_1"})
            return rows
        if "act_consolidated_consolidates_resource_legal" in query:
            found = [{"celex": "01995L0046-20180525"}]
            if self.consolidated_celex:
                found += [{"celex": "02022L2555-20230116"}, {"celex": self.consolidated_celex}, {"celex": "02022L2555-29991231"}]
            return found
        if "work_is_about_concept_eurovoc" in query:
            return [{"label": "cibersegurança"}, {"label": "segurança da informação"}]
        if "?direction" in query:
            return [
                {"direction": "out", "relation": "http://x#resource_legal_repeals_resource_legal", "target": "http://c/1", "celex": "32016L1148", "date": "2016-07-19"},
                {"direction": "out", "relation": "http://x#work_cites_work", "target": "http://c/2", "celex": "32016R0679"},
                {"direction": "in", "relation": "http://x#resource_legal_amends_resource_legal", "target": "http://c/3", "celex": "32025L0001", "date": "2025-01-10"},
                {"direction": "in", "relation": "http://x#resource_legal_corrects_resource_legal", "target": "http://c/4", "celex": "32022L2555R(01)", "date": "2023-02-01"},
            ]
        if "resource_legal_id_celex ?celex ." in query:
            return [
                {"work": "http://c/work", "eli": "http://data.europa.eu/eli/dir/2022/2555/oj", "signature_date": "2022-12-14",
                 "entry_date": "2023-01-16", "end_date": "9999-12-31", "in_force": self.in_force, "type_code": "L",
                 "year": "2022", "number": "2555", "oj_date": "2022-12-27", "oj_id": "oj:JOL_2022_333_R", "oj_number": "333",
                 "author": "http://publications.europa.eu/resource/authority/corporate-body/EP"},
                {"work": "http://c/work", "author": "http://publications.europa.eu/resource/authority/corporate-body/CONSIL"},
            ]
        raise AssertionError(query)

    def fetch_text(self, expression: Expression) -> SourceContent:
        if not expression.text_items:
            from leis_portugal.errors import MetadataError

            raise MetadataError("A expressão não tem manifestação XHTML nem HTML.")
        url = expression.text_items[0]
        return _content(url, CONSOLIDATED_XHTML if "02022L2555" in url else ORIGINAL_XHTML)

    def fetch_pdf(self, url: str) -> SourceContent:
        return _content(url, b"%PDF-1.4", "application/pdf")


def _ingestion(repo_root, **options) -> EurLexIngestion:
    consolidated = options.pop("consolidated", True)
    return EurLexIngestion(Acervo(repo_root), source_factory=lambda: EurLexSource(FakeCellar(**options)), consolidated=consolidated)


def test_discover_deduplicates_and_filters_types():
    client = FakeCellar()
    assert client.discover(date(2022, 12, 27), date(2022, 12, 27), types="L") == [("32022L2555", "2022-12-27"), ("32022R2554", "2022-12-27")]
    assert "[L]" in client.queries[-1]


def test_latest_consolidation_ignores_other_acts_and_future_versions():
    candidates = ["01995L0046-20180525", "02022L2555-20230116", "02022L2555-20260101", "02022L2555-29991231"]
    assert latest_consolidation(candidates, "32022L2555", today=date(2026, 10, 22)) == "02022L2555-20260101"
    assert latest_consolidation(["01995L0046-20180525"], "32022L2555") is None


def test_title_split_and_oj_series():
    title, summary = citation_title("Regulamento (UE) 2016/679 do Parlamento Europeu e do Conselho, de 27 de abril de 2016, relativo à proteção")
    assert title == "Regulamento (UE) 2016/679 do Parlamento Europeu e do Conselho, de 27 de abril de 2016"
    assert summary.endswith("relativo à proteção")
    assert oj_series("oj:JOL_2016_119_R") == "L"
    assert oj_series("oj:L_202602343") == "L"
    assert eu_record_id("32016R0679") == "eu:celex:32016R0679:por"


def test_collect_consolidated_record(repo_root):
    result = _ingestion(repo_root).ingest("32022L2555")
    metadata, body = read_markdown_record(result.path)
    assert result.path == repo_root.resolve() / "data/european_union/directives/2022/diretiva-ue-2022-2555.md"
    assert metadata["id"] == "eu:celex:32022L2555:por"
    assert metadata["title"] == "Diretiva (UE) 2022/2555 do Parlamento Europeu e do Conselho, de 14 de dezembro de 2022"
    assert metadata["version"]["kind"] == "consolidated"
    assert metadata["version"]["consolidation_date"] == "2026-01-01"
    assert metadata["publication"]["reference"] == "JO L 333 de 27.12.2022"
    assert metadata["issuing_authority"] == ["Parlamento Europeu", "Conselho da União Europeia"]
    assert metadata["subjects"] == ["cibersegurança", "segurança da informação"]
    relations = {(item["type"], item["target"]) for item in metadata["relationships"]}
    assert ("repeals", "celex:32016L1148") in relations
    assert ("amended_by", "celex:32025L0001") in relations
    assert ("corrected_by", "celex:32022L2555R(01)") in relations
    assert metadata["article_structure"]["article_count"] == 1
    text = body.lstrip()
    assert text.startswith("# Diretiva (UE) 2022/2555")
    assert "###### Artigo 1.º — Objeto" in text
    assert "1. A presente diretiva estabelece medidas:" in text
    assert "a) Primeira alínea;" in text
    assert "## CAPÍTULO I" in text and "*CAPÍTULO" not in text
    assert "▼M1" not in text and "►B" not in text
    assert "- [►M1](http://publications.europa.eu/resource/celex/32025L0001) — Diretiva (UE) 2025/1" in text
    assert validate_repository(Acervo(repo_root)) == []


def test_repealed_status_and_original_text(repo_root):
    result = _ingestion(repo_root, in_force="0", consolidated=False).ingest("32022L2555")
    metadata, body = read_markdown_record(result.path)
    assert metadata["version"]["kind"] == "original"
    assert metadata["legal_status"] == "not_in_force"
    assert "###### Artigo 1.º — Objeto" in body


def test_old_id_format_is_migrated_and_portuguese_links_kept(repo_root):
    first = _ingestion(repo_root).ingest("32022L2555")
    metadata, body = read_markdown_record(first.path)
    metadata["id"] = "eu:celex:32022L2555:por:original"
    metadata["relationships"].append({"type": "transposed_by", "target": "pt:dre:1:por", "label": None, "source": None})
    first.path.write_text(render_markdown(metadata, body), encoding="utf-8")

    again = _ingestion(repo_root).ingest("32022L2555")
    migrated, _ = read_markdown_record(again.path)
    assert migrated["id"] == "eu:celex:32022L2555:por"
    assert {"type": "transposed_by", "target": "pt:dre:1:por", "label": None, "source": None} in migrated["relationships"]


def test_ingest_dates_runs_in_parallel(repo_root):
    summary = _ingestion(repo_root).ingest_dates(date(2022, 12, 27), date(2022, 12, 27), types="L", workers=2)
    assert len(summary.results) + len(summary.failures) == 2


def test_plain_html_of_old_journal_acts():
    from leis_portugal.sources.eurlex.xhtml import CellarXhtmlMarkdownConverter

    html = """<html><body><div id="TexteOnly"><p><a href="../../../editorial/legal_notice.htm">Avis juridique</a></p>
    <p><txt_te><p>ADOPTARAM A PRESENTE DIRECTIVA:</p><p>CAPÍTULO I</p><p>Disposições gerais</p>
    <p>Artigo 1.o</p><p>Âmbito e objectivos</p><p>1. A presente directiva harmoniza as disposições.</p>
    <p>Artigo 2.o</p><p>2. Texto sem epígrafe.</p></txt_te></p></div></body></html>""".encode()
    result = CellarXhtmlMarkdownConverter().convert(html)
    assert result.article_count == 2
    assert "### CAPÍTULO I — Disposições gerais" in result.markdown
    assert "###### Artigo 1.º — Âmbito e objectivos" in result.markdown
    assert "###### Artigo 2.º\n" in result.markdown
    assert "Avis juridique" not in result.markdown


def test_pdf_only_act_is_recorded_with_link(repo_root):
    result = _ingestion(repo_root, consolidated=None, text=False).ingest("32022L2555")
    metadata, body = read_markdown_record(result.path)
    assert "[Ver documento original](http://cellar/32022L2555/DOC_2)" in body
    assert metadata["integrity"]["source_sha256"] == hashlib.sha256(b"%PDF-1.4").hexdigest()
    assert any("PDF" in warning for warning in metadata["validation"]["warnings"])


def test_authors_have_a_stable_order():
    from leis_portugal.sources.eurlex.mapper import _authors

    base = "http://publications.europa.eu/resource/authority/corporate-body/"
    assert _authors([base + "CONSIL", base + "EP", base + "XYZ"]) == ["Parlamento Europeu", "Conselho da União Europeia", "XYZ"]


def test_case_law_celex_is_accepted():
    assert normalize_celex("62017CJ0496") == "62017CJ0496"
    assert parse_celex("62017CJ0496").document_type_code == "CJ"
    assert parse_celex("32016R0679").document_type_code == "R"
