import json

from anthropic import AsyncAnthropic

from src.domain.entity.job import Job
from src.domain.entity.job_facts import JobFacts
from src.domain.service.fact_extractor import FactExtractor
from src.infra.llm.prompts import EXTRACTION_SYSTEM_PROMPT
from src.infra.llm.schemas import JobFactsPayload


class AnthropicExtractor(FactExtractor):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model

    async def extract(self, job: Job) -> JobFacts:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=EXTRACTION_SYSTEM_PROMPT
            + "\n\nResponda SOMENTE com JSON válido neste schema:\n"
            + json.dumps(JobFactsPayload.model_json_schema(), ensure_ascii=False),
            messages=[{"role": "user", "content": job.to_evaluation_text()}],
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.strip("`").removeprefix("json").strip()
        payload = JobFactsPayload.model_validate_json(text)
        return payload.to_domain()
