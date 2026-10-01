Feature: Resumo da vaga para o dashboard
  Como candidato
  Quero ler um trecho limpo da descrição da vaga
  Para decidir rápido se vale abrir o anúncio

  Scenario: Remove HTML e decodifica entidades
    Given uma vaga com a descrição "<p><strong>Sobre</strong> a vaga:<br>Python &amp; FastAPI</p>"
    When eu gero o resumo da vaga
    Then o resumo deve ser "Sobre a vaga: Python & FastAPI"

  Scenario: Descrição curta fica inteira
    Given uma vaga com a descrição "Vaga backend remota."
    When eu gero o resumo da vaga com no máximo 50 caracteres
    Then o resumo deve ser "Vaga backend remota."

  Scenario: Descrição longa é cortada na última palavra inteira
    Given uma vaga com a descrição "Buscamos pessoa desenvolvedora backend para atuar com microsserviços"
    When eu gero o resumo da vaga com no máximo 40 caracteres
    Then o resumo deve ser "Buscamos pessoa desenvolvedora backend…"

  Scenario: Descrição vazia não gera resumo
    Given uma vaga com a descrição "<p>  </p>"
    When eu gero o resumo da vaga
    Then não deve haver resumo
