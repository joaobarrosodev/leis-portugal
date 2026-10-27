"""Piloto da fase 2: aplica as alterações aos diplomas de `consolidacao/selecao.jsonl`.

Para cada diploma lê as instruções do diploma que altera, aplica-as por regras, verifica o
resultado e escreve:

- `consolidacao/piloto/<caminho do registo>.md`: o texto consolidado (só quando todas as
  instruções foram aplicadas e a verificação passou), com os artigos no formato do acervo;
- `consolidacao/piloto/<caminho do registo>.alteracoes.json`: um registo por alteração
  aplicada (artigo, operação, texto antes e depois, excerto que a justifica, método);
- `consolidacao/resultados.jsonl`: o estado de cada diploma (aplicado, para o LLM, falhou a
  verificação, sem instruções…) e o motivo;
- `consolidacao/pendentes.jsonl`: as instruções que as regras não aplicaram, com o texto dos
  artigos em causa, prontas para o LLM (`llm.py`).

Nada em `data/` é alterado. Uso: `python consolidacao/consolidar.py [--amostra 50] [--semente 1]`.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import yaml

from alteracoes import ler, paragrafos
from aplicar import Fonte, aplicar
from texto import RAIZ, Corpo, com_titulos, dividir, front_matter, normalizar, publicado, sem_ligacoes
from verificar import republicacao, verificar

PASTA = RAIZ / "consolidacao"
SELECAO = PASTA / "selecao.jsonl"
PILOTO = PASTA / "piloto"


def _mencao_numero(texto: str, titulo: str) -> bool:
    """O número do original aparece no alterador, mesmo numa lista ("Decretos-Leis n.os 99/99, …, 45/2007")."""
    numero = re.sub(r"\s*\(.*\)$", "", titulo).split("n.º")[-1].strip()
    if not numero or numero == titulo:
        return False
    return re.search(rf"(?<![\w/]){re.escape(numero)}(?![\w/])", normalizar(sem_ligacoes(texto))) is not None


def _so_redacao(texto: str, titulo: str) -> bool:
    """O original só aparece como o diploma que deu a redação de outro ("na redação dada pelo …")."""
    numero = re.escape(re.sub(r"\s*\(.*\)$", "", titulo).split("n.º")[-1].strip())
    plano = normalizar(sem_ligacoes(texto))
    return bool(re.search(rf"(?:reda[cç]+[ãa]o (?:que lhe (?:foi|é) )?dada|alterad[oa]s?|republicad[oa]s?) pel[oa]s? [^.;]{{0,200}}?(?<![\w/]){numero}(?![\w/])", plano, re.I))


def processar(registo: dict, escrever: bool = True) -> dict:
    estado = {"id": registo["id"], "title": registo["title"], "path": registo["path"], "citacoes": registo["citacoes"],
              "alterador": registo["alterador"].get("title") or registo["alterador"]["id"]}
    alterador_meta = registo["alterador"]
    if registo.get("republicado_por"):
        return estado | {"estado": "excluído", "motivo": "tem republished_by: o texto atual está no consolidado"}
    if registo["text_quality"] != "texto":
        return estado | {"estado": "sem texto", "motivo": f"original só com {registo['text_quality']}"}
    if not alterador_meta.get("path"):
        return estado | {"estado": "sem texto", "motivo": "o diploma que altera não está no acervo"}
    if alterador_meta.get("text_quality") != "texto":
        return estado | {"estado": "sem texto", "motivo": f"o diploma que altera só tem {alterador_meta.get('text_quality')}"}

    # Os registos que o `acervo.py` já consolidou têm em `data/` o texto em vigor: aqui conta o publicado.
    texto_original, texto_alterador = publicado(RAIZ / registo["path"]), publicado(RAIZ / alterador_meta["path"])
    original = dividir(texto_original)
    if not original.artigos and (normalizado := com_titulos(texto_original)) is not None:
        # Artigos em texto corrido: os títulos vêm do parser da fase 3 (ver `com_titulos`).
        texto_original, original = normalizado, dividir(normalizado)
        estado["titulos_normalizados"] = True
    leitura = ler(texto_alterador, registo["title"], original)
    estado |= {"instrucoes": len(leitura.instrucoes), "por_aplicar": len(leitura.por_aplicar),
               "artigos_original": len(original.artigos)}

    if not leitura.instrucoes and not leitura.por_aplicar:
        if leitura.mencoes:
            motivo = "o alterador cita o original mas não lhe dá instruções de alteração"
        elif _mencao_numero(texto_alterador, registo["title"]):
            motivo = ("o original só aparece como diploma que deu a redação de outro"
                      if _so_redacao(texto_alterador, registo["title"]) else "o original só aparece numa lista ou remissão")
        else:
            motivo = "o alterador não menciona o original"
        return estado | {"estado": "sem alteração textual", "motivo": motivo}

    revogacoes = [p for p in leitura.por_aplicar if p.motivo.startswith("revogação do diploma inteiro")]
    if revogacoes and len(revogacoes) == len(leitura.por_aplicar) and not leitura.instrucoes:
        return estado | {"estado": "revogado por inteiro", "motivo": "o alterador revoga o original (o DRE dá-o como em vigor)",
                         "excerto": revogacoes[0].excerto}

    if not original.artigos:
        motivo = _sem_artigos(texto_original)
        return estado | {"estado": "para LLM", "motivo": motivo, "pendentes": _pendentes(registo, original, leitura, None, motivo)}

    meta = front_matter((RAIZ / alterador_meta["path"]).read_text(encoding="utf-8"))
    fonte = Fonte(alterador_meta["title"], (meta.get("source") or {}).get("official_url") or "", alterador_meta.get("publication_date") or "")
    consolidado = dividir(texto_original)
    resultado = aplicar(consolidado, leitura.instrucoes, fonte)
    problemas = verificar(original, consolidado, texto_alterador, registo["title"], leitura, resultado, registo.get("rotulos_dre", []))
    comparacao = republicacao(texto_alterador, consolidado, registo["title"], resultado.tocados) if resultado.registos else None
    if comparacao:
        estado["republicacao"] = comparacao
        if comparacao["diferentes"]:
            problemas.append(f"diferente da republicação no alterador: artigos {', '.join(comparacao['diferentes'][:10])}")
    estado |= {"aplicadas": len(resultado.registos), "falhas": len(resultado.falhas),
               "regras": dict(Counter(r.regra for r in resultado.registos))}

    if leitura.por_aplicar or resultado.falhas:
        estado |= {"estado": "para LLM", "motivo": _motivo_llm(leitura, resultado), "problemas": problemas,
                   "pendentes": _pendentes(registo, original, leitura, resultado)}
    elif problemas:
        # As regras aplicaram tudo, mas a verificação não passou: vai tudo para o LLM.
        estado |= {"estado": "falhou a verificação", "motivo": problemas[0], "problemas": problemas,
                   "pendentes": _pendentes(registo, original, leitura, None, "falhou a verificação")}
    else:
        estado |= {"estado": "aplicado por regra", "motivo": ""}

    if escrever and resultado.registos:
        destino = PILOTO / Path(registo["path"]).relative_to("data")
        destino.parent.mkdir(parents=True, exist_ok=True)
        json_registos = [asdict(r) | {"diploma": registo["id"], "alterador": alterador_meta["id"]} for r in resultado.registos]
        destino.with_suffix(".alteracoes.json").write_text(json.dumps(json_registos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if estado["estado"] == "aplicado por regra":
            destino.write_text(_markdown(registo, alterador_meta, consolidado, estado.get("titulos_normalizados", False)), encoding="utf-8")
            estado["consolidado"] = str(destino.relative_to(RAIZ))
    return estado


def _sem_artigos(texto: str) -> str:
    """Porque é que nem o parser da fase 3 dá os artigos do original."""
    from leis_portugal.domain.articles import parse_articles

    tipos = Counter(a.kind for a in parse_articles(texto))
    if tipos["artigo"]:
        return "original sem artigos identificados (numeração repetida ou que recomeça sem título de anexo)"
    if tipos["numero"]:
        return "original sem artigos identificados (só números do dispositivo: 1.º, 2.º, …)"
    if tipos["base"]:
        return "original sem artigos identificados (bases em texto corrido)"
    return "original sem artigos identificados"


def _motivo_llm(leitura, resultado) -> str:
    motivos = [p.motivo for p in leitura.por_aplicar] + [f["motivo"] for f in resultado.falhas]
    return Counter(re.sub(r"\s*\(.*|\d+\.º(-[A-Z])?", "", m).strip() for m in motivos).most_common(1)[0][0]


def _pendentes(registo: dict, original: Corpo, leitura, resultado, motivo: str = "") -> list[dict]:
    """O que fica para o LLM: a instrução e o texto atual dos artigos do original que nomeia."""
    itens = [{"motivo": p.motivo, "excerto": p.excerto} for p in leitura.por_aplicar]
    if resultado is None:
        itens += [{"motivo": motivo, "excerto": i.excerto} for i in leitura.instrucoes]
    else:
        itens += [{"motivo": f["motivo"], "excerto": f["excerto"]} for f in resultado.falhas]
    for item in itens:
        numeros = {re.sub(r"\s", "", n) for n in re.findall(r"artigos?\s+(\d+\s*\.?\s*º(?:-[A-Z])?)", item["excerto"])}
        item["artigos_original"] = [
            {"chave": a.chave, "texto": "\n".join(a.linhas).strip()} for a in original.artigos if a.numero.replace(" ", "") in numeros
        ]
    return itens


def _markdown(registo: dict, alterador: dict, consolidado: Corpo, titulos_normalizados: bool) -> str:
    cabecalho = {
        "id": registo["id"],
        "title": registo["title"],
        "original": registo["path"],
        "consolidacao": {
            "metodo": "piloto da fase 2 (consolidacao/consolidar.py), sem valor oficial",
            "estado": "por verificar às cegas",
            "alteracoes_aplicadas": [{"id": alterador["id"], "title": alterador["title"], "publication_date": alterador.get("publication_date")}],
        },
    }
    if titulos_normalizados:
        cabecalho["consolidacao"]["titulos_normalizados"] = "artigos em texto corrido no original, com título pelo parser da fase 3"
    return "---\n" + yaml.safe_dump(cabecalho, allow_unicode=True, sort_keys=False) + "---\n" + consolidado.texto()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--amostra", type=int, default=0, help="só uma amostra ao acaso de N diplomas")
    parser.add_argument("--semente", type=int, default=1)
    parser.add_argument("--saida", type=Path, default=PASTA / "resultados.jsonl")
    parser.add_argument("--pendentes", type=Path, default=PASTA / "pendentes.jsonl")
    args = parser.parse_args()
    registos = [json.loads(l) for l in SELECAO.read_text(encoding="utf-8").splitlines()]
    if args.amostra:
        registos = random.Random(args.semente).sample(registos, args.amostra)
    estados = [processar(r) for r in registos]
    pendentes = [{"id": e["id"], "title": e["title"], "itens": e.pop("pendentes")} for e in estados if "pendentes" in e]
    with args.saida.open("w", encoding="utf-8") as f:
        for e in estados:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    with args.pendentes.open("w", encoding="utf-8") as f:
        for p in pendentes:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    contagem = Counter(e["estado"] for e in estados)
    for estado, n in contagem.most_common():
        print(f"{n:4d}  {estado}")
        for motivo, m in Counter(e["motivo"] for e in estados if e["estado"] == estado).most_common(8):
            print(f"        {m:4d}  {motivo[:110]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
