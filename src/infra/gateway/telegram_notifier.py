import httpx

from src.domain.entity.job import Job
from src.domain.entity.match_result import MatchResult
from src.domain.service.notifier import Notifier


class TelegramNotifier(Notifier):
    def __init__(self, bot_token: str, chat_id: str):
        self._url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self._chat_id = chat_id

    async def send_matches(self, matches: list[tuple[Job, MatchResult]]) -> None:
        async with httpx.AsyncClient(timeout=30) as client:
            for job, result in matches:
                await client.post(
                    self._url,
                    json={
                        "chat_id": self._chat_id,
                        "text": self._format(job, result),
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    },
                )

    def _format(self, job: Job, result: MatchResult) -> str:
        tag = "🎯" if result.is_worth_applying else "🟡 revisar manualmente"
        reasons = "\n".join(f"• {r}" for r in result.reasons)
        flags = (
            "\n⚠️ " + ", ".join(result.red_flags) if result.red_flags else ""
        )
        return (
            f"{tag} <b>{job.title}</b> — {job.company}\n"
            f"Score: <b>{result.score.value}</b> | {job.location} | {job.source}\n\n"
            f"{reasons}{flags}\n\n{job.url}"
        )
