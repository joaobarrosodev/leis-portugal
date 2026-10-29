"""Candidatos para o conjunto de avaliação (sessão A): artigos reais de onde se tiram perguntas.

Lê o índice exportado (`leis-portugal export` → `exports/leis-portugal.sqlite`) e escreve um
ficheiro JSONL por tipo em `--saida`:

- `literal.jsonl`: artigos de diplomas em vigor e consolidados (texto atual garantido);
- `temporal.jsonl`: artigos cuja redação mudou, com o texto numa data passada e o atual;
- `revogada.jsonl`: artigos de diplomas revogados, com o ato que os revogou;
- `distrator.jsonl`: artigos ao acaso, dados à verificação nas perguntas sem resposta;
- `alterado.jsonl`: diplomas em vigor com texto original e alterações registadas pelo DRE sem
  consolidação, com os artigos que os diplomas alteradores dizem alterar (e as passagens do
  alterador que os citam) e artigos que nenhum alterador menciona;
- `composta.jsonl`: artigos de diplomas consolidados que remetem para outro artigo do mesmo
  diploma (regra e exceção, definições, normas transitórias), com os dois textos.

A amostra é reprodutível (`--semente`). Uso: `python avaliacao/amostra.py --saida <pasta>`;
`--tipos alterado,composta` limita aos tipos pedidos.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

from comum import EXPORT, RAIZ, Artigo, artigos, corpo, menciona_artigo, normalizar, texto_em


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


_ALTERACAO = (
    "lower(r.label) like 'alterad%' and r.label like '%presente%' "
    "and lower(r.label) not like '%na reda%' and lower(r.label) not like '%republica%'"
)
_NUMEROS_ART = re.compile(r"\barts?\.?\s*((?:\d+\.?\s*º(?:-[A-Z])?(?:\s*,\s*|\s+e\s+|\s+ao\s+)?)+)", re.I)
_UM_NUMERO = re.compile(r"\d+\.?\s*º(?:-[A-Z])?")


def _versao_no_disco(caminho: str) -> str:
    """O `version.kind` do registo em disco: o export pode ser anterior a uma consolidação nossa."""
    cabecalho = (RAIZ / caminho).read_text(encoding="utf-8")[:6000]
    encontrado = re.search(r"^version:\n  kind: (\w+)", cabecalho, re.M)
    return encontrado.group(1) if encontrado else ""


def _numeros_citados(label: str) -> list[str]:
    """Os números de artigo ("7.º", "27.º-A") que a etiqueta da relação diz alterados."""
    numeros = []
    for grupo in _NUMEROS_ART.findall(label):
        for numero in _UM_NUMERO.findall(grupo):
            numeros.append(re.sub(r"\s+", "", numero.replace(".º", "º").replace("º", ".º")))
    return list(dict.fromkeys(numeros))


def alterados(db: sqlite3.Connection, rng: random.Random, n: int) -> list[dict]:
    """Diplomas em vigor com texto original cujo DRE regista alterações sem consolidar."""
    linhas = db.execute(
        f"""select d.id, d.title, d.path, a.id, a.title, a.path, a.text_quality, r.date, r.label
            from documentos d
            join relacoes r on r.source_id = d.id and r.type = 'amended_by'
            join documentos a on a.id = r.target_id
            where d.version_kind = 'original' and d.series = 'I' and d.article_count >= 4
              and d.document_type not in ('resolucao-conselho-ministros', 'resolucao-assembleia-republica', 'declaracao', 'aviso')
              and {NACIONAL.replace('jurisdiction', 'd.jurisdiction').replace('text_quality', 'd.text_quality')}
              and {EM_VIGOR.replace('legal_status', 'd.legal_status').replace('id not in', 'd.id not in')}
            order by d.id, r.date"""
    ).fetchall()
    por_diploma: dict[str, list] = {}
    for linha in linhas:
        por_diploma.setdefault(linha[0], []).append(linha)
    ids = [doc_id for doc_id, rels in por_diploma.items() if any(_limpa(r[8]) for r in rels)]
    rng.shuffle(ids)
    resultado = []
    for doc_id in ids:
        rels = por_diploma[doc_id]
        titulo, caminho = rels[0][1], rels[0][2]
        if _versao_no_disco(caminho) != "original" or any(r[6] != "texto" for r in rels):
            continue
        originais = artigos(corpo((RAIZ / caminho).read_text(encoding="utf-8")))
        alteradores, corpos = [], {}
        for _, _, _, alt_id, alt_titulo, alt_caminho, _, data, label in rels:
            alteradores.append({"documento": alt_id, "titulo": alt_titulo, "caminho": alt_caminho, "data": data, "label": label})
            corpos.setdefault(alt_id, corpo((RAIZ / alt_caminho).read_text(encoding="utf-8")))
        mudados = []
        for alt in alteradores:
            if not _limpa(alt["label"]):
                continue
            for numero in _numeros_citados(alt["label"]):
                original = next((a for a in originais if a.numero == numero and "(Revogado" not in a.texto), None)
                if original is None:
                    continue
                referencia = titulo.split("n.º")[-1].strip()
                passagens = sorted(
                    (
                        {"artigo": p.chave, "epigrafe": p.epigrafe, "texto": p.texto, "cita_o_diploma": referencia in p.texto or referencia in p.epigrafe}
                        for p in artigos(corpos[alt["documento"]]) if menciona_artigo(p.texto, numero)
                    ),
                    key=lambda p: not p["cita_o_diploma"],
                )
                mudados.append({
                    "artigo": original.chave, "epigrafe": original.epigrafe, "texto": original.texto,
                    "alterador": alt["documento"], "passagens": passagens,
                })
        republicado = any(re.search(r"\b[Rr]epublica(?:ção|d[oa]s?|-se|r\b)", c) for c in corpos.values())
        intactos = [
            registo_artigo(a) for a in originais
            if util(a) and not republicado and not any(menciona_artigo(c, a.numero) for c in corpos.values())
        ]
        if not mudados and not intactos:
            continue
        rng.shuffle(intactos)
        resultado.append({
            "documento": doc_id, "titulo": titulo, "caminho": caminho, "alteradores": alteradores,
            "republicado": republicado, "mudados": mudados, "intactos": intactos[:3],
        })
        if len(resultado) == n:
            break
    return resultado


def _limpa(label: str) -> bool:
    """Etiqueta que diz que o alterador mudou artigos deste diploma (e não de um código que ele alterou)."""
    baixo = (label or "").lower()
    return baixo.startswith("alterad") and "presente" in baixo and "na reda" not in baixo and "com a reda" not in baixo and "republica" not in baixo


def registo_artigo(artigo: Artigo) -> dict:
    return {"artigo": artigo.chave, "epigrafe": artigo.epigrafe, "texto": artigo.texto}


_REMISSAO = re.compile(r"\bartigos?\s+(\d+\.º(?:-[A-Z])?)(?:\s*(?:,|e|a|ou)\s*(\d+\.º(?:-[A-Z])?))?", re.I)
_RELATIVA = re.compile(r"\bartigo (anterior|seguinte)\b", re.I)


_EPIGRAFE_FORMAL = re.compile(r"altera|revogat|aditamento|entrada em vigor|republica|produção de efeitos", re.I)


def substantivo(artigo: Artigo) -> bool:
    """Artigo com regra própria: nem de alteração de outro diploma, nem revogatório, nem de vigência."""
    return util(artigo) and not _EPIGRAFE_FORMAL.search(artigo.epigrafe) and "passa a ter a seguinte reda" not in artigo.texto


def pares_remissao(todos: list[Artigo]) -> list[tuple[Artigo, list[Artigo]]]:
    """Os artigos que remetem para outro artigo do mesmo diploma (e da mesma parte), com os remetidos."""
    por_chave = {a.chave: a for a in todos}
    pares = []
    for indice, a in enumerate(todos):
        if not substantivo(a):
            continue
        alvos = []
        for grupo in _REMISSAO.findall(a.texto):
            alvos.extend(g for g in grupo if g)
        for relativo in _RELATIVA.findall(a.texto):
            vizinho = indice - 1 if relativo.lower() == "anterior" else indice + 1
            if 0 <= vizinho < len(todos) and todos[vizinho].parte == a.parte:
                alvos.append(todos[vizinho].numero)
        alvos = [por_chave.get(f"{a.parte}::{x}" if a.parte else x) for x in dict.fromkeys(alvos)]
        alvos = [x for x in alvos if x is not None and x.chave != a.chave and substantivo(x)]
        if alvos:
            pares.append((a, alvos[:2]))
    return pares


def compostos_de(db: sqlite3.Connection, rng: random.Random, titulos: list[str], por_diploma: int) -> list[dict]:
    """Pares de artigos com remissão em diplomas escolhidos pelo título (códigos), `por_diploma` de cada."""
    resultado = []
    for titulo in titulos:
        linha = db.execute(
            "select id, title, path from documentos where title = ? and version_kind = 'consolidated' and jurisdiction = 'portugal'", (titulo,)
        ).fetchone()
        if linha is None:
            print(f"composta: {titulo} não está consolidado no export", file=sys.stderr)
            continue
        doc_id, titulo, caminho = linha
        pares = pares_remissao(artigos(corpo((RAIZ / caminho).read_text(encoding="utf-8"))))
        rng.shuffle(pares)
        for a, alvos in pares[:por_diploma]:
            resultado.append({
                "documento": doc_id, "titulo": titulo, "caminho": caminho,
                "artigo": registo_artigo(a), "referidos": [registo_artigo(x) for x in alvos],
            })
    return resultado


def compostos(db: sqlite3.Connection, rng: random.Random, n: int) -> list[dict]:
    """Artigos de diplomas consolidados que remetem para outro artigo do mesmo diploma, com os dois textos.
    Metade vem de diplomas grandes (códigos, 150 ou mais artigos), metade de qualquer tamanho."""
    linhas = db.execute(
        f"select id, title, path, article_count from documentos where version_kind = 'consolidated' and {NACIONAL} and {EM_VIGOR}"
    ).fetchall()
    grandes = [l for l in linhas if (l[3] or 0) >= 150]
    rng.shuffle(linhas)
    rng.shuffle(grandes)
    resultado = []
    for lista, quota in ((grandes, n // 2), (linhas, n)):
        for doc_id, titulo, caminho, _ in lista:
            if len(resultado) >= quota:
                break
            if not (RAIZ / caminho.replace(".md", ".versoes.json")).exists():
                continue
            pares = pares_remissao(artigos(corpo((RAIZ / caminho).read_text(encoding="utf-8"))))
            if not pares:
                continue
            a, alvos = rng.choice(pares)
            resultado.append({
                "documento": doc_id, "titulo": titulo, "caminho": caminho,
                "artigo": registo_artigo(a), "referidos": [registo_artigo(x) for x in alvos],
            })
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
    parser.add_argument("--alterados", type=int, default=60)
    parser.add_argument("--compostos", type=int, default=60)
    parser.add_argument("--tipos", help="tipos a gerar, separados por vírgulas (por omissão, todos)")
    parser.add_argument("--documentos", help="títulos de diplomas consolidados para `composta`, separados por ponto e vírgula")
    parser.add_argument("--por-diploma", type=int, default=3)
    args = parser.parse_args()

    db = sqlite3.connect(EXPORT)
    args.saida.mkdir(parents=True, exist_ok=True)
    tipos = {
        "literal": lambda rng: literais(db, rng, args.literais),
        "temporal": lambda rng: temporais(db, rng, args.temporais),
        "revogada": lambda rng: revogadas(db, rng, args.revogadas),
        "distrator": lambda rng: distratores(db, rng, args.distratores),
        "alterado": lambda rng: alterados(db, rng, args.alterados),
        "composta": lambda rng: (
            compostos_de(db, rng, args.documentos.split(";"), args.por_diploma) if args.documentos else compostos(db, rng, args.compostos)
        ),
    }
    if args.tipos:
        tipos = {nome: gerar for nome, gerar in tipos.items() if nome in args.tipos.split(",")}
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
