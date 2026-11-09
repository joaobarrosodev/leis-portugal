"""O pedido ao LLM com todas as instruções do diploma e o texto atual inteiro.

O pedido de `llm.py` leva só os artigos que as instruções por aplicar nomeiam. Nos diplomas
que a verificação às cegas recusou (ver `README.md`, "Rendimento do LLM"), a causa mais comum
é uma instrução que nenhum passo viu: o artigo que ela visa ficou igual ao original e o LLM
nunca o recebeu. Aqui o pedido leva

- o texto atual do original, artigo a artigo, já com o que as regras aplicaram (os artigos que
  elas tocaram vêm assinalados);
- o texto de todos os diplomas que o alteram, por ordem de aplicação (como na entrada às cegas:
  inteiros até 60 mil caracteres, senão só os artigos que mencionam o original);
- a ordem de ler **todas** as instruções dirigidas ao original e devolver os artigos que ainda
  têm de mudar, com o diploma de que vem cada um.

A resposta passa pela mesma verificação letra a letra de `llm.py` e junta-se sobre o consolidado
das regras, sem recusar os artigos que as regras já tinham alterado (o LLM viu a redação delas).
Escreve `llm/juntados-completo.jsonl`, que `cegas.py --escala` e `acervo.py` leem por cima de
`llm/juntados-escala.jsonl`.

Uso:
    python consolidacao/llm_completo.py amostra N [--semente 1] [--max-chars 150000]
    python consolidacao/llm_completo.py pedidos IDS_FICHEIRO [--por-ficheiro 3]
    python consolidacao/llm_completo.py importar FICHEIRO...
    python consolidacao/llm_completo.py juntar
"""

from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import asdict
from pathlib import Path

from aplicar import _NOMES, Registo
from cegas import VERIFICACAO, _texto_alterador
from consolidar import PILOTO, _markdown, processar
from juntar import METODO, _aplicar_resposta
from llm import ESQUEMA
from llm import _alteradores as _alteradores_da_selecao
from texto import RAIZ, front_matter, publicado
from verificar import _REVOGADO, _plano


PASTA = RAIZ / "consolidacao"
COMPLETO = PASTA / "llm" / "completo"
JUNTADOS = PASTA / "llm" / "juntados-completo.jsonl"

SISTEMA = """Aplicas alterações legislativas portuguesas ao texto de um diploma.

Recebes (1) o texto atual do diploma original, artigo a artigo (alguns já alterados por um
programa, assinalados), e (2) o texto de cada diploma que o altera, por ordem de aplicação.
Lês TODAS as instruções desses diplomas dirigidas ao original (substituições, aditamentos,
revogações, retificações, renumerações, epígrafes) e devolves a nova redação de cada artigo
que, depois de todas, ainda tem de mudar em relação ao texto atual, e só desses.

Regras:
- Uma instrução que altera OUTRO diploma ("o artigo 5.º do Decreto-Lei X, na redação dada pelo
  [original]") não é do original: ignora-a. Revogação condicional ("na parte em que contrariem")
  não se aplica ao texto.
- O texto novo copia-se letra a letra do diploma que altera; o que a instrução não muda
  copia-se letra a letra do texto atual. Não corrijas grafia, pontuação nem gralhas.
- "[...]", "..." ou "(...)" numa nova redação querem dizer "fica o texto atual dessa unidade".
  "[Anterior n.º 2]" quer dizer que o antigo n.º 2 passa para aqui com o novo número.
- Um artigo revogado fica com o corpo "(Revogado.)"; um número "N - (Revogado.)"; uma alínea
  "a) (Revogada.)". Uma instrução que revoga uma lista de artigos dá um elemento por artigo.
- Um elemento de "artigos" por artigo: a chave tal como a recebes ("3.º" ou "Anexo …::3.º"; um
  artigo novo leva a chave que a instrução lhe dá), a epígrafe, o corpo inteiro do artigo
  (parágrafos separados por uma linha em branco, sem o título "Artigo N.º") e "alterador", o
  número (1, 2, …) do diploma que altera de que vem a mudança.
- Um artigo que a instrução elimina por completo (por exemplo, "é eliminado o artigo 12.º" e os
  seguintes são renumerados) ou que deixa de existir com a chave que tinha depois de uma
  renumeração (o antigo 14.º que passou a 13.º) vai em "removidos", a lista das chaves, e não em
  "artigos". Um artigo apenas revogado ("(Revogado.)") continua em "artigos".
- Se uma instrução não se puder aplicar com segurança (alvo ambíguo, texto que não existe no
  texto atual, anexo ou quadro que só vem em imagem, alteração que não é textual), não a
  inventes: diz em "nao_aplicavel" qual é e porquê. Se tudo ficou aplicado, "nao_aplicavel" é null.
"""

