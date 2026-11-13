"""Estrutura por artigo, entrada em vigor e vigência: relatório de cobertura.

Lê os registos portugueses e regionais e, sem os alterar, mede:

- quantos diplomas ficam com artigos identificados (e com id estável por artigo);
- quantas datas de entrada em vigor se calculam e quantas ficam só com a regra;
- quantos diplomas de vigência desconhecida ficam com um estado proposto, e com que prova.

Valida também o parser contra os consolidados do DRE, cujos `.versoes.json` têm os
artigos separados em fragmentos: o número de artigos e as epígrafes têm de bater.
"""

from __future__ import annotations

import json
import os
import random
import re
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from leis_portugal.domain.articles import Article, number_slug, parse_articles
from leis_portugal.domain.entry_into_force import extract
from leis_portugal.domain.history import render_version, version_at
from leis_portugal.domain.record import Relationship
from leis_portugal.domain.validity import Repeal, identity, label_scope, propose, repeals_in
from leis_portugal.infrastructure.markdown import read_markdown_record, write_if_changed
from leis_portugal.infrastructure.markdown import render_markdown as render_record
from leis_portugal.infrastructure.repository import PORTUGUESE_SCOPES, Acervo
from leis_portugal.services.export import text_quality
from leis_portugal.sources.dre.consolidated import ARTICLE_TYPES


Progress = Callable[[str], None]
_RELATION_TYPES = {"repealed_by", "repeals", "corrects", "amended_by"}
# Tipo do fragmento de anexo nos consolidados do DRE.
ANNEX_FRAGMENT = 14


def _silent(_message: str) -> None:
    return None


# --------------------------------------------------------------------- por registo


def unit_kind(articles: list[Article]) -> str:
    """`artigos` (artigos, bases ou cláusulas no diploma), `numeros` (só números do
    dispositivo), `so_anexos` (artigos só nos anexos) ou `nenhum`."""
    own = {article.kind for article in articles if article.part == ""}
    if own - {"numero"}:
        return "artigos"
    if own:
        return "numeros"
    return "so_anexos" if articles else "nenhum"


def analyse(path: str, root: str) -> dict[str, Any] | None:
    """Resumo de um registo: artigos, entrada em vigor, revogações e relações."""
    try:
        metadata, body = read_markdown_record(path)
    except (OSError, ValueError):
        return None
    record_id = metadata.get("id")
    quality = text_quality(metadata, body)
    publication = metadata.get("publication") or {}
    articles = parse_articles(body) if quality == "texto" else []
    anchors = [article.anchor for article in articles]
    eif = (
        extract(
            articles, body, publication=metadata.get("publication_date"), signature=metadata.get("official_date"),
            document_type=metadata.get("document_type"), series=publication.get("series"), jurisdiction=metadata.get("jurisdiction"),
        )
        if quality == "texto"
        else None
    )
    repeals = repeals_in(articles, body, source=record_id) if quality == "texto" and record_id else []
    relations = [
        {"type": item.get("type"), "target": item.get("target"), "label": item.get("label"), "date": item.get("date")}
        for item in metadata.get("relationships") or []
        if item.get("type") in _RELATION_TYPES
    ]
    return {
        "id": record_id,
        "path": os.path.relpath(path, root),
        # Identificação, para confirmar que uma ligação de uma norma revogatória aponta para este diploma.
        "official_number": metadata.get("official_number"),
        "title": metadata.get("title"),
        "summary": (metadata.get("summary") or "")[:400],
        "issuing_authority": list(metadata.get("issuing_authority") or []),
        "jurisdiction": metadata.get("jurisdiction"),
        "document_type": metadata.get("document_type"),
        "series": publication.get("series"),
        "publication_date": metadata.get("publication_date"),
        # Um estado gravado por este comando (com `legal_status_basis`) volta a avaliar-se
        # como o que estava antes (desconhecido, ou o do DRE numa prova manual): se a prova
        # deixar de existir, a escrita retira-o.
        "legal_status": (
            (metadata["legal_status_basis"].get("dre_status") or "unknown")
            if metadata.get("legal_status_basis")
            else metadata.get("legal_status") or "unknown"
        ),
        "proven_status": bool(metadata.get("legal_status_basis")),
        "version_kind": (metadata.get("version") or {}).get("kind"),
        "text_quality": quality,
        "units": unit_kind(articles),
        "article_count": sum(1 for article in articles if article.kind != "numero"),
        "point_count": sum(1 for article in articles if article.kind == "numero"),
        "annex_parts": len({article.part_slug for article in articles if article.part_slug}),
        "repeated_numbers": sum(1 for article in articles if article.repeat),
        "unique_ids": len(set(anchors)) == len(anchors),
        "methods": sorted({article.method for article in articles}),
        "entry_into_force": eif.to_dict() if eif else None,
        "partial_clauses": sum(1 for clause in eif.clauses if clause.scope == "parcial") if eif else 0,
        "repeals": [repeal.to_dict() for repeal in repeals],
        "relations": relations,
    }


def _analyse_pair(item: tuple[str, str]) -> dict[str, Any] | None:
    return analyse(*item)


def read_rows(acervo: Acervo, *, workers: int = 1, limit: int | None = None, progress: Progress = _silent) -> list[dict[str, Any]]:
    paths = [str(path) for path in acervo.paths(PORTUGUESE_SCOPES)]
    if limit:
        paths = paths[:limit]
    root = str(acervo.root)
    items = [(path, root) for path in paths]
    rows: list[dict[str, Any]] = []
    iterator: Iterable[dict[str, Any] | None]
    if workers <= 1:
        iterator = map(_analyse_pair, items)
        rows = _collect(iterator, len(items), progress)
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = _collect(pool.map(_analyse_pair, items, chunksize=256), len(items), progress)
    return rows


def _collect(iterator: Iterable[dict[str, Any] | None], total: int, progress: Progress) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(iterator, start=1):
        if row:
            rows.append(row)
        if index % 20000 == 0:
            progress(f"[{index}/{total}] registos lidos")
    return rows


# ---------------------------------------------------------------------- agregação


@dataclass
class StructureReport:
    summary: dict[str, Any] = field(default_factory=dict)
    proposals: list[dict[str, Any]] = field(default_factory=list)
    validation: dict[str, Any] = field(default_factory=dict)
    rows: list[dict[str, Any]] = field(default_factory=list)
    manual: list[ManualProof] = field(default_factory=list)
    # Provas de revogação total lidas no texto de diplomas que o DRE dá em vigor, com os sinais e o segmento.
    against_dre: list[dict[str, Any]] = field(default_factory=list)


def _status_group(status: str) -> str:
    return {"in_force": "em_vigor", "partially_in_force": "em_vigor"}.get(status, status)


