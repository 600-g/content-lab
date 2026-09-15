"""등급 C 도 등록한다 (v5.3) — 등급은 활용도이지 소장 가치가 아니다 (네트워크 0, LLM 0).

v5.2 까지는 C 판정이면 "DB 에 안 올라감" 으로 파이프라인이 끝났다. 사용자 원칙: 내가 준 건 다 소장 가치가
있다, C 는 활용도가 낮다는 표시일 뿐. 실사고 2026-09-14 ai-office 가 C 판정으로 사라질 뻔했다.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from scripts import collect as collect_mod
from scripts.analyzer.gemini import AnalysisResult
from scripts.scraper.router import ScrapeResult

LONG = "AI Office 대시보드 8종 소개. " * 60


def _c_result(d):
    body = "## 이게 뭔가요?\n" + LONG
    return AnalysisResult(skill_name="ai-office-list", skill_title_ko="AI 오피스 기능 목록", category="업무", grade="C",
                          grade_reason="기능명 나열뿐 절차 없음", targets=[], summary="", when_to_use="", memo="",
                          ai_tools=[], tags=[], difficulty="초급", callout="c", body_md=body, body_content=body,
                          raw={"body_md": body}, provider="claude")


class GradeCStillRegistersTest(unittest.TestCase):
    def test_grade_c_goes_through_install(self):
        scr = ScrapeResult(url="https://example.com/x", source_type="web", title="t", text=LONG, meta={})
        with mock.patch.object(collect_mod, "scrape", return_value=scr), \
             mock.patch.object(collect_mod, "analyze", side_effect=_c_result), \
             mock.patch.object(collect_mod, "find_global_by_slug", return_value=None), \
             mock.patch.object(collect_mod, "find_mirror_by_slug", return_value=None), \
             mock.patch.object(collect_mod, "find_existing_by_url", return_value=None), \
             mock.patch("scripts.analyzer.dedup_finder.find_semantic_candidates", return_value=[]), \
             mock.patch.object(collect_mod, "render_skill_md", return_value="md"), \
             mock.patch.object(collect_mod, "install_skill", return_value=(Path("/tmp/g/SKILL.md"), True)) as inst, \
             mock.patch.object(collect_mod, "mirror_skill", return_value=Path("/tmp/m/SKILL.md")), \
             mock.patch("scripts.analyzer.embedder.get_or_embed", return_value=None):
            r = collect_mod.collect("https://example.com/x", register_notion=False)
        self.assertTrue(r["ok"], r)
        inst.assert_called_once()
        self.assertTrue(r["stages"]["install"]["ok"])
        self.assertIn("C", r["stages"]["analyze"]["grade"])
        self.assertIn("참고", r["stages"]["analyze"]["note"], "C 는 '참고용' 이지 '활용 불가' 가 아니다")
        self.assertNotIn("안 올라감", r.get("message_ko", ""))


if __name__ == "__main__":
    unittest.main()
