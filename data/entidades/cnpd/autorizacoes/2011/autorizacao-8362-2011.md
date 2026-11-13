---
schema_version: '1.0'
id: pt:cnpd:35066
title: Autorização da CNPD n.º 8362/2011
short_title: null
summary: Hospitais da Universidade de Coimbra — Gestão de processo clínico e prescrição medicamentosa electrónica
jurisdiction: regulator
territory: null
document_type: autorizacao-cnpd
document_type_label: Autorização da Comissão Nacional de Proteção de Dados
issuing_authority:
- Comissão Nacional de Proteção de Dados
proposing_entity: null
official_number: 8362/2011
official_date: '2011-08-03'
publication_date: null
publication: null
entry_into_force_dates: []
end_of_validity_date: null
legal_status: unknown
notes:
- 'Entidade: Hospitais da Universidade de Coimbra'
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
  internal: pt:cnpd:35066
source:
  id: cnpd
  name: Comissão Nacional de Proteção de Dados
  official_url: https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/35066
  metadata_url: https://www.cnpd.pt/decisoes/historico-de-decisoes/?year=2011&type=1
  content_url: https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/35066
  consolidated_url: null
  retrieved_at: '2026-11-13T06:06:54Z'
  retrieval_method: Histórico de decisões do site da CNPD (páginas HTML) e descarga do PDF de cada decisão; não é uma API
  source_modified_at: null
integrity:
  source_sha256: 0505412ffd18166ea363cf836f3fc4f73945a64585fd79fa0126dbf06199572a
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal CNPD
  collector_version: 0.1.0
  generated_by: leis-portugal collect cnpd
  generated_at: '2026-11-13T06:06:54Z'
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
  checked_at: '2026-11-13T06:06:54Z'
  warnings: []
  errors: []
---

# Autorização da CNPD n.º 8362/2011

