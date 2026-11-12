"""Decisões fora da legislação: CNPD e acórdãos do Tribunal Constitucional."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from conftest import record_dict
from leis_portugal.errors import MetadataError, NoSourceText
from leis_portugal.infrastructure.markdown import render_markdown
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.decisions import CnpdIngestion, TcIngestion, dre_judgments
from leis_portugal.sources import cnpd, pdftext, tc
from leis_portugal.sources.content import SourceContent
from leis_portugal.sources.decisions import reflow, signature_date


CNPD_PAGE = """
<div class="search-result"><span class="search-count">{total}</span> registos encontrados</div>
{cards}
"""
CNPD_CARD = """
<div class="c-card c-card-s"><a href="/umbraco/surface/cnpdDecision/download/{id}" target="_blank">
<div class="c-card-header-medium">Parecer {number}/2025</div>
<div class="c-card-header">Assembleia da República - Comissão de Assuntos Constitucionais</div>
<div class="c-card-text">{subject}</div></a></div>
"""

TC_LISTING = """
<table class="ilistashtmlminimal_in">
<tr class="acordaostrtitle"><th>Acórdão</th><th>Processo</th></tr>
<tr><td class="tdright tdunderline"><a href="20240401.html">401/24</a></td>
<td class="tdright processo">1146/22</td><td class="tdcenter seccao">2ª Secção</td>
<td class="tdcenter especie">Recurso</td><td class="tdcenter data">23.05.2024</td>
<td class="tdleft relator">Cons. Dora Lucas Neto</td></tr>
<tr><td class="tdright tdunderline"><a href="20240402.html">402/24</a></td>
<td class="tdright processo">394/23</td><td class="tdcenter seccao">Conf.</td>
<td class="tdcenter especie">Reclamação</td><td class="tdcenter data">31.02.2024</td>
<td class="tdleft relator"></td></tr>
</table>
"""
TC_PAGE = """<html><body><div>Menu do site</div>
<div class="WordSection1">
<p class="MsoNormal"><b>ACÓRDÃO Nº <span>401/2024</span></b></p>
<p class="MsoNormal">Acordam, em conferência, na 2.ª Sec<span>ção</span>
do Tribunal Constitucional:</p>
<table><tr><td><p>Quadro</p></td></tr></table>
</div><div>© Tribunal Constitucional</div></body></html>"""


class FakeResponse:
    def __init__(self, content: bytes, headers: dict[str, str] | None = None) -> None:
        self.content = content
        self.headers = headers or {}


class FakeHttp:
    def __init__(self, pages: dict[str, bytes]) -> None:
        self.pages = pages
        self.calls: list[str] = []

    def get(self, url: str, params: dict[str, str] | None = None, **_kwargs) -> FakeResponse:
        key = url + ("?" + "&".join(f"{k}={v}" for k, v in sorted(params.items())) if params else "")
        self.calls.append(key)
        if key not in self.pages:
            from leis_portugal.errors import FetchError

            raise FetchError(f"HTTP 404 para {key}")
        return FakeResponse(self.pages[key], {"Content-Type": "application/pdf"})


def _cards(*items: tuple[str, str], subject: str = "Projeto de Lei n.º 1/XVII") -> str:
    return "".join(CNPD_CARD.format(id=item_id, number=number, subject=subject) for item_id, number in items)


# ---------------------------------------------------------------------------- comum


def test_signature_date_reads_the_last_written_date_of_the_year():
    text = "Lei de 8 de agosto de 2019 (...)\nLisboa, 12 de março de 2025\nA Presidente"
    assert signature_date(text, year=2025) == "2025-03-12"
    assert signature_date("sem datas", year=2025) is None


def test_reflow_joins_lines_broken_mid_sentence_and_keeps_hyphens():
    text = "A Requerente pretende com este\ntratamento a gestão.\nII. DA NOTIFICAÇÃO\nnos termos do decreto-\nlei n.º 1/2000."
    assert reflow(text) == (
        "A Requerente pretende com este tratamento a gestão.\nII. DA NOTIFICAÇÃO nos termos do decreto-lei n.º 1/2000."
    )


def test_pdf_text_reads_the_page_counts_of_the_pdfkit_tool(monkeypatch):
    monkeypatch.setattr(pdftext, "_with_pypdf", lambda _content: None)
    monkeypatch.setattr(pdftext, "_with_pdfkit", lambda _content: "%%PAGINAS 3 1 1\nTexto  da página um com   conteúdo suficiente para contar.\n\f\n")
    extracted = pdftext.extract(b"%PDF")
    assert extracted == pdftext.PdfText(text="Texto da página um com conteúdo suficiente para contar.", pages=3, ocr_pages=1, empty_pages=1)
    monkeypatch.setattr(pdftext, "_with_pdfkit", lambda _content: "%%PAGINAS 2 0 2\n\n\f\n")
    assert pdftext.extract(b"%PDF") is None


# ------------------------------------------------------------------------------ CNPD


def test_cnpd_listing_parses_cards_and_marks_cut_subjects():
    subject = "x" * 100
    total, items = cnpd.parse_listing(CNPD_PAGE.format(total=1, cards=_cards(("123269", "72"), subject=subject)), cnpd.TYPES["parecer"], 2025)
    assert total == 1
    [item] = items
    assert (item.download_id, item.heading, item.number) == ("123269", "Parecer 72/2025", "72/2025")
    assert item.url == "https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/123269"
    assert cnpd.summary_of(item) == f"Assembleia da República - Comissão de Assuntos Constitucionais — {subject}…"


def test_cnpd_listing_follows_pages_and_checks_the_announced_total():
    page1 = CNPD_PAGE.format(total=3, cards=_cards(("3", "3"), ("2", "2"))).encode()
    page2 = CNPD_PAGE.format(total=3, cards=_cards(("1", "1"))).encode()
    url = cnpd.HISTORY_URL
    http = FakeHttp({f"{url}?type=4&year=2025": page1, f"{url}?pgd=2&type=4&year=2025": page2})
    items = cnpd.CnpdClient(http).listing(cnpd.TYPES["parecer"], 2025)
    assert [item.download_id for item in items] == ["3", "2", "1"]

    short = FakeHttp({f"{url}?type=4&year=2025": page1, f"{url}?pgd=2&type=4&year=2025": page1})
    with pytest.raises(MetadataError, match="anuncia 3"):
        cnpd.CnpdClient(short).listing(cnpd.TYPES["parecer"], 2025)


def _cnpd_item(download_id: str = "123269", number: str = "72") -> cnpd.Listed:
    _total, [item] = cnpd.parse_listing(CNPD_PAGE.format(total=1, cards=_cards((download_id, number))), cnpd.TYPES["parecer"], 2025)
    return item


def test_cnpd_document_with_text_is_valid_and_lives_outside_the_legislation(repo_root: Path, monkeypatch):
    monkeypatch.setattr(
        cnpd, "extract",
        lambda _content: pdftext.PdfText(text="PARECER N.º 72/2025\nA CNPD emite\nparecer.\nLisboa, 3 de junho de 2025", pages=2),
    )
    document = cnpd.to_document(_cnpd_item(), SourceContent(url="u", content=b"%PDF-1.7", media_type="application/pdf", sha256="a" * 64))
    record = document.record
    assert (record.id, record.title, record.official_number, record.official_date) == (
        "pt:cnpd:123269", "Parecer da CNPD n.º 72/2025", "72/2025", "2025-06-03",
    )
    assert record.reuse.status == "permitted_with_conditions"
    assert "A CNPD emite parecer." in document.body
    acervo = Acervo(repo_root)
    result = acervo.save(record, document.body, target=acervo.resolve_target(record))
    assert acervo.relative(result.path) == "data/entidades/cnpd/pareceres/2025/parecer-72-2025.md"
    assert acervo.paths() == []  # coleção separada: fora das pastas da legislação


def test_cnpd_scanned_pdf_keeps_metadata_and_says_the_text_is_missing(monkeypatch):
    monkeypatch.setattr(cnpd, "extract", lambda _content: None)
    document = cnpd.to_document(_cnpd_item(), SourceContent(url="u", content=b"%PDF-1.7", media_type="application/pdf", sha256="a" * 64))
    assert any(note.startswith("Fonte sem texto:") for note in document.record.notes)
    assert document.warnings == ["Sem texto extraído do PDF."]
    assert "https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/123269" in document.body


def test_cnpd_partially_scanned_pdf_is_flagged_incomplete(monkeypatch):
    monkeypatch.setattr(cnpd, "extract", lambda _content: pdftext.PdfText(text="Texto da primeira página.", pages=3, empty_pages=2))
    document = cnpd.to_document(_cnpd_item(), SourceContent(url="u", content=b"%PDF", media_type="application/pdf", sha256="a" * 64))
    assert "Texto incompleto: 2 de 3 página(s) do PDF sem texto (digitalização sem OCR)." in document.record.notes


class FakeCnpdClient:
    def __init__(self, items: list[cnpd.Listed]) -> None:
        self.items = items
        self.downloads: list[str] = []

    def listing(self, decision_type, year):
        return [item for item in self.items if item.decision_type == decision_type and item.year == year]

    def download(self, item):
        self.downloads.append(item.download_id)
        return SourceContent(url=item.url, content=b"%PDF", media_type="application/pdf", sha256="b" * 64)


def test_cnpd_ingestion_resumes_without_downloading_what_is_saved(repo_root: Path, monkeypatch):
    monkeypatch.setattr(cnpd, "extract", lambda _content: pdftext.PdfText(text="Texto do parecer com conteúdo suficiente."))
    client = FakeCnpdClient([_cnpd_item("1", "1"), _cnpd_item("2", "2")])
    acervo = Acervo(repo_root)
    first = CnpdIngestion(acervo, client_factory=lambda: client).ingest(types=["parecer"], years=[2025], limit=1)
    assert (len(first.results), client.downloads) == (1, ["1"])
    second = CnpdIngestion(Acervo(repo_root), client_factory=lambda: client).ingest(types=["parecer"], years=[2025])
    assert (second.skipped, len(second.results), client.downloads) == (1, 1, ["1", "2"])


# ------------------------------------------------------------- Tribunal Constitucional


def test_tc_listing_reads_metadata_and_tolerates_bad_dates():
    first, second = tc.parse_listing(TC_LISTING, 2024)
    assert (first.official_number, first.process, first.formation, first.kind, first.decided, first.rapporteur) == (
        "401/2024", "1146/22", "2ª Secção", "Recurso", "2024-05-23", "Cons. Dora Lucas Neto",
    )
    assert first.url == "https://www.tribunalconstitucional.pt/tc/acordaos/20240401.html"
    assert (second.decided, second.rapporteur) == (None, None)
    assert tc.block_url(2024, 401) == "https://www.tribunalconstitucional.pt/tc/acordaos/20240401-0500.html"


def test_tc_judgment_text_comes_only_from_the_word_sections():
    text = tc.judgment_markdown(TC_PAGE)
    assert text == "ACÓRDÃO Nº 401/2024\n\nAcordam, em conferência, na 2.ª Secção do Tribunal Constitucional:\n\nQuadro"
    with pytest.raises(NoSourceText):
        tc.judgment_markdown("<html><body><p>Página não encontrada</p></body></html>")


def test_tc_judgment_text_from_older_pages_with_section_divs():
    # Até 2012 as páginas têm `div.Section1`, não `div.WordSection1`.
    page = (
        '<html><body><div class="menu"><p>Menu</p></div><div id="acimport"><div class="Section1">'
        "<p>ACÓRDÃO N.º 2/86</p><p>Acordam no Tribunal Constitucional:</p></div></div></body></html>"
    )
    assert tc.judgment_markdown(page) == "ACÓRDÃO N.º 2/86\n\nAcordam no Tribunal Constitucional:"
    # Algumas trazem o documento inteiro dentro de #acimport, sem secções.
    page = page.replace('<div class="Section1">', "<div>")
    assert tc.judgment_markdown(page) == "ACÓRDÃO N.º 2/86\n\nAcordam no Tribunal Constitucional:"


def test_tc_decode_falls_back_to_windows_1252():
    assert tc.decode("Acórdão".encode("cp1252")) == "Acórdão"
    assert tc.decode("Acórdão".encode()) == "Acórdão"


def test_tc_listing_stops_at_the_first_missing_block():
    http = FakeHttp({tc.block_url(2024, 1): TC_LISTING.encode()})
    items = tc.TcClient(http).listing(2024)
    assert [item.number for item in items] == [401, 402]
    assert http.calls == [tc.block_url(2024, 1), tc.block_url(2024, 101)]


class FakeTcClient:
    def __init__(self) -> None:
        self.pages: list[str] = []

    def listing(self, year):
        return tc.parse_listing(TC_LISTING, year)[:1]

    def page(self, item):
        self.pages.append(item.url)
        return SourceContent(url=item.url, content=TC_PAGE.encode(), media_type="text/html", sha256="c" * 64)


def test_tc_ingestion_links_the_judgment_published_in_the_dr(repo_root: Path):
    dre_path = repo_root / "data" / "portugal" / "acordaos-tribunal-constitucional" / "2024" / "acordao-tribunal-constitucional-401-2024.md"
    dre_path.parent.mkdir(parents=True)
    dre_path.write_text(render_markdown(record_dict("pt:dre:999:por", document_type="acordao-tribunal-constitucional"), "Texto"), encoding="utf-8")
    acervo = Acervo(repo_root)
    assert dre_judgments(acervo) == {"401/2024": ("pt:dre:999:por", "999")}

    client = FakeTcClient()
    summary = TcIngestion(acervo, client_factory=lambda: client).ingest(years=[2024])
    [result] = summary.results
    assert acervo.relative(result.path) == "data/jurisprudencia/tribunal-constitucional/2024/acordao-tc-401-2024.md"
    metadata = yaml.safe_load(result.path.read_text(encoding="utf-8").split("---\n")[1])
    assert metadata["id"] == "pt:tc:acordao:2024:401"
    assert metadata["official_date"] == "2024-05-23"
    assert metadata["identifiers"]["dre"] == "999"
    assert metadata["relationships"] == [
        {"type": "published_in", "target": "pt:dre:999:por", "label": "Publicado no Diário da República", "source": None}
    ]
    assert metadata["reuse"]["status"] == "restricted"
    assert "Processo: 1146/22" in metadata["notes"]

    again = TcIngestion(Acervo(repo_root), client_factory=lambda: client).ingest(years=[2024])
    assert (again.skipped, len(client.pages)) == (1, 1)


def test_cnpd_without_text_reprocesses_only_the_records_without_text(repo_root: Path, monkeypatch):
    from leis_portugal.services.decisions import ids_without_text

    client = FakeCnpdClient([_cnpd_item("1", "1"), _cnpd_item("2", "2")])
    texts = {"1": None, "2": pdftext.PdfText(text="Texto do parecer com conteúdo suficiente.")}
    monkeypatch.setattr(cnpd, "extract", lambda _content: texts[client.downloads[-1]])
    acervo = Acervo(repo_root)
    CnpdIngestion(acervo, client_factory=lambda: client).ingest(types=["parecer"], years=[2025])
    directory = repo_root / "data" / "entidades" / "cnpd"
    assert ids_without_text(directory) == {"pt:cnpd:1"}

    texts["1"] = pdftext.PdfText(text="Texto obtido por OCR com conteúdo suficiente.", pages=1, ocr_pages=1)
    summary = CnpdIngestion(Acervo(repo_root), client_factory=lambda: client, only=ids_without_text(directory)).ingest(
        types=["parecer"], years=[2025]
    )
    assert (len(summary.results), client.downloads) == (1, ["1", "2", "1"])
    assert ids_without_text(directory) == set()
    saved = (directory / "pareceres" / "2025" / "parecer-1-2025.md").read_text(encoding="utf-8")
    assert "Texto obtido por OCR em 1 de 1 página(s)" in saved


def _tc_item(decided: str | None, *, number: int = 151, year: int = 2025) -> tc.Listed:
    return tc.Listed(number, year, f"{year}{number:04d}.html", None, None, None, decided, None)


def test_tc_date_from_listing_when_the_year_matches_the_number():
    # Mesmo que a última linha "Lisboa, ..." seja outra (muitas vezes é a de um documento citado).
    text = "Acordam...\n\nLisboa, 3 de janeiro de 2025 – A – B"
    assert tc.decision_date(_tc_item("2025-02-18"), text) == ("2025-02-18", None)


def test_tc_date_typo_in_the_year_is_fixed_when_the_signature_confirms_day_and_month():
    date, note = tc.decision_date(_tc_item("0205-02-18"), "Acordam...\n\nLisboa, 18 de fevereiro de 2025 – A – B")
    assert date == "2025-02-18"
    assert note.startswith("Data corrigida: o site dá 18.02.0205")
    # Ano cortado na assinatura ("de 199"): o dia e o mês batem, vale o ano do número.
    date, _ = tc.decision_date(_tc_item("1997-02-28", number=187, year=1996), "Lisboa, 28 de Fevereiro de 199 Messias Bento")
    assert date == "1996-02-28"


def test_tc_date_from_the_signature_when_the_listing_is_wrong():
    date, note = tc.decision_date(_tc_item("2004-04-17", number=323, year=1997), "Lisboa, 5 de Fevereiro de 1997 – A")
    assert date == "1997-02-05"
    assert "usada a data da assinatura" in note
    date, _ = tc.decision_date(_tc_item(None, number=123, year=2022), "Lisboa, 3 de fevereiro de 2022")
    assert date == "2022-02-03"


def test_tc_date_kept_when_listing_and_signature_agree_and_dropped_when_nothing_matches():
    assert tc.decision_date(_tc_item("1993-12-20", number=1, year=1994), "Lisboa, 20 de dezembro de 1993") == ("1993-12-20", None)
    date, note = tc.decision_date(_tc_item("1996-05-12", number=355, year=1998), "Lisboa, 12 de Maio de 1996")
    assert date is None
    assert note.startswith("Sem data:")


def test_failure_list_keeps_other_years_and_notes_and_drops_what_was_collected(repo_root: Path):
    import json

    path = repo_root / "reports" / "tc_failures.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    earlier = [
        {"id": "pt:tc:acordao:2007:396", "motivo": "sem_texto_na_fonte", "error": "x", "nota": "erro 401 na página"},
        {"id": "pt:tc:acordao:2024:401", "motivo": "sem_texto_na_fonte", "error": "x", "nota": "já resolvido"},
        {"listagem": "2024", "motivo": "rede", "error": "x"},
    ]
    path.write_text("".join(json.dumps(item) + "\n" for item in earlier), encoding="utf-8")

    # A recolha diária só vê 2024: recolhe o 401 e lista 2024 sem erro.
    TcIngestion(Acervo(repo_root), client_factory=FakeTcClient, failures_path=path).ingest(years=[2024])
    kept = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert kept == [earlier[0]]


def test_failure_list_keeps_the_note_when_the_same_page_fails_again(repo_root: Path):
    import json

    class Broken(FakeTcClient):
        def page(self, item):
            return SourceContent(url=item.url, content=b"<html><p>Erro</p></html>", media_type="text/html", sha256="d" * 64)

    path = repo_root / "reports" / "tc_failures.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"id": "pt:tc:acordao:2024:401", "motivo": "m", "error": "velho", "nota": "erro 401"}) + "\n", encoding="utf-8")
    TcIngestion(Acervo(repo_root), client_factory=Broken, failures_path=path).ingest(years=[2024])
    [entry] = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert entry["nota"] == "erro 401" and entry["error"] != "velho"
