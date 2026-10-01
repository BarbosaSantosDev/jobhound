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
   localizações preferidas, aceita remoto, resumo, fontes ligadas). Os termos de busca
   de cada fonte (Gupy, Nerdin, RemoteOK) são **derivados automaticamente** da sua
   stack. Você escolhe só quais fontes ficam ligadas; entra no faro a fonte ligada que
   tem termo de busca (`Profile.active_sources()`). Dá pra ter vários perfis.
2. **Buscar vagas** (`FetchNewJobs`) — cada fonte é consultada com os termos derivados.
   Vagas repetidas (mesmo título+empresa+local, via hash) são gravadas uma vez só. Uma
   vaga já gravada volta para avaliação se o perfil do faro ainda não a avaliou — cada
   perfil tem as próprias avaliações e etapas (`matches.profile_id`).
3. **Extrair fatos** (`EvaluateJobMatch` → LLM via Ollama) — para cada vaga nova, o LLM
   lê a descrição e extrai só fatos objetivos: stack mencionada, senioridade, modo de
   trabalho, cidade, faixa salarial.
4. **Pontuar** (`ScoreJob`, domínio puro, sem LLM) — compara os fatos extraídos com o
   seu perfil e calcula um score 0-100 com motivos explicados: stack bate (peso 50),
   senioridade bate (peso 30), localização/remoto bate (peso 20). Cada motivo diz para
   que lado pesou (`pro`, `con` ou `info`).
5. **Salvar + notificar** — o resultado vai pro Postgres; se a vaga for boa
   (`is_worth_applying`) ou merecer revisão manual (`needs_manual_review`), dispara um
   Telegram (se configurado). Esse passo, mais `jobhound top` na CLI, já é suficiente
   pra usar o projeto só com este repositório. Cada execução fica registrada em
   `pipeline_runs`, com o resultado de cada fonte (inclusive as que falharam).
6. **Frontend** (opcional, repositório separado) — o dashboard busca `/api/v1/matches`,
   `/api/v1/stats` e `/api/v1/pipeline/status` a cada poucos segundos (polling) e mostra
   a lista sem precisar recarregar a página. Lá você também faz a triagem de cada vaga
   (salvar, candidatei, descartar).

```
perfil (você)
  -> deriva termos de busca (stack)
  -> Gupy / Nerdin / RemoteOK --fetch--> vagas novas (dedup por fingerprint)
  -> LLM (Ollama) extrai fatos --> domínio pontua (0-100 + motivos)
  -> Postgres salva --> Telegram notifica (se match)
  -> jobhound top (CLI) ou frontend (opcional) mostram o resultado
```

## Como disparar o pipeline

- `POST /api/v1/pipeline/run?profile=<slug>` — usado pelo botão "Farejar agora" do
  frontend. Roda em background, uma vez; devolve 409 se já tiver um rodando. Sem
  `profile`, usa o perfil editado por último.
- `jobhound run --profile <slug>` — mesma coisa, via CLI.
- `python -m src.scheduler` — roda o pipeline a cada 3h. Não faz parte do
  `docker-compose` hoje; suba manualmente se quiser recorrência automática.

## Rotas da API

Todas sob `/api/v1`. Onde aparece `?profile=<slug>`, o parâmetro é opcional: sem ele,
vale tudo (ou o perfil editado por último, no caso do pipeline).

| Rota | O que faz |
|---|---|
| `GET /profiles` | lista os perfis (atualizado mais recentemente primeiro) |
| `POST /profiles` · `GET`/`PUT /profiles/{slug}` | registra, lê e atualiza um perfil (inclui `enabled_sources`; devolve também `active_sources`) |
| `GET /matches?profile=` | vagas avaliadas, com score, motivos `{kind, text}`, `stage`, `work_mode` e `summary` |
| `PATCH /matches/{job_id}/stage?profile=` | move a vaga para `new`, `saved`, `applied` ou `discarded` |
| `GET /stats?profile=` | contagens + `errors` do último faro |
| `POST /pipeline/run?profile=` | dispara um faro em background |
| `GET /pipeline/status?profile=` | estado ao vivo + `last_run` (último faro registrado, com status por fonte) |

Avaliações feitas antes de existir `profile_id` (legadas) aparecem para todos os perfis:
não dá para saber com qual perfil cada uma foi feita.

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
