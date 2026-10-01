from enum import StrEnum


class JobStage(StrEnum):
    """Etapa da vaga na triagem do candidato. Toda vaga avaliada nasce NEW."""

    NEW = "new"
    SAVED = "saved"
    APPLIED = "applied"
    DISCARDED = "discarded"
