"""Batch — 메인 페이지 본문 교체 + 원본 아카이브 DB 등록.

usage: python -m scripts.batch_apply <items_json>
items_json schema:
[{"page_id": "...", "md_path": "...", "url": "...", "slug": "...", "title_hint": "..."}]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from scripts.notion_client.page_replacer import replace_page_body
from scripts.notion_client.archive import archive_source


def main():
    if len(sys.argv) < 2:
        print("usage: python -m scripts.batch_apply <items_json>")
        sys.exit(1)
    items = json.loads(Path(sys.argv[1]).read_text())
    for i, it in enumerate(items, 1):
        slug = it["slug"]
        print(f"\n[{i}/{len(items)}] {slug}")
        md = Path(it["md_path"]).read_text(encoding="utf-8")
        # 1) 메인 페이지 교체
        try:
            ok, stats = replace_page_body(it["page_id"], md)
            print(f"  메인: {'✅' if ok else '⚠️ '} archived={stats['archived']} → appended={stats['appended']}/{stats['blocks_built']}")
        except Exception as e:
            print(f"  메인 실패: {e}")
        # 2) 원본 아카이브
        try:
            arch = archive_source(it["url"], slug, it.get("title_hint", ""))
            if arch.get("ok"):
                print(f"  아카이브: ✅ {arch['char_count']:,}자 / {arch['kind']} / {arch['src_type']}")
            else:
                print(f"  아카이브: ⚠️  {arch.get('error', '')[:120]}")
        except Exception as e:
            print(f"  아카이브 실패: {e}")
        time.sleep(0.5)


if __name__ == "__main__":
    main()
