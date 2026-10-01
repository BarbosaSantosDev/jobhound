Feature: Vagas avaliadas por perfil
  Como alguém com mais de um perfil de caça
  Quero que cada perfil tenha as suas próprias avaliações e etapas
  Para que trocar de perfil mostre o faro daquele perfil

  Background:
    Given a API do jobhound com repositórios de vagas e perfis em memória
    And os perfis "Ana" e "Bruno" cadastrados
    And a vaga "job-a" avaliada para o perfil "ana" com score 90
    And a vaga "job-b" avaliada para o perfil "bruno" com score 80
    And a vaga "job-legado" avaliada antes de existirem perfis com score 70

  Scenario: Cada perfil vê as próprias avaliações e as legadas
    When eu listo as vagas do perfil "ana"
    Then as vagas listadas devem ser "job-a, job-legado"

  Scenario: Sem perfil, lista todas as avaliações
    When eu listo as vagas sem escolher perfil
    Then as vagas listadas devem ser "job-a, job-b, job-legado"

  Scenario: A etapa de uma vaga vale só para o perfil que a moveu
    Given a vaga "job-a" avaliada também para o perfil "bruno" com score 60
    When o perfil "ana" move a vaga "job-a" para a etapa "saved"
    Then para o perfil "ana", a vaga "job-a" deve estar na etapa "saved"
    And para o perfil "bruno", a vaga "job-a" deve estar na etapa "new"

  Scenario: Perfil inexistente
    When eu listo as vagas do perfil "fantasma"
    Then a resposta deve ter status 404

  Scenario: Vaga já avaliada por um perfil volta a ser oferecida para outro
    Given uma fonte que traz as vagas "job-a, job-nova"
    When eu busco vagas novas para o perfil "bruno"
    Then as vagas oferecidas devem ser "job-a, job-nova"
    When eu busco vagas novas para o perfil "ana"
    Then as vagas oferecidas devem ser "job-nova"
