import json

from rag import jurisprudencia as j
from rag import uniformizacao as u


# Um acórdão de fixação de jurisprudência como vem do DRE: o sumário é o segmento uniformizador; a
# fundamentação cita a jurisprudência fixada noutro acórdão; a decisão repete o texto entre aspas.
ACORDAO = """---
id: pt:dre:999:por
official_number: 11/2023
publication_date: '2023-11-20'
summary: «O requerimento apresentado pelo condenado, peticionando a substituição da multa por dias de trabalho, nos
  termos do artigo 48.º, n.º 1 do Código Penal, não integra a causa suspensiva da prescrição prevista no artigo
  125.º, n.º 1, alínea a), do Código Penal.»
subjects:
- Código Penal
source:
  official_url: https://diariodarepublica.pt/dr/detalhe/acordao-supremo-tribunal-justica/11-2023-999
---

# Acórdão do Supremo Tribunal de Justiça n.º 11/2023

Acordam no Pleno das Secções Criminais do Supremo Tribunal de Justiça:

II - Fundamentação

No Acórdão de fixação de jurisprudência n.º 2/2012 fixou-se jurisprudência nos seguintes termos: «A mera instauração
pelo Ministério Público de execução patrimonial contra o condenado em pena de multa não constitui a causa de
interrupção da prescrição da pena prevista no artigo 126.º, n.º 1, alínea a), do Código Penal.»

Desta forma, conclui-se que a apresentação do requerimento não integra a causa de suspensão da prescrição.

3 - jurisprudência fixada:

Em face do exposto, o Supremo Tribunal de Justiça, em Pleno das Secções Criminais, decidindo confirmar o acórdão
recorrido, fixa a seguinte jurisprudência:

«O requerimento apresentado pelo condenado, peticionando a substituição da multa por dias de trabalho, nos termos do
artigo 48.º, n.º 1 do Código Penal, não integra a causa suspensiva da prescrição prevista no artigo 125.º, n.º 1,
alínea a), do Código Penal.»

Sem custas.

Oportunamente, cumpra-se o disposto no artigo 444.º, n.º 1, do Código de Processo Penal.

Lisboa, 11 de outubro de 2023. - Fulano (Relator) - Beltrano

Declaração de voto

Fixaria jurisprudência em sentido oposto, nos termos do artigo 120.º do Código Penal.
"""


def _artigos(acordao):
    return [(n.artigo, n.diploma_texto) for n in acordao.normas]


def test_so_conta_a_jurisprudencia_deste_acordao():
    acordao = u.ler(ACORDAO, "STJ")
    assert (acordao.acordao, acordao.numero, acordao.tribunal) == ("pt:dre:999:por", "11/2023", "STJ")
    assert acordao.sentido == "fixa_jurisprudencia"
    assert acordao.fonte == "sumario" and acordao.confirmado
    # Nem o 126.º (do acórdão citado), nem o 444.º (o cumpra-se), nem o 120.º (da declaração de voto).
    assert _artigos(acordao) == [("48.º", "Código Penal"), ("125.º", "Código Penal")]
    assert all(n.principal for n in acordao.normas)


def test_data_da_decisao_e_da_publicacao_e_ligacao():
    acordao = u.ler(ACORDAO, "STJ")
    assert (acordao.data, acordao.publicacao) == ("2023-10-11", "2023-11-20")
    assert acordao.url == "https://diariodarepublica.pt/dr/detalhe/acordao-supremo-tribunal-justica/11-2023-999"


def test_decisao_que_cita_outro_acordao_no_fim_nao_confirma_o_sumario():
    # 8/2025: a última fórmula de fixação na decisão era a jurisprudência do AUJ n.º 11/2024, citada.
    texto = ("Fundamentação longa. " * 40 + "Na linha do Acórdão n.º 11/2024, que fixou jurisprudência no sentido de que "
             "«o despacho previsto no artigo 495.º, n.º 2, do CPP deve ser precedido de audição presencial do condenado».")
    sumario = "A pena suspensa prescreve decorridos 4 anos contados do termo do período de suspensão, nos termos do artigo 122.º do Código Penal"
    fixado, fonte, confirmado = u.texto_fixado(texto, sumario)
    assert fonte == "sumario" and not confirmado
    assert "122.º" in fixado


