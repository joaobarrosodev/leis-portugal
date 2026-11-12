# Consolidação: texto em vigor dos diplomas alterados

Piloto da fase 2 do [plano para um RAG jurídico fiável](../PLANO-RAG.md): obter o texto em vigor dos diplomas que o DRE dá como alterados mas não consolida, aplicando as alterações publicadas. Só `acervo.py` altera `data/`, e só com os consolidados verificados às cegas (ver "Aplicação ao acervo").

## O que falha e porquê (estado em 11/11/2026)

Resumo de todas as rondas, para quem retomar este trabalho sem o histórico das sessões que o fizeram. **2.514 diplomas** têm o texto em vigor em `data/`. As secções por bloco, mais abaixo, têm o pormenor de cada ronda; as rondas de algumas sessões foram renumeradas ao juntar ao `main` (a correspondência está em cada título de secção).

### 1. Verificados às cegas com reparos: 779 diplomas

Na última ronda em que cada diploma esteve, 2.285 ficaram com tudo `certo` e 779 não. Causas, contadas por palavras-chave nos motivos do verificador (`verificacao/saida-piloto-*.jsonl`; um diploma pode ter mais de uma, por isso a soma passa de 779):

| Causa | Diplomas | Resolúvel? |
|---|--:|---|
| Anexo, quadro, mapa ou planta só em imagem ou PDF | 447 | Não por texto: o conteúdo não está no acervo |
| Erro de texto do LLM (palavra, número, alínea) | 252 | Em parte: repedir só o artigo errado ao mesmo modelo resolveu alguns |
| Títulos de divisão e epígrafes (secção, capítulo) | 74 | Em grande parte: o formato com títulos (rondas 40–43 e 60–61) já os trata |
| Artigos a mais ou a menos | 39 | Caso a caso |
| Instrução ambígua ("[Anterior alínea b)]") | 36 | Caso a caso, com leitura jurídica |
| Fórmulas finais e assinaturas fora do sítio | 32 | Corrigido em `_recolocar_assinaturas`; falta repedir os antigos |
| Revogação condicional ou adiada | 15 | Não se aplica ao texto, por regra: ficam de fora de propósito |
| Chaves repetidas (decreto e estatuto anexo com o mesmo n.º de artigo) | 14 | Corrigido (`N.º#2`); falta repedir os antigos, como o DL 321-B/90 |
| Republicação cortada pelo limite de 60 mil caracteres | 5 | Partir da última republicação em vez do original |

A contagem é aproximada (classificação por palavras-chave, não por leitura).

### 2. Certos às cegas mas recusados pelo `acervo.py`: 11 diplomas, resolvidos a 11/11/2026

Os 11 passaram a verificação às cegas, mas o `acervo.py` recusava-os por duas razões técnicas. As duas foram corrigidas, e **10 estão agora em `data/`**: o total passa a **2.282 diplomas**.

- **6 em que o histórico não reproduzia o consolidado** (`pt:dre:372655`, `605310`, `226426`, `239822`, `541645` e `640122`, todos de texto corrido). A única diferença era uma linha em branco a mais num ponto do texto. Agora a comparação reduz todas as sequências de linhas em branco nos dois lados, e nada mais. Os 6 entraram.
- **5 com uma consolidação nossa anterior em `data/`**: DL 236/85 (`183049`), DL 350/88 (`355570`), Decreto 44240 (`516702`), DL 511/99 (`643086`) e DRR 17/2001/M (`348524`). Foram refeitos e passaram de novo às cegas. Agora o `acervo.py` substitui uma consolidação do leis-portugal quando a versão 1 do histórico (`*.versoes.json`) é, bloco a bloco, o original verificado; o histórico novo parte desse original. Antes de aplicar comparou-se cada refeita com a anterior:
  - **4 entraram**, porque corrigem a anterior: o DL 511/99 e o DRR 17/2001/M têm as assinaturas no sítio certo, antes do estatuto anexo; o Decreto 44240 junta um § 3.º que estava partido ao meio; o DL 350/88 tem "Revogado" em vez de "Alterado" na nota de um artigo revogado.
  - **O DL 236/85 fica com a anterior** (`NAO_SUBSTITUIR` no `acervo.py`). A refeita também corrige uma nota "Alterado" para "Revogado", mas tira os parênteses de todas as epígrafes do original ("ARTIGO 1.º — (Conceito)" passa a "Conceito"). A verificação às cegas não apanhou isto. Mantém-se a anterior, mais fiel ao original.

### 3. Por pedir: grandes demais para o método atual

Os 18 desta lista foram feitos em 11/11/2026, na ronda 70, com `llm_gigantes.py`. Ver "Os 18 grandes demais (ronda 70)", no fim. Ficaram assim: 5 aplicáveis, 8 verificados com reparos, 3 sem nada a aplicar e 2 que não se pedem, porque o DRE já os consolida noutro registo. O DL 38/2003 é um dos 5 aplicáveis; foi feito por unidades de texto e não precisa da correção do parser, que ficou fora do `main` (ver "DL 38/2003: o parser").

- **18 leis de orçamento** dos 93 grandes: deixadas de fora por decisão (pouco valor para o RAG; quase todos os alteradores visam os códigos fiscais e não o próprio texto). Lista em "Bloco 3 dos 93 grandes".

### 4. Nunca chegam à verificação

Em todas as filas, uma fatia grande das respostas do LLM é "sem alterações" ao texto: alteradores que só trocam anexos em imagem, revogam o diploma por inteiro, prorrogam prazos ou mudam nomes de entidades. Não são falhas do método; são diplomas cujo texto, por escrito, não muda. Ficam como informação para a vigência.

### 5. Alteradores que não estavam no acervo: ronda 80 (11/11/2026)

Na escala, 867 diplomas ficavam "sem texto do alterador": um dos alteradores não estava no acervo (1.088 diplomas diferentes, quase todos da 2.ª série: avisos, portarias e despachos) ou só tinha metadados. Recolheram-se 998 dos 1.088: 164 pelo id nos sitemaps do DRE e 834 pela nota do DRE (tipo, número e ano), confirmados no próprio DRE; 912 com texto e 86 só com metadados. Ficaram por recolher 62 cuja nota não dá um número utilizável (avisos de 1961 a 1975, "AV.DD…") e 28 só com número, sem id do DRE.

A triagem refeita mudou só os 631 diplomas com um alterador novo: **412 sem alteração ao texto** (o original já é o texto em vigor), 84 para o LLM, 4 aplicados por regra, 3 revogados por inteiro e 126 ainda sem texto do alterador. Nenhum outro diploma mudou de estado.

Os 88 com instruções seguiram o fluxo normal: 50 em 17 pedidos completos (`llm_completo.py`) e 34 em 9 de texto corrido (`llm_corrido.py`), 26 subagentes Opus; a verificação letra a letra juntou 57. **6 saíram à mão** (estado `não junto` em `llm/juntados-completo.jsonl`, com o motivo): 5 que o LLM devolveu com todos os artigos "(Revogado.)" por um alterador que revoga o diploma inteiro (RCM 85/95, 92/94, 136/95 e 144/95, Portaria 780/99), que são "revogado por inteiro" e não uma consolidação, e a RCM 116/94, com uma revogação que só produz efeito quando o plano de pormenor entrar em vigor. Ronda 80 (`verificacao/entrada-piloto-80-lote-01..02.jsonl`, 25 vistas, verificadores Sonnet às cegas): 55 diplomas, **35 sem reparos**, que estão agora em `data/`. Os 20 com reparos são sobretudo anexos e quadros só em imagem, cabeçalhos de secção em falta e um artigo substituído que ficou duplicado (Despacho 2037/2026).

**Correção no `acervo.py`:** um diploma da escala que também estava no piloto (Despacho 1941-A/2014) usava a seleção do piloto, em que o alterador ainda não estava no acervo. Agora um juntado da escala usa a seleção da escala (`_selecao_de`).

### 6. Repedir os reparos de texto: ronda 81 (12/11/2026)

Dos 807 diplomas cuja última ronda às cegas teve reparos, 487 falham por anexos, quadros, mapas ou imagens (não se resolvem com texto). Dos outros, 138 tinham só artigos `errado` ou `dúvida` e 161 uma instrução de texto em falta. Repediram-se os 100 mais citados (60 de pedido completo e 40 de texto corrido) com o mesmo método e a indicação de que já tinham falhado; ficaram de fora 6 pedidos acima de 450 mil caracteres (18 diplomas, entre eles o DL 227-B/2000). 24 subagentes Opus; a verificação letra a letra juntou 99.

**Só 17 deram um texto diferente do que já tinha falhado** (`cegas.py` só põe numa ronda nova o consolidado que mudou): nos outros 82 o pedido novo reproduziu exatamente o mesmo resultado. Ronda 81 (`verificacao/entrada-piloto-81-lote-01.jsonl`, 9 vistas, verificadores Sonnet às cegas): **6 sem reparos**, aplicados (DL 439/73, Lei 16/98, Portarias 453/78, 640-Z/94 e 994/95, DRR 3/86/A). Os 11 com reparos repetem os padrões de antes: substituições terminológicas gerais não aplicadas, alíneas "[Actual alínea …]" por renumerar, valores inventados numa tabela, e republicações com erros que o consolidado copia (DL 55-A/2000).

Conclusão: repedir com o mesmo método rende pouco (6 em 100). Para estes diplomas é preciso outra abordagem: repedir só os artigos `errado`, com o motivo do verificador, ou uma revisão humana.

**Cuidado ao correr `juntar`:** o `llm_completo.py juntar` e o `llm_corrido.py juntar` reescrevem as entradas de todos os diplomas a partir das respostas guardadas. Isto desfez as 6 exclusões manuais da ronda 80 (revogados por inteiro e revogação adiada) e tirou o campo `passagens` aos 18 grandes; essas entradas e dois consolidados dos 18 (DL 202/2000 e DL 63-A/2013) foram repostos como estavam. **Corrigido a 12/11/2026:** as exclusões feitas à mão ficam em `llm/exclusoes.json` (id → motivo) e os dois `juntar` respeitam-nas; o `juntar` do texto corrido deixa como estão as entradas dos 18 grandes (`llm/gigantes-ids.txt`), que são do `llm_gigantes.py`. Correr `juntar` duas vezes já não muda nada.

### 7. Repedir com os reparos do verificador: ronda 82 (12/11/2026)

`reparos.py` repede os diplomas do pedido completo que falharam a verificação às cegas, agora com o que o verificador apontou, logo a seguir ao início de cada diploma: os artigos `errado` ou `dúvida`, com o motivo e o texto esperado, e as instruções que não se viram aplicadas. Ficam de fora os reparos sobre anexos, quadros, mapas ou imagens, e os pedidos acima de 450 mil caracteres. O verificador da ronda nova não vê os reparos.

Foram 160 diplomas em 45 pedidos, respondidos por subagentes Opus. A verificação letra a letra juntou 150. **54 deram um texto diferente do que tinha falhado** (na ronda 81, sem os reparos, tinham sido 17 em 99). Na ronda 82 (`verificacao/entrada-piloto-82-lote-01..02.jsonl`, 21 vistas, verificadores Sonnet às cegas), dos 2.806 artigos 2.786 estão `certo`, 9 `errado` e 11 `dúvida`. **33 diplomas não têm reparos e 32 foram aplicados.** O que fica de fora é a Portaria 705-A/2000, que a Portaria 349/2007 revoga quase toda. Os 21 com reparos repetem padrões já vistos: texto antigo duplicado a seguir à nova redação, fecho com as assinaturas duplicado, marcadores "[Actual alínea …]" por substituir, substituições terminológicas por fazer e epígrafes em falta.

Conclusão: com os reparos, o rendimento sobe de 6 em 100 (ronda 81) para 32 em 160. Os outros 96 juntados reproduziram o texto que já tinha falhado.

**Ronda 83: os pedidos grandes demais.** Na ronda 82 ficaram de fora 9 pedidos acima de 450 mil caracteres, com 27 diplomas (3 por pedido). `reparos.py --ids FICHEIRO --por-ficheiro 1` repediu-os um por pedido. Ficaram dentro do limite 24; os 3 que ainda passam (até 965 mil caracteres) ficam para `llm_gigantes.py`. A verificação letra a letra aceitou as 24 respostas, mas só 5 deram um texto diferente: em vários diplomas o respondedor confirmou no alterador que o reparo do verificador não procedia e manteve o texto. Três concessões de autoestrada só têm, no texto atual, os títulos dos capítulos e não as bases, e as alterações às bases ficaram por aplicar. Às cegas (`verificacao/entrada-piloto-83-lote-01.jsonl`, 5 vistas), 2 ficaram sem reparos e foram aplicados: o DL 47627 e a Resolução da ALRAM 5/2012/M. Os 3 com reparos são o Regulamento 52-A/2005 (texto mudado onde a instrução diz "..."), o DL 315/91 (bases inseridas fora do sítio) e o DL 621-A/74 (artigo 39.º).

**Ronda 84: os 3 que nem sozinhos cabem.** Foram pelo `llm_gigantes.py`, por passagens, como os 18 grandes da ronda 70. Juntaram-se ao `llm/gigantes-ids.txt`.

- **Lei 30-G/2000:** 51 alteradores em 6 passagens. Só 3 dos alteradores mudam o texto da lei; os outros alteram os códigos fiscais que ela também alterou. Ficaram 6 trechos, todos `certo` às cegas, e foi aplicada.
- **DLR 19/2007/A:** 12 alteradores em 3 passagens. A passagem 1 copia a republicação do DLR 26/2011/A. Às cegas teve 54 trechos, todos `certo`, e também foi aplicado.
- **DL 44329 (Código das Custas Judiciais):** respondido em 3 passagens, mas não se aplica. O DL 224-A/96 revoga-o todo, menos o artigo 221.º. Ficou em `llm/exclusoes.json`.

**Um erro apanhado e corrigido.** O `llm_completo.py juntar` e o `llm_gigantes.py juntar` escrevem o consolidado no mesmo ficheiro de `piloto/`. Correr o primeiro depois do segundo repunha o texto do pedido completo. A primeira verificação às cegas da última passagem viu esse texto e deu 48 trechos `errado` (apagamentos e mudanças sem instrução).

O `juntar` do pedido completo passa agora a deixar como "não junto" os diplomas do `llm/gigantes-ids.txt`. Só três diplomas tinham resposta nos dois pedidos, estes três, por isso o erro não tocou em mais nenhum. As duas vistas refizeram-se e voltaram a ser verificadas, e as duas deram tudo `certo`.

### Triagem: alterações que as regras não leem (12/11/2026)

A leitura das instruções (`alteracoes.ler`) só vê uma instrução dirigida ao original pelo número. Escapam três coisas:
- quando o alterador o nomeia no preâmbulo e depois só fala da "referida portaria";
- quando a fórmula não é a habitual: "o quadro de pessoal …, aprovado pela Portaria n.º X, seja alterado de acordo com o quadro anexo", "Seja considerada revogada … a Portaria n.º X", "Na lista anexa ao Decreto-Lei n.º X são introduzidas as seguintes alterações";
- quando o original vem no meio de uma lista.

**Medição às cegas.** Um verificador Sonnet leu 80 pares original–alterador dados como "sem alteração textual", tirados ao acaso com 22 a 25 por motivo (9 no último). Viu o texto inteiro do alterador e não soube o que a triagem dissera (`verificacao/triagem-sem-alteracao-amostra-80.jsonl`).

| Motivo da triagem | Altera o texto | Dúvida | Não altera |
| --- | --: | --: | --: |
| O alterador cita o original mas não lhe dá instruções | 8 | 4 | 12 |
| O original só aparece numa lista ou remissão | 2 | 2 | 21 |
| O alterador não menciona o original | 0 | 3 | 19 |
| O original só aparece como diploma que deu a redação de outro | 1 | 2 | 6 |
| **Total** | **11** | **11** | **58** |

**A correção** é `alteracao_provavel` em `consolidar.py`, com testes em `tests/test_triagem.py`. Procura um verbo de alteração ("seja alterado", "é revogado", "passa a ter a seguinte redacção", "são introduzidas as seguintes alterações", "primeira alteração ao") cujo alvo é o original. O alvo é a citação mais próxima, até 350 caracteres antes ou 150 depois. Não contam como alvo o próprio alterador, os diplomas habilitantes ("ao abrigo do …") nem os que só aparecem como alteradores de outro ("alterado pelas Portarias n.os …"). Sem citação perto, conta o primeiro diploma citado.

A anexação de prédios a uma zona de caça fica de fora. Muda a área, mas não as palavras do original: numa segunda amostra às cegas, 16 de 24 não tinham nenhuma alteração de texto e 8 ficaram em dúvida. São 1.068 pares que continuam "sem alteração textual", e é uma limitação conhecida: a área que o original indica pode estar desatualizada.

**Precisão e cobertura:**
- Nos 80 ao acaso, assinala 7: 6 alteram o texto e 1 está em dúvida.
- Numa segunda amostra de 40 assinalados, já sem as zonas de caça, 13 de 16 alteram o texto.
- No total, 19 de 23 (83%).
- A cobertura é parcial: nos 80, apanha 6 dos 11. Escapam os Estatutos da Universidade de Coimbra, que não citam o número do despacho, uma "passe a englobar" sem número por perto e duas mudanças discutíveis.

**Aplicação.** `python consolidacao/consolidar.py --provaveis` passa a "para LLM" os diplomas "sem alteração textual" com uma alteração provável. Muda o `resultados-escala.jsonl` e as partes, para um `--juntar` não a desfazer. Cada um fica com `falhou_em` na leitura e o excerto em `pendentes`. Mudaram 1.896 pares em 1.325 diplomas: "sem alteração textual" passa de 19.330 para 18.005 e "para LLM" de 4.446 para 5.771.

