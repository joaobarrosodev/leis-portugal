"""Aplicação das trocas do respondedor às retificações (`consolidacao/retificacoes_llm.py`)."""

import sys
from pathlib import Path

import pytest


PASTA = Path(__file__).resolve().parents[1] / "consolidacao"
if not (PASTA / "retificacoes_llm.py").exists():
    pytest.skip("consolidacao/ não está nesta cópia", allow_module_level=True)
sys.path.insert(0, str(PASTA))

import retificacoes_llm as rl  # noqa: E402


def test_troca_confere_a_linha_e_repoe_ligacoes():
    linhas = ["# P", "", "###### Artigo 3.º — Prazo", "", "1 - Nos termos da [Lei n.º 1/90](https://x/1), o prazo é de 10 dias."]
    feitas = rl.trocar(linhas, [{"linha": 4, "texto_atual": "1 - Nos termos da Lei n.º 1/90, o prazo é de 10 dias.", "texto_novo": "1 - Nos termos da Lei n.º 1/90, o prazo é de 15 dias."}])
    assert linhas[4] == "1 - Nos termos da [Lei n.º 1/90](https://x/1), o prazo é de 15 dias."
    assert feitas[0]["artigo"] == "3"


def test_recusas_e_supressao():
    linhas = ["###### Artigo 1.º — A", "", "a) Texto;", "b) Outro."]
    with pytest.raises(rl.Recusa):  # a linha mudou desde a entrada
        rl.trocar(list(linhas), [{"linha": 2, "texto_atual": "a) Texto antigo;", "texto_novo": "a) Novo;"}])
    with pytest.raises(rl.Recusa):  # um título deixava de o ser
        rl.trocar(list(linhas), [{"linha": 0, "texto_atual": "###### Artigo 1.º — A", "texto_novo": "Artigo 1.º — A"}])
    copia = list(linhas)
    rl.trocar(copia, [{"linha": 3, "texto_atual": "b) Outro.", "texto_novo": ""}])
    assert copia[3] == ""


def test_contexto_da_ronda_seguinte():
    """Na ronda r2 o verificador vê onde fica um parágrafo curto e se foi reescrito depois."""
    linhas = ["## ANEXO V — Instituto", "", "3.º ano", "", "2.º ciclo", "", "QUADRO N.º 4", "",
              "###### Artigo 8.º — Coadjuvação", "", "3 - de que possa resultatar a sua perturbação.", "",
              "> Alterado pelo/a [Decreto-Lei n.º 364/93](https://x/364), publicado em 1993-10-22.", "", "4 - Outro."]
    c = rl.contexto(linhas, 4)
    assert c["titulo_acima"] == "## ANEXO V — Instituto"
    assert c["antes"] == ["## ANEXO V — Instituto", "3.º ano"] and c["depois"][0] == "QUADRO N.º 4"
    assert c["reescrito_depois"] is None
    c = rl.contexto(linhas, 10)
    assert c["titulo_acima"].startswith("###### Artigo 8.º")
    assert c["reescrito_depois"] == "> Alterado pelo/a Decreto-Lei n.º 364/93, publicado em 1993-10-22."
