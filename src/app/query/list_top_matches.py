from src.app.repository import JobRepository
from src.domain.entity import Job, MatchResult


class ListTopMatches:
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    async def execute(self, limit: int = 10) -> list[tuple[Job, MatchResult]]:
        return await self.job_repository.top_matches(limit)
