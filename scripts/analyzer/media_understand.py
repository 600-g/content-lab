"""미디어 이해 — 영상/이미지/유튜브를 Gemini 멀티모달로 텍스트화해 스크랩 본문에 덧붙인다.

스크랩과 분석 사이의 새 단계 (v5.1). `ScrapeResult.meta["media"]` 항목:
  {"kind": "video"|"image"|"youtube", "url": str, "key": str}
- video   : 다운로드(상한) → Files API resumable 업로드 → ACTIVE 대기 → generateContent
- image   : 최대 MAX_IMAGES 장을 inline 으로 한 번에 (카드뉴스 슬라이드)
- youtube : 다운로드 없이 URL 을 file_data 로

결과는 본문 끝에 `[영상 내용 — AI 전사]` / `[슬라이드 텍스트 — AI 판독]` 섹션으로 붙는다.
모델은 flash-lite → flash 순 (쿼터는 analyzer/gemini.py 와 공유). 캐시 logs/media_cache.json.
어떤 항목이 실패해도 예외를 밖으로 내지 않는다 (gotcha 39).
실측 (2026-09-12): 릴스 25초 = 8초·8k 토큰, 캐러셀 5장 = 7초·1.9k 토큰, 유튜브 87초 = 11초·2.6만 토큰.
설계: docs/superpowers/specs/2026-09-12-media-understanding-design.md
"""
from __future__ import annotations

import base64
import json
import logging
import os
import time
from pathlib import Path
from typing import Callable, Optional

import requests

from . import gemini as _gem

logger = logging.getLogger(__name__)

MODEL_ORDER = ("gemini-2.5-flash-lite", "gemini-2.5-flash")
MAX_VIDEO_BYTES = int(os.getenv("MEDIA_MAX_VIDEO_MB", "60")) * 1024 * 1024
MAX_IMAGES = int(os.getenv("MEDIA_MAX_IMAGES", "10"))
GEN_TIMEOUT = int(os.getenv("MEDIA_GEN_TIMEOUT", "240"))
UPLOAD_WAIT_SECONDS = 150
CACHE_FILE = Path(__file__).resolve().parents[2] / "logs" / "media_cache.json"
FETCH_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)
API = "https://generativelanguage.googleapis.com"

SECTION_VIDEO = "[영상 내용 — AI 전사]"
SECTION_IMAGES = "[슬라이드 텍스트 — AI 판독]"

VIDEO_PROMPT = (
    "이 영상의 내용을 한국어로 빠짐없이 정리해줘.\n"
    "1) 말하는 내용(나레이션·대사)을 순서대로 요약이 아니라 가능한 한 그대로 옮겨 적기\n"
    "2) 화면에 뜨는 자막·텍스트·목록을 전부 옮겨 적기\n"
    "3) 언급되거나 화면에 보이는 도구·앱·서비스·명령어 이름을 전부 나열\n"
    "광고 문구나 팔로우 유도는 제외. 마크다운 없이 평문."
)
IMAGE_PROMPT = (
    "이 이미지들은 한 게시물의 슬라이드(카드뉴스)다. 순서대로 각 슬라이드의 텍스트를 빠짐없이 옮겨 적고, "
    "표·목록·숫자·도구 이름은 그대로 보존해줘. 마지막에 전체가 무엇을 설명하는지 한국어 2줄로 요약. "
    "마크다운 없이 평문."
)
YOUTUBE_PROMPT = (
    "이 영상의 내용을 한국어로 정리해줘. 말하는 내용을 순서대로 자세히 옮기고, 화면에 나오는 텍스트·코드·"
    "명령어·도구 이름은 전부 그대로 적어줘. 마크다운 없이 평문."
)

_MIME_BY_EXT = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}


class MediaSkip(Exception):
    """정책상 건너뛰는 항목 (상한 초과 등) — 실패와 구분해 메시지만 남긴다."""


# ── 캐시 ──────────────────────────────────────────────────────────
def _load_cache(path: Path) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def _save_cache(path: Path, data: dict) -> None:
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, p)
    except Exception as e:  # noqa: BLE001
        logger.warning("media_cache 저장 실패: %s", e)


