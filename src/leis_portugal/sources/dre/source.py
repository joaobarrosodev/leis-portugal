"""Recolha de um diploma do DRE: pedidos + conversão para o modelo do acervo."""

from __future__ import annotations

from typing import Any

from leis_portugal.domain.document_types import DocumentTypeRegistry
from leis_portugal.sources.content import SourceDocument
from leis_portugal.sources.dre.client import ASSOCIATION_CORRECTIONS, ASSOCIATION_MODIFICATIONS, DreClient
from leis_portugal.sources.dre.mapper import AZORES_CATALOGUE, DreMapper


class DreSource:
    def __init__(self, types: DocumentTypeRegistry, client: DreClient | None = None) -> None:
        self.client = client or DreClient()
        self.mapper = DreMapper(types)

    def documents_by_date(self, iso_date: str) -> list[dict[str, Any]]:
        return self.client.documents_by_date(iso_date)

    def collect(self, ref: str, *, with_relations: bool = True, with_subjects: bool = True) -> SourceDocument:
        """Um diploma pelo caminho do DRE (`/dr/detalhe/<tipo>/<chave>`)."""
        detail = self.client.published_detail(ref)
        canonical = (detail.get("LinkSitemap") or ref).strip()
        associations = (
            {key: self.client.associations(canonical, key) for key in (ASSOCIATION_MODIFICATIONS, ASSOCIATION_CORRECTIONS)}
            if with_relations and (detail.get("TipoConteudo") or "") != AZORES_CATALOGUE
            else {}
        )
        subjects = self.client.descriptors(canonical) if with_subjects and (detail.get("TipoConteudo") or "") != AZORES_CATALOGUE else []
        return self.mapper.published(detail, ref=ref, associations=associations, subjects=subjects)
