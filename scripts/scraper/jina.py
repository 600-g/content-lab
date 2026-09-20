"""Jina Reader 폴백 (v5.4) — 렌더 실패로 껍데기만 잡힌 페이지의 마지막 수단.

`https://r.jina.ai/<URL>` 은 키·로그인·쿠키 없이 공개 페이지를 마크다운으로 돌려준다 (무료).
실측 2026-09-20: Playwright 가 273·453자로 끝낸 공개 노션 페이지를 5,516자로 읽었다.

한계 — 로그인 벽 자체는 못 뚫는다. 그래서 router 는 **사전 차단(skip_reason)된 URL 에는 부르지 않고**,
Playwright·requests 결과가 MIN_TEXT_LEN 미만일 때만 부른다. 결과가 더 짧으면 기존 것이 그대로 남는다.

응답 형식:
    Title: ...
    URL Source: ...
    Published Time: ...        (없을 수도)
    Markdown Content:
    <본문>
"""
from __future__ import annotations

import logging
import os
import re
from typing import Callable, Optional

import requests

from .router import ScrapeResult

logger = logging.getLogger(__name__)

ENDPOINT = os.getenv("JINA_READER_ENDPOINT", "https://r.jina.ai/")
TIMEOUT = int(os.getenv("JINA_TIMEOUT", "60"))
MIN_BODY = int(os.getenv("JINA_MIN_BODY", "200"))
# ★ 브라우저 UA 를 보내면 403 이다 (2026-09-20 실측: Safari UA → 403, curl·서비스 UA → 200).
# 다른 스크래퍼는 차단을 피하려 브라우저 UA 를 쓰기 때문에 여기서도 그러기 쉬운데, r.jina.ai 는 정반대다.
UA = os.getenv("JINA_UA", "aiskillbox/5.4 (+https://aiskillbox.600g.net)")

_TITLE_RE = re.compile(r"^Title:\s*(.+)$", re.M)
_BODY_RE = re.compile(r"(?s)^Markdown Content:\s*\n(.*)$", re.M)
_HEADER_RE = re.compile(r"(?m)^(?:Title|URL Source|Published Time|Content Length|Images|Links):.*$")
# ![alt](blob:...) — 렌더러 내부 blob 주소라 밖에서는 죽은 링크다. alt 텍스트만 남긴다.
# 단 Jina 가 붙이는 "Image 3: " 류 자리표시자는 내용이 아니라 장식이라 통째로 버린다.
_BLOB_IMG_RE = re.compile(r"!\[([^\]]*)\]\(blob:[^)]*\)")
_BLOB_LINK_RE = re.compile(r"\[([^\]]*)\]\(blob:[^)]*\)")
_IMG_PLACEHOLDER_RE = re.compile(r"^Image\s*\d+\s*:\s*")


def parse(raw: str) -> tuple[str, str]:
    """응답 → (제목, 본문). 헤더가 없으면 통째로 본문 취급."""
    text = raw or ""
    m = _TITLE_RE.search(text)
    title = m.group(1).strip() if m else ""
    b = _BODY_RE.search(text)
    body = b.group(1) if b else _HEADER_RE.sub("", text)
    def _alt(mm) -> str:
        alt = _IMG_PLACEHOLDER_RE.sub("", (mm.group(1) or "").strip()).strip()
        # 글자·숫자가 하나도 없으면 장식(이모지·기호)이라 본문이 아니다
        return alt if re.search(r"[0-9A-Za-z가-힣]", alt) else ""

    body = _BLOB_IMG_RE.sub(_alt, body)
    body = _BLOB_LINK_RE.sub(_alt, body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return title, body.strip()


def _default_fetch(target: str) -> str:
    r = requests.get(target, headers={"User-Agent": UA}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text


def scrape(url: str, *, source_type: str = "web",
           fetch: Callable[[str], str] | None = None) -> ScrapeResult:
    """r.jina.ai 로 읽는다. 실패는 예외 대신 ok=False (폴백이 원래 경로보다 방어가 약하면 안 된다 — gotcha 39)."""
    fetch = fetch or _default_fetch
    target = ENDPOINT + url
    try:
        raw = fetch(target)
    except Exception as e:  # noqa: BLE001
        logger.warning("Jina Reader 실패 %s: %s", url, e)
        return ScrapeResult(url=url, source_type=source_type, title="", text="", meta={"via": "jina"},
                            ok=False, error=f"Jina Reader 실패: {e}")
    title, body = parse(raw)
    ok = len(body) >= MIN_BODY
    if not ok:
        logger.info("Jina Reader 본문 %d자 — 폴백 가치 없음 (%s)", len(body), url)
    return ScrapeResult(url=url, source_type=source_type, title=title, text=body,
                        meta={"via": "jina"}, ok=ok,
                        error=None if ok else f"Jina Reader 본문 부족 ({len(body)}자)")
