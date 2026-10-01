"""Fakes em memória compartilhados pelos steps — mesmo espírito do FakeExtractor:
exercitam use cases e rotas sem Postgres, LLM ou rede."""

import asyncio

import httpx

from src.app.repository import ProfileRepository
from src.domain.entity.profile import Profile


class InMemoryProfileRepository(ProfileRepository):
    def __init__(self) -> None:
        self._by_slug: dict[str, Profile] = {}
        self._next_id = 1

    async def save(self, profile: Profile) -> Profile:
        if profile.id is None:
            profile = profile.model_copy(update={"id": self._next_id})
            self._next_id += 1
        # reinserir move o perfil para o fim: o último salvo é o mais recente
        self._by_slug.pop(profile.slug, None)
        self._by_slug[profile.slug] = profile
        return profile

    async def load(self, slug: str | None = None) -> Profile | None:
        if slug is None:
            return next(reversed(self._by_slug.values()), None)
        return self._by_slug.get(slug)

    async def check_if_exists(self, slug: str) -> bool:
        return slug in self._by_slug

    async def list_all(self) -> list[Profile]:
        return list(reversed(self._by_slug.values()))


async def _call(app, method: str, path: str, json=None):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method, path, json=json)


def call_api(app, method: str, path: str, json=None):
    """Uma chamada HTTP síncrona contra o app FastAPI em memória (ASGI)."""
    return asyncio.run(_call(app, method, path, json))
