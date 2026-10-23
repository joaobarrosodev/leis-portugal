"""Catálogo do Jornal Oficial dos Açores e diplomas sem texto na fonte."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from conftest import record_dict
from leis_portugal.infrastructure.markdown import read_markdown_record, render_markdown
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.dre import NO_TEXT_NOTE, DreIngestion
from leis_portugal.sources.dre.client import DreClient
from leis_portugal.sources.dre.mapper import regional_publication
from leis_portugal.sources.dre.source import DreSource
from test_dre_source import FakeSession, _fixture


AZORES_REF = "/dr/detalhe/declaracao-rectificacao/9-2020-137352194"
SOURCE = "JORNAL OFICIAL DOS AÇORES - 1.ª SÉRIE, Nº 101, de 2020-07-06, Pág. 2755 - 2757"


def _azores(**changes: Any) -> dict[str, Any]:
    detail = {
        "Id": "137352194",
        "Titulo": "Declaração de Rectificação n.º 9/2020 ",
        "Numero": "9/2020",
        "Resumo": "Retifica o Anexo da Portaria n.º 89/2020, de 30 de Junho (calendário venatório da ilha do Pico).",
        "Texto": "Declaração de Retificação n.º 9/2020 de 6 de julho de 2020\n\nNos termos do artigo 5.º...",
        "DataPublicacao": "2020-07-06",
        "DataAssinatura": "2020-07-02",
        "Vigencia": "NAO_VIGENTE",
        "URL_PDF": "https://files.diariodarepublica.pt/bases_especiais/legacor/2020/07/06/137352194.pdf",
        "TipoConteudo": "DiplomaLegacor",
        "LinkSitemap": AZORES_REF,
        "DiplomaLegacor": {"FonteRegional": SOURCE, "EntidadeEmitente_AJ": {"List": ["SECRETÁRIO REGIONAL ADJUNTO DA PRESIDÊNCIA"]}},
    }
    detail.update(changes)
    return detail


class CatalogueClient(DreClient):
    """Detalhes gravados por caminho; o resto vem da FakeSession (DL 202/2026)."""

    def __init__(self, details: dict[str, dict[str, Any]]) -> None:
        super().__init__(FakeSession())
        self.details = details

    def published_detail(self, ref: str) -> dict[str, Any]:
        return self.details[ref] if ref in self.details else super().published_detail(ref)


def _service(acervo: Acervo, details: dict[str, dict[str, Any]]) -> DreIngestion:
    return DreIngestion(acervo, source_factory=lambda: DreSource(acervo.types, CatalogueClient(details)))


def test_regional_publication_reference():
    assert regional_publication(SOURCE) == {
        "territory": "acores", "series": "I", "number": "101", "pages": "2755-2757", "reference": SOURCE,
    }
    assert regional_publication("JORNAL OFICIAL DOS AÇORES - 2.ª SÉRIE, Nº 7, de 1981-03-10, Pág. 43")["series"] == "II"


def test_azores_catalogue_is_a_regional_record(repo_root: Path):
    acervo = Acervo(repo_root)
    summary = _service(acervo, {AZORES_REF: _azores()}).ingest_many([AZORES_REF])
    assert not summary.failures and not summary.skipped
    path = summary.documents[0].path
    assert acervo.relative(path) == "data/regional/acores/declaracoes-retificacao/2020/declaracao-retificacao-9-2020.md"
    metadata, body = read_markdown_record(path)
    assert (metadata["jurisdiction"], metadata["territory"]) == ("regional", "acores")
    assert metadata["publication"]["gazette"] == "Jornal Oficial dos Açores"
    assert (metadata["publication"]["series"], metadata["publication"]["number"], metadata["publication"]["pages"]) == ("I", "101", "2755-2757")
    assert metadata["issuing_authority"] == ["SECRETÁRIO REGIONAL ADJUNTO DA PRESIDÊNCIA"]
    assert metadata["summary"].startswith("Retifica o Anexo da Portaria n.º 89/2020")
    assert metadata["legal_status"] == "not_in_force"
    assert metadata["version"]["label"] == "Texto publicado no Jornal Oficial dos Açores"
    assert "Nos termos do artigo 5.º" in body


def test_without_text_a_new_record_keeps_the_metadata(repo_root: Path):
    acervo = Acervo(repo_root)
    detail = _azores(Texto="", URL_PDF="")
    summary = _service(acervo, {AZORES_REF: detail}).ingest_many([AZORES_REF])
    assert [failure["motivo"] for failure in summary.failures] == ["sem_texto_na_fonte"]
    metadata, body = read_markdown_record(summary.documents[0].path)
    assert metadata["title"] == "Declaração de Rectificação n.º 9/2020"
    assert metadata["notes"][-1].startswith("Fonte sem texto: o DRE não tem texto eletrónico nem PDF deste diploma; o registo tem só os metadados")
    assert "só os metadados" in body
    assert metadata["integrity"]["source_sha256_scope"] == "official_source_content_bytes"


def test_without_text_an_existing_record_keeps_its_text(repo_root: Path):
    path = repo_root / "data" / "regional" / "acores" / "declaracoes-retificacao" / "2020" / "declaracao-retificacao-9-2020.md"
    path.parent.mkdir(parents=True)
    record = record_dict("pt:dre:137352194:por", identifiers={"dre": "137352194", "internal": "pt:dre:137352194:por"})
    path.write_text(render_markdown(record, "# Texto que já existia"), encoding="utf-8")
    acervo = Acervo(repo_root)
    summary = _service(acervo, {AZORES_REF: _azores(Texto="", URL_PDF="")}).ingest_many([AZORES_REF])
    assert summary.documents == [] and len(summary.failures) == 1
    metadata, body = read_markdown_record(path)
    assert body.strip() == "# Texto que já existia"
    assert metadata["notes"][-1].startswith(f"Fonte sem texto: {NO_TEXT_NOTE}")


def test_published_detail_without_text_by_date(repo_root: Path):
    # Também na recolha por datas: um diploma do DR sem texto entra só com os metadados.
    acervo = Acervo(repo_root)
    detail = {**_fixture("detail_decreto_lei.json"), "TextoFormatado": "", "Texto": "", "URL_PDF": ""}
    service = DreIngestion(acervo, DreSource(acervo.types, CatalogueClient({"/dr/detalhe/decreto-lei/202-2026-1183482554": detail})))
    summary = service.ingest_dates(*[__import__("datetime").date(2026, 10, 20)] * 2)
    assert [failure["motivo"] for failure in summary.failures] == ["sem_texto_na_fonte"]
    assert acervo.relative(summary.documents[0].path) == "data/portugal/decretos-leis/2026/decreto-lei-202-2026.md"
