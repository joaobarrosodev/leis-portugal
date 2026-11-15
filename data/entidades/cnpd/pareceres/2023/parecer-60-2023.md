---
schema_version: '1.0'
id: pt:cnpd:122097
title: Parecer da CNPD n.º 60/2023
short_title: null
summary: Banco de Portugal — Proposta de Instrução que visa alterar a Instrução n.º 8/2018 - Regulamento do Sistema de Compensação
  Interbancária…
jurisdiction: regulator
territory: null
document_type: parecer-cnpd
document_type_label: Parecer da Comissão Nacional de Proteção de Dados
issuing_authority:
- Comissão Nacional de Proteção de Dados
proposing_entity: null
official_number: 60/2023
official_date: '2023-06-27'
publication_date: null
publication: null
entry_into_force_dates: []
end_of_validity_date: null
legal_status: unknown
notes:
- 'Entidade: Banco de Portugal'
- 'Texto obtido por OCR em 5 de 5 página(s) (digitalização): pode ter erros de reconhecimento.'
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
  internal: pt:cnpd:122097
source:
  id: cnpd
  name: Comissão Nacional de Proteção de Dados
  official_url: https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/122097
  metadata_url: https://www.cnpd.pt/decisoes/historico-de-decisoes/?year=2023&type=4
  content_url: https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/122097
  consolidated_url: null
  retrieved_at: '2026-11-12T02:50:27Z'
  retrieval_method: Histórico de decisões do site da CNPD (páginas HTML) e descarga do PDF de cada decisão; não é uma API
  source_modified_at: null
integrity:
  source_sha256: 3f28c9442c1179ed71a0ca0269816af87576117feae61f500d05520d102ab17e
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal CNPD
  collector_version: 0.1.0
  generated_by: leis-portugal collect cnpd
  generated_at: '2026-11-12T02:50:27Z'
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
  checked_at: '2026-11-12T02:50:27Z'
  warnings: []
  errors: []
---

# Parecer da CNPD n.º 60/2023

PAR/2023/45 1
CNPD
Comissão Nacional de Proteção de Dados
PARECER/2023/60
I. Pedido 1. O Banco de Portugal (BdP) submeteu à Comissão Nacional de Proteção de Dados (CNPD), para parecer, a
Proposta de Instrução que visa alterar a Instrução n.º 8/2018 - Regulamento do Sistema de Compensação
Interbancária (SICOI).
2. A CNPD emite parecer no âmbito das suas atribuições e competências enquanto autoridade administrativa independente com poderes de autoridade para o controlo dos tratamentos de dados pessoais, conferidos pela alínea c) do n.º 1 do artigo 57.°, conjugado com a alínea b) do n.º 3 do artigo 58.°, e com o n.° 4 do artigo 36.°, todos do Regulamento (UE) 2016/679, de 27 de abril de 2016 - Regulamento Geral sobre a Proteção de Dados (doravante RGPD), em conjugação com o disposto no artigo 3.°, no n.º 2 do artigo 4.°, e na alínea a) do n.º 1 do artigo 6.°, todos da Lei n.° 58/2019, de 8 de agosto, que executa na ordem jurídica interna o RGPD.
3. Em 30 de maio de 2023 foi junta uma Avaliação de Impacto na Proteção de Dados (AIPD) do Projeto Proxy
Lookup e o relatório de requisitos de segurança
I. Análise 4. Nos termos do artigo 92.° do Regime Geral das Instituições de Crédito e Sociedades Financeiras (RGICSF) e do artigo 14.° da sua Lei Orgânica comete ao Banco de Portugal regular, fiscalizar e promover o bom funcionamento dos sistemas de pagamentos. Assim, o BdP é o regulador e gestor do Sistema de Compensação
Interbancária (SICOI), o sistema de pagamento de retalho onde são processados os pagamentos efetuados com cheques, efeitos comerciais, transferências a crédito, transferências imediatas, débitos diretos e operações baseadas em cartão.
5. O BdP pretende disponibilizar aos Prestadores de Serviços de Pagamento (PSP), participantes no SICOI, um serviço composto por duas funcionalidades: o mapeamento entre IBAN de contas de pagamento e um identificador do conhecimento do utilizador de serviços de pagamento (no caso, um número de telemóvel ou o
Número de Identificação de Pessoa Coletiva NIPC) _funcionalidade de proxy lookup; e a verificação da identidade do beneficiário de uma transferência a crédito ou do devedor de um débito direto no âmbito de uma operação de pagamento - funcionalidade de verificação do beneficiário/devedor.
6. De acordo com o Preâmbulo, a introdução destas novas funcionalidades tem como objetivo melhorar a usabilidade e segurança da execução de pagamentos, permitindo aos executantes a identificação da outra parte antes de completarem a operação.
Av. D. Carlos I, 134, 1° 1200-651 Lisboa
T (+351) 213 928 400
F (+351) 213 976 832 geral@cnpd.pt www.cnpd.pt

