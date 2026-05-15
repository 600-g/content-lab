"""AnalysisResult → ECC 표준 SKILL.md (TEMPLATE.md v1 기준).

본문 8섹션 고정 + 메타 callout + 누적 출처 (합병 시).
"""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..analyzer.gemini import AnalysisResult


# 카테고리별 페이지 아이콘
CATEGORY_ICON = {
    "프롬프트": "💬",
    "에이전트/자동화": "🤖",
    "영상/콘텐츠": "🎬",
    "디자인/이미지": "🎨",
    "코딩/개발": "💻",
    "업무효율": "⚡",
    "마케팅/SNS": "📱",
    "기타": "📦",
}


def render_skill_md(result: "AnalysisResult", source_url: str, source_type: str) -> str:
    """ECC 표준 SKILL.md: 프론트매터 + TEMPLATE.md v1 본문."""
    today = datetime.date.today().isoformat()
    is_merged = bool(result.raw.get("_is_merged"))
    source_urls: list[str] = result.raw.get("_merged_source_urls") or [source_url]
    collected_at = result.raw.get("_merged_collected_at") or today
    icon = CATEGORY_ICON.get(result.category, "📦")

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
  template_version: "v1"
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

    sources_block = "\n".join(f"- [{u}]({u})" for u in source_urls)
    merged_badge = " · 🔀 합병" if is_merged else ""

    body = f"""
# {icon} {result.skill_title_ko}{merged_badge}

> **TL;DR** — {result.tldr or result.summary}

> **메타** 등급 {result.grade} · 카테고리 {result.category} · 난이도 {result.difficulty}
> **도구** {', '.join(result.ai_tools) or '도구무관'}
> **적용 대상** {', '.join(result.targets) or '공통'}

---

## 🎯 When to use (언제 쓰는가)

{result.when_to_use or '(해당 없음)'}

## 🔑 How it works (작동 원리)

{result.how_it_works or '(해당 없음)'}

## 🛠 Steps (적용 단계)

{result.steps or '(해당 없음)'}

## 💡 Examples (예시)

{result.examples or '(해당 없음)'}

## 🏢 두근 환경 적용

{result.doogeun or result.memo or '(해당 없음)'}

## ⚠️ Caveats (주의사항)

{result.caveats or '(해당 없음)'}

## 📎 Sources (출처)

{sources_block}

---

## 메타 정보

- 최초 수집: {collected_at}
- 마지막 갱신: {today}
- 합병 횟수: {len(source_urls)}회
- 템플릿: v1 (TEMPLATE.md)
- 자동 생성: 두근컴퍼니 콘텐츠랩 v4.0
"""
    return frontmatter + body
