Feature: Avaliação de match entre vaga e perfil
  Como candidato
  Quero que vagas sejam pontuadas contra meu perfil
  Para receber apenas oportunidades relevantes

  Scenario: Vaga com stack compatível e senioridade correta
    Given um perfil backend pleno com Python e FastAPI
    And uma vaga remota que menciona Python e FastAPI para pleno
    When o matcher avalia a vaga
    Then o score deve ser maior ou igual a 70
    And a vaga deve ser marcada como digna de aplicação

  Scenario: Vaga sênior com stack incompatível
    Given um perfil backend pleno com Python e FastAPI
    And uma vaga presencial sênior que exige Java
    When o matcher avalia a vaga
    Then deve haver red flag "stack_incompatible"
    And a vaga não deve ser marcada como digna de aplicação

  Scenario: Vaga na zona cinzenta vai para revisão manual
    Given um perfil backend pleno com Python e FastAPI
    And uma vaga que menciona Python sem senioridade nem modo de trabalho
    When o matcher avalia a vaga
    Then a vaga deve ser marcada para revisão manual