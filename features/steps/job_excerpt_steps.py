from behave import given, then, when

from features.fakes import make_job


@given('uma vaga com a descrição "{description}"')
def step_job(context, description):
    context.job = make_job("job-1", description=description)


@when("eu gero o resumo da vaga")
def step_excerpt(context):
    context.excerpt = context.job.excerpt()


@when("eu gero o resumo da vaga com no máximo {max_chars:d} caracteres")
def step_excerpt_max(context, max_chars):
    context.excerpt = context.job.excerpt(max_chars=max_chars)


@then('o resumo deve ser "{expected}"')
def step_excerpt_is(context, expected):
    assert context.excerpt == expected, repr(context.excerpt)


@then("não deve haver resumo")
def step_no_excerpt(context):
    assert context.excerpt is None, repr(context.excerpt)
