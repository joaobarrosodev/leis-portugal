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

A IA que escreve a resposta e reescreve a pergunta escolhe-se em `rag/provedores.py`: Claude (por omissão, `claude-opus-5-5`, **o único medido**), OpenAI ou Gemini (`RAG_PROVEDOR`, `RAG_MODELO` e a chave de cada uma). As instruções, o formato JSON e o modo estrito são os mesmos para as três; com outra IA ou modelo, cada resposta diz que a qualidade não foi medida. A página (`./perguntar --web`, `rag/web.py`) e a aplicação para Mac e Windows (`app/`) usam o mesmo caminho.

Para fazer perguntas uma a uma (por exemplo, para alguém testar), na raiz do repositório:

```bash
./perguntar
```

Na primeira vez prepara tudo: o `.venv` com o extra `rag`, o export e o índice (~5 min). Depois abre as perguntas, com o reranker e o limiar 3. Mostra o artigo mais provável com os avisos e os outros artigos encontrados, e pergunta se está certo e, se não, o que se esperava. Tudo fica em `rag/resultados/privado/perguntas-testadas.jsonl` (fora do git), para as perguntas que falham entrarem no conjunto de avaliação. `./perguntar "a pergunta"` faz uma só; `./perguntar --reconstruir` refaz o export e o índice (por exemplo, depois de atualizar o acervo).

- `rag.indice` precisa de `exports/leis-portugal.sqlite` (na raiz, ou na pasta principal quando se corre numa worktree; ou `RAG_EXPORT`). `--amostra N` faz um índice só com os diplomas da avaliação e mais N, em segundos.
- Os regulamentos, deliberações, acordos coletivos de trabalho, editais e declarações que a recolha em massa da 2.ª Série trouxe a partir de 12/11/2026 (~100 mil) ficam fora do índice por omissão, porque ainda não se mediu se ajudam a pesquisa ou só a enchem de atos administrativos. Os destes tipos recolhidos antes, os que um diploma do acervo cita ou altera, continuam. Para os incluir: `python -m rag.indice --com-serie-ii` (o critério é `fora_por_omissao` em `indice.py`: o tipo e a data `retrieved_at` do registo).
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

**Teste de 530 perguntas** (29/10/2026, `teste500`): 281 reais, 100 compostas, 99 de texto alterado, 50 de premissa errada e 80 sem resposta. Quatro juízes por resposta (dois rigorosos, um cético, um sem a referência), todos às cegas; certa só se os quatro dizem correta e fundamentada. As 145 reais novas e todas as outras nunca serviram para afinar.

| Tipo | n | "Não sei" | Fiabilidade (certas/respondidas) | Limite inferior 95% |
|---|--:|--:|--:|--:|
| Reais | 281 | 36% | **95% (171/180)** | 91% |
| Premissa errada | 50 | 16% | 90% (38/42) | 78% |
| Compostas | 100 | 23% | 75% (58/77) | 65% |
| Texto alterado | 99 | 10% | **60% (53/89)** | 49% |
| Sem resposta | 80 | 98% | recusa 78 de 80 | — |
| Total com resposta | 530 | 27% | **82% (320/388)** | **78%** |

O que isto diz, sem arredondar a favor:
- **Meta não cumprida.** A fiabilidade total é 82% (pior caso 78%) e o "não sei" é 27%. As metas eram 95% e 15%.
- **Texto alterado é o pior ponto (60%).** O sistema responde com o texto original de um diploma alterado, que os artigos avisam não ter versão consolidada, e a referência segue a redação alterada. Só se resolve consolidando o texto em vigor (frente B).
- **Compostas (75%).** As 19 falhas são respostas incompletas: a pergunta pede dois artigos e um deles não chega ao contexto do LLM.
- **Reais: 95% mas com 36% de "não sei".** Nas 281 reais, o artigo certo está em 1.º em 42% e nos 10 primeiros em 77%, bem abaixo das 136 afinadas (58%/86%): as 136 estavam inflacionadas por afinação.
- **O juiz sem referência é demasiado brando** (deu 99% de corretas onde os outros apanharam erros); só vale como controlo, e o veredicto exige que os quatro concordem.
- Os juízes são todos o mesmo modelo: falta a revisão de um jurista numa amostra.

