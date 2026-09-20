"""router 가 확보한 최선의 스크랩 결과를 버리지 않는지 검증 (네트워크 0).

실사고 (2026-08-25, ChatGPT GPT 링크): Playwright 가 459자 → 477자를 확보했는데
MIN_TEXT_LEN(500) 미달이라 _retry 가 None 을 반환 → 3단계 requests 폴백이 가져온
103자가 최종 결과로 채택됐다. 사용자에겐 "본문을 103자밖에 가져오지 못했습니다"
라고 표시돼 실제 확보량보다 나쁘게 보였다.
"""
from __future__ import annotations

import contextlib
import unittest
from unittest import mock

import scripts.scraper as scraper_pkg
from scripts.scraper import router
from scripts.scraper.router import ScrapeResult


@contextlib.contextmanager
def _stub_modules(web, fallback):
    """router 의 `from . import web / mcp_fallback / jina` 를 대역으로 바꾼다.

    ★ sys.modules 만 갈아끼우면 안 된다 — `from . import X` 는 **패키지 속성**을 먼저 보므로,
    앞선 테스트가 진짜 모듈을 한 번이라도 import 했다면 패치가 통째로 무력화되고 실제 Playwright 가
    돈다 (2026-09-20 실측: 체인 테스트 5건이 example.com 을 진짜로 긁어 129자를 받고 30초 소요).
    패키지 속성을 직접 갈아끼워 import 순서와 무관하게 만든다.
    """
    no_jina = mock.Mock()
    no_jina.scrape.return_value = None   # v5.4 4단계는 이 파일의 관심사가 아니다
    with mock.patch.object(scraper_pkg, "web", web, create=True), \
         mock.patch.object(scraper_pkg, "mcp_fallback", fallback, create=True), \
         mock.patch.object(scraper_pkg, "jina", no_jina, create=True):
        yield


def _res(text: str, *, ok: bool = True, source: str = "web") -> ScrapeResult:
    return ScrapeResult(url="https://example.com", source_type=source,
                        title="t", text=text, meta={}, ok=ok)


class PickBestTest(unittest.TestCase):
    def test_longest_wins(self):
        best = router.pick_best(_res("a" * 103), _res("b" * 477))
        self.assertEqual(len(best.text), 477)

    def test_successful_result_beats_longer_failure(self):
        best = router.pick_best(_res("x" * 900, ok=False), _res("y" * 300))
        self.assertTrue(best.ok)
        self.assertEqual(len(best.text), 300)

    def test_none_entries_ignored(self):
        self.assertIsNone(router.pick_best(None, None))
        self.assertEqual(router.pick_best(None, _res("z" * 50)).text, "z" * 50)


class RetryKeepsBestTest(unittest.TestCase):
    def test_short_attempts_are_not_thrown_away(self):
        # 실사고 재현: 459자 → 477자, 둘 다 임계 미달
        attempts = [_res("a" * 459), _res("b" * 477)]
        with mock.patch.object(router.time, "sleep"):
            got = router._retry(lambda i: attempts[i], attempts=2, label="test")
        self.assertIsNotNone(got, "짧다는 이유로 결과를 통째로 버리면 안 된다")
        self.assertEqual(len(got.text), 477, "회차 중 가장 긴 결과를 남겨야 한다")

    def test_good_result_returns_immediately(self):
        calls = []

        def f(i):
            calls.append(i)
            return _res("a" * 900)

        got = router._retry(f, attempts=2, label="test")
        self.assertEqual(len(calls), 1, "충분한 결과를 얻으면 재시도하지 않는다")
        self.assertEqual(len(got.text), 900)

    def test_all_attempts_raise_returns_none(self):
        def boom(i):
            raise RuntimeError("goto timeout")

        with mock.patch.object(router.time, "sleep"):
            self.assertIsNone(router._retry(boom, attempts=2, label="test"))

    def test_skip_reason_short_circuits(self):
        calls = []

        def f(i):
            calls.append(i)
            r = _res("", ok=False)
            r.skip_reason = "ig_login_wall"
            return r

        got = router._retry(f, attempts=2, label="test")
        self.assertEqual(len(calls), 1)
        self.assertEqual(got.skip_reason, "ig_login_wall")


class ScrapeChainTest(unittest.TestCase):
    """v5.4 부터 체인 끝에 Jina Reader 가 붙는다 — 여기서는 항상 꺼두고 3단계까지만 본다."""

    """scrape() 전체 체인 — Playwright 짧은 결과 vs requests 폴백."""

    def _run(self, playwright_texts, fallback_text):
        pw = mock.Mock()
        pw.scrape.side_effect = [_res(t) for t in playwright_texts]
        fb = mock.Mock()
        fb.scrape.return_value = _res(fallback_text)
        with _stub_modules(pw, fb), mock.patch.object(router.time, "sleep"):
            return router.scrape("https://example.com/page")

    def test_playwright_477_beats_fallback_103(self):
        got = self._run(["a" * 459, "b" * 477], "c" * 103)
        self.assertEqual(len(got.text), 477,
                         "폴백이 더 짧으면 Playwright 결과를 유지해야 한다")

    def test_fallback_wins_when_actually_longer(self):
        got = self._run(["a" * 50, "a" * 60], "c" * 2000)
        self.assertEqual(len(got.text), 2000)

    def test_good_playwright_skips_fallback(self):
        fb = mock.Mock()
        pw = mock.Mock()
        pw.scrape.return_value = _res("a" * 1200)
        with _stub_modules(pw, fb):
            got = router.scrape("https://example.com/page")
        fb.scrape.assert_not_called()
        self.assertEqual(len(got.text), 1200)

    def test_fallback_exception_keeps_playwright_result(self):
        pw = mock.Mock()
        pw.scrape.side_effect = [_res("a" * 300), _res("a" * 300)]
        fb = mock.Mock()
        fb.scrape.side_effect = RuntimeError("connection reset")
        with _stub_modules(pw, fb), mock.patch.object(router.time, "sleep"):
            got = router.scrape("https://example.com/page")
        self.assertEqual(len(got.text), 300, "폴백이 터져도 확보한 본문은 남아야 한다")

    def test_everything_fails_returns_error_result(self):
        pw = mock.Mock()
        pw.scrape.side_effect = RuntimeError("goto timeout")
        fb = mock.Mock()
        fb.scrape.side_effect = RuntimeError("dns")
        with _stub_modules(pw, fb), mock.patch.object(router.time, "sleep"):
            got = router.scrape("https://example.com/page")
        self.assertFalse(got.ok)
        self.assertTrue(got.error)


if __name__ == "__main__":
    unittest.main()
