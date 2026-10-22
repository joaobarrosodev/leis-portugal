---
schema_version: '1.0'
id: eu:celex:32026R0818:por
title: Regulamento de Execução (UE) 2026/818 da Comissão, de 9 de abril de 2026
short_title: null
summary: Regulamento de Execução (UE) 2026/818 da Comissão, de 9 de abril de 2026, que estabelece disposições pormenorizadas
  para a disponibilização de uma estrutura de dados comum, de metadados normalizados, de uma autenticação normalizada e de
  uma interface comum de programação de aplicações para o repositório europeu de anúncios de cariz político em linha, em conformidade
  com o Regulamento (UE) 2024/900 do Parlamento Europeu e do Conselho
jurisdiction: european_union
territory: null
document_type: regulation
document_type_label: Regulamento de Execução
issuing_authority:
- Comissão Europeia
- JUST
proposing_entity: null
official_number: 2026/818
official_date: null
publication_date: '2026-04-10'
publication:
  gazette: Jornal Oficial da União Europeia
  reference: JO L, 2026/818, 10.4.2026
  number: '818'
  series: L
  supplement: null
  pages: null
  pdf_url: http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.01/DOC_1
entry_into_force_dates:
- '2026-04-30'
end_of_validity_date: '9999-12-31'
legal_status: in_force
notes: []
language: por
version:
  kind: original
  label: Texto original publicado no Jornal Oficial
  language: por
  consolidation_date: null
identifiers:
  celex: 32026R0818
  eli: http://data.europa.eu/eli/reg_impl/2026/818/oj
  oj: oj:L_202600818
  dre: null
  dre_path: null
  internal: eu:celex:32026R0818:por
source:
  id: eurlex-cellar
  name: EUR-Lex / CELLAR
  official_url: https://eur-lex.europa.eu/legal-content/PT/TXT/?uri=CELEX%3A32026R0818
  metadata_url: http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020
  content_url: http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1
  consolidated_url: null
  retrieved_at: '2026-10-22T03:36:54Z'
  retrieval_method: CELLAR RDF + SPARQL + negociação de conteúdo XHTML
  source_modified_at: '2026-04-10T02:53:16.588+02:00'
integrity:
  source_sha256: fbc24ed6a2eb86f3728cace67a702c801f9d3752bf769e8f4463c5547f07e950
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal EUR-Lex/CELLAR
  collector_version: 0.1.0
  generated_by: leis-portugal collect eurlex
  generated_at: '2026-10-22T03:36:54Z'
  notes: null
reuse:
  status: permitted_with_conditions
  attribution: União Europeia, EUR-Lex / Publicações da União Europeia
  reference: https://eur-lex.europa.eu/content/legal-notice/legal-notice.html
  notes: Verificar o aviso jurídico aplicável; só o texto publicado no Jornal Oficial faz fé (as consolidações são instrumentos
    de documentação).
subjects:
- arquivamento digital
- especificação técnica
- interface de programação de aplicações
- internet
- metadados
- partidos políticos
- processamento de dados
- propaganda política
- publicidade
relationships:
- type: based_on
  target: celex:32024R0900
  label: null
  source: http://publications.europa.eu/resource/cellar/825b8717-e65c-11ee-8b2b-01aa75ed71a1
  date: '2024-03-20'
- type: cites
  target: celex:32016R0679
  label: null
  source: http://publications.europa.eu/resource/cellar/3e485e15-11bd-11e6-ba9a-01aa75ed71a1
- type: cites
  target: celex:32018R1725
  label: null
  source: http://publications.europa.eu/resource/cellar/999029ee-ed62-11e8-b690-01aa75ed71a1
- type: cites
  target: celex:32022R2065
  label: null
  source: http://publications.europa.eu/resource/cellar/3ff67256-55c4-11ed-92ed-01aa75ed71a1
- type: cites
  target: celex:32024R0903
  label: null
  source: http://publications.europa.eu/resource/cellar/c008bcb6-e7ec-11ee-9ea8-01aa75ed71a1
- type: cites
  target: celex:32025R1410
  label: null
  source: http://publications.europa.eu/resource/cellar/ca1b1959-61df-11f0-bf4e-01aa75ed71a1
article_structure:
  article_count: 2
  section_count: 0
  extraction_method: Classes XHTML do CELLAR (oj-ti-art / title-article-norm)
derived_material:
  machine_generated: true
  notes: O Markdown é uma conversão derivada do XHTML do CELLAR; o conteúdo-fonte é identificado pelo URL e SHA-256.
