"""Datas de entrada em vigor, de produção de efeitos e de fim de vigência.

Lê as cláusulas do próprio diploma ("O presente decreto-lei entra em vigor no dia
seguinte ao da sua publicação", "…no 1.º dia do mês seguinte…", "…30 dias após…",
"…em 1 de janeiro de 2010", "produz efeitos a partir de…", "vigora até…") e calcula a
data quando a regra só depende da data de publicação (ou de assinatura) ou é uma data
explícita. Quando não dá para calcular ("com o Orçamento do Estado", "no dia útil
seguinte", "com a entrada em vigor do decreto-lei que…"), fica só a regra em texto.

Só contam as cláusulas do diploma (não as dos anexos, que podem ser códigos com as suas
próprias normas) e fora de aspas (a nova redação de um artigo de outro diploma).

Sem cláusula, a lei formulário fixa a regra supletiva: o 5.º dia após a publicação
(Lei n.º 74/98, art. 2.º, n.º 2; antes, Lei n.º 6/83, art. 2.º, n.º 2). Aplica-se só aos
atos da 1.ª série, de 30/07/1983 em diante e de âmbito nacional (`method: supletiva`),
e fica separada das datas lidas no texto.
"""

from __future__ import annotations

import calendar
import re
from dataclasses import dataclass, field
from datetime import date, timedelta

from leis_portugal.domain.articles import Article


MONTHS = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}
_NUMBER_WORDS = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8,
    "nove": 9, "dez": 10, "doze": 12, "quinze": 15, "vinte": 20, "trinta": 30, "quarenta": 40,
    "quarenta e cinco": 45, "sessenta": 60, "noventa": 90, "cento e vinte": 120, "cento e oitenta": 180,
    "trezentos e sessenta e cinco": 365,
    "primeiro": 1, "segundo": 2, "terceiro": 3, "quarto": 4, "quinto": 5, "sexto": 6, "sétimo": 7, "oitavo": 8,
    "nono": 9, "décimo": 10, "décimo quinto": 15, "vigésimo": 20, "trigésimo": 30, "quadragésimo quinto": 45,
    "sexagésimo": 60, "nonagésimo": 90, "centésimo vigésimo": 120, "centésimo octogésimo": 180,
}
_WORDS = "|".join(sorted((re.escape(word) for word in _NUMBER_WORDS), key=len, reverse=True))
_N = rf"(?:\d+(?:\.\s?º|º|\.o)?|{_WORDS})"
_MONTH = "|".join(MONTHS)

# Lei formulário: Lei n.º 6/83, de 29 de julho, e depois Lei n.º 74/98, de 11 de novembro.
SUPPLETIVE_FROM = "1983-07-30"
SUPPLETIVE_DAYS = 5
SUPPLETIVE_RULE = "5.º dia após a publicação (regra supletiva: Lei n.º 74/98, art. 2.º, n.º 2)"
# Tipos de ato a que se aplica a regra supletiva (atos legislativos e regulamentos da 1.ª série).
SUPPLETIVE_TYPES = frozenset({
    "lei", "lei-organica", "lei-constitucional", "decreto-lei", "decreto-regulamentar", "decreto", "portaria",
    "despacho-normativo", "resolucao-conselho-ministros",
})

