# Diagnóstico: as perguntas reais em que o artigo certo não chega aos 8 primeiros (19/11/2026)

Porque é que a pesquisa não encontra o artigo certo em 48 das 281 perguntas reais, e o que construir para as recuperar. É só diagnóstico: o código da pesquisa e os valores por omissão não mudaram. As perguntas vão só pelo `id`; o detalhe com o texto fica em `rag/resultados/privado/` (fora do git).

## Resumo

- **Das 48, 7 não são falhas da pesquisa.** Há outro artigo igualmente válido nos 8 primeiros (em 5, no 1.º lugar), e o conjunto de avaliação só aceita um. Ficam **41 falhas reais**.
- **O índice está limpo nas 48.** Em todas, o diploma está no índice e em vigor, e o artigo está na redação certa, com o excerto e sem marca de revogado. Nenhuma das 48 cita diploma ou artigo.
- **20 das 41 falham no reranker.** O artigo certo é lido e fica abaixo do 8.º. Em 10, o reranker não chega a ler o número que responde, porque só lê os primeiros 1200 caracteres de cada artigo. Nas outras 10 lê-o e dá-lhe nota baixa.
- **21 das 41 falham antes do reranker.** O artigo não entra nos candidatos lidos. Em 18, a pergunta usa palavras diferentes das da lei e o diploma não tem perguntas por artigo. Em 3, o artigo é muito comprido e o BM25 dilui-o.
- **O que mais compensa:**
  1. pôr o reranker a ler as perguntas por artigo e o número certo do artigo (até 18 das 41);
  2. gerar perguntas por artigo para os diplomas avulsos de saúde, incapacidade, pensões e mediação (até 15);
  3. tirar da frente as cópias antigas dos códigos e aceitar artigos alternativos no conjunto de avaliação.

## Base e método

- **Medição:** `app011-final`, a configuração da aplicação 0.1.1 (BM25, reranker cruzado com `maximo` 30, limiar 3, sem LLM) sobre o índice de 19/11 às 16h54. Nas 281 reais, o artigo certo fica em 1.º em 140, entre o 2.º e o 8.º em 93 e fora dos 8 primeiros em 48 (45 fora dos 10 e 3 no 9.º ou 10.º). Responde a 185 e acerta 115. No índice das 15h27 as 48 são as mesmas.
- **Por pergunta** (`scripts/diagnostico_pesquisa.py`):
  - o artigo certo no índice (vigência, excerto, marca de revogado, perguntas por artigo);
  - a posição dele no BM25 em todo o acervo, nos códigos principais e dentro do diploma;
  - se entra no conjunto que o reranker lê;
  - a nota e a posição final.
- **Testes com o reranker** (`scripts/diagnostico_variantes.py`): o artigo certo é pontuado no mesmo lote que os 10 primeiros, em várias formas:
  - como está;
  - a partir do número onde está o excerto («janela»);
  - com as perguntas por artigo;
  - com o sumário do diploma.

  A posição é a que teria entre esses 10.
- **Simulação por passagens** (`scripts/diagnostico_passagens.py`): o BM25 do FTS5 recalculado à mão para cada passagem dos 1000 melhores pedaços, como se os artigos compridos estivessem partidos por números. O cálculo à mão dá a mesma pontuação que o SQLite nos pedaços que existem.
- **Leitura à mão** dos 8 primeiros resultados de cada uma das 48, para ver se algum responde tão bem como o artigo esperado.

## Dois fatores explicam quase tudo

Nas 281 reais, cruzando dois factos do artigo certo com o resultado:

| Artigo certo | n | Em 1.º | Fora dos 8 |
|---|--:|--:|--:|
| Com perguntas por artigo, excerto nos primeiros 1100 caracteres | 159 | 104 (65%) | 8 (5%) |
| Com perguntas por artigo, excerto depois | 28 | 3 (11%) | 12 (43%) |
| Sem perguntas por artigo, excerto nos primeiros 1100 caracteres | 74 | 27 (36%) | 16 (22%) |
| Sem perguntas por artigo, excerto depois | 20 | 6 (30%) | 12 (60%) |

- O reranker lê 1200 caracteres de cada texto, contando o rótulo (`CARACTERES` em `rag/modelos.py`). Quando a resposta está mais abaixo no artigo, não a vê.
- 40 das 48 têm pelo menos um dos dois fatores.
- É uma associação nas 281; a causa de cada uma das 48 foi verificada com os testes abaixo.

