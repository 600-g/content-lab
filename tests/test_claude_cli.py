"""analyzer/claude_cli — claude -p (구독 계정) 를 분석 프로바이더로 쓰는 얇은 래퍼 (네트워크·프로세스 0).

runner 를 주입해 명령줄 구성 · envelope 파싱 · 한도 도달 쿨다운 · 파일 판독 경로를 검증한다.
"""
from __future__ import annotations

import json
import os
import subprocess
import unittest
from unittest import mock

from scripts.analyzer import claude_cli as cc


def _env(structured=None, result="", is_error=False) -> str:
    e = {"type": "result", "is_error": is_error, "result": result, "num_turns": 1}
    if structured is not None:
        e["structured_output"] = structured
    return json.dumps(e, ensure_ascii=False)


class FakeRunner:
    def __init__(self, stdout="", rc=0, stderr="", raise_timeout=False):
        self.calls: list[dict] = []
        self.stdout, self.rc, self.stderr, self.raise_timeout = stdout, rc, stderr, raise_timeout
        self.seen_files = None

    def __call__(self, cmd, *, cwd, timeout):
        self.calls.append({"cmd": cmd, "cwd": cwd, "timeout": timeout})
        try:
            self.seen_files = sorted(os.listdir(cwd))
        except OSError:
            self.seen_files = None
        if self.raise_timeout:
            raise subprocess.TimeoutExpired(cmd, timeout)
        return self.rc, self.stdout, self.stderr


class Base(unittest.TestCase):
    def setUp(self):
        cc.reset_pause()
        self._env = mock.patch.dict("os.environ", {"ANALYZER_CLAUDE": "1"})
        self._env.start()
        self._bin = mock.patch.object(cc, "_binary", return_value="/opt/homebrew/bin/claude")
        self._bin.start()

    def tearDown(self):
        self._bin.stop()
        self._env.stop()
        cc.reset_pause()


class JsonCallTest(Base):
    def test_cmd_blocks_tools_settings_and_uses_schema(self):
        r = FakeRunner(_env(structured={"a": 1}))
        cc.call_claude_json("프롬프트", schema={"type": "object"}, runner=r)
        cmd = r.calls[0]["cmd"]
        self.assertEqual(cmd[-2:], ["-p", "프롬프트"])
        for flag in ("--strict-mcp-config", "--disable-slash-commands", "--json-schema"):
            self.assertIn(flag, cmd, flag)
        self.assertEqual(cmd[cmd.index("--tools") + 1], "", "도구 전부 차단 — 순수 생성 호출")
        self.assertEqual(cmd[cmd.index("--setting-sources") + 1], "", "글로벌 CLAUDE.md/스킬 로드 차단")
        self.assertEqual(cmd[cmd.index("--output-format") + 1], "json")
        self.assertEqual(cmd[cmd.index("--model") + 1], "claude-sonnet-5")
        self.assertNotIn("--bare", cmd)   # gotcha 19 — OAuth 무시

    def test_structured_output_is_returned_as_json_text(self):
        r = FakeRunner(_env(structured={"skill_name": "x", "grade": "A"}))
        out = cc.call_claude_json("p", schema={"type": "object"}, runner=r)
        self.assertEqual(json.loads(out), {"skill_name": "x", "grade": "A"})

    def test_result_text_is_used_when_no_structured_output(self):
        r = FakeRunner(_env(result='{"skill_name": "y"}'))
        self.assertEqual(cc.call_claude_json("p", runner=r), '{"skill_name": "y"}')

    def test_usage_limit_pauses_further_calls(self):
        r = FakeRunner(_env(result="You've hit your usage limit. Resets at 3pm", is_error=True))
        self.assertIsNone(cc.call_claude_json("p", runner=r))
        self.assertTrue(cc.is_paused())
        self.assertIsNone(cc.call_claude_json("p", runner=r))
        self.assertEqual(len(r.calls), 1, "쿨다운 중엔 프로세스를 띄우지 않는다")

    def test_other_error_does_not_pause(self):
        r = FakeRunner(_env(result="Not logged in · Please run /login", is_error=True))
        self.assertIsNone(cc.call_claude_json("p", runner=r))
        self.assertFalse(cc.is_paused())

    def test_nonzero_exit_and_garbage_stdout_return_none(self):
        self.assertIsNone(cc.call_claude_json("p", runner=FakeRunner("not json", rc=1)))
        self.assertIsNone(cc.call_claude_json("p", runner=FakeRunner("", rc=0)))

    def test_timeout_returns_none(self):
        self.assertIsNone(cc.call_claude_json("p", runner=FakeRunner(raise_timeout=True)))

    def test_disabled_by_env_skips_process(self):
        r = FakeRunner(_env(structured={"a": 1}))
        with mock.patch.dict("os.environ", {"ANALYZER_CLAUDE": "0"}):
            self.assertIsNone(cc.call_claude_json("p", runner=r))
        self.assertEqual(r.calls, [])

    def test_missing_binary_skips_process(self):
        r = FakeRunner(_env(structured={"a": 1}))
        with mock.patch.object(cc, "_binary", return_value=None):
            self.assertIsNone(cc.call_claude_json("p", runner=r))
        self.assertEqual(r.calls, [])


