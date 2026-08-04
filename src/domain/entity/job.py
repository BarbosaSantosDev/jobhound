import hashlib
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


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

    def to_evaluation_text(self) -> str:
        return (
            f"Título: {self.title}\n"
            f"Empresa: {self.company}\n"
            f"Localização: {self.location}\n"
            f"Fonte: {self.source}\n\n"
            f"Descrição:\n{self.description}"
        )
