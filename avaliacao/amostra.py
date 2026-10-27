"""Candidatos para o conjunto de avaliação (sessão A): artigos reais de onde se tiram perguntas.

Lê o índice exportado (`leis-portugal export` → `exports/leis-portugal.sqlite`) e escreve um
ficheiro JSONL por tipo em `--saida`:

- `literal.jsonl`: artigos de diplomas em vigor e consolidados (texto atual garantido);
- `temporal.jsonl`: artigos cuja redação mudou, com o texto numa data passada e o atual;
- `revogada.jsonl`: artigos de diplomas revogados, com o ato que os revogou;
- `distrator.jsonl`: artigos ao acaso, dados à verificação nas perguntas sem resposta.

A amostra é reprodutível (`--semente`). Uso: `python avaliacao/amostra.py --saida <pasta>`.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sqlite3
from datetime import date
from pathlib import Path

from comum import EXPORT, RAIZ, Artigo, artigos, corpo, normalizar, texto_em


EM_VIGOR = "legal_status in ('in_force', 'partially_in_force') and id not in (select source_id from relacoes where type = 'repealed_by')"
NACIONAL = "jurisdiction in ('portugal', 'regional') and text_quality = 'texto'"
_ORTOGRAFIA = [("cç", "ç"), ("pç", "ç"), ("ct", "t"), ("pt", "t")]


def util(artigo: Artigo) -> bool:
    """Artigo com conteúdo de onde se tira uma pergunta: nem revogado, nem só de aprovação, nem
    de um anexo de republicação (o texto republicado é o dessa data, não o atual)."""
    texto = artigo.texto
    return (
        300 <= len(texto) <= 2500
        and "(Revogado" not in texto
        and "Promulgado em" not in texto
        and "republica" not in artigo.parte.lower()
        and not texto.startswith(("É aprovad", "São aprovad"))
    )


def sem_ortografia(texto: str) -> str:
    """Texto sem as diferenças do Acordo Ortográfico (actividade/atividade), para comparar redações."""
    texto = normalizar(texto).lower()
    for antes, depois in _ORTOGRAFIA:
        texto = texto.replace(antes, depois)
    return texto


def numeros(texto: str) -> set[str]:
    return set(re.findall(r"\d+(?:[.,]\d+)*", texto))


def registo(caminho: str, artigo: Artigo, **extra) -> dict:
    return {"caminho": caminho, "artigo": artigo.chave, "epigrafe": artigo.epigrafe, "texto": artigo.texto, **extra}


def escolher(caminho: str, rng: random.Random) -> Artigo | None:
    candidatos = [a for a in artigos(corpo((RAIZ / caminho).read_text(encoding="utf-8"))) if util(a)]
    return rng.choice(candidatos) if candidatos else None


def literais(db: sqlite3.Connection, rng: random.Random, n: int) -> list[dict]:
    linhas = db.execute(
        f"select id, title, path from documentos where version_kind = 'consolidated' and {NACIONAL} and {EM_VIGOR}"
    ).fetchall()
    rng.shuffle(linhas)
    resultado = []
    for doc_id, titulo, caminho in linhas:
        artigo = escolher(caminho, rng)
        if artigo:
            resultado.append(registo(caminho, artigo, documento=doc_id, titulo=titulo))
        if len(resultado) == n:
            break
    return resultado


def temporais(db: sqlite3.Connection, rng: random.Random, n: int) -> list[dict]:
    """Artigos cuja redação numa versão antiga difere da atual, de preferência nos números."""
    linhas = db.execute(
        f"select id, title, path from documentos where version_kind = 'consolidated' and version_count >= 3 and {NACIONAL} and {EM_VIGOR}"
    ).fetchall()
    rng.shuffle(linhas)
    resultado = []
    for doc_id, titulo, caminho in linhas:
        historico = RAIZ / caminho.replace(".md", ".versoes.json")
        if not historico.exists():
            continue
        versoes = [v for v in json.loads(historico.read_text(encoding="utf-8"))["versions"] if not v.get("future")]
        if len(versoes) < 3:
            continue
        indice = rng.randrange(0, len(versoes) - 1)
        inicio, fim = versoes[indice]["date"], versoes[indice + 1]["date"]
        antigos = {a.chave: a for a in artigos(texto_em(RAIZ / caminho, inicio))}
        atuais = {a.chave: a for a in artigos(corpo((RAIZ / caminho).read_text(encoding="utf-8")))}
        mudados = [
            (antigos[chave], atual) for chave, atual in atuais.items()
            if chave in antigos and util(antigos[chave]) and sem_ortografia(antigos[chave].texto) != sem_ortografia(atual.texto)
        ]
        if not mudados:
            continue
        com_numeros = [par for par in mudados if numeros(par[0].texto) != numeros(par[1].texto)]
        antigo, atual = rng.choice(com_numeros or mudados)
        resultado.append(registo(
            caminho, antigo, documento=doc_id, titulo=titulo, data=inicio, em_vigor_ate=fim, texto_atual=atual.texto,
        ))
        if len(resultado) == n:
            break
    return resultado


def revogadas(db: sqlite3.Connection, rng: random.Random, n: int) -> list[dict]:
    linhas = db.execute(
        f"""select d.id, d.title, d.path, r.target_id, r.date, a.title
            from documentos d
            join relacoes r on r.source_id = d.id and r.type = 'repealed_by' and r.target_id is not null
            join documentos a on a.id = r.target_id
            where d.legal_status in ('repealed', 'not_in_force') and d.publication_date >= '1990' and {NACIONAL.replace('jurisdiction', 'd.jurisdiction').replace('text_quality', 'd.text_quality')}"""
    ).fetchall()
    rng.shuffle(linhas)
    resultado, vistos = [], set()
    for doc_id, titulo, caminho, revogador, data, titulo_revogador in linhas:
        if doc_id in vistos:
            continue
        vistos.add(doc_id)
        artigo = escolher(caminho, rng)
        if artigo:
            resultado.append(registo(
                caminho, artigo, documento=doc_id, titulo=titulo,
                revogado_por=revogador, revogado_por_titulo=titulo_revogador, data_revogacao=data,
            ))
        if len(resultado) == n:
            break
    return resultado


def distratores(db: sqlite3.Connection, rng: random.Random, n: int) -> list[dict]:
    linhas = db.execute(f"select id, title, path from documentos where {NACIONAL} and {EM_VIGOR}").fetchall()
    resultado = []
    while len(resultado) < n:
        doc_id, titulo, caminho = rng.choice(linhas)
        artigo = escolher(caminho, rng)
        if artigo:
            resultado.append(registo(caminho, artigo, documento=doc_id, titulo=titulo))
    return resultado


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--saida", type=Path, required=True)
    parser.add_argument("--semente", type=int, default=20261027)
    parser.add_argument("--literais", type=int, default=45)
    parser.add_argument("--temporais", type=int, default=18)
    parser.add_argument("--revogadas", type=int, default=12)
    parser.add_argument("--distratores", type=int, default=10)
    args = parser.parse_args()

    db = sqlite3.connect(EXPORT)
    args.saida.mkdir(parents=True, exist_ok=True)
    tipos = {
        "literal": lambda rng: literais(db, rng, args.literais),
        "temporal": lambda rng: temporais(db, rng, args.temporais),
        "revogada": lambda rng: revogadas(db, rng, args.revogadas),
        "distrator": lambda rng: distratores(db, rng, args.distratores),
    }
    for nome, gerar in tipos.items():
        candidatos = gerar(random.Random(f"{args.semente}-{nome}"))
        with (args.saida / f"{nome}.jsonl").open("w", encoding="utf-8") as ficheiro:
            for candidato in candidatos:
                ficheiro.write(json.dumps(candidato, ensure_ascii=False) + "\n")
        print(f"{nome}: {len(candidatos)} candidato(s)")
    print(f"Amostra de {date.today().isoformat()} a partir de {EXPORT.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
