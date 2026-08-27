"""scripts.mcp_remote.oauth_grants — authorize/token/revoke (Flask test client, 네트워크 0)."""
from __future__ import annotations

import base64
import hashlib
import shutil
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from flask import Flask

from scripts.auth_routes import COOKIE_NAME
from scripts.auth_store import AuthStore
from scripts.mcp_remote.oauth_grants import register_oauth_grants
from scripts.mcp_remote.oauth_store import OAuthStore

BASE = "https://aiskillbox.600g.net"
RESOURCE = BASE + "/mcp"
REDIRECT = "https://claude.ai/api/mcp/auth_callback"
VERIFIER = "a" * 64


def _challenge(verifier: str) -> str:
    d = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(d).rstrip(b"=").decode("ascii")


CFG = {"enabled": True, "public_base_url": BASE, "dynamic_registration": False,
       "allowed_origins": ["https://claude.ai"], "access_ttl_seconds": 3600,
       "refresh_ttl_seconds": 7776000}


class GrantsTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="oauth_grants_"))
        self.auth = AuthStore(self.dir / "auth.json")
        self.code = self.auth.create_code("테스트")
        self.token = self.auth.redeem(self.code, device="test")
        self.st = OAuthStore(self.dir / "oauth.json", auth_store=self.auth)
        self.cid, self.secret = self.st.create_client("Claude", [REDIRECT])
        app = Flask(__name__)
        app.config["TESTING"] = True
        register_oauth_grants(app, store=self.st, auth=self.auth, cfg=CFG,
                              consent_template=None)
        self.c = app.test_client()

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _authorize_qs(self, **over):
        q = {"response_type": "code", "client_id": self.cid, "redirect_uri": REDIRECT,
             "code_challenge": _challenge(VERIFIER), "code_challenge_method": "S256",
             "state": "xyz", "resource": RESOURCE, "scope": "skills:read"}
        q.update(over)
        return "&".join(f"{k}={v}" for k, v in q.items() if v is not None)

    def _login(self):
        self.c.set_cookie(COOKIE_NAME, self.token)   # Flask 3.x 시그니처

    def _get_code(self):
        self._login()
        r = self.c.post("/oauth/authorize?" + self._authorize_qs(), data={"approve": "yes"})
        self.assertEqual(r.status_code, 302)
        return parse_qs(urlparse(r.headers["Location"]).query)["code"][0]

    # ── authorize ──

    def test_unauthenticated_redirects_to_login_preserving_query(self):
        r = self.c.get("/oauth/authorize?" + self._authorize_qs())
        self.assertEqual(r.status_code, 302)
        loc = r.headers["Location"]
        self.assertIn("/login", loc)
        self.assertIn("code_challenge", loc)   # 쿼리스트링이 살아있어야 한다
        self.assertIn("state", loc)

    def test_authenticated_shows_consent(self):
        self._login()
        r = self.c.get("/oauth/authorize?" + self._authorize_qs())
        self.assertEqual(r.status_code, 200)

    def test_approve_issues_code_with_state(self):
        self._login()
        r = self.c.post("/oauth/authorize?" + self._authorize_qs(), data={"approve": "yes"})
        self.assertEqual(r.status_code, 302)
        q = parse_qs(urlparse(r.headers["Location"]).query)
        self.assertTrue(q["code"][0])
        self.assertEqual(q["state"][0], "xyz")

    def test_deny_redirects_with_access_denied(self):
        self._login()
        r = self.c.post("/oauth/authorize?" + self._authorize_qs(), data={})
        q = parse_qs(urlparse(r.headers["Location"]).query)
        self.assertEqual(q["error"][0], "access_denied")

    def test_redirect_uri_mismatch_does_not_redirect(self):
        self._login()
        r = self.c.get("/oauth/authorize?" + self._authorize_qs(
            redirect_uri="https://evil.example/cb"))
        self.assertEqual(r.status_code, 400)
        self.assertNotIn("Location", r.headers)   # 오픈 리다이렉터 방지

    def test_unknown_client_does_not_redirect(self):
        self._login()
        r = self.c.get("/oauth/authorize?" + self._authorize_qs(client_id="nope"))
        self.assertEqual(r.status_code, 400)
        self.assertNotIn("Location", r.headers)

    def test_plain_pkce_is_rejected(self):
        self._login()
        r = self.c.get("/oauth/authorize?" + self._authorize_qs(code_challenge_method="plain"))
        self.assertEqual(r.status_code, 400)

    def test_missing_pkce_is_rejected(self):
        self._login()
        r = self.c.get("/oauth/authorize?" + self._authorize_qs(code_challenge=None))
        self.assertEqual(r.status_code, 400)

    def test_redirect_uri_with_existing_query_is_appended_correctly(self):
        cid2, _ = self.st.create_client("Q", ["https://ex.example/cb?tenant=1"])
        self._login()
        q = ("response_type=code&client_id=" + cid2 +
             "&redirect_uri=https://ex.example/cb?tenant=1"
             "&code_challenge=" + _challenge(VERIFIER) +
             "&code_challenge_method=S256&state=xyz&resource=" + RESOURCE +
             "&scope=skills:read")
        r = self.c.post("/oauth/authorize?" + q, data={"approve": "yes"})
        self.assertEqual(r.status_code, 302)
        loc = r.headers["Location"]
        self.assertEqual(loc.count("?"), 1)
        parsed = parse_qs(urlparse(loc).query)
        self.assertEqual(parsed["tenant"], ["1"])
        self.assertTrue(parsed["code"][0])

    # ── token ──

    def test_token_exchange_succeeds(self):
        code = self._get_code()
        r = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE})
        self.assertEqual(r.status_code, 200)
        b = r.get_json()
        self.assertEqual(b["token_type"], "Bearer")
        self.assertEqual(b["scope"], "skills:read")
        self.assertTrue(b["access_token"] and b["refresh_token"])
        self.assertIsNotNone(self.st.validate_access(b["access_token"], resource=RESOURCE))

    def test_token_response_has_no_store_cache_control(self):
        """RFC 6749 §5.1 MUST — 토큰 응답은 캐시되면 안 된다 (CF 뒤에 있는 서버)."""
        code = self._get_code()
        r = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers["Cache-Control"], "no-store")

    def test_token_exchange_via_http_basic_auth(self):
        """RFC 6749 §2.3.1 — client_secret_basic 도 지원해야 한다 (claude.ai 실사용 방식 미확인)."""
        code = self._get_code()
        basic = base64.b64encode(f"{self.cid}:{self.secret}".encode("utf-8")).decode("ascii")
        r = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "code_verifier": VERIFIER, "resource": RESOURCE},
            headers={"Authorization": f"Basic {basic}"})
        self.assertEqual(r.status_code, 200)
        b = r.get_json()
        self.assertTrue(b["access_token"])

    def test_token_rejects_wrong_verifier(self):
        code = self._get_code()
        r = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": "b" * 64, "resource": RESOURCE})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["error"], "invalid_grant")

    def test_token_rejects_bad_client_secret(self):
        code = self._get_code()
        r = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": "wrong",
            "code_verifier": VERIFIER, "resource": RESOURCE})
        self.assertEqual(r.status_code, 401)

    def test_token_locks_after_repeated_bad_secrets(self):
        for _ in range(5):
            self.c.post("/oauth/token", data={"grant_type": "authorization_code",
                                              "client_id": self.cid, "client_secret": "wrong"})
        r = self.c.post("/oauth/token", data={"grant_type": "authorization_code",
                                              "client_id": self.cid,
                                              "client_secret": self.secret})
        self.assertEqual(r.status_code, 429)

    def test_token_locks_after_repeated_bad_codes_with_valid_secret(self):
        """유효한 secret + 잘못된 code 를 반복해도 잠금이 걸려야 한다 (guard.ok 위치 회귀)."""
        for _ in range(5):
            r = self.c.post("/oauth/token", data={
                "grant_type": "authorization_code", "code": "bogus",
                "redirect_uri": REDIRECT, "client_id": self.cid,
                "client_secret": self.secret, "code_verifier": VERIFIER,
                "resource": RESOURCE})
            self.assertEqual(r.status_code, 400)
        r = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": "bogus",
            "redirect_uri": REDIRECT, "client_id": self.cid,
            "client_secret": self.secret, "code_verifier": VERIFIER,
            "resource": RESOURCE})
        self.assertEqual(r.status_code, 429)

    def test_code_reuse_revokes_all_grants_of_client(self):
        code = self._get_code()
        ok = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE}).get_json()
        again = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE})
        self.assertEqual(again.status_code, 400)
        self.assertIsNone(self.st.validate_access(ok["access_token"], resource=RESOURCE))

    def test_refresh_rotates(self):
        code = self._get_code()
        first = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE}).get_json()
        r = self.c.post("/oauth/token", data={
            "grant_type": "refresh_token", "refresh_token": first["refresh_token"],
            "client_id": self.cid, "client_secret": self.secret})
        self.assertEqual(r.status_code, 200)
        self.assertNotEqual(r.get_json()["refresh_token"], first["refresh_token"])

    def test_scope_narrowed_to_skills_read(self):
        self._login()
        r = self.c.post("/oauth/authorize?" + self._authorize_qs(scope="admin:all"),
                        data={"approve": "yes"})
        code = parse_qs(urlparse(r.headers["Location"]).query)["code"][0]
        b = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE}).get_json()
        self.assertEqual(b["scope"], "skills:read")

    def test_other_client_cannot_destroy_code(self):
        """남의 인가코드로 교환 시도해도 그 코드가 파괴되지 않아야 한다 (무흔적 DoS 차단)."""
        other_cid, other_secret = self.st.create_client("Evil", [REDIRECT])
        code = self._get_code()
        bad = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": other_cid, "client_secret": other_secret,
            "code_verifier": VERIFIER, "resource": RESOURCE})
        self.assertEqual(bad.status_code, 400)
        # 정당한 소유자의 교환이 **여전히 성공**해야 한다
        ok = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE})
        self.assertEqual(ok.status_code, 200)
        self.assertTrue(ok.get_json()["access_token"])

    def test_refresh_rejects_other_clients_token(self):
        """RFC 6749 §6 — 다른 클라이언트의 refresh 토큰은 회전시킬 수 없다."""
        other_cid, other_secret = self.st.create_client("Evil", [REDIRECT])
        code = self._get_code()
        mine = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE}).get_json()
        r = self.c.post("/oauth/token", data={
            "grant_type": "refresh_token", "refresh_token": mine["refresh_token"],
            "client_id": other_cid, "client_secret": other_secret})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["error"], "invalid_grant")
        # 원 소유자의 회전은 여전히 동작해야 한다
        good = self.c.post("/oauth/token", data={
            "grant_type": "refresh_token", "refresh_token": mine["refresh_token"],
            "client_id": self.cid, "client_secret": self.secret})
        self.assertEqual(good.status_code, 200)

    # ── revoke ──

    def test_revoke_locks_after_repeated_bad_secrets(self):
        for _ in range(5):
            self.c.post("/oauth/revoke", data={"token": "x", "client_id": self.cid,
                                               "client_secret": "wrong"})
        r = self.c.post("/oauth/revoke", data={"token": "x", "client_id": self.cid,
                                               "client_secret": self.secret})
        self.assertEqual(r.status_code, 429)

    def test_revoke_does_not_reset_token_lockout(self):
        """/oauth/revoke 성공이 /oauth/token 의 브루트포스 카운터를 씻으면 안 된다 (R-1).

        5회 실패(마지막 실패가 잠금을 건다) + 매회 사이 성공적인 revoke 호출 후, **별도의**
        6번째 요청에서 429 인지 확인한다 — 잠금을 발동시킨 요청 자신은 그 요청의 원래 오류
        (400) 를 반환하고, 잠금은 그 다음 요청부터 적용되기 때문에 6번째가 필요하다
        (F-1 의 test_token_locks_after_repeated_bad_codes_with_valid_secret 과 동일 구조).
        """
        for _ in range(5):
            self.c.post("/oauth/token", data={
                "grant_type": "authorization_code", "code": "bogus",
                "redirect_uri": REDIRECT, "client_id": self.cid,
                "client_secret": self.secret, "code_verifier": VERIFIER,
                "resource": RESOURCE})
            self.c.post("/oauth/revoke", data={"token": "x", "client_id": self.cid,
                                               "client_secret": self.secret})
        r = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": "bogus",
            "redirect_uri": REDIRECT, "client_id": self.cid,
            "client_secret": self.secret, "code_verifier": VERIFIER,
            "resource": RESOURCE})
        self.assertEqual(r.status_code, 429)

    def test_revoke_kills_token_and_returns_200_for_unknown(self):
        code = self._get_code()
        b = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE}).get_json()
        r = self.c.post("/oauth/revoke", data={"token": b["access_token"],
                                               "client_id": self.cid,
                                               "client_secret": self.secret})
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(self.st.validate_access(b["access_token"], resource=RESOURCE))
        r2 = self.c.post("/oauth/revoke", data={"token": "unknown",
                                                "client_id": self.cid,
                                                "client_secret": self.secret})
        self.assertEqual(r2.status_code, 200)
