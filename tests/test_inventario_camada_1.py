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


def test_texto_em_vigor_leva_a_marca_da_vigencia_revista():
    docs = {i: {"id": i, "title": f"Decreto-Lei n.º {n}/2001", "summary": "", "document_type": "decreto-lei", "publication_date": "2001-01-01", "legal_status": "in_force",
                "text_quality": "texto", "version_kind": "original", "path": "x.md", "series": "I"} for n, i in enumerate(("a", "b"), 1)}
    acervo = inv.Acervo(docs, {"a": [("z", "2005-01-01", None)], "b": [("z", "2005-01-01", None)]}, {}, {}, {})
    linhas = {l["id"]: l for l in inv.texto_em_vigor(acervo, {}, [], {"a": {"estado": "sem alteração textual"}}, None, ("decreto-lei",), {"a": "nao_vigora"})}
    assert linhas["a"]["marca_de_vigencia"] == "nao_vigora" and linhas["a"]["classe"] == "original_e_o_texto_em_vigor"
    assert "marca_de_vigencia" not in linhas["b"] and linhas["b"]["classe"] == "nao_triado"


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


def test_inventario_de_ponta_a_ponta_num_acervo_minimo(tmp_path):
    """O código de 1994 republicado em 2013, mais um decreto-lei alterado com marca de vigência revista."""
    epigrafes = [f"Tema {n}" for n in range(1, 13)]
    nota = "\n\n> Alterado pelo/a [Lei n.º 9/2021 - DR de 2020-12-09](https://x), em vigor a partir de 2025-04-11"
    _registo(tmp_path, "data/dl-114-94.md", _artigos(epigrafes))
    _registo(tmp_path, "data/lei-72-2013.md", "###### Artigo 1.º — Objeto\n\nAltera.\n\n## Anexo — CÓDIGO DA ESTRADA\n\n" + _artigos(epigrafes, nota), consolidado_ate="2025-04-11")
    _registo(tmp_path, "data/dl-5-2001.md", _artigos(["Objeto", "Âmbito"]))
    _registo(tmp_path, "data/lei-52-2012.md", BASES, consolidado_ate="2026-05-09")
    (tmp_path / "data" / "lei-52-2012.versoes.json").write_text("{}", encoding="utf-8")
    (tmp_path / "consolidacao" / "auditoria").mkdir(parents=True)
    (tmp_path / "consolidacao" / "auditoria" / "vigencia-revista.jsonl").write_text(json.dumps({"id": "pt:dre:3:por", "marca": "nao_vigora"}) + "\n", encoding="utf-8")
    (tmp_path / "consolidacao" / "resultados-escala.jsonl").write_text(json.dumps({"id": "pt:dre:3:por", "estado": "para LLM", "passos": [{"id": "pt:dre:9:por"}]}) + "\n", encoding="utf-8")
    export = tmp_path / "export.sqlite"
    con = sqlite3.connect(export)
    con.execute("CREATE TABLE documentos (id, title, summary, document_type, publication_date, legal_status, text_quality, version_kind, path, series, pdf_url)")
    con.execute("CREATE TABLE relacoes (source_id, type, target, target_id, date, label)")
    con.executemany("INSERT INTO documentos VALUES (?, ?, ?, ?, ?, ?, 'texto', ?, ?, 'I', NULL)", [
        ("pt:dre:1:por", "Decreto-Lei n.º 114/94", "Aprova o Código da Estrada", "decreto-lei", "1994-05-03", "in_force", "original", "data/dl-114-94.md"),
        ("pt:dre:2:por", "Lei n.º 72/2013", "Altera o Código da Estrada, aprovado pelo Decreto-Lei n.º 114/94", "lei", "2013-09-03", "in_force", "consolidated", "data/lei-72-2013.md"),
        ("pt:dre:3:por", "Decreto-Lei n.º 5/2001", "Regime de qualquer coisa", "decreto-lei", "2001-01-10", "unknown", "original", "data/dl-5-2001.md"),
        ("pt:dre:4:por", "Lei n.º 52/2012", "Lei de Bases dos Cuidados Paliativos", "lei", "2012-09-05", "in_force", "consolidated", "data/lei-52-2012.md"),
    ])
    con.executemany("INSERT INTO relacoes VALUES (?, 'amended_by', ?, ?, ?, NULL)", [
        ("pt:dre:1:por", "pt:dre:2:por", "pt:dre:2:por", "2013-09-03"), ("pt:dre:3:por", "pt:dre:9:por", "pt:dre:9:por", "2005-02-02")])
    con.commit()
    con.close()
    saida = tmp_path / "saida"
    resumo = inv.inventario(inv.argparse.Namespace(raiz=str(tmp_path), export=str(export), saida=str(saida), sitemap_consolidados=None, descarregar_sitemap=False, indice=None, hoje="2026-11-20"))
    assert resumo["texto_em_varios_registos"]["texto_atual_fora_do_registo_de_origem"] == 1
    assert resumo["texto_em_varios_registos"]["das_quais_a_origem_aponta_para_o_atual"] == 0  # falta o `republished_by` «Texto em vigor»
    assert resumo["texto_em_vigor"]["por_classe"] == {"texto_noutro_registo": 1, "alteracao_por_aplicar": 1}
    assert resumo["texto_em_vigor"]["marcas_de_vigencia_revista"]["prioritarios"] == {"nao_vigora": 1}
    assert resumo["vigencia_desconhecida"]["por_classe"] == {"alterado_depois_e_sem_revogacao": 1}
    assert "dre_consolidados" not in resumo and not resumo["com_sitemap"]
    por_fechar = [json.loads(l) for l in (saida / "texto-em-vigor-por-fechar.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [(l["id"], l["marca_de_vigencia"]) for l in por_fechar] == [("pt:dre:3:por", "nao_vigora")]
    assert "## 6. Lista de controlo" in (saida / "tabelas.md").read_text(encoding="utf-8")
    assert resumo["leitura"]["bases"]["por_vigencia"]["em_vigor"] == {
        "registos": 1, "prioritarios": 1, "portarias": 0, "leitura_no_indice": {"sem pedaços": 1}, "unidades": 2, "unidades_por_destino": {"sem_pedacos": 2}}
    assert resumo["leitura"]["em_vigor_sem_pedacos_por_ter_historico_sem_artigos"]["registos"] == 1
    assert [l["titulo"] for l in resumo["leitura"]["leis_de_bases_em_vigor"]] == ["Lei n.º 52/2012"]
    assert "## 8. O que o índice não lê como artigos" in (saida / "tabelas.md").read_text(encoding="utf-8")
    assert "indice_sem_artigos_abertos" not in resumo  # só com `--indice`


# ---------------------------------------------------------------------------------- 8. o que o índice não lê como artigos


def test_rotulo_do_titulo():
    assert inv.rotulo_do_titulo("Artigo 1.º — Objeto") is None
    assert inv.rotulo_do_titulo("«Artigo 5.º") is None  # redação nova citada num ato de alteração
    assert inv.rotulo_do_titulo("Base I — Âmbito") == "Base"
    assert inv.rotulo_do_titulo("ARTIGO 1.º") == "ARTIGO"
    assert inv.rotulo_do_titulo("1.º") == "número"
    assert inv.rotulo_do_titulo("IV") == "número romano"
    assert inv.rotulo_do_titulo("Cláusula 2.ª — Vigência") == "Cláusula"


def test_o_limite_do_pedaco_e_o_do_indice():
    from rag.indice import MAX_CARACTERES

    assert inv.LIMITE_DO_PEDACO == MAX_CARACTERES


BASES = "# Lei n.º 52/2012\n\n### Capítulo I\n\n###### Base I — Âmbito\n\nTexto.\n\n###### Base II — Conceitos\n\nTexto.\n"


def test_leitura_do_registo_so_com_bases():
    com_historico = inv.leitura_do_registo(BASES, com_historico=True)
    assert com_historico["no_indice"] == "sem pedaços" and com_historico["destino"] == {"Base": {"sem_pedacos": 2}}
    sem_historico = inv.leitura_do_registo(BASES, com_historico=False)
    assert sem_historico["no_indice"] == "blocos" and sem_historico["destino"] == {"Base": {"em_blocos": 2}}


def test_leitura_do_registo_com_artigos_e_bases_no_anexo():
    articulado = "###### Artigo 1.º — Objeto\n\nAprova as bases.\n\n###### Artigo 2.º — Entrada em vigor\n\nNo dia seguinte.\n\n"
    # «## Anexo» fecha o artigo: as bases com título ficam fora do índice.
    fora = inv.leitura_do_registo(articulado + "## Anexo — Bases da concessão\n\n###### Base I — Objeto\n\nTexto.\n\n###### Base II — Prazo\n\nTexto.\n", False)
    assert fora["artigos_lidos"] == 2 and fora["destino"] == {"Base": {"fora_do_indice": 2}}
    # «## ANEXO» em maiúsculas não fecha: as bases soltas colam-se ao último artigo, e o pedaço é cortado aos 30 000 caracteres.
    comprido = "Texto. " * 5000
    coladas = inv.leitura_do_registo(articulado + f"## ANEXO — (a que se refere o artigo 1.º)\n\nBase 1\n\n{comprido}\n\nBase 2\n\nTexto.\n", False)
    assert coladas["destino"] == {"Base (solta)": {"dentro_de_um_artigo": 1, "cortada": 1}}


def test_leitura_do_registo_deixa_passar_o_que_o_indice_le():
    assert inv.leitura_do_registo("###### Artigo 1.º — Objeto\n\nA base de dados é pública.\n\n###### «Artigo 5.º\n\nCitação.»\n", True) is None
    assert inv.leitura_do_registo("Despacho sem artigos nem bases.\n", False) is None
    # Sem artigos e com histórico: fica sem pedaços, mesmo em texto corrido.
    assert inv.leitura_do_registo("Portaria em texto corrido.\n", True)["no_indice"] == "sem pedaços"
    corrido = inv.leitura_do_registo("Artigo 1.º É criada a fundação.\n\nArt. 2.º Tem sede em Lisboa.\n\nArt. 3.º Entra em vigor.\n", False)
    assert corrido["no_indice"] == "blocos" and corrido["artigos_soltos_no_texto"] == 3


def test_revogacao_por_produzir_efeitos():
    futura = "Revogado pelo/a Artigo 62.º do/a [Decreto-Lei n.º 166/2026 - DR, Série I de 2026-08-13](https://x), em vigor a partir de 2026-08-14, com efeitos a partir de 2026-12-31."
    antiga = "Revogado pelo/a Artigo 3.º do/a [Lei n.º 45/2005 - DR, Série I-A de 2005-08-29](https://x), em vigor a partir de 2005-10-28"
    alterado = "Alterado pelo/a Artigo 2.º do/a [Decreto-Lei n.º 90/2017 - DR, Série I de 2017-07-28](https://x), em vigor a partir de 2017-07-29"
    assert inv.revogacao_por_produzir_efeitos(futura + "\n" + alterado, "2026-11-20") == "2026-12-31"
    assert inv.revogacao_por_produzir_efeitos(futura, "2026-12-31") is None  # já produziu efeitos
    assert inv.revogacao_por_produzir_efeitos(antiga, "2026-11-20") is None
    assert inv.revogacao_por_produzir_efeitos(futura + "\n" + antiga, "2026-11-20") is None  # já estava revogado antes
    assert inv.revogacao_por_produzir_efeitos(alterado, "2026-11-20") is None


def test_sem_artigos_abertos_no_indice(tmp_path):
    indice = tmp_path / "indice.sqlite"
    con = sqlite3.connect(indice)
    con.execute("CREATE TABLE documentos (id, titulo, tipo, data, legal_status, versao, com_historico)")
    con.execute("CREATE TABLE pedacos (documento, ate, texto, notas)")
    con.execute("CREATE TABLE relacoes (documento, tipo, alvo)")
    con.executemany("INSERT INTO documentos VALUES (?, ?, 'lei', '2003-05-21', ?, 'consolidated', 1)", [
        ("pt:dre:1:por", "Lei n.º 13/2003", "partially_in_force"), ("pt:dre:2:por", "Lei n.º 52/2012", "in_force"), ("pt:dre:3:por", "Decreto-Lei n.º 114/94", "in_force"),
        ("pt:dre:4:por", "Lei n.º 99/2003", "partially_in_force"), ("pt:dre:5:por", "Lei n.º 7/2009", "in_force"), ("eu:1", "Regulamento", "in_force")])
    futura = "Revogado pelo/a Artigo 62.º do/a [Decreto-Lei n.º 166/2026 - DR, Série I de 2026-08-13](https://x), em vigor a partir de 2026-08-14, com efeitos a partir de 2026-12-31."
    antiga = "Revogado pelo/a Artigo 12.º do/a [Lei n.º 7/2009 - DR, Série I de 2009-02-12](https://x), em vigor a partir de 2009-02-17"
    con.executemany("INSERT INTO pedacos VALUES (?, ?, ?, ?)", [
        ("pt:dre:1:por", None, "A presente lei institui o rendimento social de inserção.", futura), ("pt:dre:1:por", "2026-08-14", "Redação anterior.", ""),
        ("pt:dre:3:por", "1998-01-03", "Artigo do código de 1994.", ""),
        ("pt:dre:4:por", None, "Artigo do código de 2003.", antiga),
        ("pt:dre:5:por", None, "Artigo em vigor.", ""), ("pt:dre:5:por", None, "Outro, que acaba no fim do ano.", futura)])
    con.execute("INSERT INTO relacoes VALUES ('pt:dre:3:por', 'texto_em_vigor_em', 'pt:dre:9:por')")
    con.commit()
    con.close()
    sem_abertos, por_produzir = inv.sem_artigos_abertos(indice, "2026-11-20")
    assert {l["titulo"]: l["classe"] for l in sem_abertos} == {
        "Lei n.º 13/2003": "abertos_todos_revogados_com_efeitos_por_produzir", "Lei n.º 52/2012": "sem_pedacos",
        "Decreto-Lei n.º 114/94": "todos_fechados_com_ligacao", "Lei n.º 99/2003": "abertos_todos_revogados"}
    assert {l["titulo"]: l["efeitos_a_partir_de"] for l in por_produzir} == {"Lei n.º 13/2003": {"2026-12-31": 1}, "Lei n.º 7/2009": {"2026-12-31": 1}}
    resumo = inv.resumo_sem_abertos(sem_abertos, por_produzir)
    assert resumo["em_vigor_no_dre"] == 4 and resumo["revogacoes_por_produzir_efeitos"] == {
        "registos": 2, "pedacos": 2, "por_data": {"2026-12-31": 2}, "registos_com_todos_os_abertos_dados_como_revogados": 1}


def test_anexo_em_maiusculas():
    corpo = ("###### Artigo 1.º — Objeto\n\nAprova o regulamento.\n\n###### Artigo 2.º — Entrada em vigor\n\nAmanhã.\n\n"
             "## ANEXO — Regulamento\n\n###### Artigo 1.º — Âmbito\n\nTexto.\n\n###### Artigo 3.º — Taxas\n\nTexto.\n")
    assert inv.anexo_em_maiusculas(corpo.encode()) == {"artigos_no_anexo": 2, "com_o_numero_de_um_artigo_do_diploma": 1}
    assert inv.anexo_em_maiusculas(corpo.replace("## ANEXO", "## Anexo").encode()) is None
    # Um `## Anexo` bem escrito a seguir já é lido como parte: os artigos dele não contam.
    assert inv.anexo_em_maiusculas((corpo + "\n## Anexo II — Tabela\n\n###### Artigo 1.º — Valores\n\nTexto.\n").encode())["artigos_no_anexo"] == 2
    # O leitor do índice põe mesmo os dois «1.º» na parte do diploma.
    assert [(a.parte, a.numero) for a in inv.ler_artigos(corpo)] == [("", "1.º"), ("", "2.º"), ("", "1.º"), ("", "3.º")]