**Modo estrito** (05/11/2026, mesmas 530 perguntas, respostas já julgadas, medido e não simulado): o sistema recusa quando o artigo citado traz o aviso "Texto original; alterado por…" ou quando a própria resposta diz que a norma não está nos artigos dados.

| Tipo | n | "Não sei" | Fiabilidade (certas/respondidas) | Limite inferior 95% |
|---|--:|--:|--:|--:|
| Reais | 281 | 42% | **98% (158/162)** | 94% |
| Premissa errada | 50 | 26% | 92% (34/37) | 79% |
| Compostas | 100 | 50% | 96% (48/50) | 87% |
| Texto alterado | 99 | 100% | recusa todas | — |
| Sem resposta | 80 | 98% | recusa 78 de 80 | — |
| Total | 530 | 53% | **96% (240/249)** | **93%** |

A fiabilidade sobe de 82% para 96% (pior caso 78% para 93%), mas à custa de responder só a 249 de 530 (o "não sei" passa de 27% para 53%). É a troca decidida: certas primeiro, menos "não sei" depois. Ressalvas: os juízes são o mesmo modelo, e a recusa em texto alterado não resolve nada, só esconde o problema até haver texto consolidado.

**Reescrita da pergunta em consulta jurídica** (06/11/2026, as 281 coloquiais, resposta escrita e quatro juízes às cegas, modo estrito): um LLM reescreve a pergunta do utilizador numa consulta jurídica, a pesquisa usa só a consulta, e o LLM que responde e os juízes veem a pergunta original. Exige um passo de LLM antes da pesquisa (`rag.passo_llm --reescrita`).

| Medida | Pergunta original | Com consulta jurídica |
|---|--:|--:|
| Artigo certo em 1.º | 21% | **59%** |
| Artigo certo nos 10 primeiros | 40% | **91%** |
| "Não sei" | 89% | **19%** |
| Respostas dadas certas (juízes) | 94% (30/32), limite inferior 80% | **95% (215/227), limite inferior 91%** |
| Perguntas com resposta certa | 11% (30/281) | **76% (215/281)** |

Ressalvas: o reescritor é o mesmo modelo que responde e que julga, e conhece a lei por si, o que ajuda a pesquisa e pode ajudar os juízes a concordar; os 4 juízes dão mais certas (215) do que o critério brando de palavras (181), o que sugere que o critério de palavras subestima respostas certas, mas também que o conjunto de juízes pode ser brando; sem revisão de jurista. A medição de 94 perguntas que antecedeu esta (só pesquisa) dava 58% de artigo em 1.º e a de 281 dá 59%: coerentes. Falta medir o efeito nos outros tipos (compostas, texto alterado, premissa errada, sem resposta) para ver se a reescrita não faz o sistema responder onde devia recusar.

**Reescrita nos outros tipos** (09/11/2026, `teste-reescrito`: as 530 perguntas do teste, modo estrito, quatro juízes às cegas, mesma reescrita de `rag/REESCRITA.md`):

| Tipo | n | "Não sei" sem → com reescrita | Fiabilidade | Limite inferior 95% |
|---|--:|--:|--:|--:|
| Reais | 281 | 42% → **16%** | **97% (229/237)** | 93% |
| Compostas | 100 | 50% → **30%** | 96% (67/70) | 88% |
| Premissa errada | 50 | 26% → **12%** | 91% (40/44) | 79% |
| Sem resposta | 80 | recusa 78 de 80 | — | — |
| Texto alterado | 99 | recusa todas (modo estrito) | — | — |
| Total | 530 | 53% → **34%** | **96% (336/351)** | **93%** |

A reescrita não baixa a fiabilidade (96%, pior caso 93%, igual ao modo estrito sem reescrita) e faz o sistema responder a 351 perguntas em vez de 249. Nas reais, o artigo certo passa a estar em 1.º em 68% (antes 42%) e 81% das perguntas recebem resposta certa (antes 56%). Nas de premissa errada responde a mais 7 e continua a corrigir a premissa em 91% delas. Não fez o sistema responder onde devia recusar: as sem resposta continuam em 78 de 80. Ressalvas iguais às das coloquiais: reescritor, respondedor e juízes são o mesmo modelo; sem jurista. As literais, temporais e revogadas (sintéticas) não foram medidas com reescrita.

