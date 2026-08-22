"""테스트 공용 픽스처 — 임시 mirror 디렉토리에 SKILL.md 몇 건 생성.

실제 skills/ 에 의존하지 않는다 (내용이 바뀌어도 테스트가 흔들리지 않게).
"""
from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

SKILLS = {
    "instagram-reels-script-automation": {
        "title": "인스타 릴스 대본 자동 생성",
        "description": "ChatGPT 로 인스타그램 릴스 대본을 30초 만에 뽑는 프롬프트 체인",
        "category": "콘텐츠",
        "grade": "S",
        "difficulty": "초급",
        "ai_tools": ["ChatGPT", "Claude"],
        "sources": ["https://www.youtube.com/watch?v=abc123"],
        "body": (
            "## 어떻게 작동하나요?\n\n후킹 → 본문 → CTA 3단 구조로 **릴스** 대본을 만든다.\n\n"
            "```text\n너는 숏폼 작가다. 주제: {topic}\n```\n"
        ),
    },
    "notion-mcp-setup": {
        "title": "Claude Code 에 Notion MCP 붙이기",
        "description": "공식 Notion MCP 서버를 OAuth 로 연결해 워크스페이스를 자연어로 읽고 쓴다",
        "category": "개발",
        "grade": "A",
        "difficulty": "중급",
        "ai_tools": ["Claude Code", "Notion"],
        "sources": ["https://ink-jay.notion.site/notion-mcp-1234"],
        "body": "## 따라 하기\n\n1. `/mcp` 입력\n2. Notion 선택\n\n<script>alert('xss')</script>\n",
    },
    "stock-analysis-prompts": {
        "title": "Gemini 주식 분석 프롬프트 5종",
        "description": "재무제표·뉴스·차트를 Gemini 에 넣어 종목 리포트를 뽑는 프롬프트",
        "category": "업무",
        "grade": "B",
        "difficulty": "중급",
        "ai_tools": ["Gemini"],
        "sources": ["https://example.com/stock-prompts", "https://github.com/foo/bar"],
        "body": "## 실제 예시\n\n| 항목 | 프롬프트 |\n|---|---|\n| 재무 | ... |\n",
    },
    # v2.4 이전 — grade/category 등 누락 (실제 mirror 에 11건 존재)
    "legacy-no-meta": {
        "title": "옛 포맷 스킬",
        "description": "카테고리/등급 필드가 없는 옛 SKILL.md",
        "sources": ["https://example.com/legacy"],
        "body": "본문만 있음. 인스타 언급 한 번.\n",
    },
}


def render_skill_md(slug: str, spec: dict) -> str:
    lines = ["---", f"name: {slug}", f"description: {spec['description']}", "origin: content-lab"]
    if "grade" in spec:
        lines.append(f"grade: {spec['grade']}")
    if "difficulty" in spec:
        lines.append(f"difficulty: {spec['difficulty']}")
    if "category" in spec:
        lines.append(f"category: {spec['category']}")
    if "ai_tools" in spec:
        tools = ", ".join(f'"{t}"' for t in spec["ai_tools"])
        lines.append(f"ai_tools: [{tools}]")
    lines.append("sources:")
    for u in spec["sources"]:
        lines.append(f"  - {u}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {spec['title']}")
    lines.append("")
    lines.append(f"💡 {spec['description']}")
    lines.append("")
    lines.append(spec["body"].rstrip())
    lines.append("")
    lines.append("## 출처")
    lines.append("")
    for u in spec["sources"]:
        lines.append(f"- [{u}]({u})")
    lines.append("")
    return "\n".join(lines)


def make_mirror(skills: dict | None = None) -> Path:
    """임시 디렉토리에 SKILL.md 들을 만들고 루트 경로 반환. 호출자가 정리(shutil.rmtree)."""
    root = Path(tempfile.mkdtemp(prefix="skills_fixture_"))
    for i, (slug, spec) in enumerate((skills or SKILLS).items()):
        d = root / slug
        d.mkdir()
        (d / "SKILL.md").write_text(render_skill_md(slug, spec), encoding="utf-8")
        # mtime 을 서로 다르게 — 정렬/버전 테스트용
        t = time.time() - (100 - i)
        os.utime(d / "SKILL.md", (t, t))
    return root
