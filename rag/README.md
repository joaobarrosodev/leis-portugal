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
- Os regulamentos, deliberações, acordos coletivos de trabalho, editais e declarações que a recolha em massa da 2.ª Série trouxe a partir de 12/11/2026 (~90 mil) entram por omissão só pela referência: só aparecem quando a pergunta cita o ato (ver «Tipos novos»). Os destes tipos recolhidos antes, os que um diploma do acervo cita ou altera, entram como os outros. `python -m rag.indice --com-serie-ii` põe-nos também na pesquisa geral, e `--sem-serie-ii` deixa-os de fora (o critério é `fora_por_omissao` em `indice.py`: o tipo e a data `retrieved_at` do registo).
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
- Os juízes são todos o mesmo modelo: falta a revisão de um jurista numa amostra (protocolo em [`avaliacao/juristas/`](../avaliacao/juristas/README.md), ainda sem resultados).

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

Com 14% a 28% de erro, tirar o aviso faria o sistema responder com texto desatualizado, por isso o aviso fica.

**Compostas: o segundo artigo no contexto, só com a pesquisa** (16/11/2026). As 100 compostas foram pesquisadas outra vez no índice de uso de 16/11, sem LLM. Usaram-se as mesmas consultas reescritas do `teste-reescrito` e o reranker cruzado, com os 30 candidatos de sempre. Conta-se uma pergunta quando os dois artigos que ela pede estão nos k primeiros resultados.

| Os dois artigos nos primeiros… | 8 (hoje) | 10 | 12 | 16 | 20 | 30 | 45 |
|---|--:|--:|--:|--:|--:|--:|--:|
| Compostas (100) | 67 | 71 | 73 | **78** | 78 | 79 | 79 |

- **Com 16 artigos no contexto, entram mais 11 perguntas.** Sete delas eram "não sei" no `teste-reescrito` e quatro já estavam certas. Acima de 16 só entra mais uma.
- **As outras 21 falhas vêm da pesquisa, não do contexto.** Nelas, um dos artigos nem chega ao reranker:
  - em 7, não está entre os 100 candidatos do BM25;
  - em 14, está no BM25, mas abaixo dos 30 primeiros, que são os únicos que o reranker lê (6 entre o 31.º e o 45.º lugar, 3 entre o 46.º e o 60.º, 4 entre o 61.º e o 100.º e 1 além do 100.º).

  Destas 21, 16 eram "não sei" no `teste-reescrito`. Com contexto de 16, o máximo que se pode converter é 7 dos 30 "não sei". Os outros 16 só se resolvem na pesquisa, com mais candidatos para o reranker (`maximo`) ou melhores candidatos do BM25.
- **A deduplicação por artigo não tira nenhum artigo certo.** Em 36 perguntas, há cópias do mesmo artigo noutro diploma entre os 16 primeiros: ocupam lugares no contexto, mas não empurram os certos para fora.
- **Custo de 16 artigos.** Com 8 artigos, o prompt tem em média 11,4 mil caracteres (cerca de 1.400 por artigo; mediu-se nos prompts do `teste-reescrito`). Com 16, deve ficar à volta de 22 mil, ainda por medir. A pesquisa com o reranker levou em média 59 s por pergunta, com a máquina carregada por outras tarefas.
- **No código, um contexto maior obriga a mudar dois sítios.** O `passo_llm`, o `avaliar`, o `perguntar` e o `web` pedem 10 resultados à pesquisa. O `importar` do `passo_llm` lê as citações sobre os 8 primeiros (`[:8]` fixo).

Ressalva: os 67 com dois artigos nos 8 não são as 67 certas do `teste-reescrito`, embora o número coincida. O índice mudou desde 09/11 e as certas dependem do LLM e dos juízes. Ainda não foi medido com o LLM se as respostas certas sobem com 16 artigos, nem se as sem resposta e as de premissa errada pioram com mais artigos no contexto. Por isso, o contexto continua em 8 (`ARTIGOS_NO_CONTEXTO`). O que se aproveita é para os dados: a triagem deixa passar alterações reais, sobretudo em portarias que mexem em quadros e zonas de caça.

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

## Tipos novos (16/11/2026)

Medições só da pesquisa, sem LLM: o artigo certo em 1.º lugar (@1) e nos 10 primeiros (@10).

### Índice de 16/11: as traduções da UE e as correções da numeração

O índice de 16/11 tem 267.084 diplomas e 1.576.082 pedaços; o anterior tinha 246.506 e 1.484.508. Entram 1.233 dos 1.244 atos da UE em tradução não oficial e as chaves novas dos artigos («78.º-A», «1.º»).

- **Nas 1.298 perguntas do conjunto completo, a pesquisa fica igual** (`bm25-indice-1611`). Os totais por tipo são os mesmos do índice anterior (`bm25-tc-1983-2026`). Só 3 perguntas mudam de posição, sempre abaixo do 1.º lugar: lit-191, real-027 e col-102.
- **Nenhum ato traduzido aparece em 1.º lugar**, nem nessas 1.298 perguntas nem nas 167 da UE. As traduções ficam no índice: não baralham as perguntas gerais e respondem às perguntas sobre esses atos.
- **UE, só BM25** (`bm25-ue-1611-ref`, índice da noite de 16/11): 94 % @1 e 100 % @10 nas 167 perguntas. A primeira medição (`bm25-ue-1611`, 78 % @1) estava errada: as perguntas ainda tinham a chave do artigo na forma antiga («4º»), que a sessão das gralhas passou a «4.º».
- **Ficaram 11 traduções de fora no índice da tarde, entretanto corrigidas.** O original destes 11 atos só existia em PDF, e o registo guardava o aviso da recolha «o registo liga apenas ao PDF oficial», embora o texto tivesse sido extraído e traduzido. Com esse aviso, o export dava-lhes `text_quality = pdf`. O aviso saiu dos 11 registos e o passo da tradução já não o grava (`eu_translation.translated_record`, com teste). No índice da noite estão as 1.244.

**Aviso nos atos traduzidos.** Quando o artigo citado é de um ato com `version.kind = translation`, a pesquisa junta o aviso `AVISO_TRADUCAO` («Tradução não oficial para português europeu … sem valor jurídico. O ato não tem versão portuguesa oficial.»). O aviso vai para o LLM e para a resposta, como o de revogação. `rag.indice --sem-traducoes` faz um índice sem estes atos, para comparar.

### Aviso de inconstitucionalidade com os acórdãos de 1983 a 2026

Repetida a avaliação BM25 com o `normas-julgadas.jsonl` de 13/11 (371 declarações com força obrigatória geral, eram 64), no índice da manhã de 16/11 (`bm25-tc-1983-2026`):

- **Das 736 perguntas que também estavam na medição de 12/11, só 3 mudam** (cmp-024, alt-095, alt-021), e nenhuma tem aviso do TC. A mudança vem da reconstrução do índice de 13/11, não dos dados do TC.
- **Entram 2 avisos novos, ambos certos:** lit-270 e tmp-048 citam normas que o TC declarou inconstitucionais antes de 2016.
- **Correção:** 17 das 371 declarações são só de ilegalidade, e o aviso dizia «inconstitucional». Passou a dizer «ilegal» quando a alínea fala só de ilegalidade (`_so_ilegalidade`, com teste).

### 2.ª Série do DR

Os atos da 2.ª Série recolhidos desde 12/11 ficavam fora do índice por omissão (`fora_por_omissao`). São regulamentos, editais, deliberações, declarações e acordos coletivos. Para os medir, foram escritas 54 perguntas sobre eles, verificadas às cegas (`avaliacao/perguntas-serie-ii.jsonl`, ver `avaliacao/README.md`), e construído um índice com `--com-serie-ii`.

| Medição | Sem a 2.ª Série | Com a 2.ª Série |
|---|--:|--:|
| 54 perguntas da 2.ª Série, BM25: @1 / @10 | 0 % / 0 % | 65 % / 96 % |
| 54 perguntas da 2.ª Série, reranker: @1 / @10 | — | **89 % / 98 %** |
| 1.298 perguntas, BM25: pior / melhor do que antes | — | 16 / 6 |
| 281 reais, BM25: @1 / @10 | 93 / 200 | 90 / 192 |
| 281 reais, reranker: @1 / @10 | 43 % / 78 % | 41 % / 76 % |

- **Por tipo, BM25 @1:** regulamentos 17/26, editais 9/12, deliberações 5/12, declarações 3/3, acordos coletivos 1/1.
- **Com o reranker, as 54 dão 6 % de «não sei» e 92 % de fiabilidade** (47/51, limiar 3).
- **No BM25, as perguntas que pioram** quase nunca têm um ato da 2.ª Série em 1.º lugar: só 1 das 16. Os atos da 2.ª Série entram nos candidatos e empurram para baixo o artigo certo, sobretudo nas reais.
- **Correção na procura dos diplomas citados:** na 2.ª Série, o número tem às vezes um sufixo («1126/2026 (…)»). `Pesquisa.diplomas` passou a encontrar o número com sufixo (com teste).

**Com o reranker, a 2.ª Série baralha as perguntas reais** (`cruzado-reais-atual` contra `cruzado-reais-com-s2`, limiar 3):
- O artigo certo em 1.º lugar passa de 120 para 115, e nos 10 primeiros de 218 para 214. As certas passam de 101 para 99. Pioram 33 perguntas e melhoram 26.
- Em 12 das 33 que pioram, o 1.º lugar passa a ser um regulamento ou acordo coletivo da 2.ª Série: um regulamento municipal ou de um instituto que fala do mesmo tema (teletrabalho, descanso compensatório, isenção de IMT). Aí a resposta citaria a regra de uma entidade em vez da lei geral, o que engana mais do que um «não sei».

**2.ª Série só pela referência** (hoje a omissão do `rag.indice`). Os atos da 2.ª Série entram no índice, mas ficam numa tabela `so_referencia`, e a pesquisa tira-os do BM25 em todo o acervo. Só aparecem quando a pergunta cita o ato: «Regulamento n.º 1126/2026», «Edital n.º 317/2001 (2.ª série)», «Acordo Coletivo de Trabalho n.º 206/2015». Para isso, as referências passaram a ler «Edital», «Acordo Coletivo de Trabalho» e «Regulamento» com números como «296-B/2007», e os números com sufixo «11/2003 - AP». No conjunto completo, isto não muda nenhum resultado (`bm25-indice-1611-refs`).

