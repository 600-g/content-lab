"""AnalysisResult → SKILL.md (v2.4 — 폼 자유화, 속성 가지치기).

v2.4 변경 (2026-05-25):
- 메타 quote 박스 폐기 (30초 핵심·메타·도구·적용대상 stripe 다 제거)
- frontmatter 6키만: name / description / origin / grade / difficulty / category / ai_tools / sources
- 본문: # 제목 + 💡 1줄 + body_md(자유 형식) + ## 출처. 7섹션 강제 없음.
- 태그·적용대상·날짜·합병 메타 줄·이모지 아이콘 prefix 폐기.
"""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..analyzer.gemini import AnalysisResult


def _normalize(content) -> str:
    if content is None:
        return ""
    if isinstance(content, list):
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
        return "\n".join(f"- **{k}**: {v}" for k, v in content.items())
    return str(content)


def _compose_legacy_body(r: "AnalysisResult") -> str:
    """v2.2 데이터(8섹션)로 들어왔을 때 body_md 합성 — 빈 섹션 생략."""
    out: list[str] = []

    def section(label, content):
        s = _normalize(content).strip()
        if s and s not in ("(해당 없음)", "(없음)", "-", "—"):
            out.append(f"## {label}\n\n{s}")

    section("어떻게 작동", r.how_it_works)
    section("따라 하기", r.steps)
    section("실제 예시", r.examples)
    section("두근컴퍼니 적용", r.doogeun or r.memo)
    section("주의할 점", r.caveats)
    return "\n\n".join(out)


def render_skill_md(result: "AnalysisResult", source_url: str, source_type: str) -> str:
    """SKILL.md — v2.4 lean. 제목 + 💡 1줄 + body + 출처."""
    today = datetime.date.today().isoformat()  # noqa: F841 — 호환용 (현재 본문엔 미사용)
    is_merged = bool(result.raw.get("_is_merged"))
    source_urls: list[str] = result.raw.get("_merged_source_urls") or [source_url]

    # body — v2.4 우선, legacy fallback
    body_md = (getattr(result, "body_md", "") or "").strip()
    if not body_md:
        body_md = _compose_legacy_body(result)

    # description (frontmatter, AI 활성화 트리거) — callout/tldr 한 줄
    _callout = (getattr(result, "callout", "") or "").strip()
    description = (_callout or result.tldr or result.summary or "").replace("\n", " ").strip()
    if len(description) > 280:
        description = description[:277] + "..."

    tools_yaml = ", ".join(f'"{t}"' for t in (result.ai_tools or []))
    sources_yaml = "\n".join(f"  - {u}" for u in source_urls)

    frontmatter = f"""---
name: {result.skill_name}
description: {description}
origin: content-lab
grade: {result.grade}
difficulty: {result.difficulty or "중급"}
category: {result.category}
ai_tools: [{tools_yaml}]
sources:
{sources_yaml}
---
"""

    merged_badge = " (합병됨)" if is_merged else ""
    sources_md = "\n".join(f"- [{u}]({u})" for u in source_urls)
    # v2.6: callout 은 💡 prefix 로 출력 → register 가 Notion callout 블록으로 변환
    callout_line = (getattr(result, "callout", "") or result.tldr or "").strip()
    callout_md = f"\n\n💡 {callout_line}\n" if callout_line else "\n"

    body = f"""
# {result.skill_title_ko}{merged_badge}{callout_md}
{body_md.strip()}

## 출처

{sources_md}
"""
    return frontmatter + body
