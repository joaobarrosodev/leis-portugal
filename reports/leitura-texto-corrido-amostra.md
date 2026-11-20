# Texto corrido sem marcação: amostras de revisão (20/11/2026)

O `data/` não muda. Desde a revisão abaixo, o índice lê estes registos como artigos na construção (`rag/corrido.py`,
`rag.indice._unidades`), só quando passam a salvaguarda; o que entra e quanto está no `rag/README.md`, secção «Texto
corrido lido como artigos».

## Revisão de mais 350 registos aceites (tarde de 20/11/2026)

**População:** 8.750 registos em vigor no DRE que o índice guarda em blocos e têm três ou mais linhas «Artigo N.º» ou
«Art. N.º» (114.415 linhas), no export das 6h51 de 20/11 (eram 8.668 no export anterior). A primeira amostra de 50
(abaixo) foi refeita sobre os mesmos 50 registos: a salvaguarda escrita no código aceita exatamente os mesmos 34.

**Como se reviu:** para cada registo, o início de cada unidade lida (número, epígrafe, primeiros 85 caracteres), o texto
que fica fora dos artigos e o tamanho de cada artigo; e, para todos os artigos das quatro amostras (4.040), o texto lido
contra o trecho do original entre a linha que o abre e a que abre o seguinte. Nesta comparação as únicas diferenças são as
esperadas: as assinaturas e as notas «> Alterado…» que vão para fora do artigo, e a redação nova citada entre aspas que
fica dentro do artigo que a cita. Nenhuma fronteira de artigo errada.

### Amostra B: 150 registos aceites pela primeira salvaguarda (semente 20261121)

1.584 unidades em 150 registos. **Bem: 1.570. Mal: 14 unidades, em 6 registos (4 %; intervalo de 95 %: 1,5 % a 8,5 %).**
Por família:

| Família | Registos | Unidades mal | Exemplo | Regra nova |
|---|--:|--:|---|---|
| Redação nova de outro diploma com o número 1: abre uma «Parte 2» | 2 | 6 | DL 39/81 («Artigo 1.º O artigo 1.º do DL 668/75 passa a ter a seguinte redacção:», e os artigos 2.º a 5.º do próprio decreto saem como «Parte 2::2.º»…) | nenhum artigo acaba em «… seguinte redacção:» |
| Registo misto, com um título `###### Artigo` | 2 | 3 | Portaria 803/72 (um só «artigo» com a redação de outro decreto); Decreto 33/82 (a epígrafe de 2 artigos é texto) | sem nenhum título `######` |
| Aspas por fechar | 1 | 1 (com 7 artigos dentro) | DL 46379 (o artigo 5.º leva os artigos 6.º a 12.º) | o último artigo de cada parte não tem dentro o seguinte |
| Acórdão | 1 | 4 | Acórdão 637/95 (os artigos são os do decreto regional julgado; o 4.º leva o acórdão inteiro) | acórdãos e pareceres ficam em blocos |

Com as quatro regras, estes 6 registos ficam em blocos e os outros 144 (1.506 artigos) continuam aceites. O intervalo da
amostra B já não vale para a regra final: as regras foram feitas sobre ela.

### Amostra C: 100 registos aceites pela segunda salvaguarda (semente 20261122)

1.050 unidades em 100 registos. **Mal: 118 unidades, num registo (1 %; intervalo: 0,03 % a 5,5 %).** O DL 235/83
(Regulamento de Segurança e Acções) traz o sumário do regulamento («Artigo 1.º Objecto e campo de aplicação.», um por
linha), que saía como 59 artigos de uma «Parte 2», e os 59 artigos verdadeiros numa parte com o nome de uma linha do sumário
(«ANEXO III - Elementos…»). Regra nova: nenhuma parte é o sumário de outra (80 % dos artigos são o início do artigo com o
mesmo número noutra parte). Em toda a população só este registo tem o padrão.

### Os registos com uma «Parte 2» implícita: revistos todos

Quando a numeração recomeça em 1 sem título de anexo, o leitor abre uma «Parte 2». Das 7 vezes que isto aconteceu nas
amostras B e C, 3 eram erros, por isso revi a fronteira de todos os 145 registos assim aceites pela segunda salvaguarda (o
fim do artigo antes da parte e os dois primeiros artigos dela). **6 errados:** o DL 235/83 e 5 registos (14 unidades) em
que o artigo antes da parte acaba em «:» e o que vem a seguir é texto citado: a redação nova de outro diploma («… na
seguinte conformidade:», DL 793/76, DR 10/79) ou as rubricas de um orçamento («Capítulo 1.º «Encargos da dívida
pública»:» e «Artigo 1.º «Juros»», Decretos 47454 e 44255, DL 46010). Regra nova: a numeração não recomeça logo depois
de um artigo que acaba em «:». Os outros 139 eram o diploma e, a seguir, o regulamento, estatuto, contrato ou convenção que
ele aprova; 8 desses (convenções «… acordam no seguinte:», a versão inglesa de um acordo) também caem na regra e ficam em
blocos. Com a regra final ficam 131 registos com parte implícita, todos revistos.

