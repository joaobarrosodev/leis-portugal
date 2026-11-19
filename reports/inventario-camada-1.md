# Inventário da camada 1: o que falta ao texto da lei

Medido a 19/11/2026 sobre o export das 23h45 (405.830 registos portugueses), o `data/` do `main`, o sitemap da
legislação consolidada do DRE desse dia e o índice `indice-final.sqlite` (só leitura). Nada foi alterado no `data/`,
no export nem no índice.

- **Âmbito:** 1.ª Série. «Prioritários» são as leis, leis orgânicas, leis constitucionais, decretos-leis, decretos
  regulamentares e decretos legislativos regionais. As portarias têm só contagens. A 2.ª Série fica de fora.
- **Para repetir:** `python scripts/inventario_camada_1.py --descarregar-sitemap --indice rag/indice/indice.sqlite`
  (meio minuto sem o índice). Grava `reports/inventario-camada-1/`: `resumo.json` com todos os
  números, `tabelas.md` com as tabelas completas e uma lista `.jsonl` por falha.
- **«Verificado»** quer dizer contado no registo, no índice ou no DRE. **«Teto»** quer dizer que o número vem de uma
  regra (a triagem da consolidação, uma comparação de datas, o sumário) e que o número real é igual ou menor.

## Resumo, por ordem de retorno

| # | Falha | Tipo | Quantos | Verificado ou teto | Esforço | Valor para o produto |
|---|---|---|---|---|---|---|
| 1 | Cópias do mesmo texto com outra data, servidas como texto atual (anexos de republicação e originais) | apresentação | 151 cópias de 117 textos, com 14.853 pedaços «atuais» no índice; as cópias certas têm 16.123 | Verificado no índice que estão lá como atuais; «outra data» é comparação de datas (teto) | Baixo: regra no índice | Muito alto: Código da Estrada, Penal, Sociedades, Valores Mobiliários, Contratos Públicos, CPPT, LGT; 34 dos 198 centrais |
| 2 | Texto em vigor fora do registo que o aprovou, sem ligação ou com numeração diferente | apresentação | 31 textos; 20 sem ligação (Código Penal e IVA entre eles); 14 com a numeração mudada | Verificado (mínimo: a deteção falha alguns, como o Estatuto da Carreira Docente) | Baixo | Muito alto: IRS, IRC, IVA, Estrada, Penal |
| 3 | Vigência desconhecida | estado | 2.449 prioritários (752 leis, 1.172 decretos-leis); 2.418 são de 2014 em diante; 11 dos 198 centrais | Verificado; a causa também (o DRE não preenche o campo) | Baixo para uma regra, médio para confirmar um a um | Alto: as leis recentes perdem peso na pesquisa (×0,85) |
| 4 | Nomes de códigos que a pesquisa não reconhece | apresentação | 22 de 39 nomes centrais não chegam ao artigo pedido (14 nem ao registo) | Verificado, só BM25 e referência, sem reranker | Baixo | Alto para quem cita o código pelo nome |
| 5 | Consolidados por atualizar e consolidados novos do DRE | dados | 62 que o DRE mexeu depois de 22/10 (IRS, IVA, IEC, Contratos Públicos); 207 novos por recolher (32 prioritários) | Verificado no sitemap | Baixo: voltar a recolher | Alto nos 5 centrais, médio no resto |
| 6 | Alterados recentes nunca triados | dados | 687 prioritários (218 leis, 375 decretos-leis), todos de vigência desconhecida; 7 centrais (Lei n.º 58/2019…) | Verificado que não entraram na triagem; quantos mudam de texto é teto | Médio: triagem e depois LLM | Alto: são diplomas de 2014–2026 |
| 7 | Alterações ao texto por aplicar | dados | 694 prioritários (52 leis, 496 decretos-leis, 78 decretos regulamentares, 68 regionais); 16 só em imagem | Teto (triagem por regras) | Alto: rondas com LLM e verificação | Médio: 213 dos 1.381 por fechar (6 e 7) são citados por 10 ou mais diplomas em vigor |
| 8 | Revogados por inteiro que o DRE dá como em vigor | estado | 218 prioritários | Teto (triagem) | Médio | Médio |
| 9 | Consolidados com alterador posterior à última versão | dados | 210 prioritários (68 do DRE, 142 nossos) | Teto: o alterador pode não mudar o texto | Médio | Médio |
| 10 | Antigos em vigor só com digitalização | dados | 2.407 leis, 7.119 decretos-leis e 962 decretos de 1910–1959; 407 citados por 5 ou mais diplomas em vigor; o Código Comercial não existe no acervo | Verificado | Alto: OCR e revisão | Baixo, salvo o Código Comercial e poucos mais |
| 11 | Registos duplicados do mesmo diploma | apresentação | 10 prioritários com texto; 1 com consolidado e original ao mesmo tempo (Lei n.º 28/82, a do Tribunal Constitucional) | Verificado | Baixo | Baixo, salvo a Lei n.º 28/82 |

