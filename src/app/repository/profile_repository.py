from abc import ABC, abstractmethod

from src.domain.entity.profile import Profile


class ProfileRepository(ABC):
    @abstractmethod
    async def save(self, profile: Profile) -> Profile:
        pass

    @abstractmethod
    async def load(self, slug: str | None = None) -> Profile | None:
        pass

    @abstractmethod
    async def check_if_exists(self, slug: str) -> bool:
        pass