| Medição | Sem a 2.ª Série | 2.ª Série toda | Só pela referência |
|---|--:|--:|--:|
| 54 da 2.ª Série, BM25: @1 / @10 | 0 % / 0 % | 65 % / 96 % | 67 % / 96 % |
| 54 da 2.ª Série, reranker: @1 / @10 | — | 89 % / 98 % | **91 % / 98 %** |
| 281 reais, reranker: @1 / @10 | 120 / 218 | 115 / 214 | **120 / 216** |
| 281 reais, reranker: certas | 101 | 99 | **105** |
| 281 reais, BM25: @1 / @10 | 93 / 200 | 90 / 192 | 90 / 193 |

- **Com o reranker, só pela referência não perde nada nas perguntas reais.** Pioram 24 e melhoram 31, e só 1 das 24 tem um ato da 2.ª Série em 1.º lugar. Nas 54 da 2.ª Série, o «não sei» desce de 6 % para 2 %.
- **Só com BM25, as reais perdem um pouco** (−3 @1, −7 @10), mesmo sem nenhum ato da 2.ª Série nos resultados. A causa provável são as estatísticas do BM25: os 950 mil pedaços a mais mudam a raridade de cada termo e o corte dos termos que estão em mais de 20 % dos pedaços. Ler mais candidatos até haver tantos como num índice sem a 2.ª Série não mudou nada (`bm25-reais-ref-fundo`). Para o resolver, os atos só pela referência teriam de ficar numa tabela de pesquisa à parte.
- **Medido outra vez a 18/11**, no índice de uso de 17/11 contra um índice sem a 2.ª Série feito do mesmo export (`bm25-1711-uso` e `bm25-1711-sem-ii`, as 1.298 perguntas do conjunto por omissão, só BM25). A 2.ª Série custa 10 respostas certas (567 contra 577). Nas reais são 4 no 1.º lugar (94 contra 98) e 6 nos 10 primeiros (199 contra 205; 8 ganhos e 2 perdas). Os atos da 2.ª Série são 35 % dos 1.000 pedaços que o BM25 lê, mas ler 4.000 só recupera 1 real. **Decisão: fica como está.** A aplicação usa sempre o reranker, e com ele a perda não aparece. Uma tabela de pesquisa à parte mudaria o formato do índice, e as aplicações instaladas teriam de ser substituídas antes de o publicar.

**Decisão: o `rag.indice` põe por omissão a 2.ª Série só pela referência** (feito na noite de 16/11: 357.148 diplomas, 2.532.562 pedaços, 90.053 só pela referência). Os deltas levam a tabela (`rag.dados`, com teste), e `rag.dados publicar` recusa um índice com ela sem `--com-so-referencia`. A aplicação 0.1.0 não conhece a tabela e poria a 2.ª Série na pesquisa em todo o acervo, por isso este índice só vai para o Hugging Face depois de lançar a aplicação nova.

### CNPD e TC

As decisões da CNPD e os acórdãos do TC não estão no export das leis nem no índice. O TC chega às respostas pelo `normas-julgadas.jsonl`: o aviso de inconstitucionalidade, e a segunda resposta, a da jurisprudência. A CNPD ainda não entra no RAG.

## Modo sem IA: o âmbito à vista (17/11/2026)

O teste que levou a isto: «Quantos dias de férias tem um trabalhador por ano?», sem IA, dava em 1.º lugar o artigo 126.º da Lei Geral do Trabalho em Funções Públicas (LTFP), e na lista apareciam as Portarias 913/80 e 193/79 (30 dias, de um setor só). Quem lê não tinha como ver que o 1.º artigo era só da função pública. Três mudanças, nenhuma pede reconstruir o índice:

- **A. Os 3 artigos mais prováveis, cada um com o âmbito** (`rag/ambito.py`, página e `rag/web.py`). No modo sem IA a página já não mostra um artigo como se fosse a resposta. Mostra os 3 primeiros, numerados, com uma etiqueta: «Função pública», «Direito da UE», «Só Açores», «Só Madeira», «Regulamento de 1980, sem versão consolidada» ou «Regime geral».
- **B. A lei geral antes dos regimes de um setor.** Se a pergunta não fala da função pública, os diplomas da função pública levam um fator 0,8 no BM25 (`PRIOR_SETOR`). Com o reranker, contam um ponto a menos na ordenação (`RERANKER_SETOR`), mas só abaixo do nível 2 e nunca para o limiar do «não sei». Quando a pergunta cita o diploma, nada muda.
- **C. Os regulamentos antigos atrás.** Portarias, despachos e avisos de antes de 1990 sem versão consolidada levam um fator 0,75 (`PRIOR_ANTIGO`) e um ponto a menos com o reranker (`RERANKER_ANTIGO`).

Na pergunta das férias, com o reranker, o 1.º lugar passa a ser o artigo 239.º do Código do Trabalho, o 2.º o 126.º da LTFP e o 3.º o 238.º do Código do Trabalho, e as portarias saem da lista.

| Medição | Antes | Com A, B e C |
|---|--:|--:|
| 1.298 perguntas, BM25: certas | 557 | 562 |
| 281 reais, BM25: @1 / @10 | 90 / 193 | 94 / 194 |
| 281 coloquiais, BM25: @1 / @10 | 30 / 85 | 31 / 86 |
| 281 reais, reranker: @1 / @10 | 122 / 222 | 125 / 223 |
| 281 reais, reranker: certas / «não sei» | 108 / 92 | **112** / 93 |

- **Nenhum tipo piora** no conjunto completo (`bm25-indice-1611-ref` contra `bm25-ambito`). Os outros tipos ficam exatamente iguais.
- **Com o reranker** (`cruzado-reais-sem-ambito` contra `cruzado-reais-ambito`, limiar 3): ganham-se 4 certas e não se perde nenhuma. As 4 são perguntas gerais de trabalho em que a LTFP passava à frente do Código do Trabalho: o período experimental, a contagem do período experimental, o trabalho noturno e quem define o horário. Mais 2 perguntas descem do 1.º para o 2.º lugar sem mudar a resposta.
- **Sem afinar mais:** os fatores ficaram nos primeiros valores. Não foram ajustados à pergunta das férias nem às 281 reais.

**Correção: artigos repostos depois de revogados** (`fontes.revogado`). Um artigo contava como revogado se alguma nota dissesse «Revogado», mesmo que uma alteração posterior o tivesse reposto. Era o caso dos artigos 1064.º a 1113.º do Código Civil (o arrendamento, revogado em 1990 e reposto pela Lei 6/2006). Agora conta a data de publicação de cada nota: o artigo só está revogado se a última revogação for posterior à última alteração. Se uma revogação não tiver data, ou tiver uma data impossível («1079-01-01»), o artigo continua revogado. Saem 159 artigos em vigor que contavam como revogados, 53 deles do Código Civil.

- **Medido só com BM25** (`bm25-ambito` contra `bm25-ambito-revogado`, nas literais, revogadas, reais e coloquiais): as reais passam de 194 para 199 com o artigo nos 10 primeiros. As 5 que entram são perguntas de arrendamento (artigos 1101.º e 1110.º do Código Civil e o NRAU). Em 1.º lugar nada muda.
- **Aviso a menos, certo:** na lit-166, o artigo 1069.º do Código Civil (forma do contrato de arrendamento) deixa de vir com o aviso «revogado», que estava errado. As 55 revogadas continuam todas com o aviso e o diploma revogatório certo.

## Índice de 17/11: os blocos 1 e 2 da consolidação

O índice foi reconstruído com o export de 17/11, que tem os 27 diplomas consolidados nos blocos 1 e 2 da ronda 113 (2.761 no total). Ficou em `rag/indice/indice-1711.sqlite`, ao lado do índice em uso, e leva 357.148 diplomas e 2.532.809 pedaços. Medições só da pesquisa, sem LLM e com o mesmo código nos dois índices:

| Medição | Índice de 16/11 | Índice de 17/11 |
|---|--:|--:|
| 1.298 perguntas, BM25: certas | 565 | 567 |
| 99 de texto alterado, BM25: texto certo em 1.º / nos 10 primeiros | 67 / 77 | 69 / 79 |
| 99 de texto alterado, reranker: certas / «não sei» | 68 / 5 | 70 / 5 |

- **Ganham-se 2 perguntas e não se perde nenhuma** (`bm25-1711-antes` contra `bm25-1711-depois`, `cruzado-alt-1711-*`): a alt-001 e a alt-058, as duas do Despacho Normativo n.º 61-C/95, que passou a ter o texto em vigor. Os outros tipos ficam exatamente iguais.
- **Ainda não substitui o `indice.sqlite`:** a troca espera que acabem as medições da sessão das perguntas por artigo, que leem o índice em uso. O bloco 3 da consolidação ficou por aplicar.

## Perguntas por artigo (piloto, 16/11/2026)

Sem chave da API não há reescrita da pergunta numa consulta jurídica, e o BM25 recebe as palavras do dia a dia. Com a reescrita, o artigo certo em 1.º nas reais sobe de 42 % para 68 %. A ideia deste piloto é escrever uma vez, offline, perguntas de leigo para cada artigo e juntá-las aos termos do artigo. É o que na literatura se chama doc2query.

**Como se fez** (`rag/perguntas_por_artigo.py`, dados em `rag/perguntas_artigo/`):
- **Âmbito:** os artigos em vigor e não revogados do Código do Trabalho (anexo da Lei n.º 7/2009, 599), do NRAU (o articulado da Lei n.º 6/2006, 74) e do Código Civil, art. 1022.º a 1113.º (92). São 765 ao todo.
  - O anexo do NRAU que republica o Código Civil fica de fora: é texto de 2006, e o texto em vigor está no DL 47344.
  - Os revogados escolhem-se pela nota mais recente (`revogado_agora`). O `fontes.revogado` dava como revogados 50 artigos em vigor do Código Civil (1064.º a 1113.º), porque basta-lhe uma nota antiga «Revogado pelo…». Isso também os penaliza na pesquisa (abaixo, ressalvas).
