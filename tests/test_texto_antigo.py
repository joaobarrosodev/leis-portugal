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


def test_com_original_tira_tambem_as_alineas_ja_revogadas():
    original = "\n\n".join(["###### Artigo 16.º", "##### Divisão de Arquivo", "1 - À Divisão compete:", "c) Organizar;", "d) Apoiar;", "###### Artigo 17.º", "y"])
    consolidado = "\n\n".join(["###### Artigo 16.º", "(Revogado.)", NOTA, "##### Divisão de Arquivo", "1 - À Divisão compete:", "c) Organizar;",
                               "d) (Revogada.)", "> Revogado pelo/a [DL 206/98](https://x), publicado em 1998-07-13.", "###### Artigo 17.º", "y"])
    novo, feitos = t.revogar_inteiro(consolidado, original, so={"16.º"})
    assert "À Divisão compete" not in novo and "d) (Revogada.)" not in novo and len(feitos) == 1
    assert t.revogar_inteiro(consolidado, original, so={"9.º"})[1] == []


# troca_de_expressao (consolidacao/camada1.py): parágrafo com uma expressão trocada pelo alterador.
import camada1 as c1  # noqa: E402


def test_troca_de_expressao_aceita_a_retificacao():
    base = ["§ 3.º É aplicável o disposto nos artigos 13.º e 14.º do Decreto-Lei n.º 40397, com as devidas adaptações."]
    alt = ["No § 3.º do artigo 17.º, onde se lê: ... o disposto nos artigos 13.º e 14.º do Decreto-Lei n.º 40397, ..., deve ler-se: ... o disposto no artigo 13.º e na alínea a) do artigo 14.º do Decreto-Lei n.º 40397, ..."]
    par = "§ 3.º É aplicável o disposto no artigo 13.º e na alínea a) do artigo 14.º do Decreto-Lei n.º 40397, com as devidas adaptações."
    assert c1.troca_de_expressao(par, base, alt)


def test_troca_de_expressao_aceita_a_troca_de_prazo():
    base = ["Art. 25.º As sociedades apresentarão, até 30 de Abril de cada ano, a declaração."]
    alt = ["Art. 4.º Os prazos estabelecidos até 30 de Abril de cada ano nos artigos 22.º e 25.º passam para 30 de Junho de cada ano."]
    assert c1.troca_de_expressao("Art. 25.º As sociedades apresentarão, até 30 de Junho de cada ano, a declaração.", base, alt)


def test_troca_de_expressao_recusa_o_que_o_alterador_nao_traz():
    base = ["Art. 25.º As sociedades apresentarão, até 30 de Abril de cada ano, a declaração."]
    alt = ["Art. 4.º Os prazos estabelecidos até 30 de Abril de cada ano passam para 30 de Junho de cada ano."]
    assert not c1.troca_de_expressao("Art. 25.º As sociedades apresentarão, até 31 de Julho de cada ano, a declaração.", base, alt)
    assert not c1.troca_de_expressao("Art. 25.º As sociedades e os empresários apresentarão, até 30 de Junho de cada ano, a declaração.", base, alt)


def test_troca_de_expressao_recusa_duas_expressoes_num_alterador_e_outra_noutro():
    base = ["Art. 25.º As sociedades apresentarão, até 30 de Abril de cada ano, a declaração."]
    alts = ["... 30 de Abril de cada ano ...", "... 30 de Junho de cada ano ..."]
    assert not c1.troca_de_expressao("Art. 25.º As sociedades apresentarão, até 30 de Junho de cada ano, a declaração.", base, alts)


def test_revoga_o_diploma_numa_lista_sem_rotulos():
    import llm_completo as lc
    import texto as tm
    padrao = tm.padrao_diploma("Decreto-Lei n.º 476/80")
    texto = "\n\n".join([
        "###### Artigo 28.º — Norma revogatória", "São revogados:",
        "O Decreto-Lei n.º 476/80, de 15 de Outubro, com excepção do artigo 25.º;",
        "O Decreto-Lei n.º 115/83, de 24 de Fevereiro;", "Os artigos 46.º a 53.º do Decreto-Lei n.º 118/83, de 25 de Fevereiro.",
    ])
    assert lc._revoga_o_diploma(texto, padrao)
    outro = texto.replace("O Decreto-Lei n.º 476/80, de 15 de Outubro, com excepção do artigo 25.º;", "O artigo 3.º do Decreto-Lei n.º 476/80;")
    assert not lc._revoga_o_diploma(outro, padrao)


