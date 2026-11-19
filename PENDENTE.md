# Pendente para segunda-feira (16/11/2026)

O plano semanal do Claude estava a 98 % no sábado (14/11) e renova-se na segunda, por volta das 4h.
Por ordem: primeiro o que gasta pouco, depois o que precisa de modelos.

## 1. Três diplomas consolidados por confirmar: feito (16/11)

Os três estão certos no texto, e o parser lê bem. Os pormenores estão no `consolidacao/README.md`.
A chave «212.º» do DRR 2/2005/M é uma gralha do próprio DRE.

**Gralhas do DRE na numeração dos artigos: corrigidas (16/11).** Eram 138 suspeitas em 119
diplomas. Ficaram corrigidos 78 títulos em 73 diplomas: 44 gralhas isoladas e 34 números
repetidos. Cada um tem uma nota em `notes` com o número que o DRE escreve. A lista está em
`reports/numeracao_artigos_corrigidos.jsonl`. As regras estão em `consolidacao/README.md`.
- A recolha do DRE já corrige as gralhas isoladas dos registos novos, mas não os repetidos. Se um
  dos 34 repetidos voltar a ser recolhido, perde a correção: corre-se outra vez
  `scripts/corrigir_numeracao.py --repetidos --escrever`.
- Sobram 56 suspeitas, todas com o motivo em `reports/numeracao_artigos_suspeitas.jsonl`. Quase
  todas são artigos citados de outros diplomas, números de anexos diferentes ou atos de alteração,
  e não gralhas. Das 10 da UE, nenhuma é uma gralha do EUR-Lex.
- **Artigos com a letra separada: feito (16/11).** Os dois leitores de artigos passaram a ler
  «Artigo 78.º A» e «Artigo 292.º ‐A» (hífen U+2010 do EUR-Lex) como o artigo 78.º-A. São eles o
  `domain/articles.py` e o `avaliacao/comum.py`, que é o do índice do RAG. Antes, o texto destes
  artigos colava-se ao artigo anterior.
  - Com o `articles.py`, ganham-se 144 artigos em 45 registos: 80 de Portugal e 64 da UE.
  - Com o leitor do RAG, ganham-se 140 artigos em 39 registos.
  - Nenhum registo perde artigos. No Aviso n.º 17262/2018, as três unidades «1.º, 2.º, 3.º» davam
    lugar ao art. 82.º-B, que as contém.
  - O `data/` não mudou: só a leitura.
- **Os dois leitores de artigos alinhados: feito (16/11).** Em 1.751.984 títulos `###### Artigo`, os dois
  leitores dão agora o mesmo número em 1.748.096. Antes, divergiam em cerca de 38 mil.
  - **No RAG, 62.402 artigos mudam de chave em 12.516 registos** (55.598 da UE e 6.804 de Portugal). Passam à
    forma das perguntas: «1o», «1g.», «1º.», «1°», «1.», «1», «3. º», «12.ºA» e «3.º–EA» ficam «1.º», «12.º-A»
    e «3.º-EA». A pesquisa procura o artigo pelo número exato, por isso uma pergunta pelo «artigo 1.º» não
    encontrava, por exemplo, os 17 mil artigos «1o» dos atos antigos do EUR-Lex.
  - **No RAG, entram 2.805 artigos** com números compostos dos regulamentos («A/1 - 5.º», «C - 1/4.º») ou
    sem espaço («Artigo12.º»). Saem 4 títulos (como «Artigo Anexo I»), cujo texto passa para o artigo
    anterior.
  - **O `articles.py` lê mais 35.131 artigos** (21.803 da UE): os «1o», «1g.», os aditados com a letra junta e
    os compostos. 3.708 registos que não tinham nenhum artigo passam a tê-los. Só 6 se perdem, nos
    Editais 510/2017 e 790/2018: os números 1.º–5.º eram os n.ºs do artigo D-4/24.º, que agora os contém. Só no Edital 189/2011 mudam ids de forma relevante: os 243 «art-c-N»
    passam a «art-c-1-N-o».
  - Ficam diferentes 2.117 títulos. 1.055 só o RAG lê, e com a chave de antes: são títulos estranhos
    como «Artigo Segundo», «Artigo A» ou «1쨘» (com a codificação errada). 1.056 só o `articles.py` lê:
    quase todos têm a epígrafe depois de um hífen («Artigo 87.º - Ensaios.»), e o RAG continua a não a
    ler. Nos decretos antigos com essa forma, os outros artigos estão em texto corrido antes do título,
    e o índice perdê-los-ia.
  - Nas perguntas da avaliação da UE, 25 chaves passaram à forma nova («1º» → «1.º»). Todas existem no
    registo com o leitor novo.
- O índice e o relatório do `structure` (`--dry-run`) foram refeitos a 16/11: ver o ponto 3.

