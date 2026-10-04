"""글로벌(~/.claude/skills) 설치 정책 — 터미널에서 바로 쓸 S급 개발·자동화 스킬만 전역에 둔다.

2026-09-27: 수집한 스킬을 전부 전역에 깔아 스킬 설명만 ~34KB 가 매 Claude Code 세션(과 모든 `claude -p`)에
실렸다. 라이브러리 원본(mirror)과 검색·MCP 는 그대로이므로 나머지는 커넥터로 꺼내 쓴다.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from scripts.skill_builder import installer


def _result(grade: str, category: str, slug: str = "demo"):
    return SimpleNamespace(skill_name=slug, grade=grade, category=category)


class PolicyTest(unittest.TestCase):
    def test_s_grade_dev_and_automation_go_global(self):
        self.assertTrue(installer.should_install_globally("S", "개발"))
        self.assertTrue(installer.should_install_globally("S", "자동화"))

    def test_other_grades_or_categories_stay_library_only(self):
        self.assertFalse(installer.should_install_globally("A", "개발"))
        self.assertFalse(installer.should_install_globally("S", "디자인"))
        self.assertFalse(installer.should_install_globally("C", "기타"))

    def test_config_override(self):
        with mock.patch.object(installer.config_store, "get",
                               return_value={"grades": ["S", "A"], "categories": ["디자인"]}):
            self.assertTrue(installer.should_install_globally("A", "디자인"))
            self.assertFalse(installer.should_install_globally("S", "개발"))


class InstallSkillTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        patcher = mock.patch.dict("os.environ", {"SKILL_INSTALL_DIR": self.tmp.name})
        patcher.start(); self.addCleanup(patcher.stop); self.addCleanup(self.tmp.cleanup)

    def test_skips_global_when_policy_says_no(self):
        path, is_new = installer.install_skill(_result("B", "업무"), "---\nname: demo\n---\n")
        self.assertIsNone(path)
        self.assertFalse(is_new)
        self.assertFalse((Path(self.tmp.name) / "demo").exists())

    def test_installs_when_policy_says_yes(self):
        path, is_new = installer.install_skill(_result("S", "개발"), "---\nname: demo\n---\n")
        self.assertTrue(path.exists())
        self.assertTrue(is_new)

    def test_existing_global_copy_is_kept_updated(self):
        # 이미 전역에 있는 스킬(사용자가 직접 둔 것 포함)은 합병 갱신을 계속 받는다
        d = Path(self.tmp.name) / "demo"; d.mkdir()
        (d / "SKILL.md").write_text("old", encoding="utf-8")
        path, is_new = installer.install_skill(_result("B", "업무"), "new")
        self.assertEqual(path.read_text(encoding="utf-8"), "new")
        self.assertFalse(is_new)


if __name__ == "__main__":
    unittest.main()
