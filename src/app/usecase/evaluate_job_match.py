from src.app.service import PipelineStatusTracker
from src.domain.entity import Job, MatchResult, Profile
from src.domain.service import FactExtractor, ScoreInput, ScoreJob


class EvaluateJobMatch:
    """LLM extrai os fatos; o domínio pontua."""

    def __init__(
        self,
        extractor: FactExtractor,
        scorer: ScoreJob,
        profile: Profile,
        status: PipelineStatusTracker | None = None,
    ):
        self._extractor = extractor
        self._scorer = scorer
        self._profile = profile
        self._status = status

    async def execute(self, job: Job) -> MatchResult:
        await self._set_stage("extract")
        facts = await self._extractor.extract(job)
        await self._set_stage("score")
        return self._scorer.evaluate(
            ScoreInput(job_id=job.id, facts=facts, profile=self._profile)
        )

    async def _set_stage(self, stage: str) -> None:
        if self._status is not None:
            await self._status.set_stage(stage)