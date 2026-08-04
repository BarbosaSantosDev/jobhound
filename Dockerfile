FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir ".[anthropic]"

EXPOSE 8000

CMD ["sh", "-c", "cd src/infra/database && alembic upgrade head && cd /app && uvicorn src.server:app --host 0.0.0.0 --port 8000"]