# ── 기본 구현 (네트워크) ─────────────────────────────────────────────
def _default_fetch(url: str) -> bytes:
    """스트리밍 다운로드. 상한을 넘기면 상한+1 바이트에서 끊는다 (호출측이 상한 초과로 판정)."""
    limit = MAX_VIDEO_BYTES + 1
    with requests.get(url, headers={"User-Agent": FETCH_UA}, timeout=90, stream=True) as r:
        r.raise_for_status()
        buf = bytearray()
        for chunk in r.iter_content(chunk_size=1 << 16):
            buf.extend(chunk)
            if len(buf) >= limit:
                break
        return bytes(buf)


def _api_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        raise RuntimeError("GEMINI_API_KEY 미설정 (.env 확인)")
    return key


def _default_upload(data: bytes, mime: str) -> str:
    """Files API resumable 업로드 → ACTIVE 상태의 file uri."""
    key = _api_key()
    start = requests.post(
        f"{API}/upload/v1beta/files",
        headers={
            "x-goog-api-key": key,
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(len(data)),
            "X-Goog-Upload-Header-Content-Type": mime,
            "Content-Type": "application/json",
        },
        json={"file": {"display_name": "aiskillbox-media"}},
        timeout=60,
    )
    start.raise_for_status()
    upload_url = start.headers.get("X-Goog-Upload-URL")
    if not upload_url:
        raise RuntimeError("Files API 가 업로드 URL 을 주지 않음")
    fin = requests.post(
        upload_url,
        headers={
            "Content-Length": str(len(data)),
            "X-Goog-Upload-Offset": "0",
            "X-Goog-Upload-Command": "upload, finalize",
        },
        data=data,
        timeout=180,
    )
    fin.raise_for_status()
    f = fin.json().get("file") or {}
    deadline = time.time() + UPLOAD_WAIT_SECONDS
    while f.get("state") != "ACTIVE":
        if f.get("state") == "FAILED":
            raise RuntimeError("Files API 처리 실패 (state=FAILED)")
        if time.time() > deadline:
            raise RuntimeError("Files API 처리 대기 초과")
        time.sleep(3)
        f = requests.get(f"{API}/v1beta/{f['name']}", headers={"x-goog-api-key": key}, timeout=30).json()
    return f["uri"]


def _default_generate(parts: list[dict]) -> str:
    """flash-lite → flash. 쿼터 게이트/카운트는 analyzer/gemini.py 와 공유. 헤더 인증 (gotcha 22)."""
    key = _api_key()
    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {"thinkingConfig": {"thinkingBudget": 0}, "maxOutputTokens": 4096},
    }
    last: Optional[str] = None
    for model in MODEL_ORDER:
        if _gem._quota_should_skip(model):
            logger.info("media: %s quota 임계 — 스킵", model)
            continue
        try:
            r = requests.post(
                f"{API}/v1beta/models/{model}:generateContent",
                headers={"Content-Type": "application/json", "x-goog-api-key": key},
                json=body, timeout=GEN_TIMEOUT,
            )
            if r.status_code == 429:
                _gem._quota_increment(model, hit_429=True)
                last = f"{model}: 429"
                continue
            r.raise_for_status()
            _gem._quota_increment(model)
            d = r.json()
            text = "".join(
                p.get("text", "") for p in ((d.get("candidates") or [{}])[0].get("content") or {}).get("parts", [])
            )
            if text.strip():
                return text
            last = f"{model}: 빈 응답"
        except requests.RequestException as e:
            last = f"{model}: {e}"
            logger.warning("media: %s 실패 — %s", model, e)
    raise RuntimeError(last or "사용 가능한 Gemini 모델 없음")


def _mime_for(url: str) -> str:
    path = (url or "").split("?", 1)[0].lower()
    for ext, mime in _MIME_BY_EXT.items():
        if path.endswith(ext):
            return mime
    return "image/jpeg"


