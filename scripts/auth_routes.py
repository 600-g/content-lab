"""전체 잠금 게이트 + 초대코드 인증 라우트 — app.py 가 register_auth(app, pin_ok=_pin_ok) 로 등록.

- before_request 게이트: allowlist(/login, /api/auth/redeem|bootstrap, /healthz, /static/*, /sw.js,
  원격 MCP 경로(/mcp, /oauth/*, /.well-known/*, 자체 인증 보유), OPTIONS) 외 전부 인증 필요.
  쿠키 `aiskillbox_auth` 또는 헤더 `X-Auth-Token`.
- 미인증: /api/* → 401 JSON(need_login), 페이지 → 302 /login?next=<path>.
- bootstrap: ADMIN_PIN(주입된 pin_ok — app.py 의 무차별 대입 잠금 공유) 으로 첫 코드 발급 + 즉시 로그인.
  코드가 하나도 없어도 오너는 PIN 만으로 진입 (닭-달걀 해소, 전 기기 로그아웃 복구로도 사용).
- redeem 자체 무차별 대입 가드: 5회 실패 → 5분 잠금 (PIN 가드와 동일 파라미터).

설계: docs/superpowers/specs/2026-08-22-invite-auth-design.md
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Callable, Optional
from urllib.parse import quote

from flask import Flask, jsonify, redirect, render_template, request

from scripts import auth_store as auth_store_mod
from scripts.auth_store import AuthStore

logger = logging.getLogger(__name__)

COOKIE_NAME = "aiskillbox_auth"
COOKIE_MAX_AGE = 400 * 24 * 3600  # Chrome 쿠키 수명 상한 (~400일) — 사실상 영구 자동로그인
LOGIN_PATH = "/login"

# 게이트 없이 통과하는 경로 (정확 일치 or prefix)
# 여기 있는 경로는 전부 **자체 인증**을 가진다: /mcp=Bearer 토큰, /oauth/token·/oauth/revoke=
# client_secret+PKCE, /oauth/authorize=쿠키+명시적 동의, /.well-known/*=비밀 없는 공개 메타데이터,
# /oauth/register=dynamic_registration 토글 off 면 404.
#
# 원격 MCP 경로를 **prefix 가 아니라 정확 일치로** 둔 이유: prefix("/oauth/") 는 그 아래 새 라우트를
# 추가하는 순간 자동으로 게이트 밖이 된다(fail-open). 정확 일치는 여기 명시적으로 적기 전까지
# 게이트 안에 남는다(fail-closed). 새 OAuth 엔드포인트를 추가하면 자체 인증을 넣고 이 목록에도 추가할 것.
_ALLOW_EXACT = {
    LOGIN_PATH, "/api/auth/redeem", "/api/auth/bootstrap", "/healthz", "/sw.js", "/favicon.ico",
    "/mcp",
    "/oauth/authorize", "/oauth/token", "/oauth/revoke", "/oauth/register",
    "/.well-known/oauth-protected-resource",
    "/.well-known/oauth-protected-resource/mcp",
    "/.well-known/oauth-authorization-server",
}
_ALLOW_PREFIX = ("/static/",)

_REDEEM_MAX_FAILS = 5
_REDEEM_LOCK_SECONDS = 300

PinOk = Callable[[str], tuple[bool, str]]


class _RedeemGuard:
    """redeem 무차별 대입 방어 — 전역 카운터 (코드 공간이 32^8 이라 개별 IP 추적까지는 불필요)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._fails = 0
        self._locked_until = 0.0

    def check(self) -> Optional[str]:
        with self._lock:
            wait = int(self._locked_until - time.time())
            if wait > 0:
                return f"시도 잠김 — {wait}초 후 재시도"
            return None

    def fail(self) -> None:
        with self._lock:
            self._fails += 1
            if self._fails >= _REDEEM_MAX_FAILS:
                self._locked_until = time.time() + _REDEEM_LOCK_SECONDS
                self._fails = 0

    def ok(self) -> None:
        with self._lock:
            self._fails = 0


def _request_token() -> str:
    return request.headers.get("X-Auth-Token", "") or request.cookies.get(COOKIE_NAME, "")


