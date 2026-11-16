"""Os dois leitores de artigos leem os mesmos títulos com o mesmo número.

`domain/articles.py` é o do acervo; `avaliacao/comum.py` é o do índice do RAG, que guarda o número
na forma das perguntas («1.º», «78.º-A»), porque a pesquisa procura o artigo pelo número exato.
"""

import pytest
from rag.fontes import comum, ler_artigos

from leis_portugal.domain.articles import number_slug, parse_articles


# (título, número no RAG, slug no acervo)
CASOS = [
    ("Artigo 1o", "1.º", "1"),  # atos antigos do EUR-Lex
    ("Artigo 2o. — Objecto", "2.º", "2"),
    ("Artigo 3g.", "3.º", "3"),  # o «º» lido como «g» nos atos antigos do EUR-Lex
    ("Artigo 4º.", "4.º", "4"),
    ("Artigo 5°.", "5.º", "5"),
    ("Artigo 6. — Atribuição", "6.º", "6"),
    ("Artigo 7. º — Arquivos", "7.º", "7"),
    ("Artigo 34 .º — Coimas", "34.º", "34"),
    ("Artigo 9 º", "9.º", "9"),
    ("Artigo 12.ºA — Aditado", "12.º-A", "12-a"),
    ("Artigo 13.oA", "13.º-A", "13-a"),
    ("Artigo 14.º–EA", "14.º-EA", "14-ea"),
    ("Artigo 230.º-AAA — Destinatários", "230.º-AAA", "230-aaa"),
    ("Artigo A-1/2.º — Âmbito", "A-1/2.º", "a-1-2-o"),
    ("Artigo C - 1/4.º — Obras", "C-1/4.º", "c-1-4-o"),
    ("Artigo A/1 - 5.º — Decisão", "A/1-5.º", "a-1-5-o"),
    ("Artigo E-1/ 77.º — Ocupação", "E-1/77.º", "e-1-77-o"),
    ("Artigo D-11/2.º-A — Definições", "D-11/2.º-A", "d-11-2-o-a"),
    ("Artigo III/1.º — Âmbito e objeto", "III/1.º", "iii-1-o"),
    ("Artigo 2.1 — Âmbito de aplicação", "2.1", "2-1"),
    ("Artigo12.º — Regiões ultraperiféricas", "12.º", "12"),
]


@pytest.mark.parametrize(("titulo", "numero", "slug"), CASOS)
def test_os_dois_leitores_leem_o_mesmo_numero(titulo, numero, slug):
    texto = f"# Ato\n\n###### Artigo 99.º\n\nAntes.\n\n###### {titulo}\n\nTexto.\n"
    rag = ler_artigos(texto)
    acervo = parse_articles(texto)
    assert [a.chave for a in rag] == ["99.º", numero]
    assert rag[1].texto == "Texto."
    assert len(acervo) == 2
    assert number_slug(acervo[1].number) == slug
    assert comum.numero_artigo(acervo[1].number) == numero


@pytest.mark.parametrize("titulo", ["Artigo 87.º - Ensaios.", "Artigo 1.º - 1 - ...", "Artigo 6 - 15000$00;"])
def test_hifen_nao_e_titulo_no_rag(titulo):
    # Decretos antigos com o resto dos artigos em texto corrido, artigos alterados e linhas de tabela.
    assert ler_artigos(f"###### {titulo}\n\nTexto.") == []


def test_letra_depois_de_hifen():
    assert [a.chave for a in ler_artigos("###### Artigo 10.º - A — Objeto\n\nTexto.")] == ["10.º-A"]


@pytest.mark.parametrize("titulo", ["Artigo 5.º A presente lei entra em vigor", "Artigo 3.º – A Comissão"])
def test_letra_que_comeca_uma_frase_nao_e_aditado(titulo):
    numeros = [a.numero for a in ler_artigos(f"###### {titulo}\n\nTexto.")]
    assert "5.º-A" not in numeros and "3.º-A" not in numeros


def test_pontuacao_no_fim():
    # O RAG já lia estes títulos com a pontuação na chave («10.º:»); o `articles.py` não os lê, porque
    # muitos são linhas de tabela («Artigo 487.º: — … 2500$00») ou listas («Artigo 1.º;»).
    assert [a.chave for a in ler_artigos("###### Artigo 10.º:\n\nA.\n\n###### Artigo 18.º...\n\nB.")] == ["10.º", "18.º"]
    # «Artigo 42.º ...» é o artigo que o ato de alteração não muda: nenhum dos dois o lê.
    assert ler_artigos("###### Artigo 42.º ...\n\nC.") == []
    assert [a.number for a in parse_articles("# Lei\n\n###### Artigo 42.º ...\n\nArtigo 1.º Texto.")] == ["1.º"]


def test_numero_artigo():
    assert comum.numero_artigo("único.") == "único"
    assert comum.numero_artigo("IV") == "IV"
    assert comum.numero_artigo("6 - 15000$00;") is None
