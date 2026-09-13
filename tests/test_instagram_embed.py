"""Instagram 공개 embed 스크래퍼 — contextJSON 파싱·미디어 목록·폴백 (네트워크 0).

실측 (2026-09-12): /embed/captioned/ HTML 안 `"contextJSON":"…"` 는 JSON 문자열을 한 번 더
JSON 인코딩한 형태다. 파서는 그 이중 인코딩을 그대로 재현한 픽스처로 검증한다.
"""
from __future__ import annotations

import json
import unittest

from scripts.scraper import instagram_embed as ie


def _embed_html(shortcode_media: dict) -> str:
    inner = json.dumps({"context": {"type": "GraphVideo"}, "gql_data": {"shortcode_media": shortcode_media}})
    return (
        '<html><body><script>window.__d={"isSidecar":false,"contextJSON":'
        + json.dumps(inner)
        + ',"isGuideEmbed":false};</script></body></html>'
    )


REEL = {
    "__typename": "GraphVideo",
    "shortcode": "DdGu4P0MjXk",
    "is_video": True,
    "video_url": "https://scontent.cdninstagram.com/o1/v/reel.mp4?sig=1",
    "video_duration": 25.5,
    "video_view_count": 8046,
    "display_url": "https://scontent.cdninstagram.com/thumb.jpg",
    "owner": {"username": "godseng.mom"},
    "edge_media_to_caption": {"edges": [{"node": {"text": "AI Office 로 할 수 있는 것\n번호를 남겨주세요"}}]},
}

CAROUSEL = {
    "__typename": "GraphSidecar",
    "shortcode": "DdEAS85D0TV",
    "is_video": False,
    "display_url": "https://scontent.cdninstagram.com/slide1.jpg",
    "owner": {"username": "ai.asap.kr"},
    "edge_media_to_caption": {"edges": [{"node": {"text": "Komi Store 는 깃허브 릴리스 앱스토어"}}]},
    "edge_sidecar_to_children": {"edges": [
        {"node": {"is_video": False, "display_url": "https://scontent.cdninstagram.com/slide1.jpg", "accessibility_caption": "텍스트가 있는 이미지"}},
        {"node": {"is_video": False, "display_url": "https://scontent.cdninstagram.com/slide2.jpg", "accessibility_caption": ""}},
        {"node": {"is_video": True, "display_url": "https://scontent.cdninstagram.com/slide3.jpg", "video_url": "https://scontent.cdninstagram.com/slide3.mp4"}},
    ]},
}


class ShortcodeTest(unittest.TestCase):
    def test_variants(self):
        for url, kind, sc in [
            ("https://www.instagram.com/reel/DdGu4P0MjXk/?stkn=abc", "reel", "DdGu4P0MjXk"),
            ("https://www.instagram.com/p/DdEAS85D0TV/?img_index=2", "p", "DdEAS85D0TV"),
            ("https://instagram.com/p/DYYyIEqACDx/", "p", "DYYyIEqACDx"),
            ("https://www.instagram.com/reels/Dc01G4vJP_5/", "reel", "Dc01G4vJP_5"),
            ("https://www.instagram.com/tv/ABC_def-123/", "reel", "ABC_def-123"),
        ]:
            self.assertEqual(ie.parse_shortcode(url), (kind, sc), url)

    def test_non_post_urls(self):
        self.assertIsNone(ie.parse_shortcode("https://www.instagram.com/godseng.mom/"))
        self.assertIsNone(ie.parse_shortcode("https://example.com/p/abc/"))

    def test_embed_url(self):
        self.assertEqual(ie.embed_url("https://www.instagram.com/reel/DdGu4P0MjXk/?x=1"),
                         "https://www.instagram.com/reel/DdGu4P0MjXk/embed/captioned/")
        self.assertEqual(ie.embed_url("https://instagram.com/p/DYYyIEqACDx/"),
                         "https://www.instagram.com/p/DYYyIEqACDx/embed/captioned/")


