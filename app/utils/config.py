from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "production"
    log_level: str = "INFO"
    secret_key: str = "change-me"
    base_data_dir: str = "/data"
    database_path: str = "/data/app.db"
    redis_url: str = "redis://redis:6379/0"
    telegram_bot_token: str = ""
    telegram_admin_id: str | None = None
    max_video_minutes: int = 30
    max_telegram_mb: int = 45
    output_retention_days: int = 7
    failed_bundle_keep: int = 5
    whisper_model: str = "small"
    global_concurrency: int = 2
    user_concurrency: int = 1
    job_poll_seconds: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
