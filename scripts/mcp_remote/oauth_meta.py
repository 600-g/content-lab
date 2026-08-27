"""OAuth discovery 메타데이터 (RFC 9728 / RFC 8414) + 동적 등록 (RFC 7591).

동적 등록은 config 토글이다. 꺼져 있으면 registration_endpoint 를 메타데이터에서 빼고
/oauth/register 는 404 — 인터넷에 등록 창구가 열리지 않는다.
운영: 최초 커넥터 연결 때만 켜서 Claude 가 자기 redirect_uri 를 등록하게 하고 다시 끈다.
"""
from __future__ import annotations

import logging
from typing import Optional
from urllib.parse import urlparse

from flask import Flask, jsonify, request

from scripts.mcp_remote import config as mcp_config
from scripts.mcp_remote import oauth_store as store_mod
from scripts.mcp_remote.guard import FailGuard

logger = logging.getLogger(__name__)

SCOPE = "skills:read"
MAX_REDIRECT_URIS = 8


def _https_uri(u: str) -> bool:
    try:
        p = urlparse(str(u))
    except Exception:  # noqa: BLE001
        return False
    return p.scheme == "https" and bool(p.netloc)


def register_oauth_meta(app: Flask, *, store=None, cfg: Optional[dict] = None) -> None:
    # 앱(=프로세스) 당 하나 — 모듈 전역으로 두면 테스트마다 새로 만드는 앱들이 잠금 상태를
    # 공유해버려 서로 오염된다. 운영에서는 register_oauth_meta 가 기동 시 1회만 호출되므로
    # 이 인스턴스가 프로세스 수명 내내 유지되어 원래 의도(요청 간 잠금 공유)를 그대로 만족한다.
    guard = FailGuard()

    def _cfg() -> dict:
        return cfg if cfg is not None else mcp_config.load()

    def _store():
        return store if store is not None else store_mod.get_store()

    def _protected_resource():
        c = _cfg()
        return jsonify({
            "resource": mcp_config.resource_id(c),
            "authorization_servers": [mcp_config.base_url(c)],
            "scopes_supported": [SCOPE],
            "bearer_methods_supported": ["header"],
        })

    app.add_url_rule("/.well-known/oauth-protected-resource", "mcp_protected_resource",
                     _protected_resource, methods=["GET"])
    app.add_url_rule("/.well-known/oauth-protected-resource/mcp", "mcp_protected_resource_path",
                     _protected_resource, methods=["GET"])

    @app.get("/.well-known/oauth-authorization-server")
    def as_metadata():
        c = _cfg()
        meta = {
            "issuer": mcp_config.base_url(c),
            "authorization_endpoint": mcp_config.abs_url("/oauth/authorize", c),
            "token_endpoint": mcp_config.abs_url("/oauth/token", c),
            "revocation_endpoint": mcp_config.abs_url("/oauth/revoke", c),
            "scopes_supported": [SCOPE],
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "code_challenge_methods_supported": ["S256"],
            "token_endpoint_auth_methods_supported": ["client_secret_post", "none"],
        }
        if mcp_config.dynamic_registration(c):
            meta["registration_endpoint"] = mcp_config.abs_url("/oauth/register", c)
        return jsonify(meta)

    @app.post("/oauth/register")
    def register_client():
        c = _cfg()
        if not mcp_config.dynamic_registration(c):
            return jsonify({"error": "not_found"}), 404
        locked = guard.check("register")
        if locked:
            return jsonify({"error": "too_many_requests", "error_description": locked}), 429
        body = request.get_json(silent=True) or {}
        uris = body.get("redirect_uris")
        if not isinstance(uris, list) or not uris or len(uris) > MAX_REDIRECT_URIS:
            guard.fail("register")
            return jsonify({"error": "invalid_redirect_uri",
                            "error_description": "redirect_uris 배열이 필요합니다"}), 400
        if not all(_https_uri(u) for u in uris):
            guard.fail("register")
            return jsonify({"error": "invalid_redirect_uri",
                            "error_description": "redirect_uri 는 https 절대 URL 이어야 합니다"}), 400
        name = str(body.get("client_name") or "unnamed")[:120]
        client_id, secret = _store().create_client(name, [str(u) for u in uris], source="dynamic")
        logger.info("동적 등록: %s (%s) redirect_uris=%s", name, client_id, uris)
        out = {"client_id": client_id, "client_name": name, "redirect_uris": [str(u) for u in uris],
               "grant_types": ["authorization_code", "refresh_token"],
               "response_types": ["code"], "token_endpoint_auth_method": "client_secret_post",
               "scope": SCOPE}
        if secret:
            out["client_secret"] = secret
        return jsonify(out), 201
