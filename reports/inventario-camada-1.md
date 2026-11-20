# Inventário da camada 1: o que falta ao texto da lei

Medido a 19/11/2026 sobre o export das 23h45 (405.830 registos portugueses), o `data/` do `main`, o sitemap da
legislação consolidada do DRE desse dia e o índice `indice-final.sqlite` (só leitura). Nada foi alterado no `data/`,
no export nem no índice.

- **Âmbito:** 1.ª Série. «Prioritários» são as leis, leis orgânicas, leis constitucionais, decretos-leis, decretos
  regulamentares e decretos legislativos regionais. As portarias têm só contagens. A 2.ª Série fica de fora.
- **Para repetir:** `python scripts/inventario_camada_1.py --descarregar-sitemap --indice rag/indice/indice.sqlite`
  (meio minuto sem o índice e com `--sem-leitura`; a secção 8 lê todos os `.md` e leva mais minuto e meio). Grava
  `reports/inventario-camada-1/`: `resumo.json` com todos os números, `tabelas.md` com as tabelas completas e uma
  lista `.jsonl` por falha.
- **«Verificado»** quer dizer contado no registo, no índice ou no DRE. **«Teto»** quer dizer que o número vem de uma
  regra (a triagem da consolidação, uma comparação de datas, o sumário) e que o número real é igual ou menor.

## Atualização de 20/11/2026: as linhas 1 e 2 têm regra no índice

- **O que mudou.** `rag/copias.py` junta as cópias de cada texto e diz quais são redação anterior, com prova. O
  `rag.indice` fecha os pedaços dessas cópias com `ate`, como qualquer redação antiga de um consolidado, e grava a
  ligação para o registo com o texto atual. Nada se apaga. As listas estão em `reports/redacoes-anteriores/`.
- **Contagens** sobre o export de 19/11 (23h45): 641 textos em mais de um registo, **536 cópias marcadas em 493
  registos** e 345 de fora (200 sem prova de um texto posterior, 140 em que o registo mais recente já não vigora,
  4 em que o articulado de um diploma de alteração se mistura com o texto citado e 1 em texto corrido). Num índice de
  ensaio só com estes registos, a regra fecha 43.596 pedaços.
- **Das 151 cópias da linha 1, a regra marca 135** (14.247 dos 14.853 pedaços). Das outras 16, 11 deixaram de contar
  como cópias porque o texto dos artigos não o prova, 3 passaram a ser a cópia atual ou outra parte, e 2 misturam o
  articulado do diploma de alteração.
- **A deteção alargou-se** aos diplomas que alteram um texto e o republicam sem o DRE os consolidar com nome de anexo
  (os DL 2/98, 265-A/2001 e 44/2005 no Código da Estrada, o DL 198/2001 no IRS e no IRC, as Leis n.os 30/2012 e
  129/2015). Por isso `tabelas.md` e os `.jsonl`, regenerados a 20/11, têm mais textos e mais cópias do que as
  secções 2.1 e 2.2 abaixo, que são a medição de 19/11 e ficam como registo.
- **O índice foi reconstruído com a regra** a 20/11 (1h15): fecha 43.596 pedaços em 493 registos, os mesmos números
  do ensaio (lidos na tabela `meta`). Falta medir nas 1.298 perguntas. As linhas 3 a 11 não mudaram.

## Atualização de 20/11/2026 (4h): o que o índice não lê como artigos

- **Três reparos da sessão do diagnóstico, verificados:** a Lei n.º 13/2003 sem artigos em vigor, as leis de bases que
  o índice não lê, e a passagem mostrada na resposta (esta é da pesquisa, não entra aqui).
- **O que se acrescentou:** a secção 8, com as contagens, e as linhas 12 a 18 do resumo. O script ganhou a secção 8
  (`leitura-fora-dos-artigos.jsonl`, `anexos-em-maiusculas.jsonl`, `indice-sem-artigos-abertos.jsonl`,
  `revogacoes-por-produzir-efeitos.jsonl`).
- **Sobre quê:** o export de 20/11 (1h01), o `data/` do `main` e o índice reconstruído à 1h15 com as redações anteriores
  (`indice-redacoes.sqlite`, só leitura). `tabelas.md`, `resumo.json` e os `.jsonl` foram regenerados sobre este índice:
  na secção 2, os pedaços «atuais» das cópias já são os que sobram depois da regra.
- **Nada foi corrigido.** As correções estão descritas em 8.6, com o que entrava no índice.

## Atualização de 20/11/2026 (manhã): as falhas de leitura têm correção no código

