from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SourceReport(BaseModel):
    """Como foi uma fonte num faro: quantas vagas trouxe ou por que falhou."""

    name: str
    ok: bool
    fetched: int = 0
    error: str | None = None


class PipelineReport(BaseModel):
    fetched: int
    matched: int
    manual_review: int = 0
    errors: int = 0
    sources: list[SourceReport] = Field(default_factory=list)


class PipelineRun(BaseModel):
    """Registro de uma execução do pipeline, persistido para o dashboard."""

    id: int | None = None
    profile_id: int | None = None
    profile_slug: str | None = None
    started_at: datetime
    finished_at: datetime
    status: Literal["ok", "failed"]
    error: str | None = None
    report: PipelineReport
