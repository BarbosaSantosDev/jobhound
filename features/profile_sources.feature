Feature: Fontes de vagas por perfil
  Como candidato
  Quero escolher em quais fontes o jobhound fareja
  Para não receber vagas de onde não me interessa

  Scenario: Perfil novo fareja em todas as fontes
    Given um perfil com stack principal "Python" e secundária "Docker"
    Then as fontes ativas devem ser "gupy, nerdin, remoteok"

  Scenario: Fonte desligada não entra no faro
    Given um perfil com stack principal "Python" e secundária "Docker"
    And as fontes ligadas "gupy, nerdin"
    Then as fontes ativas devem ser "gupy, nerdin"

  Scenario: Fonte ligada sem termo de busca não entra no faro
    Given um perfil sem stack principal e com secundária "Docker"
    Then as fontes ativas devem ser "remoteok"

  Scenario: A API guarda as fontes escolhidas e informa as ativas
    Given a API do jobhound com um repositório de perfis em memória
    And o perfil "Ana Souza" registrado com as fontes "gupy, remoteok"
    When eu consulto o perfil "ana-souza"
    Then o perfil deve ter as fontes ligadas "gupy, remoteok"
    And o perfil deve ter as fontes ativas "gupy, remoteok"

  Scenario: Fonte desconhecida é recusada
    Given a API do jobhound com um repositório de perfis em memória
    When eu registro o perfil "Ana Souza" com a fonte "linkedin"
    Then a resposta deve ter status 422
