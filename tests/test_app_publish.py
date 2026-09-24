"""scripts/app_publish.py — claude.ai 에서 타이머 앱을 고쳐 배포하는 경로.

네트워크 없이 돈다 — gh 호출(_gh)을 전부 가로챈다.
실행: venv/bin/python -m unittest tests.test_app_publish -v
"""
from __future__ import annotations

import base64
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import app_publish as ap  # noqa: E402

SRC = (
    "using System;\n"
    "class MainForm {\n"
    '    private const string VERSION = "v1.0 (build 72)";   // 진단 표기용\n'
    "    void A() { int x = 1; }\n"
    "    void B() { int x = 1; }\n"
    "}\n"
)
SHA = "abc123"


def fake_gh(existing_tags=(), captured=None):
    """_gh 대역. contents GET/PUT 과 태그 조회만 흉내 낸다."""
    def _fake(args, stdin=None):
        joined = " ".join(args)
        if args[:2] == ["api", f"repos/{ap.REPO}/contents/{ap.SRC_PATH}"] and "-X" not in args:
            return json.dumps({"content": base64.b64encode(SRC.encode()).decode(), "sha": SHA})
        if "git/ref/tags/" in joined:
            tag = joined.split("git/ref/tags/")[1].split()[0]
            if tag in existing_tags:
                return "{}"
            raise ap.PublishError("Not Found")
        if "-X" in args and "PUT" in args:
            if captured is not None:
                captured.append(json.loads(stdin))
            return "{}"
        raise AssertionError("예상 못 한 gh 호출: " + joined)
    return _fake


class PureTest(unittest.TestCase):
    def test_current_build(self):
        self.assertEqual(ap.current_build(SRC), 72)

    def test_current_build_missing(self):
        with self.assertRaises(ap.PublishError):
            ap.current_build("class X {}")

    def test_bump_version_only_once(self):
        out = ap.bump_version(SRC, 99)
        self.assertIn('VERSION = "v1.0 (build 99)"', out)
        self.assertNotIn("build 72", out)
        self.assertIn("// 진단 표기용", out)   # 주석 보존

    def test_hardcoded_target(self):
        """호출자가 저장소·경로를 못 바꾼다는 것이 이 기능의 안전 근거다."""
        self.assertEqual(ap.REPO, "600-g/shutdown-timer")
        self.assertEqual(ap.SRC_PATH, "src/PhoneShell.cs")
        self.assertEqual(ap.BRANCH, "main")


class PublishTest(unittest.TestCase):
    def test_publish_commits_bumped_source(self):
        cap = []
        with mock.patch.object(ap, "_gh", fake_gh(captured=cap)):
            msg = ap.publish("void A() { int x = 1; }", "void A() { int x = 2; }", "테스트 수정")
        self.assertEqual(len(cap), 1)
        body = cap[0]
        self.assertEqual(body["sha"], SHA)
        self.assertEqual(body["branch"], "main")
        self.assertTrue(body["message"].startswith("v1.0.73: 테스트 수정"))
        sent = base64.b64decode(body["content"]).decode()
        self.assertIn("int x = 2;", sent)
        self.assertIn('build 73', sent)
        self.assertIn("v1.0.73", msg)

    def test_publish_skips_taken_tags(self):
        cap = []
        with mock.patch.object(ap, "_gh", fake_gh(existing_tags=("v1.0.73", "v1.0.74"), captured=cap)):
            ap.publish("void B() { int x = 1; }", "void B() { int x = 3; }")
        self.assertIn("build 75", base64.b64decode(cap[0]["content"]).decode())

    def test_publish_rejects_ambiguous_old_str(self):
        with mock.patch.object(ap, "_gh", fake_gh()):
            with self.assertRaises(ap.PublishError) as cm:
                ap.publish("int x = 1;", "int x = 2;")
        self.assertIn("2곳", str(cm.exception))

    def test_publish_rejects_missing_old_str(self):
        with mock.patch.object(ap, "_gh", fake_gh()):
            with self.assertRaises(ap.PublishError):
                ap.publish("존재하지 않는 코드", "뭐든")

    def test_publish_rejects_identical(self):
        with self.assertRaises(ap.PublishError):
            ap.publish("같음", "같음")

    def test_publish_refuses_to_delete_version_line(self):
        """VERSION 줄을 지우면 빌드 파이프라인이 통째로 깨진다 — 커밋 전에 막는다."""
        with mock.patch.object(ap, "_gh", fake_gh()) as g:
            with self.assertRaises(ap.PublishError) as cm:
                ap.publish('    private const string VERSION = "v1.0 (build 72)";   // 진단 표기용\n', "")
        self.assertIn("VERSION", str(cm.exception))

    def test_publish_rejects_oversized(self):
        with self.assertRaises(ap.PublishError):
            ap.publish("a", "x" * (ap.MAX_NEW_STR + 1))


class SearchTest(unittest.TestCase):
    def test_search_shows_line_numbers(self):
        with mock.patch.object(ap, "_gh", fake_gh()):
            out = ap.search(r"VERSION", context=0)
        self.assertIn("→", out)
        self.assertIn("build 72", out)
        self.assertIn("3", out)

    def test_search_no_hit(self):
        with mock.patch.object(ap, "_gh", fake_gh()):
            self.assertIn("걸리는 줄이 없습니다", ap.search(r"zzzz"))

    def test_search_bad_regex(self):
        with self.assertRaises(ap.PublishError):
            ap.search("[unclosed")


class AuthErrorTest(unittest.TestCase):
    def test_auth_failure_message_is_actionable(self):
        def boom(args, stdin=None):
            raise ap.PublishError("GitHub 인증이 끊겼습니다. 맥 터미널에서 `gh auth login` 후 다시 시도하세요.")
        with mock.patch.object(ap, "_gh", boom):
            with self.assertRaises(ap.PublishError) as cm:
                ap.read_source()
        self.assertIn("gh auth login", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
