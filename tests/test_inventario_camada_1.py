"""Inventário da camada 1 (`scripts/inventario_camada_1.py`): leitura das partes, obras em vários registos e classes."""

import json
import sqlite3
import sys
from pathlib import Path

import pytest


PASTA = Path(__file__).resolve().parents[1] / "scripts"
if not (PASTA / "inventario_camada_1.py").exists():
    pytest.skip("scripts/ não está nesta cópia", allow_module_level=True)
sys.path.insert(0, str(PASTA))

import inventario_camada_1 as inv  # noqa: E402


CONSOLIDADO = """---
id: pt:dre:2:por
---

# Lei n.º 72/2013

###### Artigo 1.º — Objeto

Altera o Código da Estrada.

###### Artigo 2.º — Republicação

É republicado em anexo.

## Anexo — CÓDIGO DA ESTRADA

## Título I — Disposições gerais

###### Artigo 1.º — Definições legais

Texto.

> Alterado pelo/a Artigo 2.º do/a [Lei n.º 116/2015 - Diário da República n.º 168/2015, Série I de 2015-08-28](https://exemplo), em vigor a partir de 2016-06-01

###### Artigo 2.º — Âmbito de aplicação

Texto.

> Alterado pelo/a Artigo 3.º do/a [Lei n.º 24/2025 - Diário da República n.º 50/2025, Série I de 2025-03-12](https://exemplo), em vigor a partir de 2025-04-11

###### Artigo 2.º-A — Aditado

Texto.
"""


def test_partes_separa_o_diploma_do_anexo_e_le_a_ultima_nota():
    lidas = inv.ler_partes(CONSOLIDADO)
    assert set(lidas) == {"", "Anexo — CÓDIGO DA ESTRADA"}
    assert lidas[""].artigos == {"1.º": "Objeto", "2.º": "Republicação"}
    anexo = lidas["Anexo — CÓDIGO DA ESTRADA"]
    assert list(anexo.artigos) == ["1.º", "2.º", "2.º-A"]
    assert anexo.ultima_nota == "2025-04-11"
    assert lidas[""].ultima_nota is None


def test_uma_alteracao_com_entrada_em_vigor_futura_nao_conta():
    assert inv.ler_partes(CONSOLIDADO, hoje="2025-01-01")["Anexo — CÓDIGO DA ESTRADA"].ultima_nota == "2016-06-01"


def test_texto_corrido_abre_outra_parte_quando_a_numeracao_recomeca():
    corrido = "Artigo 1.º É aprovado o Código.\n\nArt. 2.º Entra em vigor.\n\nArtigo 1.º Estão sujeitas a imposto:\n\nArtigo 2.º São sujeitos passivos:\n\nArtigo 3.º Considera-se transmissão."
    assert {p: list(a) for p, a in inv.partes(corrido).items()} == {"": ["1.º", "2.º"], "(2.ª numeração)": ["1.º", "2.º", "3.º"]}


def test_sobreposicao_conta_numeros_e_epigrafes():
    medida = inv.sobreposicao({"1.º": "Âmbito", "2.º": "Definições", "3.º": "Sinais"}, {"1.º": "ÂMBITO", "2.º": "Liberdade de trânsito", "9.º": "x"})
    assert (medida["comuns"], medida["com_epigrafe"], medida["epigrafes_iguais"]) == (2, 2, 1)
    assert medida["fracao_numeros"] == round(2 / 3, 3)


def test_referencias_na_forma_dos_titulos():
    nota = 'do Código Penal, aprovado pelo <a href="x"> Decreto-Lei n.º 400/82, de 23 de setembro</a>, e da Lei 72/2013 e do Decreto-Lei n.º 47344'
    assert inv.referencias(nota) == ["Decreto-Lei n.º 400/82", "Lei n.º 72/2013", "Decreto-Lei n.º 47344"]


