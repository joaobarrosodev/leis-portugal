"""Repara as notas e as etiquetas das retificações já aplicadas fora do articulado (19/11/2026).

Até 19/11, `retificacoes._artigo_de` dava ao último artigo o texto depois da fórmula final
(promulgação, assinatura) ou de um anexo sem título Markdown. Por isso, numa troca num anexo,
a nota «> Retificado pelo/a …» ia para o fim do diploma, e o histórico dizia «Retifica Artigo 71»
quando era o anexo II. A regra está corrigida (`_FIM_DO_ARTICULADO`). Este script refaz os
registos já aplicados (`auditoria/retificacoes-aplicadas.jsonl`):

1. tira do corpo as notas das retificações aplicadas a esse registo;
2. localiza cada troca (a linha `depois`, a mais perto da linha em que foi feita) e confirma que,
   com a regra antiga, as notas voltam a dar o texto de hoje, letra a letra (senão, não mexe);
3. põe as notas com a regra nova e troca as etiquetas «Retifica Artigo N» que estavam erradas;
4. refaz o histórico como `retificacoes_llm.aplicar`, com a mesma guarda.

Uso: `python consolidacao/retificacoes_notas.py [--dry-run]`, na pasta principal (muda o `data/`).
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
from texto import RAIZ, corpo, front_matter  # noqa: E402

from leis_portugal.domain.history import render_version, summarize  # noqa: E402
from leis_portugal.infrastructure.repository import Acervo  # noqa: E402


def _artigo_antigo(linhas: list[str], i: int) -> str | None:
    """A regra de antes de 19/11, só para confirmar que as trocas foram bem localizadas."""
    for j in range(i, -1, -1):
        if rt._TITULO.match(linhas[j]):
            m = rt._ARTIGO_TITULO.match(linhas[j])
            return rt._numero(m.group(1)) if m else None
    return None


def _com_notas(linhas: list[str], tocadas: dict[int, set[str]], artigo_de) -> list[str]:
    original = rt._artigo_de
    rt._artigo_de = artigo_de
    try:
        return rt._com_notas(linhas, tocadas)
    finally:
        rt._artigo_de = original


def _limpar(linhas: list[str]) -> str:
    return re.sub(r"\n{3,}", "\n\n", "\n".join(linhas))


class NaoConfirmado(Exception):
    pass


def reparar(registo_aplicado: dict) -> tuple[str, list[tuple[dict, str | None, str | None]]] | None:
    """O corpo novo e as trocas cuja etiqueta muda (a troca, o artigo de antes e o de agora), ou None
    se nada muda. `NaoConfirmado` quando a troca não se acha ou as notas não se reproduzem."""
    caminho = RAIZ / registo_aplicado["caminho"]
    atual = corpo(caminho.read_text(encoding="utf-8"))
    notas = {}
    for r in registo_aplicado["retificacoes"]:
        meta = front_matter((RAIZ / r["caminho_retificacao"]).read_text(encoding="utf-8"))
        notas[r["retificacao"]] = rt._nota(meta)
    sem = [l for l in atual.split("\n") if l not in set(notas.values())]
    sem = _limpar(sem).split("\n")
    tocadas_velhas: dict[int, set[str]] = defaultdict(set)
    tocadas_novas: dict[int, set[str]] = defaultdict(set)
    mudam = []
    usadas: set[int] = set()
    todas = [t for r in registo_aplicado["retificacoes"] for t in r["trocas"]]
    for r in registo_aplicado["retificacoes"]:
        for t in r["trocas"]:
            bloco = (t.get("depois") or "").split("\n")
            if not bloco[0]:
                continue  # uma supressão: a nota ficou onde estava o parágrafo, não se mexe
            if any(o is not t and o.get("antes") == t["depois"] for o in todas):
                continue  # outra retificação trocou depois a mesma linha: conta a dela
            # numa inserção (várias linhas), a nota vai para o fim do bloco inserido
            candidatas = [i for i in range(len(sem) - len(bloco) + 1) if sem[i : i + len(bloco)] == bloco and i not in usadas]
            if not candidatas:
                raise NaoConfirmado(f"a linha da troca L{t['linha']} não se acha")
            i = min(candidatas, key=lambda k: abs(k - int(t["linha"])))
            usadas.add(i)
            i += len(bloco) - 1
            tocadas_velhas[i].add(notas[r["retificacao"]])
            tocadas_novas[i].add(notas[r["retificacao"]])
            novo_artigo = rt._artigo_de(sem, i)
            if novo_artigo != t.get("artigo"):
                mudam.append((t, t.get("artigo"), novo_artigo))
    if not mudam:
        return None
    if _limpar(_com_notas(sem, tocadas_velhas, _artigo_antigo)).rstrip() != atual.rstrip():
        raise NaoConfirmado("as notas não se reproduzem com a regra antiga")
    return _limpar(_com_notas(sem, tocadas_novas, rt._artigo_de)), mudam


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    aplicadas_f = rt.APLICADAS
    aplicadas = [json.loads(l) for l in aplicadas_f.read_text(encoding="utf-8").splitlines() if l.strip()]
    acervo = Acervo(RAIZ)
    feitos, nao_confirmados = 0, []
    for d in aplicadas:
        caminho = RAIZ / d["caminho"]
        try:
            resultado = reparar(d)
        except NaoConfirmado as erro:
            nao_confirmados.append(f"{d['caminho']}: {erro}")
            continue
        if resultado is None:
            continue
        novo, mudam = resultado
        registo, _ = acervo.read(caminho)
        dados = acervo.read_history(caminho)
        primeira, segunda = (dict(v) for v in dados["versions"])
        mudadas = {id(t) for t, _, _ in mudam}
        velhos = {f"Retifica Artigo {a}" for _, a, _ in mudam if a}
        mantidos = {f"Retifica Artigo {t.get('artigo')}" for r in d["retificacoes"] for t in r["trocas"]
                    if t.get("artigo") and id(t) not in mudadas}
        changes = [c for c in segunda["changes"] if c not in velhos or c in mantidos]
        for _, _, n in mudam:
            etiqueta = f"Retifica Artigo {n}" if n else "Retifica texto"
            if etiqueta not in changes:
                changes.append(etiqueta)
        segunda["changes"] = changes
        original = render_version(dados, dados["versions"][0], title=registo.title)
        novos = historico(registo.id, registo.title, original, novo, [primeira, segunda])
        if blocos(render_version(novos, novos["versions"][1], title=registo.title)) != blocos(novo) or blocos(render_version(novos, novos["versions"][0], title=registo.title)) != blocos(original):
            nao_confirmados.append(f"{d['caminho']}: o histórico não reproduz o texto")
            continue
        registo.version_history = summarize(novos, acervo.history_path(caminho).name)
        if not args.dry_run:
            acervo.save(registo, novo, target=caminho)
            acervo.write_history(caminho, novos)
            for t, _, n in mudam:
                t["artigo"] = n
        feitos += 1
        print(f"{'(dry-run) ' if args.dry_run else ''}{d['caminho']}: {len(mudam)} troca(s) fora do articulado; " + ", ".join(sorted({f'{a} → {n or "texto"}' for _, a, n in mudam})))
    if not args.dry_run:
        aplicadas_f.write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in aplicadas), encoding="utf-8")
    print(f"Reparados: {feitos}. Não confirmados: {len(nao_confirmados)}.")
    for n in nao_confirmados:
        print("  ", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
