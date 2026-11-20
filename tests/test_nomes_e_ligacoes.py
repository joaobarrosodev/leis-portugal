"""Nomes de códigos, o texto em vigor fora do registo que o aprovou e os registos repetidos (inventário da camada 1,
linhas 2, 4 e 11)."""

import sqlite3

from rag import duplicados, referencias
from rag.pesquisa import Pesquisa

from test_dados import ENCHIMENTO, _artigos, _construir


# ------------------------------------------------------------------ nomes e siglas


def test_nomes_que_faltavam_e_siglas():
    assert referencias.extrair("artigo 62.º do Código Cooperativo").codigos == ["Código Cooperativo"]
    assert referencias.extrair("o art. 17.º do CIRE e o 97.º do CPTA").codigos == [
        "Código da Insolvência e da Recuperação de Empresas", "Código de Processo nos Tribunais Administrativos",
    ]
    assert referencias.extrair("Nos termos do artigo 129.º do CT").codigos == ["Código do Trabalho"]
    assert referencias.extrair("artigo 105.º do RGIT").codigos == ["Regime Geral das Infrações Tributárias"]
    assert referencias.extrair("Regime Geral das Infracções Tributárias").codigos == ["Regime Geral das Infrações Tributárias"]


def test_siglas_so_em_maiusculas():
    assert referencias.extrair("o ct do motor e o cpi do mês").codigos == []
    assert referencias.extrair("o CPI e o CPA").codigos == ["Código da Propriedade Industrial", "Código do Procedimento Administrativo"]


def test_constituicao_so_quando_e_a_da_republica():
    assert referencias.extrair("artigo 149.º da Constituição").codigos == ["Constituição da República Portuguesa"]
    assert referencias.extrair("Diz a Constituição da República que").codigos == ["Constituição da República Portuguesa"]
    assert referencias.extrair("Constituição da República Portuguesa, artigo 13.º").codigos == ["Constituição da República Portuguesa"]
    assert referencias.extrair("artigo 13.º da CRP").codigos == ["Constituição da República Portuguesa"]
    assert referencias.extrair("Qual o capital mínimo para a constituição de uma sociedade?").codigos == []
    assert referencias.extrair("A Constituição de sociedades anónimas exige").codigos == []


def test_nome_normalizado_sem_grafia_antiga_nem_o_a_que_se_refere():
    assert referencias.nome_normalizado("Anexo — REGIME GERAL DAS INFRACÇÕES TRIBUTÁRIAS") == "regime geral das infracoes tributarias"
    assert referencias.nome_normalizado("Regime Geral das Infrações Tributárias") == "regime geral das infracoes tributarias"
    assert referencias.nome_normalizado("Anexo I — Código do Imposto sobre Veículos a que se refere o n.º 1 do artigo 1.º") == "codigo do imposto sobre veiculos"
    assert referencias.nome_solto("Código do Processo Penal") == referencias.nome_solto("Código de Processo Penal") == "codigo processo penal"


def _codigo(n: int, palavra: str, epigrafe: str = "Epígrafe") -> list[tuple]:
    return [("", f"{i}.º", f"{epigrafe} {palavra} {i}", f"O {palavra} número {i} tem regras próprias", "2020-01-01", None) for i in range(1, n + 1)]


def test_codigo_pelo_nome_sem_palavras_de_ligacao_e_pelo_nome_do_indice(tmp_path):
    caminho = _construir(tmp_path / "i.sqlite", {
        **ENCHIMENTO,
        "pt:lei:078": ("Decreto-Lei n.º 78/87", "Aprova o Código do Processo Penal", _codigo(25, "arguido"), []),
        "pt:lei:119": ("Lei n.º 119/2015", "Aprova o Código Cooperativo e revoga a Lei n.º 51/96", _codigo(25, "cooperador"), []),
        "pt:lei:020": ("Lei n.º 20/2020", "Aprova o Código Pequeno", _codigo(5, "pequeno"), []),
    })
    p = Pesquisa(caminho)
    assert p.codigo("Código de Processo Penal") == [("pt:lei:078", "")]
    topo = p.pesquisar("artigo 12.º do Código de Processo Penal", "2026-01-01").resultados[0]
    assert (topo.documento, topo.numero, topo.origem) == ("pt:lei:078", "12.º", "referência")
    # «Código Cooperativo» não está em `referencias.CODIGOS`, mas o índice tem-no, com artigos que cheguem.
    assert p.codigos_na_pergunta("artigo 3.º do Código Cooperativo", []) == ["codigo cooperativo"]
    topo = p.pesquisar("artigo 3.º do Código Cooperativo", "2026-01-01").resultados[0]
    assert (topo.documento, topo.numero) == ("pt:lei:119", "3.º")
    # Um código com poucos artigos não conta como citado só pelo nome.
    assert p.codigos_na_pergunta("artigo 3.º do Código Pequeno", []) == []


