"""미디어 이해 단계 — 영상/이미지/유튜브를 Gemini 로 텍스트화해 본문에 덧붙인다 (네트워크 0).

fetch/upload/generate 를 주입해 검증한다. 어떤 항목이 실패해도 예외가 밖으로 새면 안 된다
(gotcha 39 — 폴백 경로가 원래 경로보다 방어가 약한 게 이 코드베이스의 반복 패턴).
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from unittest import mock

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
        # 기본 이미지 판독기는 Claude(claude -p). 이 클래스는 Gemini 경로를 검증하므로 끈다.
        self._reader = mock.patch.object(mu, "_default_read_images", lambda files, prompt: None)
        self._reader.start()

    def tearDown(self):
        self._reader.stop()
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


class ReaderRecorder:
    def __init__(self, reply=None, raise_exc=None):
        self.calls = []
        self.reply, self.raise_exc = reply, raise_exc

    def __call__(self, files, prompt):
        self.calls.append((files, prompt))
        if self.raise_exc:
            raise self.raise_exc
        return self.reply


class ClaudeImagesTest(unittest.TestCase):
    """슬라이드(이미지)는 Claude 가 먼저 읽고, 못 읽으면 Gemini. 영상은 Claude 가 못 받으니 그대로 Gemini."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = os.path.join(self.tmp.name, "media_cache.json")

    def tearDown(self):
        self.tmp.cleanup()

    def _imgs(self, n=2, ext="png"):
        return _res([{"kind": "image", "url": f"https://cdn/{i}.{ext}?sig=abc", "key": f"ig:X:{i}"} for i in range(n)])

    def test_claude_reader_runs_before_gemini(self):
        reader = ReaderRecorder("슬라이드 1: Komi Store (Claude)")
        gen = Recorder("gemini")
        r = self._imgs()
        out = mu.enrich(r, fetch=lambda u: b"png", generate=gen, read_images=reader, cache_path=self.cache)
        self.assertEqual(gen.calls, [], "Claude 가 읽었으면 Gemini 쿼터를 쓰지 않는다")
        self.assertEqual(len(reader.calls), 1)
        files, prompt = reader.calls[0]
        self.assertEqual(files, [(b"png", "image/png"), (b"png", "image/png")])
        self.assertIn("슬라이드", prompt)
        self.assertIn("(Claude)", r.text)
        self.assertTrue(out["ok"])
        self.assertEqual([i["provider"] for i in out["items"]], ["claude", "claude"])
        cache = json.load(open(self.cache, encoding="utf-8"))
        self.assertEqual(list(cache.values())[0]["provider"], "claude")

    def test_gemini_used_when_claude_returns_none(self):
        reader = ReaderRecorder(None)
        gen = Recorder("gemini 판독")
        r = self._imgs(ext="jpg")
        out = mu.enrich(r, fetch=lambda u: b"jpg", generate=gen, read_images=reader, cache_path=self.cache)
        self.assertEqual(len(gen.calls), 1)
        self.assertEqual(sum(1 for p in gen.calls[0] if "inline_data" in p), 2)
        self.assertIn("gemini 판독", r.text)
        self.assertEqual(out["items"][0]["provider"], "gemini")

    def test_gemini_used_when_claude_raises(self):
        reader = ReaderRecorder(raise_exc=RuntimeError("claude 죽음"))
        gen = Recorder("gemini 판독")
        r = self._imgs()
        out = mu.enrich(r, fetch=lambda u: b"png", generate=gen, read_images=reader, cache_path=self.cache)
        self.assertTrue(out["ok"])
        self.assertEqual(len(gen.calls), 1)

    def test_video_never_goes_to_claude(self):
        reader = ReaderRecorder("안 불려야 함")
        gen = Recorder("영상 전사")
        r = _res([{"kind": "video", "url": "https://cdn/x.mp4", "key": "ig:X:0"}])
        out = mu.enrich(r, fetch=lambda u: b"v", upload=lambda d, m: "files/1", generate=gen,
                        read_images=reader, cache_path=self.cache)
        self.assertEqual(reader.calls, [])
        self.assertEqual(out["items"][0]["provider"], "gemini")

    def test_default_reader_is_claude_cli(self):
        from scripts.analyzer import claude_cli
        with mock.patch.object(claude_cli, "call_claude_read_files", return_value="클로드 판독") as m:
            r = self._imgs(n=3, ext="webp")
            mu.enrich(r, fetch=lambda u: b"w", generate=Recorder("x"), cache_path=self.cache)
        self.assertEqual(m.call_count, 1)
        files = m.call_args.args[1]
        self.assertEqual([n for n, _ in files], ["slide_1.webp", "slide_2.webp", "slide_3.webp"])
        self.assertIn("클로드 판독", r.text)


if __name__ == "__main__":
    unittest.main()
