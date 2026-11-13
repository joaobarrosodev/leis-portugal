from rag import jurisprudencia as j


ACORDAO = """---
id: pt:tc:acordao:2022:268
official_number: 268/2022
official_date: '2022-04-19'
official_url: https://www.tribunalconstitucional.pt/tc/acordaos/20220268.html
---

# Acórdão do Tribunal Constitucional n.º 268/2022

II – Fundamentação

No Acórdão n.º 160/88 decidiu-se declarar a inconstitucionalidade, com força obrigatória geral, da norma do
artigo 5.º do Decreto-Lei n.º 118/85, de 19 de abril.

III – Decisão

Pelo exposto, o Tribunal Constitucional decide:

a) declarar a inconstitucionalidade, com força obrigatória geral, da norma constante do artigo 4.º da Lei n.º 32/2008,
de 17 de julho, conjugada com o artigo 6.º da mesma lei, por violação do disposto nos n.ºs 1 e 4 do artigo 35.º e do
n.º 1 do artigo 26.º, em conjugação com o n.º 2 do artigo 18.º, todos da Constituição;

b) Sem custas.

Lisboa, 19 de abril de 2022 - Fulano
"""


def _normas(alinea):
    return [(n.artigo, n.diploma_texto, n.principal) for n in j.normas(alinea)]


def test_so_le_a_decisao_final_e_nao_as_decisoes_citadas():
    lista = j.julgamentos(ACORDAO)
    assert len(lista) == 1
    julgamento = lista[0]
    assert (julgamento.acordao, julgamento.numero, julgamento.data) == ("pt:tc:acordao:2022:268", "268/2022", "2022-04-19")
    assert julgamento.sentido == "declara_fog"
    assert [(n.artigo, n.numero) for n in julgamento.normas] == [("4.º", "32/2008"), ("6.º", "32/2008")]


def test_parametro_constitucional_no_meio_da_alinea():
    alinea = ("Julgar inconstitucional, por violação do artigo 59.º, n.º 1, alínea f), da Constituição da República "
              "Portuguesa, a norma constante do artigo 54.º, n.º 1, da Lei n.º 98/2009, de 4 de setembro")
    assert j.sentido(alinea) == "julga"
    assert _normas(alinea) == [("54.º", "Lei n.º 98/2009", True)]


def test_varios_artigos_do_mesmo_codigo_e_siglas():
    alinea = ("Conceder provimento ao recurso e julgar inconstitucional o disposto nos artigos 11.º, n.º 1, in fine, "
              "e 25.º, n.º 4, ambos do CPTA, quando interpretados no sentido de que")
    normas = j.normas(alinea)
    assert [n.artigo for n in normas] == ["11.º", "25.º"]
    assert {n.codigo for n in normas} == {"Código de Processo nos Tribunais Administrativos"}


def test_normas_da_interpretacao_nao_sao_principais():
    alinea = ("Não julgar inconstitucional a norma contida no artigo 135.º da Lei n.º 7-A/2016, de 30 de março, na parte "
              "em que, atribuindo natureza interpretativa às alterações do artigo 88.º do Código do IRC")
    assert j.sentido(alinea) == "nao_julga"
    assert _normas(alinea)[0] == ("135.º", "Lei n.º 7-A/2016", True)
    assert ("88.º", "Código do IRC", False) in _normas(alinea)


def test_diploma_de_alteracao_e_artigo_que_aprova_ficam_de_fora():
    alinea = ("Não julgar inconstitucional o artigo 2.º do Regime Jurídico da Contribuição Extraordinária sobre o Setor "
              "Energético, aprovado pelo artigo 228.º da Lei n.º 83.º-C/2013, de 31 de dezembro, na redação dada pela "
              "Lei n.º 114/2017, de 29 de dezembro")
    normas = j.normas(alinea)
    assert [(n.artigo, n.numero) for n in normas] == [("2.º", "83-C/2013")]


