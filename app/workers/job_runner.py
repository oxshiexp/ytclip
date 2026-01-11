import json
import shutil
from datetime import datetime
from pathlib import Path

from app.core.video_pipeline import VideoPipeline
from app.db.database import get_job, update_job
from app.utils.config import settings
from app.utils.logging import setup_logging
from app.utils.telegram import notify_progress, send_results

logger = setup_logging("job_runner")


class JobRunner:
    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self.job = get_job(job_id)
        self.base_dir = Path(settings.base_data_dir) / "jobs" / job_id
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _update(self, step: str, pct: float) -> None:
        update_job(self.job_id, status="running", progress_step=step, progress_pct=pct)
        notify_progress(self.job_id, step, pct)

    def execute(self) -> None:
        if not self.job:
            logger.error("Job not found", extra={"job_id": self.job_id})
            return
        try:
            self._update("download", 5)
            pipeline = VideoPipeline(self.job_id, self.base_dir, self.job)
            result = pipeline.run(self._update)
            update_job(
                self.job_id,
                status="succeeded",
                progress_step="completed",
                progress_pct=100,
                result_json=json.dumps(result),
            )
            send_results(self.job_id, result)
        except Exception as exc:
            logger.exception("Job failed", extra={"job_id": self.job_id})
            status = "canceled" if "canceled" in str(exc).lower() else "failed"
            update_job(
                self.job_id,
                status=status,
                progress_step=status,
                progress_pct=100,
                error=str(exc),
            )
        finally:
            self._cleanup_intermediate()

    def _cleanup_intermediate(self) -> None:
        intermediates = self.base_dir / "intermediate"
        if intermediates.exists():
            shutil.rmtree(intermediates, ignore_errors=True)
        (self.base_dir / "cleanup.json").write_text(
            json.dumps({"last_cleanup": datetime.utcnow().isoformat()}), encoding="utf-8"
        )
