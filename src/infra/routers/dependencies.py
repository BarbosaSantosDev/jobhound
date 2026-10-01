from functools import lru_cache

from fastapi import Depends, Query

from src.app.query import GetLastRun, GetPipelineStatus, ListProfiles, ListTopMatches
from src.app.service import PipelineStatusTracker
from src.app.usecase import ChangeJobStage, GetProfile, RegisterProfile, UpdateProfile
from src.app.workflow import PipelineWorkflow
from src.container import (
    build_change_job_stage,
    build_get_last_run,
    build_get_profile,
    build_list_profiles,
    build_pipeline,
    build_pipeline_status_tracker,
    build_register_profile,
    build_top_matches,
    build_update_profile,
)


async def get_pipeline(
    profile: str | None = Query(default=None, description="slug do perfil a farejar"),
) -> PipelineWorkflow:
    # Sem lru_cache de propósito: monta o grafo fresco a cada run,
    # garantindo que edições no perfil valem no próximo pipeline.
    return await build_pipeline(profile)


def get_pipeline_status_tracker() -> PipelineStatusTracker:
    # Sem lru_cache aqui: o singleton já é garantido em container.py. Mantendo
    # esta função "rasa" (só repassa), tanto o POST /pipeline/run (que usa o
    # tracker direto) quanto o GET /pipeline/status (via GetPipelineStatus
    # abaixo, encadeado com Depends) resolvem pro mesmo objeto — inclusive em
    # testes com app.dependency_overrides, que só precisam sobrescrever esta
    # função uma vez.
    return build_pipeline_status_tracker()


@lru_cache
def get_last_run() -> GetLastRun:
    return build_get_last_run()


def get_pipeline_status_usecase(
    tracker: PipelineStatusTracker = Depends(get_pipeline_status_tracker),
    last_run: GetLastRun = Depends(get_last_run),
) -> GetPipelineStatus:
    return GetPipelineStatus(tracker, last_run)


@lru_cache
def get_top_matches() -> ListTopMatches:
    return build_top_matches()


@lru_cache
def get_change_job_stage() -> ChangeJobStage:
    return build_change_job_stage()


@lru_cache
def get_profile_usecase() -> GetProfile:
    return build_get_profile()


@lru_cache
def get_list_profiles() -> ListProfiles:
    return build_list_profiles()


@lru_cache
def get_update_profile_usecase() -> UpdateProfile:
    return build_update_profile()


@lru_cache
def get_register_profile_usecase() -> RegisterProfile:
    return build_register_profile()
