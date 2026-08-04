import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from src.app.query import GetPipelineStatus
from src.app.service import PipelineStatusTracker
from src.app.workflow import PipelineWorkflow
from src.infra.routers.dependencies import (
    get_pipeline,
    get_pipeline_status_tracker,
    get_pipeline_status_usecase,
)
from src.infra.routers.schemas import PipelineRunResponse, PipelineStatusSchema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["pipeline"])


async def _run_in_background(pipeline: PipelineWorkflow, status: PipelineStatusTracker) -> None:
    error: str | None = None
    try:
        report = await pipeline.execute()
        logger.info(
            "Pipeline concluído: %d novas, %d matches, %d revisão, %d erros",
            report.fetched, report.matched, report.manual_review, report.errors,
        )
    except Exception as exc:
        logger.exception("Pipeline falhou durante execução em background")
        error = str(exc)
    finally:
        # Sempre executa, mesmo se a exceção acima não for um Exception "normal"
        # (ex.: cancelamento) — garante que running nunca fica travado em true.
        await status.finish(error)


@router.post("/pipeline/run", response_model=PipelineRunResponse, status_code=202)
async def run_pipeline(
    background_tasks: BackgroundTasks,
    pipeline: PipelineWorkflow = Depends(get_pipeline),
    status: PipelineStatusTracker = Depends(get_pipeline_status_tracker),
) -> PipelineRunResponse:
    if not await status.try_start():
        raise HTTPException(status_code=409, detail="Pipeline já está em execução")

    background_tasks.add_task(_run_in_background, pipeline, status)
    return PipelineRunResponse(status="started", detail="Pipeline iniciado em background")


@router.get("/pipeline/status", response_model=PipelineStatusSchema)
async def get_pipeline_status(
    use_case: GetPipelineStatus = Depends(get_pipeline_status_usecase),
) -> PipelineStatusSchema:
    status = await use_case.execute()
    return PipelineStatusSchema.from_domain(status)
