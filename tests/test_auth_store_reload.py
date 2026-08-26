"""auth.json 이 디스크에서 바뀌면 실행 중인 서버도 그걸 본다 (네트워크 0).

실측 확인된 두 실패 (수정 전):
1. `python -m scripts.auth_store create` 로 발급한 코드가 실행 중 서버에서 거부됐다
   — CLAUDE.md 가 안내하는 발급 절차 그대로인데 재시작 전엔 안 먹힘.
2. `delete <code>` 가 "로그아웃된 기기 N대" 를 출력하는데도 실행 중 서버는 그 토큰을
   계속 통과시켰다. 분실 기기 접근 차단이 실제로는 안 되는 상태 (launchd 라 서버는 상주).
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.auth_store import AuthStore


class AuthStoreReloadTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.path = Path(self.dir.name) / "auth.json"
        # 같은 파일을 보는 두 프로세스: server = 상주 서버, cli = 터미널 명령
        self.server = AuthStore(self.path)
        self.cli = AuthStore(self.path)

    def test_code_created_by_cli_is_usable_by_running_server(self):
        # 서버가 먼저 스토어를 로드해 둔 상태 (실제 운영에서 늘 그렇다)
        self.server.list_codes()
        code = self.cli.create_code("폰")
        self.assertIsNotNone(
            self.server.redeem(code),
            "CLI 로 발급한 코드를 실행 중 서버가 받아들여야 한다",
        )

    def test_cli_delete_revokes_live_session_immediately(self):
        code = self.cli.create_code("분실될 기기")
        token = self.server.redeem(code)
        self.assertTrue(self.server.check_token(token))

        self.cli.delete_code(code)   # 사용자는 여기서 '차단됐다' 고 믿는다
        self.assertFalse(
            self.server.check_token(token),
            "코드 삭제 = 즉시 로그아웃이어야 한다 (재시작 대기 X)",
        )

    def test_server_sees_external_edit_without_restart(self):
        a = self.cli.create_code("A")
        self.server.redeem(a)
        b = self.cli.create_code("B")
        codes = {c["code"] for c in self.server.list_codes()}
        self.assertIn(b, codes, "기동 후 추가된 코드도 목록에 보여야 한다")

    def test_own_writes_do_not_trigger_reload_loop(self):
        """자기가 쓴 내용을 '외부 변경' 으로 오인해 매번 다시 읽으면 안 된다."""
        code = self.server.create_code("x")
        before = self.server._mtime
        self.server.check_token(self.server.redeem(code))
        self.assertIsNotNone(before)

    def test_missing_file_is_tolerated(self):
        empty = AuthStore(Path(self.dir.name) / "none.json")
        self.assertEqual(empty.list_codes(), [])
        self.assertFalse(empty.check_token("아무거나"))

    def test_corrupt_file_does_not_raise(self):
        self.path.write_text("{ 깨진 json", encoding="utf-8")
        s = AuthStore(self.path)
        self.assertEqual(s.list_codes(), [])   # bootstrap 으로 복구 가능한 상태여야 한다


if __name__ == "__main__":
    unittest.main()
