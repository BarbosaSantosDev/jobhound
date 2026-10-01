from behave import given, then, when

from features.fakes import InMemoryProfileRepository, call_api
from src.app.query import ListProfiles
from src.app.usecase import GetProfile, RegisterProfile, UpdateProfile
from src.infra.routers.dependencies import (
    get_list_profiles,
    get_profile_usecase,
    get_register_profile_usecase,
    get_update_profile_usecase,
)
from src.server import create_app


@given("a API do jobhound com um repositório de perfis em memória")
def step_api_with_profiles(context):
    context.app = create_app()
    context.profile_repo = InMemoryProfileRepository()
    repo = context.profile_repo
    overrides = context.app.dependency_overrides
    overrides[get_list_profiles] = lambda: ListProfiles(repo)
    overrides[get_profile_usecase] = lambda: GetProfile(repo)
    overrides[get_register_profile_usecase] = lambda: RegisterProfile(repo)
    overrides[get_update_profile_usecase] = lambda: UpdateProfile(repo)


def _profile_body(name: str, stack: str, **extra) -> dict:
    return {
        "name": name,
        "headline": "Dev",
        "seniority": "pleno",
        "primary_stack": [s.strip() for s in stack.split(",")],
        **extra,
    }


@given('o perfil "{name}" registrado com a stack "{stack}"')
def step_register(context, name, stack):
    response = call_api(context.app, "POST", "/api/v1/profiles", _profile_body(name, stack))
    assert response.status_code == 201, response.text


@when('eu atualizo a headline do perfil "{slug}" para "{headline}"')
def step_update_headline(context, slug, headline):
    current = call_api(context.app, "GET", f"/api/v1/profiles/{slug}").json()
    body = {k: v for k, v in current.items() if k not in ("slug", "search")}
    body["headline"] = headline
    response = call_api(context.app, "PUT", f"/api/v1/profiles/{slug}", body)
    assert response.status_code == 200, response.text


@when("eu listo os perfis")
def step_list(context):
    context.response = call_api(context.app, "GET", "/api/v1/profiles")


@then("a resposta deve ter status {status:d}")
def step_status(context, status):
    assert context.response.status_code == status, context.response.text


@then("a lista de perfis deve ser vazia")
def step_empty(context):
    assert context.response.json() == []


@then('os slugs listados devem ser "{slugs}"')
def step_slugs(context, slugs):
    listed = [p["slug"] for p in context.response.json()]
    assert listed == [s.strip() for s in slugs.split(",")], listed


@then('o perfil "{slug}" listado deve ter a headline "{headline}"')
def step_headline(context, slug, headline):
    profile = next(p for p in context.response.json() if p["slug"] == slug)
    assert profile["headline"] == headline, profile