- **Geração:** 22 sessões do Claude (`claude-opus-5-5`), uma por lote de 35 artigos, com as regras de `REGRAS.md`.
  - Cada sessão leu só as regras e o seu lote, sem acesso às perguntas de avaliação, e as regras não foram escritas a partir delas.
  - O `importar` validou tudo: 3 a 5 perguntas por artigo, sem números de artigos nem nomes de diplomas. As 765 linhas passaram à primeira.
  - Resultado: **3.078 perguntas**, com uma mediana de 14 palavras. Ficaram no commit antes de qualquer medição, e não se mudaram depois de ver os resultados.
- **No índice:** as perguntas entram nos termos da coluna `texto` do FTS (peso 1, fixado antes de medir), só na redação em vigor do artigo.
  - O texto do artigo, o que o reranker lê e o resto do índice não mudam.
  - A tabela `perguntas_artigo` guarda as perguntas, para os deltas apagarem a linha do FTS com os mesmos termos (`rag.dados`, com testes).
  - `rag.indice --com-perguntas` junta-as; por omissão fica desligado. `rag.dados publicar` recusa um índice com perguntas sem `--com-perguntas`, porque a aplicação 0.1.0 corrompia o FTS ao aplicar um delta.
- **Medição sem batota:**
  - «Antes» é uma cópia do índice de uso de 16/11; «depois» é a mesma cópia com as perguntas (`rag.perguntas_por_artigo juntar`). Os dois saem do mesmo export e só diferem nas perguntas.
  - A medição é `rag.avaliar --sem-llm` com o mesmo código, e o `comparar` agrupa por âmbito e emparelha pergunta a pergunta.
  - **Decide-se nas 155 perguntas do âmbito que nunca serviram para afinar**: 127 coloquiais e 28 reais novas (real-201…350). As 99 reais do Código do Trabalho são todas das 136 afinadas, e por isso ficam à parte.

**BM25** (as 1.519 perguntas: o conjunto público, as 281 reais, as 281 coloquiais, as da UE e as da 2.ª Série; resumos `rag/resultados/pa-antes-bm25.json` e `pa-depois-bm25.json`):

| Grupo | n | Artigo certo em 1.º (pontos) | Nos 10 primeiros | Ganhos / perdas no 1.º |
|---|--:|--:|--:|--:|
| **Âmbito, nunca afinaram (decisão)** | 155 | 15% → **55%** (+39) | 39% → **80%** | 69 / 8 |
| âmbito: coloquial | 127 | 13% → **57%** (+45) | 35% → **82%** | 63 / 6 |
| âmbito: real (novas) | 28 | 29% → **43%** (+14) | 57% → **71%** | 6 / 2 |
| âmbito: real (afinadas) | 99 | 46% → **71%** (+24) | 80% → **97%** | 25 / 1 |
| âmbito: premissa errada | 8 | 38% → 50% | 62% → 62% | 1 / 0 |
| âmbito: compostas | 7 | 0% → 0% | 71% → 100% | 0 / 0 |
| fora: coloquial | 154 | 9% → 7% | 26% → 22% | 0 / 3 |
| fora: real (novas) | 117 | 26% → 25% | 68% → 67% | 0 / 2 |
| fora: real (afinadas) | 37 | 14% → 14% | 49% → 49% | 0 / 0 |
| fora: literais, temporais, revogadas, texto alterado, premissa errada, compostas (com as da UE e da 2.ª Série) | 837 | sem mudança | sem mudança | 0 / 0 |
| **Fora do âmbito (todas)** | 1.145 | 58% → 57% | 80% → 79% | 0 / 5 |

Nas reais, que são FAQs escritas por pessoas, o artigo certo em 1.º passa de 32 % para 41 % (90 → 116 de 281). Nas coloquiais passa de 11 % para 30 % (30 → 84 de 281).

As perdas são de dois tipos:
- dentro do âmbito, um artigo vizinho do mesmo código, que agora tem mais palavras de leigo, passa à frente do certo (falta para assistência a filho em vez de dispensa, denúncia pelo arrendatário em vez da do senhorio);
- fora do âmbito, um artigo do Código do Trabalho passa à frente de um diploma que não tem perguntas (Lei n.º 15/2014, Portaria n.º 142-B/2012, DL 308/2007).

Este segundo tipo é o custo de só uma parte do acervo ter perguntas. Alargá-las a outros diplomas também o reduz.

**Com o reranker** (`--reranker cruzado --limiar 3`, a configuração da aplicação sem chave; as 562 reais e coloquiais, `pa-antes-reranker` e `pa-depois-reranker`). O reranker continua a ler só o caminho e o texto do artigo: as perguntas só mudam os candidatos que o BM25 lhe dá.

| Grupo | n | Artigo certo em 1.º (pontos) | Nos 10 primeiros | Ganhos / perdas no 1.º |
|---|--:|--:|--:|--:|
| **Âmbito, nunca afinaram (decisão)** | 155 | 26% → **44%** (+18) | 49% → **79%** | 31 / 3 |
| âmbito: coloquial | 127 | 27% → **47%** (+20) | 46% → **81%** | 29 / 3 |
| âmbito: real (novas) | 28 | 21% → **29%** (+7) | 64% → **68%** | 2 / 0 |
| âmbito: real (afinadas) | 99 | 66% → **69%** (+3) | 94% → **95%** | 4 / 1 |
| fora: coloquial | 154 | 19% → 18% | 33% → 32% | 2 / 3 |
| fora: real (novas) | 117 | 31% → 31% | 69% → 69% | 0 / 0 |
| fora: real (afinadas) | 37 | 38% → 41% | 65% → 62% | 1 / 0 |
| **Fora do âmbito (todas)** | 308 | 26% → **26%** | 51% → 50% | 3 / 3 |

O artigo certo chega muito mais vezes aos candidatos: nos 10 primeiros passa de 49 % para 79 %. Mas o reranker, que compara a pergunta de leigo com o texto jurídico, só o põe em 1.º em parte dos casos. Com o limiar 3, o «não sei» no grupo da decisão fica em 75 % (era 75 %), e as respostas certas passam de 18 em 39 para 22 em 38.

**Variante declarada antes de medir, em que o reranker também lê as perguntas do artigo** (`--reranker-com-perguntas`, só nas 254 do âmbito, `pa-depois-reranker-rp`):

| Grupo | n | Artigo certo em 1.º (pontos) | Nos 10 primeiros | "Não sei" (limiar 3) | Certas nas respondidas |
|---|--:|--:|--:|--:|--:|
| **Âmbito, nunca afinaram** | 155 | 26% → **71%** (+45) | 49% → **85%** | 75% → **28%** | 46% (18/39) → **83% (92/111)** |
| âmbito: coloquial | 127 | 27% → **76%** (+49) | 46% → 88% | | |
| âmbito: real (novas) | 28 | 21% → **50%** (+29) | 64% → 68% | 39% → 21% | 29% (5/17) → 59% (13/22) |
| âmbito: real (afinadas) | 99 | 66% → **82%** (+16) | 94% → 97% | | |

É o maior ganho do piloto. Nas FAQs escritas por pessoas e que nunca afinaram, o artigo certo em 1.º passa de 6 em 28 para 14 em 28, com 8 ganhos e nenhuma perda. **Ainda não pode entrar**, por duas razões:
1. Não foi medida fora do âmbito nem nas «sem resposta».
2. Ao ler perguntas de leigo, o reranker dá notas mais altas, que é por isso que o «não sei» cai. O limiar 3 foi afinado para notas sobre texto jurídico, e pode passar a deixar responder onde devia recusar. Sobretudo num acervo em que só uma parte dos artigos tem perguntas.

**Decisão:** o critério está cumprido. Com o reranker, nas 155 perguntas do âmbito que nunca afinaram, o artigo certo em 1.º sobe 18 pontos (mais de 10), e fora do âmbito fica igual. **Propõe-se alargar aos outros códigos**, com o custo abaixo. Antes de as pôr no índice de uso:
- medir a variante do reranker com perguntas fora do âmbito e nas «sem resposta», e rever o limiar com ela;
- medir outra vez com o `fontes.revogado` corrigido.

O ganho da variante principal sozinha é sobretudo de candidatos (o @10), e só se transforma em respostas se o reranker também ler as perguntas ou se houver LLM.

**Ressalvas:**
- As coloquiais foram escritas por sessões do Claude, como as perguntas geradas. Partilham vocabulário, e isso pode inflacionar o ganho nelas, embora a geração nunca as tenha visto.
- Nas FAQs escritas por pessoas, o ganho é menor e mais seguro: +14 pontos nas 28 novas (6 ganhos, 2 perdas; amostra pequena) e +24 nas 99 afinadas, que aqui servem de controlo, porque a geração também não as viu.
- 99 das 127 coloquiais reescrevem reais afinadas, e por isso o nível absoluto delas está inflacionado. A diferença entre antes e depois continua justa: a pesquisa é a mesma nos dois índices.
- Os 50 artigos do arrendamento do Código Civil dados como revogados pelo `fontes.revogado` (peso a priori 0,6, vão para trás e levam o aviso) baixam as perguntas de arrendamento nos dois índices. Entretanto corrigido (17/11): ver «Correção: artigos repostos depois de revogados» acima.
- Não houve um índice construído de raiz com `--com-perguntas`. O `construir` chama a mesma função que o `juntar` (`juntar_perguntas`), e os testes confirmam que dá o mesmo FTS, também por deltas.

**Custo de alargar** aos outros códigos principais (`Pesquisa.codigos_principais()`):
- No índice de 16/11 são 58 diplomas com 15.910 artigos em vigor e não revogados (13,7 milhões de caracteres). Sem os 765 do piloto, ficam cerca de 15.150, o resto do Código Civil incluído.
- O piloto gastou cerca de 2,3 milhões de tokens nas sessões (≈ 3.000 por artigo) e 3 minutos por lote de 35.
- Alargar dá cerca de **430 lotes e 45 milhões de tokens**: umas 2 horas com 11 sessões em paralelo, mais a validação.
- A lista dos «códigos principais» também traz alguns regulamentos e editais grandes que não são códigos: convém rever a lista antes de gerar.

