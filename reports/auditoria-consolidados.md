# Auditoria dos consolidados do leis-portugal: retificações e vigência

Medido a 19/11/2026 sobre o `data/` do commit 67caa01b451. Só leitura: o `data/` e o índice não mudaram.

O bloco 3 da consolidação (ronda 114, `PENDENTE.md`, secção 7) deixou dois achados por decidir. Este relatório mede a dimensão de cada um nos diplomas que o leis-portugal já consolidou.

- **Retificações fora da cadeia.** As declarações de retificação que o DRE dá como `corrected_by` não entram nos alteradores.
- **Vigência.** Há diplomas com o texto certo que já não vigoram, embora o DRE os dê como `in_force`.

O script é o `consolidacao/auditoria.py`, e o teste é o `tests/test_auditoria_consolidados.py`. Os resultados linha a linha estão em `consolidacao/auditoria/`:

- `retificacoes.jsonl`: uma linha por retificação por aplicar;
- `vigencia.jsonl`: uma linha por consolidado;
- `resumo.json`: as contagens.

## Resumo

| | Número |
|---|--:|
| Consolidados pelo leis-portugal no `data/` | **2.773** |
| … com pelo menos uma retificação `corrected_by` | 310 |
| … com uma retificação **por aplicar** | **221** |
| Retificações `corrected_by` ao todo | 337 |
| … aplicadas (estão nos `acts`) | 93 |
| … **por aplicar** | **244** |
| … por aplicar, de depois do original e de antes da consolidação | **234** |
| … por aplicar que se aplicariam **por regra** | **61** (+14 com correspondência aproximada) |
| … por aplicar que precisam do **LLM** | **116** (103 com pares que a regra não aplica + 13 sem pares legíveis) |
| … por aplicar sem nada a fazer no texto em vigor | 36 (trecho já reescrito, já no texto ou só nos metadados) |
| Consolidados numa das quatro classes de vigência (certeza alta) | **894** |
| … e com certeza incerta, contados à parte | 140 |
| Consolidados que o próprio registo do DRE dá como revogados | **39** (7 pelo `legal_status`, 32 por uma relação `repealed_by` de revogação inteira) |

O `PENDENTE.md` diz 2.767. O script conta os `*.versoes.json` com `consolidated_by` a começar por «leis-portugal» e encontra 2.773. A diferença de 6 não ficou explicada. Um deles é o DN 681/94 (`pt:dre:606505:por`): está em `acervo.DE_FORA` como «nunca aplicado», mas está consolidado no `data/` desde o commit a3b999d6f96 (frente B, 29/10).

## 1. Retificações fora da cadeia

### Números

Das 337 relações `corrected_by` dos 2.773 consolidados, **244 não foram aplicadas**. Estão em **221 diplomas**.

- **Datas.** 234 datam de depois do original e de antes da `consolidation_date`. Pertenciam, portanto, ao texto que consolidámos. As outras 10 são posteriores à consolidação. Nenhuma é anterior ao original.
- **No acervo.** 238 das 244 estão no acervo. As 6 que faltam são, em 5 casos, correções materiais de PDM da 2.ª série (RCM 130/99, de Sousel, e RCM 106/95, de Reguengos de Monsaraz) e, num caso, a Decl. Ret. 669/2012.

Classes das 244, pelo que o script lê de cada retificação:

| Classe | Retificações | Diplomas | O que quer dizer |
|---|--:|--:|---|
| `por_regra` | 61 | 58 | Cada «onde se lê» aparece **uma vez**, letra a letra, no texto em vigor |
| `por_regra_aprox` | 14 | 14 | Idem, mas só sem pontuação nem maiúsculas («artigo 50» e «artigo 50.º») |
| `llm` | 103 | 98 | Há pares, mas pelo menos um não se encontra (`ausente`), aparece mais de uma vez (`varios`) ou não tem aspas (`sem_aspas`, quase sempre quadros e mapas) |
| `sem_pares` | 13 | 13 | Sem «onde se lê … deve ler-se …» legível nem imagem: supressões descritas por extenso, preâmbulos, portarias que «retificam» uma expropriação |
| `imagem_ou_republicacao` | 11 | 10 | Republica o texto inteiro ou um mapa, este quase sempre em imagem |
| `substituida` | 23 | 23 | O «onde se lê» está no original publicado mas já não no texto em vigor: uma alteração posterior reescreveu o trecho |
| `ja_no_texto` | 8 | 8 | O «deve ler-se» já está no texto (o DRE publicou o original já corrigido) |
| `so_metadados` | 2 | 2 | Só corrige o sumário, o título ou a data |
| `outro_diploma` | 3 | 3 | A retificação não menciona o número do original |
| `sem_registo` | 6 | 3 | A retificação não está no acervo |

