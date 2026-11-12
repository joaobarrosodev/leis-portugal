"""As normas que cada acórdão do Tribunal Constitucional julgou, tiradas da decisão final.

Só se lê a decisão (o dispositivo), não a fundamentação: o resto do acórdão cita muitas vezes
outras decisões ("no Acórdão n.º 268/2022, decidiu-se declarar…"), que não são o que este acórdão
decidiu. De cada alínea da decisão tira-se o sentido ("julgar inconstitucional", "declarar a
inconstitucionalidade com força obrigatória geral"…) e as normas julgadas (artigo e diploma); o
parâmetro constitucional ("por violação do artigo 13.º da Constituição") fica de fora.

O diploma é resolvido no índice do RAG (`Pesquisa.diplomas` e `Pesquisa.codigo`) e o artigo só é
dado como encontrado se existir nesse documento. O resultado é o que a segunda resposta (a da
jurisprudência) e o aviso de inconstitucionalidade na resposta da lei leem:

    RAG_INDICE=… python -m rag.jurisprudencia   # grava data/jurisprudencia/tribunal-constitucional/normas-julgadas.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

from rag import referencias as refs_mod
from rag.fontes import RAIZ, corpo


PASTA_TC = RAIZ / "data" / "jurisprudencia" / "tribunal-constitucional"
SAIDA = PASTA_TC / "normas-julgadas.jsonl"

# ------------------------------------------------------------------ sentido da decisão

# Ordem importa: as formas negativas e as mais compridas primeiro.
SENTIDOS = [
    ("nao_declara_fog", r"não\s+declarar\s+a\s+(?:inconstitucionalidade|ilegalidade)"),
    ("declara_fog", r"declarar\s*(?:,\s*com\s+força\s+obrigatória\s+geral\s*,\s*)?a\s+(?:inconstitucionalidade|ilegalidade)"),
    ("nao_pronuncia", r"não\s+se\s+pronunciar\s+pela\s+(?:inconstitucionalidade|ilegalidade)"),
    ("pronuncia", r"pronunciar-se\s+pela\s+(?:inconstitucionalidade|ilegalidade)"),
    ("nao_julga", r"não\s+julgar\s+(?:inconstitucion|ilega)"),
    ("julga", r"julgar\s+(?:inconstitucion|ilega|organicamente\s+inconstitucion|materialmente\s+inconstitucion|formalmente\s+inconstitucion)"),
]
_SENTIDOS = [(nome, re.compile(r"(?<!\w)" + padrao, re.I)) for nome, padrao in SENTIDOS]
# A inconstitucionalidade é declarada "com força obrigatória geral" (fiscalização abstrata sucessiva).
_FOG = re.compile(r"força\s+obrigatória\s+geral", re.I)

ROTULOS = {
    "declara_fog": "Declara a inconstitucionalidade com força obrigatória geral",
    "nao_declara_fog": "Não declara a inconstitucionalidade",
    "julga": "Julga inconstitucional",
    "nao_julga": "Não julga inconstitucional",
    "pronuncia": "Pronuncia-se pela inconstitucionalidade",
    "nao_pronuncia": "Não se pronuncia pela inconstitucionalidade",
}

# ------------------------------------------------------------------ onde está a decisão

_TITULO_DECISAO = re.compile(r"^\s*(?:[IVXL]+|\d+)?\s*[.\-–—)]*\s*(?:Decisão|DECISÃO|Dispositivo)\s*:?\s*$", re.M)
_ABERTURA = re.compile(
    r"(?:Pelo\s+exposto|Nestes\s+termos|Termos\s+em\s+que|Em\s+face\s+do\s+exposto|Face\s+ao\s+exposto|"
    r"Pelos\s+fundamentos\s+expostos|Tudo\s+considerado|Em\s+consequência|Nos\s+termos\s+e\s+pelos\s+fundamentos|Assim\s*,|Em\s+conclusão|Em\s+suma)"
    r"[^\n]{0,200}?(?:decide|acorda|pronuncia|declara)",
    re.I,
)
_DECIDE = re.compile(r"(?:o\s+Tribunal\s+Constitucional\s+)?(?:decide(?:-se)?|decidem|acordam)[^.\n]{0,60}:", re.I)
_ASSINATURA = re.compile(r"^\s*(?:Lisboa|Lisbon)\s*,", re.M)


def decisao(texto: str) -> str:
    """O texto da decisão final: depois do último título "Decisão" (ou da última fórmula
    "Pelo exposto… decide-se"), até à assinatura."""
    inicio = None
    titulos = list(_TITULO_DECISAO.finditer(texto))
    if titulos:
        inicio = titulos[-1].end()
    else:
        aberturas = list(_ABERTURA.finditer(texto)) or list(_DECIDE.finditer(texto))
        if aberturas:
            inicio = aberturas[-1].start()
    if inicio is None:
        return ""
    resto = texto[inicio:]
    fim = _ASSINATURA.search(resto)
    return resto[: fim.start()] if fim else resto


# ------------------------------------------------------------------ alíneas

_ALINEA = re.compile(r"(?:^|\n|;\s*|:\s*)\s*(?:[a-z]|[ivx]+|\d+)\s*\)\s*(?=[A-ZÁÉÍÓÚÂÊÔÀa-záéíóúâêôàç])", re.I)


def alineas(dispositivo: str) -> list[str]:
    """Cada alínea da decisão ("a) Julgar…", "b) Negar provimento…"); sem alíneas, o todo."""
    marcas = [m.end() for m in _ALINEA.finditer(dispositivo)]
    if not marcas:
        return [dispositivo.strip()] if dispositivo.strip() else []
    partes = []
    for i, inicio in enumerate(marcas):
        fim = marcas[i + 1] if i + 1 < len(marcas) else len(dispositivo)
        parte = dispositivo[inicio:fim].strip()
        # Cortar a marca da alínea seguinte que ficou no fim ("…; b)").
        parte = re.sub(r"[;:\s]*(?:[a-z]|[ivx]+|\d+)\s*\)\s*$", "", parte, flags=re.I).strip()
        if parte:
            partes.append(parte)
    preambulo = dispositivo[: _ALINEA.search(dispositivo).start()].strip()
    return ([preambulo] if preambulo else []) + partes


def sentido(alinea: str) -> str | None:
    """O sentido da alínea pelo verbo com que decide, ou None se não julga normas."""
    melhor: tuple[int, str] | None = None
    for nome, padrao in _SENTIDOS:
        m = padrao.search(alinea)
        if m and (melhor is None or m.start() < melhor[0]):
            melhor = (m.start(), nome)
    if melhor is None:
        return None
    if re.search(r"reclama[çc]|reforma|aclara[çc]|nulidade|retifica|rectifica|lapso", alinea[: melhor[0]], re.I):
        # "indeferir a reclamação, mantendo-se a decisão sumária no sentido de não julgar…": não é um julgamento novo.
        return None
    nome = melhor[1]
    if nome == "declara_fog" and not _FOG.search(alinea):
        # "declarar a inconstitucionalidade" sem força obrigatória geral só aparece em decisões
        # que repetem um juízo de inconstitucionalidade; trata-se como julgamento.
        return "julga"
    return nome


# ------------------------------------------------------------------ normas

# O parâmetro constitucional e o resto da alínea depois dele não são a norma julgada.
_PARAMETRO = re.compile(
    r",?\s*(?:por\s+(?:violação|ofensa|contrariedade|infração|desconformidade|desrespeito)|"
    r"com\s+fundamento\s+(?:na|em)\s+violação|por\s+(?:ser|serem)\s+contrári|por\s+violar)",
    re.I,
)

# Siglas usadas nos acórdãos → nome do código (resolvido por `Pesquisa.codigo`) ou (tipo, número).
SIGLAS: dict[str, str | tuple[str, str]] = {
    "CC": "Código Civil",
    "CP": "Código Penal",
    "CPC": "Código de Processo Civil",
    "CPP": ("decreto-lei", "78/87"),
    "CPTA": "Código de Processo nos Tribunais Administrativos",
    "CPA": "Código do Procedimento Administrativo",
    "CT": "Código do Trabalho",
    "CPT": ("decreto-lei", "480/99"),
    "CE": "Código da Estrada",
    "CIRS": "Código do Imposto sobre o Rendimento das Pessoas Singulares",
    "CIRC": "Código do Imposto sobre o Rendimento das Pessoas Coletivas",
    "CIVA": "Código do Imposto sobre o Valor Acrescentado",
    "CIMI": "Código do Imposto Municipal sobre Imóveis",
    "CIMT": "Código do Imposto Municipal sobre as Transmissões Onerosas de Imóveis",
    "CIS": "Código do Imposto do Selo",
    "CPPT": "Código de Procedimento e de Processo Tributário",
    "LGT": "Lei Geral Tributária",
    "RGIT": ("lei", "15/2001"),
    "CSC": "Código das Sociedades Comerciais",
    "CCP": "Código dos Contratos Públicos",
    "CIRE": ("decreto-lei", "53/2004"),
    "CVM": ("decreto-lei", "486/99"),
    "CExp": ("lei", "168/99"),
    "CE99": ("lei", "168/99"),
    "LTC": ("lei", "28/82"),
    "LOTC": ("lei", "28/82"),
    "ETAF": ("lei", "13/2002"),
    "RCP": ("decreto-lei", "34/2008"),
    "RGCO": ("decreto-lei", "433/82"),
    "CEPMPL": ("lei", "115/2009"),
    "LGTFP": ("lei", "35/2014"),
    "CRCiv": ("decreto-lei", "131/95"),
    "CRP_PREDIAL": ("decreto-lei", "224/84"),
    "EOA": ("lei", "145/2015"),
    "NRAU": ("lei", "6/2006"),
    "LN": ("lei", "37/81"),
    "RJCESE": ("lei", "83-C/2013"),
    "CESE": ("lei", "83-C/2013"),
    "CIUC": ("lei", "22-A/2007"),
    "EBF": "Estatuto dos Benefícios Fiscais",
    "RGICSF": ("decreto-lei", "298/92"),
    "CRCSPSS": "Código dos Regimes Contributivos do Sistema Previdencial de Segurança Social",
}
# Nomes por extenso que `Pesquisa.codigo` não encontra (o anexo tem outro título no índice).
NOMES: dict[str, tuple[str, str]] = {
    "código de processo penal": ("decreto-lei", "78/87"),
    "código de processo do trabalho": ("decreto-lei", "480/99"),
    "regime geral das infrações tributárias": ("lei", "15/2001"),
    "regime geral das infracções tributárias": ("lei", "15/2001"),
    "código da insolvência e da recuperação de empresas": ("decreto-lei", "53/2004"),
    "código dos valores mobiliários": ("decreto-lei", "486/99"),
    "código das expropriações": ("lei", "168/99"),
    "lei do tribunal constitucional": ("lei", "28/82"),
    "lei da organização, funcionamento e processo do tribunal constitucional": ("lei", "28/82"),
    "estatuto dos tribunais administrativos e fiscais": ("lei", "13/2002"),
    "regulamento das custas processuais": ("decreto-lei", "34/2008"),
    "regime geral das contraordenações": ("decreto-lei", "433/82"),
    "regime geral das contra-ordenações": ("decreto-lei", "433/82"),
    "código da execução das penas e medidas privativas da liberdade": ("lei", "115/2009"),
    "lei geral do trabalho em funções públicas": ("lei", "35/2014"),
    "código do registo civil": ("decreto-lei", "131/95"),
    "código do registo predial": ("decreto-lei", "224/84"),
    "estatuto da ordem dos advogados": ("lei", "145/2015"),
    "novo regime do arrendamento urbano": ("lei", "6/2006"),
    "lei da nacionalidade": ("lei", "37/81"),
    "código da insolvência": ("decreto-lei", "53/2004"),
    "código processo penal": ("decreto-lei", "78/87"),
    "código do processo civil": ("lei", "41/2013"),
    "código de procedimento e processo tributário": ("decreto-lei", "433/99"),
    "código de procedimento e de processo tributário": ("decreto-lei", "433/99"),
    "código do imposto único de circulação": ("lei", "22-A/2007"),
    "código do imposto municipal de imóveis": ("decreto-lei", "287/2003"),
    "código do imposto municipal sobre imóveis": ("decreto-lei", "287/2003"),
    "código do imi": ("decreto-lei", "287/2003"),
    "estatuto da aposentação": ("decreto-lei", "498/72"),
    "novo regime do fundo de garantia salarial": ("decreto-lei", "59/2015"),
    "regime geral das instituições de crédito e sociedades financeiras": ("decreto-lei", "298/92"),
    "estatuto do administrador judicial": ("lei", "22/2013"),
    "novo regime jurídico da concorrência": ("lei", "19/2012"),
    "regime jurídico da concorrência": ("lei", "19/2012"),
    "código da execução das penas": ("lei", "115/2009"),
    "código de execução das penas e medidas privativas da liberdade": ("lei", "115/2009"),
    "código de valores mobiliários": ("decreto-lei", "486/99"),
    "estatutos da entidade reguladora da saúde": ("decreto-lei", "126/2014"),
    "estatutos da ers": ("decreto-lei", "126/2014"),
    "regime jurídico da contribuição extraordinária sobre o setor energético": ("lei", "83-C/2013"),
    "regime jurídico da contribuição extraordinária do setor energético": ("lei", "83-C/2013"),
}

_PALAVRAS_VAZIAS = {"de", "do", "da", "dos", "das", "e", "o", "a", "os", "as", "no", "na", "nos", "nas", "em"}


def chave_nome(nome: str) -> str:
    """"Código da Insolvência e Recuperação de Empresas [CIRE]" e "Código da Insolvência e da
    Recuperação de Empresas" dão a mesma chave."""
    nome = re.sub(r"[\[(].*?[\])]", " ", refs_mod.sem_acentos(nome.lower()))
    nome = nome.replace("colectiv", "coletiv").replace("infracc", "infrac").replace("contra-ordena", "contraordena")
    return " ".join(p for p in re.findall(r"[a-z]+", nome) if p not in _PALAVRAS_VAZIAS)


