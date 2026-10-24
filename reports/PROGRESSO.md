# Progresso do projeto

Relatório gerado em 2026-10-24.

## Estado real

| Componente | Estado | Evidência |
|---|---|---|
| Estrutura do pacote Python | Implementado | `src/leis_portugal/` |
| Registo de fontes | Implementado | `config/sources.yml` validado por esquema |
| Esquemas de metadados | Implementado | `schemas/` |
| Conector EUR-Lex/CELLAR (por data, por CELEX e atos referidos) | Operacional | 7806 ato(s) da UE no acervo |
| Conector DRE (1.ª Série, por data e consolidados) | Operacional | 269401 documento(s) do DRE |
| Recolha direta (vs. importação inicial) | Em curso | 277206 recolhidos diretamente; 1 ainda com o texto da importação inicial |
| Relações entre diplomas | Parcial | DRE e CELLAR (alterações, revogações, retificações); citações e transposições de atos da UE detetadas no texto; ligações inversas nos atos da UE |
| Relatórios derivados dos dados | Implementado | `reports/` |
| Atualização diária automática | Implementado | `.github/workflows/atualizacao-diaria.yml` (DRE + EUR-Lex do dia anterior) |
| Histórico de versões consolidadas | Implementado | 8049 registo(s) com `<registo>.versoes.json` (DRE: `collect dre-consolidated`; UE: `collect eurlex-consolidated`) |

## Estado das fontes

| Fonte | Estado | Última verificação | Documentos |
|---|---|---|---:|
| eurlex-cellar | operational | 2026-10-22 | 7806 |
| dre | operational | 2026-10-22 | 269401 |
| parlamento | planned | — | 0 |
| cnpd | planned | — | 0 |

## Próximos passos

1. Substituir o texto da importação inicial pela recolha direta do DRE (por intervalos de datas).
2. Resolver as relações por número (`pt:numero:…`) e por ELI para ids do acervo, gerando um índice de relações.
3. Comparar as transposições detetadas no texto com as medidas nacionais de execução registadas no CELLAR.
