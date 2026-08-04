import asyncio

from behave import given, then, when

from src.app.usecase.evaluate_job_match import EvaluateJobMatch
from src.domain.entity import Job, JobFacts, Profile
from src.domain.service import FactExtractor, ScoreJob
from src.domain.value_object import Seniority, WorkMode


class FakeExtractor(FactExtractor):
    """Fake determinístico — mesmo padrão dos fake repositories."""

    def __init__(self, facts: JobFacts):
        self._facts = facts

    async def extract(self, job: Job) -> JobFacts:
        return self._facts


def _job() -> Job:
    return Job(
        id="job-1",
        title="Vaga de teste",
        company="Empresa X",
        location="Remoto",
        description="...",
        url="https://example.com",
        source="fake",
    )


@given("um perfil backend pleno com Python e FastAPI")
def step_profile(context):
    context.profile = Profile.create(
        name="João",
        headline="Backend Pleno",
        seniority="pleno",
        primary_stack=["Python", "FastAPI"],
        preferred_locations=["Santos", "São Paulo"],
        accepts_remote=True,
    )


@given("uma vaga remota que menciona Python e FastAPI para pleno")
def step_good_job(context):
    context.facts = JobFacts(
        mentioned_stack=["Python", "FastAPI"],
        seniority=Seniority.PLENO,
        work_mode=WorkMode.REMOTE,
    )


@given("uma vaga presencial sênior que exige Java")
def step_bad_job(context):
    context.facts = JobFacts(
        mentioned_stack=["Java"],
        seniority=Seniority.SENIOR,
        work_mode=WorkMode.ONSITE,
        location_city="Recife",
    )


@given("uma vaga que menciona Python sem senioridade nem modo de trabalho")
def step_gray_job(context):
    context.facts = JobFacts(
        mentioned_stack=["Python"],
        seniority=Seniority.NOT_INFORMED,
        work_mode=WorkMode.NOT_INFORMED,
    )


@when("o matcher avalia a vaga")
def step_evaluate(context):
    use_case = EvaluateJobMatch(FakeExtractor(context.facts), ScoreJob(), context.profile)
    context.result = asyncio.run(use_case.execute(_job()))


@then("o score deve ser maior ou igual a 70")
def step_score_high(context):
    assert context.result.score.value >= 70, f"score={context.result.score.value}"


@then("a vaga deve ser marcada como digna de aplicação")
def step_worth(context):
    assert context.result.is_worth_applying


@then('deve haver red flag "{flag}"')
def step_flag(context, flag):
    assert flag in context.result.red_flags, context.result.red_flags


@then("a vaga não deve ser marcada como digna de aplicação")
def step_not_worth(context):
    assert not context.result.is_worth_applying


@then("a vaga deve ser marcada para revisão manual")
def step_manual(context):
    assert context.result.needs_manual_review, (
        f"score={context.result.score.value}, flags={context.result.red_flags}"
    )
