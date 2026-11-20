# Camada 1: falhas de dados fechadas a 20/11/2026

Segue a tabela «Resumo» de `reports/inventario-camada-1.md`. As provas de cada número estão em
`reports/camada-1-falhas-de-dados/`. O índice não foi reconstruído e o export é o de antes da recolha. O `data/`
está limpo e com commit no main (`c1a6cbfbd23`): recolha em `8443c1dc0d5`, `structure` em `045e132a2b9`.

## Resumo

| Linha | O que era | Antes | Depois | Fica por fechar, e porquê |
|---|---|---|---|---|
| 5 | Consolidados que o DRE mexeu | 63 | 0 | Nada |
| 5 | Consolidados novos do DRE | 217 (32 prioritários) | 97 recolhidos (20 prioritários) | 120 (12 prioritários): o DRE lista-os como consolidados e não tem texto em nenhuma data |
| 5 | Centrais conferidos contra o DRE | não conferidos | 156 conferidos, 154 com todos os artigos iguais | 2 com um artigo que a comparação não alinha (tabelas); os 42 centrais que não são consolidados do DRE não têm com que comparar |
| 10 | Código Comercial | fora do acervo | entrou a Carta de Lei de 28/6/1888 que o aprova | O articulado do código: o DRE não o tem. Precisa de outra fonte, que é decisão do João |
| 8 e 18 | Revogados por inteiro que o DRE dá como em vigor | 217 e 58 (tetos) | 9 verificados e já `repealed` nos registos | 261: sem prova que chegue (ver abaixo). 5 dos 58 já tinham marca |
| 3 | Vigência desconhecida | 2.449 prioritários | sem mudança: a regra está descrita e medida, **por aplicar** | À espera de decisão (ver «Linha 3») |

## Linha 5: consolidados do DRE

- **Como:** `collect dre-consolidated`, pelo sitemap da legislação consolidada de 20/11/2026 (6.039 entradas).
- **Mexidos:** os 63 que o DRE alterou desde a última recolha voltaram a ser recolhidos (IRS, IVA, IEC, Contratos
  Públicos entre eles).
- **Novos:** dos 217, 97 têm texto e entraram: 22 despachos (extrato), 18 portarias, 17 decretos-leis, 15 avisos, 2
  leis e outros. 23 eram registos novos no acervo; os outros já existiam e passaram a ter o texto consolidado.
- **Sem texto na fonte:** 277 entradas do sitemap não têm texto consolidado em nenhuma data (120 das novas e 157 das
  159 que já tinham falhado; 2 destas passaram a ter texto). 125 registos que já existiam ficam com a nota «Fonte sem
  texto». Lista: `consolidados-sem-texto-na-fonte.jsonl`.
- **Commit dos dados:** `8443c1dc0d5` (458 ficheiros, só os desta recolha).

### Os centrais, artigo a artigo, contra o DRE de hoje

- **O que se comparou:** para cada um dos 156 diplomas centrais consolidados pelo DRE, o corpo de cada artigo do
  nosso registo (lido com o leitor do índice) com o corpo do mesmo artigo pedido hoje ao DRE, na data da última
  versão em vigor. As notas («Alterado pelo/a…») ficaram de fora da comparação.
- **Resultado:** 24.822 artigos iguais e 11 diferentes, em 6 diplomas.
- **Quatro tinham diferenças verdadeiras, que a data do sitemap não mostrava** (a data era a mesma dos dois lados):
  - Constituição: 5 artigos. No artigo 40.º faltava o n.º 3 (tempos de antena nos períodos eleitorais);
  - União de facto (Lei n.º 7/2001): 1 artigo;
  - Código do Trabalho: 2 artigos, com gralhas que o DRE corrigiu;
  - Lei Geral do Trabalho em Funções Públicas: 1 artigo.
  Foram recolhidos de novo e ficaram com todos os artigos iguais.
- **Dois ficam com um artigo por alinhar:** o artigo 71.º do DL 91/2009 (parentalidade) e as «Listas I e II» do Código
  do IVA. Os dois registos foram recolhidos hoje; a diferença é da minha comparação, que não alinha tabelas.
