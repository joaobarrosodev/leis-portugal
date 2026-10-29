# Protótipo de RAG: o ponto de partida

Um RAG razoável sobre o acervo, medido com o [conjunto de avaliação](../avaliacao/README.md) (593 perguntas verificadas às cegas). É o ponto de partida da fase 4 do [plano](../PLANO-RAG.md): quanto acerta hoje, por tipo de pergunta, antes das fases 2 (texto em vigor) e 3 (artigos, vigência e datas).

Medido em 27/10/2026, sobre o acervo do commit `3cbc718` e o export de 26/10/2026; a versão com reranker foi medida outra vez depois de a referência exata passar a candidata. **Sem LLM**: não havia chave da API da Anthropic no ambiente, por isso mede-se a pesquisa e uma resposta extrativa (o primeiro artigo encontrado, com os avisos).

## Resumo

Com pesquisa por referência, BM25 e um reranker multilingue local, o artigo certo vem em 1.º lugar em 96% das perguntas literais (sem 20 cujo artigo já está revogado, ver abaixo), 94% das temporais e em todas as revogadas, e em 56% das reais. Quando o artigo certo vem, a redação é sempre a da data da pergunta, e as 55 revogadas trazem o aviso de revogação com o diploma revogatório certo.

| Tipo | n | Artigo certo em 1.º | Nos 5 primeiros | "Não sei" (limiar 3) | Fiabilidade sem LLM (limiar 3) |
|---|--:|--:|--:|--:|--:|
| Literais | 250 | 90% (96% sem as 20 revogadas ²) | 95% | 3% | 93% (226/243) |
| Temporais | 102 | 94% | 100% | 6% | 98% (94/96) |
| Revogadas | 55 | 100% | 100% | 0% | 100% (55/55) |
| Sem resposta | 50 | — | — | 94% | — (3 respondidas, erradas) |
| Reais (FAQs) | 136 | 56% | 78% | 22% | 65% (69/106) |
| **Total** | **593** | **83%** ¹ | **92%** ¹ | **15%** | **88% (444/503)** |

¹ Nas 543 perguntas com fonte (sem as 50 sem resposta).

² Vinte perguntas literais (`lit-008`, `-011`, `-022`, `-037`, `-052`, `-089`, `-096`, `-098`, `-114`, `-120`, `-125`, `-152`, `-153`, `-154`, `-160`, `-161`, `-194`, `-196`, `-204`, `-232`) foram feitas sobre artigos que o acervo dá hoje como revogados por nota ("Revogado pelo/a …") mas cujo texto o DRE mantém. Desde 28/10/2026 o índice trata esses artigos como revogados (nota de revogação abre redação nova, aviso "Artigo revogado" e prior menor), por isso deixam de ser a resposta: é o comportamento certo e a pergunta é que está errada. Sem elas, a literal é 96% (221/230 respondidas certas), como antes; no total, 90% (439/490).

- **Ainda longe dos 95%**: 88% de respostas certas nas dadas (444/503), com 15% de "não sei". Sem as reais, 94% (375/397); nas reais, 65%. As reais subiram de 52% para 65% com a correção das revogações por nota: "Quantos dias de férias…" deixou de dar o Código do Trabalho de 2003.
- A "fiabilidade" aqui é um **limite superior sem LLM**: conta como certa a resposta cujo primeiro artigo é o certo e tem o texto em vigor na data. Falta medir o passo do LLM (não havia chave).
- O limiar 3 do reranker foi escolhido neste mesmo conjunto; é indicativo. A curva completa está abaixo.
- O conjunto só tem perguntas sobre diplomas consolidados ou nunca alterados, por isso **não mede o maior risco do plano**: os 27 mil diplomas em vigor alterados sem consolidação, em que o sistema citaria texto desatualizado (avisa "texto original; alterado por X", mas a resposta seria a antiga).

## Como funciona

