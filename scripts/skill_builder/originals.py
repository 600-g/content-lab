"""합쳐진 원본 문서 목록 (2026-10-05 사용자 지시: "원본들도 해당 문서에 같이 리스트해놔").

여러 문서를 하나로 합성하면 원래 어떤 문서들이었는지가 사라진다. 그래서
- frontmatter `originals:` 에 원본 한 건당 한 줄 `슬러그 | 제목 | URL URL ...` 로 저장하고 (다시 합쳐도 이어진다)
- 본문 `## 출처` 아래에 `### 합쳐진 원본 문서` 표로 렌더한다.

`## 출처` 는 md_generator._strip_source_section 이 통째로 떼고 frontmatter 로 다시 그리므로, 표의 단일 진실도 frontmatter 다.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlsplit

SECTION_TITLE = "### 합쳐진 원본 문서"
_FM_RE = re.compile(r"^---\n(.*?)\n---\n?", re.S)
_SECTION_RE = re.compile(r"(?ms)^### 합쳐진 원본 문서\s*$.*?(?=^#{1,3}\s|\Z)")
_ORIG_BLOCK_RE = re.compile(r"(?m)^originals:\s*\n(?:[ \t]+-[^\n]*\n?)*")


def make_entry(slug: str, title: str, urls: list[str]) -> str:
    title = re.sub(r"\s*\((합병됨|합침)\)\s*$", "", (title or "").replace("|", "/")).strip()
    title = re.sub(r"\s*·\s*🔀\s*합병\s*$", "", title)
    return " | ".join([slug.strip(), title or slug.strip(), " ".join(u.strip() for u in urls if u.strip())]).rstrip(" |")


def parse_entry(line: str) -> tuple[str, str, list[str]]:
    parts = [p.strip() for p in line.split(" | ", 2)]
    while len(parts) < 3:
        parts.append("")
    return parts[0], parts[1] or parts[0], parts[2].split() if parts[2] else []


def read_originals(md: str) -> list[str]:
    m = _FM_RE.match(md)
    if not m:
        return []
    block = re.search(r"(?m)^originals:\s*\n((?:[ \t]+-[^\n]*\n?)*)", m.group(1) + "\n")
    if not block:
        return []
    return [ln.split("- ", 1)[1].strip() for ln in block.group(1).splitlines() if ln.strip().startswith("-")]


def self_entry(path: Path) -> str:
    """원본 목록이 없는 문서는 자기 자신이 원본 1건."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    m = _FM_RE.match(text)
    fm = m.group(1) if m else ""
    name = re.search(r"(?m)^name:\s*(.+)$", fm)
    slug = name.group(1).strip() if name else Path(path).parent.name
    title = re.search(r"(?m)^# (.+)$", text[m.end():] if m else text)
    urls = re.findall(r"(?m)^[ \t]+-\s+(\S+)\s*$", fm.split("\noriginals:")[0].split("sources:", 1)[-1]) if "sources:" in fm else []
    return make_entry(slug, title.group(1) if title else slug, urls)


def originals_of(path: Path) -> list[str]:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    return read_originals(text) or [self_entry(path)]


def merge_lists(*lists: list[str]) -> list[str]:
    """순서 유지 합집합 (슬러그 기준 — 같은 원본이 두 번 들어오지 않게)."""
    seen: set[str] = set()
    out: list[str] = []
    for lst in lists:
        for e in lst:
            slug = parse_entry(e)[0]
            if slug and slug not in seen:
                seen.add(slug)
                out.append(e)
    return out


def frontmatter_block(entries: list[str]) -> str:
    if len(entries) < 2:
        return ""
    return "originals:\n" + "".join(f"  - {e}\n" for e in entries)


def _label(url: str) -> str:
    if url.startswith("paste://"):
        return "직접 입력"
    host = urlsplit(url).netloc.lower().removeprefix("www.")
    return host or "링크"


def render_section(entries: list[str]) -> str:
    """원본이 2건 이상일 때만 표를 만든다 (합쳐지지 않은 문서엔 붙이지 않음)."""
    if len(entries) < 2:
        return ""
    rows = []
    for e in entries:
        slug, title, urls = parse_entry(e)
        links = " · ".join(f"[{_label(u)}]({u})" if not u.startswith("paste://") else "직접 입력" for u in urls) or "-"
        rows.append(f"| {title} | `{slug}` | {links} |")
    return (f"{SECTION_TITLE}\n\n이 문서는 아래 {len(entries)}개 문서를 하나로 합쳐 새로 정리한 것입니다.\n\n"
            "| 원본 문서 | 원래 슬러그 | 원본 출처 |\n|---|---|---|\n" + "\n".join(rows) + "\n")


def apply_to_md(md: str, entries: list[str]) -> str:
    """완성된 SKILL.md 에 원본 목록을 넣는다 (frontmatter + `## 출처` 아래 표). 기존 것은 교체. 멱등."""
    m = _FM_RE.match(md)
    if not m:
        return md
    fm, body = m.group(1) + "\n", md[m.end():]
    fm = _ORIG_BLOCK_RE.sub("", fm)
    block = frontmatter_block(entries)
    if block:
        fm = fm.rstrip("\n") + "\n" + block
    body = _SECTION_RE.sub("", body).rstrip() + "\n"
    section = render_section(entries)
    if section:
        body = body.rstrip() + "\n\n" + section
    return f"---\n{fm.rstrip(chr(10))}\n---\n{body}"
