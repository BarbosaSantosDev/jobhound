from src.app.query.get_last_run import GetLastRun
from src.app.service import PipelineStatus, PipelineStatusTracker


class GetPipelineStatus:
    """Estado ao vivo (tracker, em memória) + último faro registrado (banco)."""

    def __init__(self, tracker: PipelineStatusTracker, last_run: GetLastRun):
        self._tracker = tracker
        self._last_run = last_run

    async def execute(self, profile_slug: str | None = None) -> PipelineStatus:
        status = await self._tracker.snapshot()
        return status.model_copy(update={"last_run": await self._last_run.execute(profile_slug)})
