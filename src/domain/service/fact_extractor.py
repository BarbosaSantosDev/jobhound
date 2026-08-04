from abc import ABC, abstractmethod

from src.domain.entity.job import Job
from src.domain.entity.job_facts import JobFacts


class FactExtractor(ABC):
    """Extrai fatos objetivos de uma vaga. Implementado por LLM (Ollama/Anthropic)."""

    @abstractmethod
    async def extract(self, job: Job) -> JobFacts:
        pass
