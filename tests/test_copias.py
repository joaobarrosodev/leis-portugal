"""Cópias do mesmo texto em vários registos e redações anteriores (`rag/copias.py`, `rag.indice.aplicar_redacoes`)."""

from pathlib import Path

from rag import copias
from rag.indice import Pedaco, aplicar_redacoes


def _artigos(epigrafes: list[str], texto: str = "Texto do artigo {n}.", nota: str = "") -> str:
    return "\n\n".join(f"###### Artigo {n}.º — {e}\n\n{texto.format(n=n)}{nota}" for n, e in enumerate(epigrafes, 1))


TEMAS = [f"Tema {n}" for n in range(1, 13)]
NOTA = "\n\n> Alterado pelo/a [Decreto-Lei n.º 9/2025 - DR de 2025-04-01](https://x), em vigor a partir de {}"


def test_numeracoes_da_mesma_parte_do_indice():
    # «## ANEXO» em maiúsculas não abre parte no leitor do índice: o decreto e a republicação ficam na parte «».
    texto = _artigos(["Objeto", "Republicação"]) + "\n\n## ANEXO — (a que se refere o artigo 2.º)\n\n" + _artigos(TEMAS)
    lidas = copias.ler_partes(texto)
    assert {n: (len(p.artigos), p.parte_no_indice, p.numeracao, p.numeracoes) for n, p in lidas.items()} == {"": (2, "", 1, 2), "(2.ª numeração)": (12, "", 2, 2)}
    assert lidas["(2.ª numeração)"].textos["3.º"] == copias.impressao("Texto do artigo 3.")


def test_impressao_ignora_a_grafia_do_acordo_ortografico():
    assert copias.impressao("A contra-ordenação é punida com coima; a acção prescreve.") == copias.impressao("A contraordenação é punida com coima, a ação prescreve")
    assert copias.impressao("coima de 60 euros") != copias.impressao("coima de 120 euros")


def test_referencias_em_maiusculas():
    assert copias.referencias("Anexo V — REPUBLICAÇÃO DO DECRETO-LEI N.º 152-D/2017, DE 11 DE DEZEMBRO") == ["Decreto-Lei n.º 152-D/2017"]


def test_mesmo_texto_pede_epigrafes_e_texto():
    a = copias.ler_partes(_artigos(TEMAS))[""]
    assert copias.mesmo_texto(a, copias.ler_partes(_artigos(TEMAS))[""])
    # O mesmo molde com outro texto (os orçamentos de dois anos): as epígrafes coincidem, os artigos não.
    assert not copias.mesmo_texto(a, copias.ler_partes(_artigos(TEMAS, "Outro texto {n}."))[""])
    assert not copias.copia_evidente(a, copias.ler_partes(_artigos(TEMAS))[""])  # menos de 20 artigos: precisa da citação


def _acervo(tmp_path: Path, registos: list[tuple], alterado_por: dict, texto_em_vigor_em: dict | None = None):
    docs, cabecalhos = {}, {}
    for i, titulo, sumario, data, corpo, consolidado_ate in registos:
        caminho = tmp_path / f"{i}.md"
        versao = f"version:\n  kind: consolidated\n  label: Versão consolidada pelo DRE\n  consolidation_date: '{consolidado_ate}'\n" if consolidado_ate else ""
        caminho.write_text(f"---\nnotes: []\n{versao}---\n\n{corpo}", encoding="utf-8")
        docs[i] = {"id": i, "title": titulo, "summary": sumario, "document_type": "decreto-lei", "publication_date": data, "legal_status": "in_force",
                   "text_quality": "texto", "version_kind": "consolidated" if consolidado_ate else "original", "path": f"{i}.md", "series": "I"}
        if consolidado_ate:
            cabecalhos[i] = copias.cabecalho(caminho)
    altera: dict = {}
    for alvo, alteradores in alterado_por.items():
        for a, _, _ in alteradores:
            altera.setdefault(a, set()).add(alvo)
    return copias.Acervo(docs, alterado_por, {}, texto_em_vigor_em or {}, altera, por_titulo={d["title"]: [i] for i, d in docs.items()}), cabecalhos


