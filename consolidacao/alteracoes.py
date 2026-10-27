"""Instruções de alteração: o que o diploma que altera manda fazer ao original.

Lê o texto do diploma que altera, parágrafo a parágrafo, e devolve as instruções dirigidas ao
original:

- `substituir`: "O artigo 5.º … passa a ter a seguinte redação: «…»" (também só um número ou
  uma alínea);
- `aditar`: "É aditado … o artigo 5.º-A, com a seguinte redação: «…»";
- `revogar`: "É revogado o artigo 5.º …", "São revogados: a) os n.os 2 e 3 do artigo 4.º …";
- `retificar`: "… onde se lê «X» deve ler-se «Y»".

O resto do que menciona o original com um verbo de alteração (renumerações, "passa a
designar-se", citações sem aspas, alterações a capítulos…) fica em `por_aplicar`, com o motivo:
é o que fica para o LLM ou para revisão.

Uma instrução só é do original quando o original é o diploma de que se alteram os artigos, e
não o que deu a redação ("na redação dada pelo …"): essas alteram outro diploma.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from texto import _QUALQUER_DIPLOMA as _QUALQUER
from texto import Corpo, diplomas_em, sem_abreviaturas, dividir, numero_artigo, padrao_diploma, sem_ligacoes

_VERBO_SUBSTITUIR = re.compile(
    r"passa(?:m)? a ter a (?:seguinte )?reda[cç]+[ãa]o(?: seguinte)?|"
    r"(?:é|são) alterad[oa]s?[^.]*?passando a ter a (?:seguinte )?reda[cç]+[ãa]o|"
    r"(?:é|são) substituíd[oa]s? pel[oa]s? seguintes?|"
    r"passa(?:m)? a ter o seguinte (?:texto|teor)|"
    r"(?:é|são) alterad[oa]s?,? (?:nos termos seguintes|da forma seguinte|como segue)",
    re.I,
)
_VERBO_ADITAR = re.compile(r"(?:é|são|seja|sejam|fica|ficam) aditad[oa]s?|adita(?:m)?-se|(?-i:\bAditar\b)|(?:é|são) acrescentad[oa]s?|acrescenta(?:m)?-se|acréscimo d", re.I)
_VERBO_REVOGAR = re.compile(r"(?:é|são|seja|sejam) revogad[oa]s?|revoga(?:m)?-se|\brevoga(?:m)?\b(?! o presente)|(?-i:\bRevogar\b)|fica(?:m)? revogad[oa]s?|(?:é|são) eliminad[oa]s?", re.I)
_VERBO_RETIFICAR = re.compile(r"onde se l[êe]", re.I)
_OUTROS_VERBOS = re.compile(
    r"(?-i:\bAlterar\b)|(?:é|são) suprimid[oa]s?|(?:é|são) extint[oa]s?|passa(?:m)? a designar-se|(?:é|são) renumerad[oa]s?|passa(?:m)? a constituir|passa(?:m)? a ser o|"
    r"(?:é|são) alterad[oa]s?|(?:é|são) substituíd[oa]s?|altera(?:m)?-se|passa(?:m)? a ter a|passa(?:m)? a vigorar com",
    re.I,
)
_REDACAO_DE_OUTRO = re.compile(
    r"(?:reda[cç]+[ãa]o (?:que lhe (?:foi|é) )?dada|alterad[oa]s?|republicad[oa]s?|introduzid[oa]s?|aditad[oa]s?) (?:pel[oa]s?|através d[oa])\s*$",
    re.I,
)
_ANEXO_DE = re.compile(r"(?:aprovad[oa]s?|publicad[oa]s?) (?:pel[oa]|em anexo (?:a[oa]?|à))\s*$|anexos? (?:[IVXL]+ )?(?:a[oa]?|d[oa])\s*$", re.I)
_PLACEHOLDER = re.compile(r"^(?:\[\s*(?:\.\s*){3}\]|\[…\]|\(\s*(?:\.\s*){3}\)|\(…\)|…|(?:\.\s*){3,})[.;:,]?$")


@dataclass
class Alvo:
    """O que a instrução altera: artigo e, se for o caso, número e alínea."""

    parte: str
    artigo: str | None
    numero: str | None = None
    alinea: str | None = None

    def __str__(self) -> str:
        texto = "" if self.artigo is None else f"artigo {self.artigo}"
        if self.numero:
            texto = f"n.º {self.numero} do {texto}"
        if self.alinea:
            texto = f"alínea {self.alinea}) do {texto}"
        return (f"{self.parte}: " if self.parte else "") + texto


@dataclass
class Instrucao:
    tipo: str  # substituir | aditar | revogar | retificar
    alvos: list[Alvo]
    excerto: str  # o parágrafo da instrução e, se houver, a citação
    artigo_alterador: str  # o artigo do diploma que altera onde está a instrução ("" se não tiver artigos)
    citacao: str = ""  # o texto entre « » (sem as aspas exteriores)
    antes: str = ""  # retificação: o que se lê
    depois: str = ""  # retificação: o que deve ler-se
    aviso: str = ""


@dataclass
class PorAplicar:
    motivo: str
    excerto: str
    artigo_alterador: str


@dataclass
class Leitura:
    instrucoes: list[Instrucao] = field(default_factory=list)
    por_aplicar: list[PorAplicar] = field(default_factory=list)
    mencoes: int = 0  # parágrafos que mencionam o original


def e_placeholder(texto: str) -> bool:
    return bool(_PLACEHOLDER.match(texto.strip()))


# --- Parágrafos do diploma que altera -------------------------------------------------------


@dataclass
class Paragrafo:
    texto: str
    artigo: str  # chave do artigo do alterador ("" fora de artigos)
    titulo: str  # título desse artigo (epígrafe), para o contexto "Alteração ao …"


def paragrafos(texto: str) -> list[Paragrafo]:
    corpo = dividir(texto)
    resultado: list[Paragrafo] = []
    for segmento in corpo.segmentos:
        if hasattr(segmento, "linhas"):
            chave, titulo, linhas = segmento.chave, segmento.epigrafe, segmento.linhas[1:]
        else:
            chave, titulo, linhas = "", "", [l for l in segmento if not l.startswith("#")]
        bloco: list[str] = []
        for linha in linhas + [""]:
            if linha.strip():
                bloco.append(linha.strip())
            elif bloco:
                resultado.append(Paragrafo(sem_ligacoes(" ".join(bloco)), chave, sem_ligacoes(titulo)))
                bloco = []
    return resultado


def citacao(lista: list[Paragrafo], i: int) -> tuple[str, int, bool]:
    """A citação que começa no parágrafo `i` («…»), o índice a seguir a ela e se fechou.

    A citação acaba no » que fecha o primeiro «. Há textos com o » em falta: aí acaba antes do
    primeiro parágrafo noutro artigo do diploma que altera ou que abre outra citação."""
    if i >= len(lista) or not lista[i].texto.startswith("«"):
        return "", i, False
    nivel, partes, j = 0, [], i
    while j < len(lista) and (j == i or lista[j].artigo == lista[i].artigo):
        texto = lista[j].texto
        if j > i and nivel == 1 and texto.startswith("«") and partes and not partes[-1].rstrip().endswith(":"):
            break
        for k, c in enumerate(texto):
            if c == "«":
                nivel += 1
            elif c == "»":
                nivel -= 1
                if nivel == 0:
                    partes.append(texto[: k + 1])
                    return _sem_aspas("\n\n".join(partes)), j + 1, True
        partes.append(texto)
        j += 1
    return _sem_aspas("\n\n".join(partes)), j, False


def _sem_aspas(texto: str) -> str:
    texto = texto.strip()
    if texto[:1] in "«\"“":
        texto = texto[1:]
    texto = re.sub(r"[»\"”]\s*[.;,]?\s*$", "", texto)
    return texto.strip()


# --- Localizadores: "a alínea b) do n.º 1 do artigo 3.º" --------------------------------------

_TOKEN = re.compile(
    r"(?P<tipo>al[íi]neas?|n\.?\s*os|n\.?\s*º|n\.?\s*o\b|números?|artigos?|arts?\.)\s*"
    r"(?P<lista>(?:\d+(?:\.\d+)*\s*\.?\s*[º°o]?(?:\s*-\s*[A-Z]{1,2})?|[a-z]{1,2}\)|[ivxl]+\))"
    r"(?:\s*(?:,|\be\b|\ba\b)\s*(?:\d+(?:\.\d+)*\s*\.?\s*[º°o]?(?:\s*-\s*[A-Z]{1,2})?|[a-z]{1,2}\)|[ivxl]+\)))*)",
    re.I,
)


def _lista(texto: str, tipo: str) -> list[str] | None:
    itens = [t.strip() for t in re.split(r"\s*,\s*|\s+e\s+", texto.strip()) if t.strip()]
    resultado: list[str] = []
    for item in itens:
        intervalo = re.match(r"^(\d+)\D*\s+a\s+(\d+)\D*$", item)
        if intervalo:
            a, b = int(intervalo.group(1)), int(intervalo.group(2))
            if b < a or b - a > 200:
                return None
            resultado.extend(str(n) for n in range(a, b + 1))
        elif re.search(r"\s+a\s+", item):
            return None  # intervalo com letras ("4.º-A a 4.º-C"): não se expande por regra
        else:
            resultado.append(item)
    if not all(re.search(r"\w", i) for i in resultado):
        return None
    if tipo == "artigo":
        return [numero_artigo(i) for i in resultado]
    if tipo == "numero":
        return [re.sub(r"\D+$", "", i) for i in resultado]
    return [i.rstrip(")") for i in resultado]


def localizadores(texto: str, parte: str) -> list[Alvo] | None:
    """Os alvos de um troço como "os n.os 2 e 3 do artigo 4.º e o artigo 7.º".

    Devolve None se o troço tiver algo que não se sabe ler por regra."""
    alvos: list[Alvo] = []
    pendentes: list[Alvo] = []
    grupo: dict[str, list[str]] = {}
    ordem = {"alinea": 0, "numero": 1, "artigo": 2}

    def fechar_grupo() -> None:
        nonlocal grupo
        if not grupo:
            return
        artigos = grupo.get("artigo", [None])
        numeros = grupo.get("numero", [None])
        alineas = grupo.get("alinea", [None])
        if len(artigos) > 1 and (numeros != [None] or alineas != [None]):
            raise ValueError("vários artigos com números")
        for artigo in artigos:
            for numero in numeros:
                for alinea in alineas:
                    (pendentes if artigo is None else alvos).append(Alvo(parte, artigo, numero, alinea))
        if artigos != [None]:
            for p in pendentes:
                p.artigo = artigos[0]
            alvos.extend(pendentes)
            pendentes.clear()
        grupo = {}

    try:
        for m in _TOKEN.finditer(texto):
            palavra = m.group("tipo").lower()
            tipo = "alinea" if palavra.startswith("al") else "artigo" if palavra.startswith("art") else "numero"
            lista = _lista(m.group("lista"), tipo)
            if lista is None:
                return None
            if grupo and max(ordem[t] for t in grupo) >= ordem[tipo]:
                fechar_grupo()
            grupo[tipo] = lista
            if tipo == "artigo":
                fechar_grupo()
        fechar_grupo()
    except ValueError:
        return None
    if pendentes or not alvos:
        return None
    return alvos


# --- Leitura das instruções -----------------------------------------------------------------


_LOCALIZADOR = re.compile(r"artigos?|arts?\.|n\.?\s*[ºo]s?\b|al[íi]neas?|anexos?|aprovad[oa]|n[úu]meros?", re.I)


_GOVERNADO = re.compile(
    r"(?:artigos?|arts?\.|n\.?\s*[ºo]s?|al[íi]neas?|anexos?|aprovad[oa]s?|n[úu]meros?|mapas?|quadros?)\b[^;:]*?"
    r"\b(?:d[oa]s?|a[oa]s?|à|n[oa]s?|pel[oa]s?)\s*$",
    re.I,
)


def _governa(texto: str, padrao: re.Pattern[str]) -> tuple[re.Match[str] | None, str]:
    """A menção do original que é o diploma alterado no parágrafo, e se aponta para um anexo.

    O diploma alterado é o primeiro mencionado depois dos localizadores ("o artigo 5.º do …"),
    saltando os que só deram a redação ("na redação dada pelo …"). Devolve (menção, "diploma"
    | "anexo" | "outro" | "")."""
    proprias = list(padrao.finditer(texto))
    if not proprias:
        return None, ""
    refs = [(m.start(), m.end(), None) for m in diplomas_em(texto) if not any(p.start() <= m.start() < p.end() or m.start() <= p.start() < m.end() for p in proprias)]
    refs += [(m.start(), m.end(), m) for m in proprias]
    refs.sort(key=lambda r: r[0])
    validas = [r for r in refs if not _REDACAO_DE_OUTRO.search(texto[max(0, r[0] - 60) : r[0]])]
    if not validas:
        return None, "outro"
    anterior = 0
    escolhida = None
    for r in validas:
        if _GOVERNADO.search(texto[anterior : r[0]]):
            escolhida = r
            break
        anterior = r[1]
    escolhida = escolhida or validas[0]
    if escolhida[2] is None:
        return None, "outro"
    antes = texto[max(0, escolhida[0] - 60) : escolhida[0]]
    return escolhida[2], "anexo" if _ANEXO_DE.search(antes) else "diploma"


_LIGACAO_LISTA = re.compile(
    r"\b(?:o|a|os|as|e|bem como|ainda|todos?|n\.?\s*[ºo]s?|de \d+ de \w+(?: de \d{4})?|\d+[-/]?\w*)\b|[,;:()]|\s+|^[a-z]{1,2}\)|^[ivx]+\)|^\d+\s*-",
    re.I,
)


_DE_OUTRO_LISTA = re.compile(
    r"(?:reda[cç]+[ãa]o (?:que lhe (?:foi|é) )?dada|alterad[oa]s?|republicad[oa]s?|introduzid[oa]s?|nos termos|ao abrigo|"
    r"previst[oa]s?|referid[oa]s?|habilitad[oa]s?) (?:pel[oa]s?|n[oa]s?|d[oa]s?)\b[^;]*$",
    re.I,
)


_MOTIVO_INTEIRA = {
    "diploma": "revogação do diploma inteiro",
    "anexo": "revogação do que o original aprovou em anexo",
    "parcial": "revogação com exceções ou só em parte",
}


def _so_em_parte(depois: str) -> bool:
    """Depois do nome do diploma revogado, a frase limita a revogação: "com excepção dos
    artigos 1.º a 5.º", "na parte que …", "em tudo o que contrariar …", "…, os n.os 15 e 16"."""
    frase = re.split(r"[;.](?:\s|$)", sem_abreviaturas(depois), maxsplit=1)[0]
    frase = re.sub(r"^,?\s*de \d+ de \w+(?: de \d{4})?", "", frase)
    if re.search(r"na parte ainda em vigor", frase, re.I):
        return False
    return bool(re.search(
        r"exce[pç]+[ãa]o|\bsalvo\b|\bexceto\b|\bexcepto\b|na parte|em tudo o que|no que (?:contrari|respeita|se refere)|"
        r"^\W*(?:os?|as?)\s+(?:artigos?|n\s*[ºo]s?|n[úu]meros?|al[íi]neas?|anexos?)\b",
        frase, re.I,
    ))