## 2. Atos da UE em vigor: feito (16/11)

Lista do CELLAR refeita a 16/11: 34.213 atos em vigor, todos no acervo (32.969 com versão
portuguesa oficial e 1.244 em tradução não oficial). Os 30 que faltavam, caso a caso, em
`reports/eurlex_em_vigor_30.md`:

- **23 sem versão portuguesa** no CELLAR, que não estavam no relatório de 11/11: traduzidos como
  os 1.218 (o 3481/80 a partir do italiano, porque o texto inglês do CELLAR é o do 3479/80).
- **3 com a expressão portuguesa sem ficheiros** (só `print`): traduzidos do inglês ou do francês
  (o 30/65/CEE a partir do PDF francês).
- **4 com o número oficial repetido:** gravados com o CELEX no nome do ficheiro.

Verificação às cegas das 26 traduções: 2 erros graves, corrigidos antes de gravar.

**Número oficial errado do CELLAR: corrigido (16/11).** Corrige-se o `official_number`, e o caminho
fica onde está, porque o repositório encontra os registos pelo id (o CELEX). Só se corrige quando
duas fontes concordam contra o CELLAR. Foram 13 decisões, listadas em
`reports/eurlex_numero_oficial_corrigido.jsonl`, cada uma com uma nota em `notes`:
- 10 do BCE com o ano da adoção em vez do ano do Jornal Oficial (2006/48 → 2007/48, 2018/47 →
  2019/47…). O título e o ano da publicação concordam.
- A Decisão (UE) 2016/1717 do BCE, que estava com o número interno (BCE/2016/27).
- A 2016/775 (o CELLAR dava 2016/776) e a 85/269/CEE (dava 1985/1519). O título e o CELEX concordam.

Os outros 40 atos em que o título discorda do número ficam como estão: aí a gralha é do título, e o
CELEX confirma o número (por exemplo, a «Directiva 2010/45/UE» é a 2010/53/UE). A recolha do EUR-Lex
aplica a mesma regra (`official_number` em `sources/eurlex/mapper.py`), por isso a correção não se
perde quando um registo volta a ser recolhido. **Na pesquisa, só conta a partir da próxima
reconstrução do índice:** o de 16/11 ainda tem os números antigos.

## 3. RAG: feito (16/11)

Os números estão no `rag/README.md`, «Tipos novos».

- **Índice reconstruído (16/11)** com o export de 16/11: 267.084 diplomas e 1.576.082 pedaços (eram
  246.506 e 1.484.508). À noite, outra vez, com a 2.ª Série só pela referência (abaixo). Os
  inteiros estão todos na forma «N.º», e nenhuma chave tem o hífen U+2010.
  Teste: «artigo 1.º da Diretiva 88/361/CEE» dá o artigo certo em primeiro lugar (no registo, o
  título é «Artigo 1g.»).
- **Medido no índice novo:** a pesquisa fica igual nas 1.298 perguntas, com os mesmos totais por tipo,
  e só 3 mudam de posição abaixo do 1.º lugar. Nenhum ato traduzido aparece em 1.º lugar, nem
  nessas nem nas 167 da UE.
- **As traduções ficam no índice**, e a resposta avisa quando cita uma (`AVISO_TRADUCAO`).
- **As 11 traduções que faltavam já estão no índice** (1.244). Eram os atos cujo original só existia
  em PDF e que guardavam o aviso da recolha «liga apenas ao PDF oficial». O aviso saiu dos 11
  registos (2b0de97), e o passo da tradução já não o grava.
- **TC 1983–2026:** a avaliação BM25 foi repetida. Entram 2 avisos novos, ambos certos, e nada piora.
  O aviso passou a dizer «ilegal» nas 17 declarações que são só de ilegalidade.
- **2.ª Série:** 54 perguntas verificadas às cegas (`avaliacao/perguntas-serie-ii.jsonl`).
  - Fora do índice, dão 0 %. Dentro, o artigo certo vem em 1.º lugar em 65 % só com BM25 e em 89 %
    com o reranker.
  - Mas, só com BM25, as perguntas reais pioram um pouco: 200 → 192 com o artigo nos 10 primeiros.
  - Com o reranker, as reais pioram: 120 → 115 no 1.º lugar. Em 12 delas, o 1.º lugar passa a ser um
    regulamento ou acordo coletivo da 2.ª Série sobre o mesmo tema.
  - **Só pela referência** (hoje a omissão do `rag.indice`): os atos entram, mas só se encontram
    quando a pergunta os cita. Com o reranker, as 54 dão 91 % em 1.º lugar, e as reais ficam como sem
    a 2.ª Série: 120 no 1.º lugar e 105 certas (eram 101). Só com BM25, as reais perdem um pouco
    (200 → 193 nos 10 primeiros), pelas estatísticas do BM25.
  - **Decisão: o índice de uso passa a ser assim.** Reconstruído na noite de 16/11: 357.148 diplomas, dos
    quais 90.053 só pela referência.
  - **Antes de publicar no Hugging Face, lançar a aplicação nova.** A 0.1.0 não conhece a tabela
    `so_referencia` e poria a 2.ª Série na pesquisa geral. `rag.dados publicar` recusa este índice sem
    `--com-so-referencia`.
  - A perda só com BM25 foi medida outra vez a 18/11: 10 respostas certas em 1.298 (4 reais no
    1.º lugar). A aplicação usa sempre o reranker, onde a perda não aparece, por isso fica como está,
    sem tabela de pesquisa à parte (mudaria o formato do índice).
