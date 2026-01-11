from pathlib import Path
from faster_whisper import WhisperModel
import srt

from app.utils.config import settings


def transcribe_clip(clip_path: Path, output_dir: Path, language: str = "auto") -> tuple[Path, Path]:
    model = WhisperModel(settings.whisper_model)
    segments, _ = model.transcribe(str(clip_path), language=None if language == "auto" else language)
    subs = []
    for i, segment in enumerate(segments, start=1):
        subs.append(
            srt.Subtitle(
                index=i,
                start=srt.timedelta(seconds=segment.start),
                end=srt.timedelta(seconds=segment.end),
                content=segment.text.strip(),
            )
        )
    srt_path = output_dir / f"{clip_path.stem}.srt"
    vtt_path = output_dir / f"{clip_path.stem}.vtt"
    srt_path.write_text(srt.compose(subs), encoding="utf-8")
    vtt_path.write_text(srt.compose(subs).replace("00:", "00."), encoding="utf-8")
    return srt_path, vtt_path