SISTEMA_RESPOSTA = ESQUEMA | {
    "properties": ESQUEMA["properties"] | {
        "artigos": {"type": "array", "items": {"type": "object", "required": ["chave", "epigrafe", "texto", "alterador"]}},
    }
}

FORMATO = """
## Formato da resposta
Escreve (com a ferramenta Write) um ficheiro JSON com uma lista, um objeto por diploma do pedido (todos), assim:
`{"id": "<id>", "artigos": [{"chave": "...", "epigrafe": "...", "texto": "...", "alterador": 1}], "removidos": ["chave", ...], "nao_aplicavel": null ou "texto", "instrucoes": ["resumo curto de cada instrução do original e o que fizeste"]}`
Só usas o pedido; não leias mais nada. O "texto" de cada artigo é o corpo inteiro (sem o título "Artigo N.º"), parágrafos separados por uma linha em branco, copiado letra a letra do alterador ou do texto atual. "removidos" é [] quando nenhum artigo desaparece. Confirma no fim que o JSON é válido e que respondeste a todos os "<<<DIPLOMA id=...>>>".
"""

_NUMERACAO = re.compile(r"^(?:\d+[-–.\s]*|[a-z]\))\s*")
_NOTA = re.compile(r"^> (?:Alterado|Aditado|Revogado|Retificado) pelo/a .*$", re.M)


def verificar_resposta(resultado: dict, selecao: dict) -> list[str]:
    """Como `llm.verificar_resposta`: cada parágrafo vem, letra a letra, de um alterador ou do
    texto original. Uma renumeração (o corpo antigo passa a "1 - …") conta: tira-se a numeração
    do parágrafo antes de o procurar."""
    alteradores = [_plano(publicado(RAIZ / a["path"])) for a in _alteradores_da_selecao(selecao) if a.get("path")]
    original = _plano(publicado(RAIZ / selecao["path"]))
    problemas = []

    def vem_de_algum(p: str) -> bool:
        return any(p in a for a in alteradores) or p in original

    for artigo in resultado.get("artigos", []):
        for p in (x.strip() for x in artigo["texto"].split("\n\n") if x.strip()):
            if _REVOGADO.match(p) or vem_de_algum(_plano(p)) or vem_de_algum(_plano(_NUMERACAO.sub("", p))):
                continue
            problemas.append(f"{artigo['chave']}: parágrafo que não está no alterador nem no original: {p[:80]}")
    return problemas


def _estado(registo: dict) -> dict:
    extra: dict = {}
    processar(registo, escrever=False, extra=extra)
    return extra


def _alteradores(registo: dict) -> list[dict]:
    return sorted((a for a in registo["alteradores"] if a.get("path") and a.get("text_quality") == "texto"), key=lambda a: a.get("ordem") or "")


def pedido(registo: dict, extra: dict) -> tuple[str, int]:
    """O texto do pedido e o seu tamanho em caracteres."""
    consolidado, tocados = extra["consolidado"], extra["tocados"]
    alteradores = _alteradores(registo)
    partes = [f"# Diploma original: {registo['title']}", ""]
    partes.append("## Texto atual do original, por artigos")
    for a in consolidado.artigos:
        sinal = " [já alterado por um programa]" if a.chave in tocados else ""
        partes += [f"### {a.chave}{sinal}", a.epigrafe, _NOTA.sub("", a.texto).strip(), ""]
    partes.append("## Diplomas que alteram o original, por ordem de aplicação")
    for n, a in enumerate(alteradores, 1):
        texto, completo = _texto_alterador(a["path"], registo["title"])
        aviso = "" if completo else " (só os artigos que mencionam o original)"
        partes += [f"### Alterador {n}: {a.get('title') or a['id']}{aviso}", texto.strip(), ""]
    texto = "\n".join(partes)
    return texto, len(texto)


def _falhados() -> list[str]:
    """Os diplomas das rondas de LLM (8 e 9) que a verificação às cegas não aprovou."""
    falhados = []
    for ronda in (8, 9):
        for f in sorted(VERIFICACAO.glob(f"saida-piloto-{ronda}-lote-*.jsonl")):
            artigos: dict[str, list[str]] = {}
            for linha in f.read_text(encoding="utf-8").splitlines():
                d = json.loads(linha)
                if "veredicto" in d:
                    artigos.setdefault(d["id"], []).append(d["veredicto"])
                    continue
                bom = (all(v == "certo" for v in artigos.get(d["id"], [])) and not d["instrucoes_em_falta"] and not d["artigos_em_falta"]
                       and not d["artigos_a_mais"] and str(d["fora_dos_artigos"]).lower().startswith("sem alter"))
                if not bom:
                    falhados.append(d["id"])
    return falhados