Por diploma, 185 dos 221 têm pelo menos uma retificação com trabalho a fazer (as quatro primeiras classes e `imagem_ou_republicacao`). Em 66 destes, todas as que têm trabalho são `por_regra` ou `por_regra_aprox`. Os outros 36 diplomas não pedem nada no texto em vigor.

Os 3 casos `outro_diploma` são erros do DRE ou retificações de um alterador:

- **Decreto 678/76.** A declaração DD8202 retifica o DL **677/76**, não o 678/76. Foi lido à mão.
- **DR 76/86 e Portaria 1179/82.** As retificações são do alterador (o DR 34/90 e a Portaria 681/86) e só contam se esse alterador foi aplicado.

### Amostra de 10, aberta à mão

Escolhida ao acaso entre as 244 (`random.seed(1)`).

| # | Original | Retificação | Classe | Muda o texto em vigor? |
|--:|---|---|---|---|
| 1 | DL 436/73 (`pt:dre:413845:por`) | Retificação de 8/9/1973 (`pt:dre:413453:por`) | imagem | **Não, no Markdown.** Volta a publicar o mapa do art. 1.º, que está em imagem. |
| 2 | Portaria 78-A/79 (`pt:dre:402699:por`) | Declaração de 13/2/1979 (`pt:dre:165032:por`) | por_regra | **Sim.** No n.º 1.º, a remissão passa de «alínea c)» a «alínea b)». |
| 3 | RCM 91/2002 (`pt:dre:371032:por`) | Decl. Ret. 21/2002 (`pt:dre:153115:por`) | imagem/republicação | **Sim.** Republica o Regimento do Conselho de Ministros inteiro, e 24 blocos diferem do texto em vigor. Parte disto pode vir da RCM 66/2003, já aplicada, por isso pede o LLM. |
| 4 | RAR 8/98 (`pt:dre:197366:por`) | Decl. Ret. 11/98 (`pt:dre:479418:por`) | llm | **Sim.** No art. 11.º, n.º 2, acrescenta «especialista». Nos mapas I e IV, o índice 295 passa a 290 e uma remissão passa do art. 2.º ao 3.º. Os trechos têm «[...]», por isso não se encontram letra a letra. |
| 5 | Portaria 618/2008 (`pt:dre:456533:por`) | Decl. Ret. 43/2008 (`pt:dre:455129:por`) | llm | **Sim.** Na legenda do anexo II, «classe 4)» passa a «classe 4) e 5)». O trecho não está no texto: o anexo deve estar em imagem. |
| 6 | Decreto 683-A/76 (`pt:dre:384608:por`) | Declaração de 24/9/1976 (`pt:dre:409151:por`) | por_regra_aprox | **Sim.** Corrige três gralhas nos arts. 10.º e 22.º: «escutar» passa a «executar» e «29» a «23 de Janeiro». Corrige também o título, de «Decreto» para «Decreto-Lei». |
| 7 | DL 353/89 (`pt:dre:549019:por`) | Declaração de 31/10/1989 (`pt:dre:505240:por`) | llm (`sem_aspas`) | **Não, no Markdown.** O número de lugares do mapa do art. 27.º está em imagem dos dois lados. |
| 8 | DL 427/72 (`pt:dre:291607:por`) | Ato «não especificado» (`pt:dre:291609:por`) | sem_pares | **Não no dispositivo.** Publica o preâmbulo comum dos DL 426/72 a 430/72. |
| 9 | DN 10-A/98 (`pt:dre:297399:por`) | Decl. Ret. 19-M/98 (`pt:dre:235757:por`) | por_regra_aprox | **Sim, na forma.** No anexo A, «Artigo 1.º Critérios de selecção» passa a «1.º …» e o primeiro parágrafo ganha «1 -». |
| 10 | Portaria 374/2007 (`pt:dre:520412:por`) | Decl. Ret. 50/2007 (`pt:dre:638531:por`) | llm (`varios`) | **Sim.** Nos estatutos da Cinemateca, «Departamento de Exposição Permanente» passa a «… de Divulgação e Exposição Permanente» em três artigos. |

