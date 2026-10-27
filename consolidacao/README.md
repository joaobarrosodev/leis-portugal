# Consolidação: texto em vigor dos diplomas alterados

Piloto da fase 2 do [plano para um RAG jurídico fiável](../PLANO-RAG.md): obter o texto em vigor dos diplomas que o DRE dá como alterados mas não consolida, aplicando as alterações publicadas. Nada aqui altera `data/`; a aplicação ao acervo vem depois da verificação às cegas e de um merge.

## Resultado em resumo

Dos 671 diplomas do alvo, só 123 têm, no diploma que os altera, instruções de alteração dirigidas a eles. Em 498 a relação `amended_by` do DRE não corresponde a nenhuma alteração ao texto. As regras aplicaram 22 diplomas por inteiro e todos passaram a verificação automática. 84 ficam para o LLM ou para o parser da fase 3, e 17 foram revogados por inteiro, embora o DRE os dê como em vigor.

| Estado | Diplomas | O que quer dizer |
| --- | --: | --- |
| Aplicado por regra | 22 | Todas as instruções aplicadas e a verificação automática passou. Vão à verificação às cegas. |
| Para o LLM | 84 | Há instruções que as regras não aplicam com segurança; 71 destes têm o original sem artigos identificados. |
| Revogado por inteiro | 17 | O diploma que "altera" revoga o original. O DRE dá-o como em vigor. |
| Sem alteração textual | 498 | O diploma que altera não dá nenhuma instrução ao original (ver abaixo). |
| Sem texto | 50 | O original só tem PDF ou metadados (47), ou o diploma que altera não está no acervo ou não tem texto (3). |
| **Total** | **671** | |

Não houve chave da API da Anthropic no ambiente, por isso **não se usou LLM**: 0 pedidos, 0 tokens, 0 $. Para os 84 pendentes, a estimativa é de 84 pedidos, cerca de 527 mil tokens de entrada e 181 mil de saída: **cerca de 5,7 $ com a Claude Opus 5.5** (2,9 $ com a Sonnet 5.5). Os números saem de `medir.py` (`medicao.json`) sobre o export de 26/10/2026.

### A relação `amended_by` do DRE não quer dizer "alterou o texto"

O achado com mais peso no plano: 498 dos 671 diplomas (74%) não têm alteração textual a aplicar. Confirmou-se à mão em ~60 casos. A relação do DRE junta coisas muito diferentes:

- **303: o original só aparece numa lista ou numa remissão**, quase sempre "alterado pelos Decretos-Leis n.os …, 45/2007, …". O diploma que altera muda **outro** diploma, na redação que o original lhe tinha dado. O DRE regista a relação no original quando devia registá-la no outro.
- **179: o diploma que altera cita o original sem lhe dar instruções.** São portarias feitas "ao abrigo do" original, prorrogações de prazos, "mantido em vigor", ratificações, extinções de serviços, alterações de mapas orçamentais.
- **16: o diploma que altera nem sequer menciona o original.**

410 destas 498 relações têm o rótulo "Última alteração registada na importação inicial", sem data. Para o RAG, isto quer dizer que boa parte dos "27.086 alterados sem consolidação" pode ter o texto original como texto em vigor. Antes de o assumir, falta medir quantos têm outra alteração que o DRE não registou (fase 3).

### Revogados que o DRE dá como em vigor

17 originais são revogados por inteiro pelo diploma que os "altera" (por exemplo, o Decreto-Lei n.º 90/90 pela Lei n.º 54/2015, ou o Decreto-Lei n.º 162/2019 pelo Decreto-Lei n.º 15/2022). Para a vigência da fase 3, a ligação certa é `repealed_by`. Há ainda 14 revogações "com exceção dos artigos …" ou "na parte que …", que ficam nos pendentes.

### O que as regras aplicaram

Nos 22 diplomas aplicados por regra houve 75 alterações:

| Regra | Alterações |
| --- | --: |
| Revogação de artigo | 32 |
| Substituição com "[...]" (junta número a número) | 15 |
| Revogação de número ou alínea | 11 |
| Substituição integral da redação | 8 |
| Aditamento de artigo | 8 |
| Substituição parcial (só um número ou alínea) | 1 |

### Porque é que 84 ficam para o LLM

| Motivo | Instruções |
| --- | --: |
| Redação nova sem aspas «» (diplomas antigos: "Art. 3.º O n.º 6 do artigo 15.º … passa a ter a seguinte redacção:" e o texto segue sem aspas) | 34 |
| Original sem artigos identificados: as regras não sabem onde aplicar | 20 |
| Revogação com exceções ou só em parte | 14 |
| Anexo do original não identificado (o original tem vários anexos ou nenhum `## Anexo`) | 9 |
| Instrução de outro tipo ("passa a designar-se", "é suprimido", "é aditada uma alínea") | 7 |
| Alvo da nova redação não identificado | 5 |
| Retificações que não se aplicam com segurança | 5 |
| Revogações com um alvo que a regra não lê | 5 |
| Revogação do que o original aprovou em anexo | 1 |

O maior bloqueio são os **71 originais sem títulos `###### Artigo`** (portarias numeradas "1.º", "2.º" e diplomas antigos com "Art. 1.º" no texto). O parser da fase 3 resolve a maior parte. Depois disso, voltar a correr `consolidar.py` deve passar uma parte destes para as regras.

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
5. **Revisão à mão**: as diferenças dos 22 consolidados foram lidas. Apanharam dois erros que a verificação deixava passar e que estão corrigidos: uma alínea "e)" lida como a conjunção "e", que substituía o n.º 2 inteiro em vez da alínea e), e uma retificação já presente no texto do acervo, que dava ";;". A segunda verificação acima (o resto do artigo não muda) entrou por causa do primeiro.

