"""Formato do histórico de versões (`<registo>.versoes.json`), comum a Portugal e à UE.

- `versions`: cada versão, por data, com os atos que a produziram, as modificações e
  a lista ordenada dos fragmentos (artigos, divisões...) em vigor nessa data;
- `fragments`: cada versão de cada fragmento uma única vez, já em Markdown.

O texto de qualquer versão é a concatenação dos seus fragmentos.
"""

from __future__ import annotations

from typing import Any

from leis_portugal.domain.record import VersionHistory, VersionHistoryEntry


HISTORY_SCHEMA = "leis-portugal/versoes/1"


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