Em 7 dos 10, a retificação muda o texto em vigor. Em 2, muda só uma imagem de um anexo. Em 1, publica um preâmbulo. **Nenhuma corrige só o sumário ou a data.** Uma corrige o título e, além disso, o articulado.

Por regra, 3 dos 10 aplicavam-se de forma segura (2, 6 e 9), e o 10 também, com uma regra que aplique todas as ocorrências que o localizador enumera. Os outros pedem o LLM ou uma transcrição de imagem.

A primeira leitura da amostra corrigiu o script num ponto. O teste `ja` passou a vir depois do aproximado, porque no caso 9 o «deve ler-se» está contido no «onde se lê».

### Duas regras da Lei 74/98 que contam aqui

A lei formulário (Lei 74/98) regula as retificações no art. 5.º:

- n.º 4: as retificações «reportam os efeitos à data da entrada em vigor do texto rectificado». Na consolidação, uma retificação aplica-se à versão original, e não como versão nova com a data da declaração.
- n.os 2 e 3: a retificação publicada mais de 60 dias depois do texto é nula. Das 74 retificações por aplicar de diplomas posteriores a novembro de 1998, 15 passam os 60 dias. Entre elas estão as 4 correções de PDM e o Aviso 102/2016 à RAR 19/2008, um tratado, com regime próprio. Isto é uma leitura jurídica, não uma regra para o script.

## 2. Vigência

### Números

As classes saem do título, do sumário, do tipo e da data (ver «Método»). A certeza `alta` quer dizer que o diploma é da classe. **Não quer dizer que tenha deixado de vigorar.**

| Classe | Alta | Incerta | Com prova no próprio registo |
|---|--:|--:|---|
| Concessões de caça (zonas de caça, regime cinegético especial) | **404** | 15 | 7 concessões revogadas por `repealed_by` (mais o DL 227-B/2000, de certeza incerta); ver o prazo abaixo |
| Cursos anteriores a Bolonha (mestrados, licenciaturas, bacharelatos, DESE, antes de 24/3/2006) | **186** | 22 | 2 por `repealed_by` |
| Regimes de um só ano (orçamento, campanha, ano letivo, concurso de um ano) | **79** | 39 | 0 |
| Orgânicas e quadros de serviços | **225** | 64 | 4 por `repealed_by` |
| **Total** | **894** | **140** | |

Fora das quatro classes, mais duas medidas:

- **O DRE já diz que não vigoram (39).** 7 têm `legal_status: repealed` ou `not_in_force`. 32 têm uma relação `repealed_by` de revogação inteira, 14 deles nas classes acima. Lidas as 32, duas são duvidosas: no Despacho 3229/2006 o que se revoga é uma licença, e no DL 283/89 o rótulo dá a revogação por um diploma de 1988. As revogações parciais ou com ressalvas («à excepção do art. 4.º», «em tudo o que o contrarie») não entram.
- **Ultramar (66).** São diplomas anteriores a 1976 sobre províncias ultramarinas, 49 deles fora das quatro classes. Caducaram com a descolonização, mas nenhum ato do acervo o diz.

**O prazo das concessões de caça.** Das 404 de certeza alta, 310 dão no texto um prazo em anos. Para cada uma, o fim estimado é a data do último ato aplicado mais esse prazo:

- **86** têm o prazo acabado e o texto não fala em renovação;
- **224** têm o prazo acabado, mas o texto diz «renovável» ou «renováveis automaticamente». Algumas renovam-se sozinhas por dois períodos, por isso este número **não é prova**;
- **94** não dão prazo («por tempo indeterminado» ou omisso).

### Amostra por classe: prova de que deixou de vigorar

Cinco por classe, ao acaso entre as de certeza alta (`random.seed(5)`). Para cada uma vi as relações do registo e procurei no acervo inteiro (`rg`) o número do diploma ou o número do processo, perto de «revog», «extint», «caduc», «substitu» e «renova».

**Concessões de caça: 0 de 5 com prova de extinção.**

- **Portaria 405/2002** (`pt:dre:291816:por`). 12 anos, «renováveis automaticamente por dois períodos iguais». Tem anexações em 2004 e 2007 (processo 2593). Vigora provavelmente até 2038.
- **Portaria 722-J12/92** (`pt:dre:617685:por`). Foi alterada pela Portaria 167/2000 e é renovável. O prazo acabou em 2012, e não há renovação no acervo. **Dúvida.**
- **Portaria 1051/2007** (`pt:dre:641375:por`). Extingue por caducidade uma zona e concessiona outra (processo 4582-DGRF) por 12 anos, renovável. Provavelmente vigora.
- **Portaria 667-X4/93** (`pt:dre:402302:por`). Foi alterada pela Portaria 752/97. O prazo acabou em 2009, e não há renovação no acervo. **Dúvida.**
- **Portaria 493/2004** (`pt:dre:301806:por`). Zona municipal de Enxerim, em Silves, por 6 anos (processo 3437). A Portaria 393/2010 renova a transferência de gestão por mais 6 anos, até 2016. Depois de 2016 não se sabe. **Dúvida.** (Corrigido a 19/11: a Portaria 393/2010 está na cadeia; a consolidação viu-a e não muda o texto. Ver a secção 5.)

**Cursos anteriores a Bolonha: 0 de 5 com um ato expresso.**

- Portaria 716/2002 (`pt:dre:139763:por`), Portaria 1128/2001 (`pt:dre:611087:por`), Portaria 843/81 (`pt:dre:563797:por`) e Portaria 1191/2000 (`pt:dre:656077:por`): nenhum ato do acervo as revoga.
- Portaria 633/93 (`pt:dre:374176:por`): a Portaria 537/98 revoga só os n.os 4.º a 7.º.

O que há é o regime geral. O DL 74/2006, art. 84.º, n.º 1, al. b), revoga o DL 216/92, o dos mestrados, e o regime transitório dava a adequação dos cursos até 2009-2010. É a mesma dúvida da ronda 114.

**Regimes de um só ano: 4 de 5 são de um só ano pelo próprio texto, e 1 está mal classificado.**

- DN 132/82 (`pt:dre:394546:por`): programa de investimentos do SEE para 1982.
- Portaria 83/92 (`pt:dre:152136:por`): indemnizações compensatórias da campanha de 1992.
- Portaria 1075/2001 (`pt:dre:631071:por`): vagas do ano letivo de 2001-2002.
- Decreto 43340 (`pt:dre:514185:por`): orçamentos do ultramar para 1961. É também do ultramar, e há vários artigos revogados no acervo.
- **Falso positivo:** o DL 323/98 (`pt:dre:229103:por`) executa autorizações do OE para 1998, mas altera o Código do IVA de forma permanente.

**Orgânicas: 4 de 5 com prova no acervo, nenhuma no próprio registo.**

