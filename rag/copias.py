"""Cópias do mesmo texto em vários registos, e quais são redação anterior.

O DRE consolida alguns códigos no registo da lei que os republicou (o Código da Estrada na Lei n.º 72/2013),
consolida também diplomas de alteração que trazem a republicação de outro (o DL 44/2005) e guarda o
texto de origem (o DL 114/94). No índice, todas essas cópias ficavam como texto atual.

Este módulo junta as cópias de cada texto (`obras`) e diz quais são redação anterior (`redacoes_anteriores`).
Só lê o export e o `data/`. O `rag.indice` usa as marcas ao construir: os pedaços de uma cópia marcada ficam
com `ate` (a data em que há prova de um texto mais recente), como qualquer redação antiga de um consolidado.
Nada se apaga: o texto continua no índice e responde a perguntas com data anterior, com o aviso «Redação em
vigor de … a …, não a atual».

**A prova.** Uma cópia só é marcada quando as duas coisas estão provadas:

1. *É o mesmo texto* (`mesma_obra`): as epígrafes coincidem, ou o DRE o diz numa nota, ou o anexo cita o diploma.
2. *Há outra cópia mais recente*: outra cópia tem uma nota «Alterado pelo/a…» com data posterior à desta
   (nos artigos comuns, quando a numeração é a mesma), ou é a republicação trazida por um diploma que o DRE
   regista como alterador deste texto e publicado depois. Uma data de publicação diferente não chega.

O que não tem prova, ou não se consegue marcar sem apanhar o articulado do próprio diploma, fica de fora, com o
motivo (`fora`). Um texto em vigor marcado como antigo é pior do que uma cópia antiga por marcar.

Uso: `python -m rag.copias` grava `reports/redacoes-anteriores/` (marcadas, de fora e resumo).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

import yaml

from rag.fontes import RAIZ, corpo, ler_artigos


PRIORITARIOS = ("lei", "lei-organica", "lei-constitucional", "decreto-lei", "decreto-regulamentar", "decreto-legislativo-regional")
VIGENTES = ("in_force", "partially_in_force", "unknown")
ETIQUETA_TEXTO_EM_VIGOR = "Texto em vigor"  # início da etiqueta de `republished_by` que o índice lê
ANEXO_MINIMO = 10  # artigos para uma parte contar como «um texto dentro de um diploma»
_YAML = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


# ------------------------------------------------------------------ leitura do export e dos registos


@dataclass
class Acervo:
    docs: dict[str, dict]
    alterado_por: dict[str, list[tuple[str | None, str | None, str | None]]]
    revogado_por: dict[str, list[tuple[str | None, str | None, str | None]]]
    texto_em_vigor_em: dict[str, str]
    altera: dict[str, set[str]]  # alterador -> diplomas com `amended_by` para ele
    citado_por_vigentes: Counter = field(default_factory=Counter)
    por_titulo: dict[str, list[str]] = field(default_factory=dict)


def carregar(export: Path, *, com_citacoes: bool = True) -> Acervo:
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
    if com_citacoes:
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
    """O que é preciso do front matter de um registo consolidado."""
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


def cabecalhos_dos_consolidados(acervo: Acervo, raiz: Path) -> dict[str, dict]:
    return {i: cabecalho(raiz / d["path"]) for i, d in acervo.docs.items() if d["version_kind"] == "consolidated" and (raiz / d["path"]).exists()}


def do_dre(rotulo: str) -> bool:
    return rotulo.startswith("Versão consolidada pelo DRE")


# ------------------------------------------------------------------ partes e artigos

_ARTIGO_CORRIDO = re.compile(r"^(?:Artigo|ARTIGO|Art\.) +(\d+)\.[ºo°](-[A-Z])?(?=[ .]|$)")
_DATA = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


@dataclass
class Parte:
    """Um articulado seguido de um registo: o do próprio diploma («») ou o de um anexo.

    Quando a numeração recomeça em «1.º» dentro da mesma parte do índice (o decreto e, logo a seguir, o código
    que ele aprova), cada numeração é uma `Parte`: `parte_no_indice` é a mesma e `numeracao` conta-as."""

    artigos: dict[str, str] = field(default_factory=dict)  # número → epígrafe
    notas: dict[str, list[tuple[str, str]]] = field(default_factory=dict)  # número → [(data, texto da nota)]
    textos: dict[str, str] = field(default_factory=dict)  # número → impressão do texto do artigo (`impressao`)
    ultima_nota: str | None = None  # a data mais recente nas notas «> Alterado pelo/a …» desta parte
    notas_dessa_data: str = ""  # o texto das notas com essa data: diz que diploma fez a última alteração
    parte_no_indice: str = ""
    numeracao: int = 1
    numeracoes: int = 1  # quantas numerações tem a parte do índice
    corrido: bool = False  # sem títulos de artigo: o índice guarda blocos de texto, não artigos
    inicio: str = ""  # nos corridos, o início da primeira linha e da seguinte, para achar o bloco onde a numeração começa


def impressao(texto: str) -> str:
    """Impressão do texto de um artigo: igual em duas cópias quando as letras são as mesmas.

    Sem maiúsculas, acentos, pontuação nem espaços, e sem as consoantes mudas que o Acordo Ortográfico tirou
    («acção» e «ação», «contra-ordenação» e «contraordenação»): uma republicação de 2013 escreve de outra maneira
    o texto que não mudou desde 2005."""
    return hashlib.sha1(re.sub(r"[cp](?=[ct])", "", simples(texto).replace(" ", "")).encode()).hexdigest()[:16]


def _nome(parte: str, numeracao: int) -> str:
    return parte if numeracao == 1 else f"{parte} ({numeracao}.ª numeração)".strip()


def ler_partes(markdown: str, hoje: str = "9999") -> dict[str, Parte]:
    """Nome da parte → artigos, datas das notas e posição no índice.

    Os artigos são os do leitor do índice (`rag.fontes.ler_artigos`), para as partes e os números serem os dos
    pedaços. Um registo sem títulos de artigo (texto corrido) é lido pelas linhas «Artigo N.º …», sem epígrafes.
    Em cada nota conta a última data da linha: a da entrada em vigor, ou a da publicação quando só há essa; uma
    data posterior a `hoje` ainda não é o texto.
    """
    texto = corpo(markdown)
    resultado: dict[str, Parte] = {}
    numeracao: dict[str, int] = defaultdict(lambda: 1)

    def parte_de(parte: str, numero: str, **extra) -> Parte:
        atual = resultado.get(_nome(parte, numeracao[parte]))
        if atual is not None and numero == "1.º" and "1.º" in atual.artigos:
            numeracao[parte] += 1
        nome = _nome(parte, numeracao[parte])
        if nome not in resultado:
            resultado[nome] = Parte(parte_no_indice=parte, numeracao=numeracao[parte], **extra)
        return resultado[nome]

    artigos = ler_artigos(texto)
    for artigo in artigos:
        parte = parte_de(artigo.parte, artigo.numero)
        if artigo.numero not in parte.artigos:
            parte.artigos[artigo.numero] = artigo.epigrafe
            parte.textos[artigo.numero] = impressao(artigo.texto)
        for nota in artigo.notas:
            datas = [d for d in _DATA.findall(nota) if d <= hoje]
            if not datas:
                continue
            parte.notas.setdefault(artigo.numero, []).append((datas[-1], nota))
            if (parte.ultima_nota or "") < datas[-1]:
                parte.ultima_nota, parte.notas_dessa_data = datas[-1], nota
            elif parte.ultima_nota == datas[-1]:
                parte.notas_dessa_data += "\n" + nota
    if not artigos:
        linhas = [" ".join(linha.split()) for linha in texto.splitlines()]
        for k, linha in enumerate(linhas):
            m = _ARTIGO_CORRIDO.match(linha)
            if m:
                numero = f"{int(m.group(1))}.º{m.group(2) or ''}"
                seguinte = next((outra for outra in linhas[k + 1 : k + 6] if outra), "")
                parte_de("", numero, corrido=True, inicio=f"{linha[:80]}\n{seguinte[:60]}").artigos.setdefault(numero, "")
    for parte in resultado.values():
        parte.numeracoes = numeracao[parte.parte_no_indice]
    return resultado


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


def epigrafes_em_comum(a: dict[str, str], b: dict[str, str]) -> tuple[int, float]:
    """Epígrafes diferentes da parte mais pequena e a fração delas que existe na outra, seja qual for o número.

    Resiste à renumeração: o Código da Estrada de 1994 e o de 2013 têm os mesmos temas com outros números."""
    de_a, de_b = {simples(e) for e in a.values() if e}, {simples(e) for e in b.values() if e}
    menor, maior = (de_a, de_b) if len(de_a) <= len(de_b) else (de_b, de_a)
    return len(menor), round(len(menor & maior) / len(menor), 3) if menor else 0.0


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
    r"(?: n\.?\s?º)? ?(\d+(?:-[A-Z])?/\d{2,4}(?:/[AM])?|\d{4,5})(?![\d/])",
    re.I,
)
_TIPOS_DE_REFERENCIA = {t.lower(): t for t in ("Decreto Legislativo Regional", "Decreto Regulamentar Regional", "Decreto Regulamentar", "Decreto-Lei", "Lei Orgânica", "Lei", "Decreto")}


def referencias(texto: str) -> list[str]:
    """Os títulos de diplomas citados num texto, na forma do acervo («Decreto-Lei n.º 114/94»)."""
    texto = re.sub(r"<[^>]+>", " ", texto)
    return list(dict.fromkeys(f"{_TIPOS_DE_REFERENCIA[tipo.lower()]} n.º {numero.upper()}" for tipo, numero in _REFERENCIA.findall(texto)))


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


TEXTOS_IGUAIS = 0.3  # fração mínima de artigos com o mesmo texto para duas partes serem cópias, sem ligação explícita
TEXTOS_IGUAIS_CODIGO = 0.1  # o mesmo, quando 30 ou mais epígrafes coincidem


def textos_iguais(a: Parte, b: Parte, *, por_epigrafe: bool = False) -> tuple[int, float]:
    """(artigos comparáveis, fração com o mesmo texto). Comparam-se os artigos com o mesmo número ou, numa
    republicação renumerada, os que têm a mesma epígrafe (só as epígrafes que não se repetem).

    Uma republicação partilha com as outras cópias o texto dos artigos que não mudaram; um regime paralelo com as
    mesmas epígrafes («Objeto», «Âmbito») não."""
    if por_epigrafe:
        def unicas(p: Parte) -> dict[str, str]:
            conta = Counter(simples(e) for e in p.artigos.values() if e)
            return {simples(e): p.textos.get(n, "") for n, e in p.artigos.items() if e and conta[simples(e)] == 1}
        de_a, de_b = unicas(a), unicas(b)
    else:
        de_a, de_b = a.textos, b.textos
    comuns = [k for k in de_a if k in de_b and de_a[k] and de_b[k]]
    return len(comuns), round(sum(de_a[k] == de_b[k] for k in comuns) / len(comuns), 3) if comuns else 0.0


def mesmo_texto(a: Parte, b: Parte) -> bool:
    """As duas partes são cópias do mesmo texto, só pelo que têm escrito: epígrafes e texto dos artigos.

    - Com a mesma numeração: 60 % dos números em comum e 70 % de pelo menos 8 epígrafes iguais.
    - Renumerada: tamanhos parecidos e 60 % de pelo menos 30 epígrafes diferentes em comum.

    E, nos dois casos, artigos com o mesmo texto: 30 % de pelo menos 8, ou 10 % quando há 30 ou mais epígrafes a
    coincidir (na renumerada, pelo menos 8 artigos iguais). Entre duas republicações de um código grande, afastadas vários anos, poucos artigos ficam iguais
    (as coimas passaram a euros, por exemplo), mas 150 epígrafes iguais já não são coincidência."""
    medida = sobreposicao(a.artigos, b.artigos)
    if medida["fracao_numeros"] >= 0.6 and medida["com_epigrafe"] >= 8 and medida["fracao_epigrafes"] >= 0.7:
        quantos, fracao = textos_iguais(a, b)
        if quantos >= 8 and fracao >= (TEXTOS_IGUAIS_CODIGO if medida["epigrafes_iguais"] >= 30 else TEXTOS_IGUAIS):
            return True
    if mesma_obra_renumerada(a.artigos, b.artigos):
        quantos, fracao = textos_iguais(a, b, por_epigrafe=True)
        return fracao >= TEXTOS_IGUAIS_CODIGO and round(quantos * fracao) >= 8
    return False


def copia_evidente(a: Parte, b: Parte) -> bool:
    """Cópia que dispensa a citação: a mesma numeração, 70 % das epígrafes iguais e 60 % de pelo menos 20 artigos
    com o mesmo texto (os anexos «a que se refere o artigo 12.º» da Lei n.º 118/2019, que republicam o CPPT e o
    CPTA sem os nomear no sumário)."""
    medida = sobreposicao(a.artigos, b.artigos)
    if medida["fracao_numeros"] < 0.6 or medida["com_epigrafe"] < 8 or medida["fracao_epigrafes"] < 0.7:
        return False
    quantos, fracao = textos_iguais(a, b)
    return quantos >= 20 and fracao >= 0.6


def mesma_obra_renumerada(a: dict[str, str], b: dict[str, str]) -> bool:
    """Uma republicação com outra numeração: tamanhos parecidos e 60 % de pelo menos 30 epígrafes diferentes em comum."""
    if min(len(a), len(b)) < 0.5 * max(len(a), len(b)):
        return False
    quantas, fracao = epigrafes_em_comum(a, b)
    return quantas >= 30 and fracao >= 0.6


# ------------------------------------------------------------------ o mesmo texto em vários registos


def citam_se(acervo: Acervo, a: tuple[str, str], b: tuple[str, str]) -> bool:
    """Dois registos (id, nome da parte) falam um do outro: o sumário ou o nome do anexo de um cita o título do
    outro, ou o nome do anexo de um («Código do IRS») está no sumário do outro.

    Sem isto, dois diplomas feitos pelo mesmo molde (os orçamentos de dois anos) passavam por cópias um do outro."""
    for (i, nome_i), (j, _) in ((a, b), (b, a)):
        de_i, de_j = acervo.docs[i], acervo.docs[j]
        if de_j["title"] in referencias(f"{de_i['summary'] or ''} {nome_i}") or de_i["title"] == de_j["title"]:
            return True
        if nome_i and not nome_i.startswith("(") and nome_contido(nome_i, de_j["summary"] or "") >= 0.8:
            return True
    return False


class _Leitor:
    """As partes de cada registo, lidas uma vez."""

    def __init__(self, acervo: Acervo, raiz: Path, hoje: str):
        self.acervo, self.raiz, self.hoje = acervo, raiz, hoje
        self.lidas: dict[str, dict[str, Parte]] = {}

    def __call__(self, i: str) -> dict[str, Parte]:
        if i not in self.lidas:
            doc = self.acervo.docs[i]
            caminho = self.raiz / doc["path"]
            self.lidas[i] = ler_partes(caminho.read_text(encoding="utf-8"), self.hoje) if doc["text_quality"] == "texto" and caminho.exists() else {}
        return self.lidas[i]


def obras(acervo: Acervo, cabecalhos: dict[str, dict], raiz: Path, tipos: tuple[str, ...], hoje: str = "9999", *, leitor: _Leitor | None = None) -> list[dict]:
    """Os textos que existem em mais de um registo: um código, as leis que o republicaram e o diploma que o aprovou.

    1. Parte de cada consolidado do DRE com um anexo de 10 ou mais artigos (ou com uma nota a dizer que tem por
       base uma republicação) e procura o mesmo texto nos diplomas que ele altera, cita no sumário, nas notas ou
       no nome do anexo (`mesma_obra`).
    2. Alarga cada grupo aos diplomas que alteram ou são alterados por um registo do grupo e que trazem o mesmo
       texto no articulado ou num anexo, pelas epígrafes (as republicações de 1998, 2001 e 2005 do Código da Estrada).

    Cada grupo de partes ligadas é uma obra, com as suas cópias:

    - `origem`: a cópia no registo mais antigo (o diploma que aprovou o texto);
    - `atual`: a cópia com a data de texto mais recente; se o registo dela já não vigora, a obra não está em vigor
      e as cópias que ficaram em registos em vigor são texto revogado servido como atual;
    - `data_do_texto` de uma cópia: a última nota de alteração dessa parte ou, sem notas, a publicação do registo;
    - `desatualizada`: a cópia tem data de texto anterior à da atual, a não ser que seja a republicação que fez a
      última alteração (o texto é o mesmo). É uma comparação de datas, não de textos: a prova está em `redacoes_anteriores`.
    """
    partes_de = leitor or _Leitor(acervo, raiz, hoje)
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
        com_nota = bool(re.search(r"republica", " ".join(map(str, cab["notas"])), re.I))
        todas = partes_de(i)
        # Do articulado do próprio diploma só conta a maior numeração: as outras são os artigos do decreto que aprova ou republica.
        maior_do_articulado = max((p for p, v in todas.items() if not v.parte_no_indice), key=lambda p: len(todas[p].artigos), default=None)
        minhas = {p: v for p, v in todas.items() if len(v.artigos) >= ANEXO_MINIMO and (v.parte_no_indice or (com_nota and p == maior_do_articulado))}
        if not minhas:
            continue
        nas_notas = {c for titulo in aprovados_nas_notas(cab["notas"]) for c in acervo.por_titulo.get(titulo, ())}
        candidatos = set(republica[i]) | set(acervo.altera.get(i, ())) | nas_notas
        for titulo in referencias(" ".join([doc["summary"] or "", *minhas])):
            candidatos.update(acervo.por_titulo.get(titulo, ()))
        candidatos = {c for c in candidatos if c != i and (acervo.docs[c]["publication_date"] or "") < (doc["publication_date"] or "")}
        ligados: set[str] = set()
        for nome, parte in sorted(minhas.items(), key=lambda x: not x[1].parte_no_indice):  # os anexos primeiro, o articulado no fim
            no_articulado = not parte.parte_no_indice
            for c in candidatos:
                if no_articulado and c in ligados:
                    continue  # o texto já foi encontrado num anexo: o articulado é o da lei que republica
                alvo = acervo.docs[c]
                explicito = c in republica[i] or c in nas_notas or alvo["title"] in referencias(nome)
                if no_articulado and not explicito:
                    continue  # o articulado do próprio diploma só se compara com o que uma nota do DRE indica
                for nome_c, parte_c in partes_de(c).items():
                    if len(parte_c.artigos) < ANEXO_MINIMO:
                        continue
                    medida = sobreposicao(parte.artigos, parte_c.artigos)
                    contido = nome_contido(nome, f"{alvo['summary'] or ''} {nome_c}") if not no_articulado else 0.0
                    revoga = any(alvo_r == i for alvo_r, _, _ in acervo.revogado_por.get(c, ()))
                    altera = c in acervo.altera.get(i, ())
                    if explicito or (medida["com_epigrafe"] < 8 and contido >= 0.8):
                        aceite = mesma_obra(medida, len(parte.artigos), len(parte_c.artigos), explicito=explicito, nome=contido, altera=altera, revoga=revoga, no_articulado=no_articulado)
                    else:
                        aceite = mesmo_texto(parte, parte_c) and (citam_se(acervo, (i, nome), (c, nome_c)) or copia_evidente(parte, parte_c))
                    if aceite:
                        pai[raiz_de((i, nome))] = raiz_de((c, nome_c))
                        ligados.add(c)
        # A nota do DRE basta: um original em texto corrido que o leitor não parte em artigos liga-se pela maior parte.
        for c in sorted(nas_notas & candidatos - ligados):
            minha = max(minhas, key=lambda p: len(minhas[p].artigos))
            if not partes_de(c):
                partes_de.lidas[c][""] = Parte(corrido=True)
            dele = max(partes_de(c), key=lambda p: len(partes_de(c)[p].artigos))
            pai[raiz_de((i, minha))] = raiz_de((c, dele))

    # 2. Os alteradores e os alterados que trazem o mesmo texto. Cada consolidado entra também sozinho, para se
    # verem as republicações dele em diplomas de alteração que o DRE não consolida (a Lei n.º 129/2015).
    for i in sorted(cabecalhos):
        if acervo.docs[i]["document_type"] in tipos:
            for nome, parte in partes_de(i).items():
                if len(parte.artigos) >= ANEXO_MINIMO:
                    raiz_de((i, nome))
    for _ in range(3):
        grupos: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
        for no in list(pai):
            grupos[raiz_de(no)].append(no)
        novos = 0
        for nos in grupos.values():
            registos = {i for i, _ in nos}
            vizinhos = {a for i in registos for a, _, _ in acervo.alterado_por.get(i, ()) if a} | {a for i in registos for a in acervo.altera.get(i, ())}
            for c in sorted(vizinhos - registos):
                if c not in acervo.docs or acervo.docs[c]["document_type"] not in tipos:
                    continue
                for nome_c, parte_c in partes_de(c).items():
                    if len(parte_c.artigos) < ANEXO_MINIMO or raiz_de((c, nome_c)) == raiz_de(nos[0]):
                        continue
                    modelos = [partes_de(i)[nome] for i, nome in nos if len(partes_de(i)[nome].artigos) >= ANEXO_MINIMO]
                    if any(mesmo_texto(parte_c, m) for m in modelos) and (any(citam_se(acervo, (c, nome_c), no) for no in nos) or any(copia_evidente(parte_c, m) for m in modelos)):
                        pai[raiz_de((c, nome_c))] = raiz_de(nos[0])
                        novos += 1
        if not novos:
            break

    grupos = defaultdict(list)
    for no in list(pai):
        grupos[raiz_de(no)].append(no)
    resultado = []
    for nos in grupos.values():
        if len(nos) < 2:
            continue
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
        nomes = [c["parte"] for c in copias if c["parte"] and not c["parte"].startswith("(")]
        resultado.append({
            "obra": max(nomes, key=len, default="") or origem["sumario"][:80],
            "origem": origem["id"], "origem_titulo": origem["titulo"], "atual": atual["id"], "atual_titulo": atual["titulo"], "atual_parte": atual["parte"],
            "data_do_texto_atual": atual["data_do_texto"], "atual_fora_da_origem": atual["id"] != origem["id"], "em_vigor": atual["estado"] in VIGENTES,
            "origem_ligada_ao_atual": acervo.texto_em_vigor_em.get(origem["id"]) == atual["id"],
            "numeros_comuns_origem_atual": medida["comuns"], "com_epigrafe": medida["com_epigrafe"], "epigrafes_iguais": medida["epigrafes_iguais"],
            "copias_desatualizadas_servidas": sum(c["desatualizada"] and c["servida_como_vigente"] for c in copias),
            "artigos_em_copias_desatualizadas_servidas": sum(c["artigos"] for c in copias if c["desatualizada"] and c["servida_como_vigente"]),
            "copias": copias,
        })
    return sorted(resultado, key=lambda o: (-max(c["artigos"] for c in o["copias"]), o["origem"]))


# ------------------------------------------------------------------ a regra: redações anteriores com prova


@dataclass(frozen=True)
class Marca:
    """Uma cópia que é redação anterior: os pedaços abertos desta parte ficam com `ate`."""

    documento: str
    parte: str  # a parte no índice
    artigos: frozenset[tuple[str, str]] | None  # (chave do pedaço, impressão do texto) dos artigos da cópia; None nos registos em blocos
    a_partir_de: str | None  # registos em blocos de texto: a linha onde o texto começa e a seguinte
    ate: str
    alvo: str  # o registo com o texto mais recente
    alvo_parte: str
    prova: str


def _prova(copia: dict, parte: Parte, outras: list[tuple[dict, Parte]], alteradores: set[str]) -> tuple[str, str] | None:
    """(data, descrição) da prova mais antiga de que existe um texto posterior ao desta cópia, ou None.

    Uma nota que cita o diploma da própria cópia não conta: é a alteração que essa cópia já traz."""
    desde = copia["data_do_texto"]
    proprio = re.compile(re.escape(copia["titulo"]) + r"(?![\d/-])")
    provas: list[tuple[str, str]] = []
    for outra, parte_o in outras:
        medida = sobreposicao(parte.artigos, parte_o.artigos)
        alinhadas = medida["com_epigrafe"] >= 8 and medida["fracao_epigrafes"] >= 0.7
        datas = [quando for n in (parte.artigos if alinhadas else parte_o.notas) for quando, nota in parte_o.notas.get(n, ()) if quando > desde and not proprio.search(nota)]
        if datas:
            provas.append((min(datas), f"{outra['titulo']} tem alterações a {'estes artigos' if alinhadas else 'este texto'} desde {min(datas)}"))
        # Um consolidado que já cita esse diploma nas notas já tem as alterações dele: não é mais antigo.
        ja_incluido = any(re.search(re.escape(outra["titulo"]) + r"(?![\d/-])", nota) for notas in parte.notas.values() for _, nota in notas)
        if outra["id"] in alteradores and (outra["publicado"] or "") > desde and not ja_incluido:
            provas.append((outra["publicado"], f"{outra['titulo']}, que o DRE regista como alterador deste texto, republicou-o a {outra['publicado']}"))
    return min(provas) if provas else None


_DE_ALTERACAO = re.compile(r"^(?:alterac|aditamento|republicac)")


def artigos_da_copia(parte: Parte, posteriores: list[Parte]) -> dict[str, str] | None:
    """Os artigos a fechar numa cópia (número → impressão do texto), ou None se a parte mistura o texto com o
    articulado de um diploma de alteração.

    Num anexo ou numa segunda numeração, a cópia é a parte inteira. No articulado principal de um diploma pode
    estar a cópia (o DL 44/2005 é o Código da Estrada) ou o diploma de alteração com os artigos que ele cita, com
    as mesmas chaves. Distingue-os um artigo «Alteração ao…», «Aditamento…» ou «Republicação» que nenhuma cópia
    posterior tem: é do diploma de alteração, e a parte fica de fora."""
    if parte.parte_no_indice or parte.numeracao > 1:
        return dict(parte.textos)
    das_posteriores = {simples(e) for p in posteriores for e in p.artigos.values() if e}
    if any(_DE_ALTERACAO.match(simples(e)) and simples(e) not in das_posteriores for e in parte.artigos.values() if e):
        return None
    return dict(parte.textos)


def redacoes_anteriores(acervo: Acervo, cabecalhos: dict[str, dict], raiz: Path, hoje: str, tipos: tuple[str, ...] = (*PRIORITARIOS, "decreto"),
                        lista_obras: list[dict] | None = None, leitor: _Leitor | None = None) -> tuple[list[Marca], list[dict]]:
    """As cópias a marcar como redação anterior e as que ficam de fora, com o motivo.

    Cada cópia das `obras` leva `regra`: `marcada`, `atual` ou o motivo por que ficou de fora."""
    partes_de = leitor or _Leitor(acervo, raiz, hoje)
    if lista_obras is None:
        lista_obras = obras(acervo, cabecalhos, raiz, tipos, hoje, leitor=partes_de)
    marcas: list[Marca] = []
    fora: list[dict] = []
    for obra in lista_obras:
        copias = obra["copias"]
        atual = next(c for c in copias if c["papel"] == "atual")
        alteradores = {a for c in copias for a, _, _ in acervo.alterado_por.get(c["id"], ()) if a}
        com_partes = [(c, partes_de(c["id"])[c["parte"]]) for c in copias]
        for copia, parte in com_partes:
            if copia is atual:
                copia["regra"] = "atual"
                continue
            motivo = None
            prova = None
            if not obra["em_vigor"]:
                motivo = "o registo com o texto mais recente já não vigora: a regra não decide se o texto vigora"
            elif copia["texto"] != "texto":
                motivo = "sem texto no índice"
            elif len(parte.artigos) < ANEXO_MINIMO:
                motivo = "o leitor não parte este registo em artigos: não se sabe onde está o texto nos blocos do índice"
            else:
                posteriores = [(o, p) for o, p in com_partes if o is not copia and o["data_do_texto"] > copia["data_do_texto"]]
                prova = _prova(copia, parte, posteriores, alteradores)
                a_fechar = None if parte.corrido else artigos_da_copia(parte, [p for _, p in posteriores])
                seguintes = [p for p in partes_de(copia["id"]).values() if p.corrido and p.numeracao > parte.numeracao and len(p.artigos) >= ANEXO_MINIMO]
                if prova is None:
                    motivo = "sem prova de um texto posterior ao desta cópia (mesma data, ou só a data de publicação difere)"
                elif parte.corrido and seguintes:
                    motivo = "texto corrido com outro articulado a seguir: não se separa nos blocos do índice"
                elif not parte.corrido and a_fechar is None:
                    motivo = "a parte mistura o articulado de um diploma de alteração com o texto que ele cita: não se separam"
            if motivo:
                copia["regra"] = motivo
                fora.append({"obra": obra["obra"], "id": copia["id"], "titulo": copia["titulo"], "parte": copia["parte"], "artigos": copia["artigos"],
                             "data_do_texto": copia["data_do_texto"], "estado": copia["estado"], "atual": obra["atual_titulo"], "motivo": motivo})
                continue
            copia["regra"] = "marcada"
            copia["ate"], copia["prova"] = prova
            marcas.append(Marca(
                documento=copia["id"], parte=parte.parte_no_indice,
                artigos=None if parte.corrido else frozenset((f"{parte.parte_no_indice}::{n}" if parte.parte_no_indice else n, t) for n, t in a_fechar.items()),
                a_partir_de=parte.inicio if parte.corrido and parte.numeracao > 1 else None, ate=prova[0], alvo=atual["id"], alvo_parte=atual["parte"], prova=prova[1]))
    return marcas, fora


def marcas_por_documento(marcas: list[Marca]) -> dict[str, list[Marca]]:
    por_documento: dict[str, list[Marca]] = defaultdict(list)
    for marca in marcas:
        por_documento[marca.documento].append(marca)
    return dict(por_documento)


def calcular(export: Path, raiz: Path = RAIZ, hoje: str | None = None) -> tuple[list[Marca], list[dict], list[dict]]:
    """(marcas, de fora, obras) a partir do export e do `data/`: é o que o `rag.indice` chama."""
    hoje = hoje or date.today().isoformat()
    acervo = carregar(export, com_citacoes=False)
    cabecalhos = cabecalhos_dos_consolidados(acervo, raiz)
    leitor = _Leitor(acervo, raiz, hoje)
    lista_obras = obras(acervo, cabecalhos, raiz, (*PRIORITARIOS, "decreto"), hoje, leitor=leitor)
    marcas, fora = redacoes_anteriores(acervo, cabecalhos, raiz, hoje, lista_obras=lista_obras, leitor=leitor)
    return marcas, fora, lista_obras


def main(argv: list[str] | None = None) -> int:
    from rag.fontes import export_sqlite  # noqa: PLC0415

    parser = argparse.ArgumentParser(description="Lista as cópias que o índice marca como redação anterior e as que ficam de fora.")
    parser.add_argument("--saida", type=Path, default=RAIZ / "reports" / "redacoes-anteriores")
    parser.add_argument("--hoje", default=date.today().isoformat())
    args = parser.parse_args(argv)
    marcas, fora, lista_obras = calcular(export_sqlite(), RAIZ, args.hoje)
    args.saida.mkdir(parents=True, exist_ok=True)
    titulos = {c["id"]: c["titulo"] for o in lista_obras for c in o["copias"]}
    (args.saida / "marcadas.jsonl").write_text("".join(json.dumps(
        asdict(m) | {"artigos": None if m.artigos is None else len(m.artigos), "titulo": titulos[m.documento], "alvo_titulo": titulos[m.alvo]}, ensure_ascii=False, sort_keys=True) + "\n" for m in marcas), encoding="utf-8")
    (args.saida / "de-fora.jsonl").write_text("".join(json.dumps(f, ensure_ascii=False, sort_keys=True) + "\n" for f in fora), encoding="utf-8")
    resumo = {"gerado": args.hoje, "obras": len(lista_obras), "marcadas": len(marcas), "registos_com_marcas": len({m.documento for m in marcas}),
              "de_fora": len(fora), "de_fora_por_motivo": dict(Counter(f["motivo"] for f in fora).most_common())}
    (args.saida / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
