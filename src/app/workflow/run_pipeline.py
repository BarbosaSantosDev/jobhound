import logging

from src.app.dto.pipeline_report import PipelineReport
from src.app.repository import JobRepository
from src.app.service import PipelineStatusTracker
from src.app.usecase import EvaluateJobMatch, FetchNewJobs
from src.domain.service import Notifier

logger = logging.getLogger(__name__)


class PipelineWorkflow:
    def __init__(
        self,
        fetch_jobs: FetchNewJobs,
        evaluate: EvaluateJobMatch,
        job_repo: JobRepository,
        notifier: Notifier,
        status: PipelineStatusTracker | None = None,
    ):
        self._fetch_jobs = fetch_jobs
        self._evaluate = evaluate
        self._job_repo = job_repo
        self._notifier = notifier
        self._status = status

    async def execute(self) -> PipelineReport:
        await self._set_stage("fetch")
        new_jobs = await self._fetch_jobs.execute()

        matches = []
        manual_review = 0
        errors = 0
        # Avaliação em série de propósito: Ollama local não lida bem com paralelo.
        for job in new_jobs:
            try:
                result = await self._evaluate.execute(job)
            except Exception:
                logger.exception("Falha ao avaliar vaga %s", job.id)
                errors += 1
                continue
            await self._set_stage("persist")
            await self._job_repo.save_match(result)
            if result.is_worth_applying:
                matches.append((job, result))
            elif result.needs_manual_review:
                manual_review += 1
                matches.append((job, result))

        if matches:
            await self._notifier.send_matches(matches)

        return PipelineReport(
            fetched=len(new_jobs),
            matched=len(matches) - manual_review,
            manual_review=manual_review,
            errors=errors,
        )

    async def _set_stage(self, stage: str) -> None:
        if self._status is not None:
            await self._status.set_stage(stage)