_NOMES_CHAVE = {chave_nome(k): v for k, v in NOMES.items()}
# Os nomes curtos dos códigos fiscais ("Código do IRC") → nome completo, como na pergunta.
_CODIGOS_CHAVE = {chave_nome(k): v for k, v in refs_mod.CODIGOS.items() if k.startswith("código")}
_CODIGOS_CHAVE.update({chave_nome(v): v for v in refs_mod.CODIGOS.values()})


def nome_canonico(nome: str) -> tuple[str | None, tuple[str, str] | None]:
    """(nome a resolver por `Pesquisa.codigo`, ou (tipo, número) fixo)."""
    chave = chave_nome(nome)
    if chave in _NOMES_CHAVE:
        return None, _NOMES_CHAVE[chave]
    return _CODIGOS_CHAVE.get(chave, nome), None


_NOME_CODIGO = re.compile(
    r"(?<!\w)((?:Código|Regime\s+Geral|Lei\s+Geral|Estatuto|Regulamento\s+das\s+Custas|Lei\s+do\s+Tribunal|Lei\s+da\s+Nacionalidade|"
    r"Novo\s+Regime)[^,;()\n\d]{3,110}?)(?=\s*(?:\(|,|;|\.|$|\d|\s+na\s+reda|\s+aprovad|\s+quando|\s+na\s+parte|\s+interpretad|\s+no\s+sentido|\s+e\s+(?:d[oa]s?|o|a|os|as|n\.|artigos?|art\.)\s))",
)
_SIGLA = re.compile(r"(?<![\w-])(" + "|".join(sorted((re.escape(s) for s in SIGLAS if "_" not in s), key=len, reverse=True)) + r")(?![\w-])")
_DEFINICAO_SIGLA = re.compile(r"\((?:doravante\s*,?\s*|abreviadamente\s*,?\s*|adiante\s*,?\s*)?(?:designad[oa]\s+por\s+)?([A-Z][A-Za-z]{1,7})\)")
# "artigo 2034.º", "artigos 4.º e 6.º", "art.º 9.º", "art. 150.º-A"
_ARTIGO = re.compile(r"(?<!\w)(?:artigos?|arts?\.?º?|art\.º)\s*(?:n\.?\s*º\s*)?(\d+)\s*\.?\s*[º°o]?(?:\s*-\s*([A-Z]{1,2})\b)?", re.I)
_ARTIGO_SEGUINTE = re.compile(r"^\s*(?:,|e|ou)\s*(?:(?:n\.?\s*º\s*\d+|alínea\s+\w\)|\d+\.ª\s+parte)[,\s]*)*\s*(\d+)\s*\.?\s*[º°o](?:\s*-\s*([A-Z]{1,2})\b)?", re.I)
_CONSTITUICAO = re.compile(r"Constituição|\bCRP\b", re.I)


