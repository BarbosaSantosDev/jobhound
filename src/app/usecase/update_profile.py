from dataclasses import dataclass, field

from src.app.repository import ProfileRepository
from src.domain.entity.profile import Profile, SearchPreferences
from src.error import ProfileNotFoundError


@dataclass
class UpdateProfileInput:
    slug: str
    name: str
    headline: str
    seniority: str
    primary_stack: list[str]
    secondary_stack: list[str] = field(default_factory=list)
    preferred_locations: list[str] = field(default_factory=list)
    accepts_remote: bool = True
    summary: str = ""


class UpdateProfile:
    def __init__(self, profile_repo: ProfileRepository):
        self._profile_repo = profile_repo

    async def execute(self, input: UpdateProfileInput) -> Profile:
        existing = await self._profile_repo.load(input.slug)
        if existing is None:
            raise ProfileNotFoundError(input.slug)

        profile = Profile(
            id=existing.id,
            slug=existing.slug,
            name=input.name,
            headline=input.headline,
            seniority=input.seniority,
            primary_stack=input.primary_stack,
            secondary_stack=input.secondary_stack,
            preferred_locations=input.preferred_locations,
            accepts_remote=input.accepts_remote,
            summary=input.summary,
            search=SearchPreferences.derive(input.primary_stack, input.secondary_stack),
        )
        return await self._profile_repo.save(profile)
