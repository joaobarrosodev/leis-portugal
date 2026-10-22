"""Hierarquia de erros do projeto.

Os serviços tratam `LeisPortugalError` como falha de um documento (registada e
contornada); qualquer outra exceção é um erro de programação.
"""

from __future__ import annotations


class LeisPortugalError(RuntimeError):
    """Erro base do projeto."""


class SourceError(LeisPortugalError):
    """Erro de uma fonte documental."""


class FetchError(SourceError):
    """Falha de acesso a uma fonte remota."""


class MetadataError(SourceError):
    """Metadados obrigatórios em falta ou inconsistentes na fonte."""


class SkipDocument(SourceError):
    """Documento listado pela fonte mas fora do âmbito do acervo."""


class StorageError(LeisPortugalError):
    """Problema ao ler ou escrever o acervo (colisão de caminhos, ficheiro inválido)."""


class InvalidRecord(LeisPortugalError):
    """Um registo não cumpre o esquema e não pode ser gravado."""
