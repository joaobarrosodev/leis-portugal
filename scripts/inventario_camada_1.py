"""Inventário da camada 1 (o texto da lei): o que falta para estar certo no que acrescenta valor.

Só lê: o export (`exports/leis-portugal.sqlite`), os registos em `data/`, a triagem da
consolidação (`consolidacao/resultados-escala.jsonl`) e os relatórios em `reports/`. Não muda
nada no `data/`, no export nem no índice. Grava em `reports/inventario-camada-1/`:

- `resumo.json`: todos os números;
- `tabelas.md`: as tabelas geradas (resumo, texto em vigor, vigência, lista de controlo…);
- uma lista `.jsonl` por falha, com os diplomas por trás de cada número.

Âmbito: 1.ª Série do Diário da República. «Prioritários» são as leis, leis orgânicas, leis
constitucionais, decretos-leis, decretos regulamentares e decretos legislativos regionais; as
portarias contam-se à parte, sem listas.

O que mede (os números da secção correspondente do `reports/inventario-camada-1.md`):

1. **Texto em vigor.** Cada diploma em vigor (ou de vigência desconhecida) com `amended_by` cai
   numa classe: consolidado pelo DRE, consolidado pelo leis-portugal, texto noutro registo (códigos
   republicados), sem texto (só digitalização) ou, pela triagem da consolidação, original que é o
   texto em vigor, alteração por aplicar, revogado por inteiro ou não triado. Cada linha leva também a marca da
   vigência revista, quando existe (`consolidacao/auditoria/vigencia-revista.jsonl`). Nos consolidados,
   «em dia» quer dizer: nenhum `amended_by` publicado depois da última versão e fora do histórico,
   e o DRE não mexeu na página depois da recolha (com `--sitemap-consolidados`).
2. **O mesmo texto em vários registos.** Os consolidados do DRE que têm, num anexo, o texto de outro diploma
   (republicações). Para cada par: onde está o texto mais recente, se o original aponta para lá
   (`republished_by` com «Texto em vigor…», que o índice lê), e se a numeração dos artigos se
   manteve (a pesquisa troca o artigo do original pelo do consolidado com o mesmo número).
3. **Vigência desconhecida** por tipo e ano, e o que os dados que já temos permitem dizer.
4. **O que o DRE consolida e não temos**, pelo sitemap da legislação consolidada.
5. **Antigos sem texto**: em vigor segundo o DRE, só com digitalização, e citados por diplomas em vigor.
6. **Lista de controlo** dos diplomas centrais (`scripts/inventario_diplomas_centrais.json`).
7. **Fora do export**: CNPD, Tribunal Constitucional e acordos coletivos sem texto.

Uso (na raiz do repositório):

    python scripts/inventario_camada_1.py --descarregar-sitemap
    python scripts/inventario_camada_1.py --sitemap-consolidados ficheiro.xml --indice rag/indice/indice.sqlite

Sem sitemap, a secção 4 e a parte «o DRE mexeu depois da recolha» ficam por medir. Com `--indice`,
verifica também se «artigo N.º do Código X» chega ao registo certo (só BM25, sem modelos).
Num worktree sem `exports/`, usa o export da pasta principal.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ElementTree
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml


RAIZ = Path(__file__).resolve().parents[1]
SITEMAP_CONSOLIDADOS = "https://files.diariodarepublica.pt/sitemap/legislacao-consolidada-sitemap-1.xml"
PRIORITARIOS = ("lei", "lei-organica", "lei-constitucional", "decreto-lei", "decreto-regulamentar", "decreto-legislativo-regional")
VIGENTES = ("in_force", "partially_in_force", "unknown")
ETIQUETA_TEXTO_EM_VIGOR = "Texto em vigor"  # início da etiqueta de `republished_by` que o índice lê
ANEXO_MINIMO = 10  # artigos para um anexo contar como «um texto dentro de outro diploma»
_YAML = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


# ------------------------------------------------------------------ leitura


def export_por_omissao(raiz: Path = RAIZ) -> Path:
    """`exports/leis-portugal.sqlite` desta cópia ou, num worktree, o da pasta principal."""
    local = raiz / "exports" / "leis-portugal.sqlite"
    if local.exists():
        return local
    git = raiz / ".git"
    if git.is_file():
        m = re.match(r"gitdir: (.*?)/\.git/worktrees/", git.read_text(encoding="utf-8"))
        if m and (Path(m.group(1)) / "exports" / "leis-portugal.sqlite").exists():
            return Path(m.group(1)) / "exports" / "leis-portugal.sqlite"
    return local


@dataclass
class Acervo:
    docs: dict[str, dict]
    alterado_por: dict[str, list[tuple[str | None, str | None, str | None]]]
    revogado_por: dict[str, list[tuple[str | None, str | None, str | None]]]
    texto_em_vigor_em: dict[str, str]
    altera: dict[str, set[str]]  # alterador -> diplomas com `amended_by` para ele
    citado_por_vigentes: Counter = field(default_factory=Counter)
    por_titulo: dict[str, list[str]] = field(default_factory=dict)


def carregar(export: Path) -> Acervo:
    con = sqlite3.connect(f"file:{export}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    docs = {r["id"]: dict(r) for r in con.execute("SELECT * FROM documentos WHERE id LIKE 'pt:%'")}
    acervo = Acervo(docs, defaultdict(list), defaultdict(list), {}, defaultdict(set))
    for origem, tipo, alvo, quando, etiqueta in con.execute(
        "SELECT source_id, type, target_id, date, label FROM relacoes WHERE type IN ('amended_by', 'repealed_by', 'republished_by')"
    ):
        if origem not in docs:
            continue
        if tipo == "amended_by":
            acervo.alterado_por[origem].append((alvo, quando, etiqueta))
            if alvo:
                acervo.altera[alvo].add(origem)
        elif tipo == "repealed_by":
            acervo.revogado_por[origem].append((alvo, quando, etiqueta))
        elif (etiqueta or "").startswith(ETIQUETA_TEXTO_EM_VIGOR) and alvo:
            acervo.texto_em_vigor_em[origem] = alvo
    com_texto_em_vigor = {i for i, d in docs.items() if d["legal_status"] == "in_force" and d["text_quality"] == "texto"}
    for origem, alvo in con.execute("SELECT source_id, target_id FROM relacoes WHERE type = 'cites' AND target_id IS NOT NULL"):
        if origem in com_texto_em_vigor and origem != alvo:
            acervo.citado_por_vigentes[alvo] += 1
    por_titulo: dict[str, list[str]] = defaultdict(list)
    for i, d in docs.items():
        por_titulo[d["title"]].append(i)
    acervo.por_titulo = dict(por_titulo)
    con.close()
    return acervo


def cabecalho(caminho: Path) -> dict:
    """O que o inventário precisa do front matter de um registo consolidado."""
    texto = caminho.read_text(encoding="utf-8")
    fim = texto.find("\n---\n", 4)
    front = yaml.load(texto[4:fim], Loader=_YAML) if texto.startswith("---\n") and fim > 0 else {}
    versao = front.get("version") or {}
    historico = front.get("version_history") or {}
    fonte = front.get("source") or {}
    return {
        "rotulo": versao.get("label") or "",
        "data_consolidacao": versao.get("consolidation_date"),
        "alteradores_no_historico": {v.get("amending") for v in historico.get("versions") or [] if v.get("amending")},
        "lastmod": historico.get("source_lastmod"),
        "url_consolidado": fonte.get("consolidated_url"),
        "recolhido": (fonte.get("retrieved_at") or "")[:10],
        "notas": front.get("notes") or [],
    }


def do_dre(rotulo: str) -> bool:
    return rotulo.startswith("Versão consolidada pelo DRE")


# ------------------------------------------------------------------ artigos e anexos

_ANEXO = re.compile(r"^## (anexo\b.*)$", re.I)
_ARTIGO = re.compile(r"^###### (?:Artigo|ARTIGO|Art\.?|Base|BASE) +(\S+?)(?: +[—–-] +(.*))?$")
_ARTIGO_CORRIDO = re.compile(r"^(?:Artigo|ARTIGO|Art\.) +(\d+)\.[ºo°](-[A-Z])?(?=[ .]|$)")
_DATA = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


def _numero(bruto: str) -> str | None:
    m = re.match(r"^(\d+)\.?[ºo°]?(?:\.?-? ?([A-Z]{1,2}))?\.?$", bruto.strip())
    if not m:
        return "único" if bruto.strip().lower().startswith("único") else None
    return f"{int(m.group(1))}.º" + (f"-{m.group(2)}" if m.group(2) else "")


@dataclass
class Parte:
    """Uma parte de um registo: o articulado do próprio diploma («») ou um anexo."""

    artigos: dict[str, str] = field(default_factory=dict)  # número → epígrafe
    ultima_nota: str | None = None  # a data mais recente nas notas «> Alterado pelo/a …» desta parte
    notas_dessa_data: str = ""  # o texto das notas com essa data: diz que diploma fez a última alteração


def ler_partes(markdown: str, hoje: str = "9999") -> dict[str, Parte]:
    """Parte («» é o articulado do próprio diploma, o resto são os anexos) → artigos e data da última nota.

    Lê os títulos `###### Artigo N.º — Epígrafe`; um registo sem nenhum (texto corrido) é lido pelas
    linhas «Artigo N.º …», sem epígrafes, e cada «1.º» repetido abre outra parte (o decreto e o código
    que ele aprova). Um artigo repetido na mesma parte fica com a primeira epígrafe. Em cada nota
    conta a última data da linha: a da entrada em vigor, ou a da publicação quando só há essa.
    """
    corpo = markdown[markdown.find("\n---\n", 4) + 5 :] if markdown.startswith("---\n") else markdown
    linhas = corpo.splitlines()
    resultado: dict[str, Parte] = defaultdict(Parte)
    parte = ""
    for linha in linhas:
        anexo = _ANEXO.match(linha)
        if anexo:
            parte = anexo.group(1).strip()
            continue
        artigo = _ARTIGO.match(linha)
        if artigo:
            numero = _numero(artigo.group(1))
            if numero:
                resultado[parte].artigos.setdefault(numero, (artigo.group(2) or "").strip())
        elif linha.startswith("> "):
            datas = [d for d in _DATA.findall(linha) if d <= hoje]  # uma alteração com entrada em vigor futura ainda não é o texto
            if datas and (resultado[parte].ultima_nota or "") < datas[-1]:
                resultado[parte].ultima_nota, resultado[parte].notas_dessa_data = datas[-1], linha
            elif datas and resultado[parte].ultima_nota == datas[-1]:
                resultado[parte].notas_dessa_data += "\n" + linha
    if not any(p.artigos for p in resultado.values()):
        resultado, parte, numeracoes = defaultdict(Parte), "", 1
        for linha in linhas:
            m = _ARTIGO_CORRIDO.match(linha)
            if m:
                numero = f"{int(m.group(1))}.º{m.group(2) or ''}"
                if numero == "1.º" and "1.º" in resultado[parte].artigos:
                    numeracoes += 1
                    parte = f"({numeracoes}.ª numeração)"
                resultado[parte].artigos.setdefault(numero, "")
    return {p: v for p, v in resultado.items() if v.artigos}


def partes(markdown: str) -> dict[str, dict[str, str]]:
    """Só os artigos de cada parte: {parte: {número: epígrafe}}."""
    return {p: v.artigos for p, v in ler_partes(markdown).items()}


def simples(texto: str) -> str:
    """Minúsculas sem acentos nem pontuação, para comparar epígrafes e nomes."""
    sem = unicodedata.normalize("NFD", texto.lower())
    sem = "".join(c for c in sem if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", sem).split())


def sobreposicao(anexo: dict[str, str], outro: dict[str, str]) -> dict:
    """Quanto um conjunto de artigos coincide com outro: números em comum e epígrafes iguais nesses."""
    comuns = [n for n in anexo if n in outro]
    com_epigrafe = [n for n in comuns if anexo[n] and outro[n]]
    iguais = [n for n in com_epigrafe if simples(anexo[n]) == simples(outro[n])]
    menor = min(len(anexo), len(outro))
    return {
        "artigos": len(anexo),
        "comuns": len(comuns),
        "com_epigrafe": len(com_epigrafe),
        "epigrafes_iguais": len(iguais),
        "fracao_numeros": round(len(comuns) / menor, 3) if menor else 0.0,
        "fracao_epigrafes": round(len(iguais) / len(com_epigrafe), 3) if com_epigrafe else None,
    }


_PALAVRAS_VAZIAS = {"anexo", "a", "o", "e", "de", "do", "da", "dos", "das", "que", "se", "refere", "artigo", "republicacao", "n", "i", "ii", "iii", "iv", "v", "vi", "vii", "em", "ao", "no", "na", "nos", "nas", "sobre", "os", "as"}


def nome_contido(nome_do_anexo: str, texto: str) -> float:
    """Fração das palavras do nome de um anexo («CÓDIGO DO IMPOSTO SOBRE O VALOR ACRESCENTADO») que estão num sumário."""
    palavras = [p for p in simples(nome_do_anexo).split() if p not in _PALAVRAS_VAZIAS and not p.isdigit()]
    if len(palavras) < 2:
        return 0.0
    alvo = set(simples(texto).split())
    return round(sum(p in alvo for p in palavras) / len(palavras), 3)


_REFERENCIA = re.compile(
    r"(Decreto Legislativo Regional|Decreto Regulamentar Regional|Decreto Regulamentar|Decreto-Lei|Lei Orgânica|Lei|Decreto)"
    r"(?: n\.?\s?º)? ?(\d+(?:-[A-Z])?/\d{2,4}(?:/[AM])?|\d{4,5})(?![\d/])"
)


def referencias(texto: str) -> list[str]:
    """Os títulos de diplomas citados num texto, na forma do acervo («Decreto-Lei n.º 114/94»)."""
    texto = re.sub(r"<[^>]+>", " ", texto)
    return list(dict.fromkeys(f"{tipo} n.º {numero}" for tipo, numero in _REFERENCIA.findall(texto)))


def aprovados_nas_notas(notas: list) -> list[str]:
    """Os diplomas que uma nota do DRE dá como origem do texto republicado («…tem por base a republicação… do
    Código Penal, aprovado pelo Decreto-Lei n.º 400/82»), na forma dos títulos do acervo."""
    titulos: list[str] = []
    for nota in map(str, notas):
        limpa = " ".join(re.sub(r"<[^>]+>", " ", nota).split())
        if not re.search(r"republica|vers[ãa]o consolidada", limpa, re.I):
            continue
        for trecho in re.findall(r"aprovad[oa]s?\s+pel[oa]s?\s+(.{0,80})", limpa, re.I):
            titulos += referencias(trecho)[:1]
    return list(dict.fromkeys(titulos))


def mesma_obra(medida: dict, tamanho_a: int, tamanho_b: int, *, explicito: bool = False, nome: float = 0.0, altera: bool = False, revoga: bool = False, no_articulado: bool = False) -> bool:
    """Se duas partes são cópias do mesmo texto (um código e a sua republicação).

    Pede sempre 60 % dos números de artigo em comum (sobre a parte mais pequena) e pelo menos 8. Depois, uma de três:

    - as epígrafes coincidem (70 % de pelo menos 8);
    - a ligação é explícita (nota do DRE, `republished_by` ou o diploma citado no nome do anexo) e os tamanhos
      são parecidos, ou a nota fala do articulado do próprio diploma (o Código Penal no DL 48/95);
    - não há epígrafes para comparar, o nome do anexo está no sumário do outro diploma, que este altera, e os
      tamanhos são parecidos (o Código do IVA no DL 102/2008).

    As duas últimas não valem quando o diploma revoga o outro: aí é o regime que lhe sucedeu, com o mesmo nome.
    """
    if medida["fracao_numeros"] < 0.6 or medida["comuns"] < 8:
        return False
    if medida["com_epigrafe"] >= 8 and medida["fracao_epigrafes"] >= 0.7:
        return True
    if revoga:
        return False
    parecidos = min(tamanho_a, tamanho_b) >= 0.5 * max(tamanho_a, tamanho_b)
    if explicito and (parecidos or no_articulado):
        return True
    return medida["com_epigrafe"] < 8 and nome >= 0.8 and altera and parecidos


# ------------------------------------------------------------------ 2. o mesmo texto em vários registos


def obras(acervo: Acervo, cabecalhos: dict[str, dict], raiz: Path, tipos: tuple[str, ...], hoje: str = "9999") -> list[dict]:
    """Os textos que existem em mais de um registo: um código, as leis que o republicaram em anexo e o diploma que o aprovou.

    Parte de cada consolidado do DRE com um anexo de 10 ou mais artigos (ou com uma nota a dizer que tem por base uma
    republicação) e procura o mesmo texto nos diplomas que ele altera, cita no sumário, nas notas ou no nome do anexo.
    Cada grupo de partes ligadas é uma obra, com as suas cópias. Em cada obra:

    - `origem`: a cópia no registo mais antigo (o diploma que aprovou o texto);
    - `atual`: a cópia com a data de texto mais recente; se o registo dela já não vigora, a obra não está em vigor
      e as cópias que ficaram em registos em vigor são texto revogado servido como atual;
    - `data_do_texto` de uma cópia: a última nota de alteração dessa parte ou, sem notas, a publicação do registo;
    - `desatualizada`: a cópia tem data de texto anterior à da atual, a não ser que seja a republicação que fez a
      última alteração (o texto é o mesmo). É uma comparação de datas, não de textos.
    """
    lidas: dict[str, dict[str, Parte]] = {}

    def partes_de(i: str) -> dict[str, Parte]:
        if i not in lidas:
            caminho = raiz / acervo.docs[i]["path"]
            lidas[i] = ler_partes(caminho.read_text(encoding="utf-8"), hoje) if caminho.exists() else {}
        return lidas[i]

    republica = defaultdict(set)
    for original, consolidado in acervo.texto_em_vigor_em.items():
        republica[consolidado].add(original)
    pai: dict[tuple[str, str], tuple[str, str]] = {}

    def raiz_de(no: tuple[str, str]) -> tuple[str, str]:
        pai.setdefault(no, no)
        while pai[no] != no:
            pai[no] = pai[pai[no]]
            no = pai[no]
        return no

    for i, cab in sorted(cabecalhos.items()):
        doc = acervo.docs[i]
        if not do_dre(cab["rotulo"]) or doc["document_type"] not in tipos:
            continue
        notas = " ".join(map(str, cab["notas"]))
        com_nota = bool(re.search(r"republica", notas, re.I))
        minhas = {p: v for p, v in partes_de(i).items() if len(v.artigos) >= ANEXO_MINIMO and (p or com_nota)}
        if not minhas:
            continue
        nas_notas = {c for titulo in aprovados_nas_notas(cab["notas"]) for c in acervo.por_titulo.get(titulo, ())}
        candidatos = set(republica[i]) | set(acervo.altera.get(i, ())) | nas_notas
        for titulo in referencias(" ".join([doc["summary"] or "", *minhas])):
            candidatos.update(acervo.por_titulo.get(titulo, ()))
        candidatos = {c for c in candidatos if c != i and (acervo.docs[c]["publication_date"] or "") < (doc["publication_date"] or "")}
        ligados_pela_nota: set[str] = set()
        for nome, parte in sorted(minhas.items(), key=lambda x: not x[0]):  # os anexos primeiro, o articulado no fim
            for c in candidatos:
                if not nome and c in ligados_pela_nota:
                    continue  # o texto já foi encontrado num anexo: o articulado é o da lei que republica
                alvo = acervo.docs[c]
                explicito = c in republica[i] or c in nas_notas or alvo["title"] in referencias(nome)
                if not nome and not explicito:
                    continue  # o articulado do próprio diploma só se compara com o que uma nota do DRE indica
                for nome_c, parte_c in partes_de(c).items():
                    if len(parte_c.artigos) < ANEXO_MINIMO:
                        continue
                    medida = sobreposicao(parte.artigos, parte_c.artigos)
                    contido = nome_contido(nome, f"{alvo['summary'] or ''} {nome_c}") if nome else 0.0
                    revoga = any(alvo_r == i for alvo_r, _, _ in acervo.revogado_por.get(c, ()))
                    if mesma_obra(medida, len(parte.artigos), len(parte_c.artigos), explicito=explicito, nome=contido,
                                  altera=c in acervo.altera.get(i, ()), revoga=revoga, no_articulado=not nome):
                        pai[raiz_de((i, nome))] = raiz_de((c, nome_c))
                        ligados_pela_nota.add(c)
        # A nota do DRE basta: um original em texto corrido que este leitor não parte em artigos (o DL 400/82) liga-se pela maior parte.
        for c in sorted(nas_notas & candidatos - ligados_pela_nota):
            minha = max(minhas, key=lambda p: len(minhas[p].artigos))
            if not partes_de(c):
                lidas[c][""] = Parte()
            dele = max(partes_de(c), key=lambda p: len(partes_de(c)[p].artigos))
            pai[raiz_de((i, minha))] = raiz_de((c, dele))

    grupos: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    for no in list(pai):
        grupos[raiz_de(no)].append(no)
    resultado = []
    for nos in grupos.values():
        copias = []
        for i, nome in nos:
            doc, parte, cab = acervo.docs[i], partes_de(i)[nome], cabecalhos.get(i)
            copias.append({
                "id": i, "titulo": doc["title"], "parte": nome, "artigos": len(parte.artigos), "publicado": doc["publication_date"],
                "data_do_texto": max(parte.ultima_nota or "", doc["publication_date"] or ""), "estado": doc["legal_status"], "texto": doc["text_quality"],
                "consolidado_por": None if cab is None else "DRE" if do_dre(cab["rotulo"]) else "leis-portugal",
                "registo_consolidado_ate": cab["data_consolidacao"] if cab else None, "sumario": (doc["summary"] or "")[:140],
            })
        copias.sort(key=lambda c: (c["publicado"] or "", c["id"], c["parte"]))
        origem = copias[0]
        atual = max(copias, key=lambda c: (c["data_do_texto"], c["consolidado_por"] is not None, c["artigos"]))
        medida = sobreposicao(partes_de(origem["id"])[origem["parte"]].artigos, partes_de(atual["id"])[atual["parte"]].artigos)
        ultimas_notas = partes_de(atual["id"])[atual["parte"]].notas_dessa_data
        for c in copias:
            c["papel"] = "atual" if c is atual else "origem" if c is origem else "cópia"
            # A republicação que fez a última alteração tem o mesmo texto, só com a data da publicação em vez da da entrada em vigor.
            fez_a_ultima = bool(re.search(re.escape(c["titulo"]) + r"(?![\d/-])", ultimas_notas)) and c["consolidado_por"] is not None and c["data_do_texto"] == (c["publicado"] or "")
            c["desatualizada"] = c is not atual and c["data_do_texto"] < atual["data_do_texto"] and not fez_a_ultima
            c["servida_como_vigente"] = c is not atual and c["estado"] in VIGENTES and c["texto"] == "texto"
        resultado.append({
            "obra": max((c["parte"] for c in copias if c["parte"] and not c["parte"].startswith("(")), key=len, default="") or origem["sumario"][:80],
            "origem": origem["id"], "origem_titulo": origem["titulo"], "atual": atual["id"], "atual_titulo": atual["titulo"], "atual_parte": atual["parte"],
            "data_do_texto_atual": atual["data_do_texto"], "atual_fora_da_origem": atual["id"] != origem["id"], "em_vigor": atual["estado"] in VIGENTES,
            "origem_ligada_ao_atual": acervo.texto_em_vigor_em.get(origem["id"]) == atual["id"],
            "numeros_comuns_origem_atual": medida["comuns"], "com_epigrafe": medida["com_epigrafe"], "epigrafes_iguais": medida["epigrafes_iguais"],
            "copias_desatualizadas_servidas": sum(c["desatualizada"] and c["servida_como_vigente"] for c in copias),
            "artigos_em_copias_desatualizadas_servidas": sum(c["artigos"] for c in copias if c["desatualizada"] and c["servida_como_vigente"]),
            "copias": copias,
        })
    return sorted(resultado, key=lambda o: -max(c["artigos"] for c in o["copias"]))


def onde_vive(i: str, acervo: Acervo, cabecalhos: dict[str, dict], lista_obras: list[dict]) -> tuple[str | None, dict | None]:
    """O registo com o texto em vigor mais recente de um diploma (ele próprio, outro, ou nenhum) e a obra usada.

    Só conta a obra de que o diploma é a origem (o IVA no DL 394-B/84), não as que ele republica noutro anexo.
    """
    minhas = [o for o in lista_obras if o["origem"] == i]
    if minhas:
        obra = max(minhas, key=lambda o: max(c["artigos"] for c in o["copias"] if c["id"] == i))
        return obra["atual"], obra
    if i in cabecalhos:
        return i, None
    if i in acervo.texto_em_vigor_em:
        return acervo.texto_em_vigor_em[i], None
    return None, None


# ------------------------------------------------------------------ 1. texto em vigor


def em_dia(i: str, acervo: Acervo, cab: dict, sitemap: dict[str, str] | None, tambem: str | None = None, desde: str | None = None) -> dict:
    """Se um consolidado tem alteradores publicados depois da última versão e fora do histórico.

    `tambem`: o diploma de origem, quando o texto vive noutro registo (o DRE regista as alterações num ou noutro);
    `desde`: a data do texto dessa cópia, para os alteradores da origem.
    """
    ate = cab["data_consolidacao"] or ""
    posteriores = {(quando, alvo) for alvo, quando, _ in acervo.alterado_por.get(i, ()) if quando and quando > ate and alvo not in cab["alteradores_no_historico"] and alvo != i}
    if tambem:
        posteriores |= {(quando, alvo) for alvo, quando, _ in acervo.alterado_por.get(tambem, ())
                        if quando and quando > max(desde or "", ate) and alvo not in cab["alteradores_no_historico"] and alvo != i}
    mexido = bool(sitemap and cab["url_consolidado"] and sitemap.get(cab["url_consolidado"], "") > (cab["lastmod"] or ""))
    return {
        "em_dia": not posteriores and not mexido,
        "alteradores_posteriores": [{"data": q, "id": a, "titulo": (acervo.docs.get(a) or {}).get("title")} for q, a in sorted(posteriores)],
        "dre_mexeu_depois_da_recolha": mexido,
        "dre_lastmod": sitemap.get(cab["url_consolidado"]) if sitemap and cab["url_consolidado"] else None,
    }


TRIAGEM_PARA_CLASSE = {
    "sem alteração textual": "original_e_o_texto_em_vigor",
    "para LLM": "alteracao_por_aplicar",
    "aplicado por regra": "alteracao_por_aplicar",
    "alteração só em imagem": "alteracao_so_em_imagem",
    "sem texto do alterador": "alteracao_por_aplicar",
    "revogado por inteiro": "revogado_por_inteiro",
    "não triado": "nao_triado",
    "excluído": "nao_triado",
}


def classe_do_texto(doc: dict, cab: dict | None, vive_em: str | None, triagem: dict | None) -> str:
    """A classe de um diploma em vigor com `amended_by`, quanto ao texto em vigor (ver o início do ficheiro)."""
    if vive_em and vive_em != doc["id"]:
        return "texto_noutro_registo"
    if cab is not None:
        return "consolidado_dre" if do_dre(cab["rotulo"]) else "consolidado_leis_portugal"
    if doc["text_quality"] != "texto":
        return "sem_texto"
    if triagem is None:
        return "nao_triado"
    return TRIAGEM_PARA_CLASSE.get(triagem.get("estado"), "nao_triado")


def texto_em_vigor(acervo: Acervo, cabecalhos: dict[str, dict], lista_obras: list[dict], triagem: dict[str, dict], sitemap: dict[str, str] | None, tipos: tuple[str, ...],
                   marcas: dict[str, str] | None = None) -> list[dict]:
    """`marcas`: id → marca da vigência revista (`consolidacao/auditoria/vigencia-revista.jsonl`): `nao_vigora`, `regime_anterior` ou `por_confirmar`."""
    linhas = []
    for i, doc in acervo.docs.items():
        if doc["document_type"] not in tipos or doc["series"] != "I" or doc["legal_status"] not in VIGENTES or not acervo.alterado_por.get(i):
            continue
        vive_em, obra = onde_vive(i, acervo, cabecalhos, lista_obras)
        classe = classe_do_texto(doc, cabecalhos.get(i), vive_em, triagem.get(i))
        linha = {
            "id": i, "titulo": doc["title"], "tipo": doc["document_type"], "data": doc["publication_date"], "estado": doc["legal_status"],
            "classe": classe, "alteradores": len(acervo.alterado_por[i]), "citado_por_vigentes": acervo.citado_por_vigentes.get(i, 0),
            "sumario": (doc["summary"] or "")[:160],
        }
        if marcas and i in marcas:
            linha["marca_de_vigencia"] = marcas[i]
        if classe in ("consolidado_dre", "consolidado_leis_portugal"):
            linha["consolidado_ate"] = cabecalhos[i]["data_consolidacao"]
            linha |= em_dia(i, acervo, cabecalhos[i], sitemap)
        elif classe == "texto_noutro_registo":
            linha["vive_em"] = vive_em
            linha["vive_em_titulo"] = acervo.docs[vive_em]["title"]
            linha["ligado"] = acervo.texto_em_vigor_em.get(i) == vive_em
            linha["tem_consolidacao_propria_mais_antiga"] = i in cabecalhos
            if vive_em in cabecalhos:
                linha["consolidado_ate"] = obra["data_do_texto_atual"] if obra else cabecalhos[vive_em]["data_consolidacao"]
                linha |= em_dia(vive_em, acervo, cabecalhos[vive_em], sitemap, tambem=i, desde=obra["data_do_texto_atual"] if obra else None)
        elif triagem.get(i):
            linha["triagem"] = triagem[i].get("estado")
            vistos = {p.get("id") for p in triagem[i].get("passos") or []}
            linha["alteradores_novos_desde_a_triagem"] = sorted({a for a, _, _ in acervo.alterado_por[i] if a and a not in vistos}) if vistos else []
        linhas.append(linha)
    return linhas


# ------------------------------------------------------------------ 3. vigência desconhecida

_REVOGACAO_PARCIAL = re.compile(
    r"^Revogad[oa]s?,?(?: a partir de [^,]+,)?(?: com efeitos[^,]+,)? (?:o|a|os|as) (?:art|n\.?º|n\.?ºs|al\.|alínea|anexo|cap|sec|mapa|quadro|base|§|parte|disposiç|norma)",
    re.I,
)
_TEMPORARIO = re.compile(r"Orçamento do Estado para|Grandes Opções|execução do Orçamento|para o ano de \d{4}|para \d{4}\b|estado de (?:emergência|calamidade|alerta)|COVID|medidas excecionais e temporárias", re.I)
_ATO_DE_ALTERACAO = re.compile(
    r"^(?:Altera|Procede à|Primeira|Segunda|Terceira|Quarta|Quinta|Sexta|Sétima|Oitava|Nona|Décima|Vigésima|Trigésima|\d+\.ª) .{0,40}?altera|^Altera\b|^Prorroga|^Revoga\b|^Cessa|^Repristina|^Suspende", re.I
)


def revogacao(relacoes: list[tuple[str | None, str | None, str | None]]) -> str | None:
    """`inteira`, `parcial` ou None, pelas etiquetas das relações `repealed_by` do DRE.

    A etiqueta diz o que é revogado: «Revogado, a partir de …, o art. 3.º» é parcial; sem unidade
    («Revogado pelo …», «Revogado, a partir de …, o Dec Lei 5/2020») conta como o diploma inteiro.
    Com «com exceção» ou «na parte» é sempre parcial.
    """
    if not relacoes:
        return None
    inteiras = [e for _, _, e in relacoes if not _REVOGACAO_PARCIAL.match(e or "") and not re.search(r"exce[çp]|na parte|parcialmente|em tudo o que", e or "", re.I)]
    return "inteira" if inteiras else "parcial"


def classe_desconhecida(doc: dict, revogado: str | None, proposta: dict | None, ultima_alteracao: str | None) -> str:
    """O que os dados que já temos dizem de um diploma com `legal_status: unknown`."""
    sumario = doc["summary"] or ""
    if revogado == "inteira":
        return "revogado_segundo_a_relacao_do_dre"
    if proposta and proposta.get("status") in ("repealed", "not_in_force"):
        return "revogacao_lida_no_texto_de_outro_diploma"
    if _TEMPORARIO.search(sumario):
        return "temporario_ou_orcamental"
    if _ATO_DE_ALTERACAO.search(sumario):
        return "ato_de_alteracao"
    if ultima_alteracao and ultima_alteracao > (doc["publication_date"] or ""):
        return "alterado_depois_e_sem_revogacao"
    return "sem_indicio_de_revogacao"


def vigencia_desconhecida(acervo: Acervo, propostas: dict[str, dict], tipos: tuple[str, ...]) -> list[dict]:
    linhas = []
    for i, doc in acervo.docs.items():
        if doc["document_type"] not in tipos or doc["series"] != "I" or doc["legal_status"] != "unknown":
            continue
        datas = [q for _, q, _ in acervo.alterado_por.get(i, ()) if q]
        ultima = max(datas) if datas else None
        revogado = revogacao(acervo.revogado_por.get(i, []))
        linhas.append({
            "id": i, "titulo": doc["title"], "tipo": doc["document_type"], "data": doc["publication_date"], "texto": doc["text_quality"],
            "classe": classe_desconhecida(doc, revogado, propostas.get(i), ultima), "revogacao_no_dre": revogado,
            "alteradores": len(acervo.alterado_por.get(i, ())), "ultima_alteracao": ultima,
            "citado_por_vigentes": acervo.citado_por_vigentes.get(i, 0), "sumario": (doc["summary"] or "")[:160],
        })
    return linhas


# ------------------------------------------------------------------ 4. sitemap dos consolidados


def ler_sitemap(xml: bytes) -> dict[str, str]:
    """URL da legislação consolidada → `lastmod` (AAAA-MM-DD)."""
    espaco = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    entradas = {}
    for no in ElementTree.fromstring(xml).findall("s:url", espaco):
        url = (no.findtext("s:loc", default="", namespaces=espaco) or "").strip()
        if "/dr/legislacao-consolidada/" in url:
            entradas[url] = (no.findtext("s:lastmod", default="", namespaces=espaco) or "").strip()[:10]
    return entradas


def comparar_sitemap(sitemap: dict[str, str], nossos: dict[str, dict], falhas: set[str]) -> dict:
    """O que o DRE lista e não temos, e o que temos mas o DRE mudou depois da recolha.

    `nossos`: URL do consolidado → {id, lastmod}. `falhas`: URLs em que a fonte não tinha texto.
    """
    em_falta = [{"url": u, "tipo": u.split("/")[-2], "ano": u.split("/")[-1][:4], "dre_lastmod": m, "motivo": "sem_texto_na_fonte" if u in falhas else "por_recolher"}
                for u, m in sorted(sitemap.items()) if u not in nossos]
    mexidos = [{"url": u, "id": nossos[u]["id"], "dre_lastmod": m, "nosso_lastmod": nossos[u]["lastmod"]}
               for u, m in sorted(sitemap.items()) if u in nossos and m > (nossos[u]["lastmod"] or "")]
    return {"listados": len(sitemap), "temos": sum(u in nossos for u in sitemap), "em_falta": em_falta, "mexidos_depois_da_recolha": mexidos,
            "so_nossos": sorted(u for u in nossos if u not in sitemap)}


# ------------------------------------------------------------------ 5. antigos sem texto


def faixa(ano: int) -> str:
    return "antes de 1910" if ano < 1910 else "1910–1959" if ano < 1960 else "1960–1996" if ano < 1997 else "1997 ou depois"


def antigos_sem_texto(acervo: Acervo, tipos: tuple[str, ...]) -> list[dict]:
    linhas = []
    for i, doc in acervo.docs.items():
        if doc["document_type"] not in tipos or doc["series"] not in ("I", None) or doc["text_quality"] == "texto" or doc["legal_status"] not in VIGENTES:
            continue
        ano = int((doc["publication_date"] or "0000")[:4])
        linhas.append({
            "id": i, "titulo": doc["title"], "tipo": doc["document_type"], "data": doc["publication_date"], "faixa": faixa(ano), "estado": doc["legal_status"],
            "texto": doc["text_quality"], "citado_por_vigentes": acervo.citado_por_vigentes.get(i, 0), "alteradores": len(acervo.alterado_por.get(i, ())),
            "sumario": (doc["summary"] or "")[:160], "pdf": doc["pdf_url"],
        })
    return sorted(linhas, key=lambda r: (-r["citado_por_vigentes"], r["data"] or ""))


# ------------------------------------------------------------------ 6. lista de controlo


def resolver(titulo: str, acervo: Acervo) -> str | None:
    """O registo com este título; com vários, o consolidado, depois o que está em vigor, depois o mais citado."""
    ids = acervo.por_titulo.get(titulo) or []
    ordem = lambda i: (acervo.docs[i]["version_kind"] == "consolidated", acervo.docs[i]["legal_status"] == "in_force", acervo.citado_por_vigentes.get(i, 0))  # noqa: E731
    return max(ids, key=ordem) if ids else None


def duplicados(acervo: Acervo, tipos: tuple[str, ...]) -> list[dict]:
    """Diplomas com mais de um registo (o mesmo título e a mesma data de publicação) em que pelo menos dois têm texto.

    O DRE tem alguns diplomas duas vezes; se só um dos registos é consolidado, o outro serve o texto de origem."""
    grupos: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for d in acervo.docs.values():
        if d["document_type"] in tipos and d["series"] == "I" and d["publication_date"] and d["text_quality"] == "texto":
            grupos[(d["title"], d["publication_date"])].append(d)
    return [{"titulo": t, "data": q, "registos": [{"id": d["id"], "estado": d["legal_status"], "versao": d["version_kind"], "alteradores": len(acervo.alterado_por.get(d["id"], ())),
                                                  "sumario": (d["summary"] or "")[:100]} for d in sorted(g, key=lambda d: d["id"])]}
            for (t, q), g in sorted(grupos.items()) if len(g) > 1]


def lista_de_controlo(centrais: list[dict], acervo: Acervo, cabecalhos: dict[str, dict], lista_obras: list[dict], triagem: dict[str, dict], sitemap: dict[str, str] | None, raiz: Path,
                      marcas: dict[str, str] | None = None) -> list[dict]:
    linhas = []
    for entrada in centrais:
        linha = {"area": entrada["area"], "nome": entrada["nome"], "diploma": entrada["diploma"], "pesquisa": entrada.get("pesquisa")}
        i = resolver(entrada["diploma"], acervo)
        if i is None:
            linhas.append(linha | {"id": None, "problemas": ["não está no acervo"]})
            continue
        doc = acervo.docs[i]
        vive_em, obra = onde_vive(i, acervo, cabecalhos, lista_obras)
        problemas = []
        linha |= {"id": i, "estado": doc["legal_status"], "data": doc["publication_date"], "sumario": (doc["summary"] or "")[:120],
                  "vive_em": vive_em, "vive_em_titulo": acervo.docs[vive_em]["title"] if vive_em else None, "parte": obra["atual_parte"] if obra else None}
        if doc["legal_status"] == "unknown":
            problemas.append("vigência desconhecida")
        elif doc["legal_status"] not in VIGENTES:
            problemas.append(f"o DRE dá-o como {doc['legal_status']}")
        if marcas and i in marcas:
            linha["marca_de_vigencia"] = marcas[i]
            problemas.append(f"vigência revista: {marcas[i].replace('_', ' ')}")
        if vive_em is None:
            classe = classe_do_texto(doc, None, None, triagem.get(i))
            linha["texto"] = classe
            if doc["text_quality"] != "texto":
                problemas.append("sem texto (só digitalização)")
            elif not acervo.alterado_por.get(i):
                linha["texto"] = "original_sem_alteracoes"
            elif classe == "original_e_o_texto_em_vigor":
                problemas.append(f"{len(acervo.alterado_por[i])} `amended_by` e sem consolidação: a triagem diz que nenhum muda o texto")
            else:
                problemas.append(f"alterado e sem texto em vigor ({classe.replace('_', ' ')}; {len(acervo.alterado_por[i])} `amended_by`)")
        else:
            cab = cabecalhos.get(vive_em)
            linha["texto"] = ("consolidado_dre" if do_dre(cab["rotulo"]) else "consolidado_leis_portugal") if cab else "original"
            if cab:
                linha["consolidado_ate"] = obra["data_do_texto_atual"] if obra else cab["data_consolidacao"]
                dia = em_dia(vive_em, acervo, cab, sitemap, tambem=i if vive_em != i else None, desde=obra["data_do_texto_atual"] if obra else None)
                linha |= dia
                if dia["dre_mexeu_depois_da_recolha"]:
                    problemas.append(f"o DRE mexeu no consolidado a {dia['dre_lastmod']}, depois da recolha")
                if dia["alteradores_posteriores"]:
                    ultimos = ", ".join(f"{a['titulo'] or a['id']} ({a['data']})" for a in dia["alteradores_posteriores"][-3:])
                    problemas.append(f"{len(dia['alteradores_posteriores'])} alterador(es) depois da última versão: {ultimos}")
            if vive_em != i:
                if acervo.texto_em_vigor_em.get(i) != vive_em:
                    problemas.append("o original não aponta para o registo com o texto em vigor (sem `republished_by` «Texto em vigor»)")
                if obra and obra["com_epigrafe"] >= 20 and obra["epigrafes_iguais"] / obra["com_epigrafe"] < 0.8:
                    problemas.append(f"numeração diferente da do original: só {obra['epigrafes_iguais']} de {obra['com_epigrafe']} artigos com o mesmo número têm a mesma epígrafe")
        if obra:
            outras = [c for c in obra["copias"] if c["desatualizada"] and c["servida_como_vigente"]]
            if outras:
                nomes = ", ".join(f"{c['titulo']} (texto de {c['data_do_texto']})" for c in outras)
                problemas.append(f"{len(outras)} cópia(s) com texto de outra data servida(s) como em vigor: {nomes}")
            linha["copias"] = [{k: c.get(k) for k in ("id", "titulo", "parte", "artigos", "data_do_texto", "papel", "desatualizada", "servida_como_vigente", "pedacos_atuais_no_indice")} for c in obra["copias"]]
        if vive_em and (raiz / acervo.docs[vive_em]["path"]).exists():
            lidas = partes((raiz / acervo.docs[vive_em]["path"]).read_text(encoding="utf-8"))
            proprio = lidas.get("", {})
            maior = max(((p, a) for p, a in lidas.items() if p), key=lambda x: len(x[1]), default=(None, {}))
            linha["artigos_do_diploma"] = len(proprio)
            linha["artigos_no_maior_anexo"] = len(maior[1])
            linha["maior_anexo"] = maior[0]
            if len(maior[1]) >= ANEXO_MINIMO and proprio:
                linha["numeros_repetidos_entre_diploma_e_anexo"] = len(set(proprio) & set(maior[1]))
        gemeos = [g for g in acervo.por_titulo.get(doc["title"], ()) if g != i and acervo.docs[g]["publication_date"] == doc["publication_date"] and acervo.docs[g]["text_quality"] == "texto"]
        if gemeos:
            problemas.append("há outro registo do mesmo diploma com texto: " + ", ".join(f"{g} ({acervo.docs[g]['version_kind']}, {acervo.docs[g]['legal_status']})" for g in gemeos))
        linha["problemas"] = problemas
        linhas.append(linha)
    return linhas


def verificar_pesquisa(linhas: list[dict], indice: Path, raiz: Path, acervo: Acervo) -> None:
    """«artigo N.º do <nome>» chega ao registo que tem o texto em vigor? Só BM25 e referência, sem modelos."""
    sys.path.insert(0, str(raiz))
    from rag.pesquisa import Pesquisa  # noqa: PLC0415

    pesquisa = Pesquisa(indice)
    for linha in linhas:
        if not linha.get("pesquisa"):
            continue
        esperado = linha.get("vive_em")
        numero = "2.º"
        if esperado and (raiz / acervo.docs[esperado]["path"]).exists():
            lidas = partes((raiz / acervo.docs[esperado]["path"]).read_text(encoding="utf-8"))
            maior = lidas.get(linha.get("parte") or "") or max(lidas.values(), key=len, default={})
            numeros = [n for n in maior if n != "único" and "-" not in n]
            numero = numeros[len(numeros) // 2] if numeros else numero
        pergunta = f"artigo {numero} {linha['pesquisa']}"
        resultados = pesquisa.pesquisar(pergunta, k=3).resultados
        primeiro = resultados[0] if resultados else None
        registo_certo = bool(primeiro and esperado and primeiro.documento == esperado)
        certo = registo_certo and primeiro.numero == numero
        linha["pesquisa_resultado"] = {
            "pergunta": pergunta, "certo": certo, "registo_certo": registo_certo,
            "primeiro": None if primeiro is None else {"documento": primeiro.documento, "titulo": primeiro.titulo, "parte": primeiro.parte, "numero": primeiro.numero, "origem": primeiro.origem},
        }
        if not certo:
            veio = "nada" if primeiro is None else f"{primeiro.titulo}, {primeiro.parte or 'articulado'}, artigo {primeiro.numero}"
            linha["problemas"].append(f"«{pergunta}» {'chega ao registo certo mas a outro artigo' if registo_certo else 'não chega ao registo certo'} (veio: {veio})")


# ------------------------------------------------------------------ 7. fora do export


def contar_md(pasta: Path) -> int:
    return sum(1 for _ in pasta.rglob("*.md")) if pasta.exists() else 0


def fora_do_export(acervo: Acervo, raiz: Path, export: Path) -> dict:
    con = sqlite3.connect(f"file:{export}?mode=ro", uri=True)
    prefixos = dict(con.execute("SELECT substr(id, 1, instr(substr(id, 4), ':') + 3), count(*) FROM documentos GROUP BY 1"))
    con.close()
    acordos = Counter((d["series"] or "sem série", d["text_quality"]) for d in acervo.docs.values() if d["document_type"] == "acordo-coletivo-trabalho")
    return {
        "export_por_prefixo": prefixos,
        "cnpd_em_data": contar_md(raiz / "data" / "entidades" / "cnpd"),
        "tribunal_constitucional_em_data": contar_md(raiz / "data" / "jurisprudencia" / "tribunal-constitucional"),
        "acordos_coletivos": {f"{serie} / {texto}": n for (serie, texto), n in sorted(acordos.items())},
    }


# ------------------------------------------------------------------ resumo e tabelas


def _jsonl(caminho: Path, linhas: list[dict]) -> None:
    caminho.write_text("".join(json.dumps(linha, ensure_ascii=False, sort_keys=True) + "\n" for linha in linhas), encoding="utf-8")


def _tabela(cabecalho_: list[str], linhas: list[list]) -> str:
    numericas = [k > 0 and bool(linhas) and all(isinstance(l[k], int | float) or l[k] in ("", "—") for l in linhas) for k in range(len(cabecalho_))]
    saida = ["| " + " | ".join(cabecalho_) + " |", "|" + "|".join("--:" if n else "---" for n in numericas) + "|"]
    saida += ["| " + " | ".join(str(c).replace("|", "\\|") for c in linha) + " |" for linha in linhas]
    return "\n".join(saida)


ORDEM_TEXTO = ["consolidado_dre", "consolidado_leis_portugal", "texto_noutro_registo", "original_e_o_texto_em_vigor", "alteracao_por_aplicar",
               "alteracao_so_em_imagem", "nao_triado", "revogado_por_inteiro", "sem_texto"]
ORDEM_DESCONHECIDA = ["revogado_segundo_a_relacao_do_dre", "revogacao_lida_no_texto_de_outro_diploma", "temporario_ou_orcamental", "ato_de_alteracao",
                      "alterado_depois_e_sem_revogacao", "sem_indicio_de_revogacao"]
POR_FECHAR = ("alteracao_por_aplicar", "alteracao_so_em_imagem", "nao_triado", "revogado_por_inteiro")


def pedacos_no_indice(lista_obras: list[dict], indice: Path) -> None:
    """Quantos pedaços de cada cópia o índice dá como texto atual (`ate` vazio): é o que a pesquisa pode servir."""
    con = sqlite3.connect(f"file:{indice}?mode=ro", uri=True)
    for obra in lista_obras:
        for copia in obra["copias"]:
            parte = "" if copia["parte"].startswith("(") else copia["parte"]
            copia["pedacos_atuais_no_indice"] = con.execute(
                "SELECT count(*) FROM pedacos WHERE documento = ? AND parte = ? AND (ate IS NULL OR ate = '')", (copia["id"], parte)).fetchone()[0]
    con.close()


def resumo_das_obras(lista_obras: list[dict]) -> dict:
    vivas = [o for o in lista_obras if o["em_vigor"]]
    mortas = [o for o in lista_obras if not o["em_vigor"]]
    fora = [o for o in vivas if o["atual_fora_da_origem"]]

    def origem(o: dict) -> dict:
        return next(c for c in o["copias"] if c["papel"] == "origem" or c["id"] == o["origem"])

    return {
        "obras": len(lista_obras), "com_texto_atual_num_registo_em_vigor": len(vivas),
        "que_ja_nao_vigoram_com_copias_servidas": sum(any(c["servida_como_vigente"] for c in o["copias"]) for o in mortas),
        "copias_de_texto_que_ja_nao_vigora_servidas": sum(c["servida_como_vigente"] for o in mortas for c in o["copias"]),
        "artigos_em_copias_de_texto_que_ja_nao_vigora": sum(c["artigos"] for o in mortas for c in o["copias"] if c["servida_como_vigente"]),
        "texto_atual_fora_do_registo_de_origem": len(fora),
        "das_quais_a_origem_aponta_para_o_atual": sum(o["origem_ligada_ao_atual"] for o in fora),
        "das_quais_a_origem_esta_no_indice_como_vigente": sum(origem(o)["servida_como_vigente"] for o in fora),
        "das_quais_a_origem_tem_consolidacao_propria_mais_antiga": sum(origem(o)["consolidado_por"] is not None and origem(o)["desatualizada"] for o in fora),
        "das_quais_com_numeracao_diferente": sum(o["com_epigrafe"] >= 20 and o["epigrafes_iguais"] / o["com_epigrafe"] < 0.8 for o in fora),
        "copias_desatualizadas_servidas": sum(o["copias_desatualizadas_servidas"] for o in vivas),
        "artigos_em_copias_desatualizadas_servidas": sum(o["artigos_em_copias_desatualizadas_servidas"] for o in vivas),
        "obras_com_copias_desatualizadas_servidas": sum(o["copias_desatualizadas_servidas"] > 0 for o in vivas),
        "no_indice": None if not any("pedacos_atuais_no_indice" in c for o in lista_obras for c in o["copias"]) else {
            "copias_desatualizadas_com_pedacos_atuais": sum(c["desatualizada"] and c.get("pedacos_atuais_no_indice", 0) > 0 for o in vivas for c in o["copias"]),
            "pedacos_atuais_em_copias_desatualizadas": sum(c.get("pedacos_atuais_no_indice", 0) for o in vivas for c in o["copias"] if c["desatualizada"]),
            "pedacos_atuais_nas_copias_atuais": sum(c.get("pedacos_atuais_no_indice", 0) for o in vivas for c in o["copias"] if c["papel"] == "atual"),
            "pedacos_atuais_em_copias_de_texto_que_ja_nao_vigora": sum(c.get("pedacos_atuais_no_indice", 0) for o in mortas for c in o["copias"] if c["papel"] != "atual" and c["estado"] in VIGENTES),
        },
        "copias_desatualizadas_servidas_por_tipo_de_registo": dict(Counter(
            ("consolidado " + c["consolidado_por"] if c["consolidado_por"] else "original") + (" (anexo com «republica» no nome)" if "republica" in c["parte"].lower() else "")
            for o in vivas for c in o["copias"] if c["desatualizada"] and c["servida_como_vigente"])),
    }


def inventario(args: argparse.Namespace) -> dict:
    raiz, export = Path(args.raiz), Path(args.export)
    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)
    acervo = carregar(export)
    cabecalhos = {i: cabecalho(raiz / d["path"]) for i, d in acervo.docs.items() if d["version_kind"] == "consolidated" and (raiz / d["path"]).exists()}
    triagem_ficheiro = raiz / "consolidacao" / "resultados-escala.jsonl"
    triagem = {r["id"]: r for r in map(json.loads, triagem_ficheiro.read_text(encoding="utf-8").splitlines())} if triagem_ficheiro.exists() else {}
    propostas_ficheiro = raiz / "reports" / "vigencia-proposta.jsonl"
    propostas = {r["id"]: r for r in map(json.loads, propostas_ficheiro.read_text(encoding="utf-8").splitlines())} if propostas_ficheiro.exists() else {}
    marcas_ficheiro = raiz / "consolidacao" / "auditoria" / "vigencia-revista.jsonl"
    marcas = {r["id"]: r["marca"] for r in map(json.loads, marcas_ficheiro.read_text(encoding="utf-8").splitlines())} if marcas_ficheiro.exists() else {}

    sitemap = None
    if args.descarregar_sitemap:
        pedido = urllib.request.Request(SITEMAP_CONSOLIDADOS, headers={"User-Agent": "leis-portugal-inventario"})
        with urllib.request.urlopen(pedido, timeout=120) as resposta:  # noqa: S310 (endereço fixo do DRE)
            sitemap = ler_sitemap(resposta.read())
    elif args.sitemap_consolidados:
        sitemap = ler_sitemap(Path(args.sitemap_consolidados).read_bytes())

    resumo: dict = {"gerado": args.hoje, "export": {"documentos_pt": len(acervo.docs), "ficheiro": export.name}, "com_sitemap": sitemap is not None, "com_indice": bool(args.indice)}

    # 2 (antes do 1, que precisa de saber onde vive o texto)
    lista_obras = obras(acervo, cabecalhos, raiz, PRIORITARIOS + ("decreto",), args.hoje)
    if args.indice:
        pedacos_no_indice(lista_obras, Path(args.indice))
    _jsonl(saida / "texto-em-varios-registos.jsonl", lista_obras)
    resumo["texto_em_varios_registos"] = resumo_das_obras(lista_obras)

    # 1
    linhas_texto = texto_em_vigor(acervo, cabecalhos, lista_obras, triagem, sitemap, PRIORITARIOS, marcas)
    _jsonl(saida / "texto-em-vigor-por-fechar.jsonl", sorted((l for l in linhas_texto if l["classe"] in POR_FECHAR), key=lambda l: -l["citado_por_vigentes"]))
    _jsonl(saida / "consolidados-por-atualizar.jsonl", sorted((l for l in linhas_texto if l.get("em_dia") is False), key=lambda l: -l["citado_por_vigentes"]))
    portarias = texto_em_vigor(acervo, cabecalhos, lista_obras, triagem, sitemap, ("portaria",), marcas)
    nao_consolidado = lambda l: acervo.docs[l["id"]]["version_kind"] != "consolidated" and acervo.docs[l["id"]]["text_quality"] == "texto"  # noqa: E731
    resumo["texto_em_vigor"] = {
        "universo": len(linhas_texto),
        "por_classe_e_tipo": {c: {t: n for t in PRIORITARIOS if (n := sum(l["classe"] == c and l["tipo"] == t for l in linhas_texto))} for c in ORDEM_TEXTO},
        "por_classe": dict(Counter(l["classe"] for l in linhas_texto)),
        "por_classe_e_estado": {c: dict(Counter(l["estado"] for l in linhas_texto if l["classe"] == c)) for c in ORDEM_TEXTO},
        "por_fechar_citados": {f"≥{n}": sum(l["classe"] in POR_FECHAR[:3] and l["citado_por_vigentes"] >= n for l in linhas_texto) for n in (1, 10, 50)},
        "consolidados_em_dia": sum(l.get("em_dia") is True for l in linhas_texto),
        "consolidados_com_alterador_posterior": sum(bool(l.get("alteradores_posteriores")) for l in linhas_texto),
        "consolidados_dre_com_alterador_posterior": sum(bool(l.get("alteradores_posteriores")) and l["classe"] != "consolidado_leis_portugal" for l in linhas_texto),
        "consolidados_que_o_dre_mexeu": sum(bool(l.get("dre_mexeu_depois_da_recolha")) for l in linhas_texto),
        "originais_com_alterador_novo_desde_a_triagem": sum(l["classe"] == "original_e_o_texto_em_vigor" and bool(l.get("alteradores_novos_desde_a_triagem")) for l in linhas_texto),
        "marcas_de_vigencia_revista": {
            "no_ficheiro": dict(Counter(marcas.values())),
            "prioritarios": dict(Counter(l["marca_de_vigencia"] for l in linhas_texto if "marca_de_vigencia" in l)),
            "prioritarios_por_classe": {c: n for c in ORDEM_TEXTO if (n := dict(Counter(l["marca_de_vigencia"] for l in linhas_texto if l["classe"] == c and "marca_de_vigencia" in l)))},
            "portarias": dict(Counter(l["marca_de_vigencia"] for l in portarias if "marca_de_vigencia" in l)),
            "fora_do_universo": sum(i not in {l["id"] for l in linhas_texto} | {l["id"] for l in portarias} for i in marcas),
        },
        "portarias": {"universo": len(portarias), "por_classe": dict(Counter(l["classe"] for l in portarias)),
                      "consolidados_em_dia": sum(l.get("em_dia") is True for l in portarias), "consolidados_por_atualizar": sum(l.get("em_dia") is False for l in portarias)},
        "tetos_da_sessao_coordenadora": {
            t: {"teto": teto, "medido": sum(l["tipo"] == t and nao_consolidado(l) for l in linhas_texto),
                **{c: sum(l["tipo"] == t and nao_consolidado(l) and l["classe"] == c for l in linhas_texto) for c in ORDEM_TEXTO if c not in ("consolidado_dre", "consolidado_leis_portugal", "sem_texto")}}
            for t, teto in (("lei", 867), ("decreto-lei", 3494), ("decreto-regulamentar", 421))
        },
    }

    # 3
    desconhecidos = vigencia_desconhecida(acervo, propostas, PRIORITARIOS)
    _jsonl(saida / "vigencia-desconhecida.jsonl", sorted(desconhecidos, key=lambda l: -l["citado_por_vigentes"]))
    por_ano, total_por_ano = Counter(), Counter()
    for d in acervo.docs.values():
        if d["document_type"] in ("lei", "decreto-lei") and d["series"] == "I":
            ano = (d["publication_date"] or "0000")[:4]
            total_por_ano[ano] += 1
            por_ano[ano] += d["legal_status"] == "unknown"
    resumo["vigencia_desconhecida"] = {
        "total": len(desconhecidos),
        "por_tipo": dict(Counter(l["tipo"] for l in desconhecidos)),
        "com_texto": sum(l["texto"] == "texto" for l in desconhecidos),
        "por_classe": dict(Counter(l["classe"] for l in desconhecidos)),
        "por_classe_e_tipo": {c: dict(Counter(l["tipo"] for l in desconhecidos if l["classe"] == c)) for c in ORDEM_DESCONHECIDA},
        "de_2014_em_diante": sum((l["data"] or "") >= "2014" for l in desconhecidos),
        "com_amended_by": sum(l["alteradores"] > 0 for l in desconhecidos),
        "citados_por_vigentes": {f"≥{n}": sum(l["citado_por_vigentes"] >= n for l in desconhecidos) for n in (1, 10, 50)},
        "leis_e_decretos_leis_por_ano": {a: {"desconhecida": por_ano[a], "total": total_por_ano[a]} for a in sorted(total_por_ano) if por_ano[a] and a >= "2010"},
        "leis_e_decretos_leis_antes_de_2010": sum(n for a, n in por_ano.items() if a < "2010"),
        "todos_os_tipos_1a_serie": dict(Counter(d["document_type"] for d in acervo.docs.values() if d["series"] == "I" and d["legal_status"] == "unknown").most_common(12)),
    }

    # 4
    if sitemap is not None:
        nossos = {c["url_consolidado"]: {"id": i, "lastmod": c["lastmod"]} for i, c in cabecalhos.items() if c["url_consolidado"]}
        falhas_ficheiro = raiz / "reports" / "dre_consolidated_failures.jsonl"
        falhas = {json.loads(l)["url"] for l in falhas_ficheiro.read_text(encoding="utf-8").splitlines()} if falhas_ficheiro.exists() else set()
        comparacao = comparar_sitemap(sitemap, nossos, falhas)
        for m in comparacao["mexidos_depois_da_recolha"]:
            m |= {"titulo": acervo.docs[m["id"]]["title"], "tipo": acervo.docs[m["id"]]["document_type"], "sumario": (acervo.docs[m["id"]]["summary"] or "")[:120]}
        _jsonl(saida / "dre-consolidados-em-falta.jsonl", comparacao["em_falta"])
        _jsonl(saida / "dre-consolidados-mexidos.jsonl", comparacao["mexidos_depois_da_recolha"])
        resumo["dre_consolidados"] = {
            "listados_no_sitemap": comparacao["listados"], "temos": comparacao["temos"], "em_falta": len(comparacao["em_falta"]),
            "em_falta_por_motivo": dict(Counter(e["motivo"] for e in comparacao["em_falta"])),
            "por_recolher_por_tipo": dict(Counter(e["tipo"] for e in comparacao["em_falta"] if e["motivo"] == "por_recolher").most_common()),
            "por_recolher_prioritarios": sum(e["motivo"] == "por_recolher" and e["tipo"] in PRIORITARIOS for e in comparacao["em_falta"]),
            "sem_texto_na_fonte_prioritarios": sum(e["motivo"] == "sem_texto_na_fonte" and e["tipo"] in PRIORITARIOS for e in comparacao["em_falta"]),
            "mexidos_depois_da_recolha": len(comparacao["mexidos_depois_da_recolha"]),
            "mexidos_por_tipo": dict(Counter(m["tipo"] for m in comparacao["mexidos_depois_da_recolha"]).most_common()),
            "so_nossos": len(comparacao["so_nossos"]),
            "datas_de_recolha": dict(Counter(c["recolhido"] for c in cabecalhos.values() if c["url_consolidado"]).most_common(3)),
            "sitemap_lastmod_mais_recente": max(sitemap.values()),
        }

    # 5
    antigos = antigos_sem_texto(acervo, PRIORITARIOS + ("decreto", "carta-lei"))
    _jsonl(saida / "antigos-sem-texto-citados.jsonl", [a for a in antigos if a["estado"] != "unknown" and a["citado_por_vigentes"] >= 5])
    resumo["antigos_sem_texto"] = {
        "total": len(antigos),
        "por_tipo_estado_faixa": {f"{t} / {e} / {f}": n for (t, e, f), n in sorted(Counter((a["tipo"], a["estado"], a["faixa"]) for a in antigos).items())},
        "em_vigor_segundo_o_dre": {t: sum(a["tipo"] == t and a["estado"] != "unknown" for a in antigos) for t in ("lei", "decreto-lei", "decreto")},
        "em_vigor_e_citados": {f"≥{n}": sum(a["estado"] != "unknown" and a["citado_por_vigentes"] >= n for a in antigos) for n in (1, 5, 20, 100)},
        "em_vigor_com_amended_by": sum(a["estado"] != "unknown" and a["alteradores"] > 0 for a in antigos),
        "prioritarios_com_texto_antes_de_1960": sum((d["publication_date"] or "9999") < "1960" and d["text_quality"] == "texto" and d["document_type"] in PRIORITARIOS for d in acervo.docs.values()),
        "com_texto_antes_de_1960": sum((d["publication_date"] or "9999") < "1960" and d["text_quality"] == "texto" for d in acervo.docs.values()),
        "mais_citados": [{k: a[k] for k in ("titulo", "data", "citado_por_vigentes", "sumario")} for a in antigos if a["estado"] != "unknown"][:25],
    }

    # 6
    centrais = json.loads((Path(__file__).with_name("inventario_diplomas_centrais.json")).read_text(encoding="utf-8"))["diplomas"]
    controlo = lista_de_controlo(centrais, acervo, cabecalhos, lista_obras, triagem, sitemap, raiz, marcas)
    if args.indice:
        verificar_pesquisa(controlo, Path(args.indice), raiz, acervo)
    _jsonl(saida / "diplomas-centrais.jsonl", controlo)
    resumo["diplomas_centrais"] = {
        "total": len(controlo), "sem_problemas": sum(not l["problemas"] for l in controlo), "fora_do_acervo": sum(l["id"] is None for l in controlo),
        "por_texto": dict(Counter(l.get("texto", "fora do acervo") for l in controlo)),
        "com_vigencia_desconhecida": sum("vigência desconhecida" in l["problemas"] for l in controlo),
        "com_alterador_posterior": sum(bool(l.get("alteradores_posteriores")) for l in controlo),
        "que_o_dre_mexeu": sum(bool(l.get("dre_mexeu_depois_da_recolha")) for l in controlo),
        "texto_noutro_registo": sum(bool(l.get("vive_em")) and l["vive_em"] != l["id"] for l in controlo),
        "texto_noutro_registo_sem_ligacao": sum(bool(l.get("vive_em")) and l["vive_em"] != l["id"] and acervo.texto_em_vigor_em.get(l["id"]) != l["vive_em"] for l in controlo),
        "com_copias_de_outra_data_servidas": sum(any("cópia(s) com texto de outra data" in p for p in l["problemas"]) for l in controlo),
        "pesquisa": None if not args.indice else {"verificados": sum("pesquisa_resultado" in l for l in controlo), "artigo_certo": sum(l.get("pesquisa_resultado", {}).get("certo", False) for l in controlo),
                                                  "registo_certo_outro_artigo": sum(l.get("pesquisa_resultado", {}).get("registo_certo", False) and not l["pesquisa_resultado"]["certo"] for l in controlo),
                                                  "registo_errado": sum("pesquisa_resultado" in l and not l["pesquisa_resultado"]["registo_certo"] for l in controlo)},
    }

    # 7
    resumo["fora_do_export"] = fora_do_export(acervo, raiz, export)

    repetidos = duplicados(acervo, PRIORITARIOS)
    _jsonl(saida / "registos-duplicados.jsonl", repetidos)
    resumo["registos_duplicados"] = {
        "diplomas": len(repetidos),
        "com_um_consolidado_e_outro_original_vigente": sum(any(r["versao"] == "consolidated" for r in g["registos"]) and any(r["versao"] != "consolidated" and r["estado"] in VIGENTES for r in g["registos"]) for g in repetidos),
        "com_estados_diferentes": sum(len({r["estado"] for r in g["registos"]}) > 1 for g in repetidos),
    }

    (saida / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (saida / "tabelas.md").write_text(tabelas(resumo, controlo, lista_obras), encoding="utf-8")
    return resumo


def tabelas(resumo: dict, controlo: list[dict], lista_obras: list[dict]) -> str:
    t = resumo["texto_em_vigor"]
    blocos = [
        f"# Inventário da camada 1: tabelas geradas\n\nGerado a {resumo['gerado']} por `scripts/inventario_camada_1.py`, a partir de `{resumo['export']['ficheiro']}` "
        f"({resumo['export']['documentos_pt']} registos portugueses). Não editar à mão: a leitura está em `reports/inventario-camada-1.md`.",
        "## 1. Texto em vigor dos diplomas alterados\n\nPrioritários da 1.ª Série, em vigor ou de vigência desconhecida, com `amended_by`.\n\n"
        + _tabela(["Classe", *PRIORITARIOS, "Total"], [[c, *[t["por_classe_e_tipo"][c].get(tp, 0) for tp in PRIORITARIOS], sum(t["por_classe_e_tipo"][c].values())] for c in ORDEM_TEXTO if t["por_classe_e_tipo"][c]]
                  + [["**Total**", *[sum(t["por_classe_e_tipo"][c].get(tp, 0) for c in ORDEM_TEXTO) for tp in PRIORITARIOS], t["universo"]]])
        + f"\n\nConsolidados em dia: {t['consolidados_em_dia']}; com alterador publicado depois da última versão: {t['consolidados_com_alterador_posterior']}; "
        f"que o DRE mexeu depois da recolha: {t['consolidados_que_o_dre_mexeu'] if resumo['com_sitemap'] else 'por medir (sem sitemap)'}.\n\n"
        "Portarias (só contagens): " + ", ".join(f"{c} {n}" for c, n in sorted(t["portarias"]["por_classe"].items(), key=lambda x: -x[1])) + ".\n\n"
        "Marcas da vigência revista (`consolidacao/auditoria/vigencia-revista.jsonl`): no ficheiro, " + (", ".join(f"{m} {n}" for m, n in sorted(t["marcas_de_vigencia_revista"]["no_ficheiro"].items())) or "nenhuma")
        + "; nos prioritários deste universo, " + (", ".join(f"{m} {n}" for m, n in sorted(t["marcas_de_vigencia_revista"]["prioritarios"].items())) or "nenhuma")
        + "; nas portarias, " + (", ".join(f"{m} {n}" for m, n in sorted(t["marcas_de_vigencia_revista"]["portarias"].items())) or "nenhuma") + ".",
    ]
    fora = [o for o in lista_obras if o["atual_fora_da_origem"] and o["em_vigor"]]
    blocos.append(f"## 2. Textos cujo texto em vigor está fora do registo que os aprovou ({len(fora)})\n\n" + _tabela(
        ["Texto de (origem)", "Texto mais recente em", "Parte", "Artigos", "Texto até", "Origem aponta para lá", "Origem servida como em vigor", "Epígrafes iguais (mesmo n.º)", "Outras cópias desatualizadas servidas"],
        [[o["origem_titulo"], o["atual_titulo"], (o["atual_parte"] or "articulado")[:60], next(c["artigos"] for c in o["copias"] if c["papel"] == "atual"), o["data_do_texto_atual"],
          "sim" if o["origem_ligada_ao_atual"] else "**não**",
          next(("sim, consolidação de " + c["data_do_texto"] if c["consolidado_por"] else "sim, texto de " + c["data_do_texto"]) if c["servida_como_vigente"] else "não" for c in o["copias"] if c["id"] == o["origem"]),
          f"{o['epigrafes_iguais']}/{o['com_epigrafe']}" if o["com_epigrafe"] else "sem epígrafes",
          "; ".join(f"{c['titulo']} ({c['data_do_texto']})" for c in o["copias"] if c["desatualizada"] and c["servida_como_vigente"] and c["id"] != o["origem"]) or "—"] for o in fora]))
    copias = [(o, c) for o in lista_obras for c in o["copias"] if c["desatualizada"] and c["servida_como_vigente"] and not (o["atual_fora_da_origem"] and c["id"] == o["origem"])]
    mortas = [(o, c) for o in lista_obras if not o["em_vigor"] for c in o["copias"] if c["servida_como_vigente"]]
    copias.sort(key=lambda oc: -oc[1]["artigos"])
    blocos.append(f"## 2-B. Cópias com texto de outra data, em registos em vigor ({len(copias)}; as 60 maiores)\n\n" + _tabela(
        ["Texto", "Cópia em", "Parte", "Artigos", "Texto da cópia até", "Texto atual em", "Texto atual até"],
        [[o["obra"][:60], c["titulo"], (c["parte"] or "articulado")[:50], c["artigos"], c["data_do_texto"], o["atual_titulo"], o["data_do_texto_atual"]] for o, c in copias[:60]]))
    blocos.append(f"## 2-C. Cópias, em registos em vigor, de textos cujo registo mais recente já não vigora ({len(mortas)})\n\n" + _tabela(
        ["Texto", "Cópia em", "Parte", "Artigos", "Texto da cópia até", "Registo mais recente", "Estado desse registo"],
        [[o["obra"][:60], c["titulo"], (c["parte"] or "articulado")[:50], c["artigos"], c["data_do_texto"], o["atual_titulo"], next(x["estado"] for x in o["copias"] if x["papel"] == "atual")]
         for o, c in sorted(mortas, key=lambda oc: -oc[1]["artigos"])]))
    v = resumo["vigencia_desconhecida"]
    blocos.append("## 3. Vigência desconhecida (prioritários, 1.ª Série)\n\n" + _tabela(
        ["Classe", *PRIORITARIOS, "Total"],
        [[c, *[v["por_classe_e_tipo"][c].get(tp, 0) for tp in PRIORITARIOS], sum(v["por_classe_e_tipo"][c].values())] for c in ORDEM_DESCONHECIDA if v["por_classe_e_tipo"][c]]
        + [["**Total**", *[v["por_tipo"].get(tp, 0) for tp in PRIORITARIOS], v["total"]]]))
    blocos.append("Leis e decretos-leis de vigência desconhecida por ano de publicação (desde 2010):\n\n" + _tabela(
        ["Ano", "Desconhecida", "Publicados", "%"], [[a, n["desconhecida"], n["total"], round(100 * n["desconhecida"] / n["total"])] for a, n in v["leis_e_decretos_leis_por_ano"].items()]))
    blocos.append("## 6. Lista de controlo dos diplomas centrais\n\n" + _tabela(
        ["Área", "Diploma", "Aprovado por", "Texto em vigor em", "Vigência", "Texto até", "Em dia", "Problemas"],
        [[l["area"], l["nome"], l["diploma"],
          (l.get("vive_em_titulo") or "—") + (f", {l['parte'][:40]}" if l.get("parte") else "") + (f" ({l['texto'].replace('consolidado_', '').replace('_', ' ')})" if l.get("texto") else ""),
          l.get("estado", "—"), l.get("consolidado_ate") or "—", "—" if "em_dia" not in l else "sim" if l["em_dia"] else "**não**", "; ".join(l["problemas"]) or "—"] for l in controlo]))
    return "\n\n".join(blocos) + "\n"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--raiz", default=str(RAIZ), help="raiz do repositório (com data/)")
    parser.add_argument("--export", default=None, help="exports/leis-portugal.sqlite (por omissão, o desta cópia ou o da pasta principal)")
    parser.add_argument("--saida", default=None, help="pasta de saída (por omissão, reports/inventario-camada-1)")
    parser.add_argument("--sitemap-consolidados", default=None, help="ficheiro com o sitemap da legislação consolidada do DRE")
    parser.add_argument("--descarregar-sitemap", action="store_true", help=f"descarrega {SITEMAP_CONSOLIDADOS}")
    parser.add_argument("--indice", default=None, help="índice do RAG, para verificar «artigo N.º do Código X» (só leitura)")
    parser.add_argument("--hoje", default=date.today().isoformat())
    args = parser.parse_args(argv)
    args.export = args.export or str(export_por_omissao(Path(args.raiz)))
    args.saida = args.saida or str(Path(args.raiz) / "reports" / "inventario-camada-1")
    resumo = inventario(args)
    print(json.dumps({k: v for k, v in resumo.items() if k in ("texto_em_varios_registos", "diplomas_centrais", "dre_consolidados")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
