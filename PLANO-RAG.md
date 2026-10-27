# Leis de Portugal: plano para um RAG jurídico fiável

27 de outubro de 2026 · João Barroso

## Resumo

O objetivo é um RAG sobre o acervo Leis de Portugal em que pelo menos 95% das respostas dadas estejam certas, com meta de 99% ou mais. Hoje o acervo não chega lá: só 4.722 diplomas em vigor têm o texto atual garantido (consolidado), e 23.417 diplomas em vigor foram alterados mas no acervo só têm o texto original.

O trabalho pesado não é o modelo: é o texto em vigor, a estrutura por artigo e a vigência. Isso faz-se no repositório, antes de afinar a pesquisa ou o modelo.

100% não é garantível nem verificável (nem as consolidações oficiais estão livres de erros), por isso a meta é medida num conjunto de perguntas validado por juristas, e o sistema responde que não sabe quando não tem a certeza.

## O que significa 95%

Das perguntas a que o sistema responde, pelo menos 95% (meta: 99% ou mais) estão certas nas três coisas ao mesmo tempo:

- **Artigo certo:** a resposta assenta na norma que de facto rege a pergunta.
- **Versão certa:** o texto citado é o que estava em vigor na data da pergunta (hoje, por defeito).
- **Citação verificável:** cada afirmação cita o artigo, com ligação à fonte oficial (DRE ou EUR-Lex), e o texto citado suporta-a.

Três regras acompanham a meta:

- **Responder certo ou não responder.** A taxa de "não sei" é o preço da fiabilidade e desce à medida que os dados melhoram.
- **Âmbito: o que diz a lei.** Interpretação, jurisprudência e aconselhamento sobre casos concretos ficam fora.
- **Medido, não estimado.** Um conjunto de 500 ou mais perguntas validado por juristas. Com 500 perguntas, 95% tem uma margem de cerca de ±2 pontos.

## Onde estamos

Dos 137.174 diplomas portugueses e regionais em vigor, só 4.722 (3%) têm o texto atual garantido. Os números vêm do export de 26/10/2026 (281.658 registos de legislação portuguesa e regional; o acervo tem hoje 340.370 registos no total, incluindo 35.578 atos da UE).

| Situação | Diplomas | Com texto | Só PDF | Só metadados | O RAG responderia |
| --- | --: | --: | --: | --: | --- |
| Em vigor, consolidado (texto atual garantido) | 4.722 | 4.722 | 0 | 0 | Certo |
| Em vigor, nunca alterado (o original é o texto atual) | 109.035 | 81.591 | 8.343 | 19.101 | Certo, se as relações não tiverem falhas |
| Em vigor, alterado sem consolidação | 23.417 | 21.569 | 1.471 | 377 | Errado: lê o texto original, já desatualizado |
| Vigência desconhecida | 108.882 | 51.959 | 55.912 | 1.011 | Não sabe se está em vigor |
| Revogado ou sem vigência | 35.602 | 29.180 | 2.883 | 3.539 | Só serve perguntas históricas |

"Em vigor" junta o que o DRE indica como em vigor ou parcialmente em vigor e que não tem relação de revogação no acervo. Os artigos só estão identificados em ~35 mil dos 282 mil diplomas.

## O que bloqueia

Quatro lacunas nos dados impedem os 95%; a primeira é a maior.

| Lacuna | Dimensão | Porque bloqueia |
| --- | --: | --- |
| Alterados sem consolidação | 23.417 diplomas em vigor (1.672 com 10 ou mais citações no acervo) | O sistema cita texto que já não é lei |
| Sem identificadores por artigo | ~247 mil de 282 mil diplomas | Sem artigo não há citação precisa nem verificação |
| Vigência desconhecida | 108.882 diplomas | Não se sabe se a norma ainda se aplica |
| Datas de entrada em vigor | Vazias em todos os diplomas portugueses | Perguntas sobre uma data concreta não têm resposta fiável |

Há ainda ~70 mil registos só com PDF (sobretudo 1910–1959) e as relações de alteração podem ter falhas: um diploma "nunca alterado" só o é se o DRE tiver registado todas as alterações.

## Plano por fases

Cinco fases; as três primeiras são trabalho de dados no repositório e são as que mais pesam na fiabilidade.

