"""Testes da verificação e da revogação mecânica do texto antigo (consolidacao/texto_antigo.py)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "consolidacao"))

import texto_antigo as t  # noqa: E402

NOTA = "> Revogado pelo/a [Decreto Regulamentar n.º 11/2007](https://diariodarepublica.pt/x), publicado em 2007-02-27."


def test_revogado_com_divisao_interna_perde_o_corpo_antigo_e_ganha_a_epigrafe():
    texto = "\n\n".join([
        "###### Artigo 22.º", "(Revogado.)", NOTA,
        "##### Divisão de Identificação Animal", "À Divisão compete:", "a) Definir os sistemas;",
        "###### Artigo 23.º", "Texto do 23.º",
    ])
    novo, feitos = t.revogar_inteiro(texto)
    assert "À Divisão compete" not in novo and "a) Definir" not in novo
    assert "###### Artigo 22.º — Divisão de Identificação Animal" in novo
    assert NOTA in novo and "(Revogado.)" in novo
    assert "###### Artigo 23.º\n\nTexto do 23.º" in novo
    assert [f["artigo"] for f in feitos] == ["22.º"]


def test_titulos_de_estrutura_ficam():
    texto = "\n\n".join([
        "###### Artigo 3.º", "(Revogado.)", NOTA, "1 - Texto antigo do número 1.",
        "### CAPÍTULO II — Estrutura", "#### SECÇÃO I — Coordenação", "###### Artigo 4.º", "Texto.",
    ])
    novo, _ = t.revogar_inteiro(texto)
    assert "Texto antigo" not in novo
    assert "### CAPÍTULO II — Estrutura" in novo and "#### SECÇÃO I — Coordenação" in novo


def test_formulas_finais_ficam_no_ultimo_artigo():
    texto = "\n\n".join([
        "###### Artigo 20.º", "(Revogado.)", NOTA, "É revogada a Portaria n.º 336/75.",
        "Visto e aprovado em Conselho de Ministros de 4 de Abril de 1994.", "Promulgado em 5 de Agosto de 1994.",
    ])
    novo, feitos = t.revogar_inteiro(texto)
    assert "É revogada a Portaria" not in novo
    assert "Visto e aprovado" in novo and "Promulgado em" in novo
    assert len(feitos) == 1


def test_artigo_so_revogado_nao_muda():
    texto = "\n\n".join(["###### Artigo 5.º — Epígrafe", "(Revogado.)", NOTA, "###### Artigo 6.º", "Texto."])
    novo, feitos = t.revogar_inteiro(texto)
    assert novo == texto and feitos == []


def test_artigo_em_vigor_nao_muda():
    texto = "\n\n".join(["###### Artigo 5.º", "1 - Em vigor.", "2 - (Revogado.)", "###### Artigo 6.º", "Texto."])
    novo, feitos = t.revogar_inteiro(texto)
    assert novo == texto and feitos == []


def test_epigrafe_ja_no_titulo_fica_como_esta():
    texto = "\n\n".join(["###### Artigo 7.º — Divisão Técnica", "(Revogado.)", "##### Divisão Técnica", "À Divisão incumbe:", "###### Artigo 8.º", "x"])
    novo, feitos = t.revogar_inteiro(texto)
    assert "###### Artigo 7.º — Divisão Técnica\n" in novo and "À Divisão incumbe" not in novo
    assert feitos[0]["epigrafe_no_titulo"] is None


def test_marcados_ve_o_corpo_antigo_a_seguir_a_revogado():
    original = "\n\n".join(["###### Artigo 22.º", "##### Divisão de Pessoal", "À Divisão de Pessoal compete fazer muitas coisas importantes.", "###### Artigo 23.º", "y"])
    consolidado = "\n\n".join(["###### Artigo 22.º", "(Revogado.)", NOTA, "##### Divisão de Pessoal", "À Divisão de Pessoal compete fazer muitas coisas importantes.", "###### Artigo 23.º", "y"])
    assert [a["artigo"] for a in t.marcados(original, consolidado)] == ["22.º"]
    novo, _ = t.revogar_inteiro(consolidado)
    assert t.marcados(original, novo) == []


def test_subseccao_em_minusculas_e_estrutura_e_fica():
    texto = "\n\n".join([
        "###### Artigo 29.º", "(Revogado.)", NOTA,
        "##### Subsecção II — Pessoal auxiliar", "###### Artigo 30.º", "Texto.",
    ])
    novo, feitos = t.revogar_inteiro(texto)
    assert novo == texto and feitos == []


def test_divisao_numerada_e_estrutura():
    texto = "\n\n".join(["###### Artigo 103.º-A", "(Revogado.)", "texto antigo que sai aqui", "##### DIVISÃO XI — Funchal", "I - Pilotagem"])
    novo, _ = t.revogar_inteiro(texto)
    assert "texto antigo" not in novo and "##### DIVISÃO XI — Funchal" in novo and "I - Pilotagem" in novo


def test_assinaturas_ficam():
    texto = "\n\n".join(["###### Artigo 90.º", "(Revogado.)", NOTA, "Alfredo Jorge Nobre da Costa - José da Silva Lopes - Amílcar José de Gouveia Marques."])
    novo, feitos = t.revogar_inteiro(texto)
    assert "Alfredo Jorge Nobre da Costa" in novo and feitos == []


def test_com_original_so_sai_texto_antigo():
    original = "\n\n".join(["###### Artigo 24.º", "Texto antigo do 24.º.", "###### Artigo 25.º", "x"])
    consolidado = "\n\n".join(["###### Artigo 24.º", "(Revogado.)", NOTA, "III", "Das casas em regime de arrendamento", "###### Artigo 25.º", "x"])
    novo, feitos = t.revogar_inteiro(consolidado, original)
    assert novo == consolidado and feitos == []


def test_com_original_tira_o_corpo_original():
    original = "\n\n".join(["###### Artigo 22.º", "##### Divisão de Pessoal", "À Divisão compete:", "a) Gerir.", "###### Artigo 23.º", "y"])
    consolidado = "\n\n".join(["###### Artigo 22.º", "(Revogado.)", NOTA, "##### Divisão de Pessoal", "À Divisão compete:", "a) Gerir.", "###### Artigo 23.º", "y"])
    novo, feitos = t.revogar_inteiro(consolidado, original)
    assert "À Divisão compete" not in novo and "###### Artigo 22.º — Divisão de Pessoal" in novo and len(feitos) == 1