Os outros estados não mudam. Os aplicados já passaram a verificação às cegas, que vê todos os alteradores. As corridas novas de `consolidar.py --escala` aplicam a mesma regra na triagem.

Não contam como alvo os diplomas que só aparecem como os que deram a redação de outro ("o DL 296-A/98, com a redacção conferida pelo DL 76/2004"). Este caso juntou-se depois da ronda 85: nos mais citados, era a causa da maior parte dos falsos alarmes.

Há outra correção ao `processar`: um par assinalado passa a "para LLM", mas os alteradores seguintes continuam a aplicar-se por regra. Antes contava como falha e as regras paravam. No DL 16/94, isso tirava o artigo 56.º-A, aditado pelo DL 94/99, que o pedido ao LLM dava como já aplicado. A ronda 85 apanhou-o com "instruções em falta".

**Ronda 85: os 120 mais citados dos assinalados.** Pediram-se ao LLM os 120 mais citados dos 1.335 da primeira reclassificação, em 49 pedidos completos e 71 de texto corrido. Ficaram 2 pedidos acima de 450 mil caracteres, e 10 lotes do corrido não se pediram: os anteriores eram quase só quadros de pessoal em imagem. Responderam 93 diplomas.

Só 11 tinham uma alteração de texto que se aplica. O resto:
- o alterador muda outro diploma, quase sempre aquele a que o original deu a redação;
- os quadros ou mapas alterados só vêm em imagem;
- prorrogações e mudanças de designação, sem nova redação;
- alteradores sem texto no acervo.

Às cegas (`verificacao/entrada-piloto-85-lote-01.jsonl`), 7 ficaram sem reparos e foram aplicados: a Lei 46/85, os DL 166/92, 188/88, 247/79, 316/2007, 328/88 e 502/76.

O DL 283/89 e o DL 16/94 saíram da ronda 85. O consolidado deles mudou com a correção ao `processar`, e o texto em `data/` é o que já tinha passado a verificação às cegas antes. Ficaram de fora outros dois: o Despacho Normativo 5-A/2013, com uma instrução em falta, e a RCM 25/99, com 1 artigo errado e 2 em dúvida.

Conclusão: nos mais citados, o detetor assinala sobretudo diplomas que deram a redação de outro, e a precisão real nos pedidos foi de 11 em 93. Nas amostras ao acaso tinha sido muito melhor (19 de 23).

**Triagem barata às cegas e ronda 86.** Pedir os 1.239 que sobravam ao Opus seria pagar sobretudo respostas vazias: na ronda 85 foram 11 em 93. Antes disso fez-se uma triagem às cegas mais barata.

- **O que vê o verificador.** Um verificador Sonnet lê, para cada par, uma janela de ~1.500 caracteres do alterador à volta do verbo que `alteracao_provavel` encontrou (com `largura=(750, 750)`) e o início do original. Responde "sim", "outro", "imagem", "não" ou "dúvida" (`verificacao/triagem-provaveis.jsonl`).
- **Calibração antes de usar,** em 314 pares com resposta conhecida:
  - nos diplomas da ronda 85, apanhou os 9 com alteração aplicável e cortou 63 dos 77 sem nada (82%);
  - nas amostras com o alterador lido inteiro, apanhou todos os "sim" de texto menos um discutível (o DL 44190);
  - os restantes "sim" das amostras são quadros de pessoal alterados "de acordo com o quadro anexo", que a triagem dá, bem, como "imagem".
- **Resultado nos 1.601 pares:** 670 imagem, 616 sim, 169 outro, 93 não e 53 dúvida.
- **Aplicação.** `consolidar.py --confirmados FICHEIRO` passa a "sem alteração textual" os diplomas só com "não" ou "outro", e ao estado novo **"alteração só em imagem"** os que têm "imagem" e nenhum "sim" ou "dúvida". Este estado só se resolve com OCR dos quadros.
- **O mesmo para as respostas do LLM.** `--confirmados llm` faz o mesmo com as respostas da ronda 85 que não tinham nada a aplicar. Volta a "sem alteração" só quem tem o `nao_aplicavel` vazio; um `nao_aplicavel` sobre imagem ou anexo sem texto passa a "só em imagem"; qualquer outro fica para o LLM.
- **Contagem por estado:**

| Estado | Antes | Depois |
| --- | --: | --: |
| Sem alteração textual | 18.005 | 18.263 |
| Alteração só em imagem | — | 449 |
| Para LLM, por alteração provável | — | 618 |

Destes 618, 592 ainda não foram pedidos.

**Ronda 86** (`verificacao/entrada-piloto-86-lote-01.jsonl`):
- os 40 mais citados dos 592, em 37 pedidos; 3 ficaram de fora por serem grandes demais;
- 18 com texto juntado;
- às cegas, **14 sem reparos e aplicados**: um em cada 2,6 pedidos, contra 11 em 93 na ronda 85 sem a triagem barata;
- os 4 com reparos:
  - a Portaria 46-A/2001: um anexo com a ligação antiga e artigos que dependem de portarias que não vêm no pedido;
  - o Decreto Regulamentar 8/83: o quadro de pessoal e as referências ao Ministro da Qualidade de Vida;
  - a RCM 8/94: um subtítulo repetido;
  - a Portaria 18022: a tabela anexa da Portaria 19785 só em imagem.

**Rondas seguintes**, com o mesmo método e os 40 mais citados dos que faltam em cada uma. Os pedidos acima de 450 mil caracteres ficam numa lista à parte, para o `llm_gigantes.py`.

| Ronda | Pedidos | Juntados | Aplicados (sem reparos às cegas) | Por pedir depois |
| --- | --: | --: | --: | --: |
| 86 | 37 | 18 | 14 | 555 |
| 87 | 36 | 24 | 16 | 515 |
| 88 | 39 | 27 | 16 | 474 |
| 89 | 40 | 30 | 26 | 434 |
| 90 | 40 | 34 | 28 | 394 |
| 91 | 40 | 23 | 19 | 355 |
| 92 | 40 | 32 | 23 | 315 |

Na ronda 87, a Portaria 680/71 foi para `llm/exclusoes.json`, porque está revogada por inteiro pela Portaria 654/74. Dois diplomas da vista 001 ficaram sem resposta do verificador e não entram.

Na ronda 88 foram para `llm/exclusoes.json` seis diplomas revogados por inteiro: as Portarias 486/94 (pela Portaria 248/98), 1080/82 (pelo DL 190/2001), 497/96 e 317/96, o Despacho Normativo 23/2000 e o Decreto Regulamentar 61/91. Dos 23 juntados que sobram, 7 têm todos os artigos `certo` mas não se aplicam, porque o verificador deixou uma nota no diploma. Por exemplo:
- a Portaria 733/89 não tem os títulos das secções V e VI aditadas (aditar títulos continua por exprimir);
- noutros, um quadro ou um mapa só em imagem;
- ou um alargamento de composição sem texto novo.

Na ronda 89 foram para as exclusões outros quatro revogados por inteiro: as Portarias 774/78, 533-D/2000 e 142/80 e o Despacho Normativo 28/2003. Na Convenção sobre metais preciosos (Decreto 56/82), as alterações entram nos textos inglês e português, os únicos que os decretos de alteração publicam; o texto francês fica como estava.

Na ronda 90 foram para as exclusões a Portaria 181/81, revogada por inteiro pela Portaria 44/84, e o Despacho Normativo 18-B/2009 (Estatutos da Universidade do Porto). Neste, as alterações de 2025 seguem a numeração da republicação de 2015, que não está no texto, e aplicá-las sozinhas daria um texto que nunca esteve em vigor.

Na ronda 91 foram para as exclusões:
- o DL 653/74, revogado por inteiro pelo DL 201/75;
- o PDM de Moura (RCM 15/96), porque o Aviso 13157/2019 remete para números e alíneas que o texto não tem;
- o regulamento do Fundo de Apoio à Inovação (Despacho 32276-A/2008), porque o Despacho 5727/2013 o substitui com nova divisão em capítulos, e aditar e mover títulos ainda não se exprime.

Um verificador deu `certo` aos 18 artigos da Portaria 317/2003 com motivos genéricos. A vista foi verificada de novo, com a instrução de citar a instrução confirmada em cada artigo, e o resultado manteve-se. Desde a ronda 92, todos os verificadores recebem essa instrução.

Na ronda 92 foram para as exclusões:
- o PDM de Oeiras (RCM 15/94), porque o Aviso 10445/2015, provável revisão do PDM, vem sem texto;
- a Portaria 704/2001, revogada por inteiro;
- o Despacho Normativo 25/2002, porque o alterador só vem em extrato e a correspondência entre os blocos e os artigos seria adivinhada.

**O que isto quer dizer para o RAG.** O aviso "Texto original; alterado por…" mantém-se em todos os diplomas alterados sem versão consolidada, mesmo nos "sem alteração textual". Tirá-lo nesses casos faria o sistema responder com texto desatualizado em cerca de 14% a 28% deles (`rag/README.md`).

## Resultado em resumo

Dos 671 diplomas do alvo, só 123 têm, no diploma que os altera, instruções de alteração dirigidas a eles. Em 500 a relação `amended_by` do DRE não corresponde a nenhuma alteração ao texto. As regras aplicaram 27 diplomas por inteiro, e todos passaram a verificação automática. Na verificação às cegas, 24 têm todos os artigos `certo` e 3 tinham uma dúvida; uma resolveu-se, e **25 estão no acervo** desde 2026-10-27. 72 ficaram para o LLM, 5 falharam a verificação e 17 foram revogados por inteiro, embora o DRE os dê como em vigor. Uma sessão do Claude (Opus 5.5) respondeu aos 77 pendentes. 46 respostas passaram a verificação letra a letra e 26 juntaram-se ao original. Na verificação às cegas, **20 dos 26 têm tudo `certo`** e também estão no acervo: são **45 no total** (ver "Pendentes numa sessão do Claude"). A triagem e as regras correram depois nos 25.498 em vigor alterados sem consolidação: ver "Escala".

| Estado | 1.ª corrida | Com o parser da fase 3 | Depois da verificação às cegas | O que quer dizer |
| --- | --: | --: | --: | --- |
| Aplicado por regra | 22 | 28 | 27 | Todas as instruções aplicadas e a verificação automática passou. Vão à verificação às cegas. |
| Para o LLM | 84 | 73 | 72 | Há instruções que as regras não aplicam com segurança. |
| Falhou a verificação | 0 | 5 | 5 | As regras aplicaram tudo, mas a verificação automática não passou. Vão também para o LLM. |
| Revogado por inteiro | 17 | 17 | 17 | O diploma que "altera" revoga o original. O DRE dá-o como em vigor. |
| Sem alteração textual | 498 | 498 | 500 | O diploma que altera não dá nenhuma instrução ao original (ver abaixo). |
| Sem texto | 50 | 50 | 50 | O original só tem PDF ou metadados (47), ou o diploma que altera não está no acervo (3). |
| **Total** | **671** | **671** | **671** | |

Não houve chave da API da Anthropic no ambiente: 0 pedidos à API. O LLM correu numa sessão do Claude. Pela API, para os 77 pendentes (72 para o LLM e 5 que falharam a verificação), a estimativa é de 77 pedidos, cerca de 247 mil tokens de entrada e 180 mil de saída: **cerca de 4,6 $ com a Claude Opus 5.5** (2,3 $ com a Sonnet 5.5). Também se pode fazer numa sessão do Claude, sem a API: a entrada está em `llm/entrada-sessao.jsonl` (ver "Pendentes numa sessão do Claude"). Os números saem de `medir.py` (`medicao.json`), sobre o export de 26/10/2026.

### O que mudou com o parser da fase 3

Na 1.ª corrida, 71 dos 84 pendentes tinham o original sem títulos `###### Artigo`, e as regras não sabiam onde aplicar as instruções. Agora, quando um original não tem nenhum título `###### Artigo`, `texto.com_titulos` usa `parse_articles` (`src/leis_portugal/domain/articles.py`) para os encontrar no texto corrido. Encontra artigos como "Artigo 1.º", "Art. 1.º - …" ou "###### ARTIGO 1.º", com a epígrafe na linha seguinte. Depois só reescreve essas linhas: a linha do artigo passa a `###### Artigo N.º — Epígrafe`, e um anexo em texto corrido passa a `## ANEXO …`. O resto fica letra a letra. Se a divisão não der exatamente os artigos do parser, o original fica como estava.

- **46 dos 71 ficaram com artigos.** 8 passaram para as regras (todos revogações de artigos, números ou alíneas). Os outros 38 passaram a ter um motivo concreto: redação nova sem aspas, revogação com exceções, etc. Destes, 5 falharam a verificação automática.
- **25 continuam sem artigos:**
  - 19 portarias e despachos só com números do dispositivo ("1.º", "2.º"), que não são artigos;
  - 4 decretos que aprovam um regulamento no mesmo texto, em que a numeração recomeça sem título de anexo (o parser chama-lhe "Parte 2", e aqui não se inventa um título);
  - 1 lei com bases em texto corrido;
  - 1 portaria em que o parser não encontra nada.
- **Os 22 da primeira ronda têm todos títulos `###### Artigo`, e o parser novo não os muda:** os 20 que continuam aplicados ficaram iguais byte a byte. Dois saíram por outra razão, descrita a seguir.

**Três erros apanhados na revisão à mão dos novos,** que levaram a duas regras novas em `alteracoes.py`:

- **Revogação condicional.** O Decreto-Lei n.º 16/2013 revoga, "na parte em que contrariem o disposto no presente decreto-lei", números e artigos de quatro diplomas. Não é uma revogação que se aplique ao texto. Passa a ir para o LLM.
  - Dois desses diplomas, o Decreto-Lei n.º 96/87 e o Decreto-Lei n.º 163-A/2000, estavam nos 22 da primeira ronda e tinham sido aplicados como "(Revogado.)". **Saem dos aplicados.** A entrada da 1.ª ronda já estava com o verificador e não se reescreveu. O verificador deu `certo` a todos os artigos dos dois (ver a secção seguinte).
  - Os outros dois (Decreto-Lei n.º 150/94 e Decreto-Lei n.º 189/94) eram novos.
- **Localizador de outro diploma.** A Portaria n.º 537/80 revoga "o n.º 6 da portaria supracitada", que é a Portaria n.º 455/79, e só menciona a Portaria n.º 71/79 mais à frente na frase. A regra aplicava a revogação ao n.º 6 do artigo 21.º da 71/79. Agora, "portaria supracitada", "referido diploma" e semelhantes mandam para o LLM.
- Uma correção menor: "O presente diploma revoga …" não era lido como verbo de revogação, e o "Art. 16.º" do próprio diploma que altera era tomado como alvo (Decreto-Lei n.º 285/77). Com a correção, este passou para as regras.

### Resultado da verificação às cegas

O verificador foi a Claude Sonnet 5.5, numa sessão à parte, com as regras da secção "Verificação às cegas" e só os três textos de cada diploma.

| Ronda | Diplomas | Artigos | `certo` | `errado` | `dúvida` |
| --- | --: | --: | --: | --: | --: |
| 1.ª (`saida-piloto.jsonl`) | 22 | 532 | 512 | 7 | 13 |
| 2.ª (`saida-piloto-2.jsonl`) | 8 | 197 | 196 | 0 | 1 |
| 3.ª (`saida-piloto-3.jsonl`) | 1 | 8 | 8 | 0 | 0 |
| 4.ª (`saida-piloto-4.jsonl`), os juntados com o LLM | 29 | 1273 | 1248 | 9 | 16 |
| 5.ª (`saida-piloto-5.jsonl`) | 2 | 43 | 43 | 0 | 0 |

Revisão à mão de cada `errado`, `dúvida` e nota por diploma:

- **Lei Orgânica n.º 4/2004: erro real, apanhado pelo verificador.** Os 7 `errado` e 11 das `dúvida` são deste diploma. A Lei Orgânica n.º 4/2014 adita artigos à Lei n.º 30/84, "alterada pelas Leis n.os 4/95, …, e pela Lei Orgânica n.º 4/2004". A regra só tirava a primeira menção da lista "alterada pelas …", por isso o "e pela Lei Orgânica n.º 4/2004" no fim contava como o diploma alterado. Os 7 artigos aditados à Lei 30/84 foram parar ao corpo da 4/2004. Agora toda a lista conta como diplomas que deram redação a outro (`_INICIO_CADEIA` e `_CADEIA` em `alteracoes.py`). A 4/2004 passou a "sem alteração textual", que é o certo: a LO 4/2014 altera a Lei 30/84 e não a lei que a republicou. A mesma correção tirou a Lei n.º 3/2010 dos pendentes: era só mencionada em "o Decreto-Lei n.º 32/2003, alterado pelo … e pela Lei n.º 3/2010", que é revogado.
- **Decreto-Lei n.º 94/91: erro real, apanhado pelo verificador.** As fórmulas finais ("Visto e aprovado…", "Promulgado…", as assinaturas) estavam no bloco do último artigo e desapareceram quando o artigo 8.º foi revogado. Agora ficam quando um artigo é reescrito (`_formulas_finais` em `aplicar.py`, com a mesma deteção de assinaturas do parser da fase 3). O consolidado mudou e foi a uma 3.ª ronda (`entrada-piloto-3.jsonl`), com os 8 artigos `certo` e as fórmulas finais preservadas.
- **Decreto-Lei n.º 96/87 e Decreto-Lei n.º 163-A/2000: erro real, que o verificador não apanhou.** São as revogações "na parte em que contrariem" do DL 16/2013, que já tinham saído dos aplicados. O verificador deu `certo` a todos os artigos: lê a revogação ao pé da letra, como as regras liam. As regras da verificação passam a dizer que uma revogação condicional não se aplica (regra 3).
- **Decreto Legislativo Regional n.º 13/98/A, artigo 17.º: fica por decidir.** Nenhuma instrução altera o artigo, e o consolidado mantém o original. Mas a republicação em anexo ao diploma que altera, "com as alterações ora introduzidas", tem outra redação ("regime jurídico" em vez de "diploma"). As regras seguem as instruções. Uma republicação que difere das instruções num artigo não alterado é uma decisão a tomar: conta a republicação, ou só as instruções?
- **Lei n.º 10/2012, artigo 3.º: fica por decidir.** O artigo 45.º da Lei n.º 26/2016, que dá a nova redação, foi depois alterado pela Lei n.º 68/2021. O texto do registo da 26/2016 no acervo já é o consolidado. A redação aplicada pode, por isso, ser a de 2021 e não a de 2016, e a nota de alteração só nomeia a 26/2016.
- **Decreto-Lei n.º 513-M/79, artigo 19.º: decidido, entra no acervo.** A revogação produz efeitos "com a entrada em vigor do Código" (dos Regimes Contributivos), que foi adiada por leis posteriores. O texto está certo e a data resolve-se: a Lei n.º 110/2009 e o Código entraram em vigor a 2011-01-01 (artigo 6.º, na redação da Lei n.º 119/2009), que é a `entry_into_force` do registo dela. O verificador notou ainda que o artigo 5.º da Lei n.º 110/2009 foi alterado pelas Leis n.os 55-A/2010 e 64-B/2011: essas alterações só acrescentaram alíneas no fim, e a alínea a), que revoga o artigo 19.º, está igual no texto consolidado.
- Nas outras 22 notas por diploma, nada em falta. Na 2.ª ronda, o verificador confirmou a normalização dos títulos nos 8 diplomas.

