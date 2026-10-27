# Alterações

Alterações ao formato dos dados, aos comandos e aos ficheiros gerados que possam afetar quem reutiliza o acervo (por exemplo, pipelines de pesquisa ou de embeddings). As alterações de conteúdo do dia a dia (diplomas novos, recolhas) não entram aqui: estão no histórico do Git.

O esquema dos registos é [`schemas/legal_document.schema.json`](schemas/legal_document.schema.json) (`schema_version: '1.0'`). Uma alteração incompatível ao esquema muda a versão e fica assinalada aqui como **incompatível**.

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
