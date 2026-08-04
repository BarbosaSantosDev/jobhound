from abc import ABC, abstractmethod

from src.domain.entity.job import Job
from src.domain.entity.match_result import MatchResult


class Notifier(ABC):
    @abstractmethod
    async def send_matches(self, matches: list[tuple[Job, MatchResult]]) -> None: ...
