import asyncio

import httpx
from behave import given, then, when

from src.app.dto.pipeline_report import PipelineReport
from src.app.service.pipeline_status import PipelineStatusTracker
from src.infra.routers.dependencies import get_pipeline, get_pipeline_status_tracker
from src.server import create_app


class _PausedPipeline:
    """Fake de PipelineWorkflow que fica parado até o teste liberar — simula
    uma execução em andamento sem depender de LLM/Postgres reais (mesmo
    espírito do FakeExtractor em match_steps.py)."""

    def __init__(self) -> None:
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def execute(self) -> PipelineReport:
        self.started.set()
        await self.release.wait()
        return PipelineReport(fetched=0, matched=0, manual_review=0, errors=0)


@given("a API do jobhound configurada com um pipeline falso")
def step_setup_app(context):
    context.app = create_app()
    context.tracker = PipelineStatusTracker()
    context.fake_pipeline = _PausedPipeline()
    context.app.dependency_overrides[get_pipeline] = lambda: context.fake_pipeline
    context.app.dependency_overrides[get_pipeline_status_tracker] = lambda: context.tracker


async def _get_status(context):
    transport = httpx.ASGITransport(app=context.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get("/api/v1/pipeline/status")


@when("eu consulto o status do pipeline")
def step_query_status(context):
    context.status_response = asyncio.run(_get_status(context))


async def _run_check_and_retry(context):
    transport = httpx.ASGITransport(app=context.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        run_task = asyncio.create_task(client.post("/api/v1/pipeline/run"))
        await asyncio.wait_for(context.fake_pipeline.started.wait(), timeout=1)

        status_response = await client.get("/api/v1/pipeline/status")
        second_run_response = await client.post("/api/v1/pipeline/run")

        context.fake_pipeline.release.set()
        await run_task

        return status_response, second_run_response


@when("eu rodo o pipeline, consulto o status ainda em andamento e tento rodar de novo")
def step_run_and_check(context):
    context.status_response, context.second_run_response = asyncio.run(
        _run_check_and_retry(context)
    )


@then("a resposta deve ter running false e stage nulo")
def step_assert_idle(context):
    assert context.status_response.status_code == 200
    body = context.status_response.json()
    assert body["running"] is False
    assert body["stage"] is None


@then("a resposta de status deve ter running true")
def step_assert_running(context):
    assert context.status_response.status_code == 200
    body = context.status_response.json()
    assert body["running"] is True


@then("a segunda chamada de rodar deve retornar 409")
def step_assert_409(context):
    assert context.second_run_response.status_code == 409
