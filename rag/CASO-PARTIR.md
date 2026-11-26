# Partir um caso em consultas de pesquisa

Recebes o pedido de um advogado: a narrativa do caso, as leis que pensa usar e as perguntas. Um motor de pesquisa de legislação portuguesa (palavras-chave e um reordenador) vai procurar os artigos que decidem o caso. Ele funciona mal com textos longos: tu escreves as consultas curtas que ele deve fazer.

Cada linha de `entrada-NN.jsonl` é um pedido (`id`, `pedido`, `data_referencia`).

Para cada caso, escreve 3 a 6 consultas, uma por questão jurídica que o caso levanta (incluindo as que o advogado não viu e os prazos que contam). Cada consulta:
- tem 8 a 25 palavras, no vocabulário da lei (o que o artigo diria, não o que o cliente diria);
- nomeia o diploma ou código em causa pelo nome («Código do Trabalho», «Código Civil», «Código de Processo Civil», «regime jurídico do contrato de seguro»…);
- não leva números de artigos.

Separadamente, em `artigos_provaveis`, podes listar os artigos que achas que decidem, como um advogado os citaria («o 394.º do Código do Trabalho»). Só os que conheces com segurança; pode ficar vazio.

Não abras nenhum ficheiro além da tua entrada e da tua saída. Escreve em `saida-NN.jsonl` uma linha JSON por caso: {"id": "…", "consultas": ["…", "…"], "artigos_provaveis": ["…"]}
