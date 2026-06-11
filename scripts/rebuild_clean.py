"""v2.5 정리 — 누적된 메타 중복 제거 + 빈 섹션 제거 + escape 정리.

원본 본문 흐름은 그대로 보존 (## 헤더 + 그 아래 내용).
페이지 시작의 quote 메타 callout 영역만 1개로 통일.
"""
from __future__ import annotations

import os
import re
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API = "https://api.notion.com/v1"
H = {
    "Authorization": f"Bearer {os.environ['NOTION_API_KEY']}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
DB_ID = os.environ['NOTION_DB_ID']


def block_text(b: dict) -> str:
    t = b.get("type", "?")
    rt = b.get(t, {}).get("rich_text", [])
    return "".join(r.get("plain_text", "") for r in rt)


def get_all_blocks(pid: str) -> list[dict]:
    blocks = []
    cursor = None
    while True:
        path = f"{API}/blocks/{pid}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        d = requests.get(path, headers=H, timeout=20).json()
        blocks.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
    return blocks


def unescape(s: str) -> str:
    """\*\*text\*\* → **text**, \[abc\] → [abc] 등 backslash 정리."""
    s = re.sub(r"\\([\*\[\]\(\)~<>\\])", r"\1", s)
    return s


def rebuild_text(s: str) -> str:
    return unescape(s).strip()


def blocks_to_markdown(blocks: list[dict]) -> str:
    """블록 → 마크다운. 첫 메타 callout 영역(연속 quote) 자동 제거 + escape 정리."""
    # 1단계: 첫 quote/divider 연속 블록 + 그 안의 callout 모두 제거 (메타 중복 영역)
    # — 첫 heading_2/3 가 나올 때까지 quote, paragraph(빈/quote 같은) 모두 skip
    start = 0
    for i, b in enumerate(blocks):
        t = b.get("type")
        if t in ("heading_1", "heading_2", "heading_3"):
            start = i
            break
        # paragraph 인데 내용이 메타스럽지 않으면 — heading 까지 진행
    # 만약 heading 못 찾으면 처음부터 (메타만 있는 페이지)
    if start == 0:
        # 첫 메타 quote 다 지나가게
        for i, b in enumerate(blocks):
            if b.get("type") not in ("quote", "paragraph", "divider"):
                start = i
                break
        else:
            start = 0

    md_parts: list[str] = []
    prev_type = None
    for b in blocks[start:]:
        t = b.get("type", "?")
        text = rebuild_text(block_text(b))
        if t == "heading_1":
            md_parts.append(f"# {text}")
        elif t == "heading_2":
            md_parts.append(f"## {text}")
        elif t == "heading_3":
            md_parts.append(f"### {text}")
        elif t == "bulleted_list_item":
            md_parts.append(f"- {text}")
        elif t == "numbered_list_item":
            md_parts.append(f"1. {text}")
        elif t == "quote":
            if text:
                md_parts.append(f"> {text}")
        elif t == "code":
            lang = b.get("code", {}).get("language", "")
            md_parts.append(f"```{lang}\n{text}\n```")
        elif t == "divider":
            md_parts.append("---")
        elif t == "paragraph":
            if text:
                md_parts.append(text)
        prev_type = t

    md = "\n\n".join(md_parts)
    # 2단계: 빈 섹션 제거 — ## 헤더 다음 다음 ## 까지 내용 없으면 헤더 제거
    md = remove_empty_sections(md)
    # 3단계: 연속 빈 줄 정리
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def remove_empty_sections(md: str) -> str:
    lines = md.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # ## 헤더?
        if line.startswith("## "):
            # 다음 ## 또는 # 까지 내용 있는지
            j = i + 1
            has_content = False
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith("## ") or next_line.startswith("# "):
                    break
                if next_line and not next_line.startswith("---"):
                    has_content = True
                    break
                j += 1
            if has_content:
                out.append(line)
            # else: skip 헤더
        else:
            out.append(line)
        i += 1
    return "\n".join(out)


def make_meta_box(props: dict, tldr: str) -> str:
    """페이지 맨 위 깨끗한 메타 박스 1개."""
    grade = props["grade"].split("-")[0]
    cat = props["cat"]
    diff = props["diff"]
    tools = " · ".join(props["tools"][:5]) if props["tools"] else "도구무관"
    targets = " · ".join(props["targets"][:5]) if props["targets"] else "공통"
    return (
        f"> 📌 **{tldr}**\n"
        f">\n"
        f"> **{grade}** · {cat} · {diff} · 🤖 {tools} → 🎯 {targets}"
    )


def extract_tldr(md: str, fallback: str) -> str:
    """본문에서 첫 의미 있는 문장 추출 (TL;DR)."""
    # 첫 paragraph (## 헤더 다음의 첫 문장)
    for line in md.split("\n"):
        s = line.strip()
        if not s or s.startswith(("#", ">", "-", "*", "1.", "```", "---")):
            continue
        # 너무 짧으면 다음
        if len(s) > 20:
            return s[:180]
    return fallback


def md_to_blocks(md: str) -> list[dict]:
    blocks: list[dict] = []
    in_code = False
    code_lang = ""
    code_buf: list[str] = []
    for line in md.splitlines():
        if line.strip().startswith("```"):
            if in_code:
                blocks.append({
                    "object": "block", "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": "\n".join(code_buf)[:1900]}}],
                        "language": code_lang or "plain text",
                    },
                })
                in_code = False
                code_buf = []
                code_lang = ""
            else:
                in_code = True
                code_lang = line.strip().lstrip("`").strip() or ""
            continue
        if in_code:
            code_buf.append(line)
            continue
        s = line.strip()
        if not s:
            continue
        if s.startswith("> "):
            blocks.append(_b("quote", s[2:]))
        elif s.startswith("# "):
            blocks.append(_b("heading_1", s[2:]))
        elif s.startswith("## "):
            blocks.append(_b("heading_2", s[3:]))
        elif s.startswith("### "):
            blocks.append(_b("heading_3", s[4:]))
        elif s.startswith(("- ", "* ")):
            blocks.append(_b("bulleted_list_item", s[2:]))
        elif re.match(r"^\d+\.\s", s):
            blocks.append(_b("numbered_list_item", re.sub(r"^\d+\.\s", "", s)))
        elif s == "---":
            blocks.append({"object": "block", "type": "divider", "divider": {}})
        else:
            blocks.append(_b("paragraph", s[:1900]))
        if len(blocks) >= 95:
            break
    return blocks