1. **Índice por artigo** (`indice.py`). Um pedaço por artigo dos 223.357 diplomas com texto (`text_quality = texto`), num SQLite com FTS5: 1.355.396 pedaços, 3,9 GB, 5 minutos a construir.
   - Cada pedaço tem o caminho completo: diploma (tipo, número, data) › anexo › artigo e epígrafe, por exemplo `Decreto-Lei n.º 433/99, de 1999-10-26 › Anexo — CÓDIGO DE PROCEDIMENTO E DE PROCESSO TRIBUTÁRIO › Artigo 288.º — Julgamento do recurso`.
   - Guarda a vigência (`legal_status`), a versão (`original`/`consolidated`), a data de consolidação e as relações `amended_by`, `repealed_by` e `republished_by` (só as que levam ao "texto em vigor", tiradas do cabeçalho dos registos, porque o export de 26/10 ainda não as tem).
   - Nos 8.049 diplomas com histórico (`.versoes.json`) cada **redação** de cada artigo é um pedaço, com as datas em que esteve em vigor (`desde`, `ate`). Nos outros, o texto vale desde a publicação.
   - Os 154.904 diplomas sem artigos identificados (sobretudo portarias e declarações de retificação) entram em 367.830 blocos de ~300 palavras (`texto#N`); os restantes 987.566 pedaços são artigos.
   - Os artigos leem-se com `avaliacao/comum.py`, numa só função (`fontes.ler_artigos`), para se trocar pelo parser da fase 3.
2. **Pesquisa** (`pesquisa.py`), por níveis:
   1. **Referência exata**: o artigo citado ("artigo 78.º-B") no diploma ("DL 84/2021", "Decreto-Lei n.º 433/99") ou código citado ("Código do IRS", "CIVA"). Os códigos resolvem-se para o anexo em vigor com mais artigos e histórico: o Código Penal no DL 48/95, o do Trabalho na Lei 7/2009, o do IRS na Lei 82-E/2014, o do IVA no DL 102/2008.
   2. **BM25 dentro dos diplomas citados**.
   3. **BM25 em todo o acervo**, com um peso a priori pela lei atual: consolidado pelo DRE ×1,25; revogado ou sem vigência ×0,6; vigência desconhecida ×0,85; anexos de republicação ×0,6.
   - Com reranker, os níveis 1 e 2 juntam-se: a referência exata entra como candidata e o reranker decide, porque muitas perguntas citam um artigo só como contexto ("a coima das contraordenações do n.º 1 do artigo 24.º" está no 25.º). Sem reranker, a referência exata vem sempre primeiro.
   - Os termos passam pelo radical Snowball português e perdem os acentos.
   - **Filtro pela data da pergunta**: só entram redações em vigor na `data_referencia` (`desde ≤ data < ate`) e diplomas já publicados.
   - **Códigos republicados**: um artigo de um diploma com `republished_by` "texto em vigor" troca-se pelo mesmo artigo no consolidado (o artigo 78.º-B do Código do IRS vem da Lei 82-E/2014, não do DL 442-A/88).
   - **Reranker** opcional (`modelos.py`): um cross-encoder multilingue (BAAI/bge-reranker-v2-m3, int8, local em CPU) reordena os 30 primeiros candidatos (os primeiros 1.200 caracteres de cada): primeiro os do diploma ou código citado, depois os do resto do acervo. Também há embeddings (paraphrase-multilingual-MiniLM-L12-v2) para reordenar; indexar o acervo inteiro com embeddings levaria ~5 h neste CPU e ficou de fora.
3. **Resposta** (`resposta.py`).
   - Com `ANTHROPIC_API_KEY` e o pacote `anthropic`, o LLM (`claude-opus-5-5`, ou `RAG_MODELO`) responde só a partir dos 8 primeiros artigos e cita-os; sem citação de um artigo dado, a resposta é "não sei". **Não foi testado** (não havia chave).
   - Sem chave, a resposta é o primeiro artigo, com os avisos.
   - Os avisos vêm sempre da pesquisa: "Diploma revogado por X (data)", "Texto original; alterado por X, Y e mais N, sem versão consolidada no acervo", "Redação em vigor de A a B, não a atual", "Artigo revogado", "Vigência do diploma desconhecida" e "Texto em vigor do diploma republicado (…), no consolidado de …".
   - "Não sei" quando a pergunta cita um diploma que não está no acervo, quando pergunta por um ano futuro, quando não há artigos ou quando o reranker dá ao melhor artigo menos do que um limiar.