def _revogacao_inteira(texto: str, padrao: re.Pattern[str]) -> str:
    """"São revogados o Decreto n.º A e o Decreto n.º B": o original é revogado por inteiro.

    Devolve "diploma", "anexo" (o original aprovou o que se revoga: "o Estatuto …, aprovado
    pelo …"), "parcial" (revogado com exceções ou só em parte) ou "" quando o original não é o
    objeto da revogação."""
    primeiro = _VERBO_REVOGAR.search(texto)
    if not primeiro:
        return ""
    for m in padrao.finditer(texto, primeiro.end()):
        antes = sem_abreviaturas(texto[primeiro.end() : m.start()])
        if _DE_OUTRO_LISTA.search(antes):
            continue
        if _so_em_parte(texto[m.end() :]):
            return "parcial"
        resto = _LIGACAO_LISTA.sub("", _QUALQUER.sub(" ", antes))
        if re.search(r"aprovad[oa]s? (?:pel[oa]|em anexo a[oa]?)\s*$", antes, re.I) and len(_LIGACAO_LISTA.sub("", re.sub(r",?\s*aprovad\w+ .*$", "", antes))) < 80:
            return "anexo"
        if len(resto) <= 3:
            return "diploma"
    return ""


def _parte_anexo(texto: str, original: Corpo, mencao: re.Match[str]) -> str | None:
    partes = [p for p in original.partes() if p]
    designacao = re.search(r"anexo\s+([IVXL]+|\d+)\b", texto[: mencao.start()], re.I)
    if designacao:
        alvo = designacao.group(1).upper()
        candidatas = [p for p in partes if re.match(rf"^anexo\s+{alvo}\b", p, re.I)]
        return candidatas[0] if len(candidatas) == 1 else None
    return partes[0] if len(partes) == 1 else None


