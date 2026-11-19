# Escrever perguntas de leigo para cada artigo

Recebes um ficheiro `entrada-NN.jsonl`. Cada linha é um artigo em vigor do Código do Trabalho, do Código Civil (arrendamento) ou do NRAU, com os campos `documento`, `chave`, `titulo`, `parte`, `epigrafe`, `texto` e `sha`.

Para cada artigo escreves **3 a 5 perguntas** como as faria uma pessoa sem formação jurídica que tem a dúvida a que o artigo responde. As perguntas vão ajudar a pesquisa a encontrar este artigo quando alguém escreve com as palavras do dia a dia.

Usa só o que vem na entrada. Não leias mais nenhum ficheiro, nem do repositório nem de fora. Em particular, nunca abras nada em `avaliacao/` nem em `rag/resultados/`.

## Formato
Uma linha JSON por artigo, no ficheiro de saída indicado, com o mesmo `documento` e a mesma `chave` da entrada:

`{"documento": "...", "chave": "...", "perguntas": ["...?", "...?", "...?"]}`

Escreve uma linha para todos os artigos da entrada, pela mesma ordem.

## As perguntas
- **Quem pergunta:** um trabalhador, um patrão de uma pequena empresa, um inquilino, um senhorio, um familiar. Não é advogado e não sabe os termos técnicos.
- **Palavras do dia a dia**, em português de Portugal:
  - patrão ou empresa, em vez de «empregador»;
  - inquilino, em vez de «arrendatário»;
  - senhorio, em vez de «locador»;
  - casa ou loja arrendada, em vez de «locado»;
  - despedir, ficar sem trabalho, horas extra, folga, baixa, recibo, renda, contrato, sair de casa.

  Uma palavra técnica só entra se uma pessoa comum também a usa (férias, salário, despedimento, contrato a prazo).
- **Varia o jeito.** Junta pelo menos dois destes:
  - uma pergunta direta («Quantos dias de férias tenho por ano?»);
  - um caso concreto na 1.ª pessoa ou de alguém próximo («A minha filha trabalha num café e o patrão quer que ela fique depois da hora sem pagar. Pode?»);
  - a dúvida de quem não sabe por onde começar («O que acontece se eu não pagar a renda dois meses?»).
- **Cada pergunta tem resposta neste artigo**, mesmo que só em parte. As perguntas cobrem coisas diferentes que o artigo diz (o prazo, quem pode, o que acontece se…), não são cinco maneiras de dizer a mesma coisa.
- Num artigo curto ou abstrato (uma definição, um princípio, um âmbito), pergunta o que levaria alguém a precisar dele: «O que conta como contrato de trabalho?», «Trabalhar à peça também é contrato de trabalho?».
- **Não cites** números de artigos, números nem alíneas, nem nomes de diplomas («Código do Trabalho», «Código Civil», «NRAU», «Lei n.º…», «Decreto-Lei…»). Podes dizer «a lei».
- Não copies frases do artigo. Uma pessoa comum não fala assim.
- Cada pergunta tem 4 a 40 palavras e acaba em «?». Escreve uma só pergunta por entrada da lista: pode ter uma frase de contexto antes.

## No fim
Escreve o ficheiro com a ferramenta Write. Confirma com um pequeno script Python que:
- cada linha é JSON válido;
- há uma linha para cada `chave` da entrada;
- cada linha tem 3 a 5 perguntas;
- nenhuma pergunta tem «artigo», «n.º», «.º», «Código do Trabalho», «Código Civil», «NRAU», «Lei n.º» ou «Decreto».

Responde só com uma linha: quantos artigos e quantas perguntas escreveste.