- **DRR 16/2005/M** (`pt:dre:548423:por`). Revogado pelo DRR 14/2008/M, que aprova a nova orgânica da DREER, com exceções transitórias.
- **DL 158/96, Lei Orgânica do Ministério das Finanças** (`pt:dre:241227:por`). Revogado pelo DL 47/2005. A relação está nos registos dos alteradores (DL 107/97, 207/97, 28/98, 21/99 e 315/2001), **não no nosso**.
- **DR 8/93, Direção-Geral da Indústria** (`pt:dre:634493:por`). A DGI foi extinta: o DL 34/2004 cria a Direção-Geral da Empresa «assumindo as atribuições e competências das extintas» DGI e outras.
- **Portaria 312/71** (`pt:dre:643302:por`). Quadros das Inspeções de Crédito e Seguros de Angola e Moçambique (ultramar).
- **DL 47627, Lei Orgânica do LNEC de 1967** (`pt:dre:509792:por`). Há orgânicas novas do LNEC (DL 519-D1/79, 422/99, 304/2007 e 157/2012), mas não encontrei uma revogação expressa. **Substituído, sem ato expresso.**

### O que a amostra diz

- **Orgânicas.** As de certeza alta deixaram quase todas de vigorar (4 de 5 com prova, a quinta substituída). A prova está noutro registo do acervo ou no texto de um diploma posterior, quase nunca nas relações do próprio registo.
- **Regimes de um só ano.** A caducidade lê-se no próprio sumário, mas há falsos positivos: os diplomas que executam o orçamento e alteram códigos.
- **Caça e cursos.** Não há prova expressa no acervo. A caça depende de renovações que estão muitas vezes na 2.ª série ou fora da cadeia. Os cursos dependem do regime geral do DL 74/2006. Ficam em dúvida, como na ronda 114.

## 3. Método

1. **Consolidados.** Contam todos os `data/**/*.versoes.json` com `consolidated_by` a começar por «leis-portugal».
2. **Retificações por aplicar.** São as relações `corrected_by` do front matter cujo `target` não está nos `acts` de nenhuma versão. A retificação procura-se no acervo pelo id, com um índice ficheiro → id feito com `rg -m1 '^id: '` sobre `data/portugal` e `data/regional`: 405.811 registos, cerca de 1 minuto. O `Acervo.index()` usa vários processos, e o sandbox não os deixa criar.
3. **Leitura de cada retificação** (`auditoria.pares`). Encontra os pares «onde se lê «X» deve ler-se «Y»», com as aspas no mesmo parágrafo ou nos seguintes, e tira as reticências das pontas. O script tem o seu próprio leitor porque o `alteracoes.ler` do pipeline não leu nenhuma instrução no formato com as aspas em parágrafos separados («onde se lê:» / «…» / «deve ler-se:» / «…»). Exemplo: a Decl. Ret. 3/2008 ao DR 84-A/2007, que muda um prazo de candidaturas.
4. **Estado de cada par.** Procura-se o «X» no texto em vigor (o corpo do `.md`, sem ligações e com espaços normalizados), primeiro letra a letra e depois sem pontuação nem maiúsculas. Se não estiver, procura-se o «Y» (já aplicado), o localizador (sumário, título, data) e o original publicado (o `texto_original` da verificação às cegas): um «X» que está no original mas não no texto em vigor quer dizer que uma alteração posterior o reescreveu.
5. **O diploma certo.** A retificação tem de mencionar o número do original. Conta só o número, porque o DRE chama «Decreto» a decretos-leis, e o texto pode escrever «10 910/2009».
6. **Vigência.** Expressões regulares sobre o título e o sumário, por esta ordem:
   - caça: uma zona ou concessão com nome ou lugar; as taxas e as regras gerais ficam `incerta`;
   - cursos: o grau ou o curso, mais a instituição de ensino superior, antes de 24/3/2006;
   - um só ano: o ano explícito, depois de tirar as datas por extenso e os números de diplomas, para «Lei n.º 3/2000» não contar como ano;
   - orgânicas: orgânica, quadro de pessoal, estatutos de uma entidade (não os estatutos de carreira, como os dos Deputados ou dos oficiais) ou a criação de um serviço, comissão ou fundo.

   Fica a primeira classe que se aplica. As provas são três:
   - o `legal_status`;
   - o rótulo das relações `repealed_by`: só conta a revogação inteira, e as ressalvas e os alvos parciais excluem-na;
   - nas concessões de caça, o prazo em anos do texto em vigor.
