# Alterações

Alterações ao formato dos dados, aos comandos e aos ficheiros gerados que possam afetar quem reutiliza o acervo (por exemplo, pipelines de pesquisa ou de embeddings). As alterações de conteúdo do dia a dia (diplomas novos, recolhas) não entram aqui: estão no histórico do Git.

O esquema dos registos é [`schemas/legal_document.schema.json`](schemas/legal_document.schema.json) (`schema_version: '1.0'`). Uma alteração incompatível ao esquema muda a versão e fica assinalada aqui como **incompatível**.

## 2026-10-27

### Texto em vigor consolidado pelo leis-portugal (novo)
- 25 diplomas que o DRE dá como alterados mas não consolida passam a ter o texto em vigor, com as alterações publicadas aplicadas por regra e verificadas às cegas artigo a artigo (piloto da fase 2, [`consolidacao/README.md`](consolidacao/README.md)).
- Ficam como os consolidados do DRE: `version.kind: consolidated`, `consolidation_date` (a data em que a alteração entrou em vigor), notas "> Alterado pelo/a …" nos artigos alterados e `<registo>.versoes.json` com a versão original e a alterada (`leis-portugal version-at` funciona).
- Distinguem-se pelo rótulo `version.label` ("Versão consolidada pelo leis-portugal, sem valor oficial: …"), por `source.consolidated_url: null` e, no histórico, por `consolidated_by: leis-portugal` e fragmentos sem `fragment_id` nem `type`. Quem só quiser texto oficial deve filtrar pelo rótulo.
- Uma nova recolha do texto publicado não os substitui; uma versão consolidada do DRE substitui.

### Artigos, entrada em vigor e vigência (novo)
- `leis-portugal structure` lê os registos portugueses e regionais, escreve em `reports/` um relatório de cobertura (`estrutura.md`, `estrutura.json`) e as propostas de vigência com as provas (`vigencia-proposta.jsonl`), e grava nos registos a entrada em vigor e a vigência provada. `--dry-run` só mede, sem alterar registos.
- **Entrada em vigor nos registos:** `entry_into_force` (data, regra em texto, método, artigo, produção de efeitos e fim de vigência) quando há cláusula ou se aplica a regra supletiva; `entry_into_force_dates` recebe a data quando estava vazio. Em 2026-10-27: 87.382 registos.
- **Vigência provada nos registos:** nos diplomas de vigência desconhecida com prova de revogação total ou caducidade, `legal_status` muda e `legal_status_basis` guarda a fonte e as provas. Em 2026-10-27: 371 registos. Um estado gravado assim volta a avaliar-se em cada execução e é retirado se a prova deixar de existir. Uma etiqueta do DRE em que o revogado é outro diploma ("o Dec Lei 139/2012, com a redação dada pelo presente", "alterado" ou "aprovado pelo presente") não conta como revogação deste.
- Uma nova recolha preserva `entry_into_force` e, enquanto a fonte não indicar outro estado, a vigência provada.
- **Id por artigo** (`leis-portugal/artigos/1`): `<id do registo>#<parte>/<artigo>`, p. ex. `pt:dre:602073:por#art-14` (artigo do diploma) e `pt:dre:602073:por#anexo-codigo-do-trabalho/art-3` (artigo do Código do Trabalho, anexo da Lei n.º 7/2009). A parte é o slug do título do anexo (`anexo-ii` quando o anexo é numerado); o artigo é `art-<número>` (`art-10-a`, `art-unico`), `base-<número>`, `clausula-<número>` ou, nos diplomas sem artigos, `n-<número>` (números do dispositivo, `1.º`, `1 -`). O id calcula-se a partir do corpo do registo (`leis_portugal.domain.articles`), por isso não precisa de ser guardado.
- **Esquema** (compatível; os registos atuais continuam válidos): campos opcionais `entry_into_force` (data, regra em texto, método `clausula`/`supletiva`/`sem_clausula`, artigo, produção de efeitos e fim de vigência), `legal_status_basis` (a proveniência de `legal_status` quando não vem do DRE, com as provas) e, em `article_structure`, `unit`, `annex_count` e `id_scheme` (estes três ainda não se gravam: os ids por artigo calculam-se do corpo).

### Histórico de versões em blocos (alteração de formato)
- Um `<registo>.versoes.json` que passe de 50 MB (o máximo recomendado pelo GitHub) é gravado dividido: os fragmentos vão para blocos `<registo>.versoes/001.json`, `002.json`… de até 20 MB, e o `<registo>.versoes.json` fica um índice com os mesmos campos, mas com `fragment_blocks` (a lista dos blocos, com caminhos relativos à pasta do índice) no lugar de `fragments`. O `schema` do índice continua `leis-portugal/versoes/1`.
- Cada bloco tem `schema: leis-portugal/versoes-bloco/1`, `id` e `fragments` (uma parte do dicionário `fragments`, pela ordem original). Para obter o histórico completo, junta-se o `fragments` de todos os blocos, pela ordem de `fragment_blocks`.
- Os históricos abaixo de 50 MB não mudam. Quem lê os ficheiros diretamente deve tratar os dois casos: `fragments` no próprio ficheiro ou `fragment_blocks`. O `leis-portugal version-at` e a recolha (`collect dre-consolidated`, `collect eurlex-consolidated`) já o fazem; um histórico que volte a caber num ficheiro deixa de ter blocos.
- Ficaram em blocos `regulamento-ue-2014-269` (83 MB) e `regulamento-ue-2005-396` (810 MB, que deixa de estar fora do git).

## 2026-10-26

