from datetime import datetime, timedelta
from pathlib import Path
import shutil

from app.utils.config import settings


def cleanup_outputs() -> list[str]:
    removed = []
    base = Path(settings.base_data_dir) / "jobs"
    if not base.exists():
        return removed
    threshold = datetime.utcnow() - timedelta(days=settings.output_retention_days)
    for job_dir in base.iterdir():
        if not job_dir.is_dir():
            continue
        outputs = job_dir / "outputs"
        if outputs.exists():
            mtime = datetime.utcfromtimestamp(outputs.stat().st_mtime)
            if mtime < threshold:
                shutil.rmtree(outputs, ignore_errors=True)
                removed.append(str(outputs))
    return removed


def delete_outputs(job_id: str) -> bool:
    base = Path(settings.base_data_dir) / "jobs" / job_id / "outputs"
    if base.exists():
        shutil.rmtree(base, ignore_errors=True)
        return True
    return False
