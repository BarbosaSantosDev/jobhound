from src.app.service import PipelineStatus, PipelineStatusTracker


class GetPipelineStatus:
    def __init__(self, tracker: PipelineStatusTracker):
        self._tracker = tracker

    async def execute(self) -> PipelineStatus:
        return await self._tracker.snapshot()
