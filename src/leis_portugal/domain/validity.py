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
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

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

    def to_dict(self) -> dict[str, str | None]:
        return {"target": self.target, "scope": self.scope, "source": self.source, "article": self.article, "text": self.text}


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
    r"na\s+data\s+(?:da|de)\s+entrada\s+em\s+vigor|produz(?:indo)?\s+efeitos\s+(?:a\s+partir|em|no|na)|n[ãa]o\s+(?:é|são)\s+revogad",
    re.IGNORECASE,
)
_LINK_URL = re.compile(r"\]\([^)]*\)")
_CLAUSE_PARTIAL = re.compile(
    r"\bna\s+parte\b|\bnas\s+partes\b|com\s+exce|\bexce[tp]to\b|\bsalvo\b|em\s+tudo\s+o\s+que|ressalvad|à\s+exce|"
    r"sem\s+preju[íi]zo|\bparcialmente\b|\bapenas\s+(?:o|a|os|as|n[ao])\b|no\s+que\s+(?:respeita|se\s+refere|diz\s+respeito)",
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
        for paragraph in _unquoted_paragraphs(block):
            has_verb = bool(_REPEAL_VERB.search(paragraph))
            in_context = epigraph or has_verb or (listing and _LIST_ITEM.match(paragraph))
            if has_verb:
                listing = paragraph.rstrip().endswith(":")
            elif not (listing and _LIST_ITEM.match(paragraph)):
                listing = listing and epigraph
            if not in_context:
                continue
            for repeal in _paragraph_repeals(paragraph, source=source, article=anchor):
                key = (repeal.target, repeal.scope)
                found.setdefault(key, repeal)
    # Total e parcial do mesmo diploma no mesmo texto: fica a total só se não houver dúvida.
    result: list[Repeal] = []
    for (target, scope), repeal in found.items():
        if scope == "parcial" and (target, "total") in found:
            continue
        result.append(repeal)
    return result


def _paragraph_repeals(paragraph: str, *, source: str, article: str | None) -> list[Repeal]:
    repeals: list[Repeal] = []
    links = list(_DRE_LINK.finditer(paragraph))
    # Os URLs das ligações ficam tapados (mesmo comprimento): o ":" de "https:" não separa itens.
    masked = _LINK_URL.sub(lambda match: "](" + "x" * (len(match.group()) - 3) + ")", paragraph)
    verb = _REPEAL_VERB.search(masked)
    start = verb.end() if verb else 0
    context_item: int | None = None
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
        if scope == "total" and _CLAUSE_PARTIAL.search(_LINK_URL.sub("]", clause)):
            # "O Decreto-Lei n.º 350/88, de 30 de setembro, com excepção dos artigos 5.º e 6.º"
            scope = "parcial"
        if scope is None:
            continue
        target = pt_record_id(link.group("id"))
        if target == source:
            continue
        repeals.append(Repeal(target, scope, source, article, re.sub(r"\]\([^)]*\)", "]", clause).strip()[:300]))
    return repeals


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
