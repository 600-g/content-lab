"""YouTube 전용 — yt-dlp로 자막/메타 추출 (영상 다운로드 X, 텍스트만)."""
from __future__ import annotations

import json
import logging
import subprocess
from .router import ScrapeResult

logger = logging.getLogger(__name__)


def _run_yt_dlp(url: str) -> dict:
    """yt-dlp --dump-json --skip-download. 자막은 따로 가져옴."""
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--skip-download",
        "--no-warnings",
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {proc.stderr[:500]}")
    return json.loads(proc.stdout)


def _fetch_subtitles(url: str) -> str:
    """자동 자막 다운로드 (ko 우선 → en 폴백). srt 형식 텍스트만 반환."""
    import tempfile
    import os
    import glob

    with tempfile.TemporaryDirectory() as tmp:
        out_template = os.path.join(tmp, "%(id)s.%(ext)s")
        cmd = [
            "yt-dlp",
            "--write-auto-subs",
            "--write-subs",
            "--sub-langs", "ko,en",
            "--skip-download",
            "--sub-format", "vtt",
            "--no-warnings",
            "-o", out_template,
            url,
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
        vtt_files = sorted(glob.glob(os.path.join(tmp, "*.vtt")))
        if not vtt_files:
            return ""
        # ko 파일 우선
        chosen = next((f for f in vtt_files if ".ko." in f), vtt_files[0])
        with open(chosen, encoding="utf-8") as f:
            raw = f.read()
        return _vtt_to_text(raw)


def _vtt_to_text(vtt: str) -> str:
    """vtt 형식에서 타임스탬프/번호 제거 후 텍스트만 추출."""
    lines = []
    for line in vtt.splitlines():
        s = line.strip()
        if not s or s.startswith("WEBVTT") or "-->" in s:
            continue
        if s.isdigit():  # cue 번호
            continue
        if s.startswith("NOTE"):
            continue
        lines.append(s)
    # 중복 제거 (자동 자막 특성)
    deduped = []
    for ln in lines:
        if not deduped or deduped[-1] != ln:
            deduped.append(ln)
    return "\n".join(deduped)


def scrape(url: str) -> ScrapeResult:
    meta_raw = _run_yt_dlp(url)
    subtitles = _fetch_subtitles(url)

    title = meta_raw.get("title", "")
    description = meta_raw.get("description", "") or ""
    text_parts = []
    if description:
        text_parts.append(f"[설명]\n{description}")
    if subtitles:
        text_parts.append(f"[자막]\n{subtitles}")
    text = "\n\n".join(text_parts) if text_parts else title

    meta = {
        "channel": meta_raw.get("channel", ""),
        "duration": meta_raw.get("duration", 0),
        "view_count": meta_raw.get("view_count", 0),
        "upload_date": meta_raw.get("upload_date", ""),
        "thumbnail": meta_raw.get("thumbnail", ""),
        "tags": meta_raw.get("tags", []) or [],
    }

    return ScrapeResult(
        url=url,
        source_type="youtube",
        title=title,
        text=text,
        meta=meta,
    )
