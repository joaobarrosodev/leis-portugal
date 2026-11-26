from rag import referencias
from rag.fontes import revogado
from rag.indice import _com_historico


def test_referencias_diplomas_codigos_e_artigos():
    refs = referencias.extrair("Qual a taxa do artigo 78.º-B do Código do IRS e do DL 84/2021?")
    assert refs.artigos == ["78.º-B"]
    assert refs.codigos == ["Código do Imposto sobre o Rendimento das Pessoas Singulares"]
    assert refs.diplomas == [("decreto-lei", "84/2021", "DL 84/2021")]


def test_referencias_artigo_sem_a_palavra_artigo_so_antes_de_um_codigo():
    # Como os advogados citam: «o 394.º do CT», «359.º e seguintes do CT», «o 72.º, n.º 1, alínea a), do CPP».
    refs = referencias.extrair("Penso usar o 394.º do CT, o 359.º e seguintes do CT e o 72.º, n.º 1, alínea a), do CPP.")
    assert refs.artigos == ["394.º", "359.º", "72.º"]
    assert referencias.extrair("o 166.º-A do CT").artigos == ["166.º-A"]
    # Sem código logo a seguir, um ordinal não é artigo.
    for texto in ("acabou o 12.º ano", "dona do 4.º esquerdo do prédio", "no 5.º andar. O Código Civil diz", "o n.º 3 do Código do Trabalho"):
        assert referencias.extrair(texto).artigos == [], texto


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


def test_artigo_reposto_depois_de_revogado_nao_esta_revogado():
    # Código Civil, art. 1064.º: revogado em 1975, reposto pela Lei n.º 6/2006 (a nota mais recente vem primeiro).
    notas = (
        "Alterado pelo/a Artigo 3.º do/a Lei n.º 6/2006, em vigor a partir de 2006-06-27\n"
        "Revogado pelo/a Artigo 46.º do/a Decreto-Lei n.º 201/75, em vigor a partir de 1975-04-30"
    )
    assert not revogado("A presente secção aplica-se ao arrendamento…", notas)
    # Ao contrário: alterado e depois revogado.
    notas = (
        "Revogado pelo/a Lei n.º 7/2009, em vigor a partir de 2009-02-17\n"
        "Alterado pelo/a Lei n.º 1/2000, em vigor a partir de 2000-01-01"
    )
    assert revogado("22 dias úteis.", notas)
    # Data impossível na nota de revogação (gralha do DRE): fica revogado, como antes.
    notas = (
        "Revogado pelo/a Lei n.º 1/79, em vigor a partir de 1079-01-01\n"
        "Alterado pelo/a Decreto-Lei n.º 614/71, em vigor a partir de 1972-01-01"
    )
    assert revogado("Os empréstimos dos corpos administrativos…", notas)
    # Conta a data de publicação, não a de vigência (Estatuto dos Benefícios Fiscais, art. 42.º).
    notas = (
        "Revogado pelo/a Artigo 210.º do/a [Lei n.º 83-C/2013 - Diário da República n.º 253/2013, 1º Suplemento, Série I de 2013-12-31](x),"
        " em vigor a partir de 2004-01-01\n"
        "Alterado pelo/a Artigo 3.º do/a [Decreto-Lei n.º 108/2008 - Diário da República n.º 123/2008, Série I de 2008-06-26](y), em vigor a partir de 2008-06-27"
    )
    assert revogado("Os rendimentos…", notas)


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


def test_sem_traducoes_tira_os_atos_traduzidos(tmp_path):
    import sqlite3

    from rag.indice import documentos_do_export

    export = tmp_path / "export.sqlite"
    with sqlite3.connect(export) as con:
        con.execute(
            "CREATE TABLE documentos (id, title, document_type, official_number, official_date, publication_date, summary,"
            " legal_status, version_kind, consolidation_date, path, retrieved_at, text_quality)"
        )
        linhas = [
            ("t", "Diretiva", "diretiva", None, None, "1975-01-01", "", None, "translation", None, "t.md", "2026-11-14T10:00:00Z", "texto"),
            ("o", "Diretiva", "diretiva", None, None, "1975-01-01", "", None, "original", None, "o.md", "2026-11-01T10:00:00Z", "texto"),
        ]
        con.executemany("INSERT INTO documentos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", linhas)
    assert [d.id for d in documentos_do_export(export)] == ["o", "t"]
    assert [d.id for d in documentos_do_export(export, com_traducoes=False)] == ["o"]