@dataclass
class Mencao:
    """Um diploma citado na alínea e onde aparece."""

    inicio: int
    fim: int
    texto: str
    tipo: str | None = None  # (tipo, número) de um diploma citado pelo número
    numero: str | None = None
    codigo: str | None = None  # nome de um código a resolver por `Pesquisa.codigo`


@dataclass
class Norma:
    artigo: str | None  # "2034.º", ou None quando a norma não está num artigo (n.º 2 do Anexo IX)
    diploma_texto: str
    tipo: str | None = None
    numero: str | None = None
    codigo: str | None = None
    documento: str | None = None  # id no índice, depois de resolvido
    parte: str | None = None
    artigo_encontrado: bool = False
    principal: bool = True  # falso quando só aparece na interpretação, não como norma julgada


def _mencoes(texto: str, siglas: dict[str, str | tuple[str, str]]) -> list[Mencao]:
    texto = texto.translate(_HIFENS)
    encontradas: list[Mencao] = []
    for m in refs_mod._DIPLOMA.finditer(texto):
        tipo = refs_mod.TIPOS[m.group(1).lower()]
        if tipo in {"acordao-tribunal-constitucional", "acordao-supremo-tribunal-justica", "acordao-supremo-tribunal-administrativo"}:
            continue
        encontradas.append(Mencao(m.start(), m.end(), m.group(0), tipo=tipo, numero=refs_mod.numero_oficial(m.group(2).upper())))
    for m in _NOME_CODIGO.finditer(texto):
        nome = re.sub(r"\s+", " ", m.group(1)).strip()
        nome = re.sub(r"\s+(?:pel[oa]s?|que|quando|com|para|segundo|em\s+articula|na\s+interpreta|e\s+(?:n[oa]s?\s+)?artigo)\b.*$", "", nome)
        nome = re.sub(r"\s+(?:e|ou|de|do|da)$", "", nome).strip(" «»\"'")
        if any(e.inicio <= m.start() < e.fim for e in encontradas):
            continue
        codigo, fixo = nome_canonico(nome)
        if fixo:
            encontradas.append(Mencao(m.start(), m.end(), nome, tipo=fixo[0], numero=fixo[1]))
        else:
            encontradas.append(Mencao(m.start(), m.end(), nome, codigo=codigo))
    for m in _SIGLA.finditer(texto):
        alvo = siglas.get(m.group(1))
        if alvo is None or any(e.inicio <= m.start() < e.fim for e in encontradas):
            continue
        if isinstance(alvo, tuple):
            encontradas.append(Mencao(m.start(), m.end(), m.group(1), tipo=alvo[0], numero=alvo[1]))
        else:
            encontradas.append(Mencao(m.start(), m.end(), m.group(1), codigo=alvo))
    return sorted(encontradas, key=lambda e: e.inicio)


