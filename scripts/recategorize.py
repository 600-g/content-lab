"""각 페이지를 LLM 으로 카테고리 재분류 + 아이콘 동기화.

카테고리 7종:
- 프롬프트 (💬) — 프롬프트 엔지니어링, 시스템 프롬프트 설계
- 자동화 (🤖) — AI 에이전트, 워크플로우, 작업 자동화
- 콘텐츠 (🎬) — 영상/이미지/텍스트 콘텐츠 생성, SNS
- 디자인 (🎨) — UI/UX, 캐릭터, 시각 디자인
- 개발 (💻) — 코딩, 앱 구축, 배포
- 업무 (⚡) — 문서, 회의록, 일정, 지식 관리
- 기타 (📦)
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from scripts.notion_paging import query_all_pages

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API = "https://api.notion.com/v1"
H = {
    "Authorization": f"Bearer {os.environ['NOTION_API_KEY']}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
DB_ID = os.environ["NOTION_DB_ID"]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]

CATEGORIES = ["프롬프트", "자동화", "콘텐츠", "디자인", "개발", "업무", "기타"]
CATEGORY_DESC = {
    "프롬프트": "프롬프트 엔지니어링, 시스템 프롬프트 설계, 프롬프트 기법",
    "자동화": "AI 에이전트, 워크플로우, 작업 자동화, MCP, n8n, Zapier",
    "콘텐츠": "영상·이미지·텍스트 콘텐츠 생성, SNS, 광고, 마케팅 콘텐츠",
    "디자인": "UI/UX, 캐릭터, 시각 디자인, 사진 보정, 포스터",
    "개발": "코딩, 앱·서비스 구축, 배포, 개발 환경, 도구 설정",
    "업무": "문서, 회의록, 일정 관리, 지식 관리, 노트 시스템",
    "기타": "위 분류에 안 맞는 것",
}
CATEGORY_ICON = {
    "프롬프트": "💬", "자동화": "🤖", "콘텐츠": "🎬", "디자인": "🎨",
    "개발": "💻", "업무": "⚡", "기타": "📦",
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


def page_body(pid: str) -> str:
    bb = get_all_blocks(pid)
    return "\n".join(block_text(b) for b in bb)[:3000]


CLASSIFY_PROMPT = """다음 AI 스킬 페이지의 카테고리를 1개만 선택해라.

카테고리 7종:
{categories}

페이지 제목: {title}
페이지 본문 (앞부분):
---
{body}
---

응답은 JSON 만:
{{"category": "<7종 중 1개>", "reason": "<한 줄 근거>"}}
"""


def call_gemma(prompt: str) -> str | None:
    try:
        r = requests.post(
            f"{os.getenv('OLLAMA_URL','http://localhost:11434')}/api/generate",
            json={
                "model": "gemma4:26b",
                "prompt": prompt,
                "stream": False,
                "think": False,
                "format": "json",
                "keep_alive": "30m",
                "options": {"temperature": 0.1},
            },
            timeout=120,
        )
        r.raise_for_status()
        return r.json().get("response", "") or None
    except Exception:
        return None


def call_gemini(prompt: str) -> str | None:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    try:
        r = requests.post(
            url, headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "response_mime_type": "application/json"},
            },
            timeout=60,
        )
        if r.status_code != 200:
            return None
        d = r.json()
        cands = d.get("candidates", [])
        if not cands:
            return None
        return "".join(p.get("text", "") for p in cands[0].get("content", {}).get("parts", [])) or None
    except Exception:
        return None


def classify(title: str, body: str, engine: str) -> tuple[str, str] | None:
    cats = "\n".join(f"- {c}: {CATEGORY_DESC[c]}" for c in CATEGORIES)
    prompt = CLASSIFY_PROMPT.format(categories=cats, title=title, body=body)
    out = (call_gemini(prompt) if engine == "gemini" else None) or call_gemma(prompt)
    if not out:
        return None
    import json
    try:
        d = json.loads(out)
        cat = d.get("category", "기타")
        if cat not in CATEGORIES:
            cat = "기타"
        return cat, d.get("reason", "")
    except Exception:
        return None


def update_page(pid: str, new_cat: str, new_icon: str) -> bool:
    body = {
        "properties": {
            "카테고리": {"select": {"name": new_cat}},
        },
        "icon": {"type": "emoji", "emoji": new_icon},
    }
    r = requests.patch(f"{API}/pages/{pid}", headers=H, json=body, timeout=30)
    return r.status_code == 200


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--engine", choices=["gemini", "gemma"], default="gemma")
    parser.add_argument("--only", type=str, default="")
    args = parser.parse_args()

    pages = query_all_pages(API, H, DB_ID)
    if args.only:
        pages = [p for p in pages if args.only in "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])]

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"📡 모드: {mode} · 엔진: {args.engine} · 대상: {len(pages)}건\n")

    changed = 0
    for i, p in enumerate(pages, 1):
        pid = p["id"]
        title = "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])
        cur_cat = (p["properties"].get("카테고리", {}).get("select") or {}).get("name") or "기타"
        cur_icon = (p.get("icon") or {}).get("emoji", "")
        try:
            body = page_body(pid)
            result = classify(title, body, args.engine)
            if not result:
                print(f"  [{i:2d}/{len(pages)}] {title[:42]:<42}  ❌ LLM 실패 (현재 {cur_cat})")
                continue
            new_cat, reason = result
            new_icon = CATEGORY_ICON.get(new_cat, "📦")
            if new_cat == cur_cat and cur_icon == new_icon:
                print(f"  [{i:2d}/{len(pages)}] {title[:42]:<42}  ⏭ 동일 ({cur_cat} {cur_icon})")
                continue
            arrow = f"{cur_cat} {cur_icon} → {new_cat} {new_icon}"
            if not args.apply:
                print(f"  [{i:2d}/{len(pages)}] {title[:42]:<42}  🔍 {arrow} · {reason[:40]}")
                changed += 1
            else:
                ok = update_page(pid, new_cat, new_icon)
                print(f"  [{i:2d}/{len(pages)}] {title[:42]:<42}  {'✅' if ok else '❌'} {arrow}")
                if ok:
                    changed += 1
        except Exception as e:
            print(f"  [{i:2d}/{len(pages)}] {title[:42]:<42}  ❌ 예외: {e}")
        time.sleep(1)

    print(f"\n📊 변경: {changed}/{len(pages)}건")
    return 0


if __name__ == "__main__":
    sys.exit(main())
