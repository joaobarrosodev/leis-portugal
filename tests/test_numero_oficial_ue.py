"""O número oficial dos atos da UE quando o do CELLAR está errado.

Só se corrige quando duas fontes concordam contra o CELLAR; os casos são do acervo (16/11/2026).
"""

import pytest

from leis_portugal.sources.eurlex.mapper import official_number, title_number


BCE = ["Banco Central Europeu"]
COMISSAO = ["Comissão Europeia"]


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("2007/48/CE: Decisão do Banco Central Europeu, de 30 de Dezembro de 2006", (2007, 48)),
        ("85/269/CEE: Decisão da Comissão, de 30 de Abril de 1985", (1985, 269)),
        ("Decisão de Execução (UE) 2016/775 da Comissão, de 18 de maio de 2016", (2016, 775)),
        ("Decisão (UE) 2019/47 do Banco Central Europeu, de 29 de novembro de 2018", (2019, 47)),
        ("Regulamento (CEE) nº 211/91 da Comissão, de 30 de Janeiro de 1992", (1991, 211)),
        ("Regulamento (CE) n.o 1577/1998 da Comissão", (1998, 1577)),
        ("Directiva 2010/45/UE do Parlamento Europeu e do Conselho", (2010, 45)),
        ("Decisão da Comissão, de 20 de julho de 1976, que derroga a recomendação n.º 1/64", None),
    ],
)
def test_numero_no_titulo(title, expected):
    assert title_number(title) == expected


@pytest.mark.parametrize(
    ("cellar", "celex", "title", "year", "authors", "expected"),
    [
        # BCE: o CELLAR dá o ano da adoção; o título e o Jornal Oficial, o da publicação.
        ((2006, 48), (2006, 30), "2007/48/CE: Decisão do Banco Central Europeu, de 30 de Dezembro de 2006", 2007, BCE, "2007/48"),
        ((2018, 47), (2018, 31), "Decisão (UE) 2019/47 do Banco Central Europeu, de 29 de novembro de 2018", 2019, BCE, "2019/47"),
        # BCE: o CELLAR e o CELEX trazem o número interno (BCE/2016/27).
        ((2016, 27), (2016, 27), "Decisão (UE) 2016/1717 do Banco Central Europeu, de 21 de setembro de 2016", 2016, BCE, "2016/1717"),
        # O título e o CELEX contra o CELLAR.
        ((2016, 776), (2016, 775), "Decisão de Execução (UE) 2016/775 da Comissão, de 18 de maio de 2016", 2016, COMISSAO, "2016/775"),
        ((1985, 1519), (1985, 269), "85/269/CEE: Decisão da Comissão, de 30 de Abril de 1985", 1985, COMISSAO, "1985/269"),
    ],
)
def test_corrige_quando_duas_fontes_concordam(cellar, celex, title, year, authors, expected):
    number, note = official_number(cellar, celex=celex, title=title, publication_year=year, authors=authors)
    assert number == expected
    assert note is not None and f"o CELLAR dá {cellar[0]}/{cellar[1]}" in note and expected in note


@pytest.mark.parametrize(
    ("cellar", "celex", "title", "year", "authors"),
    [
        # A gralha é do título: o CELEX confirma o CELLAR.
        ((2010, 53), (2010, 53), "Directiva 2010/45/UE do Parlamento Europeu e do Conselho, de 7 de Julho de 2010", 2010, ["Parlamento Europeu"]),
        ((1985, 172), (1985, 172), "Directiva 84/172/CEE do Conselho, de 28 de Fevereiro de 1985", 1985, ["Conselho da União Europeia"]),
        # Só o título: a Decisão 2000/45/CE publicada em 2001 fica como o CELLAR a dá.
        ((2001, 45), (2001, 45), "2000/45/CE: Decisão da Comissão, de 29 de Setembro de 1999", 2001, COMISSAO),
        # O número certo.
        ((2016, 776), (2016, 776), "Decisão (UE) 2016/776 do Conselho, de 18 de maio de 2016", 2016, ["Conselho da União Europeia"]),
        ((1976, 677), (1976, 677), "Decisão da Comissão, de 20 de julho de 1976, que derroga a recomendação n.º 1/64", 1976, COMISSAO),
    ],
)
def test_nao_corrige_com_uma_so_fonte(cellar, celex, title, year, authors):
    assert official_number(cellar, celex=celex, title=title, publication_year=year, authors=authors) == (f"{cellar[0]}/{cellar[1]}", None)
