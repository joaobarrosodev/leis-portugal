from rag import referencias
from rag.fontes import revogado
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


def test_revogacao_so_com_nota_abre_redacao_nova():
    # Como no Código do Trabalho de 2003: o DRE deixa o texto e acrescenta a nota.
    historico = {
        "versions": [_versao("2003-08-27", ["a1"]), _versao("2009-02-17", ["a1r"])],
        "fragments": {
            "a1": {"markdown": "###### Artigo 1.º — Férias\n\n22 dias úteis."},
            "a1r": {"markdown": "###### Artigo 1.º — Férias\n\n22 dias úteis.\n\n> Revogado pelo/a Artigo 12.º do/a Lei n.º 7/2009, em vigor a partir de 2009-02-17"},
        },
    }
    pedacos = {(p.desde, p.ate): revogado(p.texto, p.notas) for p in _com_historico(historico)}
    assert pedacos == {("2003-08-27", "2009-02-17"): False, ("2009-02-17", None): True}


def test_revogado():
    assert revogado("(Revogado.)", "")
    assert revogado("Revogado.", "")
    assert revogado("22 dias úteis.", "Alterado pelo/a Lei n.º 1/2000\nRevogado pelo/a Lei n.º 7/2009")
    assert not revogado("O artigo revogado pela lei anterior mantém-se.", "Alterado pelo/a Lei n.º 1/2000")


def test_termos_ignoram_consoantes_mudas_da_grafia_antiga():
    from rag.texto import termos

    assert termos("trabalho noturno") == termos("trabalho nocturno")
    assert termos("exceção") == termos("excepção")
    assert termos("direção") == termos("direcção")


def test_reescrita_instrucoes_sem_a_linha_dos_ficheiros():
    from rag import reescrita

    texto = reescrita.instrucoes()
    assert "entrada-NN" not in texto and "saida-NN" not in texto
    assert "Mantém todos os elementos da pergunta" in texto
    assert texto.endswith("sem aspas nem explicações.")


def test_reescrever_sem_chave_devolve_a_pergunta(monkeypatch):
    from rag import reescrita

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert reescrita.reescrever("q tem d ter uma fatura") == "q tem d ter uma fatura"


def test_pesquisar_reescrito_guarda_a_pergunta_original():
    from rag import reescrita
    from rag.pesquisa import Consulta

    class Pesquisa:
        def pesquisar(self, pergunta, data, k):
            return Consulta(pergunta, data, referencias.extrair(pergunta), [])

    c = reescrita.pesquisar(Pesquisa(), "q tem d ter uma fatura", "2026-11-10", k=10, consulta="Requisitos da fatura como documento de transporte")
    assert c.pergunta == "q tem d ter uma fatura"
    assert c.pesquisa_por == "Requisitos da fatura como documento de transporte"
    igual = reescrita.pesquisar(Pesquisa(), "Quantos dias de férias?", "2026-11-10", k=10, consulta="Quantos dias de férias?")
    assert igual.pesquisa_por is None


def test_numeros_ue_aceita_as_formas_de_citar_atos_da_ue():
    from rag.pesquisa import _numeros_ue

    assert "1994/631" in _numeros_ue("631/94")  # Decisão 94/631
    assert "1998/195" in _numeros_ue("98/195")  # Regulamento (CE) n.º 195/98
    assert "2025/2180" in _numeros_ue("2180/2025")  # Regulamento (UE) 2025/2180
    assert _numeros_ue("2025/2180") == ["2025/2180"]
    assert _numeros_ue("13-A/2010") == ["13-A/2010"]


def test_tipos_da_serie_ii_recolhidos_em_massa_ficam_fora_do_indice(tmp_path):
    import sqlite3

    from rag.indice import documentos_do_export, fora_por_omissao

    assert fora_por_omissao("regulamento", "2026-11-12T14:50:00Z")
    assert not fora_por_omissao("regulamento", "2026-11-11T22:30:32Z")  # já citado por um diploma do acervo
    assert not fora_por_omissao("decreto-lei", "2026-11-13T09:00:00Z")
    export = tmp_path / "export.sqlite"
    with sqlite3.connect(export) as con:
        con.execute(
            "CREATE TABLE documentos (id, title, document_type, official_number, official_date, publication_date, summary,"
            " legal_status, version_kind, consolidation_date, path, retrieved_at, text_quality)"
        )
        linhas = [
            ("a", "Regulamento", "regulamento", None, None, "2020-01-01", "", None, None, None, "a.md", "2026-11-12T15:00:00Z", "texto"),
            ("b", "Regulamento", "regulamento", None, None, "2020-01-01", "", None, None, None, "b.md", "2026-11-01T15:00:00Z", "texto"),
            ("c", "Decreto-Lei", "decreto-lei", None, None, "2020-01-01", "", None, None, None, "c.md", "2026-11-12T15:00:00Z", "texto"),
        ]
        con.executemany("INSERT INTO documentos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", linhas)
    assert [d.id for d in documentos_do_export(export)] == ["b", "c"]
    assert [d.id for d in documentos_do_export(export, com_serie_ii=True)] == ["a", "b", "c"]
