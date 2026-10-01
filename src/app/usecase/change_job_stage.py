from src.app.repository import JobRepository, ProfileRepository
from src.domain.value_object import JobStage
from src.error import JobNotFoundError, ProfileNotFoundError


class ChangeJobStage:
    """Triagem do candidato: salvar, marcar candidatura ou descartar uma vaga."""

    def __init__(self, job_repo: JobRepository, profile_repo: ProfileRepository):
        self._job_repo = job_repo
        self._profile_repo = profile_repo

    async def execute(self, job_id: str, stage: JobStage, profile_slug: str | None = None) -> JobStage:
        profile_id = None
        if profile_slug is not None:
            profile = await self._profile_repo.load(profile_slug)
            if profile is None:
                raise ProfileNotFoundError(profile_slug)
            profile_id = profile.id
        if not await self._job_repo.set_stage(job_id, stage, profile_id):
            raise JobNotFoundError(job_id)
        return stage
