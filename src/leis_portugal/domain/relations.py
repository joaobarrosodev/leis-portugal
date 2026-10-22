"""Relações entre documentos detetadas no texto: atos da UE citados e transpostos."""

from __future__ import annotations

import re

from leis_portugal.domain.record import Relationship


_ELI_EU = re.compile(r"data\.europa\.eu/eli/(?P<kind>reg|dir|dec)(?:_impl|_del)?/(?P<year>[0-9]{4})/(?P<number>[0-9]+)")
_EU_CELEX_TYPE = {"reg": "R", "dir": "L", "dec": "D"}

_EU_TYPE_LETTER = {"regulamento": "R", "diretiva": "L", "directiva": "L", "decisão": "D", "decisao": "D"}
_EU_PREFIX = r"(Regulamento|Diretiva|Directiva|Decis[ãa]o)(?:\s+(?:Delegad[oa]|de\s+Execu[çc][ãa]o|Quadro))?"
_NUMBER_MARK = r"(?:n\.?\s*[ºo°]\s*)"
# "Diretiva (UE) 2016/798", "Regulamento (CE) n.º 1408/2013", "Regulamento (CEE) n.º 1408/71"
_EU_WITH_ORG = re.compile(
    rf"\b{_EU_PREFIX}\s*\((?:UE|CE|CEE|Euratom|PESC)\)\s*({_NUMBER_MARK})?(\d{{1,4}})/(\d{{1,4}})(?!/)",
    re.IGNORECASE,
)
# "Directiva 2002/58/CE", "Diretiva n.º 89/391/CEE", "Decisão 2009/750/CE"
_EU_WITH_SUFFIX = re.compile(
    rf"\b{_EU_PREFIX}\s+{_NUMBER_MARK}?(\d{{2,4}})/(\d{{1,4}})/(?:CEE|CE|UE|Euratom|CECA)\b",
    re.IGNORECASE,
)
_TRANSPOSITION = re.compile(r"transp(?:õe|oe|ondo|osição|osicao|ôs|ostas?|ostos?|or)\b", re.IGNORECASE)


def celex_from_eu_eli(eli: str) -> str | None:
    """`http://data.europa.eu/eli/reg/2013/1408/oj` -> `32013R1408`."""
    match = _ELI_EU.search(eli or "")
    if not match:
        return None
    return f"3{match.group('year')}{_EU_CELEX_TYPE[match.group('kind')]}{int(match.group('number')):04d}"


def citation_target(url: str) -> str:
    """Alvo de uma citação: CELEX para atos da UE, ELI para o resto."""
    celex = celex_from_eu_eli(url)
    if celex:
        return f"celex:{celex}"
    return f"eli:{url.strip()}"


def _full_year(value: str) -> int | None:
    year = int(value)
    if len(value) == 2:
        year += 1900 if year >= 50 else 2000
    return year if 1950 <= year <= 2100 else None


def _eu_celex(kind: str, year: int | None, number: int) -> str | None:
    letter = _EU_TYPE_LETTER.get(kind.lower())
    if not letter or year is None or not 0 < number <= 9999:
        return None
    return f"3{year}{letter}{number:04d}"


def _transposition_context(text: str, position: int, kind: str) -> bool:
    if _EU_TYPE_LETTER.get(kind.lower()) != "L":
        return False
    sentence_start = max(0, text.rfind(". ", 0, position), text.rfind("\n", 0, position), position - 400)
    return bool(_TRANSPOSITION.search(text[sentence_start:position]))


def eu_references(text: str) -> dict[str, str]:
    """CELEX dos atos da UE citados num texto português -> "transposes" ou "cites".

    Uma diretiva citada na mesma frase que "transpõe"/"transposição" conta como
    transposta pelo diploma; as restantes referências contam como citações.
    """
    found: dict[str, str] = {}
    for match in _EU_WITH_ORG.finditer(text or ""):
        kind, mark, first, second = match.group(1), match.group(2), match.group(3), match.group(4)
        if not mark and len(first) == 4 and _full_year(first):
            year, number = _full_year(first), int(second)  # estilo pós-2015: ano/número
        else:
            year, number = _full_year(second) if len(second) in {2, 4} else None, int(first)
        celex = _eu_celex(kind, year, number)
        if celex:
            found.setdefault(celex, "cites")
            if _transposition_context(text, match.start(), kind):
                found[celex] = "transposes"
    for match in _EU_WITH_SUFFIX.finditer(text or ""):
        celex = _eu_celex(match.group(1), _full_year(match.group(2)), int(match.group(3)))
        if celex:
            found.setdefault(celex, "cites")
            if _transposition_context(text, match.start(), match.group(1)):
                found[celex] = "transposes"
    return found


def eu_relationships(text: str) -> list[Relationship]:
    return [Relationship(type=relation, target=f"celex:{celex}") for celex, relation in sorted(eu_references(text).items())]
