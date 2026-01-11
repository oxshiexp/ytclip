from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4

from app.db.database import create_job, get_job, init_db, count_active_jobs
from app.utils.config import settings
from app.workers.tasks import enqueue_job
from app.utils.logging import setup_logging
from redis import Redis

logger = setup_logging("api")
app = FastAPI()


class JobRequest(BaseModel):
    url: str
    options: dict


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    redis_ok = False
    try:
        redis_ok = Redis.from_url(settings.redis_url).ping()
    except Exception:
        redis_ok = False
    return {"status": "ok", "redis": bool(redis_ok)}


@app.post("/jobs")
def create_job_endpoint(payload: JobRequest) -> dict:
    if count_active_jobs() >= settings.global_concurrency:
        raise HTTPException(status_code=429, detail="Global concurrency limit reached")
    job_id = uuid4().hex
    options = payload.options | {"url": payload.url}
    create_job(job_id, user_id="api", options=options)
    enqueue_job(job_id)
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job_endpoint(job_id: str) -> dict:
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/jobs/{job_id}/results")
def get_results(job_id: str) -> dict:
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "results": job.get("result_json")}