def test_sem_sumario_vale_a_decisao():
    texto = "Relatório. " * 60 + "Termos em que acordam em uniformizar a jurisprudência nos seguintes termos: «O artigo 147.º do CPTA não afasta a aplicação do artigo 142.º, n.º 5, do mesmo Código aos processos urgentes.» Sem custas."
    fixado, fonte, _ = u.texto_fixado(texto, "")
    assert fonte == "decisao"
    assert fixado.startswith("O artigo 147.º do CPTA")


def test_prefixos_do_sumario_do_sta():
    sumario = ("Acórdão do STA de 23-05-2024, no Processo n.º 129/22.4BALSB ― Pleno da 2.ª Secção ― Uniformiza-se a "
               "jurisprudência nos seguintes termos: «O artigo 64.º, n.º 3, alínea b), do Código do IRC deve ser interpretado…»")
    assert u.fixada_no_sumario(sumario).startswith("O artigo 64.º, n.º 3")
    sumario = ("Uniformiza a jurisprudência nos seguintes termos: Acórdão do STA de 3 de Julho de 2025, no processo n.º "
               "3807/23.7BELSB ― 1.ª Secção Julgamento Ampliado ― De acordo com o artigo 4.º do ETAF, compete aos tribunais…")
    assert u.fixada_no_sumario(sumario).startswith("De acordo com o artigo 4.º do ETAF")


def test_sentido_no_civel_e_no_sta():
    civel = (ACORDAO.replace("Pleno das Secções Criminais", "Pleno das Secções Cíveis").replace("- Código Penal", "- Direito Civil")
             .replace("fixação de jurisprudência", "uniformização de jurisprudência"))
    assert u.ler(civel, "STJ").sentido == "uniformiza_jurisprudencia"
    assert u.ler(ACORDAO, "STA").sentido == "uniformiza_jurisprudencia"


def _normas(texto):
    return [(n.artigo, n.diploma_texto) for n in j.normas(u.preparar(texto), j.SIGLAS, sigla_desconhecida=True)]


def test_codigos_com_o_ano_e_abreviaturas():
    assert _normas("excluídos da garantia do privilégio previsto no art. 377.º, n.º 1, al. b), do Código do Trabalho de 2003") == [
        ("377.º", "Lei n.º 99/2003")]
    assert _normas("Prescrevem no prazo de 5 anos, por aplicação analógica do art. 310.º/e) do C. Civil, as rendas") == [
        ("310.º", "Código Civil")]
    assert ("27.º", "Código das Expropriações") in _normas("fixada de acordo com o critério definido pelo art. 27.º do Cód. das Expropriações")
    assert _normas("princípio da igualdade [arts. 13.º da CRP e 05.º do CPA/91]") == [("5.º", "Decreto-Lei n.º 442/91")]


def test_redacao_originaria_nao_e_lei_de_alteracao():
    assert _normas("Nos termos do disposto na redacção originária do n.º 1 do artigo 10.º da Lei n.º 23/96, de 26 de Julho") == [
        ("10.º", "Lei n.º 23/96")]
    assert _normas("o vencimento imediato ao abrigo de cláusula de redacção conforme ao artigo 781.º do Código Civil") == [
        ("781.º", "Código Civil")]


def test_artigos_de_atos_da_ue_nao_vao_para_o_codigo_anterior():
    normas = _normas("não beneficia da isenção prevista no artigo 7.º, n.º 1, alínea e), do Código do Imposto do Selo, "
                     "por não se subsumir no conceito constante do artigo 3.º, n.º 1, ponto 22, da Directiva 2013/36/EU e do "
                     "artigo 4.º, n.º 1, ponto 26, do Regulamento UE n.º 575/2013")
    assert normas[0] == ("7.º", "Código do Imposto do Selo")
    assert ("3.º", "Directiva 2013/36") in normas and ("4.º", "Regulamento UE n.º 575/2013") in normas
    # "(CE Euratom)" não é o Código da Estrada.
    assert _normas("o previsto no artigo 3.º, n.º 1, do Reg. (CE Euratom) n.º 2988/95, do Conselho") == [
        ("3.º", "Reg. (CE Euratom) n.º 2988/95")]


def test_sigla_desconhecida_nao_passa_o_artigo_ao_diploma_seguinte():
    normas = _normas("nos termos do art. 17.º da Lei n.º 109/2009, aplicável por força do disposto no art. 13.º, n.º 1, "
                     "do RJX, e do art. 41.º, n.º 1, do RGCO")
    assert ("13.º", "RGCO") not in normas
    assert ("41.º", "RGCO") in normas and ("17.º", "Lei n.º 109/2009") in normas


