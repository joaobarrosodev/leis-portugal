"""Tradução para português europeu dos atos da UE em vigor sem versão portuguesa no EUR-Lex.

Quase todos são de antes da adesão de Portugal (1986) e dirigidos a outros Estados ou a
empresas; o EUR-Lex conta-os "em vigor" porque nunca foram revogados. Para o acervo ficar
completo, cada um é guardado numa tradução não oficial, com a ligação ao texto autêntico.

Dois passos:

1. `prepare`: descarrega o ato na primeira língua disponível (inglês, francês…) e grava em
   `.cache/ue-traduzir/<CELEX>.json` o registo, o corpo em Markdown e a língua.
2. `assemble`: lê a tradução `<CELEX>.pt.md` (feita fora deste módulo) e grava o registo
   português, marcado como tradução (`version.kind: translation`), com a nota de que foi
   traduzido do texto nessa língua e a ligação ao original no EUR-Lex.

A tradução tem precedência mais baixa do que qualquer texto oficial: se o EUR-Lex vier a
publicar a versão portuguesa, a recolha normal substitui-a.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from leis_portugal.domain.identifiers import eu_record_id, normalize_celex
from leis_portugal.domain.record import LegalRecord, Version
from leis_portugal.errors import LeisPortugalError, NoSourceText
from leis_portugal.infrastructure.repository import Acervo, SavePolicy
from leis_portugal.services.common import Progress, failure, run_parallel, silent
from leis_portugal.sources.eurlex.source import EurLexSource


# Ordem de preferência das línguas do original (código CELLAR → nome, código do EUR-Lex).
LANGUAGES: dict[str, tuple[str, str]] = {
    "eng": ("inglês", "EN"),
    "fra": ("francês", "FR"),
    "deu": ("alemão", "DE"),
    "ita": ("italiano", "IT"),
    "nld": ("neerlandês", "NL"),
    "spa": ("espanhol", "ES"),
    # 32015D1890 só foi publicado em irlandês.
    "gle": ("irlandês", "GA"),
}
CACHE = Path(".cache") / "ue-traduzir"
FAILURES = Path("reports") / "eurlex_em_vigor_failures.jsonl"
GENERATED_BY = "leis-portugal collect eurlex-traducao"
_ONLY_PDF = "liga apenas ao PDF oficial"


def eurlex_url(celex: str, language: str) -> str:
    return f"https://eur-lex.europa.eu/legal-content/{LANGUAGES[language][1]}/TXT/?uri=CELEX%3A{normalize_celex(celex)}"


def pending_celex(root: Path) -> list[str]:
    """Os CELEX em vigor que a recolha não encontrou em português (`sem_texto_na_fonte`)."""
    path = root / FAILURES
    if not path.exists():
        return []
    found = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            item = json.loads(line)
            if item.get("motivo") == "sem_texto_na_fonte" and item.get("celex"):
                found.append(normalize_celex(item["celex"]))
    return sorted(set(found))


@dataclass
class PrepareSummary:
    prepared: dict[str, int] = field(default_factory=dict)  # língua → n.º
    skipped: int = 0
    only_pdf: list[str] = field(default_factory=list)
    failures: list[dict[str, str]] = field(default_factory=list)


def prepare(
    celex_list: list[str],
    cache: Path,
    *,
    source_factory: Callable[[], EurLexSource] = EurLexSource,
    workers: int = 1,
    progress: Progress = silent,
) -> PrepareSummary:
    """Descarrega cada ato na primeira língua disponível; o que já está na cache não se repete."""
    cache.mkdir(parents=True, exist_ok=True)
    summary = PrepareSummary()

    def work(celex: str, source: EurLexSource) -> str:
        target = cache / f"{celex}.json"
        if target.exists():
            summary.skipped += 1
            return f"{celex}: já preparado"
        last_error: LeisPortugalError | None = None
        for language in LANGUAGES:
            try:
                document = source.collect(celex, language=language, consolidated=False)
            except NoSourceText:
                continue
            except LeisPortugalError as exc:
                # A expressão existe mas sem texto nem PDF nesta língua: tenta a seguinte.
                last_error = exc
                continue
            only_pdf = any(_ONLY_PDF in warning for warning in document.warnings)
            data = {
                "celex": celex,
                "language": language,
                "original_url": eurlex_url(celex, language),
                "record": document.record.to_dict(),
                "body": document.body,
                "only_pdf": only_pdf,
            }
            target.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
            summary.prepared[language] = summary.prepared.get(language, 0) + 1
            if only_pdf:
                summary.only_pdf.append(celex)
            return f"{celex}: {LANGUAGES[language][0]}"
        if last_error is not None:
            summary.failures.append(failure("celex", celex, last_error))
            return f"{celex}: falha: {last_error}"
        summary.failures.append({"celex": celex, "motivo": "sem_texto_na_fonte", "error": "Sem expressão em nenhuma das línguas tentadas."})
        return f"{celex}: sem expressão em {', '.join(LANGUAGES)}"

    run_parallel(celex_list, work, context=source_factory, workers=workers, progress=progress)
    return summary


_HEADER = re.compile(r"\A(?:título:\s*(?P<title>[^\n]+)\n)(?:resumo:\s*(?P<summary>[^\n]*)\n)?---\n", re.I)


def parse_translation(text: str) -> tuple[str, str | None, str]:
    """`título: …` / `resumo: …` / `---` e depois o corpo traduzido."""
    match = _HEADER.match(text.lstrip("﻿"))
    if not match:
        raise ValueError("A tradução tem de começar por 'título: …', opcionalmente 'resumo: …', e '---'.")
    summary = (match.group("summary") or "").strip() or None
    return match.group("title").strip(), summary, text[match.end():].strip()


def translated_record(data: dict, translation: str, *, translator: str, today: date) -> tuple[LegalRecord, str]:
    celex, language = data["celex"], data["language"]
    name = LANGUAGES[language][0]
    url = data["original_url"]
    title, summary, body = parse_translation(translation)
    record = LegalRecord.from_dict(data["record"])
    identifier = eu_record_id(celex, "por")
    record.id = identifier
    record.identifiers.internal = identifier
    record.title = title
    record.summary = summary
    record.short_title = None
    record.language = "por"
    record.version = Version(
        kind="translation",
        label=f"Tradução não oficial para português europeu do texto em {name} (EUR-Lex); sem valor jurídico",
        language="por",
    )
    record.source.official_url = url
    record.provenance.generated_by = GENERATED_BY
    year = int(celex[1:5]) if celex[1:5].isdigit() else 0
    if year and year < 1986:
        reason = "Sem versão portuguesa no EUR-Lex: ato anterior à adesão de Portugal (1986)."
    else:
        reason = "Sem versão portuguesa no EUR-Lex: o ato só foi publicado noutras línguas."
    extra = []
    if data.get("ocr"):
        # Sem texto eletrónico no CELLAR: o texto saiu do PDF oficial (camada de texto ou OCR).
        extra.append(f"O original só existe em PDF no EUR-Lex ({data['ocr']['pdf_url']}); o texto foi extraído do PDF antes da tradução.")
    record.notes = [
        f"Traduzido do texto em {name} publicado no EUR-Lex: {url}",
        reason,
        *extra,
        f"Tradução automática por {translator}, em {today.isoformat()}; só o texto original é autêntico.",
        *[note for note in record.notes if note],
    ]
    note = f"> Tradução não oficial para português europeu do texto em {name}. Original (autêntico) no EUR-Lex: [{celex}]({url})."
    # Como nos outros registos, o corpo começa pelo título; a nota vem logo a seguir.
    heading, rest = (body.split("\n", 1) + [""])[:2] if body.startswith("# ") else (f"# {title}", body)
    return record, f"{heading}\n\n{note}\n\n{rest.strip()}\n"


@dataclass
class AssembleSummary:
    written: int = 0
    unchanged: int = 0
    missing: list[str] = field(default_factory=list)
    failures: list[dict[str, str]] = field(default_factory=list)


# A tradução não tem precedência sobre nada: a recolha normal pode substituí-la.
TRANSLATION_POLICY = SavePolicy(respect_precedence=True)


def assemble(acervo: Acervo, cache: Path, *, translator: str, today: date | None = None, progress: Progress = silent) -> AssembleSummary:
    summary = AssembleSummary()
    today = today or date.today()
    for path in sorted(cache.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        translation = path.with_suffix(".pt.md")
        if not translation.exists():
            summary.missing.append(data["celex"])
            continue
        try:
            record, body = translated_record(data, translation.read_text(encoding="utf-8"), translator=translator, today=today)
            result = acervo.save(record, body, policy=TRANSLATION_POLICY)
        except (ValueError, LeisPortugalError) as exc:
            summary.failures.append({"celex": data["celex"], "error": f"{type(exc).__name__}: {exc}"})
            progress(f"{data['celex']}: falha: {exc}")
            continue
        if result.changed:
            summary.written += 1
        else:
            summary.unchanged += 1
    return summary
