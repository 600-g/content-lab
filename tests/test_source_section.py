"""'## 출처' 이중 출력 근절 (v5.3.1) — 모델이 body_md 에 출처 섹션을 넣으면 렌더러가 또 붙여 두 개가 된다.

실측 2026-09-18: 라이브러리 119건 중 73건이 `## 출처` 를 두 번 갖고 있었다. 프롬프트로 막는 건 불안정하므로
렌더러가 본문 속 출처 섹션을 떼고 자기 것 하나만 붙인다. 기존 파일은 repair.dedupe_source_sections 로 정리.
"""
from __future__ import annotations

import unittest

from scripts.analyzer.gemini import AnalysisResult
from scripts.skill_builder import md_generator
from scripts.library import repair

BODY_WITH_SOURCE = (
    "## 이게 뭔가요?\n본문\n\n## 따라하기\n1. 하나\n\n## 출처\n[원문 제목](https://example.com/a)\n"
)


def _res(body: str) -> AnalysisResult:
    return AnalysisResult(skill_name="s", skill_title_ko="제목", category="개발", grade="A", grade_reason="",
                          targets=[], summary="", when_to_use="", memo="", ai_tools=[], tags=[], difficulty="초급",
                          callout="콜아웃", body_md=body, body_content=body, raw={"body_md": body})


class StripInBodyTest(unittest.TestCase):
    def test_source_section_in_body_is_removed_before_render(self):
        md = md_generator.render_skill_md(_res(BODY_WITH_SOURCE), "https://example.com/a", "web")
        self.assertEqual(md.count("## 출처"), 1)
        self.assertIn("https://example.com/a", md.split("## 출처", 1)[1], "렌더러의 출처 섹션만 남는다")
        self.assertIn("## 따라하기\n1. 하나", md, "출처 앞 본문은 그대로")

    def test_source_section_in_the_middle_is_also_removed(self):
        body = "## 이게 뭔가요?\n본문\n\n## 출처\n- https://x\n\n## 주의사항\n조심\n"
        out = md_generator._strip_source_section(body)
        self.assertNotIn("## 출처", out)
        self.assertIn("## 주의사항\n조심", out)

    def test_body_without_source_is_untouched(self):
        body = "## 이게 뭔가요?\n본문\n"
        self.assertEqual(md_generator._strip_source_section(body), body)


class RepairExistingFilesTest(unittest.TestCase):
    DOUBLED = (
        "---\nname: s\nsources:\n  - https://example.com/a\n---\n\n# 제목\n\n💡 콜아웃\n\n## 이게 뭔가요?\n본문\n\n"
        "## 출처\n[원문](https://example.com/a)\n\n## 출처\n\n- [https://example.com/a](https://example.com/a)\n"
    )

    def test_keeps_only_the_last_section(self):
        out = repair.dedupe_source_sections(self.DOUBLED)
        self.assertEqual(out.count("## 출처"), 1)
        self.assertTrue(out.rstrip().endswith("- [https://example.com/a](https://example.com/a)"))
        self.assertIn("## 이게 뭔가요?\n본문", out)

    def test_single_section_is_untouched_and_idempotent(self):
        once = repair.dedupe_source_sections(self.DOUBLED)
        self.assertEqual(repair.dedupe_source_sections(once), once)
        single = "---\nname: s\n---\n\n# 제목\n\n본문\n\n## 출처\n\n- https://x\n"
        self.assertEqual(repair.dedupe_source_sections(single), single)


if __name__ == "__main__":
    unittest.main()
