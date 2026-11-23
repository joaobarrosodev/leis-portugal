"""Perguntas de leigo por artigo (rag.perguntas_por_artigo): âmbito, validação, junção ao índice e deltas."""

import json
import shutil
import sqlite3

import pytest
from rag import dados
from rag import perguntas_por_artigo as pa
from rag.indice import juntar_perguntas, perguntas_do_indice
from rag.pesquisa import Pesquisa

from test_dados import A, _bm25, _construir, _conteudo


CT = "pt:dre:602073:por"
CC = "pt:dre:477358:por"
NRAU = "pt:dre:693853:por"


def test_ambito_do_piloto_e_dos_outros_codigos():
    assert pa.bloco_de(CT, "Anexo — CÓDIGO DO TRABALHO::127.º").nome == "codigo-do-trabalho"
    assert pa.bloco_de(CT, "5.º") is None  # o articulado da Lei n.º 7/2009, não o Código
    assert pa.bloco_de(CC, "Anexo — CÓDIGO CIVIL::1069.º-A").nome == "codigo-civil-arrendamento"
    assert pa.bloco_de(CC, "Anexo — CÓDIGO CIVIL::1022.º") and pa.bloco_de(CC, "Anexo — CÓDIGO CIVIL::1113.º")
    # O resto do Código Civil está no bloco «codigo-civil», sem os artigos do arrendamento.
    assert pa.bloco_de(CC, "Anexo — CÓDIGO CIVIL::1021.º").nome == "codigo-civil"
    assert pa.bloco_de(CC, "Anexo — CÓDIGO CIVIL::1114.º").nome == "codigo-civil"
    assert pa.bloco_de(NRAU, "15.º-A").nome == "nrau"
    assert pa.bloco_de(NRAU, "Anexo — Republicação do capítulo IV do título II do livro II do Código Civil::1069.º") is None
    # O Código Penal tem parte sua desde 23/11/2026; o articulado do DL 48/95 fica de fora.
    assert pa.bloco_de("pt:dre:185720:por", "Anexo — CÓDIGO PENAL::131.º").nome == "codigo-penal"
    assert pa.bloco_de("pt:dre:185720:por", "1.º") is None
    assert pa.bloco_de("pt:dre:518992:por", "1.º") is None  # o CIRS de 1988 sem histórico: o em vigor é o da Lei 82-E/2014
    assert len({b.nome for b in pa.AMBITO}) == len(pa.AMBITO)


UTENTE = "pt:dre:571943:por"  # Lei n.º 15/2014
TAXAS = "pt:dre:146061:por"  # Decreto-Lei n.º 113/2011
CUIDADOR = "pt:dre:124500714:por"  # Lei n.º 100/2019
OCC = "pt:dre:70196966:por"  # Lei n.º 139/2015


def test_ambito_dos_avulsos():
    assert len(pa.AVULSOS) == 48 + 7  # a 1.ª leva e a 2.ª
    assert {b.arquivo for b in pa.AVULSOS} == {"avulsos-saude", "avulsos-seguranca-social", "avulsos-habitacao", "avulsos-consumo", "avulsos-familia",
                                               "avulsos-justica", "avulsos-impostos"}
    # O Estatuto dos Benefícios Fiscais: só o anexo, não o articulado do DL 215/89.
    assert pa.bloco_de("pt:dre:620928:por", "Anexo — ESTATUTO DOS BENEFÍCIOS FISCAIS::58.º-A").arquivo == "avulsos-impostos"
    assert pa.bloco_de("pt:dre:620928:por", "1.º") is None
    assert pa.bloco_de(UTENTE, "3.º").arquivo == "avulsos-saude"
    assert pa.bloco_de(UTENTE, "3.º").nome == "lei-15-2014-utente-saude"
    # Nos quatro com o regime num anexo, só o anexo: o articulado que o aprova fica de fora.
    assert pa.bloco_de(CUIDADOR, "5.º") is None
    assert pa.bloco_de(CUIDADOR, "Anexo — ESTATUTO DO CUIDADOR INFORMAL::5.º").nome == "lei-100-2019-cuidador-informal"
    # Contabilistas: o Estatuto em vigor (Anexo I); a cópia de 2019 que se lia no Anexo II sai.
    assert pa.bloco_de(OCC, "Anexo I — ESTATUTO DA ORDEM DOS CONTABILISTAS CERTIFICADOS::1.º").arquivo == "estatuto-ordem-contabilistas"
    assert pa.bloco_de(OCC, "Anexo II — CÓDIGO DEONTOLÓGICO DOS CONTABILISTAS CERTIFICADOS::1.º") is None
    # Os códigos continuam num ficheiro cada um.
    assert all(b.arquivo == b.nome for b in pa.PILOTO + pa.OUTROS_CODIGOS)