validation:
  status: validated
  checked_at: '2026-10-22T03:36:54Z'
  warnings: []
  errors: []
---

# REGULAMENTO DE EXECUÇÃO (UE) 2026/818 DA COMISSÃO

de 9 de abril de 2026

que estabelece disposições pormenorizadas para a disponibilização de uma estrutura de dados comum, de metadados normalizados, de uma autenticação normalizada e de uma interface comum de programação de aplicações para o repositório europeu de anúncios de cariz político em linha, em conformidade com o Regulamento (UE) 2024/900 do Parlamento Europeu e do Conselho

(Texto relevante para efeitos do EEE)

A COMISSÃO EUROPEIA,

Tendo em conta o Tratado sobre o Funcionamento da União Europeia,

Tendo em conta o Regulamento (UE) 2024/900 do Parlamento Europeu e do Conselho, de 13 de março de 2024, sobre a transparência e o direcionamento da propaganda política [([^1])](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntr1-L_202600818PT.000101-E0001), nomeadamente o artigo 13.º, n.º 6,

Considerando o seguinte:

(1) O Regulamento (UE) 2024/900 prevê a criação de um repositório europeu para todos os anúncios de cariz político em linha publicados na União ou dirigidos aos cidadãos ou residentes na União («repositório europeu»). As informações que constam do repositório europeu deverão ser disponibilizadas num formato legível por máquina, permitir consultas com múltiplos critérios e estar acessíveis ao público. Com vista a apoiar estes objetivos, a Comissão deve estabelecer disposições pormenorizadas para a disponibilização de uma estrutura de dados comum, de metadados normalizados, de uma autenticação normalizada e de uma interface comum de programação de aplicações para o repositório europeu.

(2) A fim de assegurar a interoperabilidade com outras redes e sistemas de informação, em especial entre o repositório europeu e os repositórios de anúncios publicitários a que se refere o artigo 39.º do Regulamento (UE) 2022/2065 do Parlamento Europeu e do Conselho [([^2])](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntr2-L_202600818PT.000101-E0002), bem como para facilitar a indexação de anúncios de cariz político em linha pelos motores de pesquisa em linha, é necessário estabelecer disposições com vista ao desenvolvimento de um vocabulário controlado com sequências de termos e frases pertinentes normalizadas e organizadas apresentadas sob a forma de listas de termos ou como tesauros e taxonomias com uma estrutura hierárquica de termos mais amplos e mais restritos, nomeadamente utilizando da melhor forma os vocabulários de base existentes [([^3])](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntr3-L_202600818PT.000101-E0003), subjacente à estrutura comum de dados e aos metadados normalizados.

(3) De modo a assegurar a interoperabilidade, em especial no contexto multilingue dos anúncios de cariz político em linha fornecidos na União, e a indexação pelos motores de pesquisa em linha, cada elemento de metadados deve ter um domínio de valor único, que pode assumir a forma de datas, cadeias de carateres ou códigos derivados de normas internacionais. A fim de apoiar o funcionamento eficaz do repositório europeu e a sua capacidade de pesquisa de informações sobre anúncios de cariz político, esses elementos de metadados devem incluir os elementos do aviso de transparência referidos no anexo II, ponto 3, do Regulamento de Execução (UE) 2025/1410 da Comissão [([^4])](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntr4-L_202600818PT.000101-E0004), informações que permitam a identificação dos anúncios de cariz político em linha, caso existam, o localizador uniforme de recursos (URL) permanente no qual o anúncio de cariz político se encontra disponível e a língua dos elementos de metadados. A fim de assegurar ligações coerentes entre os conjuntos de dados, as informações que permitam a identificação do anúncio de cariz político podem incluir, nomeadamente, consoante o caso, o texto utilizado no anúncio de cariz político, a apresentação alternativa dos conteúdos não textuais do anúncio de cariz político, a transcrição ou as legendas automatizadas dos anúncios de cariz político em formato de áudio ou vídeo, a(s) ligação(ões) para os ficheiros multimédia utilizados no anúncio de cariz político ou um identificador único atribuído pelo editor e outras informações contextuais, como a plataforma em que o anúncio de cariz político foi publicado.

(4) A fim de assegurar a preparação para o futuro e de permitir uma inovação constante, as medidas previstas no presente regulamento devem respeitar o princípio da neutralidade tecnológica, ou seja, não devem impor nem favorecer de forma discriminatória a utilização de um determinado tipo de tecnologia e devem manter a flexibilidade no que diz respeito aos avanços e desenvolvimentos tecnológicos.

