from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from src.app.service import PipelineStatus
from src.domain.entity import Job, Profile
from src.domain.entity.match_result import MatchResult


class JobSchema(BaseModel):
    id: str
    title: str
    company: str
    location: str
    source: str
    url: str
    fetched_at: datetime


class MatchResultSchema(BaseModel):
    score: int
    reasons: list[str]
    red_flags: list[str]
    is_worth_applying: bool
    needs_manual_review: bool
    evaluated_at: datetime


class MatchSchema(BaseModel):
    job: JobSchema
    result: MatchResultSchema

    @classmethod
    def from_domain(cls, job: Job, result: MatchResult) -> "MatchSchema":
        return cls(
            job=JobSchema(
                id=job.id,
                title=job.title,
                company=job.company,
                location=job.location,
                source=job.source,
                url=job.url,
                fetched_at=job.fetched_at,
            ),
            result=MatchResultSchema(
                score=result.score.value,
                reasons=result.reasons,
                red_flags=result.red_flags,
                is_worth_applying=result.is_worth_applying,
                needs_manual_review=result.needs_manual_review,
                evaluated_at=result.evaluated_at,
            ),
        )


class StatsSchema(BaseModel):
    fetched: int
    matched: int
    manual_review: int
    errors: int
    last_run: datetime | None = None


class PipelineRunResponse(BaseModel):
    status: str
    detail: str


class PipelineStatusSchema(BaseModel):
    running: bool
    stage: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    last_error: str | None = None

    @classmethod
    def from_domain(cls, status: PipelineStatus) -> "PipelineStatusSchema":
        return cls(
            running=status.running,
            stage=status.stage,
            started_at=status.started_at,
            finished_at=status.finished_at,
            last_error=status.last_error,
        )



class SearchPreferencesSchema(BaseModel):
    gupy_terms: list[str] = []
    nerdin_platforms: list[str] = []
    remoteok_tags: list[str] = []


class ProfileWriteSchema(BaseModel):
    """Corpo aceito em POST/PUT — o slug não entra aqui: é derivado do nome (registro)
    ou vem da URL (atualização). `search` também não entra: é derivado no domínio a
    partir da stack (ver SearchPreferences.derive)."""

    name: str
    headline: str
    seniority: Literal["junior", "pleno", "senior"]
    primary_stack: list[str]
    secondary_stack: list[str] = []
    preferred_locations: list[str] = []
    accepts_remote: bool = True
    summary: str = ""


class ProfileSchema(ProfileWriteSchema):
    slug: str
    search: SearchPreferencesSchema

    @classmethod
    def from_domain(cls, p: Profile) -> "ProfileSchema":
        return cls(
            slug=p.slug,
            name=p.name,
            headline=p.headline,
            seniority=p.seniority,
            primary_stack=p.primary_stack,
            secondary_stack=p.secondary_stack,
            preferred_locations=p.preferred_locations,
            accepts_remote=p.accepts_remote,
            summary=p.summary,
            search=SearchPreferencesSchema(
                gupy_terms=p.search.gupy_terms,
                nerdin_platforms=p.search.nerdin_platforms,
                remoteok_tags=p.search.remoteok_tags,
            ),
        )