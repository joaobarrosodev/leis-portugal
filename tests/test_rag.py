from rag import referencias
from rag.indice import _com_historico


def test_referencias_diplomas_codigos_e_artigos():
    refs = referencias.extrair("Qual a taxa do artigo 78.º-B do Código do IRS e do DL 84/2021?")
    assert refs.artigos == ["78.º-B"]
    assert refs.codigos == ["Código do Imposto sobre o Rendimento das Pessoas Singulares"]
    assert refs.diplomas == [("decreto-lei", "84/2021", "DL 84/2021")]


def test_referencias_numeros_antigos_e_regionais():
    refs = referencias.extrair("Segundo o Decreto-Lei n.º 433/1999 e o Decreto Regulamentar Regional n.º 21/2023/A")
    assert [d[:2] for d in refs.diplomas] == [("decreto-lei", "433/99"), ("decreto-regulamentar-regional", "21/2023/A")]


def test_referencias_regulamento_europeu():
    refs = referencias.extrair("O Regulamento (UE) 2016/679 aplica-se?")
    assert ("regulation", "2016/679") in [d[:2] for d in refs.diplomas]


def _versao(data, fragmentos):
    return {"date": data, "fragments": fragmentos}


def test_historico_da_um_pedaco_por_redacao():
    historico = {
        "versions": [_versao("2010-01-01", ["a1", "a2"]), _versao("2015-01-01", ["a1b", "a2"]), _versao("2020-01-01", ["a1b", "a2"])],
        "fragments": {
            "a1": {"markdown": "###### Artigo 1.º — Coimas\n\nCoima de 100 euros."},
            "a1b": {"markdown": "###### Artigo 1.º — Coimas\n\nCoima de 500 euros."},
            "a2": {"markdown": "###### Artigo 2.º — Entrada em vigor\n\nNo dia seguinte."},
        },
    }
    pedacos = {(p.chave, p.desde, p.ate): p.texto for p in _com_historico(historico)}
    assert pedacos == {
        ("1.º", "2010-01-01", "2015-01-01"): "Coima de 100 euros.",
        ("1.º", "2015-01-01", None): "Coima de 500 euros.",
        ("2.º", "2010-01-01", None): "No dia seguinte.",
    }
