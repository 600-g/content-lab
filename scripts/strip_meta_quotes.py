"""v2.8 — TL;DR + 메타 박스 제거.

이유: DB properties (등급/카테고리/난이도/도구/대상) 이 페이지 우상단에 이미 표시.
본문 첫 quote 2개 (TL;DR + 메타) + 그 다음 divider 도 제거.
본문은 ## 8섹션 헤더부터 바로 시작.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API = "https://api.notion.com/v1"
H = {
    "Authorization": f"Bearer {os.environ['NOTION_API_KEY']}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
DB_ID = os.environ["NOTION_DB_ID"]


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


def process(p: dict, apply: bool) -> str:
    pid = p["id"]
    blocks = get_all_blocks(pid)
    if not blocks:
        return "⏭ 빈 페이지"

    # 첫 heading 위치
    first_heading = -1
    for i, b in enumerate(blocks):
        if b.get("type") in ("heading_1", "heading_2", "heading_3"):
            first_heading = i
            break
    if first_heading < 0:
        return "⏭ heading 없음 (건드리지 않음)"

    # heading 이전까지의 quote + divider 모두 제거 대상
    to_delete: list[str] = []
    for i in range(first_heading):
        t = blocks[i].get("type")
        if t in ("quote", "divider"):
            to_delete.append(blocks[i]["id"])

    if not to_delete:
        return "⏭ 이미 정리됨"

    if not apply:
        return f"🔍[dry] {len(to_delete)}블록 제거 예정"

    deleted = 0
    for bid in to_delete:
        try:
            r = requests.delete(f"{API}/blocks/{bid}", headers=H, timeout=30)
            if r.status_code == 200:
                deleted += 1
            time.sleep(0.06)
        except Exception:
            pass
    return f"✅ {deleted}블록 제거 (TL;DR + 메타 + divider)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--only", type=str, default="")
    args = parser.parse_args()

    r = requests.post(f"{API}/databases/{DB_ID}/query", headers=H, json={"page_size": 50}).json()
    pages = r.get("results", [])
    if args.only:
        pages = [p for p in pages if args.only in "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])]

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"📡 모드: {mode} · 대상: {len(pages)}건\n")

    for i, p in enumerate(pages, 1):
        title = "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])
        try:
            result = process(p, args.apply)
            print(f"  [{i:2d}/{len(pages)}] {title[:46]:<46}  {result}")
        except Exception as e:
            print(f"  [{i:2d}/{len(pages)}] {title[:46]:<46}  ❌ {e}")
        time.sleep(0.2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
