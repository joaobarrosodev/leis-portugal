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