def test_ficheiros_de_perguntas_batem_com_o_ambito():
    # Cada ficheiro de rag/perguntas_artigo/ é de um bloco do âmbito, cada linha do bloco desse ficheiro, e todas validam.
    # Um ficheiro fora do âmbito (o «codigo-deontologico-contabilistas» de 19/11) ficava no `ler` e dava «em falta».
    arquivos = {b.arquivo for b in pa.AMBITO}
    for ficheiro in sorted(pa.PASTA.glob("*.jsonl")):
        assert ficheiro.stem in arquivos, ficheiro.name
        for linha in pa._ler_jsonl(ficheiro):
            bloco = pa.bloco_de(linha["documento"], linha["chave"])
            assert bloco is not None and bloco.arquivo == ficheiro.stem, (ficheiro.name, linha["chave"])
            assert pa.validar(linha, {}) == [], (ficheiro.name, linha["chave"])


@pytest.mark.parametrize(
    "pergunta",
    [
        "O que diz o regime jurídico do processo de adoção?",
        "A Lei de Defesa do Consumidor obriga a loja a trocar?",
        "O Estatuto do Cuidador Informal dá-me folgas?",
        "A lei de bases da saúde garante consulta?",
        "O Estatuto dos Benefícios Fiscais isenta a casa?",
        "Que isenções dá o EBF a quem compra casa?",
    ],
)
def test_validar_recusa_nomes_dos_avulsos(pergunta):
    assert any("cita" in p for p in pa.validar({**BOA, "perguntas": [*BOA["perguntas"][:2], pergunta]}, {"chave": "k"}))


def test_importar_avulsos_de_varios_diplomas_num_so_ficheiro(tmp_path):
    caminho = _construir(tmp_path / "avulsos.sqlite", {**A,
        UTENTE: ("Lei n.º 15/2014", "Direitos e deveres do utente dos serviços de saúde", [
            ("", "3.º", "Escolha", "O utente tem direito de escolher os serviços.", "2014-03-21", None),
            ("", "4.º", "Consentimento", "O consentimento é livre e esclarecido.", "2014-03-21", None),
        ], []),
        TAXAS: ("Decreto-Lei n.º 113/2011", "Taxas moderadoras", [
            ("", "4.º", "Isenção", "Estão isentos os utentes em situação de insuficiência económica.", "2011-11-29", None),
        ], []),
        CUIDADOR: ("Lei n.º 100/2019", "Estatuto do Cuidador Informal", [
            ("", "1.º", "Objeto", "A presente lei aprova o Estatuto.", "2019-09-06", None),
        ], []),
    })
    lotes, destino = tmp_path / "lotes", tmp_path / "perguntas"
    destino.mkdir()
    _gravar(destino / "avulsos-saude.jsonl", [{"documento": UTENTE, "chave": "3.º", "perguntas": ["Posso escolher o hospital?"]}])
    assert pa.exportar(caminho, lotes, 10, so_sem_perguntas=True, destino=destino) == 2  # o 3.º já tem; o articulado da Lei 100/2019 não entra
    _gravar(lotes / "saida-01.jsonl", [_linha("4.º", UTENTE), _linha("4.º", TAXAS)])
    r = pa.importar(lotes, destino, gerado="2026-11-20")
    assert (r["importados"], r["em_falta"]) == (2, [])
    assert sorted(p.name for p in destino.iterdir()) == ["avulsos-saude.jsonl"]
    assert [(x["documento"], x["chave"]) for x in pa._ler_jsonl(destino / "avulsos-saude.jsonl")] == [(UTENTE, "3.º"), (UTENTE, "4.º"), (TAXAS, "4.º")]


