"""등급 표기 정규화 — 프롬프트가 `S-즉시적용` 표기를 가르치는데 파서가 `S` 만 인정하던 버그.

실사고 2026-08-28 (fieldby.notion.site/3c9d…): Gemini 가 "S-즉시적용" 을 반환 → enum 밖 → C 로 강등 →
"스킬로 등록할 가치가 없다" 로 안내되고 미등록.
"""
from __future__ import annotations

import unittest

from scripts.analyzer import gemini


def _v(grade):
    return gemini._validate({"skill_name": "x", "skill_title_ko": "y", "category": "기타", "grade": grade})["grade"]


class GradeNormalizeTest(unittest.TestCase):
    def test_labelled_enum_is_normalized(self):
        self.assertEqual(_v("S-즉시적용"), "S")
        self.assertEqual(_v("A-참고가치"), "A")
        self.assertEqual(_v("B+"), "B")
        self.assertEqual(_v(" a "), "A")

    def test_plain_enum_untouched(self):
        for g in ("S", "A", "B", "C"):
            self.assertEqual(_v(g), g)

    def test_garbage_still_degrades_to_c(self):
        self.assertEqual(_v("즉시적용"), "C")
        self.assertEqual(_v(""), "C")
        self.assertEqual(_v(None), "C")


if __name__ == "__main__":
    unittest.main()
