import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from src.app.dto.pipeline_report import PipelineReport, PipelineRun
from src.app.repository import JobRepository, PipelineRunRepository
from src.app.service import PipelineStatusTracker
from src.app.usecase import EvaluateJobMatch, FetchNewJobs
from src.domain.service import Notifier

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RunTarget:
    """Para qual perfil este faro roda — vai junto no registro da execução."""

    profile_id: int | None = None
    profile_slug: str | None = None


class PipelineWorkflow:
    def __init__(
        self,
        fetch_jobs: FetchNewJobs,
        evaluate: EvaluateJobMatch,
        job_repo: JobRepository,
        notifier: Notifier,
        status: PipelineStatusTracker | None = None,
        run_repo: PipelineRunRepository | None = None,
        target: RunTarget = RunTarget(),
    ):
        self._fetch_jobs = fetch_jobs
        self._evaluate = evaluate
        self._job_repo = job_repo
        self._notifier = notifier
        self._status = status
        self._run_repo = run_repo
        self._target = target

    async def execute(self) -> PipelineReport:
        # O registro vale para API, CLI e scheduler: quem roda é sempre este workflow.
        started_at = datetime.now(UTC)
        try:
            report = await self._run()
        except Exception as exc:
            await self._record(started_at, PipelineReport(fetched=0, matched=0), error=str(exc))
            raise
        await self._record(started_at, report, error=None)
        return report

    async def _run(self) -> PipelineReport:
        await self._set_stage("fetch")
        fetched = await self._fetch_jobs.execute()

        matches = []
        manual_review = 0
        errors = 0
        # Avaliação em série de propósito: Ollama local não lida bem com paralelo.
        for job in fetched.jobs:
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
            fetched=len(fetched.jobs),
            matched=len(matches) - manual_review,
            manual_review=manual_review,
            errors=errors,
            sources=fetched.sources,
        )

    async def _record(self, started_at: datetime, report: PipelineReport, error: str | None) -> None:
        if self._run_repo is None:
            return
        run = PipelineRun(
            profile_id=self._target.profile_id,
            profile_slug=self._target.profile_slug,
            started_at=started_at,
            finished_at=datetime.now(UTC),
            status="failed" if error else "ok",
            error=error,
            report=report,
        )
        try:
            await self._run_repo.save(run)
        except Exception:
            # Falhar ao registrar não pode derrubar um faro que deu certo.
            logger.exception("Falha ao registrar a execução do pipeline")

    async def _set_stage(self, stage: str) -> None:
        if self._status is not None:
            await self._status.set_stage(stage)