def test_reescrever_nao_guarda_o_corpo_que_comeca_por_o_primeiro_ministro():
    from aplicar import _reescrever
    from texto import dividir
    corpo = dividir("\n\n".join([
        "###### Artigo 7.º", "O Primeiro-Ministro, salvo sua indicação em contrário, será substituído pelo Ministro da Presidência.",
        "###### Artigo 8.º", "Texto do 8.º",
    ]) + "\n")
    artigo = next(a for a in corpo.artigos if a.numero.startswith("7"))
    _reescrever(artigo, "", ["O Primeiro-Ministro será substituído pelo Ministro dos Negócios Estrangeiros."], "> Alterado pelo/a DL 55/98.")
    texto = "\n".join(artigo.linhas)
    assert "Ministro da Presidência" not in texto and "Negócios Estrangeiros" in texto


def test_reescrever_guarda_a_assinatura_do_primeiro_ministro():
    from aplicar import _reescrever
    from texto import dividir
    corpo = dividir("\n\n".join([
        "###### Artigo 9.º", "Este diploma entra em vigor amanhã.",
        "Visto e aprovado em Conselho de Ministros de 4 de Abril de 1994.", "O Primeiro-Ministro, Aníbal António Cavaco Silva.",
    ]) + "\n")
    artigo = corpo.artigos[0]
    _reescrever(artigo, "", ["Este diploma entra em vigor hoje."], "> Alterado.")
    texto = "\n".join(artigo.linhas)
    assert "Aníbal António Cavaco Silva" in texto and "amanhã" not in texto


def test_reescrever_guarda_as_ligacoes_do_corpo_iguais_a_do_fim():
    from aplicar import _reescrever
    from texto import dividir
    lig = "[(ver documento original)](https://files.diariodarepublica.pt/1s/1997/12/293a02/00980495.pdf)"
    corpo = dividir("\n\n".join([
        "###### Artigo 39.º", "Mapa I", lig, "Mapa II", lig,
        "Aprovada em 14 de Novembro de 1997.", "Publique-se.", "O Primeiro-Ministro, António Manuel de Oliveira Guterres.", lig,
    ]) + "\n")
    artigo = corpo.artigos[0]
    nova = ["Mapa I", lig, "Mapa II (novo)", lig, "Aprovada em 14 de Novembro de 1997.", "Publique-se.",
            "O Primeiro-Ministro, António Manuel de Oliveira Guterres.", lig]
    _reescrever(artigo, "", nova, "> Alterado.")
    texto = "\n".join(artigo.linhas)
    assert texto.count(lig) == 3 and texto.count("Aprovada em") == 1 and "Mapa II (novo)" in texto


def test_anexo_com_titulo_repetido_vai_pela_ordem_e_revogado_leva_nota_de_revogacao():
    import llm_completo as lc
    from texto import dividir
    titulo = "## ANEXO — Cartão especial"
    corpo = dividir("\n\n".join(["###### Artigo 1.º", "Texto.", titulo, "Corpo um.", "###### Artigo 2.º", "Texto 2.", titulo, "Corpo dois."]) + "\n")
    feito, erro = lc._mudar_corpo_do_anexo(corpo, {"titulo": titulo, "texto": "(Revogado.)"}, "Lei 16/2009", "2009-04-01", (1, 2))
    assert erro is None and feito.operacao == "revogar"
    texto = "\n".join(l for s in corpo.segmentos for l in (s.linhas if hasattr(s, "linhas") else s))
    assert "Corpo um." in texto and "Corpo dois." not in texto and "> Revogado pelo/a Lei 16/2009" in texto
    _, erro = lc._mudar_corpo_do_anexo(corpo, {"titulo": titulo, "texto": "x"}, "L", "d")
    assert erro and "repete-se" in erro