## As causas

| Causa | n | Diplomas | Perguntas |
|---|--:|---|---|
| **T. Problema do teste:** outro artigo igualmente válido nos 8 primeiros | 7 | DL 113/2011 (2), DL 202/96, Lei 25/2012, Lei 100/2019, CPPT, Código Civil | real-022, 247, 265, 281, 286, 318, 322 |
| **A. O reranker não lê o número que responde** (corte aos 1200 caracteres); lendo-o, o artigo vai para os 8 primeiros | 10 | Código do Trabalho (2), Código da Estrada (2), DL 113/2011 (2), DL 202/96, CIVA, CIRC, CIMI | real-006, 058, 106, 216, 224, 274, 287, 292, 298, 317 |
| **B1. O reranker lê a resposta e dá nota baixa:** a linguagem da pergunta não é a da lei | 7 | LGT, Código do Trabalho, Código da Estrada, Código Civil, CIRC, Lei 25/2012, DL 113/2011 | real-019, 132, 212, 253, 267, 276, 299 |
| **B2. O artigo tem nota razoável, mas outros textos têm mais** (atos de um só ano, acórdão que cita a norma) | 2 | Código do Trabalho, Código da Estrada | real-054, 208 |
| **B3. Norma remissiva:** a resposta precisa de dois artigos | 1 | Lei 6/2006 | real-254 |
| **C1. Não chega aos candidatos:** artigo muito comprido, diluído no BM25 | 3 | CIVA (2), LGT | real-001, 020, 035 |
| **C2. Não chega aos candidatos:** palavras diferentes das da lei, em diploma sem perguntas por artigo | 18 | Lei 15/2014 (5), DL 202/96 (3), DL 187/2007 (3), Lei 29/2013 (3), Lei 25/2012, DL 113/2011, DL 147/2003, EBF | real-003, 029, 037, 256, 257, 259, 260, 263, 268, 285, 288, 301, 302, 306, 315, 333, 334, 335 |
| **Total** | **48** | | |

### T. Problema do teste (7)

O sistema encontrou um artigo que responde à pergunta, e o conjunto de avaliação conta-o como falha porque espera outro. A leitura é desta sessão, sobre o texto dos artigos no índice; convém um jurista confirmar antes de mexer no conjunto.

| Pergunta | Artigo esperado | Artigo encontrado | Posição | Respondeu? |
|---|---|---|--:|---|
| real-022 | CPPT, 38.º-A | Portaria 233/2019, 6.º, n.º 3 (mesma regra, quase palavra por palavra) | 1.º | sim (3,3) |
| real-281 | Estatuto do Cuidador Informal, 6.º | Decreto Regulamentar 1/2022, 10.º, n.º 2 (mesmo prazo e mesmo dever) | 1.º | sim (5,0) |
| real-286 | DL 202/96, 4.º | DL 202/96, 4.º-A, n.º 2 (norma interpretativa, responde diretamente) | 1.º | não (2,9) |
| real-322 | DL 113/2011, 5.º | Portaria 142-B/2012, 3.º (a portaria que o artigo manda aprovar) | 1.º | não (1,0) |
| real-265 | Lei 25/2012, 4.º | Lei 25/2012, 2.º, n.º 1 («pessoa maior de idade e capaz») | 1.º | não (2,2) |
| real-318 | DL 113/2011, 8.º | Lei 112/2009, 50.º (isenção da vítima) | 2.º | não |
| real-247 | Código Civil, 1103.º | DL 157/2006, 6.º (mesma indemnização e mesmo realojamento) | 2.º | sim, mas com o 1.º |

- **real-247:** o 1.º resultado é a cópia do artigo 6.º do DL 157/2006 republicada na Lei 30/2012, com os valores de 2012 (um ano de renda e dois de realojamento, em vez de dois e três). O sistema respondeu com ela, nota 4,6. É uma resposta desatualizada, e é um problema da pesquisa, tratado em «Cópias antigas» abaixo.
- **real-318:** o 1.º é a cópia do mesmo artigo 50.º na Lei 129/2015, que republicou a Lei 112/2009. O texto é igual.
- **Efeito nos números de base:** as falhas de pesquisa nas reais são 41, não 48. Duas das 185 respostas contadas como erradas estão certas (real-022 e real-281): seriam 117 certas em vez de 115.
- A real-034, que está entre o 2.º e o 8.º, é do mesmo género: o DL 28/2019, 19.º, em 1.º e com resposta, tem o mesmo prazo de 10 anos do CIVA, 52.º. Vale a pena fazer a mesma leitura nas 93 que ficam entre o 2.º e o 8.º.

