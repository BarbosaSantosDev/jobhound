from src.app.repository import ProfileRepository
from src.domain.entity.profile import Profile


class ListProfiles:
    def __init__(self, profile_repo: ProfileRepository):
        self._profile_repo = profile_repo

    async def execute(self) -> list[Profile]:
        return await self._profile_repo.list_all()
