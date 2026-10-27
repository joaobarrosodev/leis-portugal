"""Verificação do conjunto de avaliação (`avaliacao/perguntas.jsonl`).

- `literal`: confirma que o excerto de cada pergunta está, letra a letra, no artigo citado
  (na data de referência, para as temporais; no diploma alterador, nas `texto_alterado` com
  `alterado: true`) e que os números da resposta estão no excerto.
- `cegas --saida F`: escreve a entrada da sessão B (verificação às cegas): pergunta, data e
  texto do(s) artigo(s), sem a resposta certa nem o tipo. Nas perguntas sem resposta vai o
  artigo distrator; nas compostas vão todos os artigos; nas de texto alterado vai o artigo
  original e as passagens dos diplomas que o DRE regista como alteradores.
- `compara --respostas F`: compara as respostas da sessão B com as da sessão A e lista as
  que não batem, para uma terceira revisão. Nas `premissa_errada`, os números da premissa
  falsa não contam (a resposta de A repete-os para os corrigir).

Formato das respostas da sessão B (uma por linha): `{"id", "responde": bool, "resposta",
"excerto", "ambigua": bool, "depende_de_outro": bool, "premissa_errada": bool,
"alterado": bool | null, "notas"}`.

Tipos e campos próprios (ver README): `composta` tem `fonte.artigos` e `excerto` em lista;
`premissa_errada` tem `premissa`; `texto_alterado` tem `alterado`, `alteradores` e, quando
`alterado`, `alterador` com o artigo do diploma alterador onde está a redação nova.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from comum import RAIZ, artigo, artigos, corpo, menciona_artigo, normalizar


PERGUNTAS = RAIZ / "avaliacao" / "perguntas.jsonl"


def ler(caminho: Path) -> list[dict]:
    return [json.loads(linha) for linha in caminho.read_text(encoding="utf-8").splitlines() if linha.strip()]


_ORTOGRAFIA = [("cç", "ç"), ("pç", "ç"), ("ct", "t"), ("pt", "t")]
_VAZIAS = set("ao aos as às com da das de do dos em na nas no nos os ou para pela pelas pelo pelos por que se uma um sob".split())


def numeros(texto: str) -> set[str]:
    """Os números de um texto, sem separadores de milhares nem casas decimais a zero
    (`(euro) 100 000 000,00` e `100 000 000 euros` dão o mesmo número)."""
    texto = re.sub(r"(?<=\d)[  .](?=\d{3}\b)", "", texto or "")
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


def artigos_da_composta(fonte: dict) -> list[dict]:
    """Cada artigo de uma pergunta composta com o diploma a que pertence (o da `fonte`, salvo indicação)."""
    base = {chave: fonte[chave] for chave in ("documento", "caminho", "titulo") if chave in fonte}
    return [{**base, **art} for art in fonte["artigos"]]


def excertos(pergunta: dict) -> list[str]:
    excerto = pergunta.get("excerto") or ""
    return list(excerto) if isinstance(excerto, list) else [excerto]


def fontes_a_confirmar(pergunta: dict) -> list[tuple[dict, str | None, str]]:
    """Os pares (artigo, data, excerto) em que o excerto tem de estar letra a letra."""
    if pergunta["tipo"] == "composta":
        return [(art, None, exc) for art, exc in zip(artigos_da_composta(pergunta["fonte"]), excertos(pergunta), strict=False)]
    if pergunta["tipo"] == "texto_alterado" and pergunta.get("alterado"):
        return [(pergunta["alterador"], None, pergunta["excerto"])]
    return [(pergunta["fonte"], data_do_texto(pergunta), pergunta["excerto"])]


def problemas_de_forma(pergunta: dict) -> list[str]:
    """Campos que cada tipo tem de ter."""
    tipo = pergunta["tipo"]
    problemas = []
    if tipo == "revogada" and not pergunta.get("revogado_por"):
        problemas.append("revogada sem `revogado_por`")
    if tipo == "composta":
        artigos_ = pergunta["fonte"].get("artigos") or []
        if not 2 <= len(artigos_) <= 3:
            problemas.append("composta deve ter 2 ou 3 artigos em `fonte.artigos`")
        if len(excertos(pergunta)) != len(artigos_):
            problemas.append("composta deve ter um excerto por artigo")
    if tipo == "premissa_errada" and not pergunta.get("premissa"):
        problemas.append("premissa_errada sem `premissa`")
    if tipo == "texto_alterado":
        if not isinstance(pergunta.get("alterado"), bool) or not pergunta.get("alteradores"):
            problemas.append("texto_alterado precisa de `alterado` (bool) e `alteradores`")
        if pergunta.get("alterado") and not (pergunta.get("alterador") or {}).get("artigo"):
            problemas.append("texto_alterado com `alterado: true` precisa de `alterador.artigo`")
    return problemas


def literal(perguntas: list[dict]) -> int:
    falhas = 0
    for pergunta in perguntas:
        problemas = problemas_de_forma(pergunta)
        if pergunta["tipo"] == "sem_resposta":
            if pergunta.get("fonte") or not pergunta.get("distrator"):
                problemas.append("sem resposta: deve ter distrator e nenhuma fonte")
        else:
            for fonte, data, excerto in fontes_a_confirmar(pergunta):
                texto = texto_da_fonte(fonte, data)
                if texto is None:
                    problemas.append(f"artigo {fonte['artigo']} não encontrado em {fonte['caminho']}")
                elif not excerto or normalizar(excerto) not in normalizar(texto):
                    problemas.append(f"o excerto não está no texto do artigo {fonte['artigo']}")
            em_falta = numeros(pergunta["resposta"]) - numeros(" ".join(excertos(pergunta))) - numeros(pergunta.get("premissa", ""))
            if pergunta["tipo"] not in ("revogada", "texto_alterado") and em_falta:
                problemas.append(f"números da resposta fora do excerto: {sorted(em_falta)}")
            if pergunta["tipo"] == "texto_alterado" and em_falta - numeros(" ".join(a["titulo"] for a in pergunta.get("alteradores", []))):
                problemas.append(f"números da resposta fora do excerto e dos títulos dos alteradores: {sorted(em_falta)}")
        if problemas:
            falhas += 1
            print(f"{pergunta['id']}: " + "; ".join(problemas))
    print(f"{len(perguntas) - falhas} de {len(perguntas)} pergunta(s) passam a verificação literal")
    return 1 if falhas else 0


def entrada_artigo(fonte: dict, data: str | None) -> dict:
    return {
        "artigo": fonte["artigo"],
        "epigrafe": fonte.get("epigrafe", ""),
        "texto": texto_da_fonte(fonte, data),
    }


def passagens_do_alterador(alterador: dict, fonte: dict, maximo: int = 4) -> list[dict]:
    """Os artigos do diploma alterador que falam no artigo em causa; se nenhum fala, os que falam no
    diploma original. É o que a sessão B recebe para decidir se o artigo mudou."""
    todos = artigos(corpo((RAIZ / alterador["caminho"]).read_text(encoding="utf-8")))
    numero = fonte["artigo"].split("::")[-1]
    escolhidos = [a for a in todos if menciona_artigo(a.texto, numero)]
    if not escolhidos:
        referencia = fonte["titulo"].split("n.º")[-1].strip()
        escolhidos = [a for a in todos if referencia and referencia in a.texto]
    return [{"artigo": a.chave, "epigrafe": a.epigrafe, "texto": a.texto} for a in escolhidos[:maximo]]


def cegas(perguntas: list[dict], saida: Path) -> int:
    with saida.open("w", encoding="utf-8") as ficheiro:
        for pergunta in perguntas:
            entrada = {"id": pergunta["id"], "pergunta": pergunta["pergunta"], "data_referencia": pergunta["data_referencia"]}
            if pergunta["tipo"] == "composta":
                fonte = pergunta["fonte"]
                entrada["fonte"] = {
                    "titulo": fonte["titulo"],
                    "artigos": [
                        {**entrada_artigo(art, None), **({"titulo": art["titulo"]} if art.get("titulo") != fonte["titulo"] else {})}
                        for art in artigos_da_composta(fonte)
                    ],
                }
            else:
                fonte = pergunta.get("fonte") or pergunta["distrator"]
                entrada["fonte"] = {"titulo": fonte["titulo"], **entrada_artigo(fonte, data_do_texto(pergunta))}
                if pergunta["tipo"] == "revogada":
                    revogador = pergunta["revogado_por"]
                    entrada["fonte"]["estado"] = f"Revogado por {revogador['titulo']} (em vigor desde {revogador['data']})"
                if pergunta["tipo"] == "texto_alterado":
                    entrada["fonte"]["estado"] = "Texto publicado no Diário da República; o DRE regista alterações posteriores, sem consolidação"
                    entrada["alteracoes"] = [
                        {"titulo": alt["titulo"], "data": alt.get("data"), "artigos": passagens_do_alterador(alt, fonte)}
                        for alt in pergunta["alteradores"]
                    ]
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
        if b.get("ambigua") or (b.get("depende_de_outro") and not pergunta.get("depende_de_outro") and pergunta["tipo"] != "composta"):
            rever.append((pergunta["id"], f"B assinalou: {b.get('notas', '')}"))
        if pergunta["tipo"] == "sem_resposta":
            if b.get("responde"):
                rever.append((pergunta["id"], "B respondeu a uma pergunta sem resposta"))
            continue
        if pergunta["tipo"] == "premissa_errada" and not b.get("premissa_errada"):
            rever.append((pergunta["id"], "B não assinalou a premissa errada"))
        if pergunta["tipo"] != "premissa_errada" and b.get("premissa_errada"):
            rever.append((pergunta["id"], f"B achou a premissa errada: {b.get('notas', '')}"))
        if pergunta["tipo"] == "texto_alterado" and b.get("alterado") is not pergunta["alterado"]:
            rever.append((pergunta["id"], f"alterado: A={pergunta['alterado']} B={b.get('alterado')}; {b.get('notas', '')}"))
        if not b.get("responde"):
            rever.append((pergunta["id"], "B não encontrou resposta no artigo"))
            continue
        if pergunta["tipo"] == "revogada":
            if "revog" not in (b.get("resposta") or "").lower():
                rever.append((pergunta["id"], "B não indicou que o diploma está revogado"))
            continue
        esperados = numeros(pergunta["resposta"]) - numeros(pergunta.get("premissa", ""))
        if esperados - numeros(b.get("resposta")):
            rever.append((pergunta["id"], f"números diferentes: A={pergunta['resposta']!r} B={b.get('resposta')!r}"))
        elif not esperados and not mesmo_sentido(pergunta["resposta"], b.get("resposta")):
            rever.append((pergunta["id"], f"comparar o sentido: A={pergunta['resposta']!r} B={b.get('resposta')!r}"))
    for ident, motivo in rever:
        print(f"{ident}: {motivo}")
    automaticas = len(perguntas) - len({ident for ident, _ in rever})
    print(f"{automaticas} de {len(perguntas)} pergunta(s) confirmadas automaticamente; {len(rever)} ponto(s) a rever")
    return 0


def escolher(perguntas: list[dict], tipos: str | None, desde: str | None) -> list[dict]:
    """Só os tipos pedidos e só a partir da pergunta com o id `desde` (pela ordem do ficheiro)."""
    if desde:
        posicao = next((i for i, p in enumerate(perguntas) if p["id"] == desde), None)
        if posicao is None:
            sys.exit(f"não há pergunta com o id {desde}")
        perguntas = perguntas[posicao:]
    if tipos:
        perguntas = [p for p in perguntas if p["tipo"] in tipos.split(",")]
    return perguntas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("acao", choices=["literal", "cegas", "compara"])
    parser.add_argument("--perguntas", type=Path, default=PERGUNTAS)
    parser.add_argument("--saida", type=Path)
    parser.add_argument("--respostas", type=Path)
    parser.add_argument("--tipos", help="só estes tipos, separados por vírgulas")
    parser.add_argument("--desde", help="só a partir da pergunta com este id (pela ordem do ficheiro)")
    args = parser.parse_args()
    perguntas = escolher(ler(args.perguntas), args.tipos, args.desde)
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
