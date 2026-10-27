"""Artigos de um registo, com um identificador estável por artigo.

O corpo Markdown dos registos tem os artigos de duas formas:

- títulos `###### Artigo N.º — Epígrafe` (texto formatado do DRE e consolidados);
- texto corrido, nos registos antigos e nos que vêm do texto simples do DRE
  (`Artigo 1.º Texto…`, `Art. 2.º - Texto…`, `ARTIGO 1.º` com a epígrafe na linha
  seguinte, `Artigo único.`, `BASE I`).

Quando um registo tem títulos de artigo, só os títulos contam: o texto corrido de um
título pode citar artigos de outros diplomas. Sem artigos, os números do dispositivo
(`1.º …`, `1 - …`, habituais nas portarias e despachos) ficam como unidades `numero`.

A numeração repete-se entre o diploma e os anexos (o Código do Trabalho, anexo da Lei
n.º 7/2009, tem o seu próprio artigo 3.º), por isso cada artigo pertence a uma parte:
o diploma (`""`) ou um anexo. Um anexo começa num título de nível 2 que não seja uma
divisão (`## Anexo — …`, `## ANEXO I`, mas também `## CÓDIGO DO IMPOSTO…`, como no
Decreto-Lei n.º 198/2001) ou, no texto corrido, numa linha `ANEXO`. Quando a numeração
recomeça sem nenhum título, abre-se uma parte implícita (`parte-2`).

O id de um artigo é `<id do registo>#<parte>/<artigo>`, p. ex.
`pt:dre:602073:por#anexo-codigo-do-trabalho/art-3` ou `pt:dre:602073:por#art-14`.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field


ARTICLE_KINDS = {"artigo": "art", "base": "base", "clausula": "clausula", "numero": "n"}

_NUMBER = r"(?:\d+(?:\s?\.?\s?[º°]|\.o\b|\.)?(?:\s?-\s?[A-Z]{1,2}\b)?|[IVXLCDM]+\b(?:-[A-Z]\b)?|[ÚúUu]nic[oa]\b|ÚNIC[OA]\b|UNIC[OA]\b)"
_LABELS = {
    "artigo": "artigo", "art.": "artigo", "artº": "artigo", "art.º": "artigo",
    "base": "base", "cláusula": "clausula", "clausula": "clausula",
}
_LABEL = r"(?P<label>Artigo|ARTIGO|Art\.º|Artº|Art\.|ART\.|Base|BASE|Cláusula|CLÁUSULA|Clausula|CLAUSULA)"
# Título de artigo: o número acaba no fim da linha, num travessão ou num ponto.
_HEADING_ARTICLE = re.compile(rf"^#{{6}}\s+{_LABEL}\s*(?P<number>{_NUMBER})\s*(?:$|[—–]\s*(?P<heading>.*)$|\.\s*$|-\s+(?P<heading2>.*)$)")
_HEADING_POINT = re.compile(r"^#{6}\s+(?P<number>\d+\.?\s?º)\s*$")
_PLAIN_ARTICLE = re.compile(rf"^{_LABEL}\s*(?P<number>{_NUMBER})(?P<rest>.*)$")
# Uma referência, não um artigo: "Artigo 3.º do Decreto-Lei…", "Artigo 167.º, n.º 1)".
_REFERENCE_REST = re.compile(r"^\s*(?:,|:|;|\)|do\b|da\b|dos\b|das\b|e\b|n\.º|n\.os|al[ií]nea|§)")
_PLAIN_POINT = re.compile(r"^(?P<number>\d{1,3})(?:\.\s?º|º|\s*[-–—])\s+\S")
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_DIVISION = re.compile(
    r"^(?:LIVRO|PARTE|T[ÍI]TULO|SUBT[ÍI]TULO|CAP[ÍI]TULO|SUBCAP[ÍI]TULO|SEC[ÇC][ÃA]O|SUBSEC[ÇC][ÃA]O|DIVIS[ÃA]O|SUBDIVIS[ÃA]O)"
    r"\s+(?:[IVXLCDM]+\b|\d+|[ÚU]NIC[OA]|[úu]nic[oa]|PRELIMINAR|[Pp]reliminar)",
    re.IGNORECASE,
)
_ROMAN_DIVISION = re.compile(r"^[IVXLCDM]+\s*[-—–.]\s")
_PLAIN_ANNEX = re.compile(r"^(?:ANEXO|Anexo|APÊNDICE|Apêndice)(?:\s+(?:[IVXLCDM]+|\d+|[A-Z]|ÚNICO|único))?(?:\s*[-—–:(].{0,120})?$")
_REDACTION = re.compile(r"(?:seguinte|nova) reda[cç]?[cç][ãa]o\s*:\s*$|(?:passa|passam) a ser\s*:\s*$")
_NOTE = re.compile(r"^> (Alterado|Aditado|Revogado|Retificado|Republicado)", re.IGNORECASE)
_HTML_LINK = re.compile(r"<a [^>]*>(.*?)</a>")
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
# Fim do dispositivo: assinaturas, promulgação, referenda.
_SIGNATURE = re.compile(
    r"^(?:Visto e aprovado|Vistos? e aprovad|Aprovad[oa]s? em|Promulgad[oa] em|Publique-se|Paços do Governo|Assinad[oa] em|"
    r"Referendad[oa] em|O Presidente da República,|Presidência do Conselho de Ministros, \d|O Primeiro-Ministro,)"
)
# Assinatura de um membro do Governo: "O Ministro da Administração Interna, Rui Carlos Pereira, em 30 de Dezembro de 2008."
_NAME = r"(?:[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\w'.-]*|d[aeo]s?|e)"
_MINISTER_SIGNATURE = re.compile(
    r"^(?:O|A|Pel[oa]) (?:Ministr[oa]|Secretári[oa] de Estado|Primeiro-Ministro|Presidente do Governo Regional)[^,]{0,160}, "
    rf"{_NAME}(?: {_NAME}){{1,8}}(?:, em \d{{1,2}} de \w+ de \d{{4}})?\.?$"
)


@dataclass
class Article:
    """Um artigo (ou base, cláusula, número) de um registo."""

    part: str
    part_slug: str
    kind: str
    number: str
    heading: str
    text: str
    notes: list[str] = field(default_factory=list)
    method: str = "titulo"
    # Número repetido na mesma parte (2, 3…): a chave fica `art-5-2`.
    repeat: int = 0
    # Aberto logo a seguir a "passa a ter a seguinte redacção:" (texto corrido, sem aspas):
    # pode ser a nova redação de um artigo de outro diploma e não um artigo deste.
    quoted: bool = field(default=False, repr=False, compare=False)
    source_line: str = field(default="", repr=False, compare=False)

    @property
    def key(self) -> str:
        """Chave do artigo dentro da parte: `art-3`, `art-10-a`, `art-unico`, `base-iv`, `n-2`."""
        key = f"{ARTICLE_KINDS[self.kind]}-{number_slug(self.number)}"
        return f"{key}-{self.repeat}" if self.repeat else key

    @property
    def anchor(self) -> str:
        """Âncora dentro do registo: `anexo-codigo-do-trabalho/art-3` ou `art-3`."""
        return f"{self.part_slug}/{self.key}" if self.part_slug else self.key

    def id(self, record_id: str) -> str:
        return f"{record_id}#{self.anchor}"


def _signature(line: str) -> bool:
    return bool(_SIGNATURE.match(line) or _MINISTER_SIGNATURE.match(line))


def _ascii(value: str) -> str:
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()


def number_slug(number: str) -> str:
    """`10.º-A` -> `10-a`, `1º` -> `1`, `único` -> `unico`, `IV` -> `iv`."""
    text = _ascii(number)
    text = re.sub(r"(?<=\d)\s*\.?\s*[o°]?(?=$|\s|-)", "", text) if re.match(r"\d", text) else text
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "sem-numero"


_NUMBERED_ANNEX = re.compile(r"^(anexo|apendice|appendix)s?\s+(?:n\.?\s*o\s*)?([ivxlcdm]+|\d+|[a-z]|unico)(?=$|\s*[(:,.-])(?!\.\s*o)")
_UNTITLED_ANNEX = re.compile(r"^(anexo|apendice|appendix)\s*(?:$|[-:]?\s*(?:\(|a que se refere|\[|ao?\b|referido))")


def part_slug(title: str, *, max_length: int = 60) -> str:
    """Slug de um anexo: `Anexo — CÓDIGO DO TRABALHO` -> `anexo-codigo-do-trabalho`,
    `ANEXO II (a que se refere…)` -> `anexo-ii`, `Anexo (a que se refere…)` -> `anexo`."""
    text = re.sub(r"\s*[—–]\s*", " - ", _MD_LINK.sub(r"\1", _HTML_LINK.sub(r"\1", title)))
    text = _ascii(text).strip()
    numbered = _NUMBERED_ANNEX.match(text)
    if numbered:
        return f"{numbered.group(1)}-{numbered.group(2)}"
    if _UNTITLED_ANNEX.match(text):
        return _UNTITLED_ANNEX.match(text).group(1)
    slug = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if len(slug) > max_length:
        cut = slug[:max_length]
        slug = cut[: cut.rfind("-")] if "-" in cut else cut
    return slug or "anexo"


def body(markdown: str) -> str:
    """O texto do registo sem o cabeçalho YAML."""
    if markdown.startswith("---\n"):
        end = markdown.find("\n---\n", 4)
        if end != -1:
            return markdown[end + 5 :]
    return markdown


def _canonical_label(label: str) -> str:
    return _LABELS[label.lower()]


def _clean_number(number: str) -> str:
    return re.sub(r"\s+", "", number).rstrip(".")


class _Builder:
    """Acumula artigos e partes enquanto se percorrem as linhas."""

    def __init__(self) -> None:
        self.articles: list[Article] = []
        self.part = ""
        self.slug = ""
        self.slugs: set[str] = {""}
        self.keys: set[str] = set()
        self.implicit = 1
        self.current: Article | None = None
        self.lines: list[str] = []

    def close(self) -> None:
        if self.current is not None:
            self.current.text = "\n".join(self.lines).strip()
            self.articles.append(self.current)
        self.current, self.lines = None, []

    def open_part(self, title: str, slug: str | None = None) -> None:
        self.close()
        base = slug or part_slug(title)
        candidate, counter = base, 2
        while candidate in self.slugs:
            candidate, counter = f"{base}-{counter}", counter + 1
        self.slugs.add(candidate)
        self.part, self.slug, self.keys = title, candidate, set()

    def open_article(self, kind: str, number: str, heading: str, method: str, *, quoted: bool = False, line: str = "") -> None:
        self.close()
        article = Article(self.part, self.slug, kind, number, heading, "", method=method, quoted=quoted, source_line=line)
        if article.key in self.keys and self._unquote(article.key):
            pass
        elif article.key in self.keys:
            if number_slug(number) in {"1", "unico", "i"}:
                # A numeração recomeça sem título de anexo: parte implícita.
                self.implicit += 1
                self.open_part(f"Parte {self.implicit}", f"parte-{self.implicit}")
                article = Article(self.part, self.slug, kind, number, heading, "", method=method)
            else:
                article.repeat = 2
                while article.key in self.keys:
                    article.repeat += 1
        self.keys.add(article.key)
        self.current = article

    def _unquote(self, key: str) -> bool:
        """Se o artigo anterior com esta chave era uma nova redação citada, junta-o ao
        artigo que o cita e liberta a chave."""
        for index in range(len(self.articles) - 1, 0, -1):
            candidate = self.articles[index]
            if candidate.part_slug != self.slug or candidate.key != key:
                continue
            previous = self.articles[index - 1]
            if not candidate.quoted or previous.part_slug != self.slug:
                return False
            previous.text = "\n\n".join(filter(None, [previous.text, candidate.source_line, candidate.text]))
            previous.notes.extend(candidate.notes)
            for later in self.articles[index + 1 :]:
                if later.part_slug == self.slug:
                    previous.text = "\n\n".join(filter(None, [previous.text, later.source_line, later.text]))
                    self.keys.discard(later.key)
            del self.articles[index:]
            self.keys.discard(key)
            return True
        return False

    def add(self, line: str) -> None:
        if self.current is None:
            return
        if _NOTE.match(line):
            self.current.notes.append(line[2:].strip())
            return
        self.lines.append(_HTML_LINK.sub(r"\1", line))


def _split_heading(text: str | None) -> str:
    heading = (text or "").strip()
    if heading.startswith("(") and heading.endswith(")"):
        heading = heading[1:-1].strip()
    return heading


def _is_part_heading(title: str) -> bool:
    plain = _MD_LINK.sub(r"\1", title).strip()
    return not (_DIVISION.match(plain) or _ROMAN_DIVISION.match(plain))


def _quote_depth(depth: int, line: str) -> int:
    return max(0, depth + line.count("«") - line.count("»"))


def parse_articles(markdown: str) -> list[Article]:
    """Os artigos do corpo de um registo, pela ordem em que aparecem."""
    text = body(markdown)
    lines = text.splitlines()
    if any(_HEADING_ARTICLE.match(line) for line in lines):
        articles = _parse_headings(lines)
    else:
        articles = _parse_plain(lines)
    if not any(article.part == "" and article.kind != "numero" for article in articles):
        points = _parse_points(lines)
        if points:
            articles = points + [article for article in articles if article.part]
    return articles


def _next_number(builder: _Builder) -> str | None:
    """Número do artigo seguinte ao último título de artigo da parte atual."""
    last = builder.current or (builder.articles[-1] if builder.articles else None)
    if last is None or last.part_slug != builder.slug or last.kind != "artigo":
        return None
    digits = re.fullmatch(r"(\d+)", number_slug(last.number))
    return str(int(digits.group(1)) + 1) if digits else None


def _parse_headings(lines: list[str]) -> list[Article]:
    builder = _Builder()
    ended = False
    depth = 0
    pending_heading = False
    for line in lines:
        stripped = line.strip()
        plain = _PLAIN_ARTICLE.match(stripped) if depth == 0 and not stripped.startswith("#") else None
        if plain and not plain.group("rest").strip() and number_slug(plain.group("number")) == _next_number(builder):
            # Registos mistos: depois de uma nova redação citada, o DRE deixa às vezes os artigos
            # seguintes em texto corrido ("Artigo 3.º" numa linha, a epígrafe na seguinte).
            builder.open_article(_canonical_label(plain.group("label")), _clean_number(plain.group("number")), "", "texto")
            ended, pending_heading = False, True
            continue
        if pending_heading and stripped:
            pending_heading = False
            if builder.current is not None and _looks_like_heading(stripped):
                builder.current.heading = _split_heading(stripped)
                continue
        depth = _quote_depth(depth, line) if not line.startswith("#") else 0
        heading = _HEADING.match(line)
        if heading:
            level, title = len(heading.group(1)), heading.group(2).strip()
            if level == 1:
                continue
            if level == 2 and _is_part_heading(title):
                builder.open_part(title)
                ended = False
                continue
            article = _HEADING_ARTICLE.match(line)
            if article:
                heading_text = _split_heading(article.group("heading") or article.group("heading2"))
                # Textos antigos põem o próprio texto no título ("###### ARTIGO 30.º — É facultado…").
                body_in_heading = len(heading_text) > 200
                builder.open_article(
                    _canonical_label(article.group("label")),
                    _clean_number(article.group("number")),
                    "" if body_in_heading else heading_text,
                    "titulo",
                )
                if body_in_heading:
                    builder.add(heading_text)
                ended = False
                continue
            point = _HEADING_POINT.match(line)
            if point:
                builder.open_article("numero", _clean_number(point.group("number")), "", "titulo")
                ended = False
            continue
        if ended:
            continue
        if builder.current is not None and _signature(line):
            builder.close()
            ended = True
            continue
        builder.add(line)
    builder.close()
    return builder.articles


def _parse_plain(lines: list[str]) -> list[Article]:
    builder = _Builder()
    depth = 0
    ended = False
    pending_heading = False
    redaction = False
    for line in lines:
        stripped = line.strip()
        heading = _HEADING.match(line)
        if heading:
            level, title = len(heading.group(1)), heading.group(2).strip()
            if level == 2 and _is_part_heading(title):
                builder.open_part(title)
                ended, depth, pending_heading = False, 0, False
            continue
        if depth == 0 and _PLAIN_ANNEX.match(stripped) and (builder.articles or builder.current):
            builder.open_part(stripped)
            ended, pending_heading = False, False
            continue
        match = _PLAIN_ARTICLE.match(stripped) if depth == 0 else None
        if match and not _REFERENCE_REST.match(match.group("rest")) and _valid_plain_number(match):
            rest = match.group("rest")
            heading_text, first_line = _plain_rest(rest)
            builder.open_article(
                _canonical_label(match.group("label")), _clean_number(match.group("number")), heading_text, "texto",
                quoted=redaction, line=stripped,
            )
            if first_line:
                builder.add(first_line)
            redaction = bool(_REDACTION.search(first_line))
            pending_heading = not rest.strip()
            ended = False
            depth = _quote_depth(0, first_line)
            continue
        depth = _quote_depth(depth, line)
        if ended or builder.current is None:
            continue
        if not stripped:
            builder.add(line)
            continue
        if pending_heading:
            pending_heading = False
            if _looks_like_heading(stripped):
                builder.current.heading = _split_heading(stripped)
                continue
        if _signature(stripped):
            builder.close()
            ended = True
            continue
        redaction = bool(_REDACTION.search(stripped))
        builder.add(line)
    builder.close()
    return builder.articles


def _valid_plain_number(match: re.Match[str]) -> bool:
    number, rest, label = match.group("number"), match.group("rest"), match.group("label").lower()
    if re.match(r"[IVXLCDM]", number):
        # Numeração romana só nas bases e quando o número fecha a linha ou é seguido de pontuação.
        return label in {"base"} and (not rest.strip() or bool(re.match(r"^\s*[-—–.:(]", rest)))
    if label in {"art.", "artº", "art.º"} and not re.search(r"[º°]|\.o\b", number) and not rest.startswith("."):
        return bool(re.match(r"^\s*[-—–(]", rest))
    if not re.search(r"[º°]|\.o\b|nic", number, re.IGNORECASE):
        # "Artigo 1" sem ordinal: só quando a linha acaba ou continua com pontuação.
        return not rest.strip() or bool(re.match(r"^\s*[-—–.(]", rest))
    return True


def _plain_rest(rest: str) -> tuple[str, str]:
    """Epígrafe e início do texto do que vem a seguir ao número do artigo."""
    text = rest.strip()
    text = re.sub(r"^[.:]\s*", "", text)
    text = re.sub(r"^[-—–]\s*", "", text)
    if text.startswith("("):
        end = text.find(")")
        if 0 < end <= 160:
            return text[1:end].strip(), re.sub(r"^[.:\s-]+", "", text[end + 1 :]).strip()
    return "", text


def _looks_like_heading(line: str) -> bool:
    if len(line) > 160 or line[-1] in ".;:,»" or line[0] in "«(" or line[0].islower():
        return line.startswith("(") and line.endswith(")") and len(line) <= 160
    if re.match(r"^(?:\d|[a-z]\)|[IVXLC]+\s*[-—])", line):
        return False
    return not _PLAIN_ARTICLE.match(line)


def _parse_points(lines: list[str]) -> list[Article]:
    """Números do dispositivo (`1.º …`, `1 - …`) de um diploma sem artigos."""
    runs: list[list[tuple[int, int, str]]] = []
    depth = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        heading = _HEADING.match(line)
        if heading and len(heading.group(1)) == 2 and _is_part_heading(heading.group(2)):
            break
        if depth == 0 and runs and _PLAIN_ANNEX.match(stripped):
            break
        match = _PLAIN_POINT.match(stripped) if depth == 0 else None
        depth = _quote_depth(depth, line)
        if not match:
            continue
        number = int(match.group("number"))
        if number == 1:
            runs.append([(index, number, stripped)])
        elif runs and runs[-1][-1][1] == number - 1:
            runs[-1].append((index, number, stripped))
    if not runs:
        return []
    run = runs[-1]
    articles: list[Article] = []
    for position, (index, number, _) in enumerate(run):
        end = run[position + 1][0] if position + 1 < len(run) else len(lines)
        chunk: list[str] = []
        notes: list[str] = []
        for line in lines[index:end]:
            if _HEADING.match(line) and len(_HEADING.match(line).group(1)) == 2:
                break
            if _signature(line.strip()) or (chunk and _PLAIN_ANNEX.match(line.strip())):
                break
            if _NOTE.match(line):
                notes.append(line[2:].strip())
                continue
            chunk.append(_HTML_LINK.sub(r"\1", line))
        articles.append(Article("", "", "numero", f"{number}.º", "", "\n".join(chunk).strip(), notes, "texto"))
    return articles


def article_index(articles: list[Article]) -> dict[str, Article]:
    """Artigos pela âncora (`anexo-…/art-3`), para procurar um artigo pela referência."""
    return {article.anchor: article for article in articles}
