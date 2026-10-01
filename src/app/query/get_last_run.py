from src.app.dto.pipeline_report import PipelineRun
from src.app.repository import PipelineRunRepository, ProfileRepository
from src.error import ProfileNotFoundError


class GetLastRun:
    """Último faro registrado — do perfil, se informado; senão, de qualquer um."""

    def __init__(self, run_repo: PipelineRunRepository, profile_repo: ProfileRepository):
        self._run_repo = run_repo
        self._profile_repo = profile_repo

    async def execute(self, profile_slug: str | None = None) -> PipelineRun | None:
        profile_id = None
        if profile_slug is not None:
            profile = await self._profile_repo.load(profile_slug)
            if profile is None:
                raise ProfileNotFoundError(profile_slug)
            profile_id = profile.id
        return await self._run_repo.last(profile_id)
