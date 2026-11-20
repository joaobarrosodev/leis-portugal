"""rag.modelos.Reranker: com `estavel`, a nota de um texto não depende dos outros textos do lote.

O modelo verdadeiro não está no CI: um modelo falso imita a quantização dinâmica do int8, em que
a escala sai do lote inteiro e por isso a nota de um texto muda com os vizinhos."""

from rag.modelos import Reranker


class ModeloFalso:
    def __init__(self):
        self.chamadas = 0

    def rerank(self, pergunta, textos, batch_size):
        for i in range(0, len(textos), batch_size):
            lote = textos[i : i + batch_size]
            escala = max(len(t) for t in lote)  # depende do lote, como a quantização dinâmica
            for t in lote:
                self.chamadas += 1
                yield len(t) / escala + (1.0 if "prazo" in t else 0.0)


def _reranker(estavel: bool) -> Reranker:
    r = Reranker.__new__(Reranker)  # sem carregar o modelo verdadeiro
    r.tipo, r.maximo, r.estavel, r.notas = "cruzado", 30, estavel, {}
    r.modelo = ModeloFalso()
    return r


TEXTOS = ["o prazo é de 30 dias", "curto", "um texto bastante mais comprido do que os outros todos"]


def test_por_omissao_a_nota_depende_dos_vizinhos():
    r = _reranker(False)
    sozinho = r.pontuar("prazo?", TEXTOS[:1])[0]
    com_vizinhos = r.pontuar("prazo?", TEXTOS)[0]
    assert sozinho != com_vizinhos


def test_estavel_da_a_mesma_nota_com_ou_sem_vizinhos():
    r = _reranker(True)
    sozinho = r.pontuar("prazo?", TEXTOS[:1])[0]
    r.notas.clear()
    com_vizinhos = r.pontuar("prazo?", TEXTOS)
    assert com_vizinhos[0] == sozinho
    assert r.pontuar("prazo?", list(reversed(TEXTOS))) == list(reversed(com_vizinhos))


def test_estavel_reutiliza_as_notas_ja_calculadas():
    r = _reranker(True)
    r.pontuar("prazo?", TEXTOS)
    antes = r.modelo.chamadas
    r.pontuar("prazo?", [TEXTOS[2], TEXTOS[0], TEXTOS[0]])
    assert r.modelo.chamadas == antes
    r.pontuar("outra pergunta?", TEXTOS[:1])
    assert r.modelo.chamadas == antes + 1


# --- passagens: um artigo comprido vale pela melhor passagem, não só pelo início


from rag.modelos import CARACTERES, passagens_do_artigo  # noqa: E402


class ModeloPalavras:
    """Dá 5 a um texto com «prazo», 1 a um com «recurso» e 0 aos outros; guarda os textos que leu."""

    def __init__(self):
        self.lidos = []

    def rerank(self, pergunta, textos, batch_size):
        for t in textos:
            self.lidos.append(t)
            yield 5.0 if "prazo" in t else 1.0 if "recurso" in t else 0.0


def _por_passagens(estavel: bool = False, artigo: int = 4, pergunta: int = 40) -> Reranker:
    r = _reranker(estavel)
    r.modelo = ModeloPalavras()
    r.passagens, r.passagens_artigo, r.passagens_pergunta = True, artigo, pergunta
    return r


def _numero(n: int, texto: str = "regra sobre licenças e alvarás", vezes: int = 13) -> str:
    return f"{n} - " + " ".join([texto] * vezes) + "."  # cerca de 400 caracteres


COMPRIDO = "\n\n".join([*(_numero(n) for n in range(1, 6)), "6 - O prazo do recurso é de 30 dias."])
CABECALHO = "Lei n.º 1/2020 › Artigo 1.º — Licenças"


def test_artigo_que_cabe_nao_tem_passagens():
    assert passagens_do_artigo("1 - Curto.\n\n2 - Também.", 1000) == []


def test_passagens_partem_pelos_numeros_e_deixam_de_fora_o_que_ja_se_le():
    partes = passagens_do_artigo(COMPRIDO, 1000)
    assert all(len(p) <= 1000 for p in partes)
    # Os números 1 e 2 leem-se inteiros nos primeiros 1000 caracteres; o 3 já não.
    assert partes[0].startswith("3 - ")
    junto = "\n\n".join(partes)
    assert "1 - regra" not in junto and "2 - regra" not in junto
    assert all(f"{n} - " in junto for n in (3, 4, 5, 6))
    assert "O prazo do recurso é de 30 dias." in partes[-1]


def test_numero_comprido_parte_pelas_alineas_e_repete_o_corpo():
    alineas = [f"{letra}) " + "prestações de serviços e transmissões de bens conexas " * 5 for letra in "abcdefghij"]
    partes = passagens_do_artigo("\n\n".join(["1 - Estão isentas do imposto:", *alineas]), 1000)
    assert len(partes) > 1
    assert all(p.startswith("1 - Estão isentas do imposto:\n\n") and len(p) <= 1000 for p in partes)
    assert "j) " in partes[-1]


def test_paragrafo_maior_do_que_a_passagem_e_cortado_em_fatias():
    partes = passagens_do_artigo("palavra " * 500, 1000)
    assert len(partes) >= 3 and all(len(p) <= 1000 for p in partes)