### Amostra D: 100 registos aceites pela regra final (semente 20261123)

**1.274 unidades em 100 registos, nenhuma mal. Intervalo de 95 %: de 0 % a 3,6 % dos registos aceites com algum erro.**
É a única amostra que não serviu para fazer regras: é este o número que vale para a regra final. Juntando os 376 registos
revistos que a regra final aceita (34 + 144 + 98 + 100), nenhum erro conhecido (0 % a 1 %), mas 242 deles serviram para
fazer as regras.

### Fora da população revista

A regra também se aplica aos registos sem vigência, de vigência desconhecida e aos atos da UE em blocos. Amostra E: 50 ao
acaso dos 4.985 registos portugueses fora de vigor (semente 20261124) e os 6 atos da UE: 578 unidades, nenhuma mal
(intervalo de 0 % a 6,4 %). Aparecem portarias regionais de 2021 a 2026 com «Artigo 1.º», epígrafe na linha seguinte, e o
leitor apanha bem a epígrafe.

### O que fica como defeito menor (contado como bem)

- a assinatura colada ao último artigo quando o leitor não a reconhece («… entra em vigor no dia seguinte. Mário Soares -
  …»): já acontece nos registos com títulos;
- um título de secção solto no fim do artigo anterior («b) Acomodações dos doentes»);
- «Artigo único» do decreto e, a seguir, os artigos do acordo que ele aprova na mesma parte: as chaves «1.º», «2.º»… são
  as do acordo.

### A salvaguarda final

Ver o cabeçalho de `rag/corrido.py`. Em resumo: só artigos (nem bases, nem números); numeração de cada parte de 1 (ou
«único») em diante, sem saltos nem repetidos; nenhum artigo aberto depois de «seguinte redacção:» nem a acabar nessa
frase; a numeração não recomeça depois de um artigo que acaba em «:»; o último artigo de cada parte não tem dentro o
seguinte; nenhuma parte é o sumário de outra; nenhum título `######`; três ou mais linhas «Artigo N.º»; não é acórdão nem
parecer; e, num diploma que «Aprova o Código …», todos os artigos na parte do diploma (a pesquisa procura lá o código pelo
sumário: com o código numa «Parte 2», «artigo 5.º do Código do Imposto de Capitais» ia dar ao artigo 5.º do decreto; esta
última regra saiu do índice de ensaio e tira 3 registos: os DL 44561, 45005 e 45399, que ficam em blocos). **Aceita 5.602
dos 8.750 (64 %), com 63.479 artigos.**

## A primeira amostra, de 50 registos (manhã de 20/11/2026)

Só investigação. Nada foi alterado no `data/` nem no índice. A decisão de mexer no `data/` é do João.

### O que se mediu

- **População:** 8.668 registos em vigor no DRE que o índice guarda em blocos de texto e que têm três ou mais linhas a
  começar por «Artigo N.º» ou «Art. N.º» (111.155 linhas). São 3.231 decretos-leis, 2.505 decretos, 1.464 portarias, 344
  decretos regulamentares e 226 leis, quase todos de 1960 a 1999.
- **Amostra:** 50 registos tirados ao acaso (semente 20261120).
- **A regra:** o leitor de texto corrido que já existe no acervo, `leis_portugal.domain.articles.parse_articles`. Lê
  «Artigo 1.º Texto…», «Art. 2.º - Texto…», «ARTIGO 1.º» com a epígrafe na linha seguinte e «Artigo único.»; junta ao
  artigo que a cita a redação nova que vem entre aspas; e para nas assinaturas.
- **Como se julgou:** a numeração de cada registo (seguida de 1 em diante, com saltos ou fora de ordem) e, nos 13 com
  saltos e nos 2 acórdãos, a leitura um a um do início de cada unidade lida. Nos outros 35 vi o início de cada artigo,
  não o texto inteiro.

### Resultado

- **Lidos:** 472 unidades nos 50 registos. **Bem: 393 (83 %). Mal: 79 (17 %).**
- **Os 79 mal lidos vêm de três famílias:**
  - 44 são rubricas de orçamento, em 5 decretos e portarias de abertura de créditos: «Artigo 127.º «Remunerações
    acidentais»…» é uma linha do orçamento e não um artigo do diploma;
  - 34 são a redação nova de artigos de outro diploma, em 8 diplomas de alteração: depois de «passam a ter a seguinte
    redacção:», os artigos citados vêm sem aspas e saem como se fossem do diploma que altera («Decreto-Lei n.º 47126,
    artigo 13.º» é, na verdade, o artigo 13.º de outro decreto-lei);
  - 1 é um acórdão lido como um único «número».
