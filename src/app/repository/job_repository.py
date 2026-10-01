from abc import ABC, abstractmethod

from src.domain.entity.job import Job
from src.domain.entity.match_result import MatchResult
from src.domain.value_object import JobStage

# Escopo por perfil: `profile_id=None` significa "sem filtro" (comportamento de
# antes dos perfis). Avaliações legadas (feitas antes de existir profile_id)
# valem para qualquer perfil — não dá para saber com qual delas foram feitas.


class JobRepository(ABC):
    @abstractmethod
    async def find_by_fingerprint(self, fingerprint: str) -> Job | None:
        pass

    @abstractmethod
    async def save(self, job: Job) -> None:
        pass

    @abstractmethod
    async def is_evaluated(self, job_id: str, profile_id: int | None) -> bool:
        """Já existe avaliação desta vaga para o perfil (ou legada)?"""

    @abstractmethod
    async def save_match(self, result: MatchResult) -> None:
        pass

    @abstractmethod
    async def top_matches(
        self, limit: int = 10, profile_id: int | None = None
    ) -> list[tuple[Job, MatchResult]]:
        pass

    @abstractmethod
    async def set_stage(self, job_id: str, stage: JobStage, profile_id: int | None = None) -> bool:
        """Move a vaga avaliada para outra etapa. False se não há avaliação dela."""
