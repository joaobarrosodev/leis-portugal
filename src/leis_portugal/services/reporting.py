"""Relatórios de cobertura, progresso e saúde das fontes."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from leis_portugal.infrastructure.config import load_source_registry
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.validation import validate_repository


# Acima deste número, os relatórios mostram apenas agregados (o acervo completo tem
# centenas de milhares de registos).
MAX_LISTED_DOCUMENTS = 500


def _today() -> str:
    return datetime.now(UTC).date().isoformat()


def load_records(acervo: Acervo) -> list[dict[str, Any]]:
    """Metadados dos registos realmente presentes no acervo."""
    return [{"path": acervo.relative(path), "metadata": metadata} for path, metadata in acervo.iter_front_matter()]


def build_coverage(acervo: Acervo, records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Constrói estatísticas exclusivamente a partir dos registos existentes."""
    records = load_records(acervo) if records is None else records
    sources = load_source_registry(acervo.root)
    by_jurisdiction = Counter(record["metadata"].get("jurisdiction", "unknown") for record in records)
    by_type = Counter(record["metadata"].get("document_type", "unknown") for record in records)
    by_source = Counter(record["metadata"].get("source", {}).get("id", "unknown") for record in records)
    by_year = Counter(
        str(record["metadata"].get("publication_date") or record["metadata"].get("official_date") or "desconhecido")[:4]
        for record in records
    )
    by_territory = Counter(record["metadata"].get("territory") or "nacional" for record in records)
    by_version = Counter((record["metadata"].get("version") or {}).get("kind", "unknown") for record in records)
    by_status = Counter(record["metadata"].get("legal_status", "unknown") for record in records)
    # Texto da importação inicial vs. recolhido diretamente da fonte.
    by_origin = Counter(
        "importacao_inicial" if (record["metadata"].get("integrity") or {}).get("source_sha256_scope") == "imported_derived_markdown" else "recolha_direta"
        for record in records
    )
    relationships = Counter(
        relation.get("type", "unknown") for record in records for relation in record["metadata"].get("relationships") or []
    )
    validation = Counter(record["metadata"].get("validation", {}).get("status", "unknown") for record in records)
    return {
        "generated_at": _today(),
        "methodology": "Contagem direta dos ficheiros Markdown em data/ com front matter válido; sem estimativas de completude. Ano = data de publicação.",
        "totals": {
            "documents": len(records),
            "sources_registered": len(sources),
            "sources_operational": sum(1 for source in sources if source.get("status", {}).get("operational") == "operational"),
            "validated_documents": validation.get("validated", 0),
        },
        "by_jurisdiction": dict(sorted(by_jurisdiction.items())),
        "by_document_type": dict(sorted(by_type.items())),
        "by_source": dict(sorted(by_source.items())),
        "by_year": dict(sorted(by_year.items())),
        "by_territory": dict(sorted(by_territory.items())),
        "by_version_kind": dict(sorted(by_version.items())),
        "by_legal_status": dict(sorted(by_status.items())),
        "by_origin": dict(sorted(by_origin.items())),
        "with_version_history": sum(1 for record in records if record["metadata"].get("version_history")),
        "relationships_by_type": dict(sorted(relationships.items())),
        "by_validation_status": dict(sorted(validation.items())),
        "documents_listed": len(records) <= MAX_LISTED_DOCUMENTS,
        "documents": [] if len(records) > MAX_LISTED_DOCUMENTS else [
            {
                "id": record["metadata"].get("id"),
                "path": record["path"],
                "title": record["metadata"].get("title"),
                "jurisdiction": record["metadata"].get("jurisdiction"),
                "document_type": record["metadata"].get("document_type"),
                "official_date": record["metadata"].get("official_date"),
                "source": record["metadata"].get("source", {}).get("id"),
                "validation_status": record["metadata"].get("validation", {}).get("status"),
            }
            for record in records
        ],
    }


