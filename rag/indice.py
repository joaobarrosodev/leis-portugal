"""Índice por artigo dos diplomas com texto (`text_quality = texto`).

Um pedaço por artigo, com o caminho completo (diploma › anexo › artigo e epígrafe), a
vigência do diploma, a versão (original ou consolidada) e o intervalo de datas em que
aquele texto esteve em vigor. Nos diplomas com histórico (`.versoes.json`) cada redação de
cada artigo é um pedaço, com `desde` e `ate`; nos outros, o texto vale desde a publicação.
Os diplomas sem artigos identificados entram em blocos de ~300 palavras (`chave` = `texto#N`).

Tudo fica num SQLite com FTS5 (BM25), fora do git:

    PYTHONPATH=src python -m rag.indice                # acervo completo (~1 h)
    PYTHONPATH=src python -m rag.indice --amostra 5000 # só os diplomas da avaliação e mais 5000
"""

from __future__ import annotations

import argparse
import random
import re
import sqlite3
import sys
import time
from collections.abc import Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from rag import texto as termos_mod
from rag.fontes import PASTA_INDICE, RAIZ, corpo, export_sqlite, ler_artigos, ler_historico, revogado, texto_da_versao


ESQUEMA = """
CREATE TABLE meta (chave TEXT PRIMARY KEY, valor TEXT);
CREATE TABLE documentos (
  id TEXT PRIMARY KEY, titulo TEXT, tipo TEXT, numero TEXT, data TEXT, sumario TEXT,
  legal_status TEXT, versao TEXT, data_consolidacao TEXT, caminho TEXT, com_historico INTEGER
);
CREATE TABLE relacoes (documento TEXT, tipo TEXT, alvo TEXT, alvo_titulo TEXT, data TEXT);
CREATE INDEX relacoes_documento ON relacoes (documento);
CREATE TABLE pedacos (
  id INTEGER PRIMARY KEY, documento TEXT, parte TEXT, numero TEXT, epigrafe TEXT, chave TEXT,
  rotulo TEXT, texto TEXT, notas TEXT, desde TEXT, ate TEXT, ordem INTEGER
);
CREATE INDEX pedacos_documento ON pedacos (documento, numero);
CREATE VIRTUAL TABLE pedacos_fts USING fts5(cabecalho, texto, content='', tokenize='unicode61 remove_diacritics 0');
"""

RELACOES = ("amended_by", "repealed_by")
MAX_CARACTERES = 30_000
PALAVRAS_POR_BLOCO = 300
_TEXTO_EM_VIGOR = re.compile(r"^- type: republished_by\n  target: (\S+)\n  label: '?Texto em vigor", re.M)
_LIGACAO = re.compile(r"<a [^>]*>(.*?)</a>")


@dataclass
class Documento:
    id: str
    titulo: str
    tipo: str
    numero: str
    data: str | None
    sumario: str
    legal_status: str
    versao: str
    data_consolidacao: str | None
    caminho: str


@dataclass
class Pedaco:
    parte: str
    numero: str
    epigrafe: str
    chave: str
    texto: str
    notas: str
    desde: str | None
    ate: str | None


def rotulo(doc: Documento, parte: str, numero: str, epigrafe: str) -> str:
    """O caminho completo do pedaço: diploma (tipo, número, data) › anexo › artigo e epígrafe."""
    partes = [f"{doc.titulo}, de {doc.data}" if doc.data else doc.titulo]
    if parte:
        partes.append(parte)
    if numero:
        partes.append(f"Artigo {numero}" + (f" — {epigrafe}" if epigrafe else ""))
    return " › ".join(partes)


def _blocos(texto: str) -> Iterator[str]:
    """Texto sem artigos identificados, em blocos de ~300 palavras que acabam num parágrafo."""
    atual: list[str] = []
    palavras = 0
    for paragrafo in re.split(r"\n\s*\n", texto):
        paragrafo = _LIGACAO.sub(r"\1", paragrafo).strip()
        if not paragrafo or paragrafo.startswith("# "):
            continue
        atual.append(paragrafo)
        palavras += len(paragrafo.split())
        if palavras >= PALAVRAS_POR_BLOCO:
            yield "\n\n".join(atual)
            atual, palavras = [], 0
    if atual:
        yield "\n\n".join(atual)


def _de_artigos(artigos, desde: str | None, ate: str | None) -> list[Pedaco]:
    return [Pedaco(a.parte, a.numero, a.epigrafe, a.chave, a.texto, "\n".join(a.notas), desde, ate) for a in artigos]


def _revogado(artigo) -> bool:
    return revogado(artigo.texto, "\n".join(artigo.notas))


