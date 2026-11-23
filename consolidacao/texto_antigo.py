"""Verificação mecânica, sem LLM: o texto antigo que fica num artigo que recebeu nova redação ou revogação.

O erro que mais se repete nas rondas da camada 1 é este: a resposta escreve a nova redação, ou
«(Revogado.)», e o corpo antigo do artigo fica a seguir. Às vezes fica depois de um título de divisão
interno, como «##### Divisão de Pessoal». A verificação às cegas deixou passar alguns, como o DR 44/80 na
ronda 116. Por isso esta verificação corre antes de aplicar ao acervo. Um artigo fica marcado quando:

- o corpo original inteiro está no fim do artigo e há texto novo antes dele; ou
- o artigo tem «(Revogado.)» e mantém parágrafos do corpo original.

Não contam as fórmulas finais e as assinaturas («Visto e aprovado…», «Promulgado…»), nem os anexos que
ficaram dentro do último artigo. Na varredura de 23/11/2026 aos 2.795 consolidados do data/ eram os
falsos positivos conhecidos. Os rótulos repetidos («1 -» duas vezes) também não marcam por si sós: nessa
varredura, 50 casos sem mais nada foram todos falsos positivos (redações de outros diplomas citadas,
artigos sem título juntos debaixo da mesma chave).

Uso:
    python consolidacao/texto_antigo.py "verificacao/entrada-piloto-116-lote-*.jsonl"
"""

from __future__ import annotations

import glob
import json
import re
import sys

TITULO = re.compile(r"^#{1,6}\s+(?:Artigo|Art\.?)\s*([0-9]+\.?\s*[º°o]?(?:-[A-Z])?)", re.I)
FECHO = re.compile(
    r"^(Visto e aprovado|Promulgad|Publique-se|Referendad|Assinatura|Presidência do Conselho de Ministros, \d|"
    r"O Presidente da República|Pelo Primeiro-Ministro|O Primeiro-Ministro, [A-ZÁÉÍÓÚ][a-záéíóú]+ [A-ZÁÉÍÓÚ]|"
    r"\[?\(ver documento original\))"
)
REVOGADO = re.compile(r"\(Revogad[oa]\.?\)\.?")
ANEXO = re.compile(r"^#{1,3} +(ANEXO|MAPA|QUADRO|TABELA)", re.M | re.I)


def _chave(numero: str) -> str:
    return re.sub(r"\s", "", numero).rstrip(".").replace("°", "º").replace("o", "º")


def artigos(texto: str) -> dict[str, str]:
    """Corpo de cada artigo, pela chave «N.º», até ao título do artigo seguinte."""
    resultado: dict[str, str] = {}
    atual, linhas = None, []
    for linha in texto.split("\n"):
        m = TITULO.match(linha)
        if m:
            if atual and atual not in resultado:
                resultado[atual] = "\n".join(linhas)
            atual, linhas = _chave(m.group(1)), []
        elif atual:
            linhas.append(linha)
    if atual and atual not in resultado:
        resultado[atual] = "\n".join(linhas)
    return resultado


def paragrafos(corpo: str) -> list[str]:
    """Os parágrafos do corpo, sem notas («> …») nem títulos de divisão («#…»)."""
    return [p.strip() for p in corpo.split("\n\n") if p.strip() and not p.strip().startswith((">", "#"))]


