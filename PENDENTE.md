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
- Falta o índice, e o `structure` só para o relatório: ficam para a reconstrução do ponto 3. Na
  reconstrução, entram as chaves novas (`78.º-A`, `1.º` em vez de `1o`), e as que tinham o hífen
  U+2010 passam a «-».

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

Fica por decidir: o número oficial errado que o CELLAR dá a algumas decisões, como as do BCE
(2006/48 em vez de 2007/48) e a 32016D0775 (2016/776 em vez de 2016/775). Corrigi-lo muda o
caminho de registos que já existem.

## 3. RAG

- **Reconstruir o índice** para entrarem as 1.244 traduções da UE. Usa só o PC.
- **Mostrar na resposta o `version.label`** («Tradução não oficial … sem valor jurídico») quando
  se cita um ato traduzido.
- **Decidir se as traduções ficam no índice:** quase todas são decisões antigas dirigidas a outros
  Estados e podem baralhar perguntas gerais.
- **Medir os tipos novos:**
  - a 2.ª Série, a CNPD e o TC (`--com-serie-ii`);
  - juntar à avaliação cerca de 50 perguntas desses tipos, verificadas às cegas;
  - repetir a avaliação BM25 com o aviso de inconstitucionalidade de 1983–2026.

## 4. OCR da CNPD: feito (15/11)

36.197 decisões com texto por OCR; ficam 311 sem texto. Validação sem erros e commit no main.

## 5. À espera de terceiros

- **TC e CNPD:** a resposta ao pedido de confirmação da reutilização, notificados a 12/11/2026.
- **Chave da API:** para testar as respostas escritas com o LLM.
