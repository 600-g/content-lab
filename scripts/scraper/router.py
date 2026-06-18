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

# 본문 너무 짧으면 폴백 트리거. 80자는 JS-heavy 페이지(netlify SPA / Google Drive view /
# IG 캡션) 가 placeholder HTML 만 잡혀도 통과시켜서 결과적으로 LLM 입력이 부실해진다.
# 500자 임계로 올려 의미 있는 본문 확보 후에야 LLM 단계 진입.
MIN_TEXT_LEN = int(__import__("os").environ.get("SCRAPER_MIN_TEXT_LEN", "500"))


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
    skip_reason: Optional[str] = None  # 의도적 사전 차단 (ig_login_wall 등). 잡은 실패 아닌 'skipped' 처리.
    skip_message_ko: Optional[str] = None  # 사용자용 한글 안내 메시지.

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "source_type": self.source_type,
            "title": self.title,
            "text": self.text[:200000],  # Gemini 입력 한도 고려
            "meta": self.meta,
            "ok": self.ok,
            "error": self.error,
            "skip_reason": self.skip_reason,
            "skip_message_ko": self.skip_message_ko,
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
    # notion.site / notion.so : 공개 share URL.
    # app.notion.com / www.notion.com : 워크스페이스 멤버 전용 (로그인 필수, 본문 스크랩 절대 불가).
    if (
        "notion.site" in domain
        or "notion.so" in domain
        or "notion.com" in domain
    ):
        return "notion"
    if "github.com" in domain:
        return "github"
    if "twitter.com" in domain or "x.com" in domain:
        return "twitter"
    return "web"


def _retry(func: Callable[[], "ScrapeResult"], attempts: int = 2, label: str = "") -> Optional["ScrapeResult"]:
    """exponential backoff 재시도. skip_reason 이 잡히면 즉시 반환 (재시도 무의미)."""
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            r = func()
            # 사전 차단(skip_reason) 은 재시도해도 결과 동일 → 즉시 반환.
            if getattr(r, "skip_reason", None):
                logger.info("%s skip_reason=%s → 재시도 스킵", label, r.skip_reason)
                return r
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


# config 의 IG 차단 토글 — 채팅이 켜고 끌 수 있다.
def _ig_block_enabled() -> bool:
    try:
        from scripts import config_store
        return bool(config_store.get("ig_block.enabled", True))
    except Exception:  # noqa: BLE001
        return True  # config 로딩 실패해도 안전 디폴트는 차단.


def _notion_auth_guard(url: str) -> Optional[ScrapeResult]:
    """app.notion.com / www.notion.com 워크스페이스 페이지 사전 차단.

    이 도메인의 페이지는 노션 계정 로그인 + 워크스페이스 멤버 권한이 있어야만 본문 접근 가능.
    Playwright 로 받혀도 generic landing HTML 만 떨어짐 → quota·시간 낭비 + 잡 실패.
    공개 share URL (`<slug>.notion.site/...`) 로 다시 받아오라고 안내.
    """
    lower = url.lower()
    if "app.notion.com" not in lower and "www.notion.com" not in lower:
        return None
    return ScrapeResult(
        url=url,
        source_type="notion",
        title="",
        text="",
        meta={},
        ok=False,
        skip_reason="notion_workspace_only",
        skip_message_ko=(
            "이 링크는 노션 워크스페이스 멤버만 볼 수 있는 페이지(app.notion.com)라 본문을 가져올 수 없어요. "
            "노션에서 페이지 우상단 [Share] → [Publish to web] 토글 ON → "
            "그때 표시되는 공개 URL(<워크스페이스>.notion.site/...)로 다시 등록해 주세요."
        ),
    )


def _ig_guard(url: str) -> Optional[ScrapeResult]:
    """IG /p/ 피드 포스트 사전 차단. 차단 시 안내 메시지 담은 ScrapeResult 반환.

    Meta 의 로그인 벽 때문에 /p/ 는 본문 추출이 불가능하다 (~117자만 잡힘).
    Gemini 가 빈약한 입력으로 JSON 헛 생성 후 잡 죽음을 막기 위해 사전 차단.
    /reel/ 은 yt-dlp 가 종종 캡션을 뜯어오므로 통과시키되, 실패하면 같은 메시지로 종료.
    """
    if not _ig_block_enabled():
        return None
    lower = url.lower()
    if "instagram.com/p/" not in lower:
        return None
    return ScrapeResult(
        url=url,
        source_type="instagram",
        title="",
        text="",
        meta={},
        ok=False,
        skip_reason="ig_login_wall",
        skip_message_ko=(
            "이 링크는 인스타그램 피드 포스트라 로그인 없이는 본문을 못 가져옵니다. "
            "캡션을 직접 붙여넣거나 스크린샷 → 텍스트로 변환해 등록해 주세요."
        ),
    )


def scrape(url: str) -> ScrapeResult:
    """URL을 적절한 스크래퍼로 처리. 실패 시 fallback 체인 + 재시도.

    체인:
    1. 전용 스크래퍼 (youtube/github/instagram/tiktok/twitter)
    2. 범용 Playwright + trafilatura (JS 렌더링 포함, 2회 재시도)
    3. requests 폴백 (정적 페이지만)
    """
    source = detect_source(url)
    logger.info("scraping url=%s source=%s", url, source)

    # IG 피드 포스트 사전 차단 — 로그인 벽 때문에 본문 추출 불가능.
    if source == "instagram":
        blocked = _ig_guard(url)
        if blocked is not None:
            logger.info("IG 피드 사전 차단: %s", url)
            return blocked

    # app.notion.com / www.notion.com 사전 차단 — 워크스페이스 멤버 전용 페이지.
    if source == "notion":
        blocked = _notion_auth_guard(url)
        if blocked is not None:
            logger.info("Notion 워크스페이스 페이지 사전 차단: %s", url)
            return blocked

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
