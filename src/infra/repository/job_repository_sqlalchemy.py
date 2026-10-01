from sqlalchemy import or_, select, true, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.app.repository import JobRepository
from src.domain.entity import Job, MatchResult
from src.domain.value_object import JobStage, MatchScore, Reason, WorkMode
from src.infra.model import JobModel, MatchModel


def _for_profile(profile_id: int | None):
    """Avaliações do perfil + as legadas (sem perfil). None = sem filtro."""
    if profile_id is None:
        return true()
    return or_(MatchModel.profile_id == profile_id, MatchModel.profile_id.is_(None))


def _to_job(jm: JobModel) -> Job:
    return Job(
        id=jm.id,
        title=jm.title,
        company=jm.company,
        location=jm.location,
        description=jm.description,
        url=jm.url,
        source=jm.source,
        fetched_at=jm.fetched_at,
    )


class JobRepositorySQLAlchemy(JobRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def find_by_fingerprint(self, fingerprint: str) -> Job | None:
        async with self._session_factory() as session:
            stmt = select(JobModel).where(JobModel.fingerprint == fingerprint)
            model = (await session.execute(stmt)).scalar_one_or_none()
            return _to_job(model) if model is not None else None

    async def save(self, job: Job) -> None:
        async with self._session_factory() as session:
            session.add(
                JobModel(
                    id=job.id,
                    fingerprint=job.fingerprint,
                    title=job.title,
                    company=job.company,
                    location=job.location,
                    description=job.description,
                    url=job.url,
                    source=job.source,
                    fetched_at=job.fetched_at,
                )
            )
            await session.commit()

    async def is_evaluated(self, job_id: str, profile_id: int | None) -> bool:
        async with self._session_factory() as session:
            stmt = select(MatchModel.id).where(
                MatchModel.job_id == job_id, _for_profile(profile_id)
            )
            return (await session.execute(stmt.limit(1))).first() is not None

    async def save_match(self, result: MatchResult) -> None:
        async with self._session_factory() as session:
            session.add(
                MatchModel(
                    job_id=result.job_id,
                    profile_id=result.profile_id,
                    score=result.score.value,
                    reasons=[r.model_dump(mode="json") for r in result.reasons],
                    red_flags=result.red_flags,
                    evaluated_at=result.evaluated_at,
                    stage=result.stage.value,
                    work_mode=result.work_mode.value if result.work_mode else None,
                )
            )
            await session.commit()

    async def set_stage(self, job_id: str, stage: JobStage, profile_id: int | None = None) -> bool:
        async with self._session_factory() as session:
            stmt = (
                update(MatchModel)
                .where(MatchModel.job_id == job_id, _for_profile(profile_id))
                .values(stage=stage.value)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def top_matches(
        self, limit: int = 10, profile_id: int | None = None
    ) -> list[tuple[Job, MatchResult]]:
        async with self._session_factory() as session:
            stmt = (
                select(JobModel, MatchModel)
                .join(MatchModel, MatchModel.job_id == JobModel.id)
                .where(_for_profile(profile_id))
                .order_by(MatchModel.score.desc())
                .limit(limit)
            )
            rows = (await session.execute(stmt)).all()
            return [
                (
                    _to_job(jm),
                    MatchResult(
                        job_id=mm.job_id,
                        profile_id=mm.profile_id,
                        score=MatchScore(value=mm.score),
                        reasons=[Reason(**r) for r in mm.reasons],
                        red_flags=list(mm.red_flags),
                        evaluated_at=mm.evaluated_at,
                        stage=JobStage(mm.stage),
                        work_mode=WorkMode(mm.work_mode) if mm.work_mode else None,
                    ),
                )
                for jm, mm in rows
            ]
