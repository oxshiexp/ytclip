from dataclasses import dataclass
from pathlib import Path
import json
import numpy as np

HOOK_KEYWORDS = ["wow", "amazing", "gila", "serius", "ternyata", "percaya"]
BOILERPLATE = ["subscribe", "like", "terima kasih", "halo teman"]


@dataclass
class Candidate:
    start: float
    end: float
    score: float
    reasons: list[str]


def analyze_video(source_path: Path, work_dir: Path) -> dict:
    audio_path = work_dir / "audio.raw"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-f",
        "s16le",
        str(audio_path),
    ]
    import subprocess

    subprocess.run(cmd, check=True)
    raw = audio_path.read_bytes()
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    if samples.size == 0:
        raise RuntimeError("No audio samples")
    samples /= 32768.0
    window_size = int(16000 * 0.5)
    rms = [
        float(np.sqrt(np.mean(samples[i : i + window_size] ** 2)))
        for i in range(0, len(samples), window_size)
    ]
    peaks = [float(np.max(np.abs(samples[i : i + window_size]))) for i in range(0, len(samples), window_size)]
    timeline = {
        "rms": rms,
        "peaks": peaks,
        "duration": len(samples) / 16000,
    }
    (work_dir / "analysis.json").write_text(json.dumps(timeline, indent=2), encoding="utf-8")
    return timeline


def propose_candidates(analysis: dict) -> list[dict]:
    duration = analysis["duration"]
    min_len, max_len, target = 12, 45, 25
    candidates = []
    step = 5
    for start in np.arange(0, max(duration - min_len, 0), step):
        end = min(start + target, duration)
        if end - start < min_len:
            continue
        candidates.append({"start": float(start), "end": float(end), "reasons": []})
    return candidates


def score_candidates(candidates: list[dict], analysis: dict) -> list[dict]:
    rms = np.array(analysis["rms"])
    scores = []
    for cand in candidates:
        start_idx = int(cand["start"] / 0.5)
        end_idx = int(cand["end"] / 0.5)
        window = rms[start_idx:end_idx]
        if window.size == 0:
            continue
        speech_density = float(np.mean(window > np.mean(rms)))
        excitement = float(np.max(window))
        score = speech_density * 0.5 + excitement * 0.5
        cand["score"] = score
        cand["reasons"] = [
            f"speech_density:{speech_density:.2f}",
            f"excitement:{excitement:.2f}",
        ]
        scores.append(cand)
    return sorted(scores, key=lambda x: x["score"], reverse=True)


def select_top(scored: list[dict], analysis: dict, count: int = 2) -> list[dict]:
    selected = []
    for cand in scored:
        if len(selected) >= count:
            break
        if any(_overlap(cand, existing) > 0.15 for existing in selected):
            continue
        if any(abs(cand["start"] - existing["end"]) < 20 for existing in selected):
            continue
        selected.append(cand)
    return selected


def explain_segment(segment: dict) -> list[str]:
    reasons = segment.get("reasons", [])
    if not reasons:
        return ["Selected for balanced speech and energy."]
    return reasons[:3]


def _overlap(a: dict, b: dict) -> float:
    start = max(a["start"], b["start"])
    end = min(a["end"], b["end"])
    if end <= start:
        return 0.0
    overlap = end - start
    return overlap / max(a["end"] - a["start"], 1)