# ── 본체 ──────────────────────────────────────────────────────────
def enrich(
    scrape_res,
    *,
    fetch: Callable[[str], bytes] | None = None,
    upload: Callable[[bytes, str], str] | None = None,
    generate: Callable[[list[dict]], str] | None = None,
    cache_path: Optional[Path | str] = None,
) -> dict:
    """meta["media"] 를 읽어 본문에 섹션을 덧붙인다. 반환: {"ok", "items", "added_chars"}."""
    fetch = fetch or _default_fetch
    upload = upload or _default_upload
    generate = generate or _default_generate
    cache_file = Path(cache_path) if cache_path else CACHE_FILE

    media = list(((getattr(scrape_res, "meta", None) or {}).get("media")) or [])
    result: dict = {"ok": True, "items": [], "added_chars": 0}
    if not media:
        return result

    cache = _load_cache(cache_file)
    dirty = False
    before = len(scrape_res.text or "")
    video_texts: list[str] = []
    image_texts: list[str] = []
    image_items: list[tuple[dict, dict]] = []  # (rec, item)

    for item in media:
        kind = item.get("kind")
        key = item.get("key") or item.get("url") or ""
        rec = {"key": key, "kind": kind, "ok": False, "cached": False, "error": None, "chars": 0}
        result["items"].append(rec)
        if kind == "image":
            if len(image_items) >= MAX_IMAGES:
                rec["error"] = f"이미지 상한 {MAX_IMAGES}장 초과 — 건너뜀"
            else:
                image_items.append((rec, item))
            continue
        hit = cache.get(key)
        if hit and hit.get("text"):
            rec.update(ok=True, cached=True, chars=len(hit["text"]))
            video_texts.append(hit["text"])
            continue
        try:
            if kind == "youtube":
                text = generate([{"file_data": {"file_uri": item["url"]}}, {"text": YOUTUBE_PROMPT}])
            elif kind == "video":
                data = fetch(item["url"])
                if len(data) > MAX_VIDEO_BYTES:
                    raise MediaSkip(f"영상 {len(data) // 1048576}MB — 상한 {MAX_VIDEO_BYTES // 1048576}MB 초과")
                uri = upload(data, "video/mp4")
                text = generate([{"file_data": {"file_uri": uri, "mime_type": "video/mp4"}}, {"text": VIDEO_PROMPT}])
            else:
                raise MediaSkip(f"알 수 없는 미디어 종류: {kind}")
            text = (text or "").strip()
            if not text:
                raise RuntimeError("빈 응답")
            rec.update(ok=True, chars=len(text))
            cache[key] = {"text": text, "ts": time.time(), "kind": kind}
            dirty = True
            video_texts.append(text)
        except Exception as e:  # noqa: BLE001 — 항목 실패는 격리
            rec["error"] = str(e)[:300]
            logger.warning("media %s(%s) 실패: %s", kind, key, rec["error"])

    if image_items:
        batch_key = "imgs:" + "|".join(item.get("key") or item.get("url") or "" for _, item in image_items)
        hit = cache.get(batch_key)
        if hit and hit.get("text"):
            for rec, _ in image_items:
                rec.update(ok=True, cached=True, chars=len(hit["text"]))
            image_texts.append(hit["text"])
        else:
            try:
                parts: list[dict] = []
                for _, item in image_items:
                    data = fetch(item["url"])
                    parts.append({"inline_data": {"mime_type": _mime_for(item["url"]),
                                                  "data": base64.b64encode(data).decode("ascii")}})
                parts.append({"text": IMAGE_PROMPT})
                text = (generate(parts) or "").strip()
                if not text:
                    raise RuntimeError("빈 응답")
                for rec, _ in image_items:
                    rec.update(ok=True, chars=len(text))
                cache[batch_key] = {"text": text, "ts": time.time(), "kind": "images", "n": len(image_items)}
                dirty = True
                image_texts.append(text)
            except Exception as e:  # noqa: BLE001
                for rec, _ in image_items:
                    rec["error"] = str(e)[:300]
                logger.warning("media images(%d장) 실패: %s", len(image_items), str(e)[:200])

    sections = []
    if video_texts:
        sections.append(SECTION_VIDEO + "\n" + "\n\n".join(video_texts))
    if image_texts:
        sections.append(SECTION_IMAGES + "\n" + "\n\n".join(image_texts))
    if sections:
        scrape_res.text = ((scrape_res.text or "").rstrip() + "\n\n" + "\n\n".join(sections)).strip()
    if dirty:
        _save_cache(cache_file, cache)

    result["added_chars"] = len(scrape_res.text or "") - before
    result["ok"] = all(i["ok"] for i in result["items"])
    return result
