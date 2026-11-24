"""Aplicação ao acervo dos consolidados verificados às cegas.

Para cada diploma verificado às cegas com todos os artigos `certo` (os aplicados por regra e os
juntados com o LLM, `llm/juntados.jsonl`), o registo em `data/` passa a ter o texto em vigor
(`piloto/<caminho>.md`), como os consolidados do DRE:

- o corpo é o consolidado, com as notas "> Alterado pelo/a …" nos artigos alterados;
- `version.kind` passa a `consolidated`, com um rótulo que diz que a consolidação é do
  leis-portugal e não tem valor oficial, e `consolidation_date` é a data em que a alteração
  entrou em vigor;
- ao lado fica `<registo>.versoes.json` com duas versões, a original e a alterada, para o
  `leis-portugal version-at` dar o texto em qualquer data.

Antes de gravar, confirma-se que o consolidado é o que foi verificado às cegas (a entrada da
última ronda em que o diploma esteve) e que o original em `data/` é o que a verificação
recebeu. Um diploma que falhe uma das duas fica como estava. Uma nova recolha do DRE não
substitui o consolidado, porque o texto publicado tem menos precedência
(`LegalRecord.precedence`); uma versão consolidada do próprio DRE substitui-o.

**Escala:** as rondas 6 em diante são lotes, `entrada-piloto-N-lote-NN.jsonl` com
`saida-piloto-N-lote-NN.jsonl` ao lado (uma ronda pode ter só alguns lotes verificados: os
diplomas dos lotes sem saída ficam por verificar, não se aplicam). Os diplomas vêm de
`resultados-escala.jsonl` e `selecao-escala.jsonl` e podem ter vários alteradores aplicados: a
versão alterada leva todos em `acts` (só os que deram instruções ao texto) e a data em que o
último entrou em vigor. O texto de cada passo intermédio não se guarda, por isso o histórico
tem duas versões, a original e a consolidada com todas as alterações.

`--dry-run` não grava nada e diz quantos passam em cada controlo. `--supor-verificados` (só com
`--dry-run`) conta os diplomas como se todos os artigos fossem `certo`, para ver quantos passariam
nos controlos técnicos (o consolidado é o da entrada, o original em `data/` é o verificado, o
histórico renderiza o consolidado) antes de haver saídas da verificação.

Uso: `python consolidacao/acervo.py [--dry-run [--supor-verificados]]`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

from texto import RAIZ, corpo, front_matter

from leis_portugal.domain.history import HISTORY_SCHEMA, render_version, summarize
from leis_portugal.domain.record import Version
from leis_portugal.infrastructure.repository import Acervo


PASTA = RAIZ / "consolidacao"
VERIFICACAO = PASTA / "verificacao"


def rondas() -> list[tuple[Path, Path]]:
    """Os pares (entrada, saída) por ordem de ronda: o ficheiro único das rondas 1 a 5 e os lotes
    das seguintes. Uma entrada sem saída ao lado (lote ainda por verificar) fica no par com o
    caminho da saída que faltar."""
    pares = [(VERIFICACAO / "entrada-piloto.jsonl", VERIFICACAO / "saida-piloto.jsonl")]
    numeros = sorted({int(m.group(1)) for f in VERIFICACAO.glob("entrada-piloto-*.jsonl") if (m := re.match(r"entrada-piloto-(\d+)", f.name))})
    for n in numeros:
        unico = VERIFICACAO / f"entrada-piloto-{n}.jsonl"
        if unico.exists():
            pares.append((unico, VERIFICACAO / f"saida-piloto-{n}.jsonl"))
        for lote in sorted(VERIFICACAO.glob(f"entrada-piloto-{n}-lote-*.jsonl")):
            pares.append((lote, lote.with_name(lote.name.replace("entrada-", "saida-"))))
    return pares

# Os 24 com todos os artigos `certo` e o Decreto-Lei n.º 513-M/79, cuja `dúvida` (a revogação
# do artigo 19.º só produz efeitos com a entrada em vigor do Código dos Regimes Contributivos)
# se resolve com a data: a Lei n.º 110/2009 e o Código entraram em vigor a 2011-01-01, e as
# alterações posteriores ao artigo 5.º dela não tocam na alínea a). Ficam de fora o Decreto
# Legislativo Regional n.º 13/98/A e a Lei n.º 10/2012 (ver README, "Resultado da verificação
# às cegas").
DUVIDAS_RESOLVIDAS = {"pt:dre:430016:por"}
DE_FORA = {
    "pt:dre:431229:por", "pt:dre:542458:por",
    # Ronda 112: passaram às cegas, mas a segunda leitura (jurídica) encontrou um erro que a
    # verificação letra a letra não apanha (README, "Ronda 112").
    "pt:dre:314061:por",   # Decreto 47780: alterações do imposto de um só ano aplicadas como redação permanente
    "pt:dre:488485:por",   # DL 205/2009: alterações ao ECDU (DL 448/79) aplicadas ao estatuto republicado em anexo
    "pt:dre:674410:por",   # Portaria 367/72: as assinaturas do original desaparecem com a nova redação do art. 16.º
    "pt:dre:551192:por",   # Portaria 719-C/2008: instrução sobre a numeração antiga do art. 9.º apaga o n.º 3 em vigor
    "pt:dre:617289:por",   # Portaria 809-E/94: regime transitório de 1997 substitui o art. 73.º inteiro
    "pt:dre:2336625:por",  # DN 18-A/2010: alínea c) do n.º 1 do art. 2.º revogada por um alterador fora da cadeia
    "pt:dre:339835:por",   # DLR 28/2000/A: arts. 7.º e 16.º ficam com duas versões (blocos soltos do original)
    "pt:dre:531186:por",   # Portaria 448-A/2001: segue a republicação e perde o n.º 4 do art. 10.º, que ninguém revogou
    "pt:dre:302908:por",   # Portaria 572/92: a concessão foi extinta pela Portaria 56/2000
    # Ronda 112: a resposta só desfaz uma regra mal aplicada e o texto fica igual ao original; uma
    # consolidação sem mudança não se aplica (como o DL 349/89).
    "pt:dre:161503:por", "pt:dre:510178:por", "pt:dre:520432:por", "pt:dre:667357:por",
    # Ronda 113, pela segunda leitura: o diploma deixou de vigorar e o consolidado tirava-lhe o aviso.
    "pt:dre:402278:por",   # Portaria 667-S4/93: concessão de caça extinta pela Portaria 222/2000
    "pt:dre:276236:por",   # Portaria 640-F4/94: zona de caça extinta em parte e caducada (Portaria 1105/2007)
    "pt:dre:402281:por",   # Portaria 667-S7/93: área e prazo ultrapassados pela Portaria 1154/2005 (renovação até 2017)
    "pt:dre:613430:por",   # Portaria 1086/2000: vigência suspensa pela Portaria 398/2005
    "pt:dre:570507:por",   # DL 418-B/98: a sociedade dura até à entidade da Casa da Música; art. 7.º-A remete para o n.º 3 eliminado
    # Ronda 113: igual ao original depois de desfazer a regra mal aplicada.
    "pt:dre:438049:por",
    # Ronda 114 (bloco 3), pela segunda leitura: erro no texto que a verificação letra a letra não apanha.
    # DLR 12/93/M (pt:dre:346486): faltava a revogação do art. 11.º (Lei 110/2009, na redação da Lei 64-B/2011);
    # saiu da lista na ronda 121, que a aplicou e passou às cegas e na segunda leitura.
    "pt:dre:453241:por",   # DL 329/83: falta a retificação de 31/8/1983 à al. b) do n.º 3 do art. 8.º
    "pt:dre:455150:por",   # Portaria 828/2008: faltam as Decl. Ret. 58/2008 e 32-A/2010 (arts. 10.º e 16.º, anexo III)
    "pt:dre:455670:por",   # Portaria 846/2008: falta a Decl. Ret. 59/2008 (anexo II)
    "pt:dre:492985:por",   # Portaria 813/2009: falta a Decl. Ret. 67/2009 (art. 2.º, anexos I e II)
    "pt:dre:674621:por",   # Portaria 842/91: tabela C sem a Decl. Ret. 141/92; tabelas só das épocas 1991-1993
    "pt:dre:291436:por",   # Portaria 487/94: o DL 263/2002 revoga também os n.os 1.º e 2.º
    "pt:dre:451605:por",   # Decreto do Governo 35/83: o DG 14/85 substitui o n.º 2) do art. 2.º inteiro
    # Ronda 114: os 12 que a segunda leitura tirou por já não vigorarem (o texto estava certo)
    # voltaram a entrar a 19/11/2026, com a marca em `auditoria/vigencia-revista.jsonl`: a política
    # é não tirar consolidações por vigência (`consolidacao/vigencia.py`).
    # Ronda 114: dúvida sobre a vigência, sem ato expresso no acervo (fica de fora por regra).
    "pt:dre:197516:por",   # Portaria 176/98: mestrado do DL 216/92, revogado pelo DL 74/2006 (adequação até 2009-2010)
    "pt:dre:405324:por",   # Portaria 1546/2002: idem
    "pt:dre:406366:por",   # Portaria 1205/97: licenciatura anterior a Bolonha; por coerência com as duas de cima
    "pt:dre:194625:por",   # Portaria 769/97: idem
    "pt:dre:417639:por",   # Portaria 711/87: plano de estudos substituído pela Deliberação 1112/2003
    "pt:dre:663531:por",   # Portaria 705/91: concessão de caça de 21 anos acabou em 2012, sem renovação no acervo
    "pt:dre:160371:por",   # Decreto 44598: draubaque de «milho ultramarino»
    "pt:dre:1088946:por",  # DN 5/2012: ajuda única à seca de 2012; por coerência com a Portaria 1020/2009
    "pt:dre:415444:por",   # Portaria 1307-B/93: regulamenta o DL 275-A/93, só mantida transitoriamente (DL 191/99, art. 50.º); como a 1411/95
    # Ronda 114: igual ao original.
    "pt:dre:300610:por",   # DL 78/2002
    # Verificado na ronda 6 e nunca aplicado; fora do lote da ronda 112 e sem a segunda leitura.
    "pt:dre:606505:por",
}

def _fora_da_camada1() -> set[str]:
    """Camada 1 (`camada1.py`, ronda 115): os diplomas da onda cujo estado não é «aplicar». Um que passou às
    cegas pode ter sido recusado na segunda leitura jurídica (uma retificação ou uma revogação por aplicar);
    o motivo está em `auditoria/camada1-estado.jsonl` (onda 1) e `auditoria/camada1-estado-onda-N.jsonl` (ondas seguintes).
    Um diploma de uma onda (`camada1/onda-N.jsonl`) que ainda não tem estado também fica de fora: só entra com «aplicar»."""
    fora: set[str] = set()
    for onda in sorted((PASTA / "camada1").glob("onda-*.jsonl")):
        n = onda.stem.split("-")[1]
        f = PASTA / "auditoria" / ("camada1-estado.jsonl" if n == "1" else f"camada1-estado-onda-{n}.jsonl")
        aplicar = {d["id"] for d in map(json.loads, f.read_text(encoding="utf-8").splitlines()) if d["estado"] == "aplicar"} if f.exists() else set()
        fora |= {d["id"] for d in map(json.loads, onda.read_text(encoding="utf-8").splitlines()) if d["id"] not in aplicar}
    return fora


DE_FORA |= _fora_da_camada1()

# Consolidações refeitas que passaram às cegas mas não substituem a nossa anterior, por serem
# menos fiéis ao original num ponto que a verificação não apanhou.
NAO_SUBSTITUIR = {
    # A refeita (27/10 → bloco de novembro) só corrige uma nota "Alterado" para "Revogado", mas
    # tira os parênteses de todas as epígrafes do original ("ARTIGO 1.º — (Conceito)").
    "pt:dre:183049:por": "a refeita tira os parênteses das epígrafes do original",
}
ROTULO = "Versão consolidada pelo leis-portugal, sem valor oficial: alterações aplicadas por regra e verificadas às cegas"
ROTULO_LLM = "Versão consolidada pelo leis-portugal, sem valor oficial: alterações aplicadas com um LLM e verificadas às cegas"
_NOTA_PILOTO = re.compile(r"^> (?:Alterado|Aditado|Revogado|Retificado) pelo/a .*, publicado em \d{4}-\d{2}-\d{2}\.\n\n?", re.M)
_NOTA = re.compile(r"^> ((?:Alterado|Aditado|Revogado|Retificado) pelo/a .*)$", re.M)
_TITULO = re.compile(r"^#{1,6} ", re.M)
_OPERACAO = {"revogar": "Revoga", "aditar": "Adita", "retificar": "Retifica"}


def _sem_problemas(diploma: dict) -> bool:
    """A linha do diploma na saída da verificação: nada em falta nem a mais, e nada mudado fora
    dos artigos (o verificador escreve "sem alterações…" quando está bem)."""
    listas = ("instrucoes_em_falta", "artigos_em_falta", "artigos_a_mais")
    return not any(diploma.get(k) for k in listas) and str(diploma.get("fora_dos_artigos") or "").startswith("sem alterações")


def verificados(supor_certos: bool = False) -> dict[str, dict]:
    """A entrada da última ronda de cada diploma, se todos os artigos dessa ronda são `certo`
    (ou a dúvida está resolvida) e o diploma não tem problemas fora dos artigos. Um diploma cuja
    última entrada não tem saída (lote por verificar) não está verificado, mesmo que uma ronda
    anterior o tenha aprovado com outro texto. Com `supor_certos` (dry-run) conta-se como certo
    tudo o que não tem saída."""
    entradas: dict[str, dict] = {}
    vereditos: dict[str, set[str]] = {}
    for entrada, saida in rondas():
        ronda: dict[str, set[str]] = {}
        if saida.exists():
            for linha in saida.read_text(encoding="utf-8").splitlines():
                item = json.loads(linha)
                if "veredicto" in item:
                    ronda.setdefault(item["id"], set()).add(item["veredicto"])
                elif not _sem_problemas(item):
                    ronda.setdefault(item["id"], set()).add("problema no diploma")
        for linha in entrada.read_text(encoding="utf-8").splitlines():
            item = json.loads(linha)
            entradas[item["id"]] = item
            vereditos[item["id"]] = ronda.get(item["id"], {"certo"} if supor_certos and not saida.exists() else set())
        for id_, v in ronda.items():  # o que a saída traz e a entrada não tem (não deve haver)
            vereditos.setdefault(id_, v)
    return {
        id_: item for id_, item in entradas.items()
        if id_ not in DE_FORA and (vereditos.get(id_) == {"certo"} or id_ in DUVIDAS_RESOLVIDAS)
    }


def blocos(texto: str) -> list[str]:
    """O corpo sem o título `# …`, dividido nos títulos (artigos, capítulos, anexos)."""
    texto = re.sub(r"\A# [^\n]*\n+", "", texto.strip())
    partes = [0, *(m.start() for m in _TITULO.finditer(texto) if m.start())]
    return [texto[a:b].strip() for a, b in zip(partes, [*partes[1:], len(texto)], strict=True) if texto[a:b].strip()]


def historico(id_: str, titulo: str, original: str, consolidado: str, versoes: list[dict]) -> dict:
    fragmentos: dict[str, dict] = {}

    def chaves(texto: str, desde: str | None) -> list[str]:
        lista = []
        for bloco in blocos(texto):
            chave = hashlib.sha256(bloco.encode("utf-8")).hexdigest()[:16]
            fragmentos.setdefault(chave, {
                "fragment_id": None,
                "type": None,
                "heading": bloco.splitlines()[0].lstrip("#").strip() if bloco.startswith("#") else None,
                "in_force_from": desde if _NOTA.search(bloco) else None,
                "changed_by": _NOTA.findall(bloco),
                "markdown": bloco,
            })
            lista.append(chave)
        return lista

    primeira, segunda = versoes
    primeira["fragments"] = chaves(original, None)
    segunda["fragments"] = chaves(consolidado, segunda["date"])
    return {
        "schema": HISTORY_SCHEMA,
        "id": id_,
        "consolidated_url": None,
        "consolidated_by": "leis-portugal (consolidacao/, fase 2 do PLANO-RAG.md)",
        "source_lastmod": None,
        "versions": [primeira, segunda],
        "fragments": fragmentos,
    }


def _sem_titulo(texto: str) -> str:
    return re.sub(r"\A# [^\n]*\n+", "", texto.strip())


def _linhas(texto: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", texto)


def _original_do_historico(acervo: Acervo, caminho: Path, titulo: str) -> list[str] | None:
    """Os blocos da versão 1 do histórico gravado por uma consolidação do leis-portugal."""
    dados = acervo.read_history(caminho)
    if not dados or not str(dados.get("consolidated_by") or "").startswith("leis-portugal") or len(dados.get("versions") or []) < 2:
        return None
    return blocos(render_version(dados, dados["versions"][0], title=titulo))


def em_vigor(metadados: dict) -> str:
    entrada = (metadados.get("entry_into_force") or {}).get("date")
    return entrada or (metadados.get("entry_into_force_dates") or [None])[0] or metadados["publication_date"]


def data_da_versao(alteradores: list[tuple[dict, dict]], original: dict) -> str:
    """A data da versão consolidada: a entrada em vigor do último alterador que não é uma
    declaração de retificação. Uma retificação reporta os efeitos à entrada em vigor do texto
    retificado (Lei 74/98, art. 5.º, n.º 4), por isso não adia a versão; só com retificações, a
    versão vale desde a entrada em vigor do original."""
    datas = [em_vigor(meta) for a, meta in alteradores if not a.get("retificacao")]
    return max(datas) if datas else em_vigor(original)


def _lista(texto: Path) -> list[dict]:
    return [json.loads(l) for l in texto.read_text(encoding="utf-8").splitlines()]


def alteradores_aplicados(resultado: dict, registo_selecao: dict) -> list[dict]:
    """Os diplomas que alteram o texto e cujas instruções ficaram aplicadas, por ordem de
    aplicação: o `alterador` do piloto ou, na escala, os `passos` com alterações aplicadas."""
    if "alteradores" not in registo_selecao:
        return [registo_selecao["alterador"]]
    aplicados = set(resultado["alteradores_ids"]) if "alteradores_ids" in resultado else {p["id"] for p in resultado.get("passos", []) if p.get("aplicadas")}
    return [a for a in registo_selecao["alteradores"] if a["id"] in aplicados]


def _selecao_de(id_: str, resultado: dict, selecao: dict, selecao_escala: dict) -> dict:
    """A seleção do diploma. Um juntado da escala (com `alteradores_ids`) usa a da escala, que tem
    os alteradores recolhidos depois do piloto; o piloto pode ter o mesmo diploma com um alterador
    que então não estava no acervo."""
    if "alteradores_ids" in resultado and id_ in selecao_escala:
        return selecao_escala[id_]
    return selecao[id_]


def retificados_por_regra() -> set[str]:
    """Os registos a que `retificacoes.py`/`retificacoes_llm.py` aplicaram retificações fora da
    cadeia, aqueles a que `anexos_alteradores.py` aplicou anexos de alteradores e `revogacoes.py` revogações
    registadas só como `repealed_by`: uma nova corrida
    não os escreve por cima."""
    ids: set[str] = set()
    # também os corrigidos por `texto_antigo.py`: o piloto deles ainda tem o texto antigo, e uma nova corrida
    # repunha-o (aconteceu na ronda 117 com o DL 99/94 e o DL 106/97)
    for nome in ("retificacoes-aplicadas.jsonl", "anexos-aplicados.jsonl", "plantas-aplicadas.jsonl", "revogacoes-aplicadas.jsonl",
                 "texto-antigo-corrigidos.jsonl"):
        caminho = PASTA / "auditoria" / nome
        if caminho.exists():
            ids |= {json.loads(l)["id"] for l in caminho.read_text(encoding="utf-8").splitlines() if l.strip()}
    return ids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--supor-verificados", action="store_true", help="com --dry-run: conta como `certo` os lotes sem saída")
    args = parser.parse_args()
    if args.supor_verificados and not args.dry_run:
        parser.error("--supor-verificados só com --dry-run")
    acervo = Acervo(RAIZ)
    retificados = retificados_por_regra()
    resultados = {r["id"]: r for r in _lista(PASTA / "resultados.jsonl")}
    selecao = {r["id"]: r for r in _lista(PASTA / "selecao.jsonl")}
    selecao_escala = {r["id"]: r for r in _lista(PASTA / "selecao-escala.jsonl")} if (PASTA / "selecao-escala.jsonl").exists() else {}
    for ficheiro, destino in (("resultados-escala.jsonl", resultados), ("selecao-escala.jsonl", selecao)):
        if (PASTA / ficheiro).exists():
            for r in _lista(PASTA / ficheiro):
                destino.setdefault(r["id"], r)  # o piloto, com o LLM, tem precedência
    juntados = {r["id"]: r for r in _lista(PASTA / "llm" / "juntados.jsonl")}
    if (PASTA / "llm" / "juntados-escala.jsonl").exists():
        juntados |= {r["id"]: r for r in _lista(PASTA / "llm" / "juntados-escala.jsonl") if r["id"] not in juntados}
    if (PASTA / "llm" / "juntados-completo.jsonl").exists():
        juntados |= {r["id"]: r for r in _lista(PASTA / "llm" / "juntados-completo.jsonl") if r["estado"] == "aplicado com LLM"}  # o pedido completo substitui o parcial
    if (PASTA / "llm" / "juntados-corrido.jsonl").exists():
        # Os originais sem artigos (texto corrido por unidades, `llm_corrido.py`), lidos também por `cegas.py`.
        juntados |= {r["id"]: r for r in _lista(PASTA / "llm" / "juntados-corrido.jsonl") if r["estado"] == "aplicado com LLM"}
    for id_, juntado in juntados.items():
        if juntado["estado"] == "aplicado com LLM":
            resultados[id_] = resultados[id_] | {k: juntado[k] for k in ("estado", "consolidado", "alteradores_ids") if k in juntado}
    hoje = date.today().isoformat()
    aplicados, ja_aplicados, recusados, fora = 0, 0, [], []
    verif = verificados(supor_certos=args.supor_verificados)
    sem_verificar = sum(
        1 for r in resultados.values() if r["estado"] in ("aplicado por regra", "aplicado com LLM") and r["id"] not in verif and r["id"] not in DE_FORA
    )
    for id_, entrada in sorted(verif.items(), key=lambda kv: resultados[kv[0]]["path"]):
        resultado = resultados[id_]
        if resultado["estado"] not in ("aplicado por regra", "aplicado com LLM"):
            # Ex.: as revogações condicionais do Decreto-Lei n.º 16/2013, que saíram dos aplicados,
            # ou os três que deixaram de se juntar com o LLM depois da 4.ª ronda.
            fora.append(f"{resultado['title']}: {resultado['estado']} ({resultado['motivo']})")
            continue
        piloto = RAIZ / resultado["consolidado"]
        if not piloto.exists():
            # Um juntado cujo consolidado não chegou ao repositório (ficou por fazer commit no ramo
            # de origem): fica como estava, em vez de parar a aplicação dos outros.
            recusados.append(f"{id_}: o consolidado não está no repositório ({resultado['consolidado']})")
            continue
        consolidado = corpo(piloto.read_text(encoding="utf-8"))
        if _NOTA_PILOTO.sub("", consolidado) != entrada["texto_consolidado"]:
            recusados.append(f"{id_}: o consolidado mudou depois da verificação às cegas")
            continue
        caminho = RAIZ / resultado["path"]
        registo, original = acervo.read(caminho)
        rotulo = ROTULO_LLM if resultado["estado"] == "aplicado com LLM" else ROTULO
        if registo.version.label == rotulo and original.strip() == consolidado.strip():
            ja_aplicados += 1
            continue
        if registo.version.kind == "original":
            if original.strip() != entrada["texto_original"].strip():
                recusados.append(f"{id_}: o registo em data/ já não é o original verificado")
                continue
        elif id_ in NAO_SUBSTITUIR or id_ in retificados:
            # Fica a consolidação anterior, também verificada às cegas; nos retificados por
            # `retificacoes.py`, o consolidado da entrada não tem as retificações.
            ja_aplicados += 1
            continue
        elif registo.version.label in (ROTULO, ROTULO_LLM) and _original_do_historico(acervo, caminho, registo.title) == blocos(entrada["texto_original"]):
            # Uma consolidação nossa anterior, refeita depois com mais alteradores e verificada
            # de novo às cegas: substitui-se, partindo do original guardado no histórico (versão 1).
            original = entrada["texto_original"]
        else:
            recusados.append(f"{id_}: o registo em data/ já não é o original verificado")
            continue

        alteradores = [(a, front_matter((RAIZ / a["path"]).read_text(encoding="utf-8"))) for a in alteradores_aplicados(resultado, _selecao_de(id_, resultado, selecao, selecao_escala))]
        if not alteradores:
            recusados.append(f"{id_}: nenhum alterador com alterações aplicadas")
            continue
        alteracoes = json.loads(piloto.with_name(piloto.name.replace(".md", ".alteracoes.json")).read_text(encoding="utf-8"))
        data_alteracao = data_da_versao(alteradores, front_matter(caminho.read_text(encoding="utf-8")))
        versoes = [
            {"date": registo.publication_date, "future": registo.publication_date > hoje, "acts": [], "changes": []},
            {
                "date": data_alteracao,
                "future": data_alteracao > hoje,
                "acts": [{
                    "id": meta["id"],
                    "title": meta["title"],
                    "published": meta["publication_date"],
                    "dre_path": (meta.get("identifiers") or {}).get("dre_path"),
                } for _, meta in alteradores],
                "changes": [f"{_OPERACAO.get(a['operacao'], 'Altera')} Artigo {a['artigo']}" for a in alteracoes],
            },
        ]
        try:
            dados = historico(id_, registo.title, original, consolidado, versoes)
            # O título `# …` vem do registo, não do corpo (que pode ter outra capitalização).
            # Só se ignoram as linhas em branco repetidas, que os blocos do histórico não guardam.
            assert _linhas(_sem_titulo(render_version(dados, dados["versions"][1], title=registo.title))) == _linhas(_sem_titulo(consolidado))
        except AssertionError:
            recusados.append(f"{id_}: o histórico não reproduz o consolidado")
            continue
        titulos = "; ".join(meta["title"] for _, meta in alteradores)
        nome = acervo.history_path(caminho).name
        registo.version = Version(kind="consolidated", label=rotulo, language="por", consolidation_date=data_alteracao)
        registo.version_history = summarize(dados, nome)
        registo.provenance.notes = (
            f"Texto em vigor consolidado pelo leis-portugal com as alterações publicadas em: {titulos}. "
            f"Método e verificação: consolidacao/README.md e {piloto.with_name(piloto.name.replace('.md', '.alteracoes.json')).relative_to(RAIZ)}"
        )
        if not args.dry_run:
            acervo.save(registo, consolidado, target=caminho)
            acervo.write_history(caminho, dados)
        aplicados += 1
        print(f"{'(dry-run) ' if args.dry_run else ''}{resultado['path']}: {len(alteracoes)} alteração(ões) de {len(alteradores)} alterador(es) ({resultado['estado']}), em vigor desde {data_alteracao}")
    print(f"Aplicados: {aplicados}. Já aplicados: {ja_aplicados}. Recusados: {len(recusados)}. Verificados que já não estão aplicados: {len(fora)}. Consolidados sem saída ou com reparos na última ronda (não se aplicam): {sem_verificar}.")
    for linha in recusados + fora:
        print("  ", linha)
    return 1 if recusados else 0


if __name__ == "__main__":
    raise SystemExit(main())