**Reescrita nas sintéticas** (10/11/2026, `sinteticas-reescrito`: as 407 literais, temporais e revogadas, mesmo índice e mesma reescrita de `rag/REESCRITA.md`, modo estrito, quatro juízes às cegas). O receio era a reescrita perder a referência explícita ao diploma ou artigo e piorar estas perguntas; não aconteceu: artigo certo em 1.º em 94% e nos 10 primeiros em 100%, "não sei" 1%.

| Tipo | n | Respondidas | Certas (palavras) | Certas (juízes) | Fiabilidade | Limite inferior 95% |
|---|--:|--:|--:|--:|--:|--:|
| Literais | 250 | 249 | 237 | 248 | 100% (248/249) | 98% |
| Temporais | 102 | 98 | 89 | 98 | 100% (98/98) | 96% |
| Revogadas | 55 | 55 | 55 | 55 | 100% (55/55) | 93% |
| Total | 407 | 402 | 381 (95%) | 401 | **100% (401/402)** | **99%** |

Pelo critério das palavras fica igual ao que era sem reescrita (95% contra 94%). Os juízes dão 401 certas; nas 21 em que discordam das palavras, uma amostra de 6 lida à mão dá razão aos juízes (diferenças de formatação de números e moeda, frases mais completas que a referência). Ressalvas: os juízes são o mesmo modelo e deram só 1 "incompleta" em 402, o que é pouco escrutínio; as sintéticas são perguntas fáceis por construção (citam o diploma); e houve um incidente de contaminação entre dois juízes que partilharam um ficheiro temporário, resolvido com a repetição dos 14 lotes afetados do juiz b por um juiz novo em pasta própria.

**Texto alterado com o acervo consolidado** (09/11/2026, `texto-alterado-novo`: as 99 perguntas de texto alterado, índice reconstruído com os 1.056 diplomas que a frente B pôs em vigor em `data/`, modo estrito, sem reescrita, quatro juízes às cegas): o texto em vigor chega ao 1.º lugar em 66% (antes 43%, quando só existia o original com aviso); o modo estrito deixa passar 41 respostas em vez de zero e os quatro juízes dão as **41 como certas** (limite inferior 91%); "não sei" 59%. As 58 recusadas são, na maioria, diplomas cujo artigo ainda traz o aviso "Texto original; alterado por…" (54 das 99 mensagens): só se resolvem com mais consolidação. Ressalva: 41 respostas é pouco para um intervalo apertado, e os juízes são o mesmo modelo.

**Reescrita no sistema** (10/11/2026, `rag/reescrita.py`): com `ANTHROPIC_API_KEY`, `rag.perguntar` e `rag.avaliar` reescrevem a pergunta numa consulta jurídica antes da pesquisa (regras em `rag/REESCRITA.md`, as mesmas das medições; modelo `RAG_MODELO`, esforço baixo, uma chamada curta). A pesquisa usa só a consulta; o LLM que responde vê a pergunta original. `--sem-reescrita` desliga; sem chave, ou se a chamada falhar, a pesquisa usa a pergunta tal como está. `rag.perguntar` mostra "Pesquisa por: …" e guarda a consulta em `pesquisa_por` no registo. Não foi medido com a API (não há chave): a medição acima foi com sessões do Claude a seguir as mesmas regras.

**Texto alterado com 2.329 consolidados** (12/11/2026, `texto-alterado-2323`: as mesmas 99 perguntas, índice de 12/11, modo estrito, sem reescrita, quatro juízes às cegas): texto em vigor em 1.º lugar em 67% (66% a 09/11), "não sei" 57% (59%), **42 de 43 respostas certas** (limite inferior 88%). A errada (alt-096, DL 4/93) responde com o artigo sobre quando as taxas são devidas, não com o prazo e a forma de pagamento que a pergunta pede; o juiz sem referência deu-a como certa e os três com referência como errada. Os 1.273 diplomas consolidados entre 09/11 e 12/11 quase não tocam nestas 99 perguntas, por isso o ganho é pequeno.

**Direito da União Europeia** (12/11/2026, `ue-reescrito`: as 167 perguntas de `avaliacao/perguntas-ue.jsonl`, 123 literais, 19 de atos revogados e 25 sem resposta, tiradas ao acaso dos atos da UE em vigor do acervo; índice de 12/11 com os 18 mil atos da UE recolhidos nesse dia; mesma reescrita, modo estrito, quatro juízes às cegas):