**Ficam 24 diplomas com todos os artigos `certo` (16 da 1.ª ronda, 7 da 2.ª e o DL 94/91 da 3.ª).** Com o DL 513-M/79, são 25 os que entraram no acervo (ver "Aplicação ao acervo"). As outras 2 dúvidas ficam de fora até se decidirem.

## Aplicação ao acervo

Em 2026-10-27, `acervo.py` gravou em `data/` os 25 consolidados por regra e verificados e, depois, os 20 juntados com o LLM com tudo `certo`. Cada registo fica como os consolidados do DRE:

- o corpo é o texto em vigor, com as notas "> Alterado pelo/a …" nos artigos alterados;
- `version.kind: consolidated`, com o rótulo "Versão consolidada pelo leis-portugal, sem valor oficial: alterações aplicadas por regra e verificadas às cegas" (nos juntados com o LLM, "alterações aplicadas com um LLM e verificadas às cegas"), e `consolidation_date` é a data em que a alteração entrou em vigor (a `entry_into_force` do diploma que altera; sem ela, a data de publicação);
- `<registo>.versoes.json` tem duas versões, a original (na data de publicação) e a alterada, por isso `leis-portugal version-at` dá o texto em qualquer data. Os fragmentos são os blocos entre títulos, sem `fragment_id` nem `type` do DRE, e o histórico diz `consolidated_by: leis-portugal`;
- `provenance.notes` diz que diploma deu as alterações e aponta para este README e para o `.alteracoes.json`.

Só entra um diploma com todos os artigos `certo` na última ronda em que esteve e sem problemas na linha do diploma (nada em `instrucoes_em_falta`, `artigos_em_falta` nem `artigos_a_mais`, e "sem alterações" fora dos artigos): a Portaria n.º 240/92 tinha os artigos todos `certo`, mas faltava a revogação do anexo II. Antes de gravar, o script confirma que o consolidado é o mesmo que foi verificado às cegas nessa ronda, e que o original em `data/` é o que a verificação recebeu. Se uma das duas falhar, o registo fica como estava. Correr outra vez não muda nada. Uma nova recolha do DRE não substitui o consolidado, porque o texto publicado tem menos precedência; quando o DRE publicar a sua própria versão consolidada, essa substitui a nossa.

Os Decretos-Leis n.os 96/87 e 163-A/2000 tinham todos os artigos `certo` na 1.ª ronda, mas não entram: saíram dos aplicados por regra por causa da revogação condicional.

Por tipo de erro: a verificação às cegas apanhou os 2 erros de **posição e âmbito** (artigos no sítio errado, texto apagado fora do artigo). Não apanhou o erro de **leitura jurídica** (a revogação condicional), em que o verificador faz a mesma leitura literal que as regras. Esse tipo de erro só a revisão à mão o apanhou.

### A relação `amended_by` do DRE não quer dizer "alterou o texto"

O achado com mais peso no plano: 500 dos 671 diplomas (75%) não têm alteração textual a aplicar (498 na 1.ª corrida; a contagem por motivo abaixo é dessa corrida). Confirmou-se à mão em ~60 casos. A relação do DRE junta coisas muito diferentes:

- **303: o original só aparece numa lista ou numa remissão**, quase sempre "alterado pelos Decretos-Leis n.os …, 45/2007, …". O diploma que altera muda **outro** diploma, na redação que o original lhe tinha dado. O DRE regista a relação no original quando devia registá-la no outro.
- **179: o diploma que altera cita o original sem lhe dar instruções.** São portarias feitas "ao abrigo do" original, prorrogações de prazos, "mantido em vigor", ratificações, extinções de serviços, alterações de mapas orçamentais.
- **16: o diploma que altera nem sequer menciona o original.**

410 destas 498 relações têm o rótulo "Última alteração registada na importação inicial", sem data. Para o RAG, isto quer dizer que boa parte dos "27.086 alterados sem consolidação" pode ter o texto original como texto em vigor. Antes de o assumir, falta medir quantos têm outra alteração que o DRE não registou (fase 3).

### Revogados que o DRE dá como em vigor

17 originais são revogados por inteiro pelo diploma que os "altera" (por exemplo, o Decreto-Lei n.º 90/90 pela Lei n.º 54/2015, ou o Decreto-Lei n.º 162/2019 pelo Decreto-Lei n.º 15/2022). Para a vigência da fase 3, a ligação certa é `repealed_by`. Há ainda 14 revogações "com exceção dos artigos …" ou "na parte que …" e 4 revogações condicionais, que ficam nos pendentes.

### O que as regras aplicaram

Nos 27 diplomas aplicados por regra houve 96 alterações:

| Regra | Alterações |
| --- | --: |
| Revogação de artigo | 59 |
| Substituição com "[...]" (junta número a número) | 15 |
| Revogação de número ou alínea | 12 |
| Substituição integral da redação | 8 |
| Aditamento de artigo | 1 |
| Substituição parcial (só um número ou alínea) | 1 |

### Porque é que 77 ficam para o LLM

São 72 para o LLM e 5 que falharam a verificação, com 93 instruções:

| Motivo | Instruções |
| --- | --: |
| Redação nova sem aspas «» (diplomas antigos: "Art. 3.º O n.º 6 do artigo 15.º … passa a ter a seguinte redacção:" e o texto segue sem aspas) | 34 |
| Revogação com exceções ou só em parte | 13 |
| Anexo do original não identificado (o original tem vários anexos ou nenhum `## Anexo`) | 9 |
| Falhou a verificação: as regras aplicaram tudo, mas a verificação encontrou um parágrafo do diploma que altera, com um verbo de alteração, que nenhuma instrução leu, uma marca "[Anterior …]" que ficou no texto ou um parágrafo que não vem de nenhum dos textos | 8 |
| Instrução de outro tipo ("passa a designar-se", "é suprimido", "é aditada uma alínea") | 7 |
| Alvo da nova redação não identificado | 5 |
| Retificações que não se aplicam com segurança | 5 |
| Revogação condicional ("na parte em que contrariem") | 4 |
| Revogações com um alvo que a regra não lê | 5 |
| Original só com números do dispositivo (1.º, 2.º) | 1 |
| Localizador de outro diploma ("portaria supracitada") | 1 |
| Revogação do que o original aprovou em anexo | 1 |

O maior bloqueio passa a ser **a redação nova sem aspas** (34 instruções). É o padrão dos diplomas antigos: "passa a ter a seguinte redacção:", seguido dos artigos em texto corrido até ao artigo seguinte do próprio diploma que altera. Uma regra que leia esse texto, com o parser da fase 3 para encontrar onde acaba, deve passar boa parte destes para as regras.

### Comparação com as republicações

Quando o diploma que altera republica o original em anexo, o consolidado compara-se com a republicação, que é a melhor verificação independente que há. Aconteceu em 2 diplomas:

- **Decreto Legislativo Regional n.º 13/98/A:** 13 artigos iguais, 3 com diferenças só de pontuação ("referidos número" e "referidos no número") e nenhum diferente nos artigos alterados.
- **Decreto Legislativo Regional n.º 29/2006/A** (fica para o LLM por um aditamento de capítulo): 13 iguais, 5 com diferenças menores e 1 com "60" no alterador e "sessenta" na republicação.

Esta comparação apanhou um erro real nas primeiras versões: a marca de renumeração "4 - [Anterior n.º 2]." era copiada como texto. A republicação também mostrou que **as republicações não reproduzem o alterador letra a letra**: atualizam a grafia (Acordo Ortográfico), corrigem gralhas e mudam artigos que nenhuma instrução manda alterar ("90 dias" passa a "noventa dias"). Por isso a comparação ignora a ortografia e só conta como erro uma diferença de substância num artigo alterado.

## Método

1. **Seleção** (`selecionar.py` → `selecao.jsonl`): diplomas portugueses e regionais em vigor segundo o DRE (`in_force` ou `partially_in_force`), `version_kind = original`, com um único alvo distinto nas relações `amended_by` e 10 ou mais citações (`cites`) no acervo. Dá os 671 do plano. Nenhum dos registos com `republished_by` no front matter cumpre os dois critérios (os Códigos do IRS e do IRC, por exemplo, têm mais de 100 alterações), por isso não houve nenhum a excluir; o script marca-os se aparecerem.
2. **Leitura das instruções** (`alteracoes.py`): o diploma que altera é lido parágrafo a parágrafo, sem o preâmbulo quando tem artigos. Uma instrução só conta como dirigida ao original quando o original é o diploma de que se alteram os artigos ("o artigo 5.º do Decreto-Lei n.º …"), e não o que deu a redação ("na redação dada pelo …"). Lê substituições («…» com os artigos ou só um número ou alínea), aditamentos, revogações (também em listas "São revogados: a) …"), retificações ("onde se lê «X» deve ler-se «Y»") e revogações do diploma inteiro. O resto fica em `por_aplicar`, com o motivo.
3. **Aplicação por regras** (`aplicar.py`): as regras e os casos em que falham estão no início do ficheiro. Só se reescrevem os artigos alterados; o resto do registo fica igual por construção. Cada artigo alterado leva uma nota no formato das consolidações do acervo ("> Alterado pelo/a Artigo 2.º do/a [Decreto-Lei …](…), publicado em …"). Um artigo revogado fica com o corpo "(Revogado.)", como nas consolidações do DRE.
4. **Verificação automática** (`verificar.py`), feita com um parser diferente (o de `avaliacao/comum.py`) para os artigos não alterados:
   - cada parágrafo de um artigo alterado está, letra a letra, no diploma que altera ou no artigo original (o "[...]"); nas substituições integrais e nos aditamentos, o artigo inteiro está seguido no diploma que altera;
   - não fica nenhuma marca editorial ("[...]", "[Anterior n.º 2]") no texto;
   - nas alterações parciais, o resto do artigo não muda;
   - os artigos não alterados e o texto fora dos artigos ficam iguais, e o número de artigos bate com os aditamentos;
   - nenhum parágrafo do diploma que altera menciona o original com um verbo de alteração sem ter dado uma instrução aplicada, e os artigos que o rótulo do DRE dá como alterados foram alterados;
   - quando há republicação, a comparação descrita acima.
5. **Títulos pelo parser da fase 3**: quando o original não tem nenhum `###### Artigo`, os títulos vêm de `parse_articles` (ver acima). O consolidado fica com os títulos normalizados em todos os artigos, alterados ou não, e o cabeçalho diz `titulos_normalizados`.
6. **Revisão à mão**: as diferenças dos consolidados foram lidas. Na 1.ª corrida, as dos 22 apanharam dois erros que a verificação deixava passar e que estão corrigidos: uma alínea "e)" lida como a conjunção "e", que substituía o n.º 2 inteiro em vez da alínea e), e uma retificação já presente no texto do acervo, que dava ";;". A segunda verificação acima (o resto do artigo não muda) entrou por causa do primeiro. Na 2.ª, as dos novos apanharam os três erros descritos em "O que mudou com o parser da fase 3". A verificação às cegas apanhou mais dois (ver "Resultado da verificação às cegas").

A amostra de 50 diplomas (`consolidar.py --amostra 50 --semente 1`) serviu para afinar o método antes de correr os 671. Só 8 dos 50 tinham instruções; o resto do afinamento fez-se sobre os 671.

## Ficheiros

| Ficheiro | O que é |
| --- | --- |
| `selecionar.py` | Seleção dos 671 a partir de `exports/leis-portugal.sqlite` (num worktree, usa o export da pasta principal) |
| `texto.py` | Leitura dos registos: corpo, artigos (com os títulos do parser da fase 3 quando faltam), referências a diplomas |
| `alteracoes.py` | Leitura das instruções do diploma que altera |
| `aplicar.py` | Aplicação por regras |
| `verificar.py` | Verificação automática e comparação com a republicação |
| `consolidar.py` | Corre tudo e escreve os resultados |
| `llm.py` | Pedidos ao LLM para os pendentes: `--estimar` sem chave, `--executar` com chave, `--sessao` e `--importar` para o fazer numa sessão do Claude |
| `juntar.py` | Junta ao original as respostas do LLM aprovadas (`llm/juntados.jsonl`) |
| `cegas.py` | Entrada da verificação às cegas (`--ronda N`): os aplicados por regra e os juntados com o LLM que não estão nas rondas anteriores |
| `acervo.py` | Aplicação ao acervo dos consolidados verificados às cegas, rondas e lotes (`--dry-run` só mostra; `--supor-verificados` com ele conta os lotes ainda sem saída) |
| `medir.py` | Números do piloto (`medicao.json`) |
| `selecao.jsonl` | Os 671, com o diploma que altera, os rótulos do DRE e os artigos que mencionam o original |
| `resultados.jsonl` | Estado e motivo por diploma |
| `pendentes.jsonl` | As instruções por aplicar, com o texto dos artigos do original em causa |
| `piloto/<caminho do registo>.md` | O texto consolidado (os 27 aplicados por regra e os 26 juntados com o LLM) |
| `piloto/<caminho do registo>.alteracoes.json` | Um registo por alteração: artigo, operação, regra, texto antes e depois, excerto que a justifica, método |
| `verificacao/entrada-piloto.jsonl` | Entrada da 1.ª ronda da verificação às cegas (os 22 da 1.ª corrida, como estavam) |
| `verificacao/entrada-piloto-2.jsonl` | Entrada da 2.ª ronda: os 8 aplicados por regra que não estão na 1.ª |
| `verificacao/entrada-piloto-3.jsonl` | Entrada da 3.ª ronda: o DL 94/91, que mudou depois da 1.ª |
| `verificacao/entrada-piloto-4.jsonl` | Entrada da 4.ª ronda: os 29 juntados com o LLM (3 deixaram depois de se juntar) |
| `verificacao/entrada-piloto-5.jsonl` | Entrada da 5.ª ronda: os DL 491/70 e 80/78, que mudaram depois da 4.ª |
| `verificacao/saida-piloto*.jsonl` | Saídas das rondas (escritas pela sessão que verifica) |
| `llm/entrada-sessao.jsonl` | Os 77 pendentes, prontos para uma sessão do Claude |
| `llm/respostas-sessao.jsonl`, `llm/<id>.json` | As respostas da sessão e o resultado do `--importar` |
| `llm/juntados.jsonl` | O que o `juntar.py` juntou e porque não juntou o resto |
| `medicao.json` | Os números acima |

Para repetir, a partir da raiz do worktree:

```bash
cd consolidacao && export PYTHONPATH=../src && python selecionar.py && python consolidar.py && python llm.py --sessao && python llm.py --importar llm/respostas-sessao.jsonl && python juntar.py && python cegas.py --ronda 5 && python medir.py
```

## Verificação às cegas

A verificação faz-se noutra sessão, **com outro modelo**: as regras e o código foram escritos com a Claude Opus 5.5. A sessão recebe `verificacao/entrada-piloto.jsonl`, uma linha por diploma:

| Campo | Conteúdo |
| --- | --- |
| `id`, `titulo` | O diploma original |
| `alterador` | O título do diploma que o altera |
| `texto_original` | O corpo do registo original, como está em `data/` |
| `texto_alterador` | O corpo do diploma que altera; se `alterador_completo` for `false`, só os artigos dele que mencionam o original (o diploma tem mais de 60 mil caracteres) |
| `texto_consolidado` | O texto que o piloto produziu, sem as notas "> Alterado pelo/a …" |

A entrada não diz que artigos mudaram nem como: quem verifica tem de os encontrar.

A 2.ª ronda (`verificacao/entrada-piloto-2.jsonl`) tem o mesmo formato. Quando o original tem os artigos em texto corrido, a linha traz também `titulos_normalizados: true` e `texto_original_com_titulos`, que é o original com os títulos `###### Artigo N.º — Epígrafe` postos pelo piloto.

**Regras da verificação:**

