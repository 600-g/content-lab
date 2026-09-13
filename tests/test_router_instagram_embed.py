"""router 가 인스타그램을 embed 우선으로 처리하고, 실패 시에만 기존 차단/yt-dlp 경로로 가는지 (네트워크 0)."""
from __future__ import annotations

import unittest
from unittest import mock

from scripts.scraper import router
from scripts.scraper.router import ScrapeResult


def _ok(url, media=None, text="캡션"):
    return ScrapeResult(url=url, source_type="instagram", title="t", text=text, meta={"media": media or []})


def _fail(url):
    return ScrapeResult(url=url, source_type="instagram", title="", text="", meta={}, ok=False, error="contextJSON 없음")


class RouterInstagramTest(unittest.TestCase):
    def test_feed_post_uses_embed_instead_of_block(self):
        url = "https://www.instagram.com/p/DdEAS85D0TV/"
        with mock.patch("scripts.scraper.instagram_embed.scrape", side_effect=lambda u: _ok(u, media=[{"kind": "image"}])) as emb, \
             mock.patch.object(router, "_ig_guard") as guard:
            r = router.scrape(url)
        self.assertTrue(r.ok)
        emb.assert_called_once_with(url)
        guard.assert_not_called()

    def test_embed_media_only_counts_as_success(self):
        url = "https://www.instagram.com/reel/DdGu4P0MjXk/"
        with mock.patch("scripts.scraper.instagram_embed.scrape", side_effect=lambda u: _ok(u, media=[{"kind": "video"}], text="")):
            r = router.scrape(url)
        self.assertTrue(r.ok)
        self.assertEqual(r.meta["media"][0]["kind"], "video")

    def test_feed_post_embed_failure_falls_back_to_block(self):
        url = "https://www.instagram.com/p/DdEAS85D0TV/"
        with mock.patch("scripts.scraper.instagram_embed.scrape", side_effect=_fail), \
             mock.patch.object(router, "_ig_block_enabled", return_value=True):
            r = router.scrape(url)
        self.assertEqual(r.skip_reason, "ig_login_wall")

    def test_reel_embed_failure_falls_back_to_ytdlp(self):
        url = "https://www.instagram.com/reel/DdGu4P0MjXk/"
        with mock.patch("scripts.scraper.instagram_embed.scrape", side_effect=_fail), \
             mock.patch("scripts.scraper.social.scrape_instagram", side_effect=lambda u: _ok(u, text="yt-dlp 캡션")) as yt:
            r = router.scrape(url)
        yt.assert_called_once()
        self.assertEqual(r.text, "yt-dlp 캡션")

    def test_embed_exception_does_not_break_chain(self):
        url = "https://www.instagram.com/reel/DdGu4P0MjXk/"
        def boom(u): raise RuntimeError("dns")
        with mock.patch("scripts.scraper.instagram_embed.scrape", side_effect=boom), \
             mock.patch("scripts.scraper.social.scrape_instagram", side_effect=lambda u: _ok(u, text="폴백")):
            r = router.scrape(url)
        self.assertEqual(r.text, "폴백")


if __name__ == "__main__":
    unittest.main()