### Medição completa com o código novo (18/11/2026)

As duas medições que faltavam antes de pôr as perguntas no índice de uso: a variante do reranker que lê as perguntas, agora também fora do âmbito e nas «sem resposta», e tudo com o `fontes.revogado` corrigido (código do main de 17/11, 48da30ab64d).

- **Como:** as 667 reais, coloquiais e «sem resposta», com `--reranker cruzado --limiar 3`, em 7 partes de 96 por causa do corte de luz de 17/11. «Antes» é outra vez uma cópia byte a byte do índice de uso de 16/11; «depois» é essa cópia com as 765 entradas de perguntas. A parte 1 do «depois» deu no BM25 0 diferenças face à medição de 17/11. Resumos em `rag/resultados/pa2-antes-reranker.json`, `pa2-depois-reranker.json` e `pa2-depois-reranker-rp.json`, mais os do BM25 (`pa2-antes-bm25.json`, `pa2-depois-bm25.json`).
- **Controlo:** o «antes» nas reais dá 112 certas, 125 no 1.º, 223 nos 10 primeiros e 93 «não sei», os mesmos números da medição do modo sem IA de 17/11.

| Grupo | n | Antes | Perguntas só nos candidatos | O reranker também as lê |
|---|--:|--:|--:|--:|
| **Âmbito, nunca afinaram (decisão):** artigo certo em 1.º | 155 | 30% | 50% (32 ganhos / 1 perda) | **76%** (77 / 6) |
| … nos 10 primeiros | 155 | 54% | 87% | **94%** |
| … «não sei» (limiar 3) | 155 | 116 | 115 | **35** |
| … certas nas respondidas | 155 | 54% (21/39) | 60% (24/40) | **83% (99/120)** |
| âmbito: real (novas), FAQs escritas por pessoas: em 1.º | 28 | 25% | 32% | **64%** (11 / 0) |
| … certas nas respondidas | 28 | 6/18 | 8/19 | **17/25** |
| âmbito: real (afinadas), em 1.º | 99 | 71% | 74% | 83% |
| **Fora do âmbito:** em 1.º | 308 | 25% | 26% (4 / 3) | 26% (4 / 3) |
| … certas nas respondidas | 308 | 47/92 | 47/90 | 46/92 |
| **«Sem resposta»:** respondeu quando devia recusar | 105 | 5 | 5 | **8** |

- **Fora do âmbito não muda nada,** nas duas variantes. Era a primeira dúvida.
- **As 3 «sem resposta» a mais** são todas de arrendamento: sem-024 e sem-060 (o senhorio pode aumentar a renda em 10 % ou 15 %?) e sem-051 (o coeficiente de 2026). O 1.º resultado é um artigo do piloto (NRAU 24.º e 51.º, Código Civil 1077.º), com notas entre 3,04 e 3,31, logo acima do limiar 3. É o risco previsto: ao ler perguntas de leigo, o reranker dá notas mais altas.
- **Subir o limiar para todos não serve.** Com 3,35 voltam a ser 5 «sem resposta», mas fora do âmbito as certas caem de 46 para 40 (simulado com as notas gravadas, sem nova corrida). Um limiar mais alto só quando o 1.º artigo tem perguntas (≈ 3,35) evitaria isso. No grupo da decisão daria cerca de 92 certas em 111 respondidas, em vez de 99 em 120. Mas seria afinar com 3 casos, e fica por decidir.
- As ressalvas de cima continuam: as coloquiais partilham o vocabulário das perguntas geradas, e o sinal mais seguro são as 28 reais novas (6 → 17 certas, sem perdas no 1.º; amostra pequena).

### Alargamento aos outros códigos principais (19/11/2026)

A lista de `Pesquisa.codigos_principais()` no índice de uso de 16/11, revista à mão, está em `OUTROS_CODIGOS` (`rag/perguntas_por_artigo.py`), com as razões de cada saída num comentário. Em resumo:
- **Ficam** 37 blocos: o resto do Código Civil (sem os artigos 1022.º a 1113.º do piloto), o Penal, os de Processo Civil, Penal, do Trabalho e nos Tribunais Administrativos, o da Execução das Penas, o de Justiça Militar, os dos impostos (IRS, IRC, IVA, IMI, IMT, Selo, ISV, IUC, IEC, a LGT e o CPPT), o dos Regimes Contributivos, o CPA, a LTFP, o dos Contratos Públicos, o das Expropriações, o da Estrada, o das Sociedades Comerciais, o da Insolvência, o dos Valores Mobiliários, o Cooperativo, os dos Registos Comercial, Predial e Civil, o do Notariado, o da Propriedade Industrial, o do Direito de Autor, o da Publicidade e o Deontológico dos Contabilistas.
- **Saem** 17 diplomas da lista:
  - os textos originais sem histórico de códigos que já lá estão na versão consolidada (CIRS e CIRC de 1988, CIVA de 1984);
  - os códigos substituídos (Notariado de 1960, Registo Civil de 1967, Custas Judiciais, Processo das Contribuições, Trabalho Rural, Custas do Ultramar, Código Administrativo de 1940);
  - os que não estão em vigor (Contribuição Predial, Imposto de Transacções, Processo Tributário de 1991, Recuperação da Empresa, Florestal);
  - o Código de Boas Práticas Agrícolas (um despacho) e o Código da Ação Social dos Açores (regional).
- **Entra à mão** o Código do Registo Civil do DL 131/95: `Pesquisa.codigo` escolhe o de 1967, que tem mais artigos.
- **Números antes de gerar:** 11.418 artigos em vigor e não revogados (`revogado_agora`), 9,4 milhões de caracteres, **327 lotes de 35**. Mais 1 do piloto: o 1063.º do Código Civil, que no piloto contava como revogado. A estimativa de 430 lotes contava os textos que saíram.
- As regras (`rag/perguntas_artigo/REGRAS.md`) passam a valer para todas as áreas, com palavras do dia a dia para cada uma. A validação também recusa os nomes dos outros códigos («código da estrada», «Código Penal», «Lei Geral Tributária») e as siglas (CPC, CIRS, LGT…). «O código do multibanco» e «a lei geral do trabalho» passam. As 3.078 perguntas do piloto continuam todas válidas.
- **Chaves repetidas:** o Código Penal, o de Processo Penal e o do Registo Predial estão no articulado do decreto que os aprova (parte vazia). Os artigos do próprio decreto, sem epígrafe, têm a mesma chave que os do código («1.º»). São 30 e saem da lista (`artigos_do_ambito`), porque o `juntar_perguntas` junta as perguntas a todos os pedaços com essa chave: o «Artigo 1.º» do decreto («O Código Penal é revisto…») fica com as perguntas do princípio da legalidade. Ficam 11.388 artigos.
- **Feito (23/11):** os 327 lotes gerados e validados, com 11.389 artigos e 42.392 perguntas novas (3 a 5 por artigo, 3,7 em média) em 37 ficheiros de `rag/perguntas_artigo/`, um por bloco. Com o piloto, são 12.154 artigos e 45.470 perguntas. Um lote falhou a validação e foi repetido: o 280, por uma pergunta com «decreto». O lote 38 trazia o `documento` trocado pela parte, e esse campo foi corrigido a partir da entrada. A geração parou de 19 a 23/11 por falta de uso do plano. Ainda não está medido: as perguntas só entram no índice com `rag.indice --com-perguntas`.
- `exportar --so-sem-perguntas` exporta só os artigos que ainda não têm perguntas. `estado --pasta P` diz que lotes já estão validados, para retomar depois de um corte. O `importar` só reescreve os blocos que vêm na pasta e guarda as linhas que já lá estavam.

**Compostas: 8 contra 16 artigos no contexto, com o LLM e os juízes** (19/11/2026). Mediram-se as 100 compostas, as 50 de premissa errada e as 80 sem resposta:
- **Pesquisa:** uma só por pergunta, no índice de uso de 17/11 numa cópia fixa, com as consultas reescritas de `reescrita2`, o reranker cruzado com 30 candidatos e o limiar 1. O LLM recebe os 8 ou os 16 primeiros artigos da mesma consulta (`passo_llm exportar --contextos 8,16 --consultas PASTA`). Assim, o ruído do reranker não entra na comparação.
- **LLM:** um subagente Opus por lote e por contexto, que só lê a entrada.
- **Juízes:** quatro, às cegas (a, b, c e s). Uma resposta é certa só se os quatro a dão como correta e fundamentada.
- **Resumos:** `rag/resultados/compostas-ctx8-*.json`, `compostas-ctx16-*.json` e `compostas-ctx-comparacao.json`.

| Tipo | n | Contexto | Respondidas | "Não sei" | Certas (juízes) | Fiabilidade | Limite inferior 95% |
|---|--:|--:|--:|--:|--:|--:|--:|
| Compostas | 100 | 8 | 77 | 23% | 72 | 94% (72/77) | 86% |
| | | 16 | 84 | 16% | **79** | 94% (79/84) | 87% |
| Premissa errada | 50 | 8 | 46 | 8% | 45 | 98% (45/46) | 89% |
| | | 16 | 48 | 4% | 46 | 96% (46/48) | 86% |
| Sem resposta | 80 | 8 | 1 | 99% | — | recusa 79 de 80 | — |
| | | 16 | 2 | 98% | — | recusa 78 de 80 | — |

Pergunta a pergunta:
- **Compostas: 7 ganhos e 0 perdas.**
  - Em 6 dos ganhos, o segundo artigo está entre o 9.º e o 16.º lugar (cmp-030, 069, 070, 073, 076 e 087). Com 8 artigos, o LLM dizia que faltava a norma ou citava o texto original; com 16, responde certo. É o efeito que se queria medir.
  - O 7.º ganho (cmp-052) tem os dois artigos nos 3 primeiros e passou de errada a certa: é variação do LLM.
  - As não certas ficam em 5 nos dois. Dois "não sei" passam a respostas incompletas (cmp-064 e 085, com um dos artigos fora dos 16), e uma incompleta passa a "não sei" (cmp-089).
