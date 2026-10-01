Feature: API de perfis
  Como o dashboard do jobhound
  Quero listar os perfis cadastrados
  Para trocar de perfil sem precisar saber o slug de cor

  Background:
    Given a API do jobhound com um repositório de perfis em memória

  Scenario: Sem perfis cadastrados a lista vem vazia
    When eu listo os perfis
    Then a resposta deve ter status 200
    And a lista de perfis deve ser vazia

  Scenario: Lista os perfis do atualizado mais recentemente para o mais antigo
    Given o perfil "Ana Souza" registrado com a stack "Python"
    And o perfil "Bruno Lima" registrado com a stack "Go"
    When eu atualizo a headline do perfil "ana-souza" para "Backend Sênior"
    And eu listo os perfis
    Then os slugs listados devem ser "ana-souza, bruno-lima"
    And o perfil "ana-souza" listado deve ter a headline "Backend Sênior"