class ContextJsonTest(unittest.TestCase):
    def test_roundtrip_double_encoded(self):
        sm = ie.parse_context_json(_embed_html(REEL))
        self.assertEqual(sm["shortcode"], "DdGu4P0MjXk")
        self.assertEqual(sm["video_url"], REEL["video_url"])

    def test_missing_returns_none(self):
        self.assertIsNone(ie.parse_context_json("<html>login wall</html>"))
        self.assertIsNone(ie.parse_context_json('{"contextJSON":"not json at all'))


class ExtractMediaTest(unittest.TestCase):
    def test_reel_video(self):
        media = ie.extract_media(REEL, "DdGu4P0MjXk")
        self.assertEqual([m["kind"] for m in media], ["video"])
        self.assertEqual(media[0]["url"], REEL["video_url"])
        self.assertEqual(media[0]["key"], "ig:DdGu4P0MjXk:0")

    def test_carousel_children_in_order(self):
        media = ie.extract_media(CAROUSEL, "DdEAS85D0TV")
        self.assertEqual([m["kind"] for m in media], ["image", "image", "video"])
        self.assertEqual([m["key"] for m in media], ["ig:DdEAS85D0TV:0", "ig:DdEAS85D0TV:1", "ig:DdEAS85D0TV:2"])
        self.assertEqual(media[2]["url"], "https://scontent.cdninstagram.com/slide3.mp4")
        self.assertEqual(media[0]["alt"], "텍스트가 있는 이미지")

    def test_single_image_post(self):
        single = {**CAROUSEL, "edge_sidecar_to_children": None, "__typename": "GraphImage"}
        media = ie.extract_media(single, "X")
        self.assertEqual(media, [{"kind": "image", "url": CAROUSEL["display_url"], "key": "ig:X:0", "alt": ""}])


class ScrapeTest(unittest.TestCase):
    def test_reel_scrape(self):
        r = ie.scrape("https://www.instagram.com/reel/DdGu4P0MjXk/?stkn=abc", fetch=lambda u: _embed_html(REEL))
        self.assertTrue(r.ok)
        self.assertEqual(r.source_type, "instagram")
        self.assertIn("AI Office 로 할 수 있는 것", r.text)
        self.assertIn("@godseng.mom", r.text)
        self.assertEqual(r.meta["kind"], "reel")
        self.assertEqual(r.meta["owner"], "godseng.mom")
        self.assertEqual(r.meta["duration"], 25.5)
        self.assertEqual(len(r.meta["media"]), 1)
        self.assertEqual(r.meta["media"][0]["kind"], "video")

    def test_carousel_scrape_includes_alt_text(self):
        r = ie.scrape("https://www.instagram.com/p/DdEAS85D0TV/", fetch=lambda u: _embed_html(CAROUSEL))
        self.assertTrue(r.ok)
        self.assertEqual(r.meta["kind"], "carousel")
        self.assertEqual(len(r.meta["media"]), 3)
        self.assertIn("텍스트가 있는 이미지", r.text)

    def test_fetch_uses_embed_url(self):
        seen = []
        def fetch(u):
            seen.append(u); return _embed_html(REEL)
        ie.scrape("https://www.instagram.com/reel/DdGu4P0MjXk/", fetch=fetch)
        self.assertEqual(seen, ["https://www.instagram.com/reel/DdGu4P0MjXk/embed/captioned/"])

    def test_login_wall_html_is_soft_failure(self):
        r = ie.scrape("https://www.instagram.com/p/DdEAS85D0TV/", fetch=lambda u: "<html>Log in</html>")
        self.assertFalse(r.ok)
        self.assertFalse(r.skip_reason)
        self.assertIn("contextJSON", r.error)

    def test_fetch_exception_is_soft_failure(self):
        def boom(u): raise RuntimeError("timeout")
        r = ie.scrape("https://www.instagram.com/p/DdEAS85D0TV/", fetch=boom)
        self.assertFalse(r.ok)
        self.assertIn("timeout", r.error)

    def test_non_post_url_is_soft_failure(self):
        r = ie.scrape("https://www.instagram.com/godseng.mom/", fetch=lambda u: "")
        self.assertFalse(r.ok)


if __name__ == "__main__":
    unittest.main()
