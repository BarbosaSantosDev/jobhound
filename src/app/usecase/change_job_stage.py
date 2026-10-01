from src.app.repository import JobRepository
from src.domain.value_object import JobStage
from src.error import JobNotFoundError


class ChangeJobStage:
    """Triagem do candidato: salvar, marcar candidatura ou descartar uma vaga."""

    def __init__(self, job_repo: JobRepository):
        self._job_repo = job_repo

    async def execute(self, job_id: str, stage: JobStage) -> JobStage:
        if not await self._job_repo.set_stage(job_id, stage):
            raise JobNotFoundError(job_id)
        return stage