As linhas 1, 2, 4 e 11 são **falhas de apresentação**: o texto certo existe, mas há outro texto ao lado a ser servido
como atual, ou a pesquisa não o encontra. As linhas 3 e 8 são **falhas de estado**. As linhas 5, 6, 7, 9 e 10 são
**falhas de dados**: falta texto ou o texto não está em dia.

## Os números da sessão coordenadora

| Número dado | Medido | Diferença |
|---|---|---|
| 867 leis, 3.494 decretos-leis e 421 decretos regulamentares em vigor, alterados e sem consolidação | 867, 3.494 e 421 | Nenhuma na contagem. Como «falta texto em vigor» são tetos altos: pela triagem, 592, 2.498 e 273 não têm alteração textual, 5, 119 e 47 foram revogados por inteiro e 6 decretos-leis têm o texto noutro registo. Ficam por fechar 270, 871 e 101 |
| 741 leis e 1.161 decretos-leis de vigência desconhecida no índice | 741 e 1.161 no índice; 752 e 1.172 no export | Nenhuma. A diferença para o export são 22 só com digitalização |
| 62 diplomas anteriores a 1960 no índice | 62 | 9 são atos da UE. Portugueses com texto são 53, e 38 deles prioritários |
| 1.411 acordos coletivos, 1.402 só como referência, sem texto | 1.411 no índice, 1.402 só pela referência | «Sem texto» está errado: 1.410 dos 1.411 têm texto no índice. Sem texto são outros 732, que estão fora do índice |
| IRS, IRC, IVA e Estrada consolidados noutro registo | Confirmado | O Código Penal também (no DL 48/95). O IVA e o Penal não têm a ligação que o índice lê |

## 1. Texto em vigor dos diplomas alterados

Universo: 9.690 prioritários da 1.ª Série, em vigor ou de vigência desconhecida, com pelo menos um `amended_by`.

| Classe | Leis | Leis orgânicas | Leis const. | Decretos-leis | Dec. regulamentares | Dec. leg. regionais | Total |
|---|--:|--:|--:|--:|--:|--:|--:|
| Consolidado pelo DRE no próprio registo | 473 | 11 | 0 | 1.557 | 63 | 239 | 2.343 |
| Consolidado pelo leis-portugal | 48 | 1 | 0 | 660 | 60 | 74 | 843 |
| Texto em vigor noutro registo | 2 | 0 | 0 | 16 | 0 | 3 | 21 |
| O original é o texto em vigor (triagem: nenhum `amended_by` muda o texto) | 592 | 23 | 7 | 2.498 | 273 | 234 | 3.627 |
| Alteração por aplicar | 51 | 0 | 0 | 482 | 77 | 68 | 678 |
| Alteração só em imagem | 1 | 0 | 0 | 14 | 1 | 0 | 16 |
| Não triado | 218 | 17 | 0 | 375 | 23 | 54 | 687 |
| Revogado por inteiro (triagem) | 5 | 2 | 0 | 119 | 47 | 45 | 218 |
| Sem texto (só digitalização) | 216 | 0 | 0 | 1.041 | 0 | 0 | 1.257 |

- **Com texto em vigor: 3.207** (33 %), e outros 3.627 em que o original serve, segundo a triagem. A triagem é a do
  `consolidacao/resultados-escala.jsonl` (12/11): lê as instruções do alterador por regras, e numa amostra antiga
  errou em alguns casos. É por isso um teto de confiança, não uma verificação.
- **Em dia: 2.963 dos 3.207.** Dos outros 244, 35 foram mexidos pelo DRE depois da nossa recolha (verificado pelo
  `lastmod` do sitemap) e 210 têm um `amended_by` publicado depois da última versão e fora do histórico (teto).
  Lista: `consolidados-por-atualizar.jsonl`.
