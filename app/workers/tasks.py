from rq import Queue
from redis import Redis

from app.utils.config import settings

redis_conn = Redis.from_url(settings.redis_url)
queue = Queue("jobs", connection=redis_conn)


def enqueue_job(job_id: str) -> None:
    queue.enqueue("app.workers.worker.run_job", job_id, job_id=job_id)
