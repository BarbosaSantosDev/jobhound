Feature: API de status do pipeline
  Como o dashboard do jobhound
  Quero consultar o estado da execução do pipeline via HTTP
  Para saber quando parar de mostrar a tela de carregamento

  Scenario: Consultar o status sem nenhuma execução em andamento
    Given a API do jobhound configurada com um pipeline falso
    When eu consulto o status do pipeline
    Then a resposta deve ter running false e stage nulo

  Scenario: Status e segunda chamada de rodar durante uma execução em andamento
    Given a API do jobhound configurada com um pipeline falso
    When eu rodo o pipeline, consulto o status ainda em andamento e tento rodar de novo
    Then a resposta de status deve ter running true
    And a segunda chamada de rodar deve retornar 409
