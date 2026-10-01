from fastapi import APIRouter, Depends, Query

from src.app.query import GetLastRun, ListTopMatches
from src.infra.routers.dependencies import get_last_run, get_top_matches
from src.infra.routers.schemas import StatsSchema

router = APIRouter(prefix="/api/v1", tags=["stats"])


@router.get("/stats", response_model=StatsSchema)
async def get_stats(
    profile: str | None = Query(default=None, description="slug do perfil; sem ele, todas"),
    use_case: ListTopMatches = Depends(get_top_matches),
    last_run_query: GetLastRun = Depends(get_last_run),
) -> StatsSchema:
    pairs = await use_case.execute(limit=200, profile_slug=profile)
    last_run = await last_run_query.execute(profile)
    last = max((r.evaluated_at for _, r in pairs), default=None)
    return StatsSchema(
        fetched=len(pairs),
        matched=sum(1 for _, r in pairs if r.is_worth_applying),
        manual_review=sum(1 for _, r in pairs if r.needs_manual_review),
        errors=last_run.report.errors if last_run else 0,  # do último faro registrado
        last_run=last,
    )