- **Corrigido no código que lê os dados** (o `data/` não mudou): as linhas 12, 13, 14, 15 e, nas bases com título, a 16.
  A descrição e os números de antes e depois estão em `rag/README.md`, «O que o índice lê de um registo».
- **A secção 8 abaixo é a medição de antes da correção** e fica como registo. O `resumo.json`, o `tabelas.md` e os
  `.jsonl` também são de antes: regeneram-se sobre o índice novo, quando for reconstruído. O script já mede com o leitor
  novo (conta só o que continua por ler como unidade).
- **Fica por corrigir:** a linha 17 (texto corrido por marcar) e as bases soltas da linha 16, medidas numa amostra de
  50 registos em `reports/leitura-texto-corrido-amostra.md`; e a linha 18, que é do estado no DRE.

## Atualização de 20/11/2026 (tarde): falhas de dados

- **Linhas 5, 10, 8 e 18:** o que se fechou, com os números de antes e depois, está em
  `reports/camada-1-falhas-de-dados.md`. A linha 3 tem lá a regra e a amostra, por aplicar.
- **Os ficheiros de `reports/inventario-camada-1/`** foram regenerados sobre o índice publicado (`indice-fase1.sqlite`) e
  o sitemap do DRE de 20/11, com o export de antes da recolha da linha 5.

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

Acrescentadas a 20/11 (secção 8), pela mesma ordem. «Em vigor» é `in_force` ou `partially_in_force` no DRE.

| # | Falha | Tipo | Quantos | Verificado ou teto | Esforço | Valor para o produto |
|---|---|---|---|---|---|---|
| 12 | Consolidados com histórico e sem `###### Artigo`: ficam sem um único pedaço no índice | apresentação (índice) | 2.343 em vigor: 45 prioritários, 1.436 portarias, 366 resoluções do Conselho de Ministros; a Lei n.º 52/2012 entre eles | Verificado no índice | Baixo: cair nos blocos | Alto: regulamentação em vigor que a pesquisa não pode devolver |
| 13 | `## ANEXO` em maiúsculas: os artigos do anexo ficam na parte do diploma | apresentação (leitura) | 1.946 registos em vigor (725 prioritários), 71.805 artigos; em 1.229 registos, 12.514 artigos com o número de um artigo do diploma. Mais 3.514 registos de vigência desconhecida, com 118.289 artigos | Verificado no `data/`; a mistura confirmada no índice em 10 casos | Baixo: ler «ANEXO» sem olhar a maiúsculas | Alto: regulamentos e códigos anexos respondem como «artigo N.º do decreto» |
| 14 | Revogações que ainda não produziram efeitos, lidas como revogação | apresentação (leitura) | 197 artigos em 15 registos; 5 registos em vigor com todos os artigos dados como revogados (Lei n.º 13/2003, DL 464/80, DL 568/99, DL 208/2001, Portaria n.º 257/2012) | Verificado no índice e no DL 166/2026 | Baixo: comparar a data de efeitos com a data da pergunta | Médio: rendimento social de inserção até 30/12/2026; 133 dos 197 resolvem-se sozinhos a 31/12 |
| 15 | «ARTIGO» em maiúsculas nos títulos: o registo entra em blocos, sem número nem epígrafe | apresentação (leitura) | 1.685 registos em vigor (821 prioritários), 26.731 artigos; quase todos de 1970–1989 | Verificado no `data/` e, por amostra, no índice | Baixo: ler «ARTIGO» sem olhar a maiúsculas | Médio: Lei Constitucional n.º 1/82, convenções aprovadas por decreto |
| 16 | Bases em vez de artigos | apresentação (leitura) e dados (`structure`) | 245 registos em vigor (195 prioritários) e 23 de vigência desconhecida, com 8.646 e 1.712 bases; só 37 registos as têm como título | Verificado | Médio: o leitor para os títulos, o `structure` para as 284 em texto corrido | Médio: Lei de Bases da Saúde e dos Cuidados Paliativos; o resto são bases de concessões |
| 17 | Texto corrido com «Artigo 1.º … Art. 2.º …» por marcar | dados (`structure`) | 8.768 registos em vigor em blocos (4.000 prioritários), 114.511 artigos | Teto: contagem por expressão regular no início das linhas | Médio a alto: `structure` e revisão | Médio: decretos-leis de 1960–1999 em vigor |
| 18 | Em vigor no DRE com todos os artigos revogados | estado | 59 registos (37 prioritários): Lei n.º 99/2003, DL 94-B/98, DL 275-A/2000 | Verificado no índice (as notas são do DRE) | Baixo | Baixo: cada artigo já sai com o aviso de revogado |

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

