"""analyze() 프로바이더 순서 (v5.2): Claude(구독 claude -p) → Gemini → Gemma. 네트워크·프로세스 0.

Claude 가 성공하면 Gemini 는 호출조차 안 된다 (하루 20회 쿼터 보존). Claude 가 None 이면
(비활성·한도·타임아웃) 기존 체인이 그대로 돈다. Gemini 키가 없어도 Claude 로 분석된다.
검증 재요청은 1차가 Claude 였으면 Claude 로 (Gemma 로 품질 강등 X), Claude 가 막히면 Gemma.
"""
from __future__ import annotations

import os
import unittest
from unittest import mock

from scripts.analyzer import gemini

GOOD = ('{"skill_name": "x-skill", "skill_title_ko": "테스트 스킬", "callout": "**핵심** 한 줄", '
        '"category": "개발", "grade": "A", "grade_reason": "r", "difficulty": "중급", "ai_tools": ["Claude"], '
        '"body_md": "' + ("본문 " * 400) + '"}')
NO_CALLOUT = GOOD.replace('"callout": "**핵심** 한 줄", ', "")
SCRAPE = {"url": "https://example.com/a", "source_type": "web", "title": "제목", "text": "본문 " * 400, "meta": {}}


class ChainTest(unittest.TestCase):
    def _run(self, *, claude, gemini_text="", gemma_text="", gemini_key=True):
        fake_model = mock.Mock()
        fake_model.generate_content.return_value = mock.Mock(text=gemini_text)
        fake_genai = mock.Mock()
        fake_genai.GenerativeModel.return_value = fake_model
        claude_mock = mock.Mock(side_effect=claude if callable(claude) else (lambda *a, **k: claude))
        gemma_mock = mock.Mock(return_value=gemma_text)
        with mock.patch.dict("sys.modules", {"google.generativeai": fake_genai}), \
             mock.patch.dict("os.environ", {"GEMINI_API_KEY": "k"}), \
             mock.patch.object(gemini, "call_claude_json", claude_mock), \
             mock.patch.object(gemini, "call_gemma_json", gemma_mock), \
             mock.patch.object(gemini, "_quota_should_skip", return_value=False), \
             mock.patch.object(gemini, "_quota_increment"):
            if not gemini_key:
                os.environ.pop("GEMINI_API_KEY", None)
            res = gemini.analyze(SCRAPE)
        return res, claude_mock, fake_model, gemma_mock

    def test_claude_success_skips_gemini_and_gemma(self):
        res, claude, gem_model, gemma = self._run(claude=GOOD, gemini_text=GOOD)
        self.assertTrue(res.ok, res.error)
        self.assertEqual(res.provider, "claude")
        self.assertEqual(gem_model.generate_content.call_count, 0, "Claude 성공 시 Gemini 쿼터를 쓰지 않는다")
        self.assertEqual(gemma.call_count, 0)
        self.assertEqual(res.skill_name, "x-skill")
        self.assertEqual(res.callout, "**핵심** 한 줄")

    def test_claude_none_falls_to_gemini(self):
        res, claude, gem_model, gemma = self._run(claude=None, gemini_text=GOOD)
        self.assertTrue(res.ok, res.error)
        self.assertTrue(res.provider.startswith("gemini"), res.provider)
        self.assertEqual(gem_model.generate_content.call_count, 1)

    def test_claude_garbage_falls_to_gemini(self):
        res, *_ = self._run(claude="죄송합니다. 처리할 수 없습니다.", gemini_text=GOOD)
        self.assertTrue(res.ok, res.error)
        self.assertTrue(res.provider.startswith("gemini"), res.provider)

    def test_no_gemini_key_still_works_via_claude(self):
        res, *_ = self._run(claude=GOOD, gemini_key=False)
        self.assertTrue(res.ok, res.error)
        self.assertEqual(res.provider, "claude")

    def test_no_gemini_key_and_no_claude_falls_to_gemma(self):
        res, claude, gem_model, gemma = self._run(claude=None, gemma_text=GOOD, gemini_key=False)
        self.assertTrue(res.ok, res.error)
        self.assertEqual(res.provider, "gemma")

    def test_all_fail_reports_every_provider(self):
        res, *_ = self._run(claude=None, gemini_text="", gemma_text="")
        self.assertFalse(res.ok)
        for name in ("Claude", "Gemini", "Gemma"):
            self.assertIn(name, res.error)

    def test_validation_retry_stays_on_claude(self):
        calls = iter([NO_CALLOUT, GOOD])
        res, claude, gem_model, gemma = self._run(claude=lambda *a, **k: next(calls))
        self.assertTrue(res.ok, res.error)
        self.assertEqual(claude.call_count, 2)
        self.assertEqual(gemma.call_count, 0, "Claude 1차면 재요청도 Claude")
        self.assertEqual(res.callout, "**핵심** 한 줄")

    def test_validation_retry_uses_gemma_when_claude_limited_midway(self):
        calls = iter([NO_CALLOUT, None])
        res, claude, gem_model, gemma = self._run(claude=lambda *a, **k: next(calls), gemma_text=GOOD)
        self.assertTrue(res.ok, res.error)
        self.assertEqual(gemma.call_count, 1)
        self.assertEqual(res.callout, "**핵심** 한 줄")

    def test_provider_is_in_to_dict(self):
        res, *_ = self._run(claude=GOOD)
        self.assertEqual(res.to_dict()["provider"], "claude")


if __name__ == "__main__":
    unittest.main()
