"""URL을 보고 적절한 스크래퍼로 라우팅.

순서: 도메인 → 전용 스크래퍼 (youtube/github/social) → 범용 Playwright → requests 폴백
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Callable, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

MIN_TEXT_LEN = 80  # 본문 너무 짧으면 폴백 트리거


@dataclass
class ScrapeResult:
    """스크래핑 결과 단일 컨테이너."""

    url: str
    source_type: str  # youtube / tiktok / instagram / notion / github / web
    title: str
    text: str  # 본문(자막/캡션/HTML→텍스트)
    meta: dict  # 추가 메타 (author, duration, thumbnail 등)
    ok: bool = True
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "source_type": self.source_type,
            "title": self.title,
            "text": self.text[:200000],  # Gemini 입력 한도 고려
            "meta": self.meta,
            "ok": self.ok,
            "error": self.error,
        }


def detect_source(url: str) -> str:
    """URL의 출처 유형 판별."""
    try:
        domain = urlparse(url).netloc.lower()
    except Exception:
        return "web"

    if "youtube.com" in domain or "youtu.be" in domain:
        return "youtube"
    if "tiktok.com" in domain:
        return "tiktok"
    if "instagram.com" in domain:
        return "instagram"
    if "notion.site" in domain or "notion.so" in domain:
        return "notion"
    if "github.com" in domain:
        return "github"
    if "twitter.com" in domain or "x.com" in domain:
        return "twitter"
    return "web"


def _retry(func: Callable[[], "ScrapeResult"], attempts: int = 2, label: str = "") -> Optional["ScrapeResult"]:
    """exponential backoff 재시도."""
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            r = func()
            if r.ok and len(r.text or "") >= MIN_TEXT_LEN:
                return r
            logger.warning("%s attempt %d: 빈/짧은 결과 (len=%d)", label, i + 1, len(r.text or ""))
        except Exception as e:  # noqa: BLE001
            last_err = e
            logger.warning("%s attempt %d 실패: %s", label, i + 1, e)
        if i < attempts - 1:
            time.sleep(1.5 ** i)
    if last_err:
        logger.warning("%s 모든 시도 실패: %s", label, last_err)
    return None


def scrape(url: str) -> ScrapeResult:
    """URL을 적절한 스크래퍼로 처리. 실패 시 fallback 체인 + 재시도.

    체인:
    1. 전용 스크래퍼 (youtube/github/instagram/tiktok/twitter)
    2. 범용 Playwright + trafilatura (JS 렌더링 포함, 2회 재시도)
    3. requests 폴백 (정적 페이지만)
    """
    source = detect_source(url)
    logger.info("scraping url=%s source=%s", url, source)

    # 1단계 — 전용 스크래퍼
    try:
        if source == "youtube":
            from . import youtube
            return youtube.scrape(url)
        if source == "github":
            from . import github as gh
            return gh.scrape(url)
        if source == "instagram":
            from . import social
            r = social.scrape_instagram(url)
            if r.ok and r.text.strip():
                return r
            logger.info("IG yt-dlp 실패 → Playwright 폴백")
        if source == "tiktok":
            from . import social
            r = social.scrape_tiktok(url)
            if r.ok and r.text.strip():
                return r
            logger.info("TikTok yt-dlp 실패 → Playwright 폴백")
        if source == "twitter":
            from . import social
            r = social.scrape_twitter(url)
            if r.ok and r.text.strip():
                return r
            logger.info("X yt-dlp 실패 → Playwright 폴백 (성공률 낮음)")
    except Exception as e:  # noqa: BLE001
        logger.warning("specialized scraper failed for %s: %s", source, e)

    # 2단계 — 범용 Playwright (2회 재시도, trafilatura+UA 회전 내장)
    from . import web
    result = _retry(lambda: web.scrape(url, source_type=source), attempts=2, label=f"playwright[{source}]")
    if result:
        return result

    # 3단계 — requests 폴백 (정적 페이지)
    try:
        from . import mcp_fallback
        return mcp_fallback.scrape(url, source_type=source)
    except Exception as e:  # noqa: BLE001
        logger.error("all scrapers failed for %s: %s", url, e)
        return ScrapeResult(
            url=url,
            source_type=source,
            title="",
            text="",
            meta={},
            ok=False,
            error=f"모든 스크래퍼 실패: {e}",
        )
