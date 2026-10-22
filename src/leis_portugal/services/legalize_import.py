"""Importação de um clone local do legalize-pt para a estrutura do acervo."""

from __future__ import annotations

import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from leis_portugal.infrastructure.markdown import read_record_id
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.common import PORTUGUESE_POLICY, Progress, silent
from leis_portugal.sources.legalize.mapper import LegalizeMapper
from leis_portugal.sources.legalize.snapshot import LegalizeSnapshot


@dataclass
class ImportSummary:
    total: int = 0
    written: int = 0
    unchanged: int = 0
    kept_existing: int = 0
    failures: list[dict[str, str]] = field(default_factory=list)


# Estado de cada processo: o mapeamento e o repositório são criados uma vez por processo.
_worker: dict[str, object] = {}


def _init_worker(root: str, snapshot: LegalizeSnapshot) -> None:
    acervo = Acervo(root)
    _worker["acervo"] = acervo
    _worker["mapper"] = LegalizeMapper(acervo.types, snapshot)
    _worker["snapshot"] = snapshot


def _plan(relative: str) -> tuple[str, str | None, str | None, str | None, str | None]:
    """-> (relativo, id, caminho preferido, id DRE, erro)."""
    acervo: Acervo = _worker["acervo"]  # type: ignore[assignment]
    snapshot: LegalizeSnapshot = _worker["snapshot"]  # type: ignore[assignment]
    try:
        document = _worker["mapper"].convert((snapshot.path / relative).read_bytes(), Path(relative))  # type: ignore[union-attr]
        record = document.record
        return relative, record.id, acervo.relative(acervo.path_for(record)), record.identifiers.dre, None
    except Exception as exc:  # cada falha é registada; não interrompe a importação
        return relative, None, None, None, f"{type(exc).__name__}: {exc}"


def _import(job: tuple[str, str]) -> tuple[str, str, str | None]:
    relative, target = job
    acervo: Acervo = _worker["acervo"]  # type: ignore[assignment]
    snapshot: LegalizeSnapshot = _worker["snapshot"]  # type: ignore[assignment]
    try:
        document = _worker["mapper"].convert((snapshot.path / relative).read_bytes(), Path(relative))  # type: ignore[union-attr]
        result = acervo.save(document.record, document.body, target=acervo.root / target, policy=PORTUGUESE_POLICY)
        return relative, result.action, None
    except Exception as exc:
        return relative, "failed", f"{type(exc).__name__}: {exc}"


def assign_targets(plans: list[tuple[str, str, str, str]], *, root: Path) -> dict[str, str]:
    """Caminhos finais determinísticos: entre diplomas com o mesmo caminho preferido,
    o de menor id DRE fica com o nome curto e os outros recebem o id como sufixo."""
    groups: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for relative, record_id, preferred, dre_id in plans:
        groups[preferred].append((relative, record_id, dre_id))
    targets: dict[str, str] = {}
    for preferred, members in groups.items():
        members.sort(key=lambda item: int(item[2]))
        occupant = read_record_id(root / preferred) if (root / preferred).exists() else None
        for index, (relative, record_id, dre_id) in enumerate(members):
            candidate = preferred
            if index > 0 or occupant not in (None, record_id):
                candidate = str(Path(preferred).with_name(f"{Path(preferred).stem}-{dre_id}.md"))
            targets[relative] = candidate
    return targets


def import_legalize(
    acervo: Acervo,
    legalize_path: str | Path,
    *,
    workers: int | None = None,
    limit: int | None = None,
    years: set[str] | None = None,
    progress: Progress = silent,
) -> ImportSummary:
    snapshot = LegalizeSnapshot.from_path(legalize_path)
    files = snapshot.files()
    if years:
        files = [path for path in files if path.parent.name in years]
    if limit:
        files = files[:limit]
    relatives = [path.relative_to(snapshot.path).as_posix() for path in files]
    summary = ImportSummary(total=len(relatives))
    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    progress(f"legalize-pt@{snapshot.commit[:12]}: {len(relatives)} ficheiros, {workers} processos")

    with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker, initargs=(str(acervo.root), snapshot)) as pool:
        plans: list[tuple[str, str, str, str]] = []
        for relative, record_id, preferred, dre_id, error in pool.map(_plan, relatives, chunksize=256):
            if error:
                summary.failures.append({"path": relative, "error": error})
            else:
                plans.append((relative, record_id, preferred, dre_id))  # type: ignore[arg-type]
        progress(f"Planeamento concluído: {len(plans)} registos, {len(summary.failures)} falhas")

        targets = assign_targets(plans, root=acervo.root)
        jobs = [(relative, targets[relative]) for relative, _, _, _ in plans]
        for index, (relative, action, error) in enumerate(pool.map(_import, jobs, chunksize=128), start=1):
            if error:
                summary.failures.append({"path": relative, "error": error})
            else:
                setattr(summary, action, getattr(summary, action) + 1)
            if index % 10000 == 0:
                progress(f"{index}/{len(jobs)} convertidos")
    return summary
