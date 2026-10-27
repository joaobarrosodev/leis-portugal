"""Seleção do piloto da fase 2: diplomas em vigor alterados uma só vez e muito citados.

Lê o índice exportado (`leis-portugal export` → `exports/leis-portugal.sqlite`) e escreve
`consolidacao/selecao.jsonl`, um registo por diploma:

- em vigor segundo o DRE (`in_force` ou `partially_in_force`, mesmo com revogações parciais),
  português ou regional, `version_kind = original`;
- uma só alteração (um único alvo distinto nas relações `amended_by`);
- 10 ou mais citações no acervo (relações `cites` de outros registos).

Pelo export de 26/10/2026 são 671. Ficam marcados (e de fora do piloto) os que têm
`republished_by` no front matter: o texto atual já está no consolidado que os republicou.
Para cada um junta o diploma que altera e os artigos dele que mencionam o original.

Uso: `python consolidacao/selecionar.py [--export F]`.

**Escala (`--todos`):** todos os em vigor (`in_force`, `partially_in_force`), portugueses e
regionais, `version_kind = original`, com texto (`text_quality = texto`) e pelo menos uma
relação `amended_by`, qualquer número de alterações e de citações. Escreve
`consolidacao/selecao-escala.jsonl` com, por diploma, `alteradores` (todos os diplomas que
alteram, por ordem de data de publicação; os que não estão no acervo só com o alvo da relação,
ordenados pela data da relação ou no fim), `citacoes` e `republicado_por`. Pelo export de
26/10/2026 são 25.498 (os 25.940 do plano contam também 442 diplomas da UE).
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from texto import RAIZ, artigos_alteradores, corpo, front_matter

SAIDA = RAIZ / "consolidacao" / "selecao.jsonl"
SAIDA_ESCALA = RAIZ / "consolidacao" / "selecao-escala.jsonl"
COLUNAS = "id, title, path, text_quality, document_type, legal_status, publication_date"


def export_por_omissao() -> Path:
    """O export deste checkout ou, num worktree, o da pasta principal (o export não está no git)."""
    local = RAIZ / "exports" / "leis-portugal.sqlite"
    if local.exists():
        return local
    comum = subprocess.run(["git", "rev-parse", "--git-common-dir"], capture_output=True, text=True, cwd=RAIZ)
    return Path(comum.stdout.strip()).resolve().parent / "exports" / "leis-portugal.sqlite"


def selecionar(db: sqlite3.Connection) -> list[dict]:
    colunas = COLUNAS
    alvo = {
        linha[0]: dict(zip(colunas.split(", "), linha))
        for linha in db.execute(
            f"select {colunas} from documentos where legal_status in ('in_force', 'partially_in_force')"
            " and version_kind = 'original' and jurisdiction in ('portugal', 'regional')"
        )
    }
    alteracoes: dict[str, list[dict]] = defaultdict(list)
    for origem, alvo_rel, alvo_id, data, rotulo in db.execute(
        "select source_id, target, target_id, date, label from relacoes where type = 'amended_by'"
    ):
        if origem in alvo:
            alteracoes[origem].append({"alvo": alvo_rel, "id": alvo_id, "data": data, "rotulo": rotulo})
    citacoes: dict[str, set[str]] = defaultdict(set)
    for origem, citado in db.execute("select source_id, target_id from relacoes where type = 'cites' and target_id is not null"):
        if citado in alteracoes:
            citacoes[citado].add(origem)

    resultado = []
    for diploma, lista in alteracoes.items():
        if len({a["alvo"] for a in lista}) != 1 or len(citacoes[diploma]) < 10:
            continue
        registo = alvo[diploma] | {"citacoes": len(citacoes[diploma])}
        alterador_id = lista[0]["id"]
        alterador = db.execute(f"select {colunas} from documentos where id = ?", (alterador_id,)).fetchone() if alterador_id else None
        registo["alterador"] = dict(zip(colunas.split(", "), alterador)) if alterador else {"id": lista[0]["alvo"]}
        registo["rotulos_dre"] = sorted({a["rotulo"] for a in lista if a["rotulo"]})
        registo["datas_dre"] = sorted({a["data"] for a in lista if a["data"]})
        resultado.append(registo)
    return sorted(resultado, key=lambda r: (-r["citacoes"], r["id"]))


def selecionar_todos(db: sqlite3.Connection) -> list[dict]:
    """Escala: todos os em vigor alterados, com texto, com os alteradores por ordem de data."""
    alvo = {
        linha[0]: dict(zip(COLUNAS.split(", "), linha, strict=True))
        for linha in db.execute(
            f"select {COLUNAS} from documentos where legal_status in ('in_force', 'partially_in_force')"
            " and version_kind = 'original' and jurisdiction in ('portugal', 'regional') and text_quality = 'texto'"
        )
    }
    relacoes: dict[str, dict[str, dict]] = defaultdict(dict)  # original -> alvo da relação -> relação
    for origem, alvo_rel, alvo_id, data, rotulo in db.execute(
        "select source_id, target, target_id, date, label from relacoes where type = 'amended_by'"
    ):
        if origem not in alvo:
            continue
        r = relacoes[origem].setdefault(alvo_rel, {"alvo": alvo_rel, "id": alvo_id, "rotulos": set(), "datas": set()})
        if rotulo:
            r["rotulos"].add(rotulo)
        if data:
            r["datas"].add(data)
    citacoes: dict[str, set[str]] = defaultdict(set)
    for origem, citado in db.execute("select source_id, target_id from relacoes where type = 'cites' and target_id is not null"):
        if citado in relacoes:
            citacoes[citado].add(origem)
    documentos: dict[str, dict] = {}
    ids = sorted({r["id"] for lista in relacoes.values() for r in lista.values() if r["id"]})
    for i in range(0, len(ids), 500):
        lote = ids[i : i + 500]
        for linha in db.execute(f"select {COLUNAS} from documentos where id in ({','.join('?' * len(lote))})", lote):
            documentos[linha[0]] = dict(zip(COLUNAS.split(", "), linha, strict=True))

    def alterador(r: dict) -> dict:
        meta = documentos.get(r["id"]) if r["id"] else None
        base = dict(meta) if meta else {"id": r["id"] or r["alvo"], "title": r["alvo"]}
        datas = sorted(r["datas"])
        base["rotulos_dre"] = sorted(r["rotulos"])
        base["datas_dre"] = datas
        # A ordem: data de publicação; sem ela, a data da relação do DRE; sem nenhuma, no fim.
        base["ordem"] = base.get("publication_date") or (datas[-1] if datas else "9999-99-99")
        return base

    resultado = []
    for diploma, lista in relacoes.items():
        alteradores = sorted((alterador(r) for r in lista.values()), key=lambda a: (a["ordem"], a["id"]))
        resultado.append(alvo[diploma] | {"citacoes": len(citacoes[diploma]), "alteradores": alteradores, "n_alteracoes": len(alteradores)})
    return sorted(resultado, key=lambda r: (-r["citacoes"], r["id"]))


def completar(registo: dict) -> dict:
    """Junta o que vem dos ficheiros: `republished_by` e os artigos do alterador que citam o original."""
    original = RAIZ / registo["path"]
    meta = front_matter(original.read_text(encoding="utf-8")) if original.exists() else {}
    registo["republicado_por"] = [
        r.get("target") for r in meta.get("relationships") or [] if r.get("type") == "republished_by"
    ]
    if "alteradores" in registo:
        return registo  # escala: os artigos dos alteradores que citam o original calculam-se quando são precisos
    alterador = registo["alterador"]
    caminho = RAIZ / alterador["path"] if alterador.get("path") else None
    if caminho and caminho.exists() and alterador.get("text_quality") == "texto":
        texto = corpo(caminho.read_text(encoding="utf-8"))
        registo["artigos_alteradores"] = [a.chave for a in artigos_alteradores(texto, registo["title"])]
    else:
        registo["artigos_alteradores"] = []
    return registo


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--export", type=Path, default=None)
    parser.add_argument("--saida", type=Path, default=None)
    parser.add_argument("--todos", action="store_true", help="escala: todos os em vigor alterados com texto")
    args = parser.parse_args()
    saida = args.saida or (SAIDA_ESCALA if args.todos else SAIDA)
    db = sqlite3.connect(args.export or export_por_omissao())
    registos = [completar(r) for r in (selecionar_todos(db) if args.todos else selecionar(db))]
    with saida.open("w", encoding="utf-8") as f:
        for registo in registos:
            f.write(json.dumps(registo, ensure_ascii=False) + "\n")
    republicados = sum(bool(r["republicado_por"]) for r in registos)
    print(f"{len(registos)} diplomas; {republicados} com republished_by; {saida.relative_to(RAIZ)}")
    if args.todos:
        por_n = Counter(min(r["n_alteracoes"], 11) for r in registos)
        sem_acervo = sum(1 for r in registos for a in r["alteradores"] if not a.get("path"))
        sem_texto = sum(1 for r in registos for a in r["alteradores"] if a.get("path") and a.get("text_quality") != "texto")
        print(f"alterações: 1 → {por_n[1]}, 2–3 → {por_n[2] + por_n[3]}, 4–10 → {sum(por_n[k] for k in range(4, 11))}, >10 → {por_n[11]}")
        print(f"alteradores fora do acervo: {sem_acervo}; sem texto: {sem_texto}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