### A. O reranker não lê o número que responde (10)

- O artigo certo está nos candidatos, quase sempre no topo do BM25 (1.º a 7.º em 9 das 10), e o reranker lê-o.
- O excerto que responde começa entre o carácter 1045 e o 2094 do artigo. Com o rótulo à frente, fica cortado ou de fora.
- Lido como está, o artigo tem notas entre −7,1 e −0,9. Lido a partir do número certo, fica em 1.º em 6, em 2.º ou 3.º em 3 e em 8.º em 1 (real-274), com notas entre −0,7 e 5,7. Numa segunda corrida, a real-216 ficou em 4.º e a real-274 em 7.º.
- O mesmo acontece em 4 das 7 do grupo T (real-022, 281, 286 e 318): com a janela, o artigo esperado também subia.
- **real-216 e real-287** têm ainda cópias antigas do mesmo artigo à frente (ver «Cópias antigas»).

### B1. O reranker lê a resposta e dá nota baixa (7)

O excerto está à vista (ou foi dado no teste da janela) e a nota continua baixa, entre −6,9 e −2,3. A pergunta usa a linguagem de quem pergunta, e a lei a sua:

- **Nome corrente contra nome legal:** real-132 (o artigo fala de «retribuição mínima mensal garantida»), real-267 (a lei fala de «diretivas antecipadas de vontade», e o nome corrente só está no sumário e no artigo 2.º), real-212.
- **Pergunta prática contra regra abstrata:** real-019, real-276, real-299.
- **Artigo geral à frente do específico:** real-253 (o 1101.º do Código Civil em 1.º; as condições estão no 1102.º).

Com as perguntas por artigo no texto que o reranker lê, 5 destas 7 vão para os 8 primeiros: real-019 (3.º), 132 (8.º), 212 (1.º), 253 (2.º) e 299 (1.º). As outras duas (real-267 e 276) são de diplomas sem perguntas por artigo.

### B2. Outros textos com nota mais alta (2)

- **real-054:** o artigo certo tem nota 4,3 e fica em 22.º. Os oito primeiros são despachos normativos de 1979 a 1992, um por ano, sobre o mesmo dia, com notas entre 6,4 e 6,8. São atos que se esgotaram no ano a que dizem respeito.
- **real-208:** os primeiros são blocos de um acórdão do STJ de 2013 que cita o artigo certo. Um deles, em 6.º, tem o excerto. O artigo certo tem nota 0,8 e fica em 11.º.

### B3. Norma remissiva (1)

- **real-254:** o artigo certo (Lei 6/2006, 28.º) só diz que a certos contratos não se aplica uma alínea do artigo 1101.º do Código Civil. Não tem as palavras da pergunta. O 1101.º fica em 1.º. A resposta precisa dos dois artigos e de quem os ligue. O conjunto de avaliação marca-a como dependente de outro artigo.

### C1. Artigo comprido diluído no BM25 (3)

- Os artigos têm 5200 a 11 800 caracteres (CIVA 9.º e 29.º, LGT 63.º-A). Ficam em 68.º, 125.º e 187.º no BM25 em todo o acervo, e em 22.º, 90.º e 43.º nos códigos. O reranker lê os 30 melhores do acervo e os 15 dos códigos.
- Têm perguntas por artigo, mas o BM25 penaliza o comprimento.
- Na simulação por passagens, dois sobem para os candidatos (real-035 para 1.º e real-020 para 7.º). No real-001, o artigo sobe para 5.º nos códigos, mas a passagem com o excerto fica em 90.º.

### C2. Palavras diferentes, diploma sem perguntas por artigo (18)

