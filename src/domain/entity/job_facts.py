from pydantic import BaseModel, Field

from src.domain.value_object import Seniority, WorkMode


class JobFacts(BaseModel):
    """Fatos objetivos extraídos da vaga pelo LLM.

    O LLM extrai fatos; o domínio pontua (função pura e determinística).
    """

    mentioned_stack: list[str] = Field(default_factory=list)
    seniority: Seniority
    work_mode: WorkMode
    location_city: str = ""
    salary_range: str = ""
