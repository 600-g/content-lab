"""하이브리드 검색 — 키워드(BM25, 필드 가중) + 의미(코사인, 기존 임베딩 캐시) + RRF 융합.

외부 의존 0. 의미 검색은 embed_fn/vectors 를 주입받으며, 기본값은 scripts.analyzer.embedder
(Gemini) 와 scripts/skills/embeddings.json — 둘 다 실패하면 조용히 키워드만 반환하되
응답의 semantic_used 로 드러낸다. 예외를 밖으로 내보내지 않는다.
"""
from __future__ import annotations

import functools
import json
import logging
import math
import re
import threading
import time
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable, Optional

from scripts.library.index import (
    CATEGORY_ORDER,
    GRADE_ORDER,
    LibraryIndex,
    SkillRecord,
    get_index,
)

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VECTORS_PATH = PROJECT_ROOT / "scripts" / "skills" / "embeddings.json"

MIN_QUERY_CHARS = 2
MAX_QUERY_CHARS = 300
DEFAULT_K = 8
MAX_K = 50
RRF_K = 60
BM25_K1 = 1.5
BM25_B = 0.75
FIELD_WEIGHTS = {"title": 3.0, "description": 2.0, "meta": 1.5, "body": 1.0}
TITLE_SUBSTRING_BONUS = 0.5  # × (질의 idf 합)
SEM_CANDIDATES_MIN = 10
KW_CANDIDATES_MAX = 50
SNIPPET_LEN = 160

_TOKEN_RE = re.compile(r"[0-9a-z]+|[가-힣]+")
_MD_NOISE_RE = re.compile(r"[#>*`_\[\]()|\-]+")

EmbedFn = Callable[[str], Optional[list[float]]]


# ── 토크나이저 ───────────────────────────────────────────────────

def tokenize(text: str) -> list[str]:
    """소문자 → 영숫자/한글 런 분리. 한글 런(3자+)은 2-gram 추가 (조사/어미 변형 흡수).

    영문은 단어 그대로만 (prefix 확장 안 함 — 과매칭 방지).
    """
    if not text:
        return []
    out: list[str] = []
    for tok in _TOKEN_RE.findall(text.lower()):
        out.append(tok)
        if "가" <= tok[0] <= "힣" and len(tok) >= 3:
            out.extend(tok[i:i + 2] for i in range(len(tok) - 1))
    return out


# ── BM25 ─────────────────────────────────────────────────────────

class _FieldStats:
    __slots__ = ("tfs", "lens", "avg")

    def __init__(self) -> None:
        self.tfs: list[Counter[str]] = []
        self.lens: list[int] = []
        self.avg: float = 1.0