def marcados(original: str, consolidado: str) -> list[dict]:
    """Os artigos do consolidado que mantêm o corpo antigo a seguir à nova redação ou a «(Revogado.)»."""
    o, c = artigos(original), artigos(consolidado)
    ultimo = list(o)[-1] if o else None
    achados = []
    for chave, corpo in c.items():
        if chave not in o or corpo.strip() == o[chave].strip():
            continue
        if chave == ultimo and ANEXO.search(corpo):
            continue
        antigos_todos = [p for p in paragrafos(o[chave]) if not _e_fecho(p)]
        # o que vem a partir da primeira fórmula final ou das assinaturas do original é fecho, não corpo
        po = paragrafos(o[chave])
        i = next((k for k, p in enumerate(po) if _e_fecho(p)), None)
        if i is not None:
            antigos_todos = [p for p in po[:i]]
        pc = paragrafos(corpo)
        no_fim = (bool(antigos_todos) and len(pc) > len(antigos_todos) and pc[-len(antigos_todos):] == antigos_todos
                  and any(p not in antigos_todos for p in pc[: -len(antigos_todos)]))
        revogado = any(REVOGADO.fullmatch(p) for p in pc)
        mantidos = [p for p in pc if p in antigos_todos and len(p) >= 30 and "Revogad" not in p]
        if no_fim or (revogado and mantidos):
            achados.append({"artigo": chave, "corpo_antigo_no_fim": no_fim, "revogado_com_texto_antigo": bool(revogado and mantidos),
                            "exemplo": (mantidos or antigos_todos or [""])[0][:160]})
    return achados


ESTRUTURA = re.compile(
    r"^#{1,6}\s+(?:(?:PARTE|LIVRO|T[ÍI]TULO|CAP[ÍI]TULO|SEC[ÇC][ÃA]O|SUBSEC[ÇC][ÃA]O|DIVIS[ÃA]O|SUBDIVIS[ÃA]O)\b|ANEXO|MAPA|QUADRO|TABELA|"
    r"(?:Artigo|Art\.?)\s*\d)", re.I)
# «CAPÍTULO», «Secção», «Subsecção»… fecham o artigo em qualquer caso; «Divisão» só com número («DIVISÃO XI», «Divisão I»):
# «Divisão de Pessoal» é a epígrafe de um artigo orgânico, não uma divisão do diploma
_ESTRUTURA_NOME = re.compile(r"^#{1,6}\s+(?:PARTE|LIVRO|T[ÍI]TULO|CAP[ÍI]TULO|SUBSEC[ÇC][ÃA]O|SEC[ÇC][ÃA]O)\b", re.I)
_ESTRUTURA_DIVISAO = re.compile(r"^#{1,6}\s+(?:SUB)?DIVIS[ÃA]O\s+(?:[IVXLC]+|\d+|[ÚU]NICA)\b", re.I)
# uma linha só de nomes separados por « - » é a das assinaturas
_ASSINATURAS = re.compile(r"^[A-ZÁÉÍÓÚÂÊÔ][^\d\n]{2,80}(?: - [A-ZÁÉÍÓÚÂÊÔ][^\d\n]{2,80})+\.?$")


def _e_estrutura(linha: str) -> bool:
    """Um título que fecha o artigo: o artigo seguinte, um anexo, ou uma divisão do diploma (capítulo, secção…)."""
    if TITULO.match(linha) or re.match(r"^#{1,6}\s+(ANEXO|MAPA|QUADRO|TABELA)\b", linha, re.I):
        return True
    return bool(_ESTRUTURA_NOME.match(linha) or _ESTRUTURA_DIVISAO.match(linha))


def _e_fecho(linha: str) -> bool:
    s = linha.strip()
    return bool(FECHO.search(s) or _ASSINATURAS.match(s))


