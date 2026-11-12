"""O pedido ao LLM para os originais sem artigos identificados (texto corrido).

`juntar.py` e `llm_completo.py` recusam estes diplomas ("original sem artigos: a resposta não tem
onde encaixar"): portarias com "1.º, 2.º" em texto corrido, resoluções, despachos, bases. Aqui o
original é um bloco de texto corrido dividido em **unidades**, os parágrafos separados por linha em
branco, numeradas 1..N. O pedido leva

- o texto do original, unidade a unidade (`{{7}}` antes de cada uma);
- o texto de todos os diplomas que o alteram, por ordem de aplicação (como em `llm_completo.py`);
- a ordem de ler todas as instruções dirigidas ao original e devolver (a) as **substituições**
  (`de`, `ate`, `texto`: as unidades de `de` a `ate` passam a ser `texto`, que é vazio quando
  desaparecem) e (b) as **inserções** (`depois_de`, `texto`).

A resposta passa pela mesma verificação letra a letra de `llm_completo.verificar_resposta` (cada
parágrafo vem de um alterador ou do original) e as posições têm de existir e não se sobrepor. O
consolidado é o texto do original com as unidades trocadas, cada troca seguida de uma nota
"> Alterado pelo/a …" como nos artigos (o `cegas.py` tira-a antes da verificação às cegas).
Escreve `piloto/<caminho>.md` e `.alteracoes.json`, e `llm/juntados-corrido.jsonl`, que o `cegas.py`
lê. Nada em `data/` é alterado.

Uso:
    python consolidacao/llm_corrido.py amostra N [--semente 1] [--max-chars 120000] --saida F
    python consolidacao/llm_corrido.py proximos N [--max-chars 120000] --saida F
    python consolidacao/llm_corrido.py pedidos IDS_FICHEIRO PASTA [--por-ficheiro 3]
    python consolidacao/llm_corrido.py importar FICHEIRO...
    python consolidacao/llm_corrido.py juntar
"""

from __future__ import annotations

import argparse
import json
from difflib import SequenceMatcher
import random
import re
from dataclasses import asdict
from pathlib import Path

from aplicar import Registo
from cegas import _texto_alterador
from consolidar import PILOTO, _markdown
from llm import _alteradores as _alteradores_da_selecao
from llm_completo import _alteradores, _aprovados
import texto as texto_mod
from texto import RAIZ, Corpo, front_matter, publicado
from verificar import _REVOGADO, _plano


PASTA = RAIZ / "consolidacao"
CORRIDO = PASTA / "llm" / "corrido"
JUNTADOS = PASTA / "llm" / "juntados-corrido.jsonl"
METODO = "piloto da fase 2 (consolidacao/llm_corrido.py: texto corrido por unidades, pelo LLM), sem valor oficial"
MOTIVO = "original sem artigos"

