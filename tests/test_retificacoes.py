"""Aplicação por regra das retificações fora da cadeia (`consolidacao/retificacoes.py`)."""

import sys
from pathlib import Path

import pytest


PASTA = Path(__file__).resolve().parents[1] / "consolidacao"
if not (PASTA / "retificacoes.py").exists():
    pytest.skip("consolidacao/ não está nesta cópia", allow_module_level=True)
sys.path.insert(0, str(PASTA))

import retificacoes as rt  # noqa: E402


def _par(antes, depois, localizador=""):
    return {"antes": antes, "depois": depois, "localizador": localizador}


def test_troca_exata_mantem_as_ligacoes_que_nao_mudam():
    linhas = ["# Portaria", "", "1.º Ao abrigo da [Lei n.º 65/77](https://x/65) e da alínea c) do artigo 3.º"]
    troca = rt.aplicar_par(linhas, _par("alínea c) do artigo 3.º", "alínea b) do artigo 3.º", "No n.º 1.º,"))
    assert linhas[2] == "1.º Ao abrigo da [Lei n.º 65/77](https://x/65) e da alínea b) do artigo 3.º"
    assert troca["aprox"] is False


def test_ponto_final_nao_se_duplica():
    linhas = ["Art. 22.º Regime do Decreto-Lei n.º 59/76, de 29 de Janeiro."]
    rt.aplicar_par(linhas, _par("de 29 de Janeiro", "de 23 de Janeiro."))
    assert linhas[0] == "Art. 22.º Regime do Decreto-Lei n.º 59/76, de 23 de Janeiro."


def test_aproximado_muda_so_as_palavras_e_segue_o_separador_da_retificacao():
    linhas = ["2 - Ficam revogadas as seguintes disposições do Decreto-Lei n.º 124/77, de 1 de Abril: o artigo 21.º"]
    rt.aplicar_par(linhas, _par("disposições do Decreto-Lei n.º 124/77, de 1 de Abril:", "disposições do Decreto Regulamentar n.º 24/77, de 1 de Abril:"))
    assert linhas[0] == "2 - Ficam revogadas as seguintes disposições do Decreto Regulamentar n.º 24/77, de 1 de Abril: o artigo 21.º"
    linhas = ["Este Decreto entra imediatamente em vigor."]
    rt.aplicar_par(linhas, _par("Este decreto entra imediatamente em vigor", "Este decreto entra imediatamente em vigor, excepto o artigo 9.º"))
    assert linhas[0] == "Este decreto entra imediatamente em vigor, excepto o artigo 9.º."


def test_recusas():
    artigos = ["###### Artigo 41.º — Isenções", "", "1 - São isentos de selos e emolumentos."]
    with pytest.raises(rt.Recusa):  # o localizador nomeia outro artigo
        rt.aplicar_par(list(artigos), _par("são isentos de selos e emolumentos", "são isentos de selos e custas", "No artigo 324.º,"))
    with pytest.raises(rt.Recusa):  # aparece duas vezes
        rt.aplicar_par(["a) do artigo 3.º", "b) do artigo 3.º"], _par("do artigo 3.º", "do artigo 4.º"))
    with pytest.raises(rt.Recusa):  # renumera o artigo no título
        rt.aplicar_par(["###### Artigo 8.º — Disposições transitórias"], _par("Artigo 8.º — Disposições transitórias", "Artigo 7.º — Disposições transitórias"))
    with pytest.raises(rt.Recusa):  # o localizador nomeia um anexo e o trecho não está num anexo
        rt.aplicar_par(["###### Artigo 66.º — Conteúdos", "", "3 - Os conteúdos do anexo VII."], _par("Os conteúdos do anexo VII", "Os conteúdos funcionais do anexo VII", "No anexo VII,"))


def test_titulo_do_registo_e_epigrafe():
    with pytest.raises(rt.SoMetadados):
        rt.aplicar_par(["# Decreto n.º 683-A/76", "", "Texto."], _par("Decreto n.º 683-A/76", "Decreto-Lei n.º 683-A/76", "No sumário,"))
    linhas = ["###### Artigo 28.º — (Susídio para despesas)", "", "1 - Texto."]
    rt.aplicar_par(linhas, _par("Susídio para despesas", "Subsídio para despesas", "Na epígrafe do artigo 28.º,"))
    assert linhas[0] == "###### Artigo 28.º — (Subsídio para despesas)"


def test_notas_no_fim_do_artigo_ou_a_seguir_ao_paragrafo():
    linhas = ["###### Artigo 1.º", "", "1 - A.", "", "2 - B.", "", "###### Artigo 2.º", "", "C."]
    assert rt._com_notas(linhas, {2: {"> Retificado pelo/a X."}}) == [
        "###### Artigo 1.º", "", "1 - A.", "", "2 - B.", "", "> Retificado pelo/a X.", "", "###### Artigo 2.º", "", "C."]
    sem_artigos = ["# P", "", "1.º A.", "", "2.º B."]
    assert rt._com_notas(sem_artigos, {2: {"> Retificado pelo/a X."}}) == ["# P", "", "1.º A.", "", "> Retificado pelo/a X.", "", "", "2.º B."]


def test_texto_depois_do_articulado_nao_e_de_nenhum_artigo():
    """Um anexo sem título Markdown, ou o que vem depois da promulgação, não é do último artigo:
    a nota da retificação vai logo a seguir ao parágrafo, e o histórico diz «Retifica texto»."""
    linhas = ["###### Artigo 71.º — Legislação revogada", "", "É revogado o DL 1/90.", "", "Promulgado em 21 de Junho de 1993.", "",
              "Anexo II a que se refere o artigo 41.º", "", "[(ver documento original)](https://x/b.pdf)", "", "Anexo III a que se refere o artigo 63.º"]
    assert rt._artigo_de(linhas, 2) == "71"
    assert rt._artigo_de(linhas, 8) is None
    assert rt._com_notas(linhas, {8: {"> Retificado pelo/a P."}})[9:12] == ["", "> Retificado pelo/a P.", ""]
