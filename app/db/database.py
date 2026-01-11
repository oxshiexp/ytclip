import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from app.utils.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    status TEXT,
    progress_step TEXT,
    progress_pct REAL,
    options_json TEXT,
    result_json TEXT,
    error TEXT,
    cancel_flag INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS user_settings (
    user_id TEXT PRIMARY KEY,
    settings_json TEXT,
    updated_at TEXT
);
"""


def init_db() -> None:
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(settings.database_path) as conn:
        conn.executescript(SCHEMA)


@contextmanager
def db_conn():
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def create_job(job_id: str, user_id: str, options: dict) -> None:
    now = datetime.utcnow().isoformat()
    with db_conn() as conn:
        conn.execute(
            """
            INSERT INTO jobs (id, user_id, status, progress_step, progress_pct, options_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (job_id, user_id, "queued", "queued", 0.0, json.dumps(options), now, now),
        )


def update_job(job_id: str, **fields) -> None:
    fields["updated_at"] = datetime.utcnow().isoformat()
    assignments = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [job_id]
    with db_conn() as conn:
        conn.execute(f"UPDATE jobs SET {assignments} WHERE id = ?", values)


def get_job(job_id: str) -> dict | None:
    with db_conn() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return dict(row) if row else None


def list_jobs(user_id: str, limit: int = 10) -> list[dict]:
    with db_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def count_active_jobs(user_id: str | None = None) -> int:
    with db_conn() as conn:
        if user_id:
            row = conn.execute(
                "SELECT COUNT(*) as count FROM jobs WHERE user_id = ? AND status IN ('queued','running')",
                (user_id,),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COUNT(*) as count FROM jobs WHERE status IN ('queued','running')"
            ).fetchone()
    return int(row["count"]) if row else 0


def set_cancel(job_id: str, value: bool = True) -> None:
    update_job(job_id, cancel_flag=1 if value else 0)


def get_user_settings(user_id: str) -> dict:
    with db_conn() as conn:
        row = conn.execute(
            "SELECT settings_json FROM user_settings WHERE user_id = ?", (user_id,)
        ).fetchone()
    if not row:
        return {}
    return json.loads(row["settings_json"] or "{}")


def set_user_settings(user_id: str, settings_dict: dict) -> None:
    now = datetime.utcnow().isoformat()
    payload = json.dumps(settings_dict)
    with db_conn() as conn:
        conn.execute(
            """
            INSERT INTO user_settings (user_id, settings_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET settings_json = excluded.settings_json, updated_at = excluded.updated_at
            """,
            (user_id, payload, now),
        )
