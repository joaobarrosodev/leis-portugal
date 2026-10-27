"""Piloto da fase 2: aplica as alterações aos diplomas de `consolidacao/selecao.jsonl`.

Para cada diploma lê as instruções do diploma que altera, aplica-as por regras, verifica o
resultado e escreve:

- `consolidacao/piloto/<caminho do registo>.md`: o texto consolidado (só quando todas as
  instruções foram aplicadas e a verificação passou), com os artigos no formato do acervo;
- `consolidacao/piloto/<caminho do registo>.alteracoes.json`: um registo por alteração
  aplicada (artigo, operação, texto antes e depois, excerto que a justifica, método);
- `consolidacao/resultados.jsonl`: o estado de cada diploma (aplicado, para o LLM, falhou a
  verificação, sem instruções…) e o motivo;
- `consolidacao/pendentes.jsonl`: as instruções que as regras não aplicaram, com o texto dos
  artigos em causa, prontas para o LLM (`llm.py`).

**Escala (`--escala`):** lê `selecao-escala.jsonl` (`selecionar.py --todos`), em que cada
diploma tem `alteradores`, todos os diplomas que o alteram por ordem de data. Os alteradores
aplicam-se por essa ordem, cada um sobre o resultado do anterior, com a verificação automática
depois de cada um. Por diploma fica a `triagem` (o que a leitura das instruções diz, alterador a
alterador: `sem alteração textual`, `aplicável por regra`, `para LLM`, `revogado por inteiro`,
`sem texto do alterador`) e o `estado` final (`aplicado por regra` quando todos os alteradores
com instruções se aplicaram e verificaram; `para LLM` com `falhou_em` quando um falhou: a
leitura, a aplicação ou a verificação). Uma alteração sem instruções não impede as outras. O
resultado vai para `resultados-escala.jsonl` e `pendentes-escala.jsonl`, e os consolidados para
`piloto/` como no piloto (sem reescrever os do piloto juntados com o LLM). Os originais cujo
título não tem número ("Declaração", "Despacho Conjunto") ficam `não triado`: as regras não
encontram as menções. O trabalho é retomável por diploma e divide-se em partes (`--parte i/N`,
cada uma no seu ficheiro `resultados-escala.parte-i.jsonl`; `--refazer F` repete os ids de F;
`--juntar` junta as partes).

Nada em `data/` é alterado. Uso: `python consolidacao/consolidar.py [--amostra 50] [--semente 1]`
ou `python consolidacao/consolidar.py --escala [--parte 1/4] [--limite N] [--juntar]`.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
import traceback
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import yaml

from alteracoes import Leitura, ler
from aplicar import Fonte, Resultado, aplicar
from texto import RAIZ, Corpo, com_titulos, dividir, front_matter, normalizar, padrao_diploma, publicado, sem_ligacoes
from verificar import republicacao, verificar

PASTA = RAIZ / "consolidacao"
SELECAO = PASTA / "selecao.jsonl"
SELECAO_ESCALA = PASTA / "selecao-escala.jsonl"
PILOTO = PASTA / "piloto"
RESULTADOS_ESCALA = PASTA / "resultados-escala.jsonl"
PENDENTES_ESCALA = PASTA / "pendentes-escala.jsonl"

# Os textos dos alteradores repetem-se muito (um orçamento altera centenas de diplomas).
_ALTERADORES: dict[str, str] = {}
_META: dict[str, dict] = {}


def _texto_alterador(path: str) -> str:
    if path not in _ALTERADORES:
        if len(_ALTERADORES) > 2000:
            _ALTERADORES.clear()
        _ALTERADORES[path] = publicado(RAIZ / path)
    return _ALTERADORES[path]


def _meta_alterador(path: str) -> dict:
    if path not in _META:
        if len(_META) > 5000:
            _META.clear()
        _META[path] = front_matter((RAIZ / path).read_text(encoding="utf-8"))
    return _META[path]


def _mencao_numero(texto: str, titulo: str) -> bool:
    """O número do original aparece no alterador, mesmo numa lista ("Decretos-Leis n.os 99/99, …, 45/2007")."""
    numero = re.sub(r"\s*\(.*\)$", "", titulo).split("n.º")[-1].strip()
    if not numero or numero == titulo:
        return False
    return re.search(rf"(?<![\w/]){re.escape(numero)}(?![\w/])", normalizar(sem_ligacoes(texto))) is not None


def _so_redacao(texto: str, titulo: str) -> bool:
    """O original só aparece como o diploma que deu a redação de outro ("na redação dada pelo …")."""
    numero = re.escape(re.sub(r"\s*\(.*\)$", "", titulo).split("n.º")[-1].strip())
    plano = normalizar(sem_ligacoes(texto))
    return bool(re.search(rf"(?:reda[cç]+[ãa]o (?:que lhe (?:foi|é) )?dada|alterad[oa]s?|republicad[oa]s?) pel[oa]s? [^.;]{{0,200}}?(?<![\w/]){numero}(?![\w/])", plano, re.I))


def _motivo_sem_alteracao(leitura: Leitura, texto_alterador: str, titulo: str) -> str:
    if leitura.mencoes:
        return "o alterador cita o original mas não lhe dá instruções de alteração"
    if _mencao_numero(texto_alterador, titulo):
        return ("o original só aparece como diploma que deu a redação de outro"
                if _so_redacao(texto_alterador, titulo) else "o original só aparece numa lista ou remissão")
    return "o alterador não menciona o original"


# A ordem de precedência dos estados de um diploma com vários alteradores.
_PRECEDENCIA = ("revogado por inteiro", "sem texto do alterador", "para LLM", "aplicável por regra", "sem alteração textual")


def processar(registo: dict, escrever: bool = True) -> dict:
    escala = "alteradores" in registo
    alteradores = registo.get("alteradores") or [registo["alterador"]]
    estado = {"id": registo["id"], "title": registo["title"], "path": registo["path"], "citacoes": registo["citacoes"]}
    if escala:
        estado |= {"n_alteracoes": len(alteradores), "alteradores": [a.get("title") or a["id"] for a in alteradores]}
    else:
        estado["alterador"] = alteradores[0].get("title") or alteradores[0]["id"]
    if registo.get("republicado_por"):
        return estado | {"estado": "excluído", "triagem": "excluído", "motivo": "tem republished_by: o texto atual está no consolidado"}
    if registo["text_quality"] != "texto":
        return estado | {"estado": "sem texto", "triagem": "sem texto", "motivo": f"original só com {registo['text_quality']}"}
    if not escala:
        alterador_meta = alteradores[0]
        if not alterador_meta.get("path"):
            return estado | {"estado": "sem texto", "motivo": "o diploma que altera não está no acervo"}
        if alterador_meta.get("text_quality") != "texto":
            return estado | {"estado": "sem texto", "motivo": f"o diploma que altera só tem {alterador_meta.get('text_quality')}"}

    if padrao_diploma(registo["title"]) is None:
        # "Declaração", "Despacho Conjunto", "Rectificação": sem número no título, as regras não
        # encontram as menções ao original no alterador, por isso não se diz nada sobre o texto.
        return estado | {"estado": "não triado", "triagem": "não triado",
                         "motivo": "título do original sem número: as regras não procuram as menções no alterador"}

    # Os registos que o `acervo.py` já consolidou têm em `data/` o texto em vigor: aqui conta o publicado.
    texto_original = publicado(RAIZ / registo["path"])
    original = dividir(texto_original)
    if not original.artigos and (normalizado := com_titulos(texto_original)) is not None:
        # Artigos em texto corrido: os títulos vêm do parser da fase 3 (ver `com_titulos`).
        texto_original, original = normalizado, dividir(normalizado)
        estado["titulos_normalizados"] = True

    consolidado = dividir(texto_original)  # o texto que vai sendo alterado
    base = consolidado  # o texto sobre que se lê o alterador seguinte (depois de uma falha, o de antes dela)
    passos: list[dict] = []
    registos_json: list[dict] = []
    aplicados: list[dict] = []  # os alteradores que deram registos, para o cabeçalho do consolidado
    pendentes: list[dict] = []
    falha: dict | None = None
    regras: Counter = Counter()
    republicacoes: list[dict] = []

    for k, alt in enumerate(alteradores, 1):
        passo = {"alterador": alt.get("title") or alt["id"], "id": alt["id"]}
        if not alt.get("path"):
            passos.append(passo | {"triagem": "sem texto do alterador", "motivo": "o diploma que altera não está no acervo"})
            continue
        if alt.get("text_quality") != "texto":
            passos.append(passo | {"triagem": "sem texto do alterador", "motivo": f"o diploma que altera só tem {alt.get('text_quality')}"})
            continue
        texto_alterador = _texto_alterador(alt["path"])
        antes = dividir(base.texto())  # o texto antes deste alterador, para a verificação
        leitura = ler(texto_alterador, registo["title"], antes)
        passo |= {"instrucoes": len(leitura.instrucoes), "por_aplicar": len(leitura.por_aplicar), "mencoes": leitura.mencoes}

        if not leitura.instrucoes and not leitura.por_aplicar:
            passos.append(passo | {"triagem": "sem alteração textual", "motivo": _motivo_sem_alteracao(leitura, texto_alterador, registo["title"])})
            continue
        revogacoes = [p for p in leitura.por_aplicar if p.motivo.startswith("revogação do diploma inteiro")]
        if revogacoes and len(revogacoes) == len(leitura.por_aplicar) and not leitura.instrucoes:
            passos.append(passo | {"triagem": "revogado por inteiro", "motivo": "o alterador revoga o original (o DRE dá-o como em vigor)",
                                   "excerto": revogacoes[0].excerto})
            continue
        if not original.artigos:
            motivo = _sem_artigos(texto_original)
            passos.append(passo | {"triagem": "para LLM", "motivo": motivo})
            pendentes += _pendentes(alt, antes, leitura, None, motivo)
            falha = falha or {"alterador": passo["alterador"], "indice": k, "fase": "leitura", "motivo": motivo}
            continue
        motivos = [p.motivo for p in leitura.por_aplicar]
        passo["triagem"] = "para LLM" if leitura.por_aplicar else "aplicável por regra"
        if falha is not None:
            # Já falhou num alterador anterior: só se lê, e tudo fica para o LLM.
            passo["motivo"] = _motivo_de(motivos) if motivos else "depois de uma falha num alterador anterior"
            pendentes += _pendentes(alt, antes, leitura, None, "depois de uma falha num alterador anterior")
            passos.append(passo)
            continue

        meta = _meta_alterador(alt["path"])
        fonte = Fonte(alt["title"], (meta.get("source") or {}).get("official_url") or "", alt.get("publication_date") or "")
        resultado = aplicar(consolidado, leitura.instrucoes, fonte)
        rotulos = alt.get("rotulos_dre") if escala else registo.get("rotulos_dre", [])
        problemas = verificar(antes, consolidado, texto_alterador, registo["title"], leitura, resultado, rotulos or [])
        comparacao = republicacao(texto_alterador, consolidado, registo["title"], resultado.tocados) if resultado.registos else None
        if comparacao:
            republicacoes.append({"alterador": passo["alterador"]} | comparacao)
            if comparacao["diferentes"]:
                problemas.append(f"diferente da republicação no alterador: artigos {', '.join(comparacao['diferentes'][:10])}")
        passo |= {"aplicadas": len(resultado.registos), "falhas": len(resultado.falhas), "regras": dict(Counter(r.regra for r in resultado.registos))}
        regras.update(passo["regras"])
        if resultado.registos:
            registos_json += [asdict(r) | {"diploma": registo["id"], "alterador": alt["id"]} for r in resultado.registos]
            aplicados.append({"id": alt["id"], "title": alt["title"], "publication_date": alt.get("publication_date")})
        if leitura.por_aplicar or resultado.falhas:
            motivo = _motivo_llm(leitura, resultado)
            passo |= {"motivo": motivo, "problemas": problemas}
            falha = {"alterador": passo["alterador"], "indice": k, "fase": "leitura" if leitura.por_aplicar else "aplicação", "motivo": motivo}
            pendentes += _pendentes(alt, antes, leitura, resultado)
            base = antes  # os alteradores seguintes leem-se sobre o texto de antes da falha
        elif problemas:
            # As regras aplicaram tudo, mas a verificação não passou: vai tudo para o LLM.
            passo |= {"estado": "falhou a verificação", "motivo": problemas[0], "problemas": problemas}
            falha = {"alterador": passo["alterador"], "indice": k, "fase": "verificação", "motivo": problemas[0]}
            pendentes += _pendentes(alt, antes, leitura, None, "falhou a verificação")
            base = antes
        else:
            passo["estado"] = "aplicado"
            base = consolidado
        passos.append(passo)

    estado |= {
        "instrucoes": sum(p.get("instrucoes", 0) for p in passos),
        "por_aplicar": sum(p.get("por_aplicar", 0) for p in passos),
        "artigos_original": len(original.artigos),
    }
    if escala:
        estado["passos"] = passos
    triagens = {p["triagem"] for p in passos}
    triagem = next(t for t in _PRECEDENCIA if t in triagens)
    estado["triagem"] = triagem
    if triagem == "revogado por inteiro":
        passo = next(p for p in passos if p["triagem"] == triagem)
        estado |= {"estado": triagem, "motivo": passo["motivo"], "excerto": passo["excerto"], "revogado_por": passo["alterador"]}
        depois = [p["alterador"] for p in passos[passos.index(passo) + 1 :] if p["triagem"] != "sem alteração textual"]
        if depois:
            estado["alteradores_depois_da_revogacao"] = depois
    elif triagem == "sem texto do alterador":
        em_falta = [p for p in passos if p["triagem"] == triagem]
        estado |= {"estado": "sem texto do alterador" if escala else "sem texto",
                   "motivo": em_falta[0]["motivo"] + (f" (e mais {len(em_falta) - 1})" if len(em_falta) > 1 else ""),
                   "alteradores_sem_texto": [p["alterador"] for p in em_falta]}
    elif falha is not None:
        if falha["fase"] == "verificação" and not escala:
            estado |= {"estado": "falhou a verificação", "motivo": falha["motivo"]}
        else:
            estado |= {"estado": "para LLM", "motivo": falha["motivo"]}
        estado["falhou_em"] = falha
        problemas = [x for p in passos for x in p.get("problemas", [])]
        if problemas:
            estado["problemas"] = problemas
    elif triagem == "aplicável por regra":
        estado |= {"estado": "aplicado por regra", "motivo": ""}
    else:
        estado |= {"estado": "sem alteração textual", "motivo": passos[0]["motivo"] if len(passos) == 1 else _motivo_de([p["motivo"] for p in passos])}
    if pendentes and estado["estado"] in ("para LLM", "falhou a verificação"):
        # Só o que o LLM pode fazer: um revogado por inteiro ou sem texto de um alterador não vai.
        estado["pendentes"] = pendentes
    if any("aplicadas" in p for p in passos):
        estado |= {"aplicadas": sum(regras.values()), "falhas": sum(p.get("falhas", 0) for p in passos), "regras": dict(regras)}
    if republicacoes:
        estado["republicacao"] = republicacoes[0] if len(republicacoes) == 1 and not escala else republicacoes
        if not escala:
            estado["republicacao"].pop("alterador", None)

    if escrever and registos_json and escala and registo["id"] in _juntados_no_piloto():
        estado["ficheiros"] = "do piloto, juntados com o LLM (llm/juntados.jsonl): não se reescrevem"
    elif escrever and registos_json:
        destino = PILOTO / Path(registo["path"]).relative_to("data")
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.with_suffix(".alteracoes.json").write_text(json.dumps(registos_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if estado["estado"] == "aplicado por regra":
            destino.write_text(_markdown(registo, aplicados, consolidado, estado.get("titulos_normalizados", False)), encoding="utf-8")
            estado["consolidado"] = str(destino.relative_to(RAIZ))
    return estado


_JUNTADOS: set[str] | None = None


def _juntados_no_piloto() -> set[str]:
    """Os diplomas do piloto cujo `piloto/<caminho>` tem a resposta do LLM juntada (`juntar.py`)."""
    global _JUNTADOS
    if _JUNTADOS is None:
        ficheiro = PASTA / "llm" / "juntados.jsonl"
        _JUNTADOS = {j["id"] for j in map(json.loads, ficheiro.read_text(encoding="utf-8").splitlines())
                     if j["estado"] == "aplicado com LLM"} if ficheiro.exists() else set()
    return _JUNTADOS


def _sem_artigos(texto: str) -> str:
    """Porque é que nem o parser da fase 3 dá os artigos do original."""
    from leis_portugal.domain.articles import parse_articles

    tipos = Counter(a.kind for a in parse_articles(texto))
    if tipos["artigo"]:
        return "original sem artigos identificados (numeração repetida ou que recomeça sem título de anexo)"
    if tipos["numero"]:
        return "original sem artigos identificados (só números do dispositivo: 1.º, 2.º, …)"
    if tipos["base"]:
        return "original sem artigos identificados (bases em texto corrido)"
    return "original sem artigos identificados"


def _motivo_de(motivos: list[str]) -> str:
    return Counter(re.sub(r"\s*\(.*|\d+\.º(-[A-Z])?", "", m).strip() for m in motivos).most_common(1)[0][0]


def _motivo_llm(leitura: Leitura, resultado: Resultado) -> str:
    return _motivo_de([p.motivo for p in leitura.por_aplicar] + [f["motivo"] for f in resultado.falhas])


def _pendentes(alterador: dict, original: Corpo, leitura: Leitura, resultado: Resultado | None, motivo: str = "") -> list[dict]:
    """O que fica para o LLM: a instrução e o texto atual dos artigos do original que nomeia."""
    itens = [{"motivo": p.motivo, "excerto": p.excerto} for p in leitura.por_aplicar]
    if resultado is None:
        itens += [{"motivo": motivo, "excerto": i.excerto} for i in leitura.instrucoes]
    else:
        itens += [{"motivo": f["motivo"], "excerto": f["excerto"]} for f in resultado.falhas]
    for item in itens:
        item["alterador"] = alterador.get("title") or alterador["id"]
        numeros = {re.sub(r"\s", "", n) for n in re.findall(r"artigos?\s+(\d+\s*\.?\s*º(?:-[A-Z])?)", item["excerto"])}
        item["artigos_original"] = [
            {"chave": a.chave, "texto": "\n".join(a.linhas).strip()} for a in original.artigos if a.numero.replace(" ", "") in numeros
        ]
    return itens


def _markdown(registo: dict, alteradores: list[dict], consolidado: Corpo, titulos_normalizados: bool,
              metodo: str = "piloto da fase 2 (consolidacao/consolidar.py), sem valor oficial") -> str:
    cabecalho = {
        "id": registo["id"],
        "title": registo["title"],
        "original": registo["path"],
        "consolidacao": {
            "metodo": metodo,
            "estado": "por verificar às cegas",
            "alteracoes_aplicadas": alteradores,
        },
    }
    if titulos_normalizados:
        cabecalho["consolidacao"]["titulos_normalizados"] = "artigos em texto corrido no original, com título pelo parser da fase 3"
    return "---\n" + yaml.safe_dump(cabecalho, allow_unicode=True, sort_keys=False) + "---\n" + consolidado.texto()


def _escrever(estados: list[dict], saida: Path, pendentes: Path) -> None:
    with saida.open("w", encoding="utf-8") as f_saida, pendentes.open("w", encoding="utf-8") as f_pendentes:
        for e in estados:
            e = dict(e)
            itens = e.pop("pendentes", None)
            if itens and e["estado"] in ("para LLM", "falhou a verificação"):
                f_pendentes.write(json.dumps({"id": e["id"], "title": e["title"], "itens": itens}, ensure_ascii=False) + "\n")
            f_saida.write(json.dumps(e, ensure_ascii=False) + "\n")


def _resumo(estados: list[dict], chave: str = "estado") -> None:
    contagem = Counter(e[chave] for e in estados)
    for estado, n in contagem.most_common():
        print(f"{n:5d}  {estado}")
        for motivo, m in Counter(e.get("motivo", "") for e in estados if e[chave] == estado).most_common(8):
            print(f"         {m:5d}  {motivo[:110]}")


def _parte(texto: str) -> tuple[int, int]:
    i, n = texto.split("/")
    return int(i), int(n)


def escala(args: argparse.Namespace) -> int:
    registos = [json.loads(l) for l in SELECAO_ESCALA.read_text(encoding="utf-8").splitlines()]
    if args.juntar:
        partes = sorted(PASTA.glob("resultados-escala.parte-*.jsonl"))
        feitos = {}
        for parte in partes:
            for linha in parte.read_text(encoding="utf-8").splitlines():
                e = json.loads(linha)
                feitos[e["id"]] = e
        estados = [feitos[r["id"]] for r in registos if r["id"] in feitos]
        em_falta = len(registos) - len(estados)
        _escrever(estados, RESULTADOS_ESCALA, PENDENTES_ESCALA)
        print(f"{len(estados)} diplomas de {len(partes)} partes em {RESULTADOS_ESCALA.relative_to(RAIZ)}; {em_falta} por fazer")
        _resumo(estados)
        return 0
    i, n = _parte(args.parte)
    registos = [r for k, r in enumerate(registos) if k % n == i - 1]
    if args.limite:
        registos = registos[: args.limite]
    saida = PASTA / f"resultados-escala.parte-{i}.jsonl"
    feitos: set[str] = set()
    if saida.exists() and args.refazer:
        refazer = set(args.refazer.read_text(encoding="utf-8").split())
        linhas = [l for l in saida.read_text(encoding="utf-8").splitlines() if l.strip() and json.loads(l)["id"] not in refazer]
        saida.write_text("".join(l + "\n" for l in linhas), encoding="utf-8")
    if saida.exists():
        feitos = {json.loads(l)["id"] for l in saida.read_text(encoding="utf-8").splitlines() if l.strip()}
    por_fazer = [r for r in registos if r["id"] not in feitos]
    print(f"parte {i}/{n}: {len(registos)} diplomas, {len(feitos)} feitos, {len(por_fazer)} por fazer", flush=True)
    inicio = time.time()
    contagem: Counter = Counter()
    with saida.open("a", encoding="utf-8") as f:
        for k, registo in enumerate(por_fazer, 1):
            t = time.time()
            try:
                e = processar(registo)
            except Exception as erro:  # noqa: BLE001  (um diploma com erro não para a corrida)
                e = {"id": registo["id"], "title": registo["title"], "path": registo["path"], "citacoes": registo["citacoes"],
                     "n_alteracoes": len(registo["alteradores"]), "alteradores": [a.get("title") or a["id"] for a in registo["alteradores"]],
                     "estado": "erro", "triagem": "erro", "motivo": f"{type(erro).__name__}: {erro}"[:300],
                     "traceback": traceback.format_exc()[-1500:]}
            e["segundos"] = round(time.time() - t, 3)
            contagem[e["estado"]] += 1
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
            f.flush()
            if k % 100 == 0 or k == len(por_fazer):
                decorrido = time.time() - inicio
                print(f"parte {i}/{n}: {k}/{len(por_fazer)} em {decorrido:.0f} s ({decorrido / k:.2f} s/diploma); {dict(contagem)}", flush=True)
    print(f"parte {i}/{n}: fim em {time.time() - inicio:.0f} s", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--amostra", type=int, default=0, help="só uma amostra ao acaso de N diplomas")
    parser.add_argument("--semente", type=int, default=1)
    parser.add_argument("--saida", type=Path, default=PASTA / "resultados.jsonl")
    parser.add_argument("--pendentes", type=Path, default=PASTA / "pendentes.jsonl")
    parser.add_argument("--escala", action="store_true", help="todos os em vigor alterados (selecao-escala.jsonl), com vários alteradores")
    parser.add_argument("--parte", default="1/1", help="escala: a parte i/N dos diplomas que esta corrida faz")
    parser.add_argument("--limite", type=int, default=0, help="escala: só os primeiros N da parte")
    parser.add_argument("--juntar", action="store_true", help="escala: junta as partes em resultados-escala.jsonl")
    parser.add_argument("--refazer", type=Path, default=None, help="escala: ficheiro com um id por linha; esses voltam a fazer-se")
    args = parser.parse_args()
    if args.escala:
        return escala(args)
    registos = [json.loads(l) for l in SELECAO.read_text(encoding="utf-8").splitlines()]
    if args.amostra:
        registos = random.Random(args.semente).sample(registos, args.amostra)
    estados = [processar(r) for r in registos]
    _escrever(estados, args.saida, args.pendentes)
    _resumo(estados)
    return 0


if __name__ == "__main__":
    sys.exit(main())
