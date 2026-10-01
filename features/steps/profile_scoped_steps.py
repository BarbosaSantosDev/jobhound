import asyncio

from behave import given, then, when

from features.fakes import (
    FakeSource,
    InMemoryJobRepository,
    InMemoryProfileRepository,
    call_api,
    make_job,
    make_match,
)
from src.app.query import ListProfiles, ListTopMatches
from src.app.usecase import ChangeJobStage, FetchNewJobs, GetProfile
from src.domain.entity.profile import Profile
from src.infra.routers.dependencies import (
    get_change_job_stage,
    get_list_profiles,
    get_profile_usecase,
    get_top_matches,
)
from src.server import create_app


@given("a API do jobhound com repositórios de vagas e perfis em memória")
def step_api(context):
    context.app = create_app()
    context.job_repo = InMemoryJobRepository()
    context.profile_repo = InMemoryProfileRepository()
    jobs, profiles = context.job_repo, context.profile_repo
    overrides = context.app.dependency_overrides
    overrides[get_top_matches] = lambda: ListTopMatches(jobs, profiles)
    overrides[get_change_job_stage] = lambda: ChangeJobStage(jobs, profiles)
    overrides[get_list_profiles] = lambda: ListProfiles(profiles)
    overrides[get_profile_usecase] = lambda: GetProfile(profiles)


def _profile_id(context, slug: str) -> int:
    return asyncio.run(context.profile_repo.load(slug)).id


@given('os perfis "{first}" e "{second}" cadastrados')
def step_profiles(context, first, second):
    for name in (first, second):
        profile = Profile.create(name=name, headline="Dev", seniority="pleno", primary_stack=["Python"])
        asyncio.run(context.profile_repo.save(profile))


def _seed(context, job_id: str, score: int, profile_id: int | None) -> None:
    job = make_job(job_id, title=f"Vaga {job_id}")
    asyncio.run(context.job_repo.save(job))
    asyncio.run(context.job_repo.save_match(make_match(job_id, score, profile_id=profile_id)))


@given('a vaga "{job_id}" avaliada para o perfil "{slug}" com score {score:d}')
@given('a vaga "{job_id}" avaliada também para o perfil "{slug}" com score {score:d}')
def step_seed_for_profile(context, job_id, slug, score):
    _seed(context, job_id, score, _profile_id(context, slug))


@given('a vaga "{job_id}" avaliada antes de existirem perfis com score {score:d}')
def step_seed_legacy(context, job_id, score):
    _seed(context, job_id, score, None)


@when('eu listo as vagas do perfil "{slug}"')
def step_list_for(context, slug):
    context.response = call_api(context.app, "GET", f"/api/v1/matches?limit=200&profile={slug}")


@when("eu listo as vagas sem escolher perfil")
def step_list_all(context):
    context.response = call_api(context.app, "GET", "/api/v1/matches?limit=200")


@then('as vagas listadas devem ser "{job_ids}"')
def step_listed(context, job_ids):
    assert context.response.status_code == 200, context.response.text
    listed = [m["job"]["id"] for m in context.response.json()]
    assert listed == [j.strip() for j in job_ids.split(",")], listed


@when('o perfil "{slug}" move a vaga "{job_id}" para a etapa "{stage}"')
def step_move_for(context, slug, job_id, stage):
    response = call_api(
        context.app, "PATCH", f"/api/v1/matches/{job_id}/stage?profile={slug}", {"stage": stage}
    )
    assert response.status_code == 200, response.text


@then('para o perfil "{slug}", a vaga "{job_id}" deve estar na etapa "{stage}"')
def step_stage_for(context, slug, job_id, stage):
    pid = _profile_id(context, slug)
    match = next(m for m in context.job_repo.matches if m.job_id == job_id and m.profile_id == pid)
    assert match.stage == stage, match.stage


@given('uma fonte que traz as vagas "{job_ids}"')
def step_source(context, job_ids):
    # mesma vaga = mesmo título/empresa/local (fingerprint), como viria da fonte
    context.source = FakeSource("fake", [make_job(j.strip(), title=f"Vaga {j.strip()}") for j in job_ids.split(",")])


@when('eu busco vagas novas para o perfil "{slug}"')
def step_fetch(context, slug):
    use_case = FetchNewJobs([context.source], context.job_repo, profile_id=_profile_id(context, slug))
    context.offered = asyncio.run(use_case.execute()).jobs
    # o pipeline avaliaria cada vaga oferecida; simula isso para o próximo passo
    for job in context.offered:
        asyncio.run(context.job_repo.save_match(make_match(job.id, 50, profile_id=_profile_id(context, slug))))


@then('as vagas oferecidas devem ser "{job_ids}"')
def step_offered(context, job_ids):
    offered = [j.id for j in context.offered]
    assert offered == [j.strip() for j in job_ids.split(",")], offered