def pedacos_do_documento(doc: Documento) -> tuple[list[Pedaco], list[str], bool]:
    """Os pedaços de um registo, os alvos de `republished_by` com o texto em vigor e se tem histórico."""
    caminho = RAIZ / doc.caminho
    markdown = caminho.read_text(encoding="utf-8")
    cabecalho_yaml = markdown[: markdown.find("\n---\n", 4)] if markdown.startswith("---\n") else ""
    em_vigor_em = _TEXTO_EM_VIGOR.findall(cabecalho_yaml)
    historico = ler_historico(caminho)
    if historico and historico.get("versions"):
        return _com_historico(historico), em_vigor_em, True
    texto = corpo(markdown)
    artigos = ler_artigos(texto)
    if artigos:
        return _de_artigos(artigos, doc.data, None), em_vigor_em, False
    return [Pedaco("", "", "", f"texto#{n}", bloco, "", doc.data, None) for n, bloco in enumerate(_blocos(texto), 1)], em_vigor_em, False


def _com_historico(historico: dict) -> list[Pedaco]:
    """Cada redação de cada artigo, com o intervalo [desde, ate) em que esteve em vigor.

    Uma revogação que só acrescenta a nota "Revogado pelo/a …" ao texto antigo também abre uma
    redação nova, com a nota: sem isso, o artigo ficava com o texto e as notas de antes, como em
    vigor."""
    abertos: dict[tuple[str, int], tuple[object, str]] = {}
    feitos: list[Pedaco] = []
    for versao in historico["versions"]:
        quando = versao["date"]
        atuais: dict[tuple[str, int], object] = {}
        vistos: dict[str, int] = {}
        for artigo in ler_artigos(texto_da_versao(historico, versao)):
            vistos[artigo.chave] = vistos.get(artigo.chave, 0) + 1
            atuais[(artigo.chave, vistos[artigo.chave])] = artigo
        for chave in list(abertos):
            anterior, desde = abertos[chave]
            novo = atuais.get(chave)
            if novo is None or (novo.texto, novo.epigrafe, _revogado(novo)) != (anterior.texto, anterior.epigrafe, _revogado(anterior)):
                feitos.extend(_de_artigos([anterior], desde, quando))
                del abertos[chave]
        for chave, artigo in atuais.items():
            if chave not in abertos:
                abertos[chave] = (artigo, quando)
    for artigo, desde in abertos.values():
        feitos.extend(_de_artigos([artigo], desde, None))
    return feitos


def documentos_do_export(export: Path) -> list[Documento]:
    with sqlite3.connect(f"file:{export}?mode=ro", uri=True) as con:
        linhas = con.execute(
            """SELECT id, title, document_type, official_number, coalesce(official_date, publication_date), coalesce(summary, ''),
                      coalesce(legal_status, 'unknown'), coalesce(version_kind, 'original'), consolidation_date, path
               FROM documentos WHERE text_quality = 'texto' ORDER BY path"""
        ).fetchall()
    return [Documento(*linha) for linha in linhas]


def relacoes_do_export(export: Path, ids: set[str]) -> Iterator[tuple[str, str, str, str, str | None]]:
    with sqlite3.connect(f"file:{export}?mode=ro", uri=True) as con:
        titulos = dict(con.execute("SELECT id, title FROM documentos"))
        marcadores = ",".join("?" * len(RELACOES))
        for origem, tipo, alvo, alvo_id, data, rotulo_ in con.execute(
            f"SELECT source_id, type, target, target_id, date, label FROM relacoes WHERE type IN ({marcadores})", RELACOES
        ):
            if origem in ids:
                alvo = alvo_id or alvo or ""
                yield origem, tipo, alvo, titulos.get(alvo) or rotulo_ or alvo, data


