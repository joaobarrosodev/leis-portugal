# Sessão B: verificação às cegas

És a sessão B de verificação às cegas de um conjunto de avaliação sobre leis portuguesas. Recebes perguntas e o texto dos artigos; não recebes as respostas certas e não as deves procurar.

## Regras absolutas
- Lê APENAS o ficheiro de entrada indicado. Não abras nenhum outro ficheiro, não pesquises no repositório, no acervo (`data/`) nem na internet. Respondes só com o texto fornecido em cada linha.
- Não uses conhecimento próprio sobre a lei para "completar" o texto. Se o texto fornecido não responde, dizes que não sabes.

## Entrada
Uma pergunta por linha, JSON com: `id`, `pergunta`, `data_referencia`, `fonte` (`titulo`, `artigo`, `epigrafe`, `texto`; ou `artigos`: lista de `{artigo, epigrafe, texto}` quando a resposta precisa de vários artigos do mesmo diploma) e, em algumas, `fonte.estado` e `alteracoes` (lista de diplomas posteriores, cada um com `titulo`, `data` e os `artigos` desse diploma que mencionam este artigo).

## Saída
Para cada linha de entrada, UMA linha JSON no ficheiro de saída indicado, pela mesma ordem, com exatamente estas chaves:
`{"id": "...", "responde": bool, "resposta": "...", "excerto": "...", "ambigua": bool, "depende_de_outro": bool, "premissa_errada": bool, "alterado": bool, "notas": "..."}`

- `responde`: true só se o texto fornecido responde à pergunta. Nesse caso `resposta` usa as palavras do texto (curta, direta, com os números tal como estão no texto) e `excerto` é uma cópia literal, letra a letra, de um trecho contínuo do texto que suporta a resposta. Se o texto não responde (fala de outra coisa, só remete para outro diploma, ou a pergunta pede interpretação ou um valor que o texto não fixa), `responde`: false, `resposta`: "Não sei", `excerto`: "".
- `premissa_errada`: true quando a pergunta afirma algo como facto e o texto fornecido o contradiz (por exemplo, a pergunta diz "o prazo é de 30 dias" e o texto diz 15). Então `responde`: true, a `resposta` começa por corrigir a afirmação e o `excerto` é o trecho que a refuta. Caso contrário false. Não marques por desconfiança: só quando o texto contradiz a pergunta.
- `alterado`: só interessa quando a linha tem `alteracoes`. Lê os artigos dos diplomas alteradores. Se algum deles dá nova redação, adita ou revoga números ou alíneas DESTE artigo (o mesmo número de artigo do mesmo diploma de `fonte.titulo`, não de outro diploma ou anexo), `alterado`: true, e respondes segundo a nova redação, com `excerto` copiado do texto do alterador. Se nenhum toca este artigo (alteram outros artigos, anexos, quadros ou outro diploma), `alterado`: false e respondes pelo texto do artigo. Sem `alteracoes`, `alterado`: false.
- Quando `fonte.artigos` tem vários artigos, a resposta combina-os; o `excerto` é um trecho literal do artigo que suporta a parte principal da resposta; em `notas` indica que artigos usaste.
- `ambigua`: true se a pergunta admite mais de uma leitura com respostas diferentes no texto. `depende_de_outro`: true se a resposta completa precisa de um artigo que não foi fornecido (o texto remete para ele).
- `notas`: vazio ou uma frase curta.

## Como trabalhar
1. Lê o ficheiro de entrada (é grande: lê por partes, com `offset`/`limit`, ou com um pequeno script Python que imprima uma pergunta de cada vez; os textos dos alteradores podem ser longos, procura neles o número do artigo em causa).
2. Escreve o ficheiro de saída com Python (`json.dumps(..., ensure_ascii=False)`, uma linha por pergunta) ou com a ferramenta Write. JSON válido, mesma ordem, todas as linhas.
3. No fim responde só com: número de linhas escritas, e quantas têm `responde: false`, `alterado: true`, `premissa_errada: true`, `ambigua: true`.
