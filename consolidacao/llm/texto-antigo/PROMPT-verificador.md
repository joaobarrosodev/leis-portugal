# Verificador às cegas: texto antigo retirado de artigos consolidados

Prompt dado ao subagente verificador (Sonnet) de `consolidacao/texto_antigo.py corrigir`.

Lês `entrada.jsonl`, com um artigo por linha. Em cada um, um consolidado tinha a nova redação do artigo, ou «(Revogado.)», e logo a seguir o corpo antigo do mesmo artigo. Uma regra tirou esse corpo antigo. Cada item traz:

- `artigo_original`: o corpo do artigo na versão original do diploma;
- `antes`: o artigo no consolidado, antes da correção;
- `depois`: o artigo depois da correção;
- `removido`: o que a regra tirou;
- `epigrafe_no_titulo`: a epígrafe que passou para o título do artigo, ou null.

Para cada item, decide se a correção está certa. Confirma estas três coisas:

1. **O que saiu é o corpo antigo.** O `removido` é o `artigo_original`, ou começa pelo título de divisão que lhe servia de epígrafe e continua com o corpo original. Não saiu nada que fosse da nova redação.
2. **O que ficou está completo.** O `depois` tem a nova redação inteira, ou «(Revogado.)», e as notas «> Alterado pelo/a …» ou «> Revogado pelo/a …». Faltar uma linha da nova redação é `errado`.
3. **A epígrafe.** Se passou uma epígrafe para o título, tem de ser o título de divisão do original («##### …»), copiado à letra.

Num artigo revogado, o corpo «(Revogado.)» com a nota é o resultado certo: o texto antigo não pode ficar.

Veredicto por item: `certo`, `errado` (diz o quê) ou `duvida` (diz porquê). Na dúvida, `duvida`.

Saída: `saida.jsonl` na mesma pasta, com uma linha por item, assim: `{"n": <n>, "caminho": "<caminho>", "artigo": "<artigo>", "veredicto": "certo|errado|duvida", "motivo": "<uma frase>"}`. Copia o `n`, o `caminho` e o `artigo` do item. Lê os itens com python, um de cada vez.
