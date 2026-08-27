"""OAuth 2.1 grant 흐름 — authorize / token / revoke.

authorize 가 게이트 예외인 이유: 기존 _auth_gate 의 next 는 request.path 기반이라
쿼리스트링을 버린다. OAuth 파라미터가 전부 쿼리에 있으므로 여기서 full_path 를 보존해
직접 /login 으로 보낸다.
"""
from __future__ import annotations

import base64
import hashlib
import logging
import secrets
from typing import Optional
from urllib.parse import quote, unquote, urlencode, urlparse

from flask import Flask, jsonify, redirect, render_template, request

from scripts import auth_store as auth_store_mod
from scripts.auth_routes import COOKIE_NAME
from scripts.mcp_remote import config as mcp_config
from scripts.mcp_remote import oauth_store as store_mod
from scripts.mcp_remote.guard import FailGuard

logger = logging.getLogger(__name__)

SCOPE = "skills:read"
LOGIN_PATH = "/login"


def _pkce_ok(verifier: str, challenge: str) -> bool:
    if not verifier or not challenge:
        return False
    digest = hashlib.sha256(str(verifier).encode("ascii")).digest()
    computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return secrets.compare_digest(computed, str(challenge))


def _err_page(message: str, status: int = 400):
    """리다이렉트하지 않는 오류 — 오픈 리다이렉터 방지. 잠금(429)에도 쓴다."""
    return (f"<!doctype html><meta charset='utf-8'>"
            f"<p style='font-family:sans-serif;padding:2rem'>연결 실패: {message}</p>"), status


def _with_query(uri: str, q: dict) -> str:
    """redirect_uri 에 이미 쿼리가 있으면 &, 없으면 ? 로 잇는다 (RFC 6749 §4.1.2).

    트레일링 "?" (빈 쿼리)는 먼저 떼어낸다 — 안 그러면 urlparse().query 가 "" 라서
    "??" 가 만들어진다.
    """
    base = uri[:-1] if uri.endswith("?") else uri
    return base + ("&" if urlparse(base).query else "?") + urlencode(q)