def test_artigos_seguidos_depois_do_nome_e_da_data():
    assert _normas("prevista nos artigos 116.º, n.º 1, do Código do Registo Predial e 89.º e 101.º do Código do Notariado")[:3] == [
        ("116.º", "Código do Registo Predial"), ("89.º", "Código do Notariado"), ("101.º", "Código do Notariado")]
    normas = _normas("dos artigos 89.º e 61.º do Regime Geral das Contraordenações, aprovado pelo Decreto-Lei n.º 433/82, "
                     "de 27 de outubro, 183.º e 185.º-A do Código da Estrada")
    assert ("183.º", "Código da Estrada") in normas and ("185.º-A", "Código da Estrada") in normas


def test_mesma_lei_e_daquele_codigo():
    # "desta mesma lei" é a Lei n.º 6/84, mesmo sendo a da redação.
    normas = j.normas("não declarar a inconstitucionalidade dos artigos 140º e 141º do Código Penal, na redacção que lhes "
                      "foi dada pelo artigo 1º da Lei nº 6/84, de 11 de Maio, bem como dos artigos 2º e 3º desta mesma lei.")
    assert [(n.artigo, n.diploma_texto) for n in normas if n.artigo in {"2.º", "3.º"}] == [("2.º", "Lei nº 6/84"), ("3.º", "Lei nº 6/84")]
    normas = j.normas("decide não declarar a inconstitucionalidade das normas contidas nos artigos 83º e 84º da Lei n.º 91/2001, "
                      "de 20 de Agosto, aditadas pela Lei Orgânica n.º 2/2002, de 28 de Agosto, e no artigo 3º desta última Lei.")
    assert ("3.º", "Lei Orgânica n.º 2/2002") in [(n.artigo, n.diploma_texto) for n in normas]
    normas = j.normas("decide declarar a ilegalidade da norma contida no artigo 4.º-A do Decreto Legislativo Regional n.º 1/2009/M, "
                      "de 12 de Janeiro, aditado pelo artigo 2.º do Decreto Legislativo Regional n.º 9/2010/M, de 4 de Junho, bem "
                      "como da norma contida no artigo 4.º, n.º 2 deste último diploma.")
    assert [(n.artigo, n.numero) for n in normas] == [("4.º-A", "1/2009/M"), ("4.º", "9/2010/M")]
    # "daquele Código" não é o decreto-lei da redação citado entre parênteses.
    normas = _normas("Fora dos casos previstos no artigo 688.º do Código de Processo Civil (na redacção anterior ao "
                     "Decreto-Lei n.º 303/2007, de 24 de Setembro), deverá admiti-lo como requerimento para a conferência "
                     "prevista no artigo 700.º, n.º 3, daquele Código")
    assert normas == [("688.º", "Código de Processo Civil"), ("700.º", "Código de Processo Civil")]


def test_consulta_junta_tc_e_supremos_e_ordena(tmp_path):
    def linha(acordao, data, sentido, tribunal=None):
        norma = {"artigo": "48.º", "diploma_texto": "Código Penal", "tipo": None, "numero": None, "codigo": "Código Penal",
                 "documento": "pt:dre:cp:por", "parte": "", "artigo_encontrado": True, "principal": True}
        registo = {"acordao": acordao, "numero": acordao, "data": data, "url": None, "sentido": sentido,
                   "alinea": acordao, "normas": [norma]}
        if tribunal:
            registo["tribunal"] = tribunal
        return json.dumps(registo)

    tc_ficheiro, stj_ficheiro = tmp_path / "tc.jsonl", tmp_path / "stj.jsonl"
    tc_ficheiro.write_text("\n".join([linha("tc-julga", "2024-01-01", "julga"), linha("tc-fog", "2010-01-01", "declara_fog")]))
    stj_ficheiro.write_text(linha("stj-afj", "2020-01-01", "fixa_jurisprudencia", "STJ"))
    consulta = j.Jurisprudencia((tc_ficheiro, stj_ficheiro))
    lista = consulta.por_artigo("pt:dre:cp:por", "48.º")
    assert [x["acordao"] for x in lista] == ["tc-fog", "stj-afj", "tc-julga"]
    assert [x["tribunal"] for x in lista] == ["TC", "STJ", "TC"]
    assert j.titulo_acordao(lista[1]) == "Acórdão do STJ n.º stj-afj"
    assert j.ROTULOS["fixa_jurisprudencia"] == "Fixa jurisprudência"
    # Um ficheiro que falta (a aplicação 0.1.1 só traz o do TC) não impede a consulta.
    assert j.Jurisprudencia((tc_ficheiro, tmp_path / "nao-existe.jsonl")).por_artigo("pt:dre:cp:por", "48.º")


