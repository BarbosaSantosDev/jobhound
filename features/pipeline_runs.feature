Feature: Histórico de faros com status por fonte
  Como o dashboard do jobhound
  Quero saber quando foi o último faro e como foi cada fonte
  Para mostrar "último faro" e avisar quando uma fonte está fora do ar

  Background:
    Given o perfil "Ana" cadastrado para farejar
    And um histórico de faros vazio

  Scenario: Um faro registra o relatório de cada fonte
    Given a fonte "gupy" trazendo as vagas "job-1, job-2"
    And a fonte "nerdin" fora do ar com o erro "timeout"
    When o pipeline fareja para o perfil "ana"
    Then o último faro registrado deve ter status "ok" e perfil "ana"
    And o último faro deve ter 2 vagas novas
    And a fonte "gupy" deve constar como ok com 2 vagas
    And a fonte "nerdin" deve constar com falha "timeout"

  Scenario: Um faro que quebra é registrado como falho
    Given a fonte "gupy" trazendo as vagas "job-1"
    And um notificador que falha com o erro "telegram fora do ar"
    When o pipeline fareja para o perfil "ana" e a execução quebra
    Then o último faro registrado deve ter status "failed" e perfil "ana"
    And o último faro deve ter o erro "telegram fora do ar"

  Scenario: A API devolve o último faro do perfil no status
    Given a fonte "gupy" trazendo as vagas "job-1"
    And o pipeline já farejou para o perfil "ana"
    When eu consulto o status do pipeline do perfil "ana" pela API
    Then o status deve trazer o último faro com 1 vaga nova
    And o último faro da API deve listar a fonte "gupy" como ok
