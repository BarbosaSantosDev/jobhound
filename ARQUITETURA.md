# Como o jobhound funciona

Assistente pessoal de busca de vagas: procura vagas em fontes públicas, usa um LLM
para extrair **fatos objetivos** de cada vaga, e um código determinístico (sem LLM)
pontua o quão bem ela combina com o seu perfil. O LLM não decide "gosto" nem inventa
número — só lê e extrai o que está escrito na vaga.

## As peças

- **backend** (`jobhound`) — API FastAPI + pipeline. Python, Clean Architecture + DDD.
- **frontend** (`jobhound-frontend/jobhound`) — dashboard React, consome a API.
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
   Telegram (se configurado).
6. **Frontend** — o dashboard busca `/api/v1/matches` e `/api/v1/stats` a cada poucos
   segundos (polling) e mostra a lista sem precisar recarregar a página.

```
perfil (você)
  -> deriva termos de busca (stack)
  -> Gupy / Nerdin / RemoteOK --fetch--> vagas novas (dedup por fingerprint)
  -> LLM (Ollama) extrai fatos --> domínio pontua (0-100 + motivos)
  -> Postgres salva --> Telegram notifica (se match)
  -> frontend faz polling e mostra
```

## Como disparar o pipeline

- `POST /api/v1/pipeline/run` — usado pelo botão "rodar pipeline" do frontend. Roda em
  background, uma vez; devolve 409 se já tiver um rodando.
- `agent-job run` — mesma coisa, via CLI.
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

## Correções desta revisão

- `MatchScore` (Pydantic) era instanciado com argumento posicional em dois lugares —
  quebrava `GET /matches` e `GET /stats` com 500 sempre. Corrigido para keyword arg; a
  validação de faixa (0-100), que nunca rodava (usava `__post_init__`, hook de
  dataclass, não de Pydantic), agora funciona via `@field_validator`.
- `timezone.UTC` (typo — o certo é `timezone.utc`) quebraria toda avaliação de vaga
  nova. Corrigido.
- `alembic/env.py` misturava engine síncrono com driver assíncrono (`asyncpg`) — toda
  migration quebrava com `MissingGreenlet`. Corrigido para `create_async_engine` +
  `run_sync`.
- Dependências faltando no `pyproject.toml` (`beautifulsoup4`, `langchain-core`,
  `langchain-ollama`) — funcionavam no venv local só por instalação manual, mas
  quebravam a imagem Docker construída do zero.
- CORS (backend) e a URL da API (frontend) agora são configuráveis por variável de
  ambiente (`CORS_ORIGINS`, `REACT_APP_API_URL`) em vez de fixas em `localhost`.

Testes BDD (`behave`) passam (3 cenários, 0 falhas), e os dois builds — backend em
Docker e frontend (`npm run build`) — estão limpos.

## Preparação para repositório público

Ao decidir abrir o repositório, achamos (e corrigimos) dois problemas que só importam
nesse cenário — "clonar e rodar na máquina de outra pessoa":

- `docker-compose.yml` dependia de uma rede Docker externa e de um Postgres de outro
  projeto local (conveniente pro dev original, mas inexistente em qualquer outra
  máquina). Restaurado um serviço `db` (Postgres) self-contained no próprio compose —
  `docker compose up` agora funciona sozinho, sem pré-requisito nenhum além do Docker.
- `profile/profile.yaml` guardava dados pessoais reais (nome, resumo de carreira) e não
  era mais lido por nenhum código (o perfil vive 100% no Postgres, via API) — era
  documentação/plumbing morta que só existia como conteúdo publicável sem função.
  Removido o arquivo, a pasta, a linha `COPY profile ./profile` do Dockerfile e o volume
  correspondente no compose.
