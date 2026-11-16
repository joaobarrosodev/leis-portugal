# Escrever perguntas de avaliação sobre atos da 2.ª Série do DR

Recebes um ficheiro `lote-*.jsonl` com candidatos. Cada linha tem um `id` e um artigo real de um ato da 2.ª Série do Diário da República: regulamentos municipais e de institutos, editais, deliberações, declarações e acordos coletivos de trabalho. Os campos são `documento`, `caminho`, `titulo`, `tipo_documento`, `entidade`, `sumario`, `data`, `artigo`, `epigrafe` e `texto`.

Para cada candidato escreves no máximo UMA pergunta, numa linha JSON, no ficheiro de saída indicado. Usa só o que vem no candidato; não leias mais nada.

## Formato de cada linha
`{"id": "<o id do candidato>", "tipo": "literal", "pergunta": "...", "data_referencia": "2026-11-16", "fonte": {"documento": ..., "caminho": ..., "titulo": ..., "artigo": ..., "epigrafe": ...}, "resposta": "...", "excerto": "...", "ambito": "serie_ii"}`

Copia `documento`, `caminho`, `titulo`, `artigo` e `epigrafe` do candidato para `fonte`.

## A pergunta
- Na 2.ª Série o número repete-se de ano para ano e entre entidades. Por isso, a pergunta identifica o ato pelo título **e** pela entidade, como o faria quem o procura. Exemplos: "No Regulamento n.º 154/2014, do Instituto Politécnico da Guarda, …", "Segundo o Regulamento do Programa HABITODIVELAS (Regulamento n.º 1126/2026, Município de Odivelas), …", "No Edital n.º 493/2023, que aprova o Regulamento do Centro de Recolha Oficial Animal de Famalicão, …". O `sumario` ajuda a dar o nome do regulamento.
- Não cites o número do artigo na pergunta.
- Pergunta sobre um facto escrito no artigo: prazo, valor, quem pode ou deve o quê, condição, definição, lista. Tem de ter uma só resposta possível, sem interpretação.

## A resposta e o excerto
- `resposta`: curta e completa, com os números como estão no texto.
- `excerto`: a frase ou parte do texto que suporta a resposta, copiada LETRA A LETRA do `texto`, com a mesma pontuação e os mesmos espaços, sem `*`, `#` nem ligações. Os números da resposta têm de estar no excerto.

## Quando não escrever linha
NÃO escrevas linha para o candidato quando o texto:
- é um projeto, uma proposta ou um aviso de consulta ou discussão pública, e não uma norma aprovada;
- só altera outro regulamento ("O artigo 5.º passa a ter a seguinte redação"), só aprova ou só manda publicar;
- é sobre a entrada em vigor, a publicação, a revogação de outro texto ou as dúvidas e omissões ("são resolvidos por deliberação da Câmara");
- só remete para anexos, plantas ou quadros, é uma tabela, ou é técnico demais para ter um facto claro.

## No fim
Escreve o ficheiro com a ferramenta Write: JSONL, uma linha por pergunta. Confirma que cada linha é JSON válido e que cada `excerto` aparece tal e qual no `texto` do candidato. Podes confirmar com um pequeno script Python. Responde só com uma linha: quantos candidatos, quantas perguntas escritas e quantos saltados.