def test_ambito_sem_blocos_repetidos():
    # Cada (documento, parte) num só bloco, menos o Código Civil, partido por intervalo de artigos.
    partes = [(b.documento, b.parte) for b in pa.AMBITO]
    assert [p for p in set(partes) if partes.count(p) > 1] == [(CC, "Anexo — CÓDIGO CIVIL")]


def _nota(tipo, data):
    return f"{tipo} pelo/a Artigo 2.º do/a [Lei n.º 1/2000 - Diário da República n.º 1/2000, Série I de {data}](https://x), em vigor a partir de {data}"


def test_revogado_agora_olha_para_a_nota_mais_recente():
    # Código Civil: revogado em 2006 e outra vez aditado/alterado depois: em vigor.
    assert not pa.revogado_agora("1 - O contrato...", "\n".join([_nota("Revogado", "2006-06-27"), _nota("Alterado", "2019-02-13")]))
    assert pa.revogado_agora("1 - Caso o arrendatário...", "\n".join([_nota("Aditado", "2012-11-12"), _nota("Revogado", "2023-10-07")]))
    assert pa.revogado_agora("(Revogado.)", "")
    assert not pa.revogado_agora("Texto em vigor.", "")


BOA = {"documento": CT, "chave": "k", "perguntas": ["Quantos dias de férias tenho por ano?", "O patrão pode marcar as minhas férias sozinho?",
                                                    "Se ficar doente nas férias perco esses dias?"]}


@pytest.mark.parametrize(
    ("perguntas", "problema"),
    [
        (BOA["perguntas"][:2], "3 a 5"),
        (BOA["perguntas"] * 2, "3 a 5"),
        ([*BOA["perguntas"][:2], BOA["perguntas"][0]], "repetidas"),
        ([*BOA["perguntas"][:2], "Férias?"], "palavras"),
        ([*BOA["perguntas"][:2], "Quero saber quantos dias de férias tenho"], "não acaba"),
        ([*BOA["perguntas"][:2], "O que diz o artigo 238.º sobre férias?"], "cita"),
        ([*BOA["perguntas"][:2], "O Código do Trabalho deixa trabalhar ao domingo?"], "cita"),
        ([*BOA["perguntas"][:2], "A Lei n.º 6/2006 deixa subir a renda?"], "cita"),
        ([*BOA["perguntas"][:2], "O que diz o código da estrada sobre trotinetes?"], "cita"),
        ([*BOA["perguntas"][:2], "O Código Penal pune quem rouba comida?"], "cita"),
        ([*BOA["perguntas"][:2], "Segundo o Código de Processo Civil, quanto tempo tenho?"], "cita"),
        ([*BOA["perguntas"][:2], "O CIRS deixa deduzir a renda da casa?"], "cita"),
        ([*BOA["perguntas"][:2], "A Lei Geral Tributária deixa as Finanças penhorar?"], "cita"),
    ],
)
def test_validar_recusa_cada_regra(perguntas, problema):
    assert pa.validar(BOA, {"chave": "k"}) == []
    assert any(problema in p for p in pa.validar({**BOA, "perguntas": perguntas}, {"chave": "k"}))
    assert pa.validar(BOA, None) == ["chave que não está na entrada"]


