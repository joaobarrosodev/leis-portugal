"""Aviso de vigência revista no RAG (`rag/vigencia.py`, `rag.pesquisa.Pesquisa._avisos`)."""

import json

from rag import pesquisa as pesquisa_mod
from rag import vigencia


MARCA = {"id": "pt:dre:1:por", "marca": "nao_vigora", "motivo": "foi revogado pela Portaria n.º 506/2018.", "prova": [], "fonte": "regra"}


def test_marcas_e_aviso(tmp_path):
    ficheiro = tmp_path / "vigencia-revista.jsonl"
    ficheiro.write_text(json.dumps(MARCA, ensure_ascii=False) + "\n", encoding="utf-8")
    assert vigencia.marcas(ficheiro)["pt:dre:1:por"]["marca"] == "nao_vigora"
    assert vigencia.aviso(MARCA) == "O DRE dá-o como em vigor, mas foi revogado pela Portaria n.º 506/2018."
    anterior = {"marca": "regime_anterior", "motivo": "confirmar a adequação do curso."}
    assert vigencia.aviso(anterior).startswith("Regime anterior ao Decreto-Lei n.º 74/2006")


def test_prior_desligado_por_omissao(monkeypatch):
    monkeypatch.delenv("RAG_VIGENCIA_PRIOR", raising=False)
    assert vigencia.prior_ligado() is False
    monkeypatch.setenv("RAG_VIGENCIA_PRIOR", "1")
    assert vigencia.prior_ligado() is True


def _pesquisa(estado: str, relacoes=()):
    p = pesquisa_mod.Pesquisa.__new__(pesquisa_mod.Pesquisa)
    p.vigencia = {MARCA["id"]: MARCA}
    p.vigencia_prior = False
    p.documento = lambda _id: {"legal_status": estado, "versao": "consolidated", "com_historico": 1, "titulo": "Portaria n.º 210/2007"}
    p.relacoes = lambda _id: list(relacoes)
    p.julgamentos = lambda _r: []
    return p


def _resultado():
    return pesquisa_mod.Resultado(1, MARCA["id"], "Portaria n.º 210/2007", "", "1.º", "", "1.º", "Portaria n.º 210/2007, 1.º", "Texto.", "", None, None)


def test_aviso_nos_resultados_marcados():
    r = _resultado()
    _pesquisa("in_force")._avisos(r, "2026-11-19")
    assert r.avisos == ["O DRE dá-o como em vigor, mas foi revogado pela Portaria n.º 506/2018."]


def test_sem_aviso_repetido_quando_o_dre_ja_o_da_como_revogado():
    r = _resultado()
    _pesquisa("repealed")._avisos(r, "2026-11-19")
    assert r.avisos == ["Diploma sem vigência (revogado ou caducado, segundo o DRE)."]


def test_aviso_por_confirmar():
    from rag import vigencia
    assert vigencia.aviso({"marca": "por_confirmar", "motivo": "o texto regula só o ano de 1993, que já passou."}) == \
        "Vigência por confirmar: o texto regula só o ano de 1993, que já passou."
