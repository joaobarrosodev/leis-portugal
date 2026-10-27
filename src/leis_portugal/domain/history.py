"""Formato do histórico de versões (`<registo>.versoes.json`), comum a Portugal e à UE.

- `versions`: cada versão, por data, com os atos que a produziram, as modificações e
  a lista ordenada dos fragmentos (artigos, divisões...) em vigor nessa data;
- `fragments`: cada versão de cada fragmento uma única vez, já em Markdown.

O texto de qualquer versão é a concatenação dos seus fragmentos.

Num histórico grande (acima de `HISTORY_MAX_BYTES`), os fragmentos vão para blocos
`<registo>.versoes/001.json`, `002.json`… de até `FRAGMENT_BLOCK_BYTES`, e o
`<registo>.versoes.json` fica um índice: os mesmos campos, com `fragment_blocks` (os
caminhos dos blocos, relativos à pasta do índice) no lugar de `fragments`.
"""

from __future__ import annotations

import json
from typing import Any

from leis_portugal.domain.record import VersionHistory, VersionHistoryEntry


HISTORY_SCHEMA = "leis-portugal/versoes/1"
FRAGMENT_BLOCK_SCHEMA = "leis-portugal/versoes-bloco/1"
# O GitHub recomenda ficheiros abaixo de 50 MB; acima disto o histórico é dividido.
HISTORY_MAX_BYTES = 50_000_000
FRAGMENT_BLOCK_BYTES = 20_000_000


def render_version(history: dict[str, Any], version: dict[str, Any], *, title: str) -> str:
    fragments = history["fragments"]
    blocks = [fragments[key]["markdown"] for key in version["fragments"] if fragments[key]["markdown"]]
    return "\n\n".join([f"# {title}", *blocks]).strip() + "\n"


def version_at(history: dict[str, Any], when: str) -> dict[str, Any] | None:
    """Versão em vigor numa data (a última com data <= `when`)."""
    candidates = [version for version in history["versions"] if version["date"] <= when]
    return candidates[-1] if candidates else None


def summarize(history: dict[str, Any], file_name: str) -> VersionHistory:
    """Resumo para o front matter do registo (`version_history`)."""
    return VersionHistory(
        file=file_name,
        count=len(history["versions"]),
        source_lastmod=history.get("source_lastmod"),
        versions=[
            VersionHistoryEntry(
                date=version["date"],
                amending=version["acts"][0]["id"] if version["acts"] else None,
                amending_title="; ".join(act["title"] for act in version["acts"] if act.get("title")) or None,
                changes=version["changes"][:40],
            )
            for version in history["versions"]
        ],
    )


def fragment_sizes(fragments: dict[str, Any]) -> dict[str, int]:
    """Bytes (aproximados) de cada fragmento no JSON gravado."""
    return {key: len(json.dumps({key: fragment}, ensure_ascii=False, indent=1).encode("utf-8")) for key, fragment in fragments.items()}


def split_fragments(fragments: dict[str, Any], sizes: dict[str, int], max_bytes: int) -> list[dict[str, Any]]:
    """Divide os fragmentos, pela ordem, em blocos de até `max_bytes`.

    A ordem é a da primeira versão em que cada fragmento aparece: as versões novas
    acrescentam fragmentos no fim e os blocos anteriores ficam iguais. Um fragmento
    maior do que `max_bytes` fica sozinho num bloco.
    """
    blocks: list[dict[str, Any]] = []
    used = max_bytes
    for key, fragment in fragments.items():
        if used + sizes[key] > max_bytes:
            blocks.append({})
            used = 0
        blocks[-1][key] = fragment
        used += sizes[key]
    return blocks
