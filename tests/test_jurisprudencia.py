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