1. Ler o diploma que altera e listar **todas** as instruções dirigidas ao original: substituições, aditamentos, revogações, retificações, renumerações, alterações de epígrafe. Uma instrução que altera **outro** diploma ("o artigo 5.º do Decreto-Lei X, na redação dada pelo [original]") não é do original e não se aplica.
2. Para **cada artigo** do texto consolidado, dar um veredicto:
   - `certo`: se a instrução o altera, o texto é a nova redação **letra a letra** como está no diploma que altera, com o texto original no lugar de cada "[...]"; se não o altera, é igual ao original letra a letra;
   - `errado`: qualquer diferença de substância (palavra, número, número ou alínea a mais ou a menos, epígrafe errada, artigo que devia estar revogado ou não). Escrever o texto esperado;
   - `dúvida`: a instrução é ambígua ou depende de outro diploma. Explicar porquê.
   As diferenças de grafia, pontuação ou espaços que já estão no diploma que altera não são erro: o consolidado copia o diploma que altera, mesmo com gralhas.
3. Um artigo revogado fica com o título, a epígrafe e o corpo "(Revogado.)". Um número revogado fica "N - (Revogado.)", e uma alínea "a) (Revogada.)". Uma revogação condicional ("são revogados, na parte em que contrariem o presente diploma, …") não se aplica ao texto: se o consolidado a aplicou, é `errado`.
4. Por diploma, listar à parte: **instruções em falta** (do passo 1, sem efeito no consolidado), **artigos a mais ou a menos** e **texto fora dos artigos** (preâmbulo, títulos de capítulo) que tenha mudado.
5. Não usar outras fontes (DRE, internet, outros registos): só os três textos da entrada.
6. Não ler `piloto/*.alteracoes.json`, `resultados.jsonl` nem o código desta pasta antes de terminar.
7. Com `titulos_normalizados`, os títulos `###### Artigo N.º — Epígrafe` do consolidado não são erro. Comparar os artigos com `texto_original_com_titulos` e verificar também que este só difere de `texto_original` nas linhas dos títulos: a linha "Artigo N.º" (ou "Art. N.º - …") e a da epígrafe passam a título, e o texto que vinha na mesma linha passa ao parágrafo seguinte. Um erro da normalização (um artigo partido ou juntado, texto perdido) conta como `errado`.

**Saída:** `verificacao/saida-piloto.jsonl` (na ronda N, `verificacao/saida-piloto-N.jsonl`), uma linha por artigo, `{"id", "artigo", "veredicto": "certo" | "errado" | "dúvida", "motivo", "texto_esperado"}`, e uma linha por diploma, `{"id", "instrucoes_em_falta": [...], "artigos_a_mais": [...], "artigos_em_falta": [...], "fora_dos_artigos": "..."}`.

**Depois:** cada `errado` ou `dúvida` e cada instrução em falta é revista à mão (ou numa terceira sessão) e, se for o caso, corrige-se a regra e volta a correr-se tudo. Um diploma só entra no acervo quando todos os artigos estão `certo`.

## Pendentes numa sessão do Claude

Sem chave da API, uma sessão do Claude pode aplicar os pendentes, como se fez na avaliação. `python llm.py --sessao` escreve `llm/entrada-sessao.jsonl`, uma linha por diploma (77), com:

| Campo | Conteúdo |
| --- | --- |
| `id`, `titulo`, `alterador` | O diploma original e o que o altera |
| `motivos` | Porque é que as regras não aplicaram |
| `regras` | As regras de aplicação (o mesmo texto que vai como `system` nos pedidos à API) |
| `esquema_da_resposta` | O esquema JSON da resposta |
| `pedido` | Os artigos do original em causa, ou o texto inteiro quando o original não tem artigos identificados, e as instruções do diploma que altera |

A sessão escreve uma linha por diploma, `{"id", "artigos": [{"chave", "epigrafe", "texto"}], "nao_aplicavel"}`, em `llm/respostas-sessao.jsonl`. `python llm.py --importar llm/respostas-sessao.jsonl --modelo <modelo da sessão>` passa cada resposta pela mesma verificação das respostas da API: cada parágrafo tem de estar, letra a letra, no diploma que altera ou no original. Grava o resultado em `llm/<id>.json`, com os problemas que encontrar.

### Resultado (Opus 5.5, numa sessão do Claude, em 2026-10-27)

| Resposta no `--importar` | Diplomas |
| --- | --: |
| Aprovada (artigos, sem problemas) | 46 |
| Não aplicável (sem artigos, com o motivo) | 24 |
| Com problemas na verificação letra a letra | 7 |

Os 7 com problemas não se juntam. Os 24 não aplicáveis são, sobretudo, quadros e anexos que só existem no PDF, alterações que não são textuais e revogações condicionais.

`python juntar.py` junta as 46 aprovadas ao original e escreve `piloto/<caminho>.md`, como o `consolidar.py`, e `llm/juntados.jsonl`:

- **26 juntados** (eram 29 antes da 4.ª ronda; ver abaixo). Quando as regras tinham aplicado parte das instruções (o resto foi para o LLM), o consolidado leva as duas. Quando falhou a verificação, o LLM fez todas e as regras não entram. Os artigos da resposta são reescritos no lugar ou aditados por ordem, com a nota "> Alterado/Revogado/Aditado pelo/a …". 3 são parciais: a resposta deixou uma instrução de fora (`parcial` em `juntados.jsonl`).
- **20 não juntados.** O original não tem artigos (portarias "1.º, 2.º", bases, numeração que recomeça), e os artigos da resposta não têm onde encaixar sem inventar títulos. Falta aplicar a resposta no texto corrido.

Os 29 de então foram à 4.ª ronda da verificação às cegas (`verificacao/entrada-piloto-4.jsonl`), com as mesmas regras e o mesmo verificador. A entrada não dizia quais vieram do LLM nem que havia parciais.

### Verificação às cegas dos juntados com o LLM

O verificador encontrou dois erros do piloto, já corrigidos:

- **Artigos colados ao anterior.** O parser da fase 3 não reconhece "Art. 12." nem "Art. 220:º", e o artigo ficava dentro do anterior (Portaria n.º 18523, Decretos n.os 49073 e 47951). Agora `com_titulos` recusa a normalização quando há uma destas linhas com o número que falta entre dois artigos. Os três voltam a ficar sem artigos e não se juntam.
- **Linhas perdidas no fim de um artigo revogado.** A linha dos nomes antes de "Promulgado" (Decreto-Lei n.º 80/78) e os títulos de capítulo em texto corrido, "III" e "Das farinhas" (Decreto-Lei n.º 491/70), estavam no bloco do artigo e desapareciam. Agora `_formulas_finais` guarda-os. Os dois foram à 5.ª ronda e ficaram com tudo `certo`.

Os 27 aplicados por regra não mudam com estas correções.

Encontrou também 6 diplomas com erros ou dúvidas nas respostas do LLM, que ficam de fora:

| Diploma | O que o verificador encontrou |
| --- | --- |
| Decreto-Lei n.º 118/82 | Falta a nova redação dos artigos 1.º, 7.º e 8.º (resposta parcial: o anexo só existe no PDF) |
| Decreto n.º 45575 | Falta a revogação do artigo 71.º e a troca de "engenheiros de 2.ª classe" por "engenheiro-adjunto" no articulado |
| Decreto Legislativo Regional n.º 29/2006/A | Os artigos 17.º-A e 17.º-B passam a formar um Capítulo V novo e os capítulos seguintes são renumerados; o `juntar.py` não muda capítulos |
| Portaria n.º 240/92 | Falta a revogação do anexo II (resposta parcial) |
| Decreto-Lei n.º 219/92 | Revogação "do que não ficou transitoriamente mantido" (resposta parcial), "parte inicial" de alíneas e uma regra interpretativa (CRAF) |
| Decreto-Lei n.º 201-A/79 | Interpretação autêntica do artigo 30.º, sem alteração textual (dúvida; o verificador acha razoável deixar o texto) |

As 3 respostas parciais estão todas nesta lista: o verificador encontrou o que faltava sem saber que eram parciais.

**Ficam 20 juntados com o LLM com tudo `certo`, e estão no acervo desde 2026-10-27** (ver "Aplicação ao acervo").

## Escala: os 25.498 diplomas em vigor alterados sem consolidação

Frente B do [plano de execução](../PLANO-RAG.md): a triagem e as regras do piloto, corridas em todos os diplomas em vigor que o DRE dá como alterados e não consolida, com qualquer número de alterações e de citações. Só regras e verificação automática, sem LLM; o que fica para o LLM e para a verificação às cegas sai em lotes. Tudo sobre o export de `exports/leis-portugal.sqlite` de 27/10/2026 (18:58). Os números abaixo vêm de `medicao-escala.json` (`medir.py --escala`) e de `resultados-escala.jsonl`.

### Seleção (`selecionar.py --todos`)

Em vigor (`in_force` ou `partially_in_force`), português ou regional, `version_kind = original`, com texto e pelo menos uma relação `amended_by`: **25.498 diplomas**, em `selecao-escala.jsonl`, com os alteradores por ordem de data de publicação (os que não estão no acervo, pela data da relação do DRE, ou no fim), as citações recebidas e o `republished_by`. As diferenças para os números do plano:

- **25.940 no plano, 25.498 aqui:** o plano conta também 442 diplomas da UE, que ficam de fora (a seleção é PT e regional, como no piloto).
- **A contagem por número de alterações é outra:** aqui conta-se alteradores distintos, 1 → 16.099, 2–3 → 6.820, 4–10 → 2.190, >10 → 389 (por linhas da relação, 1 → 7.278, 2–3 → 14.249, 4–10 → 3.540, >10 → 431). As faixas do plano (8.975, 14.962, 3.802, 482) somam 28.221 e não se reproduzem com este export; a faixa de citações reproduz-se (147 com ≥100, 1.998 com 10–99, 19.723 com 1–9, 3.630 com 0).
- **Os 25 do piloto já no acervo saem:** o export de 27/10 já os dá como `consolidated` (o `acervo.py` correu antes). Os 20 juntados com o LLM ainda estão no export como originais e entram; `texto.publicado` lê-lhes o texto publicado.
- 1.257 alteradores não estão no acervo e 742 estão só com PDF ou metadados; 13 diplomas têm `republished_by` e ficam excluídos.

### Resultado

| Estado | ≥100 citações | 10–99 | 1–9 | 0 | **Total** | O que quer dizer |
| --- | --: | --: | --: | --: | --: | --- |
| Sem alteração textual | 102 | 1.243 | 14.635 | 2.938 | **18.918** | Nenhum alterador dá instruções ao texto: o original é o texto em vigor |
| Para o LLM | 28 | 548 | 3.594 | 192 | **4.362** | Um alterador tem instruções que as regras não leem, não aplicam ou não verificam (`falhou_em` diz qual e em que fase) |
| Sem texto do alterador | 5 | 116 | 479 | 267 | **867** | Um dos alteradores não está no acervo (1.253 casos) ou só tem metadados (720) ou PDF (20): não se sabe se altera o texto |
| Revogado por inteiro | 5 | 57 | 684 | 53 | **799** | Um alterador revoga o original; o DRE dá-o como em vigor (9 têm alterações depois da revogação) |
| Aplicado por regra | 4 | 33 | 326 | 21 | **384** | Todos os alteradores com instruções aplicados e verificados automaticamente; vão à verificação às cegas |
| Não triado | 0 | 0 | 0 | 155 | **155** | O título do original não tem número ("Declaração", "Despacho Conjunto"): as regras não encontram as menções |
| Excluído | 3 | 1 | 5 | 4 | **13** | `republished_by`: o texto atual está no consolidado que o republicou |
| **Total** | **147** | **1.998** | **19.723** | **3.630** | **25.498** | |

| Estado | 1 alteração | 2–3 | 4–10 | >10 |
| --- | --: | --: | --: | --: |
| Sem alteração textual | 12.607 | 4.853 | 1.289 | 169 |
| Para o LLM | 2.306 | 1.366 | 586 | 104 |
| Sem texto do alterador | 275 | 268 | 228 | 96 |
| Revogado por inteiro | 536 | 196 | 55 | 12 |
| Aplicado por regra | 254 | 107 | 20 | 3 |
| Não triado | 115 | 29 | 9 | 2 |
| Excluído | 6 | 1 | 3 | 3 |
| **Total** | **16.099** | **6.820** | **2.190** | **389** |

**18.918 diplomas (74%) deixam de precisar do aviso "texto original; alterado por…"**: nenhum dos alteradores lhes dá uma instrução dirigida ao texto, como nos 500 do piloto (75%). Nos 2.145 com 10 ou mais citações são 1.345. Por motivo (o mais frequente entre os alteradores de cada diploma): 8.454 só aparecem numa lista ou remissão ("alterado pelos Decretos-Leis n.os …" de outro diploma), 7.532 são citados sem instruções (ao abrigo de, prorrogações, quadros de pessoal, exonerações) e 2.920 nem são mencionados (muitos são relações do DRE a outro diploma: a Lei n.º 37/2010 tem como "alteradores" os orçamentos que mudam a Lei Geral Tributária na redação que ela lhe deu). Uma amostra de 12 lida à mão não tinha nenhuma alteração textual. **Corrigido a 12/11/2026, ver "Triagem: alterações que as regras não leem":** numa amostra de 80 ao acaso, um verificador às cegas achou 11 com alteração do texto, e 1.325 diplomas passaram para o LLM; a triagem às cegas que se seguiu devolveu 258 a "sem alteração textual" e 449 a "alteração só em imagem". Hoje ficam 18.263 sem alteração textual.

A triagem foi alterador a alterador: 51.817 pares original–alterador, dos quais 41.723 sem alteração textual, 6.109 para o LLM, 1.993 sem texto, 1.191 aplicáveis por regra e 801 revogações por inteiro. Numa alteração múltipla, uma alteração sem instruções não impede as outras; a precedência entre os alteradores é revogado por inteiro > sem texto do alterador > para o LLM > aplicável por regra > sem alteração textual. Na triagem (só a leitura), 671 diplomas eram aplicáveis por regra; na aplicação, 384 ficaram aplicados e 287 passaram para o LLM: dos 4.362 para o LLM, 4.036 falharam na leitura das instruções, 226 na aplicação e 100 na verificação automática (`falhou_em` em `resultados-escala.jsonl`). Em 310 dos para o LLM, as regras aplicaram parte das instruções antes da falha, e o `.alteracoes.json` fica em `piloto/`.

**Os 384 aplicados por regra** têm 857 alterações, 30 deles com dois ou mais alteradores aplicados em sequência (por exemplo, o Decreto-Lei n.º 224/2000, pelos Decretos-Leis n.os 117/2002 e 109/2003). Por regra: 270 revogações de artigo, 269 substituições com "[...]", 131 substituições integrais, 79 aditamentos de artigo, 78 revogações de número ou alínea, 22 retificações, 7 substituições parciais e 1 aditamento de número ou alínea. 90 têm os títulos pelo parser da fase 3. 24 diplomas foram comparados com uma republicação.

**Os 4.362 para o LLM** são, em primeiro lugar, originais sem artigos identificados: 2.697 (2.063 só com números do dispositivo "1.º, 2.º", 528 sem nada que o parser reconheça, 101 com numeração repetida, 5 com bases em texto corrido). No piloto, as respostas do LLM para estes não se juntaram ao original (não há artigos onde encaixar), por isso o LLM só resolve a parte restante sem uma forma de aplicar a resposta no texto corrido. Depois vêm a redação nova sem aspas (555 diplomas; 2.071 instruções), o anexo do original não identificado (331; 1.529 instruções), a instrução de outro tipo (226; 1.163) e o alvo da nova redação não identificado (963 instruções). Os 155 não triados têm todos menos de 10 citações.

**Os 799 revogados por inteiro** e os 867 sem texto do alterador são para a fase 3 (vigência e relações, e recolha dos alteradores em falta).

### Tempos

- Seleção: menos de 1 minuto.
- Triagem e aplicação: 6 partes em paralelo (`consolidar.py --escala --parte i/6`, uma por processo, em background com log em `logs/escala.parte-i.txt`), 306 a 333 s cada, **cerca de 5,5 minutos de relógio**; 1.916 s de CPU somados, 0,075 s por diploma em média; o mais lento foi o Decreto-Lei n.º 394-B/84, com 137 alteradores, em 13 s. Sem nenhum erro. Os 155 sem número no título e os 26 juntados com o LLM foram refeitos com `--refazer`.
- Junção, medição, entrada às cegas e lotes do LLM: cerca de 2 minutos.

### O que mudou no código

- `selecionar.py --todos`: a seleção da escala, com `alteradores` por ordem de data.
- `consolidar.py`: `processar` aplica os alteradores por ordem sobre o resultado do anterior, com `verificar.py` depois de cada um (contra o texto de antes desse alterador, e com os rótulos do DRE dessa relação); por diploma ficam `triagem`, `estado`, `passos` (um por alterador, com a triagem, as instruções, as regras e os problemas) e `falhou_em`. Depois de uma falha, os alteradores seguintes só se leem (sobre o texto de antes da falha) e tudo vai para o LLM. `--escala`, `--parte i/N`, `--refazer`, `--juntar`; retomável por diploma (cada parte acrescenta ao seu ficheiro e salta os feitos); um diploma com erro fica com `estado: erro` e o traceback, sem parar a corrida. Um título sem número dá `não triado`. Não reescreve os ficheiros de `piloto/` dos juntados com o LLM. Os 671 do piloto dão exatamente os mesmos estados e motivos de antes (confirmado correndo o modo do piloto para um ficheiro à parte).
- `cegas.py --escala`: a ronda a seguir à última em `verificacao/`, em lotes de 30 (`entrada-piloto-N-lote-NN.jsonl`); um diploma com vários alteradores leva `alteradores` (título e texto de cada um) e `texto_alterador` com os textos juntos. `texto.publicado` ordena as rondas e os lotes pelos números do nome.
- `llm.py --escala --sessao --lote 40`: os pendentes por citações, em `llm/entrada-sessao-escala-NNN.jsonl`; os pedidos com vários alteradores dizem de que diploma vem cada instrução, e a verificação letra a letra das respostas procura em todos.
- `medir.py --escala`: `medicao-escala.json`.
- `acervo.py`: lê as rondas em lotes (`entrada-piloto-N-lote-NN.jsonl` com `saida-piloto-N-lote-NN.jsonl` ao lado; um lote sem saída fica por verificar e não se aplica, mesmo que uma ronda anterior tenha aprovado outro texto do diploma) e os diplomas com vários alteradores aplicados: lê `resultados-escala.jsonl` e `selecao-escala.jsonl` (o piloto tem precedência), a versão alterada do histórico leva em `acts` todos os alteradores com alterações aplicadas e a data em que o último entrou em vigor (`consolidation_date`); o texto intermédio de cada passo não se guarda, por isso o histórico continua a ter duas versões. O controlo do histórico ignora o título `# …`, que vem do registo. `--dry-run --supor-verificados` conta os diplomas como se tudo fosse `certo`.

