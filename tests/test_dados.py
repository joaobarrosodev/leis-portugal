"""Publicar o índice (versão completa e deltas) e descarregá-lo como a aplicação faz (rag.dados), sem rede."""

import json
import shutil
import sqlite3

import pytest
from rag import dados
from rag import texto as termos_mod
from rag.indice import ESQUEMA, textos_fts
from rag.pesquisa import Pesquisa


def _construir(caminho, documentos):
    """Um índice com o esquema verdadeiro, construído de raiz como `rag.indice.construir`.

    `documentos`: {id: (titulo, sumario, [(parte, numero, epigrafe, texto, desde, ate)], [(tipo, alvo)])}."""
    caminho.unlink(missing_ok=True)
    con = sqlite3.connect(caminho)
    con.executescript(ESQUEMA)
    proximo = 1
    for id_, (titulo, sumario, pedacos, relacoes) in documentos.items():
        con.execute("INSERT INTO documentos VALUES (?, ?, 'lei', ?, '2020-01-01', ?, 'in_force', 'original', NULL, ?, 0)", (id_, titulo, id_[-3:], sumario, f"data/{id_}.md"))
        con.executemany("INSERT INTO relacoes VALUES (?, ?, ?, ?, NULL)", [(id_, t, a, a) for t, a in relacoes])
        for ordem, (parte, numero, epigrafe, texto, desde, ate) in enumerate(pedacos):
            con.execute(
                "INSERT INTO pedacos VALUES (?, ?, ?, ?, ?, ?, ?, ?, '', ?, ?, ?)",
                (proximo, id_, parte, numero, epigrafe, numero, f"{titulo} › Artigo {numero}", texto, desde, ate, ordem),
            )
            con.execute("INSERT INTO pedacos_fts (rowid, cabecalho, texto) VALUES (?, ?, ?)", (proximo, *textos_fts(titulo, sumario, parte, epigrafe, texto)))
            proximo += 1
    con.executemany("INSERT INTO meta VALUES (?, ?)", [("metodo_termos", termos_mod.METODO), ("construido", "2026-11-01"), ("export", "/Users/alguem/export.sqlite")])
    con.execute("INSERT INTO pedacos_fts (pedacos_fts) VALUES ('optimize')")
    con.commit()
    con.close()
    return caminho


def _artigos(n, palavra, extra=""):
    return [("", f"{i}.º", f"Epígrafe {palavra} {i}", f"O {palavra} tem o prazo de {i} dias para a coima {extra}", "2020-01-01", None) for i in range(1, n + 1)]


# Diplomas de enchimento: sem eles, os termos dos outros apareceriam em mais de 20% dos pedaços e a
# pesquisa (`Pesquisa._consulta_fts`) ignorava-os.
ENCHIMENTO = {f"pt:f{i:02d}": (f"Portaria {i}", f"Matéria avulsa {i}", [("", "1.º", "", f"Texto avulso número{i} sobre pescas{i} e florestas{i}", "2020-01-01", None)] * 3, []) for i in range(40)}

A = {
    **ENCHIMENTO,
    "pt:a": ("Lei das coimas", "Regime das coimas", _artigos(5, "arguido"), [("amended_by", "pt:x")]),
    "pt:b": ("Lei das férias", "Férias dos trabalhadores", _artigos(4, "trabalhador"), []),
    "pt:c": ("Lei do arrendamento", "Arrendamento urbano", _artigos(6, "senhorio"), [("repealed_by", "pt:y")]),
}
B = {
    **ENCHIMENTO,
    "pt:a": ("Lei das coimas", "Regime das coimas", _artigos(5, "arguido", "alterado"), [("amended_by", "pt:x"), ("amended_by", "pt:z")]),
    "pt:c": A["pt:c"],
    "pt:d": ("Lei nova das coimas", "Coimas rodoviárias", _artigos(3, "condutor"), []),
}


def _conteudo(caminho):
    with sqlite3.connect(caminho) as con:
        return (
            sorted(con.execute("SELECT * FROM documentos")),
            sorted(con.execute(f"SELECT {dados._COLUNAS_PEDACO} FROM pedacos")),
            sorted(con.execute("SELECT * FROM relacoes")),
        )