- A pergunta é de leigo e o artigo usa outros termos. A real-029 usa uma sigla que o artigo não tem.
- O artigo certo fica entre o 37.º e o 430.º no BM25 em todo o acervo. Em 3 não aparece nos 3000 primeiros.
- **Dentro do próprio diploma, o artigo certo é dos primeiros:** 1.º a 5.º em 15 das 18. O que falha é chegar ao diploma.
- **Se o reranker o lesse, punha-o nos 8 primeiros em 15 das 18,** e em 9 delas em 1.º. A real-037 só com a janela. As três que nem assim subiam são a real-268, a 285 e a 315.
- **As notas são baixas:** só 4 das 15 passam o limiar 3 (real-003, 263, 288 e 334). As outras sobem porque os concorrentes ainda têm menos.
- São leis e decretos-leis avulsos, fora da lista dos códigos principais que já receberam perguntas por artigo:
  - a Lei 15/2014 (direitos dos utentes de saúde);
  - o DL 202/96 (atestado de incapacidade);
  - o DL 187/2007 (pensões);
  - a Lei 29/2013 (mediação);
  - a Lei 25/2012 (testamento vital);
  - o DL 113/2011 (taxas moderadoras);
  - o DL 147/2003 (bens em circulação);
  - o artigo 58.º-A do EBF.

## Hipóteses verificadas e afastadas

| Hipótese | Resultado nas 48 |
|---|---|
| O diploma ou o artigo não está no índice | 0 |
| O diploma não está consolidado ou não está em vigor | 0 (45 consolidados com histórico, 3 originais, todos em vigor) |
| A redação em vigor na data da pergunta não é a que lá está | 0 (o excerto está no pedaço em vigor em todas) |
| O artigo sai como revogado (`fontes.revogado`) | 0 |
| O diploma só se encontra pela referência (2.ª Série) | 0 |
| O artigo é trocado por outro pelo redirecionamento | 0 |
| O artigo está partido em pedaços e o certo não sobe | Não se aplica: o índice tem um pedaço por artigo. O que acontece é o inverso: o artigo inteiro é um pedaço e o reranker só lê o início (causa A) |
| A pergunta cita o diploma ou o artigo | 0 |

## O que construir, por retorno

Os números são o melhor caso nas 41 falhas reais: a pergunta passa a ter o artigo certo nos 8 primeiros. Não são somáveis sem cuidado, porque várias medidas recuperam as mesmas perguntas.

| # | O que construir | Esforço | Recupera no melhor caso | Perguntas |
|--:|---|---|--:|---|
| 1 | **O reranker lê as perguntas por artigo** (`reranker_com_perguntas`, já existe e já foi medido no piloto; falta decidir o limiar) | pequeno | 14 | real-006, 019, 054, 058, 106, 132, 208, 212, 224, 253, 254, 292, 298, 299 |
| 2 | **O reranker lê o número certo do artigo**, e não os primeiros 1200 caracteres (pontuar o artigo por passagens e ficar com a melhor) | médio | 10 | real-006, 058, 106, 216, 224, 274, 287, 292, 298, 317 |
| 1+2 | As duas juntas | | **18** | as de cima, sem repetir |
| 3 | **Perguntas por artigo para os diplomas avulsos** mais procurados (saúde, incapacidade, pensões, mediação, bens em circulação) | médio | **15** | real-003, 029, 037, 256, 257, 259, 260, 263, 288, 301, 302, 306, 333, 334, 335 |
| 4 | **Cópias antigas e atos esgotados fora da frente** (ver abaixo) | médio | 1 a 2 nas 48; mais nas que ficam entre o 2.º e o 8.º | real-054; real-216 só com a medida 2 |
| 5 | **Índice por passagens no BM25** (os artigos compridos entram partidos por números) | grande | 2 a 3 | real-020, 035 (e real-003) |
| 6 | Trazer os melhores artigos de cada diploma que já está nos candidatos | pequeno | 4, todas já contadas na 3 | real-260, 263, 288, 334 |
| 7 | O reranker lê o sumário do diploma junto ao rótulo | pequeno | 1 | real-267 (e a real-265, do grupo T) |
| 8 | Subir o `maximo` do reranker de 30 para 100 | pequeno | 5, com o custo já medido | real-003, 256, 260, 263, 301 |
| 9 | **Conjunto de avaliação:** aceitar artigos alternativos | pequeno | 7 (deixam de contar como falha) | grupo T |