- **Por fechar: 1.381** (alteração por aplicar, só em imagem e não triados). 1.043 são citados por pelo menos um
  diploma em vigor, 213 por 10 ou mais e 29 por 50 ou mais. Lista por ordem de citações:
  `texto-em-vigor-por-fechar.jsonl`.
- **Os 687 não triados são todos de vigência desconhecida.** A seleção da consolidação só aceitava `in_force` e
  `partially_in_force`, por isso os diplomas de 2014 em diante que o DRE não classifica nunca foram vistos. Nenhum dos
  3.627 originais tem um alterador novo desde a triagem.
- **Portarias** (15.577 no mesmo critério): 2.404 consolidadas (1.097 pelo DRE e 1.307 por nós), 10.258 em que o
  original serve, 2.102 com alteração por aplicar (413 só em imagem), 305 não triadas, 409 revogadas por inteiro e 99
  sem texto.

## 2. O mesmo texto em vários registos

O DRE consolida alguns códigos no registo da lei que os republicou, e também consolida leis de alteração que trazem,
em anexo, a republicação de outro diploma. O script junta as cópias de cada texto (162 textos em mais de um registo) e
compara a data de cada cópia: a última nota «Alterado pelo/a…» dessa parte ou, sem notas, a publicação do registo.

### 2.1 Texto em vigor fora do registo que o aprovou: 31

A lista completa está em `tabelas.md`, secção 2. Os principais:

| Texto | Aprovado por | Texto mais recente em | Até | O original aponta para lá? | O original é servido como em vigor? | Numeração igual? |
|---|---|---|---|---|---|---|
| Código Penal | DL 400/82 | DL 48/95, no articulado | 2026-09-01 | **Não** | Sim, texto de 1982 (161 pedaços) | Sem epígrafes para comparar |
| Código da Estrada | DL 114/94 | Lei n.º 72/2013, anexo | 2025-04-11 | Sim | Sim, texto de 1994 (171 pedaços) | **Não**: 31 de 171 |
| Código do IRS | DL 442-A/88 | Lei n.º 82-E/2014, anexo | 2026-05-25 | Sim | Sim, texto de 1988 (157 pedaços) | **Não**: 9 de 140 |
| Código do IRC | DL 442-B/88 | Lei n.º 2/2014, anexo | 2026-01-01 | Sim | Sim, texto de 1988 | **Não**: 1 de 115 |
| Código do IVA | DL 394-B/84 | DL 102/2008, anexo IV | 2026-09-01 | **Não** | Sim, texto de 1984 | Sem epígrafes |
| Estatuto Político-Administrativo da Madeira | Lei n.º 13/91 | Lei n.º 130/99, anexo | 2000-06-26 | **Não** | Sim | — |
| Estatutos de 9 ordens profissionais | vários | Leis n.os 101, 112, 117, 123–126, 131 e 159/2015 | 2024 | 6 sim, 3 não | Sim; em 8, com uma consolidação própria mais antiga | Não |

O que se encontrou, sem corrigir:

- **O registo original aponta para o consolidado?** Em 11 dos 31. A ligação é a relação `republished_by` com a
  etiqueta «Texto em vigor…», criada por `link_republications` a partir da nota do DRE. A regra
  (`_REPUBLICATION_NOTE`, `services/linking.py`) pede «tem por base a republicação… aprovado pelo…» por esta ordem e em
  minúsculas. Falha a nota do Código Penal («Tem por base», com maiúscula), as que dizem primeiro o diploma e depois a
  republicação (Madeira, Parque Marinho dos Açores), a que diz «publicação» (Ordem dos Engenheiros) e os casos sem
  nota (IVA). O índice tem as mesmas 11 ligações (`texto_em_vigor_em`).
- **O texto original desatualizado pode ser servido como em vigor?** Sim, em 22 dos 31: o original está no índice com
  `in_force` e o texto de origem. Em 17, o original tem até uma consolidação própria do DRE, mais antiga do que a do
  republicador (o DL 173/98 tem a nota «Versão desatualizada»), e os consolidados levam peso ×1,25 na pesquisa.
