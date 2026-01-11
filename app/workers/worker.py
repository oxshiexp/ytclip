import time
from rq import Worker
from redis import Redis

from app.utils.config import settings
from app.utils.logging import setup_logging
from app.db.database import init_db

logger = setup_logging("worker")


def run_job(job_id: str) -> None:
    from app.workers.job_runner import JobRunner

    runner = JobRunner(job_id)
    runner.execute()


def main() -> None:
    init_db()
    redis_conn = Redis.from_url(settings.redis_url)
    worker = Worker(["jobs"], connection=redis_conn)
    logger.info("Worker started")
    while True:
        worker.work(burst=True)
        time.sleep(1)


if __name__ == "__main__":
    main()