_VERB = re.compile(
    r"\b(?P<verb>"
    r"(?P<vigor>entr(?:a|am|ará|arão|ando)\s+em\s+vigor|come[çc](?:a|am|ará|arão)\s+a\s+vigorar|inicia(?:m|rá|rão)?\s+a\s+(?:sua\s+)?vig[êe]ncia)"
    r"|(?P<efeitos>produz(?:em|irá|irão|indo|e)?\s+(?:os\s+seus\s+|todos\s+os\s+seus\s+|plenos\s+|os\s+)?efeitos(?:\s+(?:remunerat[óo]rios|financeiros|retroa[ct]?tivos|jur[íi]dicos))?)"
    r"|(?P<termo>vigor(?:a|am|ará|arão)\s+(?=at[ée]\b|durante\b|no\s+ano\b|pelo\s+(?:prazo|per[íi]odo)\b)|caduca(?:m|rá|rão)?\s+(?=em\b|no\s+dia\b|a\s+\d))"
    r")",
    re.IGNORECASE,
)
_WHOLE = re.compile(
    r"(?:^|[,;:]\s*|\b(?:e|que)\s+)(?:o|a|os|as)?\s*(?:presentes?|este|esta|estes|estas)\s+"
    r"(?:diploma|lei|decreto|portaria|resolu|despacho|regulamento|delibera|aviso|decis|acordo|conven|protocolo|regime|c[óo]digo|estatuto|norma|instrumento|tratado|ato|acto)",
    re.IGNORECASE,
)
_PARTIAL = re.compile(
    r"\b(?:artigos?|art\.|n\.º|n\.os|al[íi]neas?|disposto|normas?|anexos?|cap[íi]tulos?|sec[çc][õoã]\w*|tabelas?|mapas?|"
    r"quadros?|regras?|disposi[çc][õo]es|preceitos?|pontos?|n[úu]meros?|partes?|bases?|cl[áa]usulas?)\b",
    re.IGNORECASE,
)
_EXCEPTION = re.compile(r"^\s*(?:sem\s+preju[íi]zo|com\s+exce[çp]?[çc][ãa]o|exce[tp]to|salvo|ressalvad)[^,]*,", re.IGNORECASE)
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_SENTENCE = re.compile(r"(?<=[.;])\s+(?=[A-ZÁÉÍÓÚÂÊÔÀÇ«\d]\D)")
_EPIGRAPH = re.compile(r"vigor|vig[êe]ncia|efeitos|in[íi]cio|aplica[çc][ãa]o\s+no\s+tempo|disposi[çc][õo]es\s+finais", re.IGNORECASE)
_EVENT = r"(?P<event>publica[çc][ãa]o|assinatura|aprova[çc][ãa]o|distribui[çc][ãa]o|homologa[çc][ãa]o|notifica[çc][ãa]o)"
_FILLER = re.compile(r"\b(?:sua|seu|respe[c]?tiva|respe[c]?tivo|presente)\s+", re.IGNORECASE)

_NEXT_DAY = re.compile(rf"^(?:a\s+partir\s+d)?(?:n?o\s+)?dia\s+(?P<util>útil\s+)?(?:seguinte|imediato|subsequente|imediatamente\s+a\s+seguir|a\s+seguir|após)\s+(?:ao|à|a|d[ao])\s+(?:d[ao]\s+)?(?:data\s+d[ae]\s+)?{_EVENT}")
_SAME_DAY = re.compile(
    rf"^(?:a\s+partir\s+d[ae]\s+|desde\s+[ao]\s+|n[ao]\s+|à\s+|a\s+|com\s+[ao]\s+|após\s+[ao]\s+)(?:própria\s+)?(?:dia\s+|data\s+)?(?:d[ae]\s+|da\s+)?{_EVENT}"
)
_DAYS_AFTER = re.compile(
    rf"^(?:(?P<prefix>no\s+prazo\s+de|decorridos|passados|após\s+o\s+decurso\s+de|ao\s+fim\s+de|volvidos|findos)\s+)?(?:o\s+prazo\s+de\s+)?(?P<n>{_N})\s+dias(?P<util>\s+úteis)?\s+"
    rf"(?:após|depois\s+d[ae]|a\s+contar\s+d[ae]|seguintes?\s+(?:à|ao|a)|posteriores?\s+(?:à|ao|a)|contados?\s+d[ae]|sobre)\s+(?:a\s+|o\s+)?(?:d[ao]\s+)?(?:data\s+d[ae]\s+)?{_EVENT}"
)
_NTH_DAY = re.compile(
    rf"^n?o\s+(?P<n>{_N})\s+dia(?P<util>\s+útil)?\s+(?:seguinte|posterior|após|subsequente|a\s+contar)\s+(?:à|ao|a|d[ae])?\s*(?:d[ao]\s+)?(?:data\s+d[ae]\s+)?{_EVENT}"
)
_MONTH_DAY = re.compile(
    rf"^(?:a\s+partir\s+d)?n?o\s+(?:(?P<first>1\.\s?º|1º|primeiro)|dia\s+(?P<day>\d{{1,2}}))\s+dia(?P<util>\s+útil)?\s*do\s+(?:(?P<k>{_N})\s+)?m[êe]s\s+"
    rf"(?:seguinte|subsequente|imediato|posterior)\s+(?:à|ao|a)?\s*(?:d[ao]\s+)?(?:data\s+d[ae]\s+)?{_EVENT}"
)
_MONTH_DAY_ALT = re.compile(
    rf"^(?:a\s+partir\s+d)?n?o\s+dia\s+(?P<day>\d{{1,2}})\s+do\s+(?:(?P<k>{_N})\s+)?m[êe]s\s+(?:seguinte|subsequente|imediato|posterior)\s+(?:à|ao|a)?\s*(?:d[ao]\s+)?(?:data\s+d[ae]\s+)?{_EVENT}"
)
_MONTHS_AFTER = re.compile(
    rf"^(?:(?:no\s+prazo\s+de|decorridos|passados)\s+)?(?P<n>{_N})\s+meses\s+(?:após|depois\s+d[ae]|a\s+contar\s+d[ae]|contados?\s+d[ae])\s+(?:a\s+|o\s+)?(?:d[ao]\s+)?(?:data\s+d[ae]\s+)?{_EVENT}"
)
_EXPLICIT = re.compile(
    r"^(?:(?:com\s+efeitos\s+)?(?:retroa[ct]?tivos\s+|reportados\s+)?(?:a\s+partir\s+d[eoa]|desde|em|no|na|a|à|até|com\s+efeitos\s+(?:a\s+partir\s+)?d?[ea]|retroa[ct]?tivamente\s+a|reportados?\s+a)\s+)?"
    r"(?:(?:o\s+)?dia\s+)?(?:(?P<day>\d{1,2}|primeiro)(?:\.\s?º|º)?\s+de\s+(?P<month>" + _MONTH + r")\s+(?:de|do\s+ano\s+de)\s+(?P<year>\d{4})"
    r"|(?P<d2>\d{1,2})[-./](?P<m2>\d{1,2})[-./](?P<y2>\d{4})|(?P<y3>\d{4})-(?P<m3>\d{2})-(?P<d3>\d{2}))"
)
_YEAR = re.compile(r"^(?:durante\s+)?(?:o|no)\s+ano\s+(?:de\s+)?(?P<year>\d{4})")


