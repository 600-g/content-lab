"""collect() / /api/collect 의 텍스트 입력 경로 검증 (네트워크 0, LLM 0).

분석 단계는 mock — 여기서 보는 건 '스크랩을 건너뛰고 붙여넣은 본문이 분석까지
그대로 전달되는가' 와 '실패 안내가 실제로 존재하는 우회 경로를 가리키는가' 다.
"""
from __future__ import annotations

import json
import unittest
from unittest import mock

import app as app_module
from scripts import auth_store as auth_store_mod
from scripts import collect as collect_mod
from scripts.scraper import plain_text
from scripts.scraper.router import ScrapeResult


LONG = "이 문서는 Claude Code 토큰을 아끼는 실전 패턴을 정리한다. " * 20


class CollectPasteTest(unittest.TestCase):
    def test_paste_skips_scrape_and_feeds_analyzer(self):
        seen = {}

        def fake_analyze(d):
            seen.update(d)
            raise RuntimeError("stop-here")   # 분석 이후는 이 테스트의 관심사가 아니다

        with mock.patch.object(collect_mod, "scrape") as scr, \
             mock.patch.object(collect_mod, "analyze", side_effect=fake_analyze):
            with self.assertRaises(RuntimeError):
                collect_mod.collect(text=LONG, title="내 제목", register_notion=False)
            scr.assert_not_called()      # 스크래퍼는 호출조차 되면 안 된다

        self.assertEqual(seen["source_type"], "text")
        self.assertEqual(seen["title"], "내 제목")
        self.assertEqual(seen["text"], LONG.strip())
        self.assertTrue(plain_text.is_paste_source(seen["url"]))

    def test_origin_url_is_recorded_as_source(self):
        seen = {}

        def fake_analyze(d):
            seen.update(d)
            raise RuntimeError("stop")

        with mock.patch.object(collect_mod, "analyze", side_effect=fake_analyze):
            with self.assertRaises(RuntimeError):
                collect_mod.collect("https://chatgpt.com/share/abc", text=LONG,
                                    register_notion=False)
        self.assertEqual(seen["url"], "https://chatgpt.com/share/abc")

    def test_short_paste_is_rejected_with_its_own_message(self):
        r = collect_mod.collect(text="너무 짧다", register_notion=False)
        self.assertFalse(r["ok"])
        self.assertIn("붙여넣은 텍스트가", r["error_ko"])
        self.assertEqual(r["stages"]["scrape"]["stage"], "텍스트 입력")

    def test_paste_uses_lower_threshold_than_scraping(self):
        self.assertLess(plain_text.TEXT_MIN_LEN, collect_mod.MIN_TEXT_LEN)

    def test_scrape_failure_hint_points_at_the_paste_tab(self):
        """예전엔 '텍스트로 옮겨 등록하세요' 라고만 하고 그 수단이 없었다."""
        short = ScrapeResult(url="https://chatgpt.com/g/abc", source_type="web",
                             title="t", text="a" * 103, meta={}, ok=True)
        with mock.patch.object(collect_mod, "scrape", return_value=short):
            r = collect_mod.collect("https://chatgpt.com/g/abc", register_notion=False)
        self.assertFalse(r["ok"])
        self.assertIn("103자", r["error_ko"])
        self.assertIn("텍스트", r["hint"])

    def test_blocked_url_also_gets_the_paste_hint(self):
        blocked = ScrapeResult(url="https://instagram.com/p/x", source_type="instagram",
                               title="", text="", meta={}, ok=False,
                               skip_reason="ig_login_wall",
                               skip_message_ko="로그인 벽입니다.")
        with mock.patch.object(collect_mod, "scrape", return_value=blocked):
            r = collect_mod.collect("https://instagram.com/p/x", register_notion=False)
        self.assertTrue(r["skipped"])
        self.assertIn("텍스트", r["message_ko"])


class ApiCollectTest(unittest.TestCase):
    def setUp(self):
        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()
        for patcher in (
            mock.patch.object(app_module, "JOB_QUEUE", app_module.queue.Queue()),
            # 전체 잠금(v4.6) 게이트 우회 — 인증은 test_auth_routes 의 관심사다.
            mock.patch.object(auth_store_mod.get_store(), "check_token", return_value=True),
            mock.patch.object(app_module, "_save_jobs"),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def _post(self, payload):
        return self.client.post("/api/collect", json=payload)

    def test_text_payload_accepted(self):
        r = self._post({"text": LONG, "title": "제목"})
        self.assertEqual(r.status_code, 200, r.data)
        jid = json.loads(r.data)["job_id"]
        job = app_module.JOBS[jid]
        self.assertEqual(job["input_kind"], "paste")
        self.assertEqual(job["text"], LONG.strip())
        self.assertEqual(job["url"], "")

    def test_body_pasted_into_url_field_is_accepted_not_400(self):
        """사용자가 링크칸에 본문을 통째로 붙여넣는 실수를 튕겨내지 않는다."""
        r = self._post({"url": LONG})
        self.assertEqual(r.status_code, 200, r.data)
        job = app_module.JOBS[json.loads(r.data)["job_id"]]
        self.assertEqual(job["input_kind"], "paste")

    def test_too_short_text_rejected(self):
        r = self._post({"text": "짧음"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("짧습니다", json.loads(r.data)["error"])

    def test_empty_payload_rejected(self):
        r = self._post({})
        self.assertEqual(r.status_code, 400)

    def test_url_still_works(self):
        r = self._post({"url": "https://youtu.be/abc123"})
        self.assertEqual(r.status_code, 200, r.data)
        job = app_module.JOBS[json.loads(r.data)["job_id"]]
        self.assertEqual(job["input_kind"], "url")
        self.assertEqual(job["url"], "https://youtu.be/abc123")

    def test_malformed_url_still_rejected(self):
        r = self._post({"url": "ftp://x/y"})
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
