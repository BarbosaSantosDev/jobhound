import logging

from src.app.repository import JobRepository
from src.domain.entity import Job
from src.domain.service import JobSource

logger = logging.getLogger(__name__)


class FetchNewJobs:
    """Coleta nas fontes e devolve as vagas que este perfil ainda não avaliou.

    Uma vaga já gravada (por outro perfil) não é gravada de novo, mas volta
    para avaliação se ainda não foi pontuada contra `profile_id`."""

    def __init__(self, sources: list[JobSource], job_repo: JobRepository, profile_id: int | None = None):
        self._sources = sources
        self._job_repo = job_repo
        self._profile_id = profile_id

    async def execute(self) -> list[Job]:
        to_evaluate: list[Job] = []
        seen_fingerprints: set[str] = set()
        for source in self._sources:
            try:
                jobs = await source.fetch()
            except Exception:
                logger.exception("Falha ao buscar vagas na fonte %s", source.name)
                continue
            for job in jobs:
                fp = job.fingerprint
                if fp in seen_fingerprints:
                    continue
                seen_fingerprints.add(fp)
                stored = await self._job_repo.find_by_fingerprint(fp)
                if stored is None:
                    await self._job_repo.save(job)
                    to_evaluate.append(job)
                elif not await self._job_repo.is_evaluated(stored.id, self._profile_id):
                    to_evaluate.append(stored)
        return to_evaluate
