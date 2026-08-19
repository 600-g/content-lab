"""SKILL.md를 글로벌 ~/.claude/skills/ + 로컬 mirror에 설치.

기본 동작: 같은 슬러그가 이미 있으면 합병(merge) 위임. 덮어쓰기 X.
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

if TYPE_CHECKING:
    from ..analyzer.gemini import AnalysisResult

logger = logging.getLogger(__name__)

DEFAULT_GLOBAL_SKILLS_DIR = "~/.claude/skills"
LOCAL_MIRROR_DIR = Path(__file__).resolve().parents[2] / "skills"

# 트래킹 파라미터 (중복 감지 시 무시)
TRACKING_PARAMS = {
    "fbclid", "gclid", "msclkid", "yclid",
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id",
    "_ga", "_gl", "mc_cid", "mc_eid",
    "ref", "ref_src", "referrer",
    "pvs", "p", "n",  # notion.site 트래킹
    "fragment", "from",
}


def normalize_url(url: str) -> str:
    """URL 정규화 — 트래킹 파라미터 제거 + 끝 슬래시 통일.

    같은 PDF/페이지가 fbclid 등으로 다른 URL이 되어 중복 감지 실패하는 문제 해결.
    """
    if not url:
        return ""
    try:
        s = urlsplit(url.strip())
        # query 정리
        qs = [(k, v) for k, v in parse_qsl(s.query, keep_blank_values=False)
              if k.lower() not in TRACKING_PARAMS]
        q = urlencode(qs)
        # path 끝 슬래시 통일 (제거)
        path = re.sub(r"/+$", "", s.path) or "/"
        return urlunsplit((s.scheme.lower(), s.netloc.lower(), path, q, ""))
    except Exception:
        return url


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


def _frontmatter_sources(text: str) -> list[str]:
    """SKILL.md frontmatter 의 sources / source_url(s) 값만 추출."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return []
    fm = m.group(1) + "\n"
    urls: list[str] = []
    lm = re.search(r"^(?:sources|source_urls?):\n((?:\s+-\s+\S+\n)+)", fm, re.MULTILINE)
    if lm:
        for ln in lm.group(1).splitlines():
            u = ln.strip().lstrip("-").strip().strip('"').strip("'")
            if u.startswith("http"):
                urls.append(u)
    im = re.search(r"^(?:sources|source_urls?):\s*(https?://\S+)", fm, re.MULTILINE)
    if im:
        urls.append(im.group(1).strip().strip('"').strip("'"))
    return urls


def find_existing_by_url(source_url: str) -> Path | None:
    """이미 같은 URL이 **출처(sources)** 에 포함된 스킬 찾기 (정규화 URL 비교).

    v4.4.5: 본문 전체 URL 스캔 → frontmatter sources 한정. 본문의 참고 링크
    (예: 다른 스킬 예시 속 github/nodejs 링크)에 걸려 무관한 스킬로 합병되던
    false positive 차단.
    """
    if not LOCAL_MIRROR_DIR.exists():
        return None
    target = normalize_url(source_url)
    for skill_md in LOCAL_MIRROR_DIR.glob("*/SKILL.md"):
        try:
            for u in _frontmatter_sources(skill_md.read_text(encoding="utf-8")):
                if normalize_url(u) == target:
                    return skill_md
        except Exception:  # noqa: BLE001
            continue
    return None