def test_redacoes_anteriores_com_prova_e_o_que_fica_de_fora(tmp_path):
    codigo = "Aprova o Código das Coisas"
    registos = [
        # O código de 2000 no registo que o aprovou, consolidado e alterado em 2025: é a cópia atual.
        ("atual", "Decreto-Lei n.º 1/2000", codigo, "2000-01-10", _artigos(TEMAS, nota=NOTA.format("2025-04-11")), "2025-04-11"),
        # Republicação de 2010 no anexo de um diploma de alteração que o DRE não consolida.
        ("rep", "Decreto-Lei n.º 5/2010", "Altera o Decreto-Lei n.º 1/2000", "2010-05-05", _artigos(["Objeto", "Republicação"]) + "\n\n## ANEXO\n\n" + _artigos(TEMAS), None),
        # Diploma de alteração de 2012 que cita os artigos novos no seu articulado: não se separa.
        ("cita", "Decreto-Lei n.º 7/2012", "Altera o Decreto-Lei n.º 1/2000", "2012-07-07", _artigos(["Tema 1", "Alteração ao Decreto-Lei n.º 1/2000", *TEMAS[2:]]), None),
        # A republicação de 2025 que fez a última alteração: o atual já a cita nas notas, por isso não há prova de texto posterior.
        ("ultima", "Decreto-Lei n.º 9/2025", "Altera o Decreto-Lei n.º 1/2000", "2025-04-01", _artigos(["Objeto", "Republicação"]) + "\n\n## ANEXO\n\n" + _artigos(TEMAS), None),
    ]
    alteradores = [("rep", "2010-05-05", None), ("cita", "2012-07-07", None), ("ultima", "2025-04-01", None)]
    acervo, cabecalhos = _acervo(tmp_path, registos, {"atual": alteradores})
    marcas, fora = copias.redacoes_anteriores(acervo, cabecalhos, tmp_path, "2026-11-20", tipos=("decreto-lei",))
    # A republicação de 2010 fica fechada na data da prova mais antiga: o diploma de 2012, que o DRE regista como alterador.
    assert [(m.documento, m.parte, m.ate, m.alvo, len(m.artigos)) for m in marcas] == [("rep", "", "2012-07-07", "atual", 12)]
    assert ("1.º", copias.impressao("Texto do artigo 1.")) in marcas[0].artigos
    motivos = {f["id"]: f["motivo"].split(":")[0].split(" (")[0] for f in fora}
    assert motivos == {"cita": "a parte mistura o articulado de um diploma de alteração com o texto que ele cita", "ultima": "sem prova de um texto posterior ao desta cópia"}


def test_aplicar_redacoes_fecha_so_os_artigos_da_copia():
    pedacos = [
        Pedaco("", "1.º", "Objeto", "1.º", "Altera o código.", "", "2010-05-05", None),  # artigo do decreto, com a mesma chave
        Pedaco("", "1.º", "Tema 1", "1.º", "Texto do artigo 1.", "", "2010-05-05", None),
        Pedaco("", "2.º", "Tema 2", "2.º", "Texto do artigo 2.", "", "2010-05-05", None),
        Pedaco("", "2.º", "Tema 2", "2.º", "Texto antigo.", "", "2010-05-05", "2011-01-01"),  # já fechado: fica como está
        Pedaco("", "3.º", "Tema 3", "3.º", "Texto do artigo 3.", "", "2021-01-01", None),  # começou depois da data: intervalo vazio
    ]
    artigos = frozenset((n, copias.impressao(f"Texto do artigo {k}.")) for k, n in enumerate(("1.º", "2.º", "3.º"), 1))
    marca = copias.Marca("rep", "", artigos, None, "2012-07-07", "atual", "", "prova")
    assert aplicar_redacoes(pedacos, [marca]) == 3
    assert [p.ate for p in pedacos] == [None, "2012-07-07", "2012-07-07", "2011-01-01", "2021-01-01"]


def test_aplicar_redacoes_nos_registos_em_blocos():
    pedacos = [
        Pedaco("", "", "", "texto#1", "Artigo 1.º É aprovado o Código.\n\nArt. 2.º Entra em vigor.", "", "1984-12-26", None),
        Pedaco("", "", "", "texto#2", "Art. 3.º Revogações.\n\nArtigo 1.º Estão sujeitas a imposto:\n\na) As transmissões de bens", "", "1984-12-26", None),
        Pedaco("", "", "", "texto#3", "Artigo 2.º São sujeitos passivos", "", "1984-12-26", None),
    ]
    marca = copias.Marca("iva", "", None, "Artigo 1.º Estão sujeitas a imposto:\na) As transmissões de bens", "1989-06-12", "atual", "", "prova")
    assert aplicar_redacoes(pedacos, [marca]) == 1  # o bloco onde o código começa tem o fim do decreto: fica aberto
    assert [p.ate for p in pedacos] == [None, None, "1989-06-12"]
