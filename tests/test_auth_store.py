"""scripts.auth_store — 초대코드/기기토큰 저장소 단위 테스트 (디스크는 임시 파일)."""
from __future__ import annotations

import json
import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path

from scripts import auth_store


class AuthStoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="auth_store_"))
        self.path = self.dir / "auth.json"
        self.store = auth_store.AuthStore(self.path)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_create_list_code(self):
        code = self.store.create_code("폰")
        self.assertTrue(code.startswith("DGN-"))
        self.assertEqual(len(code), len("DGN-XXXX-XXXX"))
        # 혼동 문자 제외
        for ch in "IO01":
            self.assertNotIn(ch, code.replace("DGN-", ""))
        rows = self.store.list_codes()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["code"], code)
        self.assertEqual(rows[0]["label"], "폰")
        self.assertEqual(rows[0]["sessions"], 0)

    def test_redeem_and_check(self):
        code = self.store.create_code("test")
        token = self.store.redeem(code, device="iPhone Safari")
        self.assertIsNotNone(token)
        self.assertTrue(self.store.check_token(token))
        self.assertFalse(self.store.check_token("wrong-token"))
        self.assertFalse(self.store.check_token(""))
        self.assertFalse(self.store.check_token(None))
        self.assertEqual(self.store.list_codes()[0]["sessions"], 1)

    def test_redeem_invalid_code(self):
        self.assertIsNone(self.store.redeem("DGN-FAKE-CODE", device="x"))
        self.assertIsNone(self.store.redeem("", device="x"))

    def test_delete_code_cascades_sessions(self):
        code = self.store.create_code("공유")
        t1 = self.store.redeem(code, device="d1")
        t2 = self.store.redeem(code, device="d2")
        other = self.store.create_code("본인")
        t3 = self.store.redeem(other, device="d3")
        removed = self.store.delete_code(code)
        self.assertEqual(removed, 2)
        self.assertFalse(self.store.check_token(t1))
        self.assertFalse(self.store.check_token(t2))
        self.assertTrue(self.store.check_token(t3))       # 다른 코드 세션은 유지
        self.assertEqual(len(self.store.list_codes()), 1)
        self.assertEqual(self.store.delete_code("DGN-NOPE-NOPE"), 0)

    def test_tokens_stored_hashed_only(self):
        code = self.store.create_code("x")
        token = self.store.redeem(code, device="d")
        raw = self.path.read_text(encoding="utf-8")
        self.assertNotIn(token, raw)          # 토큰 원문은 디스크에 없음
        self.assertIn(code, raw)              # 코드는 평문 (설정창 재조회용)

    def test_file_permissions_0600(self):
        self.store.create_code("x")
        mode = stat.S_IMODE(os.stat(self.path).st_mode)
        self.assertEqual(mode, 0o600)

    def test_corrupt_file_recovers_empty(self):
        self.path.write_text("{broken json", encoding="utf-8")
        s2 = auth_store.AuthStore(self.path)
        self.assertEqual(s2.list_codes(), [])
        code = s2.create_code("복구")          # 쓰기도 정상
        self.assertTrue(s2.redeem(code, device="d"))

    def test_persistence_across_instances(self):
        code = self.store.create_code("영속")
        token = self.store.redeem(code, device="d")
        s2 = auth_store.AuthStore(self.path)
        self.assertTrue(s2.check_token(token))
        self.assertEqual(s2.list_codes()[0]["code"], code)


if __name__ == "__main__":
    unittest.main()