def _set_auth_cookie(resp, token: str):
    # Secure 미설정: localhost(http) + CF Tunnel(https 종단) 양쪽에서 동작해야 함.
    # HttpOnly + SameSite=Lax 로 JS 탈취/타사이트 전송 차단.
    resp.set_cookie(
        COOKIE_NAME, token,
        max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax", path="/",
    )
    return resp


def register_auth(
    app: Flask,
    *,
    pin_ok: PinOk,
    store: AuthStore | None = None,
    login_template: Optional[str] = "login.html",
) -> None:
    """게이트 + 인증 라우트 등록. store/login_template 은 테스트 주입용."""
    st = store or auth_store_mod.get_store()
    guard = _RedeemGuard()

    # ── 게이트 ──────────────────────────────────────────────

    @app.before_request
    def _auth_gate():
        if request.method == "OPTIONS":
            return None  # CORS preflight — 커스텀 헤더를 못 싣는 단계라 통과
        path = request.path
        if path in _ALLOW_EXACT or any(path.startswith(p) for p in _ALLOW_PREFIX):
            return None
        if st.check_token(_request_token()):
            return None
        if path.startswith("/api/"):
            return jsonify({"ok": False, "error": "로그인 필요 — 초대코드를 입력해주세요", "need_login": True}), 401
        nxt = quote(path, safe="")
        return redirect(f"{LOGIN_PATH}?next={nxt}")

    # ── 로그인 페이지 ────────────────────────────────────────

    @app.get(LOGIN_PATH)
    def login_page():
        if login_template is None:  # 테스트: 템플릿 없이 등록
            return "LOGIN"
        return render_template(login_template)

    # ── 코드 입장 ───────────────────────────────────────────

    @app.post("/api/auth/redeem")
    def auth_redeem():
        locked = guard.check()
        if locked:
            return jsonify({"ok": False, "error": locked}), 429
        data = request.get_json(silent=True) or {}
        code = str(data.get("code", ""))
        device = str(data.get("device", "") or request.user_agent.string or "")
        token = st.redeem(code, device=device)
        if token is None:
            guard.fail()
            # 코드 존재 여부를 구분하지 않는 단일 문구 (코드 탐지 방지)
            return jsonify({"ok": False, "error": "초대코드가 올바르지 않아요"}), 401
        guard.ok()
        resp = jsonify({"ok": True, "token": token})
        return _set_auth_cookie(resp, token)

    # ── 관리자 첫 등록 / 복구 (PIN) ──────────────────────────

    @app.post("/api/auth/bootstrap")
    def auth_bootstrap():
        data = request.get_json(silent=True) or {}
        ok, reason = pin_ok(str(data.get("pin", "")))
        if not ok:
            return jsonify({"ok": False, "error": reason or "PIN 불일치"}), 401
        device = str(data.get("device", "") or request.user_agent.string or "")
        code = st.create_code("owner")
        token = st.redeem(code, device=device)
        logger.info("auth bootstrap — 오너 코드 발급 + 로그인 (device=%s)", device[:60])
        resp = jsonify({"ok": True, "code": code, "token": token})
        return _set_auth_cookie(resp, token)

    # ── 코드 관리 (로그인 게이트 통과 후 + PIN 이중 게이트) ───

    def _require_pin() -> Optional[tuple]:
        pin = request.headers.get("X-Admin-Pin", "")
        ok, reason = pin_ok(pin)
        if not ok:
            return jsonify({"ok": False, "error": reason or "PIN 필요"}), 403
        return None

    @app.get("/api/auth/codes")
    def auth_codes_list():
        denied = _require_pin()
        if denied:
            return denied
        return jsonify({"ok": True, "codes": st.list_codes()})

    @app.post("/api/auth/codes")
    def auth_codes_create():
        denied = _require_pin()
        if denied:
            return denied
        data = request.get_json(silent=True) or {}
        code = st.create_code(str(data.get("label", "")))
        return jsonify({"ok": True, "code": code})

    @app.delete("/api/auth/codes/<code>")
    def auth_codes_delete(code: str):
        denied = _require_pin()
        if denied:
            return denied
        removed = st.delete_code(code)
        return jsonify({"ok": True, "revoked_sessions": removed})
