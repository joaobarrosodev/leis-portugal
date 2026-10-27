"""Leitura dos artigos de um registo, partilhada pela amostragem e pela verificação.

Os artigos são os títulos `###### Artigo N.º — Epígrafe` do corpo do registo. A numeração
repete-se entre o diploma e os anexos (o Código do Trabalho, anexo da Lei n.º 7/2009, tem
o seu próprio artigo 3.º), por isso cada artigo fica identificado pela parte onde está:
"" para o diploma, o título do anexo (`## Anexo — …`) para o resto.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
EXPORT = RAIZ / "exports" / "leis-portugal.sqlite"

_ARTIGO = re.compile(r"^#{6} Artigo (\S+)(?: — (.*))?$")
_ANEXO = re.compile(r"^## (Anexo.*)$")
_NOTA = re.compile(r"^> (Alterado|Aditado|Revogado|Retificado|Republicado)", re.I)
_LIGACAO = re.compile(r"<a [^>]*>(.*?)</a>")


@dataclass
class Artigo:
    parte: str
    numero: str
    epigrafe: str
    texto: str
    notas: list[str] = field(default_factory=list)

    @property
    def chave(self) -> str:
        """Identificador do artigo dentro do diploma: `anexo::3.º` ou `3.º`."""
        return f"{self.parte}::{self.numero}" if self.parte else self.numero


def corpo(markdown: str) -> str:
    """O texto do registo sem o cabeçalho YAML."""
    if markdown.startswith("---\n"):
        fim = markdown.find("\n---\n", 4)
        if fim != -1:
            return markdown[fim + 5 :]
    return markdown


def artigos(texto: str) -> list[Artigo]:
    """Os artigos do corpo de um registo, pela ordem em que aparecem."""
    resultado: list[Artigo] = []
    parte = ""
    atual: Artigo | None = None
    linhas: list[str] = []

    def fechar() -> None:
        if atual is not None:
            atual.texto = "\n".join(linhas).strip()
            resultado.append(atual)

    for linha in texto.splitlines():
        anexo = _ANEXO.match(linha)
        if anexo:
            fechar()
            atual, linhas, parte = None, [], anexo.group(1).strip()
            continue
        if linha.startswith("#") and not linha.startswith("######"):
            continue
        cabecalho = _ARTIGO.match(linha)
        if cabecalho:
            fechar()
            atual, linhas = Artigo(parte, cabecalho.group(1), (cabecalho.group(2) or "").strip(), ""), []
            continue
        if atual is None:
            continue
        if _NOTA.match(linha):
            atual.notas.append(linha[2:].strip())
            continue
        linhas.append(_LIGACAO.sub(r"\1", linha))
    fechar()
    return resultado


def normalizar(texto: str) -> str:
    """Espaços colapsados, para comparar excertos com o texto do artigo."""
    return re.sub(r"\s+", " ", texto).strip()


def texto_em(caminho: Path, data: str | None) -> str:
    """Corpo do registo na data pedida (`version-at`), ou o texto atual sem data."""
    if data is None:
        return corpo(caminho.read_text(encoding="utf-8"))
    resultado = subprocess.run(
        [sys.executable, "-c", "from leis_portugal.cli import main; raise SystemExit(main())",
         "version-at", str(caminho), "--date", data],
        capture_output=True, text=True, check=True, cwd=RAIZ,
    )
    return corpo(resultado.stdout)


def artigo(caminho: Path, chave: str, data: str | None = None) -> Artigo | None:
    """Um artigo pela chave (`anexo::3.º` ou `3.º`), no texto atual ou numa data."""
    return next((a for a in artigos(texto_em(caminho, data)) if a.chave == chave), None)