- **A pesquisa troca o artigo do original pelo do consolidado com o mesmo número** (`_redirecionar`). Em 14 dos 31 a
  numeração mudou entre o original e a republicação: no Código da Estrada só 31 dos 171 artigos com o mesmo número têm
  a mesma epígrafe, no IRS 9 de 140, no IRC 1 de 115. Nesses, a troca leva a outro artigo. Não medi quantas respostas
  isto estraga: é do lado da pesquisa.
- **Uma pesquisa por «artigo X do Código do IRS» chega ao registo certo?** Sim para IRS, IRC, IVA, Estrada, Penal e
  Civil. O título mostrado é «Lei n.º 82-E/2014 › Anexo — Código do IRS › Artigo 10.º».
- **O título e a numeração do código distinguem-se dos da lei que o republicou?** Sim: os artigos do código têm a
  chave `Anexo — NOME::N.º`, e os da lei só `N.º`. No DL 48/95 não há anexo: o Código Penal é o articulado.

### 2.2 Cópias com outra data, em registos em vigor: 151 cópias, 14.853 pedaços

São os anexos «Republicação do…» de leis de alteração que o DRE também consolida, as republicações mais antigas e os
originais. O índice tem-nos como texto atual (`ate` vazio). 70 estão em consolidados do DRE cujo anexo não tem
«republica» no nome, por isso levam o peso ×1,25 dos consolidados e não o desconto ×0,6 das republicações.

| Texto | Cópia | Pedaços atuais no índice | Texto da cópia | Texto certo em | Até |
|---|---|--:|---|---|---|
| Código das Sociedades Comerciais | DL 76-A/2006, anexo I | 598 | 2006 | DL 262/86 | 2026-09-01 |
| Código dos Valores Mobiliários | Lei n.º 35/2018, anexo IV | 588 | 2018 | DL 486/99 | 2026-09-01 |
| RGICSF | Leis n.os 23-A/2022, 35/2018 e 23-A/2015 | 546, 476 e 462 | 2022, 2018, 2015 | DL 298/92 | 2025-12-28 |
| Código dos Contratos Públicos | DL 111-B/2017, anexo III | 531 | 2018 | DL 18/2008 | 2026-10-01 |
| Código Penal | Lei n.º 59/2007, anexo | 403 | 2007 | DL 48/95 | 2026-09-01 |
| CPPT | Lei n.º 118/2019 e Lei n.º 15/2001, anexos | 315 e 298 | 2019 e 2012 | DL 433/99 | 2025-07-01 |
| Lei de estrangeiros | Lei n.º 18/2022, anexo | 271 | 2022 | Lei n.º 23/2007 | 2026-09-11 |
| Código da Estrada | DL 44/2005, no articulado | 189 | 2021 | Lei n.º 72/2013 | 2025-04-11 |
| Lei Geral Tributária | Lei n.º 15/2001, anexo | 109 | 2001 | DL 398/98 | 2025-07-01 |

- **O Código da Estrada existe três vezes no índice como texto atual:** 199 artigos na Lei n.º 72/2013 (o certo), 189
  no DL 44/2005 (a republicação de 2005, que o DRE consolidou até 2021) e 171 no DL 114/94 (1994). É um candidato a
  causa das perguntas reais do Código da Estrada que correm mal. Não medi o efeito: fica para a sessão da pesquisa.
- **«Outra data» é uma comparação de datas, não de textos.** Uma cópia pode ter data anterior e o mesmo texto nos
  artigos que não mudaram. O número é por isso um teto de cópias com texto diferente, e um número verificado de
  cópias a mais no índice.
- **Texto que já não vigora:** mais 16 cópias (953 pedaços) de 13 textos cujo registo mais recente o DRE dá como
  revogado, em anexos de leis de alteração em vigor.
- Lista: `texto-em-varios-registos.jsonl`, com todas as cópias de cada texto.

### 2.3 Nomes de códigos na pesquisa

Para 39 diplomas centrais, o script pergunta «artigo N.º do Código X» ao índice, só com BM25 e a referência exata, sem
reranker. **17 chegam ao artigo pedido, 8 ao registo certo mas a outro artigo e 14 a outro registo.** Causa
verificada: `rag/referencias.py` só reconhece os nomes da tabela `CODIGOS`. Faltam lá, entre outros, a Constituição, o
CIRE, o CPTA, os Códigos do Registo Civil, Predial e Comercial, do Notariado, Cooperativo, da Publicidade, dos Valores
Mobiliários e do Direito de Autor. O «Código de Processo Penal» está na tabela, mas o sumário do DL 78/87 diz «Código
do Processo Penal» e a referência não resolve. O Código Comercial não existe no acervo, e a pergunta devolve o Código
do Registo Comercial. Com o reranker o resultado pode ser melhor: não medi.

