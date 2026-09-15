"""의미 중복 최종 확인 (_confirm_semantic_merge) 도 Claude 우선 (v5.3, 네트워크·프로세스 0).

합병 여부를 가르는 판정이라 품질이 곧 라이브러리 구조다. Claude 가 None 이면 종전대로 Gemma.
사용자 원칙: 정확히 유사 + 카테고리 겹침이면 합친다 — 프롬프트에 두 카테고리를 넣어 근거로 쓰게 한다.
"""
from __future__ import annotations

import logging
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import collect as collect_mod
from scripts.analyzer.gemini import AnalysisResult

CAND = """---
name: existing-skill
description: 기존 설명
origin: content-lab
grade: A
difficulty: 초급
category: 디자인
ai_tools: ["Claude"]
sources:
  - https://example.com/e
---

# 기존 제목

본문
"""


def _new() -> AnalysisResult:
    return AnalysisResult(skill_name="new-skill", skill_title_ko="신규 제목", category="디자인", grade="S", grade_reason="",
                          targets=[], summary="", when_to_use="", memo="", ai_tools=[], tags=[], difficulty="초급",
                          callout="신규 콜아웃", body_md="b", body_content="b", raw={})


class ConfirmSemanticMergeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cand = Path(self.tmp.name) / "SKILL.md"; self.cand.write_text(CAND, encoding="utf-8")
        self.log = logging.getLogger("t")

    def tearDown(self):
        self.tmp.cleanup()

    def test_claude_verdict_is_used_and_gemma_not_called(self):
        with mock.patch.object(collect_mod, "call_claude_json", return_value='{"same": true, "reason": "같은 대상"}') as c, \
             mock.patch("scripts.analyzer.gemini.call_gemma_json") as g:
            same = collect_mod._confirm_semantic_merge(_new(), "existing-skill", self.cand, self.log)
        self.assertTrue(same); g.assert_not_called()
        prompt = c.call_args.args[0]
        self.assertIn("디자인", prompt, "두 카테고리를 판정 근거로 넘긴다")
        self.assertIn("schema", c.call_args.kwargs)

    def test_falls_back_to_gemma_when_claude_none(self):
        with mock.patch.object(collect_mod, "call_claude_json", return_value=None), \
             mock.patch("scripts.analyzer.gemini.call_gemma_json", return_value='{"same": false, "reason": "다름"}') as g:
            same = collect_mod._confirm_semantic_merge(_new(), "existing-skill", self.cand, self.log)
        self.assertFalse(same); g.assert_called_once()

    def test_both_unavailable_is_conservative_no_merge(self):
        with mock.patch.object(collect_mod, "call_claude_json", return_value=None), \
             mock.patch("scripts.analyzer.gemini.call_gemma_json", return_value=None):
            self.assertFalse(collect_mod._confirm_semantic_merge(_new(), "existing-skill", self.cand, self.log))


if __name__ == "__main__":
    unittest.main()
