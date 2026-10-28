# Consolidação: texto em vigor dos diplomas alterados

Piloto da fase 2 do [plano para um RAG jurídico fiável](../PLANO-RAG.md): obter o texto em vigor dos diplomas que o DRE dá como alterados mas não consolida, aplicando as alterações publicadas. Só `acervo.py` altera `data/`, e só com os consolidados verificados às cegas (ver "Aplicação ao acervo").

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

**18.918 diplomas (74%) deixam de precisar do aviso "texto original; alterado por…"**: nenhum dos alteradores lhes dá uma instrução dirigida ao texto, como nos 500 do piloto (75%). Nos 2.145 com 10 ou mais citações são 1.345. Por motivo (o mais frequente entre os alteradores de cada diploma): 8.454 só aparecem numa lista ou remissão ("alterado pelos Decretos-Leis n.os …" de outro diploma), 7.532 são citados sem instruções (ao abrigo de, prorrogações, quadros de pessoal, exonerações) e 2.920 nem são mencionados (muitos são relações do DRE a outro diploma: a Lei n.º 37/2010 tem como "alteradores" os orçamentos que mudam a Lei Geral Tributária na redação que ela lhe deu). Uma amostra de 12 lida à mão não tinha nenhuma alteração textual.

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

### Dry-run da ronda 6 no acervo

`python consolidacao/acervo.py --dry-run --supor-verificados`, sem as saídas da verificação (ainda não existem): dos 382 diplomas da ronda 6, 382 passam nos controlos técnicos (o consolidado é o da entrada, o original em `data/` é o verificado, o histórico reproduz o consolidado), 30 deles com dois ou mais alteradores; nenhum é recusado. Sem `--supor-verificados`, `Aplicados: 0`: nenhum dos lotes tem `saida-piloto-6-lote-NN.jsonl`. Os outros 2 dos 384 aplicados por regra são do piloto, com o mesmo texto, já no acervo.