1
Proc. n.º 2830/2006
AUTORIZAÇÃO Nº 8362/ 2011
I. Pedido de autorização
Os Hospitais da Universidade de Coimbra notificaram à CNPD um tratamento de dados pessoais para prescrição medicamentosa através de receita electrónica, utilizando a aplicação
ALERT®.
No âmbito da prescrição electrónica há comunicação de dados para a ACSS, no âmbito do
Sistema de Conferência de Facturas de Medicamentos;
Os dados pessoais registados são: n.º de processo, nome, sexo, data de nascimento, morada, estado civil, profissão, filiação, habilitações literárias, n.º de BI/Passaporte/Carta de Condução,
NIF, n.º de utente, subsistema de saúde, seguro de saúde, regime de comparticipação medicamentosa/isenção, fotografia do utente, dados clínicos (anamnese, história clínica, exame físico, diagnóstico, prognóstico, MCD, terapêutica, dados sobre os medicamentos prescrito, número da Ordem dos Médicos do prescritor, código do local de prescrição e dados da receita - número da receita, data da prescrição, tipo de receita – renovável/ não renovável –
, notas e avaliação de enfermagem, alta, pareceres médicos, processo cirúrgico. São ainda registados os dados de marcação de consultas e de facturação.
A informação de prescrição fica associada ao tratamento relativo aos episódios de consulta.
A receita é impressa e entregue ao utente ou, se em ambiente hospitalar, enviada para a farmácia hospitalar para requisição do medicamento. Pode, também, ser determinada a opção de “administração do medicamento”.
O acesso à informação pelos médicos e enfermeiros está definido por diferentes perfis de utilizadores e níveis de acesso.
O profissional de saúde com o perfil “médico” pode registar e aceder a toda a informação, estando a capacidade de prescrever apenas disponível para este perfil.

2
Para o perfil “enfermeiro” apenas está disponível a visualização da informação necessária para os actos de enfermagem, o registo sobre os medicamentos prescritos e sobre a administração do medicamento no episódio.
O utilizador com o perfil de “administrativo” tem acesso às funcionalidades estritamente necessárias à sua actividade, podendo aceder a uma grelha com todas as consultas agendadas e efectuadas, altas, MCD agendados e dados de facturação.
Ao nível da segurança importa salientar que o software ALERT faz o reconhecimento dos utilizadores do sistema através de «impressão digital», recorrendo à solução “ Digital Persona
U.areU. 4000 USB Fingerprint Sensor ”, situação já apreciada pela CNPD.
O acesso ao sistema é efectuado por template da impressão dos utilizadores. O sistema faz a recolha óptica da impressão digital do utilizador a registar, guardando essa informação encriptada numa base de dados de utilizadores.
A encriptação das impressões digitais é um processo «one way». Ou seja, não é possível, a partir da representação encriptada de uma impressão digital, voltar a obter a impressão original. O processo de comparação é sempre feito entre informação já encriptada. Esta informação só pode ser utilizada para comparar com a encriptação da impressão digital que é lida no momento em que o utilizador se autentica na aplicação.
Cada acto de prescrição é enviado à ACSS, através da rede privada multimédia do Ministério da Saúde, em ficheiro XML, para integração no Sistema de Conferência de Facturas de
Medicamentos através de acesso ao sítio da ACSS, via RIS (Rede Interna da Saúde), em protocolo HTTPS. A autenticação na aplicação faz-se por login e password fornecidos pela
ACSS.
São comunicados os seguintes dados: Dados do utente (sexo, data de nascimento, localidade);
Dados sobre o medicamento (n.º de registo, quantidade, tipo de medicamento, produtos abrangidos pelo protocolo da Diabetes, descrição do manipulado, autorização para fornecimento de genérico); Dados do médico prescritor (n.º de prescritor atribuído pela Ordem dos Médicos); Local de prescrição e dados sobre a receita (n.º, data, tipo de receita, regime especial de comparticipação).

3
Na notificação foi indicado existir fluxos transfronteiriços de dados para os Estados Unidos da
América, no âmbito do armazenamento dos dados num Data Center da Alert Life Sciences
Computing, SA.
Posteriormente, após reuniões com a Alert Life Sciences Computing, SA, foi comunicado, em 4 de Fevereiro de 2011, que o Data Center estará localizado em Portugal, deixando, por isso, de haver fluxos para os EUA.
Finalmente, importa ainda ter em conta que o software ALERT® é propriedade da Alert Life
Sciences Computing, SA, entidade que armazena a informação e que, por força de contrato com o responsável, assegura as medidas de segurança indicadas. Esta entidade assume a qualidade de subcontratada.
II. Apreciação Jurídica
Os dados pessoais recolhidos são pertinentes, necessários e não excessivos em relação à finalidade do tratamento (cf. artigo 5.º n.º 1 al. c) da Lei 67/98).
O tratamento de dados de saúde é realizado para fins de «medicina preventiva, de diagnóstico médico, de prestação de cuidados ou tratamentos médicos ou de gestão de serviços de saúde» (cf. artigo 7.º n.º 4 da Lei 67/98, de 26 de Outubro). Ao mesmo tempo, e tal como resulta do mesmo preceito, o tratamento desses dados é efectuado «por um profissional de saúde obrigado a sigilo ou por outra pessoa sujeita igualmente a segredo profissional».
A transmissão de dados à ACSS para integração no Sistema de Conferência de Facturas de
Medicamento já foi autorizada pela CNPD, designadamente nas autorizações 36/99 e 38/2001, apenas se alterando agora o suporte da comunicação.
A identificação dos utilizadores faz-se através de um «par de chaves»: número de utilizador e impressão digital. É inegável que este sistema de autenticação do utilizador confere uma especial segurança à aplicação informática, impedindo que pessoas não autorizadas acedam aos dados de saúde.

