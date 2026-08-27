"""scripts.auth_routes — 전체 잠금 게이트 + /api/auth/* (Flask test client, 네트워크 0).

pin_ok 는 가짜 주입 — 실제 ADMIN_PIN/잠금 로직은 app.py 소유.
"""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from flask import Flask, jsonify

from scripts.auth_routes import register_auth
from scripts.auth_store import AuthStore

GOOD_PIN = "0910"


def _pin_ok(supplied: str):
    if supplied == GOOD_PIN:
        return True, ""
    return False, "PIN 불일치 — 4회 남음"


class AuthRoutesTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="auth_routes_"))
        self.store = AuthStore(self.dir / "auth.json")
        app = Flask(__name__)
        app.config["TESTING"] = True

        @app.get("/")
        def home():
            return "MAIN"

        @app.get("/catalog")
        def catalog():
            return "CATALOG"

        @app.get("/api/library/search")
        def search():
            return jsonify({"ok": True, "results": []})

        @app.get("/healthz")
        def healthz():
            return jsonify({"ok": True})

        @app.get("/static/style.css")
        def style():
            return "css"

        @app.post("/mcp")
        def mcp():
            return jsonify({"ok": True})

        @app.get("/.well-known/oauth-authorization-server")
        def as_meta():
            return jsonify({"ok": True})

        @app.get("/oauth/authorize")
        def oauth_authorize():
            return "AUTHORIZE"

        register_auth(app, store=self.store, pin_ok=_pin_ok, login_template=None)
        self.client = app.test_client()

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    # ── 게이트 ──────────────────────────────────────────────

    def test_unauthenticated_page_redirects_to_login(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login?next=%2F", r.headers["Location"])
        r2 = self.client.get("/catalog")
        self.assertIn("/login?next=%2Fcatalog", r2.headers["Location"])

    def test_unauthenticated_api_gets_401_json(self):
        r = self.client.get("/api/library/search?q=x")
        self.assertEqual(r.status_code, 401)
        data = r.get_json()
        self.assertFalse(data["ok"])
        self.assertTrue(data["need_login"])

    def test_allowlist_paths_pass_without_auth(self):
        self.assertEqual(self.client.get("/healthz").status_code, 200)
        self.assertEqual(self.client.get("/static/style.css").status_code, 200)
        self.assertEqual(self.client.get("/login").status_code, 200)

    def test_options_preflight_passes(self):
        r = self.client.open("/api/library/search", method="OPTIONS")
        self.assertLess(r.status_code, 400)

    def test_mcp_bypasses_gate(self):
        """/mcp 는 자체 Bearer 인증을 가지므로 게이트를 통과해야 한다."""
        r = self.client.post("/mcp", json={})
        self.assertEqual(r.status_code, 200)

    def test_well_known_bypasses_gate(self):
        r = self.client.get("/.well-known/oauth-authorization-server")
        self.assertEqual(r.status_code, 200)

    def test_oauth_path_bypasses_gate(self):
        r = self.client.get("/oauth/authorize")
        self.assertEqual(r.status_code, 200)

    def test_unrelated_path_still_gated(self):
        """예외 추가가 게이트를 넓히지 않았는지 — 회귀 가드."""
        r = self.client.get("/catalog")
        self.assertEqual(r.status_code, 302)

    def test_unknown_oauth_subpath_is_gated(self):
        """exact-match 전환 회귀 가드 — /oauth/ 아래 미등록 경로는 게이트에 걸려야 한다.

        prefix 방식이었다면 이 경로가 조용히 통과했다 (fail-open). 정확 일치라 막힌다.
        """
        r = self.client.get("/oauth/some-future-endpoint")
        self.assertNotEqual(r.status_code, 200)

    def test_unknown_well_known_subpath_is_gated(self):
        r = self.client.get("/.well-known/something-else")
        self.assertNotEqual(r.status_code, 200)

    # ── redeem ──────────────────────────────────────────────

    def test_redeem_sets_cookie_and_grants_access(self):
        code = self.store.create_code("폰")
        r = self.client.post("/api/auth/redeem", json={"code": code, "device": "테스트"})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertTrue(body["ok"])
        self.assertTrue(body["token"])
        self.assertIn("aiskillbox_auth=", r.headers.get("Set-Cookie", ""))
        # 쿠키가 test client 에 저장됨 → 이후 요청 통과
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/api/library/search?q=x").status_code, 200)

    def test_header_token_grants_access(self):
        code = self.store.create_code("agent")
        token = self.store.redeem(code, device="mcp")
        r = self.client.get("/api/library/search?q=x", headers={"X-Auth-Token": token})
        self.assertEqual(r.status_code, 200)

    def test_redeem_bad_code_401_generic_message(self):
        r = self.client.post("/api/auth/redeem", json={"code": "DGN-XXXX-YYYY"})
        self.assertEqual(r.status_code, 401)
        self.assertNotIn("존재", r.get_json()["error"])  # 코드 존재 여부 노출 금지

    def test_redeem_lockout_after_failures(self):
        for _ in range(5):
            self.client.post("/api/auth/redeem", json={"code": "DGN-BAD1-BAD1"})
        r = self.client.post("/api/auth/redeem", json={"code": "DGN-BAD1-BAD1"})
        self.assertEqual(r.status_code, 429)

    # ── bootstrap ───────────────────────────────────────────

    def test_bootstrap_with_pin_creates_code_and_logs_in(self):
        r = self.client.post("/api/auth/bootstrap", json={"pin": GOOD_PIN, "device": "오너 Mac"})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertTrue(body["ok"])
        self.assertTrue(body["code"].startswith("DGN-"))
        self.assertTrue(body["token"])
        self.assertEqual(self.client.get("/").status_code, 200)   # 쿠키로 즉시 통과
        self.assertEqual(len(self.store.list_codes()), 1)

    def test_bootstrap_wrong_pin_401(self):
        r = self.client.post("/api/auth/bootstrap", json={"pin": "9999"})
        self.assertEqual(r.status_code, 401)
        self.assertIn("PIN", r.get_json()["error"])

    # ── 코드 관리 (로그인 + PIN 이중 게이트) ─────────────────

    def _login(self) -> None:
        code = self.store.create_code("셋업")
        self.client.post("/api/auth/redeem", json={"code": code})

    def test_codes_crud_requires_login_and_pin(self):
        # 미로그인 → 401 (게이트)
        self.assertEqual(self.client.get("/api/auth/codes").status_code, 401)
        self._login()
        # 로그인 + PIN 없음 → 403
        self.assertEqual(self.client.get("/api/auth/codes").status_code, 403)
        # 로그인 + PIN → OK
        h = {"X-Admin-Pin": GOOD_PIN}
        r = self.client.post("/api/auth/codes", json={"label": "가족"}, headers=h)
        self.assertEqual(r.status_code, 200)
        new_code = r.get_json()["code"]
        rows = self.client.get("/api/auth/codes", headers=h).get_json()["codes"]
        self.assertIn(new_code, [x["code"] for x in rows])
        # 삭제 = cascade
        t = self.store.redeem(new_code, device="d")
        r2 = self.client.delete(f"/api/auth/codes/{new_code}", headers=h)
        self.assertEqual(r2.get_json()["revoked_sessions"], 1)
        self.assertFalse(self.store.check_token(t))

    def test_deleted_code_token_immediately_blocked(self):
        code = self.store.create_code("임시")
        token = self.store.redeem(code, device="d")
        self.assertEqual(
            self.client.get("/api/library/search?q=x", headers={"X-Auth-Token": token}).status_code, 200)
        self.store.delete_code(code)
        self.assertEqual(
            self.client.get("/api/library/search?q=x", headers={"X-Auth-Token": token}).status_code, 401)


if __name__ == "__main__":
    unittest.main()