def competent(source: dict[str, Any], target: dict[str, Any] | None) -> bool:
    """Se o diploma `source` pode revogar `target` (sem o alvo no acervo, não se sabe: conta).

    Um órgão regional não revoga atos do Estado. Quando um diploma regional "revoga" um diploma
    nacional, a ligação do DRE aponta quase sempre para outro diploma com o mesmo número (a
    "Portaria n.º 116/98, de 19 de Junho" da Madeira ligada à Portaria n.º 116/98 nacional), ou o
    texto é uma proposta de lei aprovada por resolução da assembleia legislativa regional."""
    if target is None:
        return True
    return source.get("jurisdiction") != "regional" or target.get("jurisdiction") == "regional"


# Uma regra de efeitos sem data que depende de outro ato ("com a entrada em vigor do decreto
# regulamentar regional…"); as retroativas ("desde a data da sua assinatura", "imediatos") não diferem nada.
_DEFERRED_EFFECTS = re.compile(
    r"(?:entrada\s+em\s+vigor|publica[çc][ãa]o|aprova[çc][ãa]o|in[íi]cio\s+de\s+(?:vig[êe]ncia|funcionamento))\s+d(?:[oa]s?)\s+(?!presente|sua\b)|"
    r"regulamenta[çc][ãa]o|\bquando\b|\bap[óo]s\s+(?:a|o)\s+(?!data\s+da\s+sua|sua)",
    re.IGNORECASE,
)


def plausible(source: dict[str, Any], target: dict[str, Any] | None, *, today: str) -> bool:
    """Se uma revogação lida no texto pode ser do diploma para que a ligação aponta, e já produziu efeitos:
    o revogador tem competência, não é anterior ao revogado (uma "revogação" num diploma mais antigo é
    uma nota editorial), já entrou em vigor (um decreto-lei de 2026 que só vigora em 2027 ainda não revogou)
    e já produz efeitos (sem uma regra de efeitos por datar nem uma data de efeitos futura)."""
    if not competent(source, target):
        return False
    eif = source.get("entry_into_force") or {}
    if eif.get("date") and eif["date"] > today:
        return False
    # Efeitos diferidos: "produz efeitos na data de entrada em vigor do decreto regulamentar regional…"
    # (só a regra, sem data) ou uma data de efeitos ainda por chegar.
    if eif.get("effects_rule") and not eif.get("effects_date") and _DEFERRED_EFFECTS.search(eif["effects_rule"]):
        return False
    if eif.get("effects_date") and eif["effects_date"] > today:
        return False
    return target is None or (source.get("publication_date") or "9999") >= (target.get("publication_date") or "")


# Segmentos das provas de revogação total contra o `in_force` do DRE (ver `proof_segment`). Só os
# segmentos com precisão medida de pelo menos `AGAINST_DRE_SAMPLE["limiar"]` entram como base automática.
SEGMENTS = {
    "a": "identidade confirmada (número e data), nacional, sem sinais contra",
    "b": "só o número confirmado (sem data citada), nacional, sem sinais contra",
    "c": "algum sinal contra (identidade suspeita, série, alteração posterior, conflito no DRE, repristinação, retificação) ou regional",
}
APPROVED_SEGMENTS: frozenset[str] = frozenset()