- **Candidatos ao reranker e pesquisa semântica (19/11):** nas 1.298 perguntas, 15, 30 e 50 candidatos dão
  617, 614 e 608 certas, e a semântica 611 contra 613. Tudo dentro do ruído do reranker: a nota de um texto muda até 0,6
  com os outros textos do mesmo lote (o modelo é int8), e duas medições da mesma configuração diferem em 8 perguntas.
  **Fica 30 candidatos e a semântica desligada.** Antes de decidir limiares (como o de 3,35 das perguntas por artigo),
  tornar as notas estáveis. Ver «Candidatos ao reranker e pesquisa semântica» no `rag/README.md`.
- **CNPD:** não está no índice nem no RAG. O TC chega às respostas pelo `normas-julgadas.jsonl`.
- **Modo sem IA (17/11):** mostra os 3 artigos mais prováveis, cada um com o âmbito («Função
  pública», «Regime geral»…). Numa pergunta que não fala da função pública, a lei geral passa à
  frente dos regimes da função pública, e as portarias e despachos de antes de 1990 ficam atrás.
  Com o reranker, as reais passam de 108 para 112 certas, e nada piora. Também passaram a contar
  como em vigor os artigos repostos depois de revogados (159, entre eles o arrendamento do Código
  Civil). Ver «Modo sem IA» no `rag/README.md`.

## Compostas: mais artigos no contexto do LLM (medido a 19/11: fica 8)

Os números estão no `rag/README.md`, em «Compostas: 8 contra 16 artigos no contexto, com o LLM e os juízes».

- **Medido** com uma só pesquisa por pergunta (índice de 17/11 numa cópia fixa), o LLM e os quatro juízes às cegas. Certas
  pelos juízes, com 8 e com 16 artigos:
  - compostas (100): 72 → **79**, com 7 ganhos e 0 perdas; erradas 5 e 5; fiabilidade 94 % nos dois;
  - premissa errada (50): 45 → 46, com 1 ganho e 0 perdas; mais uma incompleta com 16 (2 contra 1);
  - sem resposta (80): recusa 79 → 78 (com 16 responde à sem-076).
- **Reais (100, semente 16), medidas a pedido do João:** certas 91 e 91; não certas 2 → 4; fiabilidade 98 % → 96 %.
  Há 3 ganhos (artigo em 10.º ou 11.º) e 3 perdas. Duas das perdas têm o artigo em 1.º lugar e são, provavelmente, variação.
- **Decisão: fica 8** (`ARTIGOS_NO_CONTEXTO`). A regra era mudar se as reais não piorassem mais do que 1 em 100, e pioraram 2.
  Se se quiser voltar a isto, o passo seguinte é medir a variação: repetir as mesmas 100 reais com 8 artigos e ver quantas
  mudam sozinhas. Sem isso, não se sabe se os 2 erros a mais são do contexto.
- **À parte, para a pesquisa:** ~~subir o `maximo` do reranker~~. Medido a 19/11: com 50 candidatos, as compostas com
  os artigos nos 10 primeiros vão de 64 para 61, e as certas no total descem de 614 para 608. Fica 30 (`rag/README.md`,
  «Candidatos ao reranker e pesquisa semântica»).

## 4. OCR da CNPD: feito (15/11)

36.197 decisões com texto por OCR; ficam 311 sem texto. Validação sem erros e commit no main.

## 5. À espera de terceiros

- **TC e CNPD:** a resposta ao pedido de confirmação da reutilização, notificados a 12/11/2026.
- **Chave da API:** para testar as respostas escritas com o LLM.

## 6. Perguntas de leigo por artigo (piloto, 16/11)

Os números estão no `rag/README.md`, «Perguntas por artigo».

- **Feito:**
  - 3.078 perguntas de leigo para os 765 artigos em vigor do Código do Trabalho, do NRAU e do arrendamento do Código Civil (`rag/perguntas_artigo/`), escritas por 22 sessões do Claude às cegas das perguntas de avaliação;
  - o código para as juntar ao índice (`rag.indice --com-perguntas`, desligado por omissão) e para as levar nos deltas, com testes.
