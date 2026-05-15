"""AnalysisResult → ECC 표준 SKILL.md (TEMPLATE v2.2 — 사람 가독성 우선).

v2.2 변경점:
- 영문 헤더 키 제거 (한국어만)
- 빈 섹션 자동 생략 ("(해당 없음)" 표시 X)
- 메타 callout 한 묶음으로 압축
- TL;DR 강조
"""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..analyzer.gemini import AnalysisResult


CATEGORY_ICON = {
    "프롬프트": "💬",
    "자동화": "🤖",
    "콘텐츠": "🎬",
    "디자인": "🎨",
    "개발": "💻",
    "업무": "⚡",
    "기타": "📦",
}


def _normalize(content) -> str:
    """list/dict/None → string 정규화 (Gemini가 list로 줘도 안전)."""
    if content is None:
        return ""
    if isinstance(content, list):
        # 항목 끝의 점/줄바꿈 정리, "-" 없으면 자동 추가
        parts = []
        for x in content:
            s = str(x).strip()
            if not s:
                continue
            if not s.startswith(("- ", "* ", "1.", "2.", "3.", "4.", "5.")):
                s = f"- {s}"
            parts.append(s)
        return "\n".join(parts)
    if isinstance(content, dict):
        # dict면 key: value 형식
        return "\n".join(f"- **{k}**: {v}" for k, v in content.items())
    return str(content)


def _has_content(s) -> bool:
    """빈 섹션 판정: None/공백/placeholder 모두 빈 것으로."""
    t = _normalize(s).strip()
    if not t:
        return False
    if t in ("(해당 없음)", "(없음)", "(없음.)", "(N/A)", "(해당없음)", "-", "—"):
        return False
    return True


def _section(emoji: str, label: str, content) -> str:
    """섹션 내용 있으면 헤더+본문 반환, 없으면 빈 문자열."""
    if not _has_content(content):
        return ""
    return f"\n## {emoji} {label}\n\n{_normalize(content).strip()}\n"


def render_skill_md(result: "AnalysisResult", source_url: str, source_type: str) -> str:
    """SKILL.md: 프론트매터 + TEMPLATE v2.2 본문 (사람 가독성 우선)."""
    today = datetime.date.today().isoformat()
    is_merged = bool(result.raw.get("_is_merged"))
    source_urls: list[str] = result.raw.get("_merged_source_urls") or [source_url]
    collected_at = result.raw.get("_merged_collected_at") or today
    icon = CATEGORY_ICON.get(result.category, "📦")

    # 프론트매터용 description (AI 활성화 트리거)
    description = (
        f"{result.tldr or result.summary} "
        f"Use when: {result.when_to_use}"
    ).replace("\n", " ").strip()
    if len(description) > 350:
        description = description[:347] + "..."

    targets_yaml = ", ".join(f'"{t}"' for t in result.targets)
    tools_yaml = ", ".join(f'"{t}"' for t in result.ai_tools) if result.ai_tools else ""
    tags_yaml = ", ".join(f'"{t}"' for t in result.tags) if result.tags else ""
    urls_yaml = "\n".join(f'    - "{u}"' for u in source_urls)

    frontmatter = f"""---
name: {result.skill_name}
description: {description}
origin: content-lab
metadata:
  template_version: "v2.2"
  category: "{result.category}"
  grade: "{result.grade}"
  difficulty: "{result.difficulty}"
  targets: [{targets_yaml}]
  ai_tools: [{tools_yaml}]
  tags: [{tags_yaml}]
  source_urls:
{urls_yaml}
  source_type: "{source_type}"
  collected_at: "{collected_at}"
  last_updated_at: "{today}"
  merge_count: {len(source_urls)}
---
"""

    # 메타 — 한 묶음 인용 (3줄 통합)
    tools_str = " · ".join(result.ai_tools) if result.ai_tools else "도구무관"
    targets_str = " · ".join(result.targets) if result.targets else "공통"
    merged_badge = " · 🔀 합병됨" if is_merged else ""

    # 본문 — 빈 섹션 자동 생략
    sections = []
    sections.append(_section("🎯", "언제 쓰나", result.when_to_use))
    sections.append(_section("🔑", "원리", result.how_it_works))
    sections.append(_section("🛠", "단계", result.steps))
    sections.append(_section("💡", "예시", result.examples))
    sections.append(_section("🏢", "두근컴퍼니 적용", result.doogeun or result.memo))
    sections.append(_section("⚠️", "주의", result.caveats))

    # 출처 — 항상 포함 (검증 가능성)
    sources_block = "\n".join(f"- [{u}]({u})" for u in source_urls)
    sections.append(f"\n## 📎 출처\n\n{sources_block}\n")

    body_sections = "".join(sections)

    body = f"""
# {icon} {result.skill_title_ko}{merged_badge}

> **💡 {result.tldr or result.summary}**
>
> **{result.grade}** · {result.category} · {result.difficulty}
> 🤖 {tools_str} → 🎯 {targets_str}
{body_sections}

---

<details>
<summary>📋 메타 정보</summary>

- 최초 수집: `{collected_at}` · 마지막 갱신: `{today}` · 합병: {len(source_urls)}회
- 템플릿: v2.2 · slug: `{result.skill_name}`
- 자동 생성: 두근컴퍼니 콘텐츠랩

</details>
"""
    return frontmatter + body