4. **Medição** (`avaliar.py`), por tipo de pergunta.
   - `artigo@k`: o artigo certo (`fonte.documento` e `fonte.artigo`) nos k primeiros.
   - `texto@k`: e o pedaço tem o excerto, ou seja, é a redação em vigor na data da pergunta (nas temporais, a "versão certa").
   - Nas revogadas, se o primeiro resultado avisa da revogação e nomeia o diploma revogatório certo.
   - Nas sem resposta, a taxa de "não sei".
   - Fiabilidade = certas / respondidas. Sem LLM, "certa" é o primeiro artigo ser o certo e ter o excerto (nas revogadas: ser do diploma certo e avisar da revogação pelo diploma certo); é um limite superior do que um LLM acertaria com esse artigo.

## Como correr

```bash
pip install -e '.[rag]'
```

Instala o radical Snowball, o reranker e os embeddings (`fastembed`) e o SDK da Anthropic. Sem o extra, o índice usa um radical simplificado e não há reranker. Neste ambiente os pacotes ficaram em `.rag-deps/` (`pip install --target .rag-deps fastembed`), que o pacote `rag` acrescenta ao caminho.

```bash
PYTHONPATH=src python -m rag.indice
PYTHONPATH=src python -m rag.avaliar --nome bm25 --sem-llm
PYTHONPATH=src python -m rag.avaliar --nome cruzado --reranker cruzado --sem-llm
```

Para fazer perguntas uma a uma (por exemplo, para alguém testar), na raiz do repositório:

```bash
./perguntar
```

Na primeira vez prepara tudo: o `.venv` com o extra `rag`, o export e o índice (~5 min). Depois abre as perguntas, com o reranker e o limiar 3. Mostra o artigo mais provável com os avisos e os outros artigos encontrados, e pergunta se está certo e, se não, o que se esperava. Tudo fica em `rag/resultados/privado/perguntas-testadas.jsonl` (fora do git), para as perguntas que falham entrarem no conjunto de avaliação. `./perguntar "a pergunta"` faz uma só; `./perguntar --reconstruir` refaz o export e o índice (por exemplo, depois de atualizar o acervo).

- `rag.indice` precisa de `exports/leis-portugal.sqlite` (na raiz, ou na pasta principal quando se corre numa worktree; ou `RAG_EXPORT`). `--amostra N` faz um índice só com os diplomas da avaliação e mais N, em segundos.
- `rag.avaliar` lê `avaliacao/perguntas.jsonl` e, se existir, `avaliacao/privado/perguntas-reais.jsonl`. O resumo vai para `rag/resultados/<nome>.json`; o detalhe por pergunta para `rag/resultados/privado/` (fora do git, porque tem o texto das perguntas reais). Com `ANTHROPIC_API_KEY`, usa o LLM, a não ser com `--sem-llm`.
- O índice, os modelos (descarregados do Hugging Face na primeira vez, ~0,7 GB) e o detalhe ficam em `rag/indice/` e `rag/resultados/privado/`, no `.gitignore`.
- Uma medição completa leva ~5 min só com BM25 e ~65 a 85 min com o reranker (7 a 8 s por pergunta, em CPU).

## Números

### Pesquisa: o artigo certo nos k primeiros

| Tipo | n | BM25 @1 | BM25 @5 | BM25 @10 | + reranker @1 | + reranker @5 | + reranker @10 |
|---|--:|--:|--:|--:|--:|--:|--:|
| Literais | 250 | 79% | 95% | 99% | 96% | 99,6% | 99,6% |
| Temporais | 102 | 78% | 97% | 99% | 95% | 100% | 100% |
| Revogadas | 55 | 87% | 100% | 100% | 100% | 100% | 100% |
| Reais | 136 | 26% | 59% | 71% | 46% | 78% | 79% |
| **Total com fonte** | **543** | **66%** | **87%** | **92%** | **84%** | **94%** | **95%** |

- **Versão certa**: em todos os tipos e configurações, `texto@k` (o pedaço tem o excerto) é igual a `artigo@k`. Quando o artigo certo aparece, é sempre a redação em vigor na `data_referencia`; nas temporais, a versão certa vem em 1.º em 95% (com reranker).
- **Revogadas**: o primeiro resultado avisa da revogação e nomeia o diploma revogatório certo nas 55 (com e sem reranker).
- **Peso a priori da lei atual**: sem ele, o BM25 dava 21% / 42% / 59% nas reais (@1/@5/@10) e 78% / 77% / 87% @1 nas literais, temporais e revogadas. Os pesos foram fixados antes de medir e não se afinaram.
- **Referência exata como candidata**: na primeira versão com reranker, a referência exata vinha sempre em 1.º e o artigo certo ficava em 1.º em 94% das literais, 89% das temporais e 98% das revogadas. Deixá-la competir com os outros candidatos corrigiu as 11 perguntas em que a referência era só contexto (`tmp-002`, `lit-102`, `lit-166`…) e não piorou nenhuma.
- O reranker só reordena os 30 primeiros candidatos do BM25; nas reais, o artigo certo não chega aos 10 primeiros em 28 das 136.

