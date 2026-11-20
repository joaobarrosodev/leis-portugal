"""Índice por artigo dos diplomas com texto (`text_quality = texto`).

Um pedaço por artigo, com o caminho completo (diploma › anexo › artigo e epígrafe), a
vigência do diploma, a versão (original ou consolidada) e o intervalo de datas em que
aquele texto esteve em vigor. Nos diplomas com histórico (`.versoes.json`) cada redação de
cada artigo é um pedaço, com `desde` e `ate`; nos outros, o texto vale desde a publicação.
Os diplomas sem artigos identificados entram em blocos de ~300 palavras (`chave` = `texto#N`).

Tudo fica num SQLite com FTS5 (BM25), fora do git:

    PYTHONPATH=src python -m rag.indice                # acervo completo (~1 h)
    PYTHONPATH=src python -m rag.indice --amostra 5000 # só os diplomas da avaliação e mais 5000
    PYTHONPATH=src python -m rag.indice --sem-serie-ii # sem os atos da 2.ª Série recolhidos em 12/11/2026
    PYTHONPATH=src python -m rag.indice --com-serie-ii # com esses atos também no BM25 em todo o acervo
    PYTHONPATH=src python -m rag.indice --com-perguntas # com as perguntas de leigo de rag/perguntas_artigo/ (piloto)

Os regulamentos, deliberações, acordos coletivos de trabalho, editais e declarações que o
`collect dre --missing --all` trouxe a partir de 12/11/2026 (~90 mil, quase todos da 2.ª
Série; ver `fora_por_omissao`) entram por omissão só pela referência: na tabela `so_referencia`,
que a pesquisa tira do BM25 em todo o acervo. Só aparecem quando a pergunta cita o ato. Na
pesquisa geral baralhavam as perguntas reais (medição em `rag/README.md`, «Tipos novos»). Os
destes tipos que já lá estavam (os citados ou alterados por diplomas do acervo) entram como os outros.
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
from rag.copias import impressao
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


def textos_fts(titulo: str, sumario: str, parte: str, epigrafe: str, texto: str, perguntas: str = "") -> tuple[str, str]:
    """Os termos de um pedaço na tabela de pesquisa (cabeçalho e texto).

    A tabela é sem conteúdo (`content=''`): para apagar um pedaço é preciso dar-lhe os mesmos termos
    com que entrou. Por isso a construção (`construir`) e os deltas (`rag.dados`) usam esta função.
    As `perguntas` de leigo do artigo (`rag.perguntas_por_artigo`) juntam-se aos termos do texto."""
    cabecalho = f"{titulo} {sumario[:300]} {parte} {epigrafe}"
    corpo_ = termos_mod.termos(texto) + (termos_mod.termos(perguntas) if perguntas else [])
    return " ".join(termos_mod.termos(cabecalho)), " ".join(corpo_)


ESQUEMA_PERGUNTAS = "CREATE TABLE IF NOT EXISTS perguntas_artigo (documento TEXT, chave TEXT, perguntas TEXT, PRIMARY KEY (documento, chave))"


def tem_perguntas(con: sqlite3.Connection) -> bool:
    return con.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'perguntas_artigo'").fetchone() is not None


def perguntas_do_indice(con: sqlite3.Connection, documento: str | None = None) -> dict[tuple[str, str], str]:
    """(documento, chave) → perguntas (uma por linha), de um diploma ou de todos; vazio se não há a tabela."""
    if not tem_perguntas(con):
        return {}
    sql, args = "SELECT documento, chave, perguntas FROM perguntas_artigo", ()
    if documento is not None:
        sql, args = sql + " WHERE documento = ?", (documento,)
    return {(d, c): p for d, c, p in con.execute(sql, args)}


def perguntas_do_pedaco(perguntas: dict[tuple[str, str], str], documento: str, chave: str, ate: str | None) -> str:
    """As perguntas que entram nos termos de um pedaço: só na redação em vigor (`ate` vazio), de onde foram escritas."""
    return perguntas.get((documento, chave), "") if ate is None else ""


def juntar_perguntas(con: sqlite3.Connection, perguntas: dict[tuple[str, str], list[str]]) -> dict:
    """Junta as perguntas de leigo aos termos dos artigos em vigor (e grava-as em `perguntas_artigo`).

    Substitui as perguntas que o artigo já tivesse. A construção (`construir`) e a experiência
    (`rag.perguntas_por_artigo juntar`) passam por aqui; os deltas (`rag.dados`) usam as mesmas regras."""
    con.execute(ESQUEMA_PERGUNTAS)
    antigas = perguntas_do_indice(con)
    encontradas, em_falta, pedacos_ = 0, [], 0
    for (documento, chave), lista in sorted(perguntas.items()):
        texto_novo = "\n".join(lista)
        linhas = con.execute(
            "SELECT p.id, p.parte, p.epigrafe, p.texto, d.titulo, d.sumario FROM pedacos p JOIN documentos d ON d.id = p.documento "
            "WHERE p.documento = ? AND p.chave = ? AND p.ate IS NULL",
            (documento, chave),
        ).fetchall()
        if not linhas:
            em_falta.append((documento, chave))
            continue
        encontradas += 1
        velho = antigas.get((documento, chave), "")
        for id_, parte, epigrafe, texto, titulo, sumario in linhas:
            args = (titulo, sumario or "", parte or "", epigrafe or "", texto or "")
            con.execute("INSERT INTO pedacos_fts (pedacos_fts, rowid, cabecalho, texto) VALUES ('delete', ?, ?, ?)", (id_, *textos_fts(*args, velho)))
            con.execute("INSERT INTO pedacos_fts (rowid, cabecalho, texto) VALUES (?, ?, ?)", (id_, *textos_fts(*args, texto_novo)))
            pedacos_ += 1
        con.execute("INSERT OR REPLACE INTO perguntas_artigo VALUES (?, ?, ?)", (documento, chave, texto_novo))
    return {"artigos": encontradas, "pedacos": pedacos_, "em_falta": em_falta}


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


def aplicar_redacoes(pedacos: list[Pedaco], marcas) -> int:
    """Fecha (`ate`) os pedaços abertos das cópias que são redação anterior (`rag.copias.Marca`); devolve quantos.

    - Os artigos da cópia, pela chave e pelo texto: na mesma parte pode estar também o articulado do próprio
      diploma, com as mesmas chaves, e esse fica aberto. Um pedaço cujo texto não é o que a regra leu fica como está.
    - Nos registos em blocos de texto, os blocos a seguir àquele onde o texto começa. Esse bloco fica como está,
      a não ser que comece pelo texto: pode ter o fim do articulado do próprio diploma.

    Um pedaço que só começou depois da data fica com o intervalo vazio: não responde a nenhuma data."""
    fechados = 0

    def fechar(pedaco: Pedaco, ate: str) -> None:
        nonlocal fechados
        if pedaco.ate is None:
            pedaco.ate = ate if (pedaco.desde or "") < ate else pedaco.desde
            fechados += 1

    for marca in marcas:
        da_parte = [p for p in pedacos if p.parte == marca.parte]
        if marca.a_partir_de:
            primeira, _, segunda = marca.a_partir_de.partition("\n")
            textos = [" ".join(p.texto.split()) for p in da_parte]
            inicio = next((k for k, t in enumerate(textos) if primeira in t and (not segunda or segunda in t or segunda in "".join(textos[k + 1 : k + 2]))), None)
            if inicio is None:
                continue
            for pedaco in da_parte[inicio if textos[inicio].startswith(primeira) else inicio + 1 :]:
                fechar(pedaco, marca.ate)
        else:
            for pedaco in da_parte:
                if pedaco.ate is None and (pedaco.chave, impressao(pedaco.texto)) in marca.artigos:
                    fechar(pedaco, marca.ate)
    return fechados


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


# Tipos da 2.ª Série recolhidos em massa a partir de 12/11/2026 (`collect dre --missing --all
# --types ...`). Na pesquisa geral baralham as perguntas reais, por isso os registos destes tipos
# recolhidos desde essa data entram só pela referência (`so_referencia`; `--com-serie-ii` ou
# `--sem-serie-ii` para outra escolha). Os recolhidos antes (os que um diploma cita ou altera) entram.
TIPOS_SERIE_II = ("regulamento", "deliberacao", "acordo-coletivo-trabalho", "edital", "declaracao")
SERIE_II_DESDE = "2026-11-12"


def fora_por_omissao(tipo: str, recolhido_em: str | None) -> bool:
    """Registo dos tipos da 2.ª Série recolhido na recolha em massa (por omissão, só pela referência)."""
    return tipo in TIPOS_SERIE_II and (recolhido_em or "") >= SERIE_II_DESDE


def documentos_do_export(export: Path, *, com_serie_ii: bool = False, com_traducoes: bool = True) -> list[Documento]:
    with sqlite3.connect(f"file:{export}?mode=ro", uri=True) as con:
        linhas = con.execute(
            """SELECT id, title, document_type, official_number, coalesce(official_date, publication_date), coalesce(summary, ''),
                      coalesce(legal_status, 'unknown'), coalesce(version_kind, 'original'), consolidation_date, path, retrieved_at
               FROM documentos WHERE text_quality = 'texto' ORDER BY path"""
        ).fetchall()
    return [
        Documento(*linha[:-1]) for linha in linhas
        if (com_serie_ii or not fora_por_omissao(linha[2], linha[-1])) and (com_traducoes or linha[7] != "translation")
    ]


def serie_ii_do_export(export: Path) -> set[str]:
    """Os ids de que `fora_por_omissao` fala: por omissão, entram só pela referência."""
    with sqlite3.connect(f"file:{export}?mode=ro", uri=True) as con:
        linhas = con.execute("SELECT id, document_type, retrieved_at FROM documentos WHERE text_quality = 'texto'").fetchall()
    return {i for i, tipo, recolhido_em in linhas if fora_por_omissao(tipo, recolhido_em)}


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


def construir(
    saida: Path, documentos: list[Documento], export: Path, *, fios: int = 8, so_referencia: set[str] | None = None,
    perguntas: dict[tuple[str, str], list[str]] | None = None, redacoes: dict[str, list] | None = None,
) -> None:
    """`redacoes`: registo → marcas das cópias que são redação anterior (`rag.copias`)."""
    redacoes = redacoes or {}
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
    contagem = {"documentos": 0, "pedacos": 0, "sem_ficheiro": 0, "com_historico": 0, "redacoes_anteriores": 0, "registos_com_redacoes_anteriores": 0}
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
                marcas = redacoes.get(doc.id, ())
                if marcas:
                    fechados = aplicar_redacoes(pedacos, marcas)
                    contagem["redacoes_anteriores"] += fechados
                    contagem["registos_com_redacoes_anteriores"] += bool(fechados)
                    # A pesquisa troca um artigo deste registo pelo do alvo com o mesmo número (`_redirecionar`). Com o
                    # texto antigo fechado, o que fica aberto com número é o articulado do próprio diploma, que não é
                    # para trocar: aí a ligação fica com outro nome. Sem artigos abertos, fica `texto_em_vigor_em`.
                    com_artigos_abertos = any(p.ate is None and p.numero for p in pedacos)
                    alvos = list(dict.fromkeys([m.alvo for m in marcas] + em_vigor_em))
                    tipo_ligacao = "redacao_atual_em" if com_artigos_abertos else "texto_em_vigor_em"
                    con.executemany("INSERT INTO relacoes VALUES (?, ?, ?, ?, NULL)", [(doc.id, tipo_ligacao, alvo, titulos.get(alvo, alvo)) for alvo in alvos if alvo != doc.id])
                else:
                    con.executemany(
                        "INSERT INTO relacoes VALUES (?, 'texto_em_vigor_em', ?, ?, NULL)", [(doc.id, alvo, titulos.get(alvo, alvo)) for alvo in em_vigor_em]
                    )
                linhas, fts = [], []
                for ordem, p in enumerate(pedacos):
                    texto = p.texto[:MAX_CARACTERES]
                    linhas.append((proximo_id, doc.id, p.parte, p.numero, p.epigrafe, p.chave, rotulo(doc, p.parte, p.numero, p.epigrafe),
                                   texto, p.notas, p.desde, p.ate, ordem))
                    fts.append((proximo_id, *textos_fts(doc.titulo, doc.sumario, p.parte, p.epigrafe, texto)))
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
    if so_referencia:
        # Encontram-se só quando a pergunta os cita: `Pesquisa.bm25` tira-os da pesquisa em todo o acervo.
        con.execute("CREATE TABLE so_referencia (id TEXT PRIMARY KEY)")
        con.executemany("INSERT INTO so_referencia VALUES (?)", [(i,) for i in sorted(so_referencia & ids)])
    if perguntas:
        juntadas = juntar_perguntas(con, perguntas)
        print(f"Perguntas por artigo: {juntadas['artigos']} artigos, {juntadas['pedacos']} pedaços, {len(juntadas['em_falta'])} em falta", file=sys.stderr)
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
    serie_ii = parser.add_mutually_exclusive_group()
    serie_ii.add_argument(
        "--com-serie-ii", action="store_true",
        help="Os regulamentos, deliberações, ACT, editais e declarações da recolha em massa de 12/11/2026 também no BM25 em todo o acervo.",
    )
    serie_ii.add_argument(
        "--sem-serie-ii", action="store_true",
        help="Deixar de fora esses atos (por omissão entram só pela referência).",
    )
    parser.add_argument(
        "--sem-traducoes", action="store_true",
        help="Deixar de fora os atos da UE em tradução não oficial (version.kind translation), para medir o efeito deles.",
    )
    parser.add_argument(
        "--sem-redacoes-anteriores", action="store_true",
        help="Não marcar as cópias antigas de um texto como redação anterior (`rag.copias`), para medir o efeito.",
    )
    parser.add_argument(
        "--com-perguntas", action="store_true",
        help="Juntar aos artigos as perguntas de leigo de rag/perguntas_artigo/ (piloto; publicar exige --com-perguntas).",
    )
    args = parser.parse_args(argv)
    export = export_sqlite()
    documentos = documentos_do_export(export, com_serie_ii=not args.sem_serie_ii, com_traducoes=not args.sem_traducoes)
    so_referencia = None if args.com_serie_ii or args.sem_serie_ii else serie_ii_do_export(export)
    if args.amostra is not None:
        avaliacao = documentos_da_avaliacao()
        # Os consolidados que têm o texto em vigor dos códigos republicados (IRS, IRC…) também entram.
        avaliacao |= {"pt:dre:66022085:por", "pt:dre:571007:por"}
        resto = [d for d in documentos if d.id not in avaliacao]
        documentos = [d for d in documentos if d.id in avaliacao] + random.Random(20261027).sample(resto, min(args.amostra, len(resto)))
    perguntas = None
    if args.com_perguntas:
        from rag.perguntas_por_artigo import ler

        perguntas = ler()
    redacoes = None
    if not args.sem_redacoes_anteriores:
        from rag import copias

        marcas, fora, _ = copias.calcular(export, RAIZ)
        redacoes = copias.marcas_por_documento(marcas)
        print(f"Redações anteriores: {len(marcas)} cópias em {len(redacoes)} registos; {len(fora)} de fora (python -m rag.copias lista-as)", file=sys.stderr, flush=True)
    construir(args.saida, documentos, export, fios=args.fios, so_referencia=so_referencia, perguntas=perguntas, redacoes=redacoes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