def siglas_do_acordao(texto: str) -> dict[str, str | tuple[str, str]]:
    """As siglas conhecidas mais as que o acórdão define ("Código do Processo nos Tribunais
    Administrativos (doravante, CPTA)" ou "Lei n.º 32/2008 (Lei 32/2008)")."""
    siglas = dict(SIGLAS)
    for m in _DEFINICAO_SIGLA.finditer(texto):
        sigla = m.group(1)
        antes = texto[max(0, m.start() - 160): m.start()]
        mencoes = _mencoes(antes, {})
        if mencoes and mencoes[-1].fim >= len(antes) - 25:
            ultima = mencoes[-1]
            # A definição no próprio acórdão vale mais do que a sigla habitual ("CE" é o Código das Expropriações).
            siglas[sigla] = (ultima.tipo, ultima.numero) if ultima.tipo else (ultima.codigo or "")
    return siglas


_HIFENS = str.maketrans({"\u2011": "-", "\u2010": "-", "\u2012": "-", "\u2013": "-", "\u00ad": "", "\u00a0": " ", "°": "º"})
# Um número de artigo ("25.º", "3.º-A"); "n.º 4" e "1.ª parte" não casam (o º vem antes ou é ª).
_NUMERO_ARTIGO = re.compile(r"(?<![\w.])(\d+)\s*\.?\s*º(?:\s*-\s*([A-Z]{1,2})\b)?")
# Onde o objeto da norma passa a ser a interpretação: os diplomas citados daí em diante são mencionados, não julgados.
_INTERPRETACAO = re.compile(
    r"\b(?:na\s+parte\s+em\s+que|quando\s+interpretad|interpretad[oa]s?\s+no\s+sentido|na\s+interpreta[çc][ãa]o|"
    r"segundo\s+a\s+qual|no\s+segmento|no\s+sentido\s+(?:de|segundo)|ao\s+(?:prever|estabelecer|fazer|determinar|impor)|enquanto)\b",
    re.I,
)
_ALTERACAO_MENCAO = re.compile(r"(?:reda[cç][aã]o|alterad[oa]s?|republicad[oa]|introduzid[oa]|prorrogad[oa]|aditad[oa])[^;]{0,45}$", re.I)
_ALTERACAO_ANTES = re.compile(r"(?:aprovad|criad|introduzid|alterad|prorrogad|conferid|dad|republicad|mantid|aditad)[oa]s?[^,;()]{0,40}?\s+pel[oa]s?\b[^;()]{0,30}$", re.I)
# "da mesma lei", "deste diploma": o diploma é o citado antes. "do mesmo preceito" (o mesmo artigo) não conta.
_MESMO_DIPLOMA = re.compile(r"\b(?:mesm[oa]|dest[ea]|daquel[ea]|referid[oa])\s+(?:lei|diploma|código|decreto|portaria|regime|estatuto|regulamento)", re.I)
_RETOMA = re.compile(r",\s*(?:a|as|o|os|da|das|do|dos)\s+(?:norma|normas|interpreta[çc][ãa]o|disposto|artigo|segmento|dimens[ãa]o|regime|preceito|n\.\s*[º°o]s?|al[íi]nea)", re.I)


