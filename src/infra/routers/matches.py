from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from src.app.query import ListTopMatches
from src.infra.routers.dependencies import get_top_matches
from src.infra.routers.schemas import MatchSchema

router = APIRouter(prefix="/api/v1", tags=["matches"])


@router.get("/matches", response_model=list[MatchSchema])
async def list_matches(
    filter: Literal["all", "apply", "review"] = "all",
    limit: int = Query(default=50, le=200),
    use_case: ListTopMatches = Depends(get_top_matches),
) -> list[MatchSchema]:
    pairs = await use_case.execute(limit)
    schemas = [MatchSchema.from_domain(job, result) for job, result in pairs]
    if filter == "apply":
        schemas = [m for m in schemas if m.result.is_worth_applying]
    elif filter == "review":
        schemas = [m for m in schemas if m.result.needs_manual_review]
    return schemas


@router.get("/jobs/{job_id}", response_model=MatchSchema)
async def get_job(
    job_id: str,
    use_case: ListTopMatches = Depends(get_top_matches),
) -> MatchSchema:
    pairs = await use_case.execute(limit=200)
    for job, result in pairs:
        if job.id == job_id:
            return MatchSchema.from_domain(job, result)
    raise HTTPException(status_code=404, detail="Vaga não encontrada")