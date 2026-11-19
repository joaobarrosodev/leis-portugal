# Leitor: segunda leitura de vigência

Prompt dado a cada subagente leitor de `consolidacao/vigencia_llm.py`: Sonnet na primeira leitura e Opus nas dúvidas.

Tens um ficheiro `entrada-NN.jsonl` (ou `duvidas-entrada-NN.jsonl`), com um diploma por linha. O DRE dá todos como em vigor (`legal_status`). Cada diploma traz:

- o título, o sumário, a classe (`caca`, `organicas`, `um_so_ano`) e a data;
- nas concessões de caça, o prazo do texto (`prazo_anos`, `fim_estimado`, `renovavel`);
- as relações do registo no DRE (`relacoes`);
- o início e o fim do texto;
- `mencoes_no_acervo`: outros diplomas do acervo que o citam perto de um verbo de vigência, ou que têm o mesmo número de processo, com o id, o título, a data e o trecho.

Para cada diploma, decide se **já não vigora**, só com o que está na entrada:

- **`nao_vigora`**, só quando há uma prova na entrada. Exemplos:
  - uma menção que o revoga, extingue, faz caducar ou substitui por inteiro («É revogada a Portaria n.º X», «é extinta a zona de caça … (processo n.º N)», «são extintos o … e o …», «a presente portaria substitui a Portaria n.º X»);
  - uma relação `repealed_by` ou `amended_by` cujo rótulo diz isso.

  Com `nao_vigora` dás:
  - `prova`: o `id` dessa menção, ou o `alvo` da relação;
  - `motivo`: uma frase que completa «O DRE dá-o como em vigor, mas …», por exemplo «foi revogada pela Portaria n.º 506/2018» ou «a zona de caça foi extinta pela Portaria n.º 222/2000».
- **`vigora`**, quando a entrada mostra que continua: uma renovação recente, uma alteração recente, menções que o aplicam.
- **`duvida`**, em tudo o resto, que é a maioria. Alguns casos:
  - sem prova;
  - uma revogação só de uma parte;
  - um serviço que parece extinto, mas sem o diploma que o extingue na entrada;
  - um prazo acabado sem prova de que não se renovou;
  - um regime de um só ano que já passou, mas sem ato que o diga.

  Um regime de um só ano que já passou («para o ano de 1992», «campanha de 1993») vigora só nesse ano. Mesmo assim, sem um ato expresso na entrada é `duvida`, e o motivo diz o ano.

Não uses o que sabes fora da entrada: uma marca sem prova na entrada não conta. Na dúvida, `duvida`.

## Saída

Um ficheiro `resposta-NN.jsonl` (ou `duvidas-resposta-NN.jsonl`), na mesma pasta e com o mesmo NN, com uma linha por diploma da entrada e todos os diplomas:

```json
{"id": "<id do diploma>", "veredicto": "nao_vigora|vigora|duvida", "prova": "<id ou alvo, só em nao_vigora>", "motivo": "<uma frase>"}
```

Escreve o ficheiro com um script ou com Write. Confirma que é JSON válido, linha a linha, e que tem todos os ids.

## Os incertos (`incertos-entrada-NN.jsonl`)

Aqui a classe (`caca`, `organicas`, `um_so_ano`, `cursos_pre_bolonha`) é um palpite das regras, de certeza baixa. Para cada diploma, diz também se a confirmas:

- `classe_confirmada`: `true` se o diploma é mesmo da classe, `false` se não é. Por exemplo: não é uma concessão de caça, não é uma orgânica, não é um regime de um só ano, não cria nem regula um curso ou grau do ensino superior.
- Nos `cursos_pre_bolonha`, o veredicto pode ser também `regime_anterior`. Usa-o quando o diploma cria ou regula um curso, grau ou plano de estudos do ensino superior anterior ao DL 74/2006. Não se afirma que caducou. Se não é um curso, `duvida` com `classe_confirmada: false`.
- Nas outras classes, as regras de cima não mudam: `nao_vigora` só com prova na entrada.
- Um regime de um só ano que já passou leva `duvida`. Diz em `ano` o ano a que se aplica, quando o título, o sumário ou o texto o dizem («para o ano de 1992» → 1992).

Saída: `incertos-resposta-NN.jsonl`, com uma linha por diploma:

```json
{"id": "…", "veredicto": "nao_vigora|vigora|duvida|regime_anterior", "classe_confirmada": true, "ano": null, "prova": "…", "motivo": "<uma frase>"}
```
