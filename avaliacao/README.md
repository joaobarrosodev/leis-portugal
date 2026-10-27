# Conjunto de avaliação

Perguntas com a resposta certa conhecida, para medir a fiabilidade de um sistema de pesquisa e resposta (RAG) sobre o acervo. É a fase 1 do [plano para um RAG jurídico fiável](../PLANO-RAG.md).

A meta é que pelo menos 95% das respostas **dadas** estejam certas: artigo certo, versão em vigor na data certa e citação que suporta a resposta. O sistema pode responder "não sei".

## Âmbito

Só perguntas cuja resposta está **escrita** num artigo: prazos, valores, quem pode o quê, se uma norma está em vigor, o que dizia numa data. Interpretação, casos concretos e jurisprudência ficam de fora; para essas o certo é "não sei".

## Estado

| Fase | Perguntas | Margem de erro a 95% | Para que serve |
|---|---:|---:|---|
| **Piloto** (concluído) | 59 | cerca de ±5,5 pontos | Testar o processo: se as perguntas saem boas, se a verificação às cegas funciona e se a comparação apanha os erros |
| Conjunto completo | ~600 | cerca de ±1,7 pontos | Medir a fiabilidade a sério, por tipo de pergunta |

60 perguntas não chegam para medir: um resultado de 95% tanto pode ser 90% como 100%. Com ~600 já se distingue 93% de 97%.

O piloto tem 30 literais, 12 temporais, 7 revogadas e 10 sem resposta. As perguntas reais (FAQs oficiais) entram no conjunto completo.

## Resultado do piloto (27/10/2026)

A sessão B (Sonnet, às cegas) chegou às mesmas respostas que a sessão A em todas as perguntas: 59 de 59 confirmadas pela comparação automática.

| Ronda | Perguntas | Confirmadas | Assinaladas por B | O que se fez |
|---|---:|---:|---:|---|
| 1.ª | 60 | 53 | 7 | Revisão abaixo |
| 2.ª (só as reformuladas) | 2 | 2 | 0 | — |
| **Final** | **59** | **59** | **0** | |

- **Respostas erradas de A:** nenhuma. B recusou as 10 sem resposta e indicou a revogação nas revogadas.
- **Perguntas mal formuladas:** 3. `lit-013` falava em "área" quando o artigo fala em número de corpos, e `rev-002` era ambígua; ambas foram reformuladas e voltaram a passar às cegas. `rev-004` era vaga e saiu do conjunto.
- **Perguntas que remetem para outro artigo:** `lit-016` e `lit-020`, marcadas com `depende_de_outro`.
- **Comparação:** a primeira versão marcava 34 pontos a rever, quase todos ruído (números escritos de outra forma, respostas iguais por outras palavras). Com as melhorias passou a 7, todos reais.
- **Amostragem:** os anexos de republicação davam texto histórico em vez do atual; passaram a ser excluídos antes de se escreverem as perguntas.

O processo funciona. O passo seguinte é gerar as restantes ~540 perguntas, incluindo as reais (FAQs oficiais), com o mesmo processo.

## Tipos de pergunta

| Tipo | Prefixo | Como se gera | Como se sabe a resposta certa |
|---|---|---|---|
| `literal` | `lit-` | Artigo de um diploma em vigor e consolidado | O excerto tem de estar no texto atual do artigo |
| `temporal` | `tmp-` | Artigo cuja redação mudou (`.versoes.json`) | O excerto tem de estar no texto do artigo na `data_referencia` (`version-at`) |
| `revogada` | `rev-` | Artigo de um diploma revogado (relação `repealed_by`) | A resposta certa diz que a norma foi revogada, e por que diploma |
| `sem_resposta` | `sem-` | Fora do âmbito, lei inexistente ou diploma que não trata do assunto | O certo é "não sei"; a verificação recebe um artigo distrator |
| `real` | `real-` | FAQs oficiais que citam artigos (por fazer) | O artigo que a entidade cita |

## Processo