### O que fica para a verificação às cegas e para o LLM

- **Verificação às cegas, 6.ª ronda:** 382 diplomas (os 384 aplicados por regra menos 2 do piloto já verificados com o mesmo texto) em 13 lotes de até 30, `verificacao/entrada-piloto-6-lote-01.jsonl` a `-13`, 20 MB, no formato das rondas anteriores (regras na secção "Verificação às cegas"; com vários alteradores, `texto_alterador` junta os textos e `alteradores` tem-nos à parte). A verificação é de outra sessão, com outro modelo; a saída fica em `verificacao/saida-piloto-6-lote-NN.jsonl`.
- **LLM:** 4.362 diplomas em 110 lotes de até 40, `llm/entrada-sessao-escala-001.jsonl` a `-110`, primeiro os 1.665 de original com artigos identificados (lotes 001 a 042, por citações recebidas, os 28 com ≥100 sobretudo no primeiro lote) e depois os 2.697 sem artigos (a ordem está em `llm/LEIAME-lotes.md`), 52 MB. Estimativa pela API: 4.362 pedidos, cerca de 13,9 milhões de tokens de entrada e 10,9 milhões de saída, cerca de 273 $ com a Opus 5.5 (137 $ com a Sonnet 5.5). A ordem já põe primeiro os que o `juntar.py` sabe juntar.

Ficheiros novos: `selecao-escala.jsonl`, `resultados-escala.jsonl` (e `resultados-escala.parte-i.jsonl`), `pendentes-escala.jsonl`, `medicao-escala.json`, `logs/escala.parte-i.txt`, `piloto/<caminho>.md` e `.alteracoes.json` dos aplicados e dos parciais, `verificacao/entrada-piloto-6-lote-NN.jsonl`, `llm/entrada-sessao-escala-NNN.jsonl`. Para repetir, a partir da raiz do worktree:

```bash
cd consolidacao && export PYTHONPATH=../src && python selecionar.py --todos && for i in 1 2 3 4 5 6; do python consolidar.py --escala --parte $i/6 > logs/escala.parte-$i.txt 2>&1 & done; wait; python consolidar.py --escala --juntar && python medir.py --escala && python cegas.py --escala && python llm.py --sessao --escala
```

## Limites e próximos passos

- **Data de entrada em vigor:** o consolidado é o texto depois da alteração, tal como foi publicada. As alterações com entrada em vigor diferida ou com efeitos retroativos não estão modeladas (é trabalho da fase 3).
- **Grafia:** o texto novo vem do diploma que altera e o resto do original, por isso o mesmo artigo pode ter grafias diferentes ("actividade" e "atividade"), como nas consolidações oficiais.
- **Notas e ligações:** os parágrafos retificados perdem as ligações Markdown. O cabeçalho YAML de `piloto/*.md` é próprio do piloto; o formato em `data/` está em "Aplicação ao acervo".
- **O que é preciso para o resto:**
  1. decidir as 2 dúvidas que ficam (republicação que difere das instruções, alterador alterado depois);
  2. dos 77 pendentes: aplicar no texto corrido as 20 respostas aprovadas cujo original não tem artigos, e rever os 6 juntados com erros, os 7 com problemas e os 24 não aplicáveis;
  3. uma regra para a redação nova sem aspas (34 instruções);
  4. decidir o que fazer com os 500 sem alteração textual e os 17 revogados (vigência e relações, fase 3).
- **Os outros 1.468 diplomas com 10 ou mais citações** têm mais de uma alteração. O método serve na mesma (aplicar as alterações por ordem de data), mas a amostra mostra que é preciso filtrar primeiro as relações que não são alterações textuais.

### Rondas 6 e 7: verificação às cegas por subagentes e LLM em subagentes

Feito em 2026-10-28, sem alterar `data/`. A verificação e as respostas do LLM vieram de subagentes de uma sessão do Claude (Sonnet 5.5 na verificação, Opus 5.5 no LLM), sem API.

**Verificação às cegas da ronda 6** (382 diplomas, 13 lotes). `cegas_vista.py vistas 6 PASTA` divide a ronda em pedaços (de até 140 mil caracteres, nunca de dois lotes) e escreve para cada um uma vista com o texto do alterador e só os artigos do consolidado que diferem do original (comparados pelo título) e a lista dos que são iguais; 47 subagentes, um por pedaço, deram os veredictos num JSON; `cegas_vista.py saida 6 PASTA` junta-os em `verificacao/saida-piloto-6-lote-NN.jsonl`, no formato das rondas anteriores (os artigos iguais ao original ficam `certo` por omissão). O verificador não lê registos de alterações, regras nem código. Seis diplomas ficaram sem resposta no pedaço 32 (o subagente respondeu a menos do que a vista tinha) e foram repetidos.

| Lote | Diplomas | Sem reparos | Com reparos |
| --- | --: | --: | --: |
| 01 | 30 | 26 | 4 |
| 02 | 30 | 21 | 9 |
| 03 | 30 | 27 | 3 |
| 04 | 30 | 26 | 4 |
| 05 | 30 | 28 | 2 |
| 06 | 30 | 28 | 2 |
| 07 | 30 | 24 | 6 |
| 08 | 30 | 26 | 4 |
| 09 | 30 | 28 | 2 |
| 10 | 30 | 26 | 4 |
| 11 | 30 | 24 | 6 |
| 12 | 30 | 26 | 4 |
| 13 | 22 | 20 | 2 |
| **Total** | **382** | **330** | **52** |

Os artigos: 9.152 `certo`, 28 `errado`, 16 `dúvida`. 26 diplomas têm instruções em falta (quase todas anexos, quadros e mapas que só existem em PDF). Os `errado` mais frequentes são revogações aplicadas que não valiam para o texto: revogação "na parte aplicável a …" ou só do § único, revogação que só produz efeitos quando entrarem em vigor planos (artigo 53.º, n.º 2, do Decreto-Lei n.º 142/2008, em cinco diplomas), e um "(Corpo do artigo.)" copiado do alterador. São lições para as regras, não para o acervo. **Limite do método:** o verificador não vê o texto dos artigos iguais ao original, por isso uma instrução "em falta" sobre um deles pode ser falso alarme; os 26 deviam ser revistos antes de se concluir que as regras falharam.

**Dry-run no acervo** (`python consolidacao/acervo.py --dry-run`, com as saídas): **330 dos 382 da ronda 6 passariam** (mais os 2 dos 384 que são do piloto e já estão no acervo); nenhum recusado. Os 30 com dois ou mais alteradores passam ou não pelo mesmo critério dos outros.

**LLM nos lotes 001 a 010** (os de original com artigos identificados e mais citados; 400 diplomas). `llm.py --sessao --escala` deu os lotes; cada lote foi dividido em pedaços de até 150 a 220 mil caracteres e cada pedaço foi para um subagente (4 de cada vez), que escreveu uma linha por diploma; `llm.py --escala --importar` verificou-as letra a letra (respostas em `llm/escala/`); `juntar.py --escala` juntou-as ao consolidado que as regras tinham deixado.

| Lote | Sem problemas | Não aplicável | Com problemas |
| --- | --: | --: | --: |
| 001 | 14 | 25 | 1 |
| 002 | 14 | 24 | 2 |
| 003 | 15 | 22 | 3 |
| 004 | 12 | 22 | 6 |
| 005 | 10 | 28 | 2 |
| 006 | 13 | 26 | 1 |
| 007 | 15 | 23 | 2 |
| 008 | 17 | 23 | 0 |
| 009 | 8 | 30 | 2 |
| 010 | 10 | 28 | 2 |
| **Total** | **128** | **251** | **21** |

Dos 128 sem problemas, `juntar.py --escala` juntou 99 (`aplicado com LLM`, 85 deles parciais: a resposta deixou instruções por aplicar) e não juntou 29: 7 já tinham sido juntados com o LLM no piloto e 22 porque a resposta refaz um artigo que as regras já tinham alterado. O `não aplicável` dominante é "o pedido não traz o texto da nova redação" (a instrução só tem o proémio) e as alterações a quadros e anexos.

**Ronda 7** (os 99 juntados com o LLM, 4 lotes, `verificacao/entrada-piloto-7-lote-01..04.jsonl`, 22 pedaços, mesma verificação): **8 sem reparos e 91 com reparos** (88 com instruções em falta, 57 artigos `errado`, 13 `dúvida`). O rendimento do LLM em subagentes, neste estado do `juntar.py`, é baixo: das 400 entradas, 8 chegam ao acervo (2 %). Isto não contraria a ideia de usar o LLM, mas a forma: o pedido só leva os artigos que a instrução nomeia e, nos diplomas com muitas alterações, a resposta fica parcial; um diploma parcial não passa. Com a ronda 7, o `acervo.py --dry-run` passa a dar 338 aplicáveis (330 + 8).

**Para continuar:** os lotes 011 a 110 estão por fazer (os 011 a 042 são os restantes com artigos identificados, menos citados). O rendimento por lote nos primeiros dez foi de 8 a 17 respostas sem problemas, mas a ronda 7 sugere que antes de gastar mais convém tratar a causa dos parciais (pedir ao LLM todas as instruções do diploma, com o texto completo dos artigos, e juntar por artigo) e a dos conflitos com as regras (22 de 128).

### Bloco 2: LLM nos lotes 011 a 018 e ronda 8 (2026-10-29)

Mesmo processo dos lotes 001 a 010 (ver acima). `llm.py --importar` deu, por lote:

| Lote | 011 | 012 | 013 | 014 | 015 | 016 | 017 | 018 | Total |
| --- | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| Sem problemas | 11 | 13 | 12 | 13 | 7 | 9 | 6 | 16 | 87 |
| Não aplicável | 26 | 25 | 28 | 26 | 32 | 25 | 31 | 21 | 214 |
| Com problemas | 3 | 2 | 0 | 1 | 1 | 6 | 3 | 3 | 19 |

`juntar.py --escala` passou a ter 172 `aplicado com LLM` (139 parciais), 73 mais do que nos lotes 001 a 010. Ronda 8: esses 73 em 3 lotes (`verificacao/entrada-piloto-8-lote-01..03.jsonl`), verificados às cegas por 11 subagentes. **16 sem reparos** (22 %), 57 com reparos (53 com instruções em falta), 14 artigos `errado`, 4 `dúvida`. O `acervo.py --dry-run` dá agora 16 aplicáveis por aplicar (os 383 já aplicados estão no acervo).

### Bloco 3: LLM nos lotes 019 a 026 e ronda 9

| Lote | 019 | 020 | 021 | 022 | 023 | 024 | 025 | 026 | Total |
| --- | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| Sem problemas | 9 | 11 | 10 | 11 | 4 | 10 | 8 | 12 | 75 |
| Não aplicável | 28 | 28 | 27 | 28 | 35 | 29 | 32 | 26 | 233 |
| Com problemas | 3 | 1 | 3 | 1 | 1 | 1 | 0 | 2 | 12 |

`juntar.py --escala`: 233 `aplicado com LLM` (186 parciais), 61 novos. Ronda 9 (`verificacao/entrada-piloto-9-lote-01..03.jsonl`, 8 pedaços de verificação): **21 sem reparos** (34 %). O `acervo.py --dry-run` dá 21 aplicáveis por aplicar.

### Bloco 4: LLM nos lotes 027 a 042 (2026-10-29), ronda 10 por verificar

Respostas importadas (`llm/escala/`): 134 sem problemas nos lotes 027 a 042 (027: 6, 028: 11, 029: 7, 030: 5, 031: 10, 032: 6, 033: 9, 034: 2, 035: 6, 036: 9, 037: 10, 038: 12, 039: 6, 040: 9, 041: 12, 042: 14), 39 com problemas. `juntar.py --escala`: 339 `aplicado com LLM` (253 parciais), 106 novos. Ronda 10: `verificacao/entrada-piloto-10-lote-01..04.jsonl` (106 diplomas). **A verificação às cegas da ronda 10 não está concluída**: os subagentes escrevem em `verif10/` (fora do repositório, no scratchpad da sessão); falta `cegas_vista.py saida 10 PASTA` e o dry-run. Até lá, nada desta ronda é aplicável.


## Pedido completo ao LLM (`llm_completo.py`)

**Problema.** Nas rondas 7 a 9 só 8 a 34% dos diplomas juntados com o LLM passaram às cegas (8/99, 16/73, 21/61). A causa mais comum em 97 recusados das rondas 8 e 9: 62 só por "instruções em falta", 12 por isso e por artigos errados. As instruções em falta visavam artigos que ficaram iguais ao original porque o pedido de `llm.py` só leva os artigos que as instruções por aplicar nomeiam. Quase sempre são diplomas com vários alteradores em que um (ou mais) nunca foi lido por inteiro.

**Pedido novo.** Para cada diploma: o texto atual do original, artigo a artigo (com o que as regras aplicaram, assinalado), o texto de todos os alteradores por ordem de aplicação, e a ordem de ler todas as instruções dirigidas ao original e devolver os artigos que ainda faltam mudar, com o alterador de cada um. A verificação letra a letra aceita agora um parágrafo renumerado ("1 - …"). A resposta junta-se sobre o consolidado das regras sem recusar os artigos que elas já tinham tocado (o LLM viu a redação delas).

**Medição** (40 diplomas ao acaso entre os 97 recusados nas rondas 8 e 9, semente 1; 1 saltado por ter pedido acima de 150 mil caracteres; Opus, 2 diplomas por pedido):
- 39 de 40 juntados (1 era uma revogação do diploma inteiro, sem artigos); 22 com `nao_aplicavel` (anexos e quadros só em imagem, renumerações que o formato não exprime).
- 31 tinham consolidado diferente do já verificado (8 saíram iguais) e foram à ronda 11. Verificação às cegas: **19 de 31 sem reparos**.
- Rendimento: 19/40 = 48% sobre a amostra inteira, 19/39 = 49% sobre os juntados, 61% sobre os que mudaram. Antes, 8 a 34% (e 0% nesta amostra, que são todos recusados). A amostra é de diplomas já recusados, por isso o número mede o resgate, não o rendimento num lote novo.

**O que continua a travar:** quadros e anexos só em imagem (o verificador e o LLM não os veem), renumerações de artigos (o formato de resposta não apaga uma chave), e o verificador não vê o texto dos artigos iguais ao original, por isso hesita nas "instruções em falta" sobre eles.

### Blocos do pedido completo (rondas 12 a 15)

`llm_completo.py proximos N --saida F` escolhe os diplomas que ainda não passaram às cegas nem foram ao pedido completo (primeiro os já recusados, depois por citações; salta os de pedido acima de 150 mil caracteres); `pedidos` escreve os pedidos (2 diplomas cada), `importar` e `juntar` fazem o resto. A resposta pode ter `removidos` (chaves que desaparecem numa renumeração); as fórmulas finais que um artigo aditado deixa a meio passam para o último artigo da parte. Em `cegas_vista.py` a chave do artigo passou a ser o título sem a epígrafe, para uma epígrafe nova não parecer um artigo a mais e um a menos.

| Bloco | Ronda | Diplomas | Sem reparos às cegas | Sobre o bloco |
|---|---|---|---|---|
| Amostra dos recusados (8 e 9) | 11 | 40 | 19 | 48% |
| 1 (recusados por citações) | 12, 13 | 40 | 15 | 38% |
| 2 (só 14 novos; 26 repetidos por um erro, ver abaixo) | 14 | 14 | 6 | 43% |
| 3 | 15 | 40 | 14 | 35% |
| 4 | 16 | 40 | 20 | 50% |
| 5 | 17 | 40 | 16 | 40% |
| 6 | 18 | 40 | 15 | 38% |
| 7 | 19, 20 | 40 | 13 | 32% (68% dos 19 verificados) |
| 8 | 21 | 40 | 18 | 45% (72% dos 25 verificados) |
| 9 (todos os restantes de uma vez) | 22 | 1.152 respostas; 688 juntados e verificados | 465 | 68% dos 688 juntados (as 389 respostas "sem alterações" não têm nada a verificar) |

Total do pedido completo: 136 diplomas sem reparos em 334 respostas (bloco 4 incluído; `rendimento.py RONDA --ids FICHEIRO` mede um bloco; o prompt do verificador está em `verificacao/PROMPT-verificador.md`). **Erro corrigido a meio:** `proximos` não excluía os diplomas já feitos (o nome do ficheiro tem `_` onde o id tem `:`); o bloco 2 repetiu 26 do bloco 1. As respostas repetidas não foram importadas. A causa dos que ficam por passar: anexos e quadros só em imagem (`fora_dos_artigos`), revogação de diplomas inteiros que deixa os anexos, instruções ambíguas ("[Anterior alínea b)]" desfasadas), e o verificador sem o texto dos artigos iguais ao original. Faltam cerca de 1.400 diplomas na fila (`proximos`), e 107 foram saltados por tamanho.

### Os 93 diplomas por fazer (pedido acima de 150 mil caracteres)

