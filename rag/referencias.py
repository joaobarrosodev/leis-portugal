"""Referências exatas numa pergunta: diplomas ("Decreto-Lei n.º 84/2021", "DL 84/2021"),
códigos ("Código do IRS", "CIVA") e artigos ("artigo 78.º-B", "art. 3.º").
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from rag.texto import sem_acentos


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
}

_NUMERO = r"(?:n\.?\s*[º°o]\.?\s*)?(\d+(?:-[A-Z]{1,2})?(?:/\d{2,4})?(?:/[AM]|/\d)?)\b"
_TIPO = "|".join(re.escape(t) for t in sorted(TIPOS, key=len, reverse=True))
_DIPLOMA = re.compile(rf"(?<!\w)({_TIPO})\s+{_NUMERO}", re.I)
_DIPLOMA_UE = re.compile(
    r"(?<!\w)(regulamento|diretiva|directiva|decisão)(?:\s+(?:delegad[oa]|de execução))?\s*(?:\((?:UE|CE|CEE|Euratom)\)\s*)?"
    r"(?:n\.?\s*[º°o]\.?\s*)?(\d{1,4})/(\d{1,4})",
    re.I,
)
_ARTIGO = re.compile(r"(?<!\w)(?:artigo|art\.)\s*(\d+)\s*\.?\s*[º°o]?(?:\s*-\s*([A-Z]{1,2})\b)?", re.I)
_CODIGO = re.compile(r"(?<!\w)(" + "|".join(re.escape(c) for c in sorted(CODIGOS, key=len, reverse=True)) + r")(?!\w)", re.I)


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
    for m in _CODIGO.finditer(pergunta):
        nome = CODIGOS[m.group(1).lower()]
        if nome not in refs.codigos:
            refs.codigos.append(nome)
    for m in _ARTIGO.finditer(pergunta):
        numero = f"{m.group(1)}.º" + (f"-{m.group(2).upper()}" if m.group(2) else "")
        if numero not in refs.artigos:
            refs.artigos.append(numero)
    return refs


def nome_normalizado(texto: str) -> str:
    texto = sem_acentos(texto.lower())
    texto = re.sub(r"^anexo\b[^—:-]*[—:-]\s*", "", texto)
    texto = texto.replace("colectiv", "coletiv").replace("(", " ").replace(")", " ")
    return re.sub(r"\s+", " ", texto).strip(" .")
