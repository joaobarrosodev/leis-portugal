"""Aplicação por regra das retificações fora da cadeia (`corrected_by`) aos consolidados.

Parte da auditoria (`consolidacao/auditoria.py`, `auditoria/retificacoes.jsonl`): só as classes
`por_regra` e `por_regra_aprox`, em que cada «onde se lê» aparece uma única vez no texto em vigor
(letra a letra ou, no aproximado, sem pontuação nem maiúsculas). Os pares voltam a ler-se da
retificação e a procurar-se no texto de hoje; as que já estão nos `acts` não se voltam a aplicar,
por isso correr outra vez não muda nada.

Como na regra `retificar` do `aplicar.py`:

- a troca faz-se no parágrafo (uma linha do Markdown) onde está o «onde se lê»; o parágrafo
  retificado perde as ligações quando o trecho as atravessa;
- o bloco (o artigo, ou o troço entre dois títulos) leva a nota
  «> Retificado pelo/a [Declaração …](…), publicado em AAAA-MM-DD.»

Uma retificação só se aplica se todos os seus pares se aplicarem:

- o par tem de estar dentro de um parágrafo (não atravessar dois);
- não pode estar no título `# …`, que vem do front matter (conta como metadados), e num título
  de artigo ou de secção pode mudar a epígrafe mas não o nível nem o número;
- quando o localizador nomeia um artigo («No n.º 2 do artigo 52.º»), o parágrafo tem de estar
  nesse artigo;
- no aproximado, a troca vai das palavras do primeiro às do último, e a pontuação das pontas
  fica a do texto.

Os pares `ja` (o «deve ler-se» já está no texto) e `metadados` não mexem no texto.

O histórico continua com duas versões. A retificação entra nos `acts` da versão consolidada, que
mantém a data: pela Lei 74/98, art. 5.º, n.º 4, a retificação reporta os efeitos à entrada em
vigor do texto retificado. A versão original fica como foi publicada, porque é com ela que o
`acervo.py` confirma o original verificado às cegas.

O que se aplicou fica em `auditoria/retificacoes-aplicadas.jsonl` (o parágrafo antes e depois),
para a verificação, e o `acervo.py` não volta a escrever por cima destes registos.

Uso: `python consolidacao/retificacoes.py [--dry-run]`.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA))

from acervo import blocos, historico  # noqa: E402
from auditoria import _METADADOS, chave, pares  # noqa: E402
from texto import RAIZ, corpo, front_matter, normalizar, sem_ligacoes  # noqa: E402

from leis_portugal.domain.history import render_version, summarize  # noqa: E402
from leis_portugal.infrastructure.repository import Acervo  # noqa: E402


AUDITORIA = PASTA / "auditoria" / "retificacoes.jsonl"
APLICADAS = PASTA / "auditoria" / "retificacoes-aplicadas.jsonl"
CLASSES = ("por_regra", "por_regra_aprox")
_TITULO = re.compile(r"^#{1,6} ")
_ARTIGO_TITULO = re.compile(r"^#{6} Artigo (\S+)")
_INICIO_TITULO = re.compile(r"^(?:#{1,6} (?:Artigo \S+(?: — )?)?)?")
_ARTIGO_LOCALIZADOR = re.compile(r"\bartigo\s+(\d+(?:\.º|º|°)?(?:-[A-Z])?)", re.I)


class Recusa(Exception):
    pass


class SoMetadados(Exception):
    """O par é do título do registo, que vem do front matter: não se troca no corpo."""


def ids_aplicados() -> set[str]:
    """Os registos com retificações aplicadas por este script (para o `acervo.py` não os reescrever)."""
    if not APLICADAS.exists():
        return set()
    return {json.loads(l)["id"] for l in APLICADAS.read_text(encoding="utf-8").splitlines() if l.strip()}


_ANEXO_LOCALIZADOR = re.compile(r"\b(?:anexo|mapa|quadro|tabela|lista)\b", re.I)
_ANEXO_TITULO = re.compile(r"^## (?:Anexo|ANEXO)\b")


def _em_anexo(linhas: list[str], i: int) -> bool:
    """A linha está depois de um título `## Anexo …` (e de nenhum outro título de nível 2)."""
    for j in range(i, -1, -1):
        if linhas[j].startswith("## "):
            return bool(_ANEXO_TITULO.match(linhas[j]))
    return False


def _numero(artigo: str) -> str:
    return re.sub(r"[.º°]", "", artigo).upper()


# O articulado acaba na fórmula final (promulgação, assinatura) ou no primeiro anexo, mapa ou
# quadro; o que vem depois não é de nenhum artigo, mesmo sem título Markdown.
_FIM_DO_ARTICULADO = re.compile(
    r"^(?:Visto e aprovado em Conselho de Ministros|Promulgad[oa] em|Publique-se\.|O Presidente da República,|"
    r"Referendad[oa] em|Assinad[oa] em|Secretaria-Geral d)"
    r"|^(?:Anexo|ANEXO|Mapa|MAPA|Quadro|QUADRO|Modelos?)(?: (?:a que|[IVXLC]+\b|n\.º)|$)"
)


def _artigo_de(linhas: list[str], i: int) -> str | None:
    for j in range(i, -1, -1):
        if _FIM_DO_ARTICULADO.match(linhas[j].strip()):
            return None
        if _TITULO.match(linhas[j]):
            m = _ARTIGO_TITULO.match(linhas[j])
            return _numero(m.group(1)) if m else None
    return None


def _padrao_aprox(trecho: str) -> re.Pattern[str]:
    """Uma palavra por grupo, para a troca no aproximado mexer só nas palavras que mudam."""
    palavras = chave(trecho).split()
    return re.compile(r"(?<!\w)" + r"\W*".join(f"({re.escape(p)})" for p in palavras) + r"(?!\w)", re.I)


def _separador(texto: str) -> str:
    return re.sub(r"[\s«»\"'‘’“”]", "", texto)


def troca_aprox(texto: str, m: re.Match[str], antes: str, depois: str) -> str:
    """Aplica ao trecho `m` de `texto` só as diferenças de palavras entre `antes` e `depois`.

    Numa troca com o mesmo número de palavras, mudam só as palavras e a pontuação e as maiúsculas
    do resto ficam as do texto («Anexo XIII» não passa a «anexo XIII»). Quando há palavras a mais
    ou a menos, o troço leva também a pontuação da retificação («em vigor» → «em vigor, excepto …»).
    """
    a = [w.casefold() for w in re.findall(r"\w+", antes)]
    palavras = list(re.finditer(r"\w+", depois))
    b = [w.group(0).casefold() for w in palavras]
    if a != chave(antes).split():
        raise Recusa("palavras do «onde se lê» que não se mapeiam")
    n, k = len(a), len(b)

    def no_texto(i1: int, i2: int) -> tuple[int, int]:  # palavras i1..i2-1, com o separador antes
        if i1 > 0:
            return m.end(i1), m.end(i2) if i2 > 0 else m.end(i1)
        return m.start(1), m.start(i2 + 1) if i2 < n else m.end(n)

    def na_retificacao(j1: int, j2: int) -> str:
        if j1 > 0:
            return depois[palavras[j1 - 1].end() : palavras[j2 - 1].end() if j2 > 0 else palavras[j1 - 1].end()]
        return depois[palavras[0].start() : palavras[j2].start() if j2 < k else palavras[-1].end()] if k else ""

    base = m.start()
    trocas = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            # O «deve ler-se» é o texto oficial: as maiúsculas dele ganham («cofre» → «Cofre»).
            trocas += [(m.start(i + 1), m.end(i + 1), palavras[j].group(0)) for i, j in zip(range(i1, i2), range(j1, j2), strict=True)
                       if m.group(i + 1) != palavras[j].group(0)]
            continue
        if op == "replace" and i2 - i1 == j2 - j1:
            for i, j in zip(range(i1, i2), range(j1, j2), strict=True):
                # O separador antes da palavra muda quando difere em mais do que aspas e espaços
                # («Decreto-Lei» → «Decreto Regulamentar»).
                if i > 0 and j > 0 and _separador(texto[m.end(i) - base : m.start(i + 1) - base]) != _separador(depois[palavras[j - 1].end() : palavras[j].start()]):
                    trocas.append((m.end(i), m.end(i + 1), depois[palavras[j - 1].end() : palavras[j].end()]))
                else:
                    trocas.append((m.start(i + 1), m.end(i + 1), palavras[j].group(0)))
        else:
            inicio, fim = no_texto(i1, i2)
            trocas.append((inicio, fim, na_retificacao(j1, j2)))
    resultado, atual = [], 0
    for inicio, fim, novo in sorted(trocas):
        resultado += [texto[atual : inicio - base], novo]
        atual = fim - base
    return "".join(resultado) + texto[atual:]


def _achados(linhas: list[str], par: dict, aprox: bool) -> list[tuple[int, str, re.Match[str] | None]]:
    """(linha, texto da linha onde procurar, correspondência) de cada ocorrência do «onde se lê»."""
    achados = []
    padrao = _padrao_aprox(par["antes"]) if aprox else None
    for i, linha in enumerate(linhas):
        if not linha.strip():
            continue
        base = sem_ligacoes(linha)
        if aprox:
            achados += [(i, base, m) for m in padrao.finditer(base)]
            continue
        for texto in (base, normalizar(base)):
            n = texto.count(par["antes"])
            if n:
                achados += [(i, texto, None)] * n
                break
    return achados


def aplicar_par(linhas: list[str], par: dict) -> dict:
    """Troca o par numa das linhas (muda `linhas`) e devolve o registo da troca."""
    exatos = _achados(linhas, par, aprox=False)
    aprox = not exatos
    achados = exatos or _achados(linhas, par, aprox=True)
    titulo = _METADADOS.search(par["localizador"][-120:]) or re.search(r"\bno t[íi]tulo\b", par["localizador"][-120:], re.I)
    if titulo and (not achados or all(linhas[i].startswith("# ") for i, _, _ in achados)):
        raise SoMetadados
    if len(achados) != 1:
        raise Recusa(f"«{par['antes'][:60]}» aparece {len(achados)} vezes num só parágrafo")
    i, texto, m = achados[0]
    if linhas[i].startswith("# "):
        raise SoMetadados
    if linhas[i].startswith(">"):
        raise Recusa("o trecho está numa nota")
    artigos = _ARTIGO_LOCALIZADOR.findall(par["localizador"][-160:])
    # Sem títulos `###### Artigo` no registo, o localizador não se pode confirmar: fica para a
    # verificação às cegas.
    tem_artigos = any(_ARTIGO_TITULO.match(linha) for linha in linhas)
    if artigos and tem_artigos and _artigo_de(linhas, i) not in {_numero(a) for a in artigos}:
        raise Recusa(f"o localizador nomeia o artigo {artigos[-1]} e o trecho está no artigo {_artigo_de(linhas, i)}")
    if _ANEXO_LOCALIZADOR.search(par["localizador"][-160:]) and not artigos and not _em_anexo(linhas, i):
        raise Recusa("o localizador nomeia um anexo, mapa ou quadro e o trecho não está num anexo")
    if aprox:
        if chave(par["depois"]) == chave(par["antes"]):
            raise SoMetadados  # só pontuação ou maiúsculas: não se troca
        novo = texto[: m.start()] + troca_aprox(texto[m.start() : m.end()], _padrao_aprox(par["antes"]).match(texto[m.start() : m.end()]), par["antes"], par["depois"]) + texto[m.end() :]
    else:
        novo = texto.replace(par["antes"], par["depois"], 1)
    novo = repor_ligacoes(linhas[i], novo)
    # «… de 23 de Janeiro.» quando o texto já tem o ponto a seguir ao trecho: não o duplicar.
    novo = re.sub(r"([.;,:])\1(?!\1)", r"\1", novo) if not re.search(r"([.;,:])\1(?!\1)", linhas[i]) else novo
    antes = linhas[i]
    # Num título, a troca pode mudar a epígrafe, mas não o nível nem o número do artigo.
    if antes.startswith("#") and _INICIO_TITULO.match(antes).group(0) != _INICIO_TITULO.match(novo).group(0):
        raise Recusa("a troca muda o título (nível ou número do artigo)")
    linhas[i] = novo
    return {"linha": i, "artigo": _artigo_de(linhas, i), "aprox": aprox, "antes": antes, "depois": novo}


_LIGACAO = re.compile(r"\[([^\]]*)\]\(((?:[^()]|\([^()]*\))*)\)")


def repor_ligacoes(original: str, novo: str) -> str:
    """Volta a pôr no parágrafo retificado as ligações Markdown cujo texto não mudou, pela ordem.

    A troca faz-se no texto sem ligações; uma ligação cujo texto a retificação mudou («Decreto-Lei
    n.º 124/77» → «Decreto Regulamentar n.º 24/77») fica sem ligação, porque apontava para o errado.
    """
    posicao = 0
    for m in _LIGACAO.finditer(original):
        rotulo = m.group(1)
        i = novo.find(rotulo, posicao)
        if not rotulo or i == -1:
            continue
        novo = novo[:i] + m.group(0) + novo[i + len(rotulo) :]
        posicao = i + len(m.group(0))
    return novo


def _nota(meta: dict) -> str:
    caminho = (meta.get("identifiers") or {}).get("dre_path")
    titulo = meta["title"]
    ligacao = f"[{titulo}](https://diariodarepublica.pt{caminho})" if caminho else titulo
    return f"> Retificado pelo/a {ligacao}, publicado em {meta['publication_date']}."


def _com_notas(linhas: list[str], tocadas: dict[int, set[str]]) -> list[str]:
    """As notas de cada retificação: no fim do artigo (antes do título seguinte), como as do
    `aplicar.py`; fora dos artigos, logo a seguir ao parágrafo retificado."""
    fim_de: dict[int, set[str]] = defaultdict(set)
    for i, notas in tocadas.items():
        if _artigo_de(linhas, i) is None:
            fim_de[i + 1] |= notas
            continue
        j = i + 1
        while j < len(linhas) and not _TITULO.match(linhas[j]):
            j += 1
        fim_de[j] |= notas
    resultado = []
    for j, linha in enumerate([*linhas, None]):
        if j in fim_de:
            while resultado and not resultado[-1].strip():
                resultado.pop()
            for nota in sorted(fim_de[j]):
                if nota not in resultado:
                    resultado += ["", nota]
            resultado.append("")
        if linha is not None:
            resultado.append(linha)
    return resultado


def retificar_diploma(caminho: Path, retificacoes: list[dict]) -> tuple[str, list[dict], list[str]]:
    """O corpo com as retificações aplicadas, os registos das trocas e as recusas."""
    texto = corpo(caminho.read_text(encoding="utf-8"))
    linhas = texto.split("\n")
    trocas, recusas = [], []
    tocadas: dict[int, set[str]] = defaultdict(set)
    for r in retificacoes:
        ret = RAIZ / r["caminho_retificacao"]
        meta = front_matter(ret.read_text(encoding="utf-8"))
        copia = list(linhas)
        feitas = []
        try:
            for par in pares(corpo(ret.read_text(encoding="utf-8"))):
                if par.get("sem_aspas"):
                    raise Recusa("par sem aspas")
                plano = normalizar(sem_ligacoes("\n".join(copia)))
                if par["depois"] and plano.count(par["antes"]) == 0 and chave(par["depois"]) in chave(plano):
                    if not f" {chave(par['antes'])} " in f" {chave(plano)} ":
                        continue  # já no texto
                if not par["antes"] or not chave(par["antes"]):
                    raise Recusa("par vazio")
                if f" {chave(par['antes'])} " not in f" {chave(plano)} " and par["antes"] not in plano:
                    meta_original = front_matter(caminho.read_text(encoding="utf-8"))
                    if chave(par["antes"]) in chave(f"{meta_original.get('title')} {meta_original.get('summary')}"):
                        continue  # só nos metadados
                    raise Recusa(f"«{par['antes'][:60]}» não está no texto")
                try:
                    troca = aplicar_par(copia, par)
                except SoMetadados:
                    continue
                feitas.append({**troca, "onde_se_le": par["antes"], "deve_ler_se": par["depois"], "localizador": par["localizador"][-160:]})
        except Recusa as erro:
            recusas.append(f"{r['retificacao']} ({meta.get('title')}): {erro}")
            continue
        if not feitas:
            recusas.append(f"{r['retificacao']} ({meta.get('title')}): nada a trocar")
            continue
        linhas = copia
        nota = _nota(meta)
        for f in feitas:
            tocadas[f["linha"]].add(nota)
        trocas.append({"retificacao": r["retificacao"], "titulo": meta["title"], "publicacao": meta["publication_date"],
                       "dre_path": (meta.get("identifiers") or {}).get("dre_path"), "caminho_retificacao": r["caminho_retificacao"],
                       "classe": r["classe"], "trocas": feitas})
    novo = "\n".join(_com_notas(linhas, tocadas)) if trocas else texto
    return re.sub(r"\n{3,}", "\n\n", novo), trocas, recusas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dry-run", action="store_true", help="não grava no data/")
    args = parser.parse_args(argv)
    por_diploma: dict[str, list[dict]] = defaultdict(list)
    for linha in AUDITORIA.read_text(encoding="utf-8").splitlines():
        r = json.loads(linha)
        # O DRE repete às vezes a mesma retificação nas relações do registo.
        if r["classe"] in CLASSES and r["retificacao"] not in {x["retificacao"] for x in por_diploma[r["caminho"]]}:
            por_diploma[r["caminho"]].append(r)
    acervo = Acervo(RAIZ)
    saida, recusadas, aplicadas = [], [], 0
    for caminho_rel, retificacoes in sorted(por_diploma.items()):
        caminho = RAIZ / caminho_rel
        registo, _ = acervo.read(caminho)
        dados = acervo.read_history(caminho)
        if len(dados["versions"]) != 2:
            recusadas.append(f"{caminho_rel}: o histórico não tem duas versões")
            continue
        # Já aplicadas (estão nos `acts`): não se voltam a aplicar, porque um «onde se lê» contido
        # no «deve ler-se» («em vigor» → «em vigor, excepto …») encontrava-se outra vez.
        feitas = {a["id"] for v in dados["versions"] for a in v["acts"]}
        retificacoes = [r for r in retificacoes if r["retificacao"] not in feitas]
        if not retificacoes:
            continue
        novo, trocas, recusas = retificar_diploma(caminho, retificacoes)
        recusadas += [f"{caminho_rel}: {r}" for r in recusas]
        if not trocas:
            continue
        original = render_version(dados, dados["versions"][0], title=registo.title)
        primeira, segunda = (dict(v) for v in dados["versions"])
        segunda["acts"] = list(segunda["acts"]) + [
            {"id": t["retificacao"], "title": t["titulo"], "published": t["publicacao"], "dre_path": t["dre_path"]}
            for t in trocas if t["retificacao"] not in {a["id"] for a in segunda["acts"]}
        ]
        heads = {}
        for t in trocas:
            for f in t["trocas"]:
                heads[f["artigo"] or ""] = True
        segunda["changes"] = list(segunda["changes"]) + [f"Retifica Artigo {a}" if a else "Retifica texto" for a in heads]
        novos = historico(registo.id, registo.title, original, novo, [primeira, segunda])
        if blocos(render_version(novos, novos["versions"][1], title=registo.title)) != blocos(novo):
            recusadas.append(f"{caminho_rel}: o histórico não reproduz o texto retificado")
            continue
        if blocos(render_version(novos, novos["versions"][0], title=registo.title)) != blocos(original):
            recusadas.append(f"{caminho_rel}: a versão original mudou")
            continue
        registo.version_history = summarize(novos, acervo.history_path(caminho).name)
        titulos = "; ".join(t["titulo"] for t in trocas)
        nota = f" Retificações aplicadas por regra (consolidacao/retificacoes.py): {titulos}."
        if "Retificações aplicadas por regra" not in (registo.provenance.notes or ""):
            anteriores = (registo.provenance.notes or "").rstrip()
            registo.provenance.notes = (anteriores + ("" if not anteriores or anteriores.endswith(".") else ".") + nota).strip()
        if not args.dry_run:
            acervo.save(registo, novo, target=caminho)
            acervo.write_history(caminho, novos)
        aplicadas += len(trocas)
        saida.append({"id": registo.id, "caminho": caminho_rel, "titulo": registo.title, "retificacoes": trocas})
        print(f"{'(dry-run) ' if args.dry_run else ''}{caminho_rel}: {len(trocas)} retificação(ões), {sum(len(t['trocas']) for t in trocas)} troca(s)")
    destino = APLICADAS.with_suffix(".dry-run.jsonl") if args.dry_run else APLICADAS
    if not args.dry_run and APLICADAS.exists():
        anteriores = {json.loads(l)["id"]: l for l in APLICADAS.read_text(encoding="utf-8").splitlines() if l.strip()}
        for s in saida:
            anteriores[s["id"]] = json.dumps(s, ensure_ascii=False)
        destino.write_text("\n".join(anteriores.values()) + "\n", encoding="utf-8")
    else:
        destino.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in saida), encoding="utf-8")
    print(f"Retificações aplicadas: {aplicadas}, em {len(saida)} diplomas. Recusadas: {len(recusadas)}.")
    for r in recusadas:
        print("  ", r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
