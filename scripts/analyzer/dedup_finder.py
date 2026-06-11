"""의미 임베딩 기반 dedup 후보 검색.

새 스킬의 callout + ai_tools + category 를 concat → embed → 캐시된 모든 스킬과
코사인. threshold 이상 후보 top_k 를 반환.

callout 이 없거나 embedder 가 None 반환하면 빈 결과 → 안전 폴백.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, Optional

from scripts import config_store
from scripts.analyzer import embedder

logger = logging.getLogger(__name__)


@dataclass
class DedupCandidate:
    slug: str
    score: float


def _component_text(analysis_like: dict | object, components: Iterable[str]) -> str:
    """callout + ai_tools + category 같은 필드를 concat. analysis_like 는 dict 또는 AnalysisResult."""
    parts: list[str] = []
    for c in components:
        val = None
        if isinstance(analysis_like, dict):
            val = analysis_like.get(c)
        else:
            val = getattr(analysis_like, c, None)
        if val is None:
            continue
        if isinstance(val, list):
            parts.append(" ".join(str(x) for x in val))
        else:
            parts.append(str(val))
    return "\n".join(p.strip() for p in parts if p.strip())


def find_semantic_candidates(
    analysis_like: dict | object,
    *,
    exclude_slug: Optional[str] = None,
) -> list[DedupCandidate]:
    """새 스킬과 의미상 가까운 기존 스킬 후보 top_k 반환.

    Args:
        analysis_like: AnalysisResult 또는 그에 상응하는 dict (callout/ai_tools/category 필드 보유).
        exclude_slug: 결과에서 제외할 슬러그 (자기 자신 합병 방지).

    Returns:
        threshold 이상 후보 score 내림차순. 빈 리스트면 합병 없음.
    """
    if not config_store.get("dedup.enabled", True):
        return []
    threshold = float(config_store.get("dedup.threshold", 0.80))
    top_k = int(config_store.get("dedup.top_k", 3))
    components = config_store.get("dedup.components", ["callout", "ai_tools", "category"])

    text = _component_text(analysis_like, components)
    if not text:
        return []
    new_vec = embedder.embed(text)
    if new_vec is None:
        logger.info("new vec 임베딩 실패 → dedup 스킵 (신규로 등록)")
        return []

    candidates: list[DedupCandidate] = []
    for slug, entry in embedder.all_cached().items():
        if exclude_slug and slug == exclude_slug:
            continue
        vec = entry.get("vec")
        if not vec:
            continue
        score = embedder.cosine(new_vec, vec)
        if score >= threshold:
            candidates.append(DedupCandidate(slug=slug, score=score))

    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates[:top_k]