@dataclass
class Clause:
    """Uma cláusula de vigência lida no texto."""

    kind: str  # vigor | efeitos | termo
    scope: str  # diploma | parcial
    rule: str
    date: str | None
    article: str | None
    text: str

    def to_dict(self) -> dict[str, str | None]:
        return {"kind": self.kind, "scope": self.scope, "rule": self.rule, "date": self.date, "article": self.article, "text": self.text}


@dataclass
class EntryIntoForce:
    """Resumo de um diploma: entrada em vigor, produção de efeitos e fim de vigência."""

    date: str | None = None
    rule: str | None = None
    method: str = "sem_clausula"  # clausula | supletiva | sem_clausula
    article: str | None = None
    effects_date: str | None = None
    effects_rule: str | None = None
    end_date: str | None = None
    end_rule: str | None = None
    clauses: list[Clause] = field(default_factory=list)

    @property
    def dates(self) -> list[str]:
        """Datas para `entry_into_force_dates`: a do diploma primeiro, depois as parciais."""
        values = [self.date] if self.date else []
        values += sorted({c.date for c in self.clauses if c.kind == "vigor" and c.date and c.date not in values})
        return values

    def to_dict(self) -> dict[str, object]:
        return {
            "date": self.date, "rule": self.rule, "method": self.method, "article": self.article,
            "effects_date": self.effects_date, "effects_rule": self.effects_rule,
            "end_date": self.end_date, "end_rule": self.end_rule,
        }


# ---------------------------------------------------------------------- cálculo


def _number(value: str) -> int | None:
    text = value.strip().lower()
    digits = re.match(r"\d+", text)
    if digits:
        return int(digits.group())
    return _NUMBER_WORDS.get(re.sub(r"\s+", " ", text))


def _add_months(start: date, months: int, *, day: int | None = None) -> date:
    month_index = start.month - 1 + months
    year, month = start.year + month_index // 12, month_index % 12 + 1
    last = calendar.monthrange(year, month)[1]
    return date(year, month, min(day if day is not None else start.day, last))