| Fase | Critério para fechar a fase |
| --- | --- |
| 1. Âmbito e avaliação | Conjunto validado e fiabilidade atual medida |
| 2. Texto em vigor (maior ganho) | Diplomas principais com texto atual verificado |
| 3. Estrutura, vigência e datas | Artigos com id nos diplomas em vigor; vigência conhecida |
| 4. Sistema | 95% ou mais nas respostas dadas, no conjunto de avaliação |
| 5. Manter a fiabilidade | Não publica se a nota descer abaixo da meta |

A fase 2 é a que mais aumenta a fiabilidade; o detalhe de cada fase segue abaixo.

1. **Fase 1: âmbito e conjunto de avaliação** (precisa de juristas)
   - 500 ou mais perguntas reais, cada uma com o artigo certo e a versão certa.
   - Incluir armadilhas: normas revogadas, alterações recentes e perguntas sem resposta.
   - Medir o ponto de partida.
2. **Fase 2: texto em vigor**
   - Detetar as republicações: muitas leis que alteram outras republicam o diploma completo em anexo. Hoje só estão detetadas 25 (`republished_by`).
   - Consolidar os 1.672 diplomas alterados mais citados: aplicar as alterações com ajuda de um LLM, verificar artigo a artigo e rever à mão os mais importantes.
   - Nos restantes, avisar sempre "texto original; alterado por X e Y" e juntar os artigos que alteram, ou não responder.
3. **Fase 3: estrutura, vigência e datas**
   - Identificadores e partição por artigo em todos os diplomas com texto.
   - Datas de entrada em vigor a partir das cláusulas "entra em vigor…".
   - Vigência dos 108.882 desconhecidos a partir das relações e das normas revogatórias; os antigos só com PDF ficam marcados como históricos e saem do índice de lei atual.
   - Completar as alterações em falta: ler nos diplomas novos "altera o artigo X do DL Y" e cruzar com a análise jurídica do DRE.
4. **Fase 4: sistema**
   - Pesquisa por referência exata primeiro, depois pesquisa híbrida (BM25 e embeddings) com reranker, filtrada pela data de vigência.
   - Juntar os artigos de definições e as normas para onde o artigo remete.
   - Citar o texto literal e o artigo; antes de mostrar, verificar que o artigo existe, está em vigor e suporta cada frase. Se falhar, responder que não sabe.
5. **Fase 5: manter a fiabilidade**
   - Correr o conjunto de avaliação a cada atualização diária. Se a nota descer abaixo da meta, não publica.
   - Reindexar só os registos alterados e invalidar a versão antiga quando sai uma alteração.

## Metas

Os 95% chegam com as fases 2 a 4 aplicadas aos diplomas principais; 98–99% pede consolidação alargada e um conjunto de avaliação que continua a crescer.

| Momento | Fiabilidade nas respostas dadas | Taxa de "não sei" |
| --- | --: | --: |
| Agora, sem este plano | ~60–75% | Baixa, mas responde mal |
| Fases 2 a 4 nos diplomas principais | 95% ou mais | ~20–30% |
| Consolidação alargada e avaliação a crescer | 98–99% | A descer |

Estes valores são estimativas, não medições. O primeiro número real sai da fase 1.

## Riscos e limites

- **Consolidar à mão ou com LLM pode introduzir erros.** Cada diploma consolidado precisa de verificação artigo a artigo; sem isso, troca-se um erro conhecido por um escondido.
- **As relações do DRE podem ter falhas.** Se faltar uma alteração, um diploma aparece como "nunca alterado" e o sistema responde com confiança a partir de texto desatualizado.
- **O conector do DRE usa endpoints internos** sem API pública documentada e pode falhar após um deploy do DRE.
- **As consolidações não têm valor jurídico.** A resposta tem de dizer se o texto é o publicado no Diário da República ou uma consolidação.
- **Não medido ainda:** a fiabilidade atual, a quantidade real de republicações e a completude das relações de alteração. As três medem-se nas fases 1 e 2.

## Próximos passos

- [ ] Escolher os juristas que validam o conjunto de avaliação e fechar o âmbito das perguntas
- [ ] Detetar as republicações e medir quantos dos 23.417 alterados ficam com texto atual
- [ ] Listar os 1.672 diplomas alterados mais citados e escolher os primeiros a consolidar
- [ ] Construir o parser por artigo e os identificadores estáveis
- [ ] Extrair as datas de entrada em vigor e resolver a vigência dos desconhecidos

Decisão pedida: aceitar a definição de 95% acima (respostas dadas, com "não sei" permitido) como a meta do projeto.
