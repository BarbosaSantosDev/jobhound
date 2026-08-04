from functools import lru_cache

from fastapi import Depends

from src.app.query import GetPipelineStatus, ListTopMatches
from src.app.service import PipelineStatusTracker
from src.app.usecase import GetProfile, RegisterProfile, UpdateProfile
from src.app.workflow import PipelineWorkflow
from src.container import (
    build_get_profile,
    build_pipeline,
    build_pipeline_status_tracker,
    build_register_profile,
    build_top_matches,
    build_update_profile,
)


async def get_pipeline() -> PipelineWorkflow:
    # Sem lru_cache de propósito: monta o grafo fresco a cada run,
    # garantindo que edições no perfil valem no próximo pipeline.
    return await build_pipeline()


def get_pipeline_status_tracker() -> PipelineStatusTracker:
    # Sem lru_cache aqui: o singleton já é garantido em container.py. Mantendo
    # esta função "rasa" (só repassa), tanto o POST /pipeline/run (que usa o
    # tracker direto) quanto o GET /pipeline/status (via GetPipelineStatus
    # abaixo, encadeado com Depends) resolvem pro mesmo objeto — inclusive em
    # testes com app.dependency_overrides, que só precisam sobrescrever esta
    # função uma vez.
    return build_pipeline_status_tracker()


def get_pipeline_status_usecase(
    tracker: PipelineStatusTracker = Depends(get_pipeline_status_tracker),
) -> GetPipelineStatus:
    return GetPipelineStatus(tracker)


@lru_cache
def get_top_matches() -> ListTopMatches:
    return build_top_matches()


@lru_cache
def get_profile_usecase() -> GetProfile:
    return build_get_profile()


@lru_cache
def get_update_profile_usecase() -> UpdateProfile:
    return build_update_profile()


@lru_cache
def get_register_profile_usecase() -> RegisterProfile:
    return build_register_profile()