def objeto(alinea: str) -> str:
    """A alínea sem o parâmetro constitucional ("por violação do artigo 13.º da Constituição"),
    esteja ele no fim ou no meio ("Julgar inconstitucional, por violação de…, o artigo 2.º…")."""
    texto = alinea.translate(_HIFENS)
    # "Lei n.º 83.º-C/2013" e "Lei n.º 83º-C/2013" (gralhas frequentes) → "Lei n.º 83-C/2013".
    texto = re.sub(r"(?<=\d)\s*\.?\s*º\s*-\s*(?=[A-Z]{1,2}/\d)", "-", texto)
    texto = re.sub(r"(?<=\d)\s+-\s*(?=[A-Z]{1,2}/\d)", "-", texto)
    texto = re.sub(r"Decreto-(Legislativo|Regulamentar)\s+Regional", r"Decreto \1 Regional", texto, flags=re.I)
    while True:
        m = _PARAMETRO.search(texto)
        if not m:
            return texto
        retoma = _RETOMA.search(texto, m.end())
        if retoma:
            texto = texto[: m.start()] + texto[retoma.start():]
        else:
            return texto[: m.start()]


def normas(alinea: str, siglas: dict[str, str | tuple[str, str]] | None = None) -> list[Norma]:
    """As normas julgadas na alínea: cada artigo ligado ao diploma que o segue ("do artigo 4.º da
    Lei n.º 32/2008"), e os diplomas citados sem artigo ("n.ºs 2 e 3 do Anexo IX da Portaria…").

    `principal` é falso nas normas que só aparecem na interpretação ("na parte em que, atribuindo
    natureza interpretativa ao artigo 88.º do CIRC…")."""
    siglas = SIGLAS if siglas is None else siglas
    texto = objeto(alinea)
    interpretacao = _INTERPRETACAO.search(texto)
    limite = interpretacao.start() if interpretacao else len(texto)
    mencoes = [m for m in _mencoes(texto, siglas) if not _CONSTITUICAO.search(m.texto)]
    artigos: list[tuple[int, str]] = []
    palavras = list(_ARTIGO.finditer(texto))
    for k, m in enumerate(palavras):
        # Os números de artigo desde a palavra "artigo(s)" até ao diploma (ou ao "artigo" seguinte):
        # "artigos 11.º, n.º 1, in fine, e 25.º, n.º 4, ambos do CPTA".
        fim = len(texto)
        seguinte = [x.inicio for x in mencoes if x.inicio > m.start()]
        if seguinte:
            fim = min(fim, seguinte[0])
        if k + 1 < len(palavras):
            fim = min(fim, palavras[k + 1].start())
        redacao = re.search(r"\bna\s+reda[cç][aã]o|\baprovad", texto[m.start(): fim], re.I)
        if redacao:
            fim = m.start() + redacao.start()
        artigos.append((m.start(), f"{m.group(1)}.º" + (f"-{m.group(2).upper()}" if m.group(2) else "")))
        for n in _NUMERO_ARTIGO.finditer(texto, m.end(), fim):
            artigos.append((n.start(), f"{n.group(1)}.º" + (f"-{n.group(2).upper()}" if n.group(2) else "")))
    for x in mencoes:
        # "artigo 14.º do Código Penal e 7.º, n.º 2, do Regime Geral das Contraordenações".
        seguinte = re.match(r"\s*,?\s*(?:e|bem\s+como)\s+(?:o\s+)?(\d+)\s*\.?\s*º(?:\s*-\s*([A-Z]{1,2})\b)?", texto[x.fim:])
        if seguinte:
            artigos.append((x.fim + seguinte.start(1), f"{seguinte.group(1)}.º" + (f"-{seguinte.group(2).upper()}" if seguinte.group(2) else "")))
    artigos.sort()
    # O diploma de alteração ("na redação introduzida pela Lei n.º 46/2011") nunca é o diploma de um artigo julgado.
    alteracao = {i for i, x in enumerate(mencoes) if _ALTERACAO_MENCAO.search(texto[max(0, x.inicio - 70): x.inicio])}
    resultado: list[Norma] = []
    usadas: set[int] = set()
    for pos, artigo in artigos:
        if _ALTERACAO_ANTES.search(texto[max(0, pos - 40): pos]):
            # "aprovado pelo artigo 228.º da Lei n.º 83-C/2013": o artigo que aprova ou altera não é a norma julgada.
            continue
        # O diploma é a primeira menção depois do artigo; "da mesma lei" / "deste diploma" é a anterior.
        depois = [i for i, m in enumerate(mencoes) if m.inicio > pos]
        entre = texto[pos: mencoes[depois[0]].inicio] if depois else texto[pos:]
        if _CONSTITUICAO.search(entre):
            continue
        if depois and not _MESMO_DIPLOMA.search(entre):
            i = depois[0]
            if i in alteracao:
                # O diploma do artigo não foi reconhecido ("Lei de Organização e Funcionamento dos Tribunais
                # Judiciais, na redação introduzida pela Lei n.º 46/2011"): melhor sem diploma do que o errado.
                continue
        else:
            anteriores = [i for i, m in enumerate(mencoes) if m.fim <= pos]
            if not anteriores:
                continue
            i = anteriores[-1]
        usadas.add(i)
        m = mencoes[i]
        norma = Norma(artigo, m.texto, m.tipo, m.numero, m.codigo, principal=pos < limite)
        if not any(n.artigo == norma.artigo and n.diploma_texto == norma.diploma_texto for n in resultado):
            resultado.append(norma)
    for i, m in enumerate(mencoes):
        # Um diploma sem artigo é uma norma só se não for o diploma de alteração ("na redação dada pela Lei…").
        if i in usadas or i in alteracao or re.search(r"(?:aprovad[oa]|criad[oa])[^;]{0,45}$", texto[max(0, m.inicio - 70): m.inicio], re.I):
            continue
        # A sigla a seguir ao nome ("Código da Insolvência… (CIRE)") é o mesmo diploma, não outra norma.
        if any((n.tipo, n.numero, n.codigo) == (m.tipo, m.numero, m.codigo) for n in resultado):
            continue
        if not any(n.diploma_texto == m.texto for n in resultado):
            resultado.append(Norma(None, m.texto, m.tipo, m.numero, m.codigo, principal=m.inicio < limite))
    if resultado and not any(n.principal for n in resultado):
        # "Julgar inconstitucional a norma segundo a qual …, extraída do artigo 2.º do Decreto-Lei n.º 59/2015":
        # a interpretação vem primeiro e a norma de onde é extraída vem depois.
        fonte = re.search(r"\b(?:extra[íi]d[oa]s?|extra[íi]vel|resultante|decorrente|constante)\b", texto[limite:], re.I)
        if fonte:
            inicio = limite + fonte.start()
            for n, pos in zip(resultado, [texto.find(n.diploma_texto) for n in resultado], strict=True):
                n.principal = pos >= inicio
    return resultado


