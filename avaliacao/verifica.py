"""Verificação do conjunto de avaliação (`avaliacao/perguntas.jsonl`).

- `literal`: confirma que o excerto de cada pergunta está, letra a letra, no artigo citado
  (na data de referência, para as temporais) e que os números da resposta estão no excerto.
- `cegas --saida F`: escreve a entrada da sessão B (verificação às cegas): pergunta, data e
  texto do artigo, sem a resposta certa. Nas perguntas sem resposta vai o artigo distrator.
- `compara --respostas F`: compara as respostas da sessão B com as da sessão A e lista as
  que não batem, para uma terceira revisão.

Formato das respostas da sessão B (uma por linha): `{"id", "responde": bool, "resposta",
"excerto", "ambigua": bool, "depende_de_outro": bool, "notas"}`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from comum import RAIZ, artigo, normalizar


PERGUNTAS = RAIZ / "avaliacao" / "perguntas.jsonl"


def ler(caminho: Path) -> list[dict]:
    return [json.loads(linha) for linha in caminho.read_text(encoding="utf-8").splitlines() if linha.strip()]


_ORTOGRAFIA = [("cç", "ç"), ("pç", "ç"), ("ct", "t"), ("pt", "t")]
_VAZIAS = set("ao aos as às com da das de do dos em na nas no nos os ou para pela pelas pelo pelos por que se uma um sob".split())


def numeros(texto: str) -> set[str]:
    """Os números de um texto, sem separadores de milhares nem casas decimais a zero
    (`(euro) 100 000 000,00` e `100 000 000 euros` dão o mesmo número)."""
    texto = re.sub(r"(?<=\d)[  .](?=\d{3}\b)", "", texto or "")
    return {re.sub(r",0+$", "", valor) for valor in re.findall(r"\d+(?:,\d+)?", texto)}


def palavras(texto: str) -> set[str]:
    """Palavras com conteúdo, sem as diferenças do Acordo Ortográfico (director/diretor)."""
    texto = (texto or "").lower()
    for antes, depois in _ORTOGRAFIA:
        texto = texto.replace(antes, depois)
    return {palavra for palavra in re.findall(r"\w+", texto) if len(palavra) > 2 and palavra not in _VAZIAS}


def mesmo_sentido(a: str, b: str) -> bool:
    """A resposta de B contém pelo menos 80% das palavras com conteúdo da resposta de A."""
    esperadas = palavras(a)
    return bool(esperadas) and len(esperadas & palavras(b)) / len(esperadas) >= 0.8


def texto_da_fonte(fonte: dict, data: str | None) -> str | None:
    encontrado = artigo(RAIZ / fonte["caminho"], fonte["artigo"], data)
    return encontrado.texto if encontrado else None


def data_do_texto(pergunta: dict) -> str | None:
    """As temporais leem o artigo na data de referência; as outras, o texto do registo."""
    return pergunta["data_referencia"] if pergunta["tipo"] == "temporal" else None


def literal(perguntas: list[dict]) -> int:
    falhas = 0
    for pergunta in perguntas:
        problemas = []
        if pergunta["tipo"] == "sem_resposta":
            if pergunta.get("fonte") or not pergunta.get("distrator"):
                problemas.append("sem resposta: deve ter distrator e nenhuma fonte")
        else:
            texto = texto_da_fonte(pergunta["fonte"], data_do_texto(pergunta))
            if texto is None:
                problemas.append(f"artigo {pergunta['fonte']['artigo']} não encontrado")
            elif normalizar(pergunta["excerto"]) not in normalizar(texto):
                problemas.append("o excerto não está no texto do artigo")
            em_falta = numeros(pergunta["resposta"]) - numeros(pergunta["excerto"])
            if pergunta["tipo"] != "revogada" and em_falta:
                problemas.append(f"números da resposta fora do excerto: {sorted(em_falta)}")
            if pergunta["tipo"] == "revogada" and not pergunta.get("revogado_por"):
                problemas.append("revogada sem `revogado_por`")
        if problemas:
            falhas += 1
            print(f"{pergunta['id']}: " + "; ".join(problemas))
    print(f"{len(perguntas) - falhas} de {len(perguntas)} pergunta(s) passam a verificação literal")
    return 1 if falhas else 0


def cegas(perguntas: list[dict], saida: Path) -> int:
    with saida.open("w", encoding="utf-8") as ficheiro:
        for pergunta in perguntas:
            fonte = pergunta.get("fonte") or pergunta["distrator"]
            entrada = {
                "id": pergunta["id"],
                "pergunta": pergunta["pergunta"],
                "data_referencia": pergunta["data_referencia"],
                "fonte": {
                    "titulo": fonte["titulo"],
                    "artigo": fonte["artigo"],
                    "epigrafe": fonte.get("epigrafe", ""),
                    "texto": texto_da_fonte(fonte, data_do_texto(pergunta)),
                },
            }
            if pergunta["tipo"] == "revogada":
                revogador = pergunta["revogado_por"]
                entrada["fonte"]["estado"] = f"Revogado por {revogador['titulo']} (em vigor desde {revogador['data']})"
            ficheiro.write(json.dumps(entrada, ensure_ascii=False) + "\n")
    print(f"{len(perguntas)} pergunta(s) em {saida}")
    return 0


def compara(perguntas: list[dict], respostas: Path) -> int:
    por_id = {resposta["id"]: resposta for resposta in ler(respostas)}
    rever = []
    for pergunta in perguntas:
        b = por_id.get(pergunta["id"])
        if b is None:
            rever.append((pergunta["id"], "sem resposta da sessão B"))
            continue
        if b.get("ambigua") or (b.get("depende_de_outro") and not pergunta.get("depende_de_outro")):
            rever.append((pergunta["id"], f"B assinalou: {b.get('notas', '')}"))
        if pergunta["tipo"] == "sem_resposta":
            if b.get("responde"):
                rever.append((pergunta["id"], "B respondeu a uma pergunta sem resposta"))
            continue
        if not b.get("responde"):
            rever.append((pergunta["id"], "B não encontrou resposta no artigo"))
            continue
        if pergunta["tipo"] == "revogada":
            if "revog" not in (b.get("resposta") or "").lower():
                rever.append((pergunta["id"], "B não indicou que o diploma está revogado"))
            continue
        if numeros(pergunta["resposta"]) - numeros(b.get("resposta")):
            rever.append((pergunta["id"], f"números diferentes: A={pergunta['resposta']!r} B={b.get('resposta')!r}"))
        elif not numeros(pergunta["resposta"]) and not mesmo_sentido(pergunta["resposta"], b.get("resposta")):
            rever.append((pergunta["id"], f"comparar o sentido: A={pergunta['resposta']!r} B={b.get('resposta')!r}"))
    for ident, motivo in rever:
        print(f"{ident}: {motivo}")
    automaticas = len(perguntas) - len({ident for ident, _ in rever})
    print(f"{automaticas} de {len(perguntas)} pergunta(s) confirmadas automaticamente; {len(rever)} ponto(s) a rever")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("acao", choices=["literal", "cegas", "compara"])
    parser.add_argument("--perguntas", type=Path, default=PERGUNTAS)
    parser.add_argument("--saida", type=Path)
    parser.add_argument("--respostas", type=Path)
    args = parser.parse_args()
    perguntas = ler(args.perguntas)
    if args.acao == "literal":
        return literal(perguntas)
    if args.acao == "cegas":
        if not args.saida:
            sys.exit("cegas precisa de --saida")
        return cegas(perguntas, args.saida)
    if not args.respostas:
        sys.exit("compara precisa de --respostas")
    return compara(perguntas, args.respostas)


if __name__ == "__main__":
    raise SystemExit(main())
