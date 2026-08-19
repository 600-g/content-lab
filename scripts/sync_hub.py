"""Hub 페이지 상단 '📂 카테고리별 스킬 목록' 자동 동기화.

마스터 DB 를 카테고리별로 그룹핑해서 Hub 의 각 column heading_3 아래
bulleted_list_item + page mention 으로 재생성.

- collect.py 성공 마지막에 자동 호출 (best-effort, 실패해도 잡은 성공)
- CLI: `python -m scripts.sync_hub` 로 언제든 수동 갱신

Notion API 제약:
- column 은 자기 자식 블록만 추가/삭제 가능 (블록 이동은 불가 → delete + append 패턴)
- rich_text.mention.page 로 다른 페이지 링크 삽입 시 인티그레이션이 대상 페이지에도
  Connection 이 있어야 하지만, 같은 DB row 는 DB Connection 상속으로 자동 허용
"""
from __future__ import annotations

import logging
import os
import time
from typing import Iterable, Optional

import requests

logger = logging.getLogger(__name__)

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# DB 카테고리 (7종) → Hub column heading_3 이모지 접두
_CATEGORY_TO_HEADING_EMOJI = {
    "프롬프트": "💬",
    "자동화": "🤖",
    "콘텐츠": "🎬",
    "디자인": "🎨",
    "업무": "⚡",
    "개발": "💻",
    "기타": "📦",
}

# Hub column heading 텍스트 → DB 카테고리 매핑 (heading 안에 이모지+텍스트)
# heading_3 텍스트로 매칭 (첫 이모지 뒤 텍스트 부분에 포함되는 키워드)
_HEADING_TO_CATEGORY = {
    "프롬프트": "프롬프트",
    "에이전트": "자동화",       # "🤖 에이전트·자동화"
    "영상": "콘텐츠",           # "🎬 영상·콘텐츠"
    "콘텐츠": "콘텐츠",
    "디자인": "디자인",         # "🎨 디자인·이미지"
    "업무": "업무",             # "⚡ 업무효율"
    "코딩": "개발",             # "💻 코딩·개발"
    "개발": "개발",
    "기타": "기타",             # "📦 기타"
    # 마케팅·SNS 컬럼은 DB 카테고리 없음 → 빈 상태 유지
}

_EMPTY_PLACEHOLDER = "아직 없음"


def _headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _query_db(api_key: str, db_id: str) -> list[dict]:
    """마스터 DB 전체 페이지 조회 (created desc)."""
    rows: list[dict] = []
    start: Optional[str] = None
    while True:
        body = {
            "page_size": 100,
            "sorts": [{"timestamp": "created_time", "direction": "descending"}],
        }
        if start:
            body["start_cursor"] = start
        r = requests.post(
            f"{NOTION_API}/databases/{db_id}/query",
            headers=_headers(api_key),
            json=body,
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        rows.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        start = data.get("next_cursor")
    return rows


def _get_title(row: dict) -> str:
    for _, pv in (row.get("properties") or {}).items():
        if pv.get("type") == "title":
            return "".join(a.get("plain_text", "") for a in pv.get("title", []))
    return ""


def _get_category(row: dict) -> str:
    p = row.get("properties") or {}
    for name in ("카테고리", "category"):
        pv = p.get(name)
        if pv and pv.get("type") == "select":
            return ((pv.get("select") or {}).get("name")) or ""
    return ""


def _get_children(api_key: str, block_id: str) -> list[dict]:
    r = requests.get(
        f"{NOTION_API}/blocks/{block_id}/children?page_size=100",
        headers=_headers(api_key),
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("results", [])


def _delete_block(api_key: str, block_id: str) -> None:
    try:
        requests.delete(
            f"{NOTION_API}/blocks/{block_id}",
            headers=_headers(api_key),
            timeout=30,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("block delete 실패 %s: %s", block_id, e)


def _append_blocks(api_key: str, parent_id: str, blocks: list[dict]) -> None:
    if not blocks:
        return
    # Notion 한번에 append 100개 제한
    for i in range(0, len(blocks), 100):
        chunk = blocks[i : i + 100]
        r = requests.patch(
            f"{NOTION_API}/blocks/{parent_id}/children",
            headers=_headers(api_key),
            json={"children": chunk},
            timeout=60,
        )
        if r.status_code >= 400:
            logger.error("append 실패 %s: %s", r.status_code, r.text[:300])
        r.raise_for_status()


def _heading_text(block: dict) -> str:
    node = block.get(block["type"]) or {}
    return "".join(a.get("plain_text", "") for a in node.get("rich_text", []))


def _match_category(heading_text: str) -> Optional[str]:
    """heading_3 텍스트에서 DB 카테고리 추정."""
    for key, cat in _HEADING_TO_CATEGORY.items():
        if key in heading_text:
            return cat
    return None


def _bullet_page_mention(page_id: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "mention",
                    "mention": {"type": "page", "page": {"id": page_id}},
                }
            ]
        },
    }


