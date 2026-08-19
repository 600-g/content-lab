"""채팅용 Flask 엔드포인트. app.py 가 register_chat_routes(app) 으로 등록."""
from __future__ import annotations

import logging

from flask import jsonify, request

from scripts.chat import engine, history, safety

logger = logging.getLogger(__name__)


def register_chat_routes(app) -> None:
    @app.route("/api/chat/status", methods=["GET"])
    def chat_status():
        prov = engine.provider()
        return jsonify({
            "ok": True,
            "configured": safety.is_configured(),
            "provider": prov,                       # anthropic | gemini | none
            "key_present": prov != "none",
        })

    @app.route("/api/chat/pin", methods=["POST"])
    def chat_pin():
        data = request.get_json(silent=True) or {}
        pin = str(data.get("pin", ""))
        ok, token, reason = safety.verify_pin(pin)
        if not ok:
            return jsonify({"ok": False, "error": reason}), 401
        return jsonify({"ok": True, "session_token": token})

    @app.route("/api/chat/message", methods=["POST"])
    def chat_message():
        data = request.get_json(silent=True) or {}
        text = str(data.get("text", "")).strip()
        token = data.get("session_token") or None
        if not text:
            return jsonify({"ok": False, "error": "빈 메시지"}), 400
        result = engine.chat_turn(text, session_token=token)
        status = 200 if result.get("ok") else 500
        return jsonify(result), status

    @app.route("/api/chat/history", methods=["GET"])
    def chat_history():
        # PIN 세션 게이트 — 헤더 또는 쿼리로 토큰 전달. 미인증 시 401.
        token = (
            request.headers.get("X-Session-Token")
            or request.args.get("session_token")
            or ""
        )
        if not safety.check_session(token):
            return jsonify({"ok": False, "error": "PIN 세션 필요"}), 401
        try:
            limit = int(request.args.get("limit", 50))
        except Exception:
            limit = 50
        return jsonify({"ok": True, "items": history.tail_history(limit)})

    @app.route("/api/chat/audit", methods=["GET"])
    def chat_audit():
        try:
            limit = int(request.args.get("limit", 50))
        except Exception:
            limit = 50
        return jsonify({"ok": True, "items": history.tail_audit(limit)})

    @app.route("/api/fix/status", methods=["GET"])
    def fix_status():
        try:
            from scripts.chat import fixer
            return jsonify(fixer.fix_status(limit=5))
        except Exception as e:  # noqa: BLE001
            logger.warning("fix_status 실패: %s", e)
            return jsonify({"ok": False, "error": str(e)}), 500


def _anthropic_key_present() -> bool:
    import os
    return bool(os.getenv("ANTHROPIC_API_KEY", "").strip())
