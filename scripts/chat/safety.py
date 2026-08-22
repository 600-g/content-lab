"""채팅 세션 토큰 + PIN 게이트.

PIN 0910 1회 입력 → 30분 세션 토큰. mutating 도구 호출 직전에 토큰 확인.
PIN 자체 검증은 app.py 의 기존 _PIN_GUARD 와 같은 ADMIN_PIN .env 키 재사용.
"""
from __future__ import annotations

import hmac
import json
import logging
import os
import secrets
import threading
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_SESSIONS: dict[str, dict] = {}  # token -> {"expires_at": float}
_LOCK = threading.Lock()
# 서버 재시작마다 세션이 전부 날아가 사용자가 매번 PIN 재입력해야 했음 → 디스크 영속화.
_SESSIONS_PATH = Path(__file__).resolve().parents[2] / "logs" / "chat_sessions.json"
_SESSIONS_LOADED = False


def _load_sessions() -> None:
    """반드시 _LOCK 안에서 호출. 최초 1회만 디스크에서 복원."""
    global _SESSIONS_LOADED
    if _SESSIONS_LOADED:
        return
    _SESSIONS_LOADED = True
    try:
        if _SESSIONS_PATH.exists():
            data = json.loads(_SESSIONS_PATH.read_text(encoding="utf-8"))
            now = time.time()
            _SESSIONS.update({
                t: v for t, v in data.items()
                if isinstance(v, dict) and v.get("expires_at", 0) > now
            })
    except Exception as e:  # noqa: BLE001
        logger.warning("chat_sessions.json 복원 실패 — 빈 세션으로 시작: %s", e)


def _save_sessions() -> None:
    """반드시 _LOCK 안에서 호출."""
    try:
        _SESSIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SESSIONS_PATH.write_text(json.dumps(_SESSIONS), encoding="utf-8")
        os.chmod(_SESSIONS_PATH, 0o600)  # 세션 토큰 파일 — 소유자만
    except Exception as e:  # noqa: BLE001
        logger.warning("chat_sessions.json 저장 실패: %s", e)
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
        _load_sessions()
        token = secrets.token_urlsafe(24)
        _SESSIONS[token] = {"expires_at": now + _session_seconds()}
        _save_sessions()
        return True, token, None


def check_session(token: Optional[str]) -> bool:
    """세션 토큰 유효성 검증 + 만료 자동 정리."""
    if not token:
        return False
    now = time.time()
    with _LOCK:
        _load_sessions()
        # 만료 청소.
        expired = [t for t, v in _SESSIONS.items() if v["expires_at"] < now]
        for t in expired:
            del _SESSIONS[t]
        s = _SESSIONS.get(token)
        if not s:
            if expired:
                _save_sessions()
            return False
        # 활성 사용 — 슬라이딩 윈도우 갱신.
        s["expires_at"] = now + _session_seconds()
        _save_sessions()
        return True


def revoke(token: str) -> None:
    with _LOCK:
        _load_sessions()
        _SESSIONS.pop(token, None)
        _save_sessions()


def is_configured() -> bool:
    return bool(_admin_pin())
