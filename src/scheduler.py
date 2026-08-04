import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.container import build_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def job() -> None:
    pipeline = await build_pipeline()
    report = await pipeline.execute()
    logger.info(
        "Pipeline: %d novas, %d matches, %d revisão, %d erros",
        report.fetched, report.matched, report.manual_review, report.errors,
    )


def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(job, "interval", hours=3, next_run_time=None)
    scheduler.start()
    logger.info("Scheduler iniciado (a cada 3h). Ctrl+C para sair.")
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
