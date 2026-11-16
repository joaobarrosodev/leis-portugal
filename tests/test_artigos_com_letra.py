"""Artigos aditados com a letra separada do número: «78.º A», «292.º ‐A» (hífen U+2010 do EUR-Lex).

Os dois leitores de artigos (`domain/articles.py`, do acervo, e `avaliacao/comum.py`, do RAG) têm de
os ler como artigos próprios, com o número «78.º-A», e não colar o texto ao artigo anterior.
"""

from rag.fontes import ler_artigos

from leis_portugal.domain.articles import parse_articles


TEXTO = "\n\n".join([
    "# Regulamento",
    "###### Artigo 78.º — Base", "Texto do 78.º.",
    "###### Artigo 78.º A — Equipamento", "Texto do 78.º-A.",
    "###### Artigo 78.º B", "Texto do 78.º-B.",
    "###### Artigo 292.º ‐A — Disposição", "Texto do 292.º-A.",
    "###### Artigo 292.º‐B", "Texto do 292.º-B.",
    "###### Artigo 35.º- A — Subsídios", "Texto do 35.º-A.",
    "###### Artigo 13.º-A — Já lido", "Texto do 13.º-A.",
    "###### Artigo 79.º — Seguinte", "Texto do 79.º.",
])
NUMEROS = ["78.º", "78.º-A", "78.º-B", "292.º-A", "292.º-B", "35.º-A", "13.º-A", "79.º"]


def test_articles_le_a_letra_separada():
    artigos = parse_articles(TEXTO)
    assert [a.number for a in artigos] == NUMEROS
    assert [a.key for a in artigos] == ["art-78", "art-78-a", "art-78-b", "art-292-a", "art-292-b", "art-35-a", "art-13-a", "art-79"]
    assert artigos[0].text == "Texto do 78.º."
    assert artigos[1].heading == "Equipamento"


def test_leitor_do_rag_le_a_letra_separada():
    artigos = ler_artigos(TEXTO)
    assert [a.chave for a in artigos] == NUMEROS
    assert artigos[0].texto == "Texto do 78.º."
    assert artigos[3].epigrafe == "Disposição"


def test_letra_que_comeca_o_texto_nao_e_artigo_aditado():
    # Texto corrido: «Artigo 5.º A presente lei…» é o 5.º, não o 5.º-A.
    artigos = parse_articles("# Lei\n\nArtigo 5.º A presente lei entra em vigor amanhã.\n\nArtigo 6.º\n\nTexto.")
    assert [a.number for a in artigos] == ["5.º", "6.º"]
