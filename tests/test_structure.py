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
from leis_portugal.services.structure import compare


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
