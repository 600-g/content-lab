"""Notion 페이지 본문에서 텍스트로 박힌 HTML/주석 잔재 정리.

처리:
1. <!-- table 블록 생략 (보존 어려움) --> → 블록 제거
2. <details>, <summary>, </summary>, </details> → 블록 제거
3. 그 외 단독 빈 <태그> 블록 (paragraph type) → 제거. <placeholder>는 보존 (사용자 의도)
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

# 제거 대상 정확한 텍스트 (블록 전체 텍스트 매치)
DROP_EXACT = {
    "<!-- table 블록 생략 (보존 어려움) -->",
    "<details>",
    "<summary>",
    "</summary>",
    "</details>",
}


def cleanup_page(pid: str, title: str) -> int:
    """페이지 블록 순회 + 제거 대상 삭제. 제거 카운트 반환."""
    removed = 0
    cursor = None
    while True:
        path = f"{API}/blocks/{pid}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        d = requests.get(path, headers=H, timeout=20).json()
        for b in d.get("results", []):
            t = b.get("type")
            rt = b.get(t, {}).get("rich_text", [])
            text = "".join(r.get("plain_text", "") for r in rt).strip()
            if text in DROP_EXACT:
                try:
                    rd = requests.delete(f"{API}/blocks/{b['id']}", headers=H, timeout=15)
                    if rd.status_code == 200:
                        removed += 1
                    time.sleep(0.05)
                except Exception:
                    pass
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
    return removed


def main() -> int:
    r = requests.post(f"{API}/databases/{DB_ID}/query", headers=H, json={"page_size": 50}).json()
    pages = r.get("results", [])
    print(f"📡 {len(pages)}건 검사\n")
    total_removed = 0
    for i, p in enumerate(pages, 1):
        pid = p["id"]
        title = "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])
        n = cleanup_page(pid, title)
        if n > 0:
            print(f"  [{i:2d}/{len(pages)}] {title[:50]:<50} — {n}개 잔재 제거")
            total_removed += n
        else:
            print(f"  [{i:2d}/{len(pages)}] {title[:50]:<50} — 깨끗")
        time.sleep(0.2)
    print(f"\n총 {total_removed}개 잔재 제거")
    return 0


if __name__ == "__main__":
    sys.exit(main())
