# YTClip - YouTube to Shorts Bot

Production-ready system for converting YouTube videos into vertical 9:16 Shorts with subtitles, delivered via a Telegram bot. Includes a FastAPI API, Redis queue, RQ worker pipeline, and SQLite for storage.

## Features
- Telegram bot (button-based UX) with job history, cancel, and settings defaults.
- FastAPI API for job creation and status.
- RQ worker pipeline for heavy processing.
- YouTube download via `yt-dlp` (cached by video ID).
- Automatic highlight selection and explainability outputs.
- Subtitle generation via `faster-whisper` and optional burn-in.
- Vertical 9:16 output with simple smart crop fallback.
- Cleanup policy for outputs.

## Quick Start (Ubuntu VPS)
```bash
sudo apt-get update && sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER
# logout/login or run: newgrp docker
cp .env.example .env
# edit .env with TELEGRAM_BOT_TOKEN and desired settings
sudo docker compose up -d
```

## Services
- `api`: FastAPI HTTP API
- `worker`: background processing
- `bot`: Telegram polling bot
- `redis`: job queue backend

## Environment Variables
See `.env.example` for full list. Key settings:
- `TELEGRAM_BOT_TOKEN`: Telegram bot token
- `BASE_DATA_DIR`: data folder (default `/data`)
- `DATABASE_PATH`: SQLite DB file (default `/data/app.db`)
- `MAX_VIDEO_MINUTES`: maximum input video length
- `MAX_TELEGRAM_MB`: max size for Telegram uploads

## API
- `POST /jobs` -> `{url, options}`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/results`
- `GET /health`

## Telegram UX
Commands:
- `/start`, `/help`, `/status <job_id>`, `/cancel <job_id>`, `/history`, `/settings`, `/presets`

Main Menu buttons:
- 🎬 Buat Shorts Baru
- ⚙️ Pengaturan Default
- 📦 Preset
- 🧾 Riwayat Job
- ❓ Bantuan

## Cleanup Policy
- Intermediates are deleted after success.
- Outputs retained for `OUTPUT_RETENTION_DAYS` (default 7).

## Troubleshooting
- Ensure `TELEGRAM_BOT_TOKEN` is set.
- Check logs in `/data/logs/app.log`.
- If downloads fail, confirm network access and valid YouTube URL.

## Testing
```bash
pytest
```
