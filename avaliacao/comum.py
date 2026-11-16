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
# Na raiz, ou na pasta principal quando se corre numa worktree (como `rag.fontes.export_sqlite`).
EXPORT = next(
    (p / "exports" / "leis-portugal.sqlite" for p in (RAIZ, *RAIZ.parents) if (p / "exports" / "leis-portugal.sqlite").exists()),
    RAIZ / "exports" / "leis-portugal.sqlite",
)

_ARTIGO = re.compile(r"^#{6} Artigo(?: |(?=\d))(.+?)(?: — (.*))?$")
# O mesmo leitor de números que o `domain/articles.py`, mas com o número na forma das perguntas («1.º»,
# «78.º-A»), porque a pesquisa procura o artigo pelo número exato.
# Um inteiro escreve-se de muitas maneiras: «1.º», «1º», «1°.», «1.», «1», «1o», «1o.» e «1g.» (atos antigos
# do EUR-Lex), «3. º», «34 .º». A letra de um aditado vem junta («12.ºA»), separada («78.º A», «292.º ‐A»,
# com o hífen U+2010 do EUR-Lex, «10.º - A», «230.º-AAA») ou com travessão («3.º–EA»). A pontuação no fim
# («3.º:», «3.º.», «18.º...») não conta.
_INTEIRO = re.compile(r"^(\d+)\s?(?:\.?\s?[º°]|\.?o|g\.?)?\.?(?:(?:\s?[-‐‑]\s?|–)([A-Z]{1,3})|\s?([A-Z]{1,2}))?$")
# Os compostos dos regulamentos («A-1/2.º», «C - 1/4.º», «A/1 - 5.º», «D-11/2.º-A», «III/1.º») e dos acordos
# da UE («2.1», «J.1») ficam como estão, sem os espaços.
_COMPOSTO = re.compile(r"^(?:[A-Z]{1,3}|\d+)(?:[-/.](?:[A-Z]{1,3}|\d+))+(?:\.?º)?(?:-[A-Z]{1,2})?$")


def numero_artigo(bruto: str) -> str | None:
    """O número de um título de artigo na forma das perguntas («1.º», «78.º-A»), ou None se não é um número."""
    bruto = bruto.strip()
    if re.search(r"\s(?:\.\.|…)", bruto):
        return None  # «Artigo 42.º ...»: o artigo que um ato de alteração não muda.
    bruto = bruto.rstrip("-:;.…").strip()
    inteiro = _INTEIRO.match(bruto)
    if inteiro:
        letra = inteiro.group(2) or inteiro.group(3)
        return f"{inteiro.group(1)}.º" + (f"-{letra}" if letra else "")
    composto = re.sub(r"\s+", "", re.sub(r"[‐‑–]", "-", bruto))
    if _COMPOSTO.match(composto):
        return composto
    if re.search(r"\s", bruto):
        return None
    # O resto («único», «IV», «12.ª»…) como vem, se for uma palavra só.
    return bruto.replace("‐", "-").replace("‑", "-").rstrip(".") or None


def _cabecalho(linha: str) -> tuple[str, str] | None:
    """(número, epígrafe) de um título `###### Artigo …`, ou None se não é um artigo.

    Ao contrário do `articles.py`, não lê a epígrafe depois de um hífen («Artigo 87.º - Ensaios.»): nos decretos
    antigos que a têm, os outros artigos estão em texto corrido antes do título, e o índice perdia-os.
    """
    cabecalho = _ARTIGO.match(linha)
    numero = numero_artigo(cabecalho.group(1)) if cabecalho else None
    return (numero, (cabecalho.group(2) or "").strip()) if numero else None


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
        cabecalho = _cabecalho(linha)
        if cabecalho:
            fechar()
            atual, linhas = Artigo(parte, *cabecalho, ""), []
            continue
        if atual is None:
            continue
        if _NOTA.match(linha):
            atual.notas.append(linha[2:].strip())
            continue
        linhas.append(_LIGACAO.sub(r"\1", linha))
    fechar()
    return resultado


_INTERVALO = re.compile(r"\bartigos?\s+(\d+)\.º\s+a\s+(\d+)\.º", re.I)


def menciona_artigo(texto: str, numero: str) -> bool:
    """Se um texto fala no artigo com este número: "artigo 7.º", "art. 7.º", "artigos 5.º e 7.º",
    "artigos 5.º a 9.º"; não "artigo 17.º" nem "artigo 7.º-A"."""
    base = re.escape(numero.replace(".º", "")).replace("\\-", "-")
    if re.search(rf"\bart(?:igos?|\.|s\.)\s*(?:\d+\.º(?:-[A-Z])?\s*(?:,|e)\s*)*{base}\.?\s*º(?!-[A-Z])", texto, re.I):
        return True
    inteiro = re.match(r"\d+", numero)
    return inteiro is not None and "-" not in numero and any(
        int(inicio) <= int(inteiro.group()) <= int(fim) for inicio, fim in _INTERVALO.findall(texto)
    )


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
