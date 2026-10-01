from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from src.app.dto.pipeline_report import PipelineRun
from src.app.service import PipelineStatus
from src.domain.entity import Job, Profile
from src.domain.entity.match_result import MatchResult
from src.domain.value_object import JobStage, ReasonKind, SourceName, WorkMode


class JobSchema(BaseModel):
    id: str
    title: str
    company: str
    location: str
    source: str
    url: str
    fetched_at: datetime
    summary: str | None = None


class ReasonSchema(BaseModel):
    kind: ReasonKind
    text: str


class MatchResultSchema(BaseModel):
    score: int
    reasons: list[ReasonSchema]
    red_flags: list[str]
    is_worth_applying: bool
    needs_manual_review: bool
    evaluated_at: datetime
    stage: JobStage
    work_mode: WorkMode | None = None


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
                summary=job.excerpt(),
            ),
            result=MatchResultSchema(
                score=result.score.value,
                reasons=[ReasonSchema(kind=r.kind, text=r.text) for r in result.reasons],
                red_flags=result.red_flags,
                is_worth_applying=result.is_worth_applying,
                needs_manual_review=result.needs_manual_review,
                evaluated_at=result.evaluated_at,
                stage=result.stage,
                work_mode=result.work_mode,
            ),
        )


class JobStageSchema(BaseModel):
    stage: JobStage


class JobStageResponse(JobStageSchema):
    job_id: str


class StatsSchema(BaseModel):
    fetched: int
    matched: int
    manual_review: int
    errors: int
    last_run: datetime | None = None


class PipelineRunResponse(BaseModel):
    status: str
    detail: str


class SourceReportSchema(BaseModel):
    name: str
    ok: bool
    fetched: int
    error: str | None = None


class PipelineRunSchema(BaseModel):
    profile: str | None = None
    started_at: datetime
    finished_at: datetime
    status: Literal["ok", "failed"]
    error: str | None = None
    fetched: int  # vagas novas para o perfil (entraram em avaliação)
    matched: int
    manual_review: int
    errors: int
    sources: list[SourceReportSchema]

    @classmethod
    def from_domain(cls, run: PipelineRun) -> "PipelineRunSchema":
        r = run.report
        return cls(
            profile=run.profile_slug,
            started_at=run.started_at,
            finished_at=run.finished_at,
            status=run.status,
            error=run.error,
            fetched=r.fetched,
            matched=r.matched,
            manual_review=r.manual_review,
            errors=r.errors,
            sources=[SourceReportSchema(**s.model_dump()) for s in r.sources],
        )


class PipelineStatusSchema(BaseModel):
    running: bool
    profile: str | None = None
    stage: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    last_error: str | None = None
    last_run: PipelineRunSchema | None = None

    @classmethod
    def from_domain(cls, status: PipelineStatus) -> "PipelineStatusSchema":
        return cls(
            running=status.running,
            profile=status.profile,
            stage=status.stage,
            started_at=status.started_at,
            finished_at=status.finished_at,
            last_error=status.last_error,
            last_run=PipelineRunSchema.from_domain(status.last_run) if status.last_run else None,
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
    enabled_sources: list[SourceName] = Field(default_factory=lambda: list(SourceName))

    @field_validator("enabled_sources")
    @classmethod
    def _dedupe(cls, value: list[SourceName]) -> list[SourceName]:
        return list(dict.fromkeys(value))


class ProfileSchema(ProfileWriteSchema):
    slug: str
    search: SearchPreferencesSchema
    # ligadas pelo candidato E com termo de busca: o que o próximo faro usa
    active_sources: list[SourceName]

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
            enabled_sources=p.enabled_sources,
            active_sources=p.active_sources(),
            search=SearchPreferencesSchema(
                gupy_terms=p.search.gupy_terms,
                nerdin_platforms=p.search.nerdin_platforms,
                remoteok_tags=p.search.remoteok_tags,
            ),
        )