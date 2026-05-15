"""SNS 전용 — Instagram / TikTok 캡션·해시태그·메타.

yt-dlp가 IG/TikTok 일부 메타 추출 지원. 영상 다운로드는 X, 메타데이터만.
로그인 벽 만나면 ScrapeResult.ok=False로 반환 → Playwright로 폴백.
"""
from __future__ import annotations

import json
import logging
import subprocess

from .router import ScrapeResult

logger = logging.getLogger(__name__)


def _run_yt_dlp(url: str) -> dict | None:
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--skip-download",
        "--no-warnings",
        "--no-playlist",
        url,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45, check=False)
    except subprocess.TimeoutExpired:
        logger.warning("yt-dlp timeout: %s", url)
        return None
    if proc.returncode != 0:
        logger.warning("yt-dlp failed (%s): %s", proc.returncode, proc.stderr[:200])
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def scrape_instagram(url: str) -> ScrapeResult:
    data = _run_yt_dlp(url)
    if not data:
        return ScrapeResult(
            url=url, source_type="instagram", title="", text="",
            meta={}, ok=False, error="yt-dlp로 IG 메타 추출 실패 — Playwright로 폴백",
        )

    caption = data.get("description") or data.get("title") or ""
    uploader = data.get("uploader") or data.get("uploader_id") or ""
    text = f"[Instagram] @{uploader}\n\n{caption}"

    meta = {
        "uploader": uploader,
        "like_count": data.get("like_count", 0),
        "comment_count": data.get("comment_count", 0),
        "upload_date": data.get("upload_date", ""),
        "duration": data.get("duration", 0),
        "thumbnail": data.get("thumbnail", ""),
    }

    return ScrapeResult(
        url=url,
        source_type="instagram",
        title=f"IG @{uploader}",
        text=text,
        meta=meta,
    )


def scrape_tiktok(url: str) -> ScrapeResult:
    data = _run_yt_dlp(url)
    if not data:
        return ScrapeResult(
            url=url, source_type="tiktok", title="", text="",
            meta={}, ok=False, error="yt-dlp로 TikTok 메타 추출 실패 — Playwright로 폴백",
        )

    caption = data.get("description") or data.get("title") or ""
    uploader = data.get("uploader") or data.get("creator") or ""
    hashtags = []
    # TikTok 캡션에서 #해시태그 파싱
    for word in caption.split():
        if word.startswith("#"):
            hashtags.append(word)

    text = f"[TikTok] @{uploader}\n\n{caption}"
    if hashtags:
        text += f"\n\n[Tags] {' '.join(hashtags)}"

    meta = {
        "uploader": uploader,
        "view_count": data.get("view_count", 0),
        "like_count": data.get("like_count", 0),
        "comment_count": data.get("comment_count", 0),
        "duration": data.get("duration", 0),
        "hashtags": hashtags,
    }

    return ScrapeResult(
        url=url,
        source_type="tiktok",
        title=f"TikTok @{uploader}",
        text=text,
        meta=meta,
    )


def scrape_twitter(url: str) -> ScrapeResult:
    """X/Twitter — 로그인 벽 강함. yt-dlp 시도 후 실패 시 명시."""
    data = _run_yt_dlp(url)
    if data:
        caption = data.get("description") or ""
        uploader = data.get("uploader") or ""
        text = f"[X/Twitter] @{uploader}\n\n{caption}"
        return ScrapeResult(
            url=url, source_type="twitter", title=f"X @{uploader}",
            text=text,
            meta={"uploader": uploader, "duration": data.get("duration", 0)},
        )
    return ScrapeResult(
        url=url, source_type="twitter", title="", text="",
        meta={}, ok=False,
        error="X(Twitter)는 로그인 벽 강함. Claude Code MCP(firecrawl)나 수동 텍스트 입력 권장",
    )
