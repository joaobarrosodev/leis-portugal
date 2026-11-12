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

**Passagens (`passagem`):** para os diplomas cujo pedido inteiro não cabe num contexto (os 93 de
`llm/pedido-completo-grandes.tsv`), os alteradores partem-se em grupos por ordem de aplicação e
cada grupo vai num pedido à parte, sobre o texto que as passagens anteriores deixaram. Por diploma,
`passagem` lê as respostas já dadas em `PASTA/<id>/resposta-K*.json`, aplica-as ao consolidado
das regras, e escreve `pedido-(K+1).md` com o próximo grupo (os alteradores numerados de seguida,
tantos quantos cabem em `--max-chars` com o texto atual). Quando não resta nenhum alterador,
funde as passagens numa resposta só (o texto de cada artigo é o da última passagem que o deu) e
grava-a em `llm/completo/<id>.json`, verificada letra a letra, como `importar`; `juntar` faz o
resto sem saber que houve passagens. Um pedido que cabe inteiro dá uma passagem só.

Uso:
    python consolidacao/llm_completo.py amostra N [--semente 1] [--max-chars 150000]
    python consolidacao/llm_completo.py pedidos IDS_FICHEIRO [--por-ficheiro 3]
    python consolidacao/llm_completo.py passagem IDS_FICHEIRO PASTA [--max-chars 230000]
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
import texto as texto_mod
from texto import RAIZ, Artigo, front_matter, publicado
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
  não se aplica ao texto, nem a revogação cujo efeito o diploma adia para um facto futuro (a
  entrada em vigor de um regulamento ou de um plano, uma portaria a publicar): diz-o em
  "nao_aplicavel".
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
- Um artigo assinalado como "já alterado por um programa" pode ter ficado errado: se, depois de
  todas as instruções, a redação certa for outra (por exemplo, o programa revogou um artigo que
  nenhuma instrução revoga), devolve a redação certa.
- Quando a mesma chave aparece duas vezes no texto atual (o decreto que aprova e o estatuto ou
  regulamento que vem a seguir), a segunda vem como "4.º#2", a terceira "4.º#3": usa essa chave.
