from typing import Any

import httpx

from src.domain.entity.job import Job
from src.infra.gateway.base import HttpJobSource

REMOTEOK_API = "https://remoteok.com/api"


class RemoteOKSource(HttpJobSource):
    def __init__(self, tags: list[str]):
        self._tags = [t.lower() for t in tags]

    @property
    def name(self) -> str:
        return "remoteok"

    def _http2(self) -> bool:
        return True  # CDN deles filtra clientes HTTP/1.1

    async def _collect(self, client: httpx.AsyncClient) -> list[dict]:
        response = await client.get(REMOTEOK_API)
        response.raise_for_status()
        return response.json()

    def _to_job(self, raw: Any) -> Job | None:
        if not isinstance(raw, dict) or "position" not in raw:
            return None  # metadado/legal
        item_tags = [t.lower() for t in raw.get("tags", [])]
        if not any(tag in item_tags for tag in self._tags):
            return None
        return Job(
            id=self._make_id(str(raw.get("id"))),
            title=raw.get("position", ""),
            company=raw.get("company", ""),
            location=raw.get("location", "") or "Remote",
            description=raw.get("description", ""),
            url=raw.get("url", ""),
            source=self.name,
        )