# Segunda leitura jurídica dos que passaram às cegas (ronda 115)

Prompt dado a cada subagente (Opus) da segunda leitura da camada 1, como a do bloco 3 (`README.md`, secção 8).

Recebes um ficheiro `segunda-NN.md` com um ou mais diplomas. Cada diploma traz a vista da verificação às cegas: o texto dos diplomas que o alteram, os artigos que mudaram (original e consolidado) e o que quem consolidou diz que não aplicou. Traz também as relações do registo no DRE (`relationships`). Um verificador às cegas deu todos os artigos como `certo` e não viu instruções em falta. Tu fazes uma leitura de jurista, à procura do que essa verificação letra a letra não apanha.

## O que procurar

1. **Leitura jurídica das instruções.** Uma revogação «com excepção de…» ou «na parte em que…» aplicada como total. Uma alínea substituída por inteiro quando a instrução só mudava uma sub-alínea, ou o contrário. Uma renumeração mal feita. Uma instrução de um alterador que um alterador posterior já tinha tornado sem objeto.
2. **Retificações.** Uma declaração de retificação nas `relationships` (`corrected_by`) que não está entre os diplomas que alteram e cujo texto devia estar aplicado.
3. **Revogações que faltam.** Uma relação `repealed_by` ou um diploma do acervo que revogue artigos do original e não esteja aplicado. Podes procurar no acervo, em `/Users/barroso/Documents/Seamless Doubt/leis-portugal/.claude/worktrees/consolidacao-bloco-3-7237a2/data/`, com `grep -rl` pelo número do diploma. Lê só os ficheiros de que precisas.
4. **Justificações aceites que não o deviam ser.** Uma instrução que o verificador deu por justificada (imagem, outro diploma, não textual) e que muda o texto deste diploma.

A vigência não decide aqui. Um diploma revogado por inteiro, caducado ou substituído pode ter o texto certo. Se vires uma prova de que já não vigora, diz-o em `vigencia`, com a prova, mas não lhe dês `reparos` por isso.

## Veredicto por diploma

- `certo`: não encontraste nada que mude o texto;
- `reparos`: há pelo menos um problema de texto (diz qual, com o artigo e o texto certo quando o sabes);
- `duvida`: há uma questão de texto que não consegues decidir (diz porquê).

Na dúvida, `duvida`.

## Saída

`segunda-NN.json`, na mesma pasta: uma lista, um objeto por diploma, assim:

```json
{"id": "<id>", "veredicto": "certo|reparos|duvida", "problemas": ["…"], "vigencia": null}
```

`vigencia` é `null`, ou `{"conclusao": "revogado|caducado|substituido|outro", "prova": "…"}`. Responde a todos os diplomas do ficheiro. Confirma com python que o JSON é válido.
