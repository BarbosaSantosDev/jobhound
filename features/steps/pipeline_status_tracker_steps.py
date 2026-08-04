import asyncio

from behave import given, then, when

from src.app.service.pipeline_status import PipelineStatusTracker


@given("um rastreador de status novo")
def step_new_tracker(context):
    context.tracker = PipelineStatusTracker()


@given("uma execução já foi iniciada")
def step_already_started(context):
    started = asyncio.run(context.tracker.try_start())
    assert started, "setup: era esperado que a primeira execução iniciasse"


@when("eu tento iniciar uma execução")
def step_try_start(context):
    context.try_start_result = asyncio.run(context.tracker.try_start())


@then("a tentativa deve ter sido aceita")
def step_accepted(context):
    assert context.try_start_result is True


@then("a tentativa deve ter sido recusada")
def step_refused(context):
    assert context.try_start_result is False


@when("eu finalizo a execução sem erro")
def step_finish_ok(context):
    asyncio.run(context.tracker.finish(error=None))


@when('eu finalizo a execução com o erro "{message}"')
def step_finish_error(context, message):
    asyncio.run(context.tracker.finish(error=message))


@then("o status deve indicar que está rodando")
def step_status_running(context):
    status = asyncio.run(context.tracker.snapshot())
    assert status.running is True


@then("o status deve indicar que não está rodando")
def step_status_not_running(context):
    status = asyncio.run(context.tracker.snapshot())
    assert status.running is False


@then("o último erro deve ser nulo")
def step_error_none(context):
    status = asyncio.run(context.tracker.snapshot())
    assert status.last_error is None


@then('o último erro deve ser "{message}"')
def step_error_message(context, message):
    status = asyncio.run(context.tracker.snapshot())
    assert status.last_error == message
