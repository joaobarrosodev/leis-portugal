---
schema_version: '1.0'
id: pt:cnpd:82451
title: Parecer da CNPD n.º 73/2015
short_title: null
summary: SPMS - Serviços Partilhados do Ministério da Saúde, EPE — Parecer sobre as normas técnicas de software de prescrição
  electrónica de medicamentos e produtos d…
jurisdiction: regulator
territory: null
document_type: parecer-cnpd
document_type_label: Parecer da Comissão Nacional de Proteção de Dados
issuing_authority:
- Comissão Nacional de Proteção de Dados
proposing_entity: null
official_number: 73/2015
official_date: '2015-10-06'
publication_date: null
publication: null
entry_into_force_dates: []
end_of_validity_date: null
legal_status: unknown
notes:
- 'Entidade: SPMS - Serviços Partilhados do Ministério da Saúde, EPE'
- 'Texto obtido por OCR em 4 de 4 página(s) (digitalização): pode ter erros de reconhecimento.'
language: por
version:
  kind: original
  label: Texto da decisão publicada no site da CNPD
  language: por
  consolidation_date: null
identifiers:
  celex: null
  eli: null
  oj: null
  dre: null
  dre_path: null
  internal: pt:cnpd:82451
source:
  id: cnpd
  name: Comissão Nacional de Proteção de Dados
  official_url: https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/82451
  metadata_url: https://www.cnpd.pt/decisoes/historico-de-decisoes/?year=2015&type=4
  content_url: https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/82451
  consolidated_url: null
  retrieved_at: '2026-11-12T03:00:56Z'
  retrieval_method: Histórico de decisões do site da CNPD (páginas HTML) e descarga do PDF de cada decisão; não é uma API
  source_modified_at: null
integrity:
  source_sha256: 7f32e4982b466f528ca6a5c2d4ba2aa64676125e2c4245f2bdb9914c8401407d
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal CNPD
  collector_version: 0.1.0
  generated_by: leis-portugal collect cnpd
  generated_at: '2026-11-12T03:00:56Z'
  notes: null
reuse:
  status: permitted_with_conditions
  attribution: Comissão Nacional de Proteção de Dados (www.cnpd.pt) — todos os direitos reservados
  reference: https://www.cnpd.pt/avisos-legais-e-outras-informacoes/
  notes: Reprodução total ou parcial permitida com distribuição gratuita, integridade dos documentos e citação expressa do
    site com a menção de direitos reservados; uso pessoal, associativo ou profissional, sem fins comerciais ou publicitários.
    Só a cópia certificada tem valor legal.
subjects: []
relationships: []
article_structure: null
derived_material:
  machine_generated: true
  notes: null
validation:
  status: validated
  checked_at: '2026-11-12T03:00:56Z'
  warnings: []
  errors: []
---

# Parecer da CNPD n.º 73/2015

