"""노션 페이지 본문 안전 교체 — children archive + 새 블록 append.

aiskillbox 25건 수동 재처리에 사용.
- 기존 register._markdown_to_blocks() 재사용 (callout 변환 포함)
- 페이지 children 전수 archive (delete) → 새 블록 append
- 검증: 교체 후 children 재조회로 확인
"""
from __future__ import annotations

import os
import time
import requests
from typing import Tuple

from .register import _markdown_to_blocks, _headers, NOTION_API


def fetch_children(page_id: str) -> list[dict]:
    """페이지의 직속 children 전수 조회 (paginated)."""
    out, cursor = [], None
    while True:
        url = f"{NOTION_API}/blocks/{page_id}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        r = requests.get(url, headers=_headers(), timeout=15).json()
        out.extend(r.get("results", []))
        if not r.get("has_more"):
            break
        cursor = r.get("next_cursor")
    return out


def archive_children(page_id: str) -> int:
    """기존 children 전수 archive (block delete). 반환: 처리 개수."""
    children = fetch_children(page_id)
    archived = 0
    for b in children:
        bid = b.get("id")
        if not bid:
            continue
        try:
            r = requests.delete(f"{NOTION_API}/blocks/{bid}", headers=_headers(), timeout=10)
            if r.status_code in (200, 201):
                archived += 1
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.18)  # 노션 rate limit 안전 대비
    return archived


def append_blocks(page_id: str, blocks: list[dict], chunk: int = 90) -> int:
    """블록 리스트를 100개씩 분할 append (notion API 제한)."""
    appended = 0
    for i in range(0, len(blocks), chunk):
        part = blocks[i:i + chunk]
        r = requests.patch(
            f"{NOTION_API}/blocks/{page_id}/children",
            headers=_headers(),
            json={"children": part},
            timeout=20,
        )
        if r.status_code in (200, 201):
            appended += len(part)
        else:
            print(f"⚠️ append 실패 {r.status_code}: {r.text[:200]}")
            break
        time.sleep(0.3)
    return appended


def replace_page_body(page_id: str, markdown: str) -> Tuple[bool, dict]:
    """페이지 본문 전체 교체. (성공여부, stats)."""
    # 1) 기존 children archive
    archived = archive_children(page_id)
    # 2) markdown → notion blocks (register._markdown_to_blocks 재사용)
    blocks = _markdown_to_blocks(markdown)
    # 3) 새 블록 append
    appended = append_blocks(page_id, blocks)
    # 4) 검증
    after = fetch_children(page_id)
    return (appended == len(blocks), {
        "archived": archived,
        "blocks_built": len(blocks),
        "appended": appended,
        "after_count": len(after),
    })


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("사용: python -m scripts.notion_client.page_replacer <page_id> <markdown_file>")
        sys.exit(1)
    page_id, md_path = sys.argv[1], sys.argv[2]
    md = open(md_path, encoding="utf-8").read()
    ok, stats = replace_page_body(page_id, md)
    print(("✅ " if ok else "⚠️ ") + str(stats))
