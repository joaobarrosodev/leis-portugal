"""Referências exatas numa pergunta: diplomas ("Decreto-Lei n.º 84/2021", "DL 84/2021"),
códigos ("Código do IRS", "CIVA") e artigos ("artigo 78.º-B", "art. 3.º").
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from rag.texto import _CONSOANTE_MUDA, sem_acentos


# Nome (como aparece nas perguntas) → `document_type` do acervo. Os mais compridos primeiro.
TIPOS = {
    "decreto regulamentar regional": "decreto-regulamentar-regional",
    "decreto legislativo regional": "decreto-legislativo-regional",
    "resolução do conselho de ministros": "resolucao-conselho-ministros",
    "resolução da assembleia da república": "resolucao-assembleia-republica",
    "decreto do presidente da república": "decreto-presidente-republica",
    "declaração de retificação": "declaracao-retificacao",
    "declaração de rectificação": "declaracao-retificacao",
    "decreto regulamentar": "decreto-regulamentar",
    "decreto regional": "decreto-regional",
    "decreto do governo": "decreto-governo",
    "despacho normativo": "despacho-normativo",
    "despacho conjunto": "despacho-conjunto",
    "aviso do banco de portugal": "aviso-banco-portugal",
    "regulamento da cmvm": "regulamento-cmvm",
    "decreto-lei": "decreto-lei",
    "decreto lei": "decreto-lei",
    "lei orgânica": "lei-organica",
    "lei constitucional": "lei-constitucional",
    "portaria": "portaria",
    "despacho": "despacho",
    "resolução": "resolucao",
    "declaração": "declaracao",
    "deliberação": "deliberacao",
    "acordo coletivo de trabalho": "acordo-coletivo-trabalho",
    "edital": "edital",
    "regulamento": "regulamento",
    "aviso": "aviso",
    "assento": "assento",
    "acórdão do tribunal constitucional": "acordao-tribunal-constitucional",
    "acórdão do supremo tribunal de justiça": "acordao-supremo-tribunal-justica",
    "acórdão do supremo tribunal administrativo": "acordao-supremo-tribunal-administrativo",
    "decreto": "decreto",
    "lei": "lei",
    "dl": "decreto-lei",
    "dlr": "decreto-legislativo-regional",
    "drr": "decreto-regulamentar-regional",
    "rcm": "resolucao-conselho-ministros",
    "port.": "portaria",
}
TIPOS_UE = {"regulamento": "regulation", "diretiva": "directive", "directiva": "directive", "decisão": "decision"}

# Códigos e leis gerais citados pelo nome ou pela sigla → nome do anexo (ou do diploma) no acervo.
CODIGOS = {
    "cirs": "Código do Imposto sobre o Rendimento das Pessoas Singulares",
    "código do irs": "Código do Imposto sobre o Rendimento das Pessoas Singulares",
    "circ": "Código do Imposto sobre o Rendimento das Pessoas Coletivas",
    "código do irc": "Código do Imposto sobre o Rendimento das Pessoas Coletivas",
    "civa": "Código do Imposto sobre o Valor Acrescentado",
    "código do iva": "Código do Imposto sobre o Valor Acrescentado",
    "cimi": "Código do Imposto Municipal sobre Imóveis",
    "código do imi": "Código do Imposto Municipal sobre Imóveis",
    "cimt": "Código do Imposto Municipal sobre as Transmissões Onerosas de Imóveis",
    "código do imt": "Código do Imposto Municipal sobre as Transmissões Onerosas de Imóveis",
    "cis": "Código do Imposto do Selo",
    "código do imposto do selo": "Código do Imposto do Selo",
    "ciuc": "Código do Imposto Único de Circulação",
    "cppt": "Código de Procedimento e de Processo Tributário",
    "lgt": "Lei Geral Tributária",
    "lei geral tributária": "Lei Geral Tributária",
    "ebf": "Estatuto dos Benefícios Fiscais",
    "estatuto dos benefícios fiscais": "Estatuto dos Benefícios Fiscais",
    "código do trabalho": "Código do Trabalho",
    "código da estrada": "Código da Estrada",
    "código civil": "Código Civil",
    "código penal": "Código Penal",
    "código de processo civil": "Código de Processo Civil",
    "código de processo penal": "Código de Processo Penal",
    "código do procedimento administrativo": "Código do Procedimento Administrativo",
    "código das sociedades comerciais": "Código das Sociedades Comerciais",
    "código dos contratos públicos": "Código dos Contratos Públicos",
    "código contributivo": "Código dos Regimes Contributivos do Sistema Previdencial de Segurança Social",
    "código dos regimes contributivos": "Código dos Regimes Contributivos do Sistema Previdencial de Segurança Social",
    "código do imposto sobre o valor acrescentado": "Código do Imposto sobre o Valor Acrescentado",
    "código de procedimento e de processo tributário": "Código de Procedimento e de Processo Tributário",
    # Os que faltavam nos 39 nomes centrais do inventário da camada 1 (secção 2.3), como os advogados os citam.
    "constituição da república portuguesa": "Constituição da República Portuguesa",
    "constituição da república": "Constituição da República Portuguesa",
    "regulamento das custas processuais": "Regulamento das Custas Processuais",
    "código da execução das penas e medidas privativas da liberdade": "Código da Execução das Penas e Medidas Privativas da Liberdade",
    "código de execução das penas e medidas privativas da liberdade": "Código da Execução das Penas e Medidas Privativas da Liberdade",
    "código da execução das penas": "Código da Execução das Penas e Medidas Privativas da Liberdade",
    "regime geral das infrações tributárias": "Regime Geral das Infrações Tributárias",
    "regime geral das infracções tributárias": "Regime Geral das Infrações Tributárias",
    "rgit": "Regime Geral das Infrações Tributárias",
    "código de processo do trabalho": "Código de Processo do Trabalho",
    "lei geral do trabalho em funções públicas": "Lei Geral do Trabalho em Funções Públicas",
    "ltfp": "Lei Geral do Trabalho em Funções Públicas",
    "código dos impostos especiais de consumo": "Código dos Impostos Especiais de Consumo",
    "código dos iec": "Código dos Impostos Especiais de Consumo",
    "ciec": "Código dos Impostos Especiais de Consumo",
    "código do imposto sobre veículos": "Código do Imposto sobre Veículos",
    "código do isv": "Código do Imposto sobre Veículos",
    "cisv": "Código do Imposto sobre Veículos",
    "código do imposto único de circulação": "Código do Imposto Único de Circulação",
    "código do iuc": "Código do Imposto Único de Circulação",
    "código comercial": "Código Comercial",
    "código do registo comercial": "Código do Registo Comercial",
    "código dos valores mobiliários": "Código dos Valores Mobiliários",
    "código da propriedade industrial": "Código da Propriedade Industrial",
    "código do direito de autor e dos direitos conexos": "Código do Direito de Autor e dos Direitos Conexos",
    "código do direito de autor": "Código do Direito de Autor e dos Direitos Conexos",
    "cdadc": "Código do Direito de Autor e dos Direitos Conexos",
    "código cooperativo": "Código Cooperativo",
    "código da insolvência e da recuperação de empresas": "Código da Insolvência e da Recuperação de Empresas",
    "código da insolvência": "Código da Insolvência e da Recuperação de Empresas",
    "cire": "Código da Insolvência e da Recuperação de Empresas",
    "código de processo nos tribunais administrativos": "Código de Processo nos Tribunais Administrativos",
    "cpta": "Código de Processo nos Tribunais Administrativos",
    "código das expropriações": "Código das Expropriações",
    "código da publicidade": "Código da Publicidade",
    "código do registo predial": "Código do Registo Predial",
    "código do registo civil": "Código do Registo Civil",
    "código do notariado": "Código do Notariado",
}

# Siglas que só valem em maiúsculas: em minúsculas são palavras ou outras coisas («cpi», «rcp», «ct»).
# «CRP» é a Constituição (o Código do Registo Predial cita-se «CRPredial»); «CC» e «CP» ficam de fora
# (cartão de cidadão, código postal).
SIGLAS = {
    "CRP": "Constituição da República Portuguesa",
    "RCP": "Regulamento das Custas Processuais",
    "CEPMPL": "Código da Execução das Penas e Medidas Privativas da Liberdade",
    "CPT": "Código de Processo do Trabalho",
    "CT": "Código do Trabalho",
    "CPC": "Código de Processo Civil",
    "CPP": "Código de Processo Penal",
    "CPA": "Código do Procedimento Administrativo",
    "CSC": "Código das Sociedades Comerciais",
    "CCP": "Código dos Contratos Públicos",
    "CRCom": "Código do Registo Comercial",
    "CRPredial": "Código do Registo Predial",
    "CRCivil": "Código do Registo Civil",
    "CVM": "Código dos Valores Mobiliários",
    "CPI": "Código da Propriedade Industrial",
}
# «a Constituição» com maiúscula, a meio da frase, é a da República; «constituição de sociedade» não é.
_CONSTITUICAO = re.compile(r"(?<=[\w,;:] )Constituição(?! d[aoe]s? (?!República))")

_NUMERO = r"(?:n\.?\s*[º°o]\.?\s*)?(\d+(?:-[A-Z]{1,2})?(?:/\d{2,4})?(?:/[AM]|/\d)?)\b"
_TIPO = "|".join(re.escape(t) for t in sorted(TIPOS, key=len, reverse=True))
_DIPLOMA = re.compile(rf"(?<!\w)({_TIPO})\s+{_NUMERO}", re.I)
_DIPLOMA_UE = re.compile(
    r"(?<!\w)(regulamento|diretiva|directiva|decisão)(?:\s+(?:delegad[oa]|de execução))?\s*(?:\((?:UE|CE|CEE|Euratom)\)\s*)?"
    r"(?:n\.?\s*[º°o]\.?\s*)?(\d{1,4})/(\d{1,4})",
    re.I,
)
_ARTIGO = re.compile(r"(?<!\w)(?:artigo|art\.)\s*(\d+)\s*\.?\s*[º°o]?(?:\s*-\s*([A-Z]{1,2})\b)?", re.I)
# "base IV da Lei n.º 52/2012", "Base 20": as leis de bases numeram as bases em romano ou em árabe.
_BASE = re.compile(r"(?<!\w)(?i:bases?)\s+([IVXLC]+|\d{1,3})(?!\w)")
_ROMANOS = ((100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"))


def _romano_de(n: int) -> str:
    saida = ""
    for valor, letras in _ROMANOS:
        while n >= valor:
            saida, n = saida + letras, n - valor
    return saida


def _arabe(romano: str) -> int:
    valores = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    total = 0
    for letra, seguinte in zip(romano, romano[1:] + " ", strict=True):
        total += -valores[letra] if valores.get(seguinte, 0) > valores[letra] else valores[letra]
    return total


_CODIGO = re.compile(r"(?<!\w)(" + "|".join(re.escape(c) for c in sorted(CODIGOS, key=len, reverse=True)) + r")(?!\w)", re.I)
_SIGLA = re.compile(r"(?<![\w.])(" + "|".join(re.escape(c) for c in sorted(SIGLAS, key=len, reverse=True)) + r")(?![\w-])")


@dataclass
class Referencias:
    diplomas: list[tuple[str, str, str]] = field(default_factory=list)  # (document_type, número normalizado, texto)
    codigos: list[str] = field(default_factory=list)  # nomes canónicos
    artigos: list[str] = field(default_factory=list)  # "78.º-B"

    def __bool__(self) -> bool:
        return bool(self.diplomas or self.codigos or self.artigos)


def numero_oficial(numero: str) -> str:
    """`433/1999` → `433/99`: o acervo usa dois algarismos no ano até 1999."""
    m = re.fullmatch(r"(\d+(?:-[A-Z]{1,2})?)/(\d{4})(/.*)?", numero)
    if m and int(m.group(2)) < 2000:
        return f"{m.group(1)}/{m.group(2)[2:]}{m.group(3) or ''}"
    return numero


def extrair(pergunta: str) -> Referencias:
    refs = Referencias()
    for m in _DIPLOMA.finditer(pergunta):
        tipo = TIPOS[m.group(1).lower()]
        numero = numero_oficial(m.group(2).upper())
        refs.diplomas.append((tipo, numero, m.group(0)))
    for m in _DIPLOMA_UE.finditer(pergunta):
        tipo = TIPOS_UE[m.group(1).lower()]
        a, b = m.group(2), m.group(3)
        # Regulamento (UE) 2016/679 (ano/número) ou Regulamento (CE) n.º 1234/2007 (número/ano).
        ano, numero = (a, b) if len(a) == 4 and not (len(b) == 4 and int(b) > 1950) else (b, a)
        refs.diplomas = [d for d in refs.diplomas if d[2].lower() not in m.group(0).lower()]
        refs.diplomas.append((tipo, f"{ano}/{int(numero)}", m.group(0)))
        if tipo == "regulation":
            # "Regulamento n.º 372/2009" também pode ser um regulamento português.
            refs.diplomas.append(("regulamento", f"{a}/{b}", m.group(0)))
    nomes = [(m.start(), CODIGOS[m.group(1).lower()]) for m in _CODIGO.finditer(pergunta)]
    nomes += [(m.start(), SIGLAS[m.group(1)]) for m in _SIGLA.finditer(pergunta)]
    nomes += [(m.start(), "Constituição da República Portuguesa") for m in _CONSTITUICAO.finditer(pergunta)]
    for _, nome in sorted(nomes):
        if nome not in refs.codigos:
            refs.codigos.append(nome)
    for m in _ARTIGO.finditer(pergunta):
        numero = f"{m.group(1)}.º" + (f"-{m.group(2).upper()}" if m.group(2) else "")
        if numero not in refs.artigos:
            refs.artigos.append(numero)
    for m in _BASE.finditer(pergunta):
        # O índice guarda «Base IV» ou «Base 4», como o diploma escreve: procuram-se as duas formas.
        n = int(m.group(1)) if m.group(1).isdigit() else _arabe(m.group(1))
        if 0 < n < 400:
            for numero in (f"Base {_romano_de(n)}", f"Base {n}"):
                if numero not in refs.artigos:
                    refs.artigos.append(numero)
    return refs


def texto_comparavel(texto: str) -> str:
    """Minúsculas, sem acentos e sem as consoantes mudas da grafia antiga. Estas caem antes dos acentos:
    «infracções» → «infrações» → «infracoes»."""
    return sem_acentos(_CONSOANTE_MUDA.sub("", texto.lower())).replace("colectiv", "coletiv")


def nome_normalizado(texto: str) -> str:
    texto = texto_comparavel(texto)
    texto = re.sub(r"^anexo\b[^—:-]*[—:-]\s*", "", texto)
    texto = texto.replace("(", " ").replace(")", " ")
    # «Código do Imposto sobre Veículos a que se refere o n.º 1 do artigo 1.º»: o nome é o que vem antes.
    texto = re.sub(r"(?<=\w) a que se refere\b.*$", "", texto)
    return re.sub(r"\s+", " ", texto).strip(" .")


_CONECTORES = re.compile(r"\b(?:de|do|da|dos|das|e)\b")


def nome_solto(texto: str) -> str:
    """O nome sem as palavras de ligação: «Código do Processo Penal» (o sumário do DL 78/87) = «Código de Processo Penal»."""
    return re.sub(r"\s+", " ", _CONECTORES.sub(" ", nome_normalizado(texto))).strip()
