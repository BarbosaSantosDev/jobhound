# agent-job

Agente LLM que busca vagas, extrai fatos objetivos com um modelo local (Ollama) e
pontua o match contra seu perfil com lógica determinística no domínio.

Arquitetura: Clean Architecture + DDD. O LLM **extrai fatos**; o **domínio pontua**
(`src/domain/service/scoring.py`, função pura e testável).

## Estrutura

```
src/
├── domain/          # Entidades, VOs, interfaces (JobSource, FactExtractor, Notifier) e scoring
├── app/             # Use cases (fetch, evaluate), workflow (pipeline) e queries (CQRS)
├── infra/           # Postgres (database/), Gupy/RemoteOK (gateway/), Ollama/Anthropic (llm/),
│                     Telegram (gateway/), routers FastAPI (routers/)
├── server.py        # FastAPI app (entrypoint HTTP)
├── cli.py           # CLI (Typer)
└── scheduler.py     # Scheduler (APScheduler)
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env        # edite conforme necessário
docker compose up -d db     # Postgres local (ou aponte DATABASE_URL pro seu)
cd src/infra/database && alembic revision --autogenerate -m "initial" && alembic upgrade head
```

### Ollama

```bash
ollama pull qwen2.5:3b
```

`qwen2.5:3b` é o padrão porque cabe inteiro em ~4GB de VRAM (roda 100% na GPU,
rápido). Com mais VRAM disponível, `qwen2.5:7b` extrai um pouco melhor — troque
`OLLAMA_MODEL` no `.env`.

### Telegram

1. Crie um bot com o @BotFather e copie o token.
2. Mande uma mensagem para o bot e pegue seu chat_id em
   `https://api.telegram.org/bot<TOKEN>/getUpdates`.

## Docker

Sobe tudo (Postgres + Ollama + API) com um único comando — não precisa instalar
nada além de Docker. O modelo (`OLLAMA_MODEL` no `.env`, `qwen2.5:3b` por padrão)
é baixado automaticamente na primeira vez pelo serviço `ollama-init`, antes do
`app` subir:

```bash
cp .env.example .env        # edite TELEGRAM_*/ANTHROPIC_API_KEY se for usar
docker compose up -d --build
```

### GPU NVIDIA (opcional)

Por padrão o Ollama roda em CPU — funciona em qualquer máquina, sem pré-requisito
além do Docker. Se você tem GPU NVIDIA e já tem o
[nvidia-container-toolkit](https://github.com/NVIDIA/nvidia-container-toolkit)
instalado e o runtime registrado (`nvidia-ctk runtime configure --runtime=docker`
+ restart do Docker), suba com o overlay de GPU pra acelerar bastante a extração
de fatos:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

Sem isso, tudo continua funcionando normalmente — só mais lento na etapa de LLM.

- API em `http://localhost:8000` (Postgres em `localhost:5434` por padrão — veja
  `DB_HOST_PORT` no `.env.example`; Ollama só na rede interna do compose, não
  publica `11434` no host de propósito, pra não conflitar com um Ollama nativo
  já instalado)
- Migrations rodam automaticamente no start do container `app`
- Perfil é 100% via API (`POST`/`PUT /api/v1/profiles`) — persiste no Postgres,
  que tem seu próprio volume (`pgdata`), então sobrevive a `docker compose down`
  (sem o `-v`)
- `agent-job run`/`agent-job top` funcionam dentro do container:
  `docker compose exec app agent-job run`
- O scheduler (roda o pipeline a cada 3h) não faz parte do compose — rode-o à
  parte: `docker compose exec app python -m src.scheduler`
- Trocando `MATCHER_PROVIDER=anthropic` no `.env`, o serviço `ollama` deixa de ser
  necessário (mas continua subindo por padrão; pare com `docker compose stop ollama`
  se não for usar)

## Uso

```bash
agent-job run    # roda o pipeline uma vez
agent-job top    # lista os melhores matches
python -m src.scheduler   # roda a cada 3h
```

## Testes (BDD)

```bash
behave
```

Os cenários usam `FakeExtractor` determinístico — o LLM real não entra nos testes.

## Trocar Ollama por Claude

```bash
pip install -e ".[anthropic]"
# no .env:
MATCHER_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-...
```

Nada no domínio ou nos use cases muda — só a implementação de `FactExtractor` injetada
no composition root (`src/container.py`).

## Perfil

Não tem arquivo de config pra editar — o perfil é gerenciado 100% via API, e é a
fonte de verdade usada no prompt de extração e no scoring:

```bash
curl -X POST http://localhost:8000/api/v1/profiles -H "Content-Type: application/json" -d '{
  "name": "Seu Nome",
  "headline": "Dev Backend Pleno | Python",
  "seniority": "pleno",
  "primary_stack": ["Python", "FastAPI"],
  "secondary_stack": ["Docker", "PostgreSQL"],
  "preferred_locations": ["São Paulo"],
  "accepts_remote": true,
  "summary": "Um resumo curto de quem você é."
}'
```

Os termos de busca em cada fonte (Gupy/Nerdin/RemoteOK) são derivados automaticamente
da sua stack — não é algo que você configura à mão. Ver `ARQUITETURA.md` para o fluxo
completo.


<img width="1856" height="728" alt="image" src="https://github.com/user-attachments/assets/fe6a84a0-03c6-4c25-995d-6d2494aef373" />