| Tipo | n | Artigo certo em 1.º | "Não sei" | Fiabilidade (juízes) | Limite inferior 95% |
|---|--:|--:|--:|--:|--:|
| Literais | 123 | 98% | 26% | 100% (91/91) | 96% |
| Revogadas | 19 | 89% | 37% | 100% (12/12) | 76% |
| Sem resposta | 25 | — | recusa 25 de 25 | — | — |
| Total com resposta | 142 | 96% | 27% | **100% (103/103)** | **96%** |

Quando responde a uma pergunta sobre um ato da UE, acerta em pelo menos 96% (pior caso, 95% de confiança). Responde a 73% das que têm resposta. A pesquisa encontra o artigo certo em 1.º lugar em 98% das literais; os 26% de "não sei" vêm do limiar do reranker (3,0), que nas perguntas da UE deixa de fora artigos certos. As revogadas certas pelos juízes e não pelo critério de palavras (7 de 12) foram lidas à mão: dizem que o ato foi revogado e por qual, como a referência, mas com a data de adoção do revogador em vez da de publicação. Ressalvas: as perguntas citam o ato (são "bem feitas", como as sintéticas de Portugal); 76 perguntas sobre a data de entrada em vigor ou de aplicação foram retiradas por serem triviais; os juízes são o mesmo modelo e não deram nenhum erro em 103, o que é pouco escrutínio; sem jurista.

**UE, depois de corrigir a procura dos atos citados** (12/11/2026, `ue-reescrito-2`): 39 dos 42 "não sei" acima vinham de uma regra e não do limiar. O índice guarda os atos da UE como "ano/número" ("1994/631", "2025/2180"), mas a citação extraída da pergunta saía "631/94" ou "2180/2025"; o sistema dava o ato como "não está no acervo" e recusava, mesmo com o artigo certo em 1.º lugar (35 dos 39). `Pesquisa.diplomas` passa a procurar as formas ano/número possíveis de um regulamento, diretiva ou decisão (`_numeros_ue`, com teste). Medidas de novo as 64 perguntas afetadas (as 39 e as 25 sem resposta, porque 12 destas citam um ato que existe e passava a ser encontrado):

| Tipo | n | "Não sei" | Fiabilidade (juízes) | Limite inferior 95% |
|---|--:|--:|--:|--:|
| Literais | 123 | 0% | 100% (123/123) | 97% |
| Revogadas | 19 | 0% | 100% (19/19) | 83% |
| Sem resposta | 25 | recusa 25 de 25 | — | — |
| Total com resposta | 142 | **0%** | **100% (142/142)** | **97%** |

As 103 respostas da medição anterior não mudam (as perguntas não estão entre as 64) e somam-se às 39 novas. As 7 revogadas que o critério de palavras dá como erradas foram lidas à mão: dizem a revogação e o ato revogador, e explicam também o que a norma dizia. Das perguntas de Portugal, só 2 citam atos da UE: as medições de Portugal não mudam de forma relevante. Ressalvas iguais às de cima: perguntas que citam o ato, juízes do mesmo modelo, sem jurista.

**Perguntas como as escreve um utilizador** (30/10/2026, `coloquial`): as 281 reais reescritas, com a mesma resposta certa, em três perfis (pessoa de 65 anos, jovem de 22, pessoa aflita com um caso): pouco contexto, sem termos jurídicos, sem números de artigos. Quatro juízes às cegas.

| Medida | Reais bem escritas | Mesmas, coloquiais |
|---|--:|--:|
| Artigo certo em 1.º | 42% | **21%** |
| Artigo certo nos 10 primeiros | 77% | **40%** |
| "Não sei" | 36% | **89%** |
| Respostas dadas certas (juízes) | 95% (171/180) | 94% (30/32), limite inferior 80% |
| Perguntas com resposta certa | 61% (171/281) | **11% (30/281)** |

A qualidade da resposta, quando a há, mantém-se; o que cai é quantas perguntas chegam a ter resposta. A pesquisa deixa de encontrar o artigo e o reranker dá ao melhor uma pontuação à volta de 0 (mediana −0,1; o limiar é 3), por isso o sistema recusa quase tudo. Para um utilizador normal isto é o número que conta: só cerca de 1 em 9 perguntas recebe uma resposta certa. Melhorar a pesquisa para perguntas vagas é a prioridade.