def _valid(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def compute(tail: str, *, publication: str | None, signature: str | None = None) -> tuple[str | None, str]:
    """Data e regra normalizada de uma cláusula, a partir do que vem depois do verbo.

    Devolve (data ou None, regra)."""
    text = _MD_LINK.sub(r"\1", tail)
    text = re.sub(r"\s+", " ", text).strip().lstrip(",").strip()
    lowered = _FILLER.sub("", text.lower())
    lowered = re.sub(r"\s+", " ", lowered)

    def base(event: str) -> date | None:
        if event.startswith("publica"):
            value = publication
        elif event.startswith("assinatura"):
            value = signature
        else:
            return None
        return date.fromisoformat(value) if value else None

    explicit = _EXPLICIT.match(lowered)
    if explicit:
        if explicit.group("month"):
            day = 1 if explicit.group("day") == "primeiro" else int(explicit.group("day"))
            value = _valid(int(explicit.group("year")), MONTHS[explicit.group("month")], day)
        elif explicit.group("y2"):
            value = _valid(int(explicit.group("y2")), int(explicit.group("m2")), int(explicit.group("d2")))
        else:
            value = _valid(int(explicit.group("y3")), int(explicit.group("m3")), int(explicit.group("d3")))
        return value, _rule(text)
    year = _YEAR.match(lowered)
    if year:
        return None, f"ano de {year.group('year')}"

    for pattern, kind in ((_NEXT_DAY, "next"), (_SAME_DAY, "same"), (_DAYS_AFTER, "days"), (_NTH_DAY, "nth"),
                          (_MONTH_DAY, "month"), (_MONTH_DAY_ALT, "month"), (_MONTHS_AFTER, "months")):
        match = pattern.match(lowered)
        if not match:
            continue
        event = match.group("event")
        groups = match.groupdict()
        rule = _rule(text)
        if groups.get("util") or groups.get("prefix") not in (None, "no prazo de"):
            # Dias úteis e "decorridos N dias" não se calculam: a contagem pede feriados ou é discutível.
            return None, rule
        start = base(event)
        if start is None:
            return None, rule
        if kind == "next":
            return (start + timedelta(days=1)).isoformat(), rule
        if kind == "same":
            return start.isoformat(), rule
        if kind in ("days", "nth"):
            days = _number(match.group("n"))
            return ((start + timedelta(days=days)).isoformat() if days else None), rule
        if kind == "month":
            months = _number(groups["k"]) if groups.get("k") else 1
            day = int(groups["day"]) if groups.get("day") else 1
            return (_add_months(start.replace(day=1), months, day=day).isoformat() if months else None), rule
        months = _number(match.group("n"))
        return (_add_months(start, months).isoformat() if months else None), rule
    return None, _rule(text)


def _rule(text: str) -> str:
    text = re.split(r"(?<=[a-zà-ú)])\.(?:\s|$)|;", text, maxsplit=1)[0]
    return text.strip(" ,.")[:200]


# ------------------------------------------------------------------- extração


def _unquoted_paragraphs(text: str) -> list[str]:
    """Parágrafos fora de aspas «…» (a nova redação de outros diplomas fica de fora)."""
    paragraphs: list[str] = []
    depth = 0
    for line in text.splitlines():
        stripped = line.strip()
        before = depth
        depth = max(0, depth + stripped.count("«") - stripped.count("»"))
        if before == 0 and stripped and not stripped.startswith("«"):
            paragraphs.append(_MD_LINK.sub(r"\1", stripped.split("«", 1)[0]))
    return paragraphs


def _lead(subject: str) -> str:
    """O sujeito sem o número do parágrafo nem a ressalva inicial ("Sem prejuízo…,")."""
    plain = re.sub(r"^\s*(?:\d+\s*[-–—]\s*|[a-z]\)\s*|\d+\.\s?º\s*)", "", subject)
    return _EXCEPTION.sub("", plain).strip()


def _scope(subject: str, previous: str | None) -> str:
    plain = _lead(subject)
    if not plain or re.fullmatch(r"(?:e|que|,)?\s*", plain, re.IGNORECASE):
        return previous or "diploma"
    whole = _WHOLE.search(plain)
    if whole:
        before = plain[: whole.start()]
        return "parcial" if _PARTIAL.search(before) else "diploma"
    return "parcial"


def clauses_in(text: str, *, article: str | None, publication: str | None, signature: str | None, epigraph_scope: bool) -> list[Clause]:
    """As cláusulas de um texto (um artigo, um número ou o corpo de um diploma sem artigos)."""
    found: list[Clause] = []
    for paragraph in _unquoted_paragraphs(text):
        for sentence in _SENTENCE.split(paragraph):
            previous: str | None = None
            position = 0
            for match in _VERB.finditer(sentence):
                if match.start() < position:
                    continue
                kind = "vigor" if match.group("vigor") else "efeitos" if match.group("efeitos") else "termo"
                subject = sentence[position : match.start()]
                if re.search(r"\bndo\b", match.group("verb")) or match.group("verb").lower().startswith("entrando"):
                    scope = previous or "diploma"
                elif position:
                    tail_subject = re.split(r"[,;]\s*(?:e\s+)?|\s+e\s+", subject)[-1]
                    scope = _scope(tail_subject, previous)
                else:
                    scope = _scope(subject, None)
                if scope == "diploma" and not epigraph_scope and not _WHOLE.search(_lead(subject)) and not previous:
                    # Sem "o presente…", só um artigo de entrada em vigor fala do diploma.
                    scope = "parcial"
                tail = sentence[match.end() :]
                stop = _VERB.search(tail)
                clause_tail = tail[: stop.start()] if stop else tail
                if stop and not clause_tail.strip(" ,e"):
                    # "entra em vigor e produz efeitos no dia seguinte…": a regra vem depois do segundo verbo.
                    rest = tail[stop.end() :]
                    following = _VERB.search(rest)
                    clause_tail = rest[: following.start()] if following else rest
                value, rule = compute(clause_tail, publication=publication, signature=signature)
                found.append(Clause(kind, scope, rule, value, article, sentence.strip()[:400]))
                previous, position = scope, match.end()
    return found


def extract(
    articles: list[Article],
    text: str,
    *,
    publication: str | None,
    signature: str | None = None,
    document_type: str | None = None,
    series: str | None = None,
    jurisdiction: str | None = None,
) -> EntryIntoForce:
    """Entrada em vigor de um diploma a partir dos artigos (ou do corpo, sem artigos)."""
    own = [article for article in articles if article.part == ""]
    clauses: list[Clause] = []
    if own:
        ordered = [a for a in own if _EPIGRAPH.search(a.heading)] + [a for a in own if not _EPIGRAPH.search(a.heading)]
        for article in ordered:
            clauses += clauses_in(
                article.text, article=article.anchor, publication=publication, signature=signature,
                epigraph_scope=bool(_EPIGRAPH.search(article.heading)) or article.kind == "numero",
            )
    else:
        clauses = clauses_in(_dispositive(text), article=None, publication=publication, signature=signature, epigraph_scope=True)

    result = EntryIntoForce(clauses=clauses)
    for clause in clauses:
        if clause.scope != "diploma":
            continue
        if clause.kind == "vigor" and result.rule is None:
            result.date, result.rule, result.article, result.method = clause.date, clause.rule, clause.article, "clausula"
        elif clause.kind == "efeitos" and result.effects_rule is None:
            result.effects_date, result.effects_rule = clause.date, clause.rule
        elif clause.kind == "termo" and result.end_rule is None:
            result.end_date, result.end_rule = clause.date, clause.rule
    if result.rule is None and not any(c.kind == "vigor" for c in clauses) and _suppletive(publication, document_type, series, jurisdiction):
        result.date = (date.fromisoformat(publication) + timedelta(days=SUPPLETIVE_DAYS)).isoformat()
        result.rule, result.method = SUPPLETIVE_RULE, "supletiva"
    return result


def _suppletive(publication: str | None, document_type: str | None, series: str | None, jurisdiction: str | None) -> bool:
    return bool(
        publication and publication >= SUPPLETIVE_FROM and series == "I" and jurisdiction == "portugal"
        and document_type in SUPPLETIVE_TYPES
    )


_ANNEX_HEADING = re.compile(r"^##\s+(?!#)")


def _dispositive(text: str) -> str:
    """O corpo até ao primeiro anexo."""
    lines: list[str] = []
    for line in text.splitlines():
        if _ANNEX_HEADING.match(line) or re.match(r"^(?:ANEXO|Anexo)\b.{0,120}$", line.strip()) and lines:
            break
        lines.append(line)
    return "\n".join(lines)