def _bm25(caminho, pergunta):
    p = Pesquisa(caminho)
    linhas = p.bm25(pergunta, "2026-11-13", limite=50)
    ids = {i: (d, c) for i, d, c in p.con.execute("SELECT id, documento, chave FROM pedacos")}
    return sorted((ids[i], round(s, 9)) for i, s in linhas)


def test_delta_da_o_mesmo_indice_que_construir_de_raiz(tmp_path):
    antigo, novo = _construir(tmp_path / "a.sqlite", A), _construir(tmp_path / "b.sqlite", B)
    contagem = dados.gerar_delta(antigo, novo, tmp_path / "delta.sqlite", "2026-11-01", "2026-11-08")
    assert contagem == {"mudados": 2, "removidos": 1}  # pt:a alterado, pt:d novo; pt:b saiu; pt:c e o enchimento iguais
    aplicado = tmp_path / "aplicado.sqlite"
    shutil.copyfile(antigo, aplicado)
    dados.aplicar_delta(aplicado, tmp_path / "delta.sqlite")
    assert _conteudo(aplicado) == _conteudo(novo)
    for pergunta in ("prazo da coima do arguido", "senhorio arrendamento", "condutor coimas rodoviárias", "alterado", "pescas3 florestas7"):
        resultado = _bm25(novo, pergunta)
        assert resultado, pergunta  # a pergunta encontra alguma coisa: a comparação não é vazia
        assert _bm25(aplicado, pergunta) == resultado, pergunta
    with sqlite3.connect(aplicado) as con:
        # os pedaços de cada diploma continuam com ids seguidos (a pesquisa por diploma usa min/max do id)
        for doc, minimo, maximo, n in con.execute("SELECT documento, min(id), max(id), count(*) FROM pedacos GROUP BY documento"):
            assert maximo - minimo + 1 == n, doc
        assert dict(con.execute("SELECT chave, valor FROM meta"))["versao"] == "2026-11-08"


def test_delta_com_outros_termos_e_recusado(tmp_path):
    antigo, novo = _construir(tmp_path / "a.sqlite", A), _construir(tmp_path / "b.sqlite", B)
    with sqlite3.connect(novo) as con:
        con.execute("UPDATE meta SET valor = 'outro' WHERE chave = 'metodo_termos'")
    with pytest.raises(RuntimeError, match="termos diferentes"):
        dados.gerar_delta(antigo, novo, tmp_path / "d.sqlite", "1", "2")


def test_falha_a_meio_deixa_o_indice_como_estava(tmp_path, monkeypatch):
    antigo, novo = _construir(tmp_path / "a.sqlite", A), _construir(tmp_path / "b.sqlite", B)
    dados.gerar_delta(antigo, novo, tmp_path / "delta.sqlite", "1", "2")
    shutil.copyfile(antigo, tmp_path / "copia.sqlite")
    antes = _conteudo(antigo)
    chamadas = {"n": 0}
    original = textos_fts

    def falha(*a):
        chamadas["n"] += 1
        if chamadas["n"] > 8:
            raise OSError("disco cheio")
        return original(*a)

    monkeypatch.setattr("rag.indice.textos_fts", falha)
    with pytest.raises(OSError):
        dados.aplicar_delta(antigo, tmp_path / "delta.sqlite")
    assert _conteudo(antigo) == antes
    assert _bm25(antigo, "férias do trabalhador") and _bm25(antigo, "férias do trabalhador") == _bm25(tmp_path / "copia.sqlite", "férias do trabalhador")


# ------------------------------------------------------------------------------ publicar e descarregar


class _Resposta:
    def __init__(self, corpo: bytes, estado: int):
        self.corpo, self.status_code = corpo, estado

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)

    def iter_content(self, tamanho):
        for i in range(0, len(self.corpo), 1000):
            yield self.corpo[i : i + 1000]

    def json(self):
        return json.loads(self.corpo)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


