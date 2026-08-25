"""붙여넣은 일반 텍스트 → ScrapeResult (네트워크 0).

URL 이 없는 입력을 스크랩 결과와 같은 모양으로 감싸서 이후 파이프라인
(분석 → 중복 합병 → SKILL.md → 라이브러리)을 그대로 태운다.

왜 필요한가: 스크랩이 구조적으로 불가능한 출처(ChatGPT 공유·GPT 링크, IG 피드,
워크스페이스 전용 노션, 로그인 벽 뉴스레터)에 대해 collect.py 는 예전부터
"본문을 직접 텍스트로 옮겨 등록해 주세요" 라고 안내해 왔는데 정작 그 경로가
없었다. 이 모듈이 그 경로다.
"""
from __future__ import annotations

import hashlib
import re
from urllib.parse import urlsplit

from .router import ScrapeResult

# 사람이 의도적으로 붙여넣은 텍스트는 '렌더 실패로 껍데기만 잡힌' 위험이 없다.
# 스크랩용 MIN_TEXT_LEN(500)보다 낮게 잡아 짧은 프롬프트 모음/캡션도 받는다.
TEXT_MIN_LEN = 200
# 분석 프롬프트가 150k 로 자르므로 그 위는 저장해봐야 의미 없다.
TEXT_MAX_LEN = 200_000

# 붙여넣은 텍스트의 출처 식별자 스킴. 진짜 URL 이 아니므로 클릭 가능한 링크로
# 렌더하면 안 된다 (md_generator/catalog 가 is_paste_source 로 분기).
PASTE_SCHEME = "paste"

_MD_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
_URL_LINE_RE = re.compile(r"^\s*https?://\S+\s*$")


def paste_id(text: str) -> str:
    """같은 텍스트 → 같은 식별자. 재등록 시 중복 감지가 걸리게 하는 축."""
    normalized = re.sub(r"\s+", " ", (text or "").strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def paste_url(text: str) -> str:
    return f"{PASTE_SCHEME}://{paste_id(text)}"


def is_paste_source(url: str) -> bool:
    """출처 문자열이 붙여넣기 식별자인지. 링크 렌더 분기에 쓴다."""
    if not url:
        return False
    try:
        return urlsplit(url).scheme == PASTE_SCHEME
    except Exception:  # noqa: BLE001
        return False


def derive_title(text: str, fallback: str = "붙여넣은 텍스트") -> str:
    """본문 앞부분에서 제목 후보를 뽑는다 — 마크다운 헤딩 > 첫 의미 있는 줄."""
    lines = (text or "").splitlines()
    for line in lines[:40]:
        m = _MD_HEADING_RE.match(line)
        if m and m.group(1).strip():
            return m.group(1).strip()[:120]
    for line in lines[:40]:
        s = line.strip().lstrip("#*->•·").strip()
        # 링크만 있는 줄·구분선·너무 짧은 줄은 제목이 못 된다.
        if len(s) < 4 or _URL_LINE_RE.match(line) or set(s) <= set("-=_~"):
            continue
        return s[:120]
    return fallback


def scrape(text: str, *, title: str = "", origin_url: str = "") -> ScrapeResult:
    """붙여넣은 텍스트를 ScrapeResult 로 포장.

    origin_url: 사용자가 "이 링크 내용을 옮겨 적었다" 고 알려준 원본 URL(선택).
                있으면 출처로 그 URL 을 쓰고, 없으면 paste:// 식별자를 쓴다.
    """
    body = (text or "").strip()
    if len(body) > TEXT_MAX_LEN:
        body = body[:TEXT_MAX_LEN]
    source_url = (origin_url or "").strip() or paste_url(body)
    return ScrapeResult(
        url=source_url,
        source_type="text",
        title=(title or "").strip() or derive_title(body),
        text=body,
        meta={
            "input_kind": "paste",
            "char_count": len(body),
            "origin_url": (origin_url or "").strip(),
        },
        ok=bool(body),
        error=None if body else "빈 텍스트",
    )
