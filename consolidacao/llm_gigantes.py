"""Os diplomas grandes demais para o pedido corrido ou completo: passagens por unidades.

Dezoito diplomas ficaram por pedir (`README.md`, "O que falha e porquê", ponto 3): o pedido
inteiro (o original mais todos os alteradores) passa dos ~300 mil caracteres que um subagente lê
bem, ou o próprio texto do original passa disso. Aqui, para cada um:

- o original divide-se em **unidades** (os parágrafos, como em `llm_corrido.py`), também quando
  tem artigos: uma alteração a um número de um artigo de 2 000 linhas é uma troca de uma unidade, e
  a resposta não tem de reescrever o artigo inteiro;
- os alteradores partem-se em **grupos**, por ordem de aplicação (como `llm_completo.passagem`),
  e cada grupo vai num pedido à parte sobre o texto que as passagens anteriores deixaram. As
  unidades de cada pedido são as do texto atual dessa passagem;
- quando o texto atual não cabe no pedido, vai num ficheiro à parte (`texto-K.md`, com `{{N}}`
  antes de cada unidade) e o pedido leva só um índice dos títulos (artigos, capítulos, anexos):
  o subagente procura no ficheiro só as unidades que as instruções visam;
- uma resposta pode mandar **copiar** um intervalo de parágrafos de um alterador
  (`"copiar": {"alterador": n, "primeiro": "…", "ultimo": "…"}`) em vez de os escrever: é assim
  que entra uma republicação inteira (DL 55-A/2000) ou um anexo aditado longo. A cópia é feita
  pelo programa, letra a letra.

Cada passagem passa a verificação letra a letra de `llm_corrido` (cada parágrafo novo vem de um
alterador, do original ou do texto atual). No fim, as passagens fundem-se numa resposta só sobre as
unidades do **original**, com o alterador de cada troca, e grava-se em `llm/corrido/<id>.json`;
`juntar` escreve o consolidado com `llm_corrido._junto` e atualiza `llm/juntados-corrido.jsonl`,
que `cegas.py` e `acervo.py` já leem. As respostas e o estado de cada diploma ficam em
`llm/gigantes/<id>/`; os pedidos e os textos intermédios numa pasta de trabalho, porque se refazem.

**Verificação às cegas por passagem.** Uma vista com todos os alteradores não cabe num verificador
(o DL 44278 tem 206). `vistas` escreve uma vista por passagem: os alteradores dessa passagem, o
texto antes dela (no ficheiro `antes-K.md` quando é grande) e os trechos que mudam entre o texto
antes e depois (comparados por `difflib`, sem nada da resposta). `saida` junta os veredictos das
passagens na linha do diploma, em `saida-piloto-N-lote-01.jsonl`, ao lado da entrada que `entrada`
escreve com `cegas.linha_de`. Passagens certas em sequência dão um consolidado certo.

Uso:
    python consolidacao/llm_gigantes.py passagem IDS TRABALHO [--max-chars 230000] [--inline 90000]
    python consolidacao/llm_gigantes.py juntar IDS
    python consolidacao/llm_gigantes.py entrada RONDA IDS
    python consolidacao/llm_gigantes.py vistas RONDA IDS TRABALHO
    python consolidacao/llm_gigantes.py saida RONDA TRABALHO
"""

from __future__ import annotations

import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

import llm_corrido as lc
from cegas import VERIFICACAO, linha_de
from llm import _alteradores as _alteradores_da_selecao
from llm_completo import _alteradores
from texto import RAIZ, dividir, front_matter, padrao_diploma, publicado, sem_ligacoes
from verificar import _plano


PASTA = RAIZ / "consolidacao"
GIGANTES = PASTA / "llm" / "gigantes"
LIMITE_COMPLETO = 100_000  # até aqui, o alterador vai inteiro; acima, só os artigos que mencionam o original

REGRAS_EXTRA = """
## Passagens e texto grande

- Este pedido pode ser uma PASSAGEM: traz só um grupo dos alteradores, e o texto atual já tem
  aplicados os anteriores. As unidades `{{N}}` são as do texto atual DESTA passagem; "de", "ate"
  e "depois_de" referem-se a elas. "alterador" é o número com que o alterador vem neste pedido.
- Quando o texto atual não cabe no pedido, está no ficheiro `texto-K.md` da mesma pasta, com
  `{{N}}` antes de cada unidade, e o pedido traz só um índice dos títulos. Lê primeiro os
  alteradores; depois, para cada instrução, procura no ficheiro (Grep pelo artigo, pelo número ou
  por uma frase) e lê (Read com offset) as unidades em causa. Antes de responder, confirma o texto
  e o número de cada unidade que substituis. Só podes ler o pedido e esse ficheiro.
- Copiar do alterador: quando o texto novo é uma sequência de parágrafos seguidos do alterador,
  copiados como estão (uma republicação "com a redação atual", um anexo aditado, um artigo longo),
  em vez de "texto" podes dar "copiar": {"alterador": n, "primeiro": "<os primeiros 60 ou mais
  caracteres do primeiro parágrafo, exatamente>", "ultimo": "<os primeiros 60 ou mais caracteres
  do último parágrafo, exatamente>"}. O programa copia letra a letra todos os parágrafos do
  alterador do primeiro ao último, inclusive, e tira o « do início e o » do fim. Usa-o sempre que o
  texto a copiar passar de uns 30 parágrafos. Uma republicação do original (ou de um anexo dele)
  com a redação atual substitui o intervalo correspondente do texto atual inteiro.
- Escreve a resposta (um objeto JSON, não uma lista) no ficheiro indicado na tarefa. Se for
  longa demais para uma escrita, escreve-a em partes `resposta-K.parte1.json`, `…parte2.json`,
  cada uma um objeto com o mesmo "id" e parte das listas.
"""

