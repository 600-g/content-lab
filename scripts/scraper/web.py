"""범용 웹 스크래퍼 — Playwright로 JS 렌더링 + trafilatura로 본문 추출.

trafilatura: 광고/네비/푸터 자동 제거. 본문 정확도 비교 우위.
실패 시 BeautifulSoup 폴백.
"""
from __future__ import annotations

import logging
import random
from .router import MIN_TEXT_LEN, ScrapeResult

logger = logging.getLogger(__name__)

# 이 길이 미만이면 trafilatura 결과를 믿지 않고 bs4 / 렌더 innerText 와 비교해 가장 긴 것을 쓴다.
# router 의 폴백 트리거와 같은 기준이어야 '추출은 짧은데 재시도만 반복' 하는 낭비가 안 생긴다.
MIN_GOOD_TEXT_LEN = MIN_TEXT_LEN

# UA 회전 풀 — 봇 차단 회피
UA_POOL = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

# notion.site 는 Chrome UA 로 붙으면 goto 가 domcontentloaded/load 둘 다 60s 타임아웃 나고
# page.content() 가 빈 문자열을 준다 (2026-08-16 4종 UA 전수 계측 — WebKit 2종만 정상 렌더).
# random.choice 면 50% 확률로 못 읽는 UA 를 잡으므로 notion 경로는 WebKit 풀만 쓴다.
NOTION_UA_POOL = [ua for ua in UA_POOL if "Chrome/" not in ua]


def _pick_ua(source_type: str, attempt: int | None = None) -> str:
    """UA 선택. attempt 가 주어지면 순환 — 재시도가 같은 UA 로 반복되지 않게."""
    pool = NOTION_UA_POOL if source_type == "notion" else UA_POOL
    if not pool:
        pool = UA_POOL
    if attempt is None:
        return random.choice(pool)
    return pool[attempt % len(pool)]


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


def scrape(url: str, source_type: str = "web", attempt: int | None = None) -> ScrapeResult:
    """Playwright headless로 페이지 렌더 → HTML → trafilatura/bs4 본문 추출.

    attempt: 재시도 회차 (0-base). 주어지면 UA 를 회차별로 순환시킨다.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError(
            "playwright not installed. run: pip install playwright && playwright install chromium"
        )

    ua = _pick_ua(source_type, attempt)
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
            # 3단계 goto 폴백: domcontentloaded (60s) → load (60s) → commit (45s).
            # networkidle 은 텔레메트리 XHR 이 끊이지 않는 Notion/Instagram/TikTok SPA 에서
            # 절대 idle 상태가 안 됨 → 무조건 timeout → 시간만 낭비 → 폴백 체인에서 제거.
            # 마지막 commit 은 첫 응답 헤더만 받으면 리턴 → 그 다음 wait_for_selector 가
            # 실제 컨텐츠 대기 (notion selector 로직이 아래에 이미 있음).
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:  # noqa: BLE001
                logger.warning("goto domcontentloaded 실패 (%s) → load 재시도", e)
                try:
                    page.goto(url, wait_until="load", timeout=60000)
                except Exception as e2:  # noqa: BLE001
                    logger.warning("goto load 실패 (%s) → commit 최후 폴백", e2)
                    page.goto(url, wait_until="commit", timeout=45000)

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
            # 렌더된 DOM 실측 — 비공개 판별과 본문 폴백의 단일 근거.
            # HTML 문자열 마커는 공개 페이지에도 그대로 들어있어 판별력이 없다 (아래 주석 참고).
            try:
                block_count = page.eval_on_selector_all("[data-block-id]", "els => els.length")
            except Exception:  # noqa: BLE001
                block_count = -1
            try:
                body_text = (page.eval_on_selector("body", "el => el.innerText") or "").strip()
            except Exception:  # noqa: BLE001
                body_text = ""
        finally:
            browser.close()

    # Notion 접근 불가 (비공개/삭제/이동) — 렌더 결과로만 판정. 재시도해도 동일하므로 즉시 종료.
    if source_type == "notion" and _is_notion_access_denied(block_count, body_text):
        logger.info("Notion 접근 불가 페이지 감지: %s", url)
        return ScrapeResult(
            url=url,
            source_type=source_type,
            title="",
            text="",
            meta={"html_length": len(html), "text_length": 0, "blocks": block_count,
                  "ua": "mobile" if is_mobile else "desktop"},
            ok=False,
            skip_reason="notion_private",
            skip_message_ko=(
                "노션 페이지에 접근할 수 없습니다 (비공개이거나 삭제·이동된 페이지). "
                "노션에서 페이지 우상단 [Share] → [Publish to web] 토글을 ON 해주세요. "
                "(페이지를 이동했다면 share 설정이 부모 페이지를 따라 풀렸을 수 있어요)"
            ),
        )

    # 본문 추출 — trafilatura 우선, 짧으면 bs4 / 렌더 innerText 중 가장 긴 것 채택.
    # (Notion SPA 는 trafilatura 가 본문 일부만 뜯는 경우가 있다 — 실사례: 렌더 1166자 중 311자만
    #  추출돼 MIN_TEXT_LEN 미달로 실패 처리. '빈 결과일 때만 폴백' 이면 이 케이스를 못 건진다.)
    title, text = _trafilatura_extract(html, url)
    if len(text.strip()) < MIN_GOOD_TEXT_LEN:
        bs_title, bs_text = _bs4_extract(html)
        title = title or bs_title
        best = max((text or "", bs_text or "", body_text or ""), key=lambda s: len(s.strip()))
        if len(best.strip()) > len(text.strip()):
            logger.info(
                "본문 폴백 채택: trafilatura %d자 → %d자", len(text.strip()), len(best.strip())
            )
            text = best

    return ScrapeResult(
        url=url,
        source_type=source_type,
        title=title,
        text=text,
        meta={
            "html_length": len(html),
            "text_length": len(text),
            "blocks": block_count,
            "ua": "mobile" if is_mobile else "desktop",
        },
    )


# 접근 불가 노션 페이지가 실제로 렌더하는 안내 문구 (ko/en).
_NOTION_NOACCESS_MARKERS = (
    "페이지 찾지 못함",
    "사용 권한이 없거나",
    "Page not found",
    "don't have permission",
    "deleted or moved",
)


def _is_notion_access_denied(block_count: int, body_text: str) -> bool:
    """노션 페이지가 진짜 접근 불가(비공개/삭제/이동)인지 렌더 결과로 판정.

    판별 기준 (전부 만족):
    - 렌더된 DOM 에 [data-block-id] 블록이 0개 — 본문이 아예 없음
    - body innerText 에 노션의 '페이지 찾지 못함' 안내 문구가 있음

    구버전은 HTML 문자열에서 Notion 마케팅 카피(_NOTION_LANDING_MARKERS)를 찾아 판정했는데,
    그 카피는 **정상 공개 페이지의 렌더 결과에도 그대로 들어있다** (2026-08-16 계측: 본문 4302자
    공개 페이지에서 마커 2개 히트). 그래서 실질 판별이 '텍스트가 짧으면 비공개' 하나뿐이었고,
    렌더가 조금만 느려도 공개 페이지가 비공개로 확정되며 재시도까지 차단됐다 (실사고 2026-08-11).
    """
    if block_count != 0:
        return False
    body = body_text or ""
    if not body:
        return False  # 렌더 자체를 못 한 것 — 접근 불가 근거 없음. 재시도 대상.
    return any(m in body for m in _NOTION_NOACCESS_MARKERS)