**Segundo travão** (`travao.py`): um segundo modelo julga, às cegas, se cada resposta escrita se aguenta nos artigos dados e responde à pergunta. Nas 99 respostas dadas (98 reais e 1 sem resposta) aprovou todas, por isso apanhou 0 das 11 erradas e não perdeu nenhuma certa. Dos 10 erros das reais, 6 têm o artigo certo em 1.º lugar (a resposta escrita difere da de referência no critério de 80% das palavras: o erro pode estar na métrica) e 4 são de pesquisa (diploma ou artigo errado). Ou seja, o erro não é o LLM inventar, e um travão que só confere a resposta contra os artigos não o apanha. Os 6 ficam para revisão às cegas por pessoa ou outro modelo antes de se chamar erro.

**Limiar do reranker com LLM: 3 → 1** (12/11/2026, `limiar1`). Com o limiar 3, o sistema recusava antes do LLM quando o melhor artigo tinha menos de 3 pontos. Nas recusas com pontuação entre 1 e 3, o artigo certo estava nos 10 primeiros em 45 de 61. Mediram-se de novo as 85 perguntas do teste e das coloquiais que caíam nessa faixa, 24 delas sem resposta, com limiar 1, a mesma reescrita, modo estrito e quatro juízes às cegas.

| Tipo | n | Respondidas | Certas (juízes) |
|---|--:|--:|--:|
| Reais | 21 | 15 | 14 |
| Coloquiais | 32 | 22 | 22 |
| Compostas | 3 | 3 | 3 |
| Premissa errada | 4 | 2 | 1 |
| Texto alterado | 1 | 1 | 1 |
| Com resposta (total) | 61 | 43 | **41 (95%, limite inferior 85%)** |
| Sem resposta | 24 | 4 | — |

As 4 "sem resposta" a que respondeu perguntam pela "lei portuguesa" sobre matérias que são de regulamentos da UE (voos, tempos de condução, roaming, comissões dos cartões). Foram escritas antes de a UE estar no acervo. O sistema corrigiu a premissa e citou o regulamento certo; não se contam como certas nem como erradas. As 2 erradas: o artigo 29.º do Código do IVA chegou cortado e faltava a norma pedida; numa de premissa errada, a resposta não a corrigiu.

No conjunto, somando às respostas que já havia:

| Conjunto | "Não sei" | Certas nas respondidas | Limite inferior 95% |
|---|--:|--:|--:|
| Teste (450 com resposta) | 22% → **17%** | 96% → **95% (355/372)** | 93% |
| Coloquiais (281) | 19% → **11%** | 95% → **95% (237/249)** | 92% |

Passa a ser o limiar com LLM (`LIMIAR_COM_LLM = 1.0` em `resposta.py`, também por omissão no `passo_llm` e no `perguntar` com LLM). Sem LLM, o artigo do topo é a resposta, e o limiar fica em 3. Ressalvas: 43 respostas é pouco para um intervalo apertado, os juízes são o mesmo modelo, e não há revisão de jurista.

**Tirar o aviso "texto original" quando a triagem diz "sem alteração textual": não resultou** (12/11/2026). 47 das 56 recusas do texto alterado vêm do aviso "Texto original; alterado por…, sem versão consolidada"; 13 dos 35 diplomas em causa têm todos os alteradores dados pela triagem como "sem alteração textual". Antes de tirar o aviso nesses casos, um verificador às cegas leu 80 pares original–alterador ao acaso, com 10 a 27 por motivo da triagem (`consolidacao/verificacao/triagem-sem-alteracao-amostra-80.jsonl`).

O resultado foi 11 alteram mesmo o texto, 11 em dúvida e 58 não alteram:
- **Os erros:** quadros de pessoal alterados "de acordo com o quadro anexo", áreas de zonas de caça, um "n.º 1.º passa a ter a seguinte redacção", uma portaria revogada por inteiro, e os Estatutos da Universidade de Coimbra.
- **Por motivo da triagem:** "cita o original mas não lhe dá instruções" teve 8 em 24; "só aparece numa lista" teve 2 em 25; "não menciona o original" teve 0 em 22, mas as 3 dúvidas eram mudanças reais a anexos.