## 3. Vigência desconhecida

| O que os dados que já temos dizem | Leis | Leis orgânicas | Decretos-leis | Dec. regulamentares | Dec. leg. regionais | Total |
|---|--:|--:|--:|--:|--:|--:|
| Revogado, segundo a relação `repealed_by` do DRE | 4 | 1 | 14 | 1 | 0 | 20 |
| Temporário ou orçamental (pelo sumário) | 17 | 2 | 15 | 2 | 34 | 70 |
| Ato de alteração (pelo sumário): a vigência pouco importa | 217 | 20 | 503 | 21 | 165 | 926 |
| Alterado depois e sem revogação registada | 35 | 1 | 73 | 8 | 9 | 126 |
| Sem indício de revogação | 479 | 7 | 567 | 33 | 221 | 1.307 |
| **Total** | **752** | **31** | **1.172** | **65** | **429** | **2.449** |

- **Porquê:** `legal_status` vem do campo `Vigencia` do DRE (`sources/dre/mapper.py`, linha 49). Consultei hoje o DRE
  para a Lei n.º 58/2019 e a Lei n.º 93/2021: o campo vem vazio. Desde 2014 o DRE deixa muitos diplomas sem estado: entre 2014 e
  2025, de 32 % a 73 % das leis e decretos-leis de cada ano (286 de 436 em 2015, 188 de 256 em 2023). Em 2026 são 31 de 316.
  Antes de 2010 são só 30.
- **Quantos se resolvem com o que temos:** 20 pela relação de revogação, e 126 têm prova de que vigoravam na data da
  última alteração. Os 926 atos de alteração e os 70 temporários resolvem-se por regra, com pouco risco. Para os 1.307
  sem indício, a regra «sem revogação registada, está em vigor» é provável, mas não está verificada: o DRE também não
  regista todas as revogações.
- **Efeito no produto:** a pesquisa dá peso ×0,85 a `unknown`, e 11 dos 198 diplomas centrais estão assim: Leis
  n.os 58/2019, 59/2019, 83/2019, 95/2019, 117/2019, 49/2018, 8/2018, 93/2021, 95/2021 e 35/2023, e o DL 84/2021.
- Na 1.ª Série há mais 36.912 decretos e 23.701 portarias sem estado, quase todos anteriores a 1960 e só com
  digitalização. Lista dos prioritários: `vigencia-desconhecida.jsonl`.

## 4. O que o DRE consolida e nós não temos

O sitemap da legislação consolidada tinha 6.029 entradas a 19/11. Temos 5.664, todas recolhidas a 22/10.

- **365 em falta.** 158 são as do `reports/dre_consolidated_failures.jsonl` (o DRE lista-as mas o texto vem vazio; 43
  são de tipos prioritários). **207 são novas desde 22/10:** 24 decretos-leis, 4 leis, 4 decretos legislativos
  regionais, 21 portarias e 154 de outros tipos (despachos, avisos). O DRE está a consolidar diplomas de 2000–2001.
- **62 das que temos foram mexidas pelo DRE depois da recolha:** 34 decretos-leis, 2 leis e 19 portarias. Entre elas a
  Lei n.º 82-E/2014 (IRS, a 16/11), o DL 102/2008 (IVA), o DL 73/2010 (IEC), o DL 18/2008 (Contratos Públicos) e o
  DL 102-D/2020 (resíduos).
- Nenhum consolidado nosso deixou de estar no sitemap.
- Listas: `dre-consolidados-em-falta.jsonl` (só o endereço: o sitemap não diz o diploma) e
  `dre-consolidados-mexidos.jsonl`.

## 5. Antigos em vigor e sem texto

- **O texto começa em 1960.** Antes disso há 53 registos portugueses com texto (38 prioritários). O resto de
  1910–1959 é digitalização: 2.394 leis, 7.111 decretos-leis e 859 decretos que o DRE dá como em vigor, mais 36.643
  decretos sem estado. Antes de 1910 há 89 que o DRE dá como em vigor, só com metadados.