- Os títulos de divisão (capítulos, secções, subsecções, títulos, livros) vêm no texto atual como
  "#### Título de divisão: …", pela ordem em que estão. Uma instrução que muda a designação ou a
  epígrafe de um deles, ou que o elimina, vai em "titulos": {"atual": a linha tal como vem, sem
  "#### Título de divisão: ", "novo": a linha nova (com os mesmos "#" do início, e o texto novo
  copiado letra a letra do diploma que altera) ou null para o eliminar, "alterador": o número}.
  Não inventes títulos que não estão no texto atual. Põe-nos pela ordem do texto: um título que
  se repete (o mesmo "TÍTULO II" em dois livros) entende-se o primeiro a seguir ao anterior da lista.
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
`{"id": "<id>", "artigos": [{"chave": "...", "epigrafe": "...", "texto": "...", "alterador": 1}], "removidos": ["chave", ...], "titulos": [{"atual": "#### SECÇÃO IV — …", "novo": "#### SECÇÃO IV — …", "alterador": 2}], "nao_aplicavel": null ou "texto", "instrucoes": ["resumo curto de cada instrução do original e o que fizeste"]}`
Só usas o pedido; não leias mais nada. O "texto" de cada artigo é o corpo inteiro (sem o título "Artigo N.º"), parágrafos separados por uma linha em branco, copiado letra a letra do alterador ou do texto atual. "removidos" é [] quando nenhum artigo desaparece; "titulos" é [] quando nenhum título de divisão muda. Confirma no fim que o JSON é válido e que respondeste a todos os "<<<DIPLOMA id=...>>>".
"""

_TITULO_DIVISAO = re.compile(r"^#{2,5} ")
_ELIMINADO = "\x00título eliminado\x00"
_NUMERACAO = re.compile(r"^(?:\d+[-–.\s]*|[a-z]\))\s*")
_NOTA = re.compile(r"^> (?:Alterado|Aditado|Revogado|Retificado) pelo/a .*$", re.M)


def verificar_resposta(resultado: dict, selecao: dict, textos_atuais: list[str] = ()) -> list[str]:
    """Como `llm.verificar_resposta`: cada parágrafo vem, letra a letra, de um alterador ou do
    texto original. Uma renumeração (o corpo antigo passa a "1 - …") conta: tira-se a numeração
    do parágrafo antes de o procurar. `textos_atuais` são outros textos de onde um parágrafo pode
    vir (numa passagem, o texto atual que as passagens anteriores deixaram)."""
    alteradores = [_plano(publicado(RAIZ / a["path"])) for a in _alteradores_da_selecao(selecao) if a.get("path")]
    original = _plano(publicado(RAIZ / selecao["path"]))
    atuais = [_plano(t) for t in textos_atuais]
    problemas = []

    def vem_de_algum(p: str) -> bool:
        return any(p in a for a in alteradores) or p in original or any(p in t for t in atuais)

    for artigo in resultado.get("artigos", []):
        for p in (x.strip() for x in artigo["texto"].split("\n\n") if x.strip()):
            if _REVOGADO.match(p) or vem_de_algum(_plano(p)) or vem_de_algum(_plano(_NUMERACAO.sub("", p))):
                continue
            problemas.append(f"{artigo['chave']}: parágrafo que não está no alterador nem no original: {p[:80]}")
    for titulo in resultado.get("titulos") or []:
        novo = titulo.get("novo")
        if novo is None:
            continue
        texto = re.sub(r"^#+\s*", "", novo).strip()
        # o identificador ("SECÇÃO IV") pode vir noutro formato; o que tem de vir do alterador é o texto
        epigrafe = texto.split(" — ", 1)[-1].strip()
        if not (vem_de_algum(_plano(texto)) or vem_de_algum(_plano(epigrafe))):
            problemas.append(f"título {novo[:60]}: texto que não está no alterador nem no original")
    return problemas


def _estado(registo: dict) -> dict:
    extra: dict = {}
    processar(registo, escrever=False, extra=extra)
    return extra


def _alteradores(registo: dict) -> list[dict]:
    return sorted((a for a in registo["alteradores"] if a.get("path") and a.get("text_quality") == "texto"), key=lambda a: a.get("ordem") or "")


def pedido(registo: dict, extra: dict, alteradores: list[dict] | None = None, inicio: int = 1, aviso: str = "",
           tocados_llm: frozenset[str] = frozenset()) -> tuple[str, int]:
    """O texto do pedido e o seu tamanho em caracteres. Numa passagem, `alteradores` é só o grupo
    desta passagem, numerado a partir de `inicio` (a numeração é a de todos os alteradores do
    diploma, para o "alterador" da resposta apontar sempre para o mesmo), `aviso` diz ao LLM em
    que passagem está e `tocados_llm` são os artigos que as passagens anteriores mudaram."""
    consolidado, tocados = extra["consolidado"], extra["tocados"]
    if alteradores is None:
        alteradores = _alteradores(registo)
    partes = [f"# Diploma original: {registo['title']}", ""]
    if aviso:
        partes += [aviso, ""]
    partes.append("## Texto atual do original, por artigos (e os títulos de divisão, pela ordem do texto)")
    chaves = consolidado.chaves_unicas()
    for s in consolidado.segmentos:
        if not isinstance(s, Artigo):
            partes += [f"#### Título de divisão: {l.strip()}" for l in s if _TITULO_DIVISAO.match(l)]
            continue
        chave = chaves[id(s)]
        sinal = (" [já alterado por um programa]" if s.chave in tocados
                 else " [já alterado numa passagem anterior]" if chave in tocados_llm else "")
        partes += [f"### {chave}{sinal}", s.epigrafe, _NOTA.sub("", s.texto).strip(), ""]
    partes.append("## Diplomas que alteram o original, por ordem de aplicação")
    for n, a in enumerate(alteradores, inicio):
        texto, completo = _texto_alterador(a["path"], registo["title"])
        aviso_a = "" if completo else " (só os artigos que mencionam o original)"
        partes += [f"### Alterador {n}: {a.get('title') or a['id']}{aviso_a}", texto.strip(), ""]
    texto = "\n".join(partes)
    return texto, len(texto)


def _texto_atual(consolidado) -> str:
    """O texto atual, artigo a artigo, para a verificação letra a letra de uma passagem."""
    return "\n\n".join(_NOTA.sub("", a.texto).strip() for a in consolidado.artigos)


def _fundir(respostas: list[dict]) -> dict:
    """Várias respostas do mesmo diploma (passagens, ou uma resposta escrita em partes) numa só:
    o texto de um artigo é o da última resposta que o deu; os removidos somam-se (um artigo
    removido e depois dado outra vez deixa de estar removido); `nao_aplicavel` e `instrucoes`
    juntam-se."""
    saida: dict = {"id": None, "artigos": [], "removidos": [], "titulos": [], "nao_aplicavel": None, "instrucoes": []}
    por_chave: dict[str, dict] = {}
    for r in respostas:
        saida["id"] = saida["id"] or r.get("id")
        for a in r.get("artigos") or []:
            por_chave[a["chave"]] = a
            if a["chave"] in saida["removidos"]:
                saida["removidos"].remove(a["chave"])
        for c in r.get("removidos") or []:
            por_chave.pop(c, None)
            if c not in saida["removidos"]:
                saida["removidos"].append(c)
        if r.get("nao_aplicavel"):
            saida["nao_aplicavel"] = (saida["nao_aplicavel"] + " | " if saida["nao_aplicavel"] else "") + str(r["nao_aplicavel"])
        saida["instrucoes"] += list(r.get("instrucoes") or [])
        saida["titulos"] += list(r.get("titulos") or [])  # aplicam-se pela ordem
    saida["artigos"] = list(por_chave.values())
    return saida


def _ler_respostas(ficheiros: list[Path]) -> dict | None:
    """As respostas de uma passagem (lista ou objeto por ficheiro, em um ou vários ficheiros),
    fundidas; None se algum não for JSON válido."""
    objetos = []
    for f in ficheiros:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        objetos += d if isinstance(d, list) else [d]
    return _fundir(objetos) if objetos else None


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
    por_id: dict[str, list[dict]] = {}
    for f in ficheiros:
        lido = json.loads(f.read_text(encoding="utf-8"))
        for resposta in (lido if isinstance(lido, list) else [lido]):
            por_id.setdefault(resposta["id"], []).append(resposta)
    for i, partes in por_id.items():
        # uma resposta escrita em várias partes (ou repetida) funde-se numa só
        resposta = partes[0] if len(partes) == 1 else _fundir(partes)
        resposta |= {"modelo": resposta.get("modelo") or "claude-opus-5-5", "pedido": "completo"}
        resposta["problemas"] = verificar_resposta(resposta, selecao[i])
        tipo = "com problemas" if resposta["problemas"] else "sem alterações" if not resposta.get("artigos") else "sem problemas"
        contagem[tipo] = contagem.get(tipo, 0) + 1
        (COMPLETO / (i.replace(":", "_") + ".json")).write_text(json.dumps(resposta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(contagem)


def _aplicar(resposta: dict, registo: dict, consolidado) -> tuple[list[Registo], dict[str, dict], str | None]:
    """Os artigos e os removidos da resposta no consolidado (que fica alterado). Devolve os
    registos, os alteradores citados e o motivo quando não se aplica."""
    alteradores = _alteradores(registo)
    por_numero = dict(enumerate(alteradores, 1))
    registos_llm: list[Registo] = []
    citados: dict[str, dict] = {}
    grupos: dict[tuple, list[dict]] = {}
    ultimos = _ultimos_do_original(registo)
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
            return registos_llm, citados, erro
        registos_llm += feitos
    a_remover = []
    for chave in resposta.get("removidos") or []:
        parte, _, numero = chave.rpartition("::")
        artigo = consolidado.artigo(parte, numero)
        if artigo is None:
            return registos_llm, citados, f"artigo a remover {chave} não existe"
        a_remover.append(artigo)
    for artigo in a_remover:  # por identidade: com chaves repetidas, dois artigos podem ser iguais
        consolidado.segmentos = [s for s in consolidado.segmentos if s is not artigo]
        registos_llm.append(Registo(artigo.chave, "revogar", "llm", "\n".join(artigo.linhas).strip(), "", "", "", metodo="llm"))
    cursor = (-1, -1)  # os títulos vêm pela ordem do texto: um repetido é o primeiro a seguir ao anterior
    for titulo in resposta.get("titulos") or []:
        feito, erro, cursor = _mudar_titulo(consolidado, titulo, cursor)
        if erro:
            return registos_llm, citados, erro
        if feito is None:
            continue
        registos_llm.append(feito)
        n = next(iter(sorted({int(x) for x in re.findall(r"\d+", str(titulo.get("alterador") or ""))} & set(por_numero))), None)
        for a in [por_numero[n]] if n else alteradores:
            citados[a["id"]] = a
    # os títulos eliminados ficaram como linhas vazias marcadas: tiram-se agora, com a linha em branco a seguir
    for s in consolidado.segmentos:
        if not isinstance(s, Artigo) and _ELIMINADO in s:
            i = len(s) - 1
            while i >= 0:
                if s[i] == _ELIMINADO:
                    del s[i]
                    if i < len(s) and not s[i].strip():
                        del s[i]
                i -= 1
    _recolocar_assinaturas(consolidado, ultimos)
    if resposta.get("removidos") and not citados:
        citados.update({a["id"]: a for a in alteradores})
    return registos_llm, citados, None


def _junto(resposta: dict, registo: dict) -> dict:
    linha = {"id": registo["id"], "title": registo["title"], "path": registo["path"], "estado_regras": "completo"}
    extra = _estado(registo)
    consolidado = extra.get("consolidado")
    if consolidado is None or not consolidado.artigos:
        return linha | {"estado": "não junto", "motivo": "original sem artigos: a resposta não tem onde encaixar"}
    alteradores = _alteradores(registo)
    registos_llm, citados, erro = _aplicar(resposta, registo, consolidado)
    if erro:
        return linha | {"estado": "não junto", "motivo": erro}
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


def _ultimos_do_original(registo: dict) -> set[str]:
    """A chave do último artigo de cada parte no original publicado: é aí que estão as fórmulas
    finais. (Com os títulos normalizados quando o original os tem em texto corrido.)"""
    from texto import com_titulos, dividir

    texto = publicado(RAIZ / registo["path"])
    original = dividir(texto)
    if not original.artigos and (normalizado := com_titulos(texto)) is not None:
        original = dividir(normalizado)
    por_parte: dict[str, str] = {}
    for a in original.artigos:
        por_parte[a.parte] = a.chave
    return set(por_parte.values())


def _mudar_titulo(consolidado, titulo: dict, cursor: tuple[int, int] = (-1, -1)):
    """Muda (ou elimina, com `novo` null) uma linha de título de divisão fora dos artigos. A linha
    `atual` tem de existir letra a letra; o número de "#" fica o da linha atual. Quando se repete
    (o "TÍTULO II — Da Marinha" de dois livros), é a primeira depois de `cursor`, a posição do
    título anterior da mesma resposta. Devolve (registo, erro, nova posição)."""
    atual = (titulo.get("atual") or "").strip()
    novo = titulo.get("novo")
    sem_marca = lambda l: re.sub(r"^#+\s*", "", l.strip())
    lugares = [((k, i), s, i) for k, s in enumerate(consolidado.segmentos) if not isinstance(s, Artigo)
               for i, l in enumerate(s) if _TITULO_DIVISAO.match(l) and sem_marca(l) == sem_marca(atual)]
    if not lugares:
        return None, f"título a mudar não existe no texto: {atual[:80]}", cursor
    if len(lugares) > 1:
        lugares = [x for x in lugares if x[0] > cursor]
        if not lugares:
            return None, f"título repetido sem ocorrência depois do anterior: {atual[:80]}", cursor
    posicao, segmento, i = lugares[0]
    antes = segmento[i]
    if novo is None:
        segmento[i] = _ELIMINADO  # tira-se no fim, para as posições dos outros títulos não mudarem
        return Registo(sem_marca(antes), "revogar", "llm", antes, "", "", "", metodo="llm"), None, posicao
    marca = re.match(r"^#+", antes).group(0)
    depois = f"{marca} {sem_marca(novo)}"
    if depois == antes:
        return None, None, posicao
    segmento[i] = depois
    return Registo(sem_marca(antes), "substituir", "llm", antes, depois, "", "", metodo="llm"), None, posicao


def _recolocar_assinaturas(consolidado, ultimos: set[str] | None = None) -> None:
    """As fórmulas finais ("Visto e aprovado…", assinaturas) ficam no último artigo da parte: se
    um artigo aditado depois do último as deixou a meio, passam para o fim. Só se movem as que
    estavam no último artigo da parte no original (`ultimos`, as chaves): no decreto que aprova um
    regulamento na mesma parte, as fórmulas do decreto ficam a meio desde o original."""
    from leis_portugal.domain.articles import _signature

    por_parte: dict[str, list] = {}
    for a in consolidado.artigos:
        por_parte.setdefault(a.parte, []).append(a)
    for artigos in por_parte.values():
        ultimo = artigos[-1]
        for a in artigos[:-1]:
            if ultimos is not None and a.chave not in ultimos:
                continue
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


AVISO_PASSAGEM = """**Passagem {k}: alteradores {a} a {b} de {n}.** {antes}Este pedido traz só os alteradores {a} a {b};
os seguintes ({depois}) vêm numa passagem posterior e não interessam agora. Lê todas as instruções
DESTES alteradores dirigidas ao original e devolve os artigos que, depois delas, têm de mudar em
relação ao texto atual. No campo "alterador" usa o número com que o alterador vem aqui ({a} a {b})."""


def _grupo(base: int, restantes: list[tuple[int, dict, int]], max_chars: int) -> list[tuple[int, dict, int]]:
    """Os alteradores que cabem no próximo pedido: tantos quantos somam, com o texto atual,
    até `max_chars`; pelo menos um."""
    grupo, total = [], base
    for n, a, tamanho in restantes:
        if grupo and total + tamanho > max_chars:
            break
        grupo.append((n, a, tamanho))
        total += tamanho
    return grupo


def passagem(ids: list[str], pasta: Path, max_chars: int) -> None:
    """Por diploma: aplica as respostas já dadas, escreve o próximo pedido ou, se não resta
    nenhum alterador, a resposta final em `llm/completo/`. Imprime o estado de cada um."""
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines())}
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "REGRAS.md").write_text(SISTEMA + FORMATO, encoding="utf-8")
    for i in ids:
        registo = selecao[i]
        pasta_i = pasta / i.replace(":", "_")
        pasta_i.mkdir(exist_ok=True)
        ficheiro_estado = pasta_i / "estado.json"
        estado = json.loads(ficheiro_estado.read_text(encoding="utf-8")) if ficheiro_estado.exists() else {"id": i, "passagens": []}
        if estado.get("feito"):
            print(f"{i} {registo['title']}: feito")
            continue
        extra = _estado(registo)
        consolidado = extra.get("consolidado")
        if consolidado is None or not consolidado.artigos:
            print(f"{i} {registo['title']}: original sem artigos, não se pede")
            continue
        alteradores = _alteradores(registo)
        respostas, problemas, tocados_llm, falta = [], [], set(), None
        for p in estado["passagens"]:
            ficheiros = sorted(pasta_i.glob(f"resposta-{p['n']}*.json"))
            resposta = _ler_respostas(ficheiros) if ficheiros else None
            if resposta is None:
                falta = p["n"]
                break
            problemas += [f"passagem {p['n']}: {x}" for x in verificar_resposta(resposta, registo, [_texto_atual(consolidado)])]
            feitos, _, erro = _aplicar(resposta, registo, consolidado)
            if erro:
                problemas.append(f"passagem {p['n']}: não se aplica ao texto atual: {erro}")
            tocados_llm |= {r.artigo for r in feitos}
            respostas.append(resposta)
            p["artigos"] = len(resposta["artigos"])
        if falta is not None:
            print(f"{i} {registo['title']}: à espera da resposta da passagem {falta} ({pasta_i}/resposta-{falta}.json)")
            continue
        feitos_n = {n for p in estado["passagens"] for n in p["alteradores"]}
        restantes = []
        for n, a in enumerate(alteradores, 1):
            if n not in feitos_n:
                texto, _ = _texto_alterador(a["path"], registo["title"])
                restantes.append((n, a, len(texto) + len(a.get("title") or "") + 20))
        if not restantes:
            # um problema só conta se o artigo em causa ficou com o texto dessa passagem: uma
            # passagem posterior pode tê-lo reescrito (ou revogado) com texto verificado
            ultima = {a["chave"]: k for k, r in enumerate(respostas, 1) for a in r.get("artigos") or []}
            def vale(prob: str) -> bool:
                m = re.match(r"passagem (\d+): (.+?): parágrafo", prob)
                return not m or ultima.get(m.group(2)) == int(m.group(1))
            problemas = [x for x in problemas if vale(x)]
            final = _fundir(respostas) | {"id": i, "modelo": "claude-fable-5-1", "pedido": "completo", "passagens": estado["passagens"], "problemas": problemas}
            COMPLETO.mkdir(parents=True, exist_ok=True)
            (COMPLETO / (i.replace(":", "_") + ".json")).write_text(json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            estado["feito"] = True
            ficheiro_estado.write_text(json.dumps(estado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            tipo = "com problemas" if problemas else "sem alterações" if not final["artigos"] and not final["removidos"] else "sem problemas"
            print(f"{i} {registo['title']}: feito em {len(estado['passagens'])} passagens, {len(final['artigos'])} artigos, {tipo}")
            continue
        base = sum(len(a.chave) + len(a.epigrafe or "") + len(_NOTA.sub("", a.texto)) + 10 for a in consolidado.artigos) + 2000
        grupo = _grupo(base, restantes, max_chars)
        k = len(estado["passagens"]) + 1
        a, b = grupo[0][0], grupo[-1][0]
        antes = (f"Os alteradores 1 a {a - 1} já foram aplicados ao texto atual (os artigos que mudaram estão assinalados). "
                 if a > 1 else "")
        aviso = "" if (k == 1 and b == len(alteradores)) else AVISO_PASSAGEM.format(antes=antes,
            k=k, a=a, b=b, n=len(alteradores), depois=f"{b + 1} a {len(alteradores)}" if b < len(alteradores) else "nenhum")
        texto, tamanho = pedido(registo, extra, [x[1] for x in grupo], a, aviso, frozenset(tocados_llm))
        destino = pasta_i / f"pedido-{k}.md"
        destino.write_text(f"<<<DIPLOMA id={i}>>>\n{texto}\n<<<FIM DO DIPLOMA id={i}>>>\n", encoding="utf-8")
        estado["passagens"].append({"n": k, "alteradores": [x[0] for x in grupo], "chars": tamanho})
        ficheiro_estado.write_text(json.dumps(estado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        aviso_tamanho = f" (ACIMA do limite {max_chars})" if tamanho > max_chars else ""
        print(f"{i} {registo['title']}: passagem {k}, alteradores {a} a {b} de {len(alteradores)}, {tamanho} caracteres{aviso_tamanho}, {len(restantes) - len(grupo)} por pedir -> {destino}")


def juntar() -> None:
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines())}
    linhas = []
    excluidos, grandes = texto_mod.exclusoes(), texto_mod.gigantes()
    for f in sorted(COMPLETO.glob("pt_*.json")):
        resposta = json.loads(f.read_text(encoding="utf-8"))
        if resposta["id"] in excluidos:
            linhas.append({"id": resposta["id"], "title": selecao[resposta["id"]]["title"], "estado": "não junto", "motivo": excluidos[resposta["id"]]})
        elif resposta["id"] in grandes:
            # passou para `llm_gigantes.py`, que escreve o consolidado no mesmo ficheiro: juntar aqui
            # escrevia por cima o texto do pedido completo
            linhas.append({"id": resposta["id"], "title": selecao[resposta["id"]]["title"], "estado": "não junto", "motivo": "juntado por llm_gigantes.py (llm/juntados-corrido.jsonl)"})
        elif resposta["problemas"]:
            linhas.append({"id": resposta["id"], "title": selecao[resposta["id"]]["title"], "estado": "não junto", "motivo": "a resposta não passou a verificação letra a letra: " + "; ".join(resposta["problemas"])[:300]})
        elif not resposta["artigos"] and not resposta.get("removidos") and not resposta.get("titulos"):
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
    g = sub.add_parser("passagem")
    g.add_argument("ids", type=Path)
    g.add_argument("pasta", type=Path)
    g.add_argument("--max-chars", type=int, default=230_000)
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
    elif args.comando == "passagem":
        passagem(args.ids.read_text(encoding="utf-8").split(), args.pasta, args.max_chars)
    else:
        juntar()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