# ------------------------------------------------------------------ acórdão inteiro


@dataclass
class Julgamento:
    acordao: str  # id do registo (pt:tc:acordao:2022:87)
    numero: str  # "87/2022"
    data: str | None
    url: str | None
    sentido: str
    alinea: str
    normas: list[Norma] = field(default_factory=list)


_YAML_CAMPO = re.compile(r"^(id|official_number|official_date|official_url):\s*'?([^'\n]*)'?\s*$", re.M)


def julgamentos(markdown: str) -> list[Julgamento]:
    cabecalho = markdown[: markdown.find("\n---\n", 4)] if markdown.startswith("---\n") else ""
    campos = {m.group(1): m.group(2).strip() for m in _YAML_CAMPO.finditer(cabecalho)}
    texto = corpo(markdown)
    siglas = siglas_do_acordao(texto)
    resultado = []
    for alinea in alineas(decisao(texto)):
        nome = sentido(alinea)
        if nome is None:
            continue
        resultado.append(Julgamento(
            acordao=campos.get("id", ""), numero=campos.get("official_number", ""), data=campos.get("official_date") or None,
            url=campos.get("official_url") or None, sentido=nome, alinea=re.sub(r"\s+", " ", alinea).strip(),
            normas=normas(alinea, siglas),
        ))
    return resultado