@pytest.fixture
def alojamento(tmp_path, monkeypatch):
    """Publica em tmp_path/pub e serve esses ficheiros a um `requests.get` falso (com Range)."""
    pub = tmp_path / "pub"
    pedidos = []

    def get(url, headers=None, stream=False, timeout=None):
        ficheiro = pub / url.rsplit("/", 1)[1]
        if not ficheiro.exists():
            return _Resposta(b"", 404)
        corpo = ficheiro.read_bytes()
        pedidos.append((ficheiro.name, headers or {}))
        if headers and "Range" in headers:
            return _Resposta(corpo[int(headers["Range"].split("=")[1].rstrip("-")) :], 206)
        return _Resposta(corpo, 200)

    import requests

    monkeypatch.setattr(requests, "get", get)
    monkeypatch.setenv("RAG_DADOS_URL", "https://exemplo.pt/d/versao.json")
    return pub, pedidos


def _publicar(tmp_path, documentos, versao, **k):
    k.setdefault("remoto", False)
    return dados.publicar(_construir(tmp_path / f"i-{versao}.sqlite", documentos), tmp_path / "pub", versao, url_base="https://exemplo.pt/d/", **k)


def test_publicar_noutra_pasta_reconstroi_a_base_a_partir_do_alojamento(tmp_path, alojamento):
    pub, pedidos = alojamento
    _publicar(tmp_path, A, "2026-11-01")
    (pub / "publicado.sqlite").unlink()  # outra pasta ou outro computador: sem a base local
    manifesto, enviar = _publicar(tmp_path, B, "2026-11-08", limite=10, remoto=True)
    assert "completo-2026-11-01.sqlite.gz" in [n for n, _ in pedidos]  # descarregou a completa para refazer a base
    assert [d["para"] for d in manifesto["deltas"]] == ["2026-11-08"]
    app = tmp_path / "app"
    dados.descarregar(app)
    assert _conteudo(app / "indice.sqlite") == _conteudo(tmp_path / "i-2026-11-08.sqlite")


def test_primeira_publicacao_e_completa_e_sem_o_caminho_local(tmp_path, alojamento):
    manifesto, enviar = _publicar(tmp_path, A, "2026-11-01")
    assert manifesto["completo"]["versao"] == "2026-11-01" and manifesto["deltas"] == [] and manifesto["anterior"] is None
    assert [f.name for f in enviar] == ["completo-2026-11-01.sqlite.gz", "versao.json"]
    with sqlite3.connect(tmp_path / "pub" / "publicado.sqlite") as con:
        meta = dict(con.execute("SELECT chave, valor FROM meta"))
    assert "export" not in meta and meta["versao"] == "2026-11-01"


def test_depois_vem_um_delta_e_a_app_so_descarrega_o_delta(tmp_path, alojamento):
    pub, pedidos = alojamento
    _publicar(tmp_path, A, "2026-11-01")
    app = tmp_path / "app"
    dados.descarregar(app)
    assert dados.versao_local(app)["versao"] == "2026-11-01"
    manifesto, enviar = _publicar(tmp_path, B, "2026-11-08", limite=10)  # índices pequenos: o delta é grande em proporção
    assert [d["para"] for d in manifesto["deltas"]] == ["2026-11-08"] and manifesto["completo"]["versao"] == "2026-11-01"
    pedidos.clear()
    progresso = dados.Progresso()
    dados.descarregar(app, progresso)
    assert [n for n, _ in pedidos if n.endswith(".gz")] == ["delta-2026-11-01-2026-11-08.sqlite.gz"]
    assert progresso.fase == "pronto" and dados.versao_local(app)["versao"] == "2026-11-08"
    assert _conteudo(app / "indice.sqlite")[1] == _conteudo(tmp_path / "pub" / "publicado.sqlite")[1]


def test_app_nova_descarrega_a_completa_e_os_deltas(tmp_path, alojamento):
    pub, pedidos = alojamento
    _publicar(tmp_path, A, "2026-11-01")
    _publicar(tmp_path, B, "2026-11-08", limite=10)
    app = tmp_path / "app"
    dados.descarregar(app)
    assert [n for n, _ in pedidos if n.endswith(".gz")] == ["completo-2026-11-01.sqlite.gz", "delta-2026-11-01-2026-11-08.sqlite.gz"]
    assert _conteudo(app / "indice.sqlite")[1] == _conteudo(tmp_path / "pub" / "publicado.sqlite")[1]


