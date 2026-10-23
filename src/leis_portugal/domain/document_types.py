"""Tipos canónicos de diploma português, regiões autónomas e referências por número.

O vocabulário vem de `config/document_types.yml` e é injetado como dicionário: este
módulo não lê ficheiros.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cached_property
from typing import Any

from leis_portugal.domain.identifiers import slugify


@dataclass(frozen=True)
class DocumentType:
    slug: str
    label: str
    path: str
    known: bool = True


class DocumentTypeRegistry:
    """Normaliza os tipos do DRE (e grafias antigas) para os tipos canónicos do acervo."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._types: dict[str, DocumentType] = {}
        self._aliases: dict[str, str] = {}
        for slug, entry in ((config.get("jurisdictions") or {}).get("portugal") or {}).items():
            self._types[slug] = DocumentType(slug=slug, label=entry["label_pt"], path=entry["path"])
            self._aliases[slug] = slug
            for alias in entry.get("aliases") or []:
                self._aliases[alias] = slug
        self.territories: dict[str, dict[str, Any]] = config.get("territories") or {}
        # Tipos sobretudo da 2.ª Série: contados na cobertura, recolhidos só a pedido.
        self.sitemap_optional = frozenset(self.resolve(slug).slug for slug in config.get("sitemap_optional") or [])

    def order(self, slug: str) -> int:
        """Posição do tipo no vocabulário (a ordem de `document_types.yml`); desconhecidos no fim."""
        return list(self._types).index(slug) if slug in self._types else len(self._types)

    def resolve(self, raw: str | None) -> DocumentType:
        key = slugify(raw or "desconhecido")
        canonical = self._aliases.get(key)
        if canonical:
            return self._types[canonical]
        # Tipo ainda não catalogado: mantém-se o slug original numa pasta própria.
        return DocumentType(slug=key, label=raw or key, path=f"outros/{key}", known=False)

    def territory_for(
        self,
        *,
        document_type: str,
        official_number: str | None,
        issuer: str | None = None,
        hint: str | None = None,
    ) -> str | None:
        """Região autónoma de um diploma regional (Açores/Madeira), se for o caso."""
        if hint in self.territories:
            return hint
        number = (official_number or "").strip().upper()
        for territory, entry in self.territories.items():
            suffix = entry.get("number_suffix")
            if suffix and number.endswith(f"/{suffix}"):
                return territory
        normalized_issuer = slugify(issuer or "x")
        normalized_type = slugify(document_type or "x")
        for territory in self.territories:
            article = "dos" if territory == "acores" else "da"
            if f"regiao-autonoma-{article}-{territory}" in normalized_issuer or normalized_type.endswith(f"-{territory}"):
                return territory
        return None

    @cached_property
    def _citation(self) -> tuple[re.Pattern[str], dict[str, str]]:
        labels: dict[str, str] = {}
        for document_type in self._types.values():
            if "(" in document_type.label:
                continue
            labels[document_type.label.lower()] = document_type.slug
            labels[document_type.label.lower().replace("retificação", "rectificação")] = document_type.slug
        alternatives = "|".join(re.escape(label) for label in sorted(labels, key=len, reverse=True))
        pattern = re.compile(
            rf"\b({alternatives})\s+n\.?\s*[ºo°]\s*([0-9][0-9A-Za-z-]*/[0-9]{{4}}(?:/[AM])?)",
            re.IGNORECASE,
        )
        return pattern, labels

    def textual_reference(self, text: str) -> str | None:
        """Primeiro diploma citado num texto: `pt:numero:decreto-lei:140/2009`.

        Usado quando a fonte descreve a relação só em texto, sem id do diploma."""
        pattern, labels = self._citation
        match = pattern.search(text or "")
        if not match:
            return None
        return f"pt:numero:{labels[match.group(1).lower()]}:{match.group(2).upper()}"
