"""Escolha dos diplomas a repedir com os reparos do verificador (`consolidacao/reparos.py`)."""

import sys
from pathlib import Path

import pytest


PASTA = Path(__file__).resolve().parents[1] / "consolidacao"
if not (PASTA / "reparos.py").exists():
    pytest.skip("consolidacao/ não está nesta cópia", allow_module_level=True)
sys.path.insert(0, str(PASTA))

import reparos  # noqa: E402


def _diploma(falta=(), fora="sem alterações"):
    return {"id": "x", "instrucoes_em_falta": list(falta), "artigos_a_mais": [], "artigos_em_falta": [], "fora_dos_artigos": fora}


def _artigo(motivo, veredicto="errado"):
    return {"id": "x", "artigo": "Artigo 5.º", "veredicto": veredicto, "motivo": motivo, "texto_esperado": ""}


def test_anexo_de_texto_nao_e_imagem():
    linhas = [_artigo("No estatuto anexo, o n.º 2 do artigo 5.º devia ter a nova redação"), _diploma()]
    assert reparos.reparos(linhas) is not None


def test_quadro_em_pdf_e_imagem():
    linhas = [_artigo("certo", "certo"), _diploma(["Portaria 1128/92: anexo I substituído (quadros só em PDF)"])]
    assert reparos.reparos(linhas) is None


def test_um_reparo_de_imagem_basta_para_ficar_de_fora():
    linhas = [_artigo("falta a alínea c)"), _diploma(["o mapa II passa a ser o constante do documento original"])]
    assert reparos.reparos(linhas) is None


def test_sem_reparos_fica_de_fora():
    assert reparos.reparos([_artigo("igual", "certo"), _diploma()]) is None


def test_reparos_levam_o_motivo_e_a_instrucao():
    texto = reparos.reparos([_artigo("falta a alínea c)"), _diploma(["DL 5/95, art. 2.º: revoga o n.º 3"])])
    assert "Artigo 5.º: errado. falta a alínea c)" in texto
    assert "DL 5/95, art. 2.º: revoga o n.º 3" in texto


def test_caminho():
    corrido, outros = {"a"}, {"a", "b"}
    assert reparos.caminho("a", corrido, outros) == "corrido"
    assert reparos.caminho("b", corrido, outros) == "completo"
    assert reparos.caminho("c", corrido, outros) is None


def test_ficam_de_fora_os_repedidos_exclusoes_e_verificados(monkeypatch):
    falha = [_artigo("falta a alínea c)"), _diploma()]
    monkeypatch.setattr(reparos, "ultima_ronda", lambda: {i: falha for i in "abcde"})
    monkeypatch.setattr(reparos.acervo, "verificados", lambda: {"a": {}})
    monkeypatch.setattr(reparos, "_juntados", lambda nome: {"b", "c", "d", "e"} if nome == "completo" else set())
    monkeypatch.setattr(reparos.texto_mod, "exclusoes", lambda: {"b": "revogado"})
    monkeypatch.setattr(reparos.texto_mod, "gigantes", lambda: {"c"})
    monkeypatch.setattr(reparos, "repedidos", lambda: {"d"})
    monkeypatch.setattr(reparos, "PASTA", PASTA)
    assert set(reparos.candidatos()) == {"e"}
