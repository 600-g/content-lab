"""scripts.library.routes — Flask test client 로 /api/library/* + /catalog 검증 (네트워크 0)."""
from __future__ import annotations

import json
import shutil
import unittest

from flask import Flask

from tests.fixtures import SKILLS, make_mirror

from scripts.library import index as lib_index
from scripts.library import routes as lib_routes


class LibraryRoutesTest(unittest.TestCase):
    def setUp(self):
        self.root = make_mirror()
        app = Flask(__name__)
        app.config["TESTING"] = True
        # 의미 검색은 주입된 embed (항상 None) → 키워드만. 네트워크 호출 없음.
        lib_routes.register_library_routes(
            app, mirror_root=self.root, embed_fn=lambda q: None, vectors_loader=lambda: {},
        )
        self.client = app.test_client()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)
        lib_index.get_index(self.root, force=True)  # 캐시 정리 (다음 테스트 영향 최소화)

    def test_search_ok(self):
        r = self.client.get("/api/library/search?q=인스타 대본&k=3")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["results"][0]["slug"], "instagram-reels-script-automation")
        self.assertFalse(data["semantic_used"])
        self.assertEqual(r.headers.get("Access-Control-Allow-Origin"), "*")

    def test_search_too_short_400(self):
        r = self.client.get("/api/library/search?q=a")
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.get_json()["ok"])

    def test_search_missing_q_400(self):
        r = self.client.get("/api/library/search")
        self.assertEqual(r.status_code, 400)

    def test_search_filters(self):
        r = self.client.get("/api/library/search?q=프롬프트&category=업무&mode=keyword")
        data = r.get_json()
        self.assertTrue(all(x["category"] == "업무" for x in data["results"]))
        self.assertEqual(data["mode"], "keyword")

    def test_list_skills(self):
        r = self.client.get("/api/library/skills")
        data = r.get_json()
        self.assertEqual(data["total"], len(SKILLS))
        self.assertEqual(len(data["items"]), len(SKILLS))
        self.assertNotIn("body_md", data["items"][0])   # 목록은 메타만
        r2 = self.client.get("/api/library/skills?grade=S")
        self.assertEqual(r2.get_json()["total"], 1)

    def test_get_skill_json_and_raw(self):
        r = self.client.get("/api/library/skills/notion-mcp-setup")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["slug"], "notion-mcp-setup")
        self.assertIn("따라 하기", data["body_md"])
        self.assertTrue(data["raw_md"].startswith("---"))
        self.assertEqual(data["meta"]["category"], "개발")

        raw = self.client.get("/api/library/skills/notion-mcp-setup?format=raw")
        self.assertEqual(raw.status_code, 200)
        self.assertTrue(raw.content_type.startswith("text/markdown"))
        self.assertIn("name: notion-mcp-setup", raw.get_data(as_text=True))

    def test_get_skill_404_and_bad_slug(self):
        self.assertEqual(self.client.get("/api/library/skills/nope-not-here").status_code, 404)
        r = self.client.get("/api/library/skills/..%2F..%2Fetc%2Fpasswd")
        self.assertIn(r.status_code, (400, 404))

    def test_stats(self):
        data = self.client.get("/api/library/stats").get_json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["total"], len(SKILLS))
        self.assertIn("by_category", data)

    def test_catalog_html_and_etag(self):
        r = self.client.get("/catalog")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.content_type.startswith("text/html"))
        body = r.get_data(as_text=True)
        self.assertIn('<article class="card"', body)
        self.assertIn("Content-Security-Policy", body)
        etag = r.headers.get("ETag")
        self.assertTrue(etag)
        r2 = self.client.get("/catalog", headers={"If-None-Match": etag})
        self.assertEqual(r2.status_code, 304)
        self.assertEqual(self.client.get("/catalog.html").status_code, 200)

    def test_secret_like_strings_are_redacted_in_bodies(self):
        # 본문에 키 모양 문자열이 섞여 들어간 경우 서빙 전 마스킹
        p = self.root / "legacy-no-meta" / "SKILL.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nAIzaSyD-1234567890abcdefghijklmnopqrstu\n", encoding="utf-8")
        lib_index.get_index(self.root, force=True)
        r = self.client.get("/api/library/skills/legacy-no-meta")
        self.assertNotIn("AIzaSyD-1234567890", r.get_data(as_text=True))
        self.assertIn("[REDACTED]", r.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