def _avisos_de(documento: dict) -> list[str]:
    from types import SimpleNamespace

    from rag.pesquisa import Pesquisa, Resultado

    falso = SimpleNamespace(documento=lambda _id: documento, relacoes=lambda _id: [], julgamentos=lambda _r: [])
    r = Resultado(1, "x", "Diretiva", "", "1.º", "", "1.º", "Diretiva › Artigo 1.º", "Texto.", "", "1975-01-01", None)
    Pesquisa._avisos(falso, r, "2026-11-16")
    return r.avisos


def test_ato_traduzido_avisa_que_a_traducao_nao_e_oficial():
    from rag.pesquisa import AVISO_TRADUCAO

    assert AVISO_TRADUCAO in _avisos_de({"versao": "translation", "legal_status": "in_force"})
    assert AVISO_TRADUCAO not in _avisos_de({"versao": "original", "legal_status": "in_force"})


def test_numero_da_2a_serie_com_sufixo_encontra_o_diploma():
    import sqlite3
    from types import SimpleNamespace

    from rag.pesquisa import Pesquisa

    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE documentos (id, tipo, numero, data)")
    con.executemany("INSERT INTO documentos VALUES (?, ?, ?, ?)", [
        ("a", "declaracao", "81/2002 (2.ª série)", "2002-04-03"),
        ("b", "edital", "113/2000 (2.ª série) - AP", "2000-03-01"),
        ("c", "declaracao", "81/20021", "2021-01-01"),
        ("d", "declaracao", "81/2002", "2002-01-01"),
        ("e", "regulamento", "11/2003 - AP", "2003-07-10"),
    ])
    falso = SimpleNamespace(con=con)
    assert Pesquisa.diplomas(falso, "declaracao", "81/2002") == ["d", "a"]
    assert Pesquisa.diplomas(falso, "edital", "113/2000") == ["b"]
    assert Pesquisa.diplomas(falso, "declaracao", "81/200") == []
    assert Pesquisa.diplomas(falso, "regulamento", "11/2003") == ["e"]


def test_referencias_aos_atos_da_2a_serie():
    from rag import referencias

    diplomas = referencias.extrair(
        "No Edital n.º 317/2001 (2.ª série), no Acordo Coletivo de Trabalho n.º 206/2015 e no Regulamento n.º 296-B/2007"
    ).diplomas
    assert [(t, n) for t, n, _ in diplomas] == [
        ("edital", "317/2001"), ("acordo-coletivo-trabalho", "206/2015"), ("regulamento", "296-B/2007"),
    ]
    # O regulamento da UE continua a ser lido como antes (e também como regulamento português).
    assert [(t, n) for t, n, _ in referencias.extrair("Regulamento (CE) n.º 1234/2007").diplomas] == [
        ("regulation", "2007/1234"), ("regulamento", "1234/2007"),
    ]


