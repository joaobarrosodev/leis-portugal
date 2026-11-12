# Reutilizar os dados

Este guia resume o que se aplica a quem reutiliza os dados do acervo — num site, numa base de dados, num índice de pesquisa ou numa aplicação de IA. **Não é aconselhamento jurídico:** confirme sempre as condições em vigor em cada fonte.

## Duas licenças diferentes

| O quê | Condições |
|---|---|
| Código, scripts, esquemas, configuração e documentação do projeto | Licença MIT ([`LICENSE`](LICENSE)) |
| Textos e metadados recolhidos das fontes oficiais (`data/`, `exports/`) | As condições de cada fonte (abaixo); a licença MIT **não** se aplica |

## Condições por fonte

Cada registo traz as condições da sua fonte no bloco `reuse`:

```yaml
reuse:
  status: permitted                      # ou permitted_with_conditions
  attribution: Diário da República Eletrónico — Imprensa Nacional-Casa da Moeda
  reference: http://data.dre.pt/eli/dec-lei/83/2016/p/dr/pt/html
  notes: Acesso universal e gratuito ao Diário da República (…)
```

### Diário da República Eletrónico (DRE)

Inclui o catálogo do Jornal Oficial dos Açores que o DRE guarda.

- **Base:** acesso universal e gratuito ao Diário da República ([artigo 3.º do Decreto-Lei n.º 83/2016](http://data.dre.pt/eli/dec-lei/83/2016/p/dr/pt/html)) e regime de dados abertos ([Lei n.º 68/2021](https://diariodarepublica.pt/dr/detalhe/lei/68-2021-170221042)).
- **Atribuição:** "Diário da República Eletrónico — Imprensa Nacional-Casa da Moeda".
- **Atenção:** a edição eletrónica do Diário da República é a que faz fé. O texto deste repositório é uma conversão para Markdown; os textos consolidados do DRE são instrumentos de consulta.

### EUR-Lex / CELLAR

- **Base:** o [aviso jurídico do EUR-Lex](https://eur-lex.europa.eu/content/legal-notice/legal-notice.html), que permite a reutilização com indicação da fonte.
- **Atribuição:** "União Europeia, EUR-Lex / Publicações da União Europeia".
- **Atenção:** só os textos publicados no Jornal Oficial da União Europeia fazem fé. As versões consolidadas são instrumentos de documentação sem valor jurídico. Não apresente material editorial como texto oficial.

### Comissão Nacional de Proteção de Dados (CNPD)

Decisões em `data/entidades/cnpd/` (pareceres, deliberações, diretrizes, regulamentos, registos e autorizações).

- **Base:** os [avisos legais do site da CNPD](https://www.cnpd.pt/avisos-legais-e-outras-informacoes/). A reprodução total ou parcial é permitida se a distribuição for gratuita, os documentos se mantiverem íntegros e o site for citado com a menção de direitos reservados.
- **Limites:** só para fins pessoais, associativos ou profissionais. **Não são permitidos fins comerciais nem publicitários.**
- **Atribuição:** "Comissão Nacional de Proteção de Dados (www.cnpd.pt) — todos os direitos reservados".
- **Atenção:** são decisões de uma entidade administrativa independente, não legislação. Só a cópia certificada tem valor legal. O texto é extraído do PDF; os PDF digitalizados ficam só com os metadados e a ligação ao PDF.

### Tribunal Constitucional

Acórdãos em `data/jurisprudencia/tribunal-constitucional/`.

- **Base:** o site do Tribunal Constitucional declara todos os direitos reservados e autoriza a reprodução **para fins privados**, com citação da fonte e da natureza não autêntica do texto. Por isso, o bloco `reuse` destes registos tem `status: restricted`.
- **Atribuição:** "Tribunal Constitucional (www.tribunalconstitucional.pt) — todos os direitos reservados".
- **Atenção:** o texto do site não tem carácter autêntico. A versão oficial é a dos arquivos do Tribunal e, para os acórdãos publicados no Diário da República, a do DR (o registo liga-lhe com `published_in`). Antes de reutilizar estes textos fora do uso privado, confirme as condições com o Tribunal.
- **Pedido ao Tribunal:** em 12/11/2026 o projeto pediu ao Tribunal (Responsável pelo acesso à informação) a confirmação de que esta reutilização é aceite: acesso gratuito, sem fins comerciais, texto sem alterações, fonte e ligação a cada acórdão, menção de que não é a versão oficial, recolha a 1 pedido por segundo. Se o Tribunal não aceitar, o texto dos acórdãos sai do repositório e ficam só o número, a data e a ligação ao site. Enquanto não houver resposta, o estado mantém-se `restricted`.

## Boas práticas

- **Mantenha a atribuição** e a ligação à fonte oficial (`source.official_url`) junto de cada texto que reutiliza — também em índices de pesquisa, embeddings e respostas geradas por IA.
- **Distinga publicação de consolidação:** `version.kind` diz se o texto é o publicado (`original`) ou uma consolidação (`consolidated`, com `consolidation_date`).
- **Mostre a qualidade do texto:** um registo pode ter só o PDF oficial ou só os metadados (`text_quality` na exportação; nota "Fonte sem texto" no registo).
- **Não apresente o conteúdo como aconselhamento jurídico** nem como a versão oficial.
- **Indique a data da recolha** (`source.retrieved_at`) quando a atualidade importa.

## Dados pessoais

A legislação publicada pode mencionar pessoas (nomeações, louvores, acórdãos). Se reutilizar esses dados para outros fins, avalie as obrigações do RGPD aplicáveis ao seu caso.
