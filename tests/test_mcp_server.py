"""scripts/library/mcp_server.py — stdio JSON-RPC 왕복 검증 (subprocess, 외부 네트워크 0).

두 폴백 경로를 모두 실측한다:
- 닫힌 포트 (연결 실패) → 로컬 인덱스 폴백
- 라이브러리 API 미배포 서버 (Flask 식 HTML 404) → 로컬 인덱스 폴백 (실사고: 구버전
  aiskillbox 가 5050 에 떠 있으면 모든 tools/call 이 '백엔드 오류: HTTP 404' 로 죽던 버그)
"""
from __future__ import annotations

import http.server
import json
import os
import shutil
import subprocess
import sys
import threading
import unittest
from pathlib import Path

from tests.fixtures import SKILLS, make_mirror

SERVER = Path(__file__).resolve().parents[1] / "scripts" / "library" / "mcp_server.py"


class _McpHarness(unittest.TestCase):
    """서버 subprocess 기동 + JSON-RPC 왕복 헬퍼 (테스트 메서드 없음 — 상속 전용)."""

    def _start(self, base_url: str) -> None:
        self.root = make_mirror()
        env = dict(os.environ)
        env.update({
            "AISKILLBOX_URL": base_url,
            "AISKILLBOX_TIMEOUT": "2",
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

    def _init(self, protocol: str = "2025-06-18") -> dict:
        init = self._send("initialize", {
            "protocolVersion": protocol, "capabilities": {},
            "clientInfo": {"name": "test", "version": "0"},
        })
        self._send("notifications/initialized", {}, notify=True)
        return init


class McpServerTest(_McpHarness):
    def setUp(self):
        self._start("http://127.0.0.1:9")   # 닫힌 포트 → 즉시 실패 → 로컬 폴백

    def test_handshake_list_and_call(self):
        init = self._init()
        self.assertIn("result", init)
        self.assertEqual(init["result"]["protocolVersion"], "2025-06-18")
        self.assertIn("tools", init["result"]["capabilities"])
        self.assertEqual(init["result"]["serverInfo"]["name"], "skill-library")

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


class _Html404Handler(http.server.BaseHTTPRequestHandler):
    """구버전 aiskillbox 흉내 — 서버는 떠 있지만 라이브러리 라우트가 없어 HTML 404."""

    def do_GET(self):  # noqa: N802
        body = b"<!doctype html><html><body><h1>404 Not Found</h1></body></html>"
        self.send_response(404)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # noqa: D102
        pass


class McpOldServerFallbackTest(_McpHarness):
    def setUp(self):
        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Html404Handler)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self._start(f"http://127.0.0.1:{self.httpd.server_address[1]}")

    def tearDown(self):
        super().tearDown()
        self.httpd.shutdown()
        self.httpd.server_close()

    def test_html_404_falls_back_to_local(self):
        self._init()

        srch = self._send("tools/call", {"name": "search_skills", "arguments": {"query": "인스타 대본", "k": 2}})
        self.assertFalse(srch["result"].get("isError"))
        stext = srch["result"]["content"][0]["text"]
        self.assertIn("instagram-reels-script-automation", stext)
        self.assertIn("(로컬", stext)

        lst = self._send("tools/call", {"name": "list_skills", "arguments": {}})
        self.assertFalse(lst["result"].get("isError"))
        for slug in SKILLS:
            self.assertIn(slug, lst["result"]["content"][0]["text"])

        got = self._send("tools/call", {"name": "get_skill", "arguments": {"slug": "notion-mcp-setup"}})
        self.assertFalse(got["result"].get("isError"))
        self.assertIn("name: notion-mcp-setup", got["result"]["content"][0]["text"])


class LocalBackendSeamTest(unittest.TestCase):
    """use_local_backend() 이후에는 _http_get 이 절대 호출되지 않아야 한다."""

    def setUp(self):
        from scripts.library import mcp_server as ms
        self.ms = ms
        self.root = make_mirror()
        self._saved_force = getattr(ms, "_FORCE_LOCAL", False)
        self._saved_http = ms._http_get
        self._saved_root = ms.LOCAL_ROOT
        ms.LOCAL_ROOT = str(self.root)

        def landmine(*a, **kw):
            raise AssertionError("in-process 모드인데 HTTP 백엔드를 호출했다")

        ms._http_get = landmine

    def tearDown(self):
        self.ms._http_get = self._saved_http
        self.ms._FORCE_LOCAL = self._saved_force
        self.ms.LOCAL_ROOT = self._saved_root
        shutil.rmtree(self.root, ignore_errors=True)

    def test_search_uses_local_index(self):
        self.ms.use_local_backend()
        res, mode = self.ms.backend_search("릴스", 3, "")
        self.assertEqual(mode, "inproc")
        self.assertIn("results", res)

    def test_get_uses_local_index(self):
        self.ms.use_local_backend()
        raw, mode = self.ms.backend_get("instagram-reels-script-automation")
        self.assertEqual(mode, "inproc")
        self.assertIn("---", raw)

    def test_list_uses_local_index(self):
        self.ms.use_local_backend()
        items, mode = self.ms.backend_list("", "")
        self.assertEqual(mode, "inproc")
        self.assertTrue(items)

    def test_inproc_mode_has_no_fallback_warning(self):
        """'서버 미응답' 문구가 사용자에게 새면 안 된다 — 정상 경로다."""
        self.assertEqual(self.ms._mode_tag("inproc"), "")


if __name__ == "__main__":
    unittest.main()
