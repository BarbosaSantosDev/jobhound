from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.app.repository import JobRepository
from src.domain.entity import Job, MatchResult
from src.domain.value_object import MatchScore
from src.infra.model import JobModel, MatchModel


class JobRepositorySQLAlchemy(JobRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def exists(self, fingerprint: str) -> bool:
        async with self._session_factory() as session:
            stmt = select(JobModel.id).where(JobModel.fingerprint == fingerprint)
            return (await session.execute(stmt)).first() is not None

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

    async def save_match(self, result: MatchResult) -> None:
        async with self._session_factory() as session:
            session.add(
                MatchModel(
                    job_id=result.job_id,
                    score=result.score.value,
                    reasons=result.reasons,
                    red_flags=result.red_flags,
                    evaluated_at=result.evaluated_at,
                )
            )
            await session.commit()

    async def top_matches(self, limit: int = 10) -> list[tuple[Job, MatchResult]]:
        async with self._session_factory() as session:
            stmt = (
                select(JobModel, MatchModel)
                .join(MatchModel, MatchModel.job_id == JobModel.id)
                .order_by(MatchModel.score.desc())
                .limit(limit)
            )
            rows = (await session.execute(stmt)).all()
            return [
                (
                    Job(
                        id=jm.id,
                        title=jm.title,
                        company=jm.company,
                        location=jm.location,
                        description=jm.description,
                        url=jm.url,
                        source=jm.source,
                        fetched_at=jm.fetched_at,
                    ),
                    MatchResult(
                        job_id=mm.job_id,
                        score=MatchScore(value=mm.score),
                        reasons=list(mm.reasons),
                        red_flags=list(mm.red_flags),
                        evaluated_at=mm.evaluated_at,
                    ),
                )
                for jm, mm in rows
            ]