PAR/Z23/45 1V.
7. O Banco de Portugal pretende implementar e disponibilizar estas funcionalidades utilizando o SICOI, para permitir que todos os intervenientes desta rede de uma forma mais abrangente possam implementar e disponibilizar aos seus clientes estas novas funcionalidades.
8. O BP é o responsável pelo tratamento de dados decorrente da disponibilização das novas funcionalidades de pagamento aos participantes do SICOI, cujo fundamento de licitude reside na alínea e) do n.° 1 do artigo 6.° do
RGPD na medida em que resulta do exercício de funções de interesse publico e do exercício de autoridade pública de que o mesmo está investido.
9. Ao tratamento de dados já hoje realizado pelo Banco de Portugal para o processamento das operações de pagamento no SICOI, acrescerá o tratamento dos dados pessoais necessários à prossecução das finalidades de interesse público que lhe são atribuídas por lei, ao abrigo de poderes de autoridade pública, para oferecer um serviço mais seguro e de maior usabilidade.
10. Assim, e nos termos da Avaliação de Impacto sobre Proteção de Dados (AIPD) enviada, a funcionalidade
Proxy lookup pressupõe a existência de uma base de dados centralizada no Banco de Portugal, com a informação que os USP transmitiram ao seu PSP no âmbito da funcionalidade, e que foi devidamente certificada por este.
Esta informação contempla os dados necessários para dar resposta aos requisitos funcionais pelo Banco de
Portugal, enquanto fornecedor do serviço aos PSP.
11. A informação de associação ao Proxy Lookup é recebida dos PSP e armazenada na base de dados, onde ficará enquanto permanecer no estado "Ativo". A informação será removida da base de dados quando o utilizador instruir o seu PSP nesse sentido.
12. No que respeita à funcionalidade Confirmação do nome do beneficiário/devedor a confirmação será realizada através de chamadas às API que passarão sempre pelo Banco de Portugal e serão reencaminhadas para os PSP dos beneficiários/devedores. Mais concretamente, o Banco de Portugal receberá o pedido do PSP do ordenante/credor e encaminhará o pedido para o PSP do beneficiário/devedor (onde a informação relevante reside). Os PSP não terão de reportar dados dos seus USP ao Banco de Portugal para ficarem centralizados no
Banco de Portugal. O PSP do ordenante/credor facultará o identificador da conta de pagamento (IBAN) e receberá do PSP do beneficiário/devedor o nome do primeiro titular da mesma.
13. Quanto à funcionalidade Confirmação do par IBAN/NIF do beneficiário/devedor o modelo de dados que será utilizado na funcionalidade de confirmação do par IBAN/NIF do beneficiário/devedor será descentralizado. A confirmação será realizada através de chamadas às API que passarão sempre pelo Banco de Portugal e serão reencaminhadas para os PSP dos beneficiários/devedores. Mais concretamente, o Banco de Portugal receberá o pedido do PSP do ordenante/credor e encaminhará o pedido para o PSP do beneficiário/devedor (onde a

PAR/2023/45 | 2
CNPD
Comissão Nacional de Proteção de Dados informação relevante reside). Os PSP não terão de reportar dados dos seus USP ao Banco de Portugal para ficarem registados/centralizados no Banco de Portugal. O PSP do ordenante/credor facultará o identificador da conta de pagamento (IBAN) e o NIF e receberá do PSP do beneficiário/devedor apenas respostas Sim/Não, consoante o NIF indicado pertença (ou não) a um dos titulares da conta.
14. A implementação destas funcionalidades implica a comunicação, por parte dos PSP participantes no SICOI, de alguns dados pessoais dos seus clientes, ao Banco de Portugal.
15. O BdP assegura a centralização e manutenção da informação, que lhe é transmitida através do BPnet pelos participantes, assim como a resposta aos pedidos de consulta por estes efetuados.
16. No caso do Proxy lookup, o Banco de Portugal será titular de uma base de dados, alimentada pelos PSP com dados que lhe foram transmitidos pelos USP expressamente para este efeito. No caso do CoPS e do COPB, o
Banco de Portugal apenas armazenará a informação relevante por questões de controlo (da utilização das funcionalidade pelos PSP/ USP e para eventual prestação de informação a autoridades judiciárias).
17. Os dados pessoais objeto de tratamento são o nome, NIF, telefone e IBAN da conta de pagamento, sendo adequados, pertinentes e limitados ao que é necessário às finalidades para os quais são tratados em obediência ao princípio da necessidade e da minimização dos dados consagrado na alínea c) do n.° 1 do artigo 5.° do RGPD.
18. Está prevista a implementação de validação em operações com múltiplos movimentos, em que é submetido junto com o montante e IBAN o NIF/NIPC por transação para validação. Neste cenário de utilização é devolvida uma resposta "sim" ou "não" para cada transação apenas ("Sim" - no caso de o NIF/NIPC pertencer a um dos titulares da conta de pagamento; "Não" - no caso de o NIF/NIPC não pertencer a um dos titulares da conta de pagamento.
19. A responsabilidade pela completude, atualidade e exatidão dos dados necessários à utilização das funcionalidades de CoPS e CoPB é da exclusiva responsabilidade dos participantes, que devem fazer as devidas validações na submissão do pedido dos seus clientes garantindo que os dados são dos seus clientes. As entidades devem também implementar sistemas fortes de autenticação para as operações de associação ou remoção destes identificadores que serão associados ao IBAN.
20. Os participantes devem prever expressamente, no contrato-quadro com os utilizadores de serviços de pagamento as regras de suspensão do serviço em caso de ser necessário por motivos objetivamente fundamentados que se relacionem com a segurança da funcionalidade de PL ou com a suspeita de utilização fraudulenta da mesma. Também são definidas as regras de comunicação deste bloqueio aos utilizadores finais, e de comunicação ao BdP situações anómalas que ocorram.
Av. D. Carlos I, 134, 1° 1200-651 Lisboa
T (+351) 213 928 400
F (+351) 213 976 832 geral@cnpd.pt www.cnpd.pt

PAR/2023/45 | 2v.
21. A informação trocada entre o BdP e os participantes, no âmbito da funcionalidade proxy lookup, é conservada pelo tempo em que a associação do «identificador do utilizador» estiver ativa e, ainda, por um período de dois anos após a eliminação da mesma. A informação trocada no âmbito das funcionalidades CoPS e COPB, é conservada por um período de dois anos. Considera-se cumprido o principio da limitação da conservação consagrado na alínea e) do n.° 1 do artigo 5.° do RGPD.
22. Nos termos da AIPD, a segurança da informação é efetuada de acordo com a Política de Segurança do Banco de Portugal (NAP/2018/0013), com as regras referentes à classificação da documentação (NAP/2017/0008) e espelhada nos procedimentos definidos no Regulamento da Comissão de Etica e dos Deveres Gerais de Conduta dos Trabalhadores do Banco de Portugal (NAP/2016/0007) e no Código de Conduta dos Trabalhadores do Banco de Portugal (NAP/2016/0015), assegurando níveis adequados de integridade, autenticidade, disponibilidade e confidencialidade requeridos para sua proteção, incluindo no que se reporta à segurança física contra danos e acessos físicos não autorizados, com especial atenção no que toca a dados pessoais, em conformidade com a legislação, políticas e recomendações do Sistema Europeu de Bancos Centrais, do RGPD e legislação nacional aplicável.
23. São indicadas medidas técnicas e organizativas para garantir a segurança da informação. Existe, no entanto, uma pequena possibilidade de abuso da funcionalidade que pode ser explorada, se alguém iniciar repetidamente um conjunto de operações sem as concluir com o intuito de obter o nome do titular de um determinado identificador sem concluir a operação. Assim como o descobrir o identificador IBAN com base num NIPC ou telemóvel para quem tenha aderido à funcionalidade. No entanto estes comportamentos podem ser detetados e controlados pelos PSP na sua implementação das interfaces a criar com os seus clientes, quer minimizando a informação disponibilizada antes da operação ser concluída, quer por limitar o número de operações incompletas consecutivas.
24. O Anexo IX, ora aditado à Instrução n.º 8/2018, de 22 de março, regula no ponto 19 o direito à proteção de dados. Aí se consagra que os participantes devem garantir o cumprimento da legislação aplicável à proteção de dados, designadamente do RGPD. No caso de funcionalidade de PL, os participantes devem garantir aos utilizadores de serviços de pagamento o direito a conhecer a informação que a seu respeito conste da base de dados do BP e de solicitar, quando verifiquem a existência de erros ou omissões, a sua retificação ou atualização junto do participante, que será responsável pela respetiva comunicação ao BP.
25. Acrescenta-se que eventuais pedidos de informação ou esclarecimentos relacionados com o exercício de direitos relativos à proteção de dados pessoais no âmbito das funcionalidades previstas no serviço PLCP devem ser dirigidos à encarregada de proteção de dados do BP.

