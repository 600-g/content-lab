"""Jina Reader 폴백 (v5.4) — Playwright·requests 가 껍데기만 가져왔을 때의 마지막 수단 (네트워크 0).

왜: 2026-09 재처리에서 공개 노션 페이지가 273·453자 껍데기로 끝나 "본문 부족 → 분석 생략" 이 됐다.
r.jina.ai 는 키·로그인 없이 같은 페이지를 5,516자로 읽는다 (2026-09-20 실측). 무료라 쿼터 걱정도 없다.
로그인 벽 자체를 뚫지는 못하므로 '차단' 판정(skip_reason)된 URL 에는 쓰지 않는다.
"""
from __future__ import annotations

import unittest
from unittest import mock

from scripts.scraper import jina, router
from scripts.scraper.router import ScrapeResult

# 주의: 인접 문자열 리터럴은 * 보다 먼저 이어붙는다 — 반복분은 반드시 괄호로 감싼다
RAW = (
    "Title: 루프 엔지니어링 완전정복\n\n"
    "URL Source: https://example.notion.site/abc\n\n"
    "Published Time: Thu, 09 Jul 2026 17:43:03 GMT\n\n"
    "Markdown Content:\n"
    "![Image 1: 📎](blob:http://localhost/2ae2cc6f)\n\n"
) + ("한 줄로 말하면 AI 루프를 짜라는 겁니다. " * 40)


class ParseTest(unittest.TestCase):
    def test_title_and_body_are_split(self):
        title, body = jina.parse(RAW)
        self.assertEqual(title, "루프 엔지니어링 완전정복")
        self.assertTrue(body.startswith("한 줄로 말하면"), body[:40])
        self.assertNotIn("Image 1:", body, "Jina 의 이미지 자리표시자는 내용이 아니다")
        self.assertNotIn("URL Source:", body)
        self.assertNotIn("Markdown Content:", body)

    def test_dead_blob_images_become_plain_text(self):
        _, body = jina.parse(RAW)
        self.assertNotIn("blob:", body, "blob: 는 죽은 링크 — 카탈로그에 들어가면 안 된다")

    def test_header_only_response_yields_empty_body(self):
        _, body = jina.parse("Title: 제목\n\nURL Source: https://x\n\nMarkdown Content:\n")
        self.assertEqual(body.strip(), "")

    def test_plain_text_without_headers_is_kept(self):
        _, body = jina.parse("헤더 없는 본문입니다")
        self.assertEqual(body.strip(), "헤더 없는 본문입니다")


class ScrapeTest(unittest.TestCase):
    def test_success_returns_result_with_source_type(self):
        r = jina.scrape("https://example.notion.site/abc", source_type="notion", fetch=lambda u: RAW)
        self.assertTrue(r.ok)
        self.assertEqual(r.source_type, "notion")
        self.assertEqual(r.title, "루프 엔지니어링 완전정복")
        self.assertGreater(len(r.text), 500)
        self.assertEqual(r.meta.get("via"), "jina")

    def test_endpoint_is_prefixed_once(self):
        seen = {}
        jina.scrape("https://x.com/a", fetch=lambda u: seen.setdefault("u", u) or RAW)
        self.assertEqual(seen["u"], "https://r.jina.ai/https://x.com/a")

    def test_fetch_failure_is_not_raised(self):
        def boom(u):
            raise RuntimeError("timeout")
        r = jina.scrape("https://x", fetch=boom)
        self.assertFalse(r.ok)
        self.assertIn("timeout", r.error)

    def test_short_body_is_not_ok(self):
        r = jina.scrape("https://x", fetch=lambda u: "Title: t\n\nMarkdown Content:\n짧음")
        self.assertFalse(r.ok)


class UserAgentTest(unittest.TestCase):
    """r.jina.ai 는 브라우저 UA 를 403 으로 막는다 (2026-09-20 실측). 다른 스크래퍼 습관대로
    브라우저 UA 로 '고치면' 폴백이 통째로 죽는데, 예외가 삼켜져 조용히 사라진다."""

    def test_ua_is_not_browser_like(self):
        ua = jina.UA.lower()
        for token in ("mozilla/5.0 (macintosh", "applewebkit", "safari/", "chrome/"):
            self.assertNotIn(token, ua, f"브라우저 UA 토큰 금지: {token}")
        self.assertIn("aiskillbox", ua)

    def test_default_fetch_sends_that_ua(self):
        seen = {}

        class R:
            text = "Title: t\n\nMarkdown Content:\n본문"

            @staticmethod
            def raise_for_status():
                return None

        with mock.patch.object(jina.requests, "get", side_effect=lambda u, **kw: seen.update(kw) or R()):
            jina._default_fetch("https://r.jina.ai/https://x")
        self.assertEqual(seen["headers"]["User-Agent"], jina.UA)


class RouterFallbackTest(unittest.TestCase):
    """Playwright·requests 결과가 MIN_TEXT_LEN 미만일 때만 Jina 를 부른다."""

    def _short(self, n=300):
        return ScrapeResult(url="https://example.notion.site/abc", source_type="notion", title="t",
                            text="짧" * n, meta={}, ok=True)

    def _long(self):
        return ScrapeResult(url="https://example.notion.site/abc", source_type="notion", title="t",
                            text="김" * 2000, meta={}, ok=True)

    def _run(self, web_result, jina_result):
        with mock.patch.object(router, "_retry", return_value=web_result), \
             mock.patch("scripts.scraper.mcp_fallback.scrape", return_value=None), \
             mock.patch.object(jina, "scrape", return_value=jina_result) as js:
            out = router.scrape("https://example.notion.site/abc")
        return out, js

    def test_jina_is_used_when_result_is_short(self):
        rich = ScrapeResult(url="https://example.notion.site/abc", source_type="notion", title="제목",
                            text="본문" * 3000, meta={"via": "jina"}, ok=True)
        out, js = self._run(self._short(), rich)
        js.assert_called_once()
        self.assertEqual(out.meta.get("via"), "jina")

    def test_jina_is_skipped_when_result_is_long_enough(self):
        out, js = self._run(self._long(), None)
        js.assert_not_called()
        self.assertEqual(out.text, "김" * 2000)

    def test_longer_of_the_two_wins(self):
        thin_jina = ScrapeResult(url="https://example.notion.site/abc", source_type="notion", title="t",
                                 text="짧게", meta={"via": "jina"}, ok=True)
        out, js = self._run(self._short(), thin_jina)
        js.assert_called_once()
        self.assertNotEqual(out.meta.get("via"), "jina", "더 긴 쪽을 남긴다")

    def test_blocked_pages_never_call_jina(self):
        blocked = ScrapeResult(url="https://example.notion.site/abc", source_type="notion", title="",
                               text="", meta={}, ok=False, error="차단")
        blocked.skip_reason = "notion_private"
        out, js = self._run(blocked, None)
        js.assert_not_called()


if __name__ == "__main__":
    unittest.main()
