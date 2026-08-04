from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from src.domain.entity import Job, JobFacts
from src.domain.service.fact_extractor import FactExtractor
from src.infra.llm.prompts import EXTRACTION_SYSTEM_PROMPT
from src.infra.llm.schemas import JobFactsPayload


class LangChainExtractor(FactExtractor):
    """FactExtractor via LangChain + Ollama, orquestrado com LCEL
    (prompt | llm com structured output)."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen2.5:3b",
        timeout: float = 120.0,
    ):
        llm = ChatOllama(
            base_url=base_url,
            model=model,
            temperature=0.1,
            timeout=timeout,
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", EXTRACTION_SYSTEM_PROMPT),
                ("human", "{job_text}"),
            ]
        )
        self._chain = prompt | llm.with_structured_output(JobFactsPayload)

    async def extract(self, job: Job) -> JobFacts:
        payload: JobFactsPayload = await self._chain.ainvoke(
            {"job_text": job.to_evaluation_text()}
        )
        return payload.to_domain()