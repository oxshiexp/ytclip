import subprocess
from pathlib import Path


def cut_clip(source: Path, output: Path, start: float, end: float) -> None:
    duration = max(end - start, 0.1)
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        str(start),
        "-i",
        str(source),
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(cmd, check=True)


def ensure_vertical(source: Path, output: Path) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-vf",
        "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(cmd, check=True)


def burn_captions(source: Path, srt_path: Path, output: Path, style: str) -> None:
    style_map = {
        "boxed": "Fontsize=24,PrimaryColour=&HFFFFFF&,BorderStyle=4,BackColour=&H80000000&,Outline=1",
        "minimal": "Fontsize=24,PrimaryColour=&HFFFFFF&,Outline=2",
        "tiktok": "Fontsize=26,PrimaryColour=&HFFFFFF&,BorderStyle=4,BackColour=&H60000000&,Outline=1",
    }
    style_value = style_map.get(style, style_map["boxed"])
    vf = f"subtitles={srt_path}:force_style='{style_value}'"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(cmd, check=True)


def compress_for_telegram(source: Path, output: Path) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-vf",
        "scale=720:1280:force_original_aspect_ratio=decrease",
        "-b:v",
        "1500k",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(cmd, check=True)
