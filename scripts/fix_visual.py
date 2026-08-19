"""v2.6 시각 정리 — list dump / raw HTML / 빈 헤더 정리.

본문 보존 룰:
- 블록 텍스트만 업데이트 (PATCH /blocks/{id})
- 블록 삭제는 명백히 비어있거나 raw HTML만 있는 경우만
- 백업은 logs/backup_v26_{date}/{pid}.md

fix 패턴:
1. paragraph text 가 ['a','b','c'] / ["a","b"] 패턴 → 각 항목을 분리 (개행으로)
2. <summary>...</summary> / <details>...</details> 태그 제거
3. 빈 헤더 — heading 다음이 heading 이면 제거
"""
from __future__ import annotations

import argparse
import ast
import datetime
import os
import re
import sys
import time
import json
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

BACKUP_DIR = Path(__file__).resolve().parents[1] / "logs" / f"backup_v26_{datetime.date.today().isoformat()}"


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


LIST_DUMP_RE = re.compile(r"^\s*\[\s*['\"].*['\"]\s*(?:,\s*['\"].*['\"]\s*)*\]\s*$", re.DOTALL)
EMBEDDED_LIST_RE = re.compile(r"\[\s*['\"][^'\"\[\]]+['\"](?:\s*,\s*['\"][^'\"\[\]]+['\"])*\s*\]")
HTML_TAG_RE = re.compile(r"</?(?:summary|details|div|span|br|p|a|strong|em)\b[^>]*>", re.IGNORECASE)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def parse_list_dump(text: str) -> list[str] | None:
    """텍스트가 Python list literal 이면 파싱해서 항목 리스트로. 아니면 None."""
    t = text.strip()
    if not (t.startswith("[") and t.endswith("]")):
        return None
    try:
        v = ast.literal_eval(t)
        if isinstance(v, list) and all(isinstance(x, str) for x in v):
            cleaned = [x.strip() for x in v if x and x.strip()]
            return cleaned or None
    except (ValueError, SyntaxError):
        pass
    return None


LOOSE_LIST_RE = re.compile(r"\[\s*['\"][^\[\]]{5,}", re.DOTALL)


def collapse_embedded_list(text: str) -> str | None:
    """text 안에 [list] (닫힘 truncate 포함) 박혀있으면 ' · ' join 으로 풀어서 반환."""
    # 1차: strict — ast.literal_eval 가능
    m = EMBEDDED_LIST_RE.search(text)
    if m:
        try:
            items = ast.literal_eval(m.group(0))
            if isinstance(items, list):
                joined = " · ".join(re.sub(r"^[-*•]\s*", "", x).strip() for x in items if x and x.strip())
                return normalize_text(text[: m.start()] + joined + text[m.end():])
        except Exception:
            pass
    # 2차: loose — closing `]` 가 잘려도 split 으로 복구
    m = LOOSE_LIST_RE.search(text)
    if not m:
        return None
    fragment = text[m.start():]
    # 닫는 `]` 있으면 그 직전까지, 없으면 끝까지
    end = fragment.find("]")
    inner = fragment[1:end] if end >= 0 else fragment[1:]
    # `', '` / `", "` / 혼합 으로 split
    parts = re.split(r"['\"]\s*,\s*['\"]", inner)
    items = []
    for p in parts:
        p = p.strip().strip("'\"").strip()
        p = re.sub(r"^[-*•]\s*", "", p).strip()
        if p:
            items.append(p)
    if len(items) < 2:
        return None
    joined = " · ".join(items)
    tail = fragment[end + 1:] if end >= 0 else ""
    return normalize_text(text[: m.start()] + joined + tail)


def is_noise_paragraph(text: str) -> bool:
    """빈/노이즈 paragraph 판정 — '>', '<', 공백, 단일 문장부호만 등."""
    t = text.strip()
    if not t:
        return True
    if t in {">", "<", "<>", "-", "—", "---", "*"}:
        return True
    if len(t) <= 1:
        return True
    return False