@pytest.mark.parametrize(
    "pergunta",
    [
        "A lei não me deixa recusar as horas extra?",
        "Roubaram-me o código do multibanco, o banco tem de me devolver o dinheiro?",
        "Tenho de pôr o código postal certo na declaração do IRS?",
        "Quanto IVA pago numa fatura de obras em casa?",
        "Os contratos especiais seguem a lei geral do trabalho?",
        "Tenho de ir ao registo civil para casar?",
    ],
)
def test_validar_aceita_palavras_do_dia_a_dia(pergunta):
    linha = {**BOA, "perguntas": [*BOA["perguntas"][:2], pergunta]}
    assert pa.validar(linha, {"chave": "k"}) == []


def _indice_do_ambito(tmp_path):
    """Um índice pequeno com o Código do Trabalho, o Código Civil e o NRAU (chaves `parte::número`)."""
    ct = "Anexo — CÓDIGO DO TRABALHO"
    cc = "Anexo — CÓDIGO CIVIL"
    documentos = {
        **A,
        CT: ("Lei n.º 7/2009", "Aprova o Código do Trabalho", [
            ("", "1.º", "Objeto", "É aprovado o Código do Trabalho.", "2009-02-17", None),
            (ct, "238.º", "Duração das férias", "O período anual de férias tem a duração mínima de 22 dias úteis.", "2009-02-17", "2012-08-01"),
            (ct, "238.º", "Duração das férias", "O período anual de férias tem a duração mínima de 22 dias úteis, nova redação.", "2012-08-01", None),
            (ct, "239.º", "Revogado", "(Revogado.)", "2012-08-01", None),
        ], []),
        CC: ("Decreto-Lei n.º 47344", "Aprova o Código Civil", [
            (cc, "1021.º", "Liquidação de quotas", "Liquidação das quotas de sociedade.", "1967-06-01", None),
            (cc, "1069.º-A", "Forma", "O contrato de arrendamento urbano deve ser celebrado por escrito.", "2019-02-13", None),
            (cc, "1114.º", "Outra", "Disposição fora do arrendamento.", "1967-06-01", None),
        ], []),
        NRAU: ("Lei n.º 6/2006", "Aprova o Novo Regime do Arrendamento Urbano", [
            ("", "15.º", "Título para desocupação", "Não sendo o locado desocupado na data devida, o senhorio pode recorrer ao procedimento especial.", "2006-06-27", None),
            ("Anexo — Republicação do capítulo IV", "1069.º", "Forma", "Texto de 2006 republicado.", "2006-06-27", None),
        ], []),
    }
    caminho = _construir(tmp_path / "ambito.sqlite", documentos)
    with sqlite3.connect(caminho) as con:
        con.execute("UPDATE pedacos SET chave = parte || '::' || numero WHERE parte != ''")
    return caminho


def test_artigos_do_ambito_so_em_vigor_e_nao_revogados(tmp_path):
    indice = _indice_do_ambito(tmp_path)
    artigos = pa.artigos_do_ambito(indice)
    assert [(a["documento"], a["chave"]) for a in artigos] == [
        (CT, "Anexo — CÓDIGO DO TRABALHO::238.º"),
        (CC, "Anexo — CÓDIGO CIVIL::1069.º-A"),
        (NRAU, "15.º"),
        (CC, "Anexo — CÓDIGO CIVIL::1021.º"),  # o resto do Código Civil, uma só vez
        (CC, "Anexo — CÓDIGO CIVIL::1114.º"),
    ]
    assert artigos[0]["texto"].endswith("nova redação.")  # a redação em vigor, não a de 2009
    assert [a["chave"] for a in pa.artigos_do_ambito(indice, pa.PILOTO)] == [
        "Anexo — CÓDIGO DO TRABALHO::238.º", "Anexo — CÓDIGO CIVIL::1069.º-A", "15.º"]


def _linha(chave, documento=CC):
    return {"documento": documento, "chave": chave, "perguntas": BOA["perguntas"]}


def _gravar(caminho, linhas):
    caminho.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in linhas), encoding="utf-8")