4
Evita-se, deste modo, a utilização e cedência de passwords entre utilizadores, assegurando o sistema que apenas o utilizador autorizado pode ter acesso à aplicação, de acordo com os perfis definidos.
Deve ser dado especial cuidado à actualização desta informação, eliminando do sistema as impressões digitais dos utilizadores que já não exerçam funções na entidade.
Quanto à segurança da informação, deve o responsável pelo tratamento adoptar regras de procedimento interno, de forma a analisar periodicamente os registos de acesso (logs), para garantir que os acessos à informação se efectuam de acordo com os princípios da necessidade e pertinência. Os logs e os relatórios de análise devem ser conservados durante o período máximo de conservação da informação, para efeitos de auditoria da CNPD no exercício das suas competências.
Relativamente à subcontratação com a Alert Life Sciences Computing, SA, deve o responsável cumprir o disposto no artigo 14º da LPD, designadamente estabelecer um contrato ou acto jurídico com a subcontratada que a vincule ao cumprimento das obrigações de segurança do tratamento, previstas no n.º 1 do artigo 14º e, por se tratar de dados sensíveis, do artigo 15º, ambos da LPD.
Nesse contrato ou acto jurídico, o qual revestirá a forma escrita, com valor probatório legalmente reconhecido, deve constar que o subcontratante apenas actua mediante instruções do responsável pelo tratamento e que lhe incumbe a obrigação de pôr em prática as medidas técnicas e organizativas adequadas para proteger os dados pessoais contra a destruição acidental ou ilícita, a perda acidental, a alteração, a difusão ou acesso não autorizados, bem como para garantir um nível de segurança adequado em relação aos riscos inerentes ao tratamento e à natureza dos dados a proteger (cf. artigo 14º da Lei n.º 67/98).
A CNPD determina, ao abrigo do n.º 4 do artigo 15º da LPD, que a circulação da informação em rede, porque pode pôr em risco direitos, liberdades e garantias dos titulares, deve ser encriptada.

5
Independentemente das medidas de segurança adoptadas pela entidade responsável pelo tratamento, é a esta que cabe assegurar o resultado da efectiva segurança da informação e dos dados tratados.
III. Decisão
Deste modo, a CNPD autoriza o tratamento de dados – cf. artigos 7.º n.º 2, e n.º4, 28.º n.º 1 al.
a), 23.º n.º 1 al. b) e 30º da Lei n.º 67/98 – com as condições acima referidas.
Termos do tratamento:
1. Responsável: Hospitais da Universidade de Coimbra 2. Categorias de dados pessoais tratados: n.º de processo, nome, sexo, data de nascimento, morada, estado civil, profissão, filiação, habilitações literárias, n.º de
BI/Passaporte/Carta de Condução, NIF, n.º de utente, subsistema de saúde, seguro de saúde, regime de comparticipação medicamentosa/isenção, fotografia do utente, dados clínicos (anamnese, história clínica, exame físico, diagnóstico, prognóstico, MCD, terapêutica, dados sobre os medicamentos prescrito, número da Ordem dos Médicos do prescritor, código do local de prescrição e dados da receita - número da receita, data da prescrição, tipo de receita – renovável/ não renovável –, notas e avaliação de enfermagem, alta, pareceres médicos, processo cirúrgico. São ainda registados os dados de marcação de consultas e de facturação.
São, ainda, registados os dados dos utilizadores e respectiva impressão digital.
3. Finalidade: Prescrição medicamentosa electrónica.
4. Entidades a quem podem ser transmitidos: ACSS, no âmbito do Sistema de Conferência de Facturas de Medicamentos, sem transmissão de dados pessoais dos utentes;
5. Forma de exercício do direito de acesso e rectificação: Por solicitação escrita ou pessoal. A informação de saúde é revelada por «intermediação médica» (cf. artigo 11.º n.º 5 da
Lei 67/98).
6. Eventuais interconexões: Apenas aquelas permitidas pelo software de base e necessários ao funcionamento do sistema: ligação do software administrativo e laboratorial do Hospital.
7. Transferências de dados para países terceiros: Não há.
8. Tempo de conservação:
a) Dados de saúde – Nos termos do anexo à Portaria n.º 247/2000, de 8 de Maio;

6 b) Dados biométricos – Serão obrigatoriamente eliminados no momento da transferência do trabalhador para outro posto de trabalho ou no caso de cessação de funções.
c) Dados de facturação – 10 anos.
Deve ser dado conhecimento da presente autorização a todos os intervenientes no circuito da informação, designadamente aos utilizadores do sistema e ao subcontratado.
Esta Autorização é emitida no pressuposto de que o software em questão foi certificado pela ACSS.
Lisboa, 03 de Agosto de 2011
￼
Ana Roque, Luís Barroso, Carlos Campos Lobo, Helena Delgado António, Luís Paiva de
Andrade, Vasco Almeida e Luís Lingnau da Silveira (Presidente)
