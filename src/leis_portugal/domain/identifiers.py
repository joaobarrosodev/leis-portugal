"""Identificadores jurídicos (CELEX, ids do acervo), datas e slugs."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


CELEX_PATTERN = re.compile(
    # O tipo tem uma letra na legislação (R, L, D) e duas na jurisprudência (CJ, TJ, CO...).
    r"^(?P<sector>[0-9])(?P<year>[0-9]{4})(?P<type>[A-Z]{1,2})(?P<number>[0-9]{1,4})(?P<suffix>[A-Z0-9()/-]*)?$"
)


@dataclass(frozen=True)
class CelexParts:
    sector: str
    year: int
    document_type_code: str
    number: int
    suffix: str


def normalize_celex(value: str) -> str:
    """Normaliza um CELEX para a forma canónica usada pelo EUR-Lex."""
    if not isinstance(value, str):
        raise ValueError("O identificador CELEX tem de ser uma cadeia de texto.")
    normalized = value.strip().upper()
    if normalized.startswith("CELEX:"):
        normalized = normalized.removeprefix("CELEX:").strip()
    normalized = re.sub(r"\s+", "", normalized)
    if not CELEX_PATTERN.fullmatch(normalized):
        raise ValueError(f"Identificador CELEX inválido: {value!r}")
    return normalized


def parse_celex(value: str) -> CelexParts:
    """Extrai componentes estruturais de um identificador CELEX válido."""
    normalized = normalize_celex(value)
    match = CELEX_PATTERN.fullmatch(normalized)
    assert match is not None
    return CelexParts(
        sector=match.group("sector"),
        year=int(match.group("year")),
        document_type_code=match.group("type"),
        number=int(match.group("number")),
        suffix=match.group("suffix") or "",
    )


def slugify(value: str, *, max_length: int = 96) -> str:
    """Cria um slug ASCII estável para nomes de ficheiros."""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")
    if not slug:
        raise ValueError("Não foi possível criar um slug a partir do valor fornecido.")
    return slug


# Sentinela usada pelo DRE para "sem data".
NO_DATE = "1900-01-01"


def pt_record_id(dre_id: str | int) -> str:
    """Identificador estável de um diploma do DRE, independente da versão."""
    return f"pt:dre:{int(str(dre_id))}:por"


def eu_record_id(celex: str, language: str = "por") -> str:
    """Identificador estável de um ato da UE, independente da versão."""
    return f"eu:celex:{normalize_celex(celex)}:{language.lower()}"


def clean_date(value: str | None) -> str | None:
    """Devolve AAAA-MM-DD, ou None para vazios e para a sentinela 1900-01-01."""
    text = (value or "").strip()[:10]
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text) or text == NO_DATE:
        return None
    return text