Depois do bloco 9, `llm_completo.pendentes_do_pedido` só devolve estes 93: diplomas com artigos identificados, que ainda não passaram às cegas nem foram ao pedido completo, e cujo pedido (texto atual do original, artigo a artigo, mais o texto inteiro de todos os alteradores) passa dos 150 mil caracteres. A lista está em `llm/pedido-completo-grandes.tsv` (id, título, tamanho do pedido, número de alteradores, citações), do maior para o menor. O maior é a Lei n.º 39-B/94 (957 mil caracteres, 74 alteradores).

Por tamanho: 51 entre 150 e 250 mil, 28 entre 250 e 500 mil, 14 acima de 500 mil.

**Porque ficaram de fora:** um pedido destes não cabe no contexto de um subagente com margem para a resposta. Duas formas de os fazer, nenhuma tentada: (1) partir os alteradores em grupos e pedir ao LLM cada grupo sobre o texto que o grupo anterior deixou (o `juntar` já aceita várias passagens por diploma, mas o pedido não); (2) para os de 150 a 250 mil, subir `--max-chars` e usar um modelo com contexto maior. Em ambos a verificação às cegas é a mesma e `cegas_vista.py` já divide a vista por pedaços.

**Bloco 7: abaixo dos 35%, e porquê.** 21 dos 40 diplomas não deram nada a verificar: o LLM respondeu que não há instrução textual a aplicar (15 respostas "sem alterações", 3 recusadas na verificação letra a letra e mais as não juntadas). Os que mudam texto continuam a passar (13 de 19). A fila foi ficando cheia de diplomas em que tudo o que falta é quadros e anexos só em imagem, revogações condicionais, "na parte em que contrariem", prorrogações de prazo e referências a mudar de nome, que não se resolvem por texto. Depois de `_recolocar_assinaturas` corrigido (só move fórmulas curtas e com corpo antes), 5 diplomas foram a uma ronda 20 de repetição. Continuam a falhar os de chaves repetidas no texto atual (o artigo 7.º do DL 296-A/95 fica com o texto novo e o antigo).

### Os 93 grandes: passagens por grupos de alteradores (ronda 23)

Feito em 2026-11-11, sem alterar `data/`. As duas vias da secção anterior juntaram-se numa só, `llm_completo.py passagem IDS PASTA --max-chars N`. Um subagente lê bem um pedido de até ~320 mil caracteres: o teste foi um de 287 mil, com 362 artigos na resposta, e depois um de 319 mil. Por isso o limite subiu de 150 para 280 mil caracteres (320 mil na Lei n.º 30-G/2000). Quando o pedido inteiro não cabe, os alteradores partem-se em grupos, por ordem de aplicação. Cada passagem leva o texto que as anteriores deixaram, com os artigos que elas mudaram assinalados, e só os alteradores do seu grupo, numerados como no diploma inteiro.

- Por diploma, `PASTA/<id>/` guarda `estado.json`, `pedido-K.md` e as respostas `resposta-K.json` (ou `resposta-K.parteN.json`, quando a resposta é longa demais para uma escrita só).
- Cada vez que corre, `passagem` aplica as respostas que já há, faz a verificação letra a letra (contra o original, todos os alteradores e o texto atual) e escreve o pedido seguinte.
- Sem alteradores por pedir, funde as passagens: o texto de um artigo é o da última que o deu. Grava a resposta em `llm/completo/<id>.json`, e `juntar` trata-a como as outras.
- `importar` também aceita respostas em partes.
- `verificar._REVOGADO` passou a aceitar "2. (Revogado.)". Antes recusava o DL 413/71 só por isso.

**Bloco 1** (os 25 diplomas não orçamentais mais citados; um subagente Opus por passagem, até 6 de cada vez; verificação às cegas por Sonnet, uma vista por subagente, a maior com 588 mil caracteres):

| | Diplomas |
| --- | --: |
| Pedidos | 25 |
| Respondidos até ao fim | 22 (55 passagens; o DL 34-A/90 levou 6, o DL 46311 3) |
| Juntados | 16 |
| Sem reparos às cegas | **6** |

Rendimento: **6 em 25 (24%) sobre o bloco**, 6 em 16 (38%) sobre os juntados e verificados. Fica abaixo dos 35% sobre o bloco, por isso **o trabalho parou aqui** (a regra da tarefa). Os 6 sem reparos são os DL 519-A1/79, 497/85, 437/91 e 309/2001, o Decreto n.º 45266 e a Lei n.º 39/78. `acervo.py --dry-run` dá **6 aplicáveis**, mais 1.056 já aplicados.

Os 19 que não chegam ao acervo:

- **Não acabados (3).** O DL 38/2003 ficou parado: o original está mal segmentado (a chave "6.º" contém os artigos 7.º a 23.º e o anexo), e as 23 passagens, de 290 mil caracteres cada, seriam caras e quase certamente recusadas. A Lei n.º 30-G/2000 fez 7 das 8 passagens e mudou 5 artigos (os outros alteradores mexem nos códigos fiscais). A passagem 8 está escrita em `PASTA`, por responder. O DL 139-A/90 acabou e conta nos verificados.
- **Recusados na verificação letra a letra (5):** Decreto n.º 44623, DL 46311, DL 47743, DL 224-A/96 e DL 321-B/90. Um ou dois parágrafos que o LLM compôs (uma alínea renumerada, uma linha de um quadro) em vez de copiar.
- **Sem artigos a mudar (2):** a Lei n.º 65/98 (os alteradores mudam o Código Penal, não ela) e o DL 47/93 (as alterações já estavam no texto). Não há nada a verificar.
- **Com reparos às cegas (10):**
  - *Epígrafes de secção ou de título que mudam (5):* DL 376/87, 34-A/90, 361/78 e 139-A/90, e as fórmulas finais mudadas de sítio no Decreto n.º 47478. O formato de resposta só tem artigos. Uma instrução "a secção IV passa a designar-se…" fica por aplicar, e o diploma não passa.
  - *Erros do LLM (3):* o marcador "(Actual corpo do artigo.)" copiado no DL 158/96, uma alínea perdida no DL 227-B/2000 e um n.º 5 trocado no DR 42/83.
  - *Erro das regras (1):* no DL 34-A/90, o artigo 2.º "(Revogado.)" já vinha do texto que as regras deixaram.
  - *Outros:* artigos com a mesma chave no decreto preambular e no estatuto anexo (DL 139-A/90); um artigo aditado sem instrução (DL 361/78); uma anotação de quadro posta dentro do último artigo (DL 413/71); uma dúvida sobre uma revogação a prazo (DL 214/88).

**O que faria subir o rendimento:** deixar a resposta mudar epígrafes de secções, capítulos e títulos (5 dos 10 recusados às cegas); voltar a pedir, só sobre o parágrafo recusado, as 5 respostas que falharam a verificação letra a letra; e corrigir a segmentação das chaves repetidas (decreto preambular e estatuto anexo). Sem isto, os 52 diplomas não orçamentais que faltam (blocos 2 e 3) devem render à volta de um quarto.

**Bloco 2, começado antes de parar:** 7 dos 25 respondidos até ao fim e importados, todos sem problemas letra a letra: Lei n.º 3/2001, DR n.º 12/79, DLR n.º 19/2007/A, DL 633/76, DL 408/93, DLR n.º 2/2007/A e DLR n.º 4/2000/M. Nenhum foi juntado nem verificado às cegas. Os `pedido-1.md` dos 25 estão em `PASTA`. Dois subagentes avisaram do mesmo problema de chaves repetidas. No DLR n.º 2/2007/A, os artigos do apêndice II têm as chaves dos do regime do anexo I. No DL 408/93, o artigo 55.º vem partido em chaves que colidem com artigos verdadeiros. Convém corrigir antes de os juntar.

**Leis do orçamento:** não pedidas. A Lei n.º 30-G/2000 (reforma fiscal, não orçamento, mas do mesmo tipo) mostra o padrão: em 46 alteradores, só 2 mudaram o texto dela.

Os ficheiros de trabalho (pedidos, respostas por passagem, vistas da ronda 23) estão no scratchpad da sessão. O que fica no repositório é `llm/completo/<id>.json`, já fundido, e `verificacao/entrada-piloto-23-lote-01.jsonl` com a saída ao lado.



## Originais sem artigos: texto corrido por unidades (`llm_corrido.py`)

As rondas deste trabalho foram renumeradas ao juntar ao `main` (17 → 24, 18 → 25, 19 → 26, 20 → 27, 21 → 28, 22 → 29, 23 → 30, 24 → 31, 25 → 32, 26 → 33, 27 → 34, 28 → 35, 29 → 36, 30 → 37, 31 → 38, 32 → 39, 33 → 44, 34 → 45, 35 → 46, 36 → 47, 37 → 48, 38 → 49, 39 → 50, 40 → 51, 41 → 52), porque a frente B já usava os números 17 a 23 e o main já tinha as rondas 24 a 30; as rondas 40 a 43 são dos 93 grandes, por isso a ronda 33 deste trabalho, quando houver, passa a 44 para outros diplomas.

**Problema.** Dos 4.362 diplomas para o LLM, 2.697 têm um original sem artigos identificados (portarias "1.º, 2.º" em texto corrido, resoluções, despachos, declarações de retificação, bases). `juntar.py` e `llm_completo.py` recusam-nos ("original sem artigos: a resposta não tem onde encaixar").

**Método.** O original é um bloco de texto corrido dividido em **unidades**: os parágrafos separados por linha em branco, numerados de 1 a N (`itens` em `llm_corrido.py`; o texto volta a montar-se letra a letra). O pedido leva o original unidade a unidade (`{{7}}` antes de cada uma), o texto de todos os alteradores por ordem de aplicação (como no pedido completo) e a ordem de devolver só o que muda:

- `substituicoes`: `{de, ate, texto, alterador}`, as unidades de `de` a `ate` passam a ser `texto` (vazio se desaparecem);
- `insercoes`: `{depois_de, texto, alterador}`;
- `nao_aplicavel` e `instrucoes`, como no pedido completo.

Verificação letra a letra (`verificar_resposta`): as posições têm de existir e não se sobrepor, e cada parágrafo do texto novo vem de um alterador ou do original, com ou sem a numeração ("2.º ", "a) ", "1.º-A "). Um parágrafo do original com uma frase trocada ("onde se lê … deve ler-se …", um n.º que passa a ter a redação «…» com o seu número) não está inteiro em nenhum lado: passa se é parecido com a unidade que substitui e cada troca (as palavras novas, com a pontuação separada) está num alterador ou no original. O consolidado é o original com as unidades trocadas, cada troca seguida da nota "> Alterado pelo/a …" (o `cegas.py` tira-a); escreve `piloto/<caminho>.md`, `.alteracoes.json` e `llm/juntados-corrido.jsonl`. `llm/corrido/` guarda as respostas.

**Verificação às cegas.** `cegas.py --escala` lê `llm/juntados-corrido.jsonl` e marca a entrada com `modo: "corrido"`; os alteradores da entrada são todos os do pedido (`alteradores_vistos`), não só os que a resposta cita, para o verificador ver uma instrução que o LLM deixou cair. Em `cegas_vista.py` o modo corrido compara os parágrafos com `difflib`: cada troca é um `Trecho N` e a vista leva o **original inteiro** (pequeno: mediana 3 mil caracteres), por isso uma instrução que visava um parágrafo igual aparece em `instrucoes_em_falta`. O prompt do verificador tem uma secção final para este modo.

**Uso.**

```bash
cd consolidacao && export PYTHONPATH=../src
python llm_corrido.py amostra 40 --saida ids.txt     # ao acaso (semente 1); proximos N: por citações
python llm_corrido.py pedidos ids.txt PASTA --por-ficheiro 4
# um subagente por pedido escreve PASTA/resposta-NNN.json (REGRAS.md na mesma pasta)
python llm_corrido.py importar PASTA/resposta-*.json && python llm_corrido.py juntar
python cegas.py --escala --ronda N && python cegas_vista.py vistas N PASTA2   # ... saida N PASTA2
python rendimento.py N --ids ids.txt
```

### Amostra de 40 (ronda 24; no ramo de origem era a ronda 17)

40 diplomas ao acaso entre os 2.697 (semente 1; um saltado por pedido acima de 120 mil caracteres), 10 subagentes Opus, 4 diplomas cada.

| Passo | Diplomas |
|---|--:|
| Respostas importadas | 40 |
| Sem alterações possíveis (`nao_aplicavel`: anexos e quadros só em imagem, ou revogação do diploma inteiro) | 20 |
| Com mudanças, letra a letra aprovadas e juntadas | 20 (9 com instruções por aplicar) |
| **Sem reparos às cegas** (ronda 24) | **15** |

**Rendimento: 15/40 = 38% da amostra** (75% dos 20 verificados). Passa o limiar de 35% para alargar. Os 5 que falham têm todos a mesma causa: uma planta ou um quadro que só existe em imagem (`instrucoes_em_falta`). Os 20 sem alterações são, quase todos, diplomas cujos alteradores só trocam anexos em imagem ou o revogam por inteiro (Portarias 406/92, 694/90, 816/2002 e 964/2003, por exemplo, revogadas por outra portaria, embora o DRE as dê em vigor): não saem no acervo, mas ficam como informação para a vigência.

**Falha corrigida a meio.** A primeira verificação letra a letra exigia o parágrafo inteiro num alterador ou no original: recusou 9 das 20 respostas com mudanças, todas "n.º 2.º passa a ter a seguinte redação: «…»" (o parágrafo do original é "2.º " e o corpo novo) ou troca de uma frase dentro de um parágrafo. Com a troca verificada à parte (acima), as 20 passaram e a verificação às cegas confirmou-as. O que a verificação às cegas viu nos 5 reprovados: nenhum texto errado, só instruções sem efeito possível.

### Bloco 2 (ronda 25; no ramo de origem era a ronda 18)

120 diplomas por citações (`llm_corrido.py proximos 120`, 25 saltados por tamanho; ids em `llm/corrido-ids-bloco2.txt`), 15 subagentes Opus (30 pedidos). A primeira tentativa ficou a meio por limite de uso e foi repetida de raiz. Resultado: 63 sem alterações (anexos e quadros só em imagem, ou revogação total), 51 juntados, 6 recusados na verificação letra a letra (parágrafos "(Revogado.)" escritos pelo LLM que não existem no alterador). Ronda 18: 51 em 4 lotes, 18 pedaços, verificadores Sonnet às cegas. **39 sem reparos: 32 % do bloco de 120 (76 % dos 51 verificados)**, um pouco abaixo dos 38 % da amostra e do limiar de 35 %. `rendimento.py 18 --ids llm/corrido-ids-bloco2.txt`. Os 12 com reparos são quase todos instruções sobre anexos que só vêm em imagem.

### Bloco 3 (ronda 26; no ramo de origem era a ronda 19)

Mais 120 diplomas (`llm/corrido-ids-bloco3.txt`, de 2 537 candidatos; 34 saltados por tamanho), mesmo processo. 50 sem alterações, 61 juntados, 9 recusados. Ronda 19: 61 verificados às cegas, **35 sem reparos: 29 % do bloco (57 % dos verificados)**. O rendimento desce de bloco para bloco porque os diplomas vão por ordem de citações e os seguintes têm mais anexos em imagem e mais alteradores. Acumulado das rondas 17 a 19: **89 em 280 (32 %)**. Ficam cerca de 2 400 candidatos; a este ritmo cada bloco de 120 dá ~35 consolidações, abaixo do limiar de 35 % que fixámos, por isso não se alarga sem decisão.

### Bloco 4 (ronda 27; no ramo de origem era a ronda 20)

Mais 120 diplomas (`llm/corrido-ids-bloco4.txt`, de 2 417 candidatos; 35 saltados por tamanho). 47 sem alterações, 68 juntados, 5 recusados. Ronda 20: 68 verificados às cegas, **46 sem reparos: 38 % do bloco (68 % dos verificados)**. O rendimento oscila entre blocos (38, 32, 29, 38 %) conforme a proporção de quadros em imagem. Acumulado das rondas 17 a 20: **135 em 400 (34 %)**. Segue-se sempre para o bloco seguinte (cobertura); ficam cerca de 2 300 candidatos.

### Bloco 5 (ronda 28; no ramo de origem era a ronda 21)

Mais 120 diplomas (`llm/corrido-ids-bloco5.txt`, de 2 297 candidatos; 37 saltados por tamanho). 26 sem alterações, 91 juntados, 3 recusados. Ronda 21: 91 verificados às cegas, **71 sem reparos: 59 % do bloco (78 % dos verificados)**. O número alto vem de uma série de portarias de zonas de caça, quase todas só com a nova redação do n.º 1.º e o n.º 1.º-A, fáceis de verificar; não é de esperar que se mantenha. Os verificadores marcaram vários "dúvida" por efeitos implícitos (áreas, número de guardas) e contaram-se como reparos. Acumulado das rondas 17 a 21: **206 em 520 (40 %)**. Ficam cerca de 2 180 candidatos.

### Bloco 6 (ronda 29; no ramo de origem era a ronda 22)

Mais 120 diplomas (`llm/corrido-ids-bloco6.txt`, de 2 177 candidatos; 37 saltados por tamanho). 39 sem alterações, 76 juntados, 5 recusados. Ronda 22: 76 verificados às cegas, **59 sem reparos: 49 % do bloco (78 % dos verificados)**. Acumulado das rondas 17 a 22: **265 em 640 (41 %)**. Ficam cerca de 2 060 candidatos. Os reparos que se repetem: "dois guardas" passa a "um guarda" nas portarias de zonas de caça (instrução descritiva, sem redação literal, que o LLM não aplica) e alterações de área ou prazo sem redação nova.