_INDICE = re.compile(r"^(?:#{1,6}\s|Artigo\s+\d|ARTIGO\s+\d|Art\.\s*\d|Art\.º\s*\d|CAPÍTULO|Capítulo\s|SECÇÃO|Secção\s|SUBSECÇÃO|TÍTULO|Título\s|LIVRO|PARTE\s|ANEXO|Anexo\b|APÊNDICE|BASE\s|Base\s+[IVXLC\d]|MAPA|QUADRO)")


# "Art. 20.º - (Revogado.)": o `verificar._REVOGADO` não aceita o "Art." com espaço antes do número
_REVOGADO_ARTIGO = re.compile(r"^(?:§\s*(?:\d+\.?\s*[º°]|único)\.?\s*[-–—]?\s*|Art(?:igo)?\.?\s*\d+\.?\s*[º°]?(?:-[A-Z]{1,2})?\.?\s*[-–—]?\s*)\(Revogad[oa]\.\)$")


def _sem_revogados(problemas: list[str]) -> list[str]:
    return [x for x in problemas if not _REVOGADO_ARTIGO.match(x.rsplit("nem no original: ", 1)[-1].strip())]


def _carregar() -> dict[str, dict]:
    return lc._carregar("selecao-escala.jsonl")


def _nomes(texto: str, registo: dict | None = None) -> list[str]:
    """O nome do que o diploma aprova ("Código do Imposto Profissional"), para encontrar os
    artigos de um alterador grande que o alteram pelo nome e não pelo número do decreto. Vem do
    texto ("É aprovado o …") ou do sumário do registo ("Aprova o …")."""
    nomes = []
    if registo is not None:
        sumario = str(front_matter((RAIZ / registo["path"]).read_text(encoding="utf-8")).get("summary") or "")
        m = re.match(r"^Aprova (?:o|a|os|as) ((?:Código|Estatuto|Regulamento|Regime)[^,.;:]{3,100})", sumario)
        if m:
            nomes.append(re.sub(r"\s+", " ", m.group(1)).strip())
    for m in re.finditer(r"(?:É|São) aprovad[oa]s?,?\s+(?:pelo presente [^,]+,\s*)?(?:o|a|os|as)\s+(?:novo texto d[oa]\s+)?((?:Código|Estatuto|Regulamento|Regime)[^,.;:\n]{3,100}?)(?=,|\.|;| que | anexo| publicad)", texto[:20000]):
        nome = re.sub(r"\s+", " ", m.group(1)).strip()
        if nome not in nomes:
            nomes.append(nome)
    return nomes


def texto_alterador(a: dict, registo: dict, nomes: list[str]) -> tuple[str, bool]:
    """O texto do alterador para o pedido e a vista: inteiro até `LIMITE_COMPLETO`; acima, os
    artigos que mencionam o original pelo título ou pelo nome do que ele aprova."""
    texto = publicado(RAIZ / a["path"])
    if len(texto) <= LIMITE_COMPLETO:
        return texto, True
    padrao = padrao_diploma(registo["title"])
    nomes_re = [re.compile(re.escape(n).replace(r"\ ", r"\s+"), re.I) for n in nomes]
    artigos = [x for x in dividir(texto).artigos
               if (padrao and padrao.search(sem_ligacoes("\n".join(x.linhas)))) or any(n.search("\n".join(x.linhas)) for n in nomes_re)]
    # sem nenhum artigo que o mencione, não vai nada (como em `cegas._texto_alterador`)
    return "\n\n".join("\n".join(x.linhas).strip() for x in artigos), False


# --- O estado: as unidades do texto atual ----------------------------------------------------


def _estado_inicial(registo: dict) -> list[dict]:
    return [{"t": u.strip(), "orig": n, "alt": []} for n, u in enumerate(lc.unidades(lc._registo_base(registo)), 1)]


def _texto(estado: list[dict]) -> str:
    return "\n\n".join(u["t"] for u in estado)


