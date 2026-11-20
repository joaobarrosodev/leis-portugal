# Jurisprudência dos tribunais comuns: o que se pode recolher (20/11/2026)

Para o «resultado previsível» da análise de caso faltam os acórdãos do Supremo Tribunal de Justiça e das Relações. Este relatório diz onde estão, com que estrutura, quantos são e se a recolha automática é permitida. **Não se recolheu nenhum piloto.** Nenhuma das fontes publica termos de uso ou licença de reutilização, e por isso não é claro que a recolha seja permitida.

## Resumo

- **dgsi.pt (bases jurídico-documentais do IGFEJ, Ministério da Justiça).** É a fonte que tem tudo: o STJ, o STA, as cinco Relações e os TCA, com texto integral e campos estruturados.
  - Não tem `robots.txt` (o pedido dá 404).
  - A página inicial não tem termos de uso, aviso legal nem licença.
  - Sem regra escrita, a recolha em massa fica numa zona cinzenta, sobretudo por causa do direito sobre bases de dados (ver «Enquadramento»).
- **Diário da República.** A 1.ª Série só publica os acórdãos de uniformização e de fixação de jurisprudência, e esses já estão no acervo:
  - 213 do STJ e 122 do STA;
  - os 190 assentos;
  - os 183 acórdãos doutrinários.

  Com os 134 de antes de 2008, em `outros/acordao` e `outros/jurisprudencia`, são 469. A camada nova (`rag/uniformizacao.py`) liga 332 deles ao artigo. Os acórdãos comuns das Relações e do STJ não são publicados no DR: verificado nos sitemaps e no detalhe do DRE a 20/11/2026 (ver «Diário da República»).
- **stj.pt.** O `robots.txt` permite tudo (`Disallow:` vazio). O site publica sumários (não o texto integral) por secção e mês, a «Jurisprudência Temática» e a página de uniformização. Não se encontrou aviso legal.
- **jurisprudencia.csm.org.pt (CSM, com ECLI).** Não se conseguiu abrir com o `curl` do projeto: a cadeia do certificado não verifica. Não se encontraram termos de uso.
- **Recomendação:** pedir autorização por escrito ao IGFEJ (dono do dgsi.pt) e ao CSM antes de qualquer recolha, como se fez com o TC a 12/11/2026. Pedir também um descarregamento em bloco, se existir. A decisão de enviar o pedido é do João; o rascunho está no fim.

## Fontes, volume e formato

### dgsi.pt

Volume, contado na página inicial a 20/11/2026:

| Base | Acórdãos |
|---|--:|
| Supremo Tribunal de Justiça (`jstj.nsf`) | 73.979 |
| Supremo Tribunal Administrativo (`jsta.nsf`) | 90.491 |
| Tribunal da Relação do Porto (`jtrp.nsf`) | 64.507 |
| Tribunal da Relação de Lisboa (`jtrl.nsf`) | 62.370 |
| Tribunal da Relação de Évora (`jtre.nsf`) | 18.853 |
| Tribunal da Relação de Coimbra (`jtrc.nsf`) | 16.978 |
| Tribunal da Relação de Guimarães (`jtrg.nsf`) | 16.165 |
| Tribunal Central Administrativo Sul (`jtca.nsf`) | 31.523 |
| Tribunal Central Administrativo Norte (`jtcn.nsf`) | 20.973 |
| Tribunal dos Conflitos (`jcon.nsf`) | 1.269 |
| Julgados de Paz (`cajp.nsf`) | 7.322 |

Só a parte comum (o STJ e as cinco Relações) soma 252.852 documentos. O site não diz quantos têm texto integral (campo «Texto Integral: S/N»).

**Formato.** O site é Lotus Domino, com HTML em ISO-8859-1 e sem API. Para descrever o formato fizeram-se 3 pedidos, com pausas, e nada foi guardado no acervo.

- **Vista:** `/jstj.nsf/954f0ce6ad9dd8b980256b5f003fa814?OpenView`, com 99 acórdãos por página e a paginação do Domino (`&Start=`). As colunas são sessão, processo, relator e descritores; a ordem é do mais recente para o mais antigo.
- **Acórdão:** `/jstj.nsf/<vista>/<unid>?OpenDocument`, com cerca de 100 KB de HTML. Os campos, pela ordem:
  - Processo (`6038/26.0T8LSB.S1`), Nº Convencional (a secção: «5.ª SECÇÃO»), Relator;
  - Descritores (vocabulário controlado, um por linha);
  - Data do Acórdão (no formato mês/dia/ano), Votação, Texto Integral (S/N), Privacidade;
  - Meio Processual («RECURSO PENAL»), Decisão («PROVIDO EM PARTE», «NEGADA A REVISTA»…);
  - Sumário, numerado como no acórdão;
  - Decisão Texto Integral, que inclui as declarações de voto no fim.
