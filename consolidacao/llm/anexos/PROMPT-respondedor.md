# Respondedor: anexos, mapas e quadros que um alterador muda

Prompt dado a cada subagente respondedor (Opus) de `consolidacao/anexos_alteradores.py`.

Tens um ficheiro `entrada-NN.jsonl`, com um consolidado por linha. Cada item traz:

- `texto_em_vigor`: o texto consolidado de hoje, em linhas numeradas («L123: …»), em Markdown cru, com as ligações. Quando `texto_parcial` é true, vêm só as linhas relevantes, os títulos e o fim do texto. As linhas que não vês existem, mas não são para mexer.
- `alteradores_candidatos`: os alteradores que a triagem deu «sem alteração textual», mas cujo rótulo do DRE (`rotulos_dre`) diz que mudam um anexo, um mapa, um quadro, uma tabela ou uma planta. Vêm por ordem de data, com o texto (as imagens vêm como «[(ver documento original)](endereço)»).
- `outros_alteradores`: os outros alteradores do consolidado, só com o título e os rótulos. Servem para ver se um posterior substituiu o mesmo anexo.

Para cada alterador candidato, decide o que ele muda **neste** consolidado e aplica-o, ou diz porque não se aplica.

## O que se aplica

Todas as trocas levam `com_ligacoes: true`. O `texto_atual` é a linha L exatamente como está, e o `texto_novo` é Markdown cru. Uma troca por linha. Não juntes nem partas linhas, salvo para inserir: na inserção, o `texto_novo` é a linha de antes, uma linha em branco e o texto novo.

1. **Substituição de um anexo, mapa, quadro ou planta que só existe em imagem.** O alterador substitui, ratifica ou republica o anexo por inteiro. Troca o endereço da imagem desse anexo (no consolidado) pelo endereço da imagem que o alterador publica, e o resto da linha fica igual. Se o anexo tem várias imagens e o alterador uma só (ou o contrário), põe na primeira linha as imagens do alterador, separadas por uma linha em branco, e as outras imagens antigas do mesmo anexo passam a "".
2. **Alteração parcial de um quadro ou mapa que só existe em imagem** («alterado o quadro de pessoal…», «são aditados ao quadro…», «na parte referente a…»). Não se pode reescrever a tabela. Insere a seguir à última linha desse quadro no consolidado um parágrafo curto, com as palavras do próprio alterador ou do rótulo, e a imagem do alterador. Por exemplo:

   «Alteração ao quadro de pessoal (Portaria n.º 168/88):

   [(ver documento original)](endereço)»

   A nota «> Alterado pelo/a …» é posta pelo script, não a escrevas. Se o alterador traz a alteração em texto (uma lista de lugares, um quadro escrito), insere esse texto, à letra, em vez da imagem.
3. **Alteração de um anexo que está em texto no consolidado.** Aplica as alterações ao texto, como numa alteração normal: troca as linhas, insere ou suprime, à letra.
4. **Vários alteradores sobre o mesmo anexo.** Aplica-os todos, por ordem. Quando um posterior substitui o anexo por inteiro, não apliques os anteriores a esse anexo («reescrito depois», com o nome do posterior). Quando um posterior que está só em `outros_alteradores` o substitui, também não: «reescrito depois».

## O que não se aplica

Vai para `nao_aplicadas`, com um motivo final:

- `outro diploma`: muda um anexo de outro diploma (o rótulo diz «Alterados os anexos da Port 1144/2008…»), ou o quadro de um serviço que não é deste consolidado;
- `reescrito depois`: um alterador posterior substituiu o mesmo anexo;
- `já aplicada`: o consolidado já tem a imagem ou o texto do alterador;
- `sem texto nem imagem`: o alterador, no texto que tens, não traz a alteração (só o rótulo a refere);
- `não se aplica: <porquê>`: qualquer outro caso, com a razão.

Na dúvida sobre o sítio ou sobre o que muda, não apliques e escreve `não se aplica:` com a razão. Não há «dúvida» como motivo final.

## Saída

Um ficheiro `resposta-NN.jsonl`, na mesma pasta e com o mesmo NN, com uma linha por consolidado da entrada:

```json
{"id": "<id do consolidado>", "alteradores": [{"alterador": "<id do alterador>", "trocas": [{"linha": 123, "com_ligacoes": true, "texto_atual": "…", "texto_novo": "…", "nota": "<o que aplica e onde>"}], "nao_aplicadas": [{"instrucao": "<resumo curto>", "motivo": "…"}]}]}
```

Cada alterador candidato tem de aparecer, mesmo com `trocas` vazio. Escreve o ficheiro com python, copiando o `texto_atual` da entrada. Confirma com python:
- que cada linha é JSON válido;
- que cada `texto_atual` é, carácter a carácter, a linha L da entrada;
- que cada inserção começa pela linha de antes;
- que estão todos os alteradores candidatos.