## 8. O que o índice não lê como artigos (20/11/2026)

O índice parte cada registo em artigos pelos títulos `###### Artigo N.º` e separa os anexos pelos títulos `## Anexo`
(`avaliacao/comum.py`, que o `rag.indice` usa). O que não tem esta forma segue um de cinco caminhos:

- **sem pedaços:** o registo tem histórico de versões (`.versoes.json`) e nenhum artigo lido. O índice lê o histórico,
  não encontra artigos e não cai nos blocos de texto. O registo fica na tabela `documentos` e sem nenhum pedaço: a
  pesquisa não o pode devolver;
- **em blocos:** sem histórico e sem artigos, o texto entra em blocos de cerca de 300 palavras, pesquisáveis mas sem
  número nem epígrafe;
- **dentro de um artigo:** a unidade vem depois de um artigo na mesma parte e fica colada ao texto dele;
- **cortada:** o mesmo, para lá dos 30.000 caracteres a que o índice corta cada pedaço;
- **fora do índice:** a unidade vem a seguir a um `## Anexo` e antes de qualquer artigo desse anexo. Não entra.

### 8.1 Lei n.º 13/2003: a revogação só produz efeitos a 31/12/2026

- **No índice tem 62 artigos abertos**, em todos os índices de 17/11 a 20/11. Não tem «0 artigos»: tem 0 artigos que
  o leitor dê como não revogados.
- **Porquê:** os 62 trazem uma nota «Revogado pelo/a…». 24 foram revogados entre 2005 e 2017. Os outros 38 têm a
  nota do artigo 62.º do Decreto-Lei n.º 166/2026, «em vigor a partir de 2026-08-14, com efeitos a partir de
  2026-12-31». O artigo 63.º desse decreto-lei diz que entra em vigor no dia útil seguinte ao da publicação e produz
  efeitos a 31 de dezembro de 2026 (verificado no `data/`).
- **O leitor (`rag.fontes.revogado`) só vê a palavra «Revogado»** e a data de publicação da nota. Não compara a data
  de efeitos com a data da pergunta.
- **Efeito:** até 30/12/2026 os 38 artigos estão em vigor, mas a pesquisa põe-nos atrás dos não revogados do mesmo
  nível, tira-lhes peso e mostra «Artigo revogado»; as perguntas por artigo deixam-nos de fora. O DRE dá a lei como
  `partially_in_force`.
- **Quantos têm o mesmo problema:** 197 artigos em 15 registos. Por data de efeitos: 5 a 28/11/2026, 1 a 1/12, 133 a
  31/12 (os do DL 166/2026: prestações sociais), 16 a 1/1/2027, 41 a 1/3/2027 e 1 em 2032. Em 5 registos em vigor
  ficam todos os artigos abertos como revogados: Lei n.º 13/2003 (38 dos 62), DL 464/80 (22 dos 24), DL 568/99 (41 de
  41), DL 208/2001 (8 de 8) e Portaria n.º 257/2012 (32 dos 36). Lista: `revogacoes-por-produzir-efeitos.jsonl`.

### 8.2 Em vigor no DRE e sem um artigo aberto e não revogado: 2.422

Registos portugueses com texto, `in_force` ou `partially_in_force`, no índice de 20/11 (1h15). Nenhum de vigência
desconhecida está nesta situação.

| Classe | Prioritários | Portarias | Outros | Total | Causa |
|---|--:|--:|--:|--:|---|
| Sem um único pedaço | 45 | 1.436 | 862 | 2.343 | Consolidado com histórico e sem `###### Artigo` (linha 12) |
| Pedaços abertos, todos com nota de revogação | 37 | 13 | 9 | 59 | O DRE dá o diploma como em vigor e todos os artigos como revogados (linha 18) |
| Todos os pedaços fechados, com ligação ao registo que tem o texto | 15 | 0 | 0 | 15 | A regra das redações anteriores (DL 114/94, DL 44/2005…): é o pretendido |
| Pedaços abertos, todos dados como revogados, com revogações por produzir efeitos | 4 | 1 | 0 | 5 | 8.1 (linha 14) |

- **Os 2.343 sem pedaços** são 2.226 em texto corrido e 117 com unidades que o leitor não conhece (títulos «1.º»,
  «Base», «ARTIGO», «Cláusula»). Por tipo: 1.436 portarias, 366 resoluções do Conselho de Ministros, 139 despachos
  normativos, 90 avisos, 46 decretos do Presidente da República, 33 decretos-leis. A contagem feita no `data/` (histórico
  e nenhum artigo lido) dá os mesmos 2.343 que a contagem no índice. Lista: `indice-sem-artigos-abertos.jsonl`.
