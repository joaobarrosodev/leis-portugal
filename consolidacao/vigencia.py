"""Vigência revista dos consolidados: marcas à parte do registo, com o motivo e a prova.

Política aprovada a 19/11/2026: não se tiram consolidações por vigência. Um diploma que o DRE dá
como em vigor mas que já não vigora fica no `data/` com o texto certo, e a marca vai para
`auditoria/vigencia-revista.jsonl`. O RAG (`rag/vigencia.py`) junta-lhe um aviso. Na dúvida, não
se marca.

Marcas por regra (0 tokens), por esta ordem (fica a primeira):

1. `bloco3`: os 12 que a segunda leitura da ronda 114 tirou por vigência, com a prova que ela
   encontrou. Voltam a entrar no `data/` (saem de `acervo.DE_FORA`).
2. `revogado_dre`: o próprio registo tem `legal_status` revogado, ou uma relação `repealed_by`
   de revogação inteira (`auditoria.revogacao_inteira`). Ficam de fora as duas que a leitura deu
   como duvidosas.
3. `revogacao_noutro_registo`: o rótulo de uma relação de outro registo diz que este diploma foi
   revogado por inteiro («Revogado o Decreto-Lei n.º 158/96, de 3 de Setembro, …, pelo DEC
   LEI.47/2005»), sem ressalvas.
4. `ultramar`: diplomas anteriores a 1976 de um território ultramarino (uma província, Macau),
   sem os que tocam a metrópole ou regimes pessoais (pensões, vencimentos, Código Civil).
5. `caca_prazo`: concessões de caça com o prazo do texto acabado, sem cláusula de renovação no
   texto, e sem nenhum outro registo do acervo com o mesmo número de processo nem relação
   `amended_by` posterior. Uma renovação (ou anexação, ou exclusão de prédios) impede a marca. Só
   vai para `auditoria/alteradores-em-falta.jsonl` a que a consolidação não viu: as que estão na
   seleção (`selecao-escala.jsonl`) ou nos `alteradores_vistos` do LLM já foram triadas e não
   mudam o texto. Para «em falta», o número de processo tem de estar no corpo de ambos (o sumário
   tem gralhas) e o outro registo tem de falar de «zona de caça» (os acórdãos também têm
   processos). Para impedir a marca, basta o número, como antes: na dúvida, não se marca.
6. `regime_anterior`: os cursos e graus anteriores ao DL 74/2006, com a marca `regime_anterior`
   (não se afirma que caducaram).

Depois vêm as marcas da segunda leitura com o LLM (`llm/vigencia/`), só as verificadas.

Uso: `python consolidacao/vigencia.py --rotulos rotulos.txt --processos processos.txt`, com as
saídas do `rg` descritas em `consolidacao/README.md`, secção 10.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA))

from auditoria import _RESSALVA  # noqa: E402
from texto import RAIZ, corpo, front_matter  # noqa: E402


AUDITORIA = PASTA / "auditoria"
SAIDA = AUDITORIA / "vigencia-revista.jsonl"
EM_FALTA = AUDITORIA / "alteradores-em-falta.jsonl"
LLM_VIGENCIA = PASTA / "llm" / "vigencia"
HOJE = "2026-11-19"

# Ronda 114 (bloco 3): a segunda leitura jurídica tirou-os por já não vigorarem; o texto está certo.
BLOCO3 = {
    "pt:dre:1037778:por": "foi revogada pela Portaria n.º 506/2018.",
    "pt:dre:395573:por": "regulava a prova geral de acesso ao ensino superior de 1992, e o Decreto-Lei n.º 354/88, que a fundava, foi revogado pelo Decreto-Lei n.º 189/92.",
    "pt:dre:663299:por": "o Centro Regional de Segurança Social do Porto foi extinto pelo Decreto-Lei n.º 260/93.",
    "pt:dre:522225:por": "foi substituída pelo novo Regulamento do URBCOM (Portaria n.º 188/2004).",
    "pt:dre:459922:por": "o Decreto-Lei n.º 144/2007 foi revogado pelo Decreto-Lei n.º 158/2012, e a CIFE passou a ter composição legal (Decreto-Lei n.º 232/2015).",
    "pt:dre:460206:por": "os estatutos do Instituto Politécnico de Beja foram substituídos pelos do Despacho Normativo n.º 47/2008 (RJIES).",
    "pt:dre:687582:por": "o Fundo de Pensões dos Militares das Forças Armadas foi extinto pelo Decreto-Lei n.º 166-A/2013.",
    "pt:dre:692404:por": "foi substituída pela Portaria n.º 797/99.",
    "pt:dre:490019:por": "a linha de apoio era de 2010, com candidaturas até 10/12/2010.",
    "pt:dre:635585:por": "o Plano Director Municipal foi revogado pelo Aviso n.º 7886/2015 (art. 84.º).",
    "pt:dre:554384:por": "o regime era do Orçamento do Estado de 2000 e foi substituído pelo Despacho Normativo n.º 27-A/2001.",
    "pt:dre:405925:por": "a Escola Superior de Tecnologias Navais foi extinta pelo Decreto-Lei n.º 37/2008.",
}
# Camada 1, onda 2, ronda 119: a segunda leitura jurídica deu-os como sem vigência (o texto consolidado
# está certo). Os revogados ou extintos por outro diploma estão em reports/vigencia-manual.jsonl.
CAMADA1_119 = {
    "pt:dre:601283:por": ("nao_vigora", "Decreto-Lei n.º 21/93",
                          "era temporário: prorrogou o adicional até 31/12/1993 (art. 1.º) e fixou a redução «em 1993» (art. 2.º); o Decreto-Lei n.º 20/94 eliminou o adicional em 1994."),
    "pt:dre:553889:por": ("nao_vigora", "Decreto Legislativo Regional n.º 5/2012/M",
                          "é o Orçamento da Região Autónoma da Madeira para 2012, de vigência anual; as normas que alteram outros diplomas produziram efeito nesses diplomas."),
    "pt:dre:309893:por": ("por_confirmar", "Decreto-Lei n.º 621-A/74",
                          "regula só o recenseamento para a eleição da Assembleia Constituinte de 1975, com prazos de 1974-1975; não há declaração expressa de caducidade."),
    "pt:dre:512987:por": ("por_confirmar", "Decreto-Lei n.º 43351",
                          "o art. 31.º do Decreto-Lei n.º 50/93 revoga-o, mas o art. 32.º mantém-no em vigor enquanto não forem publicados os regulamentos previstos; falta confirmar essa publicação."),
}
TITULOS_BLOCO3 = {
    "pt:dre:1037778:por": "Portaria n.º 210/2007", "pt:dre:395573:por": "Portaria n.º 1171/91", "pt:dre:663299:por": "Portaria n.º 64/87",
    "pt:dre:522225:por": "Portaria n.º 317-B/2000", "pt:dre:459922:por": "Portaria n.º 22/2010", "pt:dre:460206:por": "Despacho Normativo n.º 32/95",
    "pt:dre:687582:por": "Portaria n.º 749/91", "pt:dre:692404:por": "Portaria n.º 1411/95", "pt:dre:490019:por": "Portaria n.º 1020/2009",
    "pt:dre:635585:por": "Resolução do Conselho de Ministros n.º 169/95", "pt:dre:554384:por": "Despacho Normativo n.º 23-A/2000",
    "pt:dre:405925:por": "Portaria n.º 43/2000",
}
# Revogações inteiras do registo que a leitura deu como duvidosas (auditoria, 19/11/2026).
DUVIDOSAS = {"Despacho n.º 3229/2006 (2.ª série)", "Decreto-Lei n.º 283/89"}

_TERRITORIO = re.compile(
    r"\b(?:prov[íi]ncias? (?:ultramarinas?|de (?:Angola|Moçambique|Guiné|Cabo Verde|São Tomé|Timor|Macau))|"
    r"(?:de|em|na|da|do) (?:Angola|Moçambique|Guiné|Cabo Verde|São Tomé(?: e Príncipe)?|Timor|Macau)|ultramar)\b"
)
# O que pode ainda contar na metrópole: regimes pessoais, a própria metrópole, os códigos estendidos.
_ULTRAMAR_FORA = re.compile(
    r"metr[óo]pole|aposenta|pens[ãa]o|vencimentos? (?:dos|a que) |comiss(?:ão|ões) de servi[çc]o dos militares|servidores do Estado|"
    r"C[óo]digo Civil|C[óo]digo de Justi[çc]a Militar|nacionalizad|Santa Casa|promiss[óo]rias|Banco Nacional Ultramarino",
    re.I,
)


def motivo_ultramar(titulo: str, sumario: str) -> str | None:
    texto = f"{titulo}. {sumario or ''}"
    if not _TERRITORIO.search(texto) or _ULTRAMAR_FORA.search(texto):
        return None
    if re.search(r"\bMacau\b", texto):
        return "é um diploma para Macau, cuja administração portuguesa terminou em 1999."
    return "é um diploma para os territórios ultramarinos, anterior à descolonização de 1974-1975."


# «Revogado o Decreto-Lei n.º 158/96, de 3 de Setembro, na redacção do presente diploma, pelo …»
_TIPOS = {
    "decreto-lei": r"(?:Decreto[- ]Lei|Dec\.?[- ]?Lei|DL)",
    "portaria": r"(?:Portaria|Port\.?)",
    "decreto-regulamentar": r"(?:Decreto Regulamentar|Dec\.? Reg\.?|DR)",
    "despacho-normativo": r"(?:Despacho Normativo|Desp\.? Norm\.?|DN)",
    "resolucao-conselho-ministros": r"(?:Resolução do Conselho de Ministros|RCM|Res\.? C\.? ?M\.?)",
    "lei": r"(?:Lei)",
    "decreto": r"(?:Decreto|Dec\.?)(?![- ]?(?:Lei|Reg))",
    "decreto-legislativo-regional": r"(?:Decreto Legislativo Regional|DLR)",
    "decreto-regulamentar-regional": r"(?:Decreto Regulamentar Regional|DRR)",
}


def _numero(titulo: str) -> str | None:
    m = re.search(r"n\.?\s*[º°o]\s*(\S+)$", re.sub(r"\s*\(.*\)$", "", titulo or ""))
    return m.group(1) if m else None


def padrao_revogacao(titulo: str, tipo: str) -> re.Pattern[str] | None:
    """O rótulo de outro registo que diz que este diploma foi revogado por inteiro."""
    numero, tipo_re = _numero(titulo), _TIPOS.get(tipo)
    if not numero or not tipo_re:
        return None
    partes = numero.split("/")
    num = re.escape(partes[0]) + (r"/(?:19|20)?" + re.escape(partes[1][-2:]) if len(partes) > 1 else "")
    return re.compile(
        rf"^Revogad[oa],?\s+(?:a partir de [^,]+,\s*)?(?:o|a)\s+{tipo_re}\s*(?:n\.?\s*[º°o]\.?\s*)?{num}(?![\d/])"
        r"[^.]{0,120}?\bpel[oa]s?\b",
        re.I,
    )


def revogacoes_noutros(rotulos: Path, consolidados: dict[str, dict]) -> dict[str, dict]:
    """id → primeira revogação inteira registada no rótulo de outro registo."""
    padroes = {}
    for v in consolidados.values():
        p = padrao_revogacao(v["titulo"], v["tipo"])
        if p:
            padroes[v["id"]] = (p, _numero(v["titulo"]).split("/")[0])
    por_numero = defaultdict(list)
    for id_, (p, n) in padroes.items():
        por_numero[n].append((id_, p))
    caminhos = {v["caminho"]: v["id"] for v in consolidados.values()}
    achados: dict[str, dict] = {}
    for linha in rotulos.read_text(encoding="utf-8").splitlines():
        ficheiro, _, resto = linha.partition(":")
        rotulo = resto.split("label:", 1)[-1].strip().strip('"').rstrip("\\").replace("\\x00", "").strip()
        rotulo = re.sub(r"\\x00", "", rotulo)
        if _RESSALVA.search(rotulo):
            continue
        for n in set(re.findall(r"(\d+)(?:/\d+)?", rotulo[:120])):
            for id_, p in por_numero.get(n, []):
                if id_ in achados or caminhos.get(ficheiro) == id_:
                    continue
                if p.search(rotulo):
                    achados[id_] = {"registo": ficheiro, "rotulo": rotulo[:300]}
    return achados


_PELO = re.compile(
    r"\bpel[oa]s?(?:\(a\))?\s+((?:DEC|PORT|LEI|DESP|DN|DR|DL|RCM|RES|DLR|DRR|Decreto|Portaria|Lei|Despacho|Resolução|Aviso|Regulamento)\b[^,\[]*)",
    re.I,
)


def _pelo(rotulo: str) -> str:
    """O diploma que revoga: o último «pelo/pela <ato>» do rótulo («…, com as alterações introduzidas
    pelo DR 1/2002 (…), pelo DEC LEI.39/2008» dá o segundo)."""
    achados = [m.group(1) for m in _PELO.finditer(rotulo)
               if not re.search(r"(?:introduzid|reda[cç]+[ãa]o|dada|alterad|conferid)\w*\s*$", rotulo[max(0, m.start() - 40) : m.start()], re.I)]
    return re.sub(r"\s+-\s+Diário da República.*$", "", achados[0]).strip() if achados else "outro diploma"


def na_cadeia() -> dict[str, set[str]]:
    """Por diploma, os alteradores que a consolidação já viu: os da seleção, triados um a um, e os
    `alteradores_vistos` das respostas do LLM. Um destes que não esteja nos `acts` foi visto e não
    muda o texto."""
    vistos: dict[str, set[str]] = defaultdict(set)
    selecao = PASTA / "selecao-escala.jsonl"
    if selecao.exists():
        for linha in selecao.read_text(encoding="utf-8").splitlines():
            d = json.loads(linha)
            vistos[d["id"]].update(a["id"] for a in d.get("alteradores") or [])
    for ficheiro in sorted((PASTA / "llm").glob("juntados*.jsonl")):
        for linha in ficheiro.read_text(encoding="utf-8").splitlines():
            d = json.loads(linha)
            vistos[d["id"]].update(d.get("alteradores_vistos") or [])
    return vistos


def caca_prazo(consolidados: dict[str, dict], processos: Path, vistos: dict[str, set[str]] | None = None) -> tuple[dict[str, dict], list[dict]]:
    """As concessões com o prazo acabado e nada no acervo depois; e as renovações que a consolidação
    não viu."""
    vistos = na_cadeia() if vistos is None else vistos
    _PROC = re.compile(r"processo n\.?\s*º?\s*([\d.]+)", re.I)
    def _PROC_N(t: str) -> list[str]:
        return [m.group(1).rstrip(".") for m in _PROC.finditer(t)]

    por_processo: dict[str, set[str]] = defaultdict(set)
    for linha in processos.read_text(encoding="utf-8").splitlines():
        ficheiro, _, resto = linha.partition(":")
        m = _PROC.search(resto.split(":", 1)[-1])
        if m:
            por_processo[m.group(1).rstrip(".")].add(ficheiro)
    marcas, em_falta = {}, []
    for v in consolidados.values():
        if v["classe"] != "caca" or v["certeza"] != "alta" or not v.get("prazo_anos") or v.get("renovavel") or v["fim_estimado"] >= HOJE:
            continue
        md = RAIZ / v["caminho"]
        texto = md.read_text(encoding="utf-8")
        versoes = json.loads(md.with_name(md.name[: -len(".md")] + ".versoes.json").read_text(encoding="utf-8"))
        aplicados = {a["id"] for x in versoes["versions"] for a in x["acts"]}
        meta = front_matter(texto)
        posteriores = [r for r in meta.get("relationships") or [] if r["type"] == "amended_by" and r["target"] not in aplicados]
        outros = set()
        corpo_proc = set(_PROC_N(corpo(texto)))
        for p in set(_PROC_N(texto)):
            outros |= {f for f in por_processo.get(p, set()) if f != v["caminho"]}
        movimentos = []
        for f in sorted(outros):
            tf = (RAIZ / f).read_text(encoding="utf-8")
            mf = front_matter(tf)
            if mf.get("id") in aplicados or str(mf.get("publication_date") or "") <= v["publicacao"]:
                continue
            # Qualquer registo posterior com o mesmo número impede a marca (na dúvida, não se marca), mas
            # só vai para «em falta» se o número está no corpo de ambos e o outro é de caça.
            fiavel = bool(set(_PROC_N(corpo(tf))) & corpo_proc) and bool(re.search(r"zona\s+de\s+caça", corpo(tf), re.I))
            movimentos.append({"id": mf.get("id"), "titulo": mf.get("title"), "publicacao": str(mf.get("publication_date")), "sumario": (mf.get("summary") or "")[:200], "fiavel": fiavel})
        for r in posteriores:
            movimentos.append({"id": r["target"], "titulo": None, "publicacao": str(r.get("date")), "sumario": (r.get("label") or "")[:200], "fiavel": True})
        if movimentos:
            for m in movimentos:
                if m["fiavel"] and re.search(r"renov|prorrog", m["sumario"] or "", re.I) and m["id"] not in vistos.get(v["id"], set()) \
                        and not any(x["id"] == v["id"] and x["alterador"] == m["id"] for x in em_falta):
                    em_falta.append({"id": v["id"], "titulo": v["titulo"], "alterador": m["id"], "alterador_titulo": m["titulo"], "publicacao": m["publicacao"], "sumario": m["sumario"]})
            continue
        anos = v["prazo_anos"]
        marcas[v["id"]] = {
            "motivo": f"a concessão tinha um prazo de {anos} anos, que acabou em {v['fim_estimado'][:4]}, e o acervo não tem renovação.",
            "prova": [{"tipo": "texto", "prazo_anos": anos, "fim_estimado": v["fim_estimado"]}],
        }
    return marcas, em_falta


def marcas_llm() -> dict[str, dict]:
    """As marcas da segunda leitura de vigência com o LLM que passaram a verificação."""
    ficheiro = LLM_VIGENCIA / "marcas-verificadas.jsonl"
    if not ficheiro.exists():
        return {}
    return {m["id"]: m for m in map(json.loads, ficheiro.read_text(encoding="utf-8").splitlines()) if m}


def construir(rotulos: Path, processos: Path) -> tuple[list[dict], list[dict]]:
    vig = [json.loads(l) for l in (AUDITORIA / "vigencia.jsonl").read_text(encoding="utf-8").splitlines()]
    consolidados = {v["id"]: v for v in vig}
    # Os 12 do bloco 3 não estão (ainda) entre os consolidados do `data/`: vêm do registo.
    marcas: dict[str, dict] = {}

    def marcar(id_: str, titulo: str, marca: str, classe: str, motivo: str, prova: list, fonte: str = "regra") -> None:
        if id_ not in marcas:
            marcas[id_] = {"id": id_, "titulo": titulo, "marca": marca, "classe": classe, "motivo": motivo, "prova": prova, "fonte": fonte}

    for id_, motivo in BLOCO3.items():
        titulo = consolidados.get(id_, {}).get("titulo") or TITULOS_BLOCO3[id_]
        marcar(id_, titulo, "nao_vigora", "bloco3", motivo, [{"tipo": "segunda leitura", "ficheiro": "consolidacao/verificacao/segunda-leitura-114.jsonl"}], "segunda leitura (Opus), ronda 114")
    for id_, (marca, titulo, motivo) in CAMADA1_119.items():
        marcar(id_, titulo, marca, "camada1", motivo, [{"tipo": "segunda leitura", "ficheiro": "consolidacao/camada1/segunda-119/"}], "segunda leitura (Opus), camada 1, ronda 119")
    for v in vig:
        if v["prova"] == "legal_status":
            marcar(v["id"], v["titulo"], "nao_vigora", "revogado_dre", "o próprio registo do DRE dá-o como revogado ou sem vigência.", [{"tipo": "legal_status", "valor": v["legal_status"]}])
        elif v["prova"] == "repealed_by_inteira" and v["titulo"] not in DUVIDOSAS:
            r = v["revogado_por"][0]
            marcar(v["id"], v["titulo"], "nao_vigora", "revogado_dre", f"o próprio DRE regista a revogação ({_pelo(r['rotulo'])}).", [{"tipo": "repealed_by", "alvo": r["alvo"], "rotulo": r["rotulo"][:300]}])
    for id_, a in revogacoes_noutros(rotulos, consolidados).items():
        v = consolidados[id_]
        pelo = _pelo(a["rotulo"])
        if pelo == "outro diploma" and "presente" in a["rotulo"]:  # «…, pelo presente»: o próprio registo do rótulo
            pelo = front_matter((RAIZ / a["registo"]).read_text(encoding="utf-8")).get("title") or pelo
        marcar(id_, v["titulo"], "nao_vigora", "revogacao_noutro_registo", f"foi revogado ({pelo}), segundo o DRE no registo de outro diploma.", [{"tipo": "rotulo noutro registo", **a}])
    for v in vig:
        if v["publicacao"] < "1976-01-01":
            motivo = motivo_ultramar(v["titulo"], v["sumario"] or "")
            if motivo:
                marcar(v["id"], v["titulo"], "nao_vigora", "ultramar", motivo, [{"tipo": "título e sumário"}])
    caca, em_falta = caca_prazo(consolidados, processos)
    for id_, m in caca.items():
        marcar(id_, consolidados[id_]["titulo"], "nao_vigora", "caca_prazo", m["motivo"], m["prova"])
    for v in vig:
        if v["classe"] == "cursos_pre_bolonha" and v["certeza"] == "alta":
            marcar(v["id"], v["titulo"], "regime_anterior", "cursos_pre_bolonha",
                   "os cursos e graus anteriores tiveram de ser adequados ao novo regime (o DL 74/2006 revogou o DL 216/92); confirmar se o curso ainda funciona nestes termos.",
                   [{"tipo": "regime geral", "diploma": "Decreto-Lei n.º 74/2006, art. 84.º"}])
    for id_, m in marcas_llm().items():
        marcar(id_, m["titulo"], m["marca"], m["classe"], m["motivo"], m["prova"], m.get("fonte", "llm"))
    return list(marcas.values()), em_falta


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--rotulos", type=Path, required=True, help="rg dos rótulos «Revogad…» (README, secção 10)")
    parser.add_argument("--processos", type=Path, required=True, help="rg dos números de processo das concessões (README, secção 10)")
    args = parser.parse_args(argv)
    marcas, em_falta = construir(args.rotulos, args.processos)
    SAIDA.write_text("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in sorted(marcas, key=lambda m: (m["classe"], m["id"]))), encoding="utf-8")
    EM_FALTA.write_text("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in em_falta), encoding="utf-8")
    from collections import Counter

    print(dict(Counter(m["classe"] for m in marcas).most_common()), "| em falta:", len(em_falta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