### Varredura por datas
- `collect dre --from/--to --only-missing`: lista os dias (em paralelo com `--workers`) e recolhe só os diplomas que ainda não estão no acervo. Os sitemaps do DRE não listam tudo (p. ex. muitas Resoluções do Conselho de Ministros); a lista diária da 1.ª Série é a fonte mais completa.
- A recolha por datas passa a recolher uma só vez um diploma listado em mais de um dia, e um dia que o DRE não liste fica registado como falha em vez de interromper a recolha.

### Sitemaps do DRE
- Cópia local em `.cache/dre-sitemaps/` (fora do git): só se descarregam os ficheiros cuja data de alteração no índice mudou.
- Um ficheiro que o DRE recuse (p. ex. HTTP 403 em `geral-sitemap`) é ignorado com um aviso; as famílias sem páginas de documentos deixam de ser descarregadas.
- `collect dre --referenced` procura os ids em todos os sitemaps do DRE (não só nos tipos do vocabulário).

### Ligações "sem diploma"
- As ligações da análise jurídica do DRE ao marcador "sem diploma" passam a referência por número quando a nota indica o ato (`pt:numero:decreto-lei:189/90`) e deixam de existir quando não indica. O conector deixa de as criar.

### Relações
- `leis-portugal link` resolve as referências por ELI (`eli:…`) para o id do documento no acervo (`pt:dre:…`, `eu:celex:…`) quando ele existe, comparando o ELI exato, o mesmo diploma noutra versão (publicada ou consolidada) e, para registos sem ELI, a numeração (tipo, número, ano, região e data). O URL original passa para `source`.
- As ligações partidas herdadas da importação inicial (`eli:h`, `eli:http://`, `eli:/application/external/tratado`, ELI truncados do DRE) são removidas.
- `config/document_types.yml`: cada tipo tem os códigos de tipo usados nos ELI do DRE (`eli: [dec-lei]`).

### Exportação (novo)
- `leis-portugal export` gera em `exports/` (fora do git) `relationships.jsonl`, `leis-portugal.sqlite`, `documentos.parquet` e `relacoes.parquet`.
- Cada relação tem `target` (como está no registo) e `target_id` (o id resolvido no acervo, ou vazio).
- A tabela `documentos` tem `text_quality`: `texto`, `pdf` (só a ligação ao PDF oficial) ou `metadados` (a fonte não tem texto nem PDF).
- O Parquet precisa do extra `export` (`pip install -e '.[export]'`).

### Recolha
- `collect dre --referenced`: recolhe os diplomas do DRE referidos por documentos do acervo (por id, ELI ou número) e ainda sem registo.
- `collect eurlex --referenced` passa a considerar as referências de todo o acervo (antes, só as da legislação portuguesa). O texto do progresso muda para "ato(s) da UE referidos no acervo ainda sem registo".
- Novo ficheiro de falhas `reports/dre_referenced_failures.jsonl`.

### Relatórios
- `COBERTURA.md` ganha a secção "Qualidade do texto"; `PROGRESSO.md` e as lacunas conhecidas foram atualizados.

## 2026-10-23

### Catálogo do Jornal Oficial dos Açores
- As entradas do catálogo do Jornal Oficial dos Açores que o DRE guarda (`TipoConteudo: DiplomaLegacor`) deixam de ser ignoradas e passam a registos regionais (`jurisdiction: regional`, `territory: acores`), com `publication.gazette: Jornal Oficial dos Açores`, série, número e páginas, e `version.label: Texto publicado no Jornal Oficial dos Açores`.

### Registos só com metadados
- Quando a fonte não tem texto nem PDF, o registo é gravado com os metadados, o corpo "este registo tem só os metadados" e a nota `Fonte sem texto: o DRE não tem texto eletrónico nem PDF deste diploma; o registo tem só os metadados (verificado em AAAA-MM-DD).` O `integrity.source_sha256` identifica, nesse caso, a resposta de metadados do DRE.
- Um registo que já tenha texto nunca é substituído por um sem texto: ganha só a nota.

### Cobertura pelos sitemaps do DRE (novo)
- `collect dre --missing` compara o acervo com os sitemaps públicos do DRE e recolhe o que falta; `--dry-run` só conta.
- `reports/dre_sitemap_coverage.json` (contagens por tipo) e `reports/dre_missing_failures.jsonl`.
- `config/document_types.yml`: `sitemap_optional` lista os tipos sobretudo da 2.ª Série, recolhidos só com `--all` ou `--types`.
- `collect dre --imported` aceita `--types`.

## 2026-10-22

### Estado de vigência
- `legal_status` passa a refletir só o que o DRE indica: sem indicação, fica `unknown` (a importação inicial preenchia `in_force` por omissão).

### Fonte sem texto
- Os ficheiros `reports/*_failures.jsonl` têm o campo `motivo` (`sem_texto_na_fonte`, `erro_de_acesso`, `metadados_em_falta`, `registo_invalido`, `armazenamento`, `resposta_inesperada`).
- Quando a fonte não tem o texto, o registo existente ganha a nota `Fonte sem texto: …`.

### Histórico de versões
- Diplomas portugueses (legislação consolidada do DRE) e atos da UE (consolidações do EUR-Lex) têm `<registo>.versoes.json` (formato `leis-portugal/versoes/1`): versões por data, atos que as produziram, modificações e fragmentos guardados uma só vez. O registo tem o resumo em `version_history` e o texto em vigor.
- `leis-portugal version-at <id> --date AAAA-MM-DD` reconstrói o texto numa data.

### Recolha direta
- O texto da importação inicial (`integrity.source_sha256_scope: imported_derived_markdown`) é substituído pela recolha direta do DRE (`collect dre --imported`).