- **Medido:** nas 155 perguntas do âmbito que nunca afinaram, o artigo certo em 1.º muda assim:
  - com BM25, 15 % → 55 %;
  - com o reranker, 26 % → 44 % (+18 pontos; 31 ganhos, 3 perdas), sem mudança fora do âmbito;
  - com o reranker a ler também as perguntas, 26 % → 71 %, com o «não sei» de 75 % para 28 %.
- **Medição completa (18/11), com o `fontes.revogado` corrigido:** com o reranker a ler as perguntas, 30 % → 76 % em 1.º e 54 % → 83 % de certas nas respondidas (21/39 → 99/120). Fora do âmbito não muda nada. Nas «sem resposta», responde em 8 de 105 em vez de 5: são 3 de arrendamento, com notas logo acima do limiar 3.
- **Decisão: alargar aos outros códigos** (critério de +10 pontos cumprido). Por fazer:
  - ~~medir a variante do reranker com perguntas fora do âmbito e nas «sem resposta»~~ (feito a 18/11); decidir se os artigos com perguntas levam um limiar mais alto (≈ 3,35 tira as 3 a mais e custa umas 7 certas no âmbito);
  - ~~rever a lista dos códigos principais~~ (feito a 19/11: 37 blocos em `OUTROS_CODIGOS`, 11.418 artigos, 327 lotes; ver `rag/README.md`, «Alargamento aos outros códigos principais»);
  - ~~gerar as perguntas dos outros códigos~~ (feito a 23/11): 327 lotes validados, 11.389 artigos e 42.392 perguntas em 37 blocos. Com o piloto, são 12.154 artigos e 45.470 perguntas. Um lote falhou a validação e foi repetido (o 280). A pasta de trabalho é `.cache/perguntas-codigos/`, no worktree `gigante-dec-45205-42125e`.
  - **Para a reconstrução:** 30 artigos do decreto que aprova o Código Penal, o de Processo Penal e o do Registo Predial têm a chave de artigos do código e saíram do âmbito. Mas o `juntar_perguntas` junta as perguntas a todos os pedaços com essa chave, por isso o «Artigo 1.º» do decreto também as recebe.
  - pôr as perguntas no índice de uso;
  - publicar só depois de lançar a aplicação que sabe apagá-las nos deltas (`publicar --com-perguntas`).
- **Achado:** `fontes.revogado` dá como revogados 50 artigos em vigor do Código Civil (1064.º–1113.º), por causa de notas antigas «Revogado pelo…» seguidas de «Aditado/Alterado». Corrigido no main a 17/11.

## 7. Consolidação, bloco 3 (ronda 114): feito (19/11)

Os pormenores estão no `consolidacao/README.md`, «8. Repedir com os reparos e segunda leitura jurídica».

- **Feito:** dos 107 repedidos com os reparos, 51 chegaram à verificação às cegas e 36 passaram (um ficou igual ao original). A segunda leitura jurídica (Opus) dos 35 deu 10 certos, 20 com reparos e 5 em dúvida. **Entraram 6 no `data/`** (2.767 no total), no `main` a 19/11. Os outros 29 ficaram em `acervo.DE_FORA`; os 12 que saíram só por vigência voltaram a entrar a 19/11, com a marca.
- **Falta (fora desta sessão):**
  - export e reconstrução do índice com o bloco 3, a cargo da sessão coordenadora;
  - medir o texto alterado antes e depois.
- **Os dois achados, resolvidos a 19/11** (`reports/auditoria-consolidados.md`; `consolidacao/README.md`, secções 9 e 10):
  - **Retificações fora da cadeia.** Das 243 por aplicar, 145 aplicadas: 67 por regra e 78 com o LLM, todas verificadas às cegas. O estado de cada uma está em `consolidacao/auditoria/retificacoes-estado.jsonl`. A fuga está fechada: `corrected_by` conta como alterador nas próximas rondas.
  - **Vigência.** Não se tiram consolidações por vigência. A marca `consolidacao/auditoria/vigencia-revista.jsonl` tem 155 `nao_vigora` e 184 `regime_anterior`, e o RAG dá o aviso. Os 12 do bloco 3 voltaram a entrar no `data/`.
- **Falta:**
  - export e reconstrução do índice com os 140 registos retificados e os 12 de volta; a cargo da sessão coordenadora;
  - copiar `vigencia-revista.jsonl` para a pasta do índice ao publicar no HF;
  - medir o aviso e, à parte, `RAG_VIGENCIA_PRIOR=1`;
  - aplicar as 66 renovações de caça de `alteradores-em-falta.jsonl`;
  - as 7 retificações reprovadas às cegas;
  - as 595 dúvidas de vigência e os 140 incertos, se valer a pena.