def test_aprovados_nas_notas_so_le_notas_de_republicacao():
    notas = [
        'Versão consolidada. Tem por base a republicação, em anexo ao presente Decreto-Lei, do Código Penal, aprovado pelo  <a href="x"> Decreto-Lei n.º 400/82, de 23 de setembro</a>',
        "O presente diploma encontra-se revogado pelo Decreto-Lei n.º 43-B/2024, aprovado pelo Decreto-Lei n.º 1/2024.",
    ]
    assert inv.aprovados_nas_notas(notas) == ["Decreto-Lei n.º 400/82"]


def test_mesma_obra():
    iguais = {"comuns": 100, "com_epigrafe": 100, "epigrafes_iguais": 90, "fracao_numeros": 1.0, "fracao_epigrafes": 0.9}
    renumerado = iguais | {"epigrafes_iguais": 20, "fracao_epigrafes": 0.2}
    sem_epigrafes = iguais | {"com_epigrafe": 0, "epigrafes_iguais": 0, "fracao_epigrafes": None}
    assert inv.mesma_obra(iguais, 100, 100)
    # O Código da Estrada foi renumerado: só a ligação explícita (a nota do DRE) junta o original à republicação.
    assert not inv.mesma_obra(renumerado, 100, 100)
    assert inv.mesma_obra(renumerado, 100, 100, explicito=True)
    # Sem epígrafes (o IVA de 1984 em texto corrido): o nome do anexo no sumário do diploma que este altera.
    assert inv.mesma_obra(sem_epigrafes, 100, 120, nome=1.0, altera=True)
    assert not inv.mesma_obra(sem_epigrafes, 100, 120, nome=1.0, altera=False)
    # O regime que sucedeu a outro com o mesmo nome revoga-o: não é uma cópia.
    assert not inv.mesma_obra(sem_epigrafes, 100, 120, nome=1.0, altera=True, revoga=True)
    assert not inv.mesma_obra(iguais | {"fracao_numeros": 0.3}, 100, 100, explicito=True)


def test_revogacao_inteira_ou_parcial():
    assert inv.revogacao([]) is None
    assert inv.revogacao([(None, None, "Revogado, a partir de 01.01.2020, o art. 3.º do Dec Lei 5/2019")]) == "parcial"
    assert inv.revogacao([(None, None, "Revogado, a partir de 01.01.2020, com exceção do n.º 2 do art. 4.º")]) == "parcial"
    assert inv.revogacao([(None, None, "Revogado, a partir de 01.01.2020, o Dec Lei 5/2019 de 14-jan")]) == "inteira"


def test_classe_desconhecida():
    doc = {"summary": "Estabelece o regime geral de proteção de denunciantes", "publication_date": "2021-12-20"}
    assert inv.classe_desconhecida(doc, None, None, None) == "sem_indicio_de_revogacao"
    assert inv.classe_desconhecida(doc, None, None, "2024-01-10") == "alterado_depois_e_sem_revogacao"
    assert inv.classe_desconhecida(doc, "inteira", None, "2024-01-10") == "revogado_segundo_a_relacao_do_dre"
    assert inv.classe_desconhecida(doc | {"summary": "Procede à terceira alteração ao Decreto-Lei n.º 5/2019"}, None, None, None) == "ato_de_alteracao"
    assert inv.classe_desconhecida(doc | {"summary": "Orçamento do Estado para 2022"}, None, None, None) == "temporario_ou_orcamental"


