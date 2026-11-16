"""Gralhas na numeração dos títulos de artigo.

O texto do DRE tem às vezes um artigo com o número errado: no Decreto Regulamentar Regional
n.º 2/2005/M, «Artigo 212.º» entre o 20.º e o 22.º. A chave do artigo fica `art-212` e uma pergunta
sobre o art. 21.º não o encontra. Aqui corrige-se o número do título, e a nota guarda o que a fonte
escreveu.

Só se corrige quando a sequência não deixa dúvidas, dentro da mesma parte (o diploma ou um anexo,
como em `articles.py`):
- os dois artigos antes são n-2 e n-1, e os dois depois são n+1 e n+2 (num extremo da parte basta
  um lado, mas tem de haver pelo menos um vizinho confirmado além dos imediatos);
- o número n não existe em mais nenhum artigo da parte;
- o artigo tem epígrafe se e só se os dois vizinhos a têm. Num ato de alteração, o «Artigo 2.º»
  do próprio ato no meio dos artigos citados de outro diploma não tem epígrafe, e eles têm;
- a epígrafe não é a de um artigo de um ato de alteração («Artigo 2.º — Aditamento ao
  Regulamento…», no Regulamento n.º 1135/2024);
- o mesmo título, com o número e a epígrafe, não aparece noutro sítio do registo. Se a fonte o
  repete igual, o número é provavelmente o dela (Edital n.º 969/2011, «Artigo 7.º — Cérceas» duas
  vezes).

Os números repetidos (2.º, 2.º, 4.º) só se corrigem com `repeated=True`. Um número repetido também
pode ser um erro do próprio legislador, e esses casos leem-se um a um.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from leis_portugal.domain.articles import _HEADING, _HEADING_ARTICLE, _is_part_heading


_INTEGER = re.compile(r"^(\d+)(\s?\.?\s?º)$")
_AMENDING = re.compile(r"^\(?\s*(?:Altera[çc][ãõ]o|Altera[çc][õo]es|Aditamentos?|Republica[çc][ãa]o)\b", re.IGNORECASE)


@dataclass(frozen=True)
class NumberFix:
    line: int
    written: int
    fixed: int
    before: int
    after: int
    repeated: bool

    def note(self, source: str = "o DRE") -> str:
        return (
            f"Numeração corrigida: {source} escreve «Artigo {self.written}.º» entre os artigos {self.before}.º "
            f"e {self.after}.º; usado o {self.fixed}.º."
        )


@dataclass
class _Heading:
    line: int
    number: int
    epigraph: str


def _parts(lines: list[str]) -> list[list[_Heading]]:
    """Os títulos de artigo com número inteiro, agrupados por parte."""
    parts: list[list[_Heading]] = [[]]
    for index, line in enumerate(lines):
        heading = _HEADING.match(line)
        if not heading:
            continue
        level, title = len(heading.group(1)), heading.group(2).strip()
        if level == 2 and _is_part_heading(title):
            parts.append([])
            continue
        article = _HEADING_ARTICLE.match(line)
        if not article or article.group("label").lower() not in {"artigo", "art.", "art.º", "artº"}:
            continue
        number = _INTEGER.match(article.group("number").strip())
        if not number:
            continue
        value = int(number.group(1))
        if value == 1 and any(h.number == 1 for h in parts[-1]):
            parts.append([])  # a numeração recomeça sem título: parte implícita
        epigraph = (article.group("heading") or article.group("heading2") or "").strip()
        parts[-1].append(_Heading(index, value, epigraph))
    return [part for part in parts if part]


def review_numbers(markdown: str, *, repeated: bool = False) -> list[tuple[NumberFix, str | None]]:
    """Cada título fora de sequência (n-1, X, n+1) numa parte, com o motivo para não o corrigir
    (`None` quando se corrige)."""
    lines = markdown.split("\n")
    found: list[tuple[NumberFix, str | None]] = []
    parts = _parts(lines)
    titles = [(h.number, h.epigraph) for part in parts for h in part]
    for part in parts:
        numbers = [h.number for h in part]
        for i in range(1, len(part) - 1):
            before, written, after = numbers[i - 1], numbers[i], numbers[i + 1]
            expected = before + 1
            if after != before + 2 or written == expected:
                continue
            is_repeated = written in (before, after)
            fix = NumberFix(part[i].line, written, expected, before, after, is_repeated)
            left = i - 2 < 0 or numbers[i - 2] == before - 1
            right = i + 2 >= len(part) or numbers[i + 2] == after + 1
            neighbours = {bool(part[i - 1].epigraph), bool(part[i + 1].epigraph)}
            if expected in numbers:
                reason = f"o {expected}.º já existe na mesma parte"
            elif not (left and right and (i - 2 >= 0 or i + 2 < len(part))):
                reason = "sem dois vizinhos seguidos de cada lado: artigos citados de outros diplomas ou números trocados"
            elif len(neighbours) == 1 and bool(part[i].epigraph) not in neighbours:
                reason = "epígrafe diferente da dos vizinhos: provavelmente um artigo do ato de alteração"
            elif _AMENDING.match(part[i].epigraph):
                reason = "epígrafe de um artigo de um ato de alteração"
            elif part[i].epigraph and titles.count((written, part[i].epigraph)) > 1:
                reason = "o mesmo título aparece igual noutro sítio do registo"
            elif is_repeated and not repeated:
                reason = "número repetido: ler antes de corrigir"
            else:
                reason = None
            found.append((fix, reason))
    return found


def find_number_fixes(markdown: str, *, repeated: bool = False) -> list[NumberFix]:
    """As gralhas de numeração que se podem corrigir sem dúvida (ver o docstring do módulo)."""
    return [fix for fix, reason in review_numbers(markdown, repeated=repeated) if reason is None]


def fix_article_numbers(markdown: str, *, source: str = "o DRE", repeated: bool = False) -> tuple[str, list[str]]:
    """O Markdown com os títulos corrigidos e uma nota por correção."""
    fixes = find_number_fixes(markdown, repeated=repeated)
    if not fixes:
        return markdown, []
    lines = markdown.split("\n")
    for fix in fixes:
        article = _HEADING_ARTICLE.match(lines[fix.line])
        raw = article.group("number")
        start = article.start("number") + len(raw) - len(raw.lstrip())
        end = article.end("number") - (len(raw) - len(raw.rstrip()))
        suffix = _INTEGER.match(raw.strip()).group(2)
        lines[fix.line] = f"{lines[fix.line][:start]}{fix.fixed}{suffix}{lines[fix.line][end:]}"
    return "\n".join(lines), [fix.note(source) for fix in fixes]
