from datetime import datetime, timezone

from pydantic import BaseModel, Field

from src.domain.value_object import MatchScore

BLOCKING_FLAGS = {"seniority_mismatch", "stack_incompatible"}



class MatchResult(BaseModel):
    job_id: str
    score: MatchScore
    reasons: list[str]
    red_flags: list[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_worth_applying(self) -> bool:
        return self.score.is_high and not self._has_blocking_flags()

    @property
    def needs_manual_review(self) -> bool:
        return self.score.is_gray_zone and not self._has_blocking_flags()

    def _has_blocking_flags(self) -> bool:
        return any(flag in BLOCKING_FLAGS for flag in self.red_flags)
