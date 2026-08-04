from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.app.repository import ProfileRepository
from src.domain.entity.profile import Profile, SearchPreferences
from src.infra.model.profile_model import ProfileModel


class ProfileRepositorySQLAlchemy(ProfileRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def save(self, profile: Profile) -> Profile:
        async with self._session_factory() as session:
            model = await session.get(ProfileModel, profile.id) if profile.id else None
            if model is None:
                model = ProfileModel(slug=profile.slug)
                session.add(model)

            model.name = profile.name
            model.headline = profile.headline
            model.seniority = profile.seniority
            model.primary_stack = profile.primary_stack
            model.secondary_stack = profile.secondary_stack
            model.preferred_locations = profile.preferred_locations
            model.accepts_remote = profile.accepts_remote
            model.summary = profile.summary
            model.search = profile.search.model_dump()

            await session.commit()
            await session.refresh(model)
            return _to_entity(model)

    async def load(self, slug: str | None = None) -> Profile | None:
        async with self._session_factory() as session:
            stmt = select(ProfileModel)
            if slug is not None:
                stmt = stmt.where(ProfileModel.slug == slug)
            else:
                stmt = stmt.order_by(ProfileModel.updated_at.desc())
            model = (await session.execute(stmt.limit(1))).scalar_one_or_none()
            return _to_entity(model) if model is not None else None

    async def check_if_exists(self, slug: str) -> bool:
        async with self._session_factory() as session:
            stmt = select(ProfileModel.id).where(ProfileModel.slug == slug)
            return (await session.execute(stmt)).first() is not None


def _to_entity(model: ProfileModel) -> Profile:
    return Profile(
        id=model.id,
        slug=model.slug,
        name=model.name,
        headline=model.headline,
        seniority=model.seniority,
        primary_stack=list(model.primary_stack),
        secondary_stack=list(model.secondary_stack),
        preferred_locations=list(model.preferred_locations),
        accepts_remote=model.accepts_remote,
        summary=model.summary,
        search=SearchPreferences(**(model.search or {})),
    )
