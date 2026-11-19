"""Anexos, mapas e quadros que um alterador muda e que a consolidação não aplicou (19/11/2026).

Ao fechar a auditoria dos consolidados apareceu um buraco na triagem: um alterador que muda um
anexo, um mapa ou um quadro (o rótulo do DRE diz «Alterado o quadro de pessoal pela…»,
«Substituída a planta anexa pela…») sem instruções de texto no articulado foi triado «sem
alteração textual», e o consolidado ficou com o anexo do original. Em 214 pares (89
consolidados), 125 trazem uma imagem que não está no consolidado.

Três passos, como `retificacoes_llm.py`:

1. `entrada`: um item por consolidado, com o texto em vigor em linhas numeradas (Markdown cru),
   os alteradores candidatos por ordem de data (o texto, as imagens e os rótulos do DRE) e os
   outros alteradores, só com o título e os rótulos, para se ver se um posterior substituiu o
   mesmo anexo (`llm/anexos/entrada-NN.jsonl`).
2. O respondedor (Opus, `llm/anexos/PROMPT-respondedor.md`) dá, por alterador, as trocas
   (`com_ligacoes`) e o que não se aplica, com o motivo; `verificacao` junta-as para o
   verificador às cegas (Sonnet, `llm/anexos/PROMPT-verificador.md`), com o texto do alterador.
3. `aplicar`: só as `certo`, na pasta principal. O alterador entra nos `acts` da versão
   consolidada, com a nota «> Alterado pelo/a …», e a data da versão passa a ser a mais
   recente entre a de hoje e a entrada em vigor do alterador. Os registos ficam em
   `auditoria/anexos-aplicados.jsonl`, que `acervo.py` também guarda.

Uso: `python consolidacao/anexos_alteradores.py entrada|verificacao|aplicar [--dry-run]`.
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
sys.path.insert(0, str(PASTA.parent / "src"))

import retificacoes as rt  # noqa: E402
import retificacoes_llm as rl  # noqa: E402
from acervo import blocos, em_vigor, historico  # noqa: E402
from texto import RAIZ, corpo, front_matter, sem_ligacoes  # noqa: E402

from leis_portugal.domain.history import render_version, summarize  # noqa: E402
from leis_portugal.infrastructure.repository import Acervo  # noqa: E402

LLM = PASTA / "llm" / "anexos"
APLICADOS = PASTA / "auditoria" / "anexos-aplicados.jsonl"
LOTE_BYTES = 140_000
POR_LOTE = 8
MAX_ALTERADOR = 30_000
# O rótulo do DRE diz que o alterador muda um anexo, um mapa, um quadro, uma tabela ou uma planta.
ROTULO = re.compile(
    r"(anexo|mapa|quadro|tabela|planta)s?\b[^.]{0,80}?(alterad|substitu|ratificad|rectificad|retificad|republicad|nova redac|aprovad)"
    r"|(alterad|substitu|ratificad|rectificad|retificad)\w*\s+(o|os|a|as)\s+(anexo|mapa|quadro|tabela|planta)",
    re.I,
)


def candidatos() -> dict[str, dict]:
    """Por consolidado do `data/`: o registo da seleção e os alteradores candidatos (triados «sem
    alteração textual», com o rótulo de cima)."""
    consolidados = {json.loads(l)["id"]: json.loads(l) for l in (PASTA / "auditoria" / "vigencia.jsonl").read_text(encoding="utf-8").splitlines()}
    selecao = {}
    for linha in (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines():
        d = json.loads(linha)
        if d["id"] in consolidados:
            selecao[d["id"]] = d
    por_doc: dict[str, dict] = {}
    for linha in (PASTA / "resultados-escala.jsonl").read_text(encoding="utf-8").splitlines():
        d = json.loads(linha)
        if d["id"] not in selecao:
            continue
        alts = {a["id"]: a for a in selecao[d["id"]]["alteradores"]}
        for p in d.get("passos", []):
            a = alts.get(p.get("id"))
            if p.get("triagem") != "sem alteração textual" or not a or not a.get("path"):
                continue
            if not ROTULO.search(" ".join(a.get("rotulos_dre") or [])):
                continue
            item = por_doc.setdefault(d["id"], {"selecao": selecao[d["id"]], "caminho": consolidados[d["id"]]["caminho"], "alteradores": {}})
            item["alteradores"][a["id"]] = a
    return por_doc


def entrada() -> None:
    itens = []
    for id_, c in sorted(candidatos().items()):
        caminho = RAIZ / c["caminho"]
        texto = caminho.read_text(encoding="utf-8")
        meta = front_matter(texto)
        linhas = corpo(texto).split("\n")
        alteradores = []
        for a in sorted(c["alteradores"].values(), key=lambda a: (a.get("ordem") or "", a["id"])):
            ta = corpo((RAIZ / a["path"]).read_text(encoding="utf-8")).strip()
            alteradores.append({"id": a["id"], "titulo": a["title"], "publicacao": a.get("publication_date"),
                                "rotulos_dre": [r.replace("\x00", "") for r in a.get("rotulos_dre") or []],
                                "texto": ta[:MAX_ALTERADOR], "texto_cortado": len(ta) > MAX_ALTERADOR})
        outros = [{"id": a["id"], "titulo": a["title"], "publicacao": a.get("publication_date"), "rotulos_dre": [r.replace("\x00", "")[:200] for r in a.get("rotulos_dre") or []]}
                  for a in c["selecao"]["alteradores"] if a["id"] not in c["alteradores"]]
        mostradas = rl.linhas_relevantes(linhas, [sem_ligacoes(x["texto"]) for x in alteradores] + [" ".join(x["rotulos_dre"]) for x in alteradores])
        # o fim do texto (onde costumam estar os anexos) vai sempre
        fim = [i for i in range(max(0, len(linhas) - 120), len(linhas)) if linhas[i].strip()]
        mostradas = sorted(set(mostradas) | set(fim))
        itens.append({
            "id": id_, "titulo": meta.get("title"), "caminho": c["caminho"],
            "texto_parcial": len(mostradas) < sum(1 for l in linhas if l.strip()),
            "texto_em_vigor": "\n".join(f"L{i}: {linhas[i]}" for i in mostradas),
            "alteradores_candidatos": alteradores, "outros_alteradores": outros,
        })
    LLM.mkdir(parents=True, exist_ok=True)
    for f in LLM.glob("entrada-*.jsonl"):
        f.unlink()
    lotes: list[list[dict]] = [[]]
    for x in itens:
        tamanho = len(json.dumps(x, ensure_ascii=False))
        if lotes[-1] and (sum(len(json.dumps(y, ensure_ascii=False)) for y in lotes[-1]) + tamanho > LOTE_BYTES or len(lotes[-1]) >= POR_LOTE):
            lotes.append([])
        lotes[-1].append(x)
    for n, lote in enumerate(lotes, 1):
        (LLM / f"entrada-{n:02d}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lote), encoding="utf-8")
    print(f"{len(itens)} consolidados, {sum(len(x['alteradores_candidatos']) for x in itens)} alteradores, {len(lotes)} lotes")


def respostas() -> dict[tuple[str, str], dict]:
    """(consolidado, alterador) → resposta, de todos os `resposta-NN.jsonl`."""
    resultado = {}
    for f in sorted(LLM.glob("resposta-*.jsonl")):
        for linha in f.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                d = json.loads(linha)
                for r in d.get("alteradores", []):
                    resultado[(d["id"], r["alterador"])] = r
    return resultado


def encadear(linhas: list[str], trocas: list[dict]) -> list[dict]:
    """Os respondedores escrevem as trocas sobre o texto de hoje. Quando dois alteradores mexem na
    mesma linha (um troca a imagem, outro insere a seguir; ou dois inserem), o segundo encontra a
    linha já mudada pelo primeiro: nesse caso, e só numa inserção (o texto novo começa pelo atual
    e uma linha em branco), o que ele insere acrescenta-se ao fim do que lá está, pela ordem dos
    alteradores."""
    resultado = []
    for t in trocas:
        i, atual, novo = int(t["linha"]), t["texto_atual"], t["texto_novo"]
        hoje = linhas[i] if 0 <= i < len(linhas) else None
        # a linha só difere do que o respondedor viu se um alterador anterior da mesma cadeia já a
        # mudou (outra inserção, ou a troca da imagem); numa inserção, acrescenta-se ao que lá está
        if hoje is not None and hoje != atual and novo.startswith(atual + "\n\n"):
            t = t | {"texto_atual": hoje, "texto_novo": hoje + novo[len(atual):]}
        resultado.append(t)
    return resultado


def _ordem(c: dict) -> list[str]:
    return [a["id"] for a in sorted(c["alteradores"].values(), key=lambda a: (a.get("ordem") or "", a["id"]))]


def verificacao() -> None:
    """Uma entrada por (consolidado, alterador) com trocas, encadeadas pela ordem de data."""
    resp, cands, itens = respostas(), candidatos(), []
    for id_, c in sorted(cands.items()):
        linhas = corpo((RAIZ / c["caminho"]).read_text(encoding="utf-8")).split("\n")
        for alt in _ordem(c):
            r = resp.get((id_, alt))
            if not r or not r.get("trocas"):
                continue
            copia = list(linhas)
            try:
                feitas = rl.trocar(copia, encadear(linhas, r["trocas"]))
            except rl.Recusa as erro:
                print(f"   {id_} {alt}: {erro}")
                continue
            a = c["alteradores"][alt]
            itens.append({
                "n": len(itens) + 1, "diploma": c["selecao"]["title"], "id": id_, "alterador_id": alt,
                "alterador": f"{a['title']} ({a.get('publication_date')})", "rotulos_dre": a.get("rotulos_dre"),
                "texto_do_alterador": corpo((RAIZ / a["path"]).read_text(encoding="utf-8"))[:40000],
                "alteracoes_feitas": [{"paragrafo_antes": f["antes"], "paragrafo_depois": f["depois"] or "(parágrafo apagado)",
                                       "contexto": rl.contexto(linhas, f["linha"])} | ({"nota_do_respondedor": f["nota"]} if f.get("nota") else {}) for f in feitas],
                "nao_aplicadas": r.get("nao_aplicadas", []),
            })
            linhas = copia
    (LLM / "verificacao-entrada.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in itens), encoding="utf-8")
    print(f"{len(itens)} pares com trocas para a verificação às cegas")


def _nota(meta: dict) -> str:
    caminho = (meta.get("identifiers") or {}).get("dre_path")
    ligacao = f"[{meta['title']}](https://diariodarepublica.pt{caminho})" if caminho else meta["title"]
    return f"> Alterado pelo/a {ligacao}, publicado em {meta['publication_date']}."


def aplicar(dry_run: bool) -> None:
    saida = LLM / "verificacao-saida.jsonl"
    entrada_v = {json.loads(l)["n"]: json.loads(l) for l in (LLM / "verificacao-entrada.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    certos = set()
    for linha in saida.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            v = json.loads(linha)
            if v["veredicto"] == "certo":
                certos.add((entrada_v[v["n"]]["id"], entrada_v[v["n"]]["alterador_id"]))
    resp, cands = respostas(), candidatos()
    acervo = Acervo(RAIZ)
    feitos, recusadas, n = [], [], 0
    for id_, c in sorted(cands.items()):
        lista = [alt for alt in _ordem(c) if (id_, alt) in certos]
        if not lista:
            continue
        caminho = RAIZ / c["caminho"]
        registo, _ = acervo.read(caminho)
        dados = acervo.read_history(caminho)
        if len(dados["versions"]) != 2:
            recusadas.append(f"{c['caminho']}: o histórico não tem duas versões")
            continue
        ja = {a["id"] for v in dados["versions"] for a in v["acts"]}
        linhas = corpo(caminho.read_text(encoding="utf-8")).split("\n")
        tocadas: dict[int, set[str]] = defaultdict(set)
        aplicados = []
        for alt in lista:
            if alt in ja:
                continue
            copia = list(linhas)
            try:
                feitas = rl.trocar(copia, encadear(linhas, resp[(id_, alt)]["trocas"]))
            except rl.Recusa as erro:
                recusadas.append(f"{c['caminho']}: {alt}: {erro}")
                continue
            linhas = copia
            meta = front_matter((RAIZ / c["alteradores"][alt]["path"]).read_text(encoding="utf-8"))
            for f in feitas:
                tocadas[f["linha"]].add(_nota(meta))
            aplicados.append({"alterador": alt, "titulo": meta["title"], "publicacao": str(meta["publication_date"]), "em_vigor": str(em_vigor(meta)),
                              "dre_path": (meta.get("identifiers") or {}).get("dre_path"), "trocas": feitas,
                              "nao_aplicadas": resp[(id_, alt)].get("nao_aplicadas", [])})
        if not aplicados:
            continue
        novo = re.sub(r"\n{3,}", "\n\n", "\n".join(rt._com_notas(linhas, tocadas)))
        original = render_version(dados, dados["versions"][0], title=registo.title)
        primeira, segunda = (dict(v) for v in dados["versions"])
        segunda["acts"] = list(segunda["acts"]) + [{"id": a["alterador"], "title": a["titulo"], "published": a["publicacao"], "dre_path": a["dre_path"]} for a in aplicados]
        artigos = dict.fromkeys(f["artigo"] or "" for a in aplicados for f in a["trocas"])
        segunda["changes"] = list(segunda["changes"]) + [c_ for c_ in (f"Altera Artigo {x}" if x else "Altera anexo ou texto fora do articulado" for x in artigos) if c_ not in segunda["changes"]]
        data_nova = max([segunda["date"]] + [a["em_vigor"] for a in aplicados])
        segunda["date"] = data_nova
        novos = historico(registo.id, registo.title, original, novo, [primeira, segunda])
        if blocos(render_version(novos, novos["versions"][1], title=registo.title)) != blocos(novo) or blocos(render_version(novos, novos["versions"][0], title=registo.title)) != blocos(original):
            recusadas.append(f"{c['caminho']}: o histórico não reproduz o texto")
            continue
        registo.version_history = summarize(novos, acervo.history_path(caminho).name)
        if getattr(registo, "version", None) is not None and getattr(registo.version, "consolidation_date", None):
            registo.version.consolidation_date = max(str(registo.version.consolidation_date), data_nova)
        nota = " Anexos e quadros de alteradores triados «sem alteração textual», aplicados com um LLM e verificados às cegas (consolidacao/anexos_alteradores.py): " + "; ".join(a["titulo"] for a in aplicados) + "."
        if "consolidacao/anexos_alteradores.py" not in (registo.provenance.notes or ""):
            anteriores = (registo.provenance.notes or "").rstrip()
            registo.provenance.notes = (anteriores + ("" if not anteriores or anteriores.endswith(".") else ".") + nota).strip()
        if not dry_run:
            acervo.save(registo, novo, target=caminho)
            acervo.write_history(caminho, novos)
        n += len(aplicados)
        feitos.append({"id": registo.id, "caminho": c["caminho"], "titulo": registo.title, "alteradores": aplicados})
        print(f"{'(dry-run) ' if dry_run else ''}{c['caminho']}: {len(aplicados)} alterador(es)")
    if not dry_run and feitos:
        anteriores = {json.loads(l)["id"]: json.loads(l) for l in APLICADOS.read_text(encoding="utf-8").splitlines() if l.strip()} if APLICADOS.exists() else {}
        for f in feitos:
            if f["id"] in anteriores:
                anteriores[f["id"]]["alteradores"] += f["alteradores"]
            else:
                anteriores[f["id"]] = f
        APLICADOS.write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in anteriores.values()), encoding="utf-8")
    print(f"Alteradores aplicados: {n}, em {len(feitos)} consolidados. Recusados: {len(recusadas)}.")
    for r in recusadas:
        print("  ", r)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("passo", choices=["entrada", "verificacao", "aplicar"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    {"entrada": entrada, "verificacao": verificacao}.get(args.passo, lambda: aplicar(args.dry_run))()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