def test_classe_do_texto():
    doc = {"id": "a", "text_quality": "texto"}
    dre = {"rotulo": "Versão consolidada pelo DRE"}
    nossa = {"rotulo": "Versão consolidada pelo leis-portugal, sem valor oficial: alterações aplicadas por regra e verificadas às cegas"}
    assert inv.classe_do_texto(doc, dre, "a", None) == "consolidado_dre"
    assert inv.classe_do_texto(doc, nossa, "a", None) == "consolidado_leis_portugal"
    assert inv.classe_do_texto(doc, dre, "b", None) == "texto_noutro_registo"
    assert inv.classe_do_texto(doc | {"text_quality": "pdf"}, None, None, None) == "sem_texto"
    assert inv.classe_do_texto(doc, None, None, None) == "nao_triado"
    assert inv.classe_do_texto(doc, None, None, {"estado": "sem alteração textual"}) == "original_e_o_texto_em_vigor"
    assert inv.classe_do_texto(doc, None, None, {"estado": "para LLM"}) == "alteracao_por_aplicar"


SITEMAP = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://diariodarepublica.pt/dr/legislacao-consolidada/lei/2013-1</loc><lastmod>2026-11-16</lastmod></url>
  <url><loc>https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2001-2</loc><lastmod>2026-11-17</lastmod></url>
  <url><loc>https://diariodarepublica.pt/dr/legislacao-consolidada/portaria/2017-3</loc><lastmod>2024-06-25</lastmod></url>
  <url><loc>https://diariodarepublica.pt/dr/detalhe/lei/1-2020-4</loc><lastmod>2024-06-25</lastmod></url>
