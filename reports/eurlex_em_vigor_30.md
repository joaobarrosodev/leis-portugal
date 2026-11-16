# Os 30 atos da UE em vigor que faltavam (16/11/2026)

Lista dos atos em vigor refeita no CELLAR a 16/11/2026 com o mesmo critério da de 11/11
(regulamentos, diretivas e decisões com CELEX `3AAAA[RLD]NNNN` e `resource_legal_in-force`
verdadeiro): **34.213** atos (mais 3 do que a 11/11). Cruzada com `data/european_union/` pelo
CELEX e pelo id, faltavam **30**, os mesmos do `PENDENTE.md`: os 7 de
`reports/eurlex_em_vigor_failures.jsonl` que não eram traduções e 23 que não estavam no relatório.
Nenhum estava gravado com outro id nem noutro caminho.

Depois desta recolha estão todos no acervo: 34.213 de 34.213.

## 23 sem versão portuguesa (não estavam no relatório)

Na recolha de 16/11, todos deram `NoSourceText`: o CELLAR não tem nenhuma expressão em
português, como os 1.218 traduzidos a 14/11. Porque não ficaram no relatório de 11/11 não se
sabe: o registo dessa execução não foi guardado. Seguiram o caminho das traduções
(`collect eurlex-sem-pt`, tradução, `collect eurlex-traducao`).

| CELEX | Ato | Original | Registo |
|---|---|---|---|
| 31958R0005 | Regulamento n.º 5 (CEEA), 1958 | francês | `regulations/1958/regulamento-ue-1958-5.md` |
| 31972R2864 | Regulamento (CEE) n.º 2864/72 | inglês | `regulations/1972/regulamento-ue-1972-2864.md` |
| 31973L0358 | Diretiva 73/358/CEE | inglês | `directives/1973/diretiva-ue-1973-358.md` |
| 31975L0269 | Diretiva 75/269/CEE | inglês | `directives/1975/diretiva-ue-1975-269.md` |
| 31975L0273 | Diretiva 75/273/CEE | inglês | `directives/1975/diretiva-ue-1975-273.md` |
| 31976D0687 | Decisão 76/687/CEE | inglês | `decisions/1976/decisao-ue-1976-687.md` |
| 31979D0347 | Decisão 79/347/CEE | inglês | `decisions/1979/decisao-ue-1979-347.md` |
| 31980D1097 | Decisão 80/1097/CEE | inglês | `decisions/1980/decisao-ue-1980-1097.md` |
| 31980L0370 | Diretiva 80/370/CEE | inglês | `directives/1980/diretiva-ue-1980-370.md` |
| 31980R3481 | Regulamento (CEE) n.º 3481/80 | italiano (o texto do CELLAR em inglês, francês, alemão e neerlandês é o do Regulamento 3479/80, sobre o lúpulo) | `regulations/1980/regulamento-ue-1980-3481.md` |
| 31981L0645 | Diretiva 81/645/CEE (anexo em grego) | inglês | `directives/1981/diretiva-ue-1981-645.md` |
| 31981R1390 | Regulamento (CEE) n.º 1390/81 | inglês | `regulations/1981/regulamento-ue-1981-1390.md` |
| 31982D0257 | Decisão 82/257/CEE | inglês | `decisions/1982/decisao-ue-1982-257.md` |
| 31982D0382 | Decisão 82/382/CEE | inglês | `decisions/1982/decisao-ue-1982-382.md` |
| 31983D0387 | Decisão 83/387/CEE | inglês | `decisions/1983/decisao-ue-1983-387.md` |
| 31984L0169 | Diretiva 84/169/CEE | inglês | `directives/1984/diretiva-ue-1984-169.md` |
| 31984L0513 | Diretiva 84/513/CEE | inglês | `directives/1984/diretiva-ue-1984-513.md` |
| 31985D0563 | Decisão 85/563/CEE | inglês | `decisions/1985/decisao-ue-1985-563.md` |
| 31985D0564 | Decisão 85/564/CEE | inglês | `decisions/1985/decisao-ue-1985-564.md` |
| 31985D0565 | Decisão 85/565/CEE | inglês | `decisions/1985/decisao-ue-1985-565.md` |
| 31985D0566 | Decisão 85/566/CEE | inglês | `decisions/1985/decisao-ue-1985-566.md` |
| 31985L0350 | Diretiva 85/350/CEE | inglês | `directives/1985/diretiva-ue-1985-350.md` |
| 31985R0462 | Regulamento (CEE) n.º 462/85 | inglês | `regulations/1985/regulamento-ue-1985-462.md` |

## 3 «sem texto no CELLAR»: há expressão portuguesa, mas sem nenhum ficheiro

Consulta a todas as expressões e manifestações das três obras: a expressão portuguesa só tem a
manifestação `print`, sem itens (nem PDF, nem HTML, nem XHTML). Noutras línguas há texto, por
isso seguiram também o caminho das traduções.

