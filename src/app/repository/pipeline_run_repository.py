from abc import ABC, abstractmethod

from src.app.dto.pipeline_report import PipelineRun


class PipelineRunRepository(ABC):
    @abstractmethod
    async def save(self, run: PipelineRun) -> PipelineRun:
        pass

    @abstractmethod
    async def last(self, profile_id: int | None = None) -> PipelineRun | None:
        """Execução mais recente (do perfil, se informado)."""
