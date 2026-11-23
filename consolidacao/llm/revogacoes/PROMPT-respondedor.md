# Respondedor: revogações registadas só como `repealed_by`

Prompt dado a cada subagente respondedor (Opus) de `consolidacao/revogacoes.py`.

Tens um ficheiro `entrada-NN.jsonl`, com um consolidado por linha. Cada item traz:

- `texto_em_vigor`: o texto consolidado de hoje, em linhas numeradas («L123: …»), em Markdown cru. Quando `texto_parcial` é true, vêm só as linhas relevantes, os títulos e o fim do texto. As linhas que não vês existem, mas não são para mexer.
- `alteradores_candidatos`: os diplomas que revogam partes deste consolidado, por ordem de data. Cada um traz:
  - `rotulos_dre`: o que o DRE escreveu, por exemplo «Revogados os arts. 41.º a 43.º pelo DL …»;
  - `data_dre`;
  - `texto`: o texto do diploma que revoga. Quando é grande, só os artigos que mencionam este consolidado.

Para cada diploma que revoga, lê no `texto` a disposição que revoga este consolidado e aplica-a, ou diz porque não se aplica. O rótulo do DRE ajuda a encontrar a disposição, mas o que manda é o texto.

## O que se aplica

Todas as trocas levam `com_ligacoes: true`. O `texto_atual` é a linha L exatamente como está, e o `texto_novo` é Markdown cru. Uma troca por linha.

- **Artigo revogado por inteiro.** O título (`###### Artigo N.º — Epígrafe`) fica igual. A primeira linha do corpo passa a `(Revogado.)` e as outras linhas do corpo passam a `""`. As notas «> Alterado pelo/a …» que já lá estão ficam.
- **Número revogado.** A linha do número passa a `N - (Revogado.)`, com o número como está no texto («2 -», «2.», «§ 2.º»). As linhas de continuação desse número passam a `""`.
- **Alínea revogada.** A linha passa a `a) (Revogada.)`.
- **Capítulo, secção ou parte revogados.** Cada artigo dessa divisão fica revogado como acima. Os títulos de divisão ficam.
- **Revogação com exceções** («revogados os arts. 28.º a 208.º, com exceção do art. 182.º-A»). Revogas o que a disposição revoga e deixas o resto.
- **Data de efeitos.** Quando a revogação só produz efeitos numa data («com efeitos a partir de 1 de janeiro de 2010», «a partir da entrada em vigor do decreto regulamentar…» com a data no texto), põe `"efeitos": "AAAA-MM-DD"`. Sem data própria, `"efeitos": null`.

## O que não se aplica

Vai para `nao_aplicadas`, com um motivo final:

- `já aplicada`: o texto já está «(Revogado.)» ou a revogação já lá está por outra via;
- `revogação condicional`: «na parte em que contrarie», «na parte aplicável a…», «no que se refere a…», sem dizer que palavras saem;
- `efeito adiado`: a revogação depende de um facto futuro sem data;
- `outro diploma`: a disposição revoga outro diploma, e o DRE ligou-a mal a este;
- `sem texto`: o diploma que revoga não traz a disposição no texto que tens;
- `não se aplica: <porquê>`: qualquer outro caso, com a razão (por exemplo, o artigo não está no texto atual).

Na dúvida, não apliques e escreve o motivo.

## Saída

Um ficheiro `resposta-NN.jsonl`, na mesma pasta e com o mesmo NN, com uma linha por consolidado da entrada:

```json
{"id": "<id do consolidado>", "alteradores": [{"alterador": "<id do diploma que revoga>", "efeitos": null, "trocas": [{"linha": 123, "com_ligacoes": true, "texto_atual": "…", "texto_novo": "…", "nota": "<o que revoga e onde>"}], "nao_aplicadas": [{"instrucao": "<resumo curto>", "motivo": "…"}]}]}
```

Cada diploma que revoga tem de aparecer, mesmo com `trocas` vazio. Escreve o ficheiro com python, copiando o `texto_atual` da entrada. Confirma com python:

- que cada linha é JSON válido;
- que cada `texto_atual` é, carácter a carácter, a linha L da entrada;
- que estão todos os diplomas que revogam.

## Ronda r3

Os lotes `entrada-r3-NN.jsonl` são pares a que já se respondeu uma vez. Ou a verificação às cegas não deu `certo`, ou o par ficou sem resposta. Cada diploma que revoga traz um `reparo` com o veredicto e o motivo do verificador. Lê-o primeiro. Diz o que faltou provar ou o que estava errado, por exemplo: a disposição não se via no texto, a data de efeitos, o motivo de «já aplicada» não confirmado, uma exceção não respeitada.

Nesta ronda o diploma que revoga vem mais completo (até 100 000 caracteres). O `texto_em_vigor` vem inteiro quando cabe, e então `texto_parcial` é false.

Responde de novo a cada par, com as mesmas regras. Quando o motivo é «já aplicada», diz na instrução a linha L onde já está «(Revogado.)». A `efeitos` só leva uma data quando a disposição dá à revogação uma data própria: a entrada em vigor diferida do diploma que revoga não conta. Escreve `resposta-r3-NN.jsonl`, com o mesmo NN da entrada.