def _bullet_text(text: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        },
    }


def _find_hub_columns(api_key: str, hub_page_id: str) -> list[tuple[str, str, str]]:
    """Hub 순회 → (column_id, heading_text, matched_category) 리스트.

    heading_3 을 heading 뒤 형제 블록에서 찾는 게 아니라, column 첫 자식 (heading_3)
    으로 가정.
    """
    top = _get_children(api_key, hub_page_id)
    result: list[tuple[str, str, str]] = []
    for b in top:
        if b.get("type") != "column_list":
            continue
        cols = _get_children(api_key, b["id"])
        for c in cols:
            if c.get("type") != "column":
                continue
            kids = _get_children(api_key, c["id"])
            heading_text = ""
            for h in kids:
                if h.get("type") == "heading_3":
                    heading_text = _heading_text(h)
                    break
            cat = _match_category(heading_text)
            if cat:
                result.append((c["id"], heading_text, cat))
    return result


def _clear_below_heading(api_key: str, column_id: str) -> None:
    """column 안 heading_3 아래 모든 블록 삭제 (heading_3 자체는 보존)."""
    kids = _get_children(api_key, column_id)
    saw_heading = False
    for b in kids:
        if b.get("type") == "heading_3" and not saw_heading:
            saw_heading = True
            continue
        _delete_block(api_key, b["id"])


def sync(*, limit_per_column: int = 20, dry_run: bool = False) -> dict:
    """Hub 페이지 카테고리 컬럼 재생성. 결과 딕셔너리 반환."""
    api_key = os.getenv("NOTION_API_KEY") or ""
    db_id = os.getenv("NOTION_DB_ID") or ""
    hub_id = os.getenv("NOTION_HUB_PAGE_ID") or ""
    if not (api_key and db_id and hub_id):
        return {"ok": False, "error": "NOTION_API_KEY/DB_ID/HUB_PAGE_ID 미설정"}

    # 1. DB 전체 조회 → 카테고리별 그룹핑 (최신순 유지)
    rows = _query_db(api_key, db_id)
    grouped: dict[str, list[dict]] = {}
    for r in rows:
        cat = _get_category(r) or "기타"
        grouped.setdefault(cat, []).append(
            {"id": r["id"], "title": _get_title(r)}
        )

    # 2. Hub column 매핑 스캔
    cols = _find_hub_columns(api_key, hub_id)
    plan = []
    for col_id, heading, cat in cols:
        items = grouped.get(cat, [])[:limit_per_column]
        plan.append({"col_id": col_id, "heading": heading, "category": cat, "count": len(items)})

    if dry_run:
        return {"ok": True, "dry_run": True, "plan": plan, "total_rows": len(rows)}

    # 3. 각 column: heading 아래 자식 삭제 + 새 블록 append
    for col_id, heading, cat in cols:
        items = grouped.get(cat, [])[:limit_per_column]
        _clear_below_heading(api_key, col_id)
        # Notion 이 삭제 반영에 잠깐 시간 걸림 (drift 방지)
        time.sleep(0.3)
        blocks: list[dict] = []
        if items:
            for it in items:
                blocks.append(_bullet_page_mention(it["id"]))
        else:
            blocks.append(_bullet_text(_EMPTY_PLACEHOLDER))
        _append_blocks(api_key, col_id, blocks)

    return {
        "ok": True,
        "dry_run": False,
        "plan": plan,
        "total_rows": len(rows),
    }


def main() -> None:  # pragma: no cover
    import argparse
    import json

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    parser = argparse.ArgumentParser(description="Hub 페이지 카테고리 컬럼 자동 동기화")
    parser.add_argument("--dry", action="store_true", help="변경 없이 계획만 출력")
    parser.add_argument("--limit", type=int, default=20, help="컬럼당 최대 표시 개수")
    args = parser.parse_args()

    # .env 자동 로드 (dotenv 없이)
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        for line in open(env_path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

    res = sync(limit_per_column=args.limit, dry_run=args.dry)
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
