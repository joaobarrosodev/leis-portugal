"""Gralhas na numeração dos títulos de artigo (`domain/numbering.py`) e a correção na recolha do DRE."""

from __future__ import annotations

from typing import Any

from leis_portugal.domain.articles import parse_articles
from leis_portugal.domain.numbering import find_number_fixes, fix_article_numbers
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.sources.dre.client import DreClient
from leis_portugal.sources.dre.source import DreSource
from test_dre_source import REF, FakeSession, _fixture


def _texto(*titulos: str) -> str:
    return "# Diploma\n\n" + "\n\n".join(f"###### {titulo}\n\nTexto." for titulo in titulos)


def _artigos(numeros, epigrafe: bool = True) -> list[str]:
    return [f"Artigo {n}.º — Epígrafe {n}" if epigrafe else f"Artigo {n}.º" for n in numeros]


def test_corrige_a_gralha_isolada_e_guarda_o_numero_da_fonte():
    # DRR 2/2005/M: o DRE escreve «Artigo 212.º» entre o 20.º e o 22.º.
    texto = _texto(*_artigos([19, 20]), "Artigo 212.º — Atribuições e competências", *_artigos([22, 23]))
    corrigido, notas = fix_article_numbers(texto)
    assert "###### Artigo 21.º — Atribuições e competências" in corrigido
    assert "212.º" not in corrigido
    assert notas == [
        "Numeração corrigida: o DRE escreve «Artigo 212.º» entre os artigos 20.º e 22.º; usado o 21.º."
    ]
    assert [a.key for a in parse_articles(corrigido)] == ["art-19", "art-20", "art-21", "art-22", "art-23"]
    # Correr outra vez não muda nada.
    assert fix_article_numbers(corrigido) == (corrigido, [])


def test_mantem_o_formato_do_numero():
    texto = _texto("Artigo 3.º", "Artigo 4.º", "Artigo 2º", "Artigo 6.º", "Artigo 7.º")
    corrigido, _ = fix_article_numbers(texto)
    assert "###### Artigo 5º\n" in corrigido


def test_no_extremo_da_parte_basta_um_lado():
    # Aviso n.º 39/2007: 7.º, 8.º, 22.º, 10.º e acaba.
    corrigido, _ = fix_article_numbers(_texto(*_artigos([7, 8, 22, 10], epigrafe=False)))
    assert "Artigo 9.º" in corrigido
    # Só com os vizinhos imediatos não chega (Acórdão n.º 431/94: 78.º, 388.º, 80.º do Código Penal).
    assert find_number_fixes(_texto(*_artigos([78, 388, 80]))) == []


def test_artigos_citados_de_outros_diplomas_nao_se_corrigem():
    # Lei n.º 30-C/92: o 10.º do CIRS entre os artigos 23.º e 25.º da própria lei, que saltam números.
    texto = _texto(*_artigos([22, 23]), "Artigo 10.º — Rendimentos da categoria G", *_artigos([25, 51]))
    assert find_number_fixes(texto) == []


def test_artigo_do_ato_de_alteracao_entre_artigos_citados():
    # Edital n.º 643/2003: o «Artigo 2.º» do edital, sem epígrafe, entre artigos citados que a têm.
    assert find_number_fixes(_texto(*_artigos([23, 24, 25]), "Artigo 2.º", *_artigos([27, 28]))) == []
    # Regulamento n.º 1135/2024: o artigo do ato que adita tem epígrafe, mas é de um ato de alteração.
    texto = _texto(*_artigos([39, 40, 41]), "Artigo 2.º — Aditamentos ao Regulamento", *_artigos([43, 44]))
    assert find_number_fixes(texto) == []


def test_titulo_repetido_igual_no_registo_fica_como_esta():
    # Edital n.º 969/2011: «Artigo 7.º — Cérceas» aparece duas vezes, sempre com o mesmo número.
    texto = _texto(
        *_artigos([15, 16]), "Artigo 7.º — Cérceas", *_artigos([18, 19]),
        "Artigo 7.º — Cérceas",
    )
    assert find_number_fixes(texto) == []


def test_numero_que_ja_existe_na_parte_nao_se_usa():
    texto = _texto(*_artigos([20, 21]), "Artigo 22.º — Outra", *_artigos([5, 23, 24]))
    assert find_number_fixes(texto) == []
    # Num anexo a numeração recomeça: o 21.º do diploma não conta para o anexo.
    texto = _texto(*_artigos([20, 21])) + "\n\n## ANEXO I\n\n" + _texto(*_artigos([19, 20]), "Artigo 212.º", *_artigos([22, 23]))
    texto = texto.replace("Artigo 212.º", "Artigo 212.º — Epígrafe")
    assert [f.fixed for f in find_number_fixes(texto)] == [21]


def test_repetidos_so_com_a_opcao():
    texto = _texto(*_artigos([20, 21]), "Artigo 23.º — Dever de sigilo", *_artigos([23, 24]))
    assert find_number_fixes(texto) == []
    [fix] = find_number_fixes(texto, repeated=True)
    assert (fix.written, fix.fixed, fix.repeated) == (23, 22, True)


class _SessaoComGralha(FakeSession):
    def call(self, action: str, variables: dict[str, Any]) -> dict[str, Any]:
        if action != "published_detail":
            return super().call(action, variables)
        detail = _fixture("detail_decreto_lei.json")
        titulos = [(1, "Objeto"), (2, "Âmbito"), (93, "Requisitos"), (4, "Prazos"), (5, "Entrada em vigor")]
        detail["TextoFormatado"] = "".join(
            f'<p class="paragraph-bold-center-14px">Artigo {n}.º</p>'
            f'<p class="paragraph-bold-center-14px">{epigrafe}</p><p class="paragraph-normal-text">Texto.</p>'
            for n, epigrafe in titulos
        )
        return {"DetalheConteudo": detail}


def test_a_recolha_do_dre_corrige_e_anota(repo_root):
    acervo = Acervo(repo_root)
    document = DreSource(acervo.types, DreClient(_SessaoComGralha())).collect(REF)
    assert "###### Artigo 3.º — Requisitos" in document.body
    assert "Artigo 93.º" not in document.body
    assert document.record.notes[-1] == (
        "Numeração corrigida: o DRE escreve «Artigo 93.º» entre os artigos 2.º e 4.º; usado o 3.º."
    )
