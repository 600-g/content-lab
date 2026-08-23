"""scripts.chat.engine — 실시간 스트리밍 / 스키마 정규화 / 대화 세션 테스트.

CLI 를 실제로 띄우지 않는다 (구독 한도 소모 방지) — 파서와 이벤트 프로토콜만 검증.
"""
from __future__ import annotations

import unittest

from scripts.chat import engine


class CliNormalizeTest(unittest.TestCase):
    """모델이 structured output 스키마를 살짝 어겨도 답을 건져야 한다 (모두 실측 케이스)."""

    def test_reply_nested_in_args(self):
        # 실사고: 인사 한 마디가 "(응답 필드 누락)" 으로 뜨던 원인
        reply, tool, args = engine.cli_normalize({"args": {"reply": "안녕하세요"}})
        self.assertEqual(reply, "안녕하세요")
        self.assertEqual(tool, "")
        self.assertEqual(args, {})

    def test_structured_output_name_is_not_a_tool(self):
        # tool 칸에 출력도구 이름을 적으면 예전엔 '알 수 없는 도구' 로 8라운드를 태웠다
        reply, tool, _ = engine.cli_normalize({"reply": "답", "tool": "StructuredOutput"})
        self.assertEqual(reply, "답")
        self.assertEqual(tool, "")

    def test_unknown_tool_name_ignored(self):
        _, tool, _ = engine.cli_normalize({"tool": "rm_rf_everything", "args": {}})
        self.assertEqual(tool, "")

    def test_args_flattened_to_top_level(self):
        _, tool, args = engine.cli_normalize({"tool": "recent_jobs", "limit": 3})
        self.assertEqual(tool, "recent_jobs")
        self.assertEqual(args, {"limit": 3})

    def test_normal_shape_passes_through(self):
        _, tool, args = engine.cli_normalize({"tool": "recent_jobs", "args": {"limit": 5}})
        self.assertEqual((tool, args), ("recent_jobs", {"limit": 5}))

    def test_garbage_is_safe(self):
        self.assertEqual(engine.cli_normalize(None), ("", "", {}))
        self.assertEqual(engine.cli_normalize({}), ("", "", {}))


class PartialReplyTest(unittest.TestCase):
    """input_json_delta 조각에서 reply 만큼만 뽑아내야 토큰 스트리밍이 된다."""

    def test_mid_string(self):
        self.assertEqual(engine.partial_reply('{"args": {}, "reply": "안녕하'), "안녕하")

    def test_escapes(self):
        self.assertEqual(engine.partial_reply(r'{"reply": "1\n2\"3'), '1\n2"3')

    def test_unicode_escape(self):
        self.assertEqual(engine.partial_reply(r'{"reply": "가'), "가")

    def test_nested_reply_also_streams(self):
        self.assertEqual(engine.partial_reply('{"args": {"reply": "안녕'), "안녕")

    def test_before_reply_key_arrives(self):
        self.assertEqual(engine.partial_reply('{"args": {}'), "")

    def test_complete_value_stops_at_quote(self):
        self.assertEqual(engine.partial_reply('{"reply": "끝", "tool": "x"}'), "끝")


class ConversationSessionTest(unittest.TestCase):
    """conv_id → CLI 세션(--resume) 매핑 — 멀티턴 기억의 저장소."""

    def setUp(self):
        engine.CLI_SESSIONS.clear()

    tearDown = setUp

    def test_remember_and_read(self):
        engine._conv_remember("conv-a", "sid-1")
        self.assertEqual(engine._conv_sid("conv-a"), "sid-1")

    def test_unknown_conv(self):
        self.assertIsNone(engine._conv_sid("nope"))

    def test_rejects_bad_conv_id(self):
        engine._conv_remember("../../etc/passwd", "sid-x")
        self.assertEqual(engine.CLI_SESSIONS, {})
        self.assertIsNone(engine._conv_sid("../../etc/passwd"))

    def test_expired_session_dropped(self):
        engine._conv_remember("conv-b", "sid-2")
        engine.CLI_SESSIONS["conv-b"]["ts"] -= engine.CLI_SESSION_TTL + 10
        self.assertIsNone(engine._conv_sid("conv-b"))
        self.assertNotIn("conv-b", engine.CLI_SESSIONS)

    def test_forget_conversation(self):
        engine._conv_remember("conv-c", "sid-3")
        self.assertTrue(engine.forget_conversation("conv-c"))
        self.assertFalse(engine.forget_conversation("conv-c"))


class ChatStreamProtocolTest(unittest.TestCase):
    """SSE 이벤트 순서 — 상태 → 도구 → 응답 조각 → done."""

    def test_events_forwarded_in_order(self):
        def fake_turn(user_text, *, session_token, conv_id, on_event):
            on_event({"type": "status", "text": "생각 중…"})
            on_event({"type": "tool", "phase": "start", "name": "recent_jobs"})
            on_event({"type": "tool", "phase": "end", "name": "recent_jobs", "ok": True, "summary": "s"})
            on_event({"type": "delta", "text": "안녕"})
            return {"ok": True, "reply": "안녕", "tool_calls": [{"name": "recent_jobs", "ok": True}],
                    "provider": "claude_cli"}

        original = engine.chat_turn
        engine.chat_turn = fake_turn
        try:
            evs = list(engine.chat_stream("hi", conv_id="c1"))
        finally:
            engine.chat_turn = original
        kinds = [e["type"] for e in evs if e["type"] != "ping"]
        self.assertEqual(kinds, ["status", "tool", "tool", "delta", "done"])
        self.assertEqual(evs[-1]["reply"], "안녕")

    def test_failure_becomes_error_event(self):
        def boom(user_text, *, session_token, conv_id, on_event):
            raise RuntimeError("CLI 한도 도달")

        original = engine.chat_turn
        engine.chat_turn = boom
        try:
            evs = [e for e in engine.chat_stream("hi") if e["type"] != "ping"]
        finally:
            engine.chat_turn = original
        self.assertEqual(evs[-1]["type"], "error")
        self.assertIn("한도", evs[-1]["message"])


if __name__ == "__main__":
    unittest.main()
