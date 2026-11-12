# Prova de conceito: o sistema de perguntas no browser

Mede se a pesquisa pode correr no browser, com o índice alojado na internet e lido aos bocados (pedidos HTTP Range), para um site no GitHub Pages sem instalar nada. Os resultados e a conclusão estão no [`rag/README.md`](../README.md#prova-de-conceito-no-browser-12112026).

```bash
RAG_INDICE=… PYTHONPATH=src:. python -m rag.navegador.consultas --n 50   # grava as consultas SQL de 50 perguntas
python rag/navegador/medir_leituras.py rag/indice/indice.sqlite        # páginas, MB e pedidos por pergunta (precisa de `apsw`)
```

- `consultas.py`: corre a pesquisa com um reranker falso (o mesmo caminho, sem o modelo) e grava cada consulta SQL e os seus parâmetros, as consultas de arranque e os textos que o reranker leria.
- `medir_leituras.py`: repete as consultas sobre o índice através de uma VFS do SQLite que conta cada leitura. Cada página fora da cache seria um pedido HTTP Range; páginas seguidas contam como um só pedido (o melhor caso).

Os resultados ficam em `resultados/`, fora do git.