### Bloco 7 (ronda 30; no ramo de origem era a ronda 23)

Mais 120 diplomas (`llm/corrido-ids-bloco7.txt`, de 2 057 candidatos; 37 saltados por tamanho). 20 sem alterações, 97 juntados, 3 recusados. Ronda 23: 97 verificados às cegas, **82 sem reparos: 68 % do bloco (85 % dos verificados)**. A subida (38, 32, 29, 38, 59, 49, 68 %) acompanha o peso de portarias de zonas de caça e de alterações com redação literal; os blocos de cursos e quadros de pessoal em imagem puxam para baixo. Acumulado das rondas 17 a 23: **347 em 760 (46 %)**. Ficam cerca de 1 940 candidatos.

### Bloco 8 (rondas 31 e 32; no ramo de origem eram as rondas 24 e 25)

Mais 120 diplomas (`llm/corrido-ids-bloco8.txt`, de 1 937 candidatos; 38 saltados por tamanho). 52 sem alterações, 68 juntados (65 na ronda 24 e 3 na ronda 25, porque o último agente respondeu depois de a ronda 24 estar aberta), 4 recusados. 68 verificados às cegas, **54 sem reparos: 45 % do bloco (79 % dos verificados)**. Acumulado das rondas 17 a 25: **401 em 880 (46 %)**. Ficam cerca de 1 820 candidatos. Lição: antes de `importar` conferir que há as 30 respostas do bloco.

### Bloco 9 (ronda 33; no ramo de origem era a ronda 26)

Mais 120 diplomas (`llm/corrido-ids-bloco9.txt`, de 1 817 candidatos; 39 saltados por tamanho). 48 sem alterações, 70 juntados, 2 recusados. Ronda 26: 70 verificados às cegas, **43 sem reparos: 36 % do bloco (61 % dos verificados)**. Menos que nos blocos 5 a 8: muitos "dúvida" por áreas e prazos alterados sem redação literal e anexos em imagem. Acumulado das rondas 17 a 26: **444 em 1 000 (44 %)**. Ficam cerca de 1 700 candidatos.

### Bloco 10 (ronda 34; no ramo de origem era a ronda 27)

Mais 120 diplomas (`llm/corrido-ids-bloco10.txt`, de 1 697 candidatos; 41 saltados por tamanho). 34 sem alterações, 86 juntados, 0 recusados. Ronda 27: 86 verificados às cegas, **68 sem reparos: 57 % do bloco (79 % dos verificados)**. Acumulado das rondas 17 a 27: **512 em 1 120 (46 %)**. Ficam cerca de 1 580 candidatos.

### Bloco 11 (ronda 35; no ramo de origem era a ronda 28)

Mais 120 diplomas (`llm/corrido-ids-bloco11.txt`, de 1 577 candidatos; 42 saltados por tamanho). 45 sem alterações, 70 juntados, 5 recusados. Ronda 28: 70 verificados às cegas, **51 sem reparos: 42 % do bloco (73 % dos verificados)**. Acumulado das rondas 17 a 28: **563 em 1 240 (45 %)**. Ficam cerca de 1 460 candidatos.

### Bloco 12 (ronda 36; no ramo de origem era a ronda 29)

Mais 120 diplomas (`llm/corrido-ids-bloco12.txt`, de 1 457 candidatos; 42 saltados por tamanho). 66 sem alterações (a maioria anexos ou quadros só em imagem, ou revogação total), 52 juntados, 2 recusados. Ronda 29: 52 verificados às cegas, **42 sem reparos: 35 % do bloco (81 % dos verificados)**. Acumulado das rondas 17 a 29: **605 em 1 360 (44 %)**. Ficam cerca de 1 340 candidatos. A fatia sem alterações cresce: os candidatos que restam, por ordem de citações, têm cada vez mais quadros em imagem.

### Bloco 13 (ronda 37; no ramo de origem era a ronda 30)

Mais 120 diplomas (`llm/corrido-ids-bloco13.txt`, de 1 337 candidatos; 43 saltados por tamanho). 45 sem alterações, 73 juntados, 2 recusados. Ronda 30: 73 verificados às cegas, **61 sem reparos: 51 % do bloco (84 % dos verificados)**. Acumulado das rondas 17 a 30: **666 em 1 480 (45 %)**. Ficam cerca de 1 220 candidatos.

### Bloco 14 (ronda 38; no ramo de origem era a ronda 31)

Mais 120 diplomas (`llm/corrido-ids-bloco14.txt`, de 1 217 candidatos; 43 saltados por tamanho). 52 sem alterações, 67 juntados, 1 recusado. Ronda 31: 67 verificados às cegas, **53 sem reparos: 44 % do bloco (79 % dos verificados)**. Acumulado das rondas 17 a 31: **719 em 1 600 (45 %)**. Ficam cerca de 1 100 candidatos.

### Bloco 15 (ronda 39; no ramo de origem era a ronda 32)

Mais 120 diplomas (`llm/corrido-ids-bloco15.txt`, de 1 097 candidatos; 44 saltados por tamanho). 50 sem alterações, 70 juntados, 0 recusados. Ronda 32: 70 verificados às cegas, **63 sem reparos: 52 % do bloco (90 % dos verificados)**. Acumulado das rondas 17 a 32: **782 em 1 720 (45 %)**. Ficam cerca de 980 candidatos. Nota: neste bloco o LLM tratou como "aplicáveis" várias trocas só das ligações de quadros que existem só em imagem; o verificador aceitou-as porque a ligação nova é a do alterador.

### Bloco 16 (ronda 44; no ramo de origem era a ronda 33)

Mais 120 diplomas (`llm/corrido-ids-bloco16.txt`, de 977 candidatos; 45 saltados por tamanho). 53 sem alterações, 67 juntados, 0 recusados. Ronda 33: 67 verificados às cegas, **53 sem reparos: 44 % do bloco (79 % dos verificados)**. Acumulado das rondas 17 a 33: **835 em 1 840 (45 %)**. Ficam cerca de 860 candidatos, mais os cerca de 45 por bloco que são grandes demais para o pedido de 120 000 caracteres.

### Bloco 17 (ronda 45; no ramo de origem era a ronda 34)

Mais 120 diplomas (`llm/corrido-ids-bloco17.txt`, de 857 candidatos; 46 saltados por tamanho). 59 sem alterações, 60 juntados, 1 recusado. Ronda 34: 60 verificados às cegas, **52 sem reparos: 43 % do bloco (87 % dos verificados)**. Acumulado das rondas 17 a 34: **887 em 1 960 (45 %)**. Ficam cerca de 740 candidatos.

### Bloco 18 (ronda 46; no ramo de origem era a ronda 35)

Mais 120 diplomas (`llm/corrido-ids-bloco18.txt`, de 737 candidatos; 46 saltados por tamanho). 61 sem alterações, 59 juntados, 0 recusados. Ronda 35: 59 verificados às cegas, **52 sem reparos: 43 % do bloco (88 % dos verificados)**. Acumulado das rondas 17 a 35: **939 em 2 080 (45 %)**. Ficam cerca de 620 candidatos.

### Bloco 19 (ronda 47; no ramo de origem era a ronda 36)

Mais 120 diplomas (`llm/corrido-ids-bloco19.txt`, de 617 candidatos; 46 saltados por tamanho). 65 sem alterações, 52 juntados, 3 recusados. Ronda 36: 52 verificados às cegas, **41 sem reparos: 34 % do bloco (79 % dos verificados)**. Acumulado das rondas 17 a 36: **980 em 2 200 (45 %)**. Ficam cerca de 500 candidatos.

### Bloco 20 (ronda 48; no ramo de origem era a ronda 37)

Mais 120 diplomas (`llm/corrido-ids-bloco20.txt`, de 497 candidatos; 46 saltados por tamanho). 74 sem alterações, 46 juntados, 0 recusados. Ronda 37: 46 verificados às cegas, **38 sem reparos: 32 % do bloco (83 % dos verificados)**. Acumulado das rondas 17 a 37: **1 018 em 2 320 (44 %)**. Ficam cerca de 380 candidatos.

### Bloco 21 (ronda 49; no ramo de origem era a ronda 38)

Mais 120 diplomas (`llm/corrido-ids-bloco21.txt`, de 377 candidatos; 47 saltados por tamanho). 63 sem alterações, 57 juntados, 0 recusados. Ronda 38: 57 verificados às cegas, **54 sem reparos: 45 % do bloco (95 % dos verificados)**. Acumulado das rondas 17 a 38: **1 072 em 2 440 (44 %)**. Ficam cerca de 257 candidatos.

### Bloco 22 (ronda 50; no ramo de origem era a ronda 39)

Mais 120 diplomas (`llm/corrido-ids-bloco22.txt`, de 257 candidatos; 47 saltados por tamanho). 55 sem alterações, 64 juntados, 1 recusado. Ronda 39: 64 verificados às cegas, **57 sem reparos: 48 % do bloco (89 % dos verificados)**. Acumulado das rondas 17 a 39: **1 129 em 2 560 (44 %)**. Ficam cerca de 137 candidatos.

### Bloco 23 (ronda 51; no ramo de origem era a ronda 40)

Últimos 89 diplomas que cabem no limite de 120 000 caracteres por pedido (`llm/corrido-ids-bloco23.txt`). 30 sem alterações, 58 juntados, 1 recusado. Ronda 40: 58 verificados às cegas, **56 sem reparos: 63 % do bloco (97 % dos verificados)**. Acumulado das rondas 17 a 40: **1 185 em 2 649 (45 %)**. Ficam 48 candidatos com pedidos acima de 120 000 caracteres.

### Bloco 24 (ronda 52; no ramo de origem era a ronda 41): diplomas grandes

Os 48 candidatos que ficaram por terem pedidos acima de 120 000 caracteres: 35 com até 270 000 caracteres, um diploma por pedido (`llm_corrido.py proximos 48 --max-chars 270000`, `pedidos … --por-ficheiro 1`; `llm/corrido-ids-bloco24.txt`). 12 sem alterações, 18 juntados, 5 recusados. Ronda 41: 17 verificados às cegas (uma vista por diploma), **9 sem reparos: 26 % do bloco (53 % dos verificados)**. Nos diplomas grandes o rendimento cai: muitas instruções por diploma, o modelo lê o pedido só em parte e basta um erro para o diploma chumbar. Acumulado das rondas 17 a 41: **1 194 em 2 684 (44 %; 80 % dos verificados)**.

**Cobertura.** Estão processados todos os candidatos com pedido até 270 000 caracteres. Ficam 13 diplomas entre 280 000 e mais de 1 000 000 de caracteres, que não compensam a este rendimento; se se quiserem, convém partir o pedido por alteradores e não pelo diploma inteiro.

### Correções depois do bloco 1 e rondas 40 e 41

Feito a pedido, antes do bloco 2, para atacar as causas da ronda 23. Nada em `data/`. As rondas são a 40 e a 41, porque a 24 a 28 estão ocupadas no `main`.

**O que mudou no código:**

- **Títulos de divisão.** O pedido mostra-os pela ordem do texto ("#### Título de divisão: …"). A resposta pode trazer `titulos` para mudar a designação ou a epígrafe de um título, ou para o eliminar. O texto novo passa pela verificação letra a letra. Um título repetido (o mesmo "TÍTULO II" em dois livros) é o primeiro a seguir ao anterior da lista. Mover e aditar títulos continua por exprimir.
- **Chaves repetidas.** O decreto que aprova e o estatuto que vem a seguir na mesma parte têm artigos com a mesma chave. A segunda ocorrência vem como "4.º#2" no pedido e na resposta (`texto.Corpo.artigo`). A remoção é por identidade.
- **Fórmulas finais.** `_recolocar_assinaturas` só move as fórmulas que, no original publicado, estão no último artigo da parte. Antes movia também as do decreto que aprova um regulamento, e punha-as no fim do regulamento. Isto mudou o texto de 29 juntados de rondas anteriores, que foram à ronda 40, e 12 deles passam agora.
- **Regras novas no pedido.** Um artigo que as regras deixaram errado pode ser corrigido. Uma revogação adiada para um facto futuro (um regulamento, um plano, uma portaria) não se aplica.
- `verificar._REVOGADO` aceita "1.ª (Revogada.)".

**O que se repediu:** 4 das 5 respostas recusadas letra a letra, ao mesmo subagente, só com o parágrafo recusado. O DL 46311 fica de fora, porque a última passagem adita uma tabela inteira, em anexo novo, que o formato não exprime. Refizeram-se de raiz, com o pedido novo, os 4 recusados por títulos (DL 376/87, 34-A/90, 361/78 e 139-A/90) e os 3 de chaves repetidas (DL 321-B/90, DLR n.º 2/2007/A e DL 408/93). Acabou-se a Lei n.º 30-G/2000 (8 passagens).

| Bloco 1 | Ronda 23 | Rondas 40 e 41 |
| --- | --: | --: |
| Juntados e verificados | 16 | 21 |
| Sem reparos às cegas | 6 | **8** |
| Sobre o bloco (25) | 24% | **32%** |
| Sobre os verificados | 38% | 38% |

Os 2 novos sem reparos são o DL 376/87 (o título da secção IV) e o Decreto n.º 47478 (as fórmulas finais no sítio). Ganhar 2 com 5 juntados a mais deixa o bloco **ainda abaixo dos 35%**, por isso o bloco 2 continua parado. Fica o que melhorou sem passar:

- **DL 139-A/90:** de 2 errados e 5 dúvidas para 0 errados e 2 dúvidas. As alíneas vêm com "..." de um diploma anterior que não está entre os alteradores.
- **DL 34-A/90:** 375 de 378 certos. Continua o artigo 2.º "(Revogado.)" das regras, que o LLM não desfez apesar da regra nova. Falta uma tabela que só existe em imagem.
- **DL 361/78:** falta um título aditado ("DIVISÃO XI — Funchal").
- **DL 321-B/90:** as chaves certas, mas um artigo com texto a mais e o capítulo V aditado.
- **DLR n.º 2/2007/A:** 25 de 25 certos, mas uma renomeação de hospitais não literal e um apêndice em imagem.

O DL 408/93 passou na ronda 41 e é do bloco 2, como o DR n.º 12/79. Dos 7 do bloco 2 já verificados, 2 estão sem reparos. Os outros 18 estão por pedir.

**Aplicáveis (`acervo.py --dry-run`): 19.** São 8 do bloco 1, 2 do bloco 2 e 9 juntados anteriores corrigidos pelas fórmulas finais. Há também 2 verificados sem reparos que o `acervo.py` recusa, porque o registo em `data/` já é o consolidado anterior: `pt:dre:643086:por` e `pt:dre:348524:por`. Aplicar a versão nova pede que o `acervo.py` saiba substituir um consolidado seu.

**O que ainda faria subir o rendimento:** aditar e mover títulos de divisão (DL 361/78, 321-B/90, 633/76); a fonte dos "..." quando a redação intermédia vem de um diploma que não está entre os alteradores; e anexos e tabelas, que só existem em imagem e continuam a ser a primeira causa nos diplomas grandes.

### Bloco 2 dos 93 grandes (rondas 40 a 43)

Feito a pedido, apesar de o bloco 1 estar abaixo dos 35%. Os 7 primeiros diplomas foram pedidos no formato antigo e verificados na ronda 40; 3 deles foram refeitos com chaves repetidas na ronda 41. Os outros 18 foram pedidos já no formato novo, com títulos de divisão e chaves "N.º#2", e verificados nas rondas 42 e 43. Tudo com um subagente Opus por passagem e verificadores Sonnet, até 6 de cada vez.

| Bloco 2 | Diplomas |
| --- | --: |
| Pedidos | 25 |
| Respondidos até ao fim | 24 |
| Juntados e verificados | 22 |
| Sem reparos às cegas | **5** |

Rendimento: **5 em 25 (20%) sobre o bloco**, 5 em 22 (23%) sobre os verificados. Os 5 sem reparos são o DR n.º 12/79, o DL 408/93, o DL 58/95, o DLR n.º 24/2002/M e o DL 431/80.

Os que não chegam:

- **Não pedido (1).** O DL 63-A/2013: o texto atual tem 294 mil caracteres e o pedido da primeira passagem 426 mil. O subagente esgotou o contexto antes de chegar ao alterador. O limite prático está entre 330 e 420 mil caracteres.
- **Sem artigos a mudar (2).** No DL 328/95, os 13 alteradores mudam o Código das Sociedades Comerciais e outros, não ele. Na Resolução n.º 1/2000/M, os 11 alteradores são **republicações inteiras do Regimento** (150 a 223 mil caracteres cada). O corte dos 60 mil caracteres deixa delas só as linhas que citam o original, e as instruções seguintes apontam para uma numeração que o pedido não tem. Para estes, o método certo é outro: partir da última republicação e aplicar só o que vem depois.
- **Com reparos às cegas (17):**
  - *Anexos e quadros que só existem em imagem:* Portarias 1212/2003 e 1463/2007, DL 233/2004 e DL 189/2002.
  - *Original incompleto no acervo:* os DL 189/2002 e 234/2001 não têm as bases do anexo. O LLM só pôde mudar epígrafes de capítulo.
  - *Títulos de divisão aditados ou deixados no corpo de um artigo:* os capítulos novos do Regulamento da CMVM n.º 2/2007 e do DL 249/2009. Na Resolução n.º 5/2012/M, duas "SUBDIVISÃO" que estavam dentro do corpo de um artigo perderam-se quando o artigo foi reescrito. Nos artigos 8.º a 10.º do DRR n.º 2/96/M, títulos que estavam no lugar das epígrafes foram eliminados.
  - *Redação de um diploma intermédio que não está entre os alteradores:* DL 233/2004, DLR n.º 4/2009/A e DLR n.º 2/2007/A.
  - *Epígrafes:* o DL 44329 tem 250 de 269 artigos certos (o código foi quase todo revogado pelo DL 224-A/96), mas 19 epígrafes diferem do original sem instrução.
  - *Erros do LLM:* uma subalínea mantida na Portaria 1212/2003, e as fórmulas finais repetidas no DLR n.º 19/2007/A.