def test_sem_passagens_pontuar_artigos_e_o_pontuar_de_sempre():
    r = _por_passagens()
    r.passagens = False
    assert r.pontuar_artigos("prazo do recurso?", [(CABECALHO, COMPRIDO)]) == [(0.0, None)]
    assert r.modelo.lidos == [f"{CABECALHO}\n{COMPRIDO}"[:CARACTERES]]


def test_com_passagens_o_artigo_fica_com_a_nota_da_melhor_passagem():
    r = _por_passagens()
    curto = ("Lei n.º 1/2020 › Artigo 2.º", "O recurso é apresentado por escrito.")
    (nota, passagem), (nota_curto, passagem_curto) = r.pontuar_artigos("prazo do recurso?", [(CABECALHO, COMPRIDO), curto])
    assert nota == 5.0 and "O prazo do recurso é de 30 dias." in passagem
    assert (nota_curto, passagem_curto) == (1.0, None)  # um artigo curto fica como estava
    # O início do artigo é lido como sempre, e cada passagem leva o cabeçalho à frente.
    assert r.modelo.lidos[0] == f"{CABECALHO}\n{COMPRIDO}"[:CARACTERES]
    assert all(t.startswith(CABECALHO + "\n") for t in r.modelo.lidos if "Artigo 1.º" in t)


def test_a_nota_do_artigo_nunca_desce_por_causa_das_passagens():
    r = _por_passagens()
    inicio_bom = "\n\n".join(["1 - O prazo é de 10 dias.", *(_numero(n) for n in range(2, 8))])
    assert r.pontuar_artigos("prazo?", [(CABECALHO, inicio_bom)]) == [(5.0, None)]


def test_tetos_de_passagens_por_artigo_e_por_pergunta():
    artigos = [(CABECALHO, COMPRIDO), ("Lei n.º 2/2020 › Artigo 1.º", COMPRIDO)]
    r = _por_passagens(artigo=2)  # o início e mais uma passagem de cada artigo
    r.pontuar_artigos("prazo do recurso?", artigos)
    assert len(r.modelo.lidos) == 4
    r = _por_passagens(pergunta=1)  # uma passagem a mais em toda a pergunta
    notas = r.pontuar_artigos("prazo do recurso?", artigos)
    assert len(r.modelo.lidos) == 3
    # A passagem escolhida é a que partilha mais termos com a pergunta: a do n.º 6, do primeiro artigo.
    assert [n for n, _ in notas] == [5.0, 0.0]


def test_passagens_com_estavel_so_pontuam_o_que_falta():
    r = _por_passagens(estavel=True)
    r.passagens = False
    antes = r.pontuar_artigos("prazo do recurso?", [(CABECALHO, COMPRIDO)])
    assert len(r.modelo.lidos) == 1
    r.passagens = True
    depois = r.pontuar_artigos("prazo do recurso?", [(CABECALHO, COMPRIDO)])
    assert antes == [(0.0, None)] and depois[0][0] == 5.0
    assert r.modelo.lidos[0] not in r.modelo.lidos[1:]  # o início não volta a ser pontuado
    lidos = len(r.modelo.lidos)
    r.pontuar_artigos("prazo do recurso?", [(CABECALHO, COMPRIDO)])
    assert len(r.modelo.lidos) == lidos


def test_pesquisa_ordena_pela_melhor_passagem_e_le_as_perguntas_em_cada_uma(tmp_path):
    import sqlite3

    from rag.indice import juntar_perguntas
    from rag.pesquisa import Pesquisa

    from test_dados import ENCHIMENTO, _construir

    indice = _construir(tmp_path / "i.sqlite", {
        "pt:a01": ("Lei n.º 1/2020", "licenças", [
            ("", "1.º", "Licenças", COMPRIDO, "2020-01-01", None),
            ("", "2.º", "Forma", "O recurso é apresentado por escrito.", "2020-01-01", None),
        ], []),
        **ENCHIMENTO,
    })
    with sqlite3.connect(indice) as con:
        juntar_perguntas(con, {("pt:a01", "1.º"): ["Até quando posso reclamar?"]})

    # Sem passagens (como hoje): o reranker só lê o início do artigo 1.º e o 2.º fica à frente.
    simples = _por_passagens()
    simples.passagens = False
    primeiro = Pesquisa(indice, reranker=simples).pesquisar("prazo do recurso da licença", "2026-01-01").resultados[0]
    assert (primeiro.chave, primeiro.passagem) == ("2.º", None)

    r = _por_passagens()
    primeiro = Pesquisa(indice, reranker=r, reranker_com_perguntas=True).pesquisar("prazo do recurso da licença", "2026-01-01").resultados[0]
    assert primeiro.chave == "1.º" and primeiro.reranker == 5.0
    assert "O prazo do recurso é de 30 dias." in primeiro.passagem
    # Com `reranker_com_perguntas`, as perguntas do artigo vão no cabeçalho de todas as passagens dele.
    do_artigo = [t for t in r.modelo.lidos if "Artigo 1.º" in t and t.startswith("Lei n.º 1/2020")]
    assert len(do_artigo) > 1 and all("\nPerguntas: Até quando posso reclamar?\n" in t for t in do_artigo)