def test_codigo_citado_que_o_acervo_nao_tem_fica_em_falta(tmp_path):
    caminho = _construir(tmp_path / "i.sqlite", {**ENCHIMENTO, "pt:lei:001": ("Lei n.º 1/2020", "Coimas", _artigos(3, "arguido"), [])})
    assert Pesquisa(caminho).pesquisar("artigo 2.º do Código Comercial", "2026-01-01").diplomas_em_falta == ["Código Comercial"]


# ------------------------------------------------------------------ o texto em vigor noutro registo


def _fechados(artigos: list[tuple], ate: str) -> list[tuple]:
    return [(parte, numero, epigrafe, texto, desde, ate) for parte, numero, epigrafe, texto, desde, _ in artigos]


def _indice_com_original(tmp_path, ligacao: str = "texto_em_vigor_em"):
    original = _fechados([
        ("", "5.º", "Coimas", "As coimas de 1992", "1992-01-01", None),
        ("", "6.º", "Prazos", "Os prazos de 1992", "1992-01-01", None),
        ("", "8.º", "Inscrição", "A inscrição de 1992", "1992-01-01", None),
        ("", "9.º", "", "Texto sem epígrafe de 1992", "1992-01-01", None),
        ("", "4.º", "Proibição temporária da circulação de veículos", "A proibição de 1992", "1992-01-01", None),
    ], "2015-09-01")
    atual = [
        ("Anexo — ESTATUTO", "5.º", "Deveres", "Os deveres de 2015", "2015-09-01", None),
        ("Anexo — ESTATUTO", "6.º", "Prazos", "Os prazos de 2015", "2015-09-01", None),
        ("Anexo — ESTATUTO", "7.º", "Coimas", "As coimas de 2015", "2015-09-01", None),
        ("Anexo — ESTATUTO", "8.º", "Quotas", "As quotas de 2015", "2015-09-01", None),
        ("Anexo — ESTATUTO", "9.º", "Sede", "A sede de 2015", "2015-09-01", None),
        ("Anexo — ESTATUTO", "4.º", "Proibição temporária ou permanente da circulação de veículos", "A proibição de 2015", "2015-09-01", None),
        ("", "1.º", "Objeto", "A presente lei aprova o estatuto", "2015-09-01", None),
    ]
    caminho = _construir(tmp_path / "i.sqlite", {
        **ENCHIMENTO,
        "pt:lei:119": ("Lei n.º 119/92", "Aprova o Estatuto", original, [(ligacao, "pt:lei:123")]),
        "pt:lei:123": ("Lei n.º 123/2015", "Aprova o novo Estatuto", atual, []),
    })
    with sqlite3.connect(caminho) as con:
        con.execute("UPDATE documentos SET data = '1992-01-01' WHERE id = 'pt:lei:119'")
    return Pesquisa(caminho)


def test_artigo_do_original_fechado_responde_pelo_texto_em_vigor(tmp_path):
    p = _indice_com_original(tmp_path)

    def topo(pergunta: str, data: str = "2026-01-01"):
        resultados = [r for r in p.pesquisar(pergunta, data).resultados if r.nivel == 3]
        return resultados[0] if resultados else None

    # O mesmo número e a mesma epígrafe.
    r = topo("artigo 6.º da Lei n.º 119")
    assert (r.documento, r.parte, r.numero, r.redirecionado_de, r.numero_citado) == ("pt:lei:123", "Anexo — ESTATUTO", "6.º", "pt:lei:119", None)
    assert any("Texto em vigor do diploma republicado (Lei n.º 119/92)" in a for a in r.avisos)
    # A numeração mudou: vai para o artigo com a mesma epígrafe, e diz-se.
    r = topo("artigo 5.º da Lei n.º 119")
    assert (r.documento, r.numero, r.numero_citado) == ("pt:lei:123", "7.º", "5.º")
    assert any("O artigo 5.º de Lei n.º 119/92 é, no texto em vigor, o artigo 7.º" in a for a in r.avisos)
    # O do mesmo número é outro artigo e nenhum tem a epígrafe: não se troca.
    assert topo("artigo 8.º da Lei n.º 119") is None
    # A epígrafe retocada no mesmo número conta como a mesma.
    assert topo("artigo 4.º da Lei n.º 119").numero == "4.º"
    # Sem epígrafe no original: o do mesmo número.
    assert topo("artigo 9.º da Lei n.º 119").numero == "9.º"
    # Numa data em que o original vigorava, responde ele.
    r = topo("artigo 5.º da Lei n.º 119", "2010-01-01")
    assert (r.documento, r.numero, r.redirecionado_de) == ("pt:lei:119", "5.º", None)


