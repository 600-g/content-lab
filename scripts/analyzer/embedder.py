"""Gemini text-embedding-004 기반 의미 임베딩 + 디스크 캐시.

폴백 정책: 임베딩 실패 시 None 반환 → 호출자가 dedup 스킵하고 신규 등록.
즉 임베딩 인프라가 죽어도 기존 URL-매칭 dedup + 신규 등록은 계속 동작.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

EMBED_MODEL = "models/text-embedding-004"
EMBED_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "{model}:embedContent"
)
CACHE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "skills" / "embeddings.json"
_CACHE_LOCK = threading.Lock()
_CACHE: dict[str, dict] = {}
_CACHE_LOADED = False


def _ensure_cache_loaded() -> None:
    global _CACHE, _CACHE_LOADED
    if _CACHE_LOADED:
        return
    with _CACHE_LOCK:
        if _CACHE_LOADED:
            return
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        if CACHE_PATH.exists():
            try:
                _CACHE = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
            except Exception as e:  # noqa: BLE001
                logger.warning("embeddings.json 파싱 실패 — 빈 캐시로 시작: %s", e)
                _CACHE = {}
        else:
            _CACHE = {}
        _CACHE_LOADED = True


def _save_cache() -> None:
    """반드시 _CACHE_LOCK 안에서 호출."""
    try:
        CACHE_PATH.write_text(
            json.dumps(_CACHE, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception as e:  # noqa: BLE001
        logger.error("embeddings.json 저장 실패: %s", e)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _call_gemini(text: str) -> Optional[list[float]]:
    """Gemini embedContent API 호출. 실패 시 None."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        logger.warning("GEMINI_API_KEY 미설정 — 임베딩 불가")
        return None
    url = EMBED_URL.format(model=EMBED_MODEL) + f"?key={api_key}"
    payload = {
        "model": EMBED_MODEL,
        "content": {"parts": [{"text": text[:8000]}]},  # API 입력 한도 보호.
        "taskType": "SEMANTIC_SIMILARITY",
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 429:
            logger.warning("Gemini embedding quota 초과 — 임베딩 스킵")
            return None
        r.raise_for_status()
        data = r.json()
        vec = data.get("embedding", {}).get("values")
        if not vec:
            logger.warning("Gemini embedding 빈 응답: %s", str(data)[:200])
            return None
        return list(vec)
    except Exception as e:  # noqa: BLE001
        logger.warning("Gemini embedding 호출 실패: %s", e)
        return None


def embed(text: str) -> Optional[list[float]]:
    """단일 텍스트 임베딩. 빈 입력은 None."""
    text = (text or "").strip()
    if not text:
        return None
    return _call_gemini(text)


def get_or_embed(slug: str, text: str) -> Optional[list[float]]:
    """캐시 조회 → 미스/내용 변경이면 새로 임베딩.

    cache key 는 slug 단일. text 의 sha256 prefix 를 함께 저장해서 callout 변경
    감지. text 가 비어있으면 None 반환 (캐시도 안 건드림).
    """
    text = (text or "").strip()
    if not text:
        return None
    _ensure_cache_loaded()
    h = _hash(text)
    with _CACHE_LOCK:
        cached = _CACHE.get(slug)
        if cached and cached.get("hash") == h and cached.get("vec"):
            return list(cached["vec"])
    vec = _call_gemini(text)
    if vec is None:
        return None
    with _CACHE_LOCK:
        _CACHE[slug] = {
            "vec": vec,
            "hash": h,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        _save_cache()
    return vec


def all_cached() -> dict[str, dict]:
    """전체 캐시 사본 — dedup_finder 가 일괄 코사인 계산 시 사용."""
    _ensure_cache_loaded()
    with _CACHE_LOCK:
        return json.loads(json.dumps(_CACHE))


def invalidate(slugs: list[str] | None = None) -> int:
    """slugs 가 None 이면 전체 캐시 비움. 리턴은 지운 개수."""
    _ensure_cache_loaded()
    with _CACHE_LOCK:
        if slugs is None:
            n = len(_CACHE)
            _CACHE.clear()
        else:
            n = 0
            for s in slugs:
                if s in _CACHE:
                    del _CACHE[s]
                    n += 1
        _save_cache()
    return n


def cosine(a: list[float], b: list[float]) -> float:
    """코사인 유사도 — numpy 의존 없이 순수 파이썬 (146개 페어 계산이라 충분)."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0 or nb == 0:
        return 0.0
    return dot / ((na ** 0.5) * (nb ** 0.5))