7. **Amostras.** As das retificações e da vigência foram lidas à mão, com as sementes indicadas. O teste cobre o leitor dos pares, as classes das retificações, a menção pelo número, as classes de vigência, a revogação inteira e o prazo.

Limites:

- O estado `ausente` junta casos diferentes: anexos em imagem, trechos com «[...]», diferenças de grafia e alterações que o DRE não registou. Por isso, a classe `llm` é um teto do trabalho, não uma medida de erro.
- As classes de vigência são de título e sumário: «alta» não é «caducado».

## 4. Propostas

Estimativas: tokens pela média do pipeline (cerca de 3.200 de entrada e 2.500 de saída por diploma no LLM da escala, `consolidacao/README.md`). Tempo de relógio numa sessão do Claude com subagentes, como nas rondas 112 a 114.

### Retificações

1. **Fechar a fuga.** No `selecionar.py`, no `llm_completo.py` e na entrada da verificação às cegas, `corrected_by` deve contar como alterador, para as próximas rondas verem as retificações. Pela Lei 74/98, art. 5.º, n.º 4, a retificação aplica-se à **versão original**, e não como versão nova.
   - *Custo:* 0 tokens; cerca de 1 a 2 h de código e testes.
2. **Aplicar por regra as 75** (`por_regra` e `por_regra_aprox`, em 72 diplomas, com 144 pares). **Feito a 19/11:** 67 aplicadas em 65 diplomas e verificadas às cegas; 7 recusadas, que ficam para o LLM (`consolidacao/README.md`, secção 9).
   - **Como:** a regra `retificar` do `aplicar.py` já existe. Basta dar-lhe os pares deste script e o artigo do localizador.
   - **Verificação:** às cegas, só do artigo retificado, com Sonnet. Os 14 aproximados ficam com revisão à mão, por serem diferenças de pontuação.
   - **Custo:** cerca de 72 × 4 mil tokens de entrada e 0,5 mil de saída, ou seja, **0,3 M de entrada e 0,04 M de saída**; 2 a 3 h de código e 1 h de verificação.
3. **LLM para as 116** (`llm` e `sem_pares`, em 110 diplomas).
   - **Como:** respondedor Opus com a retificação e só os artigos que o localizador nomeia. A mediana do diploma inteiro é de 25 KB, e a retificação tem cerca de 5 KB.
   - **Verificação:** às cegas, com Sonnet.
   - **Custo:**
     - resposta: 116 × cerca de 4,5 mil tokens de entrada e 2 mil de saída, ou seja, 0,5 M de entrada e 0,23 M de saída;
     - verificação: 0,4 M de entrada e 0,06 M de saída;
     - total: **cerca de 0,9 M de entrada e 0,3 M de saída**; 3 lotes, 2 a 3 h de relógio.
   - Os quadros em imagem (`sem_aspas` com «ver documento original») não se resolvem assim: ficam com o pipeline dos anexos em imagem.
4. **Sem trabalho no texto (36).** São as classes `substituida`, `ja_no_texto`, `so_metadados` e `outro_diploma`. Basta anotar o motivo. Os 3 `outro_diploma` são erros do DRE para a lista de correções a comunicar. As 6 `sem_registo` são sobretudo correções de PDM da 2.ª série e ficam como estão.
5. **Depois.** Export e reconstrução do índice, a cargo da sessão coordenadora. Medir o texto alterado antes e depois.

Se só se fizer o passo 2, corrigem-se cerca de 70 diplomas por menos de 0,4 M tokens. Com o passo 3, chega-se aos 185 diplomas com trabalho.

### Vigência

1. **Não tirar consolidações por vigência.** Tirar um diploma do `data/` por já não vigorar, como se fez no bloco 3, deixa no `data/` o texto original, que diz o mesmo `in_force`. Perde-se o texto certo e o problema fica.
   - **O que fazer:** marcar a vigência num campo à parte, por exemplo uma lista `consolidacao/auditoria/vigencia-revista.jsonl` ou uma nota no registo, que o RAG leia para avisar ou baixar a posição.
   - **Decisão do João:** esta é uma decisão de política, antes de qualquer custo. Os 12 do bloco 3 podem voltar a entrar com a marca.
