from dataclasses import dataclass, field

from src.app.repository import ProfileRepository
from src.domain.entity.profile import Profile
from src.error import ProfileAlreadyExistsError


@dataclass
class RegisterProfileInput:
    name: str
    headline: str
    seniority: str
    primary_stack: list[str]
    secondary_stack: list[str] = field(default_factory=list)
    preferred_locations: list[str] = field(default_factory=list)
    accepts_remote: bool = True
    summary: str = ""


class RegisterProfile:
    def __init__(self, profile_repository: ProfileRepository):
        self._profile_repository = profile_repository

    async def execute(self, input: RegisterProfileInput) -> Profile:
        profile = Profile.create(
            name=input.name,
            headline=input.headline,
            seniority=input.seniority,
            primary_stack=input.primary_stack,
            secondary_stack=input.secondary_stack,
            preferred_locations=input.preferred_locations,
            accepts_remote=input.accepts_remote,
            summary=input.summary,
        )

        if await self._profile_repository.check_if_exists(profile.slug):
            raise ProfileAlreadyExistsError(profile.slug)

        return await self._profile_repository.save(profile)
