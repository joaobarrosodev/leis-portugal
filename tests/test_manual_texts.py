"""Textos transcritos do PDF oficial: a recolha não volta a pôr o texto que a fonte serve por engano."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import record_dict
from leis_portugal.cli import main
from leis_portugal.domain.record import LegalRecord
from leis_portugal.errors import StorageError
from leis_portugal.infrastructure.manual_texts import MANUAL_NOTE_PREFIX, body_sha256, load_manual_texts
from leis_portugal.infrastructure.repository import Acervo

ERRADO = "# Decreto-Lei n.º 41561\n\n[Decreto-Lei n.º 41560](https://diariodarepublica.pt/dr/detalhe/decreto-lei/41560-1958-304720)\n\nArtigo 1.º O artigo 84.º do Código Administrativo passa a ter a seguinte redacção:\n"
CERTO = "# Decreto-Lei n.º 41561\n\nArtigo 1.º São isentos de toda e qualquer contribuição, taxa ou imposto.\n"


def _record() -> LegalRecord:
    return LegalRecord.from_dict(record_dict(
        "pt:dre:304721:por", title="Decreto-Lei n.º 41561", official_number="41561", publication_date="1958-03-17",
        identifiers={"dre": "304721", "internal": "pt:dre:304721:por"},
        relationships=[
            {"type": "cites", "target": "pt:dre:304720:por", "label": None, "source": None},
            {"type": "amended_by", "target": "pt:dre:438274:por", "label": None, "source": None},
        ],
    ))


def _manual(root: Path, body: str = CERTO, **overrides) -> None:
    (root / "reports/textos-manuais").mkdir(parents=True, exist_ok=True)
    (root / "reports/textos-manuais/decreto-lei-41561.md").write_text(body, encoding="utf-8")
    entry = {
        "id": "pt:dre:304721:por", "titulo": "Decreto-Lei n.º 41561", "motivo": "o DRE serve o texto do Decreto-Lei n.º 41560",
        "texto_servido_pela_fonte": "pt:dre:304720:por",
        "pdf_url": "https://files.diariodarepublica.pt/1s/1958/03/05500/01530154.pdf", "pdf_sha256": "a" * 64,
        "paginas": "153-154", "conferido_em": "2026-11-23", "corpo": "reports/textos-manuais/decreto-lei-41561.md",
        "corpo_sha256": body_sha256(CERTO),
    } | overrides
    (root / "reports/textos-manuais.jsonl").write_text(json.dumps(entry, ensure_ascii=False) + "\n", encoding="utf-8")


def test_a_recolha_grava_o_texto_transcrito_e_nao_o_da_fonte(repo_root: Path):
    _manual(repo_root)
    acervo = Acervo(repo_root)
    path = acervo.save(_record(), ERRADO).path
    record, body = acervo.read(path)
    assert body.strip() == CERTO.strip()
    assert [note for note in record.notes if note.startswith(MANUAL_NOTE_PREFIX)] == [
        f"{MANUAL_NOTE_PREFIX} (https://files.diariodarepublica.pt/1s/1958/03/05500/01530154.pdf, p. 153-154), conferido em "
        "2026-11-23: o DRE serve o texto do Decreto-Lei n.º 41560. Lista e prova em reports/textos-manuais.jsonl."
    ]
    # A ligação ao diploma vizinho vinha do texto errado; as outras relações ficam.
    assert [(r.type, r.target) for r in record.relationships] == [("amended_by", "pt:dre:438274:por")]

    # Uma nova recolha, com o mesmo texto errado da fonte, não muda nada.
    assert acervo.save(_record(), ERRADO).action == "unchanged"
    record, body = acervo.read(path)
    assert body.strip() == CERTO.strip()
    assert sum(note.startswith(MANUAL_NOTE_PREFIX) for note in record.notes) == 1


def test_a_escrita_direta_tambem_respeita_o_texto_transcrito(repo_root: Path):
    acervo = Acervo(repo_root)
    path = acervo.save(_record(), ERRADO).path
    _manual(repo_root)
    acervo = Acervo(repo_root)
    record, body = acervo.read(path)
    assert acervo.write(record, body, path)
    assert acervo.read(path)[1].strip() == CERTO.strip()
    # Registos fora da lista gravam-se como vêm.
    other = LegalRecord.from_dict(record_dict("pt:dre:304720:por", title="Decreto-Lei n.º 41560", official_number="41560",
                                              publication_date="1958-03-17", identifiers={"dre": "304720", "internal": "pt:dre:304720:por"}))
    other_path = acervo.save(other, ERRADO).path
    assert acervo.read(other_path)[1].strip() == ERRADO.strip()


def test_o_comando_grava_os_textos_da_lista(repo_root: Path, capsys):
    acervo = Acervo(repo_root)
    path = acervo.save(_record(), ERRADO).path
    _manual(repo_root)
    assert main(["--root", str(repo_root), "textos-manuais"]) == 0
    assert "gravado: data/portugal/decretos-leis/1958/" in capsys.readouterr().out
    assert Acervo(repo_root).read(path)[1].strip() == CERTO.strip()
    assert main(["--root", str(repo_root), "textos-manuais"]) == 0
    assert "igual:" in capsys.readouterr().out


def test_um_texto_diferente_do_conferido_e_recusado(repo_root: Path):
    _manual(repo_root, body=CERTO + "\nAcrescento.\n")
    with pytest.raises(StorageError, match="não é o conferido"):
        load_manual_texts(repo_root)
    _manual(repo_root, pdf_sha256="")
    with pytest.raises(StorageError, match="faltam pdf_sha256"):
        load_manual_texts(repo_root)
    assert load_manual_texts(repo_root / "sem-lista") == {}
