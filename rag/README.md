# Protótipo de RAG: o ponto de partida

Um RAG razoável sobre o acervo, medido com o [conjunto de avaliação](../avaliacao/README.md) (593 perguntas verificadas às cegas). É o ponto de partida da fase 4 do [plano](../PLANO-RAG.md): quanto acerta hoje, por tipo de pergunta, antes das fases 2 (texto em vigor) e 3 (artigos, vigência e datas).

Medido em 27/10/2026, sobre o acervo do commit `3cbc718` e o export de 26/10/2026; a versão com reranker foi medida outra vez depois de a referência exata passar a candidata. **Sem LLM**: não havia chave da API da Anthropic no ambiente, por isso mede-se a pesquisa e uma resposta extrativa (o primeiro artigo encontrado, com os avisos).

## Resumo

Com pesquisa por referência, BM25 e um reranker multilingue local, o artigo certo vem em 1.º lugar em 96% das perguntas literais, 95% das temporais e em todas as revogadas, mas só em 46% das reais. Quando o artigo certo vem, a redação é sempre a da data da pergunta, e as 55 revogadas trazem o aviso de revogação com o diploma revogatório certo.

| Tipo | n | Artigo certo em 1.º | Nos 5 primeiros | "Não sei" (limiar 3) | Fiabilidade sem LLM (limiar 3) |
|---|--:|--:|--:|--:|--:|
| Literais | 250 | 96% | 99,6% | 0% | 96% (240/250) |
| Temporais | 102 | 95% | 100% | 6% | 98% (94/96) |
| Revogadas | 55 | 100% | 100% | 0% | 100% (55/55) |
| Sem resposta | 50 | — | — | 94% | — (3 respondidas, erradas) |
| Reais (FAQs) | 136 | 46% | 78% | 20% | 52% (57/109) |
| **Total** | **593** | **84%** ¹ | **94%** ¹ | **13%** | **87% (446/513)** |

¹ Nas 543 perguntas com fonte (sem as 50 sem resposta).

- **Ainda longe dos 95%**: 87% de respostas certas nas dadas, com 13% de "não sei". Sem as reais, 96%; nas reais, 52%.
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

Só com as regras da pesquisa (diploma citado que não está no acervo, ano futuro), o sistema diz "não sei" em 10 das 50 sem resposta (as 6 sobre leis que não existem e 4 das 5 sobre o futuro) e responde a quase tudo o resto: fiabilidade de 78% (455/583).

Com um limiar na pontuação do reranker para o melhor artigo:

| Limiar | "Não sei" nas que têm resposta | "Não sei" nas sem resposta | Fiabilidade (certas/respondidas) |
|--:|--:|--:|--:|
| sem limiar | 0% | 20% | 78% (455/583) |
| 0 | 1% | 74% | 83% (455/550) |
| 2 | 3% | 88% | 85% (452/530) |
| 3 | 6% | 94% | 87% (446/513) |
| 4 | 12% | 96% | 88% (423/480) |

A pontuação do reranker separa bem as perguntas sem resposta, mas pouco os erros das reais: o reranker acha relevante um artigo do diploma errado sobre o mesmo tema. O resto tem de vir do LLM (ler o artigo e ver se responde) e de melhor pesquisa.

### Com LLM

Não medido: não havia `ANTHROPIC_API_KEY` no ambiente. O código está pronto (`resposta.py`, `avaliar.py` sem `--sem-llm`); com chave, a medição dá a fiabilidade das respostas escritas (o artigo citado é o certo e a resposta tem o mesmo sentido que a certa, pela comparação de `avaliacao/verifica.py`) e a taxa de "não sei".

## Principais tipos de erro (com reranker)

Nas literais, temporais e revogadas o artigo certo falha o 1.º lugar em 15 perguntas:

| Erro | Literais | Temporais | Revogadas | Total |
|---|--:|--:|--:|--:|
| Diploma certo, artigo vizinho | 6 | 2 | 0 | 8 |
| Outro diploma (sobretudo o que alterou o certo) | 4 | 3 | 0 | 7 |

- **Artigo vizinho**: "Na mediação dos julgados de paz (Lei n.º 78/2001), quem escolhe o mediador?" (`lit-202`) dá o artigo 32.º (seleção dos mediadores) em vez do 51.º.
- **O diploma que alterou o certo**: "Na dependência de que membro do Governo funciona a Comissão Nacional da Reserva Ecológica Nacional?" (`lit-022`) dá o artigo 28.º do DL 239/2012, que alterou o regime, e não o do DL 166/2008; "Em outubro de 2009 … professor auxiliar …" (`tmp-051`) dá o DL 205/2009, que alterou o Estatuto da Carreira Docente Universitária.
- **Reais**: 73 das 136 não têm o artigo certo em 1.º; em 67 o primeiro é de outro diploma. Usam palavras do dia a dia e quase nunca citam o código (só 3 das 136 têm uma referência que o sistema reconhece), e o BM25 traz diplomas sobre o mesmo tema (portarias, regimes especiais, leis antigas). Em 28 o artigo certo nem chega aos 10 primeiros.
- **Sem resposta**: sem LLM, só as leis inexistentes e o futuro dão "não sei" pelas regras. As que pedem aconselhamento, jurisprudência ou lei estrangeira, ou citam um diploma que não trata do assunto, recebem um artigo parecido ("Quantos dias de férias tem um trabalhador em França?" dá o Código do Trabalho de 2003). Com o limiar 3 ficam 3: duas de jurisprudência (`sem-002`, `sem-008`) e uma de um diploma que fixa o capital de uma sociedade concreta (`sem-009`).
- **Códigos**: há vários anexos com o nome de cada código (republicações nas leis de alteração, que o DRE também consolida). A primeira versão escolhia o anexo de republicação da Lei 59/2007 para o Código Penal; escolher o diploma em vigor, com histórico e com mais artigos em vigor nesse anexo acerta em todos os códigos verificados.

## Próximos passos

Por ordem de ganho esperado:

1. **Passo do LLM** com chave: medir a fiabilidade das respostas escritas e o "não sei" nas perguntas fora do âmbito, que a pesquisa sozinha não reconhece.
2. **Pesquisa semântica nas reais**: embeddings só dos diplomas em vigor consolidados e dos códigos (uma fração do acervo, cerca de 1 h a indexar), juntos ao BM25, para que o artigo certo chegue aos candidatos; e expandir temas comuns para o código (IVA → CIVA, IMI → CIMI).
3. **Perguntas sobre diplomas alterados sem consolidação** no conjunto de avaliação, para medir o risco principal do plano, que hoje fica de fora.
4. **Trocar `fontes.ler_artigos` pelo parser da fase 3** e reconstruir o índice (5 min); medir outra vez.
5. **Velocidade**: o reranker leva 7 a 8 s por pergunta em CPU; para uso real, um reranker mais pequeno, menos candidatos ou GPU.
