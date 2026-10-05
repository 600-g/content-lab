"""합쳐진 원본 문서 목록 (2026-10-05 "원본들도 해당 문서에 같이 리스트해놔").

frontmatter `originals:` 가 단일 진실이고 `## 출처` 아래 `### 합쳐진 원본 문서` 표로 렌더된다.
다시 합쳐도 이어지고(멱등·합집합), 합쳐지지 않은 문서엔 붙지 않는다. 네트워크·디스크 부작용 0.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.library.index import parse_frontmatter
from scripts.skill_builder import originals as og

MD = """---
name: keeper
description: 설명
origin: content-lab
grade: S
difficulty: 초급
category: 개발
ai_tools: ["Claude"]
sources:
  - https://example.com/k
  - https://notion.site/x
---

# 합친 제목 (합병됨)

## 이게 뭔가요?
본문

## 출처

- [https://example.com/k](https://example.com/k)
"""


class OriginalsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _file(self, slug: str, text: str = MD) -> Path:
        p = self.d / slug / "SKILL.md"; p.parent.mkdir(parents=True); p.write_text(text.replace("keeper", slug), encoding="utf-8"); return p

    def test_self_entry_reads_slug_title_sources_without_badge(self):
        slug, title, urls = og.parse_entry(og.self_entry(self._file("keeper")))
        self.assertEqual(slug, "keeper"); self.assertEqual(title, "합친 제목")
        self.assertEqual(urls, ["https://example.com/k", "https://notion.site/x"])

    def test_apply_adds_frontmatter_and_table_and_is_idempotent(self):
        es = [og.make_entry("keeper", "가", ["https://example.com/k"]), og.make_entry("b", "나 | 다", ["paste://abc"])]
        once = og.apply_to_md(MD, es)
        self.assertEqual(og.apply_to_md(once, es), once, "멱등")
        self.assertEqual(og.read_originals(once), es)
        meta, body = parse_frontmatter(once)
        self.assertEqual(meta["sources"], ["https://example.com/k", "https://notion.site/x"], "sources 파싱 불변")
        self.assertIn("### 합쳐진 원본 문서", body); self.assertIn("| 나 / 다 | `b` | 직접 입력 |", body)
        self.assertIn("[example.com](https://example.com/k)", body)
        self.assertGreater(body.index("### 합쳐진 원본 문서"), body.index("## 출처"), "출처 아래")

    def test_single_original_adds_nothing(self):
        self.assertEqual(og.apply_to_md(MD, [og.make_entry("keeper", "가", [])]).count("합쳐진 원본"), 0)

    def test_merge_lists_keeps_order_and_dedupes_by_slug(self):
        a, b, a2 = og.make_entry("a", "A", []), og.make_entry("b", "B", []), og.make_entry("a", "A2", [])
        self.assertEqual(og.merge_lists([a, b], [a2]), [a, b])

    def test_originals_carry_over_on_remerge(self):
        p = self._file("keeper")
        p.write_text(og.apply_to_md(MD, [og.make_entry("keeper", "가", []), og.make_entry("old", "옛", [])]), encoding="utf-8")
        self.assertEqual([og.parse_entry(e)[0] for e in og.originals_of(p)], ["keeper", "old"])

    def test_source_strip_removes_table_so_renderer_owns_it(self):
        from scripts.skill_builder.md_generator import _strip_source_section
        once = og.apply_to_md(MD, [og.make_entry("keeper", "가", []), og.make_entry("b", "나", [])])
        self.assertNotIn("합쳐진 원본", _strip_source_section(parse_frontmatter(once)[1]))


if __name__ == "__main__":
    unittest.main()
