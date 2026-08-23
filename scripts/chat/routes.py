"""채팅용 Flask 엔드포인트. app.py 가 register_chat_routes(app) 으로 등록."""
from __future__ import annotations

import json
import logging

from flask import Response, jsonify, request, stream_with_context

from scripts.chat import engine, history, safety

logger = logging.getLogger(__name__)


def register_chat_routes(app) -> None:
    @app.route("/api/chat/status", methods=["GET"])
    def chat_status():
        prov = engine.provider()
        return jsonify({
            "ok": True,
            "configured": safety.is_configured(),
            "provider": prov,                       # claude_cli | anthropic | gemini | ollama | none
            "key_present": prov != "none",
            "model_label": engine.model_label(prov),
            "streaming": True,
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
        conv_id = str(data.get("conv_id") or "") or None
        if not text:
            return jsonify({"ok": False, "error": "빈 메시지"}), 400
        result = engine.chat_turn(text, session_token=token, conv_id=conv_id)
        status = 200 if result.get("ok") else 500
        return jsonify(result), status

    @app.route("/api/chat/stream", methods=["POST"])
    def chat_stream_route():
        """실시간 채팅 — SSE. 한 줄씩 흘려서 '생각 중 → 도구 → 답변'이 즉시 보인다.

        일반 fetch(POST) + ReadableStream 으로 읽는다 (EventSource 는 GET 전용이라 못 씀).
        """
        data = request.get_json(silent=True) or {}
        text = str(data.get("text", "")).strip()
        token = data.get("session_token") or None
        conv_id = str(data.get("conv_id") or "") or None
        if not text:
            return jsonify({"ok": False, "error": "빈 메시지"}), 400

        def gen():
            # 프록시(CF 터널) 가 첫 바이트를 기다리며 버퍼링하지 않게 즉시 한 줄.
            yield ": open\n\n"
            try:
                for ev in engine.chat_stream(text, session_token=token, conv_id=conv_id):
                    yield "data: " + json.dumps(ev, ensure_ascii=False) + "\n\n"
            except GeneratorExit:      # 클라이언트가 [중지] — 조용히 종료
                raise
            except Exception as e:     # noqa: BLE001
                logger.exception("chat stream 실패")
                yield "data: " + json.dumps(
                    {"type": "error", "message": str(e)}, ensure_ascii=False) + "\n\n"

        return Response(
            stream_with_context(gen()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    @app.route("/api/chat/reset", methods=["POST"])
    def chat_reset():
        """'새 대화' — CLI 세션을 끊어 다음 턴부터 맥락을 새로 시작."""
        data = request.get_json(silent=True) or {}
        conv_id = str(data.get("conv_id") or "") or None
        return jsonify({"ok": True, "cleared": engine.forget_conversation(conv_id)})

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
