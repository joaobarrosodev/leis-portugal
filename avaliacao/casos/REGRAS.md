# Regras para escrever os casos de advogado

Cada caso imita o que um advogado escreveria na app: «o contexto é este, aconteceu isto ao meu cliente, estou a pensar usar estas leis». A resposta certa diz que artigos se aplicam, se as leis que ele pensou servem, o que fazer e o resultado que a lei deixa prever. Serve para medir o fluxo de análise de caso, que ainda não existe; a primeira medição é a de base, com o sistema de hoje.

## O que não se pode abrir

Para os casos não ficarem à medida do sistema:
- nada em `avaliacao/` além desta pasta (`casos/`): nem as perguntas de avaliação, nem `privado/`, nem `verificacao/`;
- nada em `rag/` (código da pesquisa e resultados).

O texto das leis lê-se só do acervo, com `avaliacao/casos/artigo.py` (o leitor do índice).

## Como se escreve um caso

- **Factos de 2025 e 2026**, para valer o texto em vigor hoje. `data_referencia` é `2026-11-26`. Não escrevas casos que dependam de um regime transitório ou de uma redação antiga.
- **Narrativa** de 120 a 300 palavras, na voz do advogado («O meu cliente…»), com datas, valores e o que cada parte já fez. Sem números de artigos na narrativa.
- **`leis_pensadas`**: 1 a 3 leis que o advogado diz que tenciona usar, escritas como ele as citaria («o 351.º do CT», «a lei do arrendamento»). Em pelo menos 2 dos teus 5 casos, uma delas não serve: artigo errado, regime que não se aplica, prazo que já passou, ou falta a lei que decide o caso. Diz em `serve` (`sim`, `nao` ou `em_parte`) e em `motivo` porquê. Quando a lei pensada é um artigo concreto, põe também a referência (`documento`, `caminho`, `titulo`, `artigo`, `epigrafe`).
- **`questoes`**: 2 a 4 perguntas jurídicas que o caso levanta, na voz do advogado, cada uma sozinha (sem «e quanto ao resto?»).
- **`resposta.artigos_essenciais`**: 2 a 5 artigos sem os quais a resposta está errada. Cada um com `documento`, `caminho`, `titulo`, `artigo` (a chave do leitor), `epigrafe`, `excerto` (cópia literal, até 200 caracteres, do trecho que sustenta a afirmação) e `para_que` (uma frase).
- **`resposta.artigos_uteis`**: artigos que uma boa resposta citaria, mas que não decidem (pode ficar vazio). Mesma forma, `excerto` opcional.
- **`resposta.conclusao`**: o que fazer e o resultado que a lei deixa prever, em 3 a 8 frases. Cada afirmação jurídica leva o artigo entre parênteses.
- **`resposta.prazos`**: os prazos que contam no caso (`o_que`, `prazo`, `artigo`), se os houver. Conta-os a partir das datas da narrativa e diz se já passaram a 26/11/2026.
- **`resposta.fora_da_lei_escrita`**: o que depende de prova, de interpretação ou de jurisprudência. Não ponhas isso na conclusão como certo.
- **`armadilha`**: o que um sistema fraco erraria (lei pensada que não serve, prazo, regime especial). `null` se não houver.
- **`dificuldade`**: `base` (um regime, artigos óbvios), `media` (dois regimes ou uma exceção) ou `alta` (vários regimes, prazos, uma armadilha).

Só o que a lei escrita diz conta como certo. Quando a resposta depende de um conceito indeterminado (justa causa, culpa grave), a conclusão diz o que a lei exige e o que fica a depender da prova; não inventes o desfecho.

## Forma (uma linha JSON por caso)

```json
{"id": "caso-trab-01", "area": "trabalho", "data_referencia": "2026-11-26", "dificuldade": "media",
 "narrativa": "O meu cliente…",
 "leis_pensadas": [{"como_cita": "o 351.º do CT", "serve": "sim", "motivo": "…", "documento": "pt:dre:602073:por",
                    "caminho": "data/portugal/leis/2009/lei-7-2009.md", "titulo": "Lei n.º 7/2009",
                    "artigo": "Anexo — CÓDIGO DO TRABALHO::351.º", "epigrafe": "Noção de justa causa de despedimento"}],
 "questoes": ["…", "…"],
 "resposta": {"artigos_essenciais": [{"documento": "…", "caminho": "…", "titulo": "…", "artigo": "…", "epigrafe": "…", "excerto": "…", "para_que": "…"}],
              "artigos_uteis": [], "conclusao": "…", "prazos": [{"o_que": "…", "prazo": "…", "artigo": "…"}],
              "fora_da_lei_escrita": "…"},
 "armadilha": "…"}
```

## A ferramenta

```
P="/Users/barroso/Documents/Seamless Doubt/leis-portugal/.venv/bin/python"
$P avaliacao/casos/artigo.py diploma "Lei n.º 7/2009"           # caminho e id (título como no DRE)
$P avaliacao/casos/artigo.py listar <caminho> "férias"          # chaves e epígrafes que batem
$P avaliacao/casos/artigo.py ler <caminho> "<chave>"            # texto em vigor e notas
$P avaliacao/casos/artigo.py procurar <caminho> "aviso prévio"  # artigos com a expressão no texto
$P avaliacao/casos/artigo.py verificar <ficheiro.jsonl>         # tem de dar «0 erros»
```

Corre-se na raiz do worktree. Os códigos aprovados em anexo têm chaves como `Anexo — CÓDIGO DO TRABALHO::351.º`; copia-as do `listar`, com o travessão e as maiúsculas.

Os códigos mais usados:

| Código | Título do registo |
|---|---|
| Código Civil | Decreto-Lei n.º 47344 |
| Código do Trabalho | Lei n.º 7/2009 |
| Código de Processo Civil | Lei n.º 41/2013 |
| Código das Sociedades Comerciais | Decreto-Lei n.º 262/86 |
| CIRE | Decreto-Lei n.º 53/2004 |
| CPA | Decreto-Lei n.º 4/2015 |
| Regime geral das contraordenações | Decreto-Lei n.º 433/82 |
| NRAU | Lei n.º 6/2006 |
| Acidentes de trabalho | Lei n.º 98/2009 |

Se o `diploma` não encontrar um título, procura com `find data -path "*/<ano>/*-<número>-<ano>*.md"`.