- **Premissa errada: igual.** Há 1 ganho (pre-010, com o artigo em 11.º). Um "não sei" passa a incompleta (pre-025, com o artigo em 14.º).
- **Sem resposta:** com 16, responde a mais uma, a sem-076 (atrasos dos comboios no DL 58/2008, que traz a resposta). É uma das perguntas escritas antes de a UE e os consolidados estarem no acervo.
- **Os dois artigos estão nos 8 primeiros em 67 compostas e nos 16 primeiros em 78**, como na medição só com a pesquisa.

**Custo.** O prompt passa de 11,4 mil para 23,4 mil caracteres em média (2,0 vezes). Um subagente que responde a um lote de 10 compostas gastou cerca de 130 mil tokens com 8 artigos e cerca de 190 mil com 16. Os juízes também leem os artigos, por isso o custo deles sobe na mesma proporção.

**Ressalvas:**
- Fez-se uma corrida por contexto, por isso a variação do LLM e dos juízes não foi medida. 7 ganhos e 0 perdas, 6 deles explicados pelo segundo artigo, é sinal, mas o número está perto das ~8 perguntas de ruído entre variantes da pesquisa.
- O LLM e os juízes são o mesmo modelo, e não houve revisão de um jurista.
- As reais foram medidas depois, numa amostra de 100 (abaixo).

**Reais, as mesmas regras** (19/11/2026, a pedido do João): 100 reais tiradas ao acaso das 281 (semente 16; os ids estão em `privado/`), o mesmo índice, a mesma reescrita e os mesmos quatro juízes. Resumos em `rag/resultados/reais1-ctx8-*.json`, `reais1-ctx16-*.json` e `reais-ctx-comparacao.json`.

| Reais (100) | Respondidas | "Não sei" | Certas (juízes) | Não certas | Fiabilidade | Limite inferior 95% |
|---|--:|--:|--:|--:|--:|--:|
| 8 artigos | 93 | 7% | 91 | 2 | 98% (91/93) | 92% |
| 16 artigos | 95 | 5% | 91 | **4** | 96% (91/95) | 90% |

- **3 ganhos e 3 perdas.** Os ganhos (real-037, 235 e 317) são "não sei" que passam a certas, com o artigo certo no 10.º ou no 11.º lugar: é o mesmo efeito das compostas.
- Das perdas, duas passam a não certas e têm o artigo certo em 1.º lugar (real-095 e real-249). Na real-095, a resposta cita a nota de suspensão de 2013 do artigo; com 8 artigos, os juízes aceitaram-na, e com 16 um deles deu-a como errada. Na real-249, a resposta troca "mais de uma semana" por "apenas uma semana". O contexto maior não explica nenhuma das duas, e é mais provável que seja variação do LLM e dos juízes, mas não se mediu.
- A terceira perda (real-288) passa de certa a "não sei".
- O prompt passa de 12,3 mil para 23,2 mil caracteres em média.

**Decisão: fica 8.** A regra combinada era mudar para 16 só se as reais não piorassem mais do que 1 em 100. Pioraram 2 (de 2 para 4 não certas), e a fiabilidade baixa de 98% para 96%. A diferença está dentro do que uma corrida só pode dar, mas o número que se mediu não passa a regra. Ganha-se nas compostas (+7 certas) e perde-se fiabilidade nas reais, com o dobro do custo por pergunta.


## Candidatos ao reranker e pesquisa semântica (19/11/2026)

As 1.298 perguntas no índice de 17/11, com `--reranker cruzado --limiar 3`, sem LLM. Resumos em `rag/resultados/max15-1711.json`, `max30-1711.json`, `max50-1711.json`, `sem1711-com.json` e `sem1711-sem.json`.

- **Como:** para poupar CPU, cada pergunta foi pontuada uma só vez com a lista maior, e as variantes menores reutilizaram as notas desses mesmos textos. Os 15/30/50 usaram a lista de 50, e o com/sem semântica a lista com os candidatos semânticos.
- **Ruído do reranker:** a nota de um texto muda com os outros textos do mesmo lote. O modelo é int8 e a quantização depende do lote. Numa pergunta temporal, os mesmos 30 textos em ordem inversa mudaram até 0,62, e lidos um a um até 0,22. A ordem dos primeiros quase não muda, mas as notas perto do limiar 3 mudam, e com elas o «não sei». Por isso `max30-1711` e `sem1711-sem`, que são a mesma configuração com lotes diferentes, diferem em 8 perguntas certas (614 e 613) e em 7 que respondem ou não. **Diferenças de menos de ~8 perguntas entre variantes são ruído.**

| `maximo` (candidatos que o reranker lê) | 15 | 30 (o atual) | 50 |
|---|--:|--:|--:|
| Certas (de 1.298) | 617 | 614 | 608 |
| Respondidas | 831 | 837 | 843 |
| Reais: certas nas respondidas | 114/185 | 111/186 | 108/191 |
| «Sem resposta» a que respondeu (de 80) | 4 | 6 | 6 |
| Compostas com os artigos nos 10 primeiros | 58 | 64 | 61 |
| Texto alterado: certas | 69 | 70 | 70 |
| Face a 30, pergunta a pergunta | 8 ganhos / 3 perdas | — | 2 ganhos / 8 perdas |

- **Mais candidatos não ajudam:** com 50 responde mais vezes e acerta menos (8 perdas, 5 delas reais). Com 15, os 2 «sem resposta» a menos e as 3 reais a mais estão dentro do ruído, e as compostas perdem 6 nos 10 primeiros.
- **Decisão: fica 30.** Falta medir o tempo por pergunta de cada um, com a máquina livre. A 19/11 de madrugada a medição foi parada, porque outras sessões levaram a carga do CPU a 70.

| Pesquisa semântica (`rag.semantica`, 20 candidatos a mais) | Sem | Com |
|---|--:|--:|
| Certas (de 1.298) | 613 | 611 |
| Reais: certas nas respondidas | 110/185 | 107/186 |
| Coloquiais: certas nas respondidas | 24/35 | 25/37 |
| Coloquiais com o artigo nos 10 primeiros (de 281) | 112 | **137** |
| Reais com o artigo nos 10 primeiros (de 281) | 223 | 227 |
| «Sem resposta» a que respondeu (de 80) | 5 | 5 |
| Pergunta a pergunta | — | 2 ganhos / 4 perdas (todas reais) |

- **A semântica traz o artigo certo para os candidatos** (+25 coloquiais nos 10 primeiros), **mas o reranker não o põe em 1.º:** as certas ficam iguais, dentro do ruído.
- **Decisão: fica desligada**, como já está por omissão. Os vetores ficam em `rag/indice/semantica.npz` para voltar a medir com um reranker melhor ou com as perguntas por artigo nos outros códigos.

**Medição de base para o índice novo** (`rag/resultados/app011-1711.json`): o índice de 17/11 com a configuração da aplicação 0.1.1 (reranker em lotes de 16, sem ler as perguntas, limiar 3), sem a reutilização de notas. Dá 615 certas de 1.298 (841 respondidas), reais 112/188, «sem resposta» respondidas 5 de 80. Bate com o `max30-1711` (614) e o `sem1711-sem` (613), dentro do ruído. É com ela que se compara o índice reconstruído com o bloco 3 e as perguntas por artigo, antes de publicar.

**O índice novo, medido como a aplicação 0.1.1 pesquisa (19/11/2026).** Mesma configuração da base, sobre dois índices: o das 15h27 (`app011-1911`), com o bloco 3 e as perguntas por artigo nos outros códigos, e o final das 16h54 (`app011-final`), que junta as retificações e a vigência revista.

| | Base 17/11 | Índice 15h27 | Índice final |
|---|--:|--:|--:|
| Certas (de 1.298) | 615 | 619 | 619 |
| Respondidas | 841 | 834 | 834 |
| «Sem resposta» respondidas | 5 | 5 | 5 |
| Artigo certo em 1.º | 693 | 738 | 739 |
| Artigo certo no top 10 | 948 | 1.038 | 1.038 |
| Coloquiais, artigo no top 10 | 112 | 186 | 186 |
| Reais, artigo no top 10 | 223 | 236 | 236 |

Pergunta a pergunta, da base para o final ganham-se 9 certas (6 reais, 2 de texto alterado, 1 coloquial) e perdem-se 5 (3 reais, 2 coloquiais): o saldo de +4 fica dentro do ruído. O ganho real é encontrar o artigo (+90 no top 10, quase todo nas coloquiais), que a 0.1.1 aproveita pouco porque o reranker dela não lê as perguntas. Entre o índice das 15h27 e o final não muda nenhuma resposta: as retificações e a vigência não mexem na pesquisa destas perguntas. Literais, temporais e revogadas ficam iguais. O índice final cumpre os critérios para se publicar; a publicação espera pelo fecho da auditoria dos consolidados, e o índice volta a construir-se nessa altura.

## Reranker por passagens (20/11/2026)

É a medida 2 do diagnóstico das reais não encontradas (`reports/diagnostico-reais-nao-encontradas.md`). **Está desligada por omissão**: a aplicação, o limiar e o índice não mudam.

- **O problema:** o reranker lê os primeiros 1.200 caracteres de cada texto, contando o rótulo. Num artigo comprido, o número que responde à pergunta pode estar depois do corte.
- **O que a opção faz** (`Reranker(passagens=True)` em `rag/modelos.py`; `--reranker-passagens` no `rag.avaliar`): o resto de um artigo comprido é partido em passagens pelos números do artigo. Um número maior do que uma passagem parte-se pelas alíneas, com o corpo do número repetido. Cada passagem leva o rótulo e a epígrafe e, com `--reranker-com-perguntas`, as perguntas do artigo. O reranker pontua o início e as passagens, e o artigo fica com a melhor nota. A nota de um artigo nunca desce.
- **Custo limitado:** no máximo 4 textos por artigo (o início e 3 passagens) e 40 passagens a mais por pergunta (`--passagens-artigo`, `--passagens-pergunta`). Quando há mais passagens do que o teto, ficam as que têm mais termos em comum com a pergunta. A escolha não usa o excerto do conjunto de avaliação, que o sistema real não conhece.
- **`Resultado.passagem`** guarda a passagem que deu a nota, quando não foi o início. A resposta ainda não a usa: mostra o início do artigo.
- Funciona com `--estavel` (as notas guardadas reutilizam-se) e com `--reranker-com-perguntas`. Testes em `tests/test_modelos.py`, com um modelo falso.