def test_exportar_so_os_artigos_sem_perguntas_e_importar_sem_apagar_o_piloto(tmp_path):
    indice = _indice_do_ambito(tmp_path)
    destino = tmp_path / "perguntas"
    destino.mkdir()
    piloto = {"documento": CC, "chave": "Anexo — CÓDIGO CIVIL::1069.º-A", "perguntas": ["O contrato de arrendamento tem de ser por escrito?"]}
    _gravar(destino / "codigo-civil-arrendamento.jsonl", [piloto])
    _gravar(destino / "codigo-do-trabalho.jsonl", [{**piloto, "documento": CT, "chave": "Anexo — CÓDIGO DO TRABALHO::238.º"}])
    _gravar(destino / "nrau.jsonl", [{**piloto, "documento": NRAU, "chave": "15.º"}])
    lotes = tmp_path / "lotes"
    assert pa.exportar(indice, lotes, 1, so_sem_perguntas=True, destino=destino) == 2
    assert sorted(p.name for p in lotes.iterdir()) == ["entrada-01.jsonl", "entrada-02.jsonl"]
    assert pa.estado(lotes) == {"entrada-01.jsonl": ["sem saída"], "entrada-02.jsonl": ["sem saída"]}
    _gravar(lotes / "saida-01.jsonl", [_linha("Anexo — CÓDIGO CIVIL::1021.º")])
    _gravar(lotes / "saida-02.jsonl", [{**_linha("Anexo — CÓDIGO CIVIL::1114.º"), "perguntas": BOA["perguntas"][:2]}])
    assert pa.estado(lotes)["entrada-01.jsonl"] == []
    assert any("3 a 5" in p for p in pa.estado(lotes)["entrada-02.jsonl"])
    r = pa.importar(lotes, destino, gerado="2026-11-19")
    assert (r["importados"], r["em_falta"]) == (1, [(CC, "Anexo — CÓDIGO CIVIL::1114.º")])
    assert [x["chave"] for x in pa._ler_jsonl(destino / "codigo-civil.jsonl")] == ["Anexo — CÓDIGO CIVIL::1021.º"]
    assert pa._ler_jsonl(destino / "codigo-civil-arrendamento.jsonl") == [piloto]  # o piloto fica como estava
    assert len(pa.ler(destino)) == 4


def test_artigos_do_decreto_ficam_fora_do_bloco_do_codigo(tmp_path):
    cp = "pt:dre:185720:por"
    caminho = _construir(tmp_path / "cp.sqlite", {**A, cp: ("Decreto-Lei n.º 48/95", "Revê o Código Penal", [
        ("", "1.º", "", "O Código Penal é revisto e republicado.", "1995-10-01", None),
        ("", "1.º", "Princípio da legalidade", "Só pode ser punido criminalmente o facto descrito na lei.", "1995-10-01", None),
        ("", "2.º", "", "Artigo do decreto sem par no código.", "1995-10-01", None),
    ], [])})
    # Num índice de antes de 23/11/2026, com o código no articulado do decreto, o bloco (a parte do código) fica vazio.
    assert [a for a in pa.artigos_do_ambito(caminho) if a["documento"] == cp] == []
    # Hoje o código tem parte sua: só os artigos dessa parte entram (o helper põe a chave no número).
    parte = "Anexo — CÓDIGO PENAL"
    caminho = _construir(tmp_path / "cp2.sqlite", {**A, cp: ("Decreto-Lei n.º 48/95", "Revê o Código Penal", [
        ("", "1.º", "", "O Código Penal é revisto e republicado.", "1995-10-01", None),
        (parte, f"{parte}::1.º", "Princípio da legalidade", "Só pode ser punido criminalmente o facto descrito na lei.", "1995-10-01", None),
    ], [])})
    artigos = [a for a in pa.artigos_do_ambito(caminho) if a["documento"] == cp]
    assert [(a["chave"], a["epigrafe"]) for a in artigos] == [(f"{parte}::1.º", "Princípio da legalidade")]


