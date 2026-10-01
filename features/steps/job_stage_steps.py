import asyncio

from behave import given, then, when

from features.fakes import (
    InMemoryJobRepository,
    InMemoryProfileRepository,
    call_api,
    make_job,
    make_match,
)
from src.app.query import ListTopMatches
from src.app.usecase import ChangeJobStage
from src.infra.routers.dependencies import get_change_job_stage, get_top_matches
from src.server import create_app


@given("a API do jobhound com um repositório de vagas em memória")
def step_api_with_jobs(context):
    context.app = create_app()
    context.job_repo = InMemoryJobRepository()
    context.profile_repo = InMemoryProfileRepository()
    jobs, profiles = context.job_repo, context.profile_repo
    overrides = context.app.dependency_overrides
    overrides[get_top_matches] = lambda: ListTopMatches(jobs, profiles)
    overrides[get_change_job_stage] = lambda: ChangeJobStage(jobs, profiles)


@given('a vaga "{job_id}" avaliada com score {score:d}')
def step_seed(context, job_id, score):
    asyncio.run(context.job_repo.save(make_job(job_id)))
    asyncio.run(context.job_repo.save_match(make_match(job_id, score)))


@given('a vaga "{job_id}" já movida para "{stage}"')
@when('eu movo a vaga "{job_id}" para a etapa "{stage}"')
def step_move(context, job_id, stage):
    context.response = call_api(
        context.app, "PATCH", f"/api/v1/matches/{job_id}/stage", {"stage": stage}
    )


@when("eu listo as vagas")
@then("eu listo as vagas")
def step_list(context):
    context.listing = call_api(context.app, "GET", "/api/v1/matches?limit=200").json()


@then('a vaga "{job_id}" deve estar na etapa "{stage}"')
def step_stage_is(context, job_id, stage):
    match = next(m for m in context.listing if m["job"]["id"] == job_id)
    assert match["result"]["stage"] == stage, match["result"]
