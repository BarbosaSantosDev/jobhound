from behave import given, then, when

from features.fakes import call_api
from src.domain.entity.profile import Profile
from src.domain.value_object import SourceName


def _split(csv: str) -> list[str]:
    return [s.strip() for s in csv.split(",") if s.strip()]


@given('um perfil com stack principal "{primary}" e secundária "{secondary}"')
def step_profile(context, primary, secondary):
    context.profile = Profile.create(
        name="Ana",
        headline="Dev",
        seniority="pleno",
        primary_stack=_split(primary),
        secondary_stack=_split(secondary),
    )


@given('um perfil sem stack principal e com secundária "{secondary}"')
def step_profile_no_primary(context, secondary):
    step_profile(context, "", secondary)


@given('as fontes ligadas "{sources}"')
def step_enabled(context, sources):
    context.profile = context.profile.model_copy(
        update={"enabled_sources": [SourceName(s) for s in _split(sources)]}
    )


@then('as fontes ativas devem ser "{sources}"')
def step_active(context, sources):
    active = [s.value for s in context.profile.active_sources()]
    assert active == _split(sources), active


@given('o perfil "{name}" registrado com as fontes "{sources}"')
def step_register_with_sources(context, name, sources):
    body = {
        "name": name,
        "headline": "Dev",
        "seniority": "pleno",
        "primary_stack": ["Python"],
        "enabled_sources": _split(sources),
    }
    response = call_api(context.app, "POST", "/api/v1/profiles", body)
    assert response.status_code == 201, response.text


@when('eu registro o perfil "{name}" com a fonte "{source}"')
def step_register_bad_source(context, name, source):
    body = {
        "name": name,
        "headline": "Dev",
        "seniority": "pleno",
        "primary_stack": ["Python"],
        "enabled_sources": [source],
    }
    context.response = call_api(context.app, "POST", "/api/v1/profiles", body)


@when('eu consulto o perfil "{slug}"')
def step_get_profile(context, slug):
    context.response = call_api(context.app, "GET", f"/api/v1/profiles/{slug}")
    assert context.response.status_code == 200, context.response.text


@then('o perfil deve ter as fontes ligadas "{sources}"')
def step_enabled_is(context, sources):
    assert context.response.json()["enabled_sources"] == _split(sources)


@then('o perfil deve ter as fontes ativas "{sources}"')
def step_active_is(context, sources):
    assert context.response.json()["active_sources"] == _split(sources)
