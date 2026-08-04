import hashlib
import logging
from abc import abstractmethod
from typing import Any

import httpx

from src.domain.entity.job import Job
from src.domain.service.job_source import JobSource

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


class HttpJobSource(JobSource):
    """Template Method: fixa o esqueleto fetch = coletar itens crus -> converter,
    com client httpx e tratamento de erro compartilhados.

    Subclasses implementam:
      - _collect(client): busca e retorna itens crus (dicts)
      - _to_job(raw): converte um item cru em Job (retorna None para descartar)

    E podem sobrescrever os hooks:
      - _headers(), _timeout(), _http2()
    """

    # ---------- template method ----------

    async def fetch(self) -> list[Job]:
        async with httpx.AsyncClient(
            timeout=self._timeout(),
            headers=self._headers(),
            http2=self._http2(),
            follow_redirects=True,
        ) as client:
            raw_items = await self._collect(client)

        jobs: list[Job] = []
        for raw in raw_items:
            try:
                job = self._to_job(raw)
            except (KeyError, TypeError, ValueError):
                logger.warning("Item malformado em %s, pulando", self.name)
                continue
            if job is not None:
                jobs.append(job)
        return jobs

    # ---------- passos obrigatórios ----------

    @abstractmethod
    async def _collect(self, client: httpx.AsyncClient) -> list[Any]: ...

    @abstractmethod
    def _to_job(self, raw: Any) -> Job | None: ...

    # ---------- hooks com default ----------

    def _headers(self) -> dict[str, str]:
        return DEFAULT_HEADERS

    def _timeout(self) -> httpx.Timeout:
        return httpx.Timeout(30, connect=10)

    def _http2(self) -> bool:
        return False

    # ---------- utilitário comum ----------

    def _make_id(self, external_id: str) -> str:
        return hashlib.sha256(f"{self.name}|{external_id}".encode()).hexdigest()[:32]