"""router._notion_auth_guard — app.notion.com/p/ 공개 공유 링크 오탐 수정 검증 (네트워크 0).

실사고 (2026-08-19): 노션 '링크 복사'가 발급하는 app.notion.com/p/<id> 공개 공유 링크가
도메인만 보고 '워크스페이스 멤버 전용' 으로 사전 차단됐다 (비로그인 렌더 실측: 본문 정상).
"""
from __future__ import annotations

import unittest

from scripts.scraper.router import _notion_auth_guard


class NotionGuardTest(unittest.TestCase):
    def test_public_share_copy_link_passes(self):
        # '링크 복사' 가 만드는 공개 공유 링크 — 차단하면 안 됨
        for url in (
            "https://app.notion.com/p/design-3c0fd99f0e5f8102ad3ed2294e75c755?source=copy_link",
            "https://app.notion.com/p/3c004aeefb608081ac9bd7814df90e34?source=copy_link",
            "https://app.notion.com/p/3c004aeefb608081ac9bd7814df90e34",
            "https://www.notion.com/p/some-public-page-abc123",
        ):
            self.assertIsNone(_notion_auth_guard(url), url)

    def test_workspace_paths_still_blocked(self):
        for url in (
            "https://app.notion.com/doogeun/some-page-35f143621b4b814b",
            "https://app.notion.com/35f143621b4b814b8947cca66ca16dcb",
            "https://www.notion.com/workspace/roadmap",
        ):
            blocked = _notion_auth_guard(url)
            self.assertIsNotNone(blocked, url)
            self.assertEqual(blocked.skip_reason, "notion_workspace_only")
            self.assertIn("Publish to web", blocked.skip_message_ko)

    def test_other_notion_domains_untouched(self):
        for url in (
            "https://doogeun.notion.site/skill-doc-123",
            "https://www.notion.so/doogeun/page-abc",
        ):
            self.assertIsNone(_notion_auth_guard(url), url)


if __name__ == "__main__":
    unittest.main()
