
# Leis de Portugal

**Legislação portuguesa em formato aberto, estruturado e versionado.**

O `leis-portugal` é um projeto open-source que pretende reunir e organizar legislação portuguesa num repositório público, com textos legíveis por pessoas e máquinas, metadados normalizados, ligações às fontes oficiais e um histórico de alterações verificável.

O objetivo é tornar o ordenamento jurídico português mais acessível, pesquisável e reutilizável, criando uma base que possa servir cidadãos, juristas, investigadores, jornalistas, programadores e aplicações de inteligência artificial.

> **Estado do projeto:** em desenvolvimento. A cobertura documental, as fontes integradas e a automatização disponíveis devem ser consultadas nos relatórios de progresso e cobertura do repositório.

## Índice

- [Objetivos](#objetivos)
- [Princípios](#princípios)
- [Fontes oficiais](#fontes-oficiais)
- [Âmbito da coleção](#âmbito-da-coleção)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Formato dos documentos](#formato-dos-documentos)
- [Consultar a legislação](#consultar-a-legislação)
- [Atualização automática](#atualização-automática)
- [Histórico e versões](#histórico-e-versões)
- [Cobertura e progresso](#cobertura-e-progresso)
- [Qualidade e validação](#qualidade-e-validação)
- [Desenvolvimento](#desenvolvimento)
- [Contribuir](#contribuir)
- [Limitações e utilização responsável](#limitações-e-utilização-responsável)
- [Licenciamento](#licenciamento)
- [Agradecimentos](#agradecimentos)

## Objetivos

O projeto procura construir, de forma incremental, uma coleção organizada de diplomas legais portugueses que seja:

- **Aberta:** acessível gratuitamente através do GitHub.
- **Estruturada:** organizada por tipo de diploma, data, número e outras propriedades relevantes.
- **Legível:** disponível em formatos simples, como Markdown, sem exigir software jurídico proprietário.
- **Rastreável:** cada documento deve identificar a respetiva fonte oficial.
- **Versionada:** o Git permite consultar as alterações registadas no próprio repositório.
- **Automatizável:** recolha, conversão, normalização e validação através de ferramentas reproduzíveis.
- **Auditável:** as lacunas conhecidas, os erros e o estado da cobertura devem ser documentados.
- **Preparada para integração:** os dados devem poder ser utilizados em motores de pesquisa, sistemas de análise documental e aplicações de IA.

A ambição é evoluir para uma base abrangente do ordenamento jurídico português, sem confundir o objetivo de cobertura total com aquilo que já foi efetivamente recolhido e validado.

## Princípios

### A fonte oficial é a referência

Cada documento deve incluir uma ligação para a sua publicação ou página oficial. Quando existam várias versões, devem distinguir-se o diploma original, as alterações posteriores e eventuais textos consolidados.

### Não confundir publicação com consolidação

A publicação oficial de um diploma e uma versão consolidada são representações diferentes.

Uma consolidação pode facilitar a leitura da redação resultante de alterações sucessivas, mas não deve ser apresentada como se fosse o diploma original. Sempre que possível, devem ser preservadas as referências necessárias para consultar ambas as versões.

### Não inventar cobertura

O repositório deve indicar explicitamente o que foi recolhido, o que está validado, o que falta e quais as limitações conhecidas. A existência de uma categoria na estrutura não significa que a respetiva coleção esteja completa.

### Automatizar com transparência

Os processos automáticos devem ser reproduzíveis, testáveis e respeitar as condições de acesso e reutilização das fontes. Erros de conversão não devem ser ocultados.

## Fontes oficiais

O projeto privilegia fontes primárias e páginas institucionais.

| Fonte | Utilização prevista |
|---|---|
| [Diário da República Eletrónico](https://diariodarepublica.pt/) | Publicação oficial de diplomas, pesquisa documental e consulta de legislação consolidada. |
| [EUR-Lex](https://eur-lex.europa.eu/) | Direito da União Europeia, regulamentos, diretivas, decisões e outros atos europeus relevantes. |
| [Assembleia da República](https://www.parlamento.pt/) | Informação parlamentar e trabalhos preparatórios, quando relevantes para o âmbito do projeto. |
| [Tribunal Constitucional](https://www.tribunalconstitucional.pt/) | Decisões e jurisprudência constitucional, numa coleção separada da legislação. |
| [Supremo Tribunal de Justiça](https://www.stj.pt/) | Jurisprudência e decisões judiciais, quando integradas. |
| [Supremo Tribunal Administrativo](https://www.stadministrativo.pt/) | Jurisprudência administrativa e fiscal, quando integrada. |
| [Comissão Nacional de Proteção de Dados](https://www.cnpd.pt/) | Orientações e informação institucional relevante, devidamente identificadas como tal. |

Esta lista identifica fontes de referência e possíveis áreas de integração; não constitui uma declaração de que todas as fontes já estão ligadas aos processos automáticos.

Cada integração deve documentar:

- A entidade responsável pela fonte.
- O endereço e o mecanismo de acesso utilizados.
- Os tipos de documentos disponíveis.
- O período temporal abrangido.
- A data da última recolha bem-sucedida.
- As condições de acesso e reutilização aplicáveis.
- As limitações técnicas ou documentais conhecidas.

O acesso público a uma página não implica, por si só, que todos os seus conteúdos possam ser recolhidos ou redistribuídos sem restrições.

## Âmbito da coleção

A estrutura foi pensada para crescer por etapas.

### 1. Legislação nacional

- Constituição da República Portuguesa.
- Leis constitucionais e leis de revisão constitucional.
- Leis e leis orgânicas.
- Decretos-leis.
- Decretos regulamentares.
- Decretos e outros atos normativos publicados oficialmente.
- Resoluções, portarias, despachos e regulamentos, de acordo com a sua natureza e o âmbito definido.
- Diplomas de aprovação, alteração, suspensão, revogação ou republicação de outros atos.

A classificação deve respeitar a designação oficial e a natureza jurídica de cada instrumento.

### 2. Direito da União Europeia

- Regulamentos.
- Diretivas.
- Decisões.
- Tratados e outros atos relevantes.
- Referências à transposição nacional, quando verificáveis.

Os atos europeus devem manter os seus identificadores próprios, como o número CELEX, quando disponível, e a ligação ao EUR-Lex.

### 3. Legislação regional e local

Quando existam fontes adequadas e condições de reutilização compatíveis, poderão ser integrados atos normativos das Regiões Autónomas e dos municípios.

Esta coleção exige atenção especial às diferenças entre entidades emissoras, séries de publicação, nomenclaturas e sistemas documentais.

### 4. Regulamentação e atos de entidades públicas

Poderão ser incluídos atos regulamentares de entidades administrativas e reguladoras, desde que identificados separadamente da legislação parlamentar e governamental.

### 5. Jurisprudência e materiais complementares

Decisões judiciais, acórdãos, jurisprudência uniformizada, orientações administrativas, trabalhos preparatórios e documentos explicativos não devem ser confundidos com diplomas legislativos.

Se forem integrados, devem ter diretórios, metadados e regras de validação próprios.

## Estrutura do repositório

```text
leis-portugal/
├── config/
│   ├── sources.yml            # registo das fontes, estado e condições de reutilização
│   └── document_types.yml     # tipos canónicos de diploma, grafias alternativas e pastas
├── schemas/                   # JSON Schema dos registos e das fontes
├── data/
│   ├── portugal/              # legislação nacional (1.ª Série do DR)
│   │   ├── leis/<ano>/lei-29-2026.md
│   │   ├── decretos-leis/<ano>/decreto-lei-140-2009.md
│   │   ├── portarias/ … declaracoes-retificacao/ … (um diretório por tipo)
│   │   └── serie-ii/          # documentos da 2.ª Série, que têm numeração própria
│   ├── regional/
│   │   ├── acores/            # legislação regional publicada no DR
│   │   └── madeira/
│   └── european_union/        # regulamentos, diretivas e decisões (EUR-Lex), mesma informação que os diplomas portugueses
│       ├── regulations/<ano>/regulamento-ue-2016-679.md
│       ├── directives/<ano>/diretiva-ue-2022-2555.md
│       └── decisions/<ano>/decisao-ue-2019-1234.md
├── reports/                   # cobertura, progresso e falhas, gerados a partir de data/
├── src/leis_portugal/         # recolha, conversão, validação e relatórios
└── tests/
```

Cada diploma é um ficheiro `data/<âmbito>/<tipo>/<ano de publicação>/<tipo>-<número>.md`. Quando dois diplomas distintos teriam o mesmo nome (por exemplo, numerações repetidas em diplomas antigos), o segundo recebe o id do DRE como sufixo.

## Arquitetura

O código em `src/leis_portugal/` está organizado em camadas, e cada camada só depende das que estão abaixo dela:

```text
cli/             comandos: lê argumentos, chama um serviço, imprime o resultado
services/        casos de uso: recolher (DRE, EUR-Lex, histórico consolidado), importar, ligar, validar, relatar
sources/         uma pasta por fonte, separando transporte (client.py) e conversão para o modelo (mapper.py)
  dre/           cliente OutSystems, mapeamento, HTML -> Markdown, fragmentos consolidados
  eurlex/        cliente CELLAR (SPARQL), mapeamento, XHTML -> Markdown
  legalize/      importação inicial: leitura de um clone local do legalize-pt (não é uma fonte)
infrastructure/  HTTP comum (espera e novas tentativas), Markdown/YAML, esquemas, configuração e o repositório `Acervo`
domain/          modelo tipado `LegalRecord`, formato do histórico de versões, identificadores, tipos de diploma, relações; sem rede nem ficheiros
```

- **`LegalRecord`** é o modelo de um registo. `from_dict`/`to_dict` fazem a ida e volta exata do front matter, por isso o formato em disco é estável.
- **`Acervo`** é o único sítio que lê e escreve em `data/`. Trata dos caminhos, do índice id → ficheiro, da validação, das colisões, da precedência entre fontes (consolidado > publicado; DRE > importação), da preservação de datas e dos ficheiros de versões.
- **As fontes** devolvem um `SourceDocument` (registo + texto + bytes oficiais) e não escrevem nada. Os serviços decidem como gravar através de uma `SavePolicy`.
- **Erros:** os erros esperados (`LeisPortugalError`: fonte, armazenamento, registo inválido) são registados por documento e a recolha continua; qualquer outro erro é um bug e interrompe a execução.

## Formato dos documentos

Cada ficheiro é Markdown com metadados YAML, validados por [`schemas/legal_document.schema.json`](schemas/legal_document.schema.json). Exemplo (resumido) de um registo real:

```yaml
---
schema_version: '1.0'
id: pt:dre:494543:por
title: Decreto-Lei n.º 140/2009
summary: Estabelece o regime jurídico dos estudos, projectos, relatórios, obras ou intervenções sobre bens culturais…
jurisdiction: portugal
territory: null
document_type: decreto-lei
document_type_label: Decreto-Lei
issuing_authority: [Ministério da Cultura]
official_number: 140/2009
publication_date: '2009-06-15'
publication:
  gazette: Diário da República
  reference: Diário da República n.º 113/2009, Série I de 2009-06-15
  pages: 3653 - 3659
  pdf_url: https://files.diariodarepublica.pt/1s/2009/06/11300/0365303659.pdf
legal_status: in_force
version: {kind: consolidated, consolidation_date: '2024-11-22'}
identifiers:
  eli: https://data.dre.pt/eli/dec-lei/140/2009/p/cons/20241122/pt/html
  dre: '494543'
  dre_path: /dr/detalhe/decreto-lei/140-2009-494543
source: {id: dre, official_url: https://diariodarepublica.pt/dr/detalhe/decreto-lei/140-2009-494543}
subjects: [Património Cultural, Vistoria]
relationships:
- type: amended_by
  target: pt:dre:897548401:por
  label: Alterados a partir de 23 de novembro de 2024 os artigos 17.º, 18.º, … pelo(a) Decreto-Lei n.º 90/2024 …
  date: '2024-11-22'
- type: cites
  target: eli:http://data.dre.pt/eli/lei/107/2001/09/08/p/dre
article_structure: {article_count: 43, section_count: 6}
---

# Decreto-Lei n.º 140/2009

###### Artigo 1.º — Objecto e âmbito de aplicação
```

### Regras para os metadados

- `id`: `pt:dre:<id DRE>:por` para diplomas portugueses e `eu:celex:<CELEX>:por` para atos da UE, ambos estáveis entre versões.
- `document_type`: vocabulário controlado em `config/document_types.yml`; as grafias do DRE e do legalize-pt (`declaracao-rectificacao`, `…-extracto`, …) são normalizadas.
- `jurisdiction` e `territory`: `regional` com `acores`/`madeira` para legislação das regiões autónomas.
- `publication`: jornal oficial, número, série, suplemento, páginas e PDF oficial.
- `version.kind`: `original` (texto publicado) ou `consolidated` (consolidação do DRE, com `consolidation_date`).
- `relationships`: `amended_by`/`amends`, `repealed_by`/`repeals`, `corrected_by`/`corrects`, `cites`/`cited_by`, `transposes`/`transposed_by` (diretivas da UE transpostas por diplomas portugueses) e `interpreted_by` (acórdãos do TJUE sobre um ato da UE). O alvo é um id do acervo (`pt:dre:…`, `celex:…`) ou, quando a fonte só dá texto, uma referência por número (`pt:numero:decreto-lei:40-A/2026`) ou ELI (`eli:…`).
- `source`, `provenance` e `integrity`: a fonte oficial (DRE ou EUR-Lex), quando e como foi obtido, e o SHA-256 dos bytes recebidos (`official_source_content_bytes` na recolha direta; `imported_derived_markdown` para o texto da importação inicial, ainda por recolher diretamente).

Não se inferem datas, estados de vigência, revogações ou outros efeitos jurídicos apenas a partir do título ou da existência de alterações posteriores.

### Identificação das versões

Quando uma fonte disponibilizar mais do que uma representação do mesmo diploma, estas devem ser distinguidas explicitamente.

Exemplos de categorias documentais:

- `original`: texto do ato publicado originalmente.
- `consolidado`: texto consolidado disponibilizado por uma fonte.
- `alteracao`: ato que modifica outro diploma.
- `historico`: versão associada a um momento temporal específico.

Uma versão consolidada não deve substituir silenciosamente o original. Sempre que possível, devem existir referências cruzadas entre o diploma de origem, os atos modificativos e a versão consolidada.

## Consultar a legislação

### No GitHub

É possível navegar pelos diretórios, abrir ficheiros Markdown e utilizar a pesquisa do GitHub para localizar diplomas por título, número, identificador ou expressões do texto.

A qualidade dos resultados depende da cobertura do acervo e da forma como os documentos foram normalizados.

### Clonar o repositório

```bash
git clone https://github.com/joaobarrosodev/leis-portugal.git
cd leis-portugal
```

Substitua `joaobarrosodev` pelo nome de utilizador ou organização que aloja o projeto.

### Pesquisar localmente

Depois de clonar o repositório, pode pesquisar o conteúdo com ferramentas habituais.

Com `grep`:

```bash
grep -Rli --include="*.md" "proteção de dados" data/portugal/leis/
```

Com `find`:

```bash
find data/portugal/decretos-leis/2024 -type f -name "*.md"
```

## Atualização automática

A atualização do acervo deve ser assegurada por processos automatizados, com execução controlada e resultados auditáveis.

O fluxo de trabalho previsto é:

1. Consultar as fontes autorizadas e os respetivos índices.
2. Identificar documentos novos ou alterados.
3. Recolher o conteúdo e os metadados disponíveis.
4. Preservar a ligação à origem e, quando permitido, uma referência ao documento original.
5. Converter o conteúdo para o formato definido pelo projeto.
6. Normalizar os metadados e a organização dos ficheiros.
7. Validar a estrutura, os identificadores e a integridade dos documentos.
8. Produzir relatórios de recolha, alterações, falhas e cobertura.
9. Registar as alterações no Git após as verificações aplicáveis.

### GitHub Actions

O workflow [`.github/workflows/atualizacao-diaria.yml`](.github/workflows/atualizacao-diaria.yml) corre todos os dias às 06:15 UTC e executa [`scripts/atualizacao_diaria.sh`](scripts/atualizacao_diaria.sh) para o dia anterior (hora de Lisboa):

1. `leis-portugal collect dre` — diplomas da 1.ª Série do Diário da República.
2. `leis-portugal collect eurlex` — regulamentos, diretivas e decisões publicados no Jornal Oficial da UE.
3. `leis-portugal link` — ligações entre os diplomas portugueses e os atos da UE.
4. `leis-portugal validate` — se a validação falhar, nada é publicado.
5. `leis-portugal reports` — cobertura e progresso.

As alterações são publicadas no `main` num commit "Atualização diária: DRE e EUR-Lex de AAAA-MM-DD" feito por `github-actions[bot]`. Se uma das recolhas falhar (por exemplo, depois de um deploy do DRE), o que foi recolhido e validado é publicado na mesma e a execução fica marcada como falhada.

Para recuperar dias em falta, execute o workflow manualmente em *Actions → Atualização diária → Run workflow* com as datas `from` e `to`. Localmente:

```bash
scripts/atualizacao_diaria.sh 2026-10-01 2026-10-22
```

## Histórico e versões

O Git é utilizado para registar as alterações aos ficheiros e aos processos de recolha.

Este histórico pode ajudar a identificar:

- Quando foi introduzido ou modificado um ficheiro.
- Que alterações textuais foram registadas.
- Quando foi corrigido um erro de conversão.
- Que alterações foram efetuadas aos metadados.
- Que alterações resultaram de uma nova recolha.

O histórico do repositório não deve ser interpretado automaticamente como um registo jurídico completo da vigência de cada diploma. A data de um commit é a data do registo da alteração no Git, não necessariamente a data de publicação, entrada em vigor ou produção de efeitos jurídicos.

Sempre que possível, o projeto deve manter as datas e referências oficiais separadas das datas de recolha e de versionamento.

## Cobertura e progresso

A cobertura deve ser mensurável e verificável.

O ficheiro `COBERTURA.md` deve documentar, progressivamente:

- As fontes integradas.
- Os tipos de diplomas abrangidos.
- Os intervalos temporais disponíveis.
- As categorias ainda não recolhidas.
- As lacunas conhecidas.
- Os documentos inacessíveis ou sem texto disponível.
- As limitações de cada processo de recolha.

O ficheiro `PROGRESSO.md` deve apresentar o estado de implementação das fontes e das tarefas, distinguindo funcionalidades planeadas, em desenvolvimento, operacionais e validadas.

Quando existirem dados suficientes, poderão ser publicadas estatísticas sobre:

- Número de documentos recolhidos.
- Número de documentos validados.
- Distribuição por tipo de diploma e ano.
- Distribuição por fonte.
- Última data de atualização.
- Falhas de recolha e conversão.
- Cobertura por categoria e período temporal.

As estatísticas devem ser geradas a partir dos dados existentes, com critérios de contagem documentados. Não devem ser utilizadas estimativas apresentadas como contagens verificadas.

## Qualidade e validação

A conversão automática pode introduzir erros. Entre os problemas possíveis encontram-se:

- Caracteres incorretos ou ausentes.
- Problemas de codificação.
- Numeração de artigos alterada.
- Tabelas e listas mal convertidas.
- Perda de notas, anexos ou elementos gráficos.
- Quebras de parágrafo inadequadas.
- Confusão entre redações originais e consolidadas.
- Metadados incompletos ou incorretos.

Para reduzir estes riscos, o projeto deve implementar testes automáticos para:

- Validar o esquema dos metadados.
- Confirmar a presença da fonte e dos identificadores disponíveis.
- Detetar ficheiros duplicados.
- Verificar datas e formatos.
- Identificar conteúdos vazios ou suspeitos.
- Confirmar a integridade dos ficheiros.
- Detetar alterações inesperadas durante novas recolhas.
- Verificar a consistência das referências entre diplomas.

Os testes automáticos ajudam a detetar problemas, mas não substituem a revisão do conteúdo nem confirmam, por si só, a validade jurídica de um documento.

## Desenvolvimento

### Requisitos

Python 3.11 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Executar testes

```bash
ruff check src tests
```

```bash
python -m pytest --cov=leis_portugal
```

Os testes não acedem à rede: o DRE, o CELLAR e o legalize-pt são simulados com respostas gravadas. O workflow [`testes.yml`](.github/workflows/testes.yml) corre o lint e os testes em cada push e pull request, com cobertura mínima de 85%.

### Executar os processos de recolha

Recolher do Diário da República (1.ª Série) uma data, um intervalo ou um diploma:

```bash
leis-portugal collect dre --date 2026-10-20
```

```bash
leis-portugal collect dre --from 2026-10-01 --to 2026-10-22
```

```bash
leis-portugal collect dre --ref /dr/detalhe/decreto-lei/140-2009-494543
```

Para cada diploma são recolhidos o texto, os metadados, as alterações e retificações registadas na análise jurídica do DRE e os descritores temáticos (`--no-relations` e `--no-subjects` desligam os dois últimos). O DRE não tem API pública: o conector usa os endpoints internos da aplicação web, a 1 pedido por segundo. Se o DRE mudar esses endpoints, a recolha falha com um erro explícito em vez de gravar um dia vazio.

Recolher atos da União Europeia (EUR-Lex/CELLAR), com a mesma informação que os diplomas portugueses (texto do JO ou consolidado, EuroVoc, autores, publicação no JO, vigência e relações nos dois sentidos):

```bash
leis-portugal collect eurlex --date 2026-10-21
```

```bash
leis-portugal collect eurlex --from 2026-01-01 --to 2026-10-22 --workers 4
```

```bash
leis-portugal collect eurlex --referenced --workers 4
```

```bash
leis-portugal collect eurlex --celex 32016R0679
```

`--from`/`--date` descobrem os regulamentos, diretivas e decisões publicados no Jornal Oficial nesse período (`--types RLD` para filtrar). `--referenced` recolhe os atos da UE que a legislação portuguesa cita ou transpõe e que ainda não estão no acervo, começando pelos mais referidos. Quando existe versão consolidada, é esse o texto guardado, tal como nos diplomas portugueses consolidados pelo DRE; `--no-consolidated` usa sempre o texto do JO.

#### Histórico de versões

Para cada diploma consolidado guarda-se, ao lado do registo, `<diploma>.versoes.json` com todas as versões por data de entrada em vigor: os atos que produziram cada versão, as modificações (Altera/Adita/Revoga…) e cada versão de cada artigo uma só vez. O registo `.md` fica com o texto em vigor hoje e um resumo em `version_history`.

Diplomas portugueses (legislação consolidada do DRE; `--stale` só volta a recolher os que o DRE atualizou):

```bash
leis-portugal collect dre-consolidated --workers 4
```

```bash
leis-portugal collect dre-consolidated --stale
```

Atos da UE (versões consolidadas do EUR-Lex, `0…-AAAAMMDD`, mais o texto original do JO quando a primeira consolidação é posterior):

```bash
leis-portugal collect eurlex-consolidated --workers 4
```

Texto de um diploma ou ato numa data, ou a lista das versões:

```bash
leis-portugal version-at pt:dre:477358:por --date 1990-01-01
```

```bash
leis-portugal version-at eu:celex:32002L0058:por --list
```

Ligar os atos da UE aos diplomas portugueses (escreve `transposed_by` e `cited_by` em cada ato da UE, a partir das referências detetadas no texto português):

```bash
leis-portugal link
```

#### Importação inicial

O acervo arrancou com o texto do DRE já convertido pelo projeto [legalize-pt](https://github.com/legalize-dev/legalize-pt), para não ter de recolher ~172 mil diplomas um a um. O legalize-pt **não é uma fonte**: a fonte desses registos é o DRE, e a importação fica registada só em `provenance` e em `integrity.source_sha256_scope: imported_derived_markdown`. Sempre que um diploma é recolhido diretamente do DRE, o texto importado é substituído; o contrário nunca acontece. O comando fica disponível para refazer o arranque a partir de um clone local:

```bash
leis-portugal import legalize --path ../legalize-pt
```

Validar e gerar relatórios:

```bash
leis-portugal validate
```

```bash
leis-portugal reports
```

## Contribuir

Contribuições são bem-vindas, incluindo:

- Integração de novas fontes oficiais.
- Melhoria dos processos de recolha.
- Correção de erros de conversão.
- Normalização de metadados.
- Implementação de testes.
- Documentação de lacunas.
- Melhoria da pesquisa e da organização do acervo.
- Identificação de problemas de qualidade ou de reutilização.

### Processo recomendado

1. Consulte as issues existentes e verifique se o problema já foi identificado.
2. Crie uma branch para a alteração.
3. Implemente a mudança e os testes relevantes.
4. Execute as validações disponíveis.
5. Documente a fonte, os limites e os resultados obtidos.
6. Abra um pull request com uma descrição clara.

### Requisitos para novas fontes

Uma nova integração deve, sempre que possível:

- Utilizar uma fonte oficial ou institucional adequada.
- Documentar o mecanismo de acesso.
- Respeitar as condições de utilização e reutilização.
- Preservar os identificadores e as ligações de origem.
- Evitar duplicações.
- Distinguir dados ausentes de dados não aplicáveis.
- Permitir repetir a recolha sem corromper o acervo.
- Incluir testes e documentação das limitações.

Não introduza credenciais, dados pessoais desnecessários, conteúdo obtido por contorno de restrições de acesso ou ficheiros cuja redistribuição não esteja devidamente avaliada.

## Limitações e utilização responsável

Este repositório tem fins informativos, documentais, educativos e de investigação.

**O conteúdo disponibilizado não constitui aconselhamento jurídico nem substitui a consulta das fontes oficiais.**

Em particular:

- Podem existir documentos em falta.
- A conversão automática pode conter erros.
- Uma versão consolidada pode não refletir todas as alterações ou questões de vigência relevantes para um caso concreto.
- A publicação de um diploma não significa necessariamente que todas as suas disposições estejam atualmente em vigor.
- A ausência de um diploma no repositório não significa que não exista ou que não seja aplicável.
- O histórico Git não certifica a vigência nem a eficácia jurídica dos textos.
- A cobertura e a frequência de atualização variam conforme as fontes integradas.

Antes de citar ou utilizar um documento num contexto jurídico, confirme o texto, a publicação, as alterações, a entrada em vigor e as disposições transitórias nas fontes oficiais pertinentes.

Para o Diário da República, consulte [diariodarepublica.pt](https://diariodarepublica.pt/). Para o direito da União Europeia, consulte [EUR-Lex](https://eur-lex.europa.eu/).

## Licenciamento

O código, os scripts, os esquemas e a documentação original do projeto são disponibilizados nos termos da licença indicada no ficheiro [`LICENSE`](LICENSE).

A licença do código não concede automaticamente direitos sobre conteúdos de terceiros, bases de dados, elementos gráficos ou outros materiais incorporados no repositório.

Antes de redistribuir conteúdos recolhidos, devem ser verificadas as condições legais de reutilização aplicáveis à fonte e ao tipo de material. As referências às fontes oficiais devem ser preservadas sempre que possível.

Se forem adotadas licenças ou condições específicas para determinados conjuntos de dados, estas devem ser documentadas de forma clara.

## Agradecimentos

Este projeto inspira-se em iniciativas de disponibilização aberta de legislação, incluindo o repositório brasileiro [`ctresb/leis`](https://github.com/ctresb/leis), e procura adaptar essa abordagem à realidade jurídica e documental portuguesa.

O objetivo é contribuir para um ecossistema em que a legislação seja mais fácil de consultar, comparar, pesquisar e utilizar no desenvolvimento de ferramentas úteis à sociedade.

---

**Legislação acessível. Fontes rastreáveis. Dados estruturados.**
