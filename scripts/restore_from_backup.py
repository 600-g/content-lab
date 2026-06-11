"""백업 raw_blocks 를 그대로 페이지에 복구.

logs/backup_v27_2026-05-15/{pid_full}__*.json 의 raw_blocks 사용.
현재 페이지 children 모두 삭제 → 원본 blocks 그대로 append.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API = "https://api.notion.com/v1"
H = {
    "Authorization": f"Bearer {os.environ['NOTION_API_KEY']}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
DB_ID = os.environ["NOTION_DB_ID"]
BACKUP_DIR = Path(__file__).resolve().parents[1] / "logs" / "backup_v27_2026-05-15"


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


def _strip_nulls(obj):
    """재귀적으로 None 값 키 제거 (Notion API write 는 null 안 받음)."""
    if isinstance(obj, dict):
        return {k: _strip_nulls(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_nulls(x) for x in obj]
    return obj


def block_to_payload(b: dict) -> dict | None:
    """저장된 raw block → POST children API 용 payload.

    Notion API 의 read 와 write 형식 차이:
    - read 응답에는 id, created_time, last_edited_time, has_children, archived 등 메타 필드 있음
    - write 는 type + 내용 필드만 받음
    - null 값 모두 제거 필요
    """
    t = b.get("type")
    if t in ("child_page", "child_database", "table", "table_row", "synced_block",
             "link_to_page", "column_list", "column", "breadcrumb", "embed",
             "file", "image", "video", "audio", "pdf", "bookmark"):
        return None
    body = b.get(t, {})
    payload = {"object": "block", "type": t, t: _strip_nulls(body)}
    # rich_text 의 annotations 도 null 제거됨 (위 _strip_nulls 가 처리)
    return payload


def restore(pid: str, raw_blocks: list[dict], apply: bool) -> str:
    new_payloads = [b for b in (block_to_payload(b) for b in raw_blocks) if b]
    if not new_payloads:
        return "⏭ 복구할 블록 없음"

    if not apply:
        return f"🔍[dry] {len(new_payloads)}블록 복구 예정"

    # 현재 블록 모두 삭제
    current = get_all_blocks(pid)
    deleted = 0
    for b in current:
        try:
            r = requests.delete(f"{API}/blocks/{b['id']}", headers=H, timeout=30)
            if r.status_code == 200:
                deleted += 1
            time.sleep(0.06)
        except Exception:
            pass

    # 백업 blocks append
    added = 0
    for i in range(0, len(new_payloads), 100):
        chunk = new_payloads[i:i+100]
        r = requests.patch(f"{API}/blocks/{pid}/children", headers=H,
                           json={"children": chunk}, timeout=60)
        if r.status_code == 200:
            added += len(chunk)
        else:
            return f"⚠️ append 실패 {r.status_code}: {r.text[:120]}"
        time.sleep(0.2)

    return f"✅ 삭제 {deleted} → 복구 {added}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("targets", nargs="+", help="제목 키워드 (여러 개 가능)")
    args = parser.parse_args()

    r = requests.post(f"{API}/databases/{DB_ID}/query", headers=H, json={"page_size": 50}).json()
    pages = r.get("results", [])

    selected = []
    for keyword in args.targets:
        for p in pages:
            title = "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])
            if keyword in title and p not in selected:
                selected.append(p)
                break

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"📡 모드: {mode} · 대상: {len(selected)}건\n")

    for p in selected:
        pid = p["id"]
        title = "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])
        backup_file = next(BACKUP_DIR.glob(f"{pid.replace('-','')}__*.json"), None)
        if not backup_file:
            print(f"  ❌ {title[:46]:<46}  백업 없음")
            continue
        data = json.loads(backup_file.read_text(encoding="utf-8"))
        raw_blocks = data.get("raw_blocks", [])
        try:
            result = restore(pid, raw_blocks, args.apply)
            print(f"  {title[:46]:<46}  {result}")
        except Exception as e:
            print(f"  ❌ {title[:46]:<46}  {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
