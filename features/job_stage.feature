Feature: Etapas da vaga na triagem
  Como candidato usando o dashboard
  Quero salvar, marcar candidatura ou descartar uma vaga
  Para separar o que já tratei do que ainda é novo

  Background:
    Given a API do jobhound com um repositório de vagas em memória
    And a vaga "job-1" avaliada com score 85

  Scenario: Toda vaga avaliada começa como nova
    When eu listo as vagas
    Then a vaga "job-1" deve estar na etapa "new"

  Scenario: Mover a vaga para outra etapa
    When eu movo a vaga "job-1" para a etapa "saved"
    Then a resposta deve ter status 200
    And eu listo as vagas
    And a vaga "job-1" deve estar na etapa "saved"

  Scenario: Voltar uma vaga descartada para nova
    Given a vaga "job-1" já movida para "discarded"
    When eu movo a vaga "job-1" para a etapa "new"
    And eu listo as vagas
    Then a vaga "job-1" deve estar na etapa "new"

  Scenario: Vaga inexistente
    When eu movo a vaga "nao-existe" para a etapa "applied"
    Then a resposta deve ter status 404

  Scenario: Etapa inválida é recusada
    When eu movo a vaga "job-1" para a etapa "arquivada"
    Then a resposta deve ter status 422
