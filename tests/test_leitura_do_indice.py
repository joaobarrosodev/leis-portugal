"""O que o índice lê de um registo (20/11/2026): unidades que não são `###### Artigo`, anexos sem artigos,
históricos sem artigos e revogações que ainda não produziram efeitos."""

import json
import re
import sqlite3

from rag import indice, referencias
from rag.fontes import efeitos_da_revogacao, fora_dos_artigos, ler_artigos, revogacao_por_produzir_efeitos, revogado
from rag.indice import Documento, Pedaco, _com_historico, pedacos_do_documento, rotulo


# ---------------------------------------------------------------------------------- o leitor


def _sem_linhas_vazias_a_mais(texto: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", texto)


def test_artigo_em_maiusculas_le_se_como_os_outros():
    texto = "###### ARTIGO 1.º\n\nUm.\n\n###### ARTIGO 2.º — Âmbito\n\nDois.\n\n###### ARTIGO 12.º-A\n\nDoze A.\n\n###### ARTIGO ÚNICO\n\nÚnico.\n\n###### ARTIGO IV\n\nQuatro."
    assert [(a.chave, a.epigrafe, a.texto) for a in ler_artigos(texto)] == [
        ("1.º", "", "Um."), ("2.º", "Âmbito", "Dois."), ("12.º-A", "", "Doze A."), ("único", "", "Único."), ("IV", "", "Quatro.")]


def test_artigo_em_maiusculas_com_o_texto_no_titulo():
    # Textos antigos: «###### ARTIGO 30.º — É facultado…» com o artigo inteiro depois do travessão.
    comprido = "É facultado aos interessados " + "requerer a revisão " * 12
    lidos = ler_artigos(f"###### ARTIGO 30.º — {comprido}\n\nSegundo parágrafo.\n\n###### Artigo 31.º — {comprido}\n\nTexto.")
    assert (lidos[0].numero, lidos[0].epigrafe) == ("30.º", "") and lidos[0].texto.startswith("É facultado") and lidos[0].texto.endswith("Segundo parágrafo.")
    assert lidos[1].epigrafe == comprido.strip()  # nos títulos «Artigo» nada muda


def test_bases_e_numeros_sao_unidades_com_o_nome_no_numero():
    texto = ("### Capítulo I\n\n###### Base I — Âmbito\n\nUma.\n\n###### BASE II\n\nDuas.\n\n###### Base 3.ª — Fim\n\nTrês.\n\n"
             "###### Base de cálculo\n\nNão é uma base.\n\n###### 1.º\n\nPrimeiro.\n\n###### 2.º\n\nSegundo.\n\n###### 3.º — Com epígrafe\n\nNão é um número.")
    lidos = ler_artigos(texto)
    assert [(a.chave, a.epigrafe) for a in lidos] == [("Base I", "Âmbito"), ("Base II", ""), ("Base 3.ª", "Fim"), ("N.º 1.º", ""), ("N.º 2.º", "")]
    assert lidos[2].texto.endswith("Não é uma base.") and lidos[4].texto.endswith("Não é um número.")


def test_anexo_em_maiusculas_abre_parte():
    texto = ("###### Artigo 1.º — Objeto\n\nAprova.\n\n###### Artigo 2.º — Vigência\n\nAmanhã.\n\nAssinaturas.\n\n"
             "## ANEXO — Regulamento\n\n###### Artigo 1.º — Âmbito\n\nTexto.\n\n## Anexo II\n\n###### Base I\n\nBase.")
    lidos = ler_artigos(texto)
    assert [a.chave for a in lidos] == ["1.º", "2.º", "Regulamento (ANEXO)::1.º", "Anexo II::Base I"]
    assert lidos[1].texto == "Amanhã.\n\nAssinaturas."


def test_nome_da_parte_de_um_anexo():
    from rag.fontes import comum

    # `## Anexo …` fica como sempre; em maiúsculas e com título, o título vem à frente (a aplicação 0.1.1 procura os
    # códigos nas partes que começam por «Anexo», sem olhar a maiúsculas).
    assert comum._nome_do_anexo("Anexo — CÓDIGO DO TRABALHO") == "Anexo — CÓDIGO DO TRABALHO"
    assert comum._nome_do_anexo("ANEXO — Código de Processo Penal") == "Código de Processo Penal (ANEXO)"
    assert comum._nome_do_anexo("ANEXO I — ESTATUTOS DA SIEV, S. A.") == "ESTATUTOS DA SIEV, S. A. (ANEXO I)"
    assert comum._nome_do_anexo("ANEXO II") == "ANEXO II"
    assert comum._nome_do_anexo("ANEXO — (a que se refere o artigo 1.º)") == "ANEXO — (a que se refere o artigo 1.º)"
    assert not any(comum._nome_do_anexo(t).lower().startswith("anexo") for t in ("ANEXO — Código de Processo Penal", "ANEXO II — CÓDIGO DAS CUSTAS JUDICIAIS"))


def test_registo_em_texto_corrido_com_titulos_soltos_nao_se_parte():
    # O Código Penal de 1982 (DL 400/82): centenas de «ARTIGO N.º» em texto corrido e dois títulos soltos pelo meio.
    corrido = "\n\n".join(f"ARTIGO {n}.º\n\nTexto do artigo {n}." for n in range(1, 13))
    texto = corrido + "\n\n###### ARTIGO 128.º\n\nTexto.\n\n###### ARTIGO 130.º\n\nTexto.\n\nArtigo 131.º Mais texto corrido."
    assert ler_artigos(texto) == [] and fora_dos_artigos(texto) == []
    # Com um título `###### Artigo`, lê-se como sempre se leu.
    assert [a.chave for a in ler_artigos(texto.replace("###### ARTIGO 128.º", "###### Artigo 128.º"))] == ["128.º", "130.º"]
    # E com poucas linhas soltas face aos títulos (o decreto que aprova uma convenção), parte-se pelos títulos.
    convencao = "Artigo único. É aprovada a convenção.\n\n" + "\n\n".join(f"###### ARTIGO {n}.º\n\nTexto." for n in range(1, 21))
    assert len(ler_artigos(convencao)) == 20


def test_anexo_em_maiusculas_sem_artigos_fica_colado_ao_artigo_anterior():
    texto = ("###### Artigo 1.º — Objeto\n\nAprova a tabela.\n\n## ANEXO I — Tabela de taxas\n\n| Ato | Taxa |\n| Registo | 10 |\n\n"
             "## ANEXO II — Regulamento\n\nPreâmbulo do regulamento.\n\n###### Artigo 1.º\n\nTexto.\n\n## ANEXO III\n\nTabela final.")
    lidos = ler_artigos(texto)
    # A tabela e o preâmbulo do regulamento ficam no artigo 1.º do diploma, como antes; o anexo II só abre parte no seu
    # primeiro artigo; a tabela final cola-se a esse artigo.
    assert [(a.chave, _sem_linhas_vazias_a_mais(a.texto)) for a in lidos] == [
        ("1.º", "Aprova a tabela.\n\n| Ato | Taxa |\n| Registo | 10 |\n\nPreâmbulo do regulamento."), ("Regulamento (ANEXO II)::1.º", "Texto.\n\nTabela final.")]
    # Um `## Anexo` fecha o artigo, como sempre: o texto antes do primeiro artigo do anexo não entra.
    antigo = ler_artigos(texto.replace("## ANEXO II — Regulamento", "## Anexo II — Regulamento"))
    assert [(a.chave, _sem_linhas_vazias_a_mais(a.texto)) for a in antigo] == [("1.º", "Aprova a tabela.\n\n| Ato | Taxa |\n| Registo | 10 |"), ("Anexo II — Regulamento::1.º", "Texto.\n\nTabela final.")]


def test_fora_dos_artigos_e_o_texto_antes_do_primeiro_artigo_de_cada_parte():
    texto = "Preâmbulo.\n\n## Título I\n\nMais.\n\n###### Artigo 1.º\n\nTexto.\n\n## Anexo I\n\nAntes.\n\n###### Artigo 1.º\n\nA.\n\n## Anexo II — Tabela\n\nLinha."
    assert [(p, _sem_linhas_vazias_a_mais(t)) for p, t in fora_dos_artigos(texto)] == [("", "Preâmbulo.\n\nMais."), ("Anexo I", "Antes."), ("Anexo II — Tabela", "Linha.")]
    assert fora_dos_artigos("Só texto corrido.") == []


# ---------------------------------------------------------------------------------- o índice


def _registo(tmp_path, monkeypatch, corpo, historico=None):
    monkeypatch.setattr(indice, "RAIZ", tmp_path)
    (tmp_path / "doc.md").write_text(f"---\nid: pt:x\n---\n\n# Diploma\n\n{corpo}", encoding="utf-8")
    if historico is not None:
        (tmp_path / "doc.versoes.json").write_text(json.dumps(historico), encoding="utf-8")
    return Documento("pt:x", "Portaria n.º 1/2020", "portaria", "1/2020", "2020-01-10", "Sumário", "in_force", "consolidated" if historico else "original", None, "doc.md")


def _versao(data, fragmentos):
    return {"date": data, "fragments": fragmentos}


def test_rotulo_das_bases_e_dos_numeros():
    doc = Documento("pt:x", "Lei n.º 52/2012", "lei", "52/2012", "2012-09-05", "", "in_force", "consolidated", None, "x.md")
    assert rotulo(doc, "", "Base IV", "Princípios") == "Lei n.º 52/2012, de 2012-09-05 › Base IV — Princípios"
    assert rotulo(doc, "", "N.º 3.º", "") == "Lei n.º 52/2012, de 2012-09-05 › N.º 3.º"
    assert rotulo(doc, "Anexo", "4.º", "Âmbito") == "Lei n.º 52/2012, de 2012-09-05 › Anexo › Artigo 4.º — Âmbito"


def test_historico_sem_artigos_entra_em_blocos_versao_a_versao(tmp_path, monkeypatch):
    historico = {
        "versions": [_versao("2020-01-10", ["t1"]), _versao("2023-05-01", ["t2"])],
        "fragments": {"t1": {"markdown": "É fixada a taxa de 10 euros."}, "t2": {"markdown": "É fixada a taxa de 12 euros."}},
    }
    pedacos, _, com_historico = pedacos_do_documento(_registo(tmp_path, monkeypatch, "É fixada a taxa de 12 euros.", historico))
    assert com_historico
    assert sorted((p.chave, p.numero, p.texto, p.desde, p.ate) for p in pedacos) == [
        ("texto#1", "", "É fixada a taxa de 10 euros.", "2020-01-10", "2023-05-01"), ("texto#1", "", "É fixada a taxa de 12 euros.", "2023-05-01", None)]


def test_historico_que_nao_da_pedacos_le_o_md(tmp_path, monkeypatch):
    historico = {"versions": [_versao("2020-01-10", ["t1"])], "fragments": {"t1": {"markdown": ""}}}
    pedacos, _, com_historico = pedacos_do_documento(_registo(tmp_path, monkeypatch, "###### Artigo 1.º — Taxa\n\nDez euros.", historico))
    assert com_historico and [(p.chave, p.texto, p.desde, p.ate) for p in pedacos] == [("1.º", "Dez euros.", "2020-01-10", None)]


def test_historico_com_bases_da_um_pedaco_por_base():
    historico = {
        "versions": [_versao("2012-09-05", ["b1", "b2"]), _versao("2026-05-09", ["b1", "b2n"])],
        "fragments": {"b1": {"markdown": "###### Base I — Âmbito\n\nA presente lei consagra o direito."}, "b2": {"markdown": "###### Base II — Conceitos\n\nAntes."},
                      "b2n": {"markdown": "###### Base II — Conceitos\n\nDepois."}},
    }
    assert sorted((p.chave, p.epigrafe, p.texto, p.ate) for p in _com_historico(historico)) == [
        ("Base I", "Âmbito", "A presente lei consagra o direito.", None), ("Base II", "Conceitos", "Antes.", "2026-05-09"), ("Base II", "Conceitos", "Depois.", None)]


def test_anexo_sem_artigos_nao_da_pedacos_novos(tmp_path, monkeypatch):
    corpo = ("###### Artigo 1.º — Objeto\n\nAprova a tabela.\n\n## ANEXO — Tabela\n\nPrimeira linha da tabela.\n\nSegunda linha.\n\n"
             "## Anexo II — Regulamento\n\nPreâmbulo.\n\n###### Artigo 1.º\n\nTexto.")
    pedacos, _, _ = pedacos_do_documento(_registo(tmp_path, monkeypatch, corpo))
    assert [(p.parte, p.chave, _sem_linhas_vazias_a_mais(p.texto)) for p in pedacos] == [
        ("", "1.º", "Aprova a tabela.\n\nPrimeira linha da tabela.\n\nSegunda linha."), ("Anexo II — Regulamento", "Anexo II — Regulamento::1.º", "Texto.")]
    # Sem artigos nenhuns, o registo inteiro continua em blocos na parte vazia, com o anexo incluído.
    so_texto, _, _ = pedacos_do_documento(_registo(tmp_path, monkeypatch, "Texto do despacho.\n\n## ANEXO\n\nTabela."))
    assert [(p.parte, p.chave) for p in so_texto] == [("", "texto#1")] and "Tabela." in so_texto[0].texto


def test_abertura_de_um_registo_so_com_titulos_novos_entra_em_blocos(tmp_path, monkeypatch):
    comprida = "Considerando o disposto na convenção e as tabelas seguintes. " * 8
    # Um registo só com títulos das formas novas entrava inteiro em blocos: o texto antes do primeiro título continua a entrar.
    convencao = f"Artigo único. É aprovada para ratificação a convenção. {comprida}\n\n###### ARTIGO 1.º\n\nAs Partes.\n\n###### ARTIGO 2.º\n\nEntra em vigor."
    pedacos, _, _ = pedacos_do_documento(_registo(tmp_path, monkeypatch, convencao))
    assert [(p.chave, p.numero) for p in pedacos] == [("1.º", "1.º"), ("2.º", "2.º"), ("texto#1", "")] and pedacos[-1].texto.startswith("Artigo único.")
    # Um `## Anexo` sem artigos de um registo destes também entrava em blocos, e continua (na parte do anexo).
    com_anexo, _, _ = pedacos_do_documento(_registo(tmp_path, monkeypatch, convencao + f"\n\n## Anexo com disposições padrão\n\n{comprida}"))
    assert [(p.parte, p.chave) for p in com_anexo][-1] == ("Anexo com disposições padrão", "Anexo com disposições padrão::texto#1")
    # Uma abertura pequena (o nome do capítulo) não dá bloco, e o preâmbulo de um registo com `###### Artigo` nunca entrou.
    assert [p.chave for p in pedacos_do_documento(_registo(tmp_path, monkeypatch, "### Capítulo I\n\nDisposições gerais\n\n###### Base I\n\nTexto."))[0]] == ["Base I"]
    assert [p.chave for p in pedacos_do_documento(_registo(tmp_path, monkeypatch, f"{comprida}\n\n###### Artigo 1.º\n\nTexto."))[0]] == ["1.º"]


def test_o_que_passa_do_limite_de_um_artigo_em_maiusculas_entra_em_blocos(tmp_path, monkeypatch):
    # Uma lei do orçamento antiga: um título «ARTIGO» e os mapas todos colados a ele.
    mapas = "\n\n".join(f"Mapa {n}: " + "verba e dotação " * 60 for n in range(60))
    assert len(mapas) > indice.MAX_CARACTERES
    pedacos, _, _ = pedacos_do_documento(_registo(tmp_path, monkeypatch, f"###### ARTIGO 1.º\n\nÉ aprovado o orçamento.\n\n{mapas}"))
    assert pedacos[0].chave == "1.º" and [p.chave for p in pedacos[1:3]] == ["texto#1", "texto#2"]
    assert "Mapa 59" in pedacos[-1].texto and all(p.numero == "" for p in pedacos[1:])
    # Num registo com títulos `###### Artigo` nada muda: o artigo é cortado no limite, como sempre.
    antigo, _, _ = pedacos_do_documento(_registo(tmp_path, monkeypatch, f"###### Artigo 1.º\n\nÉ aprovado o orçamento.\n\n{mapas}"))
    assert [p.chave for p in antigo] == ["1.º"]


# ---------------------------------------------------------------------------------- a revogação e a data de efeitos

FUTURA = ("Revogado pelo/a Artigo 62.º do/a [Decreto-Lei n.º 166/2026 - Diário da República n.º 156/2026, Série I de 2026-08-13](https://x), "
          "em vigor a partir de 2026-08-14, com efeitos a partir de 2026-12-31.")
ANTIGA = "Revogado pelo/a Artigo 3.º do/a [Lei n.º 45/2005 - Diário da República n.º 165/2005, Série I-A de 2005-08-29](https://x), em vigor a partir de 2005-10-28"
ALTERADO = "Alterado pelo/a Artigo 2.º do/a [Decreto-Lei n.º 90/2017 - Diário da República n.º 145/2017, Série I de 2017-07-28](https://x), em vigor a partir de 2017-07-29"


def test_efeitos_da_revogacao_e_a_data_mais_tardia_da_nota():
    assert efeitos_da_revogacao(FUTURA) == "2026-12-31"
    assert efeitos_da_revogacao(ANTIGA) == "2005-10-28"
    assert efeitos_da_revogacao("Revogado pelo/a Lei n.º 1/2020, em vigor a partir de 2021-01-01, produz efeitos a partir de 2020-06-01") == "2021-01-01"
    assert efeitos_da_revogacao("Revogado pelo/a Lei n.º 7/2009") is None


def test_revogacao_so_conta_quando_produz_efeitos():
    notas = FUTURA + "\n" + ALTERADO
    assert revogado("A presente lei institui o rendimento social de inserção.", notas)  # sem data, como antes
    assert not revogado("A presente lei institui o rendimento social de inserção.", notas, "2026-11-20")
    assert not revogado("A presente lei institui o rendimento social de inserção.", notas, "2026-12-30")
    assert revogado("A presente lei institui o rendimento social de inserção.", notas, "2026-12-31")
    # Já revogado antes por outra nota, com o texto «(Revogado.)» ou sem data na nota: continua revogado.
    assert revogado("Texto.", FUTURA + "\n" + ANTIGA, "2026-11-20")
    assert revogado("(Revogado.)", FUTURA, "2026-11-20")
    assert revogado("Texto.", "Revogado pelo/a Lei n.º 7/2009", "2026-11-20")
    # Uma pergunta com data anterior à revogação antiga também não a vê.
    assert not revogado("Texto.", ANTIGA, "2004-01-01")


def test_revogacao_por_produzir_efeitos_diz_a_data_e_a_nota():
    assert revogacao_por_produzir_efeitos(FUTURA + "\n" + ALTERADO, "2026-11-20") == ("2026-12-31", FUTURA)
    assert revogacao_por_produzir_efeitos(FUTURA, "2026-12-31") is None
    assert revogacao_por_produzir_efeitos(FUTURA + "\n" + ANTIGA, "2026-11-20") is None
    assert revogacao_por_produzir_efeitos(ALTERADO, "2026-11-20") is None


def test_pesquisa_avisa_de_que_o_artigo_ainda_esta_em_vigor(tmp_path):
    from rag.pesquisa import Pesquisa

    from test_dados import ENCHIMENTO, _construir

    caminho = _construir(tmp_path / "i.sqlite", {
        **ENCHIMENTO,
        "pt:rsi": ("Lei n.º 13/2003", "Rendimento social de inserção", [
            ("", "1.º", "Objecto", "A presente lei institui o rendimento social de inserção para os agregados carenciados", "2026-08-14", None),
            ("", "7.º", "Condições", "Condições específicas de atribuição do rendimento social de inserção", "2005-10-28", None)], []),
    })
    con = sqlite3.connect(caminho)
    con.execute("UPDATE pedacos SET notas = ? WHERE documento = 'pt:rsi' AND numero = '1.º'", (FUTURA,))
    con.execute("UPDATE pedacos SET notas = ? WHERE documento = 'pt:rsi' AND numero = '7.º'", (ANTIGA,))
    con.commit()
    con.close()
    pesquisa = Pesquisa(caminho)

    def avisos(data):
        return {r.numero: r.avisos for r in pesquisa.pesquisar("rendimento social de inserção", data, k=5).resultados if r.documento == "pt:rsi"}

    hoje = avisos("2026-11-20")
    assert not any(a.startswith("Artigo revogado") for a in hoje["1.º"]) and any("2026-12-31" in a and a.startswith("Em vigor até") for a in hoje["1.º"])
    assert any(a.startswith("Artigo revogado") for a in hoje["7.º"])
    assert list(hoje) == ["1.º", "7.º"]  # o que ainda vigora fica à frente do revogado
    assert any(a.startswith("Artigo revogado") for a in avisos("2027-01-02")["1.º"])


# ---------------------------------------------------------------------------------- as referências


def test_referencia_a_uma_base():
    assert referencias.extrair("O que diz a base IV da Lei n.º 52/2012?").artigos == ["Base IV", "Base 4"]
    assert referencias.extrair("Base 20 e artigo 3.º da Lei n.º 95/2019").artigos == ["3.º", "Base XX", "Base 20"]
    assert referencias.extrair("Qual é o salário base de 1000 euros e com base em que lei?").artigos == []


def test_o_pedaco_guarda_o_nome_da_unidade_no_numero():
    assert Pedaco("", "Base I", "Âmbito", "Base I", "Texto.", "", None, None).numero.startswith(indice.NAO_SAO_ARTIGOS)
