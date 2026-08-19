"""표준 8섹션 H2 가 아닌 H2 → H3 강등.

표준 H2:
- 🎯 어떨 때 쓰나요?
- 🔑 어떻게 작동하나요?
- 🛠 따라 하기 (단계별)
- 💡 실제 예시
- 🏢 두근컴퍼니에서 어떻게 활용?
- ⚠️ 주의할 점
- 📎 출처
- 📌 원본 코드/명령어 (자동 보존)

이 외 모든 H2 (LLM 출력에서 sub-section 이 H2로 박힌 것) → H3로 변환.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import requests
from dotenv import load_dotenv
from pathlib import Path
from scripts.notion_paging import query_all_pages

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API = "https://api.notion.com/v1"
H = {
    "Authorization": f"Bearer {os.environ['NOTION_API_KEY']}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
DB_ID = os.environ["NOTION_DB_ID"]

STANDARD_HEADERS = {
    "🎯 어떨 때 쓰나요?", "🔑 어떻게 작동하나요?", "🛠 따라 하기 (단계별)",
    "💡 실제 예시", "🏢 두근컴퍼니에서 어떻게 활용?", "⚠️ 주의할 점", "📎 출처",
    "📌 원본 코드/명령어 (자동 보존)",
}


def block_text(b: dict) -> str:
    t = b.get("type", "?")
    return "".join(r.get("plain_text", "") for r in b.get(t, {}).get("rich_text", []))


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


def demote_h2_to_h3(bid: str, text: str, annotations: dict | None = None) -> bool:
    """H2 → H3 변환 — Notion API: PATCH /blocks/{id} with heading_3 (heading_2 는 archive)."""
    # 새로 만들기 (Notion API 는 type 변경 직접 안 됨, 새 블록 만들고 옛 block delete)
    # 실제 방법: heading_2 의 rich_text 만 다음 paragraph 로 옮기는 건 못 함.
    # 대안 1: heading_3 으로 update — Notion API 는 type 변경 미지원.
    # 대안 2: heading_2 자리에 heading_3 새 블록 append after + 옛 heading_2 archive
    # 너무 복잡 — 그냥 heading_2 의 text 앞에 H3 표식 prefix 못 함.
    # 가장 간단한 우회: heading_2 block 의 text 만 변경하지 않고, page reorder API 없음.
    # → Notion API 로 H2→H3 직접 변환 불가. 옛 block 삭제 + 새 H3 block insert after 옛 위치.
    return False  # placeholder


def replace_h2_with_h3(pid: str, h2_bid: str, text: str, apply: bool) -> bool:
    """옛 H2 block 위치에 새 H3 block 추가 → 옛 H2 archive."""
    if not apply:
        return True
    # 1) H3 block insert after H2 (위치 보존 위해)
    r = requests.patch(
        f"{API}/blocks/{pid}/children",
        headers=H,
        json={
            "children": [{
                "object": "block", "type": "heading_3",
                "heading_3": {"rich_text": [{"type": "text", "text": {"content": text}}]},
            }],
            "after": h2_bid,
        },
        timeout=30,
    )
    if r.status_code != 200:
        return False
    # 2) 옛 H2 삭제
    time.sleep(0.1)
    requests.delete(f"{API}/blocks/{h2_bid}", headers=H, timeout=30)
    time.sleep(0.06)
    return True


def process(p: dict, apply: bool) -> str:
    pid = p["id"]
    blocks = get_all_blocks(pid)
    targets: list[tuple[str, str]] = []
    for b in blocks:
        if b.get("type") != "heading_2":
            continue
        text = block_text(b).strip()
        if text not in STANDARD_HEADERS:
            targets.append((b["id"], text))
    if not targets:
        return "⏭ 비표준 H2 없음"
    if not apply:
        return f"🔍[dry] {len(targets)}개 H2→H3: {[t[:30] for _,t in targets[:3]]}"
    ok = 0
    for bid, text in targets:
        if replace_h2_with_h3(pid, bid, text, True):
            ok += 1
    return f"✅ {ok}/{len(targets)} H3 강등"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--only", type=str, default="")
    args = parser.parse_args()

    pages = query_all_pages(API, H, DB_ID)
    if args.only:
        pages = [p for p in pages if args.only in "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])]

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"📡 모드: {mode} · 대상: {len(pages)}건\n")
    for i, p in enumerate(pages, 1):
        title = "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])
        try:
            res = process(p, args.apply)
            print(f"  [{i:2d}/{len(pages)}] {title[:46]:<46}  {res}")
        except Exception as e:
            print(f"  [{i:2d}/{len(pages)}] {title[:46]:<46}  ❌ {e}")
        time.sleep(0.2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
