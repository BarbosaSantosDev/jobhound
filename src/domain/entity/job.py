import hashlib
import html
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _plain_text(raw: str) -> str:
    """Descrições chegam com HTML das fontes: vira texto corrido de uma linha."""
    without_tags = re.sub(r"<[^>]+>", " ", raw)
    visible = re.sub(r"[\u200b-\u200d\ufeff]", "", html.unescape(without_tags))
    return re.sub(r"\s+", " ", visible).strip()


@dataclass
class Job:
    id: str
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    fetched_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def fingerprint(self) -> str:
        raw = f"{_normalize(self.title)}|{_normalize(self.company)}|{_normalize(self.location)}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def excerpt(self, max_chars: int = 600) -> str | None:
        """Trecho legível da descrição para o dashboard. Corta na última palavra
        inteira que cabe e marca o corte com reticências. None se não houver texto."""
        text = _plain_text(self.description)
        if not text:
            return None
        if len(text) <= max_chars:
            return text
        cut = text[:max_chars].rsplit(" ", 1)[0].rstrip(" ,.;:-")
        return f"{cut}…"

    def to_evaluation_text(self) -> str:
        return (
            f"Título: {self.title}\n"
            f"Empresa: {self.company}\n"
            f"Localização: {self.location}\n"
            f"Fonte: {self.source}\n\n"
            f"Descrição:\n{self.description}"
        )