2. **Primeiro passo, por regra (0 tokens, 3 a 4 h de código e cerca de 5 min de corrida).**
   - **Já com prova:** marcar os 39 que o DRE já dá como revogados e os 66 do ultramar.
   - **Caça:**
     - procurar no acervo as renovações e extinções pelo número de processo, numa só passagem de `rg` (cerca de 2 min);
     - recalcular o fim estimado;
     - marcar «prazo acabado sem renovação no acervo»: hoje 86, sem contar os renováveis;
     - as renovações encontradas que não estão na cadeia, como a Portaria 393/2010, vão para a lista de alteradores em falta.
   - **Orgânicas:** procurar no acervo as revogações do diploma registadas noutros registos, como a do DL 158/96 no DL 107/97 e seguintes. Esta procura pode ir também para o índice de relações inversas.
3. **Segunda leitura de vigência com o LLM**, só para o que o passo 2 não resolve.
   - **Quantos:** cerca de 700 de certeza alta, a saber: orgânicas (225), cursos (186), regimes de um ano (79, para tirar os falsos positivos como o DL 323/98) e a caça renovável e sem prazo (cerca de 300).
   - **Entrada:** título, sumário, relações, primeiro e último artigos e as menções no acervo com verbo de revogação.
   - **Modelo:** Sonnet, com Opus só nas dúvidas (cerca de 15%).
   - **Custo:**
     - Sonnet: 700 × cerca de 4 mil tokens de entrada e 0,3 mil de saída, ou seja, **2,8 M de entrada e 0,2 M de saída**;
     - Opus: cerca de 0,5 M de entrada e 0,1 M de saída;
     - tempo: 18 lotes de 40, 3 a 4 h de relógio com subagentes em paralelo.
   - Os 140 de certeza incerta ficam de fora até se ver o rendimento nos 700.
4. **Cursos anteriores a Bolonha.** Decidir por regra jurídica, não diploma a diploma, porque o acervo não tem os atos de adequação, que são da 2.ª série. Proposta: marcar os 186 como «regime anterior ao DL 74/2006», sem afirmar que caducaram.

## 5. Feito a 19/11/2026

O João aprovou as três propostas da secção 4.

**Retificações** (`consolidacao/README.md`, secção 9). Das 243 retificações distintas:

| Estado | Retificações |
|---|--:|
| Aplicadas por regra | 67 |
| Aplicadas com o LLM (Opus a responder, Sonnet às cegas) | 99 |
| Nada a aplicar (LLM), com o motivo | 41 |
| Sem trabalho | 36 |
| **Por ver** | **0** |

As 166 aplicadas estão em 156 diplomas. As 11 em imagem ou republicação e as 6 sem registo (recolhidas do DRE) fecharam a 19/11, à noite, nas rondas im e rc. Das 11, aplicaram-se 6, e as outras 5 tinham sido reescritas depois. Também fecharam as 4 trocas por aplicar (r4) e as 18 instruções em «dúvida» (r5 e r6). Na r4, o art. 8.º do DL 376/87 entrou, porque a decisão da r2 de o tirar estava errada: o DL 364/93 só o renumerou. Apareceu um problema novo, o da nota e da etiqueta fora do articulado, corrigido em 14 registos. Os pormenores estão no README, secção 9, passo 6. Das 85 com o LLM, 7 só passaram numa 2.ª ou 3.ª ronda, refeitas com o reparo do verificador, e 4 trocas dessas ficaram por aplicar, com o motivo. Nas próximas rondas, `corrected_by` conta como alterador (seleção, leitor, verificação às cegas, pedido ao LLM e data da versão).

**Vigência** (`consolidacao/README.md`, secção 10).

- Não se tiram consolidações por vigência. A marca fica em `consolidacao/auditoria/vigencia-revista.jsonl`, e o RAG dá o aviso. A penalização na posição fica desligada (`RAG_VIGENCIA_PRIOR`).
- Os 12 do bloco 3 voltaram a entrar no `data/`.

