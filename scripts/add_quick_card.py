"""기존 페이지에 ⚡ 30초 핵심 카드를 메타 callout 다음에 자동 추가.

추출 로직 (LLM 없이):
- 무엇 (TL;DR): 첫 quote 블록 (메타 callout 의 첫 줄 ** 사이 추출)
  또는 properties 의 핵심 요약 / 첫 paragraph
- 언제: ## 🎯 언제 쓰나 섹션 첫 bullet
- 시작: ## 🛠 단계 섹션 첫 번호/bullet
- 두근 적용: 적용 대상 property
"""
from __future__ import annotations

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

QUICK_MARKER = "⚡ 30초 핵심"


def get_blocks(pid: str) -> list[dict]:
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


def block_text(b: dict) -> str:
    t = b.get("type", "?")
    rt = b.get(t, {}).get("rich_text", [])
    return "".join(r.get("plain_text", "") for r in rt).strip()


def already_has_card(blocks: list[dict]) -> bool:
    for b in blocks[:10]:
        if QUICK_MARKER in block_text(b):
            return True
    return False


def find_first_meta_quote(blocks: list[dict]) -> str | None:
    """첫 메타 callout (quote 블록) ID 반환."""
    for b in blocks[:6]:
        if b.get("type") == "quote":
            return b["id"]
    return None


def extract_tldr(blocks: list[dict]) -> str:
    """TL;DR 추출 — 메타 callout 첫 줄의 '💡 ...' 또는 첫 paragraph."""
    for b in blocks[:8]:
        text = block_text(b)
        # > **💡 ...** 패턴
        m = re.search(r"💡\s*\*?\*?([^*\n]{10,160})\*?\*?", text)
        if m:
            return m.group(1).strip()
    # 폴백: 첫 paragraph
    for b in blocks:
        if b.get("type") == "paragraph":
            t = block_text(b)
            if len(t) > 30:
                return t[:130]
    return ""


def extract_when(blocks: list[dict]) -> str:
    """## 🎯 언제 쓰나 섹션 첫 bullet 추출."""
    in_when = False
    for b in blocks:
        text = block_text(b)
        t = b.get("type")
        if t == "heading_2" and "언제" in text:
            in_when = True
            continue
        if t == "heading_2" and in_when:
            break  # 다음 섹션
        if in_when and t == "bulleted_list_item":
            return text[:90]
        if in_when and t == "paragraph" and text:
            cleaned = re.sub(r"^[-*•]\s*", "", text)
            if cleaned:
                return cleaned[:90]
    return ""


def extract_first_step(blocks: list[dict]) -> str:
    """## 🛠 단계 섹션 첫 번호/bullet."""
    in_steps = False
    for b in blocks:
        text = block_text(b)
        t = b.get("type")
        if t == "heading_2" and "단계" in text:
            in_steps = True
            continue
        if t == "heading_2" and in_steps:
            break
        if in_steps and t in ("numbered_list_item", "bulleted_list_item"):
            return text[:90]
    return ""


def make_quick_card(tldr: str, when: str, step: str, targets: list[str]) -> list[dict]:
    """30초 핵심 카드를 Notion quote 블록 여러 개로 분할 (Notion quote는 1줄 1블록)."""
    targets_str = " · ".join(targets[:4]) if targets else "공통"
    lines = [
        f"⚡ 30초 핵심",
    ]
    if tldr:
        lines.append(f"🎯 무엇 — {tldr[:130]}")
    if when:
        lines.append(f"⏰ 언제 — {when}")
    if step:
        lines.append(f"🛠 시작 — {step}")
    lines.append(f"🏢 두근 적용 — {targets_str}")

    blocks = []
    for line in lines:
        blocks.append({
            "object": "block", "type": "quote",
            "quote": {"rich_text": [{"type": "text", "text": {"content": line}}]},
        })
    return blocks


def process_page(pid: str, title: str, targets: list[str]) -> str:
    blocks = get_blocks(pid)
    if already_has_card(blocks):
        return "이미 있음"
    after_id = find_first_meta_quote(blocks)
    if not after_id:
        return "메타 callout 못 찾음"

    tldr = extract_tldr(blocks)
    when = extract_when(blocks)
    step = extract_first_step(blocks)
    card = make_quick_card(tldr, when, step, targets)

    r = requests.patch(
        f"{API}/blocks/{pid}/children",
        headers=H,
        json={"children": card, "after": after_id},
        timeout=20,
    )
    if r.status_code == 200:
        return f"✅ {len(card)}블록 추가"
    return f"❌ {r.status_code} {r.text[:80]}"


def main() -> int:
    pages = query_all_pages(API, H, DB_ID)
    print(f"📡 {len(pages)}건 처리\n")
    for i, p in enumerate(pages, 1):
        pid = p["id"]
        title = "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])
        targets = [t["name"] for t in p["properties"].get("적용 대상", {}).get("multi_select", [])]
        result = process_page(pid, title, targets)
        print(f"  [{i:2d}/{len(pages)}] {title[:48]:<48} — {result}")
        time.sleep(0.3)
    return 0


if __name__ == "__main__":
    sys.exit(main())
