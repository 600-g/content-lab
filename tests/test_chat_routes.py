"""scripts.chat.routes — SSE 스트림 / 새 대화 엔드포인트 (Flask test client, 네트워크 0)."""
from __future__ import annotations

import json
import unittest

from flask import Flask

from scripts.chat import engine, routes


def _app() -> Flask:
    app = Flask(__name__)
    routes.register_chat_routes(app)
    return app


class ChatStreamRouteTest(unittest.TestCase):
    def setUp(self):
        self.app = _app()
        self.client = self.app.test_client()
        self._orig = engine.chat_stream

    def tearDown(self):
        engine.chat_stream = self._orig

    def _events(self, body: bytes) -> list[dict]:
        out = []
        for block in body.decode("utf-8").split("\n\n"):
            if block.startswith("data:"):
                out.append(json.loads(block[5:].strip()))
        return out

    def test_stream_emits_sse_frames(self):
        def fake(text, *, session_token=None, conv_id=None):
            yield {"type": "status", "text": "생각 중…"}
            yield {"type": "delta", "text": "안녕"}
            yield {"type": "done", "reply": "안녕", "tool_calls": [], "provider": "claude_cli"}

        engine.chat_stream = fake
        r = self.client.post("/api/chat/stream", json={"text": "hi", "conv_id": "c1"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.mimetype.startswith("text/event-stream"))
        self.assertEqual(r.headers.get("X-Accel-Buffering"), "no")   # 프록시 버퍼링 차단
        body = r.get_data()
        self.assertTrue(body.startswith(b": open"))                  # 첫 바이트 즉시 flush
        self.assertEqual([e["type"] for e in self._events(body)], ["status", "delta", "done"])

    def test_conv_id_and_token_passed_through(self):
        seen = {}

        def fake(text, *, session_token=None, conv_id=None):
            seen.update({"text": text, "token": session_token, "conv": conv_id})
            yield {"type": "done", "reply": "ok", "tool_calls": []}

        engine.chat_stream = fake
        r = self.client.post("/api/chat/stream",
                             json={"text": "안녕", "session_token": "tok", "conv_id": "abc"})
        r.get_data()   # 제너레이터는 소비돼야 실행된다 (스트리밍 응답)
        self.assertEqual(seen, {"text": "안녕", "token": "tok", "conv": "abc"})

    def test_empty_message_rejected(self):
        r = self.client.post("/api/chat/stream", json={"text": "   "})
        self.assertEqual(r.status_code, 400)

    def test_engine_failure_becomes_error_frame(self):
        def fake(text, *, session_token=None, conv_id=None):
            raise RuntimeError("터졌다")
            yield  # pragma: no cover

        engine.chat_stream = fake
        r = self.client.post("/api/chat/stream", json={"text": "hi"})
        evs = self._events(r.get_data())
        self.assertEqual(evs[-1]["type"], "error")
        self.assertIn("터졌다", evs[-1]["message"])


class ChatResetRouteTest(unittest.TestCase):
    def setUp(self):
        self.client = _app().test_client()
        engine.CLI_SESSIONS.clear()

    tearDown = setUp

    def test_reset_clears_cli_session(self):
        engine._conv_remember("abc", "sid-9")
        r = self.client.post("/api/chat/reset", json={"conv_id": "abc"})
        self.assertEqual(r.get_json(), {"ok": True, "cleared": True})
        self.assertIsNone(engine._conv_sid("abc"))

    def test_reset_unknown_conv_is_ok(self):
        r = self.client.post("/api/chat/reset", json={"conv_id": "nope"})
        self.assertEqual(r.get_json(), {"ok": True, "cleared": False})


if __name__ == "__main__":
    unittest.main()