**1 e 2: o que o reranker lê.**
- São a mesma ideia: dar ao reranker o texto que interessa. Juntas, recuperam no melhor caso 18 das 20 em que o artigo já é lido. Ficam de fora a real-267 e a real-276, de diplomas sem perguntas por artigo.
- Nas 18, a nota do artigo certo passa o limiar 3 em cerca de 12. Nas outras, o artigo chega aos 8 primeiros (serve o LLM e a análise de caso) mas o modo sem IA continua a dizer «não sei».
- A medida 1 é o maior ganho já medido no projeto (`rag/README.md`, «Medição completa com o código novo»): com o reranker a ler as perguntas, o artigo certo em 1.º passou de 30% para 76% no âmbito do piloto. Está parada pelo limiar: nas «sem resposta», respondeu a 8 em vez de 5.
- A medida 2 obriga o reranker a pontuar mais textos por pergunta (um artigo comprido tem 2 a 10 passagens). O teste usou o excerto do conjunto de avaliação para saber que número ler, e o sistema real tem de escolher sozinho.
- As duas mexem nas notas e, por isso, no «não sei». Têm de ser medidas nas 1.298 perguntas, não só nestas.

**3: perguntas por artigo nos diplomas avulsos.**
- É a alavanca para as 18 do grupo C2. O piloto já mostrou que as perguntas por artigo trazem o artigo para os candidatos (nos 10 primeiros, de 54% para 87%).
- O melhor caso de 15 parte de dois pressupostos: que as perguntas geradas trazem o artigo para os 30 que o reranker lê, e que o reranker lhe dá a nota que deu neste teste.
- A geração já tem ferramenta (`rag/perguntas_por_artigo.py`). Os 7 diplomas avulsos destas perguntas, mais a Lei 100/2019, têm 318 artigos em vigor.
- **Risco de afinar para o teste:** a lista dos diplomas deve sair dos temas (os diplomas avulsos mais consultados por cidadãos em saúde, segurança social, arrendamento e consumo), e não das perguntas que falharam. A geração nunca pode ver as perguntas do conjunto.

**4: cópias antigas e atos esgotados.**
- Nas 48 recupera pouco, mas tira texto desatualizado do 1.º lugar, que é pior do que não encontrar. Em real-247 o sistema respondeu com valores de 2012; em real-287 os dois primeiros são a redação antiga do artigo certo, nos diplomas que o alteraram.
- O efeito maior é nas perguntas em que o artigo fica entre o 2.º e o 8.º (ver «Os quatro códigos»): só no Código da Estrada, pôr as três republicações antigas a redirecionar para o código atual punha o artigo certo em 1.º em mais 4 perguntas, e 3 passavam a certas.
- São três coisas diferentes:
  - republicações de códigos em diplomas de alteração (o DL 2/98, o DL 265-A/2001 e o DL 44/2005 no Código da Estrada, o DL 198/2001 no IRS e no IRC), o texto original do IVA (DL 394-B/84) e republicações dentro de leis de alteração (a Lei 30/2012 e a Lei 129/2015);
  - artigos de leis de alteração que transcrevem a redação da altura (o DL 174/97 e o DL 291/2009 para o DL 202/96);
  - atos de um só ano (os despachos de real-054).

**5: índice por passagens.** Sozinho rende pouco (2 ou 3) e obriga a reconstruir o índice com outro formato. Só compensa se a medida 2 for feita por essa via.

**8: mais candidatos.** Já medido a 19/11 (`rag/README.md`, «Candidatos ao reranker e pesquisa semântica»): com 50 o sistema responde mais vezes e acerta menos. Aqui o melhor caso são 5.

**O que fica por recuperar:** somando as medidas 1, 2, 3 e 5 sem repetir, o melhor caso são 35 das 41. Ficam 6:
- real-267 e real-276: lidas, de diplomas sem perguntas por artigo para o reranker ler. A 267 sobe com o sumário do diploma.
- real-268, 285 e 315: não lidas, e com nota baixa mesmo se fossem. A 268 e a 315 sobem com o sumário do diploma.
- real-001: o artigo sobe com o índice por passagens, mas a passagem com o excerto fica longe.

A real-254 sobe com as perguntas por artigo, mas a resposta precisa de dois artigos.

## Os quatro códigos que vivem no diploma que os republicou

Código da Estrada (Lei 72/2013), IVA (DL 102/2008), IRC (Lei 2/2014) e IRS (Lei 82-E/2014): 41 perguntas reais. É o lado da pesquisa; o lado dos dados é da sessão `inventario-camada-1`.

