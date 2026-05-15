"""SKILL.md를 글로벌 ~/.claude/skills/ + 로컬 mirror에 설치.

기본 동작: 같은 슬러그가 이미 있으면 합병(merge) 위임. 덮어쓰기 X.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..analyzer.gemini import AnalysisResult

logger = logging.getLogger(__name__)

DEFAULT_GLOBAL_SKILLS_DIR = "~/.claude/skills"
LOCAL_MIRROR_DIR = Path(__file__).resolve().parents[2] / "skills"


def _global_skills_dir() -> Path:
    raw = os.getenv("SKILL_INSTALL_DIR", DEFAULT_GLOBAL_SKILLS_DIR)
    return Path(os.path.expanduser(raw))


def find_global_by_slug(slug: str) -> Path | None:
    """글로벌 디렉토리에서 같은 슬러그 스킬 찾기."""
    p = _global_skills_dir() / slug / "SKILL.md"
    return p if p.exists() else None


def find_mirror_by_slug(slug: str) -> Path | None:
    p = LOCAL_MIRROR_DIR / slug / "SKILL.md"
    return p if p.exists() else None


def install_skill(
    result: "AnalysisResult",
    skill_md_content: str,
) -> tuple[Path, bool]:
    """글로벌 ~/.claude/skills/{name}/SKILL.md에 설치 (있으면 갱신).

    Returns: (path, was_new). 같은 슬러그면 갱신.
    """
    skills_dir = _global_skills_dir()
    skills_dir.mkdir(parents=True, exist_ok=True)
    target_dir = skills_dir / result.skill_name
    target_path = target_dir / "SKILL.md"

    is_new = not target_path.exists()
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path.write_text(skill_md_content, encoding="utf-8")
    logger.info("스킬 %s: %s", "신규 설치" if is_new else "갱신(합병)", target_path)
    return target_path, is_new


def mirror_skill(
    result: "AnalysisResult",
    skill_md_content: str,
) -> Path:
    """content-lab/skills/{name}/SKILL.md mirror (git 추적)."""
    LOCAL_MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    mirror_dir = LOCAL_MIRROR_DIR / result.skill_name
    mirror_dir.mkdir(parents=True, exist_ok=True)
    mirror_path = mirror_dir / "SKILL.md"
    mirror_path.write_text(skill_md_content, encoding="utf-8")
    return mirror_path


def find_existing_by_url(source_url: str) -> Path | None:
    """이미 같은 URL이 source_urls에 포함된 스킬 찾기."""
    if not LOCAL_MIRROR_DIR.exists():
        return None
    for skill_md in LOCAL_MIRROR_DIR.glob("*/SKILL.md"):
        try:
            txt = skill_md.read_text(encoding="utf-8")
            if source_url in txt:
                return skill_md
        except Exception:  # noqa: BLE001
            continue
    return None