def ler(texto_alterador: str, titulo_original: str, original: Corpo) -> Leitura:
    padrao = padrao_diploma(titulo_original)
    leitura = Leitura()
    if padrao is None:
        return leitura
    lista = paragrafos(texto_alterador)
    i = 0
    alvo_anterior: tuple[str, str] | None = None  # (parte, âmbito) da última instrução, para "do mesmo diploma"
    tem_artigos = any(p.artigo for p in lista)
    em_retificacao = False  # numa declaração de retificação, os "onde se lê" seguintes são do original
    while i < len(lista):
        p = lista[i]
        texto = p.texto
        if tem_artigos and not p.artigo:
            i += 1  # preâmbulo: as instruções estão nos artigos
            continue
        mencao, ambito = _governa(texto, padrao)
        contexto = bool(padrao.search(p.titulo)) and not diplomas_em(texto)
        mesmo = re.search(r"d[oa] (?:mesmo|referid[oa]|citad[oa]) (?:diploma|decreto|lei|portaria|regulamento)", texto, re.I)
        if mencao is not None and ambito == "diploma" and re.search(r"inexact|inexat|rectific|retific", texto, re.I):
            em_retificacao = True
        elif ambito == "outro":
            em_retificacao = False
        if mencao is None and ambito != "outro" and (contexto or (mesmo and alvo_anterior) or (em_retificacao and _VERBO_RETIFICAR.search(texto))):
            ambito = "diploma"
        if mencao is not None or ambito == "diploma":
            leitura.mencoes += 1
        inteira = _revogacao_inteira(texto, padrao)
        if inteira:
            leitura.mencoes += mencao is None
            motivo = _MOTIVO_INTEIRA[inteira]
            leitura.por_aplicar.append(PorAplicar(motivo, texto, p.artigo))
            i += 1
            continue
        if ambito not in ("diploma", "anexo") or not any(
            v.search(texto) for v in (_VERBO_SUBSTITUIR, _VERBO_ADITAR, _VERBO_REVOGAR, _VERBO_RETIFICAR, _OUTROS_VERBOS)
        ):
            # Lista de revogações ("São revogados:") cujos itens nomeiam o original.
            if _VERBO_REVOGAR.search(texto) and texto.rstrip().endswith(":"):
                j = i + 1
                while j < len(lista) and re.match(r"^[a-z]{1,2}\)\s", lista[j].texto):
                    item = lista[j].texto
                    m_item, amb_item = _governa(item, padrao)
                    inteira = _revogacao_inteira(texto + " " + item, padrao)
                    if inteira:
                        leitura.mencoes += 1
                        motivo = _MOTIVO_INTEIRA[inteira]
                        leitura.por_aplicar.append(PorAplicar(motivo, texto + "\n\n" + item, p.artigo))
                    elif m_item is not None and amb_item in ("diploma", "anexo"):
                        leitura.mencoes += 1
                        _revogacao(leitura, texto + "\n\n" + item, item[: m_item.start()], amb_item, m_item, item, original, p.artigo)
                    j += 1
                i = j
                continue
            i += 1
            continue

        alvo_anterior = ("", ambito)
        parte = ""
        if ambito == "anexo":
            parte = _parte_anexo(texto, original, mencao) if mencao else None
            if parte is None:
                leitura.por_aplicar.append(PorAplicar("anexo do original não identificado", texto, p.artigo))
                i += 1
                continue
        antes_mencao = texto[: mencao.start()] if mencao else texto

        if _VERBO_RETIFICAR.search(texto):
            _retificacao(leitura, texto, antes_mencao, parte, p.artigo)
            i += 1
            continue

        e_substituir = bool(_VERBO_SUBSTITUIR.search(texto))
        e_aditar = bool(_VERBO_ADITAR.search(texto)) and ("reda" in texto.lower() or texto.rstrip().endswith(":"))
        if e_substituir or e_aditar:
            texto_citado, seguinte, fechou = citacao(lista, i + 1)
            if not texto_citado:
                leitura.por_aplicar.append(PorAplicar("redação nova sem aspas «»", texto, p.artigo))
                i += 1
                continue
            excerto = texto + "\n\n«" + texto_citado + "»"
            tipo = "aditar" if e_aditar and not e_substituir else "substituir"
            if _ANAFORA.search(antes_mencao):
                leitura.por_aplicar.append(PorAplicar("localizador de outro diploma («portaria supracitada»)", excerto, p.artigo))
                i = seguinte
                continue
            if re.match(r"^(?:Artigo|ARTIGO|Art\.)\s+\d", texto_citado):
                alvos = [Alvo(parte, None)]  # os artigos vêm na própria citação
            else:
                alvos = _alvos_parciais(texto, antes_mencao, parte)
                if not alvos or any(a.artigo is None for a in alvos):
                    leitura.por_aplicar.append(PorAplicar("alvo da nova redação não identificado", excerto, p.artigo))
                    i = seguinte
                    continue
            aviso = "" if fechou else "citação sem » de fecho"
            leitura.instrucoes.append(Instrucao(tipo, alvos, excerto, p.artigo, citacao=texto_citado, aviso=aviso))
            i = seguinte
            continue

        if _VERBO_REVOGAR.search(texto):
            _revogacao(leitura, texto, antes_mencao, ambito, mencao, texto, original, p.artigo, parte)
            i += 1
            continue

        leitura.por_aplicar.append(PorAplicar("instrução de outro tipo", texto, p.artigo))
        i += 1
    return leitura


