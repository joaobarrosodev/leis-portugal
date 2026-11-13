"""Artigos com id estável, datas de entrada em vigor e provas de vigência, com casos reais."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import record_dict
from leis_portugal.cli import main
from leis_portugal.domain.articles import number_slug, parse_articles, part_slug
from leis_portugal.domain.entry_into_force import compute, extract
from leis_portugal.domain.validity import label_scope, propose, repeals_in
from leis_portugal.infrastructure.markdown import render_markdown
from leis_portugal.services.structure import compare, competent, plausible


def link(label: str, path: str) -> str:
    return f"[{label}](https://diariodarepublica.pt/dr/detalhe/{path})"


# Lei n.º 7/2009 (excerto): o Código do Trabalho em anexo repete a numeração do diploma.
LEI_7_2009 = """# Lei n.º 7/2009

A Assembleia da República decreta, nos termos da alínea c) do artigo 161.º da Constituição, o seguinte:

###### Artigo 1.º — Aprovação do Código do Trabalho

É aprovado o Código do Trabalho, que se publica em anexo à presente lei e dela faz parte integrante.

###### Artigo 3.º — Trabalho autónomo de menor

1 - O menor com idade inferior a 16 anos não pode ser contratado para realizar uma actividade remunerada.

> Alterado pelo(a) Lei n.º 47/2012

###### Artigo 14.º — Entrada em vigor

2 - Os artigos 34.º a 62.º entram em vigor na data de início de vigência da legislação que regule o regime de protecção social da parentalidade.

Aprovada em 21 de Janeiro de 2009.

O Presidente da Assembleia da República, Jaime Gama.

## Anexo — CÓDIGO DO TRABALHO

## Livro I — Parte geral

## Título I — Fontes e aplicação do direito do trabalho

### Capítulo I — Fontes do direito do trabalho

###### Artigo 1.º — Fontes específicas

O contrato de trabalho está sujeito, em especial, aos instrumentos de regulamentação colectiva de trabalho.

###### Artigo 3.º — Relações entre fontes de regulação

1 - As normas legais reguladoras de contrato de trabalho podem ser afastadas por instrumento de regulamentação colectiva de trabalho.

###### Artigo 10.º-A — Representação e negociação coletiva

1 - As pessoas em situação de dependência económica podem ser representadas.
"""


def test_articles_are_split_by_part_with_stable_ids():
    articles = parse_articles(LEI_7_2009)
    ids = [article.id("pt:dre:602073:por") for article in articles]
    assert ids == [
        "pt:dre:602073:por#art-1",
        "pt:dre:602073:por#art-3",
        "pt:dre:602073:por#art-14",
        "pt:dre:602073:por#anexo-codigo-do-trabalho/art-1",
        "pt:dre:602073:por#anexo-codigo-do-trabalho/art-3",
        "pt:dre:602073:por#anexo-codigo-do-trabalho/art-10-a",
    ]
    diploma_3, code_3 = articles[1], articles[4]
    assert diploma_3.heading == "Trabalho autónomo de menor"
    assert diploma_3.notes == ["Alterado pelo(a) Lei n.º 47/2012"]
    assert code_3.part == "Anexo — CÓDIGO DO TRABALHO"
    assert code_3.heading == "Relações entre fontes de regulação"
    assert code_3.text.startswith("1 - As normas legais")
    # A assinatura não faz parte do último artigo do diploma.
    assert "Aprovada em" not in articles[2].text


def test_annex_without_the_word_anexo_and_uppercase_annex():
    # Decreto-Lei n.º 198/2001: o CIRS vem num título que não começa por "Anexo".
    text = """# Decreto-Lei n.º 198/2001

###### Artigo 1.º — Objecto

É aprovada a revisão do Código do Imposto sobre o Rendimento das Pessoas Singulares.

## CÓDIGO DO IMPOSTO SOBRE O RENDIMENTO DAS PESSOAS SINGULARES

### Capítulo I — Incidência

###### Artigo 1.º — Base do imposto

1 - O imposto sobre o rendimento das pessoas singulares (IRS) incide sobre o valor anual dos rendimentos.

## ANEXO II (a que se refere o n.º 2 do artigo 1.º do regulamento)

###### Artigo 1.º — Objeto

Texto.
"""
    anchors = [article.anchor for article in parse_articles(text)]
    assert anchors == ["art-1", "codigo-do-imposto-sobre-o-rendimento-das-pessoas-singulares/art-1", "anexo-ii/art-1"]


@pytest.mark.parametrize(
    ("title", "slug"),
    [
        ("Anexo — CÓDIGO DO TRABALHO", "anexo-codigo-do-trabalho"),
        ("ANEXO II (a que se refere o n.º 2 do artigo 1.º)", "anexo-ii"),
        ("Anexo I — Regulamento", "anexo-i"),
        ("Anexo (a que se refere o artigo 2.º)", "anexo"),
        ("Anexo a que se refere o artigo 1.º", "anexo"),
        ("ANEXO A", "anexo-a"),
        ("ANEXO — ([Portaria n.º 387/95](https://diariodarepublica.pt/dr/detalhe/portaria/387-1995-1))", "anexo"),
    ],
)
def test_part_slug(title, slug):
    assert part_slug(title) == slug


@pytest.mark.parametrize(("number", "slug"), [("3.º", "3"), ("10.º-A", "10-a"), ("1º", "1"), ("único", "unico"), ("IV", "iv"), ("23", "23")])
def test_number_slug(number, slug):
    assert number_slug(number) == slug


def test_plain_text_articles_of_an_old_decree():
    # Decreto-Lei n.º 46067, de 7 de dezembro de 1964 (texto corrido, "Artigo 1.º" e "Art. 2.º").
    text = """# Decreto-Lei n.º 46067

Usando da faculdade conferida pela 1.ª parte do n.º 2.º do artigo 109.º da Constituição, o Governo decreta e eu promulgo, para valer como lei, o seguinte:

Artigo 1.º Ao quadro privativo de enfermagem especializada do Hospital do Ultramar é aumentado um lugar de enfermeira-parteira.

