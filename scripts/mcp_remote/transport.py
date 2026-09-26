"""MCP Streamable HTTP 전송 — POST /mcp (stateless).

기존 stdio 서버의 순수 디스패치 mcp_server.handle(msg) 를 그대로 재사용한다.
SSE 미지원(도구가 전부 즉답형 — 스킬 3종 + 디지몬 도감 4종), 세션 ID 미발급(stateless).

설계: docs/superpowers/specs/2026-08-27-remote-mcp-oauth-design.md
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from flask import Flask, Response, jsonify, request

from scripts.library import mcp_server
from scripts.mcp_remote import config as mcp_config
from scripts.mcp_remote import oauth_store as store_mod

logger = logging.getLogger(__name__)

PROTECTED_RESOURCE_PATH = "/.well-known/oauth-protected-resource"

# RFC 6750 §3 의 error_description 은 quoted-string (ASCII) 이다 — 한글 사유는 JSON 본문으로만
# 보내고, 헤더에는 아래 ASCII 문구를 쓴다.
ERROR_DESCRIPTIONS = {
    "invalid_token": "The access token is expired, revoked, or otherwise invalid",
}


def _rpc_error(req_id, code: int, message: str, status: int):
    return jsonify({"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": code, "message": message}}), status


def register_transport(app: Flask, *, store=None, cfg: Optional[dict] = None) -> None:
    """store/cfg 는 테스트 주입용 — 운영에서는 기본값(None)."""
    mcp_server.use_local_backend()   # 자기호출 루프 차단 (Task 2)

    def _cfg() -> dict:
        return cfg if cfg is not None else mcp_config.load()

    def _store():
        return store if store is not None else store_mod.get_store()

    def _challenge(error: Optional[str] = None) -> str:
        """RFC 9728 resource_metadata + RFC 6750 §3.1 error 파라미터.

        error 를 붙이는 기준이 곧 클라이언트의 분기점이다: `error="invalid_token"` 이
        있으면 "리프레시하면 되는 상황", 없으면 "처음부터 인증하라"로 읽힌다. 만료된
        액세스 토큰에 이 값을 안 주면 클라이언트가 죽은 토큰을 그대로 재시도하는 401
        루프에 갇힌다 (2026-09-03 커넥터 단절 — 리프레시 토큰이 12월까지 살아있었는데도
        /oauth/token 요청이 한 번도 오지 않았다).

        반대로 토큰을 아예 안 보낸 요청에는 오류 코드를 넣지 않는다 (RFC 6750 §3).
        """
        url = mcp_config.abs_url(PROTECTED_RESOURCE_PATH, _cfg())
        parts = [f'resource_metadata="{url}"']
        if error:
            parts.append(f'error="{error}"')
            desc = ERROR_DESCRIPTIONS.get(error)
            if desc:
                parts.append(f'error_description="{desc}"')
        return "Bearer " + ", ".join(parts)

    def _unauthorized(msg: str, *, error: Optional[str] = None):
        resp = jsonify({"error": "invalid_token", "error_description": msg})
        resp.status_code = 401
        resp.headers["WWW-Authenticate"] = _challenge(error)
        return resp

    def _origin_ok(c: dict) -> bool:
        origin = request.headers.get("Origin")
        if not origin:
            return True   # curl·서버간 호출 — 브라우저가 아니면 Origin 이 없다
        return origin in mcp_config.allowed_origins(c)

    @app.post("/mcp")
    def mcp_endpoint():
        c = _cfg()
        if not mcp_config.enabled(c):
            return jsonify({"error": "disabled"}), 404
        if not _origin_ok(c):
            return jsonify({"error": "origin_not_allowed"}), 403

        auth = request.headers.get("Authorization", "")
        token = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
        if not token:
            return _unauthorized("Bearer 토큰이 필요합니다")
        grant = _store().validate_access(token, resource=mcp_config.resource_id(c))
        if grant is None:
            return _unauthorized("토큰이 유효하지 않거나 만료되었습니다",
                                 error="invalid_token")

        raw = request.get_data(as_text=True)
        try:
            payload = json.loads(raw) if raw.strip() else None
        except json.JSONDecodeError as e:
            return _rpc_error(None, -32700, f"Parse error: {e.msg}", 400)
        if payload is None:
            return _rpc_error(None, -32600, "Invalid Request", 400)

        batch = isinstance(payload, list)
        messages = payload if batch else [payload]
        if not messages or any(not isinstance(m, dict) for m in messages):
            return _rpc_error(None, -32600, "Invalid Request", 400)

        responses = []
        for msg in messages:
            _m = msg.get("method")
            if _m in ("tools/list", "tools/call", "initialize"):     # 커넥터가 도구 목록을 다시 받았는지 보려면 이 줄을 grep
                logger.info("mcp %s %s", _m, (msg.get("params") or {}).get("name", "") if _m == "tools/call" else "")
            try:
                resp = mcp_server.handle(msg)
            except Exception as e:  # noqa: BLE001
                logger.warning("handle 예외: %r", e)
                resp = {"jsonrpc": "2.0", "id": msg.get("id"),
                        "error": {"code": -32603, "message": f"Internal error: {e}"}}
            if resp is not None:
                responses.append(resp)

        if not responses:
            return Response(status=202)   # 알림만 있는 요청
        body = responses if batch else responses[0]
        return app.response_class(
            json.dumps(body, ensure_ascii=False), status=200,
            mimetype="application/json")

    @app.get("/mcp")
    def mcp_get_not_supported():
        resp = jsonify({"error": "method_not_allowed",
                        "error_description": "서버 발신 SSE 스트림은 지원하지 않습니다 — POST 를 쓰세요"})
        resp.status_code = 405
        resp.headers["Allow"] = "POST"
        return resp