(5) Para que se consigam cumprir os objetivos estabelecidos no artigo 13.º, n.º 6, segundo parágrafo, do Regulamento (UE) 2024/900, deve assegurar-se que o repositório europeu [([^5])](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntr5-L_202600818PT.000101-E0005) possa continuar a ser mantido ao longo do tempo e seja capaz de se adaptar à evolução das normas e práticas, ao aumento do volume de dados e às novas exigências normativas ou dos utilizadores. É necessário assegurar que as disposições técnicas relativas à disponibilização da estrutura comum de dados, de metadados normalizados e da interface comum de programação de aplicações sejam compatíveis com o desenvolvimento de outros componentes e camadas do repositório europeu e apoiem esse desenvolvimento, nomeadamente a infraestrutura de acolhimento e as definições de esquema, cuja descrição será disponibilizada ao público com suficiente antecedência em relação à data de entrada em operação do repositório europeu. É igualmente necessário assegurar que o repositório europeu mantém uma integridade sólida dos dados, uma governação eficaz e protocolos de segurança sólidos. A primeira versão do repositório europeu deverá ser compatível com os sistemas de informação existentes da Comissão, nomeadamente exigindo a utilização da linguagem de marcação extensível (XML) ou da notação de objetos JavaScript (JSON), a fim de assegurar que o repositório europeu seja implementado o mais rapidamente possível. A data de funcionamento da primeira versão do repositório europeu deverá ser anunciada no portal público do repositório com antecedência suficiente para permitir que os editores de anúncios de cariz político em linha possam preparar-se e familiarizar-se com as novas normas.

(6) A execução técnica coerente e atempada da estrutura comum de dados, dos metadados normalizados e da interface comum de programação de aplicações exige a participação ativa de um vasto leque de partes interessadas, em especial dos operadores económicos que são prestadores de serviços de propaganda política, em que se incluem editores e as associações que os representam. A Comissão criou um grupo informal de peritos da União, composto por prestadores de serviços de propaganda política, para apoiar a aplicação do Regulamento (UE) 2024/900 e contribuir para a partilha de experiências e boas práticas no domínio da transparência e do direcionamento da propaganda política.

(7) A fim de facilitar o acesso de terceiros e do público aos avisos de transparência dos anúncios de cariz político, a disponibilização da estrutura comum de dados, de metadados normalizados e da interface comum de programação de aplicações deverá permitir, entre outros, a criação de avisos de transparência de anúncios de cariz político facilmente acessíveis, legíveis por máquina e de fácil utilização, o que também reforçaria a conformidade com o artigo 12.º, n.º 3, e o artigo 13.º, n.^os^ 2 e 4, do Regulamento (UE) 2024/900 e minimizaria os encargos administrativos para os editores de anúncios de cariz político.

(8) A implementação de uma estrutura comum de dados, de metadados normalizados, de uma autenticação normalizada e de uma interface comum de programação de aplicações para o repositório europeu pode implicar o tratamento de dados pessoais, como os elementos dos avisos de transparência referidos no anexo II, pontos 3.1 a 3.3, do Regulamento de Execução (UE) 2025/1410, que deverá ser realizado em conformidade com as regras relativas à proteção de dados pessoais estabelecidas nos Regulamentos (UE) 2016/679 [([^6])](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntr6-L_202600818PT.000101-E0006) e (UE) 2018/1725 [([^7])](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntr7-L_202600818PT.000101-E0007) do Parlamento Europeu e do Conselho.

(9) O presente regulamento introduz requisitos obrigatórios para os serviços públicos digitais transfronteiriços na aceção do Regulamento (UE) 2024/903 do Parlamento Europeu e do Conselho [([^8])](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntr8-L_202600818PT.000101-E0008). Por conseguinte, foi concluída uma avaliação da interoperabilidade. O capítulo «Dimensões digitais» da ficha financeira legislativa e digital apresenta o relatório resultante dessa avaliação.

(10) A Autoridade Europeia para a Proteção de Dados foi consultada em conformidade com o disposto no artigo 42.º, n.º 1, do Regulamento (UE) 2018/1725 e emitiu um parecer em 30 de janeiro de 2026.

(11) As medidas previstas no presente regulamento estão em conformidade com o parecer do Comité instituído pelo artigo 29.º, n.º 1, do Regulamento (UE) 2024/900,

ADOTOU O PRESENTE REGULAMENTO:

###### Artigo 1.º

As disposições pormenorizadas para a disponibilização de uma estrutura de dados comum, de metadados normalizados, de uma autenticação normalizada e de uma interface comum de programação de aplicações para o repositório europeu de anúncios de cariz político em linha constam do anexo do presente regulamento.