- **Pseudonimização:** os nomes das partes vêm substituídos (AA, BB…), segundo os critérios do CSM.

Para a análise de caso, os campos mais úteis são **Decisão** e **Meio Processual** (o resultado, já normalizado), os **Descritores** (o tema) e o **Sumário** (as normas aplicadas e a regra de decisão, num texto curto). O sumário já se lê com `rag.jurisprudencia.normas`, como os sumários dos acórdãos de uniformização.

**Ritmo e tempo.** Um pedido de 5 em 5 segundos dá 720 acórdãos por hora. É o mais educado entre os coletores do projeto: o TC, o DRE e a CNPD usam `HttpClient(min_interval=1.0)`.

| Âmbito | Documentos | Tempo a 1 pedido/5 s |
|---|--:|--:|
| STJ desde 2020, Secção Social (4.ª), o piloto pedido | não contado; estimativa de algumas centenas por ano | menos de 1 dia |
| STJ inteiro | 73.979 | cerca de 103 h |
| STJ e as cinco Relações | 252.852 | cerca de 351 h (15 dias) |

O número do piloto não foi contado: contá-lo exigia percorrer a vista. Fica como estimativa, não como medida.

### Diário da República (verificado a 20/11/2026)

O DRE **não tem os acórdãos comuns do STJ nem os das Relações**. A jurisprudência que tem, toda sob o regime de reutilização do DR (artigo 3.º do Decreto-Lei n.º 83/2016 e Lei n.º 68/2021), é esta:

| Tipo no DRE (sitemap) | O que é | Volume | No acervo |
|---|---|--:|---|
| `jurisprudencia` | acórdãos de uniformização do STJ publicados de 2001 a 2004 com o título «Jurisprudência n.º X/AAAA» | 20 | sim (`outros/jurisprudencia`) |
| `acordao` (1.ª Série, até 2007) | acórdãos de uniformização do STJ e do STA anteriores à criação dos tipos próprios, junto com os do TC e do Tribunal de Contas | 106 do STJ e 8 do STA, de 1976 a 2007 | sim (`outros/acordao`) |
| `acordao-supremo-tribunal-justica`, `-administrativo` | uniformização desde 2008 | 213 e 122 | sim |
| `acordao-sta` | os acórdãos do STA publicados no Apêndice ao DR (2.ª Série), com assunto, sumário, processo, data e PDF | 53.108, de 1995 a 2016 | não |

Como se verificou, sem recolher nada:

- o índice de sitemaps (`files.diariodarepublica.pt/sitemap/sitemap.xml`, 593 sitemaps);
- os sitemaps `jurisprudencia`, `acordao` e `acordao-sta` (o último em 3 ficheiros);
- 5 detalhes pelo coletor do DRE (`published_detail`), com um pedido a cada 4 segundos.

O tipo «Jurisprudencia» dos *screenservices* corresponde a estes 20 registos. Não há tipo para as Relações nem para os acórdãos comuns do STJ.

**Consequência:** não se fez o piloto do STJ laboral desde 2020, porque o DRE não o tem e o dgsi.pt continua sem termos.

Os 134 acórdãos de uniformização anteriores a 2008 (`outros/jurisprudencia` e `outros/acordao`) entraram na extração do STJ e do STA. Os 53.108 do STA no Apêndice são direito administrativo e fiscal até 2016. Podem recolher-se pelo coletor do DRE, sob o regime do DR, mas não respondem ao que falta, que são os tribunais comuns.

### stj.pt

- O `robots.txt` (Yoast) permite tudo e indica `sitemap_index.xml`.
- O site publica:
  - os «Sumários dos Acórdãos», em PDF por secção e mês;
  - a «Jurisprudência Temática», em PDF por tema;
  - a página «Uniformização de Jurisprudência»;
  - a lista «Últimas decisões – Social».
- São sumários, não o texto integral, mas para a Secção Social trazem a regra e as normas.
- Não se encontrou aviso legal nem política de reutilização. Que o `robots.txt` permita não quer dizer que a reutilização seja permitida.

### jurisprudencia.csm.org.pt

É o portal do CSM com ECLI. Segundo o plano de atividades do STJ para 2024, indexa os acórdãos do STJ do dgsi.pt e alguns que só ali estão. O `curl` falhou na verificação do certificado e não se tentou contornar. Não se encontraram termos de uso.

