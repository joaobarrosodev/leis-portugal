# Verificador às cegas: anexos, mapas e quadros de alteradores

Prompt dado a cada subagente verificador (Sonnet) de `consolidacao/anexos_alteradores.py`.

Lês um ficheiro `verificacao-entrada-K.jsonl`, com um item por linha. Cada item é um par (consolidado, alterador) e traz:

- `texto_do_alterador` e `rotulos_dre`: o que o alterador publica e o que o DRE diz que ele muda;
- `alteracoes_feitas`: as mudanças ao consolidado. Cada uma tem `paragrafo_antes` e `paragrafo_depois` (Markdown cru, com as ligações; «(parágrafo apagado)» quer dizer que saiu), o `contexto` (o título acima e os parágrafos vizinhos) e, às vezes, `nota_do_respondedor`. A nota não é prova;
- `nao_aplicadas`: o que ficou por aplicar e porquê.

Para cada item, decide se as mudanças aplicam corretamente o alterador a este consolidado:

1. **Imagem substituída.** O endereço novo é o de uma imagem do `texto_do_alterador`, e o alterador substitui, ratifica ou republica esse anexo por inteiro. O sítio (pelo `contexto`) é o desse anexo, e nada mais mudou.
2. **Alteração parcial de um quadro em imagem.** Insere-se, a seguir ao quadro, um parágrafo curto com palavras do alterador ou do rótulo e a imagem do alterador. A linha de antes fica igual e não se inventa texto da tabela. Se o alterador traz a alteração em texto, o texto inserido é esse, à letra.
3. **Alteração a um anexo em texto.** O que muda é exatamente o que o alterador manda, no sítio que ele indica, e nada mais.
4. **Um alterador que muda o anexo de outro diploma** (o rótulo ou o texto dizem de que diploma é o anexo): qualquer mudança neste consolidado é `errado`.
5. **As `nao_aplicadas` têm um motivo que se vê no item.**

Veredicto por item: `certo`, `errado` (diz qual mudança e porquê) ou `duvida` (diz porquê). Na dúvida, `duvida`.

Saída: `verificacao-saida-K.jsonl`, na mesma pasta, uma linha por item: `{"n": <n>, "veredicto": "certo|errado|duvida", "motivo": "<uma frase>"}`. Usa o `n` do item. Lê o ficheiro com python, um item de cada vez.
