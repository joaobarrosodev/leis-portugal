"""Relações entre documentos detetadas no texto: atos da UE citados e transpostos."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

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


_VALID_ELI = re.compile(r"^eli:https?://[\w-]+(?:\.[\w-]+)+/\S+$")
_KNOWN_TARGET = re.compile(r"^(?:pt:dre:[0-9]+:por|eu:celex:\S+|celex:\S+|pt:numero:[a-z0-9-]+:\S+)$")


def valid_target(target: str) -> bool:
    """Alvo de relação utilizável: id do acervo, CELEX, número de diploma ou ELI absoluto.

    A importação inicial deixou ligações partidas (`eli:h`, `eli:http://`,
    `eli:/application/external/tratado`), que não identificam nenhum documento."""
    if target.startswith("eli:"):
        # Um ELI do DRE só identifica um diploma com tipo, número e ano (`…/eli/e` não).
        if eli_key(target).startswith("data.dre.pt/"):
            return eli_work_key(target) is not None
        return bool(_VALID_ELI.match(target))
    return bool(_KNOWN_TARGET.match(target))


def eli_key(url: str) -> str:
    """Forma comparável de um ELI: sem `eli:`, sem esquema, sem a manifestação final
    (`/pt/html`) e sem `/` final. `https://data.dre.pt/eli/lei/7/2009/02/12/p/dre/pt/html`
    e `eli:http://data.dre.pt/eli/lei/7/2009/02/12/p/dre` dão a mesma chave."""
    value = re.sub(r"^https?://", "", url.removeprefix("eli:").strip(), flags=re.IGNORECASE).rstrip("/")
    return re.sub(r"/(?:pt/html|pt|html)$", "", value).rstrip("/").lower()


_DRE_ELI_WORK = re.compile(r"^data\.dre\.pt/eli/([^/]+)/([^/]+)/([0-9]{4})(?:/|$)")


def eli_work_key(url: str) -> str | None:
    """Tipo, número e ano de um ELI do DRE, comuns a todas as versões do diploma:
    `…/eli/dec-lei/202/2004/08/18/p/dre` (publicação) e
    `…/eli/dec-lei/202/2004/p/cons/20241011/pt/html` (consolidado) dão `dec-lei/202/2004`."""
    match = _DRE_ELI_WORK.match(eli_key(url))
    return "/".join(match.groups()) if match else None


class EliIndex:
    """ELI -> id do documento no acervo: primeiro o ELI exato, depois o diploma
    (tipo/número/ano), só quando um único documento do acervo o tem."""

    def __init__(self, entries: list[tuple[str, str]]) -> None:
        self.exact: dict[str, str] = {}
        works: dict[str, set[str]] = {}
        for record_id, eli in entries:
            self.exact[eli_key(eli)] = record_id
            work = eli_work_key(eli)
            if work:
                works.setdefault(work, set()).add(record_id)
        self.works = {work: next(iter(ids)) for work, ids in works.items() if len(ids) == 1}

    def get(self, eli: str) -> str | None:
        found = self.exact.get(eli_key(eli))
        if found:
            return found
        work = eli_work_key(eli)
        return self.works.get(work) if work else None


_DRE_ELI_PARTS = re.compile(
    r"^data\.dre\.pt/eli/(?P<code>[^/]+)/(?P<number>[^/]+)/(?P<year>[0-9]{4})"
    r"(?:/(?P<month>[0-9]{2})/(?P<day>[0-9]{2}))?/(?P<region>[pam])(?:/|$)"
)
_NUMBERED = re.compile(r"^pt:numero:(?P<type>[a-z0-9-]+):(?P<number>[^/]+)/(?P<year>[0-9]{2,4})(?:/(?P<region>[AMam]))?$")
_REGION_LETTER = {"acores": "a", "madeira": "m"}


@dataclass(frozen=True)
class DiplomaKey:
    """O que identifica um diploma pela numeração: tipo, número, ano e região
    (`p` nacional, `a` Açores, `m` Madeira)."""

    document_type: str
    number: str
    year: str
    region: str = "p"


def _year(value: str | None, reference: str | None) -> str | None:
    """Ano com 4 dígitos; um ano de 2 dígitos ("51/94") usa o século da data de referência."""
    if not value or not value.isdigit():
        return None
    if len(value) == 4:
        return value
    if len(value) == 2 and reference and reference[:4].isdigit():
        candidate = int(reference[:2] + value)
        return str(candidate - 100 if candidate > int(reference[:4]) else candidate)
    return None


def diploma_key(document_type: str | None, official_number: str | None, *, publication_date: str | None, territory: str | None) -> DiplomaKey | None:
    """Chave de um registo: `decreto-lei`, `"51/94"`, 1994-07-07 -> (decreto-lei, 51, 1994, p)."""
    if not document_type or not official_number:
        return None
    parts = [part.strip() for part in official_number.split(",")[0].split("/")]
    number = parts[0].lower().replace(" ", "")
    year = _year(parts[1] if len(parts) > 1 else None, publication_date) or (publication_date or "")[:4]
    if not number or not year:
        return None
    return DiplomaKey(document_type, number, year, _REGION_LETTER.get(territory or "", "p"))


class DiplomaIndex:
    """Diplomas do acervo pela numeração, para resolver ELI do DRE e referências por número
    (`pt:numero:decreto-lei:140/2009`) mesmo quando o registo não tem ELI.

    Com vários candidatos (p. ex. a mesma numeração na 1.ª e na 2.ª Série), decide a data
    de publicação do ELI e, por fim, a 1.ª Série; se ainda houver dúvida, não resolve."""

    def __init__(self, eli_codes: dict[str, str] | None = None) -> None:
        self.eli_codes = eli_codes or {}
        self._by_key: dict[DiplomaKey, list[tuple[str, str | None, str | None]]] = {}

    def add(self, record_id: str, key: DiplomaKey | None, *, publication_date: str | None, series: str | None) -> None:
        if key:
            self._by_key.setdefault(key, []).append((record_id, publication_date, series))

    def _pick(self, key: DiplomaKey, date: str | None) -> str | None:
        candidates = self._by_key.get(key) or []
        if len(candidates) > 1 and date:
            candidates = [item for item in candidates if item[1] == date] or candidates
        if len(candidates) > 1:
            first_series = [item for item in candidates if (item[2] or "I").upper() == "I"]
            candidates = first_series if len(first_series) == 1 else candidates
        return candidates[0][0] if len(candidates) == 1 else None

    def key_from_eli(self, eli: str) -> tuple[DiplomaKey, str | None] | None:
        """(chave do diploma, data de publicação) de um ELI do DRE com tipo conhecido."""
        match = _DRE_ELI_PARTS.match(eli_key(eli))
        if not match or match["code"] not in self.eli_codes:
            return None
        key = DiplomaKey(self.eli_codes[match["code"]], match["number"].lower(), match["year"], match["region"])
        return key, f"{match['year']}-{match['month']}-{match['day']}" if match["month"] else None

    @staticmethod
    def key_from_number(target: str) -> DiplomaKey | None:
        """Chave do diploma de uma referência `pt:numero:<tipo>:<número>/<ano>[/A|M]`."""
        match = _NUMBERED.match(target)
        if not match:
            return None
        year = _year(match["year"], str(date.today().year)) if len(match["year"]) == 2 else match["year"]
        return DiplomaKey(match["type"], match["number"].lower(), year or "", (match["region"] or "p").lower())

    def from_eli(self, eli: str) -> str | None:
        found = self.key_from_eli(eli)
        return self._pick(*found) if found else None

    def from_number(self, target: str) -> str | None:
        key = self.key_from_number(target)
        return self._pick(key, None) if key else None


# Abreviaturas da análise jurídica antiga do DRE ("pelo DEC LEI.189/90", "PELA PORT 12/91").
_ABBREVIATIONS = {
    "PORT": "portaria", "PORTARIA": "portaria",
    "DEC LEI": "decreto-lei", "DECRETO LEI": "decreto-lei", "DL": "decreto-lei",
    "LEI": "lei",
    "DN": "despacho-normativo", "DESPACHO NORMATIVO": "despacho-normativo",
    "DECLARACAO DE RECTIFICACAO": "declaracao-retificacao", "DECLARACAO RECTIFICACAO": "declaracao-retificacao",
    "DECLARACAO DE RETIFICACAO": "declaracao-retificacao", "RECTIFICACAO": "declaracao-retificacao",
    "DR": "decreto-regulamentar", "DEC REG": "decreto-regulamentar", "DECRETO REGULAMENTAR": "decreto-regulamentar",
    "DRR": "decreto-regulamentar-regional", "DECRETO REGULAMENTAR REGIONAL": "decreto-regulamentar-regional",
    "DLR": "decreto-legislativo-regional", "DECRETO LEGISLATIVO REGIONAL": "decreto-legislativo-regional",
    "DEC": "decreto", "DECRETO": "decreto",
    "RES": "resolucao", "RESOLUCAO": "resolucao",
    "RCM": "resolucao-conselho-ministros", "RESOLUCAO DO CONSELHO DE MINISTROS": "resolucao-conselho-ministros",
}
_BY_ACT = re.compile(
    r"\bpel[oa](?:\(a\))?\s+(?P<kind>[A-ZÇÃÉÁÍÓÚÂÊÔ][A-Za-zÇÃÉÁÍÓÚÂÊÔçãéáíóúâêô .-]{0,45}?)\s*[.]?\s*"
    r"(?:N(?:UMERO|\.?\s*[º°O]))?\s*(?P<number>[0-9][0-9A-Za-z-]*)/(?P<year>[0-9]{2,4})(?:/(?P<region>[AMam])\b)?",
    re.IGNORECASE,
)


def _plain_upper(text: str) -> str:
    table = str.maketrans("ÇÃÉÁÍÓÚÂÊÔçãéáíóúâêô", "CAEAIOUAEOcaeaiouaeo")
    return re.sub(r"[\s.-]+", " ", text.translate(table)).strip().upper()


def acting_reference(text: str | None) -> str | None:
    """Diploma que produz a alteração numa nota da análise jurídica antiga do DRE, como
    referência por número: "…rectificado pelo DEC LEI.189/90.08.06.1990" ->
    `pt:numero:decreto-lei:189/90`. Conta a última menção "pelo/pela …", que é a do ato
    que altera (as anteriores descrevem o diploma alterado); sem abreviatura conhecida,
    devolve None."""
    found = None
    for match in _BY_ACT.finditer((text or "").replace("\x00", " ")):
        kind = _ABBREVIATIONS.get(re.sub(r"\s+NUMERO$", "", _plain_upper(match["kind"])))
        if kind:
            region = f"/{match['region'].upper()}" if match["region"] else ""
            found = f"pt:numero:{kind}:{match['number'].upper()}/{match['year']}{region}"
    return found


def placeholder_source(source: str | None) -> bool:
    """Ligação da análise jurídica do DRE a "sem diploma": aponta para um marcador, não para um documento."""
    return "/sem-diploma/" in (source or "")


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
