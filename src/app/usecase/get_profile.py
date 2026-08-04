from src.app.repository import ProfileRepository
from src.domain.entity.profile import Profile
from src.error import ProfileNotFoundError


class GetProfile:
    def __init__(self, profile_repo: ProfileRepository):
        self._profile_repo = profile_repo

    async def execute(self, slug: str) -> Profile:
        profile = await self._profile_repo.load(slug)
        if profile is None:
            raise ProfileNotFoundError(slug)
        return profile