def revogar_inteiro(texto: str, original: str | None = None, so: set[str] | None = None) -> tuple[str, list[dict]]:
    """Revogação de um artigo inteiro, por regra e sem LLM. Em cada artigo cujo corpo começa por «(Revogado.)», o
    corpo fica «(Revogado.)» e as notas («> Revogado pelo/a …»). Sai o resto até ao artigo seguinte ou a um título de
    estrutura (capítulo, secção, anexo…), incluindo os títulos de divisão que estão dentro dele («##### Divisão de
    Pessoal»), que eram a epígrafe do artigo revogado. A epígrafe passa para o título do artigo quando ele não a tem.
    As fórmulas finais e as assinaturas («Visto e aprovado…», «Promulgado…») ficam, porque não são corpo do artigo.
    Devolve o texto e, por artigo mudado, o que saiu."""
    linhas = texto.split("\n")
    saida, feitos, i = [], [], 0
    while i < len(linhas):
        m = TITULO.match(linhas[i])
        if not m:
            saida.append(linhas[i])
            i += 1
            continue
        # o bloco do artigo: até ao artigo seguinte ou a um título de estrutura
        fim = i + 1
        while fim < len(linhas) and not _e_estrutura(linhas[fim]):
            fim += 1
        bloco = linhas[i + 1:fim]
        nao_vazias = [l for l in bloco if l.strip()]
        if not nao_vazias or not REVOGADO.fullmatch(nao_vazias[0].strip()) or (so is not None and _chave(m.group(1)) not in so):
            saida.extend(linhas[i:fim])
            i = fim
            continue
        # «(Revogado.)» e as notas que o seguem ficam; o resto sai até a uma fórmula final
        k = next(j for j, l in enumerate(bloco) if l.strip())
        mantidas = bloco[:k + 1]
        j = k + 1
        while j < len(bloco) and (not bloco[j].strip() or bloco[j].lstrip().startswith(">")):
            mantidas.append(bloco[j])
            j += 1
        fecho = next((x for x in range(j, len(bloco)) if _e_fecho(bloco[x])), len(bloco))
        removidas = bloco[j:fecho]
        titulo = linhas[i]
        epigrafe = None
        if original is not None and any(l.strip() for l in removidas):
            # só sai texto antigo: cada parágrafo tirado tem de ser, letra a letra, do corpo do artigo original
            # (um título de secção em texto simples, «III / Das casas…», é da secção seguinte e fica)
            corpo_o = {p.strip() for p in artigos(original).get(_chave(m.group(1)), "").split("\n\n") if p.strip()}
            tirados = [p.strip() for p in "\n".join(removidas).split("\n\n") if p.strip()]
            # num artigo revogado, saem também as partes do corpo antigo já revogadas («d) (Revogada.)») e as suas notas
            ja_revogado = re.compile(r"^(?:[\w§º°.\-]{1,12}\s*[-–)]?\s*)?\(Revogad[oa]s?\.?\)\.?$")
            if not corpo_o or any(p not in corpo_o and not p.startswith(">") and not ja_revogado.match(p) for p in tirados):
                saida.extend(linhas[i:fim])
                i = fim
                continue
        if any(l.strip() for l in removidas):
            if " — " not in titulo:
                h = next((re.match(r"^#{1,5}\s+(.+)$", l) for l in removidas if re.match(r"^#{1,5}\s+\S", l)), None)
                if h:
                    epigrafe = h.group(1).strip()
                    titulo = f"{titulo.rstrip()} — {epigrafe}"
            feitos.append({"artigo": _chave(m.group(1)), "removido": "\n".join(removidas).strip(), "epigrafe_no_titulo": epigrafe})
            saida.append(titulo)
            saida.extend(mantidas)
            if fecho < len(bloco):
                saida.append("")
            saida.extend(bloco[fecho:])
        else:
            saida.extend(linhas[i:fim])
        i = fim
    novo = re.sub(r"\n{3,}", "\n\n", "\n".join(saida))
    return novo, feitos


CONFIRMADOS = "auditoria/texto-antigo-confirmados.jsonl"
CORRIGIDOS = "auditoria/texto-antigo-corrigidos.jsonl"
VERIFICACAO = "llm/texto-antigo"


def _bloco(linhas: list[str], chave: str) -> tuple[int, int] | None:
    """Linhas [início, fim) do artigo `chave` no texto (do título ao título do artigo seguinte)."""
    inicio = None
    for i, linha in enumerate(linhas):
        m = TITULO.match(linha)
        if m and inicio is None and _chave(m.group(1)) == chave:
            inicio = i
        elif m and inicio is not None:
            return inicio, i
    return (inicio, len(linhas)) if inicio is not None else None