| Classe | Marca | Diplomas |
|---|---|--:|
| Bloco 3 | nao_vigora | 12 |
| Revogados pelo próprio DRE | nao_vigora | 37 |
| Revogação registada noutro registo | nao_vigora | 2 |
| Ultramar | nao_vigora | 51 |
| Caça com o prazo acabado e sem renovação no acervo | nao_vigora | 27 |
| Segunda leitura: caça | nao_vigora | 18 |
| Segunda leitura: orgânicas | nao_vigora | 8 |
| Cursos anteriores ao DL 74/2006 | regime_anterior | 184 |
| **Total** | | **339** (155 nao_vigora) |

**Rendimento da segunda leitura.** Dos 658 candidatos (caça 370, orgânicas 210, um só ano 78):

- o Sonnet resolveu 38: 37 «nao_vigora» e 1 «vigora»;
- o Opus, nas 620 dúvidas, resolveu 25: 4 «nao_vigora» e 21 «vigora», 20 deles em orgânicas;
- ficam 595 dúvidas;
- das 41 «nao_vigora», passaram o critério de prova 26: 24 do Sonnet e 2 do Opus.

Por classe, as marcas foram 18 de 370 na caça, 8 de 210 nas orgânicas e 0 de 78 nos regimes de um só ano.

**As renovações de caça «fora da cadeia» (66 linhas, 40 pares).** Não havia nada a aplicar. 38 pares já estavam na cadeia: a consolidação viu-os (seleção e `alteradores_vistos` do LLM) e não mudam o texto, porque uma renovação renova a concessão sem reescrever a portaria. Os outros 2 eram números de processo trocados (um acórdão do STJ e uma gralha no sumário da Portaria 449/2004). A regra foi corrigida (`vigencia.na_cadeia()`), e `alteradores-em-falta.jsonl` fica vazio. As marcas não mudam (339).

**Problema novo, fechado: anexos e plantas de alteradores (README, secção 11).**
- **Anexos.** Alteradores triados «sem alteração textual» mudavam anexos, mapas ou quadros, e o consolidado ficava com os do original (206 pares em 89 consolidados). Aplicaram-se 113 em 45 consolidados, com resposta Opus e verificação às cegas Sonnet. Os outros 93 ficaram com o motivo: outro diploma, reescrito depois, já aplicada, ou não passaram às cegas.
- **Plantas.** Em 179 zonas de caça, o n.º 1.º reescrito remete para a planta do alterador, mas a imagem era a do original. Trocaram-se 174, todas verificadas às cegas.

**Fecho da vigência (19/11, à noite).** Os 135 incertos tiveram uma leitura com Sonnet. Cada um dos 793 candidatos acaba com marca ou com «revista, sem marca» e o motivo (`consolidacao/auditoria/vigencia-fecho.jsonl`):
- 37 `nao_vigora` com prova (26 de antes, mais 11 dos incertos);
- 10 `regime_anterior` em cursos incertos;
- 57 `por_confirmar`, uma marca branda que não afirma que caducou: 46 regimes de um só ano que já passou e 11 concessões de caça com o prazo acabado e sem renovação nas menções;
- 689 revistas, sem marca.

O total de marcas passa de 339 para 417. O README, secção 10, tem a tabela por classe.

O rendimento baixo, sobretudo do Opus nas dúvidas (2 marcas em 620), vem de a prova de que a maior parte deixou de vigorar não estar no acervo: as renovações e as extinções da 2.ª série, e os regimes que caducam sem ato expresso. Não se fizeram mais rondas.

## Ficheiros

- `consolidacao/auditoria.py`: o script.
- `consolidacao/auditoria/resumo.json`, `retificacoes.jsonl` e `vigencia.jsonl`: os resultados de 19/11/2026. Correr de novo:

  ```bash
  rg -m1 --no-heading -g '*.md' '^id: ' data/portugal data/regional > ids.txt
  python consolidacao/auditoria.py --indice ids.txt
  ```

- `tests/test_auditoria_consolidados.py`: o teste mínimo.