def _aprovados() -> set[str]:
    """Os diplomas que passaram a verificação às cegas em alguma ronda (6 em diante)."""
    bons: set[str] = set()
    for f in sorted(VERIFICACAO.glob("saida-piloto-*-lote-*.jsonl")):
        artigos: dict[str, list[str]] = {}
        for linha in f.read_text(encoding="utf-8").splitlines():
            d = json.loads(linha)
            if "veredicto" in d:
                artigos.setdefault(d["id"], []).append(d["veredicto"])
            elif (all(v == "certo" for v in artigos.get(d["id"], [])) and not d["instrucoes_em_falta"] and not d["artigos_em_falta"]
                  and not d["artigos_a_mais"] and str(d["fora_dos_artigos"]).lower().startswith("sem alter")):
                bons.add(d["id"])
    return bons


def pendentes_do_pedido(max_chars: int) -> list[str]:
    """Os diplomas de `pendentes-escala.jsonl` com artigos identificados que ainda não passaram às
    cegas nem foram ao pedido completo e cujo pedido cabe em `max_chars`, por ordem de citações."""
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines())}
    estados = {r["id"]: r for r in map(json.loads, (PASTA / "resultados-escala.jsonl").read_text(encoding="utf-8").splitlines())}
    feitos = {f.stem.replace("_", ":") for f in COMPLETO.glob("pt_*.json")} if COMPLETO.exists() else set()
    bons = _aprovados()
    vistos = {json.loads(l)["id"] for f in VERIFICACAO.glob("saida-piloto-*-lote-*.jsonl") for l in f.read_text(encoding="utf-8").splitlines()}
    ids = [r["id"] for r in map(json.loads, (PASTA / "pendentes-escala.jsonl").read_text(encoding="utf-8").splitlines())]
    candidatos = [i for i in ids if i not in bons and i not in feitos and not str(estados[i].get("motivo") or "").startswith("original sem artigos")]
    # primeiro os recusados às cegas, depois os outros
    candidatos.sort(key=lambda i: (i not in vistos, -selecao[i].get("citacoes", 0), i))
    return candidatos


def amostra(n: int, semente: int, max_chars: int) -> list[str]:
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines())}
    ids = sorted(set(_falhados()))
    random.Random(semente).shuffle(ids)
    escolhidos, grandes = [], 0
    for i in ids:
        if len(escolhidos) == n:
            break
        extra = _estado(selecao[i])
        if extra.get("consolidado") is None or not extra["consolidado"].artigos:
            continue
        if pedido(selecao[i], extra)[1] > max_chars:
            grandes += 1
            continue
        escolhidos.append(i)
    print(f"{len(ids)} falhados nas rondas 8 e 9; amostra de {len(escolhidos)} ao acaso (semente {semente}); {grandes} saltados por terem mais de {max_chars} caracteres de pedido")
    return escolhidos


def pedidos(ids: list[str], por_ficheiro: int, pasta: Path) -> None:
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines())}
    pasta.mkdir(parents=True, exist_ok=True)
    for n, inicio in enumerate(range(0, len(ids), por_ficheiro), 1):
        destino = pasta / f"pedido-{n:03d}.md"
        blocos = []
        for i in ids[inicio : inicio + por_ficheiro]:
            texto, _ = pedido(selecao[i], _estado(selecao[i]))
            blocos.append(f"<<<DIPLOMA id={i}>>>\n{texto}\n<<<FIM DO DIPLOMA id={i}>>>")
        destino.write_text("\n\n".join(blocos), encoding="utf-8")
    (pasta / "REGRAS.md").write_text(SISTEMA + FORMATO, encoding="utf-8")
    print(f"{len(ids)} diplomas em {(len(ids) + por_ficheiro - 1) // por_ficheiro} pedidos em {pasta}")