def test_redacao_atual_em_tambem_se_segue_mas_o_articulado_aberto_ganha(tmp_path):
    p = _indice_com_original(tmp_path, "redacao_atual_em")
    r = [r for r in p.pesquisar("artigo 6.º da Lei n.º 119", "2026-01-01").resultados if r.nivel == 3][0]
    assert (r.documento, r.numero) == ("pt:lei:123", "6.º")
    # O BM25 dos diplomas citados também lê o registo com o texto em vigor.
    assert any(r.documento == "pt:lei:123" and r.nivel == 2 for r in p.pesquisar("Lei n.º 119 sede", "2026-01-01").resultados)


# ------------------------------------------------------------------ registos repetidos


def test_mesmo_diploma_pelo_sumario_que_comeca_pelo_outro_e_pelos_numeros():
    def registo(sumario, inicio, numeros):
        return {"summary": sumario, "inicio": inicio, "numeros": set(numeros)}

    lei = registo("Organização, funcionamento e processo do Tribunal Constitucional", "lei n 28 82 a", [f"{i}.º" for i in range(115)])
    repeticao = registo("Organização, funcionamento e processo do Tribunal Constitucional. - Repete a publicação", "outro", [f"{i}.º" for i in range(113)])
    assert duplicados.mesmo_diploma(lei, repeticao) == "o mesmo sumário"
    assert duplicados.mesmo_diploma(lei, registo("Cria o Centro de Informática", "outro", [])) is None
    # O mesmo sumário mas outros artigos: não é o mesmo.
    assert duplicados.mesmo_diploma(lei, registo(lei["summary"], "outro", ["900.º", "901.º"])) is None
    pares = [{"repetido": "a", "principal": "b", "texto_em_vigor": True}, {"repetido": "c", "principal": "d", "texto_em_vigor": False}]
    assert duplicados.relacoes(pares, {"b": "Lei n.º 28/82"}) == [
        ("a", "mesmo_diploma_em", "b", "Lei n.º 28/82", None), ("a", "texto_em_vigor_em", "b", "Lei n.º 28/82", None), ("c", "mesmo_diploma_em", "d", "d", None),
    ]


def test_registo_repetido_responde_pelo_principal(tmp_path):
    original = [("", "6.º", "Competência", "Texto de 1982 da competência", "1982-11-15", None)]
    consolidado = [("", "6.º", "Competência", "Texto de 1982 da competência", "1982-11-15", "1998-01-01"),
                   ("", "6.º", "Competência", "Texto atual da competência", "1998-01-01", None)]
    caminho = _construir(tmp_path / "i.sqlite", {
        **ENCHIMENTO,
        "pt:lei:028": ("Lei n.º 28/82", "Tribunal Constitucional", original, [("mesmo_diploma_em", "pt:x:028"), ("texto_em_vigor_em", "pt:x:028")]),
        "pt:x:028": ("Lei n.º 28/82", "Tribunal Constitucional", consolidado, []),
    })
    with sqlite3.connect(caminho) as con:
        con.execute("CREATE TABLE so_referencia (id TEXT PRIMARY KEY)")
        con.execute("INSERT INTO so_referencia VALUES ('pt:lei:028')")
    p = Pesquisa(caminho)
    consulta = p.pesquisar("artigo 6.º da Lei n.º 028", "2026-01-01")
    assert consulta.diplomas_citados == ["pt:x:028"]
    assert [(r.documento, r.texto) for r in consulta.resultados if r.nivel == 3] == [("pt:x:028", "Texto atual da competência")]
    # Sem citar: o repetido está só pela referência e não aparece.
    assert all(r.documento != "pt:lei:028" for r in p.pesquisar("competência", "2026-01-01").resultados)
