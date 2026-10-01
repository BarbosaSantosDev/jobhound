from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.app.dto.pipeline_report import PipelineReport, PipelineRun
from src.app.repository import PipelineRunRepository
from src.infra.model import PipelineRunModel


class PipelineRunRepositorySQLAlchemy(PipelineRunRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def save(self, run: PipelineRun) -> PipelineRun:
        async with self._session_factory() as session:
            model = PipelineRunModel(
                profile_id=run.profile_id,
                profile_slug=run.profile_slug,
                started_at=run.started_at,
                finished_at=run.finished_at,
                status=run.status,
                error=run.error,
                report=run.report.model_dump(mode="json"),
            )
            session.add(model)
            await session.commit()
            return run.model_copy(update={"id": model.id})

    async def last(self, profile_id: int | None = None) -> PipelineRun | None:
        async with self._session_factory() as session:
            stmt = select(PipelineRunModel).order_by(PipelineRunModel.finished_at.desc()).limit(1)
            if profile_id is not None:
                stmt = stmt.where(PipelineRunModel.profile_id == profile_id)
            model = (await session.execute(stmt)).scalar_one_or_none()
            if model is None:
                return None
            return PipelineRun(
                id=model.id,
                profile_id=model.profile_id,
                profile_slug=model.profile_slug,
                started_at=model.started_at,
                finished_at=model.finished_at,
                status=model.status,
                error=model.error,
                report=PipelineReport(**model.report),
            )
