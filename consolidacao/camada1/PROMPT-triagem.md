# Triagem às cegas: o alterador muda o texto deste diploma?

Prompt dado a cada subagente verificador (Sonnet) de `consolidacao/camada1.py` (passo `entrada-triagem`).

Lês um ficheiro `entrada-NN.jsonl`, com um item por linha. Cada item é um diploma (o **original**) e uma parte dos diplomas que o DRE diz que o alteram (`alteradores`). Traz:

- `titulo`, `data`, `sumario`, `titulos_do_original` (os títulos de artigos, capítulos e anexos), `inicio_do_original` e `imagens_no_original` (quantos anexos ou quadros só existem em imagem);
- para cada alterador: `alterador`, `data`, `rotulos_dre` (o que o DRE escreveu sobre a relação; muitas vezes «Última alteração registada na importação inicial», que não diz nada) e `texto`. Com `completo: false`, o texto é só o início, os artigos que mencionam o original e janelas à volta das outras menções. Com `texto: null`, o acervo não tem o texto (`sem_texto` diz porquê) e só tens o `sumario` e o rótulo.

Não sabes o que outros programas ou pessoas disseram sobre estes pares. Decide tu.

## Para cada alterador, um veredicto

- `altera_texto`: dá ao original uma instrução que muda as palavras do texto e que se pode aplicar: nova redação de um artigo, número, alínea, anexo ou quadro em texto; aditamento; revogação de um artigo, número ou alínea; retificação («onde se lê … deve ler-se …»); renumeração. Lista cada instrução em `instrucoes`, curta («nova redação do art. 5.º, n.º 2»; «revoga o art. 12.º»).
- `so_imagem`: muda um quadro, mapa, tabela, planta ou anexo do original, mas o texto novo só vem em imagem («[(ver documento original)](…)») ou num quadro «anexo ao presente diploma» que não está no texto.
- `outro_diploma`: a instrução é dirigida a outro diploma, e o original só aparece porque lhe deu a redação («o artigo 5.º do Decreto-Lei X, na redação dada pelo [original]»), porque é citado numa lista («alterado pelos Decretos-Leis n.os …»), ou porque o alterador muda um diploma que o original aprovou e que tem número próprio.
- `nao_textual`: menciona o original sem lhe mudar as palavras: «ao abrigo do», regulamenta, prorroga um prazo sem dar nova redação, mantém em vigor, suspende, muda a designação de um serviço sem nova redação, fixa valores ou quotas, declara a inconstitucionalidade de uma norma sem a eliminar do texto, aprova um quadro de pessoal ou um regulamento à parte.
- `revoga_o_original`: revoga o original por inteiro (diz-o com a frase do alterador em `motivo`). Uma revogação «na parte em que contrarie» não conta: é `nao_textual`.
- `nao_menciona`: não menciona o original, nem pelo número nem por uma descrição inequívoca.
- `sem_texto`: só quando `texto` é null. Diz em `motivo` o que o sumário ou o rótulo deixam perceber («o sumário diz que altera o quadro de pessoal»; «nada se percebe»).
- `duvida`: não consegues decidir com o que tens (por exemplo, o texto vem cortado e a instrução pode estar fora do que vês). Diz porquê.

Cuidados:
- O alvo de uma instrução é o diploma que ela nomeia logo antes («o n.º 2 do artigo 3.º da Portaria n.º X»). Um alterador pode alterar vários diplomas: só contam as instruções deste original.
- «A referida portaria», «o citado decreto-lei» contam se o início do alterador mostra que é este original.
- Uma lei que aprova um código ou estatuto em anexo e um alterador que muda esse código: se o código não tem diploma próprio, o alvo é o original.
- Na dúvida entre `altera_texto` e outro veredicto, `duvida`.

## Saída

`saida-NN.jsonl`, na mesma pasta e com o mesmo NN, uma linha por item:

```json
{"id": "<id do original>", "parte": "<parte do item>", "alteradores": [{"id": "<id do alterador>", "veredicto": "altera_texto|so_imagem|outro_diploma|nao_textual|revoga_o_original|nao_menciona|sem_texto|duvida", "motivo": "<uma frase, com as palavras do alterador quando ajudam>", "instrucoes": ["…"]}]}
```

`instrucoes` só em `altera_texto` (nos outros, `[]`). Um elemento por alterador do item, pela ordem do item. Lê o ficheiro com python, um item de cada vez. No fim, confirma com python que cada linha é JSON válido e que respondeste a todos os itens e a todos os alteradores.