def importar(ficheiros: list[Path]) -> None:
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines())}
    COMPLETO.mkdir(parents=True, exist_ok=True)
    contagem: dict[str, int] = {}
    for f in ficheiros:
        for resposta in json.loads(f.read_text(encoding="utf-8")):
            i = resposta["id"]
            resposta |= {"modelo": resposta.get("modelo") or "claude-opus-5-5", "pedido": "completo"}
            resposta["problemas"] = verificar_resposta(resposta, selecao[i])
            tipo = "com problemas" if resposta["problemas"] else "sem alterações" if not resposta.get("artigos") else "sem problemas"
            contagem[tipo] = contagem.get(tipo, 0) + 1
            (COMPLETO / (i.replace(":", "_") + ".json")).write_text(json.dumps(resposta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(contagem)


def _junto(resposta: dict, registo: dict) -> dict:
    linha = {"id": registo["id"], "title": registo["title"], "path": registo["path"], "estado_regras": "completo"}
    extra = _estado(registo)
    consolidado = extra.get("consolidado")
    if consolidado is None or not consolidado.artigos:
        return linha | {"estado": "não junto", "motivo": "original sem artigos: a resposta não tem onde encaixar"}
    alteradores = _alteradores(registo)
    por_numero = dict(enumerate(alteradores, 1))
    registos_llm: list[Registo] = []
    citados: dict[str, dict] = {}
    grupos: dict[tuple, list[dict]] = {}
    for novo in resposta["artigos"]:
        numeros = tuple(sorted({int(x) for x in re.findall(r"\d+", str(novo.get("alterador") or ""))} & set(por_numero))) or tuple(por_numero)
        grupos.setdefault(numeros, []).append(novo)
    tocados: set[str] = set()  # o LLM viu a redação das regras: não há conflito
    for numeros, artigos in grupos.items():
        escolhidos = [por_numero[n] for n in numeros]
        ligacoes = []
        for a in escolhidos:
            url = (front_matter((RAIZ / a["path"]).read_text(encoding="utf-8")).get("source") or {}).get("official_url") or ""
            ligacoes.append(f"[{a['title']}]({url})" if url else a["title"])
            citados[a["id"]] = a
        data = max((a.get("publication_date") or "" for a in escolhidos), default="")
        mudancas = [novo for novo in artigos if _muda(consolidado, novo)]
        feitos, erro = _aplicar_resposta({"artigos": mudancas}, consolidado, tocados, " e ".join(ligacoes), data, registo)
        if erro:
            return linha | {"estado": "não junto", "motivo": erro}
        registos_llm += feitos
    for chave in resposta.get("removidos") or []:
        parte, _, numero = chave.rpartition("::")
        artigo = consolidado.artigo(parte, numero)
        if artigo is None:
            return linha | {"estado": "não junto", "motivo": f"artigo a remover {chave} não existe"}
        consolidado.segmentos.remove(artigo)
        registos_llm.append(Registo(artigo.chave, "revogar", "llm", "\n".join(artigo.linhas).strip(), "", "", "", metodo="llm"))
    _recolocar_assinaturas(consolidado)
    if resposta.get("removidos") and not citados:
        citados.update({a["id"]: a for a in alteradores})
    if not registos_llm:
        return linha | {"estado": "não junto", "motivo": "a resposta não muda nenhum artigo em relação ao texto das regras"}

    aplicados = list(extra["aplicados"])
    for a in citados.values():
        if a["id"] not in {x["id"] for x in aplicados}:
            aplicados.append({"id": a["id"], "title": a["title"], "publication_date": a.get("publication_date")})
    destino = PILOTO / Path(registo["path"]).relative_to("data")
    destino.parent.mkdir(parents=True, exist_ok=True)
    json_registos = extra["registos"] + [asdict(r) | {"diploma": registo["id"], "alterador": ";".join(citados)} for r in registos_llm]
    destino.with_suffix(".alteracoes.json").write_text(json.dumps(json_registos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    destino.write_text(_markdown(registo, aplicados, consolidado, extra["titulos_normalizados"], METODO), encoding="utf-8")
    linha |= {"estado": "aplicado com LLM", "consolidado": str(destino.relative_to(RAIZ)), "artigos_llm": len(registos_llm),
              "artigos_regras": len(extra["registos"]), "alteradores_ids": [a["id"] for a in aplicados], "pedido": "completo"}
    if extra["titulos_normalizados"]:
        linha["titulos_normalizados"] = True
    if resposta.get("nao_aplicavel"):
        linha["parcial"] = resposta["nao_aplicavel"]
    return linha


def _recolocar_assinaturas(consolidado) -> None:
    """As fórmulas finais ("Visto e aprovado…", assinaturas) ficam no último artigo da parte: se
    um artigo aditado depois do último as deixou a meio, passam para o fim."""
    from leis_portugal.domain.articles import _signature

    por_parte: dict[str, list] = {}
    for a in consolidado.artigos:
        por_parte.setdefault(a.parte, []).append(a)
    for artigos in por_parte.values():
        ultimo = artigos[-1]
        for a in artigos[:-1]:
            cheias = [i for i in range(1, len(a.linhas)) if a.linhas[i].strip()]
            inicio = next((i for i in cheias if _signature(a.linhas[i].strip())), None)
            if inicio is None:
                continue
            antes = [i for i in cheias if i < inicio]
            if antes and _NOMES.match(a.linhas[antes[-1]].strip()):
                inicio = antes[-1]
            formulas = a.linhas[inicio:]
            # só se há corpo antes e as fórmulas são curtas: senão é o corpo do artigo
            if inicio == cheias[0] or sum(1 for l in formulas if l.strip()) > 12:
                continue
            a.linhas = a.linhas[:inicio]
            if a.linhas and a.linhas[-1].strip():
                a.linhas.append("")
            if ultimo.linhas and ultimo.linhas[-1].strip():
                ultimo.linhas.append("")
            ultimo.linhas += formulas


def _muda(consolidado, novo: dict) -> bool:
    """O artigo da resposta difere do texto atual (um artigo igual não se reescreve)."""
    parte, _, numero = novo["chave"].rpartition("::")
    atual = consolidado.artigo(parte, numero)
    if atual is None:
        return True
    paragrafos = "\n\n".join(p.strip() for p in novo["texto"].split("\n\n") if p.strip())
    corpo = re.sub(r"\n{2,}", "\n\n", _NOTA.sub("", atual.texto).strip())
    return paragrafos != corpo or (novo["epigrafe"] or "").strip() != (atual.epigrafe or "").strip()


def juntar() -> None:
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines())}
    linhas = []
    for f in sorted(COMPLETO.glob("pt_*.json")):
        resposta = json.loads(f.read_text(encoding="utf-8"))
        if resposta["problemas"]:
            linhas.append({"id": resposta["id"], "title": selecao[resposta["id"]]["title"], "estado": "não junto", "motivo": "a resposta não passou a verificação letra a letra: " + "; ".join(resposta["problemas"])[:300]})
        elif not resposta["artigos"] and not resposta.get("removidos"):
            linhas.append({"id": resposta["id"], "title": selecao[resposta["id"]]["title"], "estado": "não junto", "motivo": "a resposta não tem artigos: " + str(resposta.get("nao_aplicavel"))[:200]})
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
    a = sub.add_parser("amostra")
    a.add_argument("n", type=int)
    a.add_argument("--semente", type=int, default=1)
    a.add_argument("--max-chars", type=int, default=150_000)
    a.add_argument("--saida", type=Path)
    q = sub.add_parser("proximos")
    q.add_argument("n", type=int)
    q.add_argument("--max-chars", type=int, default=150_000)
    q.add_argument("--saida", type=Path, required=True)
    p = sub.add_parser("pedidos")
    p.add_argument("ids", type=Path)
    p.add_argument("pasta", type=Path)
    p.add_argument("--por-ficheiro", type=int, default=3)
    i = sub.add_parser("importar")
    i.add_argument("ficheiros", type=Path, nargs="+")
    sub.add_parser("juntar")
    args = parser.parse_args()
    if args.comando == "amostra":
        ids = amostra(args.n, args.semente, args.max_chars)
        if args.saida:
            args.saida.write_text("\n".join(ids) + "\n", encoding="utf-8")
    elif args.comando == "proximos":
        selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines())}
        escolhidos, grandes, restantes = [], 0, 0
        for i in pendentes_do_pedido(args.max_chars):
            if len(escolhidos) >= args.n:
                restantes += 1
                continue
            extra = _estado(selecao[i])
            if extra.get("consolidado") is None or not extra["consolidado"].artigos:
                continue
            if pedido(selecao[i], extra)[1] > args.max_chars:
                grandes += 1
                continue
            escolhidos.append(i)
        args.saida.write_text("\n".join(escolhidos) + "\n", encoding="utf-8")
        print(f"{len(escolhidos)} escolhidos; {grandes} saltados por tamanho (> {args.max_chars}); ainda por ver (depois destes): {restantes}")
    elif args.comando == "pedidos":
        pedidos(args.ids.read_text(encoding="utf-8").split(), args.por_ficheiro, args.pasta)
    elif args.comando == "importar":
        importar(args.ficheiros)
    else:
        juntar()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