# ------------------------------------------------------------------ resolução no índice


class Resolvedor:
    """Diploma e artigo de cada norma no índice do RAG."""

    def __init__(self, pesquisa) -> None:
        self.p = pesquisa
        self._cache: dict[tuple, tuple[str | None, str | None]] = {}

    def documento(self, norma: Norma) -> tuple[str | None, str | None]:
        chave = (norma.tipo, norma.numero, norma.codigo)
        if chave not in self._cache:
            documento = parte = None
            if norma.codigo:
                achados = self.p.codigo(norma.codigo)
                if achados:
                    documento, parte = achados[0]
            elif norma.tipo and norma.numero:
                ids = self.p.diplomas(norma.tipo, norma.numero)
                if len(ids) == 1:
                    documento = ids[0]
                elif ids:
                    # Vários registos com o mesmo número (p. ex. regionais /A e /M já separados, ou retificações):
                    # fica o que tem mais artigos no índice.
                    documento = max(ids, key=lambda i: self.p.con.execute("SELECT count(*) FROM pedacos WHERE documento = ?", (i,)).fetchone()[0])
            self._cache[chave] = (documento, parte)
        return self._cache[chave]

    def resolver(self, norma: Norma) -> Norma:
        documento, parte = self.documento(norma)
        norma.documento = documento
        if documento and norma.artigo:
            linhas = self.p.con.execute(
                "SELECT DISTINCT parte FROM pedacos WHERE documento = ? AND numero = ?", (documento, norma.artigo)
            ).fetchall()
            partes = [l[0] or "" for l in linhas]
            if partes:
                norma.artigo_encontrado = True
                # O artigo de um código está no anexo; o do diploma que o aprova, no corpo.
                if parte is not None and parte in partes:
                    norma.parte = parte
                else:
                    anexos = [p for p in partes if p.startswith("Anexo")]
                    # Um código citado pelo nome ou pela sigla ("CPP", "Código de Processo Penal") está no anexo,
                    # mesmo quando o resolvemos pelo número do decreto-lei que o aprova.
                    pelo_nome = norma.codigo or not refs_mod._DIPLOMA.match(norma.diploma_texto)
                    norma.parte = anexos[0] if anexos and pelo_nome else (partes[0] if "" not in partes or not anexos else "")
        else:
            norma.parte = parte
        return norma


