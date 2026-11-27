# Como decidimos

Este ficheiro diz como se tomam decisões no leis-portugal, para que o projeto possa avançar sem depender de uma só pessoa. Vale para quem contribui e para os agentes de IA que trabalham no repositório. Quando houver dúvida, escolhe-se o que está mais de acordo com estes princípios. Quando dois princípios chocarem, ganha o que vem primeiro nesta lista.

## Princípios

1. **Os dados primeiro.** Uma base de dados sólida vem antes de qualquer melhoria da pesquisa, da aplicação ou da comunicação.
   - Enquanto uma auditoria aos dados estiver aberta, não se reconstrói o índice nem se publica.
   - «Fechado» quer dizer que cada registo ou está feito e verificado, ou tem o motivo registado. Não há «se valer a pena».
2. **A fonte oficial é a referência.** Cada texto liga à sua fonte (Diário da República, EUR-Lex, Tribunal Constitucional, CNPD).
   - O que o projeto consolida está marcado como sem valor oficial.
   - Não se inventa cobertura: o que falta diz-se que falta.
3. **Números baixos e reais, não altos e falsos.** Uma melhoria só existe se estiver medida, e mede-se com o critério mais exigente que der para aplicar:
   - juízes às cegas, mais de um, com a resposta certa a contar só quando todos concordam;
   - o n sempre escrito, e as ressalvas ao lado do número;
   - o conjunto onde se desenhou uma mudança nunca serve para a confirmar (ver [Como se mede uma mudança](#como-se-mede-uma-mudança));
   - nunca se muda o conjunto de avaliação para subir um número.
4. **Não se diz em público o que não está medido.** O [`COMUNICACAO.md`](COMUNICACAO.md) tem os números que se podem usar e as frases que não se podem dizer.
5. **Informação jurídica, não consulta jurídica.** O projeto encontra e explica o que a lei diz, e não aconselha ninguém sobre o seu caso. A consulta jurídica é competência de advogados e solicitadores (Lei n.º 10/2024).
   - O modo profissional do fluxo de caso é uma ferramenta para quem está habilitado.
   - O pormenor está no `COMUNICACAO.md`.
6. **O produto trabalha com o LLM de quem o usa.** A aplicação e o servidor MCP correm no computador de cada pessoa, com o Claude, o ChatGPT ou o Gemini que ela já tem.
   - O projeto não tem um serviço a responder a casos.
   - O projeto não recebe nem guarda as perguntas das pessoas.
7. **O técnico e os dados antes da interface e do piloto.** Ao escolher o próximo trabalho, vem primeiro o que melhora o acervo e o sistema: cobertura, consolidação, leitura dos textos, pesquisa e medições.
8. **Não se mostra o produto a advogados antes de estar bom.** Nem o produto nem os casos de teste vão a um advogado enquanto o sistema não responder bem a perguntas escritas de forma simples. Uma má primeira impressão não se recupera.

## Como se mede uma mudança

- **Pesquisa e respostas:** `python -m rag.avaliar` nas 1.298 perguntas, com a configuração da aplicação, contra a última medição publicada (`rag/resultados/`). Uma mudança só entra no índice publicado se não piorar o total de certas.
- **Análise de caso:** os casos de `avaliacao/casos/`.
  - **Desenhar e confirmar em conjuntos diferentes.** Uma mudança desenha-se num conjunto e confirma-se noutro, com casos escritos depois e às cegas para a mudança.
  - **Cada conjunto de confirmação tem prazo.** Um conjunto que já serviu para confirmar duas mudanças passa a ser de desenho, e escrevem-se casos novos.
  - **Os casos passam por três verificações:**
    1. o `artigo.py verificar`, que tem de dar 0 erros;
    2. uma revisão adversarial;
    3. a correção pelo que a revisão encontrou.
  - **Quem responde só vê a entrada.** Os dois juízes, o exigente e o cético, julgam às cegas um do outro.
- **Mudanças pequenas e soltas:** com testes em `tests/`, e o número que mudam no README do módulo.
- **Uma mudança que não melhora fica desligada.** Fica documentada com o número, como o reranker por passagens. Não se apaga o resultado.

## Como se trabalha

- **Commits:** em português de Portugal, descritivos, só com os ficheiros da tarefa.
  - Antes do push, correm-se os testes e o `ruff`, e faz-se `git fetch` e `git pull --no-rebase`.
  - Nunca force-push: o `main` está protegido.
- **O `data/` só muda no checkout principal,** e cada lote depois das verificações da sua ronda. A atualização diária (GitHub Actions) é a única que escreve no `data/` sem uma ronda.
- **O índice reconstrói-se uma vez de cada vez,** no terminal e fora do sandbox, e só quando nenhuma outra sessão estiver a mudar dados.
  - Não se apaga o índice antigo: a construção escreve num ficheiro à parte e só troca no fim.
  - A seguir mede-se, e só se publica se a medição não piorar. A versão nova tem de ser maior do que a publicada.
- **Agentes em paralelo:**
  - cada um tem a sua pasta temporária e não escreve fora dela;
  - as saídas conferem-se contra as entradas antes de se juntarem;
  - no máximo 8 de cada vez, em Opus;
  - as sessões filhas só falam ao coordenador quando uma ronda fecha, quando há um problema ou quando há uma decisão a tomar.
- **Quando algo falha:**
  - lê-se o registo antes de dizer de onde vem a falha;
  - reproduz-se o problema nas mesmas condições;
  - corrige-se, e retoma-se a partir do ponto em que parou, sem refazer o que já está validado.
- **O que se decide e porquê fica escrito.** Vai para o [`PENDENTE.md`](PENDENTE.md), para o README do módulo e para a mensagem do commit, para que quem vier a seguir não tenha de adivinhar.

## O que precisa de quem mantém o projeto

O resto decide-se com estes princípios. Isto não:
- lançar uma versão nova da aplicação;
- recolher de uma fonte nova sem as condições de reutilização confirmadas, ou mudar a licença;
- falar em nome do projeto com entidades: pedidos de autorização, imprensa, a Ordem dos Advogados;
- criar contas, pagar serviços, ou o que for irreversível fora do repositório;
- abrir a análise de caso ao público, que antes precisa de um parecer de um advogado sobre o enquadramento da Lei n.º 10/2024.
