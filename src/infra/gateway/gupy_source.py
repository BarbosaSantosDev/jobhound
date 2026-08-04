import httpx

from src.domain.entity.job import Job

from ..gateway import HttpJobSource

GUPY_SEARCH_URL = "https://employability-portal.gupy.io/api/v1/jobs"


class GupySource(HttpJobSource):
    def __init__(self, search_terms: list[str], limit_per_term: int = 20):
        self._search_terms = search_terms
        self._limit = limit_per_term

    @property
    def name(self) -> str:
        return "gupy"

    def _timeout(self) -> httpx.Timeout:
        return httpx.Timeout(60, connect=10)

    async def _collect(self, client: httpx.AsyncClient) -> list[dict]:
        items: list[dict] = []
        for term in self._search_terms:
            response = await client.get(
                GUPY_SEARCH_URL,
                params={"jobName": term, "limit": self._limit, "offset": 0},
            )
            response.raise_for_status()
            items.extend(response.json().get("data", []))
        return items

    def _to_job(self, raw: dict) -> Job:
        url = raw.get("jobUrl", "")
        return Job(
            id=self._make_id(str(raw.get("id", url))),
            title=raw.get("name", ""),
            company=raw.get("careerPageName", ""),
            location=f"{raw.get('city', '')} {raw.get('state', '')}".strip(),
            description=raw.get("description", "") or raw.get("name", ""),
            url=url,
            source=self.name,
        )