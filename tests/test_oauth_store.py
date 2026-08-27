"""scripts.mcp_remote.oauth_store — OAuth 저장소 (네트워크 0, 임시 디렉토리)."""
from __future__ import annotations

import shutil
import tempfile
import time
import unittest
from pathlib import Path

from scripts.auth_store import AuthStore
from scripts.mcp_remote.oauth_store import OAuthStore

RESOURCE = "https://aiskillbox.600g.net/mcp"


class HasCodeTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="oauth_store_"))
        self.auth = AuthStore(self.dir / "auth.json")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_has_code_true_after_create(self):
        code = self.auth.create_code("폰")
        self.assertTrue(self.auth.has_code(code))

    def test_has_code_false_after_delete(self):
        code = self.auth.create_code("폰")
        self.auth.delete_code(code)
        self.assertFalse(self.auth.has_code(code))

    def test_has_code_false_for_unknown(self):
        self.assertFalse(self.auth.has_code("DGN-ZZZZ-ZZZZ"))
        self.assertFalse(self.auth.has_code(""))

    def test_code_of_token_roundtrip(self):
        code = self.auth.create_code("폰")
        token = self.auth.redeem(code, device="test")
        self.assertEqual(self.auth.code_of_token(token), code)
        self.assertIsNone(self.auth.code_of_token("nope"))
        self.assertIsNone(self.auth.code_of_token(None))


class OAuthStoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="oauth_store_"))
        self.auth = AuthStore(self.dir / "auth.json")
        self.code = self.auth.create_code("테스트")
        self.st = OAuthStore(self.dir / "oauth.json", auth_store=self.auth)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _grant(self):
        return {"client_id": "c1", "resource": RESOURCE,
                "scope": "skills:read", "invite_code": self.code}

    def test_client_roundtrip(self):
        cid, secret = self.st.create_client("Claude", ["https://claude.ai/cb"])
        self.assertTrue(cid and secret)
        self.assertTrue(self.st.verify_client(cid, secret))
        self.assertFalse(self.st.verify_client(cid, "wrong"))
        self.assertEqual(self.st.get_client(cid)["redirect_uris"], ["https://claude.ai/cb"])

    def test_client_secret_never_stored_plaintext(self):
        cid, secret = self.st.create_client("Claude", ["https://claude.ai/cb"])
        raw = (self.dir / "oauth.json").read_text(encoding="utf-8")
        self.assertNotIn(secret, raw)
        self.assertIn(cid, raw)

    def test_public_client_has_no_secret(self):
        cid, secret = self.st.create_client("Pub", ["https://claude.ai/cb"], public=True)
        self.assertIsNone(secret)
        self.assertTrue(self.st.verify_client(cid, None))

    def test_code_is_single_use(self):
        code = self.st.issue_code(client_id="c1", redirect_uri="https://claude.ai/cb",
                                  code_challenge="chal", resource=RESOURCE,
                                  scope="skills:read", invite_code=self.code)
        first = self.st.consume_code(code)
        self.assertEqual(first["client_id"], "c1")
        self.assertIsNone(self.st.consume_code(code))

    def test_code_expires(self):
        code = self.st.issue_code(client_id="c1", redirect_uri="https://claude.ai/cb",
                                  code_challenge="chal", resource=RESOURCE,
                                  scope="skills:read", invite_code=self.code, ttl=-1)
        self.assertIsNone(self.st.consume_code(code))

    def test_access_token_validates(self):
        access, refresh, ttl = self.st.issue_tokens(self._grant(), access_ttl=60, refresh_ttl=600)
        self.assertEqual(ttl, 60)
        self.assertIsNotNone(self.st.validate_access(access, resource=RESOURCE))

    def test_access_token_rejects_wrong_resource(self):
        access, _, _ = self.st.issue_tokens(self._grant(), access_ttl=60, refresh_ttl=600)
        self.assertIsNone(self.st.validate_access(access, resource="https://evil.example/mcp"))

    def test_access_token_expires(self):
        access, _, _ = self.st.issue_tokens(self._grant(), access_ttl=-1, refresh_ttl=600)
        self.assertIsNone(self.st.validate_access(access, resource=RESOURCE))

    def test_deleting_invite_code_kills_token(self):
        access, _, _ = self.st.issue_tokens(self._grant(), access_ttl=60, refresh_ttl=600)
        self.assertIsNotNone(self.st.validate_access(access, resource=RESOURCE))
        self.auth.delete_code(self.code)
        self.assertIsNone(self.st.validate_access(access, resource=RESOURCE))

    def test_refresh_rotates_and_old_dies(self):
        _, refresh, _ = self.st.issue_tokens(self._grant(), access_ttl=60, refresh_ttl=600)
        rotated = self.st.rotate_refresh(refresh, access_ttl=60, refresh_ttl=600)
        self.assertIsNotNone(rotated)
        new_access, new_refresh, _ = rotated
        self.assertNotEqual(refresh, new_refresh)
        self.assertIsNotNone(self.st.validate_access(new_access, resource=RESOURCE))
        self.assertIsNone(self.st.rotate_refresh(refresh, access_ttl=60, refresh_ttl=600))

    def test_revoke_grants_of_client(self):
        a1, _, _ = self.st.issue_tokens(self._grant(), access_ttl=60, refresh_ttl=600)
        n = self.st.revoke_grants_of("c1")
        self.assertGreaterEqual(n, 1)
        self.assertIsNone(self.st.validate_access(a1, resource=RESOURCE))

    def test_reloads_when_file_changes_on_disk(self):
        cid, secret = self.st.create_client("Claude", ["https://claude.ai/cb"])
        other = OAuthStore(self.dir / "oauth.json", auth_store=self.auth)
        other.delete_client(cid)
        self.assertFalse(self.st.verify_client(cid, secret))

    def test_code_replay_detection(self):
        code = self.st.issue_code(client_id="c1", redirect_uri="https://claude.ai/cb",
                                  code_challenge="chal", resource=RESOURCE,
                                  scope="skills:read", invite_code=self.code)
        self.assertFalse(self.st.code_was_seen(code))
        self.st.consume_code(code)
        self.st.mark_code_spent(code, "c1")
        self.assertTrue(self.st.code_was_seen(code))

    def test_unspent_code_is_not_seen(self):
        other = self.st.issue_code(client_id="c1", redirect_uri="https://claude.ai/cb",
                                   code_challenge="chal", resource=RESOURCE,
                                   scope="skills:read", invite_code=self.code)
        self.assertFalse(self.st.code_was_seen(other))
        self.assertFalse(self.st.code_was_seen("nonexistent"))

    def test_revoke_kills_access_and_refresh(self):
        access, refresh, _ = self.st.issue_tokens(self._grant(), access_ttl=60, refresh_ttl=600)
        self.assertTrue(self.st.revoke(access))
        self.assertIsNone(self.st.validate_access(access, resource=RESOURCE))
        self.assertTrue(self.st.revoke(refresh))
        self.assertIsNone(self.st.rotate_refresh(refresh, access_ttl=60, refresh_ttl=600))
        self.assertFalse(self.st.revoke("never-existed"))
