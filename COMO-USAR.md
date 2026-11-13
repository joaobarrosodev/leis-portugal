# Como usar o sistema de perguntas no teu computador

Guia passo a passo para quem não é programador: instalar, criar a chave da API do Claude, fazer perguntas e atualizar para a versão nova.

> **Antes de começar.** É um protótipo. Responde com a lei e o artigo em vigor e, quando não tem a certeza, diz que não sabe. Não substitui um advogado nem a consulta do Diário da República. Os números da qualidade estão no [README](README.md#o-que-o-protótipo-de-perguntas-consegue-hoje).

> **Sigilo.** A pergunta e os artigos encontrados são enviados à API da Anthropic para o Claude escrever a resposta. **Não escrevas nomes, factos ou dados de clientes.** Pergunta só pelo que diz a lei.

## A forma mais simples: a aplicação

Para Mac e Windows, sem Terminal: descarrega-a em [joaobarrosodev.github.io/leis-portugal](https://joaobarrosodev.github.io/leis-portugal/), abre-a, e um passo a passo pede a IA que queres usar (Claude, OpenAI ou Gemini) e a chave. A chave fica no cofre do computador e os dados descarregam-se sozinhos. Ver [`app/README.md`](app/README.md).

Este guia é para quem a quer usar a partir do repositório. Com `./perguntar --web` (passo 6) tem a mesma página da aplicação, no browser.

## O que precisas

- Um computador com **macOS** ou **Linux**. Em Windows, funciona dentro do WSL (o Linux do Windows; ver [Windows](#windows)).
- **Espaço livre:** cerca de 20 GB, com alguma folga, porque o acervo cresce. O repositório ocupa 11 a 13 GB (a legislação toda em texto, mais o histórico), e da primeira vez acrescentam-se a base de dados (~0,8 GB), o índice de pesquisa (~4 GB) e os modelos de pesquisa (~0,7 GB).
- **Ligação à internet**, sobretudo na primeira vez (o download é grande).
- **Uma conta na Anthropic com créditos**, para a chave da API (passo 3). Sem chave também funciona, mas só mostra o artigo mais provável, sem resposta escrita.
- **Tempo:** da primeira vez, o download mais uns 10 a 15 minutos de preparação. Depois, cada pergunta demora uns segundos.

## 1. Abrir o Terminal

- **macOS:** abre a aplicação **Terminal** (Aplicações → Utilitários → Terminal, ou ⌘ + espaço e escreve "Terminal").
- **Linux:** abre o terminal da tua distribuição.

Todos os comandos deste guia escrevem-se no Terminal: copia a linha, cola e carrega em Enter.

## 2. Instalar o git e o Python

O sistema precisa do **git** (para descarregar e atualizar) e do **Python 3.11 ou mais recente**.

**macOS.** Instala o [Homebrew](https://brew.sh) (segue as instruções da página) e depois:

```bash
brew install git python@3.12
```

**Linux (Ubuntu ou Debian):**

```bash
sudo apt update && sudo apt install -y git python3 python3-venv
```

Confirma a versão do Python. Tem de dizer 3.11 ou mais:

```bash
python3 --version
```

## 3. Criar a chave da API do Claude

1. Vai a [platform.claude.com](https://platform.claude.com/) e cria uma conta (ou entra na tua).
2. Carrega créditos na conta, na parte de faturação (**Billing**) das definições. A API é paga por uso: sem créditos, a chave não funciona.
3. Abre [platform.claude.com/settings/keys](https://platform.claude.com/settings/keys) e cria uma chave (**Create Key**). Dá-lhe um nome, por exemplo "leis-portugal".
4. **Copia a chave logo.** Começa por `sk-ant-` e só é mostrada uma vez. Guarda-a num gestor de palavras-passe.

A chave dá acesso à tua conta e aos teus créditos: não a partilhes, não a ponhas em ficheiros do repositório e, se a perderes de vista, apaga-a na mesma página e cria outra.

## 4. Pôr a chave no Terminal

Para o Terminal guardar a chave de cada vez que o abres (troca `a-tua-chave` pela chave copiada, entre as aspas):

**macOS:**

```bash
echo 'export ANTHROPIC_API_KEY="a-tua-chave"' >> ~/.zshrc && source ~/.zshrc
```

**Linux:**

```bash
echo 'export ANTHROPIC_API_KEY="a-tua-chave"' >> ~/.bashrc && source ~/.bashrc
```

Para confirmar que ficou (mostra só o início):

```bash
echo ${ANTHROPIC_API_KEY:0:10}
```

## 5. Descarregar o leis-portugal

Vai para a pasta onde o queres guardar (por exemplo, a pasta pessoal) e descarrega:

```bash
cd ~
```

```bash
git clone https://github.com/joaobarrosodev/leis-portugal.git
```

O download é grande e pode demorar bastante, conforme a ligação. No fim, entra na pasta:

```bash
cd ~/leis-portugal
```

## 6. Fazer perguntas

```bash
./perguntar
```

**Da primeira vez**, antes de abrir as perguntas, prepara tudo sozinho e diz o que está a fazer:

1. cria o ambiente Python e instala o que falta;
2. prepara a base de dados da legislação (alguns minutos);
3. constrói o índice de pesquisa (~5 minutos, ~4 GB);
4. descarrega os modelos de pesquisa (~0,7 GB).

Depois escreves a pergunta e carregas em Enter. Para cada pergunta, o sistema mostra:

- **"Pesquisa por: …"**: a pergunta reescrita em linguagem jurídica, que é o que ele procura;
- **a resposta**, com os artigos citados e os avisos ("Artigo revogado", "Texto original; alterado por…", "Vigência do diploma desconhecida"…);
- **"Não sei."**, quando os artigos encontrados não chegam para responder com segurança;
- os outros artigos que encontrou.

No fim, pergunta se a resposta está certa e, se não, o que esperavas. Isso fica guardado só no teu computador, em `rag/resultados/privado/perguntas-testadas.jsonl`. **Se quiseres ajudar a melhorar o sistema, envia esse ficheiro ao autor**: as perguntas que falham entram no conjunto de avaliação.

**Numa página, no browser** (a mesma da aplicação: escolher a IA e a chave, perguntar, ver as fontes e avaliar):

```bash
./perguntar --web
```

Com a página, a chave escreve-se nas Definições e fica no cofre do computador; não precisas do passo 4. As avaliações ficam no mesmo ficheiro.

Para uma só pergunta, sem o modo interativo:

```bash
./perguntar "Quantos dias de férias tem um trabalhador por ano?"
```

Para sair do modo interativo: Enter numa linha vazia (ou `Ctrl + C`).

## 7. Atualizar para a versão nova

A legislação atualiza-se todos os dias. Para trazer a versão nova:

```bash
cd ~/leis-portugal
```

```bash
git pull
```

```bash
./perguntar --reconstruir
```

O `git pull` traz a legislação e o código novos. O `--reconstruir` volta a fazer a base de dados e o índice de pesquisa a partir deles (outra vez ~10 minutos): **sem ele, as perguntas continuam a usar a legislação antiga**, porque o índice é feito no teu computador e o `git pull` não o muda.

Se o `git pull` disser que tens alterações locais, é porque algum ficheiro do repositório foi mudado no teu computador. Para voltar à versão do GitHub (perde essas alterações; o ficheiro das tuas perguntas testadas não é afetado, porque está fora do git):

```bash
git stash && git pull
```

## Quanto custa

O leis-portugal é gratuito. Paga-se só a API da Anthropic, por uso:

- Cada pergunta faz duas chamadas: uma curta, que reescreve a pergunta, e outra que lê até 8 artigos e escreve a resposta.
- Com o modelo por omissão (Claude Opus 5.5: 4 dólares por milhão de tokens lidos e 20 por milhão escritos), **estimamos entre 5 e 15 cêntimos de dólar por pergunta**. É uma estimativa pelo tamanho do contexto, ainda não medida em uso real.
- O gasto vê-se no [Console](https://platform.claude.com/), na parte de uso e faturação.

Para gastar menos, há um modelo mais barato (Claude Sonnet 5.5, metade do preço), mas a qualidade medida foi com o Opus 5.5:

```bash
RAG_MODELO=claude-sonnet-5-5 ./perguntar
```

## Problemas comuns

| O que aparece | O que fazer |
|---|---|
| `python3: command not found`, ou versão abaixo de 3.11 | Volta ao passo 2. No macOS, fecha e abre o Terminal depois de instalar. |
| Mostra só um artigo, sem resposta escrita nem "Pesquisa por" | O Terminal não tem a chave. Volta ao passo 4 e confirma com `echo ${ANTHROPIC_API_KEY:0:10}`. |
| Erro a dizer que não há créditos (`credit balance`) | Carrega créditos no Console (passo 3). |
| Erro de chave inválida (`authentication`) | A chave foi mal copiada ou apagada. Cria outra e repete o passo 4 (apaga a linha antiga do `~/.zshrc` ou `~/.bashrc`). |
| Falta de espaço em disco | São precisos cerca de 20 GB livres. |
| "O export é mais recente do que o índice" | Corre `./perguntar --reconstruir`. |

## Windows

O `./perguntar` corre em macOS e Linux. Em Windows, instala o WSL (o Linux que vem com o Windows):

1. Abre o **PowerShell** como administrador e escreve `wsl --install`. Reinicia o computador quando pedir.
2. Abre a aplicação **Ubuntu** que ficou instalada.
3. Segue este guia a partir do passo 2, na parte do Linux.

## Ainda não testado

Este caminho, com a chave da API, ainda não foi corrido do princípio ao fim com uma chave real. As medições de qualidade foram feitas com sessões do Claude a seguir as mesmas regras. Se algum passo falhar, avisa o autor com a mensagem de erro (sem a chave).