def strip_html(text: str) -> str:
    """raw HTML 태그 + 주석 제거."""
    text = HTML_COMMENT_RE.sub("", text)
    return HTML_TAG_RE.sub("", text).strip()


def has_html_artifact(text: str) -> bool:
    return bool(HTML_TAG_RE.search(text) or HTML_COMMENT_RE.search(text))


def normalize_text(text: str) -> str:
    """공통 정규화 — 양쪽 공백, 연속 공백, escape backslash."""
    text = re.sub(r"\\([\*\[\]\(\)~<>\\`_])", r"\1", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def update_block_text(bid: str, btype: str, text: str) -> bool:
    """단일 블록의 rich_text 만 교체."""
    body = {btype: {"rich_text": [{"type": "text", "text": {"content": text[:1900]}}]}}
    r = requests.patch(f"{API}/blocks/{bid}", headers=H, json=body, timeout=30)
    return r.status_code == 200


def delete_block(bid: str) -> bool:
    r = requests.delete(f"{API}/blocks/{bid}", headers=H, timeout=30)
    return r.status_code == 200


def append_after(pid: str, after_id: str, new_blocks: list[dict]) -> bool:
    r = requests.patch(
        f"{API}/blocks/{pid}/children",
        headers=H,
        json={"children": new_blocks, "after": after_id},
        timeout=20,
    )
    return r.status_code == 200


def make_paragraph(text: str) -> dict:
    return {
        "object": "block", "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": text[:1900]}}]},
    }


def make_bullet(text: str) -> dict:
    return {
        "object": "block", "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text[:1900]}}]},
    }


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


def is_empty_heading(blocks: list[dict], idx: int) -> bool:
    """blocks[idx] 가 heading 이고 다음 비-divider 블록이 heading 인지."""
    if blocks[idx].get("type") not in ("heading_1", "heading_2", "heading_3"):
        return False
    for j in range(idx + 1, len(blocks)):
        t = blocks[j].get("type")
        if t == "divider":
            continue
        if t in ("heading_1", "heading_2", "heading_3"):
            return True
        return False
    return True  # 마지막이면 빈 헤더