SISTEMA = """Aplicas alterações legislativas portuguesas ao texto de um diploma que não tem artigos
identificados (portaria, resolução, despacho, bases em texto corrido).

Recebes (1) o texto do diploma original dividido em UNIDADES numeradas, os parágrafos separados
por linha em branco, cada uma precedida de `{{N}}`, e (2) o texto de cada diploma que o altera, por
ordem de aplicação. Lês TODAS as instruções desses diplomas dirigidas ao original (substituições,
aditamentos, revogações, retificações, renumerações, epígrafes) e devolves o que tem de mudar no
original, e só isso.

Regras:
- Uma instrução que altera OUTRO diploma ("o artigo 5.º do Decreto-Lei X, na redação dada pelo
  [original]") não é do original: ignora-a. Revogação condicional ("na parte em que contrariem")
  não se aplica ao texto.
- Há dois tipos de mudança. "substituicoes": as unidades de `de` a `ate` (inclusive; `de` = `ate`
  quando é uma só) passam a ser "texto", parágrafos separados por uma linha em branco, que é "" se
  as unidades desaparecem (artigo eliminado, ponto eliminado). "insercoes": o "texto" vai a seguir
  à unidade `depois_de`. Escolhe o menor intervalo possível; só inclui unidades que mudam ou que
  ficam a meio de uma mudança (um ponto "3.º" com epígrafe e corpo são três unidades: se só muda o
  corpo, substitui só a unidade do corpo).
- O texto novo copia-se letra a letra do diploma que altera; o que a instrução não muda copia-se
  letra a letra do texto atual (numa substituição que muda só uma frase, o "texto" é a unidade
  inteira com a frase trocada). Não corrijas grafia, pontuação nem gralhas. Sem aspas «»
  nem o tipo de nota "(redação do …)".
- "[...]", "..." ou "(...)" numa nova redação querem dizer "fica o texto atual dessa unidade".
- Uma unidade revogada fica com a sua numeração e "(Revogado.)" (ou "(Revogada.)"), por exemplo
  "3.º - (Revogado.)"; as unidades que formavam o ponto (epígrafe, corpo) entram na mesma
  substituição. Uma alínea: "a) (Revogada.)".
- Se um artigo, número ou ponto novo se acrescenta, é uma inserção; renumera as unidades que a
  instrução manda renumerar (cada uma é uma substituição ou entra numa substituição maior).
- O diploma original pode ser revogado por inteiro: se a instrução revoga todo o texto, diz em
  "nao_aplicavel" e não devolvas nada.
- Se uma instrução não se puder aplicar com segurança (alvo ambíguo, texto que não existe no texto
  atual, anexo ou quadro que só vem em imagem, alteração que não é textual), não a inventes: diz em
  "nao_aplicavel" qual é e porquê. Se tudo ficou aplicado, "nao_aplicavel" é null.
- "alterador" é o número (1, 2, …) do diploma que altera de que vem a mudança.
"""

FORMATO = """
## Formato da resposta
Escreve (com a ferramenta Write) um ficheiro JSON com uma lista, um objeto por diploma do pedido (todos), assim:
`{"id": "<id>", "substituicoes": [{"de": 3, "ate": 5, "texto": "...", "alterador": 1}], "insercoes": [{"depois_de": 8, "texto": "...", "alterador": 2}], "nao_aplicavel": null ou "texto", "instrucoes": ["resumo curto de cada instrução dirigida ao original e o que fizeste"]}`
Só usas o pedido; não leias mais nada. O "texto" é o conteúdo novo (sem `{{N}}`), parágrafos separados por uma linha em branco, copiado letra a letra do alterador ou do texto atual. As listas são [] quando não há nada para fazer. Confirma no fim que o JSON é válido e que respondeste a todos os "<<<DIPLOMA id=...>>>".
"""

_NOTA = re.compile(r"^> (?:Alterado|Aditado|Revogado|Retificado) pelo/a .*$", re.M)


def itens(texto: str) -> list[tuple[str, int | None, str]]:
    """O texto em itens `(tipo, número, texto)`: "u" para uma unidade (parágrafo, numerada de 1)
    e "s" para o resto (separadores e espaço); `"".join(t for _, _, t in itens(x)) == x`."""
    resultado, n = [], 0
    for i, parte in enumerate(re.split(r"(\n{2,})", texto)):
        if i % 2 == 0 and parte.strip():
            n += 1
            resultado.append(("u", n, parte))
        elif parte:
            resultado.append(("s", None, parte))
    return resultado


def unidades(texto: str) -> list[str]:
    return [t for tipo, _, t in itens(texto) if tipo == "u"]


def _registo_base(registo: dict) -> str:
    return publicado(RAIZ / registo["path"])