def proof_signals(source: dict[str, Any], repeal: Repeal, target: dict[str, Any] | None, by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Os sinais de uma revogação total lida no texto: a identidade do diploma ligado e o que a contraria."""
    state, signals = identity(repeal, target)
    signals = list(signals)
    if source.get("document_type") == "declaracao-retificacao":
        # Uma declaração de retificação corrige (ou republica) outro diploma: não revoga.
        signals.append("retificacao")
    if _IN_CONTRARY.search(repeal.text):
        # "Fica revogada toda a legislação em contrário, nomeadamente o…": pode ficar pela incompatibilidade.
        signals.append("legislacao_em_contrario")
    cited_series = _cited_series(repeal.text)
    if target and cited_series and cited_series != _series_group(target.get("series"), target.get("jurisdiction")):
        # "A Portaria n.º 857/2004, publicada na 2.ª série", ou "no Jornal Oficial dos Açores", ligada a um diploma da 1.ª série.
        signals.append("serie")
    if target and any(_REPRISTINATED.search(relation.get("label") or "") for relation in target.get("relations") or []):
        # "Repõe em vigor": o revogador foi revogado e o revogado repristinado (DL 94/2007 pela Lei n.º 7-A/2016).
        signals.append("repristinado")
    regulator = _regulator(" ".join([*(source.get("issuing_authority") or []), source.get("title") or ""]))
    if target and regulator and _regulator(" ".join([*(target.get("issuing_authority") or []), target.get("title") or ""])) != regulator:
        # Um regulador (Banco de Portugal, CMVM, seguros) só revoga atos seus: o "Aviso n.º 12/2001" de um
        # aviso do Banco de Portugal não é o aviso do Ministério dos Negócios Estrangeiros com o mesmo número.
        signals.append("entidade")
    published = source.get("publication_date") or ""
    if target:
        for relation in target.get("relations") or []:
            other = relation.get("target")
            if relation.get("type") == "amended_by" and other != source.get("id"):
                when = relation.get("date") or (by_id.get(other) or {}).get("publication_date") or ""
                if published and when > published:
                    # Um diploma revogado não se altera: o DRE regista uma alteração posterior ao revogador.
                    signals.append("alteracao_posterior")
                    break
        for relation in target.get("relations") or []:
            if relation.get("type") != "repealed_by":
                continue
            scope = label_scope("repealed_by", relation.get("label"))
            if relation.get("target") != source.get("id") or scope in ("parcial", "condicional", "outro"):
                signals.append("conflito_dre")
                break
    for relation in source.get("relations") or []:
        if relation.get("type") == "repeals" and relation.get("target") == repeal.target:
            if label_scope("repeals", relation.get("label")) in ("parcial", "condicional"):
                signals.append("conflito_dre")
            break
    national = source.get("jurisdiction") == "portugal" and (target or {}).get("jurisdiction") == "portugal"
    return {"identidade": state, "sinais": sorted(set(signals)), "nacional": national}


_CITED_SERIES = re.compile(r"(?P<two>\b2\.?\s*[ªa]\s*s[ée]rie|\(2\.ª\s+s[ée]rie\)|II\s+s[ée]rie)|(?P<one>\b1\.?\s*[ªa]\s*s[ée]rie)|(?P<regional>Jornal\s+Oficial)", re.IGNORECASE)


def _cited_series(text: str) -> str | None:
    match = _CITED_SERIES.search(text)
    if not match:
        return None
    if match.group("regional"):
        return "regional"
    return "II" if match.group("two") else "I"


def _series_group(series: str | None, jurisdiction: str | None) -> str | None:
    if jurisdiction == "regional":
        return "regional"
    return "II" if (series or "").upper().startswith("II") else "I"


_REPRISTINATED = re.compile(r"rep[õo]e\s+em\s+vigor|repristin", re.IGNORECASE)
_IN_CONTRARY = re.compile(r"em\s+contr[áa]rio", re.IGNORECASE)
_REGULATORS = {
    "banco de portugal": "bdp", "valores mobili": "cmvm", "cmvm": "cmvm", "seguros de portugal": "seguros",
    "supervisão de seguros": "seguros", "supervisao de seguros": "seguros",
}


def _regulator(text: str) -> str | None:
    lowered = text.lower()
    return next((value for key, value in _REGULATORS.items() if key in lowered), None)


def proof_segment(signals: dict[str, Any]) -> str:
    if signals["sinais"] or not signals["nacional"]:
        return "c"
    return "a" if signals["identidade"] == "confirmada" else "b"


AGAINST_DRE_CATEGORY = "revogado_contra_dre"
AGAINST_DRE_SOURCE = "norma_revogatoria_contra_dre"


def _against_dre(row: dict[str, Any], repeals: list[Repeal], proposal: Any, by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """As provas de revogação total de um diploma `in_force` no DRE, com o segmento de cada uma, e a
    proposta `repealed` quando uma prova é de um segmento aprovado e nenhuma outra a contraria
    (revogação parcial ou condicional, conflito)."""
    proofs: list[dict[str, Any]] = []
    for repeal in repeals:
        if repeal.scope != "total":
            continue
        source = by_id.get(repeal.source) or {}
        signals = proof_signals(source, repeal, row, by_id)
        proofs.append({
            "alvo": row["id"], "revogador": repeal.source, "artigo": repeal.article, "excerto": repeal.text,
            "rotulo": repeal.label, "data_citada": repeal.cited_date, "entidade_citada": repeal.cited_entity,
            **signals, "segmento": proof_segment(signals),
        })
    approved = [item for item in proofs if item["segmento"] in APPROVED_SEGMENTS]
    against = any(item.status in ("partially_repealed", "unclear") for item in proposal.evidence)
    if not approved or against or any(item["segmento"] not in APPROVED_SEGMENTS for item in proofs):
        return {"provas": proofs, "proposta": None}
    chosen = {f"norma revogatória: {item['revogador']}#{item['artigo'] or 'texto'}" for item in approved}
    evidence = [item.to_dict() for item in proposal.evidence if item.provenance in chosen]
    segment = min(item["segmento"] for item in approved)
    return {
        "provas": proofs,
        "proposta": {"status": "repealed", "category": AGAINST_DRE_CATEGORY, "dre_status": "in_force", "segmento": segment, "evidence": evidence},
    }


def aggregate(rows: list[dict[str, Any]], *, today: str) -> StructureReport:
    report = StructureReport()
    by_id = {row["id"]: row for row in rows if row.get("id")}

    # ---- artigos
    with_text = [row for row in rows if row["text_quality"] == "texto"]
    units = Counter(row["units"] for row in with_text)
    in_force_text = [row for row in with_text if row["legal_status"] in ("in_force", "partially_in_force")]
    articles = {
        "registos": len(rows),
        "com_texto": len(with_text),
        "por_unidade": dict(sorted(units.items())),
        "com_artigos": units["artigos"],
        "com_artigos_ou_numeros": units["artigos"] + units["numeros"],
        "em_vigor_com_texto": len(in_force_text),
        "em_vigor_com_artigos": sum(1 for row in in_force_text if row["units"] == "artigos"),
        "em_vigor_com_artigos_ou_numeros": sum(1 for row in in_force_text if row["units"] in ("artigos", "numeros")),
        "artigos_identificados": sum(row["article_count"] for row in with_text),
        "numeros_identificados": sum(row["point_count"] for row in with_text),
        "com_anexos": sum(1 for row in with_text if row["annex_parts"]),
        "com_numeracao_repetida": sum(1 for row in with_text if row["repeated_numbers"]),
        "ids_duplicados": sum(1 for row in with_text if not row["unique_ids"]),
        "so_texto_corrido": sum(1 for row in with_text if row["methods"] == ["texto"]),
        "com_titulos": sum(1 for row in with_text if "titulo" in row["methods"]),
        "artigos_antes": sum(1 for row in with_text if "titulo" in row["methods"] and row["units"] == "artigos"),
    }

    # ---- entrada em vigor
    eif_rows = [row for row in with_text if row["entry_into_force"]]
    methods = Counter()
    for row in eif_rows:
        eif = row["entry_into_force"]
        if eif["method"] == "clausula":
            methods["clausula_com_data" if eif["date"] else "clausula_so_regra"] += 1
        else:
            methods[eif["method"]] += 1
    rules = Counter(
        re.sub(r"\d+", "N", row["entry_into_force"]["rule"].lower())[:90]
        for row in eif_rows
        if row["entry_into_force"]["method"] == "clausula" and not row["entry_into_force"]["date"]
    )
    by_series = defaultdict(Counter)
    for row in eif_rows:
        eif = row["entry_into_force"]
        key = eif["method"] if eif["method"] != "clausula" else ("clausula_com_data" if eif["date"] else "clausula_so_regra")
        by_series[f"{row['jurisdiction']} / série {row['series'] or '?'}"][key] += 1
    entry = {
        "com_texto": len(eif_rows),
        "por_metodo": dict(sorted(methods.items())),
        "calculadas_do_texto": methods["clausula_com_data"],
        "so_regra": methods["clausula_so_regra"],
        "supletivas": methods["supletiva"],
        "sem_clausula": methods["sem_clausula"],
        "com_data_de_efeitos": sum(1 for row in eif_rows if row["entry_into_force"]["effects_date"]),
        "com_regra_de_efeitos_sem_data": sum(
            1 for row in eif_rows if row["entry_into_force"]["effects_rule"] and not row["entry_into_force"]["effects_date"]
        ),
        "com_fim_de_vigencia": sum(1 for row in eif_rows if row["entry_into_force"]["end_rule"]),
        "com_clausulas_parciais": sum(1 for row in eif_rows if row["partial_clauses"]),
        "regras_mais_frequentes_sem_data": rules.most_common(15),
        "por_jurisdicao_e_serie": {key: dict(sorted(value.items())) for key, value in sorted(by_series.items())},
    }

    # ---- vigência
    text_repeals: dict[str, list[Repeal]] = defaultdict(list)
    for row in rows:
        for item in row["repeals"]:
            if plausible(row, by_id.get(item["target"]), today=today):
                text_repeals[item["target"]].append(Repeal(**item))
    incoming: dict[str, list[dict[str, str | None]]] = defaultdict(list)
    for row in rows:
        for relation in row["relations"]:
            if relation["type"] == "repeals" and relation["target"] in by_id:
                incoming[relation["target"]].append({"source": row["id"], "label": relation["label"]})

    categories = Counter()
    proposed = Counter()
    agreement = Counter()
    # Diplomas que o DRE dá em vigor e que uma norma revogatória de outro diploma revoga por inteiro.
    against_dre: set[str] = set()
    against_dre_proofs = 0
    segments: Counter[str] = Counter()
    segments_by_type: Counter[tuple[str, str]] = Counter()
    proposed_against_dre = 0
    for row in rows:
        relations = row["relations"]
        eif = row["entry_into_force"] or {}
        corrected = [
            (relation["target"], by_id[relation["target"]]["legal_status"])
            for relation in relations
            if relation["type"] == "corrects" and relation["target"] in by_id
        ]
        proposal = propose(
            status=row["legal_status"],
            text_repeals=text_repeals.get(row["id"], []),
            relations=relations,
            incoming=incoming.get(row["id"], []),
            end_date=eif.get("end_date"),
            end_rule=eif.get("end_rule"),
            end_article=eif.get("article"),
            amended=any(relation["type"] == "amended_by" for relation in relations),
            document_type=row["document_type"],
            corrected_status=corrected,
            text_quality=row["text_quality"],
            publication_date=row["publication_date"],
            today=today,
        )
        if row["legal_status"] != "unknown":
            # Precisão: as mesmas provas nos diplomas cujo estado o DRE conhece.
            totals = [item for item in proposal.evidence if item.status == "repealed"]
            for item in totals:
                source = "texto" if item.provenance.startswith("norma revogatória") else "relacao"
                agreement[(source, _status_group(row["legal_status"]))] += 1
                if source == "texto" and row["legal_status"] == "in_force":
                    against_dre.add(row["id"])
                    against_dre_proofs += 1
            if row["legal_status"] == "in_force":
                against = _against_dre(row, text_repeals.get(row["id"], []), proposal, by_id)
                for item in against["provas"]:
                    segments[item["segmento"]] += 1
                    segments_by_type[(item["segmento"], row["document_type"])] += 1
                    report.against_dre.append(item)
                if against["proposta"]:
                    report.proposals.append({"id": row["id"], "path": row["path"], **against["proposta"]})
                    proposed_against_dre += 1
            continue
        categories[proposal.category] += 1
        if proposal.status:
            proposed[proposal.status] += 1
        if proposal.evidence or proposal.category == "retificacao":
            report.proposals.append({"id": row["id"], "path": row["path"], **proposal.to_dict()})

    unknown = sum(categories.values())
    precision: dict[str, Any] = {}
    for source in ("texto", "relacao"):
        counts = {group: agreement[(source, group)] for group in ("repealed", "not_in_force", "em_vigor")}
        total = sum(counts.values())
        precision[source] = {
            **counts,
            "concordam": counts["repealed"] + counts["not_in_force"],
            "total": total,
            "taxa": round((counts["repealed"] + counts["not_in_force"]) / total, 4) if total else None,
        }
    validity = {
        "desconhecidos": unknown,
        "por_categoria": dict(sorted(categories.items())),
        "estado_proposto": dict(sorted(proposed.items())),
        "resolvidos": sum(proposed.values()),
        "revogacoes_lidas_no_texto": sum(len(items) for items in text_repeals.values()),
        "diplomas_revogados_no_texto": len(text_repeals),
        "precisao_nos_estados_conhecidos": precision,
        "texto_contra_dre": {
            "diplomas": len(against_dre),
            "provas": against_dre_proofs,
            "por_segmento": {key: segments[key] for key in SEGMENTS},
            "por_segmento_e_tipo": {
                key: dict(sorted((kind, count) for (segment, kind), count in segments_by_type.items() if segment == key))
                for key in SEGMENTS
            },
            "segmentos_aplicados": sorted(APPROVED_SEGMENTS),
            "revogados_automaticamente": proposed_against_dre,
            "amostra_verificada": AGAINST_DRE_SAMPLE,
        },
    }
    report.summary = {"gerado_em": today, "artigos": articles, "entrada_em_vigor": entry, "vigencia": validity}
    return report


# Verificação às cegas das revogações totais lidas no texto de diplomas que o DRE dá em vigor: os
# verificadores leram a norma inteira do revogador e as transitórias, confirmaram a identidade do alvo
# pelo front matter e responderam se o revoga por inteiro, de imediato e sem condição. Lista e
# veredictos em `reports/vigencia-texto-contra-dre.jsonl`.
# - `primeira` (2026-11-13, seed 20261113, por tipo): a regra de então; serviu para afinar a de hoje.
# - `afinacao`: a regra de hoje nesses 113 casos, por segmento (otimista: afinada neles).
# - `segunda` (seed 20261114, só casos nunca verificados, por segmento × tipo): 10 verificadores Sonnet;
#   auditoria (Opus) de todos os não e de 20 sim, cujo veredicto prevalece; precisão ponderada pelo
#   tamanho de cada estrato na população, com o intervalo de Wilson (n efetivo de Kish).
# - `depois_da_segunda`: a regra final (série citada, repristinação, "à data da entrada em vigor das
#   portarias…", juntados depois de medir) na mesma amostra: otimista.
# Um segmento só se aplica sem prova manual com precisão ponderada >= `limiar`; nenhum chegou.
AGAINST_DRE_SAMPLE = {
    "limiar": 0.98,
    "primeira": {"data": "2026-11-13", "amostra": 113, "certos": 78, "errados": 33, "duvidas": 2},
    "afinacao": {
        "a": {"amostra": 54, "certos": 54}, "b": {"amostra": 9, "certos": 9}, "c": {"amostra": 23, "certos": 14},
        "fora": {"amostra": 27, "certos": 1, "nota": "o certo cortado: os mapas anexos ao revogado ficam em vigor noutro artigo"},
    },
    "segunda": {
        "data": "2026-11-14", "seed": 20261114, "amostra": 150,
        "auditoria": {"casos": 45, "concordam": 43},
        "por_segmento": {
            "a": {"amostra": 95, "certos": 89, "ponderada": 0.936, "wilson_95": [0.867, 0.970]},
            "b": {"amostra": 29, "certos": 22, "ponderada": 0.759, "wilson_95": [0.579, 0.878]},
            "c": {"amostra": 26, "certos": 16, "ponderada": 0.614, "wilson_95": [0.416, 0.780]},
        },
    },
    "depois_da_segunda": {"a": {"amostra": 92, "certos": 89}, "b": {"amostra": 26, "certos": 22}, "c": {"amostra": 31, "certos": 16}},
}


# ------------------------------------------------------------- validação (DRE)


def _expected_articles(history: dict[str, Any], version: dict[str, Any]) -> list[tuple[str, str, str]]:
    """(parte, número, epígrafe) dos artigos de uma versão, pelos fragmentos do DRE."""
    fragments = history["fragments"]
    expected: list[tuple[str, str, str]] = []
    part = ""
    for key in version["fragments"]:
        fragment = fragments[key]
        if fragment.get("type") == ANNEX_FRAGMENT:
            part = fragment.get("heading") or "anexo"
        if fragment.get("type") in ARTICLE_TYPES and fragment.get("markdown"):
            heading = fragment.get("heading") or ""
            title, _, epigraph = heading.partition(" — ")
            number = re.sub(r"^(?:Artigo|Base)\s+", "", title.strip())
            expected.append((part, number, epigraph.strip()))
    return expected


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def compare(parsed: list[Article], expected: list[tuple[str, str, str]]) -> dict[str, Any]:
    # O DRE trata como artigos também os números com título (`###### 1.º`).
    found = [
        (article.part, article.number, article.heading)
        for article in parsed
        if article.kind in ("artigo", "base") or (article.kind == "numero" and article.method == "titulo")
    ]
    same_count = len(found) == len(expected)
    pairs = list(zip(found, expected, strict=False))
    numbers = sum(1 for (_, number, _), (_, other, _) in pairs if number_slug(number) == number_slug(other))
    headings = sum(1 for (_, _, heading), (_, _, other) in pairs if _normalize(heading) == _normalize(other))
    parts_found = len({part for part, _, _ in found})
    parts_expected = len({part for part, _, _ in expected})
    first = next(
        (
            {"posicao": index, "parser": list(a), "dre": list(b)}
            for index, (a, b) in enumerate(pairs)
            if number_slug(a[1]) != number_slug(b[1]) or _normalize(a[2]) != _normalize(b[2])
        ),
        None,
    )
    return {
        "artigos_parser": len(found),
        "artigos_dre": len(expected),
        "mesmo_numero_de_artigos": same_count,
        "numeros_iguais": numbers,
        "epigrafes_iguais": headings,
        "tudo_igual": same_count and numbers == len(expected) and headings == len(expected),
        "partes_iguais": parts_found == parts_expected,
        "primeira_diferenca": first,
    }


def validate_consolidated(acervo: Acervo, rows: list[dict[str, Any]], *, sample: int, seed: int = 20261027) -> dict[str, Any]:
    """Compara o parser com os fragmentos do DRE numa amostra de consolidados portugueses."""
    candidates = sorted(row["path"] for row in rows if row["version_kind"] == "consolidated" and row["jurisdiction"] != "european_union")
    chosen = random.Random(seed).sample(candidates, min(sample, len(candidates)))
    results: list[dict[str, Any]] = []
    for relative in sorted(chosen):
        path = acervo.root / relative
        history = acervo.read_history(path)
        if not history or not history.get("versions"):
            continue
        metadata, body = read_markdown_record(path)
        consolidation = (metadata.get("version") or {}).get("consolidation_date")
        current = (
            next((item for item in history["versions"] if item["date"] == consolidation), None)
            or version_at(history, date.today().isoformat())
            or history["versions"][-1]
        )
        expected = _expected_articles(history, current)
        if not expected:
            continue
        item = {"path": relative, "id": metadata.get("id"), "atual": compare(parse_articles(body), expected)}
        original = history["versions"][0]
        if original is not current:
            rendered = render_version(history, original, title=metadata.get("title") or "")
            item["original"] = compare(parse_articles(rendered), _expected_articles(history, original))
        results.append(item)
    summary: dict[str, Any] = {"amostra": len(results), "consolidados_no_acervo": len(candidates)}
    for version in ("atual", "original"):
        items = [item[version] for item in results if version in item]
        if not items:
            continue
        summary[version] = {
            "diplomas": len(items),
            "mesmo_numero_de_artigos": sum(1 for item in items if item["mesmo_numero_de_artigos"]),
            "tudo_igual": sum(1 for item in items if item["tudo_igual"]),
            "partes_iguais": sum(1 for item in items if item["partes_iguais"]),
            "artigos_dre": sum(item["artigos_dre"] for item in items),
            "artigos_parser": sum(item["artigos_parser"] for item in items),
            "epigrafes_iguais": sum(item["epigrafes_iguais"] for item in items),
        }
    summary["diferencas"] = [
        {"path": item["path"], **{key: value for key, value in item["atual"].items() if key != "tudo_igual"}}
        for item in results
        if not item["atual"]["tudo_igual"]
    ][:40]
    return summary


# ------------------------------------------------------------------ relatório


def run(
    acervo: Acervo,
    *,
    workers: int = 1,
    today: str | None = None,
    validation_sample: int = 300,
    limit: int | None = None,
    progress: Progress = _silent,
) -> StructureReport:
    today = today or date.today().isoformat()
    rows = read_rows(acervo, workers=workers, limit=limit, progress=progress)
    progress(f"Registos lidos: {len(rows)}")
    report = aggregate(rows, today=today)
    report.rows = rows
    report.manual = check_manual(acervo, rows, load_manual(acervo.root / MANUAL_FILE))
    report.summary["vigencia"]["provas_manuais"] = len(report.manual)
    if report.manual:
        progress(f"Provas manuais de vigência: {len(report.manual)} ({MANUAL_FILE})")
    if validation_sample:
        progress(f"A validar o parser em {validation_sample} consolidados…")
        report.validation = validate_consolidated(acervo, rows, sample=validation_sample)
    return report


# ------------------------------------------------------------------ escrita nos registos

# Prova -> `legal_status_basis.source`.
_BASIS_SOURCES = {
    "norma revogatória": "norma_revogatoria", "DRE repealed_by": "relacao_dre", "cláusula de vigência": "clausula_vigencia",
    "prova manual": "prova_manual",
}
# Entrada em vigor que se grava: lida numa cláusula ou pela regra supletiva (sem cláusula, nada).
_WRITTEN_METHODS = {"clausula", "supletiva"}


@dataclass
class ApplySummary:
    entry_into_force: int = 0
    legal_status: int = 0
    withdrawn: int = 0
    manual: int = 0
    updated: int = 0
    changed_paths: list[Path] = field(default_factory=list)


# ------------------------------------------------------------------ provas manuais

# Provas registadas à mão de que um diploma deixou de estar em vigor, quando nenhuma das
# fontes automáticas o diz (p. ex. um PDM revisto: o aviso da revisão aprova um Regulamento
# novo sem revogar a resolução que ratificou o antigo, e o DRE continua a dá-la em vigor).
# Uma linha JSON por diploma; só esta fonte se sobrepõe a um estado do DRE.
MANUAL_FILE = "reports/vigencia-manual.jsonl"
MANUAL_SOURCE = "prova_manual"
# `Relationship.source` da relação `repealed_by` que a prova manual junta ao registo.
MANUAL_RELATION_SOURCE = f"leis-portugal structure ({MANUAL_FILE})"
_MANUAL_STATUSES = {"repealed", "not_in_force"}
_MANUAL_FIELDS = ("id", "estado", "substituido_por", "data", "citacao", "motivo")


@dataclass(frozen=True)
class ManualProof:
    """Uma linha de `vigencia-manual.jsonl`: `citacao` é uma frase do diploma `substituido_por`
    (copiada do texto do acervo, que se confirma), `data` o dia em que deixou de vigorar."""

    id: str
    status: str
    replaced_by: str
    date: str | None
    quote: str
    reason: str


def load_manual(path: Path) -> list[ManualProof]:
    """Lê o ficheiro de provas manuais (sem ficheiro, nenhuma). Uma linha mal formada é um erro:
    não se aplica uma prova incompleta."""
    if not path.is_file():
        return []
    proofs: list[ManualProof] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        item = json.loads(line)
        missing = [key for key in _MANUAL_FIELDS if key != "data" and not str(item.get(key) or "").strip()]
        if missing or set(item) - set(_MANUAL_FIELDS):
            raise ValueError(f"{path.name}:{number}: campos em falta {missing} ou desconhecidos {sorted(set(item) - set(_MANUAL_FIELDS))}")
        if item["estado"] not in _MANUAL_STATUSES:
            raise ValueError(f"{path.name}:{number}: estado {item['estado']!r} (aceites: {sorted(_MANUAL_STATUSES)})")
        if item.get("data") is not None:
            date.fromisoformat(item["data"])
        if item["id"] in {proof.id for proof in proofs}:
            raise ValueError(f"{path.name}:{number}: {item['id']} repetido")
        proofs.append(ManualProof(item["id"], item["estado"], item["substituido_por"], item.get("data"), item["citacao"], item["motivo"]))
    return proofs


def _plain(text: str) -> str:
    """Texto para comparar a citação: sem ligações markdown e com os espaços normalizados."""
    return " ".join(re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text).split())


def check_manual(acervo: Acervo, rows: list[dict[str, Any]], proofs: list[ManualProof]) -> list[ManualProof]:
    """Confirma cada prova: os dois diplomas existem no acervo e a citação está, letra a letra,
    no texto do diploma que substitui. Falhar uma é um erro (nada se marca sem a frase da fonte)."""
    paths = {row["id"]: row["path"] for row in rows if row.get("id")}
    for proof in proofs:
        for record_id in (proof.id, proof.replaced_by):
            if record_id not in paths:
                raise ValueError(f"{MANUAL_FILE}: {record_id} não está no acervo")
        _, body = read_markdown_record(str(acervo.root / paths[proof.replaced_by]))
        if _plain(proof.quote) not in _plain(body):
            raise ValueError(f"{MANUAL_FILE}: a citação de {proof.id} não está no texto de {proof.replaced_by}")
    return proofs


def manual_basis(proof: ManualProof, dre_status: str) -> dict[str, Any]:
    """`legal_status_basis` de uma prova manual; `dre_status` guarda o estado anterior, que volta
    se a prova for retirada do ficheiro."""
    return {
        "source": MANUAL_SOURCE,
        "dre_status": dre_status,
        "reason": proof.reason,
        "evidence": [{"status": proof.status, "provenance": f"prova manual: {proof.replaced_by}", "detail": proof.quote}],
    }


def manual_relation(proof: ManualProof) -> Relationship:
    return Relationship(type="repealed_by", target=proof.replaced_by, label=proof.reason, source=MANUAL_RELATION_SOURCE, date=proof.date)


def _without_manual_relations(relations: list[Relationship]) -> list[Relationship]:
    return [relation for relation in relations if relation.source != MANUAL_RELATION_SOURCE]


def legal_status_basis(proposal: dict[str, Any]) -> dict[str, Any]:
    """`legal_status_basis` de uma proposta: a fonte da primeira prova do estado proposto e as provas."""
    provenance = next(item["provenance"] for item in proposal["evidence"] if item["status"] == proposal["status"])
    source = next(value for prefix, value in _BASIS_SOURCES.items() if provenance.startswith(prefix))
    if proposal.get("dre_status"):
        # Norma revogatória contra o estado do DRE (segmento aprovado): o estado do DRE fica guardado
        # e volta se a prova deixar de existir.
        return {
            "source": AGAINST_DRE_SOURCE, "dre_status": proposal["dre_status"], "segment": proposal["segmento"],
            "evidence": [dict(item) for item in proposal["evidence"]],
        }
    return {"source": source, "evidence": [dict(item) for item in proposal["evidence"]]}


def apply(acervo: Acervo, report: StructureReport, rows: list[dict[str, Any]], *, progress: Progress = _silent) -> ApplySummary:
    """Grava nos registos a entrada em vigor (`entry_into_force` e, se estiver vazio,
    `entry_into_force_dates`) e o estado de vigência provado dos diplomas de vigência
    desconhecida (`legal_status` e `legal_status_basis`). Os ids por artigo não se gravam:
    calculam-se do corpo (`leis_portugal.domain.articles`)."""
    changes: dict[str, dict[str, Any]] = defaultdict(dict)
    for row in rows:
        eif = row["entry_into_force"]
        if eif and eif["method"] in _WRITTEN_METHODS:
            changes[row["path"]]["entry_into_force"] = eif
    for row in rows:
        if row.get("proven_status"):
            changes[row["path"]]["proposal"] = None
    for proposal in report.proposals:
        if proposal["status"]:
            changes[proposal["path"]]["proposal"] = proposal
    paths = {row["id"]: row["path"] for row in rows if row.get("id")}
    for proof in report.manual:
        changes[paths[proof.id]]["manual"] = proof
    summary = ApplySummary()
    for index, (relative, change) in enumerate(sorted(changes.items()), start=1):
        path = acervo.root / relative
        record, body = acervo.read(path)
        if "entry_into_force" in change:
            record.entry_into_force = change["entry_into_force"]
            if not record.entry_into_force_dates and record.entry_into_force.get("date"):
                record.entry_into_force_dates = [record.entry_into_force["date"]]
            summary.entry_into_force += 1
        if "manual" in change:
            # A prova manual prevalece sobre as automáticas e sobre o estado do DRE.
            proof = change["manual"]
            previous = record.legal_status_basis or {}
            dre_status = previous.get("dre_status") or ("unknown" if previous else record.legal_status)
            record.legal_status = proof.status
            record.legal_status_basis = manual_basis(proof, dre_status)
            record.relationships = _without_manual_relations(record.relationships)
            record.add_relationships([manual_relation(proof)])
            summary.legal_status += 1
            summary.manual += 1
        elif "proposal" in change:
            proposal = change["proposal"]
            if proposal and (
                record.legal_status == "unknown" or record.legal_status_basis or proposal.get("dre_status") == record.legal_status
            ):
                record.legal_status = proposal["status"]
                record.legal_status_basis = legal_status_basis(proposal)
                record.relationships = _without_manual_relations(record.relationships)
                summary.legal_status += 1
            elif not proposal and record.legal_status_basis:
                # A prova deixou de existir: o estado volta ao anterior (desconhecido, ou o do DRE).
                record.legal_status = record.legal_status_basis.get("dre_status") or "unknown"
                record.legal_status_basis = None
                record.relationships = _without_manual_relations(record.relationships)
                summary.withdrawn += 1
        if write_if_changed(path, render_record(record.to_dict(), body)):
            summary.updated += 1
            summary.changed_paths.append(path)
        if index % 20000 == 0:
            progress(f"[{index}/{len(changes)}] registos escritos")
    return summary


def write_report(report: StructureReport, output: Path) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    data = {**report.summary, "validacao": report.validation}
    paths = [output / "estrutura.json", output / "estrutura.md", output / "vigencia-proposta.jsonl"]
    paths[0].write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    paths[1].write_text(render_markdown(report), encoding="utf-8")
    with paths[2].open("w", encoding="utf-8") as handle:
        for item in sorted(report.proposals, key=lambda value: value["id"]):
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    return paths


def _pct(part: int, whole: int) -> str:
    return f"{part / whole:.1%}".replace(".", ",") if whole else "—"


def _n(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def render_markdown(report: StructureReport) -> str:
    s = report.summary
    a, e, v = s["artigos"], s["entrada_em_vigor"], s["vigencia"]
    lines = [
        "# Estrutura, entrada em vigor e vigência: cobertura",
        "",
        f"Gerado por `leis-portugal structure --dry-run` em {s['gerado_em']}. Nenhum registo foi alterado.",
        "",
        "## Artigos",
        "",
        "| | Diplomas | % dos com texto |",
        "| --- | --: | --: |",
        f"| Registos portugueses e regionais | {_n(a['registos'])} | |",
        f"| Com texto | {_n(a['com_texto'])} | 100% |",
        f"| Com artigos identificados (artigos, bases ou cláusulas) | {_n(a['com_artigos'])} | {_pct(a['com_artigos'], a['com_texto'])} |",
        f"| Só com números do dispositivo (`1.º`, `1 -`) | {_n(a['por_unidade'].get('numeros', 0))} | {_pct(a['por_unidade'].get('numeros', 0), a['com_texto'])} |",
        f"| Artigos só nos anexos | {_n(a['por_unidade'].get('so_anexos', 0))} | {_pct(a['por_unidade'].get('so_anexos', 0), a['com_texto'])} |",
        f"| Sem divisão (texto único) | {_n(a['por_unidade'].get('nenhum', 0))} | {_pct(a['por_unidade'].get('nenhum', 0), a['com_texto'])} |",
        "",
        f"- Diplomas com artigos identificados por títulos `######` (o que o export conta hoje): {_n(a['artigos_antes'])}; "
        f"só em texto corrido (novos): {_n(a['so_texto_corrido'])}.",
        f"- Em vigor com texto: {_n(a['em_vigor_com_texto'])}; com artigos: {_n(a['em_vigor_com_artigos'])} "
        f"({_pct(a['em_vigor_com_artigos'], a['em_vigor_com_texto'])}); com artigos ou números: "
        f"{_n(a['em_vigor_com_artigos_ou_numeros'])} ({_pct(a['em_vigor_com_artigos_ou_numeros'], a['em_vigor_com_texto'])}).",
        f"- Artigos com id: {_n(a['artigos_identificados'])}; números com id: {_n(a['numeros_identificados'])}.",
        f"- Diplomas com anexos com artigos: {_n(a['com_anexos'])}; com numeração repetida na mesma parte "
        f"(chave `art-5-2`): {_n(a['com_numeracao_repetida'])}; com ids repetidos: {_n(a['ids_duplicados'])}.",
        "",
        "## Entrada em vigor",
        "",
        "| | Diplomas | % dos com texto |",
        "| --- | --: | --: |",
        f"| Data calculada a partir da cláusula | {_n(e['calculadas_do_texto'])} | {_pct(e['calculadas_do_texto'], e['com_texto'])} |",
        f"| Só a regra (não dá para calcular) | {_n(e['so_regra'])} | {_pct(e['so_regra'], e['com_texto'])} |",
        f"| Regra supletiva (5.º dia após a publicação) | {_n(e['supletivas'])} | {_pct(e['supletivas'], e['com_texto'])} |",
        f"| Sem cláusula e sem regra supletiva | {_n(e['sem_clausula'])} | {_pct(e['sem_clausula'], e['com_texto'])} |",
        "",
        f"- Produção de efeitos: {_n(e['com_data_de_efeitos'])} com data; {_n(e['com_regra_de_efeitos_sem_data'])} só com a regra.",
        f"- Com fim de vigência no texto: {_n(e['com_fim_de_vigencia'])}; com cláusulas parciais (só alguns artigos): "
        f"{_n(e['com_clausulas_parciais'])}.",
        "",
        "Regras mais frequentes que ficam sem data:",
        "",
        *[f"- {count} × {rule}" for rule, count in e["regras_mais_frequentes_sem_data"]],
        "",
        "Por jurisdição e série:",
        "",
        "| | Com data | Só regra | Supletiva | Sem cláusula |",
        "| --- | --: | --: | --: | --: |",
        *[
            f"| {key} | {_n(value.get('clausula_com_data', 0))} | {_n(value.get('clausula_so_regra', 0))} | "
            f"{_n(value.get('supletiva', 0))} | {_n(value.get('sem_clausula', 0))} |"
            for key, value in e["por_jurisdicao_e_serie"].items()
        ],
        "",
        "## Vigência desconhecida",
        "",
        f"Diplomas com `legal_status: unknown`: {_n(v['desconhecidos'])}. Estado proposto com prova: "
        f"**{_n(v['resolvidos'])}** ({', '.join(f'{k}: {_n(c)}' for k, c in v['estado_proposto'].items()) or 'nenhum'}).",
        "",
        "| Categoria | Diplomas |",
        "| --- | --: |",
        *[f"| {_CATEGORY_LABELS.get(key, key)} | {_n(value)} |" for key, value in v["por_categoria"].items()],
        "",
        f"Revogações lidas nas normas revogatórias: {_n(v['revogacoes_lidas_no_texto'])} "
        f"(sobre {_n(v['diplomas_revogados_no_texto'])} diplomas).",
        "",
        "Precisão das provas de revogação total nos diplomas cujo estado o DRE conhece:",
        "",
        "| Prova | DRE: revogado | DRE: sem vigência | DRE: em vigor | Concordam |",
        "| --- | --: | --: | --: | --: |",
        *[
            f"| {'Norma revogatória (texto)' if key == 'texto' else 'Relação do DRE (etiqueta)'} | {_n(value['repealed'])} | "
            f"{_n(value['not_in_force'])} | {_n(value['em_vigor'])} | {_pct(value['concordam'], value['total'])} |"
            for key, value in v["precisao_nos_estados_conhecidos"].items()
        ],
        "",
        *_against_dre_lines(v),
        "As propostas, com as provas e a proveniência de cada uma, estão em `vigencia-proposta.jsonl`.",
        "",
        "### Como se resolve, sem inferir sem prova",
        "",
        "- **Só uma revogação total fixa o estado** (`repealed`). Conta a norma revogatória de outro diploma do acervo "
        "(\"É revogado o [Decreto-Lei n.º 253/86]…\", com a ligação ao diploma) e a etiqueta da relação do DRE "
        "(\"Revogado pelo DEC LEI…\"). Proveniência: `norma revogatória: <id do revogador>#<artigo>` ou `DRE repealed_by: <id>`.",
        "- **Revogação parcial não resolve**: \"os artigos 3.º e 5.º do…\" ou \"Revogado o nº 5 pela…\" ficam registados como prova, "
        "mas o resto do diploma continua de vigência desconhecida (não se conclui que está em vigor).",
        "- **Revogações condicionais ou diferidas não contam** (\"a partir da entrada em vigor da portaria…\", \"mantido transitoriamente…\"), "
        "e uma ligação noutro papel (\"na redação dada pelo…\", \"aprovado pelo…\") também não.",
        "- **Relação `repealed_by` sem etiqueta**: não diz se é total ou parcial; fica \"por confirmar\" até haver o texto do revogador.",
        "- **Caducidade**: só quando o próprio diploma fixa o fim (\"vigora até 31 de dezembro de 2013\"), a data já passou e o diploma "
        "não foi alterado depois (uma alteração pode ter prorrogado a vigência). Proveniência: `cláusula de vigência: <artigo>`.",
        "- **Declarações de retificação** não têm vigência própria: seguem o diploma retificado (relação `corrects`).",
        "- **Só PDF e anteriores a 1960**: sem texto não há prova; ficam marcados como históricos e saem do índice de lei atual, "
        "sem mudar `legal_status`.",
        "- Ao escrever nos registos, o estado proposto vai para `legal_status` e as provas para `legal_status_basis`; "
        "um conflito entre provas (total num lado, parcial noutro) não muda nada.",
    ]
    if report.validation:
        val = report.validation
        lines += [
            "",
            "## Validação do parser contra os consolidados do DRE",
            "",
            f"Amostra: {val['amostra']} diplomas consolidados (de {_n(val['consolidados_no_acervo'])}), "
            "comparando os artigos do parser com os fragmentos de artigo dos `.versoes.json`.",
            "",
            "| Texto | Diplomas | Mesmo n.º de artigos | Números e epígrafes iguais | Mesmas partes | Epígrafes iguais |",
            "| --- | --: | --: | --: | --: | --: |",
        ]
        for version, label in (("atual", "Atual (`.md`)"), ("original", "Original (1.ª versão)")):
            if version in val:
                item = val[version]
                lines.append(
                    f"| {label} | {item['diplomas']} | {_pct(item['mesmo_numero_de_artigos'], item['diplomas'])} | "
                    f"{_pct(item['tudo_igual'], item['diplomas'])} | {_pct(item['partes_iguais'], item['diplomas'])} | "
                    f"{_n(item['epigrafes_iguais'])} de {_n(item['artigos_dre'])} |"
                )
        if val.get("diferencas"):
            lines += ["", "Diferenças (texto atual):", ""]
            for item in val["diferencas"][:15]:
                lines.append(
                    f"- `{item['path']}`: parser {item['artigos_parser']}, DRE {item['artigos_dre']}; "
                    f"primeira diferença: {json.dumps(item['primeira_diferenca'], ensure_ascii=False)}"
                )
    return "\n".join(lines) + "\n"


def _against_dre_lines(v: dict[str, Any]) -> list[str]:
    against = v.get("texto_contra_dre")
    if not against:
        return []
    sample = against["amostra_verificada"]
    first, second = sample["primeira"], sample["segunda"]
    segments = against.get("por_segmento") or {}
    lines = [
        f"**Texto contra o DRE.** {_n(against['diplomas'])} diplomas que o DRE dá em vigor têm uma revogação total lida na norma "
        f"revogatória de outro diploma do acervo ({_n(against['provas'])} provas). Cada prova tem um segmento: a identidade do "
        "diploma ligado (o número do rótulo, a data citada até 20 dias antes da publicação, a entidade e a série) e os sinais "
        "contra (alteração registada no DRE depois do revogador, outro revogador ou revogação parcial no DRE, repristinação, "
        "declaração de retificação, \"legislação em contrário\").",
        "",
        "| Segmento | Provas | Amostra às cegas | Certos | Precisão ponderada | Wilson 95 % |",
        "| --- | --: | --: | --: | --: | --: |",
    ]
    for key, label in SEGMENTS.items():
        item = second["por_segmento"].get(key) or {}
        interval = item.get("wilson_95") or [None, None]
        lines.append(
            f"| {key}: {label} | {_n(segments.get(key, 0))} | {item.get('amostra', 0)} | {item.get('certos', 0)} | "
            f"{_pct(round(item['ponderada'] * 1000), 1000) if item else '—'} | "
            f"{_pct(round(interval[0] * 1000), 1000) if interval[0] is not None else '—'} – "
            f"{_pct(round(interval[1] * 1000), 1000) if interval[1] is not None else '—'} |"
        )
    applied = against.get("segmentos_aplicados") or []
    lines += [
        "",
        f"Amostra de {second['data']} (seed {second['seed']}, {second['amostra']} casos nunca verificados, estratificada por segmento "
        f"e tipo): verificadores às cegas e auditoria de todos os \"não\" e de 20 \"sim\" ({second['auditoria']['concordam']} de "
        f"{second['auditoria']['casos']} concordam; prevalece a auditoria). A primeira amostra ({first['data']}, {first['amostra']} casos: "
        f"{first['certos']} certos, {_pct(first['certos'], first['amostra'])}) serviu para afinar a regra e não conta para a medida. "
        "Os erros que ficam: outro diploma com o mesmo número e data próxima (só a matéria os distingue), ressalvas de situações em "
        "curso noutro artigo e revogações diferidas. "
        + (
            f"Segmentos aplicados como base automática (`norma_revogatoria_contra_dre`): {', '.join(applied)}."
            if applied
            else f"Nenhum segmento chega aos {sample['limiar']:.0%}: o estado do DRE não se substitui por esta prova. Só os casos "
            "verificados entram, como prova manual (`vigencia-manual.jsonl`). Lista, segmentos e veredictos: "
            "`vigencia-texto-contra-dre.jsonl`."
        ),
        "",
    ]
    return lines


_CATEGORY_LABELS = {
    "revogado": "Revogado (prova de revogação total)",
    "caducado": "Caducado (vigência temporária já passada, sem alterações)",
    "revogacao_parcial": "Só revogação parcial: o resto continua desconhecido",
    "revogacao_por_confirmar": "Revogação sem âmbito conhecido (relação sem etiqueta)",
    "conflito": "Provas em conflito (o mesmo revogador, total e parcial)",
    "retificacao": "Declaração de retificação: segue o diploma retificado",
    "historico_so_pdf": "Só PDF e anterior a 1960: histórico, fora do índice de lei atual",
    "sem_prova": "Sem prova",
}