class KeywordScorer:
    """인덱스 1버전에 대한 BM25 스코어러 (필드별 가중). 인덱스 버전이 바뀌면 새로 만든다."""

    def __init__(self, index: LibraryIndex) -> None:
        self.version = index.version
        self.records = index.records
        self.fields: dict[str, _FieldStats] = {f: _FieldStats() for f in FIELD_WEIGHTS}
        df: Counter[str] = Counter()
        for r in self.records:
            texts = {
                "title": r.title + " " + r.slug.replace("-", " "),
                "description": r.description,
                "meta": " ".join(r.ai_tools) + " " + r.category + " " + r.difficulty,
                "body": r.body_md,
            }
            seen: set[str] = set()
            for f, text in texts.items():
                toks = tokenize(text)
                st = self.fields[f]
                st.tfs.append(Counter(toks))
                st.lens.append(len(toks))
                seen.update(toks)
            df.update(seen)
        n = max(1, len(self.records))
        for st in self.fields.values():
            st.avg = (sum(st.lens) / len(st.lens)) if st.lens else 1.0
        self.idf = {t: math.log(1.0 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def rank(self, query: str) -> list[tuple[str, float]]:
        q_tokens = [t for t in tokenize(query) if t in self.idf]
        if not q_tokens:
            return []
        q_norm = query.strip().lower().replace(" ", "")
        idf_sum = sum(self.idf[t] for t in set(q_tokens))
        scored: list[tuple[str, float]] = []
        for i, r in enumerate(self.records):
            score = 0.0
            for f, w in FIELD_WEIGHTS.items():
                st = self.fields[f]
                tf_map = st.tfs[i]
                if not tf_map:
                    continue
                dl = st.lens[i]
                norm = BM25_K1 * (1 - BM25_B + BM25_B * dl / (st.avg or 1.0))
                s = 0.0
                for t in q_tokens:
                    tf = tf_map.get(t)
                    if not tf:
                        continue
                    s += self.idf[t] * tf * (BM25_K1 + 1) / (tf + norm)
                score += w * s
            if score <= 0:
                continue
            if q_norm and len(q_norm) >= 2 and q_norm in r.title.lower().replace(" ", ""):
                score += TITLE_SUBSTRING_BONUS * idf_sum
            scored.append((r.slug, score))
        scored.sort(key=lambda x: (-x[1], x[0]))
        return scored[:KW_CANDIDATES_MAX]


_SCORER_LOCK = threading.Lock()
_SCORER: Optional[KeywordScorer] = None


def _scorer_for(index: LibraryIndex) -> KeywordScorer:
    global _SCORER
    with _SCORER_LOCK:
        if _SCORER is None or _SCORER.version != index.version or _SCORER.records is not index.records:
            _SCORER = KeywordScorer(index)
        return _SCORER


def keyword_rank(query: str, index: LibraryIndex) -> list[tuple[str, float]]:
    return _scorer_for(index).rank(query)


# ── 의미 검색 ────────────────────────────────────────────────────

_VEC_CACHE: dict = {"path": None, "mtime": 0.0, "vectors": {}}
_VEC_LOCK = threading.Lock()


def load_vectors(path: Path | str | None = None) -> dict[str, list[float]]:
    """embeddings.json → {slug: vec}. mtime 캐시. 실패 시 {}."""
    p = Path(path) if path else DEFAULT_VECTORS_PATH
    try:
        mtime = p.stat().st_mtime
    except OSError:
        return {}
    with _VEC_LOCK:
        if _VEC_CACHE["path"] == str(p) and _VEC_CACHE["mtime"] == mtime:
            return _VEC_CACHE["vectors"]
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            vectors = {
                slug: item["vec"]
                for slug, item in data.items()
                if isinstance(item, dict) and isinstance(item.get("vec"), list) and item["vec"]
            }
        except Exception as e:  # noqa: BLE001
            logger.warning("embeddings.json 로드 실패 — 의미 검색 비활성: %s", e)
            vectors = {}
        _VEC_CACHE.update({"path": str(p), "mtime": mtime, "vectors": vectors})
        return vectors


@functools.lru_cache(maxsize=128)
def _embed_query_cached(query: str) -> Optional[tuple[float, ...]]:
    try:
        from scripts.analyzer import embedder  # 지연 import — requests 의존
        vec = embedder.embed(query)
        return tuple(vec) if vec else None
    except Exception as e:  # noqa: BLE001
        logger.warning("질의 임베딩 실패 — 키워드만: %s", e)
        return None


def default_embed(query: str) -> Optional[list[float]]:
    vec = _embed_query_cached(query)
    return list(vec) if vec else None


def _cosine(a: Iterable[float], b: Iterable[float]) -> float:
    dot = na = nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / math.sqrt(na * nb)


_DIM_WARNED: set[tuple[int, int]] = set()


def semantic_rank(
    query_vec: list[float], vectors: dict[str, list[float]], *, limit: int,
) -> list[tuple[str, float]]:
    scored: list[tuple[str, float]] = []
    qdim = len(query_vec)
    for slug, vec in vectors.items():
        if len(vec) != qdim:
            key = (qdim, len(vec))
            if key not in _DIM_WARNED:
                _DIM_WARNED.add(key)
                logger.warning("임베딩 차원 불일치 (질의 %d vs 캐시 %d) — 해당 항목 무시", qdim, len(vec))
            continue
        scored.append((slug, _cosine(query_vec, vec)))
    scored.sort(key=lambda x: (-x[1], x[0]))
    return scored[:limit]


# ── 융합 ─────────────────────────────────────────────────────────

def rrf_fuse(rank_lists: dict[str, list[tuple[str, float]]], k: int = RRF_K) -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion. 점수 스케일 무관. 결과는 (slug, fused_score) 내림차순."""
    fused: dict[str, float] = {}
    for ranked in rank_lists.values():
        for rank, (slug, _score) in enumerate(ranked, start=1):
            fused[slug] = fused.get(slug, 0.0) + 1.0 / (k + rank)
    return sorted(fused.items(), key=lambda x: (-x[1], x[0]))


# ── 스니펫 ───────────────────────────────────────────────────────

def make_snippet(record: SkillRecord, query: str) -> str:
    """질의 토큰이 들어간 줄 우선, 없으면 본문 첫 문장. 마크다운 기호 제거."""
    q_tokens = [t for t in tokenize(query) if len(t) >= 2]
    lines = [ln.strip() for ln in record.body_md.splitlines()]
    candidates = [ln for ln in lines if ln and not ln.startswith("#") and not ln.startswith("💡")
                  and not ln.startswith("```") and not ln.startswith("- [http")]
    pick = ""
    for ln in candidates:
        low = ln.lower()
        if any(t in low for t in q_tokens):
            pick = ln
            break
    if not pick:
        pick = candidates[0] if candidates else record.description
    clean = _MD_NOISE_RE.sub(" ", pick)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:SNIPPET_LEN] + ("…" if len(clean) > SNIPPET_LEN else "")


# ── 공개 API ─────────────────────────────────────────────────────

def _validate(query: str, k: int, category: str | None, grade: str | None) -> tuple[str, int, str | None, str | None, str | None]:
    q = (query or "").strip()
    if len(q) < MIN_QUERY_CHARS:
        return q, k, category, grade, f"검색어는 {MIN_QUERY_CHARS}자 이상이어야 합니다"
    if len(q) > MAX_QUERY_CHARS:
        return q, k, category, grade, f"검색어는 {MAX_QUERY_CHARS}자 이하여야 합니다"
    try:
        k = int(k)
    except (TypeError, ValueError):
        k = DEFAULT_K
    k = max(1, min(MAX_K, k))
    category = category if category in CATEGORY_ORDER else None
    grade = grade.upper() if isinstance(grade, str) and grade.upper() in GRADE_ORDER else None
    return q, k, category, grade, None


def search(
    query: str,
    *,
    k: int = DEFAULT_K,
    category: str | None = None,
    grade: str | None = None,
    mode: str = "hybrid",
    index: LibraryIndex | None = None,
    embed_fn: EmbedFn | None = None,
    vectors: dict[str, list[float]] | None = None,
) -> dict:
    """하이브리드 검색. 항상 dict envelope 반환 (ok/error)."""
    t0 = time.time()
    q, k, category, grade, err = _validate(query, k, category, grade)
    if err:
        return {"ok": False, "error": err, "query": q, "results": []}
    idx = index or get_index()
    mode = "keyword" if mode == "keyword" else "hybrid"

    kw = keyword_rank(q, idx)
    rank_lists: dict[str, list[tuple[str, float]]] = {"kw": kw}
    semantic_used = False
    # 의미 검색이 왜 빠졌는지 응답에 남긴다. 예전엔 semantic_used=False 뿐이라
    # '키가 없어서' 인지 '캐시가 비어서' 인지 구분이 안 됐고, .env 미로딩으로 CLI 가
    # 조용히 키워드 전용으로 강등된 걸 아무도 못 알아챘다.
    semantic_skip_reason: Optional[str] = None
    sem: list[tuple[str, float]] = []
    if mode == "hybrid":
        vecs = vectors if vectors is not None else load_vectors()
        if not vecs:
            semantic_skip_reason = "임베딩 캐시가 비어 있음 (scripts/skills/embeddings.json)"
        else:
            fn = embed_fn or default_embed
            qvec: Optional[list[float]] = None
            try:
                qvec = fn(q)
            except Exception as e:  # noqa: BLE001
                logger.warning("embed_fn 예외 — 키워드만: %s", e)
                semantic_skip_reason = f"질의 임베딩 예외: {e}"
            if qvec:
                sem = semantic_rank(qvec, vecs, limit=max(SEM_CANDIDATES_MIN, 3 * k))
                if sem:
                    semantic_used = True
                    rank_lists["sem"] = sem
                else:
                    semantic_skip_reason = "임베딩된 후보가 없음"
            elif semantic_skip_reason is None:
                semantic_skip_reason = (
                    "질의 임베딩 실패 — GEMINI_API_KEY 미설정이거나 임베딩 API 호출 불가"
                )
    else:
        semantic_skip_reason = "mode=keyword (요청)"

    fused = rrf_fuse(rank_lists)
    kw_rank = {slug: i for i, (slug, _) in enumerate(kw, start=1)}
    sem_rank = {slug: i for i, (slug, _) in enumerate(sem, start=1)}
    sem_score = dict(sem)

    results = []
    for slug, score in fused:
        rec = idx.get(slug)
        if rec is None:
            continue  # 캐시에만 있고 mirror 에서 사라진 슬러그
        if category and rec.category != category:
            continue
        if grade and rec.grade != grade:
            continue
        item = rec.meta()
        item.update({
            "score": round(score, 6),
            "kw_rank": kw_rank.get(slug),
            "sem_rank": sem_rank.get(slug),
            "sem_score": round(sem_score[slug], 4) if slug in sem_score else None,
            "snippet": make_snippet(rec, q),
            "detail_url": f"/api/library/skills/{slug}",   # AI — SKILL.md 본문 (JSON/raw)
            "page_url": f"/skill/{slug}",                  # 사람 — 게시글 상세
            "catalog_url": f"/catalog#{slug}",             # 구버전 링크 호환
        })
        results.append(item)
        if len(results) >= k:
            break

    return {
        "ok": True,
        "query": q,
        "mode": mode,
        "semantic_used": semantic_used,
        "semantic_skip_reason": semantic_skip_reason,
        "total_indexed": len(idx.records),
        "index_version": idx.version,
        "took_ms": int((time.time() - t0) * 1000),
        "results": results,
    }
