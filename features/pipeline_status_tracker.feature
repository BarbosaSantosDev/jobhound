Feature: Rastreador de status do pipeline
  Como backend do jobhound
  Quero rastrear se um pipeline está rodando agora
  Para que o 409 do POST /pipeline/run e o GET /pipeline/status sempre concordem

  Scenario: Do estado ocioso para rodando e de volta pra ocioso
    Given um rastreador de status novo
    When eu tento iniciar uma execução
    Then a tentativa deve ter sido aceita
    And o status deve indicar que está rodando
    When eu finalizo a execução sem erro
    Then o status deve indicar que não está rodando
    And o último erro deve ser nulo

  Scenario: Uma segunda tentativa de iniciar enquanto já está rodando é recusada
    Given um rastreador de status novo
    And uma execução já foi iniciada
    When eu tento iniciar uma execução
    Then a tentativa deve ter sido recusada

  Scenario: Uma execução que falha volta pra ocioso com o erro registrado
    Given um rastreador de status novo
    And uma execução já foi iniciada
    When eu finalizo a execução com o erro "falha ao extrair fatos"
    Then o status deve indicar que não está rodando
    And o último erro deve ser "falha ao extrair fatos"
