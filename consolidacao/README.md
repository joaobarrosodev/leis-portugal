# Consolidação: texto em vigor dos diplomas alterados

Piloto da fase 2 do [plano para um RAG jurídico fiável](../PLANO-RAG.md): obter o texto em vigor dos diplomas que o DRE dá como alterados mas não consolida, aplicando as alterações publicadas. Nada aqui altera `data/`; a aplicação ao acervo vem depois da verificação às cegas e de um merge.

## Resultado em resumo

Dos 671 diplomas do alvo, só 123 têm, no diploma que os altera, instruções de alteração dirigidas a eles. Em 500 a relação `amended_by` do DRE não corresponde a nenhuma alteração ao texto. As regras aplicaram 27 diplomas por inteiro, e todos passaram a verificação automática. Na verificação às cegas, 23 têm todos os artigos `certo`, 1 está numa 3.ª ronda e 3 têm uma dúvida por decidir. 72 ficam para o LLM, 5 falharam a verificação e 17 foram revogados por inteiro, embora o DRE os dê como em vigor.

| Estado | 1.ª corrida | Com o parser da fase 3 | Depois da verificação às cegas | O que quer dizer |
| --- | --: | --: | --: | --- |
| Aplicado por regra | 22 | 28 | 27 | Todas as instruções aplicadas e a verificação automática passou. Vão à verificação às cegas. |
| Para o LLM | 84 | 73 | 72 | Há instruções que as regras não aplicam com segurança. |
| Falhou a verificação | 0 | 5 | 5 | As regras aplicaram tudo, mas a verificação automática não passou. Vão também para o LLM. |
| Revogado por inteiro | 17 | 17 | 17 | O diploma que "altera" revoga o original. O DRE dá-o como em vigor. |
| Sem alteração textual | 498 | 498 | 500 | O diploma que altera não dá nenhuma instrução ao original (ver abaixo). |
| Sem texto | 50 | 50 | 50 | O original só tem PDF ou metadados (47), ou o diploma que altera não está no acervo (3). |
| **Total** | **671** | **671** | **671** | |

Não houve chave da API da Anthropic no ambiente, por isso **não se usou LLM**: 0 pedidos, 0 tokens, 0 $. Para os 77 pendentes (72 para o LLM e 5 que falharam a verificação), a estimativa é de 77 pedidos, cerca de 247 mil tokens de entrada e 180 mil de saída: **cerca de 4,6 $ com a Claude Opus 5.5** (2,3 $ com a Sonnet 5.5). Também se pode fazer numa sessão do Claude, sem a API: a entrada está em `llm/entrada-sessao.jsonl` (ver "Pendentes numa sessão do Claude"). Os números saem de `medir.py` (`medicao.json`), sobre o export de 26/10/2026.

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

Revisão à mão de cada `errado`, `dúvida` e nota por diploma:

- **Lei Orgânica n.º 4/2004: erro real, apanhado pelo verificador.** Os 7 `errado` e 11 das `dúvida` são deste diploma. A Lei Orgânica n.º 4/2014 adita artigos à Lei n.º 30/84, "alterada pelas Leis n.os 4/95, …, e pela Lei Orgânica n.º 4/2004". A regra só tirava a primeira menção da lista "alterada pelas …", por isso o "e pela Lei Orgânica n.º 4/2004" no fim contava como o diploma alterado. Os 7 artigos aditados à Lei 30/84 foram parar ao corpo da 4/2004. Agora toda a lista conta como diplomas que deram redação a outro (`_INICIO_CADEIA` e `_CADEIA` em `alteracoes.py`). A 4/2004 passou a "sem alteração textual", que é o certo: a LO 4/2014 altera a Lei 30/84 e não a lei que a republicou. A mesma correção tirou a Lei n.º 3/2010 dos pendentes: era só mencionada em "o Decreto-Lei n.º 32/2003, alterado pelo … e pela Lei n.º 3/2010", que é revogado.
- **Decreto-Lei n.º 94/91: erro real, apanhado pelo verificador.** As fórmulas finais ("Visto e aprovado…", "Promulgado…", as assinaturas) estavam no bloco do último artigo e desapareceram quando o artigo 8.º foi revogado. Agora ficam quando um artigo é reescrito (`_formulas_finais` em `aplicar.py`, com a mesma deteção de assinaturas do parser da fase 3). O consolidado mudou, por isso vai a uma 3.ª ronda (`entrada-piloto-3.jsonl`).
- **Decreto-Lei n.º 96/87 e Decreto-Lei n.º 163-A/2000: erro real, que o verificador não apanhou.** São as revogações "na parte em que contrariem" do DL 16/2013, que já tinham saído dos aplicados. O verificador deu `certo` a todos os artigos: lê a revogação ao pé da letra, como as regras liam. As regras da verificação passam a dizer que uma revogação condicional não se aplica (regra 3).
- **Decreto Legislativo Regional n.º 13/98/A, artigo 17.º: fica por decidir.** Nenhuma instrução altera o artigo, e o consolidado mantém o original. Mas a republicação em anexo ao diploma que altera, "com as alterações ora introduzidas", tem outra redação ("regime jurídico" em vez de "diploma"). As regras seguem as instruções. Uma republicação que difere das instruções num artigo não alterado é uma decisão a tomar: conta a republicação, ou só as instruções?
- **Lei n.º 10/2012, artigo 3.º: fica por decidir.** O artigo 45.º da Lei n.º 26/2016, que dá a nova redação, foi depois alterado pela Lei n.º 68/2021. O texto do registo da 26/2016 no acervo já é o consolidado. A redação aplicada pode, por isso, ser a de 2021 e não a de 2016, e a nota de alteração só nomeia a 26/2016.
- **Decreto-Lei n.º 513-M/79, artigo 19.º: fica por decidir.** A revogação produz efeitos "com a entrada em vigor do Código" (dos Regimes Contributivos), que foi adiada por leis posteriores. O texto está certo. O que fica por modelar é a data (é trabalho da fase 3).
- Nas outras 22 notas por diploma, nada em falta. Na 2.ª ronda, o verificador confirmou a normalização dos títulos nos 8 diplomas.

