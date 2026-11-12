"""Texto de um PDF oficial, para fontes que só publicam PDF (p. ex. a CNPD).

Usa a biblioteca `pypdf` quando está instalada; senão, o utilitário PDFKit do macOS
compilado de `scripts/pdftext.swift` (caminho em `LEIS_PORTUGAL_PDFTEXT`), que faz OCR
das páginas digitalizadas com o Vision (desligado com `LEIS_PORTUGAL_OCR=0`). Sem nenhum
dos dois, `pdf_text` devolve None e o registo fica só com os metadados e a ligação ao PDF.
"""

from __future__ import annotations

import io
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass


def _with_pypdf(content: bytes) -> str | None:
    try:
        import pypdf  # type: ignore[import-not-found]
    except ImportError:
        return None
    reader = pypdf.PdfReader(io.BytesIO(content))
    return "\n\f\n".join(page.extract_text() or "" for page in reader.pages)


def _with_pdfkit(content: bytes) -> str | None:
    tool = os.environ.get("LEIS_PORTUGAL_PDFTEXT")
    if not tool or not os.access(tool, os.X_OK):
        return None
    with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
        handle.write(content)
        handle.flush()
        command = [tool, handle.name] + (["--sem-ocr"] if os.environ.get("LEIS_PORTUGAL_OCR") == "0" else [])
        result = subprocess.run(command, capture_output=True, timeout=600, check=False)
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", "replace")


def extractor_available() -> bool:
    try:
        import pypdf  # type: ignore[import-not-found]  # noqa: F401
    except ImportError:
        tool = os.environ.get("LEIS_PORTUGAL_PDFTEXT")
        return bool(tool and os.access(tool, os.X_OK))
    return True


@dataclass(frozen=True)
class PdfText:
    text: str
    # Contagens do utilitário PDFKit/Vision (1.ª linha); o pypdf não as dá.
    pages: int | None = None
    ocr_pages: int = 0
    empty_pages: int = 0


def extract(content: bytes) -> PdfText | None:
    """O texto do PDF, limpo, ou None se não houver extrator ou o PDF não tiver texto
    (digitalização sem OCR)."""
    raw = _with_pypdf(content)
    if raw is None:
        raw = _with_pdfkit(content)
    if raw is None:
        return None
    pages, ocr_pages, empty_pages = None, 0, 0
    marker = re.match(r"%%PAGINAS (\d+) (\d+) (\d+)\n", raw)
    if marker:
        pages, ocr_pages, empty_pages = (int(value) for value in marker.groups())
        raw = raw[marker.end():]
    text = clean_pdf_text(raw)
    if len(re.sub(r"\W", "", text)) < 40:
        return None
    return PdfText(text=text, pages=pages, ocr_pages=ocr_pages, empty_pages=empty_pages)


def pdf_text(content: bytes) -> str | None:
    extracted = extract(content)
    return extracted.text if extracted else None


def clean_pdf_text(raw: str) -> str:
    """Normaliza o texto extraído: sem quebras de página, espaços nem linhas vazias repetidas."""
    lines = [re.sub(r"[ \t ]+", " ", line).strip() for line in raw.replace("\f", "\n").splitlines()]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
