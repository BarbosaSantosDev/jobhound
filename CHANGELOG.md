# Changelog

## [0.1.0] - 2026-08-04

### Fixed

- `MatchScore` era instanciado com argumento posicional, incompatível com o
  modelo Pydantic; causava erro 500 em `GET /matches` e `GET /stats`. Passou a
  usar keyword argument, e a validação de faixa (0–100) foi movida para um
  `field_validator` (o hook anterior, `__post_init__`, nunca era executado
  pelo Pydantic).
- Import incorreto de fuso horário (`timezone.UTC` em vez de `timezone.utc`)
  quebrava a avaliação de qualquer vaga nova.
- `alembic/env.py` combinava engine síncrono com driver assíncrono
  (`asyncpg`), causando falha em toda migration. Migrado para
  `create_async_engine` + `run_sync`.
- Dependências ausentes em `pyproject.toml` (`beautifulsoup4`,
  `langchain-core`, `langchain-ollama`) impediam build limpo da imagem
  Docker.
- `docker-compose.yml` dependia de uma rede Docker externa e de um serviço
  Postgres de outro projeto, impedindo a execução em qualquer máquina além da
  original. Restaurado um serviço `db` (Postgres) self-contained no próprio
  compose.

### Changed

- CORS (backend) e a URL da API (frontend) passaram a ser configuráveis por
  variável de ambiente (`CORS_ORIGINS`, `REACT_APP_API_URL`) em vez de fixas
  em `localhost`.
- Removido `profile/profile.yaml` e a plumbing associada (cópia no
  Dockerfile, volume no compose) — o perfil é gerenciado inteiramente via
  API/Postgres, e o arquivo não era mais lido por nenhum código.
