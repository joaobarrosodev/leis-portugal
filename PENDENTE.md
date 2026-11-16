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
- Falta o índice, e o `structure` só para o relatório: ficam para a reconstrução do ponto 3. Na
  reconstrução, entram as chaves novas (`78.º-A`), e as que tinham o hífen U+2010 passam a «-».

## 2. Atos da UE em vigor que ainda faltam (30)

Os 1.218 sem versão portuguesa já estão traduzidos (14/11). Faltam:

- **23 por identificar:** são a diferença entre a lista do CELLAR de 11/11/2026 e
  `reports/eurlex_em_vigor_failures.jsonl`. Refazer a lista dos atos em vigor, cruzar com o acervo
  e ver se já estão gravados com outro id ou se têm outro problema.
- **4 com o número oficial repetido:** decisões cujo número coincide com o de outra já gravada.
  Decidir se se gravam com o caminho desambiguado.
- **3 sem texto no CELLAR:** confirmar que não há PDF nem HTML em nenhuma língua.

Gasta pouco: são consultas ao CELLAR e um script.

## 3. RAG

- **Reconstruir o índice** para entrarem as 1.218 traduções da UE. Usa só o PC.
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
