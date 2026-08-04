import asyncio
import re

import httpx
from bs4 import BeautifulSoup

from src.domain.entity.job import Job
from src.infra.gateway.base import DEFAULT_HEADERS, HttpJobSource

NERDIN_BASE = "https://www.nerdin.com.br"
JOB_LINK_RE = re.compile(r"/vaga_emprego/vaga-.+-(\d+)\.php")


class NerdinSource(HttpJobSource):
    """Scraping HTML do Nerdin (nerdin.com.br). Lista filtrada por plataforma
    e busca a descrição na página de detalhe de cada vaga."""

    def __init__(
        self,
        platforms: list[str],
        max_pages: int = 2,
        max_details: int = 25,
    ):
        self._platforms = platforms
        self._max_pages = max_pages
        self._max_details = max_details

    @property
    def name(self) -> str:
        return "nerdin"

    # ---------- hooks do template ----------

    def _headers(self) -> dict[str, str]:
        return {
            **DEFAULT_HEADERS,
            "Accept": "text/html,application/xhtml+xml",
        }

    # ---------- passos do template ----------

    async def _collect(self, client: httpx.AsyncClient) -> list[dict]:
        stubs = await self._fetch_listings(client)
        return await self._enrich_with_details(client, stubs[: self._max_details])

    def _to_job(self, raw: dict) -> Job:
        company, location = self._split_meta(raw["meta"])
        return Job(
            id=self._make_id(raw["nerdin_id"]),
            title=raw["title"],
            company=company,
            location=location,
            description=raw["description"] or raw["meta"],
            url=raw["url"],
            source=self.name,
        )

    # ---------- coleta (privados, como antes) ----------

    async def _fetch_listings(self, client: httpx.AsyncClient) -> list[dict]:
        stubs: list[dict] = []
        seen_ids: set[str] = set()
        for platform in self._platforms:
            for page in range(1, self._max_pages + 1):
                response = await client.get(
                    f"{NERDIN_BASE}/vagas.php",
                    params={"Plataforma": platform, "pagina": page},
                )
                response.raise_for_status()
                page_stubs = self._parse_listing(response.text)
                if not page_stubs:
                    break  # acabaram as páginas desse filtro
                for stub in page_stubs:
                    if stub["nerdin_id"] not in seen_ids:
                        seen_ids.add(stub["nerdin_id"])
                        stubs.append(stub)
        return stubs

    async def _enrich_with_details(
        self, client: httpx.AsyncClient, stubs: list[dict]
    ) -> list[dict]:
        for stub in stubs:
            try:
                response = await client.get(stub["url"])
                response.raise_for_status()
                stub["description"] = self._parse_description(response.text)
            except httpx.HTTPError:
                stub["description"] = ""
            await asyncio.sleep(0.5)  # educação com o servidor deles
        return stubs

    # ---------- parsing (idênticos aos seus) ----------

    def _parse_listing(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        stubs: list[dict] = []
        for link in soup.find_all("a", href=JOB_LINK_RE):
            match = JOB_LINK_RE.search(link["href"])
            card = link.find_parent(
                lambda tag: tag.name in ("article", "div") and tag.find("h3")
            )
            if not card or not match:
                continue
            title = card.find("h3").get_text(" ", strip=True)
            title = re.sub(r"\s*Nova\s*$", "", title)
            lines = [
                t for t in card.stripped_strings
                if t not in (title, "Quero essa Vaga", "Nova") and not t.startswith("#")
            ]
            url = link["href"]
            if url.startswith("/"):
                url = NERDIN_BASE + url
            stubs.append(
                {
                    "nerdin_id": match.group(1),
                    "title": title,
                    "url": url,
                    "meta": " | ".join(lines[:6]),
                }
            )
        return stubs

    def _parse_description(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        main = soup.find("main") or soup.body
        if not main:
            return ""
        text = main.get_text("\n", strip=True)
        start = text.find("Descrição")
        end = text.find("Vagas Relacionadas")
        if start != -1:
            text = text[start : end if end != -1 else None]
        return text[:4000]

    def _split_meta(self, meta: str) -> tuple[str, str]:
        parts = [p.strip() for p in meta.split("|")]
        company = ""
        location = ""
        for part in parts:
            if re.search(r"•\s*[A-Z]{2}$", part) or part == "Home Office":
                location = part.replace("•", "").strip()
            elif not re.search(
                r"CLT|PJ|Freelancer|Pleno|Junior|Híbrido|Home Office|"
                r"Presencial|Salário|R\$|Há \d|Ontem|Cód\.",
                part,
            ):
                company = company or part
        return company, location