def test_norma_sem_artigo():
    alinea = ("Julgar inconstitucionais as normas constantes dos n.ºs 2 e 3 do Anexo IX da Portaria n.º 1473-B/2008, de "
              "17 de dezembro, na redação da Portaria n.º 296-A/2013, de 2 de outubro")
    assert _normas(alinea) == [(None, "Portaria n.º 1473-B/2008", True)]


def test_reclamacao_nao_e_julgamento():
    assert j.sentido("Indeferir a reclamação, mantendo-se a decisão sumária no sentido de não julgar inconstitucional a norma") is None
    assert j.sentido("Não tomar conhecimento do objeto do recurso") is None


def test_alineas_coladas_e_negativas():
    dispositivo = "Pelo exposto, decide-se: a)Não julgar inconstitucional a norma do artigo 80.º do Código Penal; b) Negar provimento ao recurso."
    partes = j.alineas(dispositivo)
    assert [j.sentido(p) for p in partes] == [None, "nao_julga", None]


def test_nomes_de_codigos_com_grafias_diferentes():
    assert j.nome_canonico("Código da Insolvência e Recuperação de Empresas [CIRE]")[1] == ("decreto-lei", "53/2004")
    assert j.nome_canonico("Código do IRC")[0] == "Código do Imposto sobre o Rendimento das Pessoas Coletivas"


def test_consulta_por_artigo_poe_as_declaracoes_primeiro(tmp_path):
    import json

    def linha(acordao, data, sentido, artigo="4.º", principal=True):
        norma = {"artigo": artigo, "diploma_texto": "Lei n.º 32/2008", "tipo": "lei", "numero": "32/2008", "codigo": None,
                 "documento": "pt:dre:1:por", "parte": "", "artigo_encontrado": True, "principal": principal}
        return json.dumps({"acordao": acordao, "numero": acordao, "data": data, "url": None, "sentido": sentido,
                           "alinea": acordao, "normas": [norma]})

    caminho = tmp_path / "normas.jsonl"
    caminho.write_text("\n".join([
        linha("a", "2020-01-01", "julga"), linha("b", "2023-01-01", "nao_julga"),
        linha("c", "2022-04-19", "declara_fog"), linha("d", "2024-01-01", "julga"),
        linha("e", "2024-01-01", "julga", principal=False),
    ]))
    consulta = j.Jurisprudencia(caminho)
    assert [x["acordao"] for x in consulta.por_artigo("pt:dre:1:por", "4.º")] == ["c", "d", "b", "a"]
    assert [x["acordao"] for x in consulta.declarado_inconstitucional("pt:dre:1:por", "4.º")] == ["c"]
    assert consulta.por_artigo("pt:dre:1:por", "5.º") == []


def test_aviso_distingue_a_redacao_declarada_da_atual():
    julgamento = {"numero": "268/2022", "data": "2022-04-19"}
    assert j.aviso_declaracao(julgamento, "2008-07-17").startswith("Declarado inconstitucional com força obrigatória geral")
    assert "uma redação anterior" in j.aviso_declaracao(julgamento, "2024-02-06")


def test_segunda_resposta_um_por_acordao_e_resumo_do_resto():
    from types import SimpleNamespace

    from rag.resposta import JULGAMENTOS_POR_ARTIGO, jurisprudencia

    julgados = [{"acordao": f"a{i}", "alinea": "x", "numero": f"{i}/2024", "data": "2024-01-01", "sentido": "nao_julga"} for i in range(8)]
    julgados.insert(1, dict(julgados[0], alinea="outra alínea do mesmo acórdão"))
    julgados.append({"acordao": "futuro", "alinea": "x", "numero": "1/2030", "data": "2030-01-01", "sentido": "julga"})
    pesquisa = SimpleNamespace(julgamentos=lambda r: julgados)
    consulta = SimpleNamespace(data="2026-11-12")
    artigo = SimpleNamespace(rotulo="Código Penal › Artigo 387.º")
    lista = jurisprudencia(consulta, [artigo], pesquisa)
    assert [x["acordao"] for x in lista] == [f"a{i}" for i in range(8)]
    assert sum(x["mostrar"] for x in lista) == JULGAMENTOS_POR_ARTIGO
    assert jurisprudencia(consulta, [artigo], None) == []


