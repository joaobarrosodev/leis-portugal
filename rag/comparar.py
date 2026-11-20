"""Compara medições com uma medição de base, pergunta a pergunta, nas perguntas reais.

    PYTHONPATH=src python -m rag.comparar --nome ultima-milha --base app011-final \\
        --variantes um-b um-c um-c-llm --limiares 2,2.5,3,3.5,4

Lê os detalhes por pergunta de `rag/resultados/privado/<medição>-detalhe.jsonl` (do `rag.avaliar` ou do
`rag.passo_llm importar`) e escreve só números em `rag/resultados/<nome>.json`. Por medição:

- nas reais: certas, respondidas, «não sei», erradas (respondidas menos certas), e o artigo certo em
  1.º e nos 8 primeiros (os que o LLM recebe);
- as «sem resposta» respondidas por engano e as certas nas de premissa errada;
- face à base, com as reais agrupadas pelo lugar do artigo certo na base (em 1.º, do 2.º ao 8.º, fora
  dos 8): quantas ficam certas, e os ganhos (não certa → certa) e as perdas (certa → não certa);
- as mesmas contas com outros limiares, a partir das notas gravadas, sem nova corrida. Sem LLM, o
  limiar decide sozinho se responde; com LLM só se pode subir o limiar da corrida (abaixo dele o LLM
  não viu a pergunta).

Numa medição com LLM que tenha juízes (`<nome>-juizes.json`, do `rag.juiz importar`), «certas» são as
que todos os juízes dão como corretas e fundamentadas, e `certas_brando` as do critério automático.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rag.avaliar import RESULTADOS


CONTEXTO = 8  # os artigos que o LLM recebe (rag.resposta.ARTIGOS_NO_CONTEXTO)
GRUPOS = ("em_1", "de_2_a_8", "fora_dos_8")
_LIMIAR = "artigo mais próximo pouco relevante"


def ler(nome: str, resultados: Path) -> tuple[dict, dict[str, dict]]:
    """A configuração e as linhas por id de uma medição, com `certa_brando` e, se houver juízes, `certa` pelos juízes."""
    configuracao = json.loads((resultados / f"{nome}.json").read_text(encoding="utf-8"))["configuracao"]
    texto = (resultados / "privado" / f"{nome}-detalhe.jsonl").read_text(encoding="utf-8")
    linhas = {x["id"]: x for x in map(json.loads, filter(str.strip, texto.splitlines()))}
    for x in linhas.values():
        x["certa_brando"] = x["certa"]
    juizes = resultados / f"{nome.removesuffix('-llm')}-juizes.json"
    if configuracao.get("llm") and nome.endswith("-llm") and juizes.exists():
        dados = json.loads(juizes.read_text(encoding="utf-8"))
        nao_certas = {i for t, r in dados["por_tipo"].items() if t != "total" for i in r.get("ids_nao_certos", [])}
        configuracao = configuracao | {"juizes": dados["juizes"]}
        for x in linhas.values():
            if x["tipo"] != "sem_resposta":
                x["certa"] = bool(x["responde"]) and x["id"] not in nao_certas
    return configuracao, linhas


def com_limiar(x: dict, limiar: float | None, com_llm: bool) -> dict:
    """A linha como ficaria com outro limiar do reranker (a própria linha sem `limiar`)."""
    if limiar is None:
        return x
    nota = x.get("topo_reranker")
    acima = nota is None or nota >= limiar
    if com_llm:
        responde = bool(x["responde"]) and acima
    else:
        por_regra = not x["responde"] and not (x.get("motivo") or "").startswith(_LIMIAR)
        responde = acima and not por_regra
    if x["tipo"] == "sem_resposta":
        return x | {"responde": responde, "certa": not responde, "certa_brando": not responde}
    certa = responde and bool(x["certa"] if com_llm else x["acerta_topo"])
    brando = responde and bool(x["certa_brando"] if com_llm else x["acerta_topo"])
    return x | {"responde": responde, "certa": certa, "certa_brando": brando}


def _nos(xs: list[dict], k: int) -> int:
    return sum(x["posicao_artigo"] is not None and x["posicao_artigo"] <= k for x in xs)


def contas(linhas: dict[str, dict], tipo: str = "real") -> dict:
    """Os números de uma medição: o tipo principal, as «sem resposta» e as de premissa errada."""
    def de(t: str) -> list[dict]:
        return [x for x in linhas.values() if x["tipo"] == t]

    def bloco(xs: list[dict]) -> dict:
        respondidas = [x for x in xs if x["responde"]]
        certas = sum(bool(x["certa"]) for x in respondidas)
        r = {"n": len(xs), "certas": certas, "respondidas": len(respondidas), "nao_sei": len(xs) - len(respondidas),
             "erradas": len(respondidas) - certas, "artigo@1": _nos(xs, 1), f"artigo@{CONTEXTO}": _nos(xs, CONTEXTO)}
        brando = sum(bool(x["certa_brando"]) for x in respondidas)
        return r | ({"certas_brando": brando} if brando != certas else {})

    r = {tipo: bloco(de(tipo))}
    if de("sem_resposta"):
        r["sem_resposta"] = {"n": len(de("sem_resposta")), "respondidas": sum(bool(x["responde"]) for x in de("sem_resposta"))}
    if de("premissa_errada"):
        r["premissa_errada"] = bloco(de("premissa_errada"))
    return r


def grupo(x: dict) -> str:
    posicao = x["posicao_artigo"]
    return "em_1" if posicao == 1 else "de_2_a_8" if posicao is not None and posicao <= CONTEXTO else "fora_dos_8"


def face_a_base(base: dict[str, dict], variante: dict[str, dict], tipo: str = "real") -> dict:
    """Por lugar do artigo certo na base: as certas na base e na variante, os ganhos e as perdas."""
    r = {g: {"n": 0, "certas_base": 0, "certas": 0, "ganhos": 0, "perdas": 0, "artigo@1": 0, f"artigo@{CONTEXTO}": 0} for g in (*GRUPOS, "total")}
    for i, b in base.items():
        v = variante.get(i)
        if b["tipo"] != tipo or v is None:
            continue
        for g in (grupo(b), "total"):
            c = r[g]
            c["n"] += 1
            c["certas_base"] += bool(b["certa"])
            c["certas"] += bool(v["certa"])
            c["ganhos"] += bool(v["certa"]) and not b["certa"]
            c["perdas"] += bool(b["certa"]) and not v["certa"]
            c["artigo@1"] += v["posicao_artigo"] == 1
            c[f"artigo@{CONTEXTO}"] += v["posicao_artigo"] is not None and v["posicao_artigo"] <= CONTEXTO
    return r


def comparar(base: str, variantes: list[str], limiares: list[float], *, tipo: str = "real", resultados: Path = RESULTADOS) -> dict:
    conf_base, linhas_base = ler(base, resultados)
    saida = {"tipo": tipo, "base": {"nome": base, "configuracao": conf_base, **contas(linhas_base, tipo)}, "variantes": {}}
    for nome in variantes:
        conf, linhas = ler(nome, resultados)
        com_llm = bool(conf.get("llm"))
        r = {"configuracao": conf, **contas(linhas, tipo), "face_a_base": face_a_base(linhas_base, linhas, tipo), "limiares": {}}
        for limiar in limiares:
            if com_llm and conf.get("limiar") is not None and limiar < conf["limiar"]:
                continue  # abaixo do limiar da corrida o LLM não viu a pergunta
            outras = {i: com_limiar(x, limiar, com_llm) for i, x in linhas.items()}
            r["limiares"][f"{limiar:g}"] = {**contas(outras, tipo), "face_a_base": face_a_base(linhas_base, outras, tipo)}
        saida["variantes"][nome] = r
    return saida


def tabela(saida: dict) -> str:
    tipo = saida["tipo"]
    linhas = [f"| Medição | Certas | Respondidas | «Não sei» | Erradas | Artigo em 1.º | Nos {CONTEXTO} primeiros | «Sem resposta» respondidas | Premissa errada: certas | Ganhos / perdas |",
              "|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|"]

    def linha(nome: str, r: dict) -> str:
        t, s, p, f = r[tipo], r.get("sem_resposta"), r.get("premissa_errada"), r.get("face_a_base")
        sem = s["respondidas"] if s else "—"
        premissa = f"{p['certas']}/{p['respondidas']}" if p else "—"
        saldo = f"{f['total']['ganhos']} / {f['total']['perdas']}" if f else "—"
        return (f"| {nome} | {t['certas']} | {t['respondidas']} | {t['nao_sei']} | {t['erradas']} | {t['artigo@1']} | {t[f'artigo@{CONTEXTO}']} | "
                f"{sem} | {premissa} | {saldo} |")

    linhas.append(linha(saida["base"]["nome"], saida["base"]))
    for nome, r in saida["variantes"].items():
        linhas.append(linha(nome, r))
        for limiar, outro in r["limiares"].items():
            linhas.append(linha(f"{nome}, limiar {limiar}", outro))
    return "\n".join(linhas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--nome", required=True, help="O resumo fica em rag/resultados/<nome>.json.")
    parser.add_argument("--base", required=True)
    parser.add_argument("--variantes", nargs="+", required=True)
    parser.add_argument("--limiares", default="", help="Outros limiares do reranker, separados por vírgulas.")
    parser.add_argument("--tipo", default="real")
    args = parser.parse_args(argv)
    limiares = [float(x) for x in args.limiares.split(",") if x]
    saida = comparar(args.base, args.variantes, limiares, tipo=args.tipo)
    (RESULTADOS / f"{args.nome}.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(tabela(saida))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