def _ids(caminho, documento, chave):
    with sqlite3.connect(caminho) as con:
        return [i for (i,) in con.execute("SELECT id FROM pedacos WHERE documento = ? AND chave = ? ORDER BY id", (documento, chave))]


def test_juntar_perguntas_entra_so_na_redacao_em_vigor(tmp_path):
    caminho = _indice_do_ambito(tmp_path)
    chave = "Anexo — CÓDIGO DO TRABALHO::238.º"
    antiga, atual = _ids(caminho, CT, chave)
    assert _bm25(caminho, "zarabatana descanso") == []
    with sqlite3.connect(caminho) as con:
        r = juntar_perguntas(con, {(CT, chave): ["Posso levar a zarabatana de férias?"], (CT, "Anexo — CÓDIGO DO TRABALHO::999.º"): ["Nada?"]})
    assert r["artigos"] == 1 and r["pedacos"] == 1 and r["em_falta"] == [(CT, "Anexo — CÓDIGO DO TRABALHO::999.º")]
    p = Pesquisa(caminho)
    assert [i for i, _ in p.bm25("zarabatana", "2026-11-16")] == [atual]
    assert p.bm25("zarabatana", "2010-01-01") == []  # a redação de 2009 não ganhou as perguntas
    # O texto do artigo continua a ser encontrado como antes.
    assert atual in [i for i, _ in p.bm25("período anual de férias", "2026-11-16")]


def test_juntar_outra_vez_troca_as_perguntas(tmp_path):
    caminho = _indice_do_ambito(tmp_path)
    chave = (CT, "Anexo — CÓDIGO DO TRABALHO::238.º")
    with sqlite3.connect(caminho) as con:
        juntar_perguntas(con, {chave: ["Posso levar a zarabatana de férias?"]})
    uma_vez = _bm25(caminho, "zarabatana férias período")
    with sqlite3.connect(caminho) as con:
        juntar_perguntas(con, {chave: ["Posso levar a zarabatana de férias?"]})
    assert _bm25(caminho, "zarabatana férias período") == uma_vez  # repetir não muda nada
    with sqlite3.connect(caminho) as con:
        juntar_perguntas(con, {chave: ["E o berimbau nas férias?"]})
        assert perguntas_do_indice(con) == {chave: "E o berimbau nas férias?"}
    assert _bm25(caminho, "zarabatana") == []  # os termos antigos saíram do FTS
    assert _bm25(caminho, "berimbau")


