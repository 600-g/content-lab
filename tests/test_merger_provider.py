"""merge_with_existing() 프로바이더 순서 (v5.2): Claude(구독) → Gemini → Gemma. 네트워크·프로세스 0.

기존 스킬에 같은 URL/주제가 다시 들어오면 합병기가 본문을 다시 쓴다 — 여기가 Gemma 로 떨어지면
analyze() 를 Claude 로 올린 의미가 없다 (합병 결과가 최종본). Gemini 키가 없어도 Claude 로 합병된다.
"""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

from scripts.analyzer import merger
from scripts.analyzer.gemini import AnalysisResult

BODY = "## 이게 뭔가요?\n" + "합병 본문 " * 600
MERGED = ('{"skill_name": "old-slug", "skill_title_ko": "합병된 스킬", "callout": "**핵심** 한 줄", '
          '"category": "개발", "grade": "A", "grade_reason": "r", "difficulty": "중급", "ai_tools": ["Claude"], '
          '"targets": [], "summary": "s", "when_to_use": "w", "memo": "m", "tags": [], '
          '"body_md": "' + BODY.replace("\n", "\\n") + '"}')
EXISTING = {"name": "old-slug", "category": "개발", "grade": "B", "body": "기존 본문 " * 200,
            "source_urls": ["https://a.example/1"], "collected_at": "2026-09-13"}


def _new() -> AnalysisResult:
    body = "신규 본문 " * 300
    return AnalysisResult(skill_name="new-slug", skill_title_ko="신규", category="개발", grade="A",
                          grade_reason="", targets=[], summary="", when_to_use="", memo="", ai_tools=[],
                          tags=[], difficulty="중급", callout="c", body_md=body, body_content=body,
                          raw={"body_md": body})


class MergeChainTest(unittest.TestCase):
    def _run(self, *, claude, gemini_text="", gemma_text="", gemini_key=True):
        fake_model = mock.Mock()
        fake_model.generate_content.return_value = mock.Mock(text=gemini_text)
        fake_genai = mock.Mock()
        fake_genai.GenerativeModel.return_value = fake_model
        claude_mock = mock.Mock(return_value=claude)
        gemma_mock = mock.Mock(return_value=gemma_text)
        with mock.patch.dict(sys.modules, {"google.generativeai": fake_genai}), \
             mock.patch.dict(os.environ, {"GEMINI_API_KEY": "k"}), \
             mock.patch.object(merger, "_parse_existing_skill_md", return_value=dict(EXISTING)), \
             mock.patch.object(merger, "call_claude_json", claude_mock), \
             mock.patch.object(merger, "call_gemma_json", gemma_mock), \
             mock.patch.object(merger, "_quota_should_skip", return_value=False), \
             mock.patch.object(merger, "_quota_increment"):
            if not gemini_key:
                os.environ.pop("GEMINI_API_KEY", None)
            res = merger.merge_with_existing(Path("/nonexistent/SKILL.md"), _new(), "https://b.example/2", "web")
        return res, claude_mock, fake_model, gemma_mock

    def test_claude_merge_skips_gemini_and_gemma(self):
        res, claude, gem_model, gemma = self._run(claude=MERGED, gemini_text=MERGED)
        self.assertEqual(res.provider, "claude")
        self.assertEqual(res.skill_name, "old-slug", "슬러그는 기존 것 유지")
        self.assertTrue(res.raw.get("_is_merged"))
        self.assertEqual(res.raw.get("_merged_source_urls"), ["https://a.example/1", "https://b.example/2"])
        self.assertEqual(gem_model.generate_content.call_count, 0)
        self.assertEqual(gemma.call_count, 0)
        self.assertEqual(claude.call_count, 1)
        self.assertIn("schema", claude.call_args.kwargs, "합병도 --json-schema 로 enum 강제")

    def test_claude_none_falls_to_gemini(self):
        res, claude, gem_model, gemma = self._run(claude=None, gemini_text=MERGED)
        self.assertTrue(res.raw.get("_is_merged"))
        self.assertTrue(res.provider.startswith("gemini"), res.provider)
        self.assertEqual(gem_model.generate_content.call_count, 1)

    def test_no_gemini_key_still_merges_via_claude(self):
        res, *_ = self._run(claude=MERGED, gemini_key=False)
        self.assertTrue(res.raw.get("_is_merged"), "종전엔 키 없으면 합병 없이 신규 결과로 덮어썼다")
        self.assertEqual(res.provider, "claude")

    def test_all_fail_returns_new_result_unchanged(self):
        res, *_ = self._run(claude=None, gemini_text="", gemma_text="")
        self.assertEqual(res.skill_name, "new-slug")
        self.assertFalse(res.raw.get("_is_merged"))


if __name__ == "__main__":
    unittest.main()