Com 14% a 28% de erro, tirar o aviso faria o sistema responder com texto desatualizado, por isso o aviso fica. O que se aproveita é para os dados: a triagem deixa passar alterações reais, sobretudo em portarias que mexem em quadros e zonas de caça.

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

## Duas respostas: a lei e a jurisprudência

A resposta da lei não mudou: a pesquisa, o reranker, o LLM e o "não sei" são os mesmos. O que muda:

- **Aviso na resposta da lei.** Se o Tribunal Constitucional declarou o artigo inconstitucional com força obrigatória geral até à data da pergunta, o artigo leva o aviso, como os de revogação, e o LLM recebe-o com o texto. Se o texto do artigo é posterior ao acórdão, o aviso diz que a declaração foi sobre uma redação anterior. É o caso do artigo 4.º da Lei n.º 32/2008, declarado pelo Acórdão n.º 268/2022 e alterado pela Lei n.º 18/2024.
- **Segunda resposta, separada.** São os acórdãos do TC que julgaram os artigos citados, até à data da pergunta. Primeiro vêm as decisões com força obrigatória geral (declarar ou recusar declarar), depois os casos concretos, do mais recente para o mais antigo: cinco por artigo e a contagem dos restantes. Vem dos dados (`rag/jurisprudencia.py`, a partir da decisão de cada acórdão), não do LLM, que continua instruído a não responder sobre jurisprudência; por isso não inventa acórdãos. Mostra o número, a data, o sentido e a ligação para o site do Tribunal, não o texto do acórdão.

O artigo de um código republicado noutro diploma (o Código Penal na Lei n.º 59/2007) encontra os acórdãos pelo nome do anexo.

Medido em 12/11/2026: com e sem os dados do TC, a avaliação BM25 dá o mesmo resumo nas 736 perguntas, porque o aviso entra depois da ordenação. Nenhuma pergunta da avaliação cai num artigo declarado inconstitucional, e 23 passam a ter a segunda resposta. A extração dos acórdãos tem 90 % de precisão e 88 % de cobertura, medidas às cegas numa amostra que o extrator não tinha visto (ver o [README](../README.md)); a segunda resposta pode por isso ter falhas, e não entra na fiabilidade da resposta da lei.

## Prova de conceito no browser (12/11/2026)

A pergunta: o sistema pode correr todo no browser, num site do GitHub Pages, sem instalar nada? O índice (4,1 GB) não cabe no GitHub Pages (1 GB por site, 100 MB por ficheiro). Teria de ficar noutro alojamento e ser lido aos bocados, com pedidos HTTP Range, só nas páginas de que cada pesquisa precisa. Código e instruções em [`navegador/`](navegador/README.md).

**Como se mediu.** 50 perguntas de `avaliacao/perguntas.jsonl`, de todos os tipos. A pesquisa correu com um reranker falso, para seguir o mesmo caminho que com o reranker, e cada consulta SQL ficou gravada. Depois, as consultas repetiram-se sobre o índice através de uma VFS do SQLite que conta cada leitura. Cada página fora da cache seria um pedido. Páginas seguidas contam como um só pedido, que é o melhor caso.

| Medida | Mediana | p90 | Viável se |
|---|--:|--:|--:|
| Consultas SQL por pergunta | 503 | 767 | — |
| Tempo no disco local (sem rede) | 2,7 s | 10,5 s | — |
| Índice lido por pergunta, cache vazia | **151 MB** | 165 MB | ≤ 30 MB |
| Pedidos por pergunta, cache vazia (melhor caso) | **36 395** | 38 059 | — |
| Índice novo por pergunta, cache aquecida pelas anteriores | 8,3 MB | 18,3 MB | ≤ 30 MB |
| Cache do browser ao fim de 50 perguntas | 654 MB | | |
| Arranque (lista dos códigos), uma vez | 321 consultas, 17 s no disco | | |

**Para onde vão os bytes**, em 6 perguntas:

| Consulta | Parte das leituras | MB por pergunta |
|---|--:|--:|
| Diplomas citados (`documentos` por tipo e número, sem índice: lê a tabela toda) | 51% | 70 |
| BM25 (`pedacos_fts MATCH`) | 13% | 18 |
| Frequência de cada termo (`fts5vocab`) | 13% | 17 |
| Datas, diploma e notas dos candidatos (`_info`) | 10% | 14 |
| Artigos em vigor de cada código candidato (`count(*)`) | 9% | 12 |

