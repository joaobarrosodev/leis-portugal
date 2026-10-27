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
from leis_portugal.domain.validity import Repeal, propose, repeals_in
from leis_portugal.infrastructure.markdown import read_markdown_record
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
        {"type": item.get("type"), "target": item.get("target"), "label": item.get("label")}
        for item in metadata.get("relationships") or []
        if item.get("type") in _RELATION_TYPES
    ]
    return {
        "id": record_id,
        "path": os.path.relpath(path, root),
        "jurisdiction": metadata.get("jurisdiction"),
        "document_type": metadata.get("document_type"),
        "series": publication.get("series"),
        "publication_date": metadata.get("publication_date"),
        "legal_status": metadata.get("legal_status") or "unknown",
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


def _status_group(status: str) -> str:
    return {"in_force": "em_vigor", "partially_in_force": "em_vigor"}.get(status, status)


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
            text_repeals[item["target"]].append(Repeal(**item))
    incoming: dict[str, list[dict[str, str | None]]] = defaultdict(list)
    for row in rows:
        for relation in row["relations"]:
            if relation["type"] == "repeals" and relation["target"] in by_id:
                incoming[relation["target"]].append({"source": row["id"], "label": relation["label"]})

    categories = Counter()
    proposed = Counter()
    agreement = Counter()
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
    }
    report.summary = {"gerado_em": today, "artigos": articles, "entrada_em_vigor": entry, "vigencia": validity}
    return report


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
    found = [(article.part, article.number, article.heading) for article in parsed if article.kind in ("artigo", "base")]
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
    if validation_sample:
        progress(f"A validar o parser em {validation_sample} consolidados…")
        report.validation = validate_consolidated(acervo, rows, sample=validation_sample)
    return report


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
        "As propostas, com as provas e a proveniência de cada uma, estão em `vigencia-proposta.jsonl`.",
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


_CATEGORY_LABELS = {
    "revogado": "Revogado (prova de revogação total)",
    "caducado": "Caducado (vigência temporária já passada, sem alterações)",
    "revogacao_parcial": "Só revogação parcial: o resto continua desconhecido",
    "revogacao_por_confirmar": "Revogação sem âmbito conhecido (relação sem etiqueta)",
    "retificacao": "Declaração de retificação: segue o diploma retificado",
    "historico_so_pdf": "Só PDF e anterior a 1960: histórico, fora do índice de lei atual",
    "sem_prova": "Sem prova",
}