## Enquadramento (a confirmar por um jurista)

- **Direito de autor:** o Código do Direito de Autor não protege os textos oficiais, entre eles as decisões dos tribunais (artigos 7.º e 8.º do CDADC; a alínea exata está por confirmar). O texto dos acórdãos não deve por isso ser o problema.
- **Direito sobre bases de dados:** o Decreto-Lei n.º 122/2000 protege o fabricante da base contra a extração de uma parte substancial. Uma recolha de todo o dgsi.pt é exatamente isso. É a razão principal para pedir autorização antes.
- **Dados pessoais:** os acórdãos estão pseudonimizados, mas continuam a ser dados pessoais (RGPD). O projeto não pode reidentificar nem cruzar as partes, e deve manter a pseudonimização tal como vem.
- **Precedente de terceiros:** o repositório público LawAgents/jurisprudencia-pt publica sumários e metadados do dgsi.pt. Diz que o site não tem aviso de reutilização nem `robots.txt` e que ainda não obteve confirmação escrita do IGFEJ ou do CSM. Não é uma autorização.

## Estrutura proposta (para quando houver autorização)

Segue as convenções dos coletores do projeto (`src/leis_portugal/sources/tc.py` e `cnpd.py`):

- `src/leis_portugal/sources/dgsi.py`:
  - `HttpClient(min_interval=5.0)`;
  - listagem pela vista por ano;
  - um registo por acórdão;
  - as falhas em `reports/dgsi_failures.jsonl`.
- Um registo por acórdão em `data/jurisprudencia/<tribunal>/<ano>/acordao-<tribunal>-<processo>.md`, com:
  - YAML: `id` (`pt:dgsi:stj:<unid>`), processo, secção, relator, data, descritores, meio processual, decisão, votação, `official_url` e `sha256` da página;
  - o sumário e o texto integral no corpo;
  - `reuse` com o que o IGFEJ autorizar.
- `data/jurisprudencia/<tribunal>/normas-aplicadas.jsonl`: o artigo e o diploma tirados do sumário, com `rag.jurisprudencia.normas` (`sigla_desconhecida=True`) e o resolvedor de `rag.uniformizacao`, mais o campo Decisão, que já diz o resultado.
- **Antes de entrar na segunda resposta:**
  - medir à mão a precisão numa amostra, como se fez para o STJ e o STA;
  - separar na apresentação o que é jurisprudência uniformizada (que orienta os tribunais) do que é um caso concreto.

## Rascunho do pedido ao IGFEJ e ao CSM (por enviar)

> Assunto: Reutilização dos acórdãos das bases jurídico-documentais (dgsi.pt) num projeto aberto
>
> O projeto leis-portugal (repositório público, licença MIT) reúne a legislação portuguesa e responde a perguntas citando os artigos. Gostaríamos de ligar a cada artigo os acórdãos do STJ e das Relações que o aplicaram, mostrando o número do processo, a data, o sentido da decisão e a ligação para o dgsi.pt.
>
> Pedimos que nos digam:
> 1. se permitem a recolha automática dos acórdãos, a que ritmo (propomos um pedido a cada 5 segundos) e com que condições de atribuição;
> 2. se existe uma exportação em bloco ou uma API que prefiram que usemos.
>
> Manteremos a pseudonimização tal como publicada e não faremos qualquer cruzamento de dados pessoais.

## Fontes consultadas

- [dgsi.pt](https://www.dgsi.pt/): página inicial, `robots.txt` (404), uma vista e um acórdão do STJ (20/11/2026).
- [stj.pt/robots.txt](https://www.stj.pt/robots.txt) e a [página inicial do STJ](https://www.stj.pt/).
- [Ministério da Justiça — Jurisprudência](https://justica.gov.pt/en-gb/Jurisprudencia): as bases são geridas pelo IGFEJ.
- [LawAgents/jurisprudencia-pt](https://github.com/LawAgents/jurisprudencia-pt): precedente de terceiros, sem autorização escrita.
- [CSM — critérios de seleção e pseudonimização (2023)](https://csm.org.pt/wp-content/uploads/2023/05/Parecer-atualizacao-dos-criterios-de-selecao-e-pseudonimizacao-das-decisoes-judiciais-31-03-2023.pdf).
- [Plano de atividades do STJ para 2024](https://www.stj.pt/wp-content/uploads/2024/02/Plano-de-atividades-2024.pdf): relação entre o dgsi.pt e o portal do CSM.
