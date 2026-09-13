"""Instagram 공개 embed 스크래퍼 — 로그인·쿠키·yt-dlp 없이 캡션 + 미디어 목록.

실측 (2026-09-12): `instagram.com/<p|reel>/<shortcode>/embed/captioned/` 는 비로그인 200 을 주고,
HTML 의 `"contextJSON":"…"` (JSON 문자열을 한 번 더 JSON 인코딩) 안 `gql_data.shortcode_media` 에
캡션 · 작성자 · `video_url` · `video_duration` · 캐러셀 자식(`edge_sidecar_to_children`) ·
`accessibility_caption` 이 들어 있다. yt-dlp 는 같은 릴스에 "login required" 로 실패한다.

이 모듈은 텍스트(캡션)만 만들고, 영상/이미지는 `meta["media"]` 목록으로 넘긴다 —
실제 내용 읽기는 `scripts/analyzer/media_understand.py` 가 한다.

실패는 전부 `ok=False` (예외 불출) → router 가 기존 경로(사전 차단 → yt-dlp → Playwright)로 폴백.
설계: docs/superpowers/specs/2026-09-12-media-understanding-design.md
"""
from __future__ import annotations

import json
import logging
import re
from typing import Callable, Optional

import requests

from .router import ScrapeResult

logger = logging.getLogger(__name__)

# WebKit UA — notion.site 와 같은 이유로 Chrome UA 보다 안정적 (gotcha 25).
EMBED_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)
TIMEOUT = 25
_SHORTCODE_RE = re.compile(
    r"instagram\.com/(?:[A-Za-z0-9_.]+/)?(p|reel|reels|tv)/([A-Za-z0-9_-]+)", re.I
)
_CONTEXT_MARK = '"contextJSON":'


def parse_shortcode(url: str) -> Optional[tuple[str, str]]:
    """(kind, shortcode). kind 는 'p' 또는 'reel' 로 정규화 (reels/tv → reel)."""
    m = _SHORTCODE_RE.search(url or "")
    if not m:
        return None
    kind = m.group(1).lower()
    kind = "reel" if kind in ("reel", "reels", "tv") else "p"
    return kind, m.group(2)


def embed_url(url: str) -> Optional[str]:
    parsed = parse_shortcode(url)
    if not parsed:
        return None
    kind, sc = parsed
    return f"https://www.instagram.com/{kind}/{sc}/embed/captioned/"


def fetch_embed_html(url: str, timeout: int = TIMEOUT) -> str:
    r = requests.get(
        url,
        headers={"User-Agent": EMBED_UA, "Accept-Language": "ko,en;q=0.8"},
        timeout=timeout,
    )
    r.raise_for_status()
    return r.text


def parse_context_json(html: str) -> Optional[dict]:
    """embed HTML → shortcode_media dict. 없거나 깨졌으면 None (예외 불출)."""
    i = (html or "").find(_CONTEXT_MARK)
    if i < 0:
        return None
    idx = i + len(_CONTEXT_MARK)
    while idx < len(html) and html[idx] in " \t\r\n":
        idx += 1
    try:
        raw, _ = json.JSONDecoder().raw_decode(html, idx)
        if not isinstance(raw, str):
            return None
        data = json.loads(raw)
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    sm = (data.get("gql_data") or {}).get("shortcode_media")
    return sm if isinstance(sm, dict) else None


def _caption(sm: dict) -> str:
    edges = ((sm.get("edge_media_to_caption") or {}).get("edges")) or []
    for e in edges:
        t = ((e or {}).get("node") or {}).get("text")
        if t:
            return str(t).strip()
    return ""


def extract_media(sm: dict, shortcode: str) -> list[dict]:
    """영상/이미지 목록. key 는 캐시 키 — URL 은 서명·만료가 붙어 매번 달라지므로 shortcode+순번."""
    children = ((sm.get("edge_sidecar_to_children") or {}).get("edges")) or []
    nodes = [((e or {}).get("node") or {}) for e in children] if children else [sm]
    out: list[dict] = []
    for i, n in enumerate(nodes):
        alt = str(n.get("accessibility_caption") or "")
        if n.get("is_video") and n.get("video_url"):
            out.append({"kind": "video", "url": n["video_url"], "key": f"ig:{shortcode}:{i}", "alt": alt})
        elif n.get("display_url"):
            out.append({"kind": "image", "url": n["display_url"], "key": f"ig:{shortcode}:{i}", "alt": alt})
    return out


def scrape(url: str, *, fetch: Callable[[str], str] | None = None) -> ScrapeResult:
    parsed = parse_shortcode(url)
    if not parsed:
        return ScrapeResult(url=url, source_type="instagram", title="", text="", meta={},
                            ok=False, error="인스타그램 게시물 URL 이 아님 (p/reel 경로 없음)")
    _, sc = parsed
    eurl = embed_url(url) or url
    try:
        html = (fetch or fetch_embed_html)(eurl)
    except Exception as e:  # noqa: BLE001
        return ScrapeResult(url=url, source_type="instagram", title="", text="", meta={},
                            ok=False, error=f"embed 페이지 요청 실패: {e}")
    sm = parse_context_json(html)
    if not sm:
        return ScrapeResult(url=url, source_type="instagram", title="", text="", meta={},
                            ok=False, error="embed 페이지에 contextJSON 없음 (로그인 벽·삭제·비공개 가능성)")

    owner = str(((sm.get("owner") or {}).get("username")) or "")
    caption = _caption(sm)
    media = extract_media(sm, sc)
    typename = str(sm.get("__typename") or "")
    is_video = bool(sm.get("is_video"))
    if typename == "GraphSidecar" or sm.get("edge_sidecar_to_children"):
        kind = "carousel"
    else:
        kind = "reel" if is_video else "post"
    duration = sm.get("video_duration")
    views = sm.get("video_view_count")

    header = f"[Instagram] @{owner}" if owner else "[Instagram]"
    if kind == "reel" and duration:
        header += f" · 릴스 {float(duration):.0f}초"
    if views:
        try:
            header += f" · 조회 {int(views):,}"
        except (TypeError, ValueError):
            pass
    parts = [header]
    if caption:
        parts.append(caption)
    alts = [m["alt"] for m in media if m.get("alt")]
    if alts:
        parts.append("[슬라이드 대체텍스트]\n" + "\n".join(f"- {a}" for a in alts))
    text = "\n\n".join(parts)
    title = f"Instagram @{owner}: {caption[:60]}" if caption else f"Instagram @{owner} {kind}"
    ok = bool(caption or media)
    meta = {
        "owner": owner, "shortcode": sc, "kind": kind, "typename": typename,
        "duration": duration, "view_count": views,
        "thumbnail": sm.get("display_url") or "",
        "media": media,
    }
    logger.info("IG embed: @%s %s 캡션 %d자 · 미디어 %d건", owner, kind, len(caption), len(media))
    return ScrapeResult(url=url, source_type="instagram", title=title, text=text, meta=meta,
                        ok=ok, error=None if ok else "캡션도 미디어도 없음")
