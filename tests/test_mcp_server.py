"""scripts/library/mcp_server.py — stdio JSON-RPC 왕복 검증 (subprocess, 네트워크 0).

HTTP 백엔드를 닫힌 포트로 강제 실패시켜 로컬 인덱스 폴백 경로를 탄다.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from tests.fixtures import SKILLS, make_mirror

SERVER = Path(__file__).resolve().parents[1] / "scripts" / "library" / "mcp_server.py"


class McpServerTest(unittest.TestCase):
    def setUp(self):
        self.root = make_mirror()
        env = dict(os.environ)
        env.update({
            "AISKILLBOX_URL": "http://127.0.0.1:9",   # 닫힌 포트 → 즉시 실패 → 로컬 폴백
            "AISKILLBOX_TIMEOUT": "1",
            "SKILL_LIBRARY_ROOT": str(self.root),
            "GEMINI_API_KEY": "",                        # 의미 검색 비활성 (네트워크 0)
        })
        self.proc = subprocess.Popen(
            [sys.executable, str(SERVER)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env, text=True, encoding="utf-8", bufsize=1,
        )
        self._id = 0

    def tearDown(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()
        for stream in (self.proc.stdout, self.proc.stderr):
            try:
                stream.close()
            except Exception:
                pass
        shutil.rmtree(self.root, ignore_errors=True)

    def _send(self, method: str, params: dict | None = None, *, notify: bool = False) -> dict | None:
        msg: dict = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            self._id += 1
            msg["id"] = self._id
        self.proc.stdin.write(json.dumps(msg, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()
        if notify:
            return None
        line = self.proc.stdout.readline()
        if not line:
            # 주의: stderr.read() 는 서버가 살아있으면 EOF 까지 블로킹 — 실패했을 때만 읽는다
            self.proc.kill()
            self.fail(f"응답 없음 (stderr: {self.proc.stderr.read()[:500]})")
        resp = json.loads(line)
        self.assertEqual(resp.get("id"), self._id)
        return resp

    def test_handshake_list_and_call(self):
        init = self._send("initialize", {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": "test", "version": "0"},
        })
        self.assertIn("result", init)
        self.assertEqual(init["result"]["protocolVersion"], "2025-06-18")
        self.assertIn("tools", init["result"]["capabilities"])
        self.assertEqual(init["result"]["serverInfo"]["name"], "skill-library")
        self._send("notifications/initialized", {}, notify=True)

        ping = self._send("ping")
        self.assertEqual(ping["result"], {})

        tools = self._send("tools/list")
        names = {t["name"] for t in tools["result"]["tools"]}
        self.assertEqual(names, {"search_skills", "get_skill", "list_skills"})
        for t in tools["result"]["tools"]:
            self.assertIn("inputSchema", t)
            self.assertEqual(t["inputSchema"]["type"], "object")

        lst = self._send("tools/call", {"name": "list_skills", "arguments": {}})
        self.assertFalse(lst["result"].get("isError"))
        text = lst["result"]["content"][0]["text"]
        for slug in SKILLS:
            self.assertIn(slug, text)

        srch = self._send("tools/call", {"name": "search_skills", "arguments": {"query": "인스타 대본", "k": 2}})
        self.assertFalse(srch["result"].get("isError"))
        stext = srch["result"]["content"][0]["text"]
        self.assertIn("instagram-reels-script-automation", stext)
        self.assertIn("(로컬", stext)   # 폴백 모드 표기

        got = self._send("tools/call", {"name": "get_skill", "arguments": {"slug": "notion-mcp-setup"}})
        self.assertFalse(got["result"].get("isError"))
        self.assertIn("name: notion-mcp-setup", got["result"]["content"][0]["text"])

    def test_errors(self):
        self._send("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}})
        unknown = self._send("no/such")
        self.assertEqual(unknown["error"]["code"], -32601)

        bad_tool = self._send("tools/call", {"name": "rm_rf", "arguments": {}})
        self.assertTrue(bad_tool["result"]["isError"])

        missing = self._send("tools/call", {"name": "get_skill", "arguments": {"slug": "does-not-exist"}})
        self.assertTrue(missing["result"]["isError"])

        short = self._send("tools/call", {"name": "search_skills", "arguments": {"query": "a"}})
        self.assertTrue(short["result"]["isError"])

        # 깨진 JSON 한 줄 → -32700, 서버는 계속 살아있어야 함
        self.proc.stdin.write("{not json\n")
        self.proc.stdin.flush()
        line = json.loads(self.proc.stdout.readline())
        self.assertEqual(line["error"]["code"], -32700)
        self.assertEqual(self._send("ping")["result"], {})


if __name__ == "__main__":
    unittest.main()
