"""Revisão por jurista: amostras, pacote de leitura, folha de registo e medidas.

O protocolo está em `avaliacao/juristas/README.md` e as instruções para o jurista em
`avaliacao/juristas/INSTRUCOES.md`. Este script faz três coisas:

    python avaliacao/juristas.py respostas [--semente 20261114] [--nome respostas-1]
    python avaliacao/juristas.py consolidacoes [--semente 20261114] [--nome consolidacoes-1]
    python avaliacao/juristas.py importar --nome respostas-1

`respostas` tira a amostra das respostas do protótipo (as das medições com juízes, em
`rag/resultados/privado/`), e `consolidacoes` a dos artigos consolidados pelo leis-portugal
(em `data/`). Cada uma escreve em `avaliacao/privado/juristas/<nome>/`:

- `pacote.html`: o que o jurista lê, com o texto integral dos artigos à frente; sem ids, sem tipo
  de pergunta, sem resposta de referência e sem os vereditos dos juízes;
- `folha.csv`: o que o jurista preenche (separador ";", abre no Excel em português);
- `chave.jsonl`: o que liga cada número à pergunta ou ao artigo, com os vereditos dos juízes.
  Não vai para o jurista.

`importar` lê a folha preenchida e escreve as medidas em `avaliacao/juristas/<nome>.json` (só
contagens, sem texto das perguntas). Nas respostas em que o jurista e os juízes discordam, escreve
também `segunda-volta.html` e `segunda-volta.csv`: a mesma resposta, agora com a resposta de
referência, para saber se o erro está no sistema ou na referência. Correr `importar` outra vez com
a segunda volta preenchida junta esse resultado.

As perguntas reais e os resultados por pergunta estão fora do git. Numa worktree sem eles, passar
`--privado-de <pasta do checkout principal>`.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import html
import json
import random
import re
import subprocess
import sys
from collections import Counter, defaultdict
from math import sqrt
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "consolidacao"))
sys.path.insert(0, str(RAIZ / "avaliacao"))
import comum  # noqa: E402
import texto as ctexto  # noqa: E402


RESUMOS = RAIZ / "avaliacao" / "juristas"

# Medições com juízes, da mais antiga para a mais recente: uma pergunta medida em várias fica
# com a mais recente (o índice e o método dessa medição).
MEDICOES = ("teste-reescrito", "sinteticas-reescrito", "texto-alterado-2323", "ue-reescrito", "ue-reescrito-2")
PAPEIS = ("a", "b", "c", "s")

# Respostas dadas: quantas por tipo na amostra principal.
QUOTAS = {
    "real": 40, "texto_alterado": 20, "composta": 15, "premissa_errada": 10,
    "literal": 10, "temporal": 10, "revogada": 10, "ue": 10,
}
RECUSAS_COM_RESPOSTA = 10  # a pergunta tem resposta no acervo e o sistema disse "não sei"
RECUSAS_SEM_RESPOSTA = 10  # a pergunta não tem resposta (lei inexistente, jurisprudência, caso concreto…)
CONTROLOS = 15  # respostas que os juízes deram como não certas, fora da amostra principal

# Artigos consolidados: quantos por caminho, e no máximo quantos do mesmo diploma.
# "visado" é um bloco à parte: artigos que o DRE dá como alterados ou revogados e que o consolidado
# deixou iguais (candidatos a instrução esquecida). Não entra na taxa de erro de nenhum caminho.
QUOTAS_CONSOLIDACAO = {"llm": 45, "corrido": 35, "regra": 30, "anexo": 20, "visado": 20}
POR_DIPLOMA = 3
MAX_CARACTERES = 12_000

VEREDICTOS_RESPOSTA = {"certa", "reservas", "errada", "recusa_correta", "recusa_indevida", "duvida"}
CAUSAS = {"pesquisa", "versao", "vigencia", "consolidacao", "leitura", "interpretacao", "outra"}
GRAVIDADES_RESERVA = {"menor", "forma"}
VEREDICTOS_CONSOLIDACAO = {"certo", "errado", "duvida"}
ERROS_CONSOLIDACAO = {"mal_aplicada", "esquecida", "sem_instrucao", "condicional", "forma", "outro"}
GRAVIDADES = {"grave", "menor", "forma"}


# --- utilitários -----------------------------------------------------------------------------


def _ler(caminho: Path) -> list[dict]:
    if not caminho.exists():
        return []
    return [json.loads(x) for x in caminho.read_text(encoding="utf-8").splitlines() if x.strip()]


def _escrever_jsonl(caminho: Path, linhas: list[dict]) -> None:
    caminho.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in linhas), encoding="utf-8")


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / d, (c + m) / d)


def kappa(pares: list[tuple[bool, bool]]) -> float | None:
    """Kappa de Cohen entre dois classificadores binários."""
    n = len(pares)
    if n == 0:
        return None
    po = sum(a == b for a, b in pares) / n
    pa = sum(a for a, _ in pares) / n
    pb = sum(b for _, b in pares) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else round((po - pe) / (1 - pe), 3)


def _pasta(nome: str) -> Path:
    pasta = RAIZ / "avaliacao" / "privado" / "juristas" / nome
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _folha(caminho: Path, colunas: list[str], n: int) -> None:
    with caminho.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(colunas)
        for i in range(1, n + 1):
            w.writerow([i] + [""] * (len(colunas) - 1))


def _ler_folha(caminho: Path) -> dict[int, dict]:
    if not caminho.exists():
        return {}
    with caminho.open(encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.DictReader(f, delimiter=";"))
    return {int(x["n"]): {k: (v or "").strip().lower() if k != "nota" else (v or "").strip() for k, v in x.items()} for x in linhas if (x.get("n") or "").strip().isdigit()}


_CSS = """
:root{--fundo:#fbfaf7;--texto:#1d1d1b;--suave:#5c5a55;--linha:#dcd8cf;--caixa:#ffffff;--marca:#7a4b00;--aviso:#8a1c1c}
@media (prefers-color-scheme: dark){:root{--fundo:#181816;--texto:#ecebe6;--suave:#a9a69e;--linha:#3a3934;--caixa:#22221f;--marca:#e0a64a;--aviso:#f08a8a}}
body{background:var(--fundo);color:var(--texto);font:16px/1.55 Georgia,serif;margin:0 auto;max-width:980px;padding:24px 16px 80px}
h1{font-size:1.6em}h2{font-size:1.25em;margin-top:2.4em;border-top:2px solid var(--marca);padding-top:.6em}
h3{font-size:1em;color:var(--suave);margin:1.4em 0 .4em;text-transform:uppercase;letter-spacing:.04em}
.caixa{background:var(--caixa);border:1px solid var(--linha);border-radius:6px;padding:12px 14px;margin:.4em 0}
.texto{white-space:pre-wrap;font-family:ui-monospace,Menlo,monospace;font-size:13.5px;line-height:1.5}
.citado{border-left:4px solid var(--marca)}.aviso{color:var(--aviso)}.suave{color:var(--suave)}
.lado{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media (max-width:760px){.lado{grid-template-columns:1fr}}
details summary{cursor:pointer;color:var(--suave)}a{color:var(--marca)}
@media print{h2{break-before:page}}
"""


def _html(titulo: str, cabecalho: str, itens: list[str]) -> str:
    return (
        f"<!doctype html><html lang=\"pt\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{html.escape(titulo)}</title><style>{_CSS}</style></head><body><h1>{html.escape(titulo)}</h1>{cabecalho}{''.join(itens)}</body></html>\n"
    )


def _e(t: str | None) -> str:
    return html.escape(t or "")


def _cortar(t: str, limite: int = MAX_CARACTERES) -> str:
    return t if len(t) <= limite else t[:limite] + f"\n\n[… cortado: mais {len(t) - limite} caracteres; ver a ligação oficial]"


# --- respostas -------------------------------------------------------------------------------


def _artigos_da_mensagem(mensagem: str) -> list[str]:
    bloco = mensagem.split("Artigos:", 1)[1].rsplit("Pergunta:", 1)[0].strip()
    return [x.strip() for x in re.split(r"\n(?=\[\d+\] )", bloco) if x.strip()]


def _referencias(privado: Path) -> dict[str, dict]:
    ficheiros = (
        RAIZ / "avaliacao" / "perguntas.jsonl", RAIZ / "avaliacao" / "perguntas-ue.jsonl",
        privado / "avaliacao" / "privado" / "perguntas-reais.jsonl", privado / "avaliacao" / "privado" / "perguntas-coloquiais.jsonl",
    )
    return {d["id"]: d for f in ficheiros for d in _ler(f)}


def _medicoes(privado: Path, refs: dict[str, dict]) -> dict[str, dict]:
    resultados = privado / "rag" / "resultados" / "privado"
    itens: dict[str, dict] = {}
    for nome in MEDICOES:
        detalhe = _ler(resultados / f"{nome}-llm-detalhe.jsonl")
        if not detalhe:
            print(f"aviso: sem {nome}-llm-detalhe.jsonl em {resultados}", file=sys.stderr)
            continue
        pasta = resultados / "llm" / nome
        entradas = {d["id"]: d["mensagem"] for f in sorted(pasta.glob("entrada-*.jsonl")) for d in _ler(f)}
        saidas = {d["id"]: d for f in sorted(pasta.glob("saida-*.jsonl")) for d in _ler(f)}
        juizes = {p: {d["id"]: d for f in sorted(pasta.glob(f"juiz-{p}-saida-*.jsonl")) for d in _ler(f)} for p in PAPEIS}
        juizes = {p: v for p, v in juizes.items() if v}
        for d in detalhe:
            ref = refs.get(d["id"], {})
            # O que conta é o que o sistema mostrou (`detalhe`): no modo estrito, o travão pode recusar
            # depois de o LLM ter escrito uma resposta, e essa resposta (a que os juízes julgaram) não
            # chegou a quem perguntou.
            responde = bool(d["responde"])
            vs = [juizes[p].get(d["id"]) for p in juizes]
            julgada = responde and bool(juizes) and all(vs)
            mensagem = entradas.get(d["id"])
            saida = saidas.get(d["id"], {})
            motivo = d.get("motivo") or ""
            if not responde and saida and not saida.get("responde") and saida.get("resposta"):
                motivo = saida["resposta"]  # a explicação do LLM para não responder
            itens[d["id"]] = {
                "id": d["id"], "medicao": nome,
                "tipo": "ue" if ref.get("ambito") == "ue" and d["tipo"] != "sem_resposta" else d["tipo"],
                "pergunta": d["pergunta"], "data": d["data"], "responde": responde,
                "resposta": (d.get("resposta") or saida.get("resposta")) if responde else None,
                "citacoes": (saida.get("citacoes") or []) if responde else [],
                "avisos": d.get("avisos") or [], "motivo": motivo, "topo": d.get("topo"),
                "artigos": _artigos_da_mensagem(mensagem) if mensagem else [],
                "juizes_ok": (all(v["veredicto"] == "correta" and v.get("fundamentada") is True for v in vs) if julgada else None),
                "juizes": {p: {"veredicto": v["veredicto"], "fundamentada": v.get("fundamentada"), "nota": v.get("nota", "")} for p, v in zip(juizes, vs, strict=False) if v} if julgada else {},
            }
    return itens


def _bloco_resposta(n: int, x: dict) -> str:
    partes = [f"<h2 id=\"r{n}\">N.º {n}</h2>", f"<p class=\"suave\">Data de referência: {_e(x['data'])}</p>",
              "<h3>Pergunta</h3>", f"<div class=\"caixa\">{_e(x['pergunta'])}</div>"]
    if x["responde"]:
        partes += ["<h3>Resposta do sistema</h3>", f"<div class=\"caixa\">{_e(x['resposta'])}</div>"]
    else:
        motivo = x.get("motivo") or ""
        partes +=["<h3>Resposta do sistema</h3>", f"<div class=\"caixa\"><strong>O sistema não respondeu.</strong> {_e(motivo)}</div>"]
    if x["avisos"]:
        partes += ["<h3>Avisos que o sistema mostrou</h3>", "".join(f"<div class=\"caixa aviso\">{_e(a)}</div>" for a in x["avisos"])]
    if x["artigos"]:
        titulo = "Artigos que o sistema leu (os citados na resposta estão marcados)" if x["responde"] else "Artigos que o sistema encontrou e rejeitou"
        partes.append(f"<h3>{titulo}</h3>")
        for i, a in enumerate(x["artigos"], 1):
            citado = i in x["citacoes"]
            marca = "<strong>Citado na resposta.</strong>\n" if citado else ""
            partes.append(f"<div class=\"caixa texto{' citado' if citado else ''}\">{marca}{_e(_cortar(a))}</div>")
    elif not x["responde"]:
        partes.append(f"<p class=\"suave\">O sistema recusou antes de ler artigos. O resultado mais próximo da pesquisa era: {_e(x.get('topo'))}.</p>")
    return "".join(partes)


def respostas(args: argparse.Namespace) -> None:
    privado = Path(args.privado_de).resolve() if args.privado_de else RAIZ
    refs = _referencias(privado)
    itens = _medicoes(privado, refs)
    rnd = random.Random(args.semente)
    escolhidos: list[tuple[str, dict]] = []
    usados: set[str] = set()

    def tirar(candidatos: list[dict], k: int, bloco: str) -> None:
        candidatos = sorted(candidatos, key=lambda x: x["id"])
        rnd.shuffle(candidatos)
        falta = k - min(k, len(candidatos))
        if falta:
            print(f"aviso: {bloco} pede {k} e só há {len(candidatos)}", file=sys.stderr)
        for x in candidatos[:k]:
            escolhidos.append((bloco, x))
            usados.add(x["id"])

    respondidas = [x for x in itens.values() if x["responde"] and x["tipo"] != "sem_resposta" and x["juizes_ok"] is not None]
    for tipo, k in QUOTAS.items():
        tirar([x for x in respondidas if x["tipo"] == tipo], k, f"principal:{tipo}")
    # Recusas: primeiro as que leram artigos (o jurista vê o que o sistema rejeitou).
    recusas = [x for x in itens.values() if not x["responde"] and x["tipo"] != "sem_resposta"]
    com_artigos = [x for x in recusas if x["artigos"]]
    tirar(com_artigos if len(com_artigos) >= RECUSAS_COM_RESPOSTA else recusas, RECUSAS_COM_RESPOSTA, "recusa_com_resposta")
    tirar([x for x in itens.values() if x["tipo"] == "sem_resposta"], RECUSAS_SEM_RESPOSTA, "recusa_sem_resposta")
    tirar([x for x in respondidas if x["juizes_ok"] is False and x["id"] not in usados], CONTROLOS, "controlo")

    rnd.shuffle(escolhidos)  # a ordem não denuncia o bloco
    pasta = _pasta(args.nome)
    chave = []
    blocos = []
    for n, (bloco, x) in enumerate(escolhidos, 1):
        blocos.append(_bloco_resposta(n, x))
        ref = refs.get(x["id"], {})
        chave.append({"n": n, "bloco": bloco, "id": x["id"], "medicao": x["medicao"], "tipo": x["tipo"], "responde": x["responde"],
                      "juizes_ok": x["juizes_ok"], "juizes": x["juizes"], "referencia": ref.get("resposta"), "fonte": ref.get("fonte")})
    populacao = Counter(x["tipo"] for x in respondidas)
    meta = {"amostra": "respostas", "semente": args.semente, "medicoes": list(MEDICOES), "quotas": QUOTAS,
            "populacao_respondidas_julgadas": dict(populacao),
            "juizes_ok_na_populacao": {t: sum(1 for x in respondidas if x["tipo"] == t and x["juizes_ok"]) for t in populacao}}
    _escrever_jsonl(pasta / "chave.jsonl", [{"meta": meta}, *chave])
    cabecalho = (
        "<p>Para cada número: leia a pergunta, a resposta e os artigos, e registe na folha (<code>folha.csv</code>) "
        "o veredicto, a causa e uma nota. As regras estão em <code>INSTRUCOES.md</code>; o essencial:</p>"
        "<div class=\"caixa\"><strong>certa</strong>: conclusão certa, base legal exata, sem omissões relevantes para o que se pergunta. "
        "<strong>reservas</strong>: conclusão principal certa, mas falta uma exceção, condição ou prazo secundário (gravidade menor ou de forma). "
        "<strong>errada</strong>: conclusão principal errada, norma revogada ou desatualizada, ou uma regra inventada. "
        "Se o sistema não respondeu: <strong>recusa_correta</strong> ou <strong>recusa_indevida</strong>. "
        "Sem certeza sem uma pesquisa demorada: <strong>duvida</strong>.</div>"
        f"<p class=\"suave\">{len(escolhidos)} respostas, por ordem ao acaso. Registe também os minutos de cada uma.</p>"
    )
    (pasta / "pacote.html").write_text(_html("Revisão de respostas", cabecalho, blocos), encoding="utf-8")
    _folha(pasta / "folha.csv", ["n", "veredicto", "gravidade", "causa", "base_certa", "nota", "minutos"], len(escolhidos))
    print(f"{len(escolhidos)} respostas em {pasta}: " + ", ".join(f"{b} {c}" for b, c in Counter(b.split(':')[0] for b, _ in escolhidos).items()))


# --- consolidações ---------------------------------------------------------------------------


_ROTULO = re.compile(r"(Altera|Adita|Revoga)\s+Artigo\s+(\S+)", re.I)


def _consolidados() -> list[Path]:
    saida = subprocess.run(["grep", "-rlF", "--include=*.md", ctexto.CONSOLIDADO_AQUI, "data"], cwd=RAIZ, capture_output=True, text=True)
    return sorted(RAIZ / p for p in saida.stdout.split())


def _caminhos_alteradores() -> dict[str, str]:
    caminhos = {}
    for f in ("selecao.jsonl", "selecao-escala.jsonl"):
        for d in _ler(RAIZ / "consolidacao" / f):
            for a in d.get("alteradores") or []:
                if a.get("id") and a.get("path"):
                    caminhos[a["id"]] = a["path"]
    return caminhos


_INICIO_ARTIGO = re.compile(r"^(?:Art(?:igo)?\.?\s*)?(\d+)\.?\s*[º°o](?:-[A-Z])?(?=[\s.,:;-])", re.I)


def _paragrafos(texto: str) -> list[str]:
    return [p.strip() for p in texto.split("\n\n") if p.strip()]


def _unidades_corrido(publicado: str, consolidado: str, visados: list[tuple[str, str, dict | None]] = ()) -> list[dict]:
    """Num diploma sem artigos identificados (texto corrido, `consolidacao/llm_corrido.py`), cada
    passagem que mudou é uma unidade: os parágrafos do original que deram lugar a outros, com o
    parágrafo do artigo onde estão ("Art. 52.º …", "3.º …") como contexto."""
    orig = _paragrafos(publicado)
    cons: list[str] = []
    notas: list[list[str]] = []  # as notas "> Alterado pelo/a …" a seguir a cada parágrafo
    for p in _paragrafos(consolidado):
        if ctexto._NOTA.match(p) and cons:
            notas[-1].append(p)
        elif not ctexto._NOTA.match(p):
            cons.append(p)
            notas.append([])
    unidades = []
    matcher = difflib.SequenceMatcher(None, orig, cons, autojunk=False)
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            continue
        inicio = next((k for k in range(i1, -1, -1) if k < len(orig) and _INICIO_ARTIGO.match(orig[k])), None)
        numero = None
        contexto: list[str] = []
        if inicio is not None:
            numero = _INICIO_ARTIGO.match(orig[inicio]).group(1) + ".º"
            if inicio < i1:
                contexto = [orig[inicio], "[…]"] if inicio < i1 - 1 else [orig[inicio]]
        unidades.append({
            "chave": f"corrido:{i1}-{i2}", "numero": numero, "parte": "", "epigrafe": "texto corrido, sem artigos identificados",
            "caminho": "corrido", "visado_sem_nota": False,
            "original": "\n\n".join(contexto + (orig[i1:i2] or ["(nada: o texto foi aditado aqui)"])),
            "consolidado": "\n\n".join(contexto + (cons[j1:j2] or ["(nada: o texto foi suprimido)"])
                                        + [n for k in range(max(j1, j2 - 1), min(j2 + 1, len(cons))) for n in notas[k]]),
        })
    # Artigos que o DRE dá como visados e onde o consolidado não mudou nada.
    tocados = {u["numero"] for u in unidades}
    inicios = [(k, _INICIO_ARTIGO.match(p)) for k, p in enumerate(orig)]
    inicios = [(k, m.group(1) + ".º") for k, m in inicios if m]
    for numero, texto_dre, ato in visados:
        if numero in tocados:
            continue
        k = next((i for i, (_, n) in enumerate(inicios) if n == numero), None)
        if k is None:
            continue
        de, ate = inicios[k][0], (inicios[k + 1][0] if k + 1 < len(inicios) else len(orig))
        bloco = "\n\n".join(orig[de:ate])
        tocados.add(numero)
        unidades.append({"chave": f"corrido:{numero}", "numero": numero, "parte": "", "epigrafe": "texto corrido, sem artigos identificados",
                         "caminho": "corrido", "visado_sem_nota": True, "rotulo_dre": texto_dre, "original": bloco, "consolidado": bloco}
                        | ({"atos": [ato]} if ato else {}))
    return unidades


def _unidades(caminho: Path) -> list[dict]:
    """Os artigos (e corpos de anexo) alterados num consolidado, e os que o DRE dá como visados sem
    nota de alteração no consolidado (possíveis instruções esquecidas)."""
    markdown = caminho.read_text(encoding="utf-8")
    meta = ctexto.front_matter(markdown)
    rotulo = str((meta.get("version") or {}).get("label") or "")
    caminho_metodo = "llm" if "com um LLM" in rotulo else "regra"
    try:
        publicado = ctexto.publicado(caminho)
    except ValueError:
        return []
    original = ctexto.dividir(publicado)
    consolidado = ctexto.dividir(ctexto.corpo(markdown))
    historico_f = caminho.with_name(caminho.name[:-3] + ".versoes.json")
    historico = json.loads(historico_f.read_text(encoding="utf-8")) if historico_f.exists() else {}
    ultima = (historico.get("versions") or [{}])[-1]
    atos = ultima.get("acts") or []
    rotulos = ultima.get("changes") or []
    base = {"diploma": meta.get("title"), "id": meta.get("id"), "path": str(caminho.relative_to(RAIZ)),
            "url": (meta.get("source") or {}).get("official_url"), "rotulo": rotulo, "atos": atos}
    if not consolidado.artigos:
        return [base | u for u in _unidades_corrido(publicado, ctexto.corpo(markdown), _visados_pelo_dre(meta, rotulos))]
    unidades = []
    chaves_c = consolidado.chaves_unicas()
    com_nota = set()
    for a in consolidado.artigos:
        chave = chaves_c[id(a)]
        if not a.notas:
            continue
        orig = original.artigo(a.parte, chave.split("::")[-1])
        com_nota.add(chave)
        unidades.append(base | {"chave": chave, "numero": a.numero, "parte": a.parte, "epigrafe": a.epigrafe,
                                "caminho": "anexo" if a.parte else caminho_metodo, "visado_sem_nota": False,
                                "original": "\n".join(orig.linhas) if orig else "(o artigo não existe no original: foi aditado)",
                                "consolidado": "\n".join(a.linhas)})
    # Corpos de anexo (quadros, listas) alterados fora de artigos.
    for s in consolidado.segmentos:
        if isinstance(s, list) and any(ctexto._NOTA.match(l) for l in s) and s and ctexto._ANEXO.match(s[0]):
            titulo = s[0][3:].strip()
            orig = next((o for o in original.segmentos if isinstance(o, list) and o and o[0].strip() == s[0].strip()), None)
            unidades.append(base | {"chave": f"anexo:{titulo}", "numero": None, "parte": titulo, "epigrafe": titulo, "caminho": "anexo",
                                    "visado_sem_nota": False, "original": "\n".join(orig) if orig else "(sem corpo correspondente no original)",
                                    "consolidado": "\n".join(s)})
    # Artigos que o DRE dá como alterados ou revogados e que o consolidado deixou iguais.
    numeros_com_nota = {c.split("::")[-1].split("#")[0] for c in com_nota}  # o mesmo número noutra parte também conta
    for numero, texto_dre, ato in _visados_pelo_dre(meta, rotulos):
        if numero in numeros_com_nota:
            continue
        orig = original.artigo("", numero)
        if orig is None:
            continue
        com_nota.add(numero)
        unidades.append(base | {"chave": numero, "numero": numero, "parte": "", "epigrafe": orig.epigrafe, "caminho": caminho_metodo,
                                "visado_sem_nota": True, "rotulo_dre": texto_dre, "original": "\n".join(orig.linhas),
                                "consolidado": "\n".join(orig.linhas)} | ({"atos": [ato]} if ato else {}))
    return unidades


_ARTIGOS_NO_ROTULO = re.compile(r"\b(?:arts?\.|artigos?)\s*((?:\d+\s*\.?\s*[º°o](?:-[A-Z])?\s*(?:,|e|a)?\s*)+)", re.I)


def _visados_pelo_dre(meta: dict, rotulos: list[str]) -> list[tuple[str, str, dict | None]]:
    """Os artigos do diploma que o DRE dá como alterados ou revogados: os rótulos do histórico
    ("Altera Artigo 5.º") e os das relações `amended_by` / `repealed_by` ("Revogados os arts. 37º,
    61º e 62º …"). Só o número: a leitura do rótulo é do jurista."""
    visados: list[tuple[str, str]] = []
    for r in rotulos:
        m = _ROTULO.search(r)
        if m and m.group(2)[0].isdigit():
            visados.append((ctexto.numero_artigo(m.group(2)), m.group(0), None))
    for rel in meta.get("relationships") or []:
        if rel.get("type") not in {"amended_by", "repealed_by"} or not rel.get("label"):
            continue
        rotulo = str(rel["label"]).replace("\0", "").strip()
        # Só a primeira lista de artigos: as seguintes costumam ser de outro diploma ("nos termos do
        # art. 5.º do Decreto-Lei …"). Uma lista de exceções ("com excepção do art. 45.º") não conta.
        m = _ARTIGOS_NO_ROTULO.search(rotulo)
        if not m or re.search(r"exce[pç]+[ãa]o|\bexceto\b|\bsalvo\b", rotulo[max(0, m.start() - 30) : m.start()], re.I):
            continue
        fonte = str(rel.get("source") or "")
        ato = {"id": rel.get("target"), "title": None, "published": str(rel.get("date") or ""),
               "dre_path": fonte.replace("https://diariodarepublica.pt", "").replace("/analise-juridica/informacoes-gerais/", "/detalhe/") or None}
        for n in re.findall(r"(\d+)\s*\.?\s*[º°o](-[A-Z])?", m.group(1)):
            visados.append((ctexto.numero_artigo(n[0] + ".º" + n[1]), rotulo, ato))
    vistos: set[tuple[str, str]] = set()
    unicos = []
    for v in visados:
        if v[:2] not in vistos:
            vistos.add(v[:2])
            unicos.append(v)
    return unicos


def _caminho_por_titulo(ato: dict) -> str | None:
    """O registo de um alterador que não está nas seleções da consolidação: procura-se pelo número
    do título no ano de publicação (`decreto-regulamentar-11-2007.md`) e confirma-se pelo id."""
    m = re.search(r"n\.?\s*º\s*(\S+)", ato.get("title") or "")
    ano = (ato.get("published") or "")[:4]
    if not ano or not ato.get("id"):
        return None
    numero = m.group(1).replace("/", "-").lower() if m else ""  # sem título: todos os registos do ano
    candidatos = [*(RAIZ / "data").glob(f"*/*/{ano}/*-{numero}*.md"), *(RAIZ / "data").glob(f"*/serie-ii/*/{ano}/*-{numero}*.md")]
    for f in sorted(candidatos):
        with f.open(encoding="utf-8") as fh:
            if f"id: {ato.get('id')}\n" in fh.read(3000):
                return str(f.relative_to(RAIZ))
    return None


def _trechos_corridos(caminho: Path, u: dict) -> list[str]:
    """Num alterador sem artigos identificados: os parágrafos que nomeiam o diploma (de preferência
    também o artigo) e os três seguintes, onde costuma vir a nova redação."""
    try:
        paras = _paragrafos(ctexto.sem_ligacoes(ctexto.alterador(caminho)))
    except (ValueError, KeyError):
        return []
    padrao = ctexto.padrao_diploma(u["diploma"] or "")
    idx = [k for k, p in enumerate(paras) if padrao and padrao.search(p)]
    if u["numero"]:
        idx = [k for k in idx if comum.menciona_artigo(paras[k], u["numero"])] or idx
    return ["\n\n".join(paras[k : k + 4]) for k in idx[:6]]


def _excertos_alterador(u: dict, caminhos: dict[str, str]) -> list[dict]:
    excertos = []
    for ato in u["atos"]:
        url = f"https://diariodarepublica.pt{ato['dre_path']}" if ato.get("dre_path") else None
        caminho = caminhos.get(ato.get("id")) or _caminho_por_titulo(ato)
        trechos: list[str] = []
        if caminho and (RAIZ / caminho).exists():
            try:
                arts = ctexto.artigos_alteradores(ctexto.alterador(RAIZ / caminho), u["diploma"] or "")
            except (ValueError, KeyError):
                arts = []
            if u["numero"]:
                visados = [a for a in arts if comum.menciona_artigo(ctexto.sem_ligacoes("\n".join(a.linhas)), u["numero"])]
                arts = visados or arts
            trechos = [ctexto.sem_ligacoes("\n".join(a.linhas)) for a in arts]
            if not trechos:
                trechos = _trechos_corridos(RAIZ / caminho, u)
            titulo = ato.get("title") or ctexto.front_matter((RAIZ / caminho).read_text(encoding="utf-8")).get("title")
        else:
            titulo = ato.get("title") or ato.get("id")
        excertos.append({"titulo": titulo, "url": url, "trechos": trechos})
    return excertos


def _bloco_consolidacao(n: int, u: dict, excertos: list[dict]) -> str:
    ligacao = f" — <a href=\"{_e(u['url'])}\">publicação oficial</a>" if u.get("url") else ""
    partes = [f"<h2 id=\"c{n}\">N.º {n}</h2>", f"<p><strong>{_e(u['diploma'])}</strong>{ligacao}</p>",
              f"<p>{'Anexo: ' + _e(u['parte']) + ' · ' if u['parte'] else ''}{_e(('Artigo ' + u['numero']) if u['numero'] else '')} {_e(u['epigrafe'])}</p>"]
    if u["visado_sem_nota"]:
        partes.append(f"<p class=\"aviso\">O DRE diz <em>{_e(u['rotulo_dre'])}</em>, mas a versão consolidada deixou este artigo igual ao original. Confirme se havia alteração ao texto.</p>")
    partes += ["<div class=\"lado\">",
               f"<div><h3>Original publicado</h3><div class=\"caixa texto\">{_e(_cortar(ctexto.sem_ligacoes(u['original'])))}</div></div>",
               f"<div><h3>Versão consolidada</h3><div class=\"caixa texto citado\">{_e(_cortar(ctexto.sem_ligacoes(u['consolidado'])))}</div></div>",
               "</div>", "<h3>Diplomas que alteram (artigos que falam deste diploma)</h3>"]
    for x in excertos:
        lig = f" — <a href=\"{_e(x['url'])}\">publicação oficial</a>" if x["url"] else ""
        partes.append(f"<p><strong>{_e(x['titulo'])}</strong>{lig}</p>")
        if x["trechos"]:
            partes += [f"<div class=\"caixa texto\">{_e(_cortar(t, 6000))}</div>" for t in x["trechos"][:6]]
        else:
            partes.append("<p class=\"suave\">Sem o texto no acervo: abra a publicação oficial.</p>")
    return "".join(partes)


def consolidacoes(args: argparse.Namespace) -> None:
    rnd = random.Random(args.semente)
    ficheiros = _consolidados()
    print(f"{len(ficheiros)} consolidados pelo leis-portugal em data/", file=sys.stderr)
    por_caminho: dict[str, list[dict]] = defaultdict(list)
    sem_unidades = 0
    for f in ficheiros:
        us = _unidades(f)
        sem_unidades += not us
        for u in us:
            por_caminho["visado" if u["visado_sem_nota"] else u["caminho"]].append(u)
    escolhidas: list[dict] = []
    por_diploma: Counter = Counter()
    for caminho, k in QUOTAS_CONSOLIDACAO.items():
        candidatos = sorted(por_caminho[caminho], key=lambda u: (u["id"], u["chave"]))
        rnd.shuffle(candidatos)
        tiradas = 0
        for u in candidatos:
            if tiradas == k:
                break
            if por_diploma[u["id"]] >= POR_DIPLOMA:
                continue
            por_diploma[u["id"]] += 1
            escolhidas.append(u)
            tiradas += 1
        if tiradas < k:
            print(f"aviso: {caminho} pede {k} e só há {tiradas}", file=sys.stderr)
    rnd.shuffle(escolhidas)
    caminhos = _caminhos_alteradores()
    pasta = _pasta(args.nome)
    blocos, chave = [], []
    for n, u in enumerate(escolhidas, 1):
        blocos.append(_bloco_consolidacao(n, u, _excertos_alterador(u, caminhos)))
        chave.append({"n": n, "id": u["id"], "path": u["path"], "chave": u["chave"], "caminho": "visado" if u["visado_sem_nota"] else u["caminho"],
                      "metodo": u["caminho"], "visado_sem_nota": u["visado_sem_nota"], "rotulo_dre": u.get("rotulo_dre")})
    meta = {"amostra": "consolidacoes", "semente": args.semente, "quotas": QUOTAS_CONSOLIDACAO, "por_diploma": POR_DIPLOMA,
            "diplomas": len(ficheiros), "diplomas_sem_unidades": sem_unidades,
            "populacao": {c: len(v) for c, v in por_caminho.items()},
            "diplomas_na_amostra": len(por_diploma)}
    _escrever_jsonl(pasta / "chave.jsonl", [{"meta": meta}, *chave])
    cabecalho = (
        "<p>Cada número é um artigo de um diploma consolidado pelo leis-portugal (sem valor oficial). "
        "Compare o original com a versão consolidada e com os diplomas que o alteram, e registe na folha "
        "(<code>folha.csv</code>) se a versão consolidada é a redação em vigor. As regras estão em <code>INSTRUCOES.md</code>.</p>"
        "<div class=\"caixa\"><strong>certo</strong>: a versão consolidada é exatamente a redação que resulta das alterações. "
        "<strong>errado</strong>: não é; diga o erro (<em>mal_aplicada</em>, <em>esquecida</em>, <em>sem_instrucao</em>, <em>condicional</em>, <em>forma</em>, <em>outro</em>) e a gravidade. "
        "<strong>duvida</strong>: não dá para decidir com o que está aqui.</div>"
        f"<p class=\"suave\">{len(escolhidas)} artigos de {len(por_diploma)} diplomas, por ordem ao acaso.</p>"
    )
    (pasta / "pacote.html").write_text(_html("Revisão de consolidações", cabecalho, blocos), encoding="utf-8")
    _folha(pasta / "folha.csv", ["n", "veredicto", "erro", "gravidade", "nota", "minutos"], len(escolhidas))
    print(f"{len(escolhidas)} artigos de {len(por_diploma)} diplomas em {pasta}; população: {meta['populacao']}")


# --- importar --------------------------------------------------------------------------------


def _taxa(k: int, n: int) -> dict:
    inf, sup = wilson(k, n)
    return {"k": k, "n": n, "taxa": round(k / n, 3) if n else None, "ic95": [round(inf, 3), round(sup, 3)]}


def _validar(folha: dict[int, dict], chave: list[dict], validos: dict[str, set[str]]) -> list[str]:
    problemas = []
    for c in chave:
        linha = folha.get(c["n"])
        if not linha or not linha.get("veredicto"):
            problemas.append(f"n.º {c['n']}: sem veredicto")
            continue
        for campo, valores in validos.items():
            v = linha.get(campo, "")
            if v and v not in valores:
                problemas.append(f"n.º {c['n']}: {campo} '{v}' não é um de {sorted(valores)}")
    return problemas


def _importar_respostas(pasta: Path, meta: dict, chave: list[dict]) -> dict:
    folha = _ler_folha(pasta / "folha.csv")
    problemas = _validar(folha, chave, {"veredicto": VEREDICTOS_RESPOSTA, "gravidade": GRAVIDADES_RESERVA, "causa": CAUSAS, "base_certa": {"sim", "nao", "não"}})
    for c in chave:
        v = folha.get(c["n"], {}).get("veredicto")
        if v in {"certa", "reservas", "errada"} and not c["responde"] or v in {"recusa_correta", "recusa_indevida"} and c["responde"]:
            problemas.append(f"n.º {c['n']}: veredicto '{v}' não condiz com {'resposta dada' if c['responde'] else 'recusa'}")
        if v in {"reservas", "errada", "recusa_indevida"} and not folha[c["n"]].get("causa"):
            problemas.append(f"n.º {c['n']}: falta a causa")
    segunda = _ler_folha(pasta / "segunda-volta.csv")
    res: dict = {"problemas_na_folha": problemas}

    def v(c):
        return folha.get(c["n"], {}).get("veredicto")

    principal = [c for c in chave if c["bloco"].startswith("principal:")]
    por_tipo = {}
    for tipo in dict.fromkeys(c["tipo"] for c in principal):
        cs = [c for c in principal if c["tipo"] == tipo and v(c) in {"certa", "reservas", "errada"}]
        por_tipo[tipo] = {"julgadas": len(cs), "duvidas": sum(1 for c in principal if c["tipo"] == tipo and v(c) == "duvida"),
                          "certas_estrito": _taxa(sum(v(c) == "certa" for c in cs), len(cs)),
                          "certas_com_reservas": _taxa(sum(v(c) in {"certa", "reservas"} for c in cs), len(cs)),
                          "erradas": sum(v(c) == "errada" for c in cs)}
    cs = [c for c in principal if v(c) in {"certa", "reservas", "errada"}]
    res["amostra_principal"] = {"por_tipo": por_tipo, "total": {
        "julgadas": len(cs), "certas_estrito": _taxa(sum(v(c) == "certa" for c in cs), len(cs)),
        "certas_com_reservas": _taxa(sum(v(c) in {"certa", "reservas"} for c in cs), len(cs)),
        "erradas": sum(v(c) == "errada" for c in cs),
        "nota": "total da amostra por quotas, não proporcional à população: citar por tipo"}}
    for bloco in ("recusa_com_resposta", "recusa_sem_resposta"):
        rs = [c for c in chave if c["bloco"] == bloco and v(c) in {"recusa_correta", "recusa_indevida"}]
        res[bloco] = {"julgadas": len(rs), "indevidas": sum(v(c) == "recusa_indevida" for c in rs), "corretas": sum(v(c) == "recusa_correta" for c in rs)}
    # Concordância com os juízes, em todas as respostas dadas e julgadas pelos dois lados.
    pares = [(bool(c["juizes_ok"]), v(c) == "certa", c) for c in chave if c["responde"] and c["juizes_ok"] is not None and v(c) in {"certa", "reservas", "errada"}]
    brando = [(j, v(c) in {"certa", "reservas"}) for j, _, c in pares]
    tabela = Counter(("juizes_certa" if j else "juizes_nao") + "/" + ("jurista_certa" if k else "jurista_nao") for j, k, _ in pares)
    res["concordancia_juizes"] = {"n": len(pares), "tabela": dict(tabela), "kappa_estrito": kappa([(j, k) for j, k, _ in pares]),
                                  "kappa_com_reservas": kappa(brando),
                                  "juizes_certa_jurista_errada": sum(1 for j, _, c in pares if j and v(c) == "errada")}
    # Cansaço: concordância no primeiro e no último terço da ordem de leitura.
    terco = max(1, len(chave) // 3)
    res["cansaco"] = {"concordancia_1o_terco": round(sum(j == k for j, k, c in pares if c["n"] <= terco) / max(1, sum(1 for *_, c in pares if c["n"] <= terco)), 3),
                      "concordancia_ultimo_terco": round(sum(j == k for j, k, c in pares if c["n"] > len(chave) - terco) / max(1, sum(1 for *_, c in pares if c["n"] > len(chave) - terco)), 3),
                      "minutos": sum(float(folha[c["n"]].get("minutos") or 0) for c in chave if c["n"] in folha)}
    res["causas"] = dict(Counter(folha[c["n"]].get("causa") for c in chave if c["n"] in folha and folha[c["n"]].get("causa")))
    res["sem_base_nos_artigos"] = sum(1 for c in chave if folha.get(c["n"], {}).get("base_certa") in {"nao", "não"})
    # Segunda volta: as que discordam, agora com a referência.
    discordam = [c for j, k, c in pares if j != k]
    if segunda:
        res["segunda_volta"] = {"n": len(segunda), "referencia_errada": sum(1 for x in segunda.values() if x.get("referencia") == "errada"),
                                "referencia_incompleta": sum(1 for x in segunda.values() if x.get("referencia") == "incompleta"),
                                "jurista_muda_veredicto": sum(1 for x in segunda.values() if x.get("mantem") == "nao")}
    elif discordam and not problemas:
        blocos = []
        for c in discordam:
            blocos.append(f"<h2>N.º {c['n']}</h2><p>O seu veredicto: <strong>{_e(v(c))}</strong>.</p>"
                          f"<h3>Resposta de referência do conjunto de avaliação</h3><div class=\"caixa\">{_e(c['referencia'])}</div>"
                          f"<p class=\"suave\">Fonte da referência: {_e(c.get('fonte') and json.dumps(c['fonte'], ensure_ascii=False))}</p>")
        cab = ("<p>Nestas respostas o seu veredicto e o dos avaliadores automáticos não coincidem. Volte a ver cada uma no "
               "<code>pacote.html</code> (mesmo número) e diga, na <code>segunda-volta.csv</code>, se a resposta de referência está "
               "<strong>certa</strong>, <strong>incompleta</strong> ou <strong>errada</strong>, e se mantém o seu veredicto (<strong>sim</strong>/<strong>nao</strong>).</p>")
        (pasta / "segunda-volta.html").write_text(_html("Segunda volta", cab, blocos), encoding="utf-8")
        with (pasta / "segunda-volta.csv").open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["n", "referencia", "mantem", "nota"])
            for c in discordam:
                w.writerow([c["n"], "", "", ""])
        res["segunda_volta"] = {"por_fazer": len(discordam)}
    return res


def _importar_consolidacoes(pasta: Path, meta: dict, chave: list[dict]) -> dict:
    folha = _ler_folha(pasta / "folha.csv")
    problemas = _validar(folha, chave, {"veredicto": VEREDICTOS_CONSOLIDACAO, "erro": ERROS_CONSOLIDACAO, "gravidade": GRAVIDADES})
    for c in chave:
        x = folha.get(c["n"], {})
        if x.get("veredicto") == "errado" and not (x.get("erro") and x.get("gravidade")):
            problemas.append(f"n.º {c['n']}: errado sem erro ou sem gravidade")

    def medida(cs: list[dict]) -> dict:
        julg = [c for c in cs if folha.get(c["n"], {}).get("veredicto") in {"certo", "errado"}]
        erros = [c for c in julg if folha[c["n"]]["veredicto"] == "errado"]
        graves = [c for c in erros if folha[c["n"]].get("gravidade") == "grave"]
        m = {"julgados": len(julg), "duvidas": sum(1 for c in cs if folha.get(c["n"], {}).get("veredicto") == "duvida"),
             "erros": _taxa(len(erros), len(julg)), "graves": _taxa(len(graves), len(julg)),
             "por_erro": dict(Counter(folha[c["n"]].get("erro") for c in erros))}
        if julg and not erros:
            m["regra_de_tres"] = round(3 / len(julg), 3)
        return m

    caminhos = list(dict.fromkeys(c["caminho"] for c in chave if c["caminho"] != "visado"))
    alterados = [c for c in chave if c["caminho"] != "visado"]
    return {"problemas_na_folha": problemas, "por_caminho": {k: medida([c for c in chave if c["caminho"] == k]) for k in caminhos},
            "artigos_alterados": medida(alterados), "visados_sem_nota": medida([c for c in chave if c["caminho"] == "visado"]),
            "nota": "por quotas de caminho: o total dos alterados não é proporcional à população; citar por caminho. "
                    "Nos visados sem nota, 'errado' quer dizer que a instrução foi esquecida."}


def importar(args: argparse.Namespace) -> None:
    pasta = RAIZ / "avaliacao" / "privado" / "juristas" / args.nome
    linhas = _ler(pasta / "chave.jsonl")
    meta, chave = linhas[0]["meta"], linhas[1:]
    res = _importar_respostas(pasta, meta, chave) if meta["amostra"] == "respostas" else _importar_consolidacoes(pasta, meta, chave)
    res = {"nome": args.nome, "amostra": meta} | res
    RESUMOS.mkdir(parents=True, exist_ok=True)
    (RESUMOS / f"{args.nome}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for p in res["problemas_na_folha"][:30]:
        print("folha:", p)
    print(json.dumps({k: v for k, v in res.items() if k not in ("amostra", "problemas_na_folha")}, ensure_ascii=False, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="comando", required=True)
    r = sub.add_parser("respostas")
    r.add_argument("--semente", type=int, default=20261114)
    r.add_argument("--nome", default="respostas-1")
    r.add_argument("--privado-de", help="checkout com rag/resultados/privado e avaliacao/privado (numa worktree, o principal)")
    c = sub.add_parser("consolidacoes")
    c.add_argument("--semente", type=int, default=20261114)
    c.add_argument("--nome", default="consolidacoes-1")
    i = sub.add_parser("importar")
    i.add_argument("--nome", required=True)
    args = ap.parse_args()
    {"respostas": respostas, "consolidacoes": consolidacoes, "importar": importar}[args.comando](args)


if __name__ == "__main__":
    main()
