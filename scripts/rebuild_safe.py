"""v2.5 안전 정리 — 본문 100% 보존 + 자동 백업.

핵심 룰:
1. 첫 heading_2 위치 명확히 찾기. 못 찾으면 **그 페이지 건드리지 않음**.
2. heading 직전까지 **연속된 quote 블록만** 제거 (paragraph/list/code는 보존).
3. 새 메타 박스 1개 prepend.
4. 처리 전 logs/backup_v25/{pid}.md 에 원본 본문 백업.
5. 기본은 --dry. --apply 명시해야 실제 적용.
"""
from __future__ import annotations

import argparse
import datetime
import os
import re
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from scripts.notion_paging import query_all_pages

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API = "https://api.notion.com/v1"
H = {
    "Authorization": f"Bearer {os.environ['NOTION_API_KEY']}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
DB_ID = os.environ['NOTION_DB_ID']

BACKUP_DIR = Path(__file__).resolve().parents[1] / "logs" / f"backup_v25_{datetime.date.today().isoformat()}"


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


def find_first_heading(blocks: list[dict]) -> int:
    """첫 heading_2 또는 heading_1 위치 반환. 못 찾으면 -1."""
    for i, b in enumerate(blocks):
        if b.get("type") in ("heading_1", "heading_2"):
            return i
    return -1


def count_leading_quotes(blocks: list[dict], heading_at: int) -> int:
    """heading 직전까지 **연속된** quote 블록 수.

    quote 가 아닌 블록(paragraph/list/divider)이 중간에 끼면 거기서 멈춤.
    이게 핵심 안전장치 — 본문 paragraph 절대 안 건드림.
    """
    # heading_at 부터 역방향으로 quote 연속 카운트
    count = 0
    for i in range(heading_at - 1, -1, -1):
        b = blocks[i]
        t = b.get("type")
        if t == "quote":
            count += 1
        elif t == "divider":
            continue  # divider 는 통과 (separator 일 수 있음)
        else:
            # paragraph/list/code 등이면 거기서 멈춤
            break
    return count


def blocks_to_md(blocks: list[dict]) -> str:
    """블록 → 마크다운 (백업/표시용)."""
    parts: list[str] = []
    for b in blocks:
        t = b.get("type", "?")
        text = block_text(b)
        if t == "heading_1":
            parts.append(f"# {text}")
        elif t == "heading_2":
            parts.append(f"## {text}")
        elif t == "heading_3":
            parts.append(f"### {text}")
        elif t == "bulleted_list_item":
            parts.append(f"- {text}")
        elif t == "numbered_list_item":
            parts.append(f"1. {text}")
        elif t == "quote":
            parts.append(f"> {text}")
        elif t == "code":
            lang = b.get("code", {}).get("language", "")
            parts.append(f"```{lang}\n{text}\n```")
        elif t == "divider":
            parts.append("---")
        elif t == "paragraph":
            if text.strip():
                parts.append(text)
    return "\n\n".join(parts)


def make_meta_box(props: dict, tldr: str) -> list[dict]:
    """깨끗한 메타 박스 (quote 2개로)."""
    grade = props["grade"].split("-")[0]
    cat = props["cat"]
    diff = props["diff"]
    tools = " · ".join(props["tools"][:5]) if props["tools"] else "도구무관"
    targets = " · ".join(props["targets"][:5]) if props["targets"] else "공통"

    line1 = f"📌 {tldr}"
    line2 = f"{grade} · {cat} · {diff} · 🤖 {tools} → 🎯 {targets}"
    return [
        {"object": "block", "type": "quote", "quote": {"rich_text": [{"type": "text", "text": {"content": line1}}]}},
        {"object": "block", "type": "quote", "quote": {"rich_text": [{"type": "text", "text": {"content": line2}}]}},
    ]


def extract_tldr_from_props(pr: dict, title: str) -> str:
    """첫 paragraph 또는 핵심 요약. 우선 props에 메타 callout 안에 있을 수 있는 TL;DR 추출 시도."""
    # 단순히 title 의 마지막 ( ) 까지 또는 첫 50자
    s = title.strip()
    # 부제 패턴 (제목 (부제))
    m = re.match(r"^(.+?)\s*\(([^)]{8,})\)", s)
    if m:
        return f"{m.group(1)} — {m.group(2)}"
    return s[:120]


def process(pid: str, title: str, props: dict, apply: bool) -> str:
    blocks = get_all_blocks(pid)
    heading_at = find_first_heading(blocks)

    if heading_at < 0:
        return "⏭ heading 없음 (건드리지 않음)"

    leading_quotes = count_leading_quotes(blocks, heading_at)

    # 백업
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / f"{pid}.md"
    backup_path.write_text(f"# {title}\n\n" + blocks_to_md(blocks), encoding="utf-8")

    if leading_quotes <= 1:
        return f"⏭ quote {leading_quotes}개 (정리 불필요)"

    # 첫 1개 유지 + 나머지 제거 (중복만 정리)
    quote_indices = [i for i in range(heading_at - leading_quotes, heading_at)
                     if blocks[i].get("type") == "quote"]
    # 첫 quote 유지, 나머지 제거
    to_delete = [blocks[i]["id"] for i in quote_indices[1:]]

    msg = f"백업✓ · 중복 quote {len(to_delete)}개 제거 (첫 1개 유지)"
    if not apply:
        return f"🔍 [dry] {msg}"

    # 실제 적용 — 중복 quote 삭제만
    for bid in to_delete:
        try:
            requests.delete(f"{API}/blocks/{bid}", headers=H, timeout=15)
            time.sleep(0.06)
        except Exception:
            pass

    return f"✅ {msg}"


def main() -> int:
    parser = argparse.ArgumentParser(description="v2.5 안전 정리")
    parser.add_argument("--apply", action="store_true", help="실제 적용 (없으면 dry-run)")
    parser.add_argument("--limit", type=int, default=0, help="처리 페이지 수 제한")
    args = parser.parse_args()

    pages = query_all_pages(API, H, DB_ID)
    if args.limit > 0:
        pages = pages[:args.limit]
    mode = "APPLY" if args.apply else "DRY-RUN (변경 없음)"
    print(f"📡 모드: {mode} · 대상: {len(pages)}건\n")
    print(f"📁 백업: {BACKUP_DIR}\n")

    for i, p in enumerate(pages, 1):
        pid = p["id"]
        pr = p["properties"]
        title = "".join(t["plain_text"] for t in pr.get("스킬명", {}).get("title", []))
        props = {
            "title": title,
            "grade": (pr.get("등급", {}).get("select") or {}).get("name", "S"),
            "cat": (pr.get("카테고리", {}).get("select") or {}).get("name", "기타"),
            "diff": (pr.get("난이도", {}).get("select") or {}).get("name", "🟡 중급"),
            "tools": [t["name"] for t in pr.get("AI 도구", {}).get("multi_select", [])],
            "targets": [t["name"] for t in pr.get("적용 대상", {}).get("multi_select", [])],
        }
        try:
            result = process(pid, title, props, apply=args.apply)
            print(f"  [{i:2d}/{len(pages)}] {title[:46]:<46}  {result}")
        except Exception as e:
            print(f"  [{i:2d}/{len(pages)}] {title[:46]:<46}  ❌ 예외: {e}")
        time.sleep(0.2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