def build_source_status(acervo: Acervo, records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Cruza o registo de fontes com contagens reais do acervo."""
    records = load_records(acervo) if records is None else records
    counts = Counter(record["metadata"].get("source", {}).get("id") for record in records)
    sources = []
    for source in load_source_registry(acervo.root):
        sources.append(
            {
                "id": source.get("id"),
                "name": source.get("name"),
                "jurisdiction": source.get("jurisdiction"),
                "operational_status": source.get("status", {}).get("operational"),
                "last_verified_at": source.get("status", {}).get("last_verified_at"),
                "verified_scope": source.get("status", {}).get("verified_scope"),
                "reuse_status": source.get("reuse", {}).get("status"),
                "documents_in_repository": counts.get(source.get("id"), 0),
            }
        )
    return {"generated_at": _today(), "sources": sources}


def _coverage_markdown(coverage: dict[str, Any], source_status: dict[str, Any], coverage_dir: Path) -> str:
    lines = [
        "# Cobertura do acervo",
        "",
        f"Relatório gerado em {coverage['generated_at']} a partir dos registos presentes em `data/`.",
        "",
        "**Este relatório não representa cobertura integral da legislação portuguesa ou europeia.**",
        "A metodologia conta apenas ficheiros existentes e válidos no repositório; não usa estimativas.",
        "",
        "## Totais verificados",
        "",
        f"- Documentos recolhidos: {coverage['totals']['documents']}",
        f"- Documentos validados: {coverage['totals']['validated_documents']}",
        f"- Fontes registadas: {coverage['totals']['sources_registered']}",
        f"- Fontes operacionais: {coverage['totals']['sources_operational']}",
        "",
        "## Fontes",
        "",
        "| Fonte | Estado operacional | Reutilização | Documentos no repositório | Âmbito verificado |",
        "|---|---|---:|---:|---|".replace("---:|---:", "---|---"),
    ]
    for source in source_status["sources"]:
        lines.append(
            "| {id} | {operational} | {reuse} | {count} | {scope} |".format(
                id=source["id"],
                operational=source["operational_status"] or "desconhecido",
                reuse=source["reuse_status"] or "desconhecido",
                count=source["documents_in_repository"],
                scope=(source["verified_scope"] or "—").replace("|", "\\|"),
            )
        )
    def counter_table(title: str, header: str, values: dict[str, int], unit: str = "Documentos") -> None:
        lines.extend(["", f"## {title}", "", f"| {header} | {unit} |", "|---|---:|"])
        lines.extend(f"| {key} | {count} |" for key, count in values.items())

    counter_table("Por jurisdição", "Jurisdição", coverage["by_jurisdiction"])
    counter_table("Por região", "Região", coverage["by_territory"])
    counter_table("Por tipo de diploma", "Tipo", dict(sorted(coverage["by_document_type"].items(), key=lambda item: -item[1])))
    counter_table("Por tipo de versão", "Versão", coverage["by_version_kind"])
    counter_table("Origem do texto", "Origem", coverage["by_origin"])
    counter_table("Por estado de vigência", "Estado", coverage["by_legal_status"])
    counter_table("Relações registadas", "Relação", coverage["relationships_by_type"], unit="Relações")
    counter_table("Por ano de publicação", "Ano", coverage["by_year"])

    failure_files = {
        "dre_consolidated_failures.jsonl": "Diplomas sem texto consolidado no DRE (histórico de versões)",
        "dre_imported_failures.jsonl": "Diplomas da importação inicial que não foi possível recolher do DRE",
        "eurlex_referenced_failures.jsonl": "Atos da UE referidos pela legislação portuguesa sem versão portuguesa no CELLAR",
        "eurlex_consolidated_failures.jsonl": "Atos da UE com consolidações mas sem versão consolidada em português",
    }
    rows = []
    for name, description in failure_files.items():
        path = coverage_dir / name
        if path.exists():
            count = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
            rows.append(f"| [{name}]({name}) | {description} | {count} |")
    if rows:
        lines.extend(["", "## Falhas de recolha registadas", "", "| Ficheiro | O que contém | Registos |", "|---|---|---:|", *rows])

    lines.extend(["", "## Registos existentes", ""])
    if not coverage["documents_listed"]:
        lines.append(f"Com mais de {MAX_LISTED_DOCUMENTS} registos, a lista individual é omitida; consulte `data/`.")
    elif coverage["documents"]:
        lines.extend([
            "| Documento | Tipo | Data oficial | Fonte | Validação |",
            "|---|---|---|---|---|",
        ])
        for document in coverage["documents"]:
            title = (document["title"] or "").replace("|", "\\|")
            lines.append(
                f"| [{document['id']}]({document['path']}) — {title} | {document['document_type']} | "
                f"{document['official_date'] or '—'} | {document['source']} | {document['validation_status']} |"
            )
    else:
        lines.append("Ainda não existem documentos recolhidos.")
    lines.extend([
        "",
        "## Lacunas conhecidas",
        "",
        "- Parte dos diplomas ainda tem o texto da importação inicial (convertido a partir do DRE); a recolha direta substitui-o diploma a diploma.",
        "- O conector DRE usa endpoints internos da aplicação web (sem API pública documentada) e pode falhar após um deploy do DRE.",
        "- Diplomas anteriores a 1960 existem no DRE apenas como digitalização; o Jornal Oficial dos Açores está fora do âmbito.",
        "- Atos da UE: recolhidos os referidos pela legislação portuguesa e os publicados no JO nos intervalos executados; não é o acervo completo do EUR-Lex.",
        "- As transposições de diretivas são detetadas no texto português (\"transpõe…\") e podem ter falsos negativos.",
        "- A jurisprudência, materiais parlamentares e orientações de reguladores estão fora da coleção até serem integrados como categorias próprias.",
        "",
    ])
    return "\n".join(lines)


def _progress_markdown(coverage: dict[str, Any], source_status: dict[str, Any]) -> str:
    lines = [
        "# Progresso do projeto",
        "",
        f"Relatório gerado em {coverage['generated_at']}.",
        "",
        "## Estado real",
        "",
        "| Componente | Estado | Evidência |",
        "|---|---|---|",
        "| Estrutura do pacote Python | Implementado | `src/leis_portugal/` |",
        "| Registo de fontes | Implementado | `config/sources.yml` validado por esquema |",
        "| Esquemas de metadados | Implementado | `schemas/` |",
        f"| Conector EUR-Lex/CELLAR (por data, por CELEX e atos referidos) | Operacional | {coverage['by_source'].get('eurlex-cellar', 0)} ato(s) da UE no acervo |",
        f"| Conector DRE (1.ª Série, por data e consolidados) | Operacional | {coverage['by_source'].get('dre', 0)} documento(s) do DRE |",
        f"| Recolha direta (vs. importação inicial) | Em curso | {coverage['by_origin'].get('recolha_direta', 0)} recolhidos diretamente; "
        f"{coverage['by_origin'].get('importacao_inicial', 0)} ainda com o texto da importação inicial |",
        "| Relações entre diplomas | Parcial | DRE e CELLAR (alterações, revogações, retificações); citações e transposições de atos da UE detetadas no texto; ligações inversas nos atos da UE |",
        "| Relatórios derivados dos dados | Implementado | `reports/` |",
        "| Atualização diária automática | Implementado | `.github/workflows/atualizacao-diaria.yml` (DRE + EUR-Lex do dia anterior) |",
        f"| Histórico de versões consolidadas | Implementado | {coverage['with_version_history']} registo(s) com `<registo>.versoes.json` (DRE: `collect dre-consolidated`; UE: `collect eurlex-consolidated`) |",
        "",
        "## Estado das fontes",
        "",
        "| Fonte | Estado | Última verificação | Documentos |",
        "|---|---|---|---:|",
    ]
    for source in source_status["sources"]:
        lines.append(
            f"| {source['id']} | {source['operational_status'] or 'desconhecido'} | "
            f"{source['last_verified_at'] or '—'} | {source['documents_in_repository']} |"
        )
    lines.extend([
        "",
        "## Próximos passos",
        "",
        "1. Substituir o texto da importação inicial pela recolha direta do DRE (por intervalos de datas).",
        "2. Resolver as relações por número (`pt:numero:…`) e por ELI para ids do acervo, gerando um índice de relações.",
        "3. Comparar as transposições detetadas no texto com as medidas nacionais de execução registadas no CELLAR.",
        "",
    ])
    return "\n".join(lines)


def generate_reports(acervo: Acervo, *, output_dir: str | Path | None = None) -> dict[str, Path]:
    """Gera relatórios e devolve os caminhos escritos."""
    reports_dir = Path(output_dir) if output_dir else acervo.root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    records = load_records(acervo)
    coverage = build_coverage(acervo, records)
    source_status = build_source_status(acervo, records)
    issues = validate_repository(acervo)

    outputs = {
        "coverage_markdown": reports_dir / "COBERTURA.md",
        "progress_markdown": reports_dir / "PROGRESSO.md",
        "coverage_json": reports_dir / "coverage.json",
        "source_status_json": reports_dir / "source_status.json",
        "failures_jsonl": reports_dir / "failures.jsonl",
    }
    outputs["coverage_markdown"].write_text(_coverage_markdown(coverage, source_status, reports_dir), encoding="utf-8", newline="\n")
    outputs["progress_markdown"].write_text(_progress_markdown(coverage, source_status), encoding="utf-8", newline="\n")
    outputs["coverage_json"].write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    outputs["source_status_json"].write_text(json.dumps(source_status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    failure_lines = [
        json.dumps({"generated_at": _today(), "path": issue.path, "message": issue.message}, ensure_ascii=False)
        for issue in issues
    ]
    outputs["failures_jsonl"].write_text(("\n".join(failure_lines) + "\n") if failure_lines else "", encoding="utf-8", newline="\n")
    return outputs
