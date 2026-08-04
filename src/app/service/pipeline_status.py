import asyncio
from datetime import UTC, datetime

from pydantic import BaseModel


class PipelineStatus(BaseModel):
    """Snapshot somente-leitura do estado do pipeline — o que a API expõe."""

    running: bool
    stage: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    last_error: str | None = None


class PipelineStatusTracker:
    """Fonte única de verdade sobre "existe um pipeline rodando agora".

    Usada tanto pelo 409 de POST /pipeline/run quanto pelo GET
    /pipeline/status — os dois lêem/escrevem o mesmo estado, nunca duas
    flags paralelas. Singleton em memória (ver container.py); vale só para
    este processo — CLI e scheduler rodam em processos separados e não
    enxergam esse estado, mesma limitação que o lock antigo já tinha.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._running = False
        self._stage: str | None = None
        self._started_at: datetime | None = None
        self._finished_at: datetime | None = None
        self._last_error: str | None = None

    async def try_start(self) -> bool:
        """Marca como "rodando" se estava livre. Retorna False se já havia
        uma execução em andamento — é o sinal que vira 409 no router."""
        async with self._lock:
            if self._running:
                return False
            self._running = True
            self._stage = None
            self._started_at = datetime.now(UTC)
            self._finished_at = None
            self._last_error = None
            return True

    async def set_stage(self, stage: str) -> None:
        async with self._lock:
            if self._running:
                self._stage = stage

    async def finish(self, error: str | None) -> None:
        async with self._lock:
            self._running = False
            self._stage = None
            self._finished_at = datetime.now(UTC)
            self._last_error = error

    async def snapshot(self) -> PipelineStatus:
        async with self._lock:
            return PipelineStatus(
                running=self._running,
                stage=self._stage,
                started_at=self._started_at,
                finished_at=self._finished_at,
                last_error=self._last_error,
            )