def test_diploma_so_por_referencia_fica_fora_do_bm25_em_todo_o_acervo(tmp_path):
    import sqlite3

    from rag.pesquisa import Pesquisa

    from test_dados import _artigos, _construir

    caminho = _construir(tmp_path / "i.sqlite", {
        "pt:lei:001": ("Lei n.º 1/2020", "piscinas", _artigos(2, "piscina"), []),
        "pt:reg:002": ("Regulamento n.º 2/2020", "piscinas municipais", _artigos(2, "piscina", "piscina municipal"), []),
        # Outros diplomas, para "piscina" não estar em mais de 20% dos pedaços (a pesquisa ignorava-a).
        **{f"pt:lei:{n:03}": (f"Lei n.º {n}/2020", "estradas", _artigos(2, "estrada"), []) for n in range(3, 13)},
    })
    con = sqlite3.connect(caminho)
    con.execute("CREATE TABLE so_referencia (id TEXT PRIMARY KEY)")
    con.execute("INSERT INTO so_referencia VALUES ('pt:reg:002')")
    con.commit()
    con.close()
    p = Pesquisa(caminho)
    documento = lambda ids: {p._info([i])[i][2] for i, _ in ids}  # noqa: E731
    assert documento(p.bm25("piscina", "2026-01-01")) == {"pt:lei:001"}
    # Quando a pergunta o cita, encontra-se como os outros.
    assert documento(p.bm25("piscina", "2026-01-01", documentos=["pt:reg:002"])) == {"pt:reg:002"}


# --- passo_llm: contextos de vários tamanhos a partir da mesma pesquisa


def _resultados(k: int):
    from rag.pesquisa import Resultado

    return [Resultado(n, "pt:doc", "Lei n.º 1/2020", "", f"{n}.º", "", f"{n}.º", f"Lei n.º 1/2020 › Artigo {n}.º", f"Texto {n}.", "", None, None) for n in range(1, k + 1)]


class _PesquisaFalsa:
    def __init__(self):
        self.chamadas: list[tuple[str, int]] = []

    def pesquisar(self, pergunta, data, k):
        from rag.pesquisa import Consulta

        self.chamadas.append((pergunta, k))
        return Consulta(pergunta, data, referencias.extrair(pergunta), _resultados(k))


def _passo_llm(monkeypatch, tmp_path):
    from rag import avaliar, passo_llm

    perguntas = [{"id": f"cmp-{i}", "tipo": "composta", "pergunta": f"Pergunta {i}?", "data_referencia": "2026-11-19"} for i in (1, 2, 3)]
    monkeypatch.setattr(passo_llm, "PASTA", tmp_path / "llm")
    monkeypatch.setattr(avaliar, "ler_perguntas", lambda ficheiro=None: perguntas)
    return passo_llm


def test_contexto_respeita_o_numero_de_artigos():
    from rag.pesquisa import Consulta
    from rag.resposta import ARTIGOS_NO_CONTEXTO, contexto

    consulta = Consulta("Pergunta?", "2026-11-19", referencias.extrair("Pergunta?"), _resultados(20))
    assert len(contexto(consulta)[1]) == ARTIGOS_NO_CONTEXTO
    texto, artigos = contexto(consulta, 16)
    assert len(artigos) == 16 and "[16] Lei n.º 1/2020 › Artigo 16.º" in texto and "[17]" not in texto


def test_exportar_sem_contextos_fica_como_antes(monkeypatch, tmp_path):
    passo_llm = _passo_llm(monkeypatch, tmp_path)
    pesquisa = _PesquisaFalsa()
    passo_llm.exportar("x", {"composta"}, 10, 1.0, None, {}, pesquisa=pesquisa)
    assert [k for _, k in pesquisa.chamadas] == [10, 10, 10]
    assert sorted(p.name for p in (tmp_path / "llm").iterdir()) == ["x"]
    entrada = (tmp_path / "llm" / "x" / "entrada-01.jsonl").read_text(encoding="utf-8")
    assert "[8]" in entrada and "[9]" not in entrada