</urlset>"""


def test_comparar_sitemap():
    sitemap = inv.ler_sitemap(SITEMAP)
    assert len(sitemap) == 3
    base = "https://diariodarepublica.pt/dr/legislacao-consolidada/"
    comparacao = inv.comparar_sitemap(sitemap, {base + "lei/2013-1": {"id": "x", "lastmod": "2024-06-25"}}, {base + "portaria/2017-3"})
    assert (comparacao["listados"], comparacao["temos"]) == (3, 1)
    assert {e["motivo"] for e in comparacao["em_falta"]} == {"por_recolher", "sem_texto_na_fonte"}
    assert [m["id"] for m in comparacao["mexidos_depois_da_recolha"]] == ["x"]


def _registo(raiz: Path, caminho: str, corpo: str, *, consolidado_ate: str | None = None, notas: str = "[]") -> None:
    versao = f"version:\n  kind: consolidated\n  label: Versão consolidada pelo DRE\n  consolidation_date: '{consolidado_ate}'\n" if consolidado_ate else "version:\n  kind: original\n"
    (raiz / caminho).parent.mkdir(parents=True, exist_ok=True)
    (raiz / caminho).write_text(f"---\nnotes: {notas}\n{versao}---\n\n{corpo}", encoding="utf-8")


def _artigos(epigrafes: list[str], nota: str = "") -> str:
    return "\n\n".join(f"###### Artigo {n}.º — {e}\n\nTexto.{nota}" for n, e in enumerate(epigrafes, 1))


def test_obras_junta_o_codigo_as_republicacoes_e_escolhe_a_mais_recente(tmp_path):
    """Um código de 1994 renumerado, republicado em 2005 (consolidado até 2021) e em 2013 (até 2025)."""
    antigas = [f"Tema antigo {n}" for n in range(1, 13)]
    novas = [f"Tema novo {n}" for n in range(1, 13)]
    nota = "\n\n> Alterado pelo/a [Lei n.º 9/2021 - DR de 2020-12-09](https://x), em vigor a partir de {}"
    _registo(tmp_path, "data/dl-114-94.md", _artigos(antigas))
    _registo(tmp_path, "data/dl-44-2005.md", _artigos(novas, nota.format("2021-01-08")), consolidado_ate="2021-01-08")
    _registo(tmp_path, "data/lei-72-2013.md", "###### Artigo 1.º — Objeto\n\nAltera.\n\n## Anexo — CÓDIGO DA ESTRADA\n\n" + _artigos(novas, nota.format("2025-04-11")),
             consolidado_ate="2025-04-11", notas="['Esta versão consolidada tem por base a republicação, em anexo à Lei 72/2013, do Código da Estrada, aprovado pelo Decreto-Lei 114/94, de 3 de maio.']")

    def doc(i, titulo, tipo, data, caminho, versao):
        return {"id": i, "title": titulo, "summary": "Código da Estrada", "document_type": tipo, "publication_date": data, "legal_status": "in_force",
                "text_quality": "texto", "version_kind": versao, "path": caminho, "series": "I"}

    docs = {
        "o": doc("o", "Decreto-Lei n.º 114/94", "decreto-lei", "1994-05-03", "data/dl-114-94.md", "original"),
        "m": doc("m", "Decreto-Lei n.º 44/2005", "decreto-lei", "2005-02-23", "data/dl-44-2005.md", "consolidated"),
        "r": doc("r", "Lei n.º 72/2013", "lei", "2013-09-03", "data/lei-72-2013.md", "consolidated"),
    }
    acervo = inv.Acervo(docs, {}, {}, {"o": "r"}, {"r": {"o", "m"}, "m": {"o"}}, por_titulo={d["title"]: [i] for i, d in docs.items()})
    cabecalhos = {i: inv.cabecalho(tmp_path / docs[i]["path"]) for i in ("m", "r")}
    (obra,) = inv.obras(acervo, cabecalhos, tmp_path, ("lei", "decreto-lei"))
    papeis = {c["id"]: c["papel"] for c in obra["copias"]}
    assert papeis == {"o": "origem", "m": "cópia", "r": "atual"}
    assert (obra["atual_parte"], obra["data_do_texto_atual"], obra["origem_ligada_ao_atual"]) == ("Anexo — CÓDIGO DA ESTRADA", "2025-04-11", True)
    assert obra["epigrafes_iguais"] == 0 and obra["com_epigrafe"] == 12  # a numeração da origem não é a do texto atual
    assert obra["copias_desatualizadas_servidas"] == 2  # o original de 1994 e a republicação de 2005
    assert inv.onde_vive("o", acervo, cabecalhos, [obra])[0] == "r"
    assert inv.onde_vive("m", acervo, cabecalhos, [obra])[0] == "m"  # só a origem é redirecionada


def test_em_dia_ve_os_alteradores_publicados_depois():
    acervo = inv.Acervo({"n": {"title": "Lei n.º 1/2026"}}, {"c": [("v", "2020-01-01", None), ("n", "2026-02-01", None), ("h", "2026-03-01", None)]}, {}, {}, {})
    cab = {"data_consolidacao": "2025-06-01", "alteradores_no_historico": {"h"}, "url_consolidado": "u", "lastmod": "2025-06-02"}
    resultado = inv.em_dia("c", acervo, cab, {"u": "2026-11-01"})
    assert not resultado["em_dia"] and resultado["dre_mexeu_depois_da_recolha"]
    assert [a["id"] for a in resultado["alteradores_posteriores"]] == ["n"]
    assert inv.em_dia("c", acervo, cab | {"data_consolidacao": "2026-02-01"}, {"u": "2025-06-02"})["em_dia"]


def test_lista_de_controlo_resolve_todos_os_titulos_bem_formados():
    centrais = json.loads((PASTA / "inventario_diplomas_centrais.json").read_text(encoding="utf-8"))["diplomas"]
    assert len(centrais) >= 100
    assert all({"area", "nome", "diploma"} <= set(c) for c in centrais)
    assert len({c["diploma"] for c in centrais}) == len(centrais)


def test_export_por_omissao_num_worktree(tmp_path):
    principal = tmp_path / "principal"
    (principal / "exports").mkdir(parents=True)
    sqlite3.connect(principal / "exports" / "leis-portugal.sqlite").close()
    copia = principal / ".claude" / "worktrees" / "x"
    copia.mkdir(parents=True)
    (copia / ".git").write_text(f"gitdir: {principal}/.git/worktrees/x\n", encoding="utf-8")
    assert inv.export_por_omissao(copia) == principal / "exports" / "leis-portugal.sqlite"