**Ficam 23 diplomas com todos os artigos `certo` (16 da 1.ª ronda e 7 da 2.ª).** O DL 94/91 está na 3.ª ronda, e há 3 com uma dúvida por decidir.

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
| `cegas.py` | Entrada da verificação às cegas (`--ronda 1` ou `--ronda 2`) |
| `medir.py` | Números do piloto (`medicao.json`) |
| `selecao.jsonl` | Os 671, com o diploma que altera, os rótulos do DRE e os artigos que mencionam o original |
| `resultados.jsonl` | Estado e motivo por diploma |
| `pendentes.jsonl` | As instruções por aplicar, com o texto dos artigos do original em causa |
| `piloto/<caminho do registo>.md` | O texto consolidado (só os 27 aplicados por regra) |
| `piloto/<caminho do registo>.alteracoes.json` | Um registo por alteração: artigo, operação, regra, texto antes e depois, excerto que a justifica, método |
| `verificacao/entrada-piloto.jsonl` | Entrada da 1.ª ronda da verificação às cegas (os 22 da 1.ª corrida, como estavam) |
| `verificacao/entrada-piloto-2.jsonl` | Entrada da 2.ª ronda: os 8 aplicados por regra que não estão na 1.ª |
| `verificacao/entrada-piloto-3.jsonl` | Entrada da 3.ª ronda: o DL 94/91, que mudou depois da 1.ª |
| `verificacao/saida-piloto*.jsonl` | Saídas das rondas (escritas pela sessão que verifica) |
| `llm/entrada-sessao.jsonl` | Os 77 pendentes, prontos para uma sessão do Claude |
| `medicao.json` | Os números acima |

Para repetir, a partir da raiz do worktree:

```bash
cd consolidacao && export PYTHONPATH=../src && python selecionar.py && python consolidar.py && python cegas.py --ronda 2 && python llm.py --sessao && python medir.py
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

**Saída:** `verificacao/saida-piloto.jsonl` (na 2.ª ronda, `verificacao/saida-piloto-2.jsonl`), uma linha por artigo, `{"id", "artigo", "veredicto": "certo" | "errado" | "dúvida", "motivo", "texto_esperado"}`, e uma linha por diploma, `{"id", "instrucoes_em_falta": [...], "artigos_a_mais": [...], "artigos_em_falta": [...], "fora_dos_artigos": "..."}`.

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

A sessão escreve uma linha por diploma, `{"id", "artigos": [{"chave", "epigrafe", "texto"}], "nao_aplicavel"}`, num ficheiro como `llm/saida-sessao.jsonl`. `python llm.py --importar llm/saida-sessao.jsonl --modelo <modelo da sessão>` passa cada resposta pela mesma verificação das respostas da API: cada parágrafo tem de estar, letra a letra, no diploma que altera ou no original. Grava o resultado em `llm/<id>.json`, com os problemas que encontrar. As respostas aprovadas ainda não se juntam ao consolidado: esse passo, e a verificação às cegas delas com outro modelo, fazem-se quando houver respostas.

## Limites e próximos passos

- **Data de entrada em vigor:** o consolidado é o texto depois da alteração, tal como foi publicada. As alterações com entrada em vigor diferida ou com efeitos retroativos não estão modeladas (é trabalho da fase 3).
- **Grafia:** o texto novo vem do diploma que altera e o resto do original, por isso o mesmo artigo pode ter grafias diferentes ("actividade" e "atividade"), como nas consolidações oficiais.
- **Notas e ligações:** os parágrafos retificados perdem as ligações Markdown. O cabeçalho YAML dos consolidados é próprio do piloto (`consolidacao.estado: por verificar às cegas`); o formato final para `data/` decide-se no merge.
- **O que é preciso para o resto:**
  1. a 3.ª ronda da verificação às cegas (DL 94/91) e decidir as 3 dúvidas (republicação que difere das instruções, alterador alterado depois, revogação com data diferida);
  2. os 77 pendentes, numa sessão do Claude a partir de `llm/entrada-sessao.jsonl` ou com uma chave da API (`llm.py --executar`, cerca de 4,6 $);
  3. uma regra para a redação nova sem aspas (34 instruções);
  4. decidir o que fazer com os 500 sem alteração textual e os 17 revogados (vigência e relações, fase 3).
- **Os outros 1.468 diplomas com 10 ou mais citações** têm mais de uma alteração. O método serve na mesma (aplicar as alterações por ordem de data), mas a amostra mostra que é preciso filtrar primeiro as relações que não são alterações textuais.