def process_page(pid: str, title: str, apply: bool) -> str:
    blocks = get_all_blocks(pid)

    # 백업
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    (BACKUP_DIR / f"{pid}.md").write_text(f"# {title}\n\n" + blocks_to_md(blocks), encoding="utf-8")

    fixed_list = 0
    fixed_html = 0
    fixed_embedded = 0
    deleted_noise = 0
    deleted_empty_h = 0
    deleted_html = 0

    # PASS 1: paragraph / list_item / quote 의 text 정리
    for b in blocks:
        t = b.get("type")
        if t not in ("paragraph", "bulleted_list_item", "numbered_list_item", "quote"):
            continue
        text = block_text(b)

        # 노이즈 paragraph (>, <, 빈줄, 단일 부호)
        if t == "paragraph" and is_noise_paragraph(text):
            deleted_noise += 1
            if apply:
                delete_block(b["id"])
            continue

        if not text.strip():
            continue

        # 패턴 A: 통째로 list dump
        items = parse_list_dump(text)
        if items:
            fixed_list += 1
            if apply:
                first = normalize_text(re.sub(r"^[-*•]\s*", "", items[0]))
                update_block_text(b["id"], t, first)
                rest_blocks = []
                for item in items[1:]:
                    clean = normalize_text(re.sub(r"^[-*•]\s*", "", item))
                    if not clean:
                        continue
                    if re.match(r"^\d+[\)\.]\s", clean):
                        rest_blocks.append(make_paragraph(clean))
                    else:
                        rest_blocks.append(make_bullet(clean))
                for i in range(0, len(rest_blocks), 100):
                    append_after(pid, b["id"], rest_blocks[i:i+100])
                    time.sleep(0.1)
            continue

        # 패턴 A': 텍스트 안에 [list] 가 박힌 경우 (quote 의 '💡 [...]')
        collapsed = collapse_embedded_list(text)
        if collapsed and collapsed != text:
            fixed_embedded += 1
            if apply:
                update_block_text(b["id"], t, collapsed)
            continue

        # 패턴 B: raw HTML 태그 / 주석
        if has_html_artifact(text):
            cleaned = normalize_text(strip_html(text))
            # ** ** 으로 감싼 단지 ** 마커만 남으면 비어있는 것으로 취급
            stripped_check = re.sub(r"\*+", "", cleaned).strip()
            if not stripped_check:
                if apply:
                    delete_block(b["id"])
                deleted_html += 1
            elif cleaned != text:
                fixed_html += 1
                if apply:
                    update_block_text(b["id"], t, cleaned)

    # PASS 2: 다시 fetch (1차 변경 반영)
    if apply and (fixed_list or fixed_embedded or fixed_html or deleted_html or deleted_noise):
        time.sleep(0.5)
        blocks = get_all_blocks(pid)

    # PASS 2a: 거의 빈 quote (이모지/별표만 남음) 제거 + quote 중복 제거
    quote_kill = 0
    quote_seen: set[str] = set()
    for b in blocks:
        if b.get("type") != "quote":
            continue
        text = block_text(b)
        # 거의 빈: 문자/한글 알파벳 제거 후 비어있으면 노이즈
        stripped = re.sub(r"[\*\s💡⚡🎯🛠📌🏢🤖🎁]", "", text)
        if len(stripped) <= 1:
            if apply:
                delete_block(b["id"])
            quote_kill += 1
            continue
        # 중복 (정규화된 텍스트 비교)
        key = re.sub(r"\s+", " ", text.strip().lower())
        if key in quote_seen:
            if apply:
                delete_block(b["id"])
            quote_kill += 1
            continue
        quote_seen.add(key)

    # PASS 2b: 빈 헤더 제거
    if apply and quote_kill:
        time.sleep(0.5)
        blocks = get_all_blocks(pid)
    empty_h_ids: list[str] = []
    for i, b in enumerate(blocks):
        if is_empty_heading(blocks, i):
            empty_h_ids.append(b["id"])
    deleted_empty_h = len(empty_h_ids)
    if apply:
        for bid in empty_h_ids:
            delete_block(bid)
            time.sleep(0.06)

    parts = []
    if fixed_list: parts.append(f"list {fixed_list}")
    if fixed_embedded: parts.append(f"내부list {fixed_embedded}")
    if fixed_html: parts.append(f"html {fixed_html}")
    if deleted_html: parts.append(f"빈html제거 {deleted_html}")
    if deleted_noise: parts.append(f"노이즈 {deleted_noise}")
    if quote_kill: parts.append(f"빈/중복quote {quote_kill}")
    if deleted_empty_h: parts.append(f"빈헤더 {deleted_empty_h}")
    if not parts:
        return "⏭ 정상"
    prefix = "✅" if apply else "🔍[dry]"
    return f"{prefix} " + " · ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--only", type=str, default="", help="제목에 포함된 키워드만")
    args = parser.parse_args()

    pages = query_all_pages(API, H, DB_ID)
    if args.only:
        pages = [p for p in pages if args.only in "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])]
    if args.limit > 0:
        pages = pages[:args.limit]
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"📡 모드: {mode} · 대상: {len(pages)}건")
    print(f"📁 백업: {BACKUP_DIR}\n")

    for i, p in enumerate(pages, 1):
        pid = p["id"]
        title = "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])
        try:
            result = process_page(pid, title, apply=args.apply)
            print(f"  [{i:2d}/{len(pages)}] {title[:44]:<44}  {result}")
        except Exception as e:
            print(f"  [{i:2d}/{len(pages)}] {title[:44]:<44}  ❌ {e}")
        time.sleep(0.3)
    return 0


if __name__ == "__main__":
    sys.exit(main())