### Medição pequena

Não é a medição das 1.298. São 140 perguntas reais no índice final de 19/11 (16h54), com `scripts/medir_passagens.py`:

- as 48 em que o artigo certo não chegava aos 8 primeiros;
- as 32 dos quatro códigos republicados (Estrada, IVA, IRC, IRS) que não estão nessas 48;
- uma amostra ao acaso de 60 das outras 201 que hoje funcionam.

Cada pergunta correu quatro vezes com o mesmo reranker em modo `estavel` e o limiar 3, sem LLM. Assim a diferença entre as colunas vem só das passagens e das perguntas por artigo, e não do ruído do lote. A coluna «Base» não é igual à medição `app011-final`, que pontua em lotes de 16: a posição do artigo certo difere em 21 das 140, quase sempre por um ou dois lugares.

| Grupo | Medida | Base | Passagens | Perguntas por artigo | As duas |
|---|---|--:|--:|--:|--:|
| As 48 que falhavam | Artigo certo nos 8 | 1 | 14 | 15 | 22 |
| | Artigo certo em 1.º | 0 | 4 | 7 | 9 |
| | Certas | 0 | 1 | 1 | 8 |
| | Respondidas e erradas | 12 | 13 | 12 | 13 |
| Quatro códigos (32) | Artigo certo nos 8 | 32 | 32 | 31 | 32 |
| | Artigo certo em 1.º | 15 | 15 | 27 | 28 |
| | Certas | 6 | 7 | 23 | 25 |
| | Respondidas e erradas | 9 | 9 | 3 | 4 |
| Amostra das que funcionam (60) | Artigo certo nos 8 | 58 | 59 | 60 | 60 |
| | Artigo certo em 1.º | 43 | 44 | 45 | 48 |
| | Certas | 35 | 36 | 40 | 45 |
| | Respondidas e erradas | 11 | 12 | 10 | 9 |

**Só as passagens, contra a base:**

- **Nas 48:** o artigo certo sobe em 15 e não desce em nenhuma. Entra nos 8 primeiros em 13, das quais 9 são falhas reais e 4 são das 7 que o diagnóstico deu como problema do teste. As 10 da causa «corte do reranker» sobem todas e ficam nos 8; 3 ficam em 1.º.
- **Nas 92 que funcionavam:** o artigo certo sobe em 6 e desce em 13. Em 12 das 13 desce um ou dois lugares e nenhuma sai dos 8; a outra (real-227) estava em 9.º e sai dos 10. O 1.º lugar ganha-se em 4 e perde-se em 3 (real-128, real-219, real-297). Ganham-se 3 certas e perde-se 1 (real-128). Uma pergunta que dizia «não sei» passa a responder errado (real-007).
- **Porque descem:** os outros artigos compridos também sobem. Em 8 das 13 descidas, o artigo que fica em 1.º tem a nota de uma passagem.

**As passagens por cima das perguntas por artigo** (da 3.ª coluna para a 4.ª): nas 140, o artigo certo sobe em 19 e desce em 7, entra nos 8 em 8 e não sai em nenhuma. Ganham-se 17 certas e perdem-se 3 (real-031, real-058, real-295, que passam de 1.º para 2.º). Duas passam a responder errado (real-007, real-241).

**O que esta medição não diz:**

- **O limiar.** Com passagens, a nota do 1.º sobe em 34 das 140 perguntas (em média 0,3 nas 140; no máximo 6,2), e o sistema responde a mais perguntas: 78 em vez de 73, e 104 em vez de 89 com as perguntas por artigo. O limiar 3 foi escolhido sem passagens. As perguntas «sem resposta», a que o sistema deve dizer «não sei», não entraram aqui.
- **Os outros tipos de pergunta** (literais, temporais, coloquiais, revogadas) não entraram.
- **A amostra é pequena:** 60 de 201. Uma ou duas perguntas de diferença nas certas ficam dentro do acaso.

### Custo em tempo

- **Textos lidos:** 44,9 por pergunta na base e mais 24,2 passagens em média (mediana 23; 40 no máximo, que é o teto). São 1,54 vezes os textos.
- **Tempo:** 1,54 vezes. Em modo `estavel`, com 3 fios e a máquina ocupada com outras medições, foram 20 s por pergunta na base e 31 s com passagens.
- **Em lotes de 16, como a aplicação pontua, não foi medido.** As passagens têm o tamanho dos outros textos, por isso a razão deve ser parecida: cerca de 11 a 12 s por pergunta em vez de 7 a 8.

### Como medir nas 1.298

```bash
PYTHONPATH=src python -m rag.avaliar --nome passagens-final --indice rag/indice/indice-final.sqlite \
    --reranker cruzado --limiar 3 --sem-llm --reranker-passagens
```

É a configuração da `app011-final` com as passagens ligadas. Com `--reranker-com-perguntas` mede as duas coisas juntas. Para comparar duas medições sem o ruído do lote, juntar `--estavel` às duas, o que demora mais.

## Última milha nas reais: as peças que faltam ligar (20/11/2026)

A aplicação 0.1.1 acerta o artigo em 1.º lugar em cerca de metade das 281 reais, e em mais um terço o artigo certo está do 2.º ao 8.º lugar. Mediu-se quanto se ganha com as peças que já existem e não estão ligadas: as notas estáveis do reranker (`--estavel`), o reranker a ler as perguntas do artigo (`--reranker-com-perguntas`) e o LLM a escrever a resposta a partir dos 8 primeiros artigos.

**Como se mediu:**
- **Índice:** `rag/indice/indice-final.sqlite`, o da medição de base `app011-final`, com as perguntas de 12.154 artigos.
- **Perguntas:** as 281 reais, as 80 «sem resposta» e as 50 de premissa errada.
- **A:** a configuração da aplicação 0.1.1 (reranker em lotes de 16, sem ler as perguntas, limiar 3, sem LLM). É a medição `app011-final`.
- **B:** A com `--estavel`. **C:** B com `--reranker-com-perguntas`.
- **D:** C com o LLM. Uma sessão do Claude (`claude-opus-5-5`) por cada 2 lotes de 10 perguntas, que só lê a entrada: a data, os 8 primeiros artigos e a pergunta. O limiar é 1, o que a aplicação usa com chave (`LIMIAR_COM_LLM`), e o modo é o estrito. Não tem reescrita da pergunta.
- **Juízes da D:** os quatro das compostas (a, b, c e s), às cegas, cada um em sessões próprias e numa pasta só com os seus lotes. Uma resposta é certa só se os quatro a dão como correta e fundamentada.
- **Uma só pesquisa por pergunta:** o `rag.avaliar` e o `rag.passo_llm` guardam e leem as consultas (`--consultas`), por isso o LLM da D viu exatamente a pesquisa medida na C.
- **Contas:** `rag.comparar` (novo), que emparelha pergunta a pergunta com a base e refaz as contas com outros limiares a partir das notas gravadas. Resumos em `rag/resultados/ultima-milha.json`, `um-b.json`, `um-c.json`, `um-c-llm.json` e `um-c-juizes.json`.
- **«Certa» não é o mesmo com e sem LLM.** Sem LLM, é responder com o artigo certo em 1.º lugar. Com LLM, é a resposta escrita que os quatro juízes aprovam.

**Nas 281 reais:**

| Medição | Certas | Respondidas | «Não sei» | Erradas | Artigo em 1.º | Nos 8 primeiros | «Sem resposta» respondidas (de 80) | Premissa errada: certas nas respondidas |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| A: aplicação 0.1.1 | 115 | 185 | 96 | 70 | 140 | 233 | 5 | 23/43 |
| B: A com notas estáveis | 108 | 186 | 95 | 78 | 138 | 231 | 5 | 26/43 |
| C: B com o reranker a ler as perguntas | **149** | 211 | 70 | 62 | 173 | 245 | 7 | 29/45 |
| D: C com o LLM (limiar 1, juízes) | **231** | 241 | 40 | 10 | 173 | 245 | 2 | 45/46 |

«Erradas» são as respondidas que não ficam certas. Na D são as 10 que pelo menos um juiz não aprovou: 6 incompletas, 1 errada e 3 sem fundamento. Em todas houve pelo menos um juiz a aprovar. Com o critério automático das 80 % de palavras, a D teria 199 certas.

**Pergunta a pergunta, face à A,** com as reais agrupadas pelo lugar do artigo certo na A:

| Lugar do artigo certo na A | n | Certas na A | B | C | D |
|---|--:|--:|--:|--:|--:|
| Em 1.º | 140 | 115 | 105 (1 ganho, 11 perdas) | 113 (14 ganhos, 16 perdas) | 130 (23 ganhos, 8 perdas) |
| Do 2.º ao 8.º | 93 | 0 | 3 | **35** | **85** |
| Fora dos 8 primeiros | 48 | 0 | 0 | 1 | 16 |
| **Total** | 281 | 115 | 108 (4 ganhos, 11 perdas) | 149 (**50 ganhos, 16 perdas**) | 231 (**124 ganhos, 8 perdas**) |

- **B:** 10 das 11 perdas são trocas no 1.º lugar entre artigos com notas próximas. O lugar do artigo certo muda em 47 das 281 perguntas e a nota do 1.º resultado muda mais de 0,3 em 29. Pontuar cada texto sozinho não é a mesma conta que pontuar em lotes de 16, e a diferença é maior do que o ruído entre duas corridas em lotes (cerca de 8 perguntas em 1.298, o que dá umas 2 em 281).
- **C:** dos 50 ganhos, em 28 a A não respondia e em 22 respondia com outro artigo. Das 16 perdas, 12 são trocas no 1.º lugar e 4 passam a «não sei». O artigo certo em 1.º sobe de 140 para 173.
- **C nas reais que nunca serviram para afinar** (real-201 a 350, 145): 36 → **60** certas, com 29 ganhos e 5 perdas. Nas 136 afinadas: 79 → 89, com 21 ganhos e 11 perdas.
- **D:** das 8 perdas, 5 são «não sei» do modo estrito (o artigo citado é o texto original de um diploma alterado) e 3 são respostas que um juiz não aprovou. Os 40 «não sei» são 17 do limiar, 12 em que o LLM diz que os artigos não respondem, 8 do texto original e 3 em que a resposta diz que falta a norma. Em 29 dos 40, o artigo certo não estava nos 8 primeiros.
- **«Sem resposta»:** a C responde às 5 da A e a mais 2 de arrendamento (sem-024 e sem-051, as mesmas da medição de 18/11). Na D, 30 das 80 chegam ao LLM, que responde a 2 (sem-069 e sem-071).