def construir(saida: Path, documentos: list[Documento], export: Path, *, fios: int = 8) -> None:
    saida.parent.mkdir(parents=True, exist_ok=True)
    temporario = saida.with_suffix(".tmp")
    temporario.unlink(missing_ok=True)
    con = sqlite3.connect(temporario)
    con.executescript("PRAGMA journal_mode = OFF; PRAGMA synchronous = OFF;" + ESQUEMA)
    ids = {d.id for d in documentos}
    con.executemany("INSERT INTO relacoes VALUES (?, ?, ?, ?, ?)", relacoes_do_export(export, ids))
    with sqlite3.connect(f"file:{export}?mode=ro", uri=True) as origem:
        titulos = dict(origem.execute("SELECT id, title FROM documentos"))

    def processar(doc: Documento):
        try:
            return doc, *pedacos_do_documento(doc)
        except FileNotFoundError:
            return doc, None, [], False

    inicio = time.time()
    proximo_id = 1
    contagem = {"documentos": 0, "pedacos": 0, "sem_ficheiro": 0, "com_historico": 0}
    with ThreadPoolExecutor(fios) as executor:
        for n, lote in enumerate(_lotes(documentos, 1000)):
            for doc, pedacos, em_vigor_em, com_historico in executor.map(processar, lote):
                if pedacos is None:
                    contagem["sem_ficheiro"] += 1
                    continue
                con.execute(
                    "INSERT OR REPLACE INTO documentos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (doc.id, doc.titulo, doc.tipo, doc.numero, doc.data, doc.sumario, doc.legal_status, doc.versao,
                     doc.data_consolidacao, doc.caminho, int(com_historico)),
                )
                con.executemany(
                    "INSERT INTO relacoes VALUES (?, 'texto_em_vigor_em', ?, ?, NULL)", [(doc.id, alvo, titulos.get(alvo, alvo)) for alvo in em_vigor_em]
                )
                linhas, fts = [], []
                cabecalho_doc = f"{doc.titulo} {doc.sumario[:300]}"
                for ordem, p in enumerate(pedacos):
                    texto = p.texto[:MAX_CARACTERES]
                    linhas.append((proximo_id, doc.id, p.parte, p.numero, p.epigrafe, p.chave, rotulo(doc, p.parte, p.numero, p.epigrafe),
                                   texto, p.notas, p.desde, p.ate, ordem))
                    cabecalho = f"{cabecalho_doc} {p.parte} {p.epigrafe}"
                    fts.append((proximo_id, " ".join(termos_mod.termos(cabecalho)), " ".join(termos_mod.termos(texto))))
                    proximo_id += 1
                con.executemany("INSERT INTO pedacos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", linhas)
                con.executemany("INSERT INTO pedacos_fts (rowid, cabecalho, texto) VALUES (?, ?, ?)", fts)
                contagem["documentos"] += 1
                contagem["pedacos"] += len(linhas)
                contagem["com_historico"] += int(com_historico)
            con.commit()
            feitos = min((n + 1) * 1000, len(documentos))
            decorrido = time.time() - inicio
            print(f"{feitos}/{len(documentos)} diplomas, {contagem['pedacos']} pedaços, {decorrido / 60:.1f} min", file=sys.stderr, flush=True)
    con.executemany(
        "INSERT INTO meta VALUES (?, ?)",
        [("metodo_termos", termos_mod.METODO), ("construido", date.today().isoformat()), ("export", str(export)),
         *((k, str(v)) for k, v in contagem.items())],
    )
    con.execute("INSERT INTO pedacos_fts (pedacos_fts) VALUES ('optimize')")
    con.commit()
    con.close()
    temporario.replace(saida)
    print(f"Índice em {saida}: {contagem}", file=sys.stderr)


def _lotes(itens: list, tamanho: int) -> Iterable[list]:
    for i in range(0, len(itens), tamanho):
        yield itens[i : i + tamanho]


def documentos_da_avaliacao() -> set[str]:
    import json

    ids: set[str] = set()
    ficheiros = [RAIZ / "avaliacao" / "perguntas.jsonl", RAIZ / "avaliacao" / "privado" / "perguntas-reais.jsonl"]
    principal = next((p / "avaliacao" / "privado" / "perguntas-reais.jsonl" for p in RAIZ.parents if (p / "avaliacao" / "privado").is_dir()), None)
    for ficheiro in [*ficheiros, principal]:
        if ficheiro and ficheiro.exists():
            for linha in ficheiro.read_text(encoding="utf-8").splitlines():
                pergunta = json.loads(linha)
                for chave in ("fonte", "distrator"):
                    if pergunta.get(chave):
                        ids.add(pergunta[chave]["documento"])
                if pergunta.get("revogado_por"):
                    ids.add(pergunta["revogado_por"]["documento"])
    return ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--saida", type=Path, default=PASTA_INDICE / "indice.sqlite")
    parser.add_argument("--amostra", type=int, help="Só os diplomas da avaliação e mais N ao acaso (para desenvolver).")
    parser.add_argument("--fios", type=int, default=8)
    args = parser.parse_args(argv)
    export = export_sqlite()
    documentos = documentos_do_export(export)
    if args.amostra is not None:
        avaliacao = documentos_da_avaliacao()
        # Os consolidados que têm o texto em vigor dos códigos republicados (IRS, IRC…) também entram.
        avaliacao |= {"pt:dre:66022085:por", "pt:dre:571007:por"}
        resto = [d for d in documentos if d.id not in avaliacao]
        documentos = [d for d in documentos if d.id in avaliacao] + random.Random(20261027).sample(resto, min(args.amostra, len(resto)))
    construir(args.saida, documentos, export, fios=args.fios)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
