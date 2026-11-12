# Verificação às cegas (sessão B)

Cada linha do ficheiro de entrada tem `id`, `pergunta`, `data_referencia` e `fonte` (título, artigo, epígrafe e `texto` do artigo). NÃO tens a resposta certa. Responde a cada pergunta usando só o `texto` da fonte; não leias mais nada.

Escreve no ficheiro de saída uma linha JSON por `id`, com:
`{"id": ..., "responde": true|false, "resposta": "...", "excerto": "...", "ambigua": true|false, "depende_de_outro": true|false, "notas": ""}`

- `responde`: false se o texto não responde à pergunta (nesse caso `resposta` = "Não sei" e explica em `notas`).
- `resposta`: curta e completa, com os números como estão no texto. Se a fonte for de um ato revogado e a pergunta o tratar como em vigor, responde com o que o texto diz; não sabes se está revogado.
- `excerto`: a frase do texto que suporta a resposta, copiada letra a letra.
- `ambigua`: true se a pergunta admite mais de uma resposta razoável.
- `depende_de_outro`: true se a resposta depende de outro artigo, anexo ou ato que não está no texto.

Confirma no fim que escreveste uma linha válida por cada `id` da entrada. Responde só com uma linha: quantas perguntas, quantas respondidas, quantas ambíguas ou dependentes.