def test_exportar_varios_contextos_com_uma_so_pesquisa(monkeypatch, tmp_path):
    import json

    passo_llm = _passo_llm(monkeypatch, tmp_path)
    pesquisa = _PesquisaFalsa()
    consultas = tmp_path / "consultas"
    passo_llm.exportar("x", {"composta"}, 2, 1.0, None, {"cmp-1": "Consulta jurídica 1"}, contextos=[8, 16], consultas=consultas, pesquisa=pesquisa)
    assert pesquisa.chamadas == [("Consulta jurídica 1", 16), ("Pergunta 2?", 16), ("Pergunta 3?", 16)]
    for n in (8, 16):
        pasta = tmp_path / "llm" / f"x-ctx{n}"
        linhas = [json.loads(x) for f in sorted(pasta.glob("entrada-*.jsonl")) for x in f.read_text(encoding="utf-8").splitlines()]
        assert [x["id"] for x in linhas] == ["cmp-1", "cmp-2", "cmp-3"]
        assert all(f"[{n}] " in x["mensagem"] and f"[{n + 1}] " not in x["mensagem"] for x in linhas)
        assert (pasta / "INSTRUCOES.md").exists()
    assert sorted(f.name for f in consultas.iterdir()) == ["cmp-1.pickle", "cmp-2.pickle", "cmp-3.pickle"]
    # Depois de um corte, as consultas guardadas não se pesquisam outra vez.
    (consultas / "cmp-3.pickle").unlink()
    outra = _PesquisaFalsa()
    passo_llm.exportar("x", {"composta"}, 2, 1.0, None, {}, contextos=[8, 16], consultas=consultas, pesquisa=outra)
    assert outra.chamadas == [("Pergunta 3?", 16)]


def test_consulta_guardada_com_menos_resultados_pesquisa_outra_vez(monkeypatch, tmp_path):
    passo_llm = _passo_llm(monkeypatch, tmp_path)
    p = {"id": "cmp-1", "pergunta": "Pergunta 1?", "data_referencia": "2026-11-19"}
    pesquisa = _PesquisaFalsa()
    passo_llm.pesquisar(pesquisa, p, {}, k=10, consultas=tmp_path)
    assert len(passo_llm.pesquisar(pesquisa, p, {}, k=8, consultas=tmp_path).resultados) == 10
    assert len(passo_llm.pesquisar(pesquisa, p, {}, k=16, consultas=tmp_path).resultados) == 16
    assert [k for _, k in pesquisa.chamadas] == [10, 16]


def test_importar_le_as_citacoes_sobre_o_contexto_dado(monkeypatch, tmp_path):
    import json

    from rag import avaliar

    passo_llm = _passo_llm(monkeypatch, tmp_path)
    consultas = tmp_path / "consultas"
    passo_llm.exportar("x", {"composta"}, 10, 1.0, None, {}, contextos=[8, 16], consultas=consultas, pesquisa=_PesquisaFalsa())
    respostas = [{"id": "cmp-1", "responde": True, "resposta": "Diz o artigo 12.º.", "citacoes": [12]},
                 {"id": "cmp-2", "responde": True, "resposta": "Diz o artigo 2.º.", "citacoes": [2]},
                 {"id": "cmp-3", "responde": False, "resposta": "", "citacoes": []}]
    vistas: dict[int, dict] = {}
    for n in (8, 16):
        (tmp_path / "llm" / f"x-ctx{n}" / "saida-01.jsonl").write_text("".join(json.dumps(r) + "\n" for r in respostas), encoding="utf-8")
        monkeypatch.setattr(avaliar, "pontuar", lambda p, consulta, resposta, n=n: vistas.setdefault(n, {}).setdefault(p["id"], resposta) and {})
        monkeypatch.setattr(avaliar, "guardar", lambda nome, configuracao, linhas: {})
        monkeypatch.setattr(avaliar, "tabela", lambda resumo: "")
        sem_pesquisa = _PesquisaFalsa()
        passo_llm.importar(f"x-ctx{n}", {"composta"}, 1.0, None, {}, n=n, consultas=consultas, pesquisa=sem_pesquisa)
        assert sem_pesquisa.chamadas == []  # usa as consultas do exportar
    assert vistas[16]["cmp-1"].responde and vistas[16]["cmp-1"].citacoes[0].numero == "12.º"
    assert not vistas[8]["cmp-1"].responde  # [12] não está nos 8 que o LLM viu
    assert vistas[8]["cmp-2"].responde and vistas[16]["cmp-2"].responde
