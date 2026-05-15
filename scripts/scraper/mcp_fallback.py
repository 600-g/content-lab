"""MCP 폴백 — Playwright도 실패하면 검색 결과로 우회.

실제 구현: Claude Code 환경에서 exa-search/firecrawl MCP 호출은
스크립트 단독 실행이 아닌 Claude Code 도구 호출로만 가능하다.
이 모듈은 그 신호를 stdout에 남기고, ScrapeResult.error에 안내를 담아
이후 Claude Code 세션에서 사람이 MCP로 재시도하도록 트리거한다.

본 모듈을 직접 실행하는 케이스: requests + 최소한의 HTML 파싱으로 정적 페이지만 처리.
"""
from __future__ import annotations

import logging
import requests
from .router import ScrapeResult
from .web import _extract_text

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
}


def scrape(url: str, source_type: str = "web") -> ScrapeResult:
    """가장 가벼운 requests + BeautifulSoup 폴백."""
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=20)
        resp.raise_for_status()
        title, text = _extract_text(resp.text)
        if not text.strip():
            return ScrapeResult(
                url=url,
                source_type=source_type,
                title=title,
                text="",
                meta={},
                ok=False,
                error="empty body — Claude Code에서 MCP(exa/firecrawl)로 재시도 권장",
            )
        return ScrapeResult(
            url=url,
            source_type=source_type,
            title=title,
            text=text,
            meta={"fallback": "requests"},
        )
    except Exception as e:  # noqa: BLE001
        return ScrapeResult(
            url=url,
            source_type=source_type,
            title="",
            text="",
            meta={},
            ok=False,
            error=f"requests 폴백 실패: {e} — Claude Code에서 MCP(exa/firecrawl)로 재시도",
        )
