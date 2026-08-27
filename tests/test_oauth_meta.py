"""scripts.mcp_remote.oauth_meta — discovery 메타데이터 + 동적 등록 (네트워크 0)."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from flask import Flask

from scripts.auth_store import AuthStore
from scripts.mcp_remote.oauth_meta import register_oauth_meta
from scripts.mcp_remote.oauth_store import OAuthStore

BASE = "https://aiskillbox.600g.net"


def _cfg(dcr: bool):
    return {"enabled": True, "public_base_url": BASE, "dynamic_registration": dcr,
            "allowed_origins": ["https://claude.ai"], "access_ttl_seconds": 3600,
            "refresh_ttl_seconds": 7776000}


class MetaTest(unittest.TestCase):
    def _client(self, dcr=False):
        self.dir = Path(tempfile.mkdtemp(prefix="oauth_meta_"))
        self.auth = AuthStore(self.dir / "auth.json")
        self.st = OAuthStore(self.dir / "oauth.json", auth_store=self.auth)
        app = Flask(__name__)
        app.config["TESTING"] = True
        register_oauth_meta(app, store=self.st, cfg=_cfg(dcr))
        return app.test_client()

    def tearDown(self):
        shutil.rmtree(getattr(self, "dir", Path(tempfile.gettempdir())), ignore_errors=True)

    def test_protected_resource_metadata(self):
        r = self._client().get("/.well-known/oauth-protected-resource")
        self.assertEqual(r.status_code, 200)
        b = r.get_json()
        self.assertEqual(b["resource"], BASE + "/mcp")
        self.assertEqual(b["authorization_servers"], [BASE])
        self.assertIn("skills:read", b["scopes_supported"])

    def test_protected_resource_path_variant(self):
        r = self._client().get("/.well-known/oauth-protected-resource/mcp")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["resource"], BASE + "/mcp")

    def test_as_metadata_shape(self):
        b = self._client().get("/.well-known/oauth-authorization-server").get_json()
        self.assertEqual(b["issuer"], BASE)
        self.assertEqual(b["authorization_endpoint"], BASE + "/oauth/authorize")
        self.assertEqual(b["token_endpoint"], BASE + "/oauth/token")
        self.assertEqual(b["code_challenge_methods_supported"], ["S256"])
        self.assertIn("authorization_code", b["grant_types_supported"])
        self.assertIn("refresh_token", b["grant_types_supported"])

    def test_no_http_urls_anywhere(self):
        """CF Tunnel 함정 회귀 가드."""
        import json as _json
        for path in ("/.well-known/oauth-protected-resource",
                     "/.well-known/oauth-authorization-server"):
            raw = _json.dumps(self._client().get(path).get_json())
            self.assertNotIn("http://", raw, path)

    def test_registration_endpoint_absent_when_toggle_off(self):
        b = self._client(dcr=False).get("/.well-known/oauth-authorization-server").get_json()
        self.assertNotIn("registration_endpoint", b)

    def test_registration_endpoint_present_when_toggle_on(self):
        b = self._client(dcr=True).get("/.well-known/oauth-authorization-server").get_json()
        self.assertEqual(b["registration_endpoint"], BASE + "/oauth/register")

    def test_register_is_404_when_toggle_off(self):
        r = self._client(dcr=False).post("/oauth/register",
                                         json={"redirect_uris": ["https://claude.ai/cb"]})
        self.assertEqual(r.status_code, 404)

    def test_register_creates_client_when_toggle_on(self):
        c = self._client(dcr=True)
        r = c.post("/oauth/register", json={"redirect_uris": ["https://claude.ai/cb"],
                                            "client_name": "Claude"})
        self.assertEqual(r.status_code, 201)
        b = r.get_json()
        self.assertTrue(b["client_id"])
        self.assertEqual(b["redirect_uris"], ["https://claude.ai/cb"])
        self.assertEqual(self.st.get_client(b["client_id"])["source"], "dynamic")

    def test_register_rejects_missing_redirect_uris(self):
        r = self._client(dcr=True).post("/oauth/register", json={"client_name": "X"})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["error"], "invalid_redirect_uri")

    def test_register_rejects_non_https_redirect(self):
        r = self._client(dcr=True).post("/oauth/register",
                                        json={"redirect_uris": ["http://evil.example/cb"]})
        self.assertEqual(r.status_code, 400)

    def test_register_locks_after_repeated_failures(self):
        c = self._client(dcr=True)
        for _ in range(5):
            c.post("/oauth/register", json={})
        r = c.post("/oauth/register", json={"redirect_uris": ["https://claude.ai/cb"]})
        self.assertEqual(r.status_code, 429)