def _alvos_parciais(texto: str, antes_mencao: str, parte: str) -> list[Alvo]:
    """Alvo de uma redação nova que não traz o artigo inteiro: "O n.º 2 do artigo 5.º …" ou
    "É aditado ao artigo 5.º … um n.º 4"."""
    verbo = re.split(r"\b(?:passa|passam|é|são)\b", antes_mencao)[0]
    alvos = localizadores(verbo, parte) or localizadores(antes_mencao, parte)
    if alvos:
        return alvos
    artigos = re.findall(r"\bartigo\s+(\d+\.?\s*[º°o]?(?:\s*-\s*[A-Z]{1,2})?)", texto, re.I)
    numeros = re.findall(r"\bn\.?\s*[ºo]\s*(\d+)\b(?!\.?\s*º)", texto, re.I)
    alineas = re.findall(r"\bal[íi]nea\s+([a-z]{1,2})\)", texto, re.I)
    if len(set(artigos)) == 1 and len(set(numeros)) <= 1 and len(set(alineas)) <= 1:
        return [Alvo(parte, numero_artigo(artigos[0]), numeros[0] if numeros else None, alineas[0] if alineas else None)]
    return []


# "Revogados, na parte em que contrariem o presente decreto-lei: …": a revogação depende do
# diploma novo e não se aplica ao texto por regra.
_CONDICIONAL = re.compile(r"na parte em que|na medida em que|em tudo o que|no que (?:contrari|for contrári)", re.I)
# "o n.º 6 da portaria supracitada": o localizador é de outro diploma, mesmo que o parágrafo
# nomeie o original mais à frente.
_ANAFORA = re.compile(
    r"\b(?:portaria|decreto(?:-lei)?|lei|diploma|despacho|regulamento|resolu[çc][ãa]o)\s+(?:acima\s+|atrás\s+)?"
    r"(?:supra)?(?:citad|referid|mencionad|aludid)[oa]|"
    r"\b(?:supracitad|citad|referid|mencionad|aludid|mesm)[oa]\s+(?:portaria|decreto|lei|diploma|despacho|regulamento)",
    re.I,
)


