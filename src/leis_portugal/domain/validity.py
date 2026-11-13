"""Provas de vigência: revogações lidas no texto e nas relações do DRE.

O DRE não indica o estado de vigência de muitos diplomas (`legal_status: unknown`). Este
módulo não o infere: junta provas, cada uma com a sua proveniência, e só propõe um estado
quando a prova o fixa sem ambiguidade.

- **Norma revogatória** de outro diploma do acervo ("São revogados: a) O Decreto-Lei
  n.º 85/83…"), com a ligação ao diploma revogado. A revogação é **total** quando o que
  vem antes da ligação é só o verbo e o artigo ("É revogado o"), e **parcial** quando
  nomeia uma parte ("o artigo 5.º do", "os n.os 2 e 3 do"). Ligações noutro papel
  ("na redação dada pelo", "aprovado pelo") e revogações condicionais ("a partir da
  entrada em vigor da portaria…") não contam.
- **Relações do DRE** (`repealed_by` do próprio diploma, `repeals` de outros): a etiqueta
  diz se é total ("Revogado pelo DEC LEI…") ou parcial ("Revogado o nº 5 pela…"); sem
  etiqueta, não se sabe.
- **Cláusula de vigência temporária** do próprio diploma ("vigora até 31 de dezembro de
  2015"), já passada e sem alterações posteriores: caducou.

Uma revogação parcial não diz se o resto está em vigor: o estado fica desconhecido e a
revogação parcial fica registada como prova.

Contra um estado do DRE (`in_force`), a norma revogatória só conta se a ligação apontar mesmo
para o diploma revogado (`identity`: o número do rótulo, a data citada e a entidade) e se nenhum
outro artigo do revogador a ressalvar (`saving_clauses`). Não contam as notas do DRE ("> Nota:"),
os parágrafos sem verbo de um artigo "Revogação" (a lista de legislação de um PDM) nem as
revogações descritas ("…que aprova… e revoga a Lei Orgânica n.º 4/2006").
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date as _date

from leis_portugal.domain.articles import Article
from leis_portugal.domain.identifiers import pt_record_id


@dataclass
class Repeal:
    """Uma revogação lida na norma revogatória de um diploma."""

    target: str
    scope: str  # total | parcial
    source: str
    article: str | None
    text: str
    # O rótulo da ligação ("Portaria n.º 216/85"), a data citada a seguir ("--05-15" sem ano,
    # "1985-05-15" com ano) e a entidade nomeada ("Banco de Portugal"): confirmam se a ligação do
    # DRE aponta para o diploma que o texto revoga (ver `identity`).
    label: str = ""
    cited_date: str | None = None
    cited_entity: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "target": self.target, "scope": self.scope, "source": self.source, "article": self.article, "text": self.text,
            "label": self.label, "cited_date": self.cited_date, "cited_entity": self.cited_entity,
        }


@dataclass
class Evidence:
    """Uma prova sobre a vigência de um diploma, com a proveniência."""

    status: str  # repealed | partially_repealed | not_in_force | unclear
    provenance: str
    detail: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"status": self.status, "provenance": self.provenance, "detail": self.detail}


@dataclass
class Proposal:
    """O estado proposto para um diploma de vigência desconhecida, com as provas."""

    status: str | None
    category: str
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {"status": self.status, "category": self.category, "evidence": [item.to_dict() for item in self.evidence]}


# ------------------------------------------------------------- norma revogatória

_DRE_LINK = re.compile(r"\[(?P<label>[^\]]*)\]\((?P<url>https?://(?:www\.)?diariodarepublica\.pt/dr/detalhe/[^)\s]*?-(?P<id>\d+))\)")
_REPEAL_VERB = re.compile(
    r"\b(?:(?:é|são|fica|ficam|serão|será|considera-se|consideram-se)\s+(?:(?:também|ainda|igualmente|expressamente)\s+)?revogad[oa]s?|"
    r"revoga(?:m)?-se|revoga(?:m)?\b|revogando)",
    re.IGNORECASE,
)
_REPEAL_EPIGRAPH = re.compile(r"revoga", re.IGNORECASE)
_LIST_ITEM = re.compile(r"^(?:[a-z]{1,2}\)|[ivxl]+\)|\d+\)|[-–•])\s", re.IGNORECASE)
_PARTIAL_WORDS = re.compile(
    r"\b(?:artigos?|art\.|arts\.|n\.º|n\.os|n\.ºs|nºs?|al[íi]neas?|anexos?|cap[íi]tulos?|sec[çc](?:ão|ões)|subsec|t[íi]tulos?|"
    r"partes?|pontos?|n[úu]meros?|quadros?|mapas?|tabelas?|listas?|bases?|cl[áa]usulas?|par[áa]grafos?|§|preceitos?|"
    r"disposi[çc](?:ão|ões)|normas?|regras?|redac?[çc][ãa]o|parte\s+final|segmento|express[ãa]o|palavras?)\b",
    re.IGNORECASE,
)
_CONTEXT_WORDS = re.compile(
    r"redac?[çc][ãa]o|alterad|aprovad|republicad|previst|referid|nos\s+termos|ao\s+abrigo|regulamentad|conferid|constante|"
    r"estabelecid|a\s+que\s+se\s+refere|por\s+for[çc]a|mant[êée]m|mantid|exce[çp]|salvo|ressalv|sem\s+preju[íi]zo|"
    r"sequ[êe]ncia|decorrente|introduzid|dada\s+pel|conjugad|publicad|aplic[áa]ve|previsto|bem\s+como\s+(?:a|as|os|o)\s+(?:respetiv|respectiv)",
    re.IGNORECASE,
)
_CONDITIONAL = re.compile(
    r"a\s+partir\s+d[ao]s?\s+(?:entrada\s+em\s+vigor|publica[çc][ãa]o|in[íi]cio)|com\s+a\s+entrada\s+em\s+vigor|"
    r"transitoriamente|at[ée]\s+(?:à|a)\s+(?:entrada|publica|aprova)|mantendo-se|mant[ée]m-se|continua(?:m)?\s+(?:em\s+vigor|a\s+aplicar)|"
    r"(?:na|à)\s+data\s+d[ao]s?\s+(?!sua\s+(?:publica|entrada)|publica[çc][ãa]o\s+d[oa]\s+presente|entrada\s+em\s+vigor\s+d[oa]\s+presente)|produz(?:indo)?\s+efeitos\s+(?:a\s+partir|em|no|na)|n[ãa]o\s+(?:é|são)\s+revogad|"
    # Diferidas: "Findo o processo de transição…", "Concluído o processo…", "a partir do momento em que…",
    # "com efeito à data da entrada em vigor da regulamentação", "de acordo com a calendarização…".
    r"\bfind[oa]s?\s+(?:o|a|os|as)\b|\bconclu[íi]d[oa]s?\s+(?:o|a|os|as)\b|a\s+partir\s+do\s+momento|"
    r"a\s+partir\s+da\s+data\s+(?:da|de|em)\s+(?!sua\s+publica|publica[çc][ãa]o\s+d[oa]\s+presente)|"
    r"com\s+efeitos?\s+(?:reportados?\s+)?(?:(?:à|a)\s+data|após|a\s+partir\s+da\s+(?:entrada|publica))|calendariza[çc]|"
    r"\bdependente\b|\bpermanecendo\b|mant[êée]m(?:-se)?\s+(?:em\s+vigor|aplic[áa]ve|a\s+vig)|vig[êe]ncia\s+transit|"
    r"at[ée]\s+que\b|at[ée]\s+(?:à|ao)\s+(?:altera|aprova|publica|entrada|revis)|repristin|\bcaduque\b|"
    r"em\s+rela[çc][ãa]o\s+(?:à|ao|às|aos)\b|ap[óo]s\s+a\s+(?:entrada\s+em\s+vigor|publica[çc][ãa]o)\s+d[oa]s?\s+(?!presente)",
    re.IGNORECASE,
)
_LINK_URL = re.compile(r"\]\([^)]*\)")
_CLAUSE_PARTIAL = re.compile(
    r"\bna\s+parte\b|\bnas\s+partes\b|com\s+exce|\bexce[tp]to\b|\bsalvo\b|em\s+tudo\s+o\s+que|ressalvad|à\s+exce|"
    r"sem\s+preju[íi]zo|\bparcialmente\b|\bapenas\s+(?:o|a|os|as|n[ao])\b|no\s+que\s+(?:respeita|se\s+refere|diz\s+respeito)|"
    # "em tudo quanto se oponha ao presente diploma", "na matéria respeitante a…", "quanto às disposições…".
    r"em\s+tudo\s+quanto|tudo\s+o\s+que\s+(?:contrari|se\s+op)|na\s+mat[ée]ria|\bquanto\s+(?:à|ao|às|aos)\b|no\s+ponto\s+que|"
    r"\bsalv[ao]s\s+(?:as|os)\b|na\s+medida\s+em\s+que|\ba\s+parte\s+que",
    re.IGNORECASE,
)
_AFTER_PARTIAL = re.compile(
    r"^\s*,?\s*(?:na\s+parte|no\s+que|com\s+exce|exce[tp]|salvo|em\s+tudo\s+o\s+que|apenas|s[óo]\s|somente|relativamente|quanto|"
    r"nas?\s+partes?|ressalvad|à\s+exce)",
    re.IGNORECASE,
)
# O que pode ficar entre o verbo e a ligação numa revogação total: artigos, conjunções,
# designações do tipo de diploma, a data ("de 11 de fevereiro") e marcas de lista.
_FILLER = re.compile(
    r"(?:[a-z]{1,2}\)|\b(?:o|a|os|as|e|ainda|também|igualmente|expressamente|bem\s+como|assim\s+como|integralmente|na\s+íntegra|"
    r"lei|leis|org[âa]nica|decretos?-leis?|decretos?|regulamentar(?:es)?|legislativos?|regionais?|portarias?|despachos?|"
    r"normativos?|conjuntos?|resolu[çc](?:ão|ões)|do\s+conselho\s+de\s+ministros|da\s+assembleia\s+da\s+rep[úu]blica|"
    r"avisos?|deliberaç(?:ão|ões)|n\.º|n\.os|n\.ºs|nºs?|seguintes?|diplomas?|de\s+\d{1,2}\s+de\s+\w+(?:\s+de\s+\d{2,4})?|"
    r"de\s+\d{1,2}-\w+|com\s+as\s+(?:posteriores\s+)?alterações(?:\s+posteriores)?|e\s+demais\s+legislação)\b|\d+\s*[-–—]\s|[,;:.\s]|\(\s*\))",
    re.IGNORECASE,
)
_PARTIAL_TAIL = re.compile(r"\b(?:do|da|dos|das|ao|à|aos|às|no|na|nos|nas)\s*$", re.IGNORECASE)


def _unquoted_paragraphs(text: str) -> list[str]:
    paragraphs: list[str] = []
    depth = 0
    for line in text.splitlines():
        stripped = line.strip()
        before = depth
        depth = max(0, depth + stripped.count("«") - stripped.count("»"))
        if before == 0 and stripped and not stripped.startswith("«"):
            paragraphs.append(stripped.split("«", 1)[0])
    return paragraphs


def _classify(segment: str, after: str, clause: str) -> str | None:
    """`total`, `parcial` ou None (a ligação não é o diploma revogado, ou não se sabe)."""
    if _CONDITIONAL.search(clause):
        return None
    if _CONTEXT_WORDS.search(segment):
        return None
    # "os Decretos-Leis n.os [85/83]…": o número do diploma, não de um preceito.
    segment = re.sub(r"(?:n\.º|n\.os|n\.ºs|nºs?)\s*$", "", segment.rstrip())
    if _PARTIAL_WORDS.search(segment):
        return "parcial" if _PARTIAL_TAIL.search(segment) else None
    remainder = _FILLER.sub("", _REPEAL_VERB.sub("", segment))
    if remainder:
        return None
    if _AFTER_PARTIAL.match(after):
        return "parcial"
    return "total"


def _filler_only(segment: str) -> bool:
    return not _FILLER.sub("", segment)


def repeals_in(articles: list[Article], text: str, *, source: str) -> list[Repeal]:
    """As revogações das normas revogatórias de um diploma (só a parte do diploma, sem anexos)."""
    own = [article for article in articles if article.part == ""]
    if own:
        blocks = [(article.anchor, article.text, bool(_REPEAL_EPIGRAPH.search(article.heading))) for article in own]
    else:
        blocks = [(None, text, False)]
    found: dict[tuple[str, str], Repeal] = {}
    for anchor, block, epigraph in blocks:
        listing = False
        intro = ""
        for paragraph in _unquoted_paragraphs(block):
            if paragraph.startswith(">"):
                # Notas do DRE ("> Nota: [Artigo 3.º, Portaria n.º 128-A/2022 - Diário da República …]"):
                # não são texto do diploma.
                listing = False
                continue
            has_verb = bool(_REPEAL_VERB.search(paragraph))
            # Numa lista aberta por uma frase com o verbo ("São revogados:"), contam os itens com marca
            # ("a) …") e, num artigo de epígrafe revogatória, os itens sem marca enquanto a lista continua
            # (o anterior acabou em ":" ou ";"). Sem verbo, um parágrafo de um artigo "Revogação" (a lista
            # de legislação ou de imóveis classificados de um PDM) não revoga nada.
            item = listing and (bool(_LIST_ITEM.match(paragraph)) or epigraph)
            in_context = has_verb or item
            if has_verb:
                listing = paragraph.rstrip().endswith(":")
                intro = paragraph
            elif item:
                listing = bool(_LIST_ITEM.match(paragraph)) or paragraph.rstrip().endswith((";", ":"))
            else:
                listing = False
                intro = ""
            if not in_context:
                continue
            # Os itens de uma lista ("São revogados: a) …") herdam a condição da frase que a abre
            # ("Findo o processo de transição…, são revogadas:").
            lead = intro if (item and not has_verb) else ""
            for repeal in _paragraph_repeals(paragraph, source=source, article=anchor, lead=lead):
                key = (repeal.target, repeal.scope)
                found.setdefault(key, repeal)
    # Total e parcial do mesmo diploma no mesmo texto: fica a total só se não houver dúvida.
    result: list[Repeal] = []
    for (target, scope), repeal in found.items():
        if scope == "parcial" and (target, "total") in found:
            continue
        result.append(repeal)
    saved = saving_clauses([article.text for article in own] or [text], result)
    for repeal in result:
        if repeal.scope == "total" and repeal.target in saved:
            # "Mantém-se em vigor a Portaria n.º 213/2000 até à publicação das portarias…", noutro artigo.
            repeal.scope = "parcial"
    return result


# Ressalvas e vigência transitória do revogado noutro artigo (ou noutro número) do revogador.
_SAVING = re.compile(
    r"mant[êée]m(?:-se)?\s+(?:em\s+vigor|a\s+vig[êe]ncia|aplic[áa]ve)|mant[êe]m-se\b|mant[êe]m\s+a\s+vig[êe]ncia|"
    r"continua(?:m)?\s+(?:a\s+(?:aplicar-se|vigorar|produzir)|em\s+vigor)|at[ée]\s+(?:à|ao)\s+(?:publica[çc][ãa]o|entrada\s+em\s+vigor)|"
    r"transitoriamente|permanece(?:m)?\s+em\s+vigor|ressalv|sem\s+preju[íi]zo\s+d[oa]\s+dispost",
    re.IGNORECASE,
)


def _number_of(label: str) -> str | None:
    match = _LABEL_NUMBER.search(label)
    return match.group("number").lower() if match else None


_LABEL_NUMBER = re.compile(r"(?:n\.?\s*[º°o]s?\s*|^)(?P<number>\d+(?:-[a-z]{1,3})?(?:/\d{2,4})?(?:/[a-z])?)(?![\w/])", re.IGNORECASE)


def saving_clauses(blocks: list[str], repeals: list[Repeal]) -> set[str]:
    """Os alvos de revogações totais que outro parágrafo do revogador ressalva ou mantém em vigor
    ("mantêm-se em vigor… até à publicação", "continua a aplicar-se transitoriamente"). Procura-se
    o alvo pela ligação (id do DRE) ou pelo número do rótulo."""
    keys: dict[str, list[str]] = {}
    for repeal in repeals:
        if repeal.scope != "total":
            continue
        dre_id = repeal.target.split(":")[2] if repeal.target.count(":") >= 2 else repeal.target
        number = _number_of(repeal.label)
        keys[repeal.target] = [f"-{dre_id})"] + ([number] if number and "/" in number else [])
    saved: set[str] = set()
    if not keys:
        return saved
    for block in blocks:
        for paragraph in _unquoted_paragraphs(block):
            if paragraph.startswith(">") or not _SAVING.search(_LINK_URL.sub("]", paragraph)):
                continue
            lowered = paragraph.lower()
            for target, needles in keys.items():
                if any(_mentions(lowered, needle) for needle in needles):
                    saved.add(target)
    return saved


# "A regulamentação emitida ao abrigo do [Decreto-Lei n.º 129/93] mantém-se em vigor": o que fica é
# outro ato, não o revogado.
_DERIVED = re.compile(r"(?:ao\s+abrigo|emitid[oa]s?|regulamenta[çc][ãa]o|regulamentos?|aprovad[oa]s?\s+(?:ao\s+abrigo|nos\s+termos))\s+(?:d[oa]s?|n[oa]s?|pel[oa]s?)\s+(?:\[\s*)?(?:[\w.º-]+\s+){0,3}$")


def _mentions(text: str, needle: str) -> bool:
    for match in re.finditer(re.escape(needle) if needle.endswith(")") else rf"(?<![\w/-]){re.escape(needle)}(?![\w/])", text):
        before = text[max(0, match.start() - 160) : match.start()]
        if needle.endswith(")"):
            before = before[: before.rfind("[")] if "[" in before else before
        if not _DERIVED.search(before):
            return True
    return False


def _paragraph_repeals(paragraph: str, *, source: str, article: str | None, lead: str = "") -> list[Repeal]:
    repeals: list[Repeal] = []
    links = list(_DRE_LINK.finditer(paragraph))
    # Os URLs das ligações ficam tapados (mesmo comprimento): o ":" de "https:" não separa itens.
    masked = _LINK_URL.sub(lambda match: "](" + "x" * (len(match.group()) - 3) + ")", paragraph)
    verb = _REPEAL_VERB.search(masked)
    if verb and _DESCRIPTIVE.search(masked[: verb.end()]):
        # "…a [Lei Orgânica n.º 7/2015], que aprova a lei de programação militar e revoga a [Lei Orgânica
        # n.º 4/2006]" ou o sumário "…em alguns concelhos. Revoga o [Decreto-Lei n.º 47892]": descreve uma
        # revogação feita por outro diploma.
        return []
    start = verb.end() if verb else 0
    # O que vem antes do verbo (ou a frase que abre a lista) também pode diferir ou limitar a revogação.
    lead = _LINK_URL.sub("]", lead) + " " + (masked[: verb.start()] if verb else "")
    if _CONDITIONAL.search(lead):
        return []
    lead_partial = bool(_CLAUSE_PARTIAL.search(lead))
    context_item: int | None = None
    dates = _cited_dates(masked, links)
    for index, link in enumerate(links):
        if verb and link.start() < verb.start():
            continue
        item_start = max(masked.rfind(";", 0, link.start()) + 1, masked.rfind(":", 0, link.start()) + 1)
        clause_start = max(start, item_start)
        previous_end = links[index - 1].end() if index else 0
        segment = masked[max(clause_start, previous_end) : link.start()]
        next_start = links[index + 1].start() if index + 1 < len(links) else len(paragraph)
        after = masked[link.end() : next_start]
        after = re.split(r"[;]", after, maxsplit=1)[0]
        clause_end = masked.find(";", link.end())
        clause = paragraph[item_start : clause_end if clause_end != -1 else len(paragraph)]
        scope = _classify(segment, after, clause)
        if _CONTEXT_WORDS.search(segment):
            # As ligações seguintes do mesmo item continuam a lista ("alterado pelos Decretos-Leis n.os [A], de…, e [B]").
            context_item = item_start
        elif context_item == item_start and index and _filler_only(segment):
            scope = None
        if scope == "total" and (lead_partial or _CLAUSE_PARTIAL.search(_LINK_URL.sub("]", clause))):
            # "O Decreto-Lei n.º 350/88, de 30 de setembro, com excepção dos artigos 5.º e 6.º"
            scope = "parcial"
        if scope is None:
            continue
        target = pt_record_id(link.group("id"))
        if target == source:
            continue
        repeals.append(Repeal(
            target, scope, source, article, re.sub(r"\]\([^)]*\)", "]", clause).strip()[:300],
            label=link.group("label"), cited_date=dates.get(index), cited_entity=_entity(masked[link.end() : link.end() + 160]),
        ))
    return repeals


# Um diploma citado como o sujeito de "que aprova… e revoga", ou um sumário que começa por "Revoga o".
_DESCRIPTIVE = re.compile(
    r"\]\([x]*\)[^\[\];]{0,200}?\bque\s+(?:[^\[\];.]{0,200}?\s)?(?:revoga|revogam|revogou)$|[a-zà-ú)\]]\.\s+Revoga\s*$"
)
_MONTHS = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}
_DATE = r"(?P<day>\d{1,2})(?:\.?\s*[º°o])?\s+de\s+(?P<month>[A-Za-zçÇ]+)(?:\s*(?:de\s+)?(?P<year>1[89]\d\d|20\d\d))?"
# A data citada a seguir à ligação: ", de 19 de Junho [de 1998]", ", publicado no Diário da República, 1.ª série-B, de 28 de Setembro de 2002".
_CITED_DATE = re.compile(
    r"^\s*,?\s*(?:\([^)]{0,80}\)\s*,?\s*)?(?:publicad[oa]s?\s+no\s+Di[áa]rio\s+(?:da\s+Rep[úu]blica|do\s+Governo)[^,;]{0,40},\s*(?:[^,;]{0,25}s[ée]rie[^,;]{0,10},\s*)?(?:n\.?\s*º\s*\d+,\s*)?)?de\s+"
    + _DATE,
    re.IGNORECASE,
)
_RESPECTIVELY = re.compile(r"respectiv|respetiv", re.IGNORECASE)
_ANY_DATE = re.compile(r"\bde\s+" + _DATE, re.IGNORECASE)
_ENTITY = re.compile(
    r"^\s*,?\s*(?:de\s+\d{1,2}\s+de\s+\w+(?:\s+de\s+\d{4})?\s*,?\s*)?(?:,\s*)?(?:do|da|dos|das)\s+(?P<entity>"
    r"Banco\s+de\s+Portugal|CMVM|Comiss[ãa]o\s+do\s+Mercado\s+de\s+Valores\s+Mobili[áa]rios|Instituto\s+de\s+Seguros\s+de\s+Portugal|"
    r"Autoridade\s+de\s+Supervis[ãa]o\s+de\s+Seguros|Secretari[ao]\s+Regional[^,;.]{0,60}|Governo\s+Regional[^,;.]{0,30}|"
    r"Regi[ãa]o\s+Aut[óo]noma[^,;.]{0,30}|Assembleia\s+Legislativa[^,;.]{0,40}|Presid[êe]ncia\s+do\s+Governo\s+Regional)",
    re.IGNORECASE,
)


def _iso(day: str, month: str, year: str | None) -> str | None:
    number = _MONTHS.get(month.lower())
    if not number or not 1 <= int(day) <= 31:
        return None
    return f"{year}-{number:02d}-{int(day):02d}" if year else f"--{number:02d}-{int(day):02d}"


def _entity(after: str) -> str | None:
    match = _ENTITY.match(after)
    return re.sub(r"\s+", " ", match.group("entity")).strip() if match else None


def _cited_dates(masked: str, links: list[re.Match[str]]) -> dict[int, str]:
    """A data citada de cada ligação (índice -> data), lida a seguir à ligação; numa enumeração
    "As Portarias n.os [282/73] e [428/77], respectivamente de 13 de Abril e de 15 de Julho", pela ordem."""
    dates: dict[int, str] = {}
    pending: list[int] = []
    for index, link in enumerate(links):
        end = links[index + 1].start() if index + 1 < len(links) else len(masked)
        after = masked[link.end() : end]
        match = _CITED_DATE.match(after)
        if match:
            value = _iso(match.group("day"), match.group("month"), match.group("year"))
            if value:
                dates[index] = value
            pending = []
            continue
        pending.append(index)
        head = re.split(r"[;:]", after, maxsplit=1)[0]
        if _RESPECTIVELY.search(head) and len(pending) > 1:
            values = [_iso(m.group("day"), m.group("month"), m.group("year")) for m in _ANY_DATE.finditer(head)]
            if len(values) == len(pending) and all(values):
                dates.update(dict(zip(pending, values, strict=True)))
            pending = []
        elif not re.fullmatch(r"\s*(?:,|e|,\s*e)\s*", head):
            pending = []
    return dates


# ------------------------------------------------------------ relações do DRE

_LABEL_PARTIAL = re.compile(
    r"^revogad[oa]s?,?\s+(?:o|a|os|as)\s+(?!pel|partir)|parcialmente|na\s+parte|com\s+exce|exce[tp]|salvo|\bart\.|\bartigos?\b|\bn\.?\s*º|\bal[íi]n|"
    r"\bn[úu]meros?\b|anexo|ponto|quadro|mapa|§|\bnormas?\b|\binstru[cç]",
    re.IGNORECASE,
)
# O objeto da revogação é o próprio diploma ("Revogada, a partir de …, a presente portaria")…
_LABEL_SELF = re.compile(
    r"^revogad[oa]s?\b.{0,120}?\b(?:o|a)\s+presente\s+(?:diploma|decreto|lei|portaria|resolu[cç][ãa]o|regulamento|aviso|despacho|delibera[cç][ãa]o)\b",
    re.IGNORECASE,
)
# …ou outro, a que este deu a redação ou que aprovou ("o Dec Lei 139/2012, com a redação dada pelo presente").
_LABEL_OTHER = re.compile(
    r"\b(?:alterad[oa]s?|aprovad[oa]s?|com\s+a\s+reda[cç][ãa]o(?:\s+dada)?|na\s+reda[cç][ãa]o(?:\s+dada)?|na\s+vers[ãa]o\s+republicada)\s+(?:d[oa]|pel[oa])\s+presente\b",
    re.IGNORECASE,
)
_LABEL_CONDITIONAL = re.compile(
    r"mantid|transitoriamente|a\s+partir\s+da\s+entrada\s+em\s+vigor\s+d|com\s+a\s+entrada\s+em\s+vigor|ap[óo]s\s+a\s+publica|"
    r"at[ée]\s+(?:à|a)\s+(?:publica|entrada)",
    re.IGNORECASE,
)


def label_scope(relation_type: str, label: str | None) -> str | None:
    """Âmbito de uma relação `repealed_by` ou `repeals` pela etiqueta do DRE.

    `total`, `parcial`, `condicional` ou None (sem etiqueta ou etiqueta que não se percebe)."""
    text = re.sub(r"\s+", " ", label or "").strip()
    if not text:
        return None
    if _LABEL_CONDITIONAL.search(text):
        return "condicional"
    if relation_type == "repealed_by":
        if not re.match(r"^revogad[oa]s?\b", text, re.IGNORECASE):
            return None
        head = re.split(r"\bpel[oa]\(?a?\)?\b|\bpelos?\b|\bpelas?\b", text, maxsplit=1, flags=re.IGNORECASE)[0]
        # "Revogado … o Dec Lei 202/94, na redação do presente diploma": o revogado é outro
        # diploma (este só lhe deu a redação), salvo quando o objeto é "a presente portaria…".
        if not _LABEL_SELF.match(text) and _LABEL_OTHER.search(text):
            return "outro"
        return "parcial" if _LABEL_PARTIAL.search(head) else "total"
    if relation_type == "repeals":
        if not re.match(r"^revoga\b", text, re.IGNORECASE):
            return None
        head = re.sub(r"^revoga\s+", "", text, flags=re.IGNORECASE)
        if re.match(r"^(?:o|a|os|as)\s+(?:artigos?|art\.|n\.?\s*º|n\.os|al[íi]neas?|anexos?|pontos?|n[úu]meros?|cap[íi]tulos?|quadros?)", head, re.IGNORECASE):
            return "parcial"
        if re.match(r"^(?:o|a)\s+(?:lei|decreto|portaria|despacho|resolu|aviso|regulamento|delibera|dec\b|port\b)", head, re.IGNORECASE):
            return "parcial" if re.search(r"\bna\s+parte|parcialmente|com\s+exce|exce[tp]", head, re.IGNORECASE) else "total"
        return None
    return None


# ---------------------------------------------------------------------- proposta


def propose(
    *,
    status: str,
    text_repeals: list[Repeal],
    relations: list[dict[str, str | None]],
    incoming: list[dict[str, str | None]],
    end_date: str | None,
    end_rule: str | None,
    end_article: str | None,
    amended: bool,
    document_type: str | None,
    corrected_status: list[tuple[str, str]],
    text_quality: str,
    publication_date: str | None,
    today: str,
) -> Proposal:
    """Estado proposto para um diploma, a partir das provas.

    `relations`: as relações do próprio diploma (`type`, `target`, `label`);
    `incoming`: relações `repeals` de outros diplomas que o apontam (`source`, `label`);
    `corrected_status`: (id, estado) dos diplomas que uma declaração de retificação corrige."""
    evidence: list[Evidence] = []
    for repeal in text_repeals:
        status_value = "repealed" if repeal.scope == "total" else "partially_repealed"
        evidence.append(Evidence(status_value, f"norma revogatória: {repeal.source}#{repeal.article or 'texto'}", repeal.text))
    for relation in relations:
        if relation.get("type") != "repealed_by":
            continue
        scope = label_scope("repealed_by", relation.get("label"))
        status_value = {"total": "repealed", "parcial": "partially_repealed"}.get(scope or "", "unclear")
        evidence.append(Evidence(status_value, f"DRE repealed_by: {relation.get('target')}", relation.get("label") or "(sem etiqueta)"))
    for relation in incoming:
        scope = label_scope("repeals", relation.get("label"))
        status_value = {"total": "repealed", "parcial": "partially_repealed"}.get(scope or "", "unclear")
        evidence.append(Evidence(status_value, f"DRE repeals de {relation.get('source')}", relation.get("label") or "(sem etiqueta)"))
    if end_date and end_date < today and not amended:
        evidence.append(Evidence("not_in_force", f"cláusula de vigência: {end_article or 'texto'}", end_rule or end_date))

    if status != "unknown":
        return Proposal(None, "estado_do_dre", evidence)
    totals = [item for item in evidence if item.status == "repealed"]
    partial_sources = {_repealer(item) for item in evidence if item.status == "partially_repealed"}
    if any(_repealer(item) in partial_sources for item in totals):
        # O mesmo revogador dá uma revogação total numa prova e parcial noutra.
        return Proposal(None, "conflito", evidence)
    if totals:
        return Proposal("repealed", "revogado", evidence)
    if any(item.status == "not_in_force" for item in evidence):
        return Proposal("not_in_force", "caducado", evidence)
    if any(item.status == "partially_repealed" for item in evidence):
        return Proposal(None, "revogacao_parcial", evidence)
    if any(item.status == "unclear" for item in evidence):
        return Proposal(None, "revogacao_por_confirmar", evidence)
    if document_type == "declaracao-retificacao" and corrected_status:
        target, target_status = corrected_status[0]
        evidence.append(Evidence(target_status, f"retifica {target}", "uma declaração de retificação não tem vigência própria"))
        return Proposal(None, "retificacao", evidence)
    if text_quality == "pdf" and (publication_date or "9999") < "1960-01-01":
        return Proposal(None, "historico_so_pdf", evidence)
    return Proposal(None, "sem_prova", evidence)


_RECORD_ID = re.compile(r"pt:dre:\d+:por")


def _repealer(item: Evidence) -> str | None:
    match = _RECORD_ID.search(item.provenance)
    return match.group() if match else None


# ------------------------------------------------- identidade do diploma ligado

# A data citada ("Portaria n.º 216/85, de 15 de Maio") é a da assinatura ou a da publicação: fica
# entre 0 e `IDENTITY_DAYS` dias antes da publicação do diploma para que a ligação aponta. Medido nos
# 113 casos verificados em 2026-11-13: nos certos, no máximo 12 dias; nos errados, 29 e 33 (a "Portaria
# n.º 690/73, de 7 de Setembro" ligada à de 10 de Outubro).
IDENTITY_DAYS = 20


def _number_key(number: str) -> tuple[str, str]:
    """(número, ano em dois dígitos): "216/85" e "216/1985" são o mesmo."""
    parts = number.lower().replace(" ", "").split("/")
    head = parts[0]
    year = next((part for part in parts[1:] if part.isdigit()), "")
    return head, year[-2:]


def _days_before(cited: str, publication: str) -> int | None:
    """Dias da data citada até à publicação; sem ano, o ano que a põe mais perto (antes) da publicação."""
    try:
        published = _date.fromisoformat(publication)
    except ValueError:
        return None
    if not cited.startswith("--"):
        try:
            return (published - _date.fromisoformat(cited)).days
        except ValueError:
            return None
    month, day = int(cited[2:4]), int(cited[5:7])
    best: int | None = None
    for year in (published.year, published.year - 1):
        try:
            delta = (published - _date(year, month, day)).days
        except ValueError:
            continue
        if delta >= 0 and (best is None or delta < best):
            best = delta
    if best is None:
        try:
            best = (published - _date(published.year, month, day)).days
        except ValueError:
            return None
    return best


def identity(repeal: Repeal, target: dict[str, object] | None) -> tuple[str, list[str]]:
    """Se a ligação do DRE aponta para o diploma que o texto revoga.

    `confirmada` (o número do rótulo e a data citada batem com o alvo), `so_numero` (o número bate,
    sem data citada) ou `suspeita`, com os motivos: `numero` (o rótulo tem outro número), `sem_numero`,
    `data` (a data citada não é a do alvo: a "Portaria n.º 216/85, de 15 de Maio" ligada à de 18 de
    Abril) e `entidade` (o texto nomeia uma entidade, "do Banco de Portugal", que não emitiu o alvo)."""
    if target is None:
        return "suspeita", ["alvo_fora_do_acervo"]
    reasons: list[str] = []
    official = str(target.get("official_number") or "")
    cited = _number_of(repeal.label)
    if not cited or not official:
        reasons.append("sem_numero")
    elif _number_key(cited) != _number_key(official):
        reasons.append("numero")
    dated = False
    if repeal.cited_date and target.get("publication_date"):
        delta = _days_before(repeal.cited_date, str(target["publication_date"]))
        if delta is not None:
            dated = True
            if not 0 <= delta <= IDENTITY_DAYS:
                reasons.append("data")
    if repeal.cited_entity:
        authority = " ".join(str(item) for item in (target.get("issuing_authority") or []))
        haystack = f"{authority} {target.get('title') or ''} {target.get('summary') or ''}".lower()
        entity = repeal.cited_entity.lower()
        regional = any(word in entity for word in ("regional", "região", "regiao", "assembleia legislativa"))
        if regional:
            if target.get("jurisdiction") != "regional":
                reasons.append("entidade")
        elif not any(word in haystack for word in _entity_words(entity)):
            reasons.append("entidade")
    if reasons:
        return "suspeita", reasons
    return ("confirmada" if dated else "so_numero"), []


def _entity_words(entity: str) -> list[str]:
    if "banco de portugal" in entity:
        return ["banco de portugal"]
    if "cmvm" in entity or "valores mobili" in entity:
        return ["cmvm", "valores mobili"]
    if "seguros" in entity:
        return ["seguros"]
    return [entity]