- **Limites dos artigos:** em 2 dos registos bem lidos o último artigo leva atrás o que vem depois (mapas e modelos): 11.673
  e 15.919 caracteres. É o que o índice já faz hoje nos registos com títulos.
- **Com uma salvaguarda simples o erro desaparece nesta amostra:** aceitar a leitura só quando o registo tem artigos e a
  numeração de cada parte é seguida de 1 em diante (ou «único» e depois 1 em diante). Passam 34 dos 50 registos, com 352
  artigos, e nenhum dos 79 erros. Os outros 16 ficam em blocos, como hoje.

### Quanto vale

- 34 em 50 dá 68 % dos registos (com 50 registos, o intervalo vai de 54 % a 80 %): cerca de 5.900 dos 8.668.
- Em artigos, 352 das 544 linhas da amostra: cerca de 72.000 dos 111.155.
- Zero erros em 34 registos não prova zero: com esta amostra, até 9 % dos registos aceites podem ter algum erro. Para
  apertar o intervalo é preciso ver mais uns 150 registos aceites pela salvaguarda.

### Proposta

1. **Compensa, e sem mexer no `data/`:** o índice pode ler estes registos com o `parse_articles` na construção, como
   já lê os títulos, e ficar com os artigos só quando a numeração é seguida. O `data/` fica como está e a mudança
   desfaz-se com uma reconstrução.
2. **Antes de ligar:** ver mais 150 registos aceites pela salvaguarda, e medir nas 1.298 perguntas com e sem a leitura.
   Os registos são antigos (1960–1999): o ganho esperado é em perguntas que citam o diploma e o artigo, não nas de leigo.
3. **As duas famílias de erro têm regra própria,** se um dia se quiser ler também os 16 que ficam de fora: «Artigo N.º «…»»
   não é artigo; e, depois de «a seguinte redacção:», um artigo fora da sequência fica dentro do artigo que o cita até a
   sequência voltar. Isto mexe no `domain/articles.py`, que dá os identificadores de artigo ao acervo: é uma decisão à parte.
4. **Fora desta medição:** as «Base N» soltas no texto (a Lei n.º 95/2019, Lei de Bases da Saúde, tem as 37 bases assim,
   num `## ANEXO` sem títulos). O `parse_articles` só as lê em registos sem nenhum título de artigo. Ficam como estavam:
   34 dentro do pedaço do artigo 4.º e 3 cortadas.

### Os 50 registos