def test_juntar_copia_o_indice(tmp_path):
    antes = _indice_do_ambito(tmp_path)
    pasta = tmp_path / "perguntas"
    pasta.mkdir()
    (pasta / "nrau.jsonl").write_text(
        json.dumps({"documento": NRAU, "chave": "15.º", "perguntas": ["O senhorio pode pôr-me na rua com a gaiola?"]}, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    depois = tmp_path / "depois.sqlite"
    assert pa.juntar(antes, depois, pasta)["artigos"] == 1
    assert _bm25(antes, "gaiola") == []
    assert [d for (d, _), _ in _bm25(depois, "gaiola")] == [NRAU]


# ---------------------------------------------------------------------------------------- deltas


def _com_perguntas(caminho, destino, perguntas):
    shutil.copyfile(caminho, destino)
    with sqlite3.connect(destino) as con:
        juntar_perguntas(con, perguntas)
        con.execute("INSERT INTO pedacos_fts (pedacos_fts) VALUES ('optimize')")
    return destino


def _perguntas(caminho):
    with sqlite3.connect(caminho) as con:
        return perguntas_do_indice(con)


def test_delta_leva_as_perguntas_e_volta_atras(tmp_path):
    antigo = _construir(tmp_path / "a.sqlite", A)
    novo = _com_perguntas(antigo, tmp_path / "b.sqlite", {("pt:c", "2.º"): ["O inquilino pode ter um papagaio em casa?"]})
    contagem = dados.gerar_delta(antigo, novo, tmp_path / "d.sqlite", "1", "2")
    assert contagem == {"mudados": 1, "removidos": 0}  # só o diploma das perguntas
    aplicado = tmp_path / "aplicado.sqlite"
    shutil.copyfile(antigo, aplicado)
    dados.aplicar_delta(aplicado, tmp_path / "d.sqlite")
    assert _conteudo(aplicado) == _conteudo(novo)
    assert _perguntas(aplicado) == _perguntas(novo)
    for pergunta in ("papagaio", "senhorio prazo", "prazo da coima do arguido"):
        assert _bm25(aplicado, pergunta) == _bm25(novo, pergunta), pergunta
    assert _bm25(aplicado, "papagaio")
    with sqlite3.connect(aplicado) as a, sqlite3.connect(novo) as n:
        assert dados.impressoes(a) == dados.impressoes(n)
    # E de volta, sem as perguntas: o delta apaga-as com os termos com que entraram.
    dados.gerar_delta(novo, antigo, tmp_path / "d2.sqlite", "2", "3")
    dados.aplicar_delta(aplicado, tmp_path / "d2.sqlite")
    assert _bm25(aplicado, "papagaio") == []
    assert _perguntas(aplicado) == {}
    for pergunta in ("senhorio prazo", "prazo da coima do arguido"):
        assert _bm25(aplicado, pergunta) == _bm25(antigo, pergunta), pergunta


def test_mudar_so_as_perguntas_muda_o_diploma(tmp_path):
    base = _construir(tmp_path / "a.sqlite", A)
    um = _com_perguntas(base, tmp_path / "um.sqlite", {("pt:c", "2.º"): ["O inquilino pode ter um papagaio em casa?"]})
    dois = _com_perguntas(base, tmp_path / "dois.sqlite", {("pt:c", "2.º"): ["O inquilino pode ter um periquito em casa?"]})
    assert dados.gerar_delta(um, dois, tmp_path / "d.sqlite", "1", "2") == {"mudados": 1, "removidos": 0}
    dados.aplicar_delta(um, tmp_path / "d.sqlite")
    assert _bm25(um, "papagaio") == []
    assert _bm25(um, "periquito") == _bm25(dois, "periquito") != []


def test_indice_sem_perguntas_tem_as_impressoes_de_sempre(tmp_path):
    caminho = _construir(tmp_path / "a.sqlite", A)
    with sqlite3.connect(caminho) as con:
        antes = dados.impressoes(con)
    with sqlite3.connect(caminho) as con:
        juntar_perguntas(con, {})  # a tabela vazia
        assert dados.impressoes(con) == antes


def test_publicar_recusa_as_perguntas_sem_a_opcao(tmp_path):
    indice = _com_perguntas(_construir(tmp_path / "a.sqlite", A), tmp_path / "i.sqlite", {("pt:c", "2.º"): ["O inquilino pode ter um papagaio?"]})
    with pytest.raises(RuntimeError, match="perguntas_artigo"):
        dados.publicar(indice, tmp_path / "pub", "2026-11-17", url_base="https://exemplo.pt/d/", remoto=False)
    manifesto, _ = dados.publicar(indice, tmp_path / "pub", "2026-11-17", url_base="https://exemplo.pt/d/", remoto=False, com_perguntas=True)
    assert manifesto["versao"] == "2026-11-17"


def test_reranker_com_perguntas_le_as_perguntas_do_artigo(tmp_path):
    indice = _com_perguntas(_construir(tmp_path / "a.sqlite", A), tmp_path / "i.sqlite", {("pt:c", "2.º"): ["Pergunta um?", "Pergunta dois?"]})
    simples, com = Pesquisa(indice), Pesquisa(indice, reranker_com_perguntas=True)
    r = simples._pedacos(_ids(indice, "pt:c", "2.º"))
    r = next(iter(r.values()))
    assert "Perguntas" not in simples._passagem(r)
    assert com._passagem(r) == f"{r.rotulo}\nPerguntas: Pergunta um? Pergunta dois?\n{r.texto}"