PAR/2023/45 3
CNPD
Comissão Nacional de Proteção de Dados 26. Ora, do direito de acesso previsto no artigo 15.° do RGPD resulta que o titular dos dados tem o direito de obter do responsável pelo tratamento a confirmação de que os seus dados pessoais que lhe digam respeito são ou não objeto de tratamento e, se for o caso, o direito de aceder aos seus dados pessoais. O mesmo se diga relativamente ao direito de retificação que deverá ser assegurado pelo responsável pelo tratamento.
27. Assim, recomenda-se a revisão do ponto 19.2 do Anexo IX por forma a prever o exercício destes direitos pelos USP diretamente junto do BP.
II. Conclusão 28. Com os fundamentos acima expostos, a CNPD recomenda:
a) Que os PSP na implementação das interfaces a criar com os UPS, procedam à minimização da informação disponibilizada antes da operação ser concluída, e à limitação do número de operações incompletas consecutivas nos termos descritos no ponto 27; e b) A reformulação do ponto 19.2 do Anexo IX por forma a clarificar o exercício do direito de acesso e retificação do titular dos dados junto do BP.
Aprovado na reunião de 27 de junho de 2023
Pele Me t
Paula Meira Lourenço (Presidente)
Av. D. Carlos I, 134, 1° 1200-651 Lisboa
T (+351) 213 928 400
F (+351) 213 976 832 geral@cnpd.pt www.cnpd.pt
