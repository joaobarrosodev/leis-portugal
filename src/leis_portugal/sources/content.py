"""O que uma fonte devolve: o registo normalizado, o texto e os bytes oficiais."""

from __future__ import annotations

from dataclasses import dataclass, field

from leis_portugal.domain.record import LegalRecord


@dataclass(frozen=True)
class SourceContent:
    """Conteúdo oficial obtido de uma fonte remota."""

    url: str
    content: bytes
    media_type: str
    sha256: str


@dataclass
class SourceDocument:
    """Um documento recolhido e já convertido para o modelo do acervo."""

    record: LegalRecord
    body: str
    content: SourceContent | None = None
    warnings: list[str] = field(default_factory=list)