def _paragrafos(texto: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n{2,}", texto or "") if p.strip()]


def _copiar(c: dict, alteradores: dict[int, dict]) -> tuple[str | None, str | None]:
    """O texto de um "copiar" ou o erro."""
    a = alteradores.get(int(c.get("alterador") or 0)) if str(c.get("alterador") or "").isdigit() else None
    if a is None:
        return None, f"copiar: alterador {c.get('alterador')} não existe"
    ps = _paragrafos(publicado(RAIZ / a["path"]))
    norm = lambda s: re.sub(r"\s+", " ", s.lstrip("«").strip())
    primeiro, ultimo = norm(c.get("primeiro") or ""), norm(c.get("ultimo") or "")
    def bate(p: str, inicio: str) -> bool:
        # um início curto ("CAPÍTULO I") só conta como o parágrafo inteiro
        return norm(p) == inicio if len(inicio) < 20 else norm(p).startswith(inicio)

    if not primeiro or not ultimo:
        return None, "copiar: faltam primeiro e ultimo"
    candidatos = [k for k, p in enumerate(ps) if bate(p, primeiro)]
    if not candidatos:
        return None, f"copiar: primeiro parágrafo não está no alterador: {primeiro[:60]}"
    if len(primeiro) < 20 and len(candidatos) > 1:
        return None, f"copiar: primeiro parágrafo curto e repetido no alterador: {primeiro[:60]}"
    i = candidatos[0]
    j = next((k for k in range(i, len(ps)) if bate(ps[k], ultimo)), None)
    if j is None:
        return None, f"copiar: último parágrafo não está no alterador depois do primeiro: {ultimo[:60]}"
    copia = ps[i : j + 1]
    copia[0] = copia[0].lstrip("«").lstrip()
    copia[-1] = re.sub(r"»\s*([.;,]?)\s*$", "", copia[-1]).rstrip() if copia[-1].rstrip().endswith(("»", "».", "»;", "»,")) else copia[-1]
    return "\n\n".join(copia), None


def _expandir(resposta: dict, alteradores: dict[int, dict]) -> list[str]:
    problemas = []
    for s in (resposta.get("substituicoes") or []) + (resposta.get("insercoes") or []):
        if s.get("copiar"):
            texto, erro = _copiar(s["copiar"], alteradores)
            if erro:
                problemas.append(erro)
                s["texto"] = ""
            else:
                s["texto"] = texto
                s.setdefault("alterador", s["copiar"].get("alterador"))
                s["copiado"] = True
    return problemas


_TITULO_ARTIGO = re.compile(r"^#{6} Artigo (\S+)(?: — (.*))?$")
GRANDE = 60_000  # acima disto (uma unidade enorme, sem linhas em branco), compara-se linha a linha


def _linhas(texto: str) -> list[str]:
    """As linhas não vazias; uma linha muito longa (um anexo inteiro numa linha só) parte-se nas frases."""
    saida = []
    for l in texto.split("\n"):
        if not l.strip():
            continue
        saida += [f for f in re.split(r"(?<=[.;:])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9«(])", l) if f.strip()] if len(l) > 2000 else [l]
    return saida


def _coberto(fragmento: list[str], tokens: list[str], minimo: int = 4) -> bool:
    """O fragmento é uma sequência de pedaços com `minimo` ou mais palavras seguidas, cada um numa
    fonte (texto novo que junta o fim de um artigo e o título do seguinte, que no alterador estão em
    sítios diferentes). Um pedaço mais curto (uma palavra ou um número trocado) não conta."""
    i = 0
    while i < len(fragmento):
        n = 0
        while i + n < len(fragmento) and any(" ".join(fragmento[i : i + n + 1]) in f for f in tokens):
            n += 1
        if n < minimo and i + n < len(fragmento):
            return False
        if n == 0:
            return False
        i += n
    return True


def verificar_mudanca(s: dict, antigo: list[str], fontes: list[str], tokens: list[str]) -> list[str]:
    """`llm_corrido.verificar_texto`; numa troca enorme (uma unidade de 373 mil caracteres no DL
    202/2000), só as linhas que mudam, cada bloco contra as linhas que substitui."""
    paragrafos = _paragrafos(s.get("texto") or "")
    problemas = []
    # um título "###### Artigo 24.º-A — Epígrafe" posto no formato do original: o número e a
    # epígrafe têm de vir de uma fonte (no alterador estão em linhas separadas)
    for p in [p for p in paragrafos if _TITULO_ARTIGO.match(p)]:
        m = _TITULO_ARTIGO.match(p)
        partes = [f"Artigo {m.group(1)}"] + ([m.group(2)] if m.group(2) else [])
        if not all(any(_plano(x) in f for f in fontes) for x in partes):
            problemas.append(f"título que não está no alterador nem no original: {p[:80]}")
    paragrafos = [p for p in paragrafos if not _TITULO_ARTIGO.match(p)]
    velho, novo = "\n\n".join(antigo), "\n\n".join(paragrafos)
    if len(velho) + len(novo) <= GRANDE:
        por_paragrafo = lc.verificar_texto({"texto": novo}, antigo, fontes, tokens)
        # um parágrafo trocado por um só parágrafo em que a nova redação junta o texto atual e um
        # trecho do alterador ("é aditado o seguinte período", um "leia-se" que só cobre o princípio
        # da frase, numa ata de retificação): palavra a palavra, como numa troca enorme
        if por_paragrafo and len(antigo) == 1 and len(paragrafos) == 1 and not _por_palavras(velho, novo, tokens):
            return problemas
        return problemas + por_paragrafo
    return problemas + _por_palavras(velho, novo, tokens)


def _por_palavras(velho: str, novo: str, tokens: list[str]) -> list[str]:
    """Palavra a palavra: cada sequência nova tem de estar seguida numa fonte, ou ser feita de
    pedaços de 4 ou mais palavras seguidas, cada um numa fonte."""
    problemas = []
    a, b = lc._tokens(velho), lc._tokens(novo)
    for tipo, _i1, _i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tipo not in ("replace", "insert"):
            continue
        fragmento = " ".join(b[j1:j2])
        # o alinhamento pode pôr na troca um sinal de pontuação da fronteira ("." do fim da frase anterior)
        variantes = [b[j1:j2], b[j1 + 1 : j2], b[j1 : j2 - 1], b[j1 + 1 : j2 - 1]]
        if not any(v and any(" ".join(v) in f for f in tokens) for v in variantes) and not _coberto(b[j1:j2], tokens):
            problemas.append(f"troca que não está no alterador nem no original: «{fragmento[:80]}»")
    return problemas


def _numeros(m: dict, validos: set[int]) -> list[int]:
    return sorted({int(x) for x in re.findall(r"\d+", str(m.get("alterador") or ""))} & validos)


def aplicar(resposta: dict, estado: list[dict], validos: set[int]) -> list[dict]:
    """O estado depois da resposta (posições já validadas). As unidades novas levam o alterador;
    as do original que saem guardam-no em `saiu` na unidade seguinte que fica (para a fusão)."""
    subst = {s["de"]: s for s in resposta.get("substituicoes") or []}
    ins: dict[int, list[dict]] = {}
    for s in resposta.get("insercoes") or []:
        ins.setdefault(s["depois_de"], []).append(s)
    novo: list[dict] = []
    removidos: list[int] = []  # alteradores das unidades que saíram desde a última que ficou
    k, n = 1, len(estado)
    while k <= n:
        if k in subst:
            s = subst[k]
            alt = _numeros(s, validos)
            textos = _paragrafos(s.get("texto") or "")
            antigos = [u["t"] for u in estado[k - 1 : s["ate"]]]
            if textos == antigos:  # troca por texto igual: nada muda
                novo += estado[k - 1 : s["ate"]]
            else:
                for u in estado[k - 1 : s["ate"]]:
                    removidos += alt + u.get("saiu", [])
                for t in textos:
                    novo.append({"t": t, "orig": None, "alt": alt})
            k = s["ate"]
        else:
            u = dict(estado[k - 1])
            if removidos:
                u["saiu"] = sorted(set(u.get("saiu", []) + removidos))
                removidos = []
            novo.append(u)
        for s in ins.get(k, []):
            alt = _numeros(s, validos)
            novo += [{"t": t, "orig": None, "alt": alt} for t in _paragrafos(s.get("texto") or "")]
        k += 1
    if removidos and novo:
        novo[-1] = dict(novo[-1]) | {"saiu_fim": sorted(set(novo[-1].get("saiu_fim", []) + removidos))}
    return novo


def fundir(estado: list[dict], original: list[str]) -> tuple[list[dict], list[dict]]:
    """As trocas do original ao estado final, sobre as unidades do original: (substituições,
    inserções), cada uma com os alteradores que lhe deram o texto ou a apagaram."""
    substituicoes, insercoes = [], []
    n = len(original)
    ancoras = [(i, u) for i, u in enumerate(estado) if u["orig"] is not None]
    marcos = [(-1, {"orig": 0})] + ancoras + [(len(estado), {"orig": n + 1})]
    for (i0, a), (i1, b) in zip(marcos, marcos[1:], strict=False):
        novos = estado[i0 + 1 : i1]
        de, ate = a["orig"] + 1, b["orig"] - 1
        alt = sorted({x for u in novos for x in u["alt"] + u.get("saiu", [])} | set(b.get("saiu", [])) | (set(a.get("saiu_fim", [])) if i1 == len(estado) else set()))
        texto = "\n\n".join(u["t"] for u in novos)
        if de <= ate:
            substituicoes.append({"de": de, "ate": ate, "texto": texto, "alterador": alt})
        elif novos:
            if a["orig"] >= 1:
                insercoes.append({"depois_de": a["orig"], "texto": texto, "alterador": alt})
            else:  # antes da primeira unidade: entra na troca da primeira
                substituicoes.append({"de": 1, "ate": 1, "texto": texto + "\n\n" + original[0].strip(), "alterador": alt})
    return substituicoes, insercoes


# --- Passagens ---------------------------------------------------------------------------------


AVISO = """**Passagem {k}: alteradores {a} a {b} de {n}.** {antes}Este pedido traz só os alteradores {a} a {b};
os seguintes ({depois}) vêm numa passagem posterior e não interessam agora. Lê todas as instruções
DESTES alteradores dirigidas ao original e devolve o que muda no texto atual. No campo "alterador"
usa o número com que o alterador vem aqui ({a} a {b})."""


def _ler(pasta_i: Path, k: int) -> dict | None:
    ficheiros = sorted(pasta_i.glob(f"resposta-{k}.json")) + sorted(pasta_i.glob(f"resposta-{k}.parte*.json"))
    if not ficheiros:
        return None
    junta: dict = {"id": None, "substituicoes": [], "insercoes": [], "nao_aplicavel": None, "instrucoes": []}
    for f in ficheiros:
        d = json.loads(f.read_text(encoding="utf-8"))
        for o in d if isinstance(d, list) else [d]:
            junta["id"] = junta["id"] or o.get("id")
            junta["substituicoes"] += o.get("substituicoes") or []
            junta["insercoes"] += o.get("insercoes") or []
            junta["instrucoes"] += o.get("instrucoes") or []
            if o.get("nao_aplicavel"):
                junta["nao_aplicavel"] = (junta["nao_aplicavel"] + " | " if junta["nao_aplicavel"] else "") + str(o["nao_aplicavel"])
    return junta


ALTERADOR_EM_FICHEIRO = 150_000  # um alterador maior do que isto vai num ficheiro à parte, com índice


def _indice_texto(texto: str) -> list[str]:
    return [f"linha {n}: {l.strip()[:90]}" for n, l in enumerate(texto.split("\n"), 1) if l.strip() and len(l) <= 200 and _INDICE.match(l.strip())]


def _indice(estado: list[dict]) -> list[str]:
    return [f"{{{{{n}}}}} {u['t'].splitlines()[0][:90]}" for n, u in enumerate(estado, 1) if len(u["t"]) <= 200 and _INDICE.match(u["t"])]


def _fontes(registo: dict) -> tuple[list[str], list[str]]:
    fontes = [_plano(publicado(RAIZ / a["path"])) for a in _alteradores_da_selecao(registo) if a.get("path")]
    fontes.append(_plano(lc._registo_base(registo)))
    return fontes, [" ".join(lc._tokens(f)) for f in fontes]


def reconstruir(registo: dict, pasta_i: Path) -> tuple[list[dict], list[dict], list[str], list[dict], int | None]:
    """Aplica as respostas que há. Devolve (estados por passagem, começando no original,
    respostas, problemas, passagens do estado.json, a primeira passagem sem resposta)."""
    estado_f = json.loads((pasta_i / "estado.json").read_text(encoding="utf-8")) if (pasta_i / "estado.json").exists() else {"passagens": []}
    alteradores = dict(enumerate(_alteradores(registo), 1))
    validos = set(alteradores)
    fontes, tokens = _fontes(registo)
    estados = [_estado_inicial(registo)]
    respostas, problemas, falta = [], [], None
    for p in estado_f["passagens"]:
        resposta = _ler(pasta_i, p["n"])
        if resposta is None:
            falta = p["n"]
            break
        atual = estados[-1]
        probs = _expandir(resposta, alteradores)
        probs += lc._validar(resposta, len(atual))
        if not probs:
            atual_plano = _plano(_texto(atual))
            f2, t2 = fontes + [atual_plano], tokens + [" ".join(lc._tokens(atual_plano))]
            for s in resposta["substituicoes"]:
                if not s.get("copiado"):
                    probs += [f"substituição {s['de']}-{s['ate']}: {x}" for x in verificar_mudanca(s, [u["t"] for u in atual[s["de"] - 1 : s["ate"]]], f2, t2)]
            for s in resposta["insercoes"]:
                if not s.get("copiado"):
                    probs += [f"inserção depois de {s['depois_de']}: {x}" for x in verificar_mudanca(s, [], f2, t2)]
            for s in resposta["substituicoes"] + resposta["insercoes"]:
                fora = [n for n in _numeros(s, set(range(1, 10_000))) if n not in p["alteradores"]]
                if fora or not _numeros(s, validos):
                    probs.append(f"mudança com alterador {s.get('alterador')} fora desta passagem ({p['alteradores'][0]} a {p['alteradores'][-1]})")
        problemas += [f"passagem {p['n']}: {x}" for x in _sem_revogados(probs)]
        estados.append(atual if probs and any("posições" in x or "sobrepõem" in x or "inserção a meio" in x for x in probs) else aplicar(resposta, atual, validos))
        respostas.append(resposta)
    return estados, respostas, problemas, estado_f["passagens"], falta


def _verificar_fundida(final: dict, registo: dict, original: list[str]) -> list[str]:
    """`llm_corrido.verificar_resposta` sobre a resposta fundida, com `verificar_mudanca`."""
    fontes, tokens = _fontes(registo)
    problemas = []
    for s in final["substituicoes"]:
        problemas += [f"substituição {s['de']}-{s['ate']}: {x}" for x in verificar_mudanca(s, original[s["de"] - 1 : s["ate"]], fontes, tokens)]
    for s in final["insercoes"]:
        problemas += [f"inserção depois de {s['depois_de']}: {x}" for x in verificar_mudanca(s, [], fontes, tokens)]
    return problemas


def passagem(ids: list[str], trabalho: Path, max_chars: int, inline: int) -> None:
    selecao = _carregar()
    trabalho.mkdir(parents=True, exist_ok=True)
    (trabalho / "REGRAS.md").write_text(lc.SISTEMA + lc.FORMATO + REGRAS_EXTRA, encoding="utf-8")
    for i in ids:
        registo = selecao[i]
        pasta_i = GIGANTES / i.replace(":", "_")
        trab_i = trabalho / i.replace(":", "_")
        pasta_i.mkdir(parents=True, exist_ok=True)
        trab_i.mkdir(parents=True, exist_ok=True)
        ficheiro_estado = pasta_i / "estado.json"
        estado_f = json.loads(ficheiro_estado.read_text(encoding="utf-8")) if ficheiro_estado.exists() else {"id": i, "passagens": []}
        if estado_f.get("feito"):
            print(f"{i} {registo['title']}: feito")
            continue
        estados, respostas, problemas, passagens, falta = reconstruir(registo, pasta_i)
        if falta is not None:
            print(f"{i} {registo['title']}: à espera de {pasta_i}/resposta-{falta}.json (pedido em {trab_i}/pedido-{falta}.md)")
            continue
        alteradores = _alteradores(registo)
        nomes = _nomes(lc._registo_base(registo), registo)
        feitos = {n for p in passagens for n in p["alteradores"]}
        textos_a = {n: texto_alterador(a, registo, nomes) for n, a in enumerate(alteradores, 1) if n not in feitos}
        tamanho_a = {n: (len(t) if len(t) <= ALTERADOR_EM_FICHEIRO else sum(len(x) + 12 for x in _indice_texto(t))) + 200 for n, (t, _) in textos_a.items()}
        restantes = [(n, a, tamanho_a[n]) for n, a in enumerate(alteradores, 1) if n not in feitos]
        atual = estados[-1]
        if not restantes:
            original = lc.unidades(lc._registo_base(registo))
            subst, ins = fundir(atual, original)
            final = {"id": i, "substituicoes": subst, "insercoes": ins,
                     "nao_aplicavel": " | ".join(f"passagem {k}: {r['nao_aplicavel']}" for k, r in enumerate(respostas, 1) if r.get("nao_aplicavel")) or None,
                     "instrucoes": [x for r in respostas for x in r.get("instrucoes") or []],
                     "modelo": "claude-opus-5-5", "pedido": "corrido", "passagens": passagens}
            # A verificação letra a letra que conta é a de cada passagem: cada parágrafo novo vem de um
            # alterador, do original ou do texto que as passagens anteriores deixaram (já verificado).
            # Sobre a resposta fundida, um parágrafo mudado por dois alteradores já não se parece com
            # o original: o resultado fica em "avisos", para leitura, e não recusa o diploma.
            final["problemas"] = problemas + lc._validar(final, len(original))
            final["avisos"] = _sem_revogados(_verificar_fundida(final, registo, original))
            lc.CORRIDO.mkdir(parents=True, exist_ok=True)
            (lc.CORRIDO / (i.replace(":", "_") + ".json")).write_text(json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            estado_f["feito"] = True
            ficheiro_estado.write_text(json.dumps(estado_f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            tipo = "com problemas" if final["problemas"] else "sem alterações" if not subst and not ins else "sem problemas"
            print(f"{i} {registo['title']}: feito em {len(passagens)} passagens, {len(subst)} substituições e {len(ins)} inserções, {tipo}")
            for x in final["problemas"][:10]:
                print("     ", x[:200])
            for x in final["avisos"][:5]:
                print("      aviso:", x[:200])
            continue
        texto_atual = _texto(atual)
        em_ficheiro = len(texto_atual) > inline
        indice = _indice(atual) if em_ficheiro else []
        base = (sum(len(x) + 1 for x in indice) if em_ficheiro else len(texto_atual) + 8 * len(atual)) + 4000
        grupo, total = [], base
        for n, a, tamanho in restantes:
            if grupo and total + tamanho > max_chars:
                break
            grupo.append((n, a))
            total += tamanho
        k = len(passagens) + 1
        a0, b0 = grupo[0][0], grupo[-1][0]
        antes = f"Os alteradores 1 a {a0 - 1} já foram aplicados ao texto atual. " if a0 > 1 else ""
        aviso = "" if (k == 1 and b0 == len(alteradores)) else AVISO.format(
            k=k, a=a0, b=b0, n=len(alteradores), antes=antes, depois=f"{b0 + 1} a {len(alteradores)}" if b0 < len(alteradores) else "nenhum")
        partes = [f"# Diploma original: {registo['title']}", ""]
        if aviso:
            partes += [aviso, ""]
        if em_ficheiro:
            numerado = "\n\n".join(f"{{{{{n}}}}}\n{u['t']}" for n, u in enumerate(atual, 1))
            (trab_i / f"texto-{k}.md").write_text(numerado + "\n", encoding="utf-8")
            partes += ["## Texto atual do original: no ficheiro", "",
                       f"O texto atual tem {len(atual)} unidades e {len(texto_atual)} caracteres. Está em `{trab_i}/texto-{k}.md`, com `{{{{N}}}}` "
                       "numa linha antes de cada unidade. Procura lá (Grep, Read com offset) as unidades que as instruções visam.", "",
                       "### Índice dos títulos (unidade e primeira linha)", *indice, ""]
        else:
            partes.append("## Texto atual do original, por unidades")
            for n, u in enumerate(atual, 1):
                partes += [f"{{{{{n}}}}}", u["t"], ""]
        partes.append("## Diplomas que alteram o original, por ordem de aplicação")
        for n, a in grupo:
            texto, completo = textos_a[n]
            aviso_a = "" if completo else " (só os artigos que mencionam o original ou o que ele aprova)"
            if len(texto) > ALTERADOR_EM_FICHEIRO:
                ficheiro_a = trab_i / f"alterador-{k}-{n}.md"
                ficheiro_a.write_text(texto, encoding="utf-8")
                partes += [f"### Alterador {n}: {a.get('title') or a['id']}{aviso_a}: no ficheiro", "",
                           f"Tem {len(texto)} caracteres e está em `{ficheiro_a}`. Lê-o por partes (Read com offset) e por inteiro "
                           "antes de responder: as instruções podem estar em qualquer sítio. Índice dos títulos (linha do ficheiro e texto):",
                           *_indice_texto(texto), ""]
            else:
                partes += [f"### Alterador {n}: {a.get('title') or a['id']}{aviso_a}", texto.strip(), ""]
        pedido = f"<<<DIPLOMA id={i}>>>\n" + "\n".join(partes) + f"\n<<<FIM DO DIPLOMA id={i}>>>\n"
        (trab_i / f"pedido-{k}.md").write_text(pedido, encoding="utf-8")
        passagens.append({"n": k, "alteradores": [n for n, _ in grupo], "chars": len(pedido), "texto_em_ficheiro": em_ficheiro})
        estado_f["passagens"] = passagens
        ficheiro_estado.write_text(json.dumps(estado_f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{i} {registo['title']}: passagem {k}, alteradores {a0} a {b0} de {len(alteradores)}, pedido {len(pedido)} caracteres"
              f"{' (texto em ficheiro, ' + str(len(texto_atual)) + ')' if em_ficheiro else ''}, {len(restantes) - len(grupo)} por pedir -> {trab_i}/pedido-{k}.md")


_NOTA_NO_FIM = re.compile(r"\n> (?:Alterado|Aditado|Revogado|Retificado) pelo/a [^\n]*, publicado em \d{4}-\d{2}-\d{2}\.\Z")


def juntar(ids: list[str]) -> None:
    """Junta as respostas fundidas destes diplomas e põe as linhas em `llm/juntados-corrido.jsonl`
    (as dos outros diplomas ficam como estão)."""
    selecao = _carregar()
    novas = {}
    for i in ids:
        f = lc.CORRIDO / (i.replace(":", "_") + ".json")
        if not f.exists():
            continue
        resposta = json.loads(f.read_text(encoding="utf-8"))
        base = {"id": i, "title": selecao[i]["title"], "estado": "não junto"}
        if resposta["problemas"]:
            novas[i] = base | {"motivo": "a resposta não passou a verificação letra a letra: " + "; ".join(resposta["problemas"])[:300]}
        elif not resposta["substituicoes"] and not resposta["insercoes"]:
            novas[i] = base | {"motivo": "a resposta não muda nada: " + str(resposta.get("nao_aplicavel"))[:300]}
        else:
            novas[i] = lc._junto(resposta, selecao[i]) | {"pedido": "corrido", "passagens": len(resposta.get("passagens") or [])}
            destino = RAIZ / novas[i]["consolidado"]
            texto = destino.read_text(encoding="utf-8")
            if _NOTA_NO_FIM.search(texto):
                # a última troca no fim do texto deixa a nota sem "\n" depois, e o `cegas.py` e o
                # `acervo.py` só a tiram com ele: a nota ficava no texto verificado às cegas
                destino.write_text(texto + "\n", encoding="utf-8")
        print(f"{selecao[i]['title']}: {novas[i]['estado']}" + (f" ({novas[i]['motivo'][:200]})" if "motivo" in novas[i] else ""))
    linhas = [json.loads(l) for l in lc.JUNTADOS.read_text(encoding="utf-8").splitlines()] if lc.JUNTADOS.exists() else []
    linhas = [novas.pop(l["id"]) if l["id"] in novas else l for l in linhas] + list(novas.values())
    lc.JUNTADOS.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas), encoding="utf-8")


# --- Verificação às cegas por passagem ---------------------------------------------------------


def entrada(ronda: int, ids: list[str]) -> Path:
    """A entrada da ronda (um lote) com `cegas.linha_de`, como as outras: é ela que o `acervo.py`
    compara com o consolidado. O texto dos alteradores grandes vai como no pedido."""
    selecao = _carregar()
    juntados = {l["id"]: l for l in map(json.loads, lc.JUNTADOS.read_text(encoding="utf-8").splitlines())}
    destino = VERIFICACAO / f"entrada-piloto-{ronda}-lote-01.jsonl"
    linhas = []
    for i in ids:
        j = juntados.get(i)
        if not j or j["estado"] != "aplicado com LLM":
            continue
        linha = linha_de(j, selecao[i])
        nomes = _nomes(lc._registo_base(selecao[i]), selecao[i])
        alts = [a for a in _alteradores(selecao[i]) if a["id"] in set(j["alteradores_vistos"])]
        textos = [{"titulo": a["title"], **dict(zip(("texto", "completo"), texto_alterador(a, selecao[i], nomes), strict=False))} for a in alts]
        linha |= {"alterador": " e ".join(t["titulo"] for t in textos), "alterador_completo": all(t["completo"] for t in textos),
                  "texto_alterador": "\n\n".join(f"# {t['titulo']}\n\n{t['texto']}" for t in textos), "alteradores": textos,
                  "passagens": len(j.get("passagens") and json.loads((GIGANTES / i.replace(':', '_') / 'estado.json').read_text())["passagens"] or [])}
        linhas.append(linha)
    destino.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas), encoding="utf-8")
    print(f"{len(linhas)} diplomas em {destino.relative_to(RAIZ)}")
    return destino


def _trechos(antes: str, depois: str) -> list[tuple[str, str | None, str, int, int]]:
    a, b = _paragrafos(antes), _paragrafos(depois)
    saida = []
    for tipo, i1, i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tipo == "equal":
            continue
        velho, novo = "\n\n".join(a[i1:i2]), "\n\n".join(b[j1:j2])
        if tipo == "replace" and min(len(velho), len(novo)) > GRANDE:
            # uma unidade enorme que muda em poucos sítios: os trechos são as linhas que mudam
            la, lb = _linhas(velho), _linhas(novo)
            for t2, k1, k2, m1, m2 in SequenceMatcher(None, la, lb, autojunk=False).get_opcodes():
                if t2 != "equal":
                    saida.append((f"Trecho {len(saida) + 1}", "\n".join(la[k1:k2]) or None, "\n".join(lb[m1:m2]), i1, i2))
            continue
        saida.append((f"Trecho {len(saida) + 1}", velho or None, novo, i1, i2))
    return saida


TRECHO_NA_VISTA = 20_000  # um trecho maior (uma republicação, um anexo revogado) vai num ficheiro à parte

VISTA_INSTRUCOES = """Verificação às cegas, por passagem. Este diploma é grande demais para uma vista só: as alterações
foram aplicadas em passagens, cada uma com um grupo de alteradores, por ordem. Esta vista é UMA passagem:
os diplomas que alteram DESTA passagem, o texto ANTES dela (o original com as passagens anteriores já
aplicadas) e os trechos que mudaram entre o texto antes e o texto depois. Verifica só esta passagem:
cada trecho (`certo`/`errado`/`dúvida`, como nas regras), e em `instrucoes_em_falta` as instruções destes
alteradores dirigidas ao original que não tiveram efeito. Instruções de alteradores de outras passagens
não são desta vista. O "texto antes" é o ponto de partida: não o verifiques."""


def vistas(ronda: int, ids: list[str], trabalho: Path, inline: int) -> None:
    selecao = _carregar()
    trabalho.mkdir(parents=True, exist_ok=True)
    entradas = {d["id"]: d for d in map(json.loads, (VERIFICACAO / f"entrada-piloto-{ronda}-lote-01.jsonl").read_text(encoding="utf-8").splitlines())}
    indice = []
    for i in ids:
        if i not in entradas:
            continue
        registo = selecao[i]
        pasta_i = GIGANTES / i.replace(":", "_")
        estados, _, _, passagens, falta = reconstruir(registo, pasta_i)
        assert falta is None, i
        alteradores = dict(enumerate(_alteradores(registo), 1))
        nomes = _nomes(lc._registo_base(registo), registo)
        # o texto antes da 1.ª passagem é o original letra a letra; o depois da última, o consolidado da entrada
        textos = [entradas[i]["texto_original"]] + [_texto(e) for e in estados[1:-1]] + [entradas[i]["texto_consolidado"]]
        for k, p in enumerate(passagens, 1):
            antes, depois = textos[k - 1], textos[k]
            trechos = _trechos(antes, depois)
            nome = f"{i.replace(':', '_')}-p{k}"
            linhas = [f"## DIPLOMA {i}", f"Original: {registo['title']}", f"Passagem {k} de {len(passagens)}: alteradores {p['alteradores'][0]} a {p['alteradores'][-1]} de {len(alteradores)}", "",
                      VISTA_INSTRUCOES, "", "### TEXTO DOS DIPLOMAS QUE ALTERAM, DESTA PASSAGEM"]
            for n in p["alteradores"]:
                texto, completo = texto_alterador(alteradores[n], registo, nomes)
                titulo = f"#### Alterador {n}: {alteradores[n]['title']}" + ("" if completo else " (só os artigos que mencionam o original ou o que ele aprova)")
                if len(texto) > ALTERADOR_EM_FICHEIRO:
                    f_alt = trabalho / f"alterador-{nome}-{n}.md"
                    f_alt.write_text(texto, encoding="utf-8")
                    linhas += [titulo + ": no ficheiro", f"Tem {len(texto)} caracteres e está em `{f_alt}`. Lê-o por inteiro, por partes (Read com offset). Índice:", *_indice_texto(texto), ""]
                else:
                    linhas += [titulo, texto.strip(), ""]
            if len(antes) > inline:
                (trabalho / f"antes-{nome}.md").write_text(antes, encoding="utf-8")
                linhas += [f"### TEXTO ANTES DESTA PASSAGEM: no ficheiro `{trabalho / f'antes-{nome}.md'}` ({len(antes)} caracteres). Procura lá (Grep, Read com offset) o que as instruções visam.", ""]
            else:
                linhas += ["### TEXTO ANTES DESTA PASSAGEM (inteiro; os trechos abaixo são os parágrafos que mudaram, o resto fica igual)", antes.strip(), ""]
            linhas.append(f"### TRECHOS QUE MUDAM NESTA PASSAGEM ({len(trechos)})")
            def curto(texto: str, rotulo: str, chave: str) -> str:
                """Um trecho longo vai num ficheiro; a vista leva o princípio e o fim."""
                if len(texto) <= TRECHO_NA_VISTA:
                    return texto
                f_t = trabalho / f"{rotulo}-{nome}-{chave.replace(' ', '')}.md"  # noqa: B023 (só nesta iteração)
                f_t.write_text(texto, encoding="utf-8")
                ps = _paragrafos(texto)
                if len(ps) < 7:
                    ps = _linhas(texto)
                return (f"(trecho longo: {len(ps)} parágrafos, {len(texto)} caracteres, inteiro em `{f_t}`; lê-o por inteiro. Princípio e fim:)\n\n"
                        + "\n\n".join(ps[:3]) + "\n\n[…]\n\n" + "\n\n".join(ps[-3:]))

            for chave, a, d, i1, i2 in trechos:
                linhas += [f"#### ARTIGO: {chave}", f"--- ANTES (parágrafos {i1 + 1} a {i2})" if a is not None else f"--- ANTES: (não existe: texto novo, depois do parágrafo {i1})"]
                if a is not None:
                    linhas.append(curto(a, "antes", chave))
                linhas += ["--- DEPOIS", curto(d, "depois", chave) if d else "(apagado)", ""]
            vista = "\n".join(linhas) + "\n"
            (trabalho / f"vista-{nome}.md").write_text(vista, encoding="utf-8")
            indice.append({"id": i, "passagem": k, "trechos": [t[0] for t in trechos], "chars": len(vista), "vista": str(trabalho / f"vista-{nome}.md"),
                           "resposta": str(trabalho / f"resposta-{nome}.json")})
    (trabalho / "pedacos.json").write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(indice)} vistas em {trabalho}: " + ", ".join(f"{x['id'].split(':')[2]}-p{x['passagem']} {x['chars'] // 1000}k/{len(x['trechos'])}t" for x in indice))


def saida(ronda: int, trabalho: Path) -> None:
    indice = json.loads((trabalho / "pedacos.json").read_text(encoding="utf-8"))
    por_id: dict[str, list] = {}
    for p in indice:
        r = Path(p["resposta"])
        resposta = None
        if r.exists():
            d = json.loads(r.read_text(encoding="utf-8"))
            resposta = (d[0] if isinstance(d, list) else d) if d else None
        por_id.setdefault(p["id"], []).append((p, resposta))
    linhas = []
    for i, passagens in por_id.items():
        em_falta, a_mais, artigos_falta, fora = [], [], [], []
        for p, r in passagens:
            k = p["passagem"]
            if r is None:
                fora.append(f"passagem {k}: dúvida: o verificador não respondeu")
                continue
            veredictos = {a["artigo"]: a for a in r.get("artigos", [])}
            for chave in p["trechos"]:
                a = veredictos.get(chave) or {"veredicto": "dúvida", "motivo": "o verificador não deu veredicto para este trecho", "texto_esperado": ""}
                linhas.append({"id": i, "artigo": f"Passagem {k}, {chave}", "veredicto": a["veredicto"], "motivo": a.get("motivo", ""), "texto_esperado": a.get("texto_esperado", "")})
            em_falta += [f"passagem {k}: {x}" for x in r.get("instrucoes_em_falta") or []]
            a_mais += [f"passagem {k}: {x}" for x in r.get("artigos_a_mais") or []]
            artigos_falta += [f"passagem {k}: {x}" for x in r.get("artigos_em_falta") or []]
            f = str(r.get("fora_dos_artigos") or "dúvida: o verificador não respondeu")
            if not f.lower().startswith("sem alter"):
                fora.append(f"passagem {k}: {f}")
        linhas.append({"id": i, "instrucoes_em_falta": em_falta, "artigos_a_mais": a_mais, "artigos_em_falta": artigos_falta,
                       "fora_dos_artigos": " | ".join(fora) if fora else "sem alterações", "passagens": len(passagens)})
    destino = VERIFICACAO / f"saida-piloto-{ronda}-lote-01.jsonl"
    destino.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas), encoding="utf-8")
    print(f"{len(por_id)} diplomas, {sum(1 for l in linhas if 'veredicto' in l)} trechos em {destino.relative_to(RAIZ)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("passagem")
    p.add_argument("ids", type=Path)
    p.add_argument("trabalho", type=Path)
    p.add_argument("--max-chars", type=int, default=230_000)
    p.add_argument("--inline", type=int, default=90_000)
    j = sub.add_parser("juntar")
    j.add_argument("ids", type=Path)
    e = sub.add_parser("entrada")
    e.add_argument("ronda", type=int)
    e.add_argument("ids", type=Path)
    v = sub.add_parser("vistas")
    v.add_argument("ronda", type=int)
    v.add_argument("ids", type=Path)
    v.add_argument("trabalho", type=Path)
    v.add_argument("--inline", type=int, default=90_000)
    s = sub.add_parser("saida")
    s.add_argument("ronda", type=int)
    s.add_argument("trabalho", type=Path)
    args = parser.parse_args()
    ler_ids = lambda f: f.read_text(encoding="utf-8").split()
    if args.comando == "passagem":
        passagem(ler_ids(args.ids), args.trabalho, args.max_chars, args.inline)
    elif args.comando == "juntar":
        juntar(ler_ids(args.ids))
    elif args.comando == "entrada":
        entrada(args.ronda, ler_ids(args.ids))
    elif args.comando == "vistas":
        vistas(args.ronda, ler_ids(args.ids), args.trabalho, args.inline)
    else:
        saida(args.ronda, args.trabalho)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
