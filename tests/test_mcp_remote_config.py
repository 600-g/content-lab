"""scripts.mcp_remote.config — 설정 로드 + 절대 URL 빌더 (네트워크 0)."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.mcp_remote import config as cfg


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="mcp_cfg_"))
        self.path = self.dir / "config.json"

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _write(self, block):
        self.path.write_text(json.dumps({"mcp_remote": block}), encoding="utf-8")

    def test_defaults_when_block_missing(self):
        self.path.write_text(json.dumps({}), encoding="utf-8")
        c = cfg.load(self.path)
        self.assertFalse(c["dynamic_registration"])
        self.assertEqual(c["access_ttl_seconds"], 3600)

    def test_trailing_slash_stripped(self):
        self._write({"public_base_url": "https://x.example/"})
        self.assertEqual(cfg.load(self.path)["public_base_url"], "https://x.example")

    def test_abs_url_and_resource_id(self):
        self._write({"public_base_url": "https://x.example"})
        c = cfg.load(self.path)
        self.assertEqual(cfg.abs_url("/oauth/token", c), "https://x.example/oauth/token")
        self.assertEqual(cfg.resource_id(c), "https://x.example/mcp")

    def test_http_base_url_is_rejected(self):
        """CF Tunnel 함정 — http 가 새면 Claude 가 연결을 거부한다."""
        self._write({"public_base_url": "http://x.example"})
        with self.assertRaises(ValueError):
            cfg.load(self.path)

    def test_reloads_when_file_changes(self):
        self._write({"dynamic_registration": False})
        self.assertFalse(cfg.load(self.path)["dynamic_registration"])
        self._write({"dynamic_registration": True})
        import os, time
        os.utime(self.path, (time.time() + 2, time.time() + 2))
        self.assertTrue(cfg.load(self.path)["dynamic_registration"])