def corrigir_artigo(linhas: list[str], chave: str, corpo_original: str) -> tuple[list[str], dict] | None:
    """Tira do artigo `chave` o bloco final que é, letra a letra, o corpo do artigo original (com o título de
    divisão que lhe servia de epígrafe). Os títulos de capítulo e secção que fecham o bloco ficam, e a epígrafe
    passa ao título do artigo quando ele não a tem. Devolve None quando o fim do artigo não é o corpo original."""
    lim = _bloco(linhas, chave)
    if lim is None:
        return None
    ini, fim = lim
    # os títulos de estrutura (capítulo, secção…) no fim do bloco são do que vem a seguir
    fecho = fim
    while fecho > ini and (not linhas[fecho - 1].strip() or re.match(r"^#{1,4} ", linhas[fecho - 1])):
        fecho -= 1
    alvo = [l for l in corpo_original.split("\n")]
    while alvo and (not alvo[-1].strip() or re.match(r"^#{1,4} ", alvo[-1])):
        alvo.pop()
    while alvo and not alvo[0].strip():
        alvo.pop(0)
    n = len(alvo)
    if n == 0 or fecho - n <= ini + 1 or linhas[fecho - n:fecho] != alvo:
        return None
    resto = linhas[ini:fecho - n]
    if not any(l.strip() for l in resto[1:]):
        return None  # sem texto novo antes: não é este erro
    epigrafe = None
    m = re.match(r"^#{5}\s+(.+)$", alvo[0])
    titulo = linhas[ini]
    if m and " — " not in titulo:
        epigrafe = m.group(1).strip()
        titulo = f"{titulo.rstrip()} — {epigrafe}"
    novas = linhas[:ini] + [titulo] + linhas[ini + 1:fecho - n] + linhas[fecho:]
    removido = "\n".join(alvo)
    return novas, {"artigo": chave, "removido": removido, "epigrafe_no_titulo": epigrafe,
                   "antes": "\n".join(linhas[ini:fim]).strip(), "depois": "\n".join(novas[ini:ini + (fim - ini) - n]).strip()}