def test_resolvedor_escolhe_o_anexo_pelo_nome_e_corta_palavras_a_mais():
    import sqlite3

    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE pedacos (documento TEXT, numero TEXT, parte TEXT)")
    con.executemany("INSERT INTO pedacos VALUES (?, ?, ?)", [
        ("lei-22a", "3.º", "Anexo I — Código do Imposto sobre Veículos"),
        ("lei-22a", "3.º", "Anexo II — Código do Imposto Único de Circulação"),
        ("dl-224", "7.º", ""), ("dl-224", "7.º", "Anexo — Tabela de emolumentos do registo predial"),
        ("dl-48", "348.º", ""),
    ])

    class Pesquisa:
        def __init__(self):
            self.con = con

        def diplomas(self, tipo, numero):
            return {("lei", "22-A/2007"): ["lei-22a"], ("decreto-lei", "224/84"): ["dl-224"]}.get((tipo, numero), [])

        def codigo(self, nome):
            return [("dl-48", "")] if nome == "Código Penal" else []

    resolvedor = u.Resolvedor(Pesquisa())
    iuc = resolvedor.resolver(j.Norma("3.º", "Código do Imposto Único de Circulação", "lei", "22-A/2007"), "2026-01-01")
    assert iuc.parte.startswith("Anexo II")
    predial = resolvedor.resolver(j.Norma("7.º", "Código do Registo Predial", "decreto-lei", "224/84"), "2017-01-01")
    assert predial.parte == ""
    penal = resolvedor.resolver(j.Norma("348.º", "Código Penal e não o crime de desobediência qualificada do artigo",
                                        codigo="Código Penal e não o crime de desobediência qualificada do artigo"), "2009-02-18")
    assert penal.documento == "dl-48" and penal.artigo_encontrado


def test_codigos_antigos_pelo_ano_e_pela_data():
    assert _normas("Requerida a abertura da instrução ao abrigo do n.º 2 do artigo 391.º do Código de Processo Penal de 1929, "
                   "não caduca a interrupção da prescrição nos termos do artigo 120.º, n.º 1, do Código Penal de 1982") == [
        ("391.º", "Decreto n.º 16489"), ("120.º", "Decreto-Lei n.º 400/82")]
    assert _normas("nos termos do artigo 79.º, n.º 1, do Código de Processo do Trabalho de 1981, para obter o efeito suspensivo") == [
        ("79.º", "Decreto-Lei n.º 272-A/81")]
    # Num acórdão anterior à revisão de 1995, o "Código Penal" é o de 1982.
    cp = j.Norma("142.º", "Código Penal", codigo="Código Penal")
    antigo = j.no_tempo(cp, "1991-12-18")
    assert (antigo.tipo, antigo.numero) == ("decreto-lei", "400/82")
    assert j.no_tempo(cp, "1996-03-14") is cp


def test_artigo_ja_citado_e_artigo_que_altera_nao_contam():
    normas = _normas("Quando o procedimento se reporte a um dos crimes referidos no n.º 1 do artigo 54.º do Decreto-Lei n.º 15/93, "
                     "a elevação dos prazos nos termos do n.º 3 do artigo 215.º do Código de Processo Penal decorre do disposto no "
                     "n.º 3 daquele artigo 54.º")
    assert normas == [("54.º", "Decreto-Lei n.º 15/93"), ("215.º", "Código de Processo Penal")]
    normas = _normas("As normas do artigo 74.º do Código de Processo Civil, resultantes da alteração decorrente do artigo 1.º da "
                     "Lei n.º 14/2006, de 26 de Abril, aplicam-se às acções instauradas após a sua entrada em vigor")
    assert ("1.º", "Lei n.º 14/2006") not in normas


def test_codigo_penal_de_1982_revisto_em_1995_e_o_atual():
    normas = _normas("da alínea a) do n.º 1 do artigo 119.º do Código Penal de 1982, versão original, ou da alínea a) do n.º 1 "
                     "do artigo 120.º do Código Penal de 1982, revisão de 1995")
    assert normas == [("119.º", "Decreto-Lei n.º 400/82"), ("120.º", "Código Penal")]
    assert _normas("aplica-se o disposto no artigo 107.º do Código Penal, na versão de 1982, ressalvando-se") == [
        ("107.º", "Decreto-Lei n.º 400/82")]
