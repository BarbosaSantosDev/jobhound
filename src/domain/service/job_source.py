from abc import ABC, abstractmethod

from src.domain.entity.job import Job


class JobSource(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def fetch(self) -> list[Job]: 
        pass