def _revogacao(leitura: Leitura, excerto: str, antes: str, ambito: str, mencao, texto: str, original: Corpo, artigo: str, parte: str = "") -> None:
    if _CONDICIONAL.search(excerto):
        leitura.por_aplicar.append(PorAplicar("revogação condicional («na parte em que contrarie»)", excerto, artigo))
        return
    if _ANAFORA.search(antes):
        leitura.por_aplicar.append(PorAplicar("localizador de outro diploma («portaria supracitada»)", excerto, artigo))
        return
    if ambito == "anexo" and not parte:
        parte = _parte_anexo(texto, original, mencao) if mencao else None
        if parte is None:
            leitura.por_aplicar.append(PorAplicar("anexo do original não identificado", excerto, artigo))
            return
    troco = re.split(r"revogad[oa]s?|\brevoga(?:m)?(?:-se)?\b|eliminad[oa]s?", antes, flags=re.I)[-1]
    sem_diplomas = _QUALQUER.sub(" ", troco)
    if not re.search(r"artigo|art\.|n\.?\s*[ºo]|alínea|número", sem_diplomas, re.I) and mencao is not None and _so_em_parte(texto[mencao.end() :]):
        leitura.por_aplicar.append(PorAplicar(_MOTIVO_INTEIRA["parcial"], excerto, artigo))
        return
    if not re.search(r"artigo|art\.|n\.?\s*[ºo]|alínea|número", sem_diplomas, re.I):
        motivo = "revogação de anexo ou parte sem artigo" if re.search(r"anexo|cap[íi]tulo|sec[çc][ãa]o|mapa|quadro|tabela|\bbases?\b|\bpontos?\b", sem_diplomas, re.I) else "revogação do diploma inteiro"
        leitura.por_aplicar.append(PorAplicar(motivo, excerto, artigo))
        return
    troco = sem_diplomas
    alvos = localizadores(troco, parte)
    if not alvos:
        leitura.por_aplicar.append(PorAplicar("revogação com alvo que a regra não lê", excerto, artigo))
        return
    leitura.instrucoes.append(Instrucao("revogar", alvos, excerto, artigo))


_ONDE = re.compile(
    r"onde se l[êe],?\s*(?:«(?P<antes>.*?)»|\"(?P<antes2>.*?)\"),?\s*deve ler-se,?\s*(?:«(?P<depois>.*?)»|\"(?P<depois2>.*?)\")",
    re.I | re.S,
)


def _retificacao(leitura: Leitura, texto: str, antes_mencao: str, parte: str, artigo: str) -> None:
    pares = list(_ONDE.finditer(texto))
    if not pares:
        leitura.por_aplicar.append(PorAplicar("retificação sem «» que a regra leia", texto, artigo))
        return
    prefixo = texto[: pares[0].start()]
    alvos = localizadores(prefixo, parte) or _alvos_parciais(prefixo, prefixo, parte) or [Alvo(parte, None)]
    for m in pares:
        leitura.instrucoes.append(
            Instrucao("retificar", alvos, texto, artigo, antes=(m.group("antes") or m.group("antes2")).strip(),
                      depois=(m.group("depois") or m.group("depois2") or "").strip())
        )
