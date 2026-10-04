"""검색 결과의 사람용 게시글 링크는 공개 주소여야 한다 (localhost 면 폰·claude.ai 에서 죽은 링크)."""
from __future__ import annotations

import unittest
from unittest import mock

from scripts.library import mcp_server


class LinkBaseTest(unittest.TestCase):
    def test_env_override_wins(self):
        with mock.patch.dict("os.environ", {"AISKILLBOX_PUBLIC_URL": "https://x.example/"}):
            self.assertEqual(mcp_server._public_link_base(), "https://x.example")

    def test_defaults_to_https_public_base_from_config(self):
        with mock.patch.dict("os.environ", {"AISKILLBOX_PUBLIC_URL": ""}):
            self.assertTrue(mcp_server._public_link_base().startswith("https://"))


if __name__ == "__main__":
    unittest.main()
