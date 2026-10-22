"""Peças partilhadas pelos serviços: políticas de gravação, progresso e execução paralela."""

from __future__ import annotations

import threading
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar

from leis_portugal.domain.record import LegalRecord
from leis_portugal.domain.relations import eu_relationships
from leis_portugal.infrastructure.repository import SavePolicy


Progress = Callable[[str], None]
T = TypeVar("T")
C = TypeVar("C")


def silent(_message: str) -> None:
    return None


def _add_eu_relationships(record: LegalRecord, body: str) -> None:
    # Atos da UE citados ou transpostos, detetados no texto que fica no registo.
    record.add_relationships(eu_relationships(body))


# Diplomas portugueses: juntam-se todas as relações e respeita-se a precedência.
PORTUGUESE_POLICY = SavePolicy(enrich=_add_eu_relationships)
# Atos da UE: as relações do CELLAR são substituídas a cada recolha; mantêm-se só as
# ligações a diplomas portugueses (escritas por `link`).
EU_POLICY = SavePolicy(keep_relationship=lambda relation: relation.target.startswith("pt:"), respect_precedence=False)


def run_parallel(
    items: Iterable[T],
    work: Callable[[T, C], str],
    *,
    context: Callable[[], C],
    workers: int,
    progress: Progress = silent,
) -> None:
    """Executa `work(item, contexto)` para cada item, com um contexto por thread.

    O contexto (p. ex. uma sessão HTTP) não é partilhado entre threads. `work` devolve
    a mensagem de progresso e trata os seus próprios erros."""
    items = list(items)
    local = threading.local()
    lock = threading.Lock()
    done = 0

    def run(item: T) -> None:
        nonlocal done
        if not hasattr(local, "context"):
            local.context = context()
        message = work(item, local.context)
        with lock:
            done += 1
            progress(f"[{done}/{len(items)}] {message}")

    if workers <= 1:
        for item in items:
            run(item)
        return
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(run, items))
