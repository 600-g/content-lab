"""library/regrade — 활용도 등급 재판정 도구 (네트워크·프로세스 0).

등급 = 활용도 (S 즉시 실행 / A 절차형 / B 개념·방법론 / C 정보·소개). 소장 가치가 아니다 — C 도 남긴다.
Claude 판정은 call 주입, 프론트매터 패치는 순수 함수로 검증한다.
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.library import regrade as rg

FM = """---
name: {slug}
description: 설명 {slug}
origin: content-lab
grade: {grade}
difficulty: {diff}
category: {cat}
ai_tools: ["Claude"]
sources:
  - https://example.com/{slug}
---

# 제목 {slug}

💡 콜아웃 {slug}

## 이게 뭔가요?
본문 {slug} """ + ("내용 " * 300)

OLD_FM = """---
name: old-style
description: 옛 형식
origin: content-lab
sources:
  - https://example.com/old
---

# 옛 스킬

본문 """ + ("내용 " * 200)


def _write(d: Path, slug: str, text: str) -> Path:
    p = d / slug / "SKILL.md"; p.parent.mkdir(parents=True); p.write_text(text, encoding="utf-8"); return p


class LoadAndBatchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.d = Path(self.tmp.name)
        for i in range(7):
            _write(self.d, f"s{i}", FM.format(slug=f"s{i}", grade="S", diff="초급", cat="개발"))
        _write(self.d, "old-style", OLD_FM)

    def tearDown(self):
        self.tmp.cleanup()

    def test_load_parses_meta_and_body(self):
        docs = {x.slug: x for x in rg.load_all(self.d)}
        self.assertEqual(len(docs), 8)
        self.assertEqual(docs["s1"].grade, "S")
        self.assertEqual(docs["s1"].category, "개발")
        self.assertEqual(docs["s1"].title, "제목 s1")
        self.assertIn("본문 s1", docs["s1"].body)
        self.assertEqual(docs["old-style"].grade, "", "구버전은 등급 없음")

    def test_batches_are_bounded_and_cover_all(self):
        docs = rg.load_all(self.d)
        batches = rg.build_batches(docs, size=3)
        self.assertEqual([len(b) for b in batches], [3, 3, 2])
        self.assertEqual(sorted(x.slug for b in batches for x in b), sorted(x.slug for x in docs))

    def test_prompt_carries_rubric_and_each_skill(self):
        docs = rg.load_all(self.d)[:2]
        p = rg.build_prompt(docs)
        for key in ("S", "A", "B", "C", "즉시", "절차", "개념", "정보"):
            self.assertIn(key, p)
        for x in docs:
            self.assertIn(x.slug, p); self.assertIn(x.title, p)
        self.assertLess(len(p), 2 * rg.BODY_CAP + 4000, "본문은 cap 으로 잘라 넣는다")


class ParseJudgementTest(unittest.TestCase):
    def test_valid_items_are_kept_and_normalised(self):
        raw = json.dumps({"items": [
            {"slug": "a", "grade": "S-즉시", "grade_reason": "r", "category": "개발", "difficulty": "초급", "ai_tools": ["Claude", "없는도구"]},
            {"slug": "b", "grade": "Z", "grade_reason": "r", "category": "개발", "difficulty": "초급", "ai_tools": []},
            {"slug": "ghost", "grade": "A", "grade_reason": "r", "category": "개발", "difficulty": "초급", "ai_tools": []},
        ]}, ensure_ascii=False)
        out = rg.parse_judgement(raw, expected_slugs={"a", "b"})
        self.assertEqual(out["a"]["grade"], "S", "첫 글자 정규화 (gotcha 48)")
        self.assertEqual(out["a"]["ai_tools"], ["Claude"], "enum 밖 도구는 버린다")
        self.assertNotIn("b", out, "등급 enum 밖이면 버린다")
        self.assertNotIn("ghost", out, "모르는 슬러그는 버린다")

    def test_garbage_returns_empty(self):
        self.assertEqual(rg.parse_judgement("죄송합니다", expected_slugs={"a"}), {})


class ApplyMetaTest(unittest.TestCase):
    def test_grade_is_replaced_and_missing_fields_added(self):
        text = OLD_FM
        out = rg.apply_meta(text, {"grade": "B", "category": "업무", "difficulty": "초급", "ai_tools": ["GPT"]})
        fm = out.split("\n---", 1)[0]
        self.assertIn("grade: B", fm); self.assertIn("category: 업무", fm); self.assertIn("difficulty: 초급", fm)
        self.assertIn('ai_tools: ["GPT"]', fm)
        self.assertIn("본문", out.split("\n---", 1)[1], "본문은 그대로")

    def test_valid_category_is_kept_unless_forced(self):
        text = FM.format(slug="s", grade="S", diff="초보OK", cat="개발")
        out = rg.apply_meta(text, {"grade": "A", "category": "업무", "difficulty": "중급", "ai_tools": ["Claude"]})
        fm = out.split("\n---", 1)[0]
        self.assertIn("grade: A", fm)
        self.assertIn("category: 개발", fm, "유효한 카테고리는 강제 옵션 없이는 안 바꾼다")
        self.assertIn("difficulty: 중급", fm, "enum 밖(초보OK) 은 교체")
        out2 = rg.apply_meta(text, {"grade": "A", "category": "업무", "difficulty": "중급", "ai_tools": ["Claude"]}, recategorize=True)
        self.assertIn("category: 업무", out2.split("\n---", 1)[0])

    def test_idempotent(self):
        text = FM.format(slug="s", grade="S", diff="초급", cat="개발")
        fields = {"grade": "A", "category": "개발", "difficulty": "초급", "ai_tools": ["Claude"]}
        once = rg.apply_meta(text, fields); twice = rg.apply_meta(once, fields)
        self.assertEqual(once, twice)


class RegradeRunTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.d = Path(self.tmp.name)
        self.g = self.d / "global"; self.m = self.d / "mirror"
        for i in range(3):
            _write(self.m, f"s{i}", FM.format(slug=f"s{i}", grade="S", diff="초급", cat="개발"))
            _write(self.g, f"s{i}", FM.format(slug=f"s{i}", grade="S", diff="초급", cat="개발"))

    def tearDown(self):
        self.tmp.cleanup()

    def _call(self, prompt, **kw):
        slugs = [s for s in ("s0", "s1", "s2") if s in prompt]
        return json.dumps({"items": [{"slug": s, "grade": "B", "grade_reason": "개념 위주", "category": "개발",
                                      "difficulty": "초급", "ai_tools": ["Claude"]} for s in slugs]}, ensure_ascii=False)

    def test_dry_run_changes_nothing(self):
        rows = rg.regrade(rg.load_all(self.m), call=self._call, apply=False, global_dir=self.g)
        self.assertEqual({r["slug"]: r["new_grade"] for r in rows}, {"s0": "B", "s1": "B", "s2": "B"})
        self.assertIn("grade: S", (self.m / "s0" / "SKILL.md").read_text())

    def test_apply_writes_mirror_and_global(self):
        rows = rg.regrade(rg.load_all(self.m), call=self._call, apply=True, global_dir=self.g)
        self.assertTrue(all(r["applied"] for r in rows))
        for root in (self.m, self.g):
            self.assertIn("grade: B", (root / "s1" / "SKILL.md").read_text())

    def test_claude_unavailable_marks_rows_skipped(self):
        rows = rg.regrade(rg.load_all(self.m), call=lambda *a, **k: None, apply=True, global_dir=self.g)
        self.assertTrue(all(r["new_grade"] is None for r in rows))
        self.assertIn("grade: S", (self.m / "s0" / "SKILL.md").read_text())


if __name__ == "__main__":
    unittest.main()