- Sem vigência (revogados ou caducados) há mais 117 sem pedaços e 735 só com artigos revogados; não são falha.

### 8.3 Bases em vez de artigos

312 registos têm o texto, ou um anexo, organizado em bases. São 245 em vigor (195 prioritários), 23 de vigência
desconhecida e 44 sem vigência. Só 37 têm as bases como título (`###### Base I — …`, todos consolidados do DRE); nos
outros 284 a «Base N» está sozinha numa linha de texto corrido (9 têm as duas formas).

| Onde ficam as bases dos registos em vigor | Bases com título | Bases soltas no texto | Total |
|---|--:|--:|--:|
| Fora do índice (a seguir a um `## Anexo`) | 1.705 | 22 | 1.727 |
| Em blocos de texto | 0 | 2.810 | 2.810 |
| Dentro do texto de um artigo, até aos 30.000 caracteres | 52 | 1.722 | 1.774 |
| Cortadas, para lá dos 30.000 caracteres | 129 | 2.012 | 2.141 |
| Em registos sem pedaços | 71 | 123 | 194 |
| **Total** | **1.957** | **6.689** | **8.646** |

- **Lei n.º 52/2012 (cuidados paliativos):** 35 bases com título, registo consolidado com histórico, **0 pedaços**. As
  outras três nesta situação são as Leis n.os 4/73 e 5/73 e o DL 193/92.
- **Lei n.º 95/2019 (Lei de Bases da Saúde):** está como texto original e de vigência desconhecida. As 37 bases estão
  num `## ANEXO` em maiúsculas, soltas no texto: 34 ficam dentro do pedaço do artigo 4.º («Entrada em vigor»), que tem
  os 30.000 caracteres do limite, e 3 são cortadas. Verificado no índice.
- **A maior parte são bases de concessões** (autoestradas, águas, gás, portos) anexas a decretos-leis: 139 dos 245
  registos em vigor são decretos-leis. No DL 62/2020 as 184 bases estão fora do índice; no DL 248-A/99, as 105.
- **Leis em vigor com bases: 37.** Trinta e duas são de 1960 a 1973 (Lei n.º 2127, dos acidentes de trabalho; Lei
  n.º 2114, do arrendamento rural; Lei n.º 5/73, da reforma do sistema educativo). Quatro são leis posteriores que só
  alteram ou citam duas ou três bases. A outra é a Lei n.º 52/2012. As leis de bases recentes (educação, segurança
  social, habitação, clima) usam artigos e leem-se bem. Lista em `tabelas.md`.

### 8.4 Outras unidades que o leitor não conhece

| Unidade | Registos | Em vigor | Dos quais prioritários | Unidades nos em vigor | Onde ficam |
|---|--:|--:|--:|--:|---|
| `###### ARTIGO N.º` em maiúsculas | 2.168 | 1.685 | 821 | 26.731 | 24.973 em blocos, 862 dentro de um artigo, 515 fora do índice, 339 em registos sem pedaços, 42 cortadas |
| `###### 1.º` ou `###### IV` (número sem «Artigo») | 172 | 137 | 3 | 1.157 | 908 em registos sem pedaços, 187 fora do índice, 62 dentro de um artigo |
| «Cláusula N» | 1.803 | 209 | 11 | 4.307 | 3.560 em blocos; 1.285 dos registos são acordos coletivos de vigência desconhecida |
| `## ANEXO` em maiúsculas com artigos a seguir | 6.393 | 1.946 | 725 | 71.805 artigos | na parte do diploma, e não na do anexo; mais 3.514 registos de vigência desconhecida, com 118.289 artigos |

- **«ARTIGO» em maiúsculas:** 538 leis, 407 decretos, 231 decretos-leis e 150 portarias em vigor, quase todos de 1970
  a 1989 (a Lei Constitucional n.º 1/82 tem 590, o DL 42826 tem 684). Numa amostra de 300 registos, 5.360 dos 5.361
  títulos têm um número que o leitor atual sabe ler.
- **`## ANEXO` em maiúsculas:** o leitor só conhece `## Anexo`. Os artigos do anexo ficam com a parte vazia, como os
  do diploma. Em 1.229 registos em vigor, 12.514 artigos do anexo têm o número de um artigo do próprio
  diploma: há dois «artigo 1.º» na mesma parte. Verificado no índice: o DL 177/2026 tem 581 pedaços abertos na parte
  vazia (11 do decreto e 570 do Código dos Contratos Públicos republicado), a Lei n.º 59/98 tem 542. Estes anexos também
  não levam o desconto das republicações, que procura «republica» no nome da parte. Lista: `anexos-em-maiusculas.jsonl`.