def pedido(registo: dict) -> tuple[str, int]:
    """O texto do pedido e o seu tamanho em caracteres."""
    partes = [f"# Diploma original: {registo['title']}", "", "## Texto do original, por unidades"]
    for n, texto in enumerate(unidades(_registo_base(registo)), 1):
        partes += [f"{{{{{n}}}}}", texto.strip(), ""]
    partes.append("## Diplomas que alteram o original, por ordem de aplicação")
    for n, a in enumerate(_alteradores(registo), 1):
        texto, completo = _texto_alterador(a["path"], registo["title"])
        aviso = "" if completo else " (só os artigos que mencionam o original)"
        partes += [f"### Alterador {n}: {a.get('title') or a['id']}{aviso}", texto.strip(), ""]
    texto = "\n".join(partes)
    return texto, len(texto)


def _carregar(nome: str) -> dict[str, dict]:
    return {r["id"]: r for r in map(json.loads, (PASTA / nome).read_text(encoding="utf-8").splitlines())}


def candidatos() -> list[str]:
    """Os pendentes cujo original não tem artigos identificados, ainda sem resposta nem aprovação
    às cegas, por ordem de citações recebidas."""
    selecao, estados = _carregar("selecao-escala.jsonl"), _carregar("resultados-escala.jsonl")
    feitos = {f.stem.replace("_", ":") for f in CORRIDO.glob("pt_*.json")} if CORRIDO.exists() else set()
    bons = _aprovados()
    ids = [r["id"] for r in map(json.loads, (PASTA / "pendentes-escala.jsonl").read_text(encoding="utf-8").splitlines())]
    ids = [i for i in ids if str(estados[i].get("motivo") or "").startswith(MOTIVO) and i not in feitos and i not in bons]
    return sorted((i for i in ids if _alteradores(selecao[i])), key=lambda i: (-selecao[i].get("citacoes", 0), i))


def _escolher(ids: list[str], n: int, max_chars: int) -> list[str]:
    selecao = _carregar("selecao-escala.jsonl")
    escolhidos, grandes = [], 0
    for i in ids:
        if len(escolhidos) == n:
            break
        if pedido(selecao[i])[1] > max_chars:
            grandes += 1
            continue
        escolhidos.append(i)
    print(f"{len(escolhidos)} escolhidos de {len(ids)} candidatos; {grandes} saltados por terem mais de {max_chars} caracteres de pedido")
    return escolhidos


def amostra(n: int, semente: int, max_chars: int) -> list[str]:
    ids = candidatos()
    random.Random(semente).shuffle(ids)
    return _escolher(ids, n, max_chars)


def pedidos(ids: list[str], por_ficheiro: int, pasta: Path) -> None:
    selecao = _carregar("selecao-escala.jsonl")
    pasta.mkdir(parents=True, exist_ok=True)
    for n, inicio in enumerate(range(0, len(ids), por_ficheiro), 1):
        blocos = [f"<<<DIPLOMA id={i}>>>\n{pedido(selecao[i])[0]}\n<<<FIM DO DIPLOMA id={i}>>>" for i in ids[inicio : inicio + por_ficheiro]]
        (pasta / f"pedido-{n:03d}.md").write_text("\n\n".join(blocos), encoding="utf-8")
    (pasta / "REGRAS.md").write_text(SISTEMA + FORMATO, encoding="utf-8")
    print(f"{len(ids)} diplomas em {(len(ids) + por_ficheiro - 1) // por_ficheiro} pedidos em {pasta}")


_NUMERACAO = re.compile(r"^(?:\d+\s*\.?\s*[º°o]?(?:\s*-\s*[A-Z]{1,2}\b)?\s*[-–.]?\s+|[a-z]{1,3}\)\s+|\(\w{1,3}\)\s+)")


def _tokens(texto: str) -> list[str]:
    return re.findall(r"\w+|[^\w\s]", _plano(texto))


def _na_fonte(p: str, fontes: list[str]) -> bool:
    plano = _plano(p)
    return any(plano in f for f in fontes) or any(_plano(_NUMERACAO.sub("", p.strip())) in f for f in fontes)


