"""범용 웹 스크래퍼 — Playwright로 JS 렌더링 + trafilatura로 본문 추출.

trafilatura: 광고/네비/푸터 자동 제거. 본문 정확도 비교 우위.
실패 시 BeautifulSoup 폴백.
"""
from __future__ import annotations

import logging
import random
from .router import ScrapeResult

logger = logging.getLogger(__name__)

# UA 회전 풀 — 봇 차단 회피
UA_POOL = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]


def _bs4_extract(html: str) -> tuple[str, str]:
    """BeautifulSoup 폴백 — title + body 텍스트."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "iframe", "nav", "footer", "header", "aside"]):
        tag.decompose()

    title = ""
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()
    elif soup.title and soup.title.string:
        title = soup.title.string.strip()

    main = soup.find("main") or soup.find("article") or soup.body or soup
    text = main.get_text(separator="\n", strip=True)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return title, "\n".join(lines)


def _trafilatura_extract(html: str, url: str) -> tuple[str, str]:
    """trafilatura 본문 추출 — 광고/네비 자동 제거. 실패 시 ('','') 반환."""
    try:
        import trafilatura
    except ImportError:
        return "", ""

    try:
        result = trafilatura.extract(
            html,
            url=url,
            include_comments=False,
            include_tables=True,
            favor_precision=False,
            no_fallback=False,
            output_format="markdown",
        )
        meta = trafilatura.extract_metadata(html, default_url=url)
        title = (meta.title if meta else "") or ""
        return title, result or ""
    except Exception as e:  # noqa: BLE001
        logger.warning("trafilatura failed: %s", e)
        return "", ""


def scrape(url: str, source_type: str = "web") -> ScrapeResult:
    """Playwright headless로 페이지 렌더 → HTML → trafilatura/bs4 본문 추출."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError(
            "playwright not installed. run: pip install playwright && playwright install chromium"
        )

    ua = random.choice(UA_POOL)
    is_mobile = "iPhone" in ua

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        try:
            context = browser.new_context(
                user_agent=ua,
                viewport={"width": 390, "height": 844} if is_mobile else {"width": 1280, "height": 800},
                locale="ko-KR",
                timezone_id="Asia/Seoul",
            )
            page = context.new_page()
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
            except Exception as e:  # noqa: BLE001
                logger.warning("goto failed (%s) → networkidle 재시도", e)
                page.goto(url, wait_until="networkidle", timeout=45000)

            # JS 렌더링 사이트 대기
            if source_type == "notion":
                # Notion SPA — 본문 블록 셀렉터 등장까지 우선 대기, 실패 시 고정 9초.
                try:
                    page.wait_for_selector(
                        "[data-block-id], .notion-page-content",
                        timeout=9000,
                    )
                    page.wait_for_timeout(1500)
                except Exception:  # noqa: BLE001
                    page.wait_for_timeout(9000)
            elif source_type in ("instagram", "tiktok", "twitter"):
                page.wait_for_timeout(4500)
            else:
                page.wait_for_timeout(1500)

            # 무한 스크롤 사이트 대응 — 1회 스크롤
            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(800)
            except Exception:  # noqa: BLE001
                pass

            html = page.content()
        finally:
            browser.close()

    # 본문 추출 — trafilatura 우선
    title, text = _trafilatura_extract(html, url)
    if not text.strip():
        logger.info("trafilatura 빈 결과 → bs4 폴백")
        bs_title, bs_text = _bs4_extract(html)
        title = title or bs_title
        text = bs_text

    # Notion 비공개 페이지 자동 진단 — generic landing HTML 의 마커가 잡히면 즉시 차단.
    if source_type == "notion" and _is_notion_private_landing(html, text):
        logger.info("Notion 비공개 페이지 감지: %s", url)
        return ScrapeResult(
            url=url,
            source_type=source_type,
            title=title,
            text="",
            meta={
                "html_length": len(html),
                "text_length": 0,
                "ua": "mobile" if is_mobile else "desktop",
            },
            ok=False,
            skip_reason="notion_private",
            skip_message_ko=(
                "노션 페이지가 비공개 상태라 본문을 가져올 수 없습니다. "
                "노션에서 페이지 우상단 [Share] → [Publish to web] 토글을 ON 해주세요. "
                "(페이지를 이동했다면 share 설정이 부모 페이지를 따라 풀렸을 수 있어요)"
            ),
        )

    return ScrapeResult(
        url=url,
        source_type=source_type,
        title=title,
        text=text,
        meta={
            "html_length": len(html),
            "text_length": len(text),
            "ua": "mobile" if is_mobile else "desktop",
        },
    )


_NOTION_LANDING_MARKERS = (
    "Notion | Where teams and agents work together",
    "A collaborative AI workspace, built on your company context",
    "Build and orchestrate agents right alongside",
)


def _is_notion_private_landing(html: str, extracted_text: str) -> bool:
    """노션 비공개 페이지에 떨어지면 generic 마케팅 랜딩 HTML 이 받힌다.

    판별 기준 (전부 만족):
    - HTML 안에 위 _NOTION_LANDING_MARKERS 중 하나 이상 포함 (Notion 워크스페이스 카피)
    - extracted_text 가 매우 짧음 (<500자) — 진짜 페이지 본문이 없음
    """
    if not html:
        return False
    if len(extracted_text or "") >= 500:
        return False
    for marker in _NOTION_LANDING_MARKERS:
        if marker in html:
            return True
    return False