**O resto do caminho**
- **Reranker:** são 571 MB a descarregar da primeira vez (bge-reranker-v2-m3 int8). Não foi corrido no browser, por isso o tempo não está medido.
- **Chamadas às IAs:** feitas de uma página de outro site, com chaves falsas, as três respostas de erro chegaram à página. Logo, aceitam chamadas diretas do browser. O Claude só as aceita com o cabeçalho `anthropic-dangerous-direct-browser-access: true` (sem ele, o browser bloqueia); a OpenAI e a Gemini aceitam-nas sem cabeçalho especial.

**Conclusão: com o índice de hoje, não é viável.**
- Com a cache vazia, cada pergunta pede cerca de 150 MB em dezenas de milhares de pedidos. Mesmo em paralelo, seriam minutos por pergunta.
- Com a cache aquecida, ainda são cerca de 8 MB e milhares de pedidos.
- Não se mediu a pesquisa num browser real: com estes números, não mudaria a conclusão.
- Três das cinco consultas mais pesadas corrigem-se no índice:
  - um índice em `documentos(tipo, numero)`;
  - uma tabela pequena com a frequência de cada termo;
  - as contagens dos códigos calculadas de antemão.
- Mesmo assim, estima-se que fiquem cerca de 35 a 40 MB por pergunta com a cache vazia, e milhares de pedidos. Esta estimativa não foi medida.

Para correr no browser seria preciso um índice próprio, desenhado para ser lido pela rede, mais os 571 MB do reranker, e depois medir a qualidade de novo. É um projeto à parte.

**Recomendação**
- Para o sistema completo, com a qualidade medida: a aplicação instalável. O site no GitHub Pages serve para a descarregar.
- A versão no browser fica para depois, se o índice próprio for desenhado e medido.

## Deltas do índice: iguais a construir de raiz (13/11/2026)

A aplicação atualiza o índice com deltas por diploma (`rag/dados.py`), em vez de descarregar outra vez a versão completa. Para isso ser seguro, aplicar um delta tem de dar o mesmo índice que construí-lo do zero.

Mediu-se no índice inteiro (`rag/navegador/equivalencia.py`):
1. B é o índice verdadeiro.
2. A é B sem 2.108 diplomas: os 108 que aparecem nos resultados das 50 perguntas de `rag/navegador/` e mais 2.000 ao acaso. Tiraram-se com o próprio código dos deltas.
3. Gerou-se o delta de A para B, aplicou-se a A e comparou-se o resultado com B.

| Medida | Resultado |
|---|--:|
| Diplomas diferentes de B (impressão digital de cada um, em 265.805) | **0** |
| Pesquisa sem reranker, 10 primeiros por diploma e artigo | **iguais nas 50 perguntas** |
| BM25, 100 primeiros com a pontuação | iguais em 48 de 50 |
| Delta de 2.108 diplomas (25.976 pedaços) | 50,8 MB; **9,9 MB comprimido** |
| Tempo para gerar e aplicar o delta | ~5 min e ~3 min, neste computador |

Nas 2 perguntas em que o BM25 difere, os 100 resultados e as pontuações são os mesmos; só muda a ordem entre artigos com exatamente a mesma pontuação. Os empates ficam pela ordem do id, e os diplomas reinseridos têm ids novos. Os 10 primeiros, que são o que segue para o reranker e para a resposta, são iguais nas 50 perguntas.

A versão completa de 12/11/2026 tem 1,35 GB comprimida (4,35 GB sem comprimir). Por esta medição, um delta de 2 mil diplomas é cerca de 0,7% da versão completa. O tamanho de um delta numa semana normal ainda não foi medido: só se sabe com duas publicações seguidas.

## Próximos passos

Por ordem de ganho esperado:

1. **Passo do LLM** com chave: medir a fiabilidade das respostas escritas e o "não sei" nas perguntas fora do âmbito, que a pesquisa sozinha não reconhece.
2. **Pesquisa semântica nas reais**: embeddings só dos diplomas em vigor consolidados e dos códigos (uma fração do acervo, cerca de 1 h a indexar), juntos ao BM25, para que o artigo certo chegue aos candidatos; e expandir temas comuns para o código (IVA → CIVA, IMI → CIMI).
3. **Perguntas sobre diplomas alterados sem consolidação** no conjunto de avaliação, para medir o risco principal do plano, que hoje fica de fora.
4. **Trocar `fontes.ler_artigos` pelo parser da fase 3** e reconstruir o índice (5 min); medir outra vez.
5. **Velocidade**: o reranker leva 7 a 8 s por pergunta em CPU; para uso real, um reranker mais pequeno, menos candidatos ou GPU.