| | Código da Estrada | IVA | IRC | IRS | Total |
|---|--:|--:|--:|--:|--:|
| Perguntas | 24 | 12 | 4 | 1 | 41 |
| Certas (artigo em 1.º e respondeu) | 2 | 3 | 1 | 0 | 6 |
| Artigo em 1.º e «não sei» | 7 | 2 | 0 | 0 | 9 |
| Artigo entre o 2.º e o 8.º | 11 | 4 | 1 | 1 | 17 |
| Artigo fora dos 8 | 4 | 3 | 2 | 0 | 9 |

**As quatro hipóteses, com contagens:**

| Hipótese | Perguntas | Quais |
|---|--:|---|
| **Limiar:** artigo certo em 1.º, nota abaixo de 3, «não sei» | 9 | real-201, 204, 210, 213, 219, 221, 223 (Estrada); real-032, 290 (IVA) |
| **Excerto que não bate com a redação consolidada** | 0 | Nas 41, a posição do texto é igual à do artigo |
| **Cópia antiga do código à frente do artigo certo** (republicações de 1998, 2001 e 2005 do Código da Estrada; DL 198/2001 no IRS) | 10 | Em 1.º: real-203, 205, 206, 207, 216, 220, 222. Mais abaixo, mas à frente do certo: real-208, 215, 295 |
| … com o mesmo número de artigo | 6 | real-206, 215, 216, 220, 222, 295 |
| … com outro número (numeração antiga) | 4 | real-203, 205, 207, 208 |
| **Texto original desatualizado a competir** | 2 | DL 394-B/84 (IVA): real-291 (em 1.º) e real-033 (em 2.º). DL 114/94, DL 442-A/88 e DL 442-B/88: 0 |

**Nas 9 com o artigo certo em 1.º e sem resposta certa, a causa é sempre o limiar.**
- O excerto bate em todas, e não há confusão com outro artigo.
- As notas são 3,00, 2,35, 2,18, 1,34, 1,14, 0,60 e −1,75 no Código da Estrada, e 2,02 e 0,51 no IVA. A de 3,00 ficou abaixo do limiar por milésimas.
- A de −1,75 (real-213) tem o excerto no carácter 1863: o reranker não o lê.
- O reranker dá notas baixas a perguntas de leigo contra texto jurídico. No piloto, ler as perguntas por artigo baixou o «não sei» de 116 para 35 em 155 perguntas.

**As cópias antigas do Código da Estrada competem com o peso máximo.**
- O DL 2/98, o DL 265-A/2001 e o DL 44/2005 alteraram e republicaram o código. No índice, estão como consolidados, em vigor e com histórico, por isso levam o mesmo peso (1,25) do código atual.
- Os artigos do código republicado estão na parte principal do diploma, sem nome de anexo. Por isso não levam o desconto das republicações nem têm a ligação `texto_em_vigor_em`, que só o DL 114/94 tem.
- Os três diplomas têm 570 pedaços em vigor no índice. O DL 198/2001, que republicou os códigos do IRS e do IRC em 2001, tem 354, no mesmo estado.
- **Em 4 perguntas o sistema respondeu com a cópia antiga em 1.º** (real-203, 205, 206 e 207): texto de 1998 ou 2001, com a numeração de então.
- Sem as cópias, o artigo certo ficava em 1.º em real-203, 205, 206 e 220, e três passavam a certas (notas 3,3, 5,9 e 4,5). O Código da Estrada passava de 2 para 5 certas em 24.

**O texto original do IVA não redireciona.**
- O DL 394-B/84 não tem a ligação `texto_em_vigor_em` para o DL 102/2008. Aparece 8 vezes nos 10 primeiros das 12 perguntas de IVA, em blocos sem artigo.
- Na real-033, o 1.º é um bloco do DL 195/89, uma alteração de 1989 ao código, e o 2.º é o DL 394-B/84.
- Os originais do Código da Estrada, do IRS e do IRC redirecionam bem: nas 41 perguntas, não aparecem nos 10 primeiros.

