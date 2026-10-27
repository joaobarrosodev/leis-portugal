"""Hierarquia de erros do projeto.

Os serviços tratam `LeisPortugalError` como falha de um documento (registada e
contornada); qualquer outra exceção é um erro de programação.
"""

from __future__ import annotations

from typing import Any


class LeisPortugalError(RuntimeError):
    """Erro base do projeto."""


class SourceError(LeisPortugalError):
    """Erro de uma fonte documental."""


class FetchError(SourceError):
    """Falha de acesso a uma fonte remota."""


class MetadataError(SourceError):
    """Metadados obrigatórios em falta ou inconsistentes na fonte."""


class NoSourceText(MetadataError):
    """A fonte oficial não tem o texto do documento (nem eletrónico, nem na língua pedida).

    Não é um erro de acesso: voltar a tentar não muda nada até a fonte publicar o texto."""

    def __init__(self, message: str, *, record_id: str | None = None, document: Any = None) -> None:
        super().__init__(message)
        self.record_id = record_id
        # O registo só com os metadados (`SourceDocument`), quando a fonte os tem.
        self.document = document


class SkipDocument(SourceError):
    """Documento listado pela fonte mas fora do âmbito do acervo."""


class StorageError(LeisPortugalError):
    """Problema ao ler ou escrever o acervo (colisão de caminhos, ficheiro inválido)."""


class InvalidRecord(LeisPortugalError):
    """Um registo não cumpre o esquema e não pode ser gravado."""


def failure_reason(exc: BaseException) -> str:
    """Motivo legível de uma falha, para as listas em `reports/`."""
    if isinstance(exc, NoSourceText):
        return "sem_texto_na_fonte"
    if isinstance(exc, FetchError):
        return "erro_de_acesso"
    if isinstance(exc, MetadataError):
        return "metadados_em_falta"
    if isinstance(exc, InvalidRecord):
        return "registo_invalido"
    if isinstance(exc, StorageError):
        return "armazenamento"
    return "resposta_inesperada"