A amostra de 50 diplomas (`consolidar.py --amostra 50 --semente 1`) serviu para afinar o método antes de correr os 671. Só 8 dos 50 tinham instruções; o resto do afinamento fez-se sobre os 671.

## Ficheiros

| Ficheiro | O que é |
| --- | --- |
| `selecionar.py` | Seleção dos 671 a partir de `exports/leis-portugal.sqlite` (num worktree, usa o export da pasta principal) |
| `texto.py` | Leitura dos registos: corpo, artigos, referências a diplomas |
| `alteracoes.py` | Leitura das instruções do diploma que altera |
| `aplicar.py` | Aplicação por regras |
| `verificar.py` | Verificação automática e comparação com a republicação |
| `consolidar.py` | Corre tudo e escreve os resultados |
| `llm.py` | Pedidos ao LLM para os pendentes (`--estimar` sem chave, `--executar` com chave) |
| `cegas.py` | Entrada da verificação às cegas |
| `medir.py` | Números do piloto (`medicao.json`) |
| `selecao.jsonl` | Os 671, com o diploma que altera, os rótulos do DRE e os artigos que mencionam o original |
| `resultados.jsonl` | Estado e motivo por diploma |
| `pendentes.jsonl` | As instruções por aplicar, com o texto dos artigos do original em causa |
| `piloto/<caminho do registo>.md` | O texto consolidado (só os 22 aplicados por regra) |
| `piloto/<caminho do registo>.alteracoes.json` | Um registo por alteração: artigo, operação, regra, texto antes e depois, excerto que a justifica, método |
| `verificacao/entrada-piloto.jsonl` | Entrada da verificação às cegas |
| `medicao.json` | Os números acima |

Para repetir, a partir da raiz do worktree:

```bash
cd consolidacao && PYTHONPATH=../src python selecionar.py && python consolidar.py && python cegas.py && python medir.py
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

**Regras da verificação:**

1. Ler o diploma que altera e listar **todas** as instruções dirigidas ao original: substituições, aditamentos, revogações, retificações, renumerações, alterações de epígrafe. Uma instrução que altera **outro** diploma ("o artigo 5.º do Decreto-Lei X, na redação dada pelo [original]") não é do original e não se aplica.
2. Para **cada artigo** do texto consolidado, dar um veredicto:
   - `certo`: se a instrução o altera, o texto é a nova redação **letra a letra** como está no diploma que altera, com o texto original no lugar de cada "[...]"; se não o altera, é igual ao original letra a letra;
   - `errado`: qualquer diferença de substância (palavra, número, número ou alínea a mais ou a menos, epígrafe errada, artigo que devia estar revogado ou não). Escrever o texto esperado;
   - `dúvida`: a instrução é ambígua ou depende de outro diploma. Explicar porquê.
   As diferenças de grafia, pontuação ou espaços que já estão no diploma que altera não são erro: o consolidado copia o diploma que altera, mesmo com gralhas.
3. Um artigo revogado fica com o título, a epígrafe e o corpo "(Revogado.)". Um número revogado fica "N - (Revogado.)", e uma alínea "a) (Revogada.)".
4. Por diploma, listar à parte: **instruções em falta** (do passo 1, sem efeito no consolidado), **artigos a mais ou a menos** e **texto fora dos artigos** (preâmbulo, títulos de capítulo) que tenha mudado.
5. Não usar outras fontes (DRE, internet, outros registos): só os três textos da entrada.
6. Não ler `piloto/*.alteracoes.json`, `resultados.jsonl` nem o código desta pasta antes de terminar.

**Saída:** `verificacao/saida-piloto.jsonl`, uma linha por artigo, `{"id", "artigo", "veredicto": "certo" | "errado" | "dúvida", "motivo", "texto_esperado"}`, e uma linha por diploma, `{"id", "instrucoes_em_falta": [...], "artigos_a_mais": [...], "artigos_em_falta": [...], "fora_dos_artigos": "..."}`.

**Depois:** cada `errado` ou `dúvida` e cada instrução em falta é revista à mão (ou numa terceira sessão) e, se for o caso, corrige-se a regra e volta a correr-se tudo. Um diploma só entra no acervo quando todos os artigos estão `certo`.

## Limites e próximos passos

- **Data de entrada em vigor:** o consolidado é o texto depois da alteração, tal como foi publicada. As alterações com entrada em vigor diferida ou com efeitos retroativos não estão modeladas (é trabalho da fase 3).
- **Grafia:** o texto novo vem do diploma que altera e o resto do original, por isso o mesmo artigo pode ter grafias diferentes ("actividade" e "atividade"), como nas consolidações oficiais.
- **Notas e ligações:** os parágrafos retificados perdem as ligações Markdown. O cabeçalho YAML dos consolidados é próprio do piloto (`consolidacao.estado: por verificar às cegas`); o formato final para `data/` decide-se no merge.
- **O que é preciso para o resto:** (1) a verificação às cegas dos 22; (2) uma chave da API (`ANTHROPIC_API_KEY`) para correr `llm.py --executar` nos 84 pendentes, cerca de 6 $; (3) o parser de artigos da fase 3, para os 71 originais sem artigos identificados; (4) decidir o que fazer com os 498 sem alteração textual e os 17 revogados (vigência e relações, fase 3).
- **Os outros 1.468 diplomas com 10 ou mais citações** têm mais de uma alteração. O método serve na mesma (aplicar as alterações por ordem de data), mas a amostra mostra que é preciso filtrar primeiro as relações que não são alterações textuais.
