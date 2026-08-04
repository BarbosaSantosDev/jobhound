"""Composition root: monta o grafo de dependências conforme a configuração."""

import os
from functools import lru_cache

from dotenv import load_dotenv

from src.app.query import ListTopMatches
from src.app.repository import ProfileRepository
from src.app.service import PipelineStatusTracker
from src.app.usecase import (
    EvaluateJobMatch,
    FetchNewJobs,
    GetProfile,
    RegisterProfile,
    UpdateProfile,
)
from src.app.workflow import PipelineWorkflow
from src.domain.entity.profile import Profile
from src.domain.service import FactExtractor, JobSource, ScoreJob
from src.infra.database import get_session_factory
from src.infra.gateway import GupySource, NerdinSource, RemoteOKSource, TelegramNotifier
from src.infra.llm import LangChainExtractor
from src.infra.repository import JobRepositorySQLAlchemy, ProfileRepositorySQLAlchemy

load_dotenv()

ollama_base_url = os.getenv("OLLAMA_BASE_URL")
ollama_model = os.getenv("OLLAMA_MODEL")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
matcher_provider = os.getenv("MATCHER_PROVIDER", "ollama")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")


def build_profile_repo() -> ProfileRepository:
    return ProfileRepositorySQLAlchemy(get_session_factory())


async def load_profile() -> Profile | None:
    return await build_profile_repo().load()


def build_get_profile() -> GetProfile:
    return GetProfile(build_profile_repo())


def build_update_profile() -> UpdateProfile:
    return UpdateProfile(build_profile_repo())


def build_register_profile() -> RegisterProfile:
    return RegisterProfile(build_profile_repo())


def build_extractor() -> FactExtractor:
    if matcher_provider == "anthropic":
        # Import local: "anthropic" é dependência opcional ([anthropic] no
        # pyproject.toml) — não deve ser exigida de quem só usa Ollama.
        from src.infra.llm.anthropic_extractor import AnthropicExtractor

        return AnthropicExtractor(api_key=anthropic_api_key, model=anthropic_model)

    return LangChainExtractor(
        base_url=ollama_base_url,
        model=ollama_model,
    )


def build_sources(profile: Profile) -> list[JobSource]:
    sources: list[JobSource] = []
    if profile.search.gupy_terms:
        sources.append(GupySource(profile.search.gupy_terms))
    if profile.search.nerdin_platforms:
        sources.append(NerdinSource(platforms=profile.search.nerdin_platforms))
    if profile.search.remoteok_tags:
        sources.append(RemoteOKSource(profile.search.remoteok_tags))
    return sources


@lru_cache
def build_pipeline_status_tracker() -> PipelineStatusTracker:
    """Singleton em memória, válido para a vida do processo: única fonte de
    verdade sobre "tem pipeline rodando agora", compartilhada entre o 409 de
    POST /pipeline/run e o GET /pipeline/status (ver src/infra/routers/pipeline.py)."""
    return PipelineStatusTracker()


async def build_pipeline() -> PipelineWorkflow:
    job_repo = JobRepositorySQLAlchemy(get_session_factory())

    profile = await load_profile()
    if profile is None:
        raise RuntimeError(
            "Nenhum perfil cadastrado ainda — registre um via POST /api/v1/profiles "
            "antes de rodar o pipeline."
        )

    status = build_pipeline_status_tracker()
    return PipelineWorkflow(
        fetch_jobs=FetchNewJobs(build_sources(profile), job_repo),
        evaluate=EvaluateJobMatch(build_extractor(), ScoreJob(), profile, status=status),
        job_repo=job_repo,
        notifier=TelegramNotifier(telegram_bot_token, telegram_chat_id),
        status=status,
    )


def build_top_matches() -> ListTopMatches:
    return ListTopMatches(JobRepositorySQLAlchemy(get_session_factory()))
