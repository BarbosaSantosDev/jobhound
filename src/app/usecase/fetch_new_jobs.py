import logging

from src.app.repository import JobRepository
from src.domain.entity import Job
from src.domain.service import JobSource

logger = logging.getLogger(__name__)


class FetchNewJobs:
    def __init__(self, sources: list[JobSource], job_repo: JobRepository):
        self._sources = sources
        self._job_repo = job_repo

    async def execute(self) -> list[Job]:
        new_jobs: list[Job] = []
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
                if await self._job_repo.exists(fp):
                    continue
                seen_fingerprints.add(fp)
                await self._job_repo.save(job)
                new_jobs.append(job)
        return new_jobs
