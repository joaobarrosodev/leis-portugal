"""Vista compacta de uma ronda às cegas para um verificador, e a montagem da saída.

A verificação às cegas (ver `README.md`) recebe só `entrada-piloto-N-lote-NN.jsonl`. Num lote de
30 diplomas isso são mais de um milhão de tokens, por isso `vistas` divide a ronda em pedaços e
escreve, para cada um, uma vista com o que o verificador precisa e só vem da entrada:

- o texto do diploma que altera, inteiro (quando `alterador_completo` é `false`, só os artigos
  dele que mencionam o original, como na entrada);
- o texto do original e o texto consolidado **só dos artigos que diferem** (comparados pelo
  título, `texto_original_com_titulos` quando a entrada o traz), mais a lista dos títulos do
  consolidado e dos artigos que são iguais ao original.

Nada vem dos registos de alterações, das regras ou dos resultados. O verificador dá um veredicto
por artigo diferente e lista as instruções que não se vêem no consolidado; os artigos iguais ao
original ficam `certo` por omissão (se uma instrução os visava, o verificador di-lo em
`instrucoes_em_falta` e o diploma não passa).

`saida` junta os JSON dos verificadores e escreve `saida-piloto-N-lote-NN.jsonl` no formato das
rondas anteriores (uma linha por artigo e uma por diploma).

Uso:
    python consolidacao/cegas_vista.py vistas RONDA PASTA [--max-chars 140000]
    python consolidacao/cegas_vista.py saida RONDA PASTA
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from texto import RAIZ


VERIFICACAO = RAIZ / "consolidacao" / "verificacao"
_TITULO = re.compile(r"^#{1,6} ", re.M)


def blocos(texto: str) -> list[tuple[str, str]]:
    """O corpo dividido nos títulos: (chave, texto). A chave é o título; repetidos levam `#2`, …
    O que vem antes do primeiro título (depois do `# Título` do diploma) é o "(preâmbulo)"."""
    texto = re.sub(r"\A# [^\n]*\n+", "", texto.strip())
    partes = [0, *(m.start() for m in _TITULO.finditer(texto) if m.start())]
    resultado, vistos = [], {}
    for a, b in zip(partes, [*partes[1:], len(texto)], strict=True):
        bloco = texto[a:b].strip()
        if not bloco:
            continue
        chave = bloco.splitlines()[0].lstrip("#").strip() if _TITULO.match(bloco) else "(preâmbulo)"
        vistos[chave] = vistos.get(chave, 0) + 1
        resultado.append((chave if vistos[chave] == 1 else f"{chave} #{vistos[chave]}", bloco))
    return resultado


def comparar(d: dict) -> dict:
    original = blocos(d.get("texto_original_com_titulos") or d["texto_original"])
    consolidado = blocos(d["texto_consolidado"])
    por_chave = dict(original)
    chaves_consolidado = {c for c, _ in consolidado}
    return {
        "diferentes": [(c, por_chave.get(c), b) for c, b in consolidado if por_chave.get(c) != b],
        "iguais": [c for c, b in consolidado if por_chave.get(c) == b],
        "removidos": [(c, b) for c, b in original if c not in chaves_consolidado],
    }


def vista(d: dict) -> str:
    c = comparar(d)
    linhas = [
        f"## DIPLOMA {d['id']}", f"Original: {d['titulo']}", f"Altera-o: {d['alterador']}",
        f"Alterador completo: {str(d['alterador_completo']).lower()}",
        f"Títulos normalizados: {str(bool(d.get('titulos_normalizados'))).lower()}", "",
        "### TEXTO DO DIPLOMA QUE ALTERA", d["texto_alterador"].strip(), "",
        f"### ARTIGOS DO CONSOLIDADO IGUAIS AO ORIGINAL ({len(c['iguais'])})", "; ".join(c["iguais"]) or "(nenhum)", "",
        f"### ARTIGOS DO CONSOLIDADO QUE DIFEREM DO ORIGINAL ({len(c['diferentes'])})",
    ]
    for chave, antes, depois in c["diferentes"]:
        linhas += [f"#### ARTIGO: {chave}", "--- ORIGINAL" if antes is not None else "--- ORIGINAL: (não existe: artigo novo)"]
        if antes is not None:
            linhas.append(antes)
        linhas += ["--- CONSOLIDADO", depois, ""]
    linhas.append(f"### ARTIGOS DO ORIGINAL QUE NÃO ESTÃO NO CONSOLIDADO ({len(c['removidos'])})")
    for chave, antes in c["removidos"]:
        linhas += [f"#### ARTIGO: {chave}", antes, ""]
    linhas.append("")
    return "\n".join(linhas)


def _entradas(ronda: int) -> list[tuple[Path, dict]]:
    ficheiros = sorted(VERIFICACAO.glob(f"entrada-piloto-{ronda}-lote-*.jsonl")) or [VERIFICACAO / f"entrada-piloto-{ronda}.jsonl"]
    return [(f, json.loads(l)) for f in ficheiros for l in f.read_text(encoding="utf-8").splitlines()]


def vistas(ronda: int, pasta: Path, max_chars: int) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    pedacos: list[dict] = []
    atual: dict | None = None
    for ficheiro, d in _entradas(ronda):
        texto = vista(d)
        if atual is None or atual["lote"] != ficheiro.name or (atual["chars"] + len(texto) > max_chars and atual["ids"]):
            atual = {"lote": ficheiro.name, "ids": [], "chars": 0, "textos": []}
            pedacos.append(atual)
        atual["ids"].append(d["id"])
        atual["chars"] += len(texto)
        atual["textos"].append(texto)
    indice = []
    for n, p in enumerate(pedacos, 1):
        ficheiro = pasta / f"vista-{n:03d}.md"
        ficheiro.write_text("\n".join(p["textos"]), encoding="utf-8")
        indice.append({"pedaco": n, "lote": p["lote"], "ids": p["ids"], "chars": p["chars"], "vista": str(ficheiro), "resposta": str(pasta / f"resposta-{n:03d}.json")})
    (pasta / "pedacos.json").write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(pedacos)} pedaços, {sum(p['chars'] for p in pedacos)} caracteres, em {pasta}")


def saida(ronda: int, pasta: Path) -> None:
    indice = json.loads((pasta / "pedacos.json").read_text(encoding="utf-8"))
    respostas: dict[str, dict] = {}
    for p in indice:
        r = Path(p["resposta"])
        if r.exists():
            respostas |= {x["id"]: x for x in json.loads(r.read_text(encoding="utf-8"))}
    por_lote: dict[str, list[str]] = {}
    sem_resposta = 0
    for ficheiro, d in _entradas(ronda):
        if d["id"] not in respostas:
            sem_resposta += 1
            continue
        r = respostas[d["id"]]
        c = comparar(d)
        veredictos = {a["artigo"]: a for a in r.get("artigos", [])}
        linhas = []
        for chave in [x for x, _, _ in c["diferentes"]]:
            a = veredictos.get(chave) or {"veredicto": "dúvida", "motivo": "o verificador não deu veredicto para este artigo", "texto_esperado": ""}
            linhas.append({"id": d["id"], "artigo": chave, "veredicto": a["veredicto"], "motivo": a.get("motivo", ""), "texto_esperado": a.get("texto_esperado", "")})
        for chave in c["iguais"]:
            linhas.append({"id": d["id"], "artigo": chave, "veredicto": "certo", "motivo": "Igual ao original letra a letra (nenhuma instrução o visa).", "texto_esperado": ""})
        for chave, _ in c["removidos"]:
            a = veredictos.get(chave)
            linhas.append({"id": d["id"], "artigo": chave, "veredicto": (a or {}).get("veredicto", "dúvida"), "motivo": (a or {}).get("motivo", "artigo do original que não está no consolidado"), "texto_esperado": ""})
        linhas.append({
            "id": d["id"], "instrucoes_em_falta": r.get("instrucoes_em_falta", []), "artigos_a_mais": r.get("artigos_a_mais", []),
            "artigos_em_falta": r.get("artigos_em_falta", []), "fora_dos_artigos": r.get("fora_dos_artigos") or "dúvida: o verificador não respondeu",
        })
        por_lote.setdefault(ficheiro.name, []).extend(json.dumps(x, ensure_ascii=False) for x in linhas)
    for nome, linhas in por_lote.items():
        destino = VERIFICACAO / nome.replace("entrada-", "saida-")
        destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"{len(respostas)} diplomas com resposta, {sem_resposta} sem; {len(por_lote)} ficheiros de saída")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("comando", choices=["vistas", "saida"])
    parser.add_argument("ronda", type=int)
    parser.add_argument("pasta", type=Path)
    parser.add_argument("--max-chars", type=int, default=140_000)
    args = parser.parse_args()
    if args.comando == "vistas":
        vistas(args.ronda, args.pasta, args.max_chars)
    else:
        saida(args.ronda, args.pasta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