def register_oauth_grants(app: Flask, *, store=None, auth=None, cfg: Optional[dict] = None,
                          consent_template: Optional[str] = "oauth_consent.html") -> None:
    """store/auth/cfg/consent_template 은 테스트 주입용.

    guard 는 함수 지역 변수로 둔다 (모듈 레벨 싱글턴 금지 — Task 5 에서 모듈 레벨 가드가
    테스트 간 상태를 공유해 잠금 테스트 뒤 알파벳순 다음 테스트들을 429 로 오염시킨 사고가
    있었다). register_oauth_grants 는 운영에서 앱 기동 시 1회만 호출되므로, nested 핸들러들이
    이 인스턴스를 closure 로 캡처해도 요청 간 5회 실패 → 5분 잠금 공유라는 원래 의도는
    그대로 성립한다.
    """
    guard = FailGuard()

    def _cfg() -> dict:
        return cfg if cfg is not None else mcp_config.load()

    def _store():
        return store if store is not None else store_mod.get_store()

    def _auth():
        return auth if auth is not None else auth_store_mod.get_store()

    def _client_credentials() -> tuple[str, Optional[str]]:
        """RFC 6749 §2.3.1 — Basic 헤더 우선, 없으면 form 폴백.

        Basic 의 client_id/secret 은 base64 앞에 form-urlencode 되어 있으므로 unquote 한다.
        """
        auth_header = request.headers.get("Authorization", "")
        if auth_header.lower().startswith("basic "):
            try:
                raw = base64.b64decode(auth_header[6:].strip()).decode("utf-8")
            except Exception:  # noqa: BLE001
                return "", None
            cid, sep, secret = raw.partition(":")
            if not sep:
                return "", None
            return unquote(cid), (unquote(secret) or None)
        return request.form.get("client_id", ""), (request.form.get("client_secret") or None)

    # ── authorize ────────────────────────────────────────────

    def _validate_authorize(c: dict):
        """(client, params) 또는 (None, 오류응답)."""
        q = request.args
        locked = guard.check(q.get("client_id", "") or "anon")
        if locked:
            return None, _err_page(locked, 429)
        client = _store().get_client(q.get("client_id", ""))
        if client is None:
            guard.fail(q.get("client_id", "") or "anon")
            logger.warning("authorize: 미등록 client_id=%r", q.get("client_id"))
            return None, _err_page("등록되지 않은 클라이언트입니다")
        redirect_uri = q.get("redirect_uri", "")
        if redirect_uri not in client["redirect_uris"]:
            guard.fail(q.get("client_id", ""))
            logger.warning("authorize: redirect_uri 불일치 요청=%r 등록=%r",
                           redirect_uri, client["redirect_uris"])
            return None, _err_page("redirect_uri 가 등록값과 일치하지 않습니다")
        if q.get("response_type") != "code":
            return None, _err_page("response_type 은 code 여야 합니다")
        if q.get("code_challenge_method", "S256") != "S256" or not q.get("code_challenge"):
            return None, _err_page("PKCE S256 이 필요합니다")
        resource = q.get("resource") or mcp_config.resource_id(c)
        if resource != mcp_config.resource_id(c):
            return None, _err_page("resource 가 이 서버와 일치하지 않습니다")
        return client, {"redirect_uri": redirect_uri, "state": q.get("state", ""),
                        "code_challenge": q.get("code_challenge"), "resource": resource}

    def _invite_code_of_request() -> Optional[str]:
        """로그인 쿠키 → 그 세션을 발급한 초대코드 (grant 에 승인 주체로 박는다)."""
        token = request.cookies.get(COOKIE_NAME, "")
        if not token or not _auth().check_token(token):
            return None
        return _auth().code_of_token(token)   # Task 1 에서 추가함

    @app.get("/oauth/authorize")
    def oauth_authorize_get():
        c = _cfg()
        client, out = _validate_authorize(c)
        if client is None:
            return out
        if _invite_code_of_request() is None:
            nxt = quote(request.full_path.rstrip("?"), safe="")
            return redirect(f"{LOGIN_PATH}?next={nxt}")
        if consent_template is None:
            return "CONSENT", 200
        return render_template(consent_template, client_name=client["name"],
                               action=request.full_path.rstrip("?"))

    @app.post("/oauth/authorize")
    def oauth_authorize_post():
        c = _cfg()
        client, out = _validate_authorize(c)
        if client is None:
            return out
        invite = _invite_code_of_request()
        if invite is None:
            nxt = quote(request.full_path.rstrip("?"), safe="")
            return redirect(f"{LOGIN_PATH}?next={nxt}")
        params = out
        if request.form.get("approve") != "yes":
            q = {"error": "access_denied"}
            if params["state"]:
                q["state"] = params["state"]
            return redirect(_with_query(params["redirect_uri"], q))
        code = _store().issue_code(
            client_id=request.args.get("client_id", ""), redirect_uri=params["redirect_uri"],
            code_challenge=params["code_challenge"], resource=params["resource"],
            scope=SCOPE, invite_code=invite)
        q = {"code": code}
        if params["state"]:
            q["state"] = params["state"]
        return redirect(_with_query(params["redirect_uri"], q))

    # ── token ────────────────────────────────────────────────

    @app.post("/oauth/token")
    def oauth_token():
        c = _cfg()
        st = _store()
        cid, secret = _client_credentials()
        locked = guard.check(cid or "anon")
        if locked:
            return jsonify({"error": "too_many_requests", "error_description": locked}), 429
        if not st.verify_client(cid, secret):
            guard.fail(cid or "anon")
            resp = jsonify({"error": "invalid_client"})
            resp.status_code = 401
            resp.headers["WWW-Authenticate"] = 'Basic realm="aiskillbox"'
            return resp
        grant_type = request.form.get("grant_type", "")

        if grant_type == "authorization_code":
            code = request.form.get("code", "")
            if st.code_was_seen(code):
                n = st.revoke_grants_of(cid)
                logger.warning("인가코드 재사용 감지 — client=%s grant %d건 폐기", cid, n)
                return jsonify({"error": "invalid_grant",
                                "error_description": "인가코드 재사용"}), 400
            g = st.consume_code(code, client_id=cid)
            if g is None:
                guard.fail(cid or "anon")
                logger.warning("token: 인가코드 거부 (없음/만료/소유자 불일치) client=%s", cid)
                return jsonify({"error": "invalid_grant"}), 400
            st.mark_code_spent(code, cid)
            if g["redirect_uri"] != request.form.get("redirect_uri", ""):
                return jsonify({"error": "invalid_grant",
                                "error_description": "redirect_uri 불일치"}), 400
            if not _pkce_ok(request.form.get("code_verifier", ""), g["code_challenge"]):
                return jsonify({"error": "invalid_grant",
                                "error_description": "PKCE 검증 실패"}), 400
            req_resource = request.form.get("resource") or g["resource"]
            if req_resource != g["resource"]:
                return jsonify({"error": "invalid_target"}), 400
            access, refresh, ttl = st.issue_tokens(
                g, access_ttl=mcp_config.access_ttl(c), refresh_ttl=mcp_config.refresh_ttl(c))

        elif grant_type == "refresh_token":
            rotated = st.rotate_refresh(request.form.get("refresh_token", ""),
                                        access_ttl=mcp_config.access_ttl(c),
                                        refresh_ttl=mcp_config.refresh_ttl(c),
                                        client_id=cid)
            if rotated is None:
                return jsonify({"error": "invalid_grant"}), 400
            access, refresh, ttl = rotated

        else:
            return jsonify({"error": "unsupported_grant_type"}), 400

        guard.ok(cid)   # 실제 grant 발급에만 리셋 — 클라이언트 인증 성공만으로는 리셋하지 않는다
        resp = jsonify({"access_token": access, "token_type": "Bearer", "expires_in": ttl,
                        "refresh_token": refresh, "scope": SCOPE})
        resp.headers["Cache-Control"] = "no-store"
        resp.headers["Pragma"] = "no-cache"
        return resp

    # ── revoke ───────────────────────────────────────────────

    @app.post("/oauth/revoke")
    def oauth_revoke():
        cid, secret = _client_credentials()
        locked = guard.check(cid or "anon")
        if locked:
            return jsonify({"error": "too_many_requests", "error_description": locked}), 429
        if not _store().verify_client(cid, secret):
            guard.fail(cid or "anon")
            return jsonify({"error": "invalid_client"}), 401
        # guard.ok(cid) 없음 — revoke 는 실패에만 guard.fail 을 걸므로 리셋할 이유가 없다.
        # /oauth/token 과 guard 를 공유하는데, 여기서 리셋하면 token 의 브루트포스 잠금이
        # 무효화된다 (R-1 회귀).
        _store().revoke(request.form.get("token", ""))
        return "", 200   # RFC 7009 — 알 수 없는 토큰도 200
