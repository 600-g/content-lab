"""스킬 자동 큐레이션 — 등록 후 후처리.

v2 (2026-05-15): "관련 스킬" relation property 제거됨 (DB 슬림화).
→ curate_after_register는 no-op으로 유지 (호출부 호환).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..analyzer.gemini import AnalysisResult

logger = logging.getLogger(__name__)


def curate_after_register(page_id: str, result: "AnalysisResult") -> dict:
    """v2: 관련 스킬 property 제거됐으므로 no-op.

    향후 다른 큐레이션 후처리(허브 페이지 자동 추가 등) 추가 시 여기에 구현.
    """
    return {"related_linked": 0, "hub_updated": False, "note": "v2: relation 제거됨"}