def corrigir(raiz: str, aplicar: bool) -> int:
    """Corrige os artigos confirmados em `auditoria/texto-antigo-confirmados.jsonl` e escreve a entrada da
    verificação às cegas (`llm/texto-antigo/entrada.jsonl`). Com `aplicar`, grava no data/ só os artigos que a
    verificação deu `certo` (`llm/texto-antigo/saida.jsonl`)."""
    from pathlib import Path  # noqa: PLC0415

    sys.path.insert(0, str(Path(raiz) / "src"))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from acervo import blocos, historico  # noqa: PLC0415

    from leis_portugal.domain.history import render_version, summarize  # noqa: PLC0415
    from leis_portugal.infrastructure.repository import Acervo  # noqa: PLC0415

    pasta = Path(__file__).resolve().parent
    acervo = Acervo(Path(raiz))
    por: dict[str, list[str]] = {}
    for l in (pasta / CONFIRMADOS).read_text(encoding="utf-8").splitlines():
        if l.strip():
            d = json.loads(l)
            por.setdefault(d["caminho"], []).append(d["artigo"])
    certos = set()
    if aplicar:
        for l in (pasta / VERIFICACAO / "saida.jsonl").read_text(encoding="utf-8").splitlines():
            if l.strip():
                v = json.loads(l)
                if v["veredicto"] == "certo":
                    certos.add((v["caminho"], v["artigo"]))
    itens, feitos, recusas = [], [], []
    for caminho, chaves in sorted(por.items()):
        md = Path(raiz) / caminho
        registo, texto = acervo.read(md)
        dados = acervo.read_history(md)
        if len(dados["versions"]) != 2:
            recusas.append(f"{caminho}: o histórico não tem duas versões")
            continue
        original = render_version(dados, dados["versions"][0], title=registo.title)
        artigos_o = artigos(original)
        linhas = texto.split("\n")
        mudou = []
        for chave in chaves:
            r = corrigir_artigo(linhas, chave, artigos_o.get(chave, ""))
            if r is None:
                recusas.append(f"{caminho} art. {chave}: o fim do artigo não é o corpo original")
                continue
            novas, info = r
            itens.append({"n": len(itens) + 1, "caminho": caminho, "id": registo.id, "diploma": registo.title,
                          "artigo_original": artigos_o.get(chave, "").strip()} | info)
            if aplicar and (caminho, chave) not in certos:
                continue
            linhas = novas
            mudou.append(chave)
        if not aplicar or not mudou:
            continue
        novo = "\n".join(linhas)
        primeira, segunda = (dict(v) for v in dados["versions"])
        novos = historico(registo.id, registo.title, original, novo, [primeira, segunda])
        if blocos(render_version(novos, novos["versions"][1], title=registo.title)) != blocos(novo):
            recusas.append(f"{caminho}: o histórico não reproduz o texto")
            continue
        registo.version_history = summarize(novos, acervo.history_path(md).name)
        nota = " Texto antigo deixado a seguir à nova redação ou a «(Revogado.)» retirado por regra e verificado às cegas (consolidacao/texto_antigo.py): arts. " + ", ".join(mudou) + "."
        if "consolidacao/texto_antigo.py" not in (registo.provenance.notes or ""):
            anteriores = (registo.provenance.notes or "").rstrip()
            registo.provenance.notes = (anteriores + ("" if not anteriores or anteriores.endswith(".") else ".") + nota).strip()
        acervo.save(registo, novo, target=md)
        acervo.write_history(md, novos)
        feitos.append({"id": registo.id, "caminho": caminho, "titulo": registo.title, "artigos": mudou})
    if aplicar:
        (pasta / CORRIGIDOS).write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in feitos), encoding="utf-8")
        print(f"{sum(len(f['artigos']) for f in feitos)} artigos corrigidos em {len(feitos)} consolidados")
    else:
        (pasta / VERIFICACAO).mkdir(parents=True, exist_ok=True)
        (pasta / VERIFICACAO / "entrada.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in itens), encoding="utf-8")
        print(f"{len(itens)} artigos para a verificação às cegas em {VERIFICACAO}/entrada.jsonl")
    for r in recusas:
        print("  recusa:", r)
    return 0


PENDENTES_R2 = "auditoria/texto-antigo-revogar.jsonl"
VERIFICACAO_R2 = "llm/texto-antigo-r2"


def revogar_no_acervo(raiz: str, aplicar: bool) -> int:
    """`revogar_inteiro` nos artigos de `auditoria/texto-antigo-revogar.jsonl` (caminho, artigo) do data/. Sem
    `aplicar`, escreve a entrada da verificação às cegas em `llm/texto-antigo-r2/entrada.jsonl`; com `aplicar`,
    grava só os artigos que a verificação deu `certo` (`llm/texto-antigo-r2/saida.jsonl`), com o histórico refeito."""
    from pathlib import Path  # noqa: PLC0415

    sys.path.insert(0, str(Path(raiz) / "src"))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from acervo import blocos, historico  # noqa: PLC0415

    from leis_portugal.domain.history import render_version, summarize  # noqa: PLC0415
    from leis_portugal.infrastructure.repository import Acervo  # noqa: PLC0415

    pasta = Path(__file__).resolve().parent
    acervo = Acervo(Path(raiz))
    por: dict[str, set[str]] = {}
    for l in (pasta / PENDENTES_R2).read_text(encoding="utf-8").splitlines():
        if l.strip():
            d = json.loads(l)
            por.setdefault(d["caminho"], set()).add(d["artigo"])
    certos = set()
    if aplicar:
        for l in (pasta / VERIFICACAO_R2 / "saida.jsonl").read_text(encoding="utf-8").splitlines():
            if l.strip():
                v = json.loads(l)
                if v["veredicto"] == "certo":
                    certos.add((v["caminho"], v["artigo"]))
    itens, feitos, recusas = [], [], []
    for caminho, chaves in sorted(por.items()):
        md = Path(raiz) / caminho
        registo, texto = acervo.read(md)
        dados = acervo.read_history(md)
        if len(dados["versions"]) != 2:
            recusas.append(f"{caminho}: o histórico não tem duas versões")
            continue
        original = render_version(dados, dados["versions"][0], title=registo.title)
        so = {c for c in chaves if not aplicar or (caminho, c) in certos}
        if not so:
            continue
        novo, mudados = revogar_inteiro(texto, original, so=so)
        for c in chaves - {x["artigo"] for x in mudados}:
            recusas.append(f"{caminho} art. {c}: a regra não se aplica (o que vem a seguir a «(Revogado.)» não é só texto antigo)")
        a_o, a_c, a_n = artigos(original), artigos(texto), artigos(novo)
        for x in mudados:
            itens.append({"n": len(itens) + 1, "caminho": caminho, "id": registo.id, "diploma": registo.title, "artigo": x["artigo"],
                          "artigo_original": a_o.get(x["artigo"], "").strip(), "antes": a_c.get(x["artigo"], "").strip(),
                          "depois": a_n.get(x["artigo"], "").strip(), "removido": x["removido"], "epigrafe_no_titulo": x["epigrafe_no_titulo"]})
        if not aplicar or not mudados:
            continue
        primeira, segunda = (dict(v) for v in dados["versions"])
        novos = historico(registo.id, registo.title, original, novo, [primeira, segunda])
        if blocos(render_version(novos, novos["versions"][1], title=registo.title)) != blocos(novo):
            recusas.append(f"{caminho}: o histórico não reproduz o texto")
            continue
        registo.version_history = summarize(novos, acervo.history_path(md).name)
        acervo.save(registo, novo, target=md)
        acervo.write_history(md, novos)
        feitos.append({"id": registo.id, "caminho": caminho, "titulo": registo.title, "artigos": [x["artigo"] for x in mudados]})
    if aplicar:
        anteriores = (pasta / CORRIGIDOS).read_text(encoding="utf-8") if (pasta / CORRIGIDOS).exists() else ""
        (pasta / CORRIGIDOS).write_text(anteriores + "".join(json.dumps(f, ensure_ascii=False) + "\n" for f in feitos), encoding="utf-8")
        print(f"{sum(len(f['artigos']) for f in feitos)} artigos revogados por regra em {len(feitos)} consolidados")
    else:
        (pasta / VERIFICACAO_R2).mkdir(parents=True, exist_ok=True)
        (pasta / VERIFICACAO_R2 / "entrada.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in itens), encoding="utf-8")
        print(f"{len(itens)} artigos para a verificação às cegas em {VERIFICACAO_R2}/entrada.jsonl")
    for r in recusas:
        print("  recusa:", r)
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in ("revogar", "revogar-aplicar"):
        return revogar_no_acervo(sys.argv[2], sys.argv[1] == "revogar-aplicar")
    if len(sys.argv) > 1 and sys.argv[1] in ("corrigir", "aplicar"):
        return corrigir(sys.argv[2], sys.argv[1] == "aplicar")
    total = 0
    for f in sorted(glob.glob(sys.argv[1])):
        for linha in open(f, encoding="utf-8"):
            d = json.loads(linha)
            a = marcados(d.get("texto_original", ""), d.get("texto_consolidado", ""))
            if a:
                total += 1
                print(d["id"], d.get("titulo"), [x["artigo"] for x in a])
    print(f"{total} diplomas marcados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
