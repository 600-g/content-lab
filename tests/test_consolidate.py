"""library/consolidate — 이미 등록된 스킬 두 개를 하나로 합친다 (네트워크·프로세스 0, merge 주입).

사용자 원칙 (2026-09-16): 정확히 유사하고 카테고리가 겹치면 합쳐 간소화. 흡수된 스킬은 백업 후 삭제,
출처 URL 은 합집합으로 보존. 합병 LLM 이 실패하면 아무것도 지우지 않는다.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.analyzer.gemini import AnalysisResult
from scripts.library import consolidate as cs

SKILL = """---
name: {slug}
description: 설명 {slug}
origin: content-lab
grade: A
difficulty: 초급
category: 개발
ai_tools: ["Claude"]
sources:
  - https://example.com/{slug}
---

# 제목 {slug}

💡 콜아웃 {slug}

## 이게 뭔가요?
본문 {slug} """ + ("내용 " * 300)


def _write(root: Path, slug: str) -> Path:
    p = root / slug / "SKILL.md"; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(SKILL.format(slug=slug), encoding="utf-8"); return p


def _merged(existing_path, new_result, url, src_type) -> AnalysisResult:
    body = "## 이게 뭔가요?\n합병 본문 " + ("내용 " * 400)
    r = AnalysisResult(skill_name="keeper", skill_title_ko="합쳐진 스킬", category="개발", grade="S", grade_reason="",
                       targets=[], summary="", when_to_use="", memo="", ai_tools=["Claude"], tags=[], difficulty="초급",
                       callout="합쳐진 콜아웃", body_md=body, body_content=body, raw={"body_md": body}, provider="claude")
    r.raw["_is_merged"] = True
    r.raw["_merged_source_urls"] = ["https://example.com/keeper", url]
    return r


class MergePairTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); d = Path(self.tmp.name)
        self.m, self.g, self.b = d / "mirror", d / "global", d / "backup"
        for root in (self.m, self.g):
            _write(root, "keeper"); _write(root, "absorbed")

    def tearDown(self):
        self.tmp.cleanup()

    def test_result_from_skill_reads_title_callout_and_body(self):
        r = cs.result_from_skill(self.m / "absorbed" / "SKILL.md")
        self.assertEqual(r.skill_name, "absorbed"); self.assertEqual(r.skill_title_ko, "제목 absorbed")
        self.assertEqual(r.callout, "콜아웃 absorbed"); self.assertIn("본문 absorbed", r.body_md)
        self.assertEqual(r.category, "개발"); self.assertEqual(r.grade, "A")

    def test_merge_writes_keeper_and_removes_absorbed(self):
        out = cs.merge_pair("keeper", "absorbed", mirror_dir=self.m, global_dir=self.g, backup_dir=self.b, merge=_merged)
        self.assertTrue(out["ok"], out)
        for root in (self.m, self.g):
            text = (root / "keeper" / "SKILL.md").read_text()
            self.assertIn("합쳐진 스킬", text); self.assertIn("https://example.com/absorbed", text)
            self.assertFalse((root / "absorbed").exists(), "흡수된 스킬은 지운다")
        self.assertTrue((self.b / "absorbed" / "SKILL.md").exists(), "지우기 전 백업")
        self.assertEqual(out["provider"], "claude"); self.assertEqual(out["sources"], 2)

    def test_failed_merge_deletes_nothing(self):
        def fail(existing_path, new_result, url, src_type):
            return new_result   # merger 가 실패하면 신규 결과를 그대로 돌려준다 (_is_merged 없음)
        out = cs.merge_pair("keeper", "absorbed", mirror_dir=self.m, global_dir=self.g, backup_dir=self.b, merge=fail)
        self.assertFalse(out["ok"])
        self.assertTrue((self.m / "absorbed").exists()); self.assertTrue((self.g / "absorbed").exists())
        self.assertIn("본문 keeper", (self.m / "keeper" / "SKILL.md").read_text(), "keeper 도 그대로")

    def test_missing_skill_is_reported(self):
        out = cs.merge_pair("keeper", "nope", mirror_dir=self.m, global_dir=self.g, backup_dir=self.b, merge=_merged)
        self.assertFalse(out["ok"]); self.assertIn("nope", out["reason"])


if __name__ == "__main__":
    unittest.main()
