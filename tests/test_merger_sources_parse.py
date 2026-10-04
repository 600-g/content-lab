"""_parse_existing_skill_md 의 sources 파싱 — 여러 줄 출처를 전부 읽어야 한다.

2026-09-27 회귀: 정규식 lookahead 의 `$` 가 MULTILINE 에서 첫 줄 끝에 걸려 첫 URL 만 읽혔다.
그 결과 출처 2개 이상인 스킬을 다시 합병하면 나머지 출처가 조용히 사라졌다.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.analyzer.merger import _parse_existing_skill_md

SKILL = """---
name: demo
description: 데모
origin: content-lab
grade: A
category: 개발
ai_tools: ["Claude"]
sources:
  - https://a.example/1
  - https://b.example/2
  - https://c.example/3
---

# 데모

본문
"""


class SourcesParseTest(unittest.TestCase):
    def _parse(self, text: str) -> dict:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "SKILL.md"
            p.write_text(text, encoding="utf-8")
            return _parse_existing_skill_md(p)

    def test_reads_every_source_line(self):
        meta = self._parse(SKILL)
        self.assertEqual(meta["source_urls"],
                         ["https://a.example/1", "https://b.example/2", "https://c.example/3"])

    def test_single_inline_source_still_works(self):
        meta = self._parse(SKILL.replace(
            "sources:\n  - https://a.example/1\n  - https://b.example/2\n  - https://c.example/3",
            "source_url: https://only.example/x"))
        self.assertEqual(meta["source_urls"], ["https://only.example/x"])

    def test_sources_as_last_frontmatter_key(self):
        text = SKILL.replace('ai_tools: ["Claude"]\n', "")
        meta = self._parse(text)
        self.assertEqual(len(meta["source_urls"]), 3)


if __name__ == "__main__":
    unittest.main()
