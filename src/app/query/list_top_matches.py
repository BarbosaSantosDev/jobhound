from src.app.repository import JobRepository, ProfileRepository
from src.domain.entity import Job, MatchResult
from src.error import ProfileNotFoundError


class ListTopMatches:
    def __init__(self, job_repository: JobRepository, profile_repository: ProfileRepository):
        self.job_repository = job_repository
        self.profile_repository = profile_repository

    async def execute(
        self, limit: int = 10, profile_slug: str | None = None
    ) -> list[tuple[Job, MatchResult]]:
        """Sem slug: todas as avaliações (comportamento anterior aos perfis)."""
        profile_id = await _resolve_profile_id(self.profile_repository, profile_slug)
        return await self.job_repository.top_matches(limit, profile_id)


async def _resolve_profile_id(repo: ProfileRepository, slug: str | None) -> int | None:
    if slug is None:
        return None
    profile = await repo.load(slug)
    if profile is None:
        raise ProfileNotFoundError(slug)
    return profile.id