| Registo | Data | Linhas «Artigo N.º» | Unidades lidas | Bem | Mal | Numeração seguida | Porquê |
|---|---|--:|--:|--:|--:|---|---|
| Portaria n.º 17954 | 1960-09-23 | 70 | 70 | 70 | 0 | sim |  |
| Decreto n.º 43261 | 1960-10-20 | 23 | 11 | 3 | 8 | não | rubricas orçamentais |
| Decreto n.º 43402 | 1960-12-16 | 21 | 10 | 3 | 7 | não | rubricas orçamentais |
| Decreto n.º 43584 | 1961-04-05 | 4 | 4 | 2 | 2 | não | redação nova de artigos de outro diploma |
| Decreto-Lei n.º 43773 | 1961-07-01 | 4 | 4 | 4 | 0 | sim |  |
| Decreto-Lei n.º 43803 | 1961-07-19 | 3 | 3 | 3 | 0 | sim |  |
| Decreto-Lei n.º 44408 | 1962-06-20 | 7 | 7 | 7 | 0 | sim |  |
| Decreto-Lei n.º 45293 | 1963-10-04 | 3 | 3 | 3 | 0 | sim |  |
| Decreto n.º 45312 | 1963-10-16 | 69 | 22 | 5 | 17 | não | rubricas orçamentais |
| Decreto n.º 45540 | 1964-01-22 | 3 | 3 | 3 | 0 | sim |  |
| Decreto n.º 45722 | 1964-05-19 | 3 | 3 | 3 | 0 | sim |  |
| Decreto-Lei n.º 46133 | 1964-12-31 | 5 | 6 | 1 | 5 | não | redação nova de artigos de outro diploma, depois de «passam a ter a seguinte redacção» |
| Portaria n.º 21068 | 1965-01-27 | 3 | 2 | 2 | 0 | não | não tem artigos: números de um portaria |
| Decreto-Lei n.º 46683 | 1965-12-03 | 5 | 5 | 5 | 0 | sim |  |
| Decreto-Lei n.º 46734 | 1965-12-10 | 3 | 3 | 3 | 0 | sim |  |
| Decreto n.º 46888 | 1966-03-05 | 3 | 3 | 3 | 0 | sim |  |
| Decreto-Lei n.º 47126 | 1966-08-01 | 9 | 9 | 3 | 6 | não | redação nova de artigos de outro diploma |
| Decreto-Lei n.º 47908 | 1967-09-07 | 64 | 64 | 64 | 0 | sim |  |
| Decreto n.º 48228 | 1968-01-27 | 4 | 4 | 4 | 0 | sim |  |
| Portaria n.º 23737 | 1968-11-30 | 11 | 11 | 0 | 11 | não | rubricas orçamentais («Artigo 2.º «Remunerações acidentais»…») lidas como artigos |
| Decreto-Lei n.º 48879 | 1969-02-22 | 8 | 8 | 6 | 2 | não | redação nova de artigos de outro diploma |
| Decreto n.º 48977 | 1969-04-23 | 3 | 3 | 3 | 0 | sim |  |
| Decreto-Lei n.º 49488 | 1969-12-30 | 5 | 5 | 5 | 0 | sim |  |
| Decreto n.º 397/70 | 1970-08-20 | 10 | 10 | 10 | 0 | sim |  |
| Decreto-Lei n.º 639/70 | 1970-12-23 | 4 | 4 | 4 | 0 | sim |  |
| Decreto n.º 23/71 | 1971-01-30 | 5 | 5 | 4 | 1 | não | redação nova de um artigo de outro diploma |
| Decreto-Lei n.º 231/71 | 1971-05-28 | 5 | 5 | 2 | 3 | não | redação nova de artigos de outro diploma |
| Decreto n.º 248/71 | 1971-06-04 | 10 | 10 | 10 | 0 | sim |  |
| Decreto-Lei n.º 508/71 | 1971-11-20 | 4 | 3 | 3 | 0 | sim |  |
| Decreto-Lei n.º 585/71 | 1971-12-23 | 4 | 4 | 4 | 0 | sim |  |
| Decreto n.º 245/72 | 1972-07-22 | 19 | 20 | 20 | 0 | sim |  |
| Decreto n.º 362/72 | 1972-09-23 | 3 | 3 | 3 | 0 | sim |  |
| Decreto-Lei n.º 490/73 | 1973-10-02 | 13 | 13 | 13 | 0 | sim |  |
| Decreto n.º 99/74 | 1974-03-14 | 3 | 3 | 2 | 1 | não | rubrica orçamental |
| Decreto n.º 250/74 | 1974-06-12 | 4 | 4 | 4 | 0 | sim |  |
| Decreto n.º 706/74 | 1974-12-10 | 4 | 4 | 4 | 0 | sim |  |
| Decreto n.º 78/76 | 1976-01-27 | 17 | 18 | 18 | 0 | sim |  |
| Decreto n.º 90/76 | 1976-01-29 | 3 | 3 | 3 | 0 | sim |  |
| Portaria n.º 69/76 | 1976-02-06 | 5 | 5 | 2 | 3 | não | redação nova de artigos de outro diploma |
| Decreto n.º 103/77 | 1977-08-05 | 3 | 3 | 3 | 0 | sim |  |
| Decreto Regulamentar n.º 67/77 | 1977-10-15 | 3 | 2 | 2 | 0 | sim |  |
| Decreto Regional n.º 8/78/M | 1978-03-01 | 5 | 5 | 5 | 0 | sim |  |
| Decreto n.º 28/79 | 1979-04-10 | 3 | 3 | 3 | 0 | sim |  |
| Portaria n.º 607/80 | 1980-09-13 | 12 | 12 | 0 | 12 | não | redação nova de artigos de um regulamento alterado |
| Decreto Regional n.º 19/81/A | 1981-10-27 | 21 | 21 | 21 | 0 | sim |  |
| Acórdão n.º 348/86 | 1987-01-09 | 5 | 1 | 0 | 1 | não | um acórdão: o texto inteiro num só «número» |
| Decreto-Lei n.º 227/88 | 1988-06-29 | 6 | 6 | 6 | 0 | sim |  |
| Decreto-Lei n.º 407/88 | 1988-11-09 | 5 | 5 | 5 | 0 | sim |  |
| Decreto-Lei n.º 55/91 | 1991-01-26 | 31 | 31 | 31 | 0 | sim |  |
| Acórdão n.º 246/2005 | 2005-06-21 | 4 | 6 | 6 | 0 | não | não tem artigos: números de um acordao |
| **Total (50 registos)** | | **544** | **472** | **393** | **79** | **34 registos, 352 artigos** | |
