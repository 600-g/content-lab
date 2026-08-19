"""Notion DB 전체 row 조회 — 커서 페이지네이션 단일 구현.

왜 따로 두는가: DB 정리/감사 스크립트 13개가 각자
`requests.post(.../query, json={"page_size": 50})` 단발 호출을 복붙해 쓰고 있었다.
`page_size` 는 '한 번에 최대 몇 건'이지 '전부'가 아니라서, DB 가 50건을 넘는 순간
**뒤쪽 row 가 조용히 빠진 채로 "전수 처리 완료" 라고 출력**됐다.

2026-08-16 발견 시점 기준 DB 69건 중 19건이 모든 일괄 작업(백업/감사/재작성/재분류/
헤더 정리/복원)에서 누락돼 있었다. 오류도 경고도 없이 조용히 빠지는 종류라
새 DB 스크립트는 반드시 이 헬퍼를 쓴다.
"""
from __future__ import annotations

from typing import Any, Optional

import requests

NOTION_PAGE_SIZE_MAX = 100


def query_all_pages(
    api: str,
    headers: dict,
    db_id: str,
    *,
    extra_body: Optional[dict] = None,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """DB 의 모든 row 를 has_more/next_cursor 를 따라 끝까지 조회.

    Args:
        api: Notion API base (예: "https://api.notion.com/v1")
        headers: Authorization/Notion-Version 포함 헤더
        db_id: 대상 database id
        extra_body: filter/sorts 같은 추가 쿼리 바디 (page_size/start_cursor 는 덮어씀)

    Raises:
        RuntimeError: 응답에 results 가 없을 때 (권한 오류 등을 조용히 넘기지 않기 위함)
    """
    pages: list[dict[str, Any]] = []
    cursor: Optional[str] = None
    while True:
        body: dict[str, Any] = dict(extra_body or {})
        body["page_size"] = NOTION_PAGE_SIZE_MAX
        if cursor:
            body["start_cursor"] = cursor
        d = requests.post(
            f"{api}/databases/{db_id}/query", headers=headers, json=body, timeout=timeout
        ).json()
        if "results" not in d:
            raise RuntimeError(f"Notion DB 조회 실패: {d.get('message') or d}")
        pages.extend(d["results"])
        if not d.get("has_more"):
            return pages
        cursor = d.get("next_cursor")
