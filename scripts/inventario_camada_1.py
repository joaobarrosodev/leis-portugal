"""Inventário da camada 1 (o texto da lei): o que falta para estar certo no que acrescenta valor.

Só lê: o export (`exports/leis-portugal.sqlite`), os registos em `data/`, a triagem da
consolidação (`consolidacao/resultados-escala.jsonl`) e os relatórios em `reports/`. Não muda
nada no `data/`, no export nem no índice. Grava em `reports/inventario-camada-1/`:

- `resumo.json`: todos os números;
- `tabelas.md`: as tabelas geradas (resumo, texto em vigor, vigência, lista de controlo…);
- uma lista `.jsonl` por falha, com os diplomas por trás de cada número.

Âmbito: 1.ª Série do Diário da República. «Prioritários» são as leis, leis orgânicas, leis
constitucionais, decretos-leis, decretos regulamentares e decretos legislativos regionais; as
portarias contam-se à parte, sem listas.

O que mede (os números da secção correspondente do `reports/inventario-camada-1.md`):

1. **Texto em vigor.** Cada diploma em vigor (ou de vigência desconhecida) com `amended_by` cai
   numa classe: consolidado pelo DRE, consolidado pelo leis-portugal, texto noutro registo (códigos
   republicados), sem texto (só digitalização) ou, pela triagem da consolidação, original que é o
   texto em vigor, alteração por aplicar, revogado por inteiro ou não triado. Cada linha leva também a marca da
   vigência revista, quando existe (`consolidacao/auditoria/vigencia-revista.jsonl`). Nos consolidados,
   «em dia» quer dizer: nenhum `amended_by` publicado depois da última versão e fora do histórico,
   e o DRE não mexeu na página depois da recolha (com `--sitemap-consolidados`).
2. **O mesmo texto em vários registos.** Os consolidados do DRE que têm, num anexo, o texto de outro diploma
   (republicações). Para cada par: onde está o texto mais recente, se o original aponta para lá
   (`republished_by` com «Texto em vigor…», que o índice lê), e se a numeração dos artigos se
   manteve (a pesquisa troca o artigo do original pelo do consolidado com o mesmo número).
3. **Vigência desconhecida** por tipo e ano, e o que os dados que já temos permitem dizer.
4. **O que o DRE consolida e não temos**, pelo sitemap da legislação consolidada.
5. **Antigos sem texto**: em vigor segundo o DRE, só com digitalização, e citados por diplomas em vigor.
6. **Lista de controlo** dos diplomas centrais (`scripts/inventario_diplomas_centrais.json`).
7. **Fora do export**: CNPD, Tribunal Constitucional e acordos coletivos sem texto.
8. **O que o índice não lê como artigos.** Desde 20/11/2026 o leitor conhece `###### ARTIGO`, `###### Base`,
   `###### 1.º` e `## ANEXO`. Fica por ler como unidade: as «Base N» e «Cláusula N» soltas no texto, os títulos
   de outra forma e os «Artigo 1.º … Art. 2.º …» em texto corrido (`leitura-fora-dos-artigos.jsonl`). Com
   `--indice`, também os registos em vigor sem um pedaço aberto e não revogado, e as revogações que ainda
   não produziram efeitos (`indice-sem-artigos-abertos.jsonl`, `revogacoes-por-produzir-efeitos.jsonl`).

Uso (na raiz do repositório):

    python scripts/inventario_camada_1.py --descarregar-sitemap
    python scripts/inventario_camada_1.py --sitemap-consolidados ficheiro.xml --indice rag/indice/indice.sqlite

Sem sitemap, a secção 4 e a parte «o DRE mexeu depois da recolha» ficam por medir. Com `--indice`,
verifica também se «artigo N.º do Código X» chega ao registo certo (só BM25, sem modelos).
`--sem-leitura` salta a secção 8, que lê todos os `.md` (cerca de um minuto e meio).
Num worktree sem `exports/`, usa o export da pasta principal.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import urllib.request
import xml.etree.ElementTree as ElementTree
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from rag.copias import (  # noqa: E402, F401 (os testes usam estes nomes a partir daqui)
    ANEXO_MINIMO,
    PRIORITARIOS,
    VIGENTES,
    Acervo,
    aprovados_nas_notas,
    cabecalho,
    carregar,
    do_dre,
    ler_partes,
    mesma_obra,
    obras,
    partes,
    redacoes_anteriores,
    referencias,
    sobreposicao,
)
from rag.fontes import comum, corpo, fora_dos_artigos, ler_artigos, revogacao_por_produzir_efeitos, revogado  # noqa: E402


SITEMAP_CONSOLIDADOS = "https://files.diariodarepublica.pt/sitemap/legislacao-consolidada-sitemap-1.xml"


# ------------------------------------------------------------------ leitura


def export_por_omissao(raiz: Path = RAIZ) -> Path:
    """`exports/leis-portugal.sqlite` desta cópia ou, num worktree, o da pasta principal."""
    local = raiz / "exports" / "leis-portugal.sqlite"
    if local.exists():
        return local
    git = raiz / ".git"
    if git.is_file():
        m = re.match(r"gitdir: (.*?)/\.git/worktrees/", git.read_text(encoding="utf-8"))
        if m and (Path(m.group(1)) / "exports" / "leis-portugal.sqlite").exists():
            return Path(m.group(1)) / "exports" / "leis-portugal.sqlite"
    return local


# ------------------------------------------------------------------ 2. o mesmo texto em vários registos


def onde_vive(i: str, acervo: Acervo, cabecalhos: dict[str, dict], lista_obras: list[dict]) -> tuple[str | None, dict | None]:
    """O registo com o texto em vigor mais recente de um diploma (ele próprio, outro, ou nenhum) e a obra usada.

    Só conta a obra de que o diploma é a origem (o IVA no DL 394-B/84), não as que ele republica noutro anexo.
    """
    minhas = [o for o in lista_obras if o["origem"] == i]
    if minhas:
        obra = max(minhas, key=lambda o: max(c["artigos"] for c in o["copias"] if c["id"] == i))
        return obra["atual"], obra
    if i in cabecalhos:
        return i, None
    if i in acervo.texto_em_vigor_em:
        return acervo.texto_em_vigor_em[i], None
    return None, None


# ------------------------------------------------------------------ 1. texto em vigor


def em_dia(i: str, acervo: Acervo, cab: dict, sitemap: dict[str, str] | None, tambem: str | None = None, desde: str | None = None) -> dict:
    """Se um consolidado tem alteradores publicados depois da última versão e fora do histórico.

    `tambem`: o diploma de origem, quando o texto vive noutro registo (o DRE regista as alterações num ou noutro);
    `desde`: a data do texto dessa cópia, para os alteradores da origem.
    """
    ate = cab["data_consolidacao"] or ""
    posteriores = {(quando, alvo) for alvo, quando, _ in acervo.alterado_por.get(i, ()) if quando and quando > ate and alvo not in cab["alteradores_no_historico"] and alvo != i}
    if tambem:
        posteriores |= {(quando, alvo) for alvo, quando, _ in acervo.alterado_por.get(tambem, ())
                        if quando and quando > max(desde or "", ate) and alvo not in cab["alteradores_no_historico"] and alvo != i}
    mexido = bool(sitemap and cab["url_consolidado"] and sitemap.get(cab["url_consolidado"], "") > (cab["lastmod"] or ""))
    return {
        "em_dia": not posteriores and not mexido,
        "alteradores_posteriores": [{"data": q, "id": a, "titulo": (acervo.docs.get(a) or {}).get("title")} for q, a in sorted(posteriores)],
        "dre_mexeu_depois_da_recolha": mexido,
        "dre_lastmod": sitemap.get(cab["url_consolidado"]) if sitemap and cab["url_consolidado"] else None,
    }


TRIAGEM_PARA_CLASSE = {
    "sem alteração textual": "original_e_o_texto_em_vigor",
    "para LLM": "alteracao_por_aplicar",
    "aplicado por regra": "alteracao_por_aplicar",
    "alteração só em imagem": "alteracao_so_em_imagem",
    "sem texto do alterador": "alteracao_por_aplicar",
    "revogado por inteiro": "revogado_por_inteiro",
    "não triado": "nao_triado",
    "excluído": "nao_triado",
}


def classe_do_texto(doc: dict, cab: dict | None, vive_em: str | None, triagem: dict | None) -> str:
    """A classe de um diploma em vigor com `amended_by`, quanto ao texto em vigor (ver o início do ficheiro)."""
    if vive_em and vive_em != doc["id"]:
        return "texto_noutro_registo"
    if cab is not None:
        return "consolidado_dre" if do_dre(cab["rotulo"]) else "consolidado_leis_portugal"
    if doc["text_quality"] != "texto":
        return "sem_texto"
    if triagem is None:
        return "nao_triado"
    return TRIAGEM_PARA_CLASSE.get(triagem.get("estado"), "nao_triado")


def texto_em_vigor(acervo: Acervo, cabecalhos: dict[str, dict], lista_obras: list[dict], triagem: dict[str, dict], sitemap: dict[str, str] | None, tipos: tuple[str, ...],
                   marcas: dict[str, str] | None = None) -> list[dict]:
    """`marcas`: id → marca da vigência revista (`consolidacao/auditoria/vigencia-revista.jsonl`): `nao_vigora`, `regime_anterior` ou `por_confirmar`."""
    linhas = []
    for i, doc in acervo.docs.items():
        if doc["document_type"] not in tipos or doc["series"] != "I" or doc["legal_status"] not in VIGENTES or not acervo.alterado_por.get(i):
            continue
        vive_em, obra = onde_vive(i, acervo, cabecalhos, lista_obras)
        classe = classe_do_texto(doc, cabecalhos.get(i), vive_em, triagem.get(i))
        linha = {
            "id": i, "titulo": doc["title"], "tipo": doc["document_type"], "data": doc["publication_date"], "estado": doc["legal_status"],
            "classe": classe, "alteradores": len(acervo.alterado_por[i]), "citado_por_vigentes": acervo.citado_por_vigentes.get(i, 0),
            "sumario": (doc["summary"] or "")[:160],
        }
        if marcas and i in marcas:
            linha["marca_de_vigencia"] = marcas[i]
        if classe in ("consolidado_dre", "consolidado_leis_portugal"):
            linha["consolidado_ate"] = cabecalhos[i]["data_consolidacao"]
            linha |= em_dia(i, acervo, cabecalhos[i], sitemap)
        elif classe == "texto_noutro_registo":
            linha["vive_em"] = vive_em
            linha["vive_em_titulo"] = acervo.docs[vive_em]["title"]
            linha["ligado"] = acervo.texto_em_vigor_em.get(i) == vive_em
            linha["tem_consolidacao_propria_mais_antiga"] = i in cabecalhos
            if vive_em in cabecalhos:
                linha["consolidado_ate"] = obra["data_do_texto_atual"] if obra else cabecalhos[vive_em]["data_consolidacao"]
                linha |= em_dia(vive_em, acervo, cabecalhos[vive_em], sitemap, tambem=i, desde=obra["data_do_texto_atual"] if obra else None)
        elif triagem.get(i):
            linha["triagem"] = triagem[i].get("estado")
            vistos = {p.get("id") for p in triagem[i].get("passos") or []}
            linha["alteradores_novos_desde_a_triagem"] = sorted({a for a, _, _ in acervo.alterado_por[i] if a and a not in vistos}) if vistos else []
        linhas.append(linha)
    return linhas


# ------------------------------------------------------------------ 3. vigência desconhecida

_REVOGACAO_PARCIAL = re.compile(
    r"^Revogad[oa]s?,?(?: a partir de [^,]+,)?(?: com efeitos[^,]+,)? (?:o|a|os|as) (?:art|n\.?º|n\.?ºs|al\.|alínea|anexo|cap|sec|mapa|quadro|base|§|parte|disposiç|norma)",
    re.I,
)
_TEMPORARIO = re.compile(r"Orçamento do Estado para|Grandes Opções|execução do Orçamento|para o ano de \d{4}|para \d{4}\b|estado de (?:emergência|calamidade|alerta)|COVID|medidas excecionais e temporárias", re.I)
_ATO_DE_ALTERACAO = re.compile(
    r"^(?:Altera|Procede à|Primeira|Segunda|Terceira|Quarta|Quinta|Sexta|Sétima|Oitava|Nona|Décima|Vigésima|Trigésima|\d+\.ª) .{0,40}?altera|^Altera\b|^Prorroga|^Revoga\b|^Cessa|^Repristina|^Suspende", re.I
)


def revogacao(relacoes: list[tuple[str | None, str | None, str | None]]) -> str | None:
    """`inteira`, `parcial` ou None, pelas etiquetas das relações `repealed_by` do DRE.

    A etiqueta diz o que é revogado: «Revogado, a partir de …, o art. 3.º» é parcial; sem unidade
    («Revogado pelo …», «Revogado, a partir de …, o Dec Lei 5/2020») conta como o diploma inteiro.
    Com «com exceção» ou «na parte» é sempre parcial.
    """
    if not relacoes:
        return None
    inteiras = [e for _, _, e in relacoes if not _REVOGACAO_PARCIAL.match(e or "") and not re.search(r"exce[çp]|na parte|parcialmente|em tudo o que", e or "", re.I)]
    return "inteira" if inteiras else "parcial"


def classe_desconhecida(doc: dict, revogado: str | None, proposta: dict | None, ultima_alteracao: str | None) -> str:
    """O que os dados que já temos dizem de um diploma com `legal_status: unknown`."""
    sumario = doc["summary"] or ""
    if revogado == "inteira":
        return "revogado_segundo_a_relacao_do_dre"
    if proposta and proposta.get("status") in ("repealed", "not_in_force"):
        return "revogacao_lida_no_texto_de_outro_diploma"
    if _TEMPORARIO.search(sumario):
        return "temporario_ou_orcamental"
    if _ATO_DE_ALTERACAO.search(sumario):
        return "ato_de_alteracao"
    if ultima_alteracao and ultima_alteracao > (doc["publication_date"] or ""):
        return "alterado_depois_e_sem_revogacao"
    return "sem_indicio_de_revogacao"


def vigencia_desconhecida(acervo: Acervo, propostas: dict[str, dict], tipos: tuple[str, ...]) -> list[dict]:
    linhas = []
    for i, doc in acervo.docs.items():
        if doc["document_type"] not in tipos or doc["series"] != "I" or doc["legal_status"] != "unknown":
            continue
        datas = [q for _, q, _ in acervo.alterado_por.get(i, ()) if q]
        ultima = max(datas) if datas else None
        revogado = revogacao(acervo.revogado_por.get(i, []))
        linhas.append({
            "id": i, "titulo": doc["title"], "tipo": doc["document_type"], "data": doc["publication_date"], "texto": doc["text_quality"],
            "classe": classe_desconhecida(doc, revogado, propostas.get(i), ultima), "revogacao_no_dre": revogado,
            "alteradores": len(acervo.alterado_por.get(i, ())), "ultima_alteracao": ultima,
            "citado_por_vigentes": acervo.citado_por_vigentes.get(i, 0), "sumario": (doc["summary"] or "")[:160],
        })
    return linhas


# ------------------------------------------------------------------ 4. sitemap dos consolidados


def ler_sitemap(xml: bytes) -> dict[str, str]:
    """URL da legislação consolidada → `lastmod` (AAAA-MM-DD)."""
    espaco = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    entradas = {}
    for no in ElementTree.fromstring(xml).findall("s:url", espaco):
        url = (no.findtext("s:loc", default="", namespaces=espaco) or "").strip()
        if "/dr/legislacao-consolidada/" in url:
            entradas[url] = (no.findtext("s:lastmod", default="", namespaces=espaco) or "").strip()[:10]
    return entradas


def comparar_sitemap(sitemap: dict[str, str], nossos: dict[str, dict], falhas: set[str]) -> dict:
    """O que o DRE lista e não temos, e o que temos mas o DRE mudou depois da recolha.

    `nossos`: URL do consolidado → {id, lastmod}. `falhas`: URLs em que a fonte não tinha texto.
    """
    em_falta = [{"url": u, "tipo": u.split("/")[-2], "ano": u.split("/")[-1][:4], "dre_lastmod": m, "motivo": "sem_texto_na_fonte" if u in falhas else "por_recolher"}
                for u, m in sorted(sitemap.items()) if u not in nossos]
    mexidos = [{"url": u, "id": nossos[u]["id"], "dre_lastmod": m, "nosso_lastmod": nossos[u]["lastmod"]}
               for u, m in sorted(sitemap.items()) if u in nossos and m > (nossos[u]["lastmod"] or "")]
    return {"listados": len(sitemap), "temos": sum(u in nossos for u in sitemap), "em_falta": em_falta, "mexidos_depois_da_recolha": mexidos,
            "so_nossos": sorted(u for u in nossos if u not in sitemap)}


# ------------------------------------------------------------------ 5. antigos sem texto


def faixa(ano: int) -> str:
    return "antes de 1910" if ano < 1910 else "1910–1959" if ano < 1960 else "1960–1996" if ano < 1997 else "1997 ou depois"


def antigos_sem_texto(acervo: Acervo, tipos: tuple[str, ...]) -> list[dict]:
    linhas = []
    for i, doc in acervo.docs.items():
        if doc["document_type"] not in tipos or doc["series"] not in ("I", None) or doc["text_quality"] == "texto" or doc["legal_status"] not in VIGENTES:
            continue
        ano = int((doc["publication_date"] or "0000")[:4])
        linhas.append({
            "id": i, "titulo": doc["title"], "tipo": doc["document_type"], "data": doc["publication_date"], "faixa": faixa(ano), "estado": doc["legal_status"],
            "texto": doc["text_quality"], "citado_por_vigentes": acervo.citado_por_vigentes.get(i, 0), "alteradores": len(acervo.alterado_por.get(i, ())),
            "sumario": (doc["summary"] or "")[:160], "pdf": doc["pdf_url"],
        })
    return sorted(linhas, key=lambda r: (-r["citado_por_vigentes"], r["data"] or ""))


# ------------------------------------------------------------------ 6. lista de controlo


def resolver(titulo: str, acervo: Acervo) -> str | None:
    """O registo com este título; com vários, o consolidado, depois o que está em vigor, depois o mais citado."""
    ids = acervo.por_titulo.get(titulo) or []
    ordem = lambda i: (acervo.docs[i]["version_kind"] == "consolidated", acervo.docs[i]["legal_status"] == "in_force", acervo.citado_por_vigentes.get(i, 0))  # noqa: E731
    return max(ids, key=ordem) if ids else None


def duplicados(acervo: Acervo, tipos: tuple[str, ...]) -> list[dict]:
    """Diplomas com mais de um registo (o mesmo título e a mesma data de publicação) em que pelo menos dois têm texto.

    O DRE tem alguns diplomas duas vezes; se só um dos registos é consolidado, o outro serve o texto de origem."""
    grupos: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for d in acervo.docs.values():
        if d["document_type"] in tipos and d["series"] == "I" and d["publication_date"] and d["text_quality"] == "texto":
            grupos[(d["title"], d["publication_date"])].append(d)
    return [{"titulo": t, "data": q, "registos": [{"id": d["id"], "estado": d["legal_status"], "versao": d["version_kind"], "alteradores": len(acervo.alterado_por.get(d["id"], ())),
                                                  "sumario": (d["summary"] or "")[:100]} for d in sorted(g, key=lambda d: d["id"])]}
            for (t, q), g in sorted(grupos.items()) if len(g) > 1]


def lista_de_controlo(centrais: list[dict], acervo: Acervo, cabecalhos: dict[str, dict], lista_obras: list[dict], triagem: dict[str, dict], sitemap: dict[str, str] | None, raiz: Path,
                      marcas: dict[str, str] | None = None) -> list[dict]:
    linhas = []
    for entrada in centrais:
        linha = {"area": entrada["area"], "nome": entrada["nome"], "diploma": entrada["diploma"], "pesquisa": entrada.get("pesquisa")}
        i = resolver(entrada["diploma"], acervo)
        if i is None:
            linhas.append(linha | {"id": None, "problemas": ["não está no acervo"]})
            continue
        doc = acervo.docs[i]
        vive_em, obra = onde_vive(i, acervo, cabecalhos, lista_obras)
        problemas = []
        linha |= {"id": i, "estado": doc["legal_status"], "data": doc["publication_date"], "sumario": (doc["summary"] or "")[:120],
                  "vive_em": vive_em, "vive_em_titulo": acervo.docs[vive_em]["title"] if vive_em else None, "parte": obra["atual_parte"] if obra else None}
        if doc["legal_status"] == "unknown":
            problemas.append("vigência desconhecida")
        elif doc["legal_status"] not in VIGENTES:
            problemas.append(f"o DRE dá-o como {doc['legal_status']}")
        if marcas and i in marcas:
            linha["marca_de_vigencia"] = marcas[i]
            problemas.append(f"vigência revista: {marcas[i].replace('_', ' ')}")
        if vive_em is None:
            classe = classe_do_texto(doc, None, None, triagem.get(i))
            linha["texto"] = classe
            if doc["text_quality"] != "texto":
                problemas.append("sem texto (só digitalização)")
            elif not acervo.alterado_por.get(i):
                linha["texto"] = "original_sem_alteracoes"
            elif classe == "original_e_o_texto_em_vigor":
                problemas.append(f"{len(acervo.alterado_por[i])} `amended_by` e sem consolidação: a triagem diz que nenhum muda o texto")
            else:
                problemas.append(f"alterado e sem texto em vigor ({classe.replace('_', ' ')}; {len(acervo.alterado_por[i])} `amended_by`)")
        else:
            cab = cabecalhos.get(vive_em)
            linha["texto"] = ("consolidado_dre" if do_dre(cab["rotulo"]) else "consolidado_leis_portugal") if cab else "original"
            if cab:
                linha["consolidado_ate"] = obra["data_do_texto_atual"] if obra else cab["data_consolidacao"]
                dia = em_dia(vive_em, acervo, cab, sitemap, tambem=i if vive_em != i else None, desde=obra["data_do_texto_atual"] if obra else None)
                linha |= dia
                if dia["dre_mexeu_depois_da_recolha"]:
                    problemas.append(f"o DRE mexeu no consolidado a {dia['dre_lastmod']}, depois da recolha")
                if dia["alteradores_posteriores"]:
                    ultimos = ", ".join(f"{a['titulo'] or a['id']} ({a['data']})" for a in dia["alteradores_posteriores"][-3:])
                    problemas.append(f"{len(dia['alteradores_posteriores'])} alterador(es) depois da última versão: {ultimos}")
            if vive_em != i:
                if acervo.texto_em_vigor_em.get(i) != vive_em:
                    problemas.append("o original não aponta para o registo com o texto em vigor (sem `republished_by` «Texto em vigor»)")
                if obra and obra["com_epigrafe"] >= 20 and obra["epigrafes_iguais"] / obra["com_epigrafe"] < 0.8:
                    problemas.append(f"numeração diferente da do original: só {obra['epigrafes_iguais']} de {obra['com_epigrafe']} artigos com o mesmo número têm a mesma epígrafe")
        if obra:
            outras = [c for c in obra["copias"] if c["desatualizada"] and c["servida_como_vigente"]]
            if outras:
                nomes = ", ".join(f"{c['titulo']} (texto de {c['data_do_texto']})" for c in outras)
                problemas.append(f"{len(outras)} cópia(s) com texto de outra data servida(s) como em vigor: {nomes}")
            linha["copias"] = [{k: c.get(k) for k in ("id", "titulo", "parte", "artigos", "data_do_texto", "papel", "desatualizada", "servida_como_vigente", "pedacos_atuais_no_indice")} for c in obra["copias"]]
        if vive_em and (raiz / acervo.docs[vive_em]["path"]).exists():
            lidas = partes((raiz / acervo.docs[vive_em]["path"]).read_text(encoding="utf-8"))
            proprio = lidas.get("", {})
            maior = max(((p, a) for p, a in lidas.items() if p), key=lambda x: len(x[1]), default=(None, {}))
            linha["artigos_do_diploma"] = len(proprio)
            linha["artigos_no_maior_anexo"] = len(maior[1])
            linha["maior_anexo"] = maior[0]
            if len(maior[1]) >= ANEXO_MINIMO and proprio:
                linha["numeros_repetidos_entre_diploma_e_anexo"] = len(set(proprio) & set(maior[1]))
        gemeos = [g for g in acervo.por_titulo.get(doc["title"], ()) if g != i and acervo.docs[g]["publication_date"] == doc["publication_date"] and acervo.docs[g]["text_quality"] == "texto"]
        if gemeos:
            problemas.append("há outro registo do mesmo diploma com texto: " + ", ".join(f"{g} ({acervo.docs[g]['version_kind']}, {acervo.docs[g]['legal_status']})" for g in gemeos))
        linha["problemas"] = problemas
        linhas.append(linha)
    return linhas


def verificar_pesquisa(linhas: list[dict], indice: Path, raiz: Path, acervo: Acervo) -> None:
    """«artigo N.º do <nome>» chega ao registo que tem o texto em vigor? Só BM25 e referência, sem modelos."""
    sys.path.insert(0, str(raiz))
    from rag.pesquisa import Pesquisa  # noqa: PLC0415

    pesquisa = Pesquisa(indice)
    for linha in linhas:
        if not linha.get("pesquisa"):
            continue
        esperado = linha.get("vive_em")
        numero = "2.º"
        if esperado and (raiz / acervo.docs[esperado]["path"]).exists():
            lidas = partes((raiz / acervo.docs[esperado]["path"]).read_text(encoding="utf-8"))
            maior = lidas.get(linha.get("parte") or "") or max(lidas.values(), key=len, default={})
            numeros = [n for n in maior if n != "único" and "-" not in n]
            numero = numeros[len(numeros) // 2] if numeros else numero
        pergunta = f"artigo {numero} {linha['pesquisa']}"
        resultados = pesquisa.pesquisar(pergunta, k=3).resultados
        primeiro = resultados[0] if resultados else None
        registo_certo = bool(primeiro and esperado and primeiro.documento == esperado)
        certo = registo_certo and primeiro.numero == numero
        linha["pesquisa_resultado"] = {
            "pergunta": pergunta, "certo": certo, "registo_certo": registo_certo,
            "primeiro": None if primeiro is None else {"documento": primeiro.documento, "titulo": primeiro.titulo, "parte": primeiro.parte, "numero": primeiro.numero, "origem": primeiro.origem},
        }
        if not certo:
            veio = "nada" if primeiro is None else f"{primeiro.titulo}, {primeiro.parte or 'articulado'}, artigo {primeiro.numero}"
            linha["problemas"].append(f"«{pergunta}» {'chega ao registo certo mas a outro artigo' if registo_certo else 'não chega ao registo certo'} (veio: {veio})")


# ------------------------------------------------------------------ 7. fora do export


def contar_md(pasta: Path) -> int:
    return sum(1 for _ in pasta.rglob("*.md")) if pasta.exists() else 0


def fora_do_export(acervo: Acervo, raiz: Path, export: Path) -> dict:
    con = sqlite3.connect(f"file:{export}?mode=ro", uri=True)
    prefixos = dict(con.execute("SELECT substr(id, 1, instr(substr(id, 4), ':') + 3), count(*) FROM documentos GROUP BY 1"))
    con.close()
    acordos = Counter((d["series"] or "sem série", d["text_quality"]) for d in acervo.docs.values() if d["document_type"] == "acordo-coletivo-trabalho")
    return {
        "export_por_prefixo": prefixos,
        "cnpd_em_data": contar_md(raiz / "data" / "entidades" / "cnpd"),
        "tribunal_constitucional_em_data": contar_md(raiz / "data" / "jurisprudencia" / "tribunal-constitucional"),
        "acordos_coletivos": {f"{serie} / {texto}": n for (serie, texto), n in sorted(acordos.items())},
    }


# ------------------------------------------------------------------ 8. o que o índice não lê como artigos

# O leitor do índice (`avaliacao/comum.py`) conhece `###### Artigo N.º`, `###### ARTIGO N.º`, `###### Base IV`,
# `###### 1.º` e os anexos `## Anexo` e, com artigos, `## ANEXO` (desde 20/11/2026). O que fica por ler como unidade: as «Base N» e
# «Cláusula N» sozinhas numa linha de texto corrido, os títulos de nível 6 de outra forma e os «Artigo 1.º … Art. 2.º …»
# do texto corrido que o `structure` não marcou.
LIMITE_DO_PEDACO = 30_000  # `rag.indice.MAX_CARACTERES`: o texto de um pedaço é cortado aqui
ABERTURA_MINIMA = 300  # `rag.indice.ABERTURA_MINIMA`: o texto fora dos artigos de um registo só com títulos novos entra em blocos a partir daqui
EM_VIGOR_NO_DRE = ("in_force", "partially_in_force")
_SOLTA = re.compile(r"^(?:\*\*)?(Base|Cláusula) +(?:[IVXLC]+|\d+)\.?[ªº]?\.?(?:\*\*)?$", re.M | re.I)
_ARTIGO_SOLTO = re.compile(r"^(?:Artigo|ARTIGO|Art\.) ?\d+\.?[º°]", re.M)
_ROMANO = re.compile(r"^[IVXLC]+\.?$")
# Na leitura rápida, em bytes: um título de nível 6 que não é «Artigo», ou uma «Base»/«Cláusula»/«Artigo» no início de uma linha.
_SUSPEITO = re.compile(rb"^###### (?!Artigo[ \d])|^(?:\*\*)?(?:Base|BASE|Cl\xc3\xa1usula|CL\xc3\x81USULA) |^(?:Artigo|ARTIGO|Art\.) ?\d", re.M)


def rotulo_do_titulo(titulo: str) -> str | None:
    """A classe de um título de nível 6 que o índice não lê como unidade; None se o lê ou se é uma citação.

    Uma citação («Artigo 5.º, com aspas) é a redação nova dentro de um ato de alteração: fica bem no texto do artigo que a traz."""
    palavra = titulo.split()[0] if titulo.split() else ""
    if not palavra or palavra[0] in "«\"“'[(" or comum._cabecalho("###### " + titulo):
        return None
    if palavra.lower().rstrip(".º") in ("artigo", "art", "artº") or palavra.startswith(("Artigo", "ARTIGO")):
        return "Artigo (outra forma)"
    if palavra.lower() == "base":
        return "Base (outra forma)"
    if palavra.lower() in ("cláusula", "clausula"):
        return "Cláusula"
    if palavra[0].isdigit():
        return "número (outra forma)"
    if _ROMANO.match(palavra):
        return "número romano"
    return "outro"


def _unidade(linha: str) -> str | None:
    """«Cláusula», «Base (solta)»… se a linha é uma unidade que o índice não lê (título de nível 6 ou «Base N» solta)."""
    if linha.startswith("###### "):
        return rotulo_do_titulo(linha[7:])
    solta = _SOLTA.match(linha)
    return solta.group(1).capitalize() + " (solta)" if solta else None


def leitura_do_registo(markdown: str) -> dict | None:
    """Como o índice lê um registo que tem unidades que não conhece, ou que está em blocos com artigos soltos no texto.

    Destino de cada unidade, pelo que `rag.indice.pedacos_do_documento` faz:

    - `em_blocos`: o registo não tem nenhuma unidade lida, ou a unidade está na abertura que o índice guarda em blocos:
      blocos de ~300 palavras (pesquisável, mas sem número nem epígrafe);
    - `dentro_de_um_artigo`: a unidade vem depois de um artigo (também num `## ANEXO` sem artigos): fica colada ao texto dele;
    - `cortada`: o mesmo, mas para lá dos 30 000 caracteres do pedaço, que o índice corta;
    - `fora_do_indice`: a unidade vem antes do primeiro artigo do diploma, ou de um `## Anexo` que depois tem artigos.

    Nos registos com histórico o índice lê as versões e não o `.md`; aqui lê-se o `.md`, que é a última versão.
    """
    texto = corpo(markdown)
    unidades = Counter(u for linha in texto.split("\n") if (u := _unidade(linha)))
    artigos = ler_artigos(texto)
    soltos = 0 if artigos else len(_ARTIGO_SOLTO.findall(texto))
    if not unidades and soltos < 3:
        return None
    destino: dict[str, Counter] = defaultdict(Counter)
    if not artigos:
        for u, n in unidades.items():
            destino[u]["em_blocos"] += n
    else:
        contadas: Counter = Counter()
        for artigo in artigos:
            posicao = 0
            for linha in artigo.texto.split("\n"):
                u = _unidade(linha)
                if u:
                    destino[u]["cortada" if posicao >= LIMITE_DO_PEDACO else "dentro_de_um_artigo"] += 1
                    contadas[u] += 1
                posicao += len(linha) + 1
        # O texto fora dos artigos entra em blocos nos registos só com títulos das formas novas (`rag.indice._unidades`).
        if all(a.forma != "Artigo" for a in artigos):
            for _, fora in fora_dos_artigos(texto):
                if sum(len(l.strip()) for l in fora.split("\n") if not l.startswith("#")) < ABERTURA_MINIMA:
                    continue
                for linha in fora.split("\n"):
                    u = _unidade(linha)
                    if u:
                        destino[u]["em_blocos"] += 1
                        contadas[u] += 1
        for u, n in unidades.items():
            if n > contadas[u]:
                destino[u]["fora_do_indice"] += n - contadas[u]
    return {
        "artigos_lidos": len(artigos), "unidades": dict(unidades), "caracteres": len(texto),
        "destino": {u: dict(d) for u, d in destino.items()},
        "no_indice": "artigos" if artigos else "blocos",
        **({"artigos_soltos_no_texto": soltos} if soltos >= 3 else {}),
    }


def leitura_dos_registos(acervo: Acervo, raiz: Path) -> list[dict]:
    """Os registos portugueses com texto em que o índice não lê tudo como unidades (lê todos os `.md`: cerca de um minuto e meio)."""
    linhas = []
    for i, d in acervo.docs.items():
        if d["text_quality"] != "texto" or not d["path"]:
            continue
        try:
            bruto = (raiz / d["path"]).read_bytes()
        except OSError:
            continue
        if not _SUSPEITO.search(bruto):
            continue
        leitura = leitura_do_registo(bruto.decode("utf-8"))
        if leitura:
            linhas.append({"id": i, "titulo": d["title"], "tipo": d["document_type"], "data": d["publication_date"], "estado": d["legal_status"] or "unknown",
                           "versao": d["version_kind"], "serie": d["series"], "sumario": (d["summary"] or "")[:120], "citado_por_vigentes": acervo.citado_por_vigentes.get(i, 0), **leitura})
    return linhas


def gravar_leitura(saida: Path, nao_lidos: list[dict]) -> None:
    """A lista da secção 8: os registos com unidades por ler, em vigor no DRE, e as bases também dos de vigência desconhecida
    (a Lei n.º 95/2019 é um deles). Os que só têm «Artigo N.º» em texto corrido são um teto e ficam só contados."""
    escolhidos = [l for l in nao_lidos if l["unidades"] and (l["estado"] in EM_VIGOR_NO_DRE or (vigencia_no_dre(l["estado"]) == "desconhecida" and "Base (solta)" in l["unidades"]))]
    _jsonl(saida / "leitura-fora-dos-artigos.jsonl", sorted(
        ({k: v for k, v in l.items() if k not in ("sumario", "serie", "versao") or (k == "sumario" and "Base (solta)" in l["unidades"])} for l in escolhidos),
        key=lambda l: (l["estado"] not in EM_VIGOR_NO_DRE, -sum(l["unidades"].values()), -l["caracteres"], l["id"])))


def vigencia_no_dre(estado: str | None) -> str:
    return "em_vigor" if estado in EM_VIGOR_NO_DRE else "desconhecida" if estado in (None, "", "unknown") else "sem_vigencia"


def resumo_da_leitura(linhas: list[dict]) -> dict:
    """Por família de unidades por ler e por vigência: registos, unidades e o destino de cada uma no índice."""

    def prioritario(l: dict) -> bool:
        return l["tipo"] in PRIORITARIOS and l["serie"] == "I"

    def conta(escolhidas: list[dict], rotulos: tuple[str, ...]) -> dict:
        saida: dict = {"registos": len(escolhidas), "unidades": sum(l["unidades"].get(u, 0) for l in escolhidas for u in rotulos), "por_vigencia": {}}
        for vigencia in ("em_vigor", "desconhecida", "sem_vigencia"):
            grupo = [l for l in escolhidas if vigencia_no_dre(l["estado"]) == vigencia]
            destino: Counter = Counter()
            for l in grupo:
                for u in rotulos:
                    destino.update(l["destino"].get(u, {}))
            saida["por_vigencia"][vigencia] = {
                "registos": len(grupo), "prioritarios": sum(prioritario(l) for l in grupo), "portarias": sum(l["tipo"] == "portaria" for l in grupo),
                "leitura_no_indice": dict(Counter(l["no_indice"] for l in grupo)),
                "unidades": sum(l["unidades"].get(u, 0) for l in grupo for u in rotulos), "unidades_por_destino": dict(destino),
            }
        return saida

    familias = {"bases_soltas": ("Base (solta)",), "clausulas": ("Cláusula", "Cláusula (solta)"),
                "outros_titulos": ("Artigo (outra forma)", "Base (outra forma)", "número (outra forma)", "número romano", "outro")}
    em_vigor = [l for l in linhas if vigencia_no_dre(l["estado"]) == "em_vigor"]
    soltos = [l for l in em_vigor if l.get("artigos_soltos_no_texto")]
    return {
        "registos": len(linhas),
        **{nome: conta([l for l in linhas if any(u in l["unidades"] for u in rotulos)], rotulos) for nome, rotulos in familias.items()},
        "leis_com_bases_soltas": [{k: l[k] for k in ("titulo", "data", "estado", "sumario", "no_indice", "unidades", "citado_por_vigentes")}
                                  for l in sorted(linhas, key=lambda l: l["data"] or "") if l["tipo"] == "lei" and vigencia_no_dre(l["estado"]) != "sem_vigencia" and "Base (solta)" in l["unidades"]],
        "em_vigor_em_blocos_com_artigos_soltos_no_texto": {
            "registos": len(soltos), "prioritarios": sum(prioritario(l) for l in soltos), "portarias": sum(l["tipo"] == "portaria" for l in soltos),
            "artigos_soltos": sum(l["artigos_soltos_no_texto"] for l in soltos),
            "leis_e_decretos_leis_por_decada": dict(sorted(Counter((l["data"] or "0000")[:3] + "0" for l in soltos if l["tipo"] in ("lei", "decreto-lei")).items())),
        },
    }


def sem_artigos_abertos(indice: Path, hoje: str) -> tuple[list[dict], list[dict]]:
    """Os registos portugueses do índice sem um pedaço que a pesquisa possa dar como lei em vigor, e as revogações por produzir efeitos.

    Classes: `sem_pedacos`; `todos_fechados` (todos com `ate`), com ou sem ligação a outro registo; `abertos_todos_revogados`
    (todos os pedaços abertos estão revogados em `hoje`). Uma revogação que ainda não produziu efeitos não conta como
    revogação (`rag.fontes.revogado` com data): esses pedaços vão na segunda lista."""
    con = sqlite3.connect(f"file:{indice}?mode=ro", uri=True)
    docs = {r[0]: r for r in con.execute("SELECT id, titulo, tipo, data, legal_status, versao, com_historico FROM documentos WHERE id LIKE 'pt:%'")}
    ligados = {r[0] for r in con.execute("SELECT DISTINCT documento FROM relacoes WHERE tipo IN ('texto_em_vigor_em', 'redacao_atual_em')")}
    conta: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])  # pedaços, abertos, abertos não revogados, abertos com revogação por produzir efeitos
    datas: dict[str, Counter] = defaultdict(Counter)
    for documento, ate, inicio, notas in con.execute("SELECT documento, ate, substr(texto, 1, 40), notas FROM pedacos"):
        if documento not in docs:
            continue
        c = conta[documento]
        c[0] += 1
        if ate is None or ate == "":
            c[1] += 1
            if not revogado(inicio, notas or "", hoje):
                c[2] += 1
                if notas and (por_produzir := revogacao_por_produzir_efeitos(notas, hoje)):
                    c[3] += 1
                    datas[documento][por_produzir[0]] += 1
    con.close()

    def linha(i: str, classe: str | None = None) -> dict:
        _, titulo, tipo, data, estado, versao, com_historico = docs[i]
        c = conta.get(i, [0, 0, 0, 0])
        return {"id": i, "titulo": titulo, "tipo": tipo, "data": data, "estado": estado, "versao": versao, "com_historico": bool(com_historico), **({"classe": classe} if classe else {}),
                "pedacos": c[0], "abertos": c[1], "abertos_nao_revogados": c[2], "abertos_com_revogacao_por_produzir_efeitos": c[3],
                **({"efeitos_a_partir_de": dict(datas[i])} if i in datas else {})}

    sem_abertos = []
    for i in docs:
        c = conta.get(i)
        if c is None:
            classe = "sem_pedacos"
        elif c[1] == 0:
            classe = "todos_fechados_com_ligacao" if i in ligados else "todos_fechados_sem_ligacao"
        elif c[2] == 0:
            classe = "abertos_todos_revogados"
        else:
            continue
        sem_abertos.append(linha(i, classe))
    return sem_abertos, [linha(i) for i in datas]


def resumo_sem_abertos(sem_abertos: list[dict], por_produzir: list[dict]) -> dict:
    def grupo(l: dict) -> str:
        return "prioritarios" if l["tipo"] in PRIORITARIOS else "portarias" if l["tipo"] == "portaria" else "outros"

    em_vigor = [l for l in sem_abertos if l["estado"] in EM_VIGOR_NO_DRE]
    return {
        "em_vigor_no_dre": len(em_vigor),
        "em_vigor_por_classe": dict(Counter(l["classe"] for l in em_vigor)),
        "em_vigor_por_classe_e_grupo": {c: dict(Counter(grupo(l) for l in em_vigor if l["classe"] == c)) for c in sorted({l["classe"] for l in em_vigor})},
        "vigencia_desconhecida_por_classe": dict(Counter(l["classe"] for l in sem_abertos if l["estado"] == "unknown")),
        "sem_vigencia_por_classe": dict(Counter(l["classe"] for l in sem_abertos if l["estado"] not in EM_VIGOR_NO_DRE and l["estado"] != "unknown")),
        "revogacoes_por_produzir_efeitos": {
            "registos": len(por_produzir), "pedacos": sum(l["abertos_com_revogacao_por_produzir_efeitos"] for l in por_produzir),
            "por_data": dict(sorted(sum((Counter(l["efeitos_a_partir_de"]) for l in por_produzir), Counter()).items())),
            "registos_em_que_sao_todos_os_abertos_em_vigor": sum(l["abertos_nao_revogados"] == l["abertos_com_revogacao_por_produzir_efeitos"] for l in por_produzir),
        },
    }


# ------------------------------------------------------------------ resumo e tabelas


def _jsonl(caminho: Path, linhas: list[dict]) -> None:
    caminho.write_text("".join(json.dumps(linha, ensure_ascii=False, sort_keys=True) + "\n" for linha in linhas), encoding="utf-8")


def _tabela(cabecalho_: list[str], linhas: list[list]) -> str:
    numericas = [k > 0 and bool(linhas) and all(isinstance(l[k], int | float) or l[k] in ("", "—") for l in linhas) for k in range(len(cabecalho_))]
    saida = ["| " + " | ".join(cabecalho_) + " |", "|" + "|".join("--:" if n else "---" for n in numericas) + "|"]
    saida += ["| " + " | ".join(str(c).replace("|", "\\|") for c in linha) + " |" for linha in linhas]
    return "\n".join(saida)


ORDEM_TEXTO = ["consolidado_dre", "consolidado_leis_portugal", "texto_noutro_registo", "original_e_o_texto_em_vigor", "alteracao_por_aplicar",
               "alteracao_so_em_imagem", "nao_triado", "revogado_por_inteiro", "sem_texto"]
ORDEM_DESCONHECIDA = ["revogado_segundo_a_relacao_do_dre", "revogacao_lida_no_texto_de_outro_diploma", "temporario_ou_orcamental", "ato_de_alteracao",
                      "alterado_depois_e_sem_revogacao", "sem_indicio_de_revogacao"]
POR_FECHAR = ("alteracao_por_aplicar", "alteracao_so_em_imagem", "nao_triado", "revogado_por_inteiro")


def pedacos_no_indice(lista_obras: list[dict], indice: Path) -> None:
    """Quantos pedaços de cada cópia o índice dá como texto atual (`ate` vazio): é o que a pesquisa pode servir."""
    con = sqlite3.connect(f"file:{indice}?mode=ro", uri=True)
    for obra in lista_obras:
        for copia in obra["copias"]:
            parte = re.sub(r" ?\(\d+\.ª numeração\)$", "", copia["parte"])
            copia["pedacos_atuais_no_indice"] = con.execute(
                "SELECT count(*) FROM pedacos WHERE documento = ? AND parte = ? AND (ate IS NULL OR ate = '')", (copia["id"], parte)).fetchone()[0]
    con.close()


def resumo_das_obras(lista_obras: list[dict]) -> dict:
    vivas = [o for o in lista_obras if o["em_vigor"]]
    mortas = [o for o in lista_obras if not o["em_vigor"]]
    fora = [o for o in vivas if o["atual_fora_da_origem"]]

    def origem(o: dict) -> dict:
        return next(c for c in o["copias"] if c["papel"] == "origem" or c["id"] == o["origem"])

    return {
        "obras": len(lista_obras), "com_texto_atual_num_registo_em_vigor": len(vivas),
        "que_ja_nao_vigoram_com_copias_servidas": sum(any(c["servida_como_vigente"] for c in o["copias"]) for o in mortas),
        "copias_de_texto_que_ja_nao_vigora_servidas": sum(c["servida_como_vigente"] for o in mortas for c in o["copias"]),
        "artigos_em_copias_de_texto_que_ja_nao_vigora": sum(c["artigos"] for o in mortas for c in o["copias"] if c["servida_como_vigente"]),
        "texto_atual_fora_do_registo_de_origem": len(fora),
        "das_quais_a_origem_aponta_para_o_atual": sum(o["origem_ligada_ao_atual"] for o in fora),
        "das_quais_a_origem_esta_no_indice_como_vigente": sum(origem(o)["servida_como_vigente"] for o in fora),
        "das_quais_a_origem_tem_consolidacao_propria_mais_antiga": sum(origem(o)["consolidado_por"] is not None and origem(o)["desatualizada"] for o in fora),
        "das_quais_com_numeracao_diferente": sum(o["com_epigrafe"] >= 20 and o["epigrafes_iguais"] / o["com_epigrafe"] < 0.8 for o in fora),
        "copias_desatualizadas_servidas": sum(o["copias_desatualizadas_servidas"] for o in vivas),
        "artigos_em_copias_desatualizadas_servidas": sum(o["artigos_em_copias_desatualizadas_servidas"] for o in vivas),
        "obras_com_copias_desatualizadas_servidas": sum(o["copias_desatualizadas_servidas"] > 0 for o in vivas),
        "no_indice": None if not any("pedacos_atuais_no_indice" in c for o in lista_obras for c in o["copias"]) else {
            "copias_desatualizadas_com_pedacos_atuais": sum(c["desatualizada"] and c.get("pedacos_atuais_no_indice", 0) > 0 for o in vivas for c in o["copias"]),
            "pedacos_atuais_em_copias_desatualizadas": sum(c.get("pedacos_atuais_no_indice", 0) for o in vivas for c in o["copias"] if c["desatualizada"]),
            "pedacos_atuais_nas_copias_atuais": sum(c.get("pedacos_atuais_no_indice", 0) for o in vivas for c in o["copias"] if c["papel"] == "atual"),
            "pedacos_atuais_em_copias_de_texto_que_ja_nao_vigora": sum(c.get("pedacos_atuais_no_indice", 0) for o in mortas for c in o["copias"] if c["papel"] != "atual" and c["estado"] in VIGENTES),
        },
        "copias_desatualizadas_servidas_por_tipo_de_registo": dict(Counter(
            ("consolidado " + c["consolidado_por"] if c["consolidado_por"] else "original") + (" (anexo com «republica» no nome)" if "republica" in c["parte"].lower() else "")
            for o in vivas for c in o["copias"] if c["desatualizada"] and c["servida_como_vigente"])),
    }


def inventario(args: argparse.Namespace) -> dict:
    raiz, export = Path(args.raiz), Path(args.export)
    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)
    acervo = carregar(export)
    cabecalhos = {i: cabecalho(raiz / d["path"]) for i, d in acervo.docs.items() if d["version_kind"] == "consolidated" and (raiz / d["path"]).exists()}
    triagem_ficheiro = raiz / "consolidacao" / "resultados-escala.jsonl"
    triagem = {r["id"]: r for r in map(json.loads, triagem_ficheiro.read_text(encoding="utf-8").splitlines())} if triagem_ficheiro.exists() else {}
    propostas_ficheiro = raiz / "reports" / "vigencia-proposta.jsonl"
    propostas = {r["id"]: r for r in map(json.loads, propostas_ficheiro.read_text(encoding="utf-8").splitlines())} if propostas_ficheiro.exists() else {}
    marcas_ficheiro = raiz / "consolidacao" / "auditoria" / "vigencia-revista.jsonl"
    marcas = {r["id"]: r["marca"] for r in map(json.loads, marcas_ficheiro.read_text(encoding="utf-8").splitlines())} if marcas_ficheiro.exists() else {}

    sitemap = None
    if args.descarregar_sitemap:
        pedido = urllib.request.Request(SITEMAP_CONSOLIDADOS, headers={"User-Agent": "leis-portugal-inventario"})
        with urllib.request.urlopen(pedido, timeout=120) as resposta:  # noqa: S310 (endereço fixo do DRE)
            sitemap = ler_sitemap(resposta.read())
    elif args.sitemap_consolidados:
        sitemap = ler_sitemap(Path(args.sitemap_consolidados).read_bytes())

    resumo: dict = {"gerado": args.hoje, "export": {"documentos_pt": len(acervo.docs), "ficheiro": export.name}, "com_sitemap": sitemap is not None, "com_indice": bool(args.indice)}

    # 2 (antes do 1, que precisa de saber onde vive o texto)
    lista_obras = obras(acervo, cabecalhos, raiz, PRIORITARIOS + ("decreto",), args.hoje)
    marcas_da_regra, fora_da_regra = redacoes_anteriores(acervo, cabecalhos, raiz, args.hoje, lista_obras=lista_obras)
    if args.indice:
        pedacos_no_indice(lista_obras, Path(args.indice))
    _jsonl(saida / "texto-em-varios-registos.jsonl", lista_obras)
    resumo["texto_em_varios_registos"] = resumo_das_obras(lista_obras)
    servidas = [c for o in lista_obras for c in o["copias"] if c["desatualizada"] and c["servida_como_vigente"]]
    resumo["texto_em_varios_registos"]["regra_das_redacoes_anteriores"] = {
        "marcas": len(marcas_da_regra), "registos_com_marcas": len({m.documento for m in marcas_da_regra}), "de_fora": len(fora_da_regra),
        "de_fora_por_motivo": dict(Counter(f["motivo"] for f in fora_da_regra).most_common()),
        "copias_desatualizadas_servidas": {"marcadas": sum(c.get("regra") == "marcada" for c in servidas), "de_fora": sum(c.get("regra") != "marcada" for c in servidas),
                                           "pedacos_atuais_das_marcadas": sum(c.get("pedacos_atuais_no_indice", 0) for c in servidas if c.get("regra") == "marcada"),
                                           "pedacos_atuais_das_de_fora": sum(c.get("pedacos_atuais_no_indice", 0) for c in servidas if c.get("regra") != "marcada")},
    }

    # 1
    linhas_texto = texto_em_vigor(acervo, cabecalhos, lista_obras, triagem, sitemap, PRIORITARIOS, marcas)
    _jsonl(saida / "texto-em-vigor-por-fechar.jsonl", sorted((l for l in linhas_texto if l["classe"] in POR_FECHAR), key=lambda l: -l["citado_por_vigentes"]))
    _jsonl(saida / "consolidados-por-atualizar.jsonl", sorted((l for l in linhas_texto if l.get("em_dia") is False), key=lambda l: -l["citado_por_vigentes"]))
    portarias = texto_em_vigor(acervo, cabecalhos, lista_obras, triagem, sitemap, ("portaria",), marcas)
    nao_consolidado = lambda l: acervo.docs[l["id"]]["version_kind"] != "consolidated" and acervo.docs[l["id"]]["text_quality"] == "texto"  # noqa: E731
    resumo["texto_em_vigor"] = {
        "universo": len(linhas_texto),
        "por_classe_e_tipo": {c: {t: n for t in PRIORITARIOS if (n := sum(l["classe"] == c and l["tipo"] == t for l in linhas_texto))} for c in ORDEM_TEXTO},
        "por_classe": dict(Counter(l["classe"] for l in linhas_texto)),
        "por_classe_e_estado": {c: dict(Counter(l["estado"] for l in linhas_texto if l["classe"] == c)) for c in ORDEM_TEXTO},
        "por_fechar_citados": {f"≥{n}": sum(l["classe"] in POR_FECHAR[:3] and l["citado_por_vigentes"] >= n for l in linhas_texto) for n in (1, 10, 50)},
        "consolidados_em_dia": sum(l.get("em_dia") is True for l in linhas_texto),
        "consolidados_com_alterador_posterior": sum(bool(l.get("alteradores_posteriores")) for l in linhas_texto),
        "consolidados_dre_com_alterador_posterior": sum(bool(l.get("alteradores_posteriores")) and l["classe"] != "consolidado_leis_portugal" for l in linhas_texto),
        "consolidados_que_o_dre_mexeu": sum(bool(l.get("dre_mexeu_depois_da_recolha")) for l in linhas_texto),
        "originais_com_alterador_novo_desde_a_triagem": sum(l["classe"] == "original_e_o_texto_em_vigor" and bool(l.get("alteradores_novos_desde_a_triagem")) for l in linhas_texto),
        "marcas_de_vigencia_revista": {
            "no_ficheiro": dict(Counter(marcas.values())),
            "prioritarios": dict(Counter(l["marca_de_vigencia"] for l in linhas_texto if "marca_de_vigencia" in l)),
            "prioritarios_por_classe": {c: n for c in ORDEM_TEXTO if (n := dict(Counter(l["marca_de_vigencia"] for l in linhas_texto if l["classe"] == c and "marca_de_vigencia" in l)))},
            "portarias": dict(Counter(l["marca_de_vigencia"] for l in portarias if "marca_de_vigencia" in l)),
            "fora_do_universo": sum(i not in {l["id"] for l in linhas_texto} | {l["id"] for l in portarias} for i in marcas),
        },
        "portarias": {"universo": len(portarias), "por_classe": dict(Counter(l["classe"] for l in portarias)),
                      "consolidados_em_dia": sum(l.get("em_dia") is True for l in portarias), "consolidados_por_atualizar": sum(l.get("em_dia") is False for l in portarias)},
        "tetos_da_sessao_coordenadora": {
            t: {"teto": teto, "medido": sum(l["tipo"] == t and nao_consolidado(l) for l in linhas_texto),
                **{c: sum(l["tipo"] == t and nao_consolidado(l) and l["classe"] == c for l in linhas_texto) for c in ORDEM_TEXTO if c not in ("consolidado_dre", "consolidado_leis_portugal", "sem_texto")}}
            for t, teto in (("lei", 867), ("decreto-lei", 3494), ("decreto-regulamentar", 421))
        },
    }

    # 3
    desconhecidos = vigencia_desconhecida(acervo, propostas, PRIORITARIOS)
    _jsonl(saida / "vigencia-desconhecida.jsonl", sorted(desconhecidos, key=lambda l: -l["citado_por_vigentes"]))
    por_ano, total_por_ano = Counter(), Counter()
    for d in acervo.docs.values():
        if d["document_type"] in ("lei", "decreto-lei") and d["series"] == "I":
            ano = (d["publication_date"] or "0000")[:4]
            total_por_ano[ano] += 1
            por_ano[ano] += d["legal_status"] == "unknown"
    resumo["vigencia_desconhecida"] = {
        "total": len(desconhecidos),
        "por_tipo": dict(Counter(l["tipo"] for l in desconhecidos)),
        "com_texto": sum(l["texto"] == "texto" for l in desconhecidos),
        "por_classe": dict(Counter(l["classe"] for l in desconhecidos)),
        "por_classe_e_tipo": {c: dict(Counter(l["tipo"] for l in desconhecidos if l["classe"] == c)) for c in ORDEM_DESCONHECIDA},
        "de_2014_em_diante": sum((l["data"] or "") >= "2014" for l in desconhecidos),
        "com_amended_by": sum(l["alteradores"] > 0 for l in desconhecidos),
        "citados_por_vigentes": {f"≥{n}": sum(l["citado_por_vigentes"] >= n for l in desconhecidos) for n in (1, 10, 50)},
        "leis_e_decretos_leis_por_ano": {a: {"desconhecida": por_ano[a], "total": total_por_ano[a]} for a in sorted(total_por_ano) if por_ano[a] and a >= "2010"},
        "leis_e_decretos_leis_antes_de_2010": sum(n for a, n in por_ano.items() if a < "2010"),
        "todos_os_tipos_1a_serie": dict(Counter(d["document_type"] for d in acervo.docs.values() if d["series"] == "I" and d["legal_status"] == "unknown").most_common(12)),
    }

    # 4
    if sitemap is not None:
        nossos = {c["url_consolidado"]: {"id": i, "lastmod": c["lastmod"]} for i, c in cabecalhos.items() if c["url_consolidado"]}
        falhas_ficheiro = raiz / "reports" / "dre_consolidated_failures.jsonl"
        falhas = {json.loads(l)["url"] for l in falhas_ficheiro.read_text(encoding="utf-8").splitlines()} if falhas_ficheiro.exists() else set()
        comparacao = comparar_sitemap(sitemap, nossos, falhas)
        for m in comparacao["mexidos_depois_da_recolha"]:
            m |= {"titulo": acervo.docs[m["id"]]["title"], "tipo": acervo.docs[m["id"]]["document_type"], "sumario": (acervo.docs[m["id"]]["summary"] or "")[:120]}
        _jsonl(saida / "dre-consolidados-em-falta.jsonl", comparacao["em_falta"])
        _jsonl(saida / "dre-consolidados-mexidos.jsonl", comparacao["mexidos_depois_da_recolha"])
        resumo["dre_consolidados"] = {
            "listados_no_sitemap": comparacao["listados"], "temos": comparacao["temos"], "em_falta": len(comparacao["em_falta"]),
            "em_falta_por_motivo": dict(Counter(e["motivo"] for e in comparacao["em_falta"])),
            "por_recolher_por_tipo": dict(Counter(e["tipo"] for e in comparacao["em_falta"] if e["motivo"] == "por_recolher").most_common()),
            "por_recolher_prioritarios": sum(e["motivo"] == "por_recolher" and e["tipo"] in PRIORITARIOS for e in comparacao["em_falta"]),
            "sem_texto_na_fonte_prioritarios": sum(e["motivo"] == "sem_texto_na_fonte" and e["tipo"] in PRIORITARIOS for e in comparacao["em_falta"]),
            "mexidos_depois_da_recolha": len(comparacao["mexidos_depois_da_recolha"]),
            "mexidos_por_tipo": dict(Counter(m["tipo"] for m in comparacao["mexidos_depois_da_recolha"]).most_common()),
            "so_nossos": len(comparacao["so_nossos"]),
            "datas_de_recolha": dict(Counter(c["recolhido"] for c in cabecalhos.values() if c["url_consolidado"]).most_common(3)),
            "sitemap_lastmod_mais_recente": max(sitemap.values()),
        }

    # 5
    antigos = antigos_sem_texto(acervo, PRIORITARIOS + ("decreto", "carta-lei"))
    _jsonl(saida / "antigos-sem-texto-citados.jsonl", [a for a in antigos if a["estado"] != "unknown" and a["citado_por_vigentes"] >= 5])
    resumo["antigos_sem_texto"] = {
        "total": len(antigos),
        "por_tipo_estado_faixa": {f"{t} / {e} / {f}": n for (t, e, f), n in sorted(Counter((a["tipo"], a["estado"], a["faixa"]) for a in antigos).items())},
        "em_vigor_segundo_o_dre": {t: sum(a["tipo"] == t and a["estado"] != "unknown" for a in antigos) for t in ("lei", "decreto-lei", "decreto")},
        "em_vigor_e_citados": {f"≥{n}": sum(a["estado"] != "unknown" and a["citado_por_vigentes"] >= n for a in antigos) for n in (1, 5, 20, 100)},
        "em_vigor_com_amended_by": sum(a["estado"] != "unknown" and a["alteradores"] > 0 for a in antigos),
        "prioritarios_com_texto_antes_de_1960": sum((d["publication_date"] or "9999") < "1960" and d["text_quality"] == "texto" and d["document_type"] in PRIORITARIOS for d in acervo.docs.values()),
        "com_texto_antes_de_1960": sum((d["publication_date"] or "9999") < "1960" and d["text_quality"] == "texto" for d in acervo.docs.values()),
        "mais_citados": [{k: a[k] for k in ("titulo", "data", "citado_por_vigentes", "sumario")} for a in antigos if a["estado"] != "unknown"][:25],
    }

    # 6
    centrais = json.loads((Path(__file__).with_name("inventario_diplomas_centrais.json")).read_text(encoding="utf-8"))["diplomas"]
    controlo = lista_de_controlo(centrais, acervo, cabecalhos, lista_obras, triagem, sitemap, raiz, marcas)
    if args.indice:
        verificar_pesquisa(controlo, Path(args.indice), raiz, acervo)
    _jsonl(saida / "diplomas-centrais.jsonl", controlo)
    resumo["diplomas_centrais"] = {
        "total": len(controlo), "sem_problemas": sum(not l["problemas"] for l in controlo), "fora_do_acervo": sum(l["id"] is None for l in controlo),
        "por_texto": dict(Counter(l.get("texto", "fora do acervo") for l in controlo)),
        "com_vigencia_desconhecida": sum("vigência desconhecida" in l["problemas"] for l in controlo),
        "com_alterador_posterior": sum(bool(l.get("alteradores_posteriores")) for l in controlo),
        "que_o_dre_mexeu": sum(bool(l.get("dre_mexeu_depois_da_recolha")) for l in controlo),
        "texto_noutro_registo": sum(bool(l.get("vive_em")) and l["vive_em"] != l["id"] for l in controlo),
        "texto_noutro_registo_sem_ligacao": sum(bool(l.get("vive_em")) and l["vive_em"] != l["id"] and acervo.texto_em_vigor_em.get(l["id"]) != l["vive_em"] for l in controlo),
        "com_copias_de_outra_data_servidas": sum(any("cópia(s) com texto de outra data" in p for p in l["problemas"]) for l in controlo),
        "pesquisa": None if not args.indice else {"verificados": sum("pesquisa_resultado" in l for l in controlo), "artigo_certo": sum(l.get("pesquisa_resultado", {}).get("certo", False) for l in controlo),
                                                  "registo_certo_outro_artigo": sum(l.get("pesquisa_resultado", {}).get("registo_certo", False) and not l["pesquisa_resultado"]["certo"] for l in controlo),
                                                  "registo_errado": sum("pesquisa_resultado" in l and not l["pesquisa_resultado"]["registo_certo"] for l in controlo)},
    }

    # 7
    resumo["fora_do_export"] = fora_do_export(acervo, raiz, export)

    # 8
    if not getattr(args, "sem_leitura", False):
        nao_lidos = leitura_dos_registos(acervo, raiz)
        gravar_leitura(saida, nao_lidos)
        resumo["leitura"] = resumo_da_leitura(nao_lidos)
    if args.indice:
        sem_abertos, por_produzir = sem_artigos_abertos(Path(args.indice), args.hoje)
        _jsonl(saida / "indice-sem-artigos-abertos.jsonl", sorted((l for l in sem_abertos if l["estado"] in EM_VIGOR_NO_DRE), key=lambda l: (l["classe"], l["tipo"] not in PRIORITARIOS, -l["pedacos"], l["id"])))
        _jsonl(saida / "revogacoes-por-produzir-efeitos.jsonl", sorted(por_produzir, key=lambda l: -l["abertos_com_revogacao_por_produzir_efeitos"]))
        resumo["indice_sem_artigos_abertos"] = resumo_sem_abertos(sem_abertos, por_produzir)

    repetidos = duplicados(acervo, PRIORITARIOS)
    _jsonl(saida / "registos-duplicados.jsonl", repetidos)
    resumo["registos_duplicados"] = {
        "diplomas": len(repetidos),
        "com_um_consolidado_e_outro_original_vigente": sum(any(r["versao"] == "consolidated" for r in g["registos"]) and any(r["versao"] != "consolidated" and r["estado"] in VIGENTES for r in g["registos"]) for g in repetidos),
        "com_estados_diferentes": sum(len({r["estado"] for r in g["registos"]}) > 1 for g in repetidos),
    }

    (saida / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (saida / "tabelas.md").write_text(tabelas(resumo, controlo, lista_obras), encoding="utf-8")
    return resumo


def tabelas(resumo: dict, controlo: list[dict], lista_obras: list[dict]) -> str:
    t = resumo["texto_em_vigor"]
    blocos = [
        f"# Inventário da camada 1: tabelas geradas\n\nGerado a {resumo['gerado']} por `scripts/inventario_camada_1.py`, a partir de `{resumo['export']['ficheiro']}` "
        f"({resumo['export']['documentos_pt']} registos portugueses). Não editar à mão: a leitura está em `reports/inventario-camada-1.md`.",
        "## 1. Texto em vigor dos diplomas alterados\n\nPrioritários da 1.ª Série, em vigor ou de vigência desconhecida, com `amended_by`.\n\n"
        + _tabela(["Classe", *PRIORITARIOS, "Total"], [[c, *[t["por_classe_e_tipo"][c].get(tp, 0) for tp in PRIORITARIOS], sum(t["por_classe_e_tipo"][c].values())] for c in ORDEM_TEXTO if t["por_classe_e_tipo"][c]]
                  + [["**Total**", *[sum(t["por_classe_e_tipo"][c].get(tp, 0) for c in ORDEM_TEXTO) for tp in PRIORITARIOS], t["universo"]]])
        + f"\n\nConsolidados em dia: {t['consolidados_em_dia']}; com alterador publicado depois da última versão: {t['consolidados_com_alterador_posterior']}; "
        f"que o DRE mexeu depois da recolha: {t['consolidados_que_o_dre_mexeu'] if resumo['com_sitemap'] else 'por medir (sem sitemap)'}.\n\n"
        "Portarias (só contagens): " + ", ".join(f"{c} {n}" for c, n in sorted(t["portarias"]["por_classe"].items(), key=lambda x: -x[1])) + ".\n\n"
        "Marcas da vigência revista (`consolidacao/auditoria/vigencia-revista.jsonl`): no ficheiro, " + (", ".join(f"{m} {n}" for m, n in sorted(t["marcas_de_vigencia_revista"]["no_ficheiro"].items())) or "nenhuma")
        + "; nos prioritários deste universo, " + (", ".join(f"{m} {n}" for m, n in sorted(t["marcas_de_vigencia_revista"]["prioritarios"].items())) or "nenhuma")
        + "; nas portarias, " + (", ".join(f"{m} {n}" for m, n in sorted(t["marcas_de_vigencia_revista"]["portarias"].items())) or "nenhuma") + ".",
    ]
    fora = [o for o in lista_obras if o["atual_fora_da_origem"] and o["em_vigor"]]
    blocos.append(f"## 2. Textos cujo texto em vigor está fora do registo que os aprovou ({len(fora)})\n\n" + _tabela(
        ["Texto de (origem)", "Texto mais recente em", "Parte", "Artigos", "Texto até", "Origem aponta para lá", "Origem servida como em vigor", "Epígrafes iguais (mesmo n.º)", "Outras cópias desatualizadas servidas"],
        [[o["origem_titulo"], o["atual_titulo"], (o["atual_parte"] or "articulado")[:60], next(c["artigos"] for c in o["copias"] if c["papel"] == "atual"), o["data_do_texto_atual"],
          "sim" if o["origem_ligada_ao_atual"] else "**não**",
          next(("sim, consolidação de " + c["data_do_texto"] if c["consolidado_por"] else "sim, texto de " + c["data_do_texto"]) if c["servida_como_vigente"] else "não" for c in o["copias"] if c["id"] == o["origem"]),
          f"{o['epigrafes_iguais']}/{o['com_epigrafe']}" if o["com_epigrafe"] else "sem epígrafes",
          "; ".join(f"{c['titulo']} ({c['data_do_texto']})" for c in o["copias"] if c["desatualizada"] and c["servida_como_vigente"] and c["id"] != o["origem"]) or "—"] for o in fora]))
    copias = [(o, c) for o in lista_obras for c in o["copias"] if c["desatualizada"] and c["servida_como_vigente"] and not (o["atual_fora_da_origem"] and c["id"] == o["origem"])]
    mortas = [(o, c) for o in lista_obras if not o["em_vigor"] for c in o["copias"] if c["servida_como_vigente"]]
    copias.sort(key=lambda oc: -oc[1]["artigos"])
    blocos.append(f"## 2-B. Cópias com texto de outra data, em registos em vigor ({len(copias)}; as 60 maiores)\n\n" + _tabela(
        ["Texto", "Cópia em", "Parte", "Artigos", "Texto da cópia até", "Texto atual em", "Texto atual até"],
        [[o["obra"][:60], c["titulo"], (c["parte"] or "articulado")[:50], c["artigos"], c["data_do_texto"], o["atual_titulo"], o["data_do_texto_atual"]] for o, c in copias[:60]]))
    blocos.append(f"## 2-C. Cópias, em registos em vigor, de textos cujo registo mais recente já não vigora ({len(mortas)})\n\n" + _tabela(
        ["Texto", "Cópia em", "Parte", "Artigos", "Texto da cópia até", "Registo mais recente", "Estado desse registo"],
        [[o["obra"][:60], c["titulo"], (c["parte"] or "articulado")[:50], c["artigos"], c["data_do_texto"], o["atual_titulo"], next(x["estado"] for x in o["copias"] if x["papel"] == "atual")]
         for o, c in sorted(mortas, key=lambda oc: -oc[1]["artigos"])]))
    v = resumo["vigencia_desconhecida"]
    blocos.append("## 3. Vigência desconhecida (prioritários, 1.ª Série)\n\n" + _tabela(
        ["Classe", *PRIORITARIOS, "Total"],
        [[c, *[v["por_classe_e_tipo"][c].get(tp, 0) for tp in PRIORITARIOS], sum(v["por_classe_e_tipo"][c].values())] for c in ORDEM_DESCONHECIDA if v["por_classe_e_tipo"][c]]
        + [["**Total**", *[v["por_tipo"].get(tp, 0) for tp in PRIORITARIOS], v["total"]]]))
    blocos.append("Leis e decretos-leis de vigência desconhecida por ano de publicação (desde 2010):\n\n" + _tabela(
        ["Ano", "Desconhecida", "Publicados", "%"], [[a, n["desconhecida"], n["total"], round(100 * n["desconhecida"] / n["total"])] for a, n in v["leis_e_decretos_leis_por_ano"].items()]))
    blocos.append("## 6. Lista de controlo dos diplomas centrais\n\n" + _tabela(
        ["Área", "Diploma", "Aprovado por", "Texto em vigor em", "Vigência", "Texto até", "Em dia", "Problemas"],
        [[l["area"], l["nome"], l["diploma"],
          (l.get("vive_em_titulo") or "—") + (f", {l['parte'][:40]}" if l.get("parte") else "") + (f" ({l['texto'].replace('consolidado_', '').replace('_', ' ')})" if l.get("texto") else ""),
          l.get("estado", "—"), l.get("consolidado_ate") or "—", "—" if "em_dia" not in l else "sim" if l["em_dia"] else "**não**", "; ".join(l["problemas"]) or "—"] for l in controlo]))
    if "leitura" in resumo:
        le = resumo["leitura"]
        nomes = {"bases_soltas": "«Base N» solta no texto", "clausulas": "«Cláusula N»", "outros_titulos": "títulos de nível 6 de outra forma"}
        destinos = ["em_blocos", "dentro_de_um_artigo", "cortada", "fora_do_indice"]
        blocos.append(
            "## 8. O que o índice não lê como artigos\n\nRegistos portugueses com texto. «Em vigor»: `in_force` ou `partially_in_force` no DRE. O leitor conhece "
            "`###### Artigo`, `###### ARTIGO`, `###### Base`, `###### 1.º` e os anexos `## Anexo` e `## ANEXO`; aqui conta-se o que fica por ler como unidade. "
            "Destino das unidades dos registos em vigor: em blocos de ~300 palavras, dentro do texto de um artigo, cortada (para lá dos 30 000 caracteres do pedaço) "
            "e fora do índice (antes do primeiro artigo do diploma ou do anexo).\n\n" + _tabela(
                ["Unidade", "Registos", "Em vigor", "Dos quais prioritários", "Vigência desconhecida", "Unidades (em vigor)", "Em blocos", "Dentro de um artigo", "Cortadas", "Fora do índice"],
                [[nomes[f], le[f]["registos"], le[f]["por_vigencia"]["em_vigor"]["registos"], le[f]["por_vigencia"]["em_vigor"]["prioritarios"], le[f]["por_vigencia"]["desconhecida"]["registos"],
                  le[f]["por_vigencia"]["em_vigor"]["unidades"], *[le[f]["por_vigencia"]["em_vigor"]["unidades_por_destino"].get(d, 0) for d in destinos]] for f in nomes]))
        so = le["em_vigor_em_blocos_com_artigos_soltos_no_texto"]
        blocos.append(
            f"Em vigor, em blocos, com «Artigo 1.º … Art. 2.º …» no início das linhas (teto, por expressão regular): {so['registos']} registos "
            f"({so['prioritarios']} prioritários, {so['portarias']} portarias), {so['artigos_soltos']} artigos.")
        if le["leis_com_bases_soltas"]:
            blocos.append("Leis em vigor ou de vigência desconhecida com bases soltas no texto:\n\n" + _tabela(
                ["Lei", "Data", "Vigência", "Sumário", "No índice", "Bases", "Citada por vigentes"],
                [[l["titulo"], l["data"], l["estado"], l["sumario"][:90], l["no_indice"], sum(l["unidades"].values()), l["citado_por_vigentes"]] for l in le["leis_com_bases_soltas"]]))
    if "indice_sem_artigos_abertos" in resumo:
        ia = resumo["indice_sem_artigos_abertos"]
        classes = {"sem_pedacos": "sem um único pedaço", "todos_fechados_com_ligacao": "todos os pedaços fechados, com ligação ao registo que tem o texto",
                   "todos_fechados_sem_ligacao": "todos os pedaços fechados, sem ligação", "abertos_todos_revogados": "pedaços abertos, todos revogados"}
        r = ia["revogacoes_por_produzir_efeitos"]
        blocos.append(
            f"## 8-B. Em vigor no DRE e sem um artigo aberto e não revogado no índice ({ia['em_vigor_no_dre']})\n\n" + _tabela(
                ["Classe", "Prioritários", "Portarias", "Outros", "Total"],
                [[classes[c], g.get("prioritarios", 0), g.get("portarias", 0), g.get("outros", 0), sum(g.values())] for c, g in ia["em_vigor_por_classe_e_grupo"].items()])
            + f"\n\nRevogações publicadas que ainda não produziram efeitos (os artigos contam como em vigor até lá): {r['pedacos']} artigos em {r['registos']} registos "
            f"({r['registos_em_que_sao_todos_os_abertos_em_vigor']} em que são todos os artigos em vigor do registo); por data de efeitos: "
            + ", ".join(f"{d} {n}" for d, n in r["por_data"].items()) + ".")
    return "\n\n".join(blocos) + "\n"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--raiz", default=str(RAIZ), help="raiz do repositório (com data/)")
    parser.add_argument("--export", default=None, help="exports/leis-portugal.sqlite (por omissão, o desta cópia ou o da pasta principal)")
    parser.add_argument("--saida", default=None, help="pasta de saída (por omissão, reports/inventario-camada-1)")
    parser.add_argument("--sitemap-consolidados", default=None, help="ficheiro com o sitemap da legislação consolidada do DRE")
    parser.add_argument("--descarregar-sitemap", action="store_true", help=f"descarrega {SITEMAP_CONSOLIDADOS}")
    parser.add_argument("--indice", default=None, help="índice do RAG, para verificar «artigo N.º do Código X» (só leitura)")
    parser.add_argument("--sem-leitura", action="store_true", help="salta a secção 8 (lê todos os .md do data/: cerca de um minuto e meio)")
    parser.add_argument("--hoje", default=date.today().isoformat())
    args = parser.parse_args(argv)
    args.export = args.export or str(export_por_omissao(Path(args.raiz)))
    args.saida = args.saida or str(Path(args.raiz) / "reports" / "inventario-camada-1")
    resumo = inventario(args)
    print(json.dumps({k: v for k, v in resumo.items() if k in ("texto_em_varios_registos", "diplomas_centrais", "dre_consolidados")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