- **O Código Comercial de 1888 não existe no acervo**, nem como registo sem texto: não há nenhum diploma de 1888 com
  esse sumário, e o sitemap dos consolidados do DRE não tem nenhuma entrada anterior a 1926. É preciso outra fonte.
- **Citados por diplomas em vigor com texto:** 1.616 por pelo menos um, 407 por 5 ou mais, 81 por 20 ou mais e 18 por
  100 ou mais. Os mais citados são regras antigas de contabilidade pública (Decreto n.º 16670, de 1929, com 1.518
  citações; DL 25299; DL 41375), citadas por diplomas orçamentais. 1.832 têm `amended_by`.
- Os de 1960–1996 têm texto. Lista dos 407: `antigos-sem-texto-citados.jsonl`.

## 6. Lista de controlo dos diplomas centrais

198 códigos e regimes, em `scripts/inventario_diplomas_centrais.json`. A tabela completa, com uma linha por diploma
(registo onde vive, vigência, data do texto, se está em dia e problemas), está em
[`inventario-camada-1/tabelas.md`](inventario-camada-1/tabelas.md), secção 6.

| Situação | Diplomas |
|---|--:|
| Sem nenhum problema | 130 |
| Texto consolidado pelo DRE (no próprio registo ou noutro) | 178 |
| … dos quais em dia | 173 |
| … que o DRE mexeu depois da recolha (IRS, IVA, IEC, Contratos Públicos, resíduos) | 5 |
| Texto em vigor noutro registo (IRS, IRC, IVA, Estrada, Penal) | 5 |
| … sem ligação do original (IVA, Penal) | 2 |
| Com cópias de outra data servidas como atuais | 34 |
| Vigência desconhecida | 11 |
| Alterados e nunca triados (Leis n.os 58/2019, 59/2019, 83/2019, 95/2019, 95/2021, 49/2018, 8/2018) | 7 |
| Alteração por aplicar (Lei n.º 19/2014; DL 139-A/90) | 2 |
| Original sem alterações registadas | 8 |
| Alterados em que a triagem diz que o original serve (Lei n.º 63/2011; DL 62/2013) | 2 |
| Fora do acervo (Código Comercial) | 1 |

Três casos a ver à mão:

- **Estatuto da Carreira Docente (DL 139-A/90).** O texto mais recente está no anexo do DL 41/2012, consolidado pelo
  DRE até 2023-12-30. O script não liga os dois, porque o original não tem as mesmas epígrafes. Conta por isso como
  «alteração por aplicar», e a secção 2.1 é um mínimo.
- **Lei do Tribunal Constitucional (Lei n.º 28/82).** Tem dois registos: `pt:dre:626985`, consolidado até 2022, e
  `pt:dre:377508`, com o texto de 1982, vigência desconhecida e nenhuma alteração registada.
- **Consolidações antigas.** 13 centrais têm o texto parado antes de 2016 (Lei de Bases da Segurança Social em 2013,
  responsabilidade civil do Estado em 2008, agência em 1993). Não há `amended_by` posterior, por isso contam como em
  dia. Não confirmei no DRE se não houve mesmo alterações.

## 7. Fora do export e do índice

| Fonte | Em `data/` | No export | No índice |
|---|--:|--:|--:|
| CNPD | 122.225 | 0 | 0 |
| Tribunal Constitucional | 34.753 | 0 | 0 (chega às respostas por `normas-julgadas.jsonl`) |
| Acordos coletivos com texto (2.ª Série) | 1.411 | 1.411 | 1.411, dos quais 1.402 só pela referência |
| Acordos coletivos sem texto | 732 (252 só metadados, 480 só PDF) | 732 | 0 |

O export tem só `pt:dre:` (405.830) e `eu:celex:` (55.250).

## Limites deste inventário

- A separação entre «alteração que muda o texto» e «`amended_by` sem alteração textual» é a da triagem da
  consolidação, de 12/11. Não foi refeita.
- A deteção de textos em vários registos parte dos consolidados do DRE com anexos de 10 ou mais artigos e compara
  números de artigo e epígrafes. Não vê cópias em registos que o DRE não consolida, nem pares sem epígrafes e sem nota
  do DRE.
- «Em dia» não vê uma alteração que o DRE não tenha registado como `amended_by`.
- A lista de controlo foi escrita à mão: os 198 títulos resolvem todos menos o Código Comercial, mas a escolha dos
  diplomas é minha e pode faltar algum.
