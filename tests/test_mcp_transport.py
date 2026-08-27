"""scripts.mcp_remote.transport — POST /mcp Streamable HTTP (Flask test client, 네트워크 0)."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from flask import Flask

from scripts.auth_store import AuthStore
from scripts.mcp_remote.oauth_store import OAuthStore
from scripts.mcp_remote.transport import register_transport

BASE = "https://aiskillbox.600g.net"
RESOURCE = BASE + "/mcp"
CFG = {"enabled": True, "public_base_url": BASE, "dynamic_registration": False,
       "allowed_origins": ["https://claude.ai"], "access_ttl_seconds": 3600,
       "refresh_ttl_seconds": 7776000}


class TransportTest(unittest.TestCase):
    def setUp(self):
        from scripts.library import mcp_server as ms
        self._ms = ms
        self._saved_force = getattr(ms, "_FORCE_LOCAL", False)

        self.dir = Path(tempfile.mkdtemp(prefix="mcp_tr_"))
        self.auth = AuthStore(self.dir / "auth.json")
        self.code = self.auth.create_code("테스트")
        self.st = OAuthStore(self.dir / "oauth.json", auth_store=self.auth)
        self.access, _, _ = self.st.issue_tokens(
            {"client_id": "c1", "resource": RESOURCE, "scope": "skills:read",
             "invite_code": self.code}, access_ttl=600, refresh_ttl=600)
        app = Flask(__name__)
        app.config["TESTING"] = True
        register_transport(app, store=self.st, cfg=CFG)
        self.c = app.test_client()

    def tearDown(self):
        self._ms._FORCE_LOCAL = self._saved_force
        shutil.rmtree(self.dir, ignore_errors=True)

    def _post(self, body, token=None, origin="https://claude.ai"):
        h = {"Content-Type": "application/json"}
        if token:
            h["Authorization"] = "Bearer " + token
        if origin:
            h["Origin"] = origin
        return self.c.post("/mcp", json=body, headers=h)

    def test_no_token_is_401_with_resource_metadata_header(self):
        r = self._post({"jsonrpc": "2.0", "id": 1, "method": "ping"})
        self.assertEqual(r.status_code, 401)
        www = r.headers.get("WWW-Authenticate", "")
        self.assertIn("Bearer", www)
        self.assertIn("/.well-known/oauth-protected-resource", www)
        self.assertIn("https://", www)
        self.assertNotIn("http://", www)

    def test_bad_token_is_401(self):
        r = self._post({"jsonrpc": "2.0", "id": 1, "method": "ping"}, token="nope")
        self.assertEqual(r.status_code, 401)

    def test_revoked_invite_code_is_401(self):
        self.auth.delete_code(self.code)
        r = self._post({"jsonrpc": "2.0", "id": 1, "method": "ping"}, token=self.access)
        self.assertEqual(r.status_code, 401)

    def test_initialize_roundtrip(self):
        r = self._post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                        "params": {"protocolVersion": "2025-06-18"}}, token=self.access)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers["Content-Type"].split(";")[0], "application/json")
        body = r.get_json()
        self.assertEqual(body["id"], 1)
        self.assertEqual(body["result"]["serverInfo"]["name"], "skill-library")

    def test_tools_list_has_three_read_tools(self):
        r = self._post({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, token=self.access)
        names = {t["name"] for t in r.get_json()["result"]["tools"]}
        self.assertEqual(names, {"search_skills", "get_skill", "list_skills"})

    def test_notification_returns_202_no_body(self):
        r = self._post({"jsonrpc": "2.0", "method": "notifications/initialized"}, token=self.access)
        self.assertEqual(r.status_code, 202)
        self.assertEqual(r.get_data(), b"")

    def test_get_is_405(self):
        r = self.c.get("/mcp", headers={"Authorization": "Bearer " + self.access})
        self.assertEqual(r.status_code, 405)

    def test_bad_origin_is_403(self):
        r = self._post({"jsonrpc": "2.0", "id": 1, "method": "ping"},
                       token=self.access, origin="https://evil.example")
        self.assertEqual(r.status_code, 403)

    def test_missing_origin_is_allowed(self):
        """curl·서버간 호출은 Origin 이 없다 — 브라우저만 강제한다."""
        r = self._post({"jsonrpc": "2.0", "id": 1, "method": "ping"},
                       token=self.access, origin=None)
        self.assertEqual(r.status_code, 200)

    def test_batch_request(self):
        r = self._post([{"jsonrpc": "2.0", "id": 1, "method": "ping"},
                        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}], token=self.access)
        body = r.get_json()
        self.assertEqual(len(body), 2)
        self.assertEqual({m["id"] for m in body}, {1, 2})

    def test_malformed_json_is_jsonrpc_parse_error(self):
        r = self.c.post("/mcp", data="{not json",
                        headers={"Content-Type": "application/json",
                                 "Authorization": "Bearer " + self.access})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["error"]["code"], -32700)

    def test_register_transport_sets_local_backend(self):
        """register_transport 가 자기호출 루프 차단 스위치를 실제로 켰는지."""
        self.assertTrue(self._ms._FORCE_LOCAL)


if __name__ == "__main__":
    unittest.main()
