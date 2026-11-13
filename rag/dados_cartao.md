---
license: other
license_name: condicoes-das-fontes-oficiais
license_link: https://github.com/joaobarrosodev/leis-portugal/blob/main/REUTILIZACAO.md
language:
  - pt
pretty_name: Leis de Portugal — índice de pesquisa
tags:
  - legal
  - portugal
  - legislacao
  - eur-lex
  - rag
size_categories:
  - 1M<n<10M
---

# Leis de Portugal: índice de pesquisa

O índice de pesquisa por artigo do projeto [leis-portugal](https://github.com/joaobarrosodev/leis-portugal), já construído. Serve a aplicação Leis de Portugal (Mac e Windows) e qualquer pessoa que queira pesquisar a legislação sem construir o índice. É gerado pelo `python -m rag.indice` e publicado pelo `python -m rag.dados`.

## O que tem

Um ficheiro SQLite com um pedaço por artigo (e por redação de cada artigo, com as datas em que esteve em vigor), cerca de 1,5 milhões de pedaços e uma tabela de pesquisa de texto (FTS5). Os diplomas vêm de duas fontes:

- **Diário da República Eletrónico:** legislação nacional e regional;
- **EUR-Lex / CELLAR:** atos da União Europeia em vigor.

Não inclui as decisões da CNPD nem os acórdãos do Tribunal Constitucional.

## Ficheiros

| Ficheiro | O que é |
|---|---|
| `versao.json` | O manifesto: a versão atual, a versão completa, os deltas desde ela e a completa anterior, com o tamanho e o sha256 de cada ficheiro |
| `completo-AAAA-MM-DD.sqlite.gz` | O índice inteiro numa data (gzip) |
| `delta-A-B.sqlite.gz` | Os diplomas que mudaram entre duas versões, para atualizar sem descarregar tudo |

A aplicação lê o `versao.json`. Se o índice local estiver numa versão da cadeia, descarrega só os deltas; senão, descarrega a versão completa. Ficam guardadas a versão completa atual, os deltas desde ela e a completa anterior. O histórico do repositório é limpo a cada publicação.

## Condições de reutilização

O código do projeto está sob a licença MIT. **Os textos e os metadados seguem as condições de cada fonte oficial**, resumidas no [`REUTILIZACAO.md`](https://github.com/joaobarrosodev/leis-portugal/blob/main/REUTILIZACAO.md):

- **Diário da República Eletrónico:** acesso universal e gratuito (artigo 3.º do Decreto-Lei n.º 83/2016) e regime de dados abertos (Lei n.º 68/2021). Atribuição: "Diário da República Eletrónico — Imprensa Nacional-Casa da Moeda".
- **EUR-Lex:** reutilização permitida com indicação da fonte, segundo o aviso jurídico do EUR-Lex. Atribuição: "União Europeia, EUR-Lex / Publicações da União Europeia".

## Avisos

- **Não é a versão oficial.** Só a edição eletrónica do Diário da República e o Jornal Oficial da União Europeia fazem fé. As versões consolidadas são instrumentos de consulta.
- **Há texto em vigor feito pelo projeto.** Nos diplomas alterados que o DRE não consolida, o projeto produziu o texto em vigor, verificado às cegas e marcado como **sem valor oficial**.
- **Não é aconselhamento jurídico.**
- **Pode ter dados pessoais.** A legislação publicada menciona pessoas (nomeações, louvores). Se reutilizares os dados para outros fins, avalia as obrigações do RGPD aplicáveis ao teu caso.
