import logging

from arq.connections import RedisSettings

from app.config import get_settings
from app.db.models import Run
from app.db.session import SessionLocal

log = logging.getLogger(__name__)


async def execute_run(ctx: dict, run_id: str) -> None:
    """Placeholder until the LangGraph swarm lands (milestone 2)."""
    async with SessionLocal() as db:
        run = await db.get(Run, run_id)
        if run is None or run.status == "cancelled":
            return
        run.status = "running"
        await db.commit()
        log.info("run %s picked up: %s", run_id, run.question)
        run.status = "completed"
        run.phase = "done"
        run.report_md = "_The research swarm is not implemented yet._"
        await db.commit()


class WorkerSettings:
    functions = [execute_run]
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
    max_jobs = 4
    job_timeout = 60 * 60 * 6