- **O que isto diz do resto:** 4 em 156 (2,6 %) tinham texto diferente do DRE sem a data do sitemap mudar. `--stale` não
  apanha estes casos. Só uma recolha completa dos cerca de 5.760 consolidados os apanha (horas de recolha). Não a fiz.
- Lista: `centrais-contra-o-dre.jsonl`.

## Linha 10: Código Comercial

- **O que o DRE tem:** a Carta de Lei de 28 de junho de 1888 (Diário do Governo n.º 203, de 6/9/1888), com cinco artigos:
  aprova o código e manda-o vigorar a 1/1/1889. O DRE dá-a como vigente. Entrou no acervo:
  `data/portugal/outros/carta-lei/1888/carta-lei-1888-09-06-321492.md`.
- **O que o DRE não tem:** o articulado do código. O número do Diário do Governo tem uma página e um só diploma, e o
  sitemap da legislação consolidada não tem nenhuma carta de lei.
- **Outra fonte:** a Procuradoria-Geral Distrital de Lisboa publica o código consolidado, mas não é uma fonte
  registada em `config/sources.yml` e não confirmei as condições de reutilização. Fica para decisão.

## Linhas 8 e 18: revogados por inteiro que o DRE dá como em vigor

- **Regra para contar como verificado:** o DRE regista a revogação do diploma inteiro; o diploma que revoga está no
  acervo e tem uma frase que o revoga, sem ressalva; o número e a data batem; nenhuma alteração posterior; e eu li a
  frase e todas as outras menções ao diploma no revogador.
- **Verificados: 9**, todos `in_force` no DRE. Entraram em `reports/vigencia-manual.jsonl`, com a frase do revogador:
  DL 249/96, DL 288/98, DL 92/94, DL 69/94, DR 18/2004, DR 72/84, DL 354-A/80, DLR 14/89/A e DL 395/2007.
  O `structure` aplicou-as: os nove registos estão `repealed`, com a prova em `legal_status_basis` (commit `045e132a2b9`).
- **Ficam 261, com o motivo em `revogados-por-inteiro.jsonl`:**
  - 169: a frase de revogação tem ressalva, não está no revogador, ou há uma alteração posterior;
  - 66: o DRE não regista a revogação do diploma inteiro (só de partes, ou nenhuma). São 48 da linha 18, em que cada
    artigo tem a sua nota de revogação e já sai com o aviso, e 18 da linha 8;
  - 18: o DRE dá o diploma como parcialmente em vigor. A frase de revogação existe, mas falta conferir o regime
    transitório de cada um;
  - 8: li e não aceitei (revogação condicional ou diferida, só de um anexo, ou a frase não é a norma revogatória).
- A linha 8 era um teto da triagem: 133 dos 217 estão `partially_in_force` no DRE, e em muitos é o DRE que tem razão.

## Linha 3: vigência desconhecida (regra descrita, por aplicar)

**Universo:** 2.427 prioritários da 1.ª Série com `legal_status: unknown` e com texto (os outros 22 só têm
digitalização). 2.418 são de 2014 em diante: o DRE deixou de preencher o campo.

**A regra.** Fica `in_force` o diploma que:

1. foi publicado de 2014 em diante;
2. não tem nenhuma relação «revogado por» no DRE, nem parcial;
3. não tem revogação lida na norma revogatória de outro diploma do acervo (`structure`);
4. não é temporário pelo sumário: orçamento, autorização legislativa, regime excecional, transitório ou
   extraordinário, prorrogação ou alargamento de prazo, contingência, quadro plurianual, recenseamento, um ano;
5. não fala, no próprio texto, em vigência limitada («vigora até», «cessa a vigência», «produz efeitos até»).

**Quantos:** 1.946 entram (938 decretos-leis, 595 leis, 337 decretos legislativos regionais, 49 decretos
regulamentares e 27 leis orgânicas). 786 são atos de alteração. Ficam de fora 481: 258 temporários pelo sumário, 181
pelo próprio texto, 31 com revogação no DRE, 7 anteriores a 2014 e 4 com revogação lida.

**A amostra: 150 diplomas ao acaso** (60 com a semente 20261120 e 90 com a 20261121), tirados antes de alargar a
condição 4. Para cada um:

- pedi o registo ao DRE hoje: 149 continuam sem vigência e 1 já vem `in_force` (DL 204/2026); **nenhum tem relação
  «revogado por»**;
- procurei no acervo todos os parágrafos de diplomas posteriores que o citam, no singular e no plural, com
  «revog», «caduc» ou «cessa»: 33 diplomas tinham menções e li-as todas. **Nenhuma revoga o diploma da amostra**
  (são outros diplomas com o mesmo número, ou menções do tipo «alterado pelo…»);
- li os 150 sumários à procura de vigência limitada: 15 são temporários por natureza (4 autorizações legislativas, 4
  prorrogações de prazo, 4 regimes excecionais ou extraordinários, 2 quadros plurianuais já passados e o recenseamento
  de 2021). Foi por estes
  que a condição 4 foi alargada; todos ficam agora de fora.

**O que a amostra diz:** dos 135 que a regra final aceita, 135 não têm revogação conhecida nem vigência limitada
que eu visse. Com 135 em 135, o erro pode ir até 2,2 % (limite a 95 %). O projeto pede 98 % para mudar um estado sem
prova manual: está na fronteira. Para a passar com folga é preciso conferir mais uns 150.

**O que «em vigor» quer dizer aqui:** que não há revogação nem caducidade conhecidas, como o `in_force` do DRE nos
diplomas anteriores a 2014. Um ato de alteração fica «em vigor» mesmo com o conteúdo já gasto.

**Como se aplicaria:** uma regra nova no `structure`, com `legal_status_basis` a dizer a regra e o estado do DRE
(`unknown`), que volta sozinho se aparecer uma revogação. Efeito na pesquisa: 1.946 diplomas deixam de ter o peso
×0,85 e o aviso «Vigência do diploma desconhecida». 786 são atos de alteração, que passam a pesar o mesmo que os
anteriores a 2014; pode valer a pena deixá-los de fora numa primeira aplicação.

Listas: `vigencia-regra.jsonl` (os 2.427, com o motivo dos que ficam de fora) e `vigencia-amostra.jsonl` (os 150).

## O `structure` depois da recolha (commit `045e132a2b9`)

Corri o `structure` na pasta principal para aplicar as nove provas e dar entrada em vigor aos registos de hoje. Alterou
**17.004 registos**, muito mais do que isso. Antes do commit vi porquê:

- **Causa:** os editais e os regulamentos recolhidos a 13/11 (commits `c69a66827c4` e `ab3486874a0`) ainda não tinham
  os campos que o `structure` escreve. No commit anterior, só 3.440 registos da 2.ª Série tinham `entry_into_force`;
  o relatório de 16/11 já contava 20.204. Dos 17.004 alterados, 16.930 são da 2.ª Série (11.701 regulamentos e 4.878
  editais) e 11.718 vêm do commit dos regulamentos.
- **O que mudou:** 16.826 registos passam a ter `entry_into_force` (uns 10.300 com data; os outros só com a regra,
  porque a data depende de um facto que o texto não dá). 364 mudam
  de `legal_status`, todos com a prova em `legal_status_basis`:
  - 9 `in_force` → `repealed`, pelas provas manuais acima;
  - 351 `unknown` → `repealed`: 341 pela norma revogatória e 10 pela relação do DRE. 348 são da 2.ª Série;
  - 4 `unknown` → `not_in_force`, pela cláusula de vigência.
- **O que conferi:** o corpo de nenhum registo muda (31 registos dos Açores passam de fins de linha CRLF para LF); os
  17.004 passam o esquema do projeto; numa amostra de 8 das 341 revogações pela norma revogatória, as 8 têm a frase
  de revogação do diploma inteiro, com o número e a data.
- **Na camada 1** entram os nove estados e a entrada em vigor dos registos de hoje. O resto é 2.ª Série.

## O que não fiz

- Não corri `export` nem `rag.indice`.
- Não apliquei a regra da linha 3.
- Não fiz a recolha completa dos consolidados do DRE.
- Os relatórios de `reports/inventario-camada-1/` foram regenerados sobre o índice publicado (`indice-fase1.sqlite`) e
  o sitemap de 20/11, mas com o export de antes desta recolha: a linha 5 ainda aparece lá com os números de antes.