### Jurisprudência (estado em 12/11/2026)

1. **Acórdãos do TC de 1983 a 2015.** Recolhidos e no main (12/11/2026): 29.392 dos 29.405 acórdãos de 1983 a 2026; os 13 que faltam são lacunas do site, com o motivo em `reports/tc_failures.jsonl` (o 652/2021 incluído). O `normas-julgadas.jsonl` foi refeito com todos os anos (13/11/2026): 5.773 alíneas, 371 declarações com força obrigatória geral (eram 64). Medido às cegas antes de 2016: 78 % de precisão e 82 % de cobertura das normas (90 % e 88 % em 2016–2026); números e erros no README, em "Normas julgadas pelo Tribunal Constitucional". Falta:
   - repetir a avaliação BM25 com os dados novos (o aviso entra em mais respostas) e experimentar as duas respostas com o LLM;
   - os erros que sobram: listas de artigos apanhadas só em parte, diplomas no plural, o CPP de 1929 ligado ao de 1987, regulamentos e editais antigos que o índice não tem;
   - desde 12/11/2026 os acórdãos novos (e as decisões novas da CNPD e as decisões sumárias) entram na atualização diária, mas o `normas-julgadas.jsonl` não se refaz sozinho: o aviso de inconstitucionalidade só apanha um acórdão novo depois de correr `rag.jurisprudencia` outra vez.
2. **Commit da recolha em partes.** As autorizações da CNPD (114.331 anunciadas, perto de 1 GB) e os acórdãos vão inteiros para o git (decisão do utilizador). O primeiro commit (44.274 ficheiros, com as autorizações de 2016 a 2020) passou num só push; o GitHub recusa um push acima de 2 GB, por isso os anos que faltam devem ir em partes. Depois desse commit o repositório ocupa 4,4 GB (`git count-objects -vH`), perto dos 5 GB em que o GitHub avisa, e faltam cerca de 84 mil autorizações: confirmar com o utilizador antes de passar dos 5 GB. Medido depois: as 30.391 autorizações já gravadas ocupam 21 MB no pack (224 MB em texto), por isso as que faltam devem acrescentar 60 a 150 MB, e cada push fica muito abaixo dos 2 GB.
3. **Datas com gralhas no site do TC.** Corrigidas na recolha (`tc.decision_date`, 12/11/2026): eram 85 em 1983–2026, não 30, contando as do ano anterior em acórdãos de janeiro (`2000-01-17` nos 7 a 16/2001). Quando o ano da listagem não é o do número, vale a assinatura do acórdão ("Lisboa, 18 de fevereiro de 2025"): 83 ficaram com a data certa e uma nota, 2 sem data (355/1998 e 58/2004). A guarda de `rag.jurisprudencia` pode ficar: já não apanha nenhuma.
4. **Experimentar as duas respostas com o LLM.** Só foram vistas sem LLM (não havia chave na sessão): ver se o aviso de inconstitucionalidade aparece bem na resposta escrita.
5. **Diplomas citados por um nome que o índice não reconhece.** É a maior parte das falhas da extração (regulamentos, estatutos, a Lei de Organização e Funcionamento dos Tribunais Judiciais…): ficam sem diploma. Resolver pelo sumário ("Aprova o Regulamento…") tendo em conta a data do acórdão, e medir outra vez.
6. **Decisões sumárias do TC.** Recolhidas (13/11/2026, `collect tc --sumarias`, `decisoes-sumarias/`): 5.320 das 5.335 listadas, de 1998 a 2026; ficam fora do `normas-julgadas.jsonl` até se medir a extração nelas. As 15 que faltam são páginas vazias no site (`reports/tc_sumarias_failures.jsonl`).
7. **Mais tarde:** STJ e STA (bases do ITIJ, dgsi.pt) só depois de a segunda resposta estar medida; o TC foi notificado em 12/11/2026, à espera de resposta.