### "Não sei" e fiabilidade, sem LLM

Só com as regras da pesquisa (diploma citado que não está no acervo, ano futuro), o sistema diz "não sei" em 10 das 50 sem resposta (as 6 sobre leis que não existem e 4 das 5 sobre o futuro) e responde a quase tudo o resto: fiabilidade de 78% (453/582).

Com um limiar na pontuação do reranker para o melhor artigo:

| Limiar | "Não sei" nas que têm resposta | "Não sei" nas sem resposta | Fiabilidade (certas/respondidas) |
|--:|--:|--:|--:|
| sem limiar | 0% | 22% | 78% (453/582) |
| 0 | 1% | 72% | 83% (453/549) |
| 2 | 4% | 86% | 86% (451/526) |
| 3 | 8% | 94% | 88% (444/503) |
| 4 | 15% | 94% | 90% (419/467) |

A pontuação do reranker separa bem as perguntas sem resposta, mas pouco os erros das reais: o reranker acha relevante um artigo do diploma errado sobre o mesmo tema. O resto tem de vir do LLM (ler o artigo e ver se responde) e de melhor pesquisa.

### Com LLM

Sem chave da API, o LLM foi uma sessão do Claude (`claude-opus-5-5`) que leu os 8 primeiros artigos de cada pergunta e respondeu só a partir deles, sem ver as respostas certas (`passo_llm.py`: `exportar`, as sessões respondem aos lotes, `importar`). Medido em 28/10/2026 nas 136 reais e nas 50 sem resposta, com o reranker e o limiar 3; as 77 a que as regras já respondem "não sei" não foram ao LLM:

| Tipo | n | "Não sei" | Fiabilidade (certas/respondidas) | Sem LLM |
|---|--:|--:|--:|--:|
| Reais | 136 | 28% | **90% (88/98)** | 65% (69/106) |
| Sem resposta | 50 | 98% | 1 respondida, errada | 94% |

O LLM sobe a fiabilidade das reais de 65% para 90% à custa de 6 pontos de "não sei". "Certa" é citar o artigo certo e a resposta ter pelo menos 80% das palavras com conteúdo da resposta certa (`avaliacao/verifica.py`), um critério brando: falta uma verificação às cegas das respostas escritas. Em 29/10/2026 passaram também pelo LLM as literais, temporais e revogadas (4 sessões às cegas, mesmo critério):

| Tipo | n | "Não sei" | Fiabilidade (certas/respondidas) |
|---|--:|--:|--:|
| Literais | 250 | 3% | 93% (225/242); 95% (219/230) sem as 20 de resposta revogada² |
| Temporais | 102 | 6% | 94% (90/96) |
| Revogadas | 55 | 0% | 100% (55/55) |
| Total sintéticas | 407 | 3% | 94% (370/393) |

Com as reais (90%) o conjunto fica abaixo de 95% por causa das reais; nas sintéticas o LLM praticamente não muda o artigo@1 (93%), logo o teto é a pesquisa.

**Fase 4** (29/10/2026, ramo fundido):

Com o canal dos códigos principais e a grafia antiga (secção abaixo), repetido às cegas por 11 sessões do Claude (`claude-opus-5-5`), uma por lote, nas 136 reais:

| Reais, com LLM | "Não sei" | Certas | Fiabilidade (certas/respondidas) |
|---|--:|--:|--:|
| Antes | 28% | 88 | 90% (88/98) |
| Com mais candidatos | 24% | **92** | 89% (92/103) |

Responde-se a mais 5 perguntas e acerta-se em mais 4, com a fiabilidade igual. O número de artigos no contexto (8) não foi alterado: não se mediu 12 ou 16, que pede nova ronda de sessões.