def test_codigo_anterior_na_data_do_acordao():
    cpc = j.Norma("668.º", "CPC", codigo="Código de Processo Civil")
    assert j.no_tempo(cpc, "2015-03-01") is cpc
    antigo = j.no_tempo(cpc, "2010-05-12")
    assert (antigo.tipo, antigo.numero, antigo.codigo) == ("decreto-lei", "44129", None)
    assert j.no_tempo(cpc, "1955-01-01") is None
    cpp = j.Norma("400.º", "CPP", tipo="decreto-lei", numero="78/87")
    assert j.no_tempo(cpp, "1986-06-01") is None
    assert j.no_tempo(cpp, "2000-01-01") is cpp
    outra = j.Norma("4.º", "Lei n.º 32/2008", tipo="lei", numero="32/2008")
    assert j.no_tempo(outra, "1990-01-01") is outra


def test_data_com_gralha_no_site_fica_vazia():
    md = ACORDAO.replace("official_date: '2022-04-19'", "official_date: '1922-04-19'")
    assert j.julgamentos(md)[0].data is None


def test_formas_antigas_de_declarar():
    assert j.sentido(
        "Nestes termos, o Tribunal Constitucional declara a inconstitucionalidade, com força obrigatória geral, "
        "das normas dos artigos 7.º, n.º 2, do Decreto-Lei n.º 387-B/87"
    ) == "declara_fog"
    assert j.sentido(
        "Assim, declara-se, com força obrigatória geral, e com referência ao disposto no artigo 168º, nº 1, alínea q), "
        "da Constituição, a inconstitucionalidade das normas do Decreto-Lei n.º 1/80"
    ) == "declara_fog"
    assert j.sentido("Nos termos expostos, não se declara a ilegalidade da norma do artigo 59.º, n.º 2, da Lei Orgânica n.º 2/2013") == "nao_declara_fog"
    assert j.sentido("o Tribunal Constitucional não declara a ilegalidade, nem a inconstitucionalidade, das normas do artigo 69.º-D") == "nao_declara_fog"
    assert j.sentido("decide-se não declarar a inconstitucionalidade de qualquer das normas do Decreto-Lei n.º 2/80") == "nao_declara_fog"
    assert j.sentido("b) Não declarar inconstitucional a parte restante da mesma norma") == "nao_declara_fog"
    # "declarado" não é o verbo da decisão.
    assert j.sentido("o artigo já declarado a inconstitucionalidade") is None


def test_hifen_invisivel_dos_acordaos_antigos():
    texto = ACORDAO.replace("declarar a inconstitucionalidade, com força obrigatória geral, da norma constante",
                            "declarar a inconsti\u00adtucionalidade, com força obrigatória geral, da norma constante")
    assert [x.sentido for x in j.julgamentos(texto)] == ["declara_fog"]


def _acordao_antigo(decisao):
    return ACORDAO.split("III – Decisão")[0].replace("pt:tc:acordao:2022:268", "pt:tc:acordao:1984:56") + decisao + "\n\nLisboa, 2 de maio de 1984\n"


def test_verbo_antes_das_alineas():
    texto = _acordao_antigo(
        "28 — Pelos motivos expostos, o Tribunal Constitucional: Não conhece, por inútil, da constitucionalidade dos "
        "artigos 7.º, n.ºs 3 e 4, do Decreto-Lei n.º 349-B/83; Declara com força obrigatória geral: a) Por violação dos "
        "artigos 168.º, n.º 1, alínea c), da Constituição, a inconstitucionalidade dos artigos 2.º, n.ºs 1 e 2, do "
        "Decreto-Lei n.º 349-B/83; b) E por violação do artigo 189.º, a inconstitucionalidade do artigo 6.º do mesmo diploma."
    )
    assert [x.sentido for x in j.julgamentos(texto)] == ["declara_fog", "declara_fog"]


