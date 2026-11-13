# Progresso do projeto

Relatório gerado em 2026-11-13.

## Estado real

| Componente | Estado | Evidência |
|---|---|---|
| Estrutura do pacote Python | Implementado | `src/leis_portugal/` |
| Registo de fontes | Implementado | `config/sources.yml` validado por esquema |
| Esquemas de metadados | Implementado | `schemas/` |
| Conector EUR-Lex/CELLAR (por data, por CELEX e atos referidos) | Operacional | 53947 ato(s) da UE no acervo |
| Conector DRE (por data, por caminho, consolidados, em falta e referidos) | Operacional | 380370 documento(s) do DRE |
| Verificação pelos sitemaps do DRE | Implementado | `collect dre --missing` (`reports/dre_sitemap_coverage.json`) |
| Catálogo do Jornal Oficial dos Açores | Implementado | registos regionais em `data/regional/acores/` |
| Recolha direta (vs. importação inicial) | Concluída | 434316 recolhidos diretamente; 1 ainda com o texto da importação inicial |
| Relações entre diplomas | Implementado | DRE e CELLAR (alterações, revogações, retificações); citações e transposições detetadas no texto; ligações inversas nos atos da UE; referências por ELI resolvidas para ids do acervo (`link`) |
| Índice de relações e exportação | Implementado | `leis-portugal export` (JSONL, SQLite, Parquet em `exports/`) |
| Relatórios derivados dos dados | Implementado | `reports/` |
| Atualização diária automática | Implementado | `.github/workflows/atualizacao-diaria.yml` (DRE + EUR-Lex do dia anterior) |
| Histórico de versões consolidadas | Implementado | 10789 registo(s) com `<registo>.versoes.json` (DRE: `collect dre-consolidated`; UE: `collect eurlex-consolidated`) |

## Estado das fontes

| Fonte | Estado | Última verificação | Documentos |
|---|---|---|---:|
| eurlex-cellar | operational | 2026-10-26 | 53947 |
| dre | operational | 2026-10-26 | 380370 |
| parlamento | planned | — | 0 |
| cnpd | operational | 2026-11-12 | 0 |
| tribunal-constitucional | operational | 2026-11-12 | 0 |

## Próximos passos

1. Tornar a atualização diária autónoma: recuperar dias em falta, repetir falhas temporárias, atualizar consolidados e diplomas alterados, e verificar semanalmente os sitemaps do DRE.
2. OCR dos diplomas que só têm o PDF oficial (sobretudo 1910–1959).
3. Datas de entrada em vigor e identificadores estáveis por artigo.
4. Novas categorias: tratados e jurisprudência do TJUE (EUR-Lex), jurisprudência portuguesa, trabalhos parlamentares.
5. Comparar as transposições detetadas no texto com as medidas nacionais de execução registadas no CELLAR.