Proc. n.° 12530/2015
COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS
Parecer n.° 73/2015
A SPMS - Serviços Partilhados do Ministério da Saúde, EPE, (SPMS) remeteu à
Comissão Nacional de Protecção de Dados (CNPD) um documento designado por "Normas técnicas de software de prescrição eletrónica de medicamentos", para pronúncia.
A definição, aprovação e publicitação das normas técnicas relativas a prescrição e dispensa eletrónica de medicamentos está prevista nos n.ºs 1 e 2 do artigo 21.° da
Portaria n.º 224/2015, de 27 de julho, doravante Portaria, especificando o n.º 4 daquele artigo que a SPMS emite as especificações técnicas e os requisitos de segurança necessários para a produção da receita desmaterializada, incluindo os mecanismos a utilizar e a respetiva estrutura de dados.
Na medida em que as normas, as especificações técnicas e os requisitos de segurança da prescrição eletrónica podem, caso não sejam os adequados, colocar problemas de autenticidade, integridade e privacidade, com reflexos diretos para a proteção de dados pessoais, considerou a CNPD, no Parecer n.º 57/2015, dever pronunciar-se, o que veio refletir-se no artigo 22.° da Portaria, que determina o parecer prévio da CNPD a aprovação das normas, requisitos e especificações dos sistemas de prescrição eletrónica.
Numa apreciação geral do documento remetido ressalta que dele não constam referências a questões que se consideram da maior relevância. Destas, destacam-se, em especial, as seguintes:
- Definição de requisitos para garantir que, quer a comunicação entre os sistemas de dispensa e o sistema central, quer o armazenamento da informação são efetuados de modo a assegurar a confidencialidade e integridade dos dados;
- Definição de requisitos mínimos de segurança física e lógica;
- Estabelecimento de regras organizacionais e técnicas para as situações em que o processamento e o armazenamento da informação não ocorra em sistemas detidos pelo prescritor, ¡.e. nas situações em que existem entidades externas a assegurar os sistemas de prescrição.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976 832 www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 12530/2015 2
COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS
Deste modo, não pode a CNPD verificar se os requisitos técnicos que serão adotados para esta finalidade garantem a autenticidade e integridade da prescrição e a privacidade dos titulares dos dados pessoais.
Ainda assim, quanto ao teor do documento remetido suscitam-se algumas questões que, por necessitarem de alteração ou clarificação, a seguir se elencam:
a) - Na Secção 4.6.1., sob a epígrafe Operação Online, é descrito o procedimento para as situações de "insucesso na validação" de receita. Aí se refere que o software de prescrição eletrónica (PEM) notifica o prescritor desse insucesso, identificando o erro para correção. Na eventualidade de não ser possível a correção do erro, em tempo útil, o PEM deve emitir a receita em operação offline.
Ora, não há qualquer elemento que permita ter um intervalo de tempo para este "tempo útil", o que pode suscitar problemas de integridade da prescrição. A CNPD sublinha que os procedimentos excecionais devem ser exaustivamente caracterizados;
b) - Na Secção 5.2.2., sob a epígrafe Prescrição materializada enunciam-se as situações em que uma receita eletrónica online pode ser materializada, sendo a primeira delas a indisponibilidade da "autenticação forte/chave móvel digital".
Neste caso, apresenta-se como alternativa de autenticação a utilização das credenciais de acesso ao Portal de Requisição de Vinhetas e Receitas (PRVR).
Em primeiro lugar, nota-se que não se indica onde reside esta indisponibilidade, se no fornecedor dos serviços, se no prescritor. Em segundo lugar, não são estabelecidas quaisquer limitações a essa forma de acesso, designadamente número máximo de acessos num período definido. Ora, como a autenticação perante o PRVR não é uma autenticação forte, a mesma suscita reservas por poder colocar em causa garantias de não repúdio, tanto mais que não é referida qualquer alarmística dirigida à monitorização da utilização deste recurso alternativo.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976 832 www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 12530/2015 3
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
Relembra-se que a Portaria, no artigo 10.°, exige que a prescrição desmaterializada, aquela que deve ser a regra, seja efetuada por recurso a autenticação forte. O expediente de transformação de uma receita eletrónica online em receita materializada por ausência de autenticação forte deve ser excecional e tal deve ser refletido nestas normas.
c) - Nas Secções 5.6.1. e 5.6.2., sob as epígrafes respetivamente de Prescrição
Desmaterializada e Prescrição Materializada, é indicado que o contacto telefónico dos médicos prescritores é um elemento obrigatório.
No Parecer n.º 57/2015, a CNPD considerou que, não se alcançando as razões de facto e de direito que poderiam estar na origem da exigência desta informação, com natureza obrigatória, nem em que medida tal informação era apta a transmitir aos destinatários que o prescritor era profissional de saúde (cf. artigo 3°, n.º1, alíneas ccc) e hhh), do Decreto-Lei n.º 176/2006, de 30 de agosto), a validade da receita não poderia depender desta informação. Neste sentido, concluiu-se que apenas com o consentimento do próprio médico prescritor tal dado poderia ser recolhido, com a ressalva de que detém natureza opcional. Esta posição foi acolhida, apenas estando prevista a obrigatoriedade do contacto telefónico do prescritor nos casos de prescrição não eletrónica (cf. alínea c) do artigo 12.° da
Portaria). Deste modo, entende-se que deverá tal situação ser refletida no documento.
d) Na Secção 5.7., relativa à Identificação do Utente, é indicado que (...) o software de PEM deve recolher outros dados relativos à identificação do utente, nomeadamente: nacionalidade, sexo e data de nascimento.
Desde logo, importa sublinhar que neste ponto não se alude à prescrição mas antes aos softwares de prescrição, o que não pode deixar de causar perplexidade.
Da redação resulta a dúvida se o pretendido é que das prescrições constem tais elementos ou que os softwares recolham e guardem esta informação, a que
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976832 www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 12530/2015 4
COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS acresce, se o sentido for este último, não se indicar onde é guardada a informação.
Qualquer que seja a resposta, parece que estes dados serão consultados no
Registo Nacional de Utente e, eventualmente, processados no sistema de prescrição, não sendo evidente nem estando demonstrada a sua necessidade.
Ora, os dados pessoais a constar na prescrição estão exaustivamente elencados na Portaria, deles não constando os dados supra indicados. Não se pode através das normas técnicas pretender alargar o tratamento de dados pessoais a mais informações do que aquelas que foram definidas e são necessárias para finalidade da prescrição, devendo ser o documento corrigido nesta parte;
e) Na Secção 8.4, sob epígrafe Códigos para a dispensa, não é indicado o algoritmo para a criação dos códigos de dispensa e direito de opção a inscrever na guia de tratamento. Estando-se perante normas técnicas seria expectável que estivesse definida a estrutura constitutiva destes códigos. Não havendo qualquer informação dá-se apenas nota que dos códigos não pode constar informação que diretamente identifique o utente, v.g. n.° de utente.
É este o parecer da CNPD.
Lisboa, 6 de outubro de 2015
Filipa Calvão (Presidente)
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976 832 www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt
