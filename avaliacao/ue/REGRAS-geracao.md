# Escrever perguntas de avaliação sobre direito da UE

Recebes um ficheiro `lote-*.jsonl` com candidatos: cada linha tem um `id` e um artigo real de um ato da UE (`documento`, `caminho`, `titulo`, `artigo`, `epigrafe`, `texto`). Para cada candidato escreves no máximo UMA pergunta, numa linha JSON, no ficheiro de saída indicado. Usa só o texto do candidato; não leias mais nada.

## Formato de cada linha
`{"id": "<o id do candidato>", "tipo": "literal|revogada|sem_resposta", "pergunta": "...", "data_referencia": "2026-11-12", "fonte": {"documento": ..., "caminho": ..., "titulo": ..., "artigo": ..., "epigrafe": ...}, "resposta": "...", "excerto": "...", "ambito": "ue"}`
(copia `documento`, `caminho`, `titulo`, `artigo` e `epigrafe` do candidato para `fonte`.)

## literal (lotes lote-lit-*)
- A pergunta nomeia o ato pelo número curto, como o diria um jurista: "Segundo o Regulamento (UE) n.º 715/2013, …", "Nos termos da Decisão 2009/860/CE, …", "Na Diretiva 2006/112/CE, …". Não cites o número do artigo na pergunta.
- Pergunta sobre um facto escrito no artigo: prazo, valor, quem pode ou deve o quê, condição, definição, lista. Uma só resposta possível, sem interpretação.
- `resposta`: curta e completa, com os números como estão no texto.
- `excerto`: a frase ou parte do texto que suporta a resposta, copiada LETRA A LETRA do `texto` (mesma pontuação e espaços; sem `*`, `#` nem ligações). Os números da resposta têm de estar no excerto.
- NÃO escrevas perguntas sobre a data de entrada em vigor, de aplicação ou de publicação do ato, nem sobre quem são os destinatários: são triviais e não medem nada.
- Se o artigo não dá uma pergunta boa (só remete para anexos, só altera outro ato, é uma tabela, é só "o anexo X é substituído", texto muito técnico sem facto claro), NÃO escrevas linha para esse candidato.

## revogada (lote-rev-1)
- O candidato traz `revogado_por`, `revogado_por_titulo` e `data_revogacao`. Escreve uma pergunta literal sobre o artigo, como acima, mas no presente ("Qual é o prazo previsto no Regulamento X para…?").
- `resposta`: "O <titulo curto do ato> foi revogado pelo <revogado_por_titulo curto> (<data_revogacao>); a norma já não está em vigor."
- `excerto`: como nas literais (do texto do artigo revogado).
- Acrescenta `"revogado_por": {"documento": <revogado_por>, "titulo": <revogado_por_titulo>, "data": <data_revogacao>}`.
- Sem `revogado_por` ou sem data: não escrevas linha.

## sem_resposta (lote-sem-1)
- O candidato é um DISTRATOR: a pergunta NÃO pode ter resposta nele nem, tanto quanto saibas, em nenhum ato da UE. Alterna dois tipos: (a) um ato que não existe, com número impossível ("Regulamento (UE) 2031/9998", "Diretiva (UE) 2029/777"); (b) um ato real conhecido (por exemplo o do distrator) mas sobre um assunto de que ele não trata.
- `fonte`: null. Acrescenta `"distrator": {"documento": ..., "caminho": ..., "titulo": ..., "artigo": ..., "epigrafe": ...}` copiado do candidato.
- `resposta`: "Não sei: <porquê, numa frase>". `excerto`: "".

## No fim
Escreve o ficheiro com a ferramenta Write (JSONL, uma linha por pergunta), confirma que cada linha é JSON válido e, nas literais e revogadas, que cada `excerto` aparece tal e qual no `texto` do candidato (podes confirmar com um pequeno script Python). Responde só com uma linha: quantos candidatos, quantas perguntas escritas e quantos saltados.
