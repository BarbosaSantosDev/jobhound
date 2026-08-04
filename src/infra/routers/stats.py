from fastapi import APIRouter, Depends

from src.app.query import ListTopMatches
from src.infra.routers.dependencies import get_top_matches
from src.infra.routers.schemas import StatsSchema

router = APIRouter(prefix="/api/v1", tags=["stats"])


@router.get("/stats", response_model=StatsSchema)
async def get_stats(
    use_case: ListTopMatches = Depends(get_top_matches),
) -> StatsSchema:
    pairs = await use_case.execute(limit=200)
    last = max((r.evaluated_at for _, r in pairs), default=None)
    return StatsSchema(
        fetched=len(pairs),
        matched=sum(1 for _, r in pairs if r.is_worth_applying),
        manual_review=sum(1 for _, r in pairs if r.needs_manual_review),
        errors=0,  # vem da tabela pipeline_runs quando ela existir
        last_run=last,
    )