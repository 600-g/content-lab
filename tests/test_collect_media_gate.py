"""본문 길이 게이트 — 미디어 이해가 내용을 실제로 읽었으면 붙여넣기 기준(200자)을 쓴다.

실사고 2026-09-13 재처리 첫 항목 (릴스 DdGu4P0MjXk): 캡션 260자 + 영상 전사 209자 = 469자 →
스크랩용 500자 게이트에 걸려 "본문 부족 → 분석 생략". 500 은 '렌더 실패로 껍데기만 잡힘' 방어인데,
영상을 실제로 읽어 붙인 본문엔 그 위험이 없다 — 짧은 릴스는 내용 자체가 짧다.
"""
from __future__ import annotations

import unittest

from scripts import collect
from scripts.scraper import plain_text
from scripts.scraper.router import MIN_TEXT_LEN


class MinTextLenTest(unittest.TestCase):
    def test_scrape_only_uses_scraper_threshold(self):
        self.assertEqual(collect._min_text_len(is_paste=False, media_added=0), MIN_TEXT_LEN)

    def test_paste_uses_paste_threshold(self):
        self.assertEqual(collect._min_text_len(is_paste=True, media_added=0), plain_text.TEXT_MIN_LEN)

    def test_media_understood_uses_paste_threshold(self):
        self.assertEqual(collect._min_text_len(is_paste=False, media_added=209), plain_text.TEXT_MIN_LEN)

    def test_media_attempted_but_empty_keeps_scraper_threshold(self):
        # 미디어 단계가 돌았지만 아무것도 못 읽었으면 껍데기 위험은 그대로다
        self.assertEqual(collect._min_text_len(is_paste=False, media_added=0), MIN_TEXT_LEN)


if __name__ == "__main__":
    unittest.main()
