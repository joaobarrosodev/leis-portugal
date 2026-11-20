"""Segunda leitura de vigência com o LLM, para os consolidados que as regras não marcaram.

São os de certeza `alta` nas classes `caca`, `organicas` e `um_so_ano` da auditoria
(`auditoria/vigencia.jsonl`) sem marca em `auditoria/vigencia-revista.jsonl`. Os cursos anteriores
a Bolonha têm a marca `regime_anterior` por regra, e os 140 incertos ficam de fora até se ver o
rendimento.

1. `entrada`: um item por diploma em `llm/vigencia/entrada-NN.jsonl`, com:
   - o título, o sumário, a data e as relações do registo (sem as citações);
   - o início e o fim do texto em vigor;
   - as menções no acervo (outro registo que cite o diploma, ou o mesmo número de processo
     numa concessão de caça) perto de um verbo de vigência (revogar, extinguir, caducar,
     substituir, renovar, prorrogar), com o título e a data do registo onde estão.
2. O leitor (Sonnet, `llm/vigencia/PROMPT-leitor.md`) responde `nao_vigora`, `vigora` ou `duvida`,
   e em `nao_vigora` dá o motivo e a prova (o id de uma menção da entrada ou uma relação). As
   dúvidas vão a uma segunda leitura (Opus, o mesmo prompt) em `llm/vigencia/duvidas-NN.jsonl`.
3. `juntar`: só conta `nao_vigora` com uma prova que esteja na entrada. Grava
   `llm/vigencia/marcas-verificadas.jsonl`, que `vigencia.py` junta às marcas.

Uso: `python consolidacao/vigencia_llm.py entrada --numeros nums-hits.txt --processos procs-hits.txt`
e `python consolidacao/vigencia_llm.py duvidas|juntar`.
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

from texto import RAIZ, corpo, front_matter, padrao_diploma, sem_ligacoes  # noqa: E402


LLM = PASTA / "llm" / "vigencia"
AUDITORIA = PASTA / "auditoria"
CLASSES = ("caca", "organicas", "um_so_ano")
POR_LOTE = 40
MAX_MENCOES = 8
_VERBO = re.compile(r"revog|extin|caduc|substitu|cess[ao]|termo|renov|prorrog|deixa de vigorar|transita|sucede", re.I)
_PROC = re.compile(r"processo n\.?\s*º?\s*([\d.]+)", re.I)
_PARCIAL = re.compile(r"exce[pç]+[ãa]o|excep[cç]|salvo|em parte|\bparte d[aeo]s?\b|parcial|na parte|com ressalva|com exce|sem preju[íi]zo", re.I)
# Uma relação com este rótulo não diz nada sobre a vigência: não serve de prova.
_ROTULO_GENERICO = re.compile(r"^Última alteração registada na importação inicial$")
# Lidos à mão a 19/11/2026: o próprio leitor disse que só o conteúdo principal foi substituído
# (ficam normas transitórias ou outras disposições). Na dúvida, não se marca.
DESCARTADAS = {
    "pt:dre:297246:por": "Despacho Normativo n.º 47-B/86: só a quota foi substituída; o despacho tem outras disposições",
    "pt:dre:472275:por": "Portaria n.º 690/74: substituído o quadro de pessoal anexo; ficam normas transitórias",
    "pt:dre:368260:por": "Portaria n.º 752/71: substituído o quadro de pessoal; o mesmo critério da Portaria n.º 690/74",
}


CLASSES_INCERTOS = CLASSES + ("cursos_pre_bolonha",)


def candidatos(incertos: bool = False) -> list[dict]:
    """Os de certeza alta das três classes; com `incertos`, os de certeza incerta das quatro (a
    classe é um palpite das regras: o leitor também diz se a confirma)."""
    marcados = {json.loads(l)["id"] for l in (AUDITORIA / "vigencia-revista.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    vig = [json.loads(l) for l in (AUDITORIA / "vigencia.jsonl").read_text(encoding="utf-8").splitlines()]
    if incertos:
        return [v for v in vig if v["certeza"] == "incerta" and v["classe"] in CLASSES_INCERTOS and v["id"] not in marcados]
    return [v for v in vig if v["certeza"] == "alta" and v["classe"] in CLASSES and v["id"] not in marcados]


def _linhas_rg(ficheiro: Path) -> dict[str, list[str]]:
    """ficheiro → linhas (sem o «ficheiro:n:») de uma saída do rg."""
    por = defaultdict(list)
    for linha in ficheiro.read_text(encoding="utf-8", errors="replace").splitlines():
        f, _, resto = linha.partition(":")
        _, _, texto = resto.partition(":")
        por[f].append(texto)
    return por


_NUMERO = re.compile(r"(?<![\d/])(\d+(?:-[A-Z]+\d*)?)/(\d{2,4})(?![\d])")


def por_numero(linhas_rg: dict[str, list[str]]) -> dict[str, list[tuple[str, str]]]:
    """«158/96» → [(ficheiro, linha sem ligações)], com o ano em dois algarismos («1996» → «96»)."""
    indice: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for f, linhas in linhas_rg.items():
        for texto in linhas:
            plano = sem_ligacoes(texto)
            for chave_n in {f"{m.group(1)}/{m.group(2)[-2:]}" for m in _NUMERO.finditer(plano)}:
                indice[chave_n].append((f, plano))
    return indice


def _chave_numero(titulo: str) -> str | None:
    m = re.search(r"n\.?\s*[º°o]\s*(\d+(?:-[A-Z]+\d*)?)/(\d{2,4})\b", titulo or "")
    return f"{m.group(1)}/{m.group(2)[-2:]}" if m else None


_META: dict[str, dict] = {}


def _meta(caminho: str) -> dict:
    if caminho not in _META:
        _META[caminho] = front_matter((RAIZ / caminho).read_text(encoding="utf-8"))
    return _META[caminho]


def mencoes(v: dict, linhas_numeros: dict[str, list[tuple[str, str]]], ficheiros_processo: set[str]) -> list[dict]:
    """As menções do diploma noutros registos, perto de um verbo de vigência, as mais recentes primeiro."""
    padrao = padrao_diploma(v["titulo"])
    achados = []
    chave_n = _chave_numero(v["titulo"])
    if padrao is not None and chave_n:
        for f, plano in linhas_numeros.get(chave_n, []):
            if f == v["caminho"]:
                continue
            for m in padrao.finditer(plano):
                trecho = plano[max(0, m.start() - 250) : m.end() + 200]
                if _VERBO.search(trecho):
                    achados.append((f, trecho))
                    break
    for f in ficheiros_processo:
        if f != v["caminho"]:
            meta = _meta(f)
            achados.append((f, f"(mesmo número de processo) {meta.get('summary') or ''}"[:450]))
    resultado, vistos = [], set()
    for f, trecho in achados:
        if f in vistos:
            continue
        vistos.add(f)
        meta = _meta(f)
        resultado.append({"id": meta.get("id"), "titulo": meta.get("title"), "data": str(meta.get("publication_date") or ""), "trecho": trecho.strip()})
    resultado.sort(key=lambda m: m["data"], reverse=True)
    return resultado[:MAX_MENCOES]


def entrada(numeros: Path, processos: Path, incertos: bool = False) -> None:
    linhas_numeros = por_numero(_linhas_rg(numeros))
    por_processo: dict[str, set[str]] = defaultdict(set)
    for f, linhas in _linhas_rg(processos).items():
        for texto in linhas:
            m = _PROC.search(texto)
            if m:
                por_processo[m.group(1).rstrip(".")].add(f)
    itens = []
    for v in candidatos(incertos):
        texto = (RAIZ / v["caminho"]).read_text(encoding="utf-8")
        meta = front_matter(texto)
        corpo_ = sem_ligacoes(corpo(texto)).strip()
        ficheiros_processo: set[str] = set()
        if v["classe"] == "caca":
            for p in {m.group(1).rstrip(".") for m in _PROC.finditer(texto)}:
                ficheiros_processo |= por_processo.get(p, set())
        relacoes = [{"tipo": r["type"], "alvo": r["target"], "rotulo": (r.get("label") or "").replace("\x00", "")[:250]} for r in meta.get("relationships") or [] if r["type"] != "cites"]
        itens.append({
            "id": v["id"], "titulo": v["titulo"], "sumario": v["sumario"], "tipo": v["tipo"], "classe": v["classe"],
            "publicacao": v["publicacao"], "texto_consolidado_ate": v.get("consolidacao"), "legal_status": v["legal_status"],
            "prazo_anos": v.get("prazo_anos"), "fim_estimado": v.get("fim_estimado"), "renovavel": v.get("renovavel"),
            "relacoes": relacoes[:25],
            "inicio_do_texto": corpo_[:1800], "fim_do_texto": corpo_[-700:] if len(corpo_) > 2500 else "",
            "mencoes_no_acervo": mencoes(v, linhas_numeros, ficheiros_processo),
        })
    LLM.mkdir(parents=True, exist_ok=True)
    prefixo = "incertos-entrada" if incertos else "entrada"
    for f in LLM.glob(f"{prefixo}-*.jsonl"):
        f.unlink()
    for n in range(0, len(itens), POR_LOTE):
        (LLM / f"{prefixo}-{n // POR_LOTE + 1:02d}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in itens[n : n + POR_LOTE]), encoding="utf-8")
    print(f"{len(itens)} diplomas em {-(-len(itens) // POR_LOTE)} lotes; com menções: {sum(1 for x in itens if x['mencoes_no_acervo'])}")


def _respostas(padrao: str) -> dict[str, dict]:
    resultado = {}
    for f in sorted(LLM.glob(padrao)):
        for linha in f.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                d = json.loads(linha)
                resultado[d["id"]] = d
    return resultado


def _entradas() -> dict[str, dict]:
    return _respostas("entrada-*.jsonl")


def duvidas() -> None:
    entradas, leituras = _entradas(), _respostas("resposta-*.jsonl")
    lista = [entradas[i] for i, r in leituras.items() if r["veredicto"] == "duvida"]
    for f in LLM.glob("duvidas-entrada-*.jsonl"):
        f.unlink()
    for n in range(0, len(lista), POR_LOTE):
        (LLM / f"duvidas-entrada-{n // POR_LOTE + 1:02d}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lista[n : n + POR_LOTE]), encoding="utf-8")
    print(f"{len(lista)} dúvidas para a segunda leitura (Opus)")


def prova_valida(r: dict, e: dict) -> bool:
    """A prova cita uma menção ou uma relação da entrada (o id) e há motivo."""
    ids = {m["id"] for m in e["mencoes_no_acervo"]} | {x["alvo"] for x in e["relacoes"]}
    # Uma revogação com exceções ou só em parte não é «já não vigora»: na dúvida, não se marca.
    if not (r.get("motivo") and r.get("prova") and r["prova"] in ids):
        return False
    if e["id"] in DESCARTADAS:
        return False
    mencao = next((m.get("trecho", "") for m in e["mencoes_no_acervo"] if m["id"] == r["prova"]), "")
    rotulos = [x["rotulo"].strip() for x in e["relacoes"] if x["alvo"] == r["prova"]]
    if not mencao and rotulos and all(_ROTULO_GENERICO.match(x) or not x for x in rotulos):
        return False
    prova = mencao + " " + " ".join(rotulos)
    return not (_PARCIAL.search(r["motivo"]) or _PARCIAL.search(prova))


def juntar() -> None:
    entradas = _entradas()
    leituras = _respostas("resposta-*.jsonl")
    leituras.update({i: r | {"segunda": True} for i, r in _respostas("duvidas-resposta-*.jsonl").items()})
    marcas, contas = [], defaultdict(int)
    for i, r in leituras.items():
        e = entradas.get(i)
        if not e:
            continue
        contas[r["veredicto"] + (" (Opus)" if r.get("segunda") else "")] += 1
        if r["veredicto"] != "nao_vigora":
            continue
        if not prova_valida(r, e):
            contas["nao_vigora sem prova na entrada (não conta)"] += 1
            continue
        prova = next((m for m in e["mencoes_no_acervo"] if m["id"] == r["prova"]), None) or next(x for x in sorted(e["relacoes"], key=lambda x: bool(_ROTULO_GENERICO.match(x["rotulo"].strip()))) if x["alvo"] == r["prova"])
        marcas.append({
            "id": i, "titulo": e["titulo"], "marca": "nao_vigora", "classe": f"llm_{e['classe']}",
            "motivo": r["motivo"].strip().rstrip(".") + ".", "prova": [{"tipo": "menção no acervo" if "trecho" in prova else "relação", **prova}],
            "fonte": "segunda leitura de vigência (Opus)" if r.get("segunda") else "segunda leitura de vigência (Sonnet)",
        })
    (LLM / "marcas-verificadas.jsonl").write_text("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in marcas), encoding="utf-8")
    print(dict(contas), "| marcas:", len(marcas))


HOJE = "2026-11-19"
FECHO = AUDITORIA / "vigencia-fecho.jsonl"
_ANO = re.compile(
    r"\b(?:para|durante|n[oa]|relativ[oa]s? ao|referentes? ao)\s+(?:o\s+|a\s+)?"
    r"((?:ano(?: lectivo| letivo| económico| escolar| civil| agrícola)?|exercício|campanha|época venatória|calendário venatório)(?: de)?)\s+"
    r"((?:1[89]|20)\d\d)(?:\s*[-/]\s*((?:1[89]|20)?\d\d))?\b"
    r"|\bOrçamento(?: Geral)? do Estado para ((?:1[89]|20)\d\d)\b",
    re.I,
)
_A_PARTIR = re.compile(r"a partir d|e seguintes|anos seguintes|prorrog", re.I)


def _ano(*textos: str) -> tuple[str, int] | None:
    """O período de um regime de um só ano, se os textos o dizem sem ambiguidade («para o ano de
    1992» → («o ano de 1992», 1992); «no ano lectivo de 2006-2007» → («o ano lectivo de
    2006-2007», 2007)). Com dois períodos diferentes, ou «a partir de», nenhum."""
    achados = {}
    for t in textos:
        if not t or _A_PARTIR.search(t):
            if t and _A_PARTIR.search(t):
                return None
            continue
        for m in _ANO.finditer(t):
            if m.group(4):
                achados[f"o ano de {m.group(4)}"] = int(m.group(4))
                continue
            tipo, a, b = m.group(1).lower(), m.group(2), m.group(3)
            tipo = re.sub(r"\s+de$", "", tipo)
            if b:
                b = b if len(b) == 4 else a[:2] + b
                achados[f"{'a' if tipo.startswith(('campanha', 'época')) else 'o'} {tipo} de {a}-{b}"] = int(b)
            else:
                achados[f"{'a' if tipo.startswith(('campanha', 'época')) else 'o'} {tipo} de {a}"] = int(a)
    return next(iter(achados.items())) if len(achados) == 1 else None


_RENOVACAO = re.compile(r"renov|prorrog", re.I)


def _porque_nao(r: dict, e: dict) -> str:
    """Porque é que um «nao_vigora» do leitor não passou o critério de prova."""
    ids = {m["id"] for m in e["mencoes_no_acervo"]} | {x["alvo"] for x in e["relacoes"]}
    if e["id"] in DESCARTADAS:
        return DESCARTADAS[e["id"]]
    if not r.get("prova") or r["prova"] not in ids:
        return "a prova não é uma menção nem uma relação da entrada"
    rotulos = [x["rotulo"].strip() for x in e["relacoes"] if x["alvo"] == r["prova"]]
    mencao = next((m.get("trecho", "") for m in e["mencoes_no_acervo"] if m["id"] == r["prova"]), "")
    if not mencao and rotulos and all(_ROTULO_GENERICO.match(x) or not x for x in rotulos):
        return "a relação só tem o rótulo genérico da importação"
    return "a revogação ou a extinção é só de uma parte, ou tem ressalvas"


def fecho() -> None:
    """Cada candidato da segunda leitura (os de certeza alta e os incertos) acaba com marca ou com
    «revista, sem marca» e o motivo, em `auditoria/vigencia-fecho.jsonl`. As marcas vão para
    `llm/vigencia/marcas-verificadas.jsonl`:

    - `nao_vigora`, com uma prova da entrada (o critério de `prova_valida`);
    - `regime_anterior`, nos cursos incertos que o leitor confirma como cursos do ensino superior
      anteriores ao DL 74/2006 (a mesma marca dos de certeza alta);
    - `por_confirmar`, uma marca branda, sem afirmar que caducou, quando o próprio texto dá o facto:
      uma concessão de caça cujo prazo do texto acabou sem renovação nem extinção no acervo, ou um
      regime de um só ano que já passou. O RAG dá o aviso; o peso no prior é só para `nao_vigora`.
    """
    entradas = _entradas()
    leituras = _respostas("resposta-*.jsonl")
    leituras.update({i: r | {"segunda": True} for i, r in _respostas("duvidas-resposta-*.jsonl").items()})
    entradas_inc = _respostas("incertos-entrada-*.jsonl")
    leituras_inc = _respostas("incertos-resposta-*.jsonl")
    marcas, linhas, contas = [], [], defaultdict(int)
    todos = [(i, entradas[i], r, "alta") for i, r in leituras.items() if i in entradas]
    todos += [(i, entradas_inc[i], r, "incerta") for i, r in leituras_inc.items() if i in entradas_inc]
    for i, e, r, certeza in todos:
        fonte = "Opus" if r.get("segunda") else "Sonnet"
        classe_ok = certeza == "alta" or bool(r.get("classe_confirmada"))
        base = {"id": i, "titulo": e["titulo"], "classe": e["classe"], "certeza": certeza,
                "leitura": {"veredicto": r["veredicto"], "leitor": fonte, "motivo": (r.get("motivo") or "").strip()}}
        if certeza == "incerta":
            base["leitura"]["classe_confirmada"] = r.get("classe_confirmada")
        marca = None
        if r["veredicto"] == "nao_vigora" and prova_valida(r, e):
            prova = next((m for m in e["mencoes_no_acervo"] if m["id"] == r["prova"]), None) or next(
                x for x in sorted(e["relacoes"], key=lambda x: bool(_ROTULO_GENERICO.match(x["rotulo"].strip()))) if x["alvo"] == r["prova"])
            marca = {"marca": "nao_vigora", "classe": f"llm_{e['classe']}" + ("_incertos" if certeza == "incerta" else ""),
                     "motivo": r["motivo"].strip().rstrip(".") + ".", "prova": [{"tipo": "menção no acervo" if "trecho" in prova else "relação", **prova}],
                     "fonte": f"segunda leitura de vigência ({fonte})" if certeza == "alta" else "leitura dos incertos (Sonnet)"}
        elif certeza == "incerta" and r["veredicto"] == "regime_anterior" and e["classe"] == "cursos_pre_bolonha" and classe_ok:
            marca = {"marca": "regime_anterior", "classe": "cursos_pre_bolonha_incertos",
                     "motivo": "os cursos e graus anteriores tiveram de ser adequados ao novo regime (o DL 74/2006 revogou o DL 216/92); confirmar se o curso ainda funciona nestes termos.",
                     "prova": [{"tipo": "regime geral", "diploma": "Decreto-Lei n.º 74/2006, art. 84.º"}, {"tipo": "leitura", "motivo": r.get("motivo")}],
                     "fonte": "leitura dos incertos (Sonnet)"}
        elif (r["veredicto"] == "duvida" and classe_ok and e["classe"] == "caca" and e.get("prazo_anos") and (e.get("fim_estimado") or "9") < HOJE
              and not _RENOVACAO.search(" ".join([m.get("trecho", "") for m in e["mencoes_no_acervo"]] + [x["rotulo"] for x in e["relacoes"]] + [r.get("motivo") or ""]))):
            frase = f"o prazo da concessão no texto ({e['prazo_anos']} anos) acabou em {e['fim_estimado'][:4]}, e o acervo não tem a renovação nem a extinção"
            if e.get("renovavel"):
                frase += "; o texto prevê a renovação"
            marca = {"marca": "por_confirmar", "classe": "caca_prazo_acabado", "motivo": frase + ".",
                     "prova": [{"tipo": "texto", "prazo_anos": e["prazo_anos"], "fim_estimado": e["fim_estimado"], "renovavel": bool(e.get("renovavel"))}],
                     "fonte": "regra, depois da leitura sem prova"}
        elif r["veredicto"] == "duvida" and classe_ok and e["classe"] == "um_so_ano":
            periodo = _ano(e["titulo"], e.get("sumario") or "")
            if periodo and periodo[1] < int(HOJE[:4]):
                marca = {"marca": "por_confirmar", "classe": "um_so_ano", "motivo": f"o texto regula só {periodo[0]}, que já passou.",
                         "prova": [{"tipo": "título ou sumário", "periodo": periodo[0]}], "fonte": "regra, depois da leitura sem prova"}
        if marca:
            marcas.append({"id": i, "titulo": e["titulo"], **marca})
            linhas.append(base | {"estado": "marca", "marca": marca["marca"], "classe_marca": marca["classe"], "motivo": marca["motivo"]})
            contas[f"marca {marca['marca']} ({marca['classe']})"] += 1
            continue
        if r["veredicto"] == "vigora":
            motivo = "a leitura dá-o como em vigor: " + base["leitura"]["motivo"]
        elif r["veredicto"] == "nao_vigora":
            motivo = f"a leitura deu «já não vigora», mas a prova não passou o critério ({_porque_nao(r, e)})."
        elif not classe_ok:
            motivo = "a classe das regras não se confirma, e não há prova de que já não vigore: " + base["leitura"]["motivo"]
        else:
            motivo = "sem prova, na entrada, de que já não vigore: " + base["leitura"]["motivo"]
        linhas.append(base | {"estado": "revista, sem marca", "motivo": motivo})
        contas[f"revista, sem marca ({r['veredicto']})"] += 1
    (LLM / "marcas-verificadas.jsonl").write_text("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in marcas), encoding="utf-8")
    FECHO.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in linhas), encoding="utf-8")
    print(len(linhas), "revistos;", dict(sorted(contas.items())))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("passo", choices=["entrada", "duvidas", "juntar", "fecho"])
    parser.add_argument("--numeros", type=Path)
    parser.add_argument("--processos", type=Path)
    parser.add_argument("--incertos", action="store_true", help="com entrada: os de certeza incerta (incertos-entrada-NN.jsonl)")
    args = parser.parse_args(argv)
    if args.passo == "entrada":
        entrada(args.numeros, args.processos, args.incertos)
    elif args.passo == "duvidas":
        duvidas()
    elif args.passo == "fecho":
        fecho()
    else:
        juntar()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
