"""Retificações fora da cadeia que a regra não aplica: pedido ao LLM, verificação às cegas e aplicação.

São as classes `llm` e `sem_pares` da auditoria (`auditoria/retificacoes.jsonl`) e as recusadas
por `retificacoes.py`. Três passos:

1. `entrada`: um item por diploma, com o texto de cada retificação e o texto em vigor em
   linhas numeradas (sem ligações), em `llm/retificacoes/entrada-NN.jsonl`. Nos textos grandes
   vão só os blocos (de título a título) que a retificação nomeia ou com que partilha frases, mais
   todos os títulos.
2. O respondedor (Opus, `llm/retificacoes/PROMPT-respondedor.md`) devolve, por retificação, as
   trocas linha a linha (`linha`, `texto_atual`, `texto_novo`) e as instruções que não aplicou,
   com o motivo, em `llm/retificacoes/resposta-NN.jsonl`. `verificacao` junta as trocas no formato
   da verificação às cegas de `retificacoes.py` (`llm/retificacoes/verificacao-entrada.jsonl`).
3. `aplicar`: só as retificações `certo` às cegas (`llm/retificacoes/verificacao-saida.jsonl`).
   Cada troca só entra se a linha do texto de hoje, sem ligações, for a que o respondedor viu;
   a linha nova recupera as ligações cujo texto não mudou, um título continua título do mesmo
   nível, e a nota «> Retificado pelo/a …» vai como em `retificacoes.py`. O histórico, as notas
   e a guarda do `acervo.py` são os de `retificacoes.py` (`auditoria/retificacoes-aplicadas.jsonl`).

Uma ronda seguinte (`--ronda r2`) refaz só as retificações reprovadas às cegas: o respondedor
escreve `resposta-r2-NN.jsonl` (a resposta mais recente de cada par vale), `verificacao --ronda r2`
junta só esses pares em `verificacao-entrada-r2.jsonl`, com o contexto de cada mudança (o título
acima, os parágrafos vizinhos e se o parágrafo foi reescrito depois), e `aplicar --ronda r2` lê
`verificacao-saida-r2.jsonl`.

Uso: `python consolidacao/retificacoes_llm.py entrada|verificacao|aplicar [--dry-run] [--ronda r2]`.
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

import retificacoes as rt  # noqa: E402
from acervo import blocos, historico  # noqa: E402
from auditoria import chave  # noqa: E402
from texto import RAIZ, corpo, front_matter, normalizar, sem_ligacoes  # noqa: E402

from leis_portugal.domain.history import render_version, summarize  # noqa: E402
from leis_portugal.infrastructure.repository import Acervo  # noqa: E402


LLM = PASTA / "llm" / "retificacoes"
CLASSES = ("llm", "sem_pares", "imagem_ou_republicacao")  # a última desde a ronda «im» (19/11/2026)
# As que `retificacoes.py` recusou (19/11/2026): localizador noutro artigo ou num anexo, renumerações.
RECUSADAS = {
    "pt:dre:314399:por", "pt:dre:222406:por", "pt:dre:235757:por", "pt:dre:3485579:por",
    "pt:dre:520020:por", "pt:dre:150288:por", "pt:dre:407348:por",
}
GRANDE = 60_000  # caracteres do texto em vigor acima dos quais vão só os blocos relevantes
BLOCO_GRANDE = 15_000
POR_LOTE = 10
LOTE_BYTES = 160_000
_TITULO = re.compile(r"^#{1,6} ")
_ARTIGO = re.compile(r"\bartigos?\s+(\d+(?:\.º|º)?(?:-[A-Z])?)", re.I)
_TITULO_ARTIGO = re.compile(r"^#{6} Artigo (\S+)")


# As que a auditoria deu «sem registo» e que se recolheram depois (19/11/2026), com o caminho.
RECOLHIDAS = PASTA / "auditoria" / "retificacoes-recolhidas.jsonl"


def selecao() -> list[dict]:
    recolhidas = {}
    if RECOLHIDAS.exists():
        recolhidas = {d["retificacao"]: d["caminho"] for d in map(json.loads, RECOLHIDAS.read_text(encoding="utf-8").splitlines()) if d}
    vistas, resultado = set(), []
    for linha in (PASTA / "auditoria" / "retificacoes.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(linha)
        chave_r = (r["id"], r["retificacao"])
        if not r.get("caminho_retificacao") and r["retificacao"] in recolhidas:
            r = r | {"caminho_retificacao": recolhidas[r["retificacao"]]}
        if chave_r in vistas or not r.get("caminho_retificacao"):
            continue
        if r["classe"] in CLASSES or r["retificacao"] in RECUSADAS or r["retificacao"] in recolhidas:
            vistas.add(chave_r)
            resultado.append(r)
    return resultado


def _shingles(texto: str, n: int = 6) -> set[str]:
    palavras = chave(texto).split()
    return {" ".join(palavras[i : i + n]) for i in range(max(0, len(palavras) - n + 1))}


def linhas_relevantes(linhas: list[str], textos_ret: list[str]) -> list[int]:
    """Os índices das linhas a mostrar: todas num texto pequeno; num grande, os títulos e os
    blocos que a retificação nomeia («artigo 52.º») ou com que partilha seis palavras seguidas."""
    if sum(len(l) for l in linhas) <= GRANDE:
        return [i for i, l in enumerate(linhas) if l.strip()]
    artigos = {rt._numero(a) for t in textos_ret for a in _ARTIGO.findall(t)}
    frases = set().union(*(_shingles(t) for t in textos_ret))
    inicios = [i for i, l in enumerate(linhas) if _TITULO.match(l)] or [0]
    if inicios[0] != 0:
        inicios = [0, *inicios]
    escolhidas: set[int] = {i for i in inicios}
    for a, b in zip(inicios, [*inicios[1:], len(linhas)], strict=True):
        bloco = linhas[a:b]
        m = _TITULO_ARTIGO.match(linhas[a])
        nomeado = bool(m and rt._numero(m.group(1)) in artigos)
        if not nomeado and not (_shingles("\n".join(bloco)) & frases):
            continue
        if nomeado or sum(len(l) for l in bloco) <= BLOCO_GRANDE:
            escolhidas |= set(range(a, b))
            continue
        # Um bloco grande (um anexo sem títulos): as linhas com frases da retificação e 3 de cada lado.
        for i in range(a, b):
            if _shingles(linhas[i]) & frases:
                escolhidas |= set(range(max(a, i - 3), min(b, i + 4)))
    return sorted(i for i in escolhidas if linhas[i].strip())


def entrada() -> None:
    por_diploma: dict[str, list[dict]] = defaultdict(list)
    for r in selecao():
        por_diploma[r["caminho"]].append(r)
    LLM.mkdir(parents=True, exist_ok=True)
    itens = []
    for caminho_rel, rets in sorted(por_diploma.items()):
        caminho = RAIZ / caminho_rel
        meta = front_matter(caminho.read_text(encoding="utf-8"))
        linhas = corpo(caminho.read_text(encoding="utf-8")).split("\n")
        textos = []
        for r in rets:
            ret = RAIZ / r["caminho_retificacao"]
            mr = front_matter(ret.read_text(encoding="utf-8"))
            textos.append({"retificacao": r["retificacao"], "titulo": mr.get("title"), "publicacao": str(mr.get("publication_date")),
                           "texto": sem_ligacoes(corpo(ret.read_text(encoding="utf-8"))).strip()})
        mostradas = linhas_relevantes(linhas, [t["texto"] for t in textos])
        itens.append({
            "id": meta["id"], "titulo": meta.get("title"), "sumario": meta.get("summary"), "caminho": caminho_rel,
            "texto_parcial": len(mostradas) < sum(1 for l in linhas if l.strip()),
            "retificacoes": textos,
            "texto_em_vigor": "\n".join(f"L{i}: {sem_ligacoes(linhas[i])}" for i in mostradas),
        })
    for f in LLM.glob("entrada-*.jsonl"):
        f.unlink()
    lotes: list[list[dict]] = [[]]
    for x in itens:  # lotes até LOTE_BYTES (um diploma maior fica sozinho) e POR_LOTE diplomas
        tamanho = len(json.dumps(x, ensure_ascii=False))
        if lotes[-1] and (sum(len(json.dumps(y, ensure_ascii=False)) for y in lotes[-1]) + tamanho > LOTE_BYTES or len(lotes[-1]) >= POR_LOTE):
            lotes.append([])
        lotes[-1].append(x)
    for n, lote in enumerate(lotes, 1):
        (LLM / f"entrada-{n:02d}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lote), encoding="utf-8")
    print(f"{len(itens)} diplomas, {sum(len(x['retificacoes']) for x in itens)} retificações, {len(lotes)} lotes em {LLM.relative_to(RAIZ)}")


def respostas(ronda: str | None = None) -> dict[tuple[str, str], dict]:
    """(id do diploma, id da retificação) → resposta, de todos os `resposta-NN.jsonl` (a mais
    recente vale), ou só dos `resposta-<ronda>-NN.jsonl` de uma ronda."""
    resultado = {}
    for f in sorted(LLM.glob(f"resposta-{ronda}-*.jsonl" if ronda else "resposta-*.jsonl")):
        for linha in f.read_text(encoding="utf-8").splitlines():
            if not linha.strip():
                continue
            d = json.loads(linha)
            for r in d.get("retificacoes", []):
                resultado[(d["id"], r["retificacao"])] = r | {"diploma": d["id"]}
    return resultado


class Recusa(Exception):
    pass


def trocar(linhas: list[str], trocas: list[dict]) -> list[dict]:
    """Aplica as trocas do respondedor a `linhas` (muda a lista) e devolve-as com a linha original.

    `texto_novo` vazio apaga a linha (uma supressão). A linha tem de ser, sem ligações e com os
    espaços normalizados, a que o respondedor viu; um título continua título do mesmo nível.

    Com `com_ligacoes`, `texto_atual` e `texto_novo` são o Markdown cru, com as ligações: serve
    para trocar a imagem de um mapa por outra (só o endereço muda) e para inserir parágrafos que a
    retificação publica (`texto_novo` = a linha atual, uma linha em branco e o que se insere).
    """
    feitas = []
    for t in sorted(trocas, key=lambda t: -int(t["linha"])):
        i = int(t["linha"])
        if not 0 <= i < len(linhas):
            raise Recusa(f"a linha L{i} não existe")
        cru = bool(t.get("com_ligacoes"))
        if normalizar(linhas[i] if cru else sem_ligacoes(linhas[i])) != normalizar(t["texto_atual"]):
            raise Recusa(f"a linha L{i} não é a que o respondedor viu")
        novo = t["texto_novo"].strip()
        nivel = re.match(r"^#*", linhas[i]).group(0)
        if nivel and novo and re.match(r"^#*", novo).group(0) != nivel:
            raise Recusa(f"a linha L{i} é um título de nível {len(nivel)} e deixava de o ser")
        if not nivel and novo.startswith("#"):
            raise Recusa(f"a linha L{i} passava a título")
        antes = linhas[i]
        linhas[i] = (novo if cru else rt.repor_ligacoes(antes, novo)) if novo else ""
        feitas.append({"linha": i, "artigo": rt._artigo_de(linhas, i), "antes": antes, "depois": linhas[i], "com_ligacoes": cru, "nota": t.get("nota"), "prova": t.get("prova")})
    return sorted(feitas, key=lambda f: f["linha"])


def contexto(linhas: list[str], i: int, vizinhos: int = 2) -> dict:
    """O que o verificador precisa para ver onde fica a linha `i`: o título acima, os parágrafos
    vizinhos e se a nota a seguir diz que o parágrafo foi reescrito por um alterador."""
    titulo = next((sem_ligacoes(linhas[j]) for j in range(i - 1, -1, -1) if linhas[j].startswith("#")), None)
    antes = [j for j in range(i - 1, -1, -1) if linhas[j].strip()][:vizinhos]
    depois = [j for j in range(i + 1, len(linhas)) if linhas[j].strip()][: vizinhos + 1]
    nota = linhas[depois[0]] if depois and linhas[depois[0]].startswith("> ") else None
    return {"titulo_acima": titulo, "antes": [sem_ligacoes(linhas[j])[:300] for j in reversed(antes)],
            "depois": [sem_ligacoes(linhas[j])[:300] for j in depois], "reescrito_depois": sem_ligacoes(nota) if nota else None}


def pares_da_ronda(ronda: str) -> set[tuple[str, str]]:
    pares = set()
    for f in sorted(LLM.glob(f"resposta-{ronda}-*.jsonl")):
        for linha in f.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                d = json.loads(linha)
                pares |= {(d["id"], r["retificacao"]) for r in d.get("retificacoes", [])}
    return pares


def verificacao(ronda: str | None = None) -> None:
    itens = []
    da_ronda = pares_da_ronda(ronda) if ronda else None
    resp = respostas(ronda)
    sel = {(x["id"], x["retificacao"]): x for x in selecao()}
    # Na 1.ª ronda, a ordem dos ids (a numeração `n` de verificacao-saida.jsonl depende dela). Numa
    # ronda seguinte, a ordem da seleção, que é a do `aplicar`: as retificações do mesmo diploma
    # encadeiam-se, cada uma sobre o texto deixado pela anterior (três plantas depois da mesma linha).
    ordem = list(sel) if ronda else sorted(resp)
    correntes: dict[str, list[str]] = {}
    for diploma, retificacao in ordem:
        r = resp.get((diploma, retificacao))
        if not r or not r.get("trocas") or (da_ronda is not None and (diploma, retificacao) not in da_ronda):
            continue
        s = sel[(diploma, retificacao)]
        linhas = correntes.get(s["caminho"]) or corpo((RAIZ / s["caminho"]).read_text(encoding="utf-8")).split("\n")
        copia = list(linhas)
        try:
            feitas = trocar(copia, r["trocas"])
        except Recusa as erro:
            print(f"   {s['titulo']}: {retificacao}: {erro}")
            continue
        if ronda:
            correntes[s["caminho"]] = copia
        ret = RAIZ / s["caminho_retificacao"]
        mr = front_matter(ret.read_text(encoding="utf-8"))
        itens.append({
            "n": len(itens) + 1, "diploma": s["titulo"], "id": diploma, "retificacao_id": retificacao,
            "retificacao": f"{mr.get('title')} ({mr.get('publication_date')})",
            "texto_da_retificacao": corpo(ret.read_text(encoding="utf-8"))[:40000],
            "alteracoes_feitas": [{"artigo": f["artigo"],
                                   "paragrafo_antes": f["antes"] if f["com_ligacoes"] else sem_ligacoes(f["antes"]),
                                   "paragrafo_depois": (f["depois"] if f["com_ligacoes"] else sem_ligacoes(f["depois"])) or "(parágrafo apagado)"}
                                  | ({"contexto": contexto(linhas, f["linha"])} if ronda else {})
                                  | ({"com_ligacoes": True} if f["com_ligacoes"] else {})
                                  | ({"nota_do_respondedor": f["nota"]} if f["nota"] else {})
                                  | ({"prova_do_respondedor": f["prova"]} if f.get("prova") else {}) for f in feitas],
            "nao_aplicadas": r.get("nao_aplicadas", []),
        })
    (LLM / (f"verificacao-entrada-{ronda}.jsonl" if ronda else "verificacao-entrada.jsonl")).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in itens), encoding="utf-8")
    print(f"{len(itens)} retificações com trocas para a verificação às cegas")


def aplicar(dry_run: bool, ronda: str | None = None) -> None:
    sufixo = f"-{ronda}" if ronda else ""
    saida = LLM / f"verificacao-saida{sufixo}.jsonl"
    entrada_v = {json.loads(l)["n"]: json.loads(l) for l in (LLM / f"verificacao-entrada{sufixo}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    certos = set()
    for linha in saida.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            v = json.loads(linha)
            if v["veredicto"] == "certo":
                certos.add((entrada_v[v["n"]]["id"], entrada_v[v["n"]]["retificacao_id"]))
    resp = respostas(ronda)
    por_diploma: dict[str, list[tuple[dict, dict]]] = defaultdict(list)
    for s in selecao():
        if (s["id"], s["retificacao"]) in certos:
            por_diploma[s["caminho"]].append((s, resp[(s["id"], s["retificacao"])]))
    acervo = Acervo(RAIZ)
    saida_aplicadas, recusadas, n = [], [], 0
    for caminho_rel, lista in sorted(por_diploma.items()):
        caminho = RAIZ / caminho_rel
        registo, _ = acervo.read(caminho)
        dados = acervo.read_history(caminho)
        if len(dados["versions"]) != 2:
            recusadas.append(f"{caminho_rel}: o histórico não tem duas versões")
            continue
        ja = {a["id"] for v in dados["versions"] for a in v["acts"]}
        linhas = corpo(caminho.read_text(encoding="utf-8")).split("\n")
        tocadas: dict[int, set[str]] = defaultdict(set)
        trocas_feitas = []
        for s, r in lista:
            # uma retificação já aplicada só se completa (com trocas que tinham ficado de fora) quando
            # a resposta o diz (`"completa": true`); o ato não se repete
            completar = s["retificacao"] in ja
            if completar and not r.get("completa"):
                continue
            copia = list(linhas)
            try:
                feitas = trocar(copia, r["trocas"])
            except Recusa as erro:
                recusadas.append(f"{caminho_rel}: {s['retificacao']}: {erro}")
                continue
            linhas = copia
            meta = front_matter((RAIZ / s["caminho_retificacao"]).read_text(encoding="utf-8"))
            for f in feitas:
                tocadas[f["linha"]].add(rt._nota(meta))
            trocas_feitas.append({"retificacao": s["retificacao"], "completa": completar, "titulo": meta["title"], "publicacao": str(meta["publication_date"]),
                                  "dre_path": (meta.get("identifiers") or {}).get("dre_path"), "caminho_retificacao": s["caminho_retificacao"],
                                  "classe": "llm", "trocas": feitas, "nao_aplicadas": r.get("nao_aplicadas", [])})
        if not trocas_feitas:
            continue
        # As linhas apagadas (supressões) saem depois de pôr as notas, para os índices não mudarem.
        com_notas = rt._com_notas(linhas, tocadas)
        novo = re.sub(r"\n{3,}", "\n\n", "\n".join(com_notas))
        original = render_version(dados, dados["versions"][0], title=registo.title)
        primeira, segunda = (dict(v) for v in dados["versions"])
        segunda["acts"] = list(segunda["acts"]) + [{"id": t["retificacao"], "title": t["titulo"], "published": t["publicacao"], "dre_path": t["dre_path"]} for t in trocas_feitas if not t["completa"]]
        artigos = dict.fromkeys(f["artigo"] or "" for t in trocas_feitas for f in t["trocas"])
        segunda["changes"] = list(segunda["changes"]) + [c for c in (f"Retifica Artigo {a}" if a else "Retifica texto" for a in artigos) if c not in segunda["changes"]]
        novos = historico(registo.id, registo.title, original, novo, [primeira, segunda])
        if blocos(render_version(novos, novos["versions"][1], title=registo.title)) != blocos(novo) or blocos(render_version(novos, novos["versions"][0], title=registo.title)) != blocos(original):
            recusadas.append(f"{caminho_rel}: o histórico não reproduz o texto")
            continue
        registo.version_history = summarize(novos, acervo.history_path(caminho).name)
        frase = f"Retificações aplicadas com um LLM, na ronda {ronda}," if ronda else "Retificações aplicadas com um LLM"
        nota = f" {frase} e verificadas às cegas (consolidacao/retificacoes_llm.py): " + "; ".join(t["titulo"] for t in trocas_feitas) + "."
        if frase not in (registo.provenance.notes or ""):
            anteriores = (registo.provenance.notes or "").rstrip()
            registo.provenance.notes = (anteriores + ("" if not anteriores or anteriores.endswith(".") else ".") + nota).strip()
        if not dry_run:
            acervo.save(registo, novo, target=caminho)
            acervo.write_history(caminho, novos)
        n += len(trocas_feitas)
        saida_aplicadas.append({"id": registo.id, "caminho": caminho_rel, "titulo": registo.title, "retificacoes": trocas_feitas})
        print(f"{'(dry-run) ' if dry_run else ''}{caminho_rel}: {len(trocas_feitas)} retificação(ões)")
    if not dry_run:
        destino = rt.APLICADAS
        anteriores = {json.loads(l)["id"]: json.loads(l) for l in destino.read_text(encoding="utf-8").splitlines() if l.strip()} if destino.exists() else {}
        for s in saida_aplicadas:
            if s["id"] in anteriores:
                anteriores[s["id"]]["retificacoes"] += s["retificacoes"]
            else:
                anteriores[s["id"]] = s
        destino.write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in anteriores.values()), encoding="utf-8")
    print(f"Retificações aplicadas: {n}, em {len(saida_aplicadas)} diplomas. Recusadas: {len(recusadas)}.")
    for r in recusadas:
        print("  ", r)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("passo", choices=["entrada", "verificacao", "aplicar"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ronda", help="uma ronda seguinte sobre as reprovadas (r2, …): verificacao e aplicar")
    args = parser.parse_args(argv)
    if args.passo == "entrada":
        entrada()
    elif args.passo == "verificacao":
        verificacao(args.ronda)
    else:
        aplicar(args.dry_run, args.ronda)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
