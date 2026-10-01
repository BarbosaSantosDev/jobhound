from datetime import datetime, timezone

from pydantic import BaseModel, Field

from src.domain.value_object import JobStage, MatchScore, Reason, WorkMode

BLOCKING_FLAGS = {"seniority_mismatch", "stack_incompatible"}



class MatchResult(BaseModel):
    job_id: str
    # perfil contra o qual a vaga foi pontuada; None em avaliações legadas
    profile_id: int | None = None
    score: MatchScore
    reasons: list[Reason]
    red_flags: list[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    stage: JobStage = JobStage.NEW
    # modalidade extraída da vaga; None em avaliações anteriores a este campo
    work_mode: WorkMode | None = None

    @property
    def is_worth_applying(self) -> bool:
        return self.score.is_high and not self._has_blocking_flags()

    @property
    def needs_manual_review(self) -> bool:
        return self.score.is_gray_zone and not self._has_blocking_flags()

    def _has_blocking_flags(self) -> bool:
        return any(flag in BLOCKING_FLAGS for flag in self.red_flags)
