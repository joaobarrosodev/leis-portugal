# Contribuir para o Leis de Portugal

Obrigado pelo interesse! Este guia explica como preparar o ambiente, as convenções do código e dos dados, e o que esperar de um pull request.

## O que é útil

- Correções de conversão (texto, tabelas, artigos) e de metadados.
- Novas fontes oficiais (ver [Acrescentar uma fonte](#acrescentar-uma-fonte)).
- Melhorias aos conectores, à resolução de relações, à exportação e aos relatórios.
- Testes, documentação e identificação de lacunas.

Antes de começar algo grande, abra uma issue a descrever a ideia: evita trabalho em duplicado e permite discutir o âmbito.

## Preparar o ambiente

Python 3.11 ou superior.

```bash
git clone https://github.com/joaobarrosodev/leis-portugal.git
cd leis-portugal
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Verificar antes de abrir um pull request

```bash
ruff check src tests
```

```bash
python -m pytest --cov=leis_portugal --cov-fail-under=85
```

```bash
leis-portugal validate
```

O CI ([`testes.yml`](.github/workflows/testes.yml)) corre o lint e os testes com cobertura mínima de 85% em cada push e pull request.

## Convenções do código

- **Camadas** (ver "Arquitetura" no [README](README.md#arquitetura)): `cli/` → `services/` → `sources/` e `infrastructure/` → `domain/`. Uma camada só usa as que estão abaixo. O `domain/` não acede à rede nem a ficheiros.
- **Só o `Acervo` escreve em `data/`.** As fontes devolvem um `SourceDocument` e não gravam nada.
- **Erros esperados** são `LeisPortugalError` (fonte, armazenamento, registo inválido): são registados por documento, com motivo, e a recolha continua. Qualquer outro erro é um bug.
- **Os testes não acedem à rede:** o DRE e o CELLAR são simulados com respostas gravadas (`tests/fixtures/`). Um teste novo de um conector deve usar uma resposta real gravada.
- **Português de Portugal** nas mensagens, na documentação e nos comentários; identificadores do código em inglês.
- **Estilo:** `ruff` (configuração no `pyproject.toml`), linhas até 140 caracteres. Comentários só onde o código não se explica sozinho.
- **Vocabulário em configuração:** tipos de diploma, grafias do DRE, códigos de ELI e pastas estão em `config/document_types.yml`, não no código.

## Convenções dos dados

- **Não edite à mão os ficheiros de `data/`.** Os registos são gerados pelos conectores; uma correção manual desaparece na recolha seguinte. Corrija o conector ou a conversão e volte a recolher.
- **A fonte oficial é a referência.** Cada registo liga à publicação oficial e guarda o SHA-256 dos bytes recebidos.
- **Não inferir.** Datas, estados de vigência, revogações e outros efeitos jurídicos só entram quando a fonte os indica.
- **Distinguir dados em falta de dados não aplicáveis.** Quando a fonte não tem o texto, o registo diz isso ("Fonte sem texto") em vez de ficar vazio.
- **Alterações ao formato** (novos campos, mudanças de significado, ficheiros gerados) entram no [`CHANGELOG.md`](CHANGELOG.md); uma alteração incompatível ao esquema muda `schema_version`.

## Acrescentar uma fonte

1. Registe a fonte em [`config/sources.yml`](config/sources.yml): entidade, mecanismo de acesso, âmbito verificado, limites conhecidos e condições de reutilização (validado por `schemas/source_record.schema.json`).
2. Crie `src/leis_portugal/sources/<fonte>/` com `client.py` (transporte, sem conversão) e `mapper.py` (conversão para `LegalRecord`, sem rede).
3. Use o `HttpClient` comum, com espera entre pedidos e novas tentativas, e respeite os limites da fonte.
4. Acrescente o serviço de recolha em `services/` e o comando em `cli/`.
5. Grave respostas reais em `tests/fixtures/<fonte>/` e teste o mapeamento e a recolha de ponta a ponta.
6. Documente no README a utilização e as limitações, e no `CHANGELOG.md` o que muda nos dados.

Não introduza credenciais, dados pessoais desnecessários, conteúdo obtido contornando restrições de acesso, nem conteúdo cuja redistribuição não esteja avaliada (ver [`REUTILIZACAO.md`](REUTILIZACAO.md)).

## Pull requests

- Um assunto por pull request, com uma descrição do problema, da solução e de como foi verificado.
- Inclua testes para o comportamento novo ou corrigido.
- Se a alteração muda dados em massa (por exemplo, uma nova conversão), diga quantos registos muda e mostre um exemplo antes/depois.

## Reportar problemas

Abra uma issue com: o registo (`id` ou caminho em `data/`), o que está errado, o que devia estar e a ligação à fonte oficial que o confirma.
