from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ReasonKind(StrEnum):
    PRO = "pro"  # conta a favor da vaga
    CON = "con"  # conta contra
    INFO = "info"  # neutro: falta informação ou é ponto de atenção


class Reason(BaseModel):
    """Um motivo do score, com a direção em que ele pesou."""

    model_config = ConfigDict(frozen=True)
    kind: ReasonKind
    text: str

    @classmethod
    def pro(cls, text: str) -> "Reason":
        return cls(kind=ReasonKind.PRO, text=text)

    @classmethod
    def con(cls, text: str) -> "Reason":
        return cls(kind=ReasonKind.CON, text=text)

    @classmethod
    def info(cls, text: str) -> "Reason":
        return cls(kind=ReasonKind.INFO, text=text)
