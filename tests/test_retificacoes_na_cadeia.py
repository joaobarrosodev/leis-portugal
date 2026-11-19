"""As declarações de retificação (`corrected_by`) entram na cadeia da consolidação (achado do bloco 3)."""

import sqlite3
import sys
from pathlib import Path

import pytest


PASTA = Path(__file__).resolve().parents[1] / "consolidacao"
if not (PASTA / "selecionar.py").exists():
    pytest.skip("consolidacao/ não está nesta cópia", allow_module_level=True)
sys.path.insert(0, str(PASTA))

import acervo  # noqa: E402
import cegas  # noqa: E402
import selecionar  # noqa: E402
from alteracoes import ler  # noqa: E402
from texto import dividir  # noqa: E402


def _db():
    db = sqlite3.connect(":memory:")
    db.execute("create table documentos (id, title, path, text_quality, document_type, legal_status, publication_date, version_kind, jurisdiction)")
    db.execute("create table relacoes (source_id, target, target_id, date, label, type)")
    linhas = [
        ("o", "Portaria n.º 1/90", "o.md", "texto", "portaria", "in_force", "1990-01-10", "original", "portugal"),
        ("alt", "Portaria n.º 9/91", "alt.md", "texto", "portaria", "in_force", "1991-01-01", "original", "portugal"),
        ("ret", "Declaração de Rectificação n.º 5/90", "ret.md", "texto", "declaracao-retificacao", "in_force", "1990-02-20", "original", "portugal"),
        ("ret2", "Declaração", "ret2.md", "texto", "declaracao", "in_force", "1991-03-01", "original", "portugal"),
    ]
    db.executemany("insert into documentos values (?, ?, ?, ?, ?, ?, ?, ?, ?)", linhas)
    db.executemany("insert into relacoes values (?, ?, ?, ?, ?, ?)", [
        ("o", "alt", "alt", None, "Alterado pela PORT.9/91", "amended_by"),
        ("o", "ret", "ret", "1990-02-20", "Rectificada pela DECL-RECT.5/90", "corrected_by"),
        ("o", "ret2", "ret2", "1991-03-01", "Rectificada a Port 9/91, que conferiu nova redacção ao presente diploma", "corrected_by"),
        ("so", "ret", "ret", None, "Rectificado", "corrected_by"),
    ])
    db.execute("insert into documentos values ('so', 'Decreto n.º 2/90', 'so.md', 'texto', 'decreto', 'in_force', '1990-01-01', 'original', 'portugal')")
    return db


def test_selecao_conta_retificacoes_e_poe_as_do_original_primeiro():
    por_id = {r["id"]: r for r in selecionar.selecionar_todos(_db())}
    assert set(por_id) == {"o", "so"}  # um diploma só com retificações também entra
    cadeia = [(a["id"], a.get("retificacao", False)) for a in por_id["o"]["alteradores"]]
    # A retificação do original vai primeiro; a que retifica o alterador fica pela data, depois dele.
    assert cadeia == [("ret", True), ("alt", False), ("ret2", True)]


def test_rotulo_que_retifica_o_alterador():
    assert selecionar.retifica_outro("Rectificada a Port 681/86 de 13-Nov, que conferiu nova redacção ao presente diploma")
    assert selecionar.retifica_outro("Rectificado o art. único do DR 34/90 de 03-Nov, na redacção que conferiu")
    assert not selecionar.retifica_outro("Rectificado pela DECL.DD2657.1988.05.16.PCM")
    assert not selecionar.retifica_outro("Retificados o nº 5 do art. 52º e nº 1 do art. 57º, pela DECL-RECT.14/2012")


def test_leitura_de_pares_em_paragrafos_seguidos():
    ret = (
        "# Declaração\n\nDeclara-se que o Decreto Regulamentar n.º 84-A/2007 saiu com uma inexactidão, que assim se rectifica:\n\n"
        "No n.º 2 do artigo 52.º, onde se lê:\n\n«até 31 de Janeiro de 2008.»\n\ndeve ler-se:\n\n«até 31 de Março de 2008.»\n\n"
        "No artigo 53.º, onde se lê: «prazo de 10 dias», deve ler-se: «prazo de 15 dias».\n"
    )
    original = dividir("# DR\n\n###### Artigo 52.º — C\n\n2 - Até 31 de Janeiro de 2008.\n\n###### Artigo 53.º — P\n\nNo prazo de 10 dias.\n")
    leitura = ler(ret, "Decreto Regulamentar n.º 84-A/2007", original)
    assert [(i.tipo, str(i.alvos[0]), i.antes, i.depois) for i in leitura.instrucoes] == [
        ("retificar", "n.º 2 do artigo 52.º", "até 31 de Janeiro de 2008.", "até 31 de Março de 2008."),
        ("retificar", "artigo 53.º", "prazo de 10 dias", "prazo de 15 dias"),
    ]


def test_verificador_ve_sempre_as_retificacoes():
    registo = {"alteradores": [{"id": "alt", "path": "a.md"}, {"id": "ret", "path": "r.md", "retificacao": True}, {"id": "ret3", "retificacao": True}]}
    assert [a["id"] for a in cegas.alteradores_vistos({"alteradores_ids": ["alt"]}, registo)] == ["alt", "ret"]


def test_retificacao_nao_adia_a_versao():
    original = {"publication_date": "1990-01-10", "entry_into_force_dates": ["1990-01-15"]}
    alt = ({"id": "alt"}, {"publication_date": "1991-01-01", "entry_into_force_dates": ["1991-01-06"]})
    ret = ({"id": "ret", "retificacao": True}, {"publication_date": "1992-05-01"})
    assert acervo.data_da_versao([ret, alt], original) == "1991-01-06"
    assert acervo.data_da_versao([ret], original) == "1990-01-15"
