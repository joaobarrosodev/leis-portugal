"""Peças comuns às fontes de decisões (CNPD, Tribunal Constitucional)."""

from __future__ import annotations

import hashlib
import re
from datetime import date


MONTHS = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}
_WRITTEN_DATE = re.compile(
    r"\b(\d{1,2})\s*(?:\.º|º)?\s+de\s+(" + "|".join(MONTHS) + r")\s+de\s+(\d{4})\b", re.IGNORECASE
)


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def written_dates(text: str) -> list[date]:
    """Datas por extenso ("12 de março de 2010") pela ordem em que aparecem."""
    found: list[date] = []
    for day, month, year in _WRITTEN_DATE.findall(text):
        try:
            found.append(date(int(year), MONTHS[month.lower()], int(day)))
        except ValueError:
            continue
    return found


def signature_date(text: str, *, year: int | None = None) -> str | None:
    """A data da assinatura: a última data por extenso do texto (no ano indicado, se dado)."""
    candidates = [item for item in written_dates(text[-3000:]) if year is None or item.year == year]
    return candidates[-1].isoformat() if candidates else None


def reflow(text: str) -> str:
    """Junta as linhas partidas a meio de uma frase (texto de PDF com quebras de linha fixas)."""
    lines = text.split("\n")
    merged: list[str] = []
    for line in lines:
        if (
            merged
            and line
            and merged[-1]
            and not re.search(r"[.:;!?»)]$", merged[-1])
            and re.match(r"[a-zà-ÿ(«\"“0-9]", line)
        ):
            # Um hífen no fim da linha fica (p. ex. "decreto-" + "lei"): sem dicionário não
            # se distingue a translineação de uma palavra composta.
            merged[-1] += ("" if merged[-1].endswith("-") else " ") + line
        else:
            merged.append(line)
    return "\n".join(merged)
