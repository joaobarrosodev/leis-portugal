# A aplicação Leis de Portugal (Mac e Windows)

A página de perguntas (`rag/web.py` e `rag/pagina/`) numa janela própria, empacotada com o PyInstaller. Quem a usa não precisa do Terminal, do git nem do repositório:

1. **Passo a passo da primeira vez:**
   - boas-vindas, com o aviso de sigilo;
   - escolher a IA: Claude (o único modelo medido, Claude Opus 5.5), OpenAI ou Gemini;
   - criar a chave na conta dessa IA;
   - colar a chave. A aplicação testa-a sem gastar créditos e guarda-a no cofre do sistema (`rag/definicoes.py`, `rag/provedores.py`).
2. **Descarregar os dados:** o índice pronto (`rag/dados.py`), com barra de progresso e retoma, e os modelos de pesquisa da primeira vez. As atualizações fazem-se nas Definições.
3. **Perguntar e avaliar:** como o `./perguntar`, com as fontes, os avisos, a jurisprudência e "Está certo?".

Tudo fica na pasta da aplicação: `~/Library/Application Support/Leis de Portugal` no Mac e `%APPDATA%\Leis de Portugal` no Windows. Nas variáveis do sistema não se mexe.

## Construir

```bash
pip install -e '.[rag,app]'
```

```bash
python app/leis_portugal_app.py --verificar "Qual o prazo para pagar uma coima?"
```

```bash
pyinstaller app/leis-portugal.spec --noconfirm
```

O resultado fica em `dist/Leis de Portugal.app` no Mac (cerca de 210 MB) ou em `dist/Leis de Portugal/` no Windows. Os dados não vão dentro da aplicação. O ícone gera-se com `python app/icone.py`.

O workflow `.github/workflows/aplicacao.yml` constrói as duas versões em macOS e em Windows. Com uma etiqueta `app-v*`, põe os `.zip` numa Release, que é de onde o site os descarrega:

```bash
git tag app-v0.1.0 && git push origin app-v0.1.0
```

## Publicar os dados

O índice está no Hugging Face, em [`joaobarrosodev/leis-portugal-indice`](https://huggingface.co/datasets/joaobarrosodev/leis-portugal-indice) (`rag/dados.py`). Lá ficam:
- a versão completa;
- os **deltas** desde ela, com os diplomas novos, alterados e removidos, que são poucos MB numa semana normal;
- a versão completa anterior, para poder voltar atrás.

Uma aplicação atualizada descarrega só os deltas. Uma aplicação nova, ou parada há muito tempo, descarrega a versão completa.

Para publicar, depois de reconstruir o índice (`python -m rag.indice`) e com a sessão do Hugging Face iniciada (`hf auth login`):

```bash
python -m rag.dados publicar --versao 2026-11-20 --enviar
```

- **Delta ou versão completa:** se o delta passar de 30% da versão completa, publica-se uma completa nova (para forçar, usar `--completo`).
- **Ordem do envio:** os ficheiros vão primeiro e o `versao.json` depois, para nunca apontar para um ficheiro que ainda não lá está. Só no fim se apagam os ficheiros que já não fazem falta e se limpa o histórico (`super_squash_history`), para o espaço não crescer.
- **Privacidade:** o caminho local do export sai da cópia publicada, porque tinha o nome do utilizador da máquina.
- **Base do próximo delta:** fica em `dist/dados/publicado.sqlite`. Não a apagues.
- **Descrição do repositório:** é o `rag/dados_cartao.md`, com a licença (as condições de cada fonte oficial).

Os deltas dão o mesmo índice que uma reconstrução de raiz. Isso é testado nos índices pequenos de `tests/test_dados.py` e no índice inteiro com `rag/navegador/equivalencia.py`.

## Site

`pages/index.html` é a página de descarga, publicada pelo workflow `.github/workflows/site.yml` no GitHub Pages. É preciso ativar uma vez: Settings → Pages → Source: GitHub Actions. Os botões apontam para os ficheiros da última Release.

## O que falta

- **Assinatura:** a aplicação não é assinada. O macOS (Gatekeeper) e o Windows (SmartScreen) avisam da primeira vez, e o site e o `COMO-USAR.md` explicam como passar esse aviso. Para assinar é preciso uma conta Apple Developer (99 USD por ano, com notarização) e um certificado de assinatura de código para Windows.
- **Testado:** a construção para Mac, o executável a responder a uma pergunta com o índice verdadeiro, e os pedidos da página (`tests/test_web.py`).
- **Não testado:**
  - a janela (pywebview);
  - a construção para Windows, que só corre no workflow;
  - as chamadas reais às três IAs, que precisam de chaves.