def _b(btype: str, text: str) -> dict:
    return {
        "object": "block", "type": btype,
        btype: {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def replace_blocks(pid: str, new_blocks: list[dict]) -> bool:
    cursor = None
    old_ids: list[str] = []
    while True:
        path = f"{API}/blocks/{pid}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        d = requests.get(path, headers=H, timeout=20).json()
        old_ids.extend(b["id"] for b in d.get("results", []))
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
    for bid in old_ids:
        try:
            requests.delete(f"{API}/blocks/{bid}", headers=H, timeout=15)
        except Exception:
            pass
        time.sleep(0.04)
    for i in range(0, len(new_blocks), 100):
        chunk = new_blocks[i:i+100]
        r = requests.patch(f"{API}/blocks/{pid}/children", headers=H, json={"children": chunk}, timeout=30)
        if r.status_code >= 400:
            return False
        time.sleep(0.2)
    return True


def main() -> int:
    r = requests.post(f"{API}/databases/{DB_ID}/query", headers=H, json={"page_size": 50}).json()
    pages = r.get("results", [])
    print(f"📡 {len(pages)}건 정리\n")
    ok = 0
    failed = 0
    for i, p in enumerate(pages, 1):
        pid = p["id"]
        pr = p["properties"]
        title = "".join(t["plain_text"] for t in pr.get("스킬명", {}).get("title", []))
        meta_props = {
            "title": title,
            "grade": (pr.get("등급", {}).get("select") or {}).get("name", "S"),
            "cat": (pr.get("카테고리", {}).get("select") or {}).get("name", "기타"),
            "diff": (pr.get("난이도", {}).get("select") or {}).get("name", "🟡 중급"),
            "tools": [t["name"] for t in pr.get("AI 도구", {}).get("multi_select", [])],
            "targets": [t["name"] for t in pr.get("적용 대상", {}).get("multi_select", [])],
        }
        try:
            blocks = get_all_blocks(pid)
            body_md = blocks_to_markdown(blocks)
            tldr = extract_tldr(body_md, title)
            meta_box = make_meta_box(meta_props, tldr)
            final_md = f"{meta_box}\n\n---\n\n{body_md}"
            new_blocks = md_to_blocks(final_md)
            print(f"  [{i:2d}/{len(pages)}] {title[:48]:<48}  블록 {len(blocks)}→{len(new_blocks)}")
            if replace_blocks(pid, new_blocks):
                ok += 1
                print(f"            ✅ 정리 완료")
            else:
                failed += 1
                print(f"            ❌ 실패")
        except Exception as e:
            failed += 1
            print(f"  [{i:2d}/{len(pages)}] {title[:48]} 예외: {e}")
        time.sleep(0.4)
    print(f"\n총 {ok}/{ok+failed} 성공")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