1. **Amostragem** (`amostra.py`): escolhe artigos ao acaso no índice exportado (`leis-portugal export`), com semente fixa. Exclui artigos revogados, só de aprovação, com blocos de assinaturas e de **anexos de republicação**: o texto republicado é o dessa data, não o atual, e daria respostas certas erradas.
2. **Sessão A (geração):** lê os candidatos e escreve a pergunta, a resposta e o excerto do artigo que a suporta, em `perguntas.jsonl`.
3. **Verificação literal** (`verifica.py literal`): confirma que cada excerto está, letra a letra, no artigo citado (na data de referência, nas temporais) e que os números da resposta estão no excerto.
4. **Sessão B (verificação às cegas, outro modelo):** recebe `verifica.py cegas`, que tem só a pergunta, a data e o texto do artigo, **sem a resposta certa**. Responde a partir do texto e assinala perguntas ambíguas ou que dependem de outro artigo. Não pode abrir `perguntas.jsonl`.
5. **Comparação** (`verifica.py compara`): compara as respostas de B com as de A e lista o que não bate. Os números comparam-se sem separadores de milhares nem decimais a zero (`100 000 000,00` = `100 000 000`). As respostas sem números contam como iguais quando a de B tem pelo menos 80% das palavras com conteúdo da de A, ignorando as diferenças do Acordo Ortográfico.
6. **Discordâncias:** vão a uma terceira revisão, são corrigidas ou a pergunta sai do conjunto.
7. **Calibração (opcional):** revisão humana de ~20 perguntas ao acaso, para medir quanto confiar na verificação automática. Sem ela, o resultado escreve-se "95% segundo a verificação automática".

## Ficheiros

| Ficheiro | O que é |
|---|---|
| `perguntas.jsonl` | O conjunto de avaliação, com as respostas certas (sessão A) |
| `verificacao/entrada-piloto.jsonl` | A entrada da sessão B, sem as respostas |
| `verificacao/respostas-b-piloto.jsonl` | As respostas da sessão B |
| `verificacao/entrada-piloto-revistas.jsonl`, `respostas-b-piloto-revistas.jsonl` | Segunda ronda às cegas das perguntas reformuladas depois da revisão |
| `amostra.py` | Amostragem dos candidatos |
| `verifica.py` | Verificação literal, entrada às cegas e comparação |
| `comum.py` | Leitura dos artigos de um registo (partilhada) |

## Formato

Uma pergunta por linha em `perguntas.jsonl`:

```json
{
  "id": "lit-001",
  "tipo": "literal",
  "pergunta": "…",
  "data_referencia": "2026-10-27",
  "fonte": {"documento": "pt:dre:…:por", "caminho": "data/…/….md", "titulo": "…", "artigo": "17.º", "epigrafe": "…"},
  "resposta": "…",
  "excerto": "texto literal do artigo que suporta a resposta"
}
```

- `fonte.artigo` é a chave do artigo no registo: `17.º` no diploma, `Anexo — …::17.º` num anexo. A numeração repete-se entre o diploma e os anexos (o Código do Trabalho, anexo da Lei n.º 7/2009, tem o seu próprio artigo 3.º).
- `depende_de_outro: true` (opcional) marca as perguntas cuja resposta completa precisa de outro artigo para o qual o texto remete. Servem para avaliar a pesquisa em vários artigos; a comparação não as volta a assinalar por isso.
- `revogada` tem ainda `revogado_por` (`documento`, `titulo`, `data`).
- `sem_resposta` tem `fonte: null` e `distrator` (mesmo formato de `fonte`).

Uma resposta por linha da sessão B: `{"id", "responde": bool, "resposta", "excerto", "ambigua": bool, "depende_de_outro": bool, "notas"}`.

## Comandos

```bash
python avaliacao/amostra.py --saida <pasta>
cd avaliacao && python verifica.py literal
cd avaliacao && python verifica.py cegas --saida verificacao/entrada-piloto.jsonl
cd avaliacao && python verifica.py compara --respostas verificacao/respostas-b-piloto.jsonl
```

Precisam do ambiente do projeto (`pip install -e .`) e de `exports/leis-portugal.sqlite`.

## Limites

- Perguntas geradas a partir de um artigo são mais fáceis do que as reais, porque usam as mesmas palavras. Cada tipo é medido e mostrado em separado.
- A amostra usa o estado de vigência que o DRE indica. Alguns diplomas "em vigor" já caducaram na prática (por exemplo, os que vigoravam só até uma data); na geração estes ficam de fora.
- Os termos de reutilização das FAQs oficiais ainda têm de ser verificados; no pior caso usam-se só para avaliar e não se publicam.