**Outros limiares,** só a partir das notas gravadas, sem nova corrida. Na D só se pode subir o limiar: abaixo de 1 o LLM não viu a pergunta.

| Limiar | C: certas / respondidas | C: erradas | C: «sem resposta» respondidas | C: ganhos / perdas | D: certas / respondidas | D: não certas | D: «sem resposta» respondidas | D: ganhos / perdas |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 | | | | | 231 / 241 | 10 | 2 | 124 / 8 |
| 2 | 162 / 246 | 84 | 20 | 61 / 14 | 221 / 231 | 10 | 1 | 115 / 9 |
| 2,5 | 155 / 230 | 75 | 15 | 55 / 15 | 208 / 218 | 10 | 1 | 103 / 10 |
| **3** | 149 / 211 | 62 | 7 | 50 / 16 | 192 / 200 | 8 | 1 | 89 / 12 |
| 3,5 | 145 / 196 | 51 | 5 | 48 / 18 | 181 / 187 | 6 | 1 | 83 / 17 |
| 4 | 138 / 182 | 44 | 3 | 43 / 20 | 169 / 174 | 5 | 1 | 73 / 19 |

O limiar fica 3 no código. Os números servem para quando se decidir: com 3,5, a C tem as mesmas 5 «sem resposta» da A, mais 30 certas e menos 19 erradas. Com o LLM, subir o limiar tira muito mais respostas certas do que erradas (de 1 para 3: menos 39 certas, menos 2 não certas).

**Confirmação da C nas 1.298 perguntas** (`um-c-todas`, com as mesmas consultas guardadas; `rag.comparar --por-tipo`, resumo em `rag/resultados/ultima-milha-todas.json`). As 411 perguntas repetidas deram exatamente o mesmo resultado, como se espera das notas estáveis.

| Tipo | n | Certas (A → C) | Respondidas | Artigo em 1.º | Nos 8 primeiros | Ganhos / perdas |
|---|--:|--:|--:|--:|--:|--:|
| Reais | 281 | 115 → 149 | 185 → 211 | 140 → 173 | 233 → 245 | 50 / 16 |
| Coloquiais | 281 | 23 → 109 | 33 → 137 | 100 → 160 | 179 → 201 | 88 / 2 |
| Literais | 250 | 237 → 240 | 249 → 250 | 238 → 240 | 249 → 249 | 5 / 2 |
| Temporais | 102 | 94 → 92 | 97 → 95 | 96 → 96 | 102 → 102 | 1 / 3 |
| Revogadas | 55 | 55 → 55 | 55 → 55 | 55 → 55 | 55 → 55 | 0 / 0 |
| Texto alterado | 99 | 72 → 73 | 94 → 95 | 84 → 84 | 94 → 94 | 1 / 0 |
| Premissa errada | 50 | 23 → 29 | 43 → 45 | 26 → 31 | 47 → 47 | 7 / 1 |
| Compostas (sem LLM não há certas) | 100 | 0 → 0 | 73 → 78 | — | 60 → 61 | — |
| «Sem resposta» (respondidas por engano) | 80 | — | 5 → 7 | — | — | — |
| **Total** | 1.298 | **619 → 747** | 834 → 973 | 739 → 839 | 1.019 → 1.054 | **152 / 24** |

- **O ganho confirma-se:** mais 128 certas em 1.298, com 152 ganhos e 24 perdas. O ruído entre duas corridas em lotes é de cerca de 8 perguntas.
- **Fora das reais e das coloquiais quase não mexe:** literais, temporais, revogadas e texto alterado somam 7 ganhos e 5 perdas em 506. As temporais perdem 2 no saldo (1 ganho, 3 perdas).
- **As coloquiais sobem muito** (23 → 109), mas foram escritas por sessões do Claude, como as perguntas dos artigos: partilham vocabulário e o ganho nelas está inflacionado. O número mais seguro continua a ser o das reais.
- **«Sem resposta»:** 7 respondidas em vez de 5. Com o limiar 3,5 voltam a ser 5, e as certas no total ficam em 726.

**Custo em tempo.** Tempo de pesquisa por pergunta em 15 reais, com as três configurações alternadas pergunta a pergunta e a máquina carregada por outras medições (por isso só a relação entre elas conta): mediana de 19,6 s na A, 21,4 s na B (+9 %) e 23,6 s na C (+20 %). Com o CPU livre, a A leva 7 a 8 s («Próximos passos»), o que dá cerca de 1,5 s a mais por pergunta na C. O tempo do LLM não se mediu: as sessões não são a API. O prompt da D tem 11,8 mil caracteres em média.

**Ressalvas:**
- O LLM não foi medido sobre a pesquisa da A nem da B. Não se sabe quanto do ganho da D vem do LLM e quanto das perguntas no reranker: a pesquisa só limita a parte dela (o artigo certo nos 8 primeiros passa de 233 para 245).
- A C foi medida com as notas estáveis. A leitura das perguntas com lotes de 16 não se mediu aqui.
- Uma corrida por configuração. O LLM e os juízes são o mesmo modelo e não houve revisão de um jurista.
- 136 das 281 reais serviram para afinar as regras da pesquisa. As perguntas por artigo foram escritas sem ver nenhuma pergunta de avaliação.

**Conclusão:**
1. **O reranker a ler as perguntas compensa, sem chave:** mais 34 certas em 281 (115 → 149), com 50 ganhos e 16 perdas, menos 8 erradas e mais 2 «sem resposta» respondidas, por cerca de 20 % mais tempo de pesquisa. O ganho está muito acima do ruído, é maior nas reais que nunca afinaram e confirma-se nas 1.298 perguntas (619 → 747 certas, 152 ganhos e 24 perdas), sem estragar os outros tipos.
2. **As notas estáveis sozinhas não melhoram:** menos 7 certas (4 ganhos, 11 perdas). Valem porque tornam a medição repetível e as notas comparáveis com um limiar, não pelo número.
3. **O LLM dá o maior salto:** 231 certas em 241 respondidas, e 85 das 93 perguntas com o artigo do 2.º ao 8.º lugar passam a certas. Depende de o utilizador ter chave.


## Próximos passos

Por ordem de ganho esperado:

1. **Passo do LLM** com chave: medir a fiabilidade das respostas escritas e o "não sei" nas perguntas fora do âmbito, que a pesquisa sozinha não reconhece.
2. ~~**Pesquisa semântica nas reais**~~: medida a 19/11 («Candidatos ao reranker e pesquisa semântica»). Traz o artigo certo para os candidatos, mas o reranker não o põe em 1.º. Fica desligada. Continua por fazer: expandir os temas comuns para o código (IVA → CIVA, IMI → CIMI).
3. **Perguntas sobre diplomas alterados sem consolidação** no conjunto de avaliação, para medir o risco principal do plano, que hoje fica de fora.
4. **Trocar `fontes.ler_artigos` pelo parser da fase 3** e reconstruir o índice (5 min); medir outra vez.
5. **Velocidade**: o reranker leva 7 a 8 s por pergunta em CPU; para uso real, um reranker mais pequeno, menos candidatos ou GPU.

### Atos da UE em tradução não oficial (14 e 16/11/2026)

Os 1.244 atos da UE em vigor sem versão portuguesa estão no acervo em tradução não oficial (`version.kind: translation`). Desde 16/11 estão no índice (1.233; as outras 11 ficam de fora por um aviso antigo no registo), a resposta avisa quando cita um deles, e medido não baralham as perguntas gerais: ver "Tipos novos".

### Jurisprudência (estado em 12/11/2026)

1. **Acórdãos do TC de 1983 a 2015.** Recolhidos e no main (12/11/2026): 29.392 dos 29.405 acórdãos de 1983 a 2026; os 13 que faltam são lacunas do site, com o motivo em `reports/tc_failures.jsonl` (o 652/2021 incluído). O `normas-julgadas.jsonl` foi refeito com todos os anos (13/11/2026): 5.773 alíneas, 371 declarações com força obrigatória geral (eram 64). Medido às cegas antes de 2016: 78 % de precisão e 82 % de cobertura das normas (90 % e 88 % em 2016–2026); números e erros no README, em "Normas julgadas pelo Tribunal Constitucional". Falta:
   - repetir a avaliação BM25 com os dados novos (o aviso entra em mais respostas) e experimentar as duas respostas com o LLM;
   - os erros que sobram: listas de artigos apanhadas só em parte, diplomas no plural, o CPP de 1929 ligado ao de 1987, regulamentos e editais antigos que o índice não tem;
   - desde 12/11/2026 os acórdãos novos (e as decisões novas da CNPD e as decisões sumárias) entram na atualização diária, mas o `normas-julgadas.jsonl` não se refaz sozinho: o aviso de inconstitucionalidade só apanha um acórdão novo depois de correr `rag.jurisprudencia` outra vez.