**Juízes estritos** (`juiz.py`, 29/10/2026): cada resposta escrita das 136 reais (com a fase 4) foi julgada por dois juízes independentes (sessões do Claude, às cegas um do outro) contra a resposta de referência e os artigos vistos. Só conta como certa se os dois a dão como correta e fundamentada.

| Reais, com LLM | Valor |
|---|--:|
| Respondidas / "não sei" | 103 / 33 (24%) |
| Certas pelo critério brando (80% das palavras) | 89% (92/103) |
| Certas pelos juízes | **98% (101/103)** |
| Limite inferior a 95% de confiança (Wilson) | **93%** |
| Não certas | 1 incompleta (real-058), 1 errada (real-074: menor *de* 16 anos tratado com a regra dos 16 ou mais) |

Lido caso a caso, o critério das 80% de palavras dava como erradas 9 respostas que estão certas (diferem em palavras, não em sentido). Ressalvas, sem as quais o número engana: (1) estas 136 serviram para afinar o limiar e a pesquisa, por isso 98% não é desempenho em perguntas novas; (2) os dois juízes são o mesmo modelo, com os mesmos pontos cegos; (3) o "não sei" de 24% falha a meta de 15%; (4) 33 + 2 de 136 significa que só 74% das perguntas recebem resposta certa. O número a citar para fiabilidade é o limite inferior, 93%, e só depois de medir num conjunto que nunca serviu para afinar.

**Segundo travão** (`travao.py`): um segundo modelo julga, às cegas, se cada resposta escrita se aguenta nos artigos dados e responde à pergunta. Nas 99 respostas dadas (98 reais e 1 sem resposta) aprovou todas, por isso apanhou 0 das 11 erradas e não perdeu nenhuma certa. Dos 10 erros das reais, 6 têm o artigo certo em 1.º lugar (a resposta escrita difere da de referência no critério de 80% das palavras: o erro pode estar na métrica) e 4 são de pesquisa (diploma ou artigo errado). Ou seja, o erro não é o LLM inventar, e um travão que só confere a resposta contra os artigos não o apanha. Os 6 ficam para revisão às cegas por pessoa ou outro modelo antes de se chamar erro.

## Principais tipos de erro (com reranker)

Nas literais, temporais e revogadas o artigo certo falha o 1.º lugar em 15 perguntas:

| Erro | Literais | Temporais | Revogadas | Total |
|---|--:|--:|--:|--:|
| Diploma certo, artigo vizinho | 6 | 2 | 0 | 8 |
| Outro diploma (sobretudo o que alterou o certo) | 4 | 3 | 0 | 7 |

- **Artigo vizinho**: "Na mediação dos julgados de paz (Lei n.º 78/2001), quem escolhe o mediador?" (`lit-202`) dá o artigo 32.º (seleção dos mediadores) em vez do 51.º.
- **O diploma que alterou o certo**: "Na dependência de que membro do Governo funciona a Comissão Nacional da Reserva Ecológica Nacional?" (`lit-022`) dá o artigo 28.º do DL 239/2012, que alterou o regime, e não o do DL 166/2008; "Em outubro de 2009 … professor auxiliar …" (`tmp-051`) dá o DL 205/2009, que alterou o Estatuto da Carreira Docente Universitária.
- **Reais**: 73 das 136 não têm o artigo certo em 1.º; em 67 o primeiro é de outro diploma. Usam palavras do dia a dia e quase nunca citam o código (só 3 das 136 têm uma referência que o sistema reconhece), e o BM25 traz diplomas sobre o mesmo tema (portarias, regimes especiais, leis antigas). Em 28 o artigo certo nem chega aos 10 primeiros. O diagnóstico pergunta a pergunta está abaixo.
- **Sem resposta**: sem LLM, só as leis inexistentes e o futuro dão "não sei" pelas regras. As que pedem aconselhamento, jurisprudência ou lei estrangeira, ou citam um diploma que não trata do assunto, recebem um artigo parecido ("Quantos dias de férias tem um trabalhador em França?" dá o Código do Trabalho de 2003). Com o limiar 3 ficam 3: duas de jurisprudência (`sem-002`, `sem-008`) e uma de um diploma que fixa o capital de uma sociedade concreta (`sem-009`).
- **Códigos**: há vários anexos com o nome de cada código (republicações nas leis de alteração, que o DRE também consolida). A primeira versão escolhia o anexo de republicação da Lei 59/2007 para o Código Penal; escolher o diploma em vigor, com histórico e com mais artigos em vigor nesse anexo acerta em todos os códigos verificados.