def test_delta_grande_passa_a_completa_e_guarda_a_anterior(tmp_path, alojamento):
    _publicar(tmp_path, A, "2026-11-01")
    manifesto, enviar = _publicar(tmp_path, B, "2026-11-08", limite=0.0001)
    assert manifesto["completo"]["versao"] == "2026-11-08" and manifesto["deltas"] == []
    assert manifesto["anterior"]["nome"] == "completo-2026-11-01.sqlite.gz"
    assert dados.nomes_a_manter(manifesto) == {"versao.json", "README.md", ".gitattributes", "completo-2026-11-08.sqlite.gz", "completo-2026-11-01.sqlite.gz"}


def test_plano():
    m = {"versao": "3", "completo": {"versao": "1"}, "deltas": [{"para": "2"}, {"para": "3"}]}
    assert dados.plano(m, "3") == (False, [])
    assert dados.plano(m, "1") == (False, m["deltas"])
    assert dados.plano(m, "2") == (False, m["deltas"][1:])
    assert dados.plano(m, None) == (True, m["deltas"])
    assert dados.plano(m, "0") == (True, m["deltas"])


def test_retoma_e_corrompido(tmp_path, alojamento):
    pub, pedidos = alojamento
    manifesto, _ = _publicar(tmp_path, A, "2026-11-01")
    app = tmp_path / "app"
    app.mkdir()
    c = manifesto["completo"]
    (app / (c["nome"] + ".parte")).write_bytes((pub / c["nome"]).read_bytes()[: c["bytes"] // 2])
    dados.descarregar(app)
    assert pedidos[-1][1] == {"Range": f"bytes={c['bytes'] // 2}-"}
    estragado = json.loads(json.dumps(manifesto))
    estragado["versao"] = estragado["completo"]["versao"] = "2026-12-01"
    estragado["completo"]["sha256"] = "0" * 64
    (app / "indice.sqlite").write_bytes(b"antigo")
    with pytest.raises(RuntimeError, match="corrompido"):
        dados.descarregar(app, manifesto=estragado)
    assert (app / "indice.sqlite").read_bytes() == b"antigo"


def test_sem_publicacao_diz_que_ainda_nao_foi_publicado(tmp_path, alojamento):
    with pytest.raises(RuntimeError, match="ainda não foi publicado"):
        dados.ler_manifesto()


def test_enviar_manda_os_ficheiros_antes_do_manifesto_e_limpa(tmp_path, alojamento):
    _publicar(tmp_path, A, "2026-11-01")
    manifesto, enviar = _publicar(tmp_path, B, "2026-11-08", limite=0.0001)

    class Api:
        chamadas = []

        def list_repo_files(self, repo, repo_type):
            return [".gitattributes", "versao.json", "completo-2026-10-01.sqlite.gz", "completo-2026-11-01.sqlite.gz", "delta-2026-10-01-2026-10-08.sqlite.gz"]

        def create_commit(self, repo, repo_type, operations, commit_message):
            self.chamadas.append(("commit", sorted(o.path_in_repo for o in operations)))

        def upload_file(self, path_or_fileobj, path_in_repo, repo_id, repo_type, commit_message):
            self.chamadas.append(("upload", path_in_repo))

        def super_squash_history(self, repo, repo_type, commit_message):
            self.chamadas.append(("squash",))

    cartao = tmp_path / "README.md"
    cartao.write_text("cartão")
    apagados = dados.enviar_hf(manifesto, enviar, cartao=cartao, api=Api())
    assert apagados == ["completo-2026-10-01.sqlite.gz", "delta-2026-10-01-2026-10-08.sqlite.gz"]
    assert Api.chamadas == [
        ("commit", ["README.md", "completo-2026-11-08.sqlite.gz"]),
        ("upload", "versao.json"),
        ("commit", apagados),
        ("squash",),
    ]
