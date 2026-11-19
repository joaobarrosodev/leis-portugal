"""A planta das zonas de caça cujo n.º 1.º foi reescrito por um alterador (19/11/2026).

Ao fechar a auditoria dos consolidados apareceu este caso: um alterador reescreve o n.º 1.º de
uma portaria de concessão de caça («Ficam sujeitos ao regime cinegético especial os prédios …
englobados pela poligonal constante da planta anexa à presente portaria …») e publica a planta
nova. A consolidação aplicou o n.º 1.º novo, mas a imagem da planta ficou a do original. O n.º
1.º em vigor remete para a planta do alterador, e o consolidado mostrava a antiga.

A regra (sem LLM), só quando tudo bate:

- o alterador tem no rótulo do DRE «Alterado o n.º 1» (ou «nova redacção ao n.º 1»), o seu
  texto fala da «planta anexa à presente portaria» e traz uma só imagem;
- é o último alterador assim do consolidado;
- o consolidado tem uma só imagem e o n.º 1.º tem a nota «> Alterado pelo/a» desse alterador.

Troca-se o endereço da imagem do consolidado pelo da imagem do alterador, com a nota
«> Alterado pelo/a …» a seguir. O alterador já está nos `acts`; a data da versão não muda. Os
que não batem ficam em `auditoria/plantas-n1.jsonl` com o motivo. Verificação às cegas de todos
(Sonnet, `llm/plantas/PROMPT-verificador.md`).

Uso: `python consolidacao/plantas_n1.py entrada|aplicar [--dry-run]`.
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
from acervo import blocos, historico  # noqa: E402
from texto import RAIZ, corpo, front_matter, sem_ligacoes  # noqa: E402

from leis_portugal.domain.history import render_version, summarize  # noqa: E402
from leis_portugal.infrastructure.repository import Acervo  # noqa: E402

LLM = PASTA / "llm" / "plantas"
ESTADO = PASTA / "auditoria" / "plantas-n1.jsonl"
APLICADAS = PASTA / "auditoria" / "plantas-aplicadas.jsonl"
POR_LOTE = 60
_LIGACAO = re.compile(r"\]\((https://files\.diariodarepublica\.pt/[^)]+)\)")
_LINHA_IMAGEM = re.compile(r"^\[\((?:ver )?(?:documento original|planta[^)]*|plantas[^)]*)\)\]\((https://files\.diariodarepublica\.pt/[^)]+)\)\s*$", re.I)
_N1 = re.compile(r"\b(alterad[oa]s?|nova reda[cç]+[ãa]o)\b[^.]{0,40}\bn\.?\s*[ºo°]?\s*1(\.?º)?\b", re.I)
_PLANTA = re.compile(r"planta anexa (?:à|ao) presente (?:portaria|diploma)", re.I)


def _nota(meta: dict) -> str:
    caminho = (meta.get("identifiers") or {}).get("dre_path")
    ligacao = f"[{meta['title']}](https://diariodarepublica.pt{caminho})" if caminho else meta["title"]
    return f"> Alterado pelo/a {ligacao}, publicado em {meta['publication_date']}."


def casos() -> tuple[list[dict], list[dict]]:
    """Os que a regra troca e os que ficam, com o motivo."""
    consolidados = {json.loads(l)["id"]: json.loads(l) for l in (PASTA / "auditoria" / "vigencia.jsonl").read_text(encoding="utf-8").splitlines()}
    trocar, ficam = [], []
    for linha in (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines():
        d = json.loads(linha)
        if d["id"] not in consolidados:
            continue
        caminho = consolidados[d["id"]]["caminho"]
        linhas = corpo((RAIZ / caminho).read_text(encoding="utf-8")).split("\n")
        if not any("planta" in l.lower() for l in linhas):
            continue
        ultimo = None
        for a in sorted(d["alteradores"], key=lambda a: (a.get("ordem") or "", a["id"])):
            if not a.get("path") or not _N1.search(" ".join(a.get("rotulos_dre") or [])):
                continue
            ta = corpo((RAIZ / a["path"]).read_text(encoding="utf-8"))
            imagens = list(dict.fromkeys(_LIGACAO.findall(ta)))
            if imagens and _PLANTA.search(ta):
                ultimo = (a, imagens, ta)
        if not ultimo:
            continue
        a, imagens, ta = ultimo
        base = {"id": d["id"], "titulo": consolidados[d["id"]]["titulo"], "caminho": caminho, "alterador": a["id"], "alterador_titulo": a["title"]}
        indices = [i for i, l in enumerate(linhas) if _LINHA_IMAGEM.match(l.strip())]
        if any(_LIGACAO.findall(linhas[i]) == imagens[:1] for i in indices):
            continue  # a planta do alterador já lá está
        if len(imagens) != 1:
            ficam.append(base | {"motivo": f"o alterador tem {len(imagens)} imagens; não se sabe qual é a planta"})
        elif len(indices) != 1:
            ficam.append(base | {"motivo": f"o consolidado tem {len(indices)} imagens; não se sabe qual é a planta"})
        elif not any(l.startswith("> Alterado pelo/a") and a["title"] in l for l in linhas):
            ficam.append(base | {"motivo": "o n.º 1.º do consolidado não tem a nota deste alterador: não se confirma que a redação em vigor é a dele"})
        else:
            i = indices[0]
            n1 = next((j for j, l in enumerate(linhas) if re.match(r"^1\.?º?\s", sem_ligacoes(l).strip())), None)
            trocar.append(base | {"linha": i, "antes": linhas[i], "depois": linhas[i].replace(_LIGACAO.findall(linhas[i])[0], imagens[0]),
                                  "n1_do_consolidado": sem_ligacoes(linhas[n1]) if n1 is not None else None,
                                  "texto_do_alterador": sem_ligacoes(ta)[:6000], "imagem_do_alterador": imagens[0]})
    return trocar, ficam


def entrada() -> None:
    trocar, ficam = casos()
    LLM.mkdir(parents=True, exist_ok=True)
    for f in LLM.glob("verificacao-entrada-*.jsonl"):
        f.unlink()
    for k in range(0, len(trocar), POR_LOTE):
        lote = [{"n": k + j + 1, "diploma": t["titulo"], "id": t["id"], "alterador": t["alterador_titulo"], "texto_do_alterador": t["texto_do_alterador"],
                 "n1_do_consolidado": t["n1_do_consolidado"], "linha_da_planta_antes": t["antes"], "linha_da_planta_depois": t["depois"]} for j, t in enumerate(trocar[k : k + POR_LOTE])]
        (LLM / f"verificacao-entrada-{k // POR_LOTE + 1}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lote), encoding="utf-8")
    ESTADO.write_text("".join(json.dumps({k: v for k, v in t.items() if k not in ("texto_do_alterador",)} | {"estado": "a trocar"}, ensure_ascii=False) + "\n" for t in trocar)
                      + "".join(json.dumps(f | {"estado": "fica, com o motivo"}, ensure_ascii=False) + "\n" for f in ficam), encoding="utf-8")
    print(f"{len(trocar)} a trocar ({-(-len(trocar) // POR_LOTE)} lotes de verificação), {len(ficam)} ficam com o motivo")


def aplicar(dry_run: bool) -> None:
    trocar, _ = casos()
    entradas = {}
    for f in sorted(LLM.glob("verificacao-entrada-*.jsonl")):
        for linha in f.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                e = json.loads(linha)
                entradas[e["n"]] = e
    ok = set()
    for f in sorted(LLM.glob("verificacao-saida-*.jsonl")):
        for linha in f.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                v = json.loads(linha)
                e = entradas.get(v["n"])
                if v["veredicto"] == "certo" and e:
                    ok.add((e["id"], e["linha_da_planta_depois"]))
    por_n = {t["id"]: t for t in trocar}
    acervo = Acervo(RAIZ)
    feitos, recusadas = [], []
    for id_, t in sorted(por_n.items()):
        if (id_, t["depois"]) not in ok:
            continue  # só o que a verificação às cegas deu certo, e com a mesma troca
        caminho = RAIZ / t["caminho"]
        registo, _ = acervo.read(caminho)
        dados = acervo.read_history(caminho)
        if len(dados["versions"]) != 2:
            recusadas.append(f"{t['caminho']}: o histórico não tem duas versões")
            continue
        linhas = corpo(caminho.read_text(encoding="utf-8")).split("\n")
        if linhas[t["linha"]] != t["antes"]:
            recusadas.append(f"{t['caminho']}: a linha da planta mudou")
            continue
        linhas[t["linha"]] = t["depois"]
        caminho_alterador = next(a["path"] for a in _alteradores(id_) if a["id"] == t["alterador"])
        meta = front_matter((RAIZ / caminho_alterador).read_text(encoding="utf-8"))
        novo = re.sub(r"\n{3,}", "\n\n", "\n".join(rt._com_notas(linhas, {t["linha"]: {_nota(meta)}})))
        original = render_version(dados, dados["versions"][0], title=registo.title)
        primeira, segunda = (dict(v) for v in dados["versions"])
        if "Altera planta" not in segunda["changes"]:
            segunda["changes"] = list(segunda["changes"]) + ["Altera planta"]
        novos = historico(registo.id, registo.title, original, novo, [primeira, segunda])
        if blocos(render_version(novos, novos["versions"][1], title=registo.title)) != blocos(novo) or blocos(render_version(novos, novos["versions"][0], title=registo.title)) != blocos(original):
            recusadas.append(f"{t['caminho']}: o histórico não reproduz o texto")
            continue
        registo.version_history = summarize(novos, acervo.history_path(caminho).name)
        nota = f" Planta trocada pela do alterador que reescreveu o n.º 1.º (consolidacao/plantas_n1.py, verificada às cegas): {t['alterador_titulo']}."
        if "consolidacao/plantas_n1.py" not in (registo.provenance.notes or ""):
            anteriores = (registo.provenance.notes or "").rstrip()
            registo.provenance.notes = (anteriores + ("" if not anteriores or anteriores.endswith(".") else ".") + nota).strip()
        if not dry_run:
            acervo.save(registo, novo, target=caminho)
            acervo.write_history(caminho, novos)
        feitos.append({"id": id_, "caminho": t["caminho"], "titulo": t["titulo"], "alterador": t["alterador"], "alterador_titulo": t["alterador_titulo"], "antes": t["antes"], "depois": t["depois"]})
    if not dry_run and feitos:
        anteriores = {json.loads(l)["id"]: json.loads(l) for l in APLICADAS.read_text(encoding="utf-8").splitlines() if l.strip()} if APLICADAS.exists() else {}
        for f in feitos:
            anteriores[f["id"]] = f
        APLICADAS.write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in anteriores.values()), encoding="utf-8")
    print(f"{'(dry-run) ' if dry_run else ''}Plantas trocadas: {len(feitos)}. Recusadas: {len(recusadas)}.")
    for r in recusadas:
        print("  ", r)


_SELECAO: dict[str, list[dict]] = {}


def _alteradores(id_: str) -> list[dict]:
    if not _SELECAO:
        for linha in (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines():
            d = json.loads(linha)
            _SELECAO[d["id"]] = d["alteradores"]
    return _SELECAO[id_]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("passo", choices=["entrada", "aplicar"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    entrada() if args.passo == "entrada" else aplicar(args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