def construir(pesquisa, pasta: Path = PASTA_TC, saida: Path = SAIDA, progresso=print) -> Counter:
    resolvedor = Resolvedor(pesquisa)
    contas: Counter = Counter()
    linhas = []
    for caminho in sorted(pasta.rglob("*.md")):
        contas["acordaos"] += 1
        lista = julgamentos(caminho.read_text(encoding="utf-8"))
        if lista:
            contas["acordaos_com_julgamento"] += 1
        for julgamento in lista:
            contas[f"sentido:{julgamento.sentido}"] += 1
            julgamento.normas = [resolvedor.resolver(n) for n in julgamento.normas]
            contas["alineas"] += 1
            if not julgamento.normas:
                contas["alineas_sem_norma"] += 1
            if any(n.documento for n in julgamento.normas):
                contas["alineas_com_diploma"] += 1
            for norma in julgamento.normas:
                contas["normas"] += 1
                contas["normas_com_diploma"] += bool(norma.documento)
                contas["normas_com_artigo"] += bool(norma.artigo)
                contas["normas_artigo_encontrado"] += norma.artigo_encontrado
            linhas.append(json.dumps(asdict(julgamento), ensure_ascii=False))
        if contas["acordaos"] % 1000 == 0:
            progresso(f"{contas['acordaos']} acórdãos lidos")
    saida.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return contas


class Jurisprudencia:
    """Consulta do `normas-julgadas.jsonl`: os acórdãos que julgaram um artigo de um diploma.

    As decisões com força obrigatória geral vêm primeiro (as declarações mudam o que vigora; a
    resposta da lei deve avisar delas), depois os juízos em casos concretos, do mais recente para o mais antigo.
    A `parte` (o anexo de um código) só separa quando se sabe dos dois lados: o artigo 1.º do
    Decreto-Lei n.º 78/87 não é o artigo 1.º do Código de Processo Penal, que está no anexo."""

    # As decisões do Plenário em fiscalização abstrata (declarar ou recusar declarar com força obrigatória
    # geral) e preventiva valem para todos e vêm antes dos juízos em casos concretos.
    _ORDEM = {"declara_fog": 0, "nao_declara_fog": 1, "pronuncia": 2, "nao_pronuncia": 2, "julga": 3, "nao_julga": 3}

    def __init__(self, caminho: Path = SAIDA) -> None:
        self._por_artigo: dict[tuple[str, str | None], list[tuple[str | None, dict]]] = {}
        if not caminho.exists():
            return
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            if not linha.strip():
                continue
            julgamento = json.loads(linha)
            for norma in julgamento["normas"]:
                if norma["principal"] and norma["documento"]:
                    lista = self._por_artigo.setdefault((norma["documento"], norma["artigo"]), [])
                    if not any(j["acordao"] == julgamento["acordao"] and j["alinea"] == julgamento["alinea"] for _, j in lista):
                        lista.append((norma.get("parte"), julgamento))

    def __bool__(self) -> bool:
        return bool(self._por_artigo)

    def por_artigo(self, documento: str, artigo: str | None, parte: str | None = None) -> list[dict]:
        lista = [
            j for p, j in self._por_artigo.get((documento, artigo), [])
            if parte is None or p is None or p == parte
        ]
        return sorted(lista, key=lambda j: (self._ORDEM.get(j["sentido"], 9), "".join(chr(0x10FFFF - ord(c)) for c in (j["data"] or ""))))

    def declarado_inconstitucional(self, documento: str, artigo: str | None, parte: str | None = None) -> list[dict]:
        """Os acórdãos que declararam o artigo inconstitucional (ou ilegal) com força obrigatória geral."""
        return [j for j in self.por_artigo(documento, artigo, parte) if j["sentido"] == "declara_fog"]


def data_pt(data: str | None) -> str:
    return f"{data[8:10]}/{data[5:7]}/{data[:4]}" if data and len(data) >= 10 else (data or "")


def aviso_declaracao(julgamento: dict, desde: str | None) -> str:
    """O aviso que acompanha um artigo declarado inconstitucional com força obrigatória geral.

    A declaração recai sobre a redação em vigor na altura: se o texto do artigo é posterior ao
    acórdão, a declaração foi sobre uma redação anterior e o aviso diz isso."""
    acordao = f"Acórdão do Tribunal Constitucional n.º {julgamento['numero']}, de {data_pt(julgamento['data'])}"
    if desde and julgamento["data"] and desde > julgamento["data"]:
        return f"O {acordao} declarou inconstitucional, com força obrigatória geral, uma redação anterior deste artigo."
    return f"Declarado inconstitucional com força obrigatória geral, pelo menos em parte, pelo {acordao}."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--saida", type=Path, default=SAIDA)
    args = parser.parse_args(argv)
    from rag.pesquisa import Pesquisa

    contas = construir(Pesquisa(), saida=args.saida, progresso=lambda m: print(m, file=sys.stderr))
    for chave, valor in sorted(contas.items()):
        print(f"{chave}: {valor}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