- **Sem artigo e sem anexo com nome,** o texto de um anexo em maiúsculas cola-se ao último artigo do diploma (é o caso
  da Lei n.º 95/2019). É por isso que há bases «dentro de um artigo».

### 8.5 Texto corrido com artigos por marcar (teto)

8.768 registos em vigor entram em blocos e têm três ou mais linhas a começar por «Artigo N.º» ou «Art. N.º»: são
114.511 artigos que o `structure` não marcou como título. 4.000 são prioritários e 1.469 são portarias. Nas leis e
decretos-leis: 1.227 são de 1960–1969, 1.059 de 1970–1979, 765 de 1980–1989 e 436 de 1990–1999. É um teto: a contagem é por expressão regular no início das linhas e não foi vista caso a
caso. A pesquisa encontra o texto, mas não o artigo pelo número.

### 8.6 Correções, sem as fazer, e o que entrava

| Correção | Onde | O que entrava no índice |
|---|---|---|
| Quando o histórico não dá nenhum pedaço, ler o `.md` (artigos ou blocos) | `rag/indice.py`, `pedacos_do_documento` | 2.343 registos em vigor, em cerca de 11.330 blocos (contados com o partidor do índice; o script estima 11.640 pelos caracteres) |
| Ler `## ANEXO` sem olhar a maiúsculas | `avaliacao/comum.py`, `_ANEXO` | Nenhum pedaço novo: 71.805 artigos de 1.946 registos em vigor (e 118.289 de 3.514 de vigência desconhecida) mudam de parte e deixam de repetir chaves. As chaves mudam, por isso as perguntas por artigo e os conjuntos de avaliação que as usam têm de ser conferidos. **Risco:** o texto de um anexo sem artigos, que hoje se cola ao último artigo do diploma, passava a ficar fora do índice (as 34 bases da Lei n.º 95/2019, por exemplo). Só deve entrar com a correção seguinte, ou com o texto dos anexos sem artigos a entrar em blocos |
| Ler `###### ARTIGO`, `###### Base` e `###### N.º` como unidades | `avaliacao/comum.py`, `_ARTIGO` | Nos registos em vigor: 26.731 artigos, 1.957 bases e 1.157 números passam a pedaços com número e epígrafe (hoje, 24.973 estão em blocos e 2.407 fora do índice). Para as bases, a referência («base IV da Lei n.º 52/2012») também tem de ser lida em `rag/referencias.py` |
| Comparar a data de efeitos da revogação com a data da pergunta | `rag/fontes.py`, `revogado`, e quem a chama | 197 artigos em 15 registos deixam de sair como revogados até à data de efeitos; o aviso pode dizer a data |
| Marcar as «Base N» soltas e os «Artigo N.º» em texto corrido | `structure` (muda o `data/`) | 6.689 bases em 219 registos em vigor, mais as 37 da Lei n.º 95/2019; até 114.511 artigos em 8.768 registos (teto) |

A segunda e a terceira mexem no leitor que a avaliação também usa: convém medir nas 1.298 perguntas antes e depois.
Não contei quanto texto de anexos sem artigos fica hoje fora do índice para além das bases (tabelas, mapas, estatutos
em texto corrido a seguir a um `## Anexo`).

## Limites deste inventário

- A separação entre «alteração que muda o texto» e «`amended_by` sem alteração textual» é a da triagem da
  consolidação, de 12/11. Não foi refeita.
- A deteção de textos em vários registos parte dos consolidados do DRE com anexos de 10 ou mais artigos e compara
  números de artigo e epígrafes. Não vê cópias em registos que o DRE não consolida, nem pares sem epígrafes e sem nota
  do DRE.
- «Em dia» não vê uma alteração que o DRE não tenha registado como `amended_by`.
- A secção 8 conta os títulos no `.md`. Nos registos com histórico o índice lê as versões e não o `.md`; a última
  versão é o `.md`, mas a comparação não foi feita registo a registo. O total de registos sem pedaços bate com o índice.
- Na secção 8, «em vigor» é o estado do DRE. Os de vigência desconhecida estão contados à parte e só nas bases.
- Os «artigos por marcar» em texto corrido (8.5) são uma contagem por expressão regular: é um teto.
- A lista de controlo foi escrita à mão: os 198 títulos resolvem todos menos o Código Comercial, mas a escolha dos
  diplomas é minha e pode faltar algum.
