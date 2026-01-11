import json
import os
import subprocess
from pathlib import Path
from uuid import uuid4

from app.core.highlight_finder import analyze_video, propose_candidates, score_candidates, select_top, explain_segment
from app.core.transcribe import transcribe_clip
from app.core.ffmpeg_utils import cut_clip, burn_captions, ensure_vertical
from app.utils.config import settings
from app.utils.logging import setup_logging
from app.db.database import get_job

logger = setup_logging("pipeline")


class VideoPipeline:
    def __init__(self, job_id: str, base_dir: Path, job: dict) -> None:
        self.job_id = job_id
        self.base_dir = base_dir
        self.job = job
        self.options = json.loads(job.get("options_json") or "{}")
        self.output_dir = base_dir / "outputs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.intermediate = base_dir / "intermediate"
        self.intermediate.mkdir(parents=True, exist_ok=True)

    def run(self, progress_cb) -> dict:
        url = self.options.get("url")
        self._check_cancel()
        progress_cb("download", 10)
        source_path = self._download(url)
        self._check_cancel()
        progress_cb("analyze", 20)
        analysis = analyze_video(source_path, self.intermediate)
        self._check_cancel()
        candidates = propose_candidates(analysis)
        scored = score_candidates(candidates, analysis)
        selected = select_top(scored, analysis, count=self.options.get("clip_count", 2))
        selections = []
        progress_cb("cut", 40)
        for index, segment in enumerate(selected, start=1):
            self._check_cancel()
            clip_id = f"clip_{index}_{uuid4().hex[:6]}"
            clip_path = self.output_dir / f"{clip_id}.mp4"
            cut_clip(source_path, clip_path, segment["start"], segment["end"])
            if self.options.get("smart_crop", True):
                ensure_vertical(clip_path, clip_path)
            progress_cb("transcribe", 55 + index * 5)
            srt_path, vtt_path = transcribe_clip(clip_path, self.output_dir, language=self.options.get("language", "auto"))
            if self.options.get("captions", True):
                styled_path = self.output_dir / f"{clip_id}_captioned.mp4"
                burn_captions(clip_path, srt_path, styled_path, style=self.options.get("caption_style", "boxed"))
                final_path = styled_path
            else:
                final_path = clip_path
            selections.append({
                "clip_id": clip_id,
                "start": segment["start"],
                "end": segment["end"],
                "reasons": explain_segment(segment),
                "video": str(final_path),
                "srt": str(srt_path),
                "vtt": str(vtt_path),
            })
        progress_cb("render", 90)
        analysis_path = self.output_dir / "analysis.json"
        analysis_path.write_text(json.dumps(analysis, indent=2), encoding="utf-8")
        candidates_path = self.output_dir / "candidates.json"
        candidates_path.write_text(json.dumps(candidates, indent=2), encoding="utf-8")
        selected_path = self.output_dir / "selected.json"
        selected_path.write_text(json.dumps(selected, indent=2), encoding="utf-8")
        progress_cb("send", 95)
        return {
            "job_id": self.job_id,
            "source": str(source_path),
            "clips": selections,
            "analysis": str(analysis_path),
            "candidates": str(candidates_path),
            "selected": str(selected_path),
        }

    def _download(self, url: str) -> Path:
        if not url or "youtube.com" not in url and "youtu.be" not in url:
            raise ValueError("Invalid YouTube URL")
        output_dir = Path(settings.base_data_dir) / "downloads"
        output_dir.mkdir(parents=True, exist_ok=True)
        video_id = subprocess.check_output(["yt-dlp", "--print", "id", url]).decode().strip()
        cached = output_dir / f"{video_id}.mp4"
        if cached.exists():
            return cached
        output_template = output_dir / "%(id)s.%(ext)s"
        cmd = [
            "yt-dlp",
            "--no-playlist",
            "-f",
            "mp4",
            "-o",
            str(output_template),
            url,
        ]
        subprocess.run(cmd, check=True)
        download_files = sorted(output_dir.glob("*.mp4"), key=os.path.getmtime, reverse=True)
        if not download_files:
            raise RuntimeError("Download failed")
        return download_files[0]

    def _check_cancel(self) -> None:
        job = get_job(self.job_id)
        if job and job.get("cancel_flag") == 1:
            raise RuntimeError("Job canceled")
