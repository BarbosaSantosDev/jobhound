"""Fakes em memória compartilhados pelos steps — mesmo espírito do FakeExtractor:
exercitam use cases e rotas sem Postgres, LLM ou rede."""

import asyncio

import httpx

from src.app.repository import JobRepository, ProfileRepository
from src.domain.entity import Job, MatchResult
from src.domain.entity.profile import Profile
from src.domain.value_object import JobStage, MatchScore


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


class InMemoryJobRepository(JobRepository):
    def __init__(self) -> None:
        self.jobs: dict[str, Job] = {}
        self.matches: list[MatchResult] = []

    async def exists(self, fingerprint: str) -> bool:
        return any(j.fingerprint == fingerprint for j in self.jobs.values())

    async def save(self, job: Job) -> None:
        self.jobs[job.id] = job

    async def save_match(self, result: MatchResult) -> None:
        self.matches.append(result)

    async def top_matches(self, limit: int = 10) -> list[tuple[Job, MatchResult]]:
        ranked = sorted(self.matches, key=lambda m: m.score.value, reverse=True)[:limit]
        return [(self.jobs[m.job_id], m) for m in ranked]

    async def set_stage(self, job_id: str, stage: JobStage) -> bool:
        found = False
        for i, m in enumerate(self.matches):
            if m.job_id == job_id:
                self.matches[i] = m.model_copy(update={"stage": stage})
                found = True
        return found


def make_job(job_id: str, title: str = "Vaga de teste", **extra) -> Job:
    return Job(
        id=job_id,
        title=title,
        company=extra.pop("company", "Empresa X"),
        location=extra.pop("location", "Remoto"),
        description=extra.pop("description", "..."),
        url=extra.pop("url", f"https://example.com/{job_id}"),
        source=extra.pop("source", "fake"),
        **extra,
    )


def make_match(job_id: str, score: int = 80, **extra) -> MatchResult:
    return MatchResult(job_id=job_id, score=MatchScore(value=score), reasons=[], **extra)


async def _call(app, method: str, path: str, json=None):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method, path, json=json)


def call_api(app, method: str, path: str, json=None):
    """Uma chamada HTTP síncrona contra o app FastAPI em memória (ASGI)."""
    return asyncio.run(_call(app, method, path, json))