###### Artigo 2.º

O presente regulamento entra em vigor no vigésimo dia seguinte ao da sua publicação no *Jornal Oficial da União Europeia*.

O presente regulamento é obrigatório em todos os seus elementos e diretamente aplicável em todos os Estados-Membros.

Feito em Bruxelas, em 9 de abril de 2026.

***Pela Comissão***

***A Presidente***

**Ursula VON DER LEYEN**

---

## Notas

> [(^1^)](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntc1-L_202600818PT.000101-E0001) [JO L, 2024/900, 20.3.2024, ELI: http://data.europa.eu/eli/reg/2024/900/oj](https://data.europa.eu/eli/reg/2024/900/oj).

> [(^2^)](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntc2-L_202600818PT.000101-E0002) Regulamento (UE) 2022/2065 do Parlamento Europeu e do Conselho, de 19 de outubro de 2022, relativo a um mercado único para os serviços digitais e que altera a Diretiva 2000/31/CE (Regulamento dos Serviços Digitais) ([JO L 277 de 27.10.2022, p. 1](http://publications.europa.eu/resource/oj/JOL_2022_277_R_TOC), ELI: [http://data.europa.eu/eli/reg/2022/2065/oj](http://data.europa.eu/eli/reg/2022/2065/oj)).

> [(^3^)](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntc3-L_202600818PT.000101-E0003) [https://op.europa.eu/pt/web/eu-vocabularies/corevocs](https://op.europa.eu/en/web/eu-vocabularies/corevocs?etrans=pt).

> [(^4^)](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntc4-L_202600818PT.000101-E0004) Regulamento de Execução (UE) 2025/1410 da Comissão, de 9 de julho de 2025, relativo ao formato, ao modelo e às especificações técnicas dos rótulos e dos avisos de transparência dos anúncios de cariz político, em conformidade com os artigos 11.º e 12.º do Regulamento (UE) 2024/900 do Parlamento Europeu e do Conselho ([JO L, 2025/1410, 16.7.2025, ELI: http://data.europa.eu/eli/reg_impl/2025/1410/oj](https://data.europa.eu/eli/reg_impl/2025/1410/oj)).

> [(^5^)](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntc5-L_202600818PT.000101-E0005) As opções relativas à estratégia de desenvolvimento e contratação de tecnologias de informação serão sujeitas a aprovação prévia do Conselho das Tecnologias da Informação e da Cibersegurança da Comissão Europeia.

> [(^6^)](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntc6-L_202600818PT.000101-E0006) Regulamento (UE) 2016/679 do Parlamento Europeu e do Conselho, de 27 de abril de 2016, relativo à proteção das pessoas singulares no que diz respeito ao tratamento de dados pessoais e à livre circulação desses dados e que revoga a Diretiva 95/46/CE (Regulamento Geral sobre a Proteção de Dados) ([JO L 119 de 4.5.2016, p. 1](http://publications.europa.eu/resource/oj/JOL_2016_119_R_TOC), ELI: [http://data.europa.eu/eli/reg/2016/679/oj](http://data.europa.eu/eli/reg/2016/679/oj)).

> [(^7^)](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntc7-L_202600818PT.000101-E0007) Regulamento (UE) 2018/1725 do Parlamento Europeu e do Conselho, de 23 de outubro de 2018, relativo à proteção das pessoas singulares no que diz respeito ao tratamento de dados pessoais pelas instituições e pelos órgãos e organismos da União e à livre circulação desses dados, e que revoga o Regulamento (CE) n.º 45/2001 e a Decisão n.º 1247/2002/CE ([JO L 295 de 21.11.2018, p. 39](http://publications.europa.eu/resource/oj/JOL_2018_295_R_TOC), ELI: [http://data.europa.eu/eli/reg/2018/1725/oj](http://data.europa.eu/eli/reg/2018/1725/oj)).

> [(^8^)](http://publications.europa.eu/resource/cellar/52332f89-3475-11f1-be39-01aa75ed71a1.0020.03/DOC_1#ntc8-L_202600818PT.000101-E0008) Regulamento (UE) 2024/903 do Parlamento Europeu e do Conselho, de 13 de março de 2024, que estabelece medidas para um elevado nível de interoperabilidade do setor público em toda a União (Regulamento Europa Interoperável) ([JO L, 2024/903, 22.3.2024, ELI: http://data.europa.eu/eli/reg/2024/903/oj](https://data.europa.eu/eli/reg/2024/903/oj)).
