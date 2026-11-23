"""Textos transcritos do PDF oficial para registos em que a fonte serve o texto de outro diploma.

O DRE serve, nalguns registos, o texto do diploma vizinho: no 304721 (Decreto-Lei n.º 41561, de 1958) o
`Texto` e o `TextoFormatado` são os do Decreto-Lei n.º 41560. A recolha copia o que vem. Para estes
registos, o texto certo é transcrito do PDF oficial, conferido à vista, e fica em
`reports/textos-manuais/`; a lista com a prova de cada um está em `reports/textos-manuais.jsonl`.

`Acervo.write` e `Acervo.save` usam este texto em vez do que a recolha traz (ver `apply_manual_text`):
uma nova recolha destes registos atualiza os metadados mas não volta a pôr o texto errado.

Cada linha do JSONL:
- `id`: id do registo;
- `titulo`: para quem lê a lista;
- `motivo`: o que estava errado (p. ex. «o DRE serve o texto do Decreto-Lei n.º 41560»);
- `texto_servido_pela_fonte`: id do diploma cujo texto a fonte serve (opcional); a relação `cites` para ele,
  que vinha da ligação no texto errado, sai do registo;
- `pdf_url`, `pdf_sha256`, `paginas`: o PDF oficial de onde veio o texto;
- `conferido_em`: data (AAAA-MM-DD) em que o texto foi conferido com o PDF;
- `corpo`: caminho do texto, relativo à raiz (`reports/textos-manuais/…md`), com o título `# …`;
- `corpo_sha256`: sha256 do texto, para se notar qualquer mudança ao ficheiro.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from leis_portugal.domain.record import LegalRecord
from leis_portugal.errors import StorageError


MANUAL_TEXTS_FILE = "reports/textos-manuais.jsonl"
MANUAL_NOTE_PREFIX = "Texto transcrito do PDF oficial"
_REQUIRED = ("id", "motivo", "pdf_url", "pdf_sha256", "paginas", "conferido_em", "corpo", "corpo_sha256")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class ManualText:
    id: str
    motivo: str
    pdf_url: str
    pdf_sha256: str
    paginas: str
    conferido_em: str
    corpo: str
    corpo_sha256: str
    body: str
    texto_servido_pela_fonte: str | None = None

    def note(self) -> str:
        return (
            f"{MANUAL_NOTE_PREFIX} ({self.pdf_url}, p. {self.paginas}), conferido em {self.conferido_em}: "
            f"{self.motivo}. Lista e prova em {MANUAL_TEXTS_FILE}."
        )


def body_sha256(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def load_manual_texts(root: Path) -> dict[str, ManualText]:
    """A lista de `MANUAL_TEXTS_FILE`, com o texto de cada entrada; vazia se o ficheiro não existir.

    Uma entrada incompleta, ou com o texto diferente do `corpo_sha256`, é um erro: não se grava um
    registo com um texto que não foi o conferido."""
    path = Path(root) / MANUAL_TEXTS_FILE
    if not path.exists():
        return {}
    texts: dict[str, ManualText] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        entry = json.loads(line)
        missing = [name for name in _REQUIRED if not entry.get(name)]
        if missing:
            raise StorageError(f"{MANUAL_TEXTS_FILE}:{number}: faltam {', '.join(missing)}")
        if not _DATE.match(entry["conferido_em"]) or not _SHA256.match(entry["pdf_sha256"]) or not _SHA256.match(entry["corpo_sha256"]):
            raise StorageError(f"{MANUAL_TEXTS_FILE}:{number}: data ou sha256 mal escritos")
        if entry["id"] in texts:
            raise StorageError(f"{MANUAL_TEXTS_FILE}:{number}: {entry['id']} repetido")
        body_path = Path(root) / entry["corpo"]
        if not body_path.exists():
            raise StorageError(f"{MANUAL_TEXTS_FILE}:{number}: falta o texto {entry['corpo']}")
        body = body_path.read_text(encoding="utf-8")
        if body_sha256(body) != entry["corpo_sha256"]:
            raise StorageError(f"{MANUAL_TEXTS_FILE}:{number}: o texto {entry['corpo']} não é o conferido (sha256 diferente)")
        texts[entry["id"]] = ManualText(
            id=entry["id"], motivo=entry["motivo"], pdf_url=entry["pdf_url"], pdf_sha256=entry["pdf_sha256"],
            paginas=str(entry["paginas"]), conferido_em=entry["conferido_em"], corpo=entry["corpo"],
            corpo_sha256=entry["corpo_sha256"], body=body, texto_servido_pela_fonte=entry.get("texto_servido_pela_fonte"),
        )
    return texts


def apply_manual_text(record: LegalRecord, body: str, texts: dict[str, ManualText]) -> str:
    """O texto a gravar: o transcrito, se o registo estiver na lista; senão, o que veio.

    Junta a nota de proveniência (uma só) e tira a relação `cites` para o diploma cujo texto a fonte serve."""
    manual = texts.get(record.id)
    if manual is None:
        return body
    record.notes = [note for note in record.notes if not note.startswith(MANUAL_NOTE_PREFIX)] + [manual.note()]
    if manual.texto_servido_pela_fonte:
        record.relationships = [
            relation for relation in record.relationships
            if not (relation.type == "cites" and relation.target == manual.texto_servido_pela_fonte)
        ]
    return manual.body
