"""v2.8 — H2 헤더 텍스트 초보자 친화 한글로 통일.

영문 부제 (When to use / How it works / Steps / Examples / Caveats / Sources) 제거.
"메타" 같은 jargon 제거. 친근 질문 톤.

매핑:
- "🎯 When to use ..." → "🎯 어떨 때 쓰나요?"
- "🔑 How it works ..." → "🔑 어떻게 작동하나요?"
- "🛠 Steps ..." → "🛠 따라 하기 (단계별)"
- "💡 Examples ..." → "💡 실제 예시"
- "🏢 두근 환경 적용" → "🏢 두근컴퍼니에서 어떻게 활용?"
- "⚠️ Caveats ..." → "⚠️ 주의할 점"
- "📎 Sources ..." → "📎 출처"
"""
from __future__ import annotations

import argparse
import os
import re
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

# 매칭 패턴 → 새 텍스트
HEADING_MAP: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^🎯\s*(When\s*to\s*use|언제\s*쓰[는나]|사용\s*시점|언제).*$", re.I), "🎯 어떨 때 쓰나요?"),
    (re.compile(r"^🔑\s*(How\s*it\s*works|작[동업]\s*원리|원리|핵심|어떻게|작동).*$", re.I), "🔑 어떻게 작동하나요?"),
    (re.compile(r"^🛠\s*(Steps|적용\s*단계|단계|따라\s*하기|적용\s*순서).*$", re.I), "🛠 따라 하기 (단계별)"),
    (re.compile(r"^💡\s*(Examples|예시|실제\s*예).*$", re.I), "💡 실제 예시"),
    (re.compile(r"^🏢\s*(두근(컴퍼니)?\s*(환경)?\s*(적용|활용)|두근|적용\s*대상).*$", re.I), "🏢 두근컴퍼니에서 어떻게 활용?"),
    (re.compile(r"^⚠️\s*(Caveats|주의(사항|할\s*점)?|미리|한계|제한).*$", re.I), "⚠️ 주의할 점"),
    (re.compile(r"^📎\s*(Sources|출처|참고|원본|레퍼런스|링크).*$", re.I), "📎 출처"),
]

# 표준 H2 헤더 (변경 대상이 아닌, 정확히 일치하는 것)
STANDARD_HEADERS = {
    "🎯 어떨 때 쓰나요?", "🔑 어떻게 작동하나요?", "🛠 따라 하기 (단계별)",
    "💡 실제 예시", "🏢 두근컴퍼니에서 어떻게 활용?", "⚠️ 주의할 점", "📎 출처",
    "📌 원본 코드/명령어 (자동 보존)",
}


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


def map_heading(text: str) -> str | None:
    t = text.strip()
    for pat, new_text in HEADING_MAP:
        if pat.match(t):
            return new_text
    return None


def update_heading(bid: str, btype: str, new_text: str) -> bool:
    body = {btype: {"rich_text": [{"type": "text", "text": {"content": new_text}}]}}
    r = requests.patch(f"{API}/blocks/{bid}", headers=H, json=body, timeout=30)
    return r.status_code == 200


def process(p: dict, apply: bool) -> str:
    pid = p["id"]
    blocks = get_all_blocks(pid)
    changes: list[tuple[str, str, str]] = []
    for b in blocks:
        t = b.get("type")
        if t not in ("heading_1", "heading_2", "heading_3"):
            continue
        text = block_text(b)
        mapped = map_heading(text)
        if mapped and mapped != text.strip():
            changes.append((b["id"], t, mapped))
    if not changes:
        return "⏭ 이미 정리됨"
    if not apply:
        return f"🔍[dry] {len(changes)}개 헤더 변경 예정"
    ok = 0
    for bid, btype, new_text in changes:
        if update_heading(bid, btype, new_text):
            ok += 1
        time.sleep(0.08)
    return f"✅ {ok}/{len(changes)} 헤더 변경"


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