2. **CNPD completa** (13/11/2026): as 122.223 decisões do histórico de 1994 a 2026 estão no main, com as 114.331 autorizações; 70 % com texto. Faltam o OCR das digitalizações (`collect cnpd --without-text` num Mac fora do sandbox, cerca de 36 mil PDF) e decidir se a CNPD entra no índice do RAG.
3. **Datas com gralhas no site do TC.** Corrigidas na recolha (`tc.decision_date`, 12/11/2026): eram 85 em 1983–2026, não 30, contando as do ano anterior em acórdãos de janeiro (`2000-01-17` nos 7 a 16/2001). Quando o ano da listagem não é o do número, vale a assinatura do acórdão ("Lisboa, 18 de fevereiro de 2025"): 83 ficaram com a data certa e uma nota, 2 sem data (355/1998 e 58/2004). A guarda de `rag.jurisprudencia` pode ficar: já não apanha nenhuma.
4. **Experimentar as duas respostas com o LLM.** Só foram vistas sem LLM (não havia chave na sessão): ver se o aviso de inconstitucionalidade aparece bem na resposta escrita.
5. **Diplomas citados por um nome que o índice não reconhece.** É a maior parte das falhas da extração (regulamentos, estatutos, a Lei de Organização e Funcionamento dos Tribunais Judiciais…): ficam sem diploma. Resolver pelo sumário ("Aprova o Regulamento…") tendo em conta a data do acórdão, e medir outra vez.
6. **Decisões sumárias do TC.** Recolhidas (13/11/2026, `collect tc --sumarias`, `decisoes-sumarias/`): 5.320 das 5.335 listadas, de 1998 a 2026; ficam fora do `normas-julgadas.jsonl` até se medir a extração nelas. As 15 que faltam são páginas vazias no site (`reports/tc_sumarias_failures.jsonl`).
7. **Mais tarde:** STJ e STA (bases do ITIJ, dgsi.pt) só depois de a segunda resposta estar medida; o TC foi notificado em 12/11/2026, à espera de resposta.

## Redações anteriores: cópias antigas do mesmo texto (20/11/2026)

O DRE consolida alguns códigos no registo da lei que os republicou (o Código da Estrada na Lei n.º 72/2013), consolida diplomas de alteração que trazem a republicação de outro (o DL 44/2005) e guarda o texto de origem (o DL 114/94). No índice, todas essas cópias ficavam como texto atual: o Código da Estrada estava lá cinco vezes.

`rag/copias.py` junta as cópias de cada texto e diz quais são redação anterior. Uma cópia só é marcada com duas provas:

1. **É o mesmo texto:** as epígrafes coincidem e uma parte dos artigos tem o mesmo texto (30 %, ou 10 % quando 30 ou mais epígrafes coincidem), e um dos diplomas cita o outro; ou o DRE o diz numa nota; ou o anexo cita o diploma.
2. **Há outra cópia mais recente:** outra cópia tem uma nota «Alterado pelo/a…» com data posterior, ou é a republicação trazida por um diploma que o DRE regista como alterador e publicado depois. Uma data de publicação diferente não chega.

O `rag.indice` usa as marcas ao construir (por omissão; `--sem-redacoes-anteriores` desliga, para medir):

- os pedaços abertos da cópia ficam com `ate`, a data da prova mais antiga. Respondem a perguntas com data anterior, com o aviso «Redação em vigor de … a …, não a atual», e deixam de responder como texto atual;
- só fecham os artigos da cópia, pela chave e pelo texto: os artigos do decreto que aprova ou republica, que partilham a parte e as chaves, ficam abertos;
- nos registos em blocos de texto (o IVA de 1984), fecham os blocos a seguir àquele onde o código começa;
- a ligação para o registo com o texto atual é `texto_em_vigor_em` quando o registo fica sem artigos abertos, e `redacao_atual_em` quando ficam os do próprio diploma: a pesquisa troca artigos pelo número só no primeiro caso.

`python -m rag.copias` grava `reports/redacoes-anteriores/`: `marcadas.jsonl` (com a prova de cada uma), `de-fora.jsonl` (com o motivo) e `resumo.json`. A 20/11: 536 cópias marcadas em 493 registos e 345 de fora; num índice de ensaio só com esses registos, 43.596 pedaços fechados. Falta medir nas 1.298 perguntas.

## O que o índice lê de um registo (20/11/2026)

O inventário da camada 1 (`reports/inventario-camada-1.md`, secção 8) encontrou texto que o índice não lia como artigos, ou lia mal. Três correções, todas no código que lê os dados; o `data/` não muda.

**1. Histórico sem artigos (`rag/indice.py`).** Um consolidado com histórico de versões e sem `###### Artigo` ficava sem nenhum pedaço. Agora cada versão sem artigos entra em blocos de texto, com o intervalo em que vigorou, e se o histórico não der nada lê-se o `.md`.

**2. Mais unidades e anexos (`avaliacao/comum.py`, que o índice usa).**

- `###### ARTIGO 1.º`, em maiúsculas, lê-se como artigo (leis e decretos de 1970 a 1989).
- `###### Base IV — Epígrafe` é uma unidade com o número «Base IV»; `###### 1.º` (os números das portarias) fica «N.º 1.º». O rótulo diz «Base IV» e não «Artigo Base IV». A pesquisa lê «base IV da Lei n.º 52/2012» (`rag/referencias.py`).
- `## ANEXO` em maiúsculas abre parte quando tem artigos, como `## Anexo`. Os artigos do anexo deixam de ficar na parte do diploma, com as mesmas chaves que os dele.
- **O nome da parte:** com título, o título vem à frente. `## ANEXO — CÓDIGO DE PROCESSO PENAL` é a parte «CÓDIGO DE PROCESSO PENAL (ANEXO)». A pesquisa (a de hoje e a da aplicação 0.1.1) procura os códigos nas partes que começam por «Anexo», sem olhar a maiúsculas. Com «ANEXO — Código de Processo Penal», uma pergunta que cite o código passava a receber a republicação de 2007 (verificado com o código da 0.1.1).
- **Sem artigos, um `## ANEXO` fica onde estava:** o texto continua colado ao artigo anterior. Experimentei pô-lo em blocos na parte do anexo: eram 188 mil blocos novos (tabelas, regras, listas) a competir com os artigos, e o artigo certo saía dos dez primeiros em perguntas que antes acertavam.

**Salvaguardas, para nenhum texto sair do índice:**

- um registo quase todo em texto corrido, com dois ou três títulos soltos em maiúsculas (o Código Penal de 1982 no DL 400/82), não se parte por eles: fica inteiro em blocos, como antes;
- nos registos em que nenhum artigo vem de um `###### Artigo` (antes entravam inteiros em blocos), o texto fora dos artigos e o que passa dos 30.000 caracteres de um artigo entram em blocos.

**3. Revogação com data de efeitos (`rag/fontes.py`).** `revogado(texto, notas, data)` só conta uma nota «Revogado pelo/a…» a partir do dia em que produz efeitos: a mais tardia das datas da própria nota («em vigor», «com efeitos», «produz efeitos a partir de»). A Lei n.º 13/2003 foi revogada em agosto de 2026 com efeitos a 31/12: até lá os artigos saem como em vigor, com o aviso «Em vigor até à véspera de 2026-12-31…». A data vem sempre escrita na nota do DRE; nenhuma é inferida. Sem data na nota, conta como revogado, como antes.

**As chaves das perguntas de avaliação.** 58 das 1.620 fontes esperadas apontam para artigos de anexos em maiúsculas, que mudam de chave («13.º» passa a «… (ANEXO)::13.º»). `rag.fontes.acertar_fontes`, chamado por `rag.avaliar.ler_perguntas`, acerta a chave em memória pelo número e pela epígrafe; os ficheiros das perguntas ficam como estão. Um índice construído antes desta data tem as chaves antigas: mede-se com o código dessa altura.

**Antes e depois,** pelos pedaços que o código dá a cada registo do export de 20/11 (357.225 registos):

| | Antes | Depois |
|---|--:|--:|
| Pedaços | 2.533.936 | 2.582.317 |
| Abertos com número (artigos, bases, números) | 1.706.670 | 1.742.579 |
| Abertos em blocos | 611.586 | 609.789 |
| Fechados (redações anteriores) | 215.680 | 229.949 |
| Registos que mudam | | 12.597 |

Por correção, nos registos em vigor no DRE:

- **histórico sem artigos:** 2.343 registos passam de nenhum pedaço para 12.015 abertos (984 com número);
- **«ARTIGO»:** 1.538 registos passam de 18.124 blocos para 22.679 artigos e 7.105 blocos; mais 873 artigos em 48 registos que já tinham alguns;
- **bases e números:** 1.920 bases e 1.040 números abertos no índice inteiro (a Lei n.º 52/2012 passa de 0 pedaços para 35 bases);
- **`## ANEXO`:** 59.062 artigos de 1.951 registos passam para a parte do anexo (e 109.689 de 3.404 registos de vigência desconhecida); as chaves repetidas nesses registos descem de 14.419 para 2.071.

**Verificado num índice de ensaio** (12.120 registos: os da avaliação, os 198 centrais, os das redações anteriores, os que mudam e 4.000 ao acaso), antes e depois:

- nenhum dos 198 diplomas centrais perde artigos abertos; os nomes de códigos resolvem-se para os mesmos registos; entra um registo nos códigos principais (DL 44561, Código do Imposto de Capitais de 1962, que passa dos 60 pedaços);
- a regra das redações anteriores não perde nenhuma marca (536 → 558, por ver melhor as republicações em anexos);
- as perguntas por artigo encontram os mesmos artigos (127 em falta, antes e depois);
- só com BM25 e referências, sem reranker nem LLM, o artigo esperado fica em 1.º em 845 → 844 de 1.414 perguntas e nos dez primeiros em 1.185 → 1.182 (20 sobem, 32 descem);
- com o código da aplicação 0.1.1: o esquema é o mesmo, a pesquisa corre, e um delta gerado hoje e aplicado por ela dá o mesmo índice que a construção de raiz.

**O que a aplicação 0.1.1 não ganha:** a correção 3 está no código. A 0.1.1 calcula a revogação com o código dela e continua a dar os artigos da Lei n.º 13/2003 como revogados, até haver versão nova.

**Reconstruir:** `python -m rag.indice`, como sempre. Não há opções novas. Depois, `python -m rag.jurisprudencia` volta a escrever as normas julgadas com as partes novas (6 das 2.713 normas apontam para artigos que mudaram de parte; a pesquisa de hoje aceita as duas formas).

**Falta medir** nas 1.298 perguntas com o reranker. O que ficou por ler (texto corrido com «Artigo 1.º … Art. 2.º …», bases soltas como as da Lei n.º 95/2019) está em `reports/leitura-texto-corrido-amostra.md`.
