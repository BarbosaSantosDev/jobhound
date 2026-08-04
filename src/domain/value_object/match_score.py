from pydantic import BaseModel, ConfigDict, field_validator


class MatchScore(BaseModel):
    model_config = ConfigDict(frozen=True)
    value: int

    @field_validator("value")
    @classmethod
    def _validate_range(cls, value: int) -> int:
        if not 0 <= value <= 100:
            raise ValueError(f"MatchScore deve estar entre 0 e 100, recebido: {value}")
        return value

    @property
    def is_high(self) -> bool:
        return self.value >= 70

    @property
    def is_gray_zone(self) -> bool:
        return 50 <= self.value < 70
