from abc import ABC, abstractmethod

from src.domain.entity.job import Job
from src.domain.entity.match_result import MatchResult


class JobRepository(ABC):
    @abstractmethod
    async def exists(self, fingerprint: str) -> bool:
        pass

    @abstractmethod
    async def save(self, job: Job) -> None:
        pass

    @abstractmethod
    async def save_match(self, result: MatchResult) -> None: 
        pass

    @abstractmethod
    async def top_matches(self, limit: int = 10) -> list[tuple[Job, MatchResult]]:
        pass
