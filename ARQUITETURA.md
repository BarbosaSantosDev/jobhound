# Como o jobhound funciona

Assistente pessoal de busca de vagas: procura vagas em fontes públicas, usa um LLM
para extrair **fatos objetivos** de cada vaga, e um código determinístico (sem LLM)
pontua o quão bem ela combina com o seu perfil. O LLM não decide "gosto" nem inventa
número — só lê e extrai o que está escrito na vaga.

Este repositório é a API e o pipeline (o backend). O dashboard web é um projeto
separado: <!-- TODO: link do repo do frontend -->. Rodando só este repositório,
sem o dashboard, o resultado chega por notificação no Telegram e pela CLI
(`jobhound top`) — o dashboard é uma forma opcional de visualizar o mesmo resultado
pelo navegador.

## As peças

- **backend** (este repositório) — API FastAPI + pipeline. Python, Clean
  Architecture + DDD. Funciona sozinho — Telegram e `jobhound top` são as saídas
  nativas.
- **frontend** (repositório separado, opcional) — dashboard React, consome a API.
  <!-- TODO: link do repo do frontend -->
- **Postgres** — sobe junto no `docker-compose` (`db`), com seu próprio volume
  (`pgdata`). Pode apontar pra outra instância trocando `DATABASE_URL` no `.env`.
- **Ollama** — roda local (container `jobhound_ollama`), serve o modelo que extrai
  fatos das vagas.

## O fluxo ponta a ponta

1. **Perfil** — você cadastra um perfil (nome, senioridade, stack principal/secundária,
   localizações preferidas, aceita remoto, resumo). Os termos de busca de cada fonte
   (Gupy, Nerdin, RemoteOK) são **derivados automaticamente** da sua stack — você não
   escolhe isso diretamente.
2. **Buscar vagas** (`FetchNewJobs`) — cada fonte é consultada com os termos derivados.
   Vagas repetidas (mesmo título+empresa+local, via hash) são descartadas, e vagas já
   salvas no banco não entram de novo.
3. **Extrair fatos** (`EvaluateJobMatch` → LLM via Ollama) — para cada vaga nova, o LLM
   lê a descrição e extrai só fatos objetivos: stack mencionada, senioridade, modo de
   trabalho, cidade, faixa salarial.
4. **Pontuar** (`ScoreJob`, domínio puro, sem LLM) — compara os fatos extraídos com o
   seu perfil e calcula um score 0-100 com motivos explicados: stack bate (peso 50),
   senioridade bate (peso 30), localização/remoto bate (peso 20).
5. **Salvar + notificar** — o resultado vai pro Postgres; se a vaga for boa
   (`is_worth_applying`) ou merecer revisão manual (`needs_manual_review`), dispara um
   Telegram (se configurado). Esse passo, mais `jobhound top` na CLI, já é suficiente
   pra usar o projeto só com este repositório.
6. **Frontend** (opcional, repositório separado) — o dashboard busca `/api/v1/matches`
   e `/api/v1/stats` a cada poucos segundos (polling) e mostra a lista sem precisar
   recarregar a página.

```
perfil (você)
  -> deriva termos de busca (stack)
  -> Gupy / Nerdin / RemoteOK --fetch--> vagas novas (dedup por fingerprint)
  -> LLM (Ollama) extrai fatos --> domínio pontua (0-100 + motivos)
  -> Postgres salva --> Telegram notifica (se match)
  -> jobhound top (CLI) ou frontend (opcional) mostram o resultado
```

## Como disparar o pipeline

- `POST /api/v1/pipeline/run` — usado pelo botão "rodar pipeline" do frontend. Roda em
  background, uma vez; devolve 409 se já tiver um rodando.
- `jobhound run` — mesma coisa, via CLI.
- `python -m src.scheduler` — roda o pipeline a cada 3h. Não faz parte do
  `docker-compose` hoje; suba manualmente se quiser recorrência automática.

## Camadas (Clean Architecture + DDD)

```
src/
├── domain/   regras de negócio puras — Profile, Job, JobFacts, MatchResult, ScoreJob.
│             Não conhece banco, HTTP nem LLM.
├── app/      casos de uso (orquestram domínio + infra) — FetchNewJobs,
│             EvaluateJobMatch, RegisterProfile...
├── infra/    implementações concretas — Postgres (SQLAlchemy), scrapers
│             (Gupy/Nerdin/RemoteOK), LLM (LangChain + Ollama/Anthropic), rotas FastAPI.
├── server.py    monta a API HTTP
├── cli.py       comandos de terminal
└── scheduler.py roda o pipeline periodicamente
```

Regra de ouro do projeto: **o LLM extrai fatos, o domínio pontua**. É o que torna o
score testável — `ScoreJob` é testado sem nenhum LLM real (`features/`, com um
`FakeExtractor` determinístico).

## Isso está pronto pra produção?

Pra uso pessoal, single-user, numa rede privada/VPS que só você acessa: **sim**, depois
da revisão de hoje. Pra expor publicamente na internet, ainda falta:

- **Autenticação** — hoje qualquer um que alcance a API pode cadastrar perfil, rodar o
  pipeline, ler vagas. Não tem chave de API nem login.
- **Rate limiting** — nada impede abuso de `POST /pipeline/run` batendo repetido.
- **Observabilidade** — só tem log local (`logging`); sem métricas nem alerta de erro.

Nada disso impede rodar isso pra você mesmo hoje — só importa se algum dia isso for
além de "eu uso sozinho".