**Mudou no código:** uma passagem posterior que reescreve ou revoga um artigo apaga os problemas letra a letra das passagens anteriores sobre esse artigo. Só conta o texto que fica.

**Os dois blocos juntos:** 13 de 50 sem reparos às cegas (26%). O `acervo.py --dry-run` dá **22 aplicáveis**: 8 do bloco 1, 5 do bloco 2 e 9 juntados anteriores corrigidos pelas fórmulas finais. Os 25 do bloco 3 estão por pedir. As 18 leis de orçamento continuam de fora.

### Bloco 3 dos 93 grandes (rondas 60 e 61)

Os 25 menos citados dos não orçamentais. Foram feitos a pedido, já no formato novo e com o mesmo processo do bloco 2. A ronda 60 era a 44 no ramo de origem: foi renumerada ao juntar ao `main`, porque a 44 do `main` é dos sem artigos. As seguintes começam no 61.

| Bloco 3 | Diplomas |
| --- | --: |
| Pedidos | 25 |
| Não pedidos (o pedido passa dos ~420 mil caracteres) | 3 |
| Respondidos | 22 |
| Sem artigos a mudar | 4 |
| Juntados e verificados | 18 |
| Sem reparos às cegas | **8** |

Rendimento: **8 em 25 (32%) sobre o bloco**, 8 em 18 (44%) sobre os verificados. Os 8 são o Despacho n.º 10393/2010, o DL 323/98, o Decreto n.º 492/73, a Portaria n.º 1238/2008, o DL 251-A/91, o DL 39/2004, o DRR n.º 37/2000/A e o DRR n.º 15-A/97/M.

- **Não pedidos (3):** o DL 55-A/2000 (o alterador sozinho tem 452 mil caracteres), o DL 202/2000 (o texto atual tem 487 mil) e o DLR n.º 5/2006/A (734 mil). Precisam de partir o texto atual, não só os alteradores.
- **Sem artigos a mudar (4):** os DL 206/90, 365/98 e 242/2006, e o DRR n.º 20/97/M. Os alteradores mudam outros diplomas ou só os anexos.
- **Com reparos às cegas (10):**
  - *Bases do anexo em falta no original:* o DL 87-A/2000, o 323-G/2000 e o 142-A/2001, como os do bloco 2. São concessões de autoestradas cujo original no acervo só tem os artigos do decreto e os títulos dos capítulos.
  - *Anexos só em imagem ou fora do texto:* as Portarias n.os 1137-B/2008 e 1462/2007, e os DL 195/2000 e 114/2002.
  - *Troca genérica de designações:* «Direcção-Geral de Viação» passa a «Instituto da Mobilidade e dos Transportes, I.P.» em todo o diploma, nos DL 114/2002 e 291/2000. Para o verificador é uma instrução. Feita palavra a palavra, falha a verificação letra a letra e dá erros de concordância ("a Instituto"). O formato não tem forma segura de a aplicar.
  - *Outros:* o DL 47611 tem a tabela de emolumentos omitida em vez de "(Revogado.)", e o DL 204/97 um artigo com texto de uma alteração intermédia.

**Os três blocos juntos:** **21 de 75 sem reparos às cegas (28%)**, 21 de 61 (34%) sobre os verificados. O `acervo.py --dry-run` dá **30 aplicáveis**: 21 dos 93 grandes e 9 juntados anteriores corrigidos pelas fórmulas finais. Ficam por fazer:

- **As 18 leis de orçamento**, que não foram pedidas.
- **Os 4 com pedido grande demais**, a fazer partindo o texto atual: os DL 63-A/2013, 55-A/2000 e 202/2000, e o DLR n.º 5/2006/A.
- **O DL 38/2003**, com o original mal segmentado.
- **As causas que dependem do acervo e não do LLM:** anexos em imagem, bases em falta e republicações cortadas pelos 60 mil caracteres.

## Os 18 grandes demais (ronda 70)

Feito em 2026-11-11 no ramo `claude/frente-b-gigantes-a1e827`, sem alterar `data/` nem o `acervo.py`. São os 18 do ponto 3 de "O que falha e porquê":

- 13 sem artigos com um pedido acima de 270 mil caracteres;
- 4 dos 93 grandes em que o próprio texto é grande demais;
- o DL 38/2003.

As 18 leis de orçamento continuam de fora.

| | Diplomas |
| --- | --: |
| Não pedidos: o DRE consolida-os noutro registo | 2 |
| Sem nada a aplicar: só quadros em imagem | 3 |
| Juntados e verificados às cegas | 13 |
| Sem reparos às cegas (`acervo.py --dry-run`: aplicáveis) | **5** |
| Com reparos | 8 |

Rendimento: **5 dos 18** (28%), ou 5 dos 13 verificados (38%). Os 5 são o DL 43335, o DL 38/2003, o DL 63-A/2013, a Portaria 721-A/2000 e a RCM 81-A/2026. O `acervo.py --dry-run` dá-os como aplicáveis; aplicam-se a partir do `main`.

### Método (`llm_gigantes.py`)

O original divide-se em **unidades**, os parágrafos, como em `llm_corrido.py`. Isto vale também para os 5 que têm artigos (DL 63-A/2013, 55-A/2000, 202/2000, 38/2003 e DLR 5/2006/A). Uma alteração a um número de um artigo de 2.000 linhas é assim uma troca de uma unidade, e a resposta não tem de reescrever o artigo inteiro.

- **Passagens.** Os alteradores partem-se em grupos, por ordem de data, até ~230 mil caracteres por pedido. Cada passagem pede só o seu grupo, sobre o texto que as anteriores deixaram, com as unidades renumeradas. O DL 44278 levou 4 passagens (206 alteradores), o DL 44305 4, o DL 45399 3, e o DL 38/2003, a RCM 27/2000 e a Portaria 413-E/98 2 cada.
- **Texto atual em ficheiro.** Acima de 90 mil caracteres, o texto atual vai num ficheiro à parte (`texto-K.md`, com `{{N}}` antes de cada unidade). O pedido leva só um índice dos títulos, e o subagente procura no ficheiro as unidades que as instruções visam. O mesmo se faz com um alterador acima de 150 mil caracteres: o DL 214-C/2015 tem 452 mil.
- **Alteradores grandes pelo nome.** Acima de 100 mil caracteres, um alterador vai só com os artigos que mencionam o original, pelo título ou pelo nome do que ele aprova ("Código do Imposto Profissional", "Estatuto Judiciário", tirados do texto ou do sumário). Antes só se procurava o título.
- **Copiar do alterador.** Uma resposta pode mandar copiar um intervalo de parágrafos de um alterador (`"copiar": {"alterador", "primeiro", "ultimo"}`) em vez de os escrever. É o programa que copia, letra a letra. Foi assim que entrou a republicação das bases do DL 55-A/2000: 967 unidades de uma vez.
- **Verificação letra a letra por passagem.** Cada parágrafo novo vem de um alterador, do original ou do texto que as passagens anteriores deixaram, que já passou a mesma verificação. Há três extensões:
  - "Art. 20.º - (Revogado.)" e "§ 1.º (Revogado.)" contam como revogações;
  - um título "###### Artigo N.º — Epígrafe" posto no formato do original verifica-se pelas duas partes;
  - uma troca enorme verifica-se palavra a palavra. É o caso da unidade 697 do DL 202/2000, uma linha única de 393 mil caracteres. Cada sequência nova tem de ser feita de pedaços de 4 ou mais palavras seguidas numa fonte, e uma palavra ou um número trocados sozinhos não passam.
- **Fusão.** No fim, as passagens fundem-se numa resposta sobre as unidades do original, com o alterador de cada troca, em `llm/corrido/<id>.json`. `juntar` escreve o consolidado com `llm_corrido._junto` e põe a linha em `llm/juntados-corrido.jsonl`, que o `cegas.py` e o `acervo.py` já leem.
  - A verificação da resposta fundida contra o original fica em `avisos` e não recusa o diploma. Um parágrafo mudado por dois alteradores já não se parece com o original, mas cada passo foi verificado.
  - As respostas e o estado de cada passagem estão em `llm/gigantes/<id>/`. Os pedidos e os textos intermédios refazem-se com `passagem`.
- **Verificação às cegas por passagem** (`vistas` e `saida`; prompt em `verificacao/PROMPT-verificador-passagens.md`). Uma vista com todos os alteradores não cabe num verificador. Cada passagem tem a sua vista, com:
  - os alteradores dessa passagem;
  - o texto antes dela, num ficheiro quando é grande;
  - os trechos que mudam entre o texto antes e o texto depois, comparados por `difflib` sem nada da resposta. Um trecho longo vai num ficheiro, e a vista leva o princípio e o fim.

  Ao todo, 23 vistas e 23 verificadores Sonnet. A `saida` junta as passagens na linha do diploma. A chave de cada trecho é "Passagem K, Trecho N". A entrada é a de `cegas.linha_de`, por isso o `acervo.py` compara o consolidado como nas outras rondas.

**Um erro apanhado e corrigido:** a nota "> Alterado pelo/a …" no fim do texto. Quando a última troca cai no fim do original, a nota fica sem uma quebra de linha depois dela. O `cegas.py` e o `acervo.py` só a tiram com essa quebra, por isso a nota entrava no texto verificado às cegas. O `juntar` destes 18 acaba agora o ficheiro com "\n". Três diplomas foram verificados de novo: o DL 63-A/2013 passou outra vez, e os DL 55-A/2000 e 202/2000 já tinham reparos de outra ordem. **Fica por fazer:** em rondas anteriores, 138 diplomas foram verificados com essa nota no texto. Os que entraram em `data/` têm-na no fim, como texto. Não mexi neles, porque o `acervo.py` está a ser corrigido noutra sessão. Aviso também que `llm_corrido.py juntar`, se voltar a correr, reescreve os consolidados destes 18 sem a quebra de linha final: os 3 afetados deixariam de bater com a entrada.

### DL 38/2003: o parser

O registo tem `###### Artigo` só nos artigos 1.º a 6.º. Do 7.º ao 23.º e no anexo, os artigos estão em texto corrido. O artigo 6.º cita a nova redação de artigos do Código do Registo Predial e falta o "»" que a fecha. O parser da fase 3 (`_parse_headings`) achava que o resto do diploma estava todo dentro de aspas, e o "artigo 6.º" engolia os artigos 7.º a 23.º e o anexo.

**A correção** está em `src/leis_portugal/domain/articles.py`. Quando há aspas abertas e aparecem seguidos um título de divisão em texto corrido ("CAPÍTULO IV"), a sua epígrafe e "Artigo N.º" sozinho na linha, as aspas fecham-se se N é o número a seguir ao último artigo do diploma. Há uma exceção: se N é também o número a seguir ao último artigo citado, é a nova redação que continua, e as aspas ficam abertas. Foi essa guarda que afastou um falso positivo no DRR 13/2002/M.

**Antes e depois**, em todo o `data/` (340.556 registos): mudam **10**, todos com a mesma falha. Um artigo que engolia o resto passa a estar dividido nos artigos seguintes. São eles:

- Decreto 43367: 65 → 103 artigos;
- Decreto do Governo 2/84: 2 → 73;
- DL 38/2003: 6 → 23;
- DL 1/2008: 20 → 239;
- DL 97/2020: 23 → 47;
- Lei 127-B/97: 39 → 59;
- Lei 16/2008: 536 → 609;
- Lei 119/2019: 24 → 26;
- RCM 137/96: 4 → 34;
- Aviso do BdP 10/2011: 2 → 21.

Sem a guarda, mudavam também o DL 28/2010, o DRR 21/2022/A e o DRR 13/2002/M (este, um falso positivo); com ela, ficam como estavam.

**A correção ficou no ramo `claude/frente-b-gigantes-a1e827` e não entrou no `main` (11/11/2026).** Com ela, o `acervo.py --dry-run` deixava de reconhecer como já aplicados 1.262 dos 2.318 diplomas consolidados (de 2.318 para 1.056 "já aplicados", 60 "aplicáveis" e 3 recusados), porque as entradas das verificações às cegas foram feitas com o parser antigo. Com o parser do `main`, os 5 aplicáveis desta ronda (o DL 38/2003 incluído) passam e nenhum outro muda. Para a fazer entrar é preciso medir, diploma a diploma, o que muda na divisão em artigos e refazer as entradas afetadas. O texto original desta secção dizia: Os testes passam. Na consolidação nada muda para os outros diplomas, por construção: `texto.dividir` não usa este parser, e `com_titulos` só serve originais sem nenhum `###### Artigo`. O DL 38/2003 foi feito por unidades, como os outros: o artigo 1.º tem 2.350 linhas de novas redações do CPC.

### Os 18, um a um

**Aplicáveis (5):**

- **RCM 81-A/2026:** a Declaração de Retificação 18/2026/1 troca o Despacho 4223/2025 pelo 675/2026 em 59 unidades. Às cegas: 59 certos.
- **DL 43335:** o art. 67.º é revogado pela Lei 20/2023, e o art. 46.º das Condições Gerais tem a redação do DL 116/87. O art. 49.º fica o original, porque o Acórdão 33/88 declarou inconstitucional a redação do DL 296/82.
- **DL 38/2003:** só o DL 199/2003 muda o próprio texto (os n.os 3 a 5 do art. 21.º). Os outros 22 alteradores alteram o CPC e os outros códigos, não ele.
- **DL 63-A/2013:** a Lei 16/2015 revoga o Regime Jurídico dos OIC aprovado em anexo, que fica "(Revogado.)". O decreto-lei fica como estava.
- **Portaria 721-A/2000:** a Portaria 161/2014 revoga a parte da 1.ª instância, e a Portaria 170/2009 muda o Ministério Público da Relação de Coimbra. As alterações dos outros alteradores à 1.ª instância ficam absorvidas pela revogação.

**Com reparos (8)**, todos com os trechos `certo` ou quase. O que os trava é sobretudo o que não está no texto:

- **DL 44278 (Estatuto Judiciário):** 206 alteradores em 4 passagens, 498 de 500 trechos certos. Um errado: o art. 318.º perdeu o "3. ..." que o DL 414/73 manda manter. Uma dúvida: se o DL 414/73 substitui o art. 49.º inteiro. Há ainda entradas dos mapas VIII ("Cascais", "Barreiro") que não existem no texto antes.
- **DL 44305 (Código do Imposto Profissional):** 133 trechos certos. Um erro do LLM: a alínea b) do § 2.º do art. 1.º não recebeu a redação do DL 209/75. O resto são tabelas de taxas e de actividades que só existem em PDF.
- **DL 45399 (Código do Imposto Complementar):** 165 trechos certos. Faltam só as tabelas do art. 33.º, do art. 94.º e do art. 15.º-A, que só existem em PDF.
- **Decreto 46982:** 25 certos. Falta a tabela de vencimentos do Decreto 268/70, que só existe em PDF.
- **DL 740/74:** 7 certos. Falta a redação dos arts. 3.º e 4.º do Regulamento de Instalações Colectivas, que o DR 90/84 remete para o seu próprio regulamento anexo, que não vem no pedido.
- **DL 55-A/2000:** 117 certos (a republicação). Em 3 pontos, a republicação "com a redação atual" difere do articulado do DL 214-C/2015: o n.º 7 da base IX e duas epígrafes de secção. É a mesma decisão por tomar que no DLR 13/98/A: conta a republicação ou as instruções?
- **DL 202/2000:** 44 de 45 certos. Faltam os anexos que o art. 4.º do DL 224/2003 dá numa redação que não está no acervo, o n.º 6.6 do anexo 24.º e quadros em imagem.
- **RCM 27/2000:** 6 certos. O verificador conta como em falta as nomeações, exonerações e "considerar alterado … em consonância", que não dão texto novo. O consolidador tratou-as como alterações não textuais. Decidir se uma nomeação muda o texto de uma resolução que nomeia é leitura jurídica, por isso fica com reparos.

**Sem nada a aplicar (3):** em todos, as instruções visam quadros ou tabelas que só existem em imagem ("ver quadro no documento original").

- RCM 92/2000: a tabela 4.8;
- DLR 5/2006/A: o quadro n.º 1;
- Portaria 413-E/98: o quadro do anexo, nas 34 alterações.

**Não pedidos (2):**

- **DL 394-B/84 (Código do IVA):** o próprio registo diz "Consulte a versão consolidada … na republicação publicada no anexo IV ao Decreto-Lei n.º 102/2008". O DL 102/2008 já está no acervo como "Versão consolidada pelo DRE" (consolidada a 2026-05-25).
- **DL 400/82 (Código Penal):** o registo remete para a republicação em anexo ao DL 48/95, que está no acervo como "Versão consolidada pelo DRE" (2026-08-24).

Consolidar os originais de 1982 e 1984, com 68 e 137 alteradores, duplicaria por LLM um texto que o DRE já dá consolidado. O certo é que o registo original aponte para o consolidado do DRE, e não refazê-lo.

**Ficheiros:**

- `llm_gigantes.py`;
- `llm/gigantes-ids.txt` (os 16 pedidos);
- `llm/gigantes/<id>/` (o estado e as respostas de cada passagem);
- `llm/corrido/<id>.json` (as respostas fundidas);
- `piloto/…` (os consolidados);
- `verificacao/entrada-piloto-70-lote-01.jsonl` e `saida-piloto-70-lote-01.jsonl`;
- `verificacao/PROMPT-verificador-passagens.md`.

As vistas e as respostas dos verificadores ficaram no scratchpad da sessão. `vistas` refá-las a partir da entrada e das respostas.