**Nas restantes que ficam entre o 2.º e o 8.º (9 de 17), o 1.º é:**
- um artigo de lei de orçamento ou uma disposição transitória: real-297 (Orçamento de 2009) e real-295 (disposição transitória da própria Lei 82-E/2014);
- jurisprudência que cita a norma: real-215;
- outro artigo do mesmo código: real-218, 225 e 294;
- outro diploma: real-217 (regime das contraordenações laborais), real-214 (uma diretiva de 2025) e real-034 (DL 28/2019, igualmente válido: é do teste).

**As 9 fora dos 8** estão nas causas de cima: A (real-216, 224, 292, 298), B1 (real-212, 299), B2 (real-208) e C1 (real-001, 035).

**O corte dos 1200 caracteres pesa também aqui:** além das 4 da causa A, baixa a nota da real-213 (com a janela, sobe de −1,75 para 0,3) e deixa a real-218 em 3.º e a real-291 em 6.º. Com a janela, estas duas ficavam em 1.º e 2.º.

## Código do Trabalho

99 das 281 reais, todas no anexo da Lei 7/2009.

| | n |
|---|--:|
| Artigo certo em 1.º | 75 |
| … respondeu e certa | 69 |
| … «não sei» (nota abaixo de 3) | 6 |
| Entre o 2.º e o 8.º | 20 |
| … com um artigo de outro diploma em 1.º | 19 |
| Fora dos 8 | 4 |

- É o código que melhor funciona: 76% em 1.º, contra 36% nas outras 182 reais. 599 dos 601 artigos em vigor têm perguntas por artigo.
- **As 4 que falham são todas do reranker:** o artigo certo está entre os 12 primeiros do BM25 e é lido.
  - **real-058 e real-106 (causa A):** o excerto está depois do corte. Com a janela, o artigo fica em 1.º.
  - **real-132 (causa B1):** a pergunta usa o nome corrente e o artigo o nome legal.
  - **real-054 (causa B2):** os despachos de um só ano à frente.
- Com o reranker a ler as perguntas por artigo, as quatro iam para os 8 primeiros (1.º, 1.º, 8.º e 7.º).
- As 20 que ficam entre o 2.º e o 8.º são da sessão `ultima-milha`. Em 19, o 1.º é de outro diploma.

## Ressalvas

- **Melhor caso.** Os testes das variantes mudam só o artigo certo e comparam-no com os 10 primeiros tal como estão. Num sistema real, os concorrentes também mudam, e a janela tem de ser escolhida sem o excerto.
- **Só as falhas.** Os testes correram nas 48 (e nas 41 dos quatro códigos). Não dizem quantas das 233 que hoje funcionam se perdiam com cada medida. Isso só se sabe medindo as 1.298.
- **Ruído do reranker.** A nota muda com o lote (até 0,6). Entre duas corridas, a posição do artigo certo mudou um ou dois lugares em algumas perguntas. As 14 que sobem com a janela subiram nas duas corridas.
- **A simulação por passagens é uma estimativa:** usa o comprimento médio dos pedaços do índice atual e só os 1000 melhores pedaços de cada pergunta.
- **As 7 do grupo T** são leitura desta sessão sobre o texto no índice, não de um jurista.
- **«Nos 8 primeiros» não é «certa».** Sem LLM, a resposta só sai se o artigo estiver em 1.º e a nota passar o limiar.

## Como reproduzir

```bash
export RAG_INDICE=<pasta com os modelos> PYTHONPATH=src:.
python scripts/diagnostico_pesquisa.py --detalhe rag/resultados/privado/app011-final-detalhe.jsonl \
    --perguntas avaliacao/privado/perguntas-reais.jsonl --indice rag/indice/indice-final.sqlite \
    --saida rag/resultados/privado/diag-reranker.jsonl --reranker
python scripts/diagnostico_variantes.py rag/resultados/privado/diag-reranker.jsonl \
    rag/resultados/privado/diag-variantes.jsonl rag/indice/indice-final.sqlite
python scripts/diagnostico_passagens.py rag/resultados/privado/diag-reranker.jsonl \
    rag/resultados/privado/diag-simulacao.json rag/indice/indice-final.sqlite
```

Com a máquina carregada, o primeiro leva cerca de 40 s por pergunta e o segundo 20 s. O detalhe por pergunta desta sessão, com o texto e a causa, está em `rag/resultados/privado/diagnostico-reais-nao-encontradas-detalhe.md` e `.jsonl` e em `diagnostico-quatro-codigos-detalhe.md`, no worktree `diagnostico-reais-nao-encontradas-6a120e`.