class ReadFilesTest(Base):
    def test_files_are_written_into_cwd_and_only_read_tool_is_allowed(self):
        r = FakeRunner(_env(result="슬라이드 1: Komi Store"))
        out = cc.call_claude_read_files("판독", [("slide_1.jpg", b"jpg"), ("slide_2.png", b"png")], runner=r)
        self.assertEqual(out, "슬라이드 1: Komi Store")
        self.assertEqual(r.seen_files, ["slide_1.jpg", "slide_2.png"], "작업 폴더엔 판독할 파일만 있어야 한다")
        cmd = r.calls[0]["cmd"]
        self.assertEqual(cmd[cmd.index("--tools") + 1], "Read")
        self.assertEqual(cmd[cmd.index("--allowedTools") + 1], "Read")
        self.assertIn("--max-turns", cmd)
        self.assertIn("slide_1.jpg", cmd[-1])
        self.assertIn("slide_2.png", cmd[-1])
        self.assertFalse(os.path.exists(r.calls[0]["cwd"]), "임시 폴더는 호출 후 지운다")

    def test_path_traversal_in_names_is_neutralised(self):
        r = FakeRunner(_env(result="ok"))
        cc.call_claude_read_files("판독", [("../../evil.jpg", b"x")], runner=r)
        self.assertEqual(r.seen_files, ["evil.jpg"])

    def test_temp_dir_is_removed_even_on_failure(self):
        r = FakeRunner(raise_timeout=True)
        self.assertIsNone(cc.call_claude_read_files("판독", [("a.jpg", b"x")], runner=r))
        self.assertFalse(os.path.exists(r.calls[0]["cwd"]))

    def test_limit_pauses_read_calls_too(self):
        r = FakeRunner(_env(result="usage limit reached", is_error=True))
        self.assertIsNone(cc.call_claude_read_files("판독", [("a.jpg", b"x")], runner=r))
        self.assertTrue(cc.is_paused())


class SchemaTest(unittest.TestCase):
    def test_skill_schema_enums_match_prompt(self):
        from scripts.analyzer.prompt import GRADES, CATEGORIES, DIFFICULTIES
        p = cc.SKILL_SCHEMA["properties"]
        self.assertEqual(p["grade"]["enum"], GRADES)
        self.assertEqual(p["category"]["enum"], CATEGORIES)
        self.assertEqual(p["difficulty"]["enum"], DIFFICULTIES)
        for k in ("skill_name", "skill_title_ko", "callout", "body_md"):
            self.assertIn(k, cc.SKILL_SCHEMA["required"])
        self.assertNotIn("oneOf", json.dumps(cc.SKILL_SCHEMA))   # gotcha 20


if __name__ == "__main__":
    unittest.main()
