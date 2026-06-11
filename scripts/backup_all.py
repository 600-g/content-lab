"""v2.7 재정리 전 전체 페이지 백업.

logs/backup_v27_{date}/
  {pid}__{slug}.md      — markdown 본문
  {pid}__{slug}.json    — properties + raw blocks
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
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

BACKUP_DIR = Path(__file__).resolve().parents[1] / "logs" / f"backup_v27_{datetime.date.today().isoformat()}"


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
        d = requests.get(path, headers=H, timeout=30).json()
        blocks.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
    return blocks


def blocks_to_md(blocks: list[dict]) -> str:
    parts: list[str] = []
    for b in blocks:
        t = b.get("type", "?")
        text = block_text(b)
        if t == "heading_1": parts.append(f"# {text}")
        elif t == "heading_2": parts.append(f"## {text}")
        elif t == "heading_3": parts.append(f"### {text}")
        elif t == "bulleted_list_item": parts.append(f"- {text}")
        elif t == "numbered_list_item": parts.append(f"1. {text}")
        elif t == "quote": parts.append(f"> {text}")
        elif t == "code":
            lang = b.get("code", {}).get("language", "")
            parts.append(f"```{lang}\n{text}\n```")
        elif t == "divider": parts.append("---")
        elif t == "paragraph":
            if text.strip(): parts.append(text)
    return "\n\n".join(parts)


def slugify(s: str) -> str:
    s = re.sub(r"[^\w가-힣]+", "-", s).strip("-")
    return s[:60]


def main() -> int:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.post(f"{API}/databases/{DB_ID}/query", headers=H, json={"page_size": 50}).json()
    pages = r.get("results", [])
    print(f"📁 백업 디렉토리: {BACKUP_DIR}")
    print(f"📡 {len(pages)}건 백업\n")

    for i, p in enumerate(pages, 1):
        pid = p["id"]
        pr = p["properties"]
        title = "".join(t["plain_text"] for t in pr.get("스킬명", {}).get("title", []))
        try:
            blocks = get_all_blocks(pid)
            md = blocks_to_md(blocks)
            stem = f"{pid.replace('-','')}__{slugify(title)}"
            (BACKUP_DIR / f"{stem}.md").write_text(f"# {title}\n\n{md}", encoding="utf-8")
            meta = {
                "page_id": pid,
                "title": title,
                "icon": p.get("icon"),
                "properties": pr,
                "raw_blocks": blocks,
            }
            (BACKUP_DIR / f"{stem}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            md_chars = len(md)
            print(f"  [{i:2d}/{len(pages)}] {title[:46]:<46}  {len(blocks)}블록 / {md_chars}자")
        except Exception as e:
            print(f"  [{i:2d}/{len(pages)}] {title[:46]:<46}  ❌ {e}")
    print(f"\n✅ 백업 완료: {BACKUP_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