| CELEX | Ato | Em português | Noutras línguas | Traduzido de | Registo |
|---|---|---|---|---|---|
| 31965R0004 | Regulamento n.º 30/65/CEE, 4/65/Euratom | só `print` | PDF em dinamarquês, alemão, francês, italiano e neerlandês; nada em inglês | francês, texto da camada de texto do PDF (7 páginas, sem OCR) | `regulations/1965/regulamento-ue-1965-4.md` |
| 31980R0680 | Regulamento (CEE) n.º 680/80 | só `print` | XHTML ou HTML em 20 línguas | inglês | `regulations/1980/regulamento-ue-1980-680.md` |
| 32006D1004 | Decisão 2006/1004/CE do Conselho | só `print` | HTML em francês e maltês (e PDF e XHTML em maltês); as outras 21 línguas só `print` | francês | `decisions/2006/decisao-ue-2006-1004.md` |

## 4 com o número oficial repetido: gravados com o CELEX no nome

O caminho dos atos da UE é `<tipo>-ue-<ano>-<número>.md`, com o ano do CELEX e o número
`resource_legal_number_natural` do CELLAR. Nestes quatro, esse caminho já era de outro ato. O
repositório passa a gravar o segundo com o CELEX no nome; os caminhos que já existiam não mudam.

| CELEX | Ato | Ocupava o caminho | Porquê | Registo |
|---|---|---|---|---|
| 32006D0030 | Decisão 2007/48/CE do BCE (BCE/2006/30) | 32006D0048, Decisão 2006/48/CE da Comissão | o CELLAR dá o ano do CELEX (2006) com o número do JO (48) | `decisions/2006/decisao-ue-2006-48-32006d0030.md` |
| 32010D0033 | Decisão 2011/11/UE do BCE (BCE/2010/33) | 32010D0011, Decisão 2010/11/UE da Comissão | o mesmo: ano 2010 com o número 11 | `decisions/2010/decisao-ue-2010-11-32010d0033.md` |
| 32014D0034 | Decisão 2014/541/UE do BCE (BCE/2014/34) | 32014D0541, Decisão n.º 541/2014/UE do Parlamento Europeu e do Conselho | número igual de verdade, em séries diferentes (antes de 2015) | `decisions/2014/decisao-ue-2014-541-32014d0034.md` |
| 32016D0776 | Decisão (UE) 2016/776 do Conselho | 32016D0775, Decisão de Execução (UE) 2016/775 da Comissão | erro do CELLAR: dá o número 776 à 2016/775 | `decisions/2016/decisao-ue-2016-776-32016d0776.md` |

Ficam com o número oficial do CELLAR (2006/48, 2010/11, 2014/541; e 2016/776 também na
32016D0775), como as outras decisões do BCE: corrigir o número mudaria o caminho de registos que
já existem.

## Verificação das 26 traduções

Traduzidas por subagentes do Claude (`claude-sonnet`), com as regras de terminologia do Jornal
Oficial em português. Antes de gravar:

- **Números:** um script comparou todos os números de cada bloco com os do original. Ficaram só
  diferenças explicadas: «n0 30/65» passou a «n.º 30/65», «Article premier» a «Artigo 1.º»,
  «km2» a «km²» e «line 2» a «segunda linha».
- **Às cegas, por outro modelo (Claude Opus), frase a frase:** 23 atos por inteiro. Nos três
  grandes, por inteiro só as partes principais: no Regulamento 1390/81, os blocos 01, 03 e 08, e
  nos outros blocos 20 ou mais parágrafos por bloco e 44 pontos do anexo VI; nas Diretivas 81/645
  e 75/273, o texto até ao anexo e uma amostra do anexo (77 e 361 linhas). As linhas do anexo da
  81/645 (em grego) foram também conferidas por script: nenhum nome nem número mudou.
- **Resultado:** 2 erros graves em 25 atos, ambos corrigidos. No 2864/72, a referência «Article
  1 (1) No 2» ficou «n.º 2 do ponto 1» em vez de «ponto 2 do n.º 1» (três vezes na mesma frase).
  No 1390/81, «travelling or flying personnel» ficou só «pessoal navegante», o que deixava de
  fora o pessoal ferroviário e rodoviário. Houve cerca de 30 reparos menores; os de terminologia
  foram corrigidos («impostos cedulares», «prestações pecuniárias», «progressão de escalão»,
  «Regras e Regulamentos», «prazo de viagem»…).
- **31980R3481:** a verificação mostrou que o texto inglês do CELLAR não era deste ato. O
  regulamento foi traduzido de novo do italiano e conferido à mão (é curto).
- **Erros dos originais, mantidos:** na Decisão 76/687, o título «II. FODDER BEET» antecede uma
  lista de gramíneas e trevos; na Decisão 85/566, o número aparece como «89/566/EEC»; na
  Diretiva 75/269, há um parêntese a mais.

## O relatório de falhas

`reports/eurlex_em_vigor_failures.jsonl` passa a listar os 1.244 atos em vigor sem texto
português no CELLAR (`sem_texto_na_fonte`): os 1.218 de 14/11 e estes 26. Todos estão no acervo
em tradução não oficial. É a lista que `collect eurlex-sem-pt` lê por omissão. As 4 colisões
saíram do relatório, porque já estão gravadas.