### Diagnóstico das 73 reais falhadas

Cada uma das 73 reais sem o artigo certo em 1.º (limiar 3, `cruzado`) foi lida com o artigo certo e os três primeiros resultados e classificada (`rag/resultados/privado/reais-diagnostico.jsonl`, fora do git):

| Classe | n | O que é |
|---|--:|---|
| (a) O 1.º também responde | 2 | O CIMI 121.º remete para o art. 44.º da LGT (juros de mora); o DL 28/2019 art. 19.º tem o mesmo prazo de conservação que o CIVA 52.º |
| (b) Diploma errado | 65 | Ver abaixo |
| (c) Artigo vizinho no diploma certo | 6 | O 1.º (âmbito) em vez do 3.º (exclusões); o 2081.º do Código Civil em vez do 2080.º… |
| (d) Sem resposta na lei | 0 | |
| (e) Diploma fora do acervo | 0 | |

Aceitando as duas alternativas válidas, o artigo certo em 1.º nas reais passa de 63/136 (46%) para 65/136 (48%): o problema é mesmo a pesquisa, não o conjunto de avaliação.

Os 65 "diploma errado" são de quatro tipos:

| Tipo | n | Exemplo | Onde está o artigo certo |
|---|--:|---|---|
| **Diploma antigo, substituído** | 30 | O Código do Trabalho de 2003 (Lei n.º 99/2003, "parcialmente em vigor" no DRE, sem nota de revogação nos artigos) em 24; a Lei n.º 35/2004 que o regulamentava; a Lei n.º 4/84 (maternidade); o texto original do CIVA (DL 394-B/84, em blocos) | 2.º a 6.º lugar em 23, fora dos 10 em 7 |
| **Regime especial ou paralelo** | 16 | A Lei Geral do Trabalho em Funções Públicas, o Estatuto dos Profissionais da Cultura, o acordo com os EUA nos Açores (RAR n.º 24/85), o serviço doméstico (DL 235/92), regulamentos internos de organismos | 2.º a 5.º em 14 |
| **Outro tema** | 15 | Comunicação de contratos de arrendamento à AT (CIS 60.º) dá o NRAU; faltas por falecimento dá a licença de paternidade de 1995 | Fora dos 10 em todos os 15 |
| **Lei de alteração ou de autorização** | 4 | "O artigo 3.º do DL 198/2012 passa a ter a seguinte redação: …" na Lei n.º 12/2022; a autorização legislativa do CIMI (Lei n.º 26/2003) | 2.º a 5.º |

- Em 21 dos 65 o primeiro resultado tem **a mesma regra** (o CT de 2003 diz também 22 dias úteis de férias) e em 15 dá **uma resposta diferente ou não responde** (o CT de 2003 permitia contratos a termo de três anos, não dois; a Lei n.º 4/84 dizia 98 dias de puérpera, não 120). O reranker dá pontuações quase iguais a textos quase iguais; o desempate tem de vir de saber qual é a lei atual.
- Os dados do DRE não chegam para isso: a Lei n.º 99/2003 e a Lei n.º 4/84 estão "em vigor" ou "parcialmente em vigor", e o texto original do CIVA (DL 394-B/84) "em vigor". A revogação com exceções (o art. 12.º da Lei n.º 7/2009 revoga a Lei n.º 99/2003 "com exceção dos artigos…") é tratada na fase 2.
- Os 15 "outro tema" são o único grupo em que a pesquisa nem traz o artigo certo; a pesquisa por diploma com embeddings (abaixo) foi tentada para eles e não resultou.

### Mais candidatos de recuperação: códigos principais e grafia antiga

No diagnóstico, 17 das 136 reais nem chegavam aos candidatos do reranker. Quase todas são de códigos grandes (Trabalho, IRS, IVA, Civil) que a pergunta não nomeia: o BM25 em todo o acervo põe à frente portarias e regulamentos pequenos que repetem as palavras, e o artigo certo fica na posição 800 a 12 000. Duas alterações:

- **Canal dos códigos principais** (`Pesquisa.codigos_principais`): o BM25 corre também só nos 54 códigos e leis gerais com 60 ou mais artigos, e os 15 melhores entram no reranker além dos 30 de antes (o reranker lê até 45). Custa cerca de 2 s por pergunta.
- **Grafia anterior ao Acordo de 1990** (`rag.texto`): "nocturno", "acção", "excepção" e "óptimo" passam ao mesmo termo que "noturno", "ação", "exceção" e "ótimo", dos dois lados. Os textos consolidados do DRE ainda têm a grafia antiga e as perguntas não. Muda o método dos termos: é preciso reconstruir o índice (9 min).

| Reais (136), limiar 3, sem LLM | Partida (`main`) | Com as duas alterações |
|---|--:|--:|
| Artigo certo em 1.º | 56% | 58% |
| Nos 5 primeiros | 78% | 84% |
| Nos 10 primeiros | 80% | 86% |
| "Não sei" | 21% | 21% |
| Fiabilidade | 65% (69/106) | 65% (70/108) |

O ganho está na recuperação (+9 perguntas nos 10 primeiros), que é o que o passo do LLM usa. Nas outras 457 perguntas, com as mesmas alterações: literais 225/250 no 1.º (partida de antes da correção das revogações: 226), temporais 96/102 (96), revogadas 55/55 (55); das 16 perguntas que mudaram de posição contra aquela partida, 15 têm a mesma posição no código do `main` (a diferença vem da correção das revogações) e uma, lit-019, passou de 1.º para 2.º por causa das alterações. A medição completa das 593 perguntas no código do `main`, para uma comparação exata, não foi feita.

### Pesquisa por diplomas com embeddings: não resultou

Tentou-se atacar o diploma errado procurando primeiro o diploma: um vetor (modelo denso multilingue MiniLM) por diploma em vigor (título, sumário, nomes dos anexos), por anexo com nome e por cada 25 epígrafes (274 mil vetores, 1 h 50 em CPU), os 15 diplomas mais próximos da pergunta e o BM25 de artigos só dentro deles, junto aos candidatos do reranker. Medido nas 136 reais, sobre o índice com o tratamento dos artigos revogados (partida: 56% no 1.º, fiabilidade 65% com limiar 3):

| Configuração | Artigo certo em 1.º | Nos 5 primeiros | "Não sei" | Fiabilidade (limiar 3) |
|---|--:|--:|--:|--:|
| Partida (`cruzado`) | 56% | 78% | 21% | 65% |
| + 15 diplomas candidatos | 55% | 78% | 21% | 64% (69/107) |

- Das 15 perguntas "outro tema" (o artigo certo nem entra nos 10 primeiros), só uma passou a entrar, e nenhuma ficou em 1.º. O embedding de título e sumário de um diploma não diz do que tratam os artigos (a Lei do Imposto do Selo não menciona senhorios), e as epígrafes de 25 artigos diluem-se.
- O código foi revertido; o diagnóstico acima continua válido. Não se mediu com o LLM (não há `ANTHROPIC_API_KEY`).
- Uma experiência à parte, sem ficar no código, somou ao resultado do reranker uma penalização aos anexos duplicados de códigos, aos artigos de leis de alteração ("passa a ter a seguinte redação") e ao texto original de diplomas alterados: subiu as reais para 58% (fiabilidade 69%). Foi desenhada depois de ver as falhas das mesmas 136 perguntas e o ganho é de três perguntas, por isso **não** ficou: precisa de perguntas novas (frente C) e de medir as literais, temporais e revogadas antes de entrar.

## Próximos passos

Por ordem de ganho esperado:

1. **Passo do LLM** com chave: medir a fiabilidade das respostas escritas e o "não sei" nas perguntas fora do âmbito, que a pesquisa sozinha não reconhece.
2. **Pesquisa semântica nas reais**: embeddings só dos diplomas em vigor consolidados e dos códigos (uma fração do acervo, cerca de 1 h a indexar), juntos ao BM25, para que o artigo certo chegue aos candidatos; e expandir temas comuns para o código (IVA → CIVA, IMI → CIMI).
3. **Perguntas sobre diplomas alterados sem consolidação** no conjunto de avaliação, para medir o risco principal do plano, que hoje fica de fora.
4. **Trocar `fontes.ler_artigos` pelo parser da fase 3** e reconstruir o índice (5 min); medir outra vez.
5. **Velocidade**: o reranker leva 7 a 8 s por pergunta em CPU; para uso real, um reranker mais pequeno, menos candidatos ou GPU.
