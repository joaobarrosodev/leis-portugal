# Para agentes de IA neste repositório

Lê primeiro [`COMO-DECIDIMOS.md`](COMO-DECIDIMOS.md): como se decide, como se mede uma mudança, como se trabalha e o que precisa de quem mantém o projeto. As decisões em aberto e as já tomadas estão em [`PENDENTE.md`](PENDENTE.md).

Regras que se esquecem mais:
- **Linguagem:** português de Portugal, nos textos, nos commits e nas mensagens.
- **Commits:** só com os ficheiros da tarefa. Antes do push, `git fetch` e `git pull --no-rebase`, e nunca force-push.
- **O `data/`** só muda no checkout principal, e o índice (`rag/indice/`) reconstrói-se uma vez de cada vez, no terminal.
- **Números:** nada de números sem medição. Escreve o n e as ressalvas, e não uses o conjunto de afinação para confirmar uma mudança.
- **Fora do git:** não ponhas nada de `avaliacao/privado/` nem de `rag/resultados/privado/` no repositório. São as perguntas reais das pessoas.
- **Informação jurídica, não consulta jurídica:** nenhum texto público diz que o projeto aconselha, analisa o caso de alguém ou substitui um advogado.
