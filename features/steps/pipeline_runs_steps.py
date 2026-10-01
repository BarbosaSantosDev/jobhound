import asyncio

from behave import given, then, when

from features.fakes import (
    ConstantExtractor,
    FakeSource,
    InMemoryJobRepository,
    InMemoryPipelineRunRepository,
    InMemoryProfileRepository,
    RecordingNotifier,
    call_api,
    make_job,
)
from src.app.query import GetLastRun
from src.app.service.pipeline_status import PipelineStatusTracker
from src.app.usecase import EvaluateJobMatch, FetchNewJobs
from src.app.workflow import PipelineWorkflow, RunTarget
from src.domain.entity.profile import Profile
from src.domain.service import ScoreJob
from src.infra.routers.dependencies import get_last_run, get_pipeline_status_tracker
from src.server import create_app


@given('o perfil "{name}" cadastrado para farejar')
def step_profile(context, name):
    context.profile_repo = InMemoryProfileRepository()
    profile = Profile.create(name=name, headline="Dev", seniority="pleno", primary_stack=["Python"])
    context.profile = asyncio.run(context.profile_repo.save(profile))
    context.job_repo = InMemoryJobRepository()
    context.sources = []
    context.notifier = RecordingNotifier()


@given("um histórico de faros vazio")
def step_empty_history(context):
    context.run_repo = InMemoryPipelineRunRepository()


@given('a fonte "{name}" trazendo as vagas "{job_ids}"')
def step_source_ok(context, name, job_ids):
    jobs = [make_job(j.strip(), title=f"Vaga {j.strip()}", source=name) for j in job_ids.split(",")]
    context.sources.append(FakeSource(name, jobs))


@given('a fonte "{name}" fora do ar com o erro "{error}"')
def step_source_down(context, name, error):
    context.sources.append(FakeSource(name, error=error))


@given('um notificador que falha com o erro "{error}"')
def step_failing_notifier(context, error):
    context.notifier = RecordingNotifier(error=error)


def _workflow(context, slug: str) -> PipelineWorkflow:
    profile = asyncio.run(context.profile_repo.load(slug))
    return PipelineWorkflow(
        fetch_jobs=FetchNewJobs(context.sources, context.job_repo, profile_id=profile.id),
        evaluate=EvaluateJobMatch(ConstantExtractor(), ScoreJob(), profile),
        job_repo=context.job_repo,
        notifier=context.notifier,
        run_repo=context.run_repo,
        target=RunTarget(profile_id=profile.id, profile_slug=profile.slug),
    )


@given('o pipeline já farejou para o perfil "{slug}"')
@when('o pipeline fareja para o perfil "{slug}"')
def step_run(context, slug):
    asyncio.run(_workflow(context, slug).execute())


@when('o pipeline fareja para o perfil "{slug}" e a execução quebra')
def step_run_breaks(context, slug):
    try:
        asyncio.run(_workflow(context, slug).execute())
    except RuntimeError as exc:
        context.run_error = exc
    assert getattr(context, "run_error", None) is not None, "era esperado que o faro quebrasse"


def _last(context):
    return asyncio.run(context.run_repo.last(context.profile.id))


@then('o último faro registrado deve ter status "{status}" e perfil "{slug}"')
def step_last_status(context, status, slug):
    run = _last(context)
    assert run is not None, "nenhum faro registrado"
    assert (run.status, run.profile_slug) == (status, slug), (run.status, run.profile_slug)


@then("o último faro deve ter {count:d} vagas novas")
def step_last_fetched(context, count):
    assert _last(context).report.fetched == count, _last(context).report


@then('a fonte "{name}" deve constar como ok com {count:d} vagas')
def step_source_ok_report(context, name, count):
    report = next(s for s in _last(context).report.sources if s.name == name)
    assert report.ok and report.fetched == count, report


@then('a fonte "{name}" deve constar com falha "{error}"')
def step_source_failed_report(context, name, error):
    report = next(s for s in _last(context).report.sources if s.name == name)
    assert not report.ok and report.error == error, report


@then('o último faro deve ter o erro "{error}"')
def step_last_error(context, error):
    assert _last(context).error == error, _last(context).error


@when('eu consulto o status do pipeline do perfil "{slug}" pela API')
def step_status_api(context, slug):
    app = create_app()
    runs, profiles = context.run_repo, context.profile_repo
    app.dependency_overrides[get_pipeline_status_tracker] = PipelineStatusTracker
    app.dependency_overrides[get_last_run] = lambda: GetLastRun(runs, profiles)
    context.response = call_api(app, "GET", f"/api/v1/pipeline/status?profile={slug}")
    assert context.response.status_code == 200, context.response.text


@then("o status deve trazer o último faro com {count:d} vaga nova")
def step_status_last_run(context, count):
    last_run = context.response.json()["last_run"]
    assert last_run is not None and last_run["fetched"] == count, last_run


@then('o último faro da API deve listar a fonte "{name}" como ok')
def step_status_source(context, name):
    sources = {s["name"]: s for s in context.response.json()["last_run"]["sources"]}
    assert sources[name]["ok"] is True, sources