def test_abertura_antiga_da_decisao():
    texto = _acordao_antigo(
        "16 — De harmonia com o exposto, decide o Tribunal Constitucional não declarar a inconstitucionalidade, da norma "
        "constante do ponto 6.5 do Regulamento do Conselho Superior de Polícia."
    ).replace("No Acórdão n.º 160/88", "Acordam, em plenário, no Tribunal Constitucional:\n\nNo Acórdão n.º 160/88")
    assert [x.sentido for x in j.julgamentos(texto)] == ["nao_declara_fog"]


def test_parametro_entre_travessoes_e_leis_antigas_pelo_nome():
    alinea = ("Julgar inconstitucionais - por violação do artigo 29º, nº 4, da Constituição - os artigos 2º e 5º, nº 2, "
              "do Decreto-Lei nº 20-A/90, de 15 de Janeiro, interpretados no sentido de visarem impedir a aplicação da nova lei")
    assert [(n.artigo, n.diploma_texto) for n in j.normas(alinea)] == [("2.º", "Decreto-Lei nº 20-A/90"), ("5.º", "Decreto-Lei nº 20-A/90")]
    alinea = "Não julgar inconstitucional o artigo 24º, alínea b) da Lei de Processo nos Tribunais Administrativos, na parte em que remete"
    [norma] = j.normas(alinea)
    assert (norma.artigo, norma.tipo, norma.numero) == ("24.º", "decreto-lei", "267/85")
    assert [(n.artigo, n.numero) for n in j.normas("não julgar inconstitucionais as normas dos artigos 66.º e 77.º, n.º 4, da LOPTC")] == [
        ("66.º", "98/97"), ("77.º", "98/97")]


def test_redaccao_antiga_e_art_o():
    alinea = ("não julgar inconstitucionais as normas constantes do artigo 53º, nº 3, do Decreto-Lei nº 214/88, de 17 de Junho, "
              "na redacção do Decreto-Lei nº 312/93, de 15 de Setembro e do artigo 55º, nº 2, na redacção do Decreto-Lei nº 206/91")
    assert [(n.artigo, n.numero) for n in j.normas(alinea) if n.artigo] == [("53.º", "214/88"), ("55.º", "214/88")]
    assert all(n.artigo for n in j.normas("Não julgar inconstitucional a norma do artigo 1º do Decreto-Lei nº 362/78, com a redacção do Decreto-Lei nº 23/80"))
    alinea = ("julgar inconstitucional, por violação da al. c) do art.º 167.º da Constituição na sua primitiva redacção, "
              "o art.º 7.º do Decreto Regional n.º 21/80/A, de 11 de Setembro")
    assert [(n.artigo, n.numero) for n in j.normas(alinea)] == [("7.º", "21/80/A")]


def test_cabecalho_acordam_nao_e_a_decisao():
    texto = ("Acordam no plenário do Tribunal Constitucional:\n\nI\n\nO procurador-geral requer a declaração da inconstitucionalidade "
             "das normas da Lei n.º 16/79.\n\n" + "Fundamentação longa. " * 200 +
             "\n\nDeclara-se, com força obrigatória geral, a inconstitucionalidade das normas dos artigos 1.º a 7.º do Decreto-Lei n.º 280/85."
             "\n\nLisboa, 8 de fevereiro de 1989.\n")
    assert j.decisao(texto).startswith("Declara-se, com força obrigatória geral")


def test_citacao_longe_do_inicio_nao_e_decisao():
    relatorio = "Relatório do processo, com as alegações das partes e a decisão recorrida. " * 8
    assert j._citacao_e_nao_decisao(relatorio + "O Tribunal firmou jurisprudência no sentido de não julgar inconstitucional a norma do artigo 64.º do Código da Estrada")
    assert not j._citacao_e_nao_decisao(relatorio + "Assim, decide-se, pelos fundamentos constantes do Acórdão nº 331/92, publicado no Diário da República, "
                                        "não julgar inconstitucional a norma do artigo 9.º do Decreto-Lei n.º 154/91")
    assert not j._citacao_e_nao_decisao("Não julgar inconstitucional a norma do artigo 9.º do Decreto-Lei n.º 154/91")
