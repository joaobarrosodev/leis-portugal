"""Marcas de vigência por regra (`consolidacao/vigencia.py`)."""

import sys
from pathlib import Path

import pytest


PASTA = Path(__file__).resolve().parents[1] / "consolidacao"
if not (PASTA / "vigencia.py").exists():
    pytest.skip("consolidacao/ não está nesta cópia", allow_module_level=True)
sys.path.insert(0, str(PASTA))

import vigencia  # noqa: E402


def test_ultramar_so_territorio_e_sem_regimes_pessoais():
    assert vigencia.motivo_ultramar("Decreto n.º 572/72", "Aprova o Estatuto da Polícia de Segurança Pública de Moçambique").startswith("é um diploma para os territórios")
    assert "Macau" in vigencia.motivo_ultramar("Decreto-Lei n.º 411/70", "Regula o exercício das funções de crédito na província de Macau")
    assert vigencia.motivo_ultramar("Decreto n.º 52/75", "Harmoniza os regimes da aposentação dos servidores civis do Estado em serviço nos territórios ultramarinos") is None
    assert vigencia.motivo_ultramar("Portaria n.º 22869", "Torna extensivo às províncias ultramarinas o novo Código Civil") is None
    assert vigencia.motivo_ultramar("Decreto-Lei n.º 1/70", "Regula o arrendamento urbano") is None


def test_revogacao_registada_noutro_registo():
    p = vigencia.padrao_revogacao("Decreto-Lei n.º 158/96", "decreto-lei")
    assert p.search("Revogado o Decreto-Lei n.º 158/96, de 3 de Setembro, na redacção do presente diploma, pelo DEC LEI.47/2005.24.02.2005.MFAP")
    assert p.search("Revogado o Dec Lei 158/96, de 3-Set, pelo DEC LEI.47/2005")
    assert not p.search("Revogado o art. 24.º do Decreto-Lei n.º 158/96, pelo DEC LEI.1/2000")
    assert not p.search("Revogado o Decreto-Lei n.º 158/97, pelo DEC LEI.1/2000")
    q = vigencia.padrao_revogacao("Portaria n.º 132/2009", "portaria")
    assert q.search("Revogada, a partir de 29.04.2013, a Port 132/2009, de 30 de janeiro, com as alterações introduzidas pelo presente")


def test_diploma_que_revoga():
    assert vigencia._pelo("Revogada pelo(a) Portaria n.º 207/2017 - Diário da República n.º 132/2017, Série I") == "Portaria n.º 207/2017"
    assert vigencia._pelo("Revogada a concessão atribuída pelo presente diploma, pela PORT.188/99.1999.03.20.MECO, DR.IS-B [67]") == "PORT.188/99.1999.03.20.MECO"
    assert vigencia._pelo("Revogado, com as alterações introduzidas pelo DR 1/2002 de 03-Jan, pelo DEC LEI.39/2008.07.03.2008.MEI") == "DEC LEI.39/2008.07.03.2008.MEI"


def _registo(raiz, caminho, id_, data, sumario, corpo_, relacoes=None, acts=()):
    import json
    md = raiz / caminho
    md.parent.mkdir(parents=True, exist_ok=True)
    rel = "".join(f"- type: amended_by\n  target: {a}\n  date: '{d}'\n  label: {l}\n" for a, d, l in relacoes or [])
    md.write_text(f"---\nid: {id_}\ntitle: T {id_}\npublication_date: '{data}'\nsummary: {sumario}\n"
                  f"relationships:{chr(10) + rel if rel else ' []' + chr(10)}---\n\n{corpo_}\n", encoding="utf-8")
    versoes = {"versions": [{"acts": []}, {"acts": [{"id": a} for a in acts]}]}
    md.with_name(md.name[:-3] + ".versoes.json").write_text(json.dumps(versoes), encoding="utf-8")


def test_renovacao_vista_pela_consolidacao_nao_fica_em_falta(tmp_path, monkeypatch):
    """Uma renovação que a consolidação já viu não está em falta; um acórdão com o mesmo número de
    processo, ou um registo que só bate com uma gralha do sumário, também não. Todos continuam a
    impedir a marca."""
    monkeypatch.setattr(vigencia, "RAIZ", tmp_path)
    _registo(tmp_path, "a.md", "alvo", "2004-05-03", "Cria a zona (processo n.º 2945-DGF)",
             "1.º É criada a zona de caça municipal de Alqueva 1 (processo n.º 2954-DGF), pelo período de seis anos.",
             [("renov", "2010-06-25", "Renovada por seis anos a zona de caça criada pelo presente diploma")])
    _registo(tmp_path, "renov.md", "renov", "2010-06-25", "Renova a zona de caça", "Renova a zona de caça (processo n.º 2954-DGF).")
    _registo(tmp_path, "acordao.md", "acordao", "2025-06-30", "sem que tenha sido prorrogado o prazo", "processo n.º 2954/11.4PBEVR")
    _registo(tmp_path, "outra.md", "outra", "2008-11-03", "Renova a zona de caça", "a zona de caça (processo n.º 2945-AFN) é renovada.")
    processos = tmp_path / "processos.txt"
    processos.write_text("renov.md:1:processo n.º 2954\nacordao.md:1:processo n.º 2954\noutra.md:1:processo n.º 2945\n", encoding="utf-8")
    consolidados = {"alvo": {"id": "alvo", "titulo": "T alvo", "classe": "caca", "certeza": "alta", "prazo_anos": 6,
                             "renovavel": False, "fim_estimado": "2010-05-03", "caminho": "a.md", "publicacao": "2004-05-03"}}

    marcas, em_falta = vigencia.caca_prazo(consolidados, processos, vistos={"alvo": {"renov"}})
    assert marcas == {} and em_falta == []

    marcas, em_falta = vigencia.caca_prazo(consolidados, processos, vistos={})
    assert marcas == {}
    assert [m["alterador"] for m in em_falta] == ["renov"]
