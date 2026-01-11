import os
from pathlib import Path
import httpx

from app.utils.config import settings
from app.db.database import get_job
from app.utils.logging import setup_logging
from app.core.ffmpeg_utils import compress_for_telegram

logger = setup_logging("telegram")


def notify_progress(job_id: str, step: str, pct: float) -> None:
    job = get_job(job_id)
    if not job:
        return
    options = job.get("options_json")
    if not options:
        return
    import json

    opts = json.loads(options)
    telegram_meta = opts.get("telegram")
    if not telegram_meta:
        return
    text = f"Progress {pct:.0f}% - {step}"
    _edit_message(telegram_meta["chat_id"], telegram_meta["message_id"], text)


def send_results(job_id: str, result: dict) -> None:
    job = get_job(job_id)
    if not job:
        return
    import json

    opts = json.loads(job.get("options_json") or "{}")
    telegram_meta = opts.get("telegram")
    if not telegram_meta:
        return
    chat_id = telegram_meta["chat_id"]
    for clip in result.get("clips", []):
        _send_file(chat_id, clip["video"], caption=f"Clip {clip['clip_id']}")
        _send_file(chat_id, clip["srt"])
        _send_file(chat_id, clip["vtt"])
    summary = f"Job {job_id} selesai. {len(result.get('clips', []))} clip." 
    _send_message(chat_id, summary)


def _send_message(chat_id: int, text: str) -> None:
    _request("sendMessage", {"chat_id": chat_id, "text": text})


def _edit_message(chat_id: int, message_id: int, text: str) -> None:
    _request("editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text})


def _send_file(chat_id: int, path: str, caption: str | None = None) -> None:
    file_path = Path(path)
    if not file_path.exists():
        return
    size_mb = file_path.stat().st_size / (1024 * 1024)
    if size_mb > settings.max_telegram_mb:
        compressed = file_path.with_name(f"{file_path.stem}_compressed{file_path.suffix}")
        compress_for_telegram(file_path, compressed)
        file_path = compressed
    with file_path.open("rb") as f:
        files = {"document": f}
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        _request("sendDocument", data, files=files)


def _request(method: str, data: dict, files: dict | None = None) -> None:
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/{method}"
    with httpx.Client(timeout=60) as client:
        client.post(url, data=data, files=files)