Art. 2.º A cadeira do Instituto de Medicina Tropical referida no artigo 1.º do [Decreto n.º 43387](https://diariodarepublica.pt/dr/detalhe/decreto/43387-1960-512782) tem a designação de cadeira de Epidemiologia e Bioestatística.

Art. 3.º É fixado em 25 o número de assistentes do quadro do pessoal contratado do Instituto de Medicina Tropical.

§ 1.º Os primeiros-assistentes referidos no corpo do artigo consideram-se incluídos no grupo J.

Art. 5.º O presente decreto-lei entrará em vigor em 1 de Janeiro de 1965.

Paços do Governo da República, 7 de Dezembro de 1964. - AMÉRICO DEUS RODRIGUES THOMAZ - António de Oliveira Salazar.
"""
    articles = parse_articles(text)
    assert [article.anchor for article in articles] == ["art-1", "art-2", "art-3", "art-5"]
    assert all(article.method == "texto" for article in articles)
    assert articles[2].text.endswith("consideram-se incluídos no grupo J.")
    assert "Paços do Governo" not in articles[3].text
    eif = extract(articles, text, publication="1964-12-07", document_type="decreto-lei", series="I", jurisdiction="portugal")
    assert (eif.date, eif.method, eif.article) == ("1965-01-01", "clausula", "art-5")


def test_plain_text_heading_on_the_next_line_and_single_article():
    text = """# Decreto-Lei n.º 1/90

ARTIGO 1.º

Objecto

1 - O presente diploma regula a matéria.

Artigo único. É prorrogado pelo prazo de 1 ano o regime de instalação.
"""
    first, second = parse_articles(text)
    assert (first.anchor, first.heading, first.text) == ("art-1", "Objecto", "1 - O presente diploma regula a matéria.")
    assert (second.anchor, second.text) == ("art-unico", "É prorrogado pelo prazo de 1 ano o regime de instalação.")


def test_quoted_new_wording_is_not_an_article():
    # Decreto-Lei n.º 411/90: a nova redação de um artigo de outro diploma, sem aspas.
    text = """# Decreto-Lei n.º 411/90

Artigo 1.º O artigo 2.º do [Decreto-Lei n.º 389/76](https://diariodarepublica.pt/dr/detalhe/decreto-lei/389-1976-426921), de 24 de Maio, passa a ter a seguinte redacção:

Art. 2.º - 1 - ...

2 - Estão isentos do pagamento da taxa os consumidores domésticos.

Art. 2.º O presente diploma entra em vigor em 1 de Janeiro de 1991.
"""
    articles = parse_articles(text)
    assert [article.anchor for article in articles] == ["art-1", "art-2"]
    assert "Estão isentos" in articles[0].text
    assert articles[1].text == "O presente diploma entra em vigor em 1 de Janeiro de 1991."


def test_mixed_headings_and_plain_articles():
    # Portaria n.º 44/2023 (Açores): depois de uma nova redação, os artigos seguintes vêm em texto corrido.
    text = """# Portaria n.º 44/2023

###### Artigo 1.º — Objeto

A presente portaria procede à primeira alteração à Portaria n.º 155/2020.

###### Artigo 2.º — Alteração à Portaria n.º 155/2020

O artigo 4.º passa a ter a seguinte redação:

«Artigo 4.º

[…]»

Artigo 3.º

Republicação da Portaria n.º 155/2020, de 6 de novembro

É republicada, em anexo à presente Portaria, a Portaria n.º 155/2020.

Artigo 4.º

Entrada em vigor e produção de efeitos

A presente portaria entra em vigor no dia seguinte ao da sua publicação.
"""
    articles = parse_articles(text)
    assert [(a.anchor, a.heading) for a in articles][2:] == [
        ("art-3", "Republicação da Portaria n.º 155/2020, de 6 de novembro"),
        ("art-4", "Entrada em vigor e produção de efeitos"),
    ]
    eif = extract(articles, text, publication="2023-06-12")
    assert (eif.date, eif.article) == ("2023-06-13", "art-4")


def test_numbered_points_when_there_are_no_articles():
    # Portaria n.º 144-A/96.
    text = """# Portaria n.º 144-A/96

Manda o Governo, pelo Ministro da Agricultura, do Desenvolvimento Rural e das Pescas, o seguinte:

1.º Nos casos em que se verifique a necessidade de aplicação de medidas de defesa sanitária excepcionais.

2.º O despacho a que se refere o número anterior definirá, nomeadamente:

a) Quais os tipos de animais ou produtos que serão abrangidos;

3.º A presente portaria entra em vigor à data da sua publicação.

Assinada em 2 de Maio de 1996.
"""
    articles = parse_articles(text)
    assert [article.anchor for article in articles] == ["n-1", "n-2", "n-3"]
    assert articles[1].text.endswith("a) Quais os tipos de animais ou produtos que serão abrangidos;")
    eif = extract(articles, text, publication="1996-05-06", document_type="portaria", series="I", jurisdiction="portugal")
    assert (eif.date, eif.method) == ("1996-05-06", "clausula")


def test_restarted_numbering_without_annex_heading_opens_an_implicit_part():
    text = "###### Artigo 1.º — Objeto\n\nA.\n\n###### Artigo 2.º — Fim\n\nB.\n\n###### Artigo 1.º — Âmbito\n\nC.\n\n###### Artigo 2.º — Fim\n\nD.\n"
    assert [article.anchor for article in parse_articles(text)] == ["art-1", "art-2", "parte-2/art-1", "parte-2/art-2"]
    repeated = "###### Artigo 1.º — A\n\nA.\n\n###### Artigo 2.º — B\n\nB.\n\n###### Artigo 2.º — C\n\nC.\n"
    assert [article.anchor for article in parse_articles(repeated)] == ["art-1", "art-2", "art-2-2"]


# ------------------------------------------------------------- entrada em vigor


@pytest.mark.parametrize(
    ("tail", "publication", "expected"),
    [
        # Decreto-Lei n.º 1/2019 e tantos outros.
        ("no dia seguinte ao da sua publicação.", "2019-01-10", "2019-01-11"),
        ("no dia imediato ao da sua publicação", "2010-12-31", "2011-01-01"),
        # Decreto-Lei n.º 246/2015 (publicado a 20/10/2015).
        ("no 1.º dia do 3.º mês seguinte ao da data da sua publicação.", "2015-10-20", "2016-01-01"),
        # Decreto-Lei n.º 34/2011 (publicado a 08/03/2011).
        ("no prazo de 45 dias após a sua publicação.", "2011-03-08", "2011-04-22"),
        ("no 1.º dia do mês seguinte ao da sua publicação", "2012-12-15", "2013-01-01"),
        ("no primeiro dia do mês seguinte ao da sua publicação", "2012-01-16", "2012-02-01"),
        ("30 dias após a data da sua publicação", "2020-01-31", "2020-03-01"),
        ("no quinto dia após a sua publicação", "2020-02-27", "2020-03-03"),
        ("à data da sua publicação.", "1996-05-06", "1996-05-06"),
        ("seis meses após a sua publicação", "2019-08-31", "2020-02-29"),
        ("no dia 15 do mês seguinte ao da sua publicação", "2015-12-20", "2016-01-15"),
        ("em 1 de Janeiro de 1965.", "1964-12-07", "1965-01-01"),
        ("a partir de 01-01-2021", "2020-12-30", "2021-01-01"),
    ],
)
def test_entry_into_force_dates(tail, publication, expected):
    assert compute(tail, publication=publication)[0] == expected


@pytest.mark.parametrize(
    "tail",
    [
        "com o Orçamento do Estado posterior à sua aprovação",
        "no dia útil seguinte ao da sua publicação",
        "decorridos 30 dias sobre a data da sua publicação",
        "na data de início de vigência da legislação que proceda à revisão do Código de Processo do Trabalho",
    ],
)
def test_rules_that_cannot_be_computed_keep_the_text(tail):
    value, rule = compute(tail, publication="2015-10-20")
    assert value is None
    assert rule == tail


def test_signature_date_when_known():
    assert compute("a partir da data da sua assinatura", publication="2020-01-10", signature="2020-01-03")[0] == "2020-01-03"
    assert compute("a partir da data da sua assinatura", publication="2020-01-10")[0] is None


def test_entry_into_force_effects_and_end_of_validity():
    # Decreto-Lei n.º 142/2012: entra em vigor no dia seguinte, com efeitos retroativos.
    text = (
        "###### Artigo 9.º — Entrada em vigor\n\nO presente decreto-lei entra em vigor no dia seguinte ao da sua publicação, "
        "produzindo efeitos a partir de 1 de janeiro de 2012.\n"
    )
    eif = extract(parse_articles(text), text, publication="2012-07-11")
    assert (eif.date, eif.effects_date) == ("2012-07-12", "2012-01-01")
    # Portaria n.º 297/2012: vigência temporária.
    text = "###### Artigo 20.º — Vigência\n\nA presente portaria entra em vigor no dia seguinte ao da sua publicação e vigora até 31 de dezembro de 2013.\n"
    eif = extract(parse_articles(text), text, publication="2012-09-28")
    assert (eif.date, eif.end_date) == ("2012-09-29", "2013-12-31")


def test_partial_clauses_and_exceptions():
    text = (
        "###### Artigo 7.º — Entrada em vigor\n\n"
        "1 - Sem prejuízo do disposto no número seguinte, o presente decreto-lei entra em vigor no dia seguinte ao da sua publicação.\n\n"
        "2 - O artigo 5.º entra em vigor em 1 de janeiro de 2016.\n"
    )
    eif = extract(parse_articles(text), text, publication="2015-10-20")
    assert (eif.date, eif.method) == ("2015-10-21", "clausula")
    assert [(clause.scope, clause.date) for clause in eif.clauses] == [("diploma", "2015-10-21"), ("parcial", "2016-01-01")]
    assert eif.dates == ["2015-10-21", "2016-01-01"]


def test_only_partial_clause_keeps_the_rule_and_no_diploma_date():
    # Lei n.º 7/2009, artigo 14.º: só fala de alguns artigos; o diploma fica sem cláusula.
    articles = parse_articles(LEI_7_2009)
    eif = extract(articles, LEI_7_2009, publication="2009-02-12", document_type="lei", series="I", jurisdiction="portugal")
    assert eif.method == "sem_clausula"
    assert eif.date is None
    assert [clause.scope for clause in eif.clauses] == ["parcial"]


def test_suppletive_rule_only_for_national_first_series_acts():
    text = "###### Artigo 1.º — Objeto\n\nÉ aprovado o regulamento.\n"
    articles = parse_articles(text)
    eif = extract(articles, text, publication="2010-03-01", document_type="decreto-lei", series="I", jurisdiction="portugal")
    assert (eif.date, eif.method) == ("2010-03-06", "supletiva")
    assert extract(articles, text, publication="2010-03-01", document_type="despacho", series="II", jurisdiction="portugal").method == "sem_clausula"
    assert extract(articles, text, publication="1975-03-01", document_type="decreto-lei", series="I", jurisdiction="portugal").method == "sem_clausula"


def test_quoted_clause_of_another_diploma_is_ignored():
    text = (
        "###### Artigo 2.º — Alteração\n\nO artigo 9.º do Decreto-Lei n.º 5/90 passa a ter a seguinte redação:\n\n"
        "«Artigo 9.º\n\nO presente decreto-lei entra em vigor no dia 1 de março de 1990.»\n"
    )
    assert extract(parse_articles(text), text, publication="2015-10-20").clauses == []


# --------------------------------------------------------------------- vigência


def test_repeals_read_from_the_repealing_norm():
    # Decreto-Lei de 2019 (excerto real): total e parcial na mesma frase.
    real = (
        "###### Artigo 18.º — Norma revogatória\n\nÉ revogado o "
        + link("Decreto-Lei n.º 253/86", "decreto-lei/253-1986-219123")
        + ", de 26 de agosto, e o artigo 72.º do "
        + link("Decreto-Lei n.º 28/84", "decreto-lei/28-1984-659911")
        + ", de 20 de janeiro.\n"
    )
    repeals = repeals_in(parse_articles(real), real, source="pt:dre:1:por")
    assert {(item.target, item.scope, item.article) for item in repeals} == {
        ("pt:dre:219123:por", "total", "art-18"),
        ("pt:dre:659911:por", "parcial", "art-18"),
    }
    listing = (
        "###### Artigo 10.º — Norma revogatória\n\nSão revogados:\n\n"
        f"a) O artigo 3.º-A da {link('Lei n.º 60/2005', 'lei/60-2005-469066')}, de 29 de dezembro, na sua redação atual;\n\n"
        f"b) A {link('Portaria n.º 5/90', 'portaria/5-1990-3')}, na redação dada pela {link('Portaria n.º 7/91', 'portaria/7-1991-4')};\n\n"
        f"c) O {link('Decreto-Lei n.º 6/80', 'decreto-lei/6-1980-5')}, na parte relativa aos transportes;\n\n"
        f"d) Os Decretos-Leis n.os {link('10/80', 'decreto-lei/10-1980-7')}, de 1 de março, e {link('11/80', 'decreto-lei/11-1980-8')}, de 2 de março.\n\n"
        "###### Artigo 11.º — Revogação diferida\n\n"
        f"É revogado o {link('Decreto-Lei n.º 8/88', 'decreto-lei/8-1988-6')} a partir da entrada em vigor da portaria referida no artigo 1.º.\n"
    )
    found = {(item.target, item.scope) for item in repeals_in(parse_articles(listing), listing, source="pt:dre:1:por")}
    assert found == {
        ("pt:dre:469066:por", "parcial"),
        ("pt:dre:3:por", "total"),
        ("pt:dre:5:por", "parcial"),
        ("pt:dre:7:por", "total"),
        ("pt:dre:8:por", "total"),
    }


@pytest.mark.parametrize(
    ("text", "scope"),
    [
        # Excertos reais de diplomas que o DRE dá em vigor: só a revogação imediata e por inteiro conta.
        (f"6.º Fica revogada a {link('Portaria n.º 1/80', 'portaria/1-1980-9')}, de 28 de Novembro, em tudo quanto se oponha ao presente diploma.", "parcial"),
        (f"Findo o processo de transição fixado nos termos do artigo 31.º do Regulamento, é revogada a {link('Portaria n.º 1/80', 'portaria/1-1980-9')}, de 16 de Julho.", None),
        (f"Concluído o processo a que se refere o n.º 24.º, é revogada a {link('Portaria n.º 1/80', 'portaria/1-1980-9')}, de 22 de Junho.", None),
        (f"d) A {link('Portaria n.º 1/80', 'portaria/1-1980-9')}, de 16 de Julho, com efeito à data em que caduque o calendário venatório.", None),
        (f"É revogado o {link('Decreto n.º 1/80', 'decreto/1-1980-9')}, com efeitos reportados à data da entrada em vigor da portaria prevista no artigo anterior.", None),
        (f"São revogadas as Portarias n.os {link('1/80', 'portaria/1-1980-9')} e 2/80, a partir da data da publicação das classificações profissionais.", None),
        (f"Ficam revogados o {link('Decreto n.º 1/80', 'decreto/1-1980-9')}, a partir do momento em que entrarem em vigor as disposições do presente decreto-lei.", None),
        (f"É revogada a {link('Portaria n.º 1/80', 'portaria/1-1980-9')}, de 17 de fevereiro, de acordo com a calendarização de produção de efeitos fixada no artigo seguinte.", None),
        (f"17.º É revogado o {link('Aviso n.º 1/80', 'aviso/1-1980-9')}, permanecendo, contudo, em vigor até 31 de Dezembro de 2007 relativamente às instituições.", None),
        (f"Na data da posse dos membros do CCR é revogada a {link('Resolução n.º 1/80', 'resolucao/1-1980-9')}, de 3 de Novembro.", None),
        (f"Fica revogada a {link('Portaria n.º 1/80', 'portaria/1-1980-9')}, de 7 de Maio, na matéria respeitante aos Aeroportos de Santa Maria.", "parcial"),
        (f"No ponto que respeita às empresas adiante mencionadas, é revogado o {link('Despacho Normativo n.º 1/80', 'despacho/1-1980-9')}, de 19 de Janeiro.", "parcial"),
        (f"3. Fica revogado o {link('Decreto n.º 1/80', 'decreto/1-1980-9')}, salvas as disposições transitórias dos seus artigos 27.º e 32.º.", "parcial"),
        (f"d) A {link('Portaria n.º 1/80', 'portaria/1-1980-9')}, após a entrada em vigor da portaria referida no artigo 2.º.", None),
        # Imediatas: continuam totais.
        (f"Este decreto entra em vigor na data da sua publicação e revoga o {link('Decreto n.º 1/80', 'decreto/1-1980-9')}.", "total"),
        (f"Esta portaria entra em vigor no dia imediato ao da publicação e revoga a {link('Portaria n.º 1/80', 'portaria/1-1980-9')}, de 23 de Agosto.", "total"),
        (f"É revogada a {link('Lei n.º 1/80', 'lei/1-1980-9')}, bem como as demais disposições que se mostrem incompatíveis com o presente regime.", "total"),
    ],
)
def test_deferred_and_conditional_repeals(text, scope):
    found = {item.scope for item in repeals_in([], text, source="pt:dre:1:por") if item.target == "pt:dre:9:por"}
    assert found == ({scope} if scope else set())


def test_list_items_inherit_the_condition_of_the_opening_sentence():
    text = (
        "###### Artigo 5.º — Norma revogatória\n\nFindo o processo de transição, são revogadas:\n\n"
        f"a) A {link('Portaria n.º 1/80', 'portaria/1-1980-9')}, de 1 de Março;\n\n"
        f"b) A {link('Portaria n.º 2/80', 'portaria/2-1980-10')}, de 2 de Março.\n"
    )
    assert repeals_in(parse_articles(text), text, source="pt:dre:1:por") == []


def test_a_regional_act_does_not_repeal_national_acts():
    # Resolução da Assembleia Legislativa da Madeira que aprova uma proposta de lei ("É revogada a Lei n.º 30/2000"),
    # e o DRR 5/2002/M, cuja "Portaria n.º 116/98, de 19 de Junho" (regional) o DRE liga à Portaria n.º 116/98 nacional.
    resolution = {"jurisdiction": "regional", "document_type": "resolucao-assembleia-legislativa-regional"}
    regional_decree = {"jurisdiction": "regional", "document_type": "decreto-regulamentar-regional"}
    assert not competent(resolution, {"jurisdiction": "portugal", "document_type": "lei"})
    assert not competent(regional_decree, {"jurisdiction": "portugal", "document_type": "portaria"})
    assert competent(regional_decree, {"jurisdiction": "regional", "document_type": "portaria"})
    assert competent({"jurisdiction": "portugal", "document_type": "lei"}, {"jurisdiction": "regional", "document_type": "portaria"})
    assert competent(regional_decree, None)


def test_a_repeal_needs_a_later_act_already_in_force():
    source = {"jurisdiction": "portugal", "publication_date": "2026-09-16", "entry_into_force": {"date": "2026-09-21"}}
    target = {"jurisdiction": "portugal", "publication_date": "1999-12-23"}
    assert plausible(source, target, today="2026-11-13")
    # O DL 183/2026 só entra em vigor em 2027-03-01; a Portaria 111-A/2022 é anterior ao "revogado" (nota editorial).
    assert not plausible({**source, "entry_into_force": {"date": "2027-03-01"}}, target, today="2026-11-13")
    assert not plausible({**source, "publication_date": "1999-01-01"}, target, today="2026-11-13")
    assert not plausible({**source, "jurisdiction": "regional"}, target, today="2026-11-13")
    assert plausible(source, None, today="2026-11-13")


@pytest.mark.parametrize(
    ("relation_type", "label", "scope"),
    [
        ("repealed_by", "Revogado pelo DEC LEI.34-A/90.24.01.1990.MDN, DR.IS [20]Supl de 24.01.1990", "total"),
        ("repealed_by", "Revogado a partir de 20.04.2019 pelo(a) Decreto-Lei n.º 49/2019 - Diário da República n.º 74/2019", "total"),
        ("repealed_by", "Revogado o nº 5 pela PORT.327/2003.2003.04.21.MADRP, DR.IS-B [93]", "parcial"),
        ("repealed_by", "Revogado com a entrada em vigor das portarias previstas no n.º 1 do art. 11.º do Dec Lei 16/2009", "condicional"),
        ("repealed_by", "", None),
        # O revogado é outro diploma, na redação que este lhe deu.
        ("repealed_by", "Revogado, a partir de 01.01.2020, o Dec Lei 202/94 de 23-jul, na redação do presente diploma pelo(a) Decreto-Lei n.º 151/2019", "outro"),
        ("repealed_by", "Revogado, a partir de 01.01.2018, o Dec Lei 366-A/97 de 20-dez, na versão republicada pelo presente diploma", "outro"),
        ("repealed_by", "Revogada, a partir de 15.10.2018, a presente portaria, na redação da Port 553-A/2008 de 27-jun pelo(a) Portaria n.º 506/2018", "total"),
        ("repealed_by", "Revogado, a partir de 07.07.2018, o Dec Lei 139/2012 de 05-jul, com a redação dada pelo presente, pelo(a) Decreto-Lei n.º 55/2018", "outro"),
        ("repealed_by", "Revogado, a partir de 02.04.2019, o Dec Lei 36/95 de 14-fev, alterado pelo presente diploma, pelo(a) Decreto-Lei n.º 108/2018", "outro"),
        ("repealed_by", "Revogado, a partir de 15.11.2019, o Regulamento de Segurança das Construções Contra os Sismos, aprovado pelo presente Decreto, pelo(a) Decreto-Lei n.º 95/2019", "outro"),
        ("repealed_by", "Revogada, a partir de 30 de janeiro de 2024 e com efeitos a 01 de janeiro de 2024, a presente resolução pelo(a) Decreto-Lei n.º 17/2024", "total"),
        ("repealed_by", "Revogadas a partir de 06.09.2022, as normas constantes do presente diploma que colidam com as competências do Secretário Regional", "parcial"),
        ("repeals", "Revoga o Despacho n.º 3675/2024 de 4 de abril, DR.IIS[67]", "total"),
        ("repeals", "Revoga o artigo 3.º da Portaria n.º 5/90", "parcial"),
    ],
)
def test_dre_label_scope(relation_type, label, scope):
    assert label_scope(relation_type, label) == scope


def _propose(**overrides):
    values = {
        "status": "unknown", "text_repeals": [], "relations": [], "incoming": [], "end_date": None, "end_rule": None,
        "end_article": None, "amended": False, "document_type": "portaria", "corrected_status": [], "text_quality": "texto",
        "publication_date": "2010-01-01", "today": "2026-10-27",
    }
    return propose(**{**values, **overrides})


def test_proposals_need_proof():
    assert _propose().category == "sem_prova"
    total = _propose(relations=[{"type": "repealed_by", "target": "pt:dre:9:por", "label": "Revogada pela PORT.686/2002.2002.06.20.MECO"}])
    assert (total.status, total.category) == ("repealed", "revogado")
    assert total.evidence[0].provenance == "DRE repealed_by: pt:dre:9:por"
    partial = _propose(relations=[{"type": "repealed_by", "target": "pt:dre:9:por", "label": "Revogado o nº 5 pela PORT.327/2003"}])
    assert (partial.status, partial.category) == (None, "revogacao_parcial")
    unlabelled = _propose(relations=[{"type": "repealed_by", "target": "pt:dre:9:por", "label": None}])
    assert (unlabelled.status, unlabelled.category) == (None, "revogacao_por_confirmar")
    expired = _propose(end_date="2013-12-31", end_rule="até 31 de dezembro de 2013", end_article="art-20")
    assert (expired.status, expired.evidence[0].provenance) == ("not_in_force", "cláusula de vigência: art-20")
    assert _propose(end_date="2013-12-31", amended=True).status is None
    assert _propose(status="in_force", end_date="2013-12-31").status is None
    assert _propose(text_quality="pdf", publication_date="1925-01-01").category == "historico_so_pdf"


# ------------------------------------------------------------- validação e CLI


def test_compare_with_dre_fragments():
    parsed = parse_articles(LEI_7_2009)
    expected = [
        ("", "1.º", "Aprovação do Código do Trabalho"), ("", "3.º", "Trabalho autónomo de menor"), ("", "14.º", "Entrada em vigor"),
        ("Anexo — CÓDIGO DO TRABALHO", "1.º", "Fontes específicas"),
        ("Anexo — CÓDIGO DO TRABALHO", "3.º", "Relações entre fontes de regulação"),
        ("Anexo — CÓDIGO DO TRABALHO", "10.º-A", "Representação e negociação coletiva"),
    ]
    assert compare(parsed, expected)["tudo_igual"]
    different = compare(parsed, expected[:-1] + [("Anexo — CÓDIGO DO TRABALHO", "10.º-B", "Outra")])
    assert not different["tudo_igual"]
    assert different["primeira_diferenca"]["posicao"] == 5


def test_structure_command_writes_the_report_without_touching_records(repo_root: Path, capsys):
    repealed_path = repo_root / "data/portugal/decretos-leis/1986/decreto-lei-253-86.md"
    repealed_path.parent.mkdir(parents=True)
    repealed_path.write_text(render_markdown(record_dict(
        "pt:dre:219123:por", title="Decreto-Lei n.º 253/86", legal_status="unknown", publication_date="1986-08-26",
        publication={"series": "I"},
    ), "# Decreto-Lei n.º 253/86\n\nArtigo 1.º É criado o serviço.\n\nArt. 2.º O presente diploma entra em vigor no dia seguinte ao da sua publicação.\n"), encoding="utf-8")
    consolidated = repo_root / "data/portugal/leis/2009/lei-7-2009.md"
    consolidated.parent.mkdir(parents=True)
    consolidated.write_text(render_markdown(record_dict(
        "pt:dre:602073:por", title="Lei n.º 7/2009", document_type="lei", legal_status="in_force", publication_date="2009-02-12",
        version={"kind": "consolidated", "label": "Versão consolidada pelo DRE", "language": "por", "consolidation_date": "2025-04-26"},
    ), LEI_7_2009), encoding="utf-8")
    fragments = {}
    order = []
    part = None
    for index, article in enumerate(parse_articles(LEI_7_2009)):
        if article.part and article.part != part:
            part = article.part
            fragments[f"anexo{index}"] = {"type": 14, "heading": part, "markdown": f"## {part}"}
            order.append(f"anexo{index}")
        fragments[str(index)] = {"type": 11, "heading": f"Artigo {article.number} — {article.heading}", "markdown": "###### x"}
        order.append(str(index))
    history = {"versions": [{"date": "2025-04-26", "acts": [], "changes": [], "fragments": order}], "fragments": fragments}
    consolidated.with_name("lei-7-2009.versoes.json").write_text(json.dumps(history), encoding="utf-8")
    repealing = repo_root / "data/portugal/decretos-leis/2019/decreto-lei-1-2019.md"
    repealing.parent.mkdir(parents=True)
    repealing.write_text(render_markdown(record_dict(
        "pt:dre:123968666:por", title="Decreto-Lei n.º 1/2019", legal_status="in_force", publication_date="2019-01-10",
        publication={"series": "I"},
    ), "# Decreto-Lei n.º 1/2019\n\n###### Artigo 18.º — Norma revogatória\n\nÉ revogado o "
       + link("Decreto-Lei n.º 253/86", "decreto-lei/253-1986-219123") + ", de 26 de agosto.\n"), encoding="utf-8")
    before = {path: path.read_text(encoding="utf-8") for path in (repo_root / "data").rglob("*") if path.is_file()}

    assert main(["--root", str(repo_root), "structure", "--dry-run", "--workers", "2", "--today", "2026-10-27"]) == 0
    out = capsys.readouterr().out
    assert "com estado proposto: 1" in out

    summary = json.loads((repo_root / "reports/estrutura.json").read_text(encoding="utf-8"))
    assert summary["artigos"]["com_artigos"] == 3
    assert summary["entrada_em_vigor"]["calculadas_do_texto"] == 1
    assert summary["entrada_em_vigor"]["supletivas"] == 1
    assert summary["vigencia"]["estado_proposto"] == {"repealed": 1}
    assert summary["validacao"]["atual"] == {
        "diplomas": 1, "mesmo_numero_de_artigos": 1, "tudo_igual": 1, "partes_iguais": 1, "artigos_dre": 6, "artigos_parser": 6,
        "epigrafes_iguais": 6,
    }
    proposals = [json.loads(line) for line in (repo_root / "reports/vigencia-proposta.jsonl").read_text(encoding="utf-8").splitlines()]
    assert proposals == [{
        "id": "pt:dre:219123:por", "path": "data/portugal/decretos-leis/1986/decreto-lei-253-86.md", "status": "repealed",
        "category": "revogado",
        "evidence": [{"status": "repealed", "provenance": "norma revogatória: pt:dre:123968666:por#art-18",
                      "detail": "É revogado o [Decreto-Lei n.º 253/86], de 26 de agosto."}],
    }]
    assert "Estrutura, entrada em vigor e vigência" in (repo_root / "reports/estrutura.md").read_text(encoding="utf-8")
    after = {path: path.read_text(encoding="utf-8") for path in (repo_root / "data").rglob("*") if path.is_file()}
    assert after == before


def test_schema_accepts_the_proposed_fields(repo_root: Path):
    from leis_portugal.infrastructure.repository import Acervo

    record = record_dict(
        "pt:dre:219123:por",
        legal_status="repealed",
        entry_into_force={
            "date": "1986-08-27", "rule": "no dia seguinte ao da sua publicação", "method": "clausula", "article": "art-2",
            "effects_date": None, "effects_rule": None, "end_date": None, "end_rule": None,
        },
        legal_status_basis={
            "source": "norma_revogatoria",
            "evidence": [{"status": "repealed", "provenance": "norma revogatória: pt:dre:123968666:por#art-18", "detail": "É revogado o …"}],
        },
        article_structure={"article_count": 2, "section_count": 0, "extraction_method": "texto", "unit": "artigos", "annex_count": 0,
                           "id_scheme": "leis-portugal/artigos/1"},
    )
    schema = Acervo(repo_root).schema
    assert schema.record_errors(record) == []
    assert schema.record_errors({**record, "entry_into_force": {"method": "adivinhada"}})


def test_conflicting_evidence_from_the_same_repealer_resolves_nothing():
    from leis_portugal.domain.validity import Repeal

    proposal = _propose(
        text_repeals=[Repeal("pt:dre:5:por", "total", "pt:dre:9:por", "art-4", "É revogado o …")],
        relations=[{"type": "repealed_by", "target": "pt:dre:9:por", "label": "Revogado o n.º 2 do art. 3.º pelo DEC LEI 9/90"}],
    )
    assert (proposal.status, proposal.category) == (None, "conflito")


def test_shared_rule_for_entry_into_force_and_effects():
    text = "###### Artigo 5.º — Entrada em vigor\n\nO presente decreto-lei entra em vigor e produz efeitos no dia seguinte ao da sua publicação.\n"
    eif = extract(parse_articles(text), text, publication="2020-05-04")
    assert (eif.date, eif.effects_date) == ("2020-05-05", "2020-05-05")


def test_exception_after_the_date_makes_the_repeal_partial():
    # Decreto-Lei n.º 212/2004, artigo 23.º, alínea d).
    text = (
        "###### Artigo 23.º — Norma revogatória\n\nSão revogados:\n\n"
        f"d) O {link('Decreto-Lei n.º 350/88', 'decreto-lei/350-1988-1')}, de 30 de Setembro, com excepção dos artigos 5.º e 6.º;\n\n"
        f"e) Os Decretos-Leis n.os {link('390/87', 'decreto-lei/390-1987-2')}, de 31 de dezembro, e {link('179/96', 'decreto-lei/179-1996-3')}, de 24 de setembro.\n"
    )
    found = {(item.target, item.scope, item.text) for item in repeals_in(parse_articles(text), text, source="pt:dre:9:por")}
    assert found == {
        ("pt:dre:1:por", "parcial", "d) O [Decreto-Lei n.º 350/88], de 30 de Setembro, com excepção dos artigos 5.º e 6.º"),
        ("pt:dre:2:por", "total", "e) Os Decretos-Leis n.os [390/87], de 31 de dezembro, e [179/96], de 24 de setembro."),
        ("pt:dre:3:por", "total", "e) Os Decretos-Leis n.os [390/87], de 31 de dezembro, e [179/96], de 24 de setembro."),
    }


def test_amending_acts_listed_after_the_repealed_one_are_not_repealed():
    # Decreto-Lei n.º 9/2011, artigo 7.º, alínea a).
    text = (
        "###### Artigo 7.º — Norma revogatória\n\nSão revogados:\n\n"
        f"a) O artigo 21.º do {link('Decreto-Lei n.º 191/98', 'decreto-lei/191-1998-1')}, de 10 de Julho, alterado pelos Decretos-Leis n.os "
        f"{link('271/2001', 'decreto-lei/271-2001-2')}, de 13 de Outubro, e {link('138/2002', 'decreto-lei/138-2002-3')}, de 16 de Maio;\n\n"
        f"b) A {link('Portaria n.º 1115/2004', 'portaria/1115-2004-4')}, de 14 de Setembro.\n"
    )
    found = {(item.target, item.scope) for item in repeals_in(parse_articles(text), text, source="pt:dre:9:por")}
    assert found == {("pt:dre:1:por", "parcial"), ("pt:dre:4:por", "total")}


def test_numbered_headings_without_articles():
    # Portaria n.º 55-C/86: os números do dispositivo vêm como títulos (`###### 1.º`).
    text = "# Portaria n.º 55-C/86\n\n###### 1.º\n\nOs quadros de pessoal docente.\n\n###### 2.º\n\nSão criadas as seguintes escolas.\n"
    articles = parse_articles(text)
    assert [(article.anchor, article.method) for article in articles] == [("n-1", "titulo"), ("n-2", "titulo")]


def test_structure_command_writes_entry_into_force_and_proven_status(repo_root: Path, capsys):
    from leis_portugal.infrastructure.markdown import read_markdown_record
    from leis_portugal.infrastructure.repository import Acervo

    repealed = repo_root / "data/portugal/decretos-leis/1986/decreto-lei-253-86.md"
    repealed.parent.mkdir(parents=True)
    repealed.write_text(render_markdown(record_dict(
        "pt:dre:219123:por", title="Decreto-Lei n.º 253/86", legal_status="unknown", publication_date="1986-08-26",
        publication={"series": "I"},
    ), "# Decreto-Lei n.º 253/86\n\nArtigo 1.º É criado o serviço.\n\nArt. 2.º O presente diploma entra em vigor no dia seguinte ao da sua publicação.\n"), encoding="utf-8")
    repealing = repo_root / "data/portugal/decretos-leis/2019/decreto-lei-1-2019.md"
    repealing.parent.mkdir(parents=True)
    repealing.write_text(render_markdown(record_dict(
        "pt:dre:123968666:por", title="Decreto-Lei n.º 1/2019", legal_status="in_force", publication_date="2019-01-10",
        publication={"series": "I"},
    ), "# Decreto-Lei n.º 1/2019\n\n###### Artigo 18.º — Norma revogatória\n\nÉ revogado o "
       + link("Decreto-Lei n.º 253/86", "decreto-lei/253-1986-219123") + ", de 26 de agosto.\n"), encoding="utf-8")

    assert main(["--root", str(repo_root), "structure", "--workers", "1", "--today", "2026-10-27", "--validation-sample", "0"]) == 0
    assert "1 com vigência provada" in capsys.readouterr().out

    acervo = Acervo(repo_root)
    metadata, _ = read_markdown_record(repealed)
    assert metadata["entry_into_force"]["date"] == "1986-08-27" and metadata["entry_into_force"]["method"] == "clausula"
    assert metadata["entry_into_force_dates"] == ["1986-08-27"]
    assert metadata["legal_status"] == "repealed"
    assert metadata["legal_status_basis"] == {
        "source": "norma_revogatoria",
        "evidence": [{"status": "repealed", "provenance": "norma revogatória: pt:dre:123968666:por#art-18",
                      "detail": "É revogado o [Decreto-Lei n.º 253/86], de 26 de agosto."}],
    }
    # A regra supletiva (5.º dia após a publicação) também se grava, com o método.
    metadata, _ = read_markdown_record(repealing)
    assert (metadata["entry_into_force"]["method"], metadata["entry_into_force"]["date"]) == ("supletiva", "2019-01-15")
    assert "legal_status_basis" not in metadata
    for path in (repealed, repealing):
        assert acervo.schema.record_errors(read_markdown_record(path)[0]) == []

    # Segunda passagem: nada a mudar.
    before = {path: path.read_text(encoding="utf-8") for path in (repealed, repealing)}
    assert main(["--root", str(repo_root), "structure", "--workers", "1", "--today", "2026-10-27", "--validation-sample", "0"]) == 0
    assert {path: path.read_text(encoding="utf-8") for path in (repealed, repealing)} == before

    # A prova deixa de existir (o revogador já não revoga): o estado volta a desconhecido.
    repealing.write_text(render_markdown(record_dict(
        "pt:dre:123968666:por", title="Decreto-Lei n.º 1/2019", legal_status="in_force", publication_date="2019-01-10",
        publication={"series": "I"},
    ), "# Decreto-Lei n.º 1/2019\n\n###### Artigo 18.º — Norma revogatória\n\nÉ alterado o "
       + link("Decreto-Lei n.º 253/86", "decreto-lei/253-1986-219123") + ", de 26 de agosto.\n"), encoding="utf-8")
    assert main(["--root", str(repo_root), "structure", "--workers", "1", "--today", "2026-10-27", "--validation-sample", "0"]) == 0
    assert "1 com a vigência retirada" in capsys.readouterr().out
    metadata, _ = read_markdown_record(repealed)
    assert metadata["legal_status"] == "unknown" and "legal_status_basis" not in metadata
    repealing.write_text(before[repealing], encoding="utf-8")
    assert main(["--root", str(repo_root), "structure", "--workers", "1", "--today", "2026-10-27", "--validation-sample", "0"]) == 0

    # Uma nova recolha (a fonte sem estes campos) não apaga o que se tirou do texto.
    record, body = acervo.read(repealed)
    fresh = type(record).from_dict({key: value for key, value in record.to_dict().items()
                                    if key not in ("entry_into_force", "legal_status_basis", "entry_into_force_dates")} | {"legal_status": "unknown"})
    acervo.save(fresh, body, target=repealed)
    metadata, _ = read_markdown_record(repealed)
    assert metadata["legal_status"] == "repealed" and metadata["entry_into_force"]["date"] == "1986-08-27"
    assert metadata["entry_into_force_dates"] == ["1986-08-27"]


def _pdm_records(repo_root: Path) -> tuple[Path, Path]:
    # RCM n.º 94/94 (PDM de Lisboa) e Aviso n.º 11622/2012 (a revisão), em excerto.
    old = repo_root / "data/portugal/resolucoes-conselho-ministros/1994/resolucao-conselho-ministros-94-94.md"
    old.parent.mkdir(parents=True)
    old.write_text(render_markdown(record_dict(
        "pt:dre:609283:por", title="Resolução do Conselho de Ministros n.º 94/94", document_type="resolucao-conselho-ministros",
        legal_status="in_force", publication_date="1994-09-29", publication={"series": "I"},
        relationships=[{"type": "amended_by", "target": "pt:dre:138128:por", "label": "Suspensa", "source": None, "date": "1999-03-25"}],
    ), "# Resolução do Conselho de Ministros n.º 94/94\n\n1 - Ratificar o Plano Director Municipal de Lisboa.\n"), encoding="utf-8")
    new = repo_root / "data/portugal/serie-ii/avisos/2012/aviso-11622-2012.md"
    new.parent.mkdir(parents=True)
    new.write_text(render_markdown(record_dict(
        "pt:dre:1787349:por", title="Aviso n.º 11622/2012", document_type="aviso", legal_status="in_force", publication_date="2012-08-30",
        publication={"series": "II"},
    ), "# Aviso n.º 11622/2012\n\nTorna-se público que a Assembleia Municipal de Lisboa deliberou, através da "
       "[Deliberação n.º 46/AML/2012](https://example.org), aprovar a Revisão do Plano Diretor Municipal de Lisboa,\n"
       "incluindo o Regulamento, que se publica em anexo.\n"), encoding="utf-8")
    return old, new


def _manual_line(**extra) -> str:
    item = {
        "id": "pt:dre:609283:por", "estado": "not_in_force", "substituido_por": "pt:dre:1787349:por", "data": "2012-08-31",
        "citacao": "através da Deliberação n.º 46/AML/2012, aprovar a Revisão do Plano Diretor Municipal de Lisboa, incluindo o Regulamento",
        "motivo": "Substituído pela revisão do PDM de Lisboa (Aviso n.º 11622/2012).",
    }
    return json.dumps({**item, **extra}, ensure_ascii=False) + "\n"


def _structure(repo_root: Path) -> int:
    return main(["--root", str(repo_root), "structure", "--workers", "1", "--today", "2026-11-12", "--validation-sample", "0"])


def test_manual_proof_overrides_the_dre_status_and_names_the_replacement(repo_root: Path, capsys):
    from leis_portugal.infrastructure.markdown import read_markdown_record
    from leis_portugal.infrastructure.repository import Acervo
    from leis_portugal.services.structure import MANUAL_RELATION_SOURCE

    old, new = _pdm_records(repo_root)
    untouched = new.read_text(encoding="utf-8")
    (repo_root / "reports").mkdir(exist_ok=True)
    manual = repo_root / "reports/vigencia-manual.jsonl"
    manual.write_text(_manual_line(), encoding="utf-8")

    assert _structure(repo_root) == 0
    assert "1 com vigência provada (1 por prova manual)" in capsys.readouterr().out
    metadata, _ = read_markdown_record(old)
    assert metadata["legal_status"] == "not_in_force"
    assert metadata["legal_status_basis"] == {
        "source": "prova_manual", "dre_status": "in_force", "reason": "Substituído pela revisão do PDM de Lisboa (Aviso n.º 11622/2012).",
        "evidence": [{"status": "not_in_force", "provenance": "prova manual: pt:dre:1787349:por",
                      "detail": "através da Deliberação n.º 46/AML/2012, aprovar a Revisão do Plano Diretor Municipal de Lisboa, incluindo o Regulamento"}],
    }
    assert {"type": "repealed_by", "target": "pt:dre:1787349:por", "label": "Substituído pela revisão do PDM de Lisboa (Aviso n.º 11622/2012).",
            "source": MANUAL_RELATION_SOURCE, "date": "2012-08-31"} in metadata["relationships"]
    assert any(item["type"] == "amended_by" for item in metadata["relationships"])
    acervo = Acervo(repo_root)
    assert acervo.schema.record_errors(metadata) == []
    summary = json.loads((repo_root / "reports/estrutura.json").read_text(encoding="utf-8"))
    assert summary["vigencia"]["provas_manuais"] == 1 and summary["vigencia"]["desconhecidos"] == 0
    # Só o diploma substituído muda (fora a entrada em vigor, que este comando também grava).
    assert read_markdown_record(new)[0]["legal_status"] == "in_force"
    assert "legal_status_basis" not in read_markdown_record(new)[0]
    del untouched

    # Segunda passagem: nada muda (o reset não apaga a prova manual).
    before = old.read_text(encoding="utf-8")
    assert _structure(repo_root) == 0
    assert old.read_text(encoding="utf-8") == before

    # Uma nova recolha do DRE (que continua a dizer `in_force`) não apaga a prova nem a relação.
    record, body = acervo.read(old)
    fresh = type(record).from_dict(
        {key: value for key, value in record.to_dict().items() if key != "legal_status_basis"}
        | {"legal_status": "in_force", "relationships": [item for item in record.to_dict()["relationships"] if item["type"] == "amended_by"]}
    )
    acervo.save(fresh, body, target=old)
    metadata, _ = read_markdown_record(old)
    assert metadata["legal_status"] == "not_in_force" and metadata["legal_status_basis"]["dre_status"] == "in_force"
    assert any(item["type"] == "repealed_by" for item in metadata["relationships"])

    # A prova sai do ficheiro: volta o estado do DRE e a relação desaparece.
    manual.write_text("", encoding="utf-8")
    assert _structure(repo_root) == 0
    assert "1 com a vigência retirada" in capsys.readouterr().out
    metadata, _ = read_markdown_record(old)
    assert metadata["legal_status"] == "in_force" and "legal_status_basis" not in metadata
    assert [item["type"] for item in metadata["relationships"]] == ["amended_by"]


@pytest.mark.parametrize(
    "line, message",
    [
        (_manual_line(citacao="revoga a Resolução do Conselho de Ministros n.º 94/94"), "citação"),
        (_manual_line(estado="in_force"), "estado"),
        (_manual_line(motivo=""), "campos em falta"),
        (_manual_line(substituido_por="pt:dre:1:por"), "não está no acervo"),
        (_manual_line() * 2, "repetido"),
    ],
)
def test_manual_proof_without_the_quoted_sentence_is_refused(repo_root: Path, capsys, line: str, message: str):
    old, _ = _pdm_records(repo_root)
    before = old.read_text(encoding="utf-8")
    (repo_root / "reports").mkdir(exist_ok=True)
    (repo_root / "reports/vigencia-manual.jsonl").write_text(line, encoding="utf-8")
    assert _structure(repo_root) != 0
    assert message in capsys.readouterr().err
    assert old.read_text(encoding="utf-8") == before


# ------------------------------------------- norma revogatória contra o in_force do DRE


def test_editorial_notes_and_lists_under_a_repealing_epigraph_repeal_nothing():
    # Aviso n.º 13300/2013 (PDM da Figueira da Foz), art. 66.º: depois da revogação do PGU, a lista de imóveis classificados.
    pdm = (
        "###### Artigo 66.º — Norma revogatória\n\n"
        "É revogado o Plano Geral de Urbanização da Figueira da Foz, aprovado por despacho de 17 de julho de 1967.\n\n"
        "Imóveis classificados - Concelho da Figueira da Foz\n\n"
        f"{link('Decreto n.º 251/70', 'decreto/251-1970-9')}, de 3 de junho.\n"
    )
    assert repeals_in(parse_articles(pdm), pdm, source="pt:dre:1:por") == []
    # Portaria n.º 111-A/2022: nota do DRE sobre outra portaria.
    note = (
        "###### Artigo 5.º — Norma revogatória\n\nÉ revogada a Portaria n.º 1/2022.\n\n"
        f"> Nota: {link('Artigo 3.º, Portaria n.º 128-A/2022 - Diário da República n.º 60/2022', 'portaria/128-a-2022-9')} "
        "A presente portaria entra em vigor no dia 28 de março de 2022.\n"
    )
    assert repeals_in(parse_articles(note), note, source="pt:dre:1:por") == []
    # Uma lista aberta pelo verbo continua a contar, com ou sem marca.
    listing = (
        "###### Artigo 9.º — Revogação\n\nSão revogados:\n\n"
        f"{link('Decreto n.º 1/80', 'decreto/1-1980-9')}, de 1 de março;\n\n"
        f"{link('Decreto n.º 2/80', 'decreto/2-1980-10')}, de 2 de março.\n\n"
        f"{link('Decreto n.º 3/80', 'decreto/3-1980-11')}, de 3 de março.\n"
    )
    assert {item.target for item in repeals_in(parse_articles(listing), listing, source="pt:dre:1:por")} == {"pt:dre:9:por", "pt:dre:10:por"}


@pytest.mark.parametrize(
    "text",
    [
        # Lei n.º 42/2016, art. 109.º: descreve a revogação feita por outra lei.
        f"O Governo fica autorizado, nos termos do artigo 8.º da {link('Lei Orgânica n.º 7/2015', 'lei-organica/7-2015-8')}, de 18 de maio, "
        f"que aprova a lei de programação militar e revoga a {link('Lei Orgânica n.º 4/2006', 'lei-organica/4-2006-9')}, de 29 de agosto.",
        # Portaria n.º 338/89: o sumário de outro diploma, num índice.
        f"Sujeita a licenciamento prévio a abertura de poços e furos em alguns concelhos. Revoga o {link('Decreto-Lei n.º 47892', 'decreto-lei/47892-1967-9')}.",
    ],
)
def test_a_described_repeal_is_not_a_repeal(text):
    assert repeals_in([], text, source="pt:dre:1:por") == []


def test_a_repeal_saved_in_another_article_is_not_total():
    text = (
        "###### Artigo 23.º — Norma revogatória\n\nSão revogados:\n\n"
        f"a) A {link('Portaria n.º 213/2000', 'portaria/213-2000-9')}, de 8 de Abril;\n\n"
        f"b) A {link('Portaria n.º 214/2000', 'portaria/214-2000-10')}, de 8 de Abril.\n\n"
        "###### Artigo 24.º — Norma transitória\n\n"
        "2 - Até à publicação das portarias previstas no artigo 5.º, mantém-se em vigor a Portaria n.º 213/2000.\n\n"
        f"3 - A regulamentação emitida ao abrigo da {link('Portaria n.º 214/2000', 'portaria/214-2000-10')} mantém-se em vigor.\n"
    )
    found = {(item.target, item.scope) for item in repeals_in(parse_articles(text), text, source="pt:dre:1:por")}
    # A ressalva da 213/2000 torna-a parcial; manter a regulamentação emitida ao abrigo da 214/2000 não a ressalva.
    assert found == {("pt:dre:9:por", "parcial"), ("pt:dre:10:por", "total")}


def test_cited_date_and_entity_of_the_linked_act():
    text = (
        f"13.º Ficam revogadas as Portarias n.os {link('680/71', 'portaria/680-1971-11')}, {link('515/72', 'portaria/515-1972-2')} e "
        f"{link('690/73', 'portaria/690-1973-3')}, respectivamente, de 7 de Dezembro, de 1 de Setembro e de 7 de Setembro.\n\n"
        f"14.º É revogado o {link('Aviso n.º 6/2002', 'aviso/6-2002-4')} do Banco de Portugal.\n\n"
        f"15.º É revogada a {link('Portaria n.º 216/85', 'portaria/216-1985-5')}, de 15 de Maio de 1985.\n"
    )
    found = {item.target: (item.label, item.cited_date, item.cited_entity) for item in repeals_in([], text, source="pt:dre:1:por")}
    assert found == {
        "pt:dre:11:por": ("680/71", "--12-07", None),
        "pt:dre:2:por": ("515/72", "--09-01", None),
        "pt:dre:3:por": ("690/73", "--09-07", None),
        "pt:dre:4:por": ("Aviso n.º 6/2002", None, "Banco de Portugal"),
        "pt:dre:5:por": ("Portaria n.º 216/85", "1985-05-15", None),
    }


@pytest.mark.parametrize(
    ("label", "cited", "entity", "target", "expected"),
    [
        ("Portaria n.º 216/85", "--04-15", None, {"official_number": "216/85", "publication_date": "1985-04-18"}, ("confirmada", [])),
        ("216/85", None, None, {"official_number": "216/85", "publication_date": "1985-04-18"}, ("so_numero", [])),
        # Dezembro citado, publicado em janeiro.
        ("Decreto n.º 44889", "--12-28", None, {"official_number": "44889", "publication_date": "1963-01-04"}, ("confirmada", [])),
        # Portaria n.º 216/85, de 15 de Maio, ligada à de 18 de Abril; a 690/73 de 7 de Setembro ligada à de 10 de Outubro.
        ("Portaria n.º 216/85", "--05-15", None, {"official_number": "216/85", "publication_date": "1985-04-18"}, ("suspeita", ["data"])),
        ("690/73", "--09-07", None, {"official_number": "690/73", "publication_date": "1973-10-10"}, ("suspeita", ["data"])),
        ("Portaria n.º 216/86", None, None, {"official_number": "216/85", "publication_date": "1985-04-18"}, ("suspeita", ["numero"])),
        ("Regulamento", None, None, {"official_number": "1/97", "publication_date": "1997-01-01"}, ("suspeita", ["sem_numero"])),
        ("Aviso n.º 6/2002", None, "Banco de Portugal",
         {"official_number": "6/2002", "publication_date": "2002-02-07", "issuing_authority": ["Ministério dos Negócios Estrangeiros"]},
         ("suspeita", ["entidade"])),
        ("Portaria n.º 1/77", None, "Secretaria Regional da Educação",
         {"official_number": "1/77", "publication_date": "1977-01-04", "jurisdiction": "portugal"}, ("suspeita", ["entidade"])),
    ],
)
def test_identity_of_the_linked_act(label, cited, entity, target, expected):
    from leis_portugal.domain.validity import Repeal, identity

    repeal = Repeal("pt:dre:9:por", "total", "pt:dre:1:por", "art-1", "", label=label, cited_date=cited, cited_entity=entity)
    assert identity(repeal, target) == expected


def _row(record_id: str, **extra):
    return {
        "id": record_id, "jurisdiction": "portugal", "document_type": "portaria", "publication_date": "2000-01-01", "official_number": "1/2000",
        "title": "Portaria n.º 1/2000", "issuing_authority": [], "relations": [], "entry_into_force": None, **extra,
    }


def test_signals_against_a_text_repeal_of_an_act_in_force():
    from leis_portugal.domain.validity import Repeal
    from leis_portugal.services.structure import proof_segment, proof_signals

    repeal = Repeal("pt:dre:9:por", "total", "pt:dre:1:por", "n-3", "3.º É revogada a [Portaria n.º 1/2000], de 1 de Janeiro.",
                    label="Portaria n.º 1/2000", cited_date="--01-01")
    source = _row("pt:dre:1:por", publication_date="2005-01-01", official_number="5/2005")
    target = _row("pt:dre:9:por")
    by_id = {"pt:dre:1:por": source, "pt:dre:9:por": target}
    clean = proof_signals(source, repeal, target, by_id)
    assert clean == {"identidade": "confirmada", "sinais": [], "nacional": True} and proof_segment(clean) == "a"
    # Alterada pelo DRE depois do revogador: um diploma revogado não se altera.
    later = {**target, "relations": [{"type": "amended_by", "target": "pt:dre:7:por", "label": "", "date": "2007-03-01"}]}
    assert proof_signals(source, repeal, later, by_id)["sinais"] == ["alteracao_posterior"]
    # O DRE dá-lhe outro revogador, ou uma revogação parcial.
    other = {**target, "relations": [{"type": "repealed_by", "target": "pt:dre:8:por", "label": "Revogado o n.º 2 pela PORT 8/2001"}]}
    assert proof_signals(source, repeal, other, by_id)["sinais"] == ["conflito_dre"]
    # Uma declaração de retificação; "toda a legislação em contrário, nomeadamente"; um aviso do Banco de Portugal.
    assert proof_signals({**source, "document_type": "declaracao-retificacao"}, repeal, target, by_id)["sinais"] == ["retificacao"]
    contrary = Repeal(**{**repeal.to_dict(), "text": "Fica revogada toda a legislação em contrário, nomeadamente o [Decreto-Lei n.º 37517]"})
    assert proof_signals(source, contrary, target, by_id)["sinais"] == ["legislacao_em_contrario"]
    bdp = {**source, "title": "Aviso do Banco de Portugal n.º 1/2026"}
    assert proof_signals(bdp, repeal, {**target, "issuing_authority": ["Ministério dos Negócios Estrangeiros"]}, by_id)["sinais"] == ["entidade"]
    assert proof_signals(bdp, repeal, {**target, "title": "Aviso do Banco de Portugal n.º 6/2003"}, by_id)["sinais"] == []
    # Sem data citada: segmento b; regional ou com sinais: c.
    undated = proof_signals(source, Repeal(**{**repeal.to_dict(), "cited_date": None}), target, by_id)
    assert proof_segment(undated) == "b"
    assert proof_segment(proof_signals({**source, "jurisdiction": "regional"}, repeal, {**target, "jurisdiction": "regional"}, by_id)) == "c"


def test_deferred_effects_of_the_repealing_act():
    target = {"jurisdiction": "portugal", "publication_date": "2002-07-17"}
    source = {"jurisdiction": "portugal", "publication_date": "2005-01-01", "entry_into_force": {"date": "2005-01-02"}}
    assert plausible(source, target, today="2026-11-13")
    rule = {"date": "2005-01-02", "effects_rule": "com a entrada em vigor do decreto regulamentar regional", "effects_date": None}
    assert not plausible({**source, "entry_into_force": rule}, target, today="2026-11-13")
    future = {"date": "2026-09-21", "effects_rule": "a 1 de janeiro de 2027", "effects_date": "2027-01-01"}
    assert not plausible({**source, "entry_into_force": future}, target, today="2026-11-13")
    past = {"date": "2005-01-02", "effects_rule": "desde 1 de janeiro de 2005", "effects_date": "2005-01-01"}
    assert plausible({**source, "entry_into_force": past}, target, today="2026-11-13")
    # Sem data, mas retroativas ou imediatas: não diferem a revogação.
    for rule in ("desde a data da sua assinatura", "imediatos", "a partir do ano lectivo de 2006-2007",
                 "apenas para os procedimentos cuja decisão de contratar ocorrer após a data da sua entrada em vigor"):
        assert plausible({**source, "entry_into_force": {"date": "2005-01-02", "effects_rule": rule, "effects_date": None}}, target, today="2026-11-13")


def test_text_repeal_against_the_dre_status_in_an_approved_segment(repo_root: Path, capsys, monkeypatch):
    from leis_portugal.infrastructure.markdown import read_markdown_record
    from leis_portugal.infrastructure.repository import Acervo
    from leis_portugal.services import structure

    target = repo_root / "data/portugal/portarias/2002/portaria-654-2002.md"
    target.parent.mkdir(parents=True)
    target.write_text(render_markdown(record_dict(
        "pt:dre:146249:por", title="Portaria n.º 654/2002", document_type="portaria", official_number="654/2002", legal_status="in_force",
        publication_date="2002-06-17", publication={"series": "I"},
    ), "# Portaria n.º 654/2002\n\n1.º É criada a zona de caça.\n"), encoding="utf-8")
    source = repo_root / "data/portugal/portarias/2003/portaria-351-2003.md"
    source.parent.mkdir(parents=True)
    repealing = (
        "# Portaria n.º 351/2003\n\n1.º É renovada a zona de caça.\n\n2.º É revogada a "
        + link("Portaria n.º 654/2002", "portaria/654-2002-146249") + ", de 14 de Junho.\n"
    )
    source.write_text(render_markdown(record_dict(
        "pt:dre:571878:por", title="Portaria n.º 351/2003", document_type="portaria", official_number="351/2003", legal_status="in_force",
        publication_date="2003-05-02", publication={"series": "I"},
    ), repealing), encoding="utf-8")

    # Sem segmento aprovado, o estado do DRE fica: a prova só se conta, com o segmento.
    assert _structure(repo_root) == 0
    assert read_markdown_record(target)[0]["legal_status"] == "in_force"
    summary = json.loads((repo_root / "reports/estrutura.json").read_text(encoding="utf-8"))["vigencia"]["texto_contra_dre"]
    assert summary["por_segmento"] == {"a": 1, "b": 0, "c": 0} and summary["revogados_automaticamente"] == 0

    monkeypatch.setattr(structure, "APPROVED_SEGMENTS", frozenset({"a"}))
    assert _structure(repo_root) == 0
    metadata, _ = read_markdown_record(target)
    assert metadata["legal_status"] == "repealed"
    assert metadata["legal_status_basis"] == {
        "source": "norma_revogatoria_contra_dre", "dre_status": "in_force", "segment": "a",
        "evidence": [{"status": "repealed", "provenance": "norma revogatória: pt:dre:571878:por#n-2",
                      "detail": "2.º É revogada a [Portaria n.º 654/2002], de 14 de Junho."}],
    }
    acervo = Acervo(repo_root)
    assert acervo.schema.record_errors(metadata) == []
    before = target.read_text(encoding="utf-8")
    assert _structure(repo_root) == 0
    assert target.read_text(encoding="utf-8") == before

    # Uma nova recolha do DRE (que continua a dizer `in_force`) não apaga a base.
    record, body = acervo.read(target)
    fresh = type(record).from_dict({key: value for key, value in record.to_dict().items() if key != "legal_status_basis"} | {"legal_status": "in_force"})
    acervo.save(fresh, body, target=target)
    metadata, _ = read_markdown_record(target)
    assert metadata["legal_status"] == "repealed" and metadata["legal_status_basis"]["dre_status"] == "in_force"

    # A prova deixa de existir (o revogador já não revoga): volta o estado do DRE.
    source.write_text(source.read_text(encoding="utf-8").replace("É revogada a", "É alterada a"), encoding="utf-8")
    assert _structure(repo_root) == 0
    assert "1 com a vigência retirada" in capsys.readouterr().out
    metadata, _ = read_markdown_record(target)
    assert metadata["legal_status"] == "in_force" and "legal_status_basis" not in metadata


def test_cited_series_and_repristination_signals():
    from leis_portugal.domain.validity import Repeal
    from leis_portugal.services.structure import proof_signals

    source = _row("pt:dre:1:por", publication_date="2005-01-01")
    target = _row("pt:dre:9:por", series="I", official_number="857/2004", publication_date="2004-07-19")
    # Portaria n.º 1141/2004: a "Portaria n.º 857/2004, publicada na 2.ª série", ligada à da 1.ª série (zona de caça).
    second = Repeal("pt:dre:9:por", "total", "pt:dre:1:por", "n-3",
                    "3.º É revogada a [Portaria n.º 857/2004], publicada na 2.ª série do Diário da República de 30 de Julho de 2004.",
                    label="Portaria n.º 857/2004")
    assert proof_signals(source, second, target, {})["sinais"] == ["serie"]
    azores = Repeal(**{**second.to_dict(), "text": "c) A [Portaria n.º 857/2004], publicada no Jornal Oficial dos Açores, 1.ª série."})
    assert "serie" in proof_signals(source, azores, target, {})["sinais"]
    first = Repeal(**{**second.to_dict(), "text": "É revogada a [Portaria n.º 857/2004], publicada no Diário da República, 1.ª série-B."})
    assert proof_signals(source, first, target, {})["sinais"] == []
    # DL 94/2007: o revogador (DL 208/2012) foi revogado e o DRE regista "Repõe em vigor".
    restored = {**target, "relations": [{"type": "amended_by", "target": "pt:dre:7:por", "label": "Repoe em Vigor Diploma", "date": "2004-07-20"}]}
    assert "repristinado" in proof_signals(source, first, restored, {})["sinais"]


@pytest.mark.parametrize(
    ("text", "scope"),
    [
        (f"b) O {link('Decreto n.º 36974', 'decreto/36974-1948-9')}, à data da entrada em vigor das portarias mencionadas no artigo anterior.", None),
        (f"24.º O presente diploma revoga a {link('Portaria n.º 264/85', 'portaria/264-1985-9')}, de 9 de Maio, e aplica-se aos processos em curso à data da sua entrada em vigor.", "total"),
    ],
)
def test_repeal_at_the_entry_into_force_of_other_acts(text, scope):
    found = {item.scope for item in repeals_in([], text, source="pt:dre:1:por") if item.target == "pt:dre:9:por"}
    assert found == ({scope} if scope else set())
