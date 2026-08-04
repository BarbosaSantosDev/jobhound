from pydantic import BaseModel, Field

from src.domain.entity.job_facts import JobFacts
from src.domain.value_object.seniority import Seniority
from src.domain.value_object.work_mode import WorkMode


class JobFactsPayload(BaseModel):
    """Schema de structured output — o LLM é forçado a responder neste formato."""

    mentioned_stack: list[str] = Field(
        default_factory=list,
        description=(
            "Todas as linguagens, frameworks e tecnologias citadas como requisito "
            "obrigatório da vaga (ex: Python, Java, FastAPI, Spring, React, Node)."
        ),
    )
    seniority: Seniority = Field(description="Senioridade declarada na vaga")
    work_mode: WorkMode = Field(description="Modo de trabalho da vaga")
    location_city: str = Field(default="", description="Cidade da vaga, se houver")
    salary_range: str = Field(default="", description="Faixa salarial, se informada")

    def to_domain(self) -> JobFacts:
        return JobFacts(
            mentioned_stack=self.mentioned_stack,
            seniority=self.seniority,
            work_mode=self.work_mode,
            location_city=self.location_city,
            salary_range=self.salary_range,
        )
