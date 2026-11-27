# Servidor MCP do leis-portugal

Liga a legislação portuguesa e da UE do acervo a um cliente MCP (Claude Code, Claude Desktop, Cursor e outros). O servidor corre no teu computador, sobre o índice de pesquisa (SQLite com FTS5, um pedaço por artigo) que a aplicação também usa. Não precisas de clonar os gigabytes do acervo nem de uma chave de IA, porque o LLM é o do teu cliente.

## Instalar

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/joaobarrosodev/leis-portugal.git
cd leis-portugal
git sparse-checkout set rag mcp avaliacao src
python3 -m venv .venv && .venv/bin/pip install -e '.[mcp]'
.venv/bin/python -m rag.dados descarregar --pasta ~/leis-portugal-indice
```

- O clone esparso traz só o código, sem `data/`: são cerca de 120 MB.
- O índice vem do Hugging Face ([`joaobarrosodev/leis-portugal-indice`](https://huggingface.co/datasets/joaobarrosodev/leis-portugal-indice)). São cerca de 2 GB comprimidos, que ficam em cerca de 6 GB.
- Para o atualizar mais tarde, corre o mesmo comando: descarrega só os deltas desde a tua versão.

## Ligar ao cliente

**Claude Code:**

```bash
claude mcp add leis-portugal -e RAG_INDICE=$HOME/leis-portugal-indice -- $PWD/.venv/bin/python $PWD/mcp/servidor.py
```

**Claude Desktop** (`claude_desktop_config.json`) e **Cursor** (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "leis-portugal": {
      "command": "/caminho/para/leis-portugal/.venv/bin/python",
      "args": ["/caminho/para/leis-portugal/mcp/servidor.py"],
      "env": {"RAG_INDICE": "/caminho/para/leis-portugal-indice"}
    }
  }
}
```

## Ferramentas

| Ferramenta | O que faz |
|---|---|
| `pesquisar` | Os artigos mais próximos de uma pergunta, numa data, com os avisos de vigência (revogado, redação antiga, texto original). |
| `ler_artigo` | O texto de um artigo, com as notas e as datas de cada redação. |
| `diploma` | Os metadados de um diploma pelo número ou nome («Lei n.º 7/2009», «Código do Trabalho»). |
| `relacoes` | O que um diploma altera, revoga ou transpõe, e o que o altera. |
| `contar_prazo` | O fim de um prazo com as regras da lei: CC 279.º e 296.º, CPC 138.º e 142.º, CPA 87.º, feriados do CT 234.º e férias judiciais ([`rag/prazos.py`](../rag/prazos.py)). |

- **Reranker:** `pesquisar` usa o BM25 do índice e, se o extra `rag` estiver instalado (`pip install -e '.[rag]'`), também o reranker cruzado da aplicação, que é mais lento e mais preciso. Para desligar o reranker, usa `RAG_RERANKER=0`.
- **Qualidade medida:** está em [`rag/README.md`](../rag/README.md), com a pesquisa e o reranker como na aplicação. Com o BM25 sozinho, a pesquisa é pior.

## Limites

- **Não é aconselhamento jurídico.** O texto é o do acervo, sem valor oficial. Confirma-o sempre na fonte oficial: o Diário da República e o EUR-Lex.
- **O índice tem a data da versão publicada.** O que saiu no Diário da República depois disso só aparece na versão seguinte.
- **`contar_prazo` não conta feriados municipais nem tolerâncias de ponto.**
- **Protocolo:** transporte stdio, uma mensagem JSON-RPC 2.0 por linha, versão `2025-06-18`. O servidor não usa o SDK do MCP, por isso só precisa da biblioteca normal do Python e do radical Snowball.
