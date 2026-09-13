"""미디어 이해 단계 — 영상/이미지/유튜브를 Gemini 로 텍스트화해 본문에 덧붙인다 (네트워크 0).

fetch/upload/generate 를 주입해 검증한다. 어떤 항목이 실패해도 예외가 밖으로 새면 안 된다
(gotcha 39 — 폴백 경로가 원래 경로보다 방어가 약한 게 이 코드베이스의 반복 패턴).
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest

from scripts.analyzer import media_understand as mu
from scripts.scraper.router import ScrapeResult


def _res(media, text="캡션") -> ScrapeResult:
    return ScrapeResult(url="https://www.instagram.com/reel/X/", source_type="instagram",
                        title="t", text=text, meta={"media": media})


class Recorder:
    def __init__(self, reply="AI Office 로 할 수 있는 것 8가지"):
        self.calls = []
        self.reply = reply
    def __call__(self, parts):
        self.calls.append(parts)
        return self.reply


class EnrichTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = os.path.join(self.tmp.name, "media_cache.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_video_is_uploaded_then_transcribed(self):
        gen = Recorder()
        uploads = []
        r = _res([{"kind": "video", "url": "https://cdn/x.mp4", "key": "ig:X:0"}])
        out = mu.enrich(r, fetch=lambda u: b"\x00" * 10, upload=lambda data, mime: uploads.append((len(data), mime)) or "files/abc",
                        generate=gen, cache_path=self.cache)
        self.assertTrue(out["ok"])
        self.assertEqual(uploads, [(10, "video/mp4")])
        self.assertEqual(len(gen.calls), 1)
        self.assertEqual(gen.calls[0][0]["file_data"]["file_uri"], "files/abc")
        self.assertIn("[영상 내용", r.text)
        self.assertIn("8가지", r.text)
        self.assertEqual(out["added_chars"], len(r.text) - len("캡션"))
        self.assertEqual(out["items"][0]["ok"], True)

    def test_images_are_batched_into_one_call(self):
        gen = Recorder("슬라이드 1: Komi Store")
        r = _res([{"kind": "image", "url": f"https://cdn/{i}.jpg", "key": f"ig:X:{i}"} for i in range(3)])
        out = mu.enrich(r, fetch=lambda u: b"jpg", upload=None, generate=gen, cache_path=self.cache)
        self.assertEqual(len(gen.calls), 1)
        inline = [p for p in gen.calls[0] if "inline_data" in p]
        self.assertEqual(len(inline), 3)
        self.assertEqual(inline[0]["inline_data"]["mime_type"], "image/jpeg")
        self.assertIn("[슬라이드 텍스트", r.text)
        self.assertEqual(sum(1 for i in out["items"] if i["ok"]), 3)

    def test_youtube_passes_url_without_download(self):
        gen = Recorder("영상 요약")
        def no_fetch(u): raise AssertionError("유튜브는 다운로드하면 안 된다")
        r = ScrapeResult(url="https://www.youtube.com/watch?v=abc", source_type="youtube", title="t",
                         text="[설명] x", meta={"media": [{"kind": "youtube", "url": "https://www.youtube.com/watch?v=abc", "key": "yt:abc"}]})
        mu.enrich(r, fetch=no_fetch, upload=None, generate=gen, cache_path=self.cache)
        self.assertEqual(gen.calls[0][0]["file_data"]["file_uri"], "https://www.youtube.com/watch?v=abc")
        self.assertIn("[영상 내용", r.text)

    def test_cache_hit_skips_generate(self):
        gen = Recorder()
        media = [{"kind": "video", "url": "https://cdn/x.mp4?sig=1", "key": "ig:X:0"}]
        mu.enrich(_res(media), fetch=lambda u: b"v", upload=lambda d, m: "files/1", generate=gen, cache_path=self.cache)
        # 두 번째: URL 서명이 바뀌어도 key 가 같으면 캐시
        r2 = _res([{**media[0], "url": "https://cdn/x.mp4?sig=2"}])
        def no_fetch(u): raise AssertionError("캐시 히트면 다운로드도 없어야 한다")
        out = mu.enrich(r2, fetch=no_fetch, upload=None, generate=gen, cache_path=self.cache)
        self.assertEqual(len(gen.calls), 1)
        self.assertTrue(out["items"][0]["cached"])
        self.assertIn("8가지", r2.text)
        with open(self.cache, encoding="utf-8") as f:
            self.assertIn("ig:X:0", json.load(f))

    def test_generate_failure_is_isolated(self):
        def boom(parts): raise RuntimeError("429 quota")
        r = _res([{"kind": "video", "url": "https://cdn/x.mp4", "key": "ig:X:0"}])
        out = mu.enrich(r, fetch=lambda u: b"v", upload=lambda d, m: "files/1", generate=boom, cache_path=self.cache)
        self.assertFalse(out["ok"])
        self.assertEqual(r.text, "캡션")
        self.assertIn("429", out["items"][0]["error"])

    def test_oversized_video_is_skipped(self):
        gen = Recorder()
        r = _res([{"kind": "video", "url": "https://cdn/big.mp4", "key": "ig:X:0"}])
        out = mu.enrich(r, fetch=lambda u: b"x" * (mu.MAX_VIDEO_BYTES + 1), upload=lambda d, m: "files/1",
                        generate=gen, cache_path=self.cache)
        self.assertEqual(gen.calls, [])
        self.assertIn("상한", out["items"][0]["error"])

    def test_no_media_is_noop(self):
        r = ScrapeResult(url="u", source_type="web", title="t", text="본문", meta={})
        out = mu.enrich(r, generate=Recorder(), cache_path=self.cache)
        self.assertEqual(out["items"], [])
        self.assertEqual(r.text, "본문")

    def test_empty_reply_is_not_appended(self):
        r = _res([{"kind": "video", "url": "https://cdn/x.mp4", "key": "ig:X:0"}])
        out = mu.enrich(r, fetch=lambda u: b"v", upload=lambda d, m: "files/1", generate=Recorder("   "), cache_path=self.cache)
        self.assertEqual(r.text, "캡션")
        self.assertFalse(out["items"][0]["ok"])


if __name__ == "__main__":
    unittest.main()