def verificar_texto(mudanca: dict, antigo: list[str], fontes: list[str], fontes_tokens: list[str]) -> list[str]:
    """Cada parágrafo do texto novo vem, letra a letra, de um alterador ou do original (com ou sem
    a numeração). Um parágrafo do original com uma frase trocada ("onde se lê … deve ler-se …")
    passa se o resto é o texto antigo e o que mudou está num alterador ou no original."""
    problemas = []
    for p in (x.strip() for x in (mudanca.get("texto") or "").split("\n\n") if x.strip()):
        if _REVOGADO.match(p) or _na_fonte(p, fontes):
            continue
        melhor = max(antigo, key=lambda a: SequenceMatcher(None, _plano(a), _plano(p), autojunk=False).ratio(), default="")
        a, b = _tokens(melhor), _tokens(p)
        if not melhor or SequenceMatcher(None, a, b, autojunk=False).ratio() < 0.6:
            problemas.append(f"parágrafo que não está no alterador nem no original: {p[:80]}")
            continue
        for tipo, i1, i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            fragmento = " ".join(b[j1:j2])
            if tipo in ("replace", "insert") and not any(fragmento in f for f in fontes_tokens):
                problemas.append(f"troca que não está no alterador nem no original: «{fragmento[:60]}» em {p[:50]}")
    return problemas


def verificar_resposta(resposta: dict, selecao: dict) -> list[str]:
    fontes = [_plano(publicado(RAIZ / a["path"])) for a in _alteradores_da_selecao(selecao) if a.get("path")]
    todas = unidades(_registo_base(selecao))
    fontes.append(_plano(_registo_base(selecao)))
    tokens = [" ".join(_tokens(f)) for f in fontes]
    problemas = []
    for s in resposta.get("substituicoes") or []:
        antigo = todas[s["de"] - 1 : s["ate"]] if isinstance(s.get("de"), int) and isinstance(s.get("ate"), int) else todas
        problemas += [f"substituição {s.get('de')}-{s.get('ate')}: {x}" for x in verificar_texto(s, antigo, fontes, tokens)]
    for s in resposta.get("insercoes") or []:
        problemas += [f"inserção depois de {s.get('depois_de')}: {x}" for x in verificar_texto(s, [], fontes, tokens)]
    return problemas


def _validar(resposta: dict, n: int) -> list[str]:
    """Posições que existem e não se sobrepõem."""
    problemas, ocupadas = [], set()
    for s in resposta.get("substituicoes") or []:
        de, ate = s.get("de"), s.get("ate")
        if not (isinstance(de, int) and isinstance(ate, int) and 1 <= de <= ate <= n):
            problemas.append(f"substituição com posições inválidas: {de}-{ate} (o original tem {n} unidades)")
        elif ocupadas & set(range(de, ate + 1)):
            problemas.append(f"substituições que se sobrepõem em {de}-{ate}")
        else:
            ocupadas |= set(range(de, ate + 1))
    for s in resposta.get("insercoes") or []:
        k = s.get("depois_de")
        if not (isinstance(k, int) and 1 <= k <= n):
            problemas.append(f"inserção com posição inválida: {k} (o original tem {n} unidades)")
        elif k in ocupadas and not any(x.get("ate") == k for x in resposta.get("substituicoes") or []):
            problemas.append(f"inserção a meio de uma substituição, depois de {k}")
    return problemas


