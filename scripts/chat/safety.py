"""채팅 세션 토큰 + PIN 게이트.

PIN 0910 1회 입력 → 30분 세션 토큰. mutating 도구 호출 직전에 토큰 확인.
PIN 자체 검증은 app.py 의 기존 _PIN_GUARD 와 같은 ADMIN_PIN .env 키 재사용.
"""
from __future__ import annotations

import hmac
import logging
import os
import secrets
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)

_SESSIONS: dict[str, dict] = {}  # token -> {"expires_at": float}
_LOCK = threading.Lock()
_PIN_FAILS = {"count": 0, "locked_until": 0.0}
_MAX_FAILS = 5
_LOCK_SECONDS = 300


def _admin_pin() -> str:
    return os.getenv("ADMIN_PIN", "")


def _session_seconds() -> int:
    # config_store 에서 분 단위로 읽고 초 변환. 임포트 순환 회피 위해 함수 안에서 lazy import.
    try:
        from scripts import config_store
        m = int(config_store.get("chat.session_minutes", 30))
        return max(1, m) * 60
    except Exception:
        return 30 * 60


def verify_pin(pin: str) -> tuple[bool, Optional[str], Optional[str]]:
    """PIN 검증. Returns (ok, session_token | None, reason | None)."""
    now = time.time()
    with _LOCK:
        if now < _PIN_FAILS["locked_until"]:
            wait = int(_PIN_FAILS["locked_until"] - now)
            return False, None, f"잠금 — {wait}초 후 재시도"

        real = _admin_pin()
        if not real:
            return False, None, "ADMIN_PIN 미설정 (.env 확인)"

        if not hmac.compare_digest(str(pin), real):
            _PIN_FAILS["count"] += 1
            if _PIN_FAILS["count"] >= _MAX_FAILS:
                _PIN_FAILS["locked_until"] = now + _LOCK_SECONDS
                _PIN_FAILS["count"] = 0
                return False, None, f"{_MAX_FAILS}회 실패 — {_LOCK_SECONDS}초 잠금"
            return False, None, "PIN 불일치"

        # 성공.
        _PIN_FAILS["count"] = 0
        token = secrets.token_urlsafe(24)
        _SESSIONS[token] = {"expires_at": now + _session_seconds()}
        return True, token, None


def check_session(token: Optional[str]) -> bool:
    """세션 토큰 유효성 검증 + 만료 자동 정리."""
    if not token:
        return False
    now = time.time()
    with _LOCK:
        # 만료 청소.
        expired = [t for t, v in _SESSIONS.items() if v["expires_at"] < now]
        for t in expired:
            del _SESSIONS[t]
        s = _SESSIONS.get(token)
        if not s:
            return False
        # 활성 사용 — 슬라이딩 윈도우 갱신.
        s["expires_at"] = now + _session_seconds()
        return True


def revoke(token: str) -> None:
    with _LOCK:
        _SESSIONS.pop(token, None)


def is_configured() -> bool:
    return bool(_admin_pin())
