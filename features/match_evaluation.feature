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
    And a modalidade registrada deve ser "remote"

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
    And a modalidade registrada deve ser "not_informed"
  Scenario: Cada motivo diz para que lado pesou
    Given um perfil backend pleno com Python e FastAPI
    And uma vaga presencial sênior que exige Java
    When o matcher avalia a vaga
    Then o motivo "Stack exigida incompatível: java" deve contar contra
    And o motivo "Vaga sênior — possível stretch" deve ser neutro
    And o motivo "Localização/modo de trabalho fora das preferências" deve contar contra

  Scenario: Motivos a favor e neutros
    Given um perfil backend pleno com Python e FastAPI
    And uma vaga que menciona Python sem senioridade nem modo de trabalho
    When o matcher avalia a vaga
    Then o motivo "Vaga menciona stack principal: python" deve contar a favor
    And o motivo "Senioridade não informada" deve ser neutro
    And o motivo "Modo de trabalho não informado" deve ser neutro