def importar(ficheiros: list[Path]) -> None:
    selecao = _carregar("selecao-escala.jsonl")
    CORRIDO.mkdir(parents=True, exist_ok=True)
    contagem: dict[str, int] = {}
    for f in ficheiros:
        for resposta in json.loads(f.read_text(encoding="utf-8")):
            i = resposta["id"]
            resposta |= {"modelo": resposta.get("modelo") or "claude-opus-5-5", "pedido": "corrido"}
            resposta.setdefault("substituicoes", [])
            resposta.setdefault("insercoes", [])
            mudancas = resposta["substituicoes"] + resposta["insercoes"]
            resposta["problemas"] = _validar(resposta, len(unidades(_registo_base(selecao[i])))) + verificar_resposta(resposta, selecao[i])
            tipo = "com problemas" if resposta["problemas"] else "sem alterações" if not mudancas else "sem problemas"
            contagem[tipo] = contagem.get(tipo, 0) + 1
            (CORRIDO / (i.replace(":", "_") + ".json")).write_text(json.dumps(resposta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(contagem)


def _nota(operacao: str, ligacao: str, data: str) -> str:
    return f"> {operacao} pelo/a {ligacao}, publicado em {data}."


def _junto(resposta: dict, registo: dict) -> dict:
    linha = {"id": registo["id"], "title": registo["title"], "path": registo["path"], "estado_regras": "corrido"}
    base = _registo_base(registo)
    todos = itens(base)
    n = len(unidades(base))
    alteradores = _alteradores(registo)
    por_numero = dict(enumerate(alteradores, 1))
    citados: dict[str, dict] = {}

    def ligacao_de(m: dict) -> tuple[str, str]:
        numeros = sorted({int(x) for x in re.findall(r"\d+", str(m.get("alterador") or ""))} & set(por_numero)) or list(por_numero)
        escolhidos = [por_numero[k] for k in numeros]
        ligacoes = []
        for a in escolhidos:
            url = (front_matter((RAIZ / a["path"]).read_text(encoding="utf-8")).get("source") or {}).get("official_url") or ""
            ligacoes.append(f"[{a['title']}]({url})" if url else a["title"])
            citados[a["id"]] = a
        return " e ".join(ligacoes), max((a.get("publication_date") or "" for a in escolhidos), default="")

    texto_de = {n_: t for tipo, n_, t in todos if tipo == "u"}
    substituicoes = {}
    for s in resposta["substituicoes"]:
        antigo = "\n\n".join(texto_de[k].strip() for k in range(s["de"], s["ate"] + 1))
        novo = "\n\n".join(p.strip() for p in (s.get("texto") or "").split("\n\n") if p.strip())
        if novo != antigo:  # uma troca por texto igual não é mudança
            substituicoes[s["de"]] = s | {"antigo": antigo, "novo": novo}
    insercoes: dict[int, list[dict]] = {}
    for s in resposta["insercoes"]:
        if (s.get("texto") or "").strip():
            insercoes.setdefault(s["depois_de"], []).append(s)
    if not substituicoes and not insercoes:
        return linha | {"estado": "não junto", "motivo": "a resposta não muda nada no texto"}

    registos: list[Registo] = []
    saida: list[str] = []
    saltar_ate = 0  # dentro de uma substituição: as unidades até esta já entraram no texto novo

    def inserir_depois_de(k: int) -> None:
        for ins in insercoes.get(k, []):
            ligacao, data = ligacao_de(ins)
            novo = "\n\n".join(p.strip() for p in ins["texto"].split("\n\n") if p.strip())
            saida.append("\n\n" + novo + "\n\n" + _nota("Aditado", ligacao, data))
            registos.append(Registo(f"depois da unidade {ins['depois_de']}", "aditar", "llm", "", novo, "", "", metodo="llm"))

    for tipo, k, texto in todos:
        if tipo == "s":
            if not saltar_ate:
                saida.append(texto)
            continue
        if saltar_ate:
            if k == saltar_ate:
                saltar_ate = 0
                inserir_depois_de(k)
            continue
        if k in substituicoes:
            s = substituicoes[k]
            ligacao, data = ligacao_de(s)
            partes = ([s["novo"]] if s["novo"] else []) + [_nota("Alterado", ligacao, data)]
            saida.append("\n\n".join(partes))
            registos.append(Registo(f"unidades {s['de']}-{s['ate']}", "substituir" if s["novo"] else "remover", "llm", s["antigo"], s["novo"], "", "", metodo="llm"))
            if s["ate"] > k:
                saltar_ate = s["ate"]
                continue
        else:
            saida.append(texto)
        inserir_depois_de(k)
    consolidado = "".join(saida)

    aplicados = [{"id": a["id"], "title": a["title"], "publication_date": a.get("publication_date")} for a in citados.values()]
    destino = PILOTO / Path(registo["path"]).relative_to("data")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.with_suffix(".alteracoes.json").write_text(
        json.dumps([asdict(r) | {"diploma": registo["id"], "alterador": ";".join(citados)} for r in registos], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    destino.write_text(_markdown(registo, aplicados, Corpo(segmentos=[consolidado.split("\n")]), False, METODO), encoding="utf-8")
    linha |= {"estado": "aplicado com LLM", "consolidado": str(destino.relative_to(RAIZ)), "artigos_llm": len(registos), "artigos_regras": 0,
              "alteradores_ids": [a["id"] for a in aplicados], "alteradores_vistos": [a["id"] for a in alteradores], "pedido": "corrido", "unidades": n}
    if resposta.get("nao_aplicavel"):
        linha["parcial"] = resposta["nao_aplicavel"]
    return linha


def juntar() -> None:
    selecao = _carregar("selecao-escala.jsonl")
    anteriores, excluidos, grandes = texto_mod.linhas_anteriores(JUNTADOS), texto_mod.exclusoes(), texto_mod.gigantes()
    linhas = []
    for f in sorted(CORRIDO.glob("pt_*.json")):
        resposta = json.loads(f.read_text(encoding="utf-8"))
        base = {"id": resposta["id"], "title": selecao[resposta["id"]]["title"], "estado": "não junto"}
        if resposta["id"] in grandes and resposta["id"] in anteriores:
            linhas.append(anteriores[resposta["id"]])  # juntado por llm_gigantes.py; não se reescreve
        elif resposta["id"] in excluidos:
            linhas.append(base | {"motivo": excluidos[resposta["id"]]})
        elif resposta["problemas"]:
            linhas.append(base | {"motivo": "a resposta não passou a verificação letra a letra: " + "; ".join(resposta["problemas"])[:300]})
        elif not resposta["substituicoes"] and not resposta["insercoes"]:
            linhas.append(base | {"motivo": "a resposta não muda nada: " + str(resposta.get("nao_aplicavel"))[:200]})
        else:
            linhas.append(_junto(resposta, selecao[resposta["id"]]))
    JUNTADOS.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas), encoding="utf-8")
    juntados = [l for l in linhas if l["estado"] == "aplicado com LLM"]
    print(f"{len(linhas)} respostas: {len(juntados)} juntadas ({sum('parcial' in l for l in juntados)} com instruções por aplicar), {len(linhas) - len(juntados)} não juntas")
    for l in linhas:
        if l["estado"] != "aplicado com LLM":
            print(f"   {l['title']}: {l['motivo']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="comando", required=True)
    for nome in ("amostra", "proximos"):
        a = sub.add_parser(nome)
        a.add_argument("n", type=int)
        a.add_argument("--max-chars", type=int, default=120_000)
        a.add_argument("--saida", type=Path, required=True)
        if nome == "amostra":
            a.add_argument("--semente", type=int, default=1)
    p = sub.add_parser("pedidos")
    p.add_argument("ids", type=Path)
    p.add_argument("pasta", type=Path)
    p.add_argument("--por-ficheiro", type=int, default=3)
    i = sub.add_parser("importar")
    i.add_argument("ficheiros", type=Path, nargs="+")
    sub.add_parser("juntar")
    args = parser.parse_args()
    if args.comando == "amostra":
        args.saida.write_text("\n".join(amostra(args.n, args.semente, args.max_chars)) + "\n", encoding="utf-8")
    elif args.comando == "proximos":
        args.saida.write_text("\n".join(_escolher(candidatos(), args.n, args.max_chars)) + "\n", encoding="utf-8")
    elif args.comando == "pedidos":
        pedidos(args.ids.read_text(encoding="utf-8").split(), args.por_ficheiro, args.pasta)
    elif args.comando == "importar":
        importar(args.ficheiros)
    else:
        juntar()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
