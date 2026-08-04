from __future__ import annotations

import re
import unicodedata

from pydantic import BaseModel, Field


def _slugify(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.strip().lower()).strip("-")
    return slug or "profile"


class SearchPreferences(BaseModel):
    """O que buscar em cada fonte. Derivado da stack do perfil — não é escolha do usuário."""

    gupy_terms: list[str] = Field(default_factory=list)
    nerdin_platforms: list[str] = Field(default_factory=list)
    remoteok_tags: list[str] = Field(default_factory=list)

    @staticmethod
    def derive(primary_stack: list[str], secondary_stack: list[str]) -> SearchPreferences:
        return SearchPreferences(
            gupy_terms=[s.lower() for s in primary_stack],
            nerdin_platforms=list(primary_stack),
            remoteok_tags=[s.lower() for s in [*primary_stack, *secondary_stack]],
        )


class Profile(BaseModel):
    id: int | None = None
    slug: str
    name: str
    headline: str
    seniority: str
    primary_stack: list[str]
    secondary_stack: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    accepts_remote: bool = True
    summary: str
    search: SearchPreferences = Field(default_factory=SearchPreferences)

    @staticmethod
    def create(
        name: str,
        headline: str,
        seniority: str,
        primary_stack: list[str],
        secondary_stack: list[str] | None = None,
        preferred_locations: list[str] | None = None,
        accepts_remote: bool = True,
        summary: str = "",
    ) -> Profile:
        secondary_stack = secondary_stack or []
        return Profile(
            id=None,
            slug=_slugify(name),
            name=name,
            headline=headline,
            seniority=seniority,
            primary_stack=primary_stack,
            secondary_stack=secondary_stack,
            preferred_locations=preferred_locations or [],
            accepts_remote=accepts_remote,
            summary=summary,
            search=SearchPreferences.derive(primary_stack, secondary_stack),
        )

    @classmethod
    def from_dict(cls, data: dict) -> Profile:
        search_data = data.pop("search", {}) or {}
        return cls(
            **data,
            search=SearchPreferences(
                gupy_terms=search_data.get("gupy_terms", []),
                nerdin_platforms=search_data.get("nerdin_platforms", []),
                remoteok_tags=search_data.get("remoteok_tags", []),
            ),
        )

    def to_prompt_text(self) -> str:
        return (
            f"Nome: {self.name}\n"
            f"Headline: {self.headline}\n"
            f"Senioridade: {self.seniority}\n"
            f"Stack principal: {', '.join(self.primary_stack)}\n"
            f"Stack secundária: {', '.join(self.secondary_stack)}\n"
            f"Localizações preferidas: {', '.join(self.preferred_locations)}\n"
            f"Aceita remoto: {'sim' if self.accepts_remote else 'não'}\n\n"
            f"Resumo:\n{self.summary}"
        )
