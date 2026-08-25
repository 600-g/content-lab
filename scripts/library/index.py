"""SKILL.md 인덱스 — skills/*/SKILL.md 를 읽어 불변 레코드로 보관.

- 외부 의존 0 (표준 라이브러리만). MCP 서버 로컬 폴백 경로에서도 import 가능해야 한다.
- frontmatter 파서는 md_generator.render_skill_md 가 쓰는 형태(key: value / 리스트 / 인라인 배열)만 지원.
- 파일 1건이 깨져도 전체 실패 금지 — 경고 로그 + 해당 파일 제외.
- get_index() 는 2초 스로틀 + (파일 수, 최대 mtime) 변경 시만 재빌드.
"""
from __future__ import annotations

import collections
import logging
import os
import re
import threading
import time
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIRROR_DIR = PROJECT_ROOT / "skills"

# TEMPLATE.md / prompt.py CATEGORIES 와 같은 순서 (카탈로그 섹션 순서에도 사용)
CATEGORY_ORDER: tuple[str, ...] = ("프롬프트", "자동화", "콘텐츠", "디자인", "개발", "업무", "기타")
GRADE_ORDER: tuple[str, ...] = ("S", "A", "B", "C")
DEFAULT_CATEGORY = "기타"

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._\-]*$")
# scripts/chat/tools.py:_redact_secrets 와 같은 패턴 — 라이브러리는 공개 API 로 본문을 내보내므로
# 인덱스 단계에서 한 번 거른다 (API/카탈로그/MCP 모두 같은 레코드를 쓴다).
_SECRET_RE = re.compile(
    r"(AIza[0-9A-Za-z_\-]{20,}|sk-[A-Za-z0-9_\-]{16,}|key=[0-9A-Za-z_\-]{16,}"
    r"|secret_[0-9A-Za-z]{16,}|ntn_[0-9A-Za-z]{16,})"
)


def redact_secrets(text: str) -> str:
    return _SECRET_RE.sub("[REDACTED]", text or "")
_FM_RE = re.compile(r"^---\n(.*?)\n---\n?", re.S)
_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.M)
_CALLOUT_RE = re.compile(r"^💡\s*(.+?)\s*$", re.M)

REBUILD_THROTTLE_SEC = 2.0


@dataclass(frozen=True)
class SkillRecord:
    slug: str
    title: str
    description: str
    category: str
    grade: str
    difficulty: str
    ai_tools: tuple[str, ...]
    sources: tuple[str, ...]
    source_types: tuple[str, ...]
    body_md: str      # frontmatter 제거한 본문 (H1 포함)
    raw_md: str       # 파일 전문 (frontmatter 포함) — "SKILL.md 복사" 용
    path: str
    mtime: float

    @property
    def updated_date(self) -> str:
        return time.strftime("%Y-%m-%d", time.localtime(self.mtime))

    def meta(self) -> dict:
        """API/카탈로그 공용 메타 dict (본문 제외)."""
        return {
            "slug": self.slug,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "grade": self.grade,
            "difficulty": self.difficulty,
            "ai_tools": list(self.ai_tools),
            "sources": list(self.sources),
            "source_types": list(self.source_types),
            "updated": self.updated_date,
        }


@dataclass(frozen=True)
class LibraryIndex:
    records: tuple[SkillRecord, ...]
    version: str
    root: str
    built_at: float

    def get(self, slug: str) -> Optional[SkillRecord]:
        for r in self.records:
            if r.slug == slug:
                return r
        return None

    def filter(self, *, category: str | None = None, grade: str | None = None) -> list[SkillRecord]:
        out = []
        for r in self.records:
            if category and r.category != category:
                continue
            if grade and r.grade != grade:
                continue
            out.append(r)
        return out

    def stats(self) -> dict:
        by_cat: dict[str, int] = collections.OrderedDict((c, 0) for c in CATEGORY_ORDER)
        by_grade: dict[str, int] = collections.OrderedDict((g, 0) for g in GRADE_ORDER)
        tools: collections.Counter[str] = collections.Counter()
        latest = 0.0
        for r in self.records:
            by_cat[r.category] = by_cat.get(r.category, 0) + 1
            if r.grade:
                by_grade[r.grade] = by_grade.get(r.grade, 0) + 1
            tools.update(r.ai_tools)
            latest = max(latest, r.mtime)
        return {
            "total": len(self.records),
            "by_category": dict(by_cat),
            "by_grade": dict(by_grade),
            "top_tools": tools.most_common(12),
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(latest)) if latest else "",
            "version": self.version,
        }


# ── frontmatter 파서 ─────────────────────────────────────────────

_INLINE_ITEM_RE = re.compile(r'\s*(?:"([^"]*)"|\'([^\']*)\'|([^,\[\]]+))')


def _parse_inline_list(value: str) -> list[str]:
    """`["a", "b"]` / `[a, b]` → ["a","b"]. 따옴표 안 쉼표(`"LLM (Claude Max, Gemini 등)"`)는 분리 안 함."""
    inner = value.strip()[1:-1]
    items = []
    for m in _INLINE_ITEM_RE.finditer(inner):
        p = (m.group(1) if m.group(1) is not None else m.group(2) if m.group(2) is not None else m.group(3) or "").strip()
        if p:
            items.append(p)
    return items


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """(meta, body). frontmatter 없으면 ({}, text)."""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    meta: dict = {}
    current_list: str | None = None
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") or line.startswith("- "):
            if current_list is not None:
                meta.setdefault(current_list, []).append(line.split("- ", 1)[1].strip())
            continue
        if ":" not in line or line.startswith(" "):
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            current_list = key
            meta.setdefault(key, [])
            continue
        current_list = None
        if val.startswith("[") and val.endswith("]"):
            meta[key] = _parse_inline_list(val)
        else:
            meta[key] = val.strip('"') if (val.startswith('"') and val.endswith('"')) else val
    return meta, text[m.end():].lstrip("\n")


def source_type(url: str) -> str:
    """scripts.scraper.router.detect_source 와 같은 규칙 (의존 차단용 복제 — 규칙 바꾸면 양쪽 동시).

    paste:// 는 붙여넣은 텍스트의 출처 식별자 (scripts/scraper/plain_text.PASTE_SCHEME).
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme == "paste":
            return "text"
        domain = parsed.netloc.lower()
    except Exception:  # noqa: BLE001
        return "web"
    if "youtube.com" in domain or "youtu.be" in domain:
        return "youtube"
    if "tiktok.com" in domain:
        return "tiktok"
    if "instagram.com" in domain:
        return "instagram"
    if "notion.site" in domain or "notion.so" in domain or "notion.com" in domain:
        return "notion"
    if "github.com" in domain:
        return "github"
    if "twitter.com" in domain or "x.com" in domain:
        return "twitter"
    return "web"


def _title_from_body(body: str, fallback: str) -> str:
    m = _H1_RE.search(body)
    if m:
        return m.group(1).strip()
    return fallback


def parse_skill_md(path: Path) -> Optional[SkillRecord]:
    """SKILL.md 1건 → SkillRecord. 읽기/파싱 실패 시 None (호출자가 제외)."""
    try:
        raw = redact_secrets(path.read_text(encoding="utf-8"))
        st = path.stat()
    except (OSError, UnicodeDecodeError) as e:
        logger.warning("SKILL.md 읽기 실패 — 인덱스 제외: %s (%s)", path, e)
        return None
    meta, body = parse_frontmatter(raw)
    slug = str(meta.get("name") or path.parent.name).strip()
    if not _SLUG_RE.match(slug):
        slug = path.parent.name
    sources_raw = meta.get("sources") or []
    if isinstance(sources_raw, str):
        sources_raw = [sources_raw]
    sources = tuple(s for s in (str(u).strip() for u in sources_raw) if s)
    tools_raw = meta.get("ai_tools") or []
    if isinstance(tools_raw, str):
        tools_raw = [tools_raw]
    description = str(meta.get("description") or "").strip()
    if not description:
        cm = _CALLOUT_RE.search(body)
        description = cm.group(1).strip() if cm else ""
    return SkillRecord(
        slug=slug,
        title=_title_from_body(body, slug),
        description=description,
        category=str(meta.get("category") or DEFAULT_CATEGORY).strip() or DEFAULT_CATEGORY,
        grade=str(meta.get("grade") or "").strip().upper(),
        difficulty=str(meta.get("difficulty") or "").strip(),
        ai_tools=tuple(str(t).strip() for t in tools_raw if str(t).strip()),
        sources=sources,
        source_types=tuple(source_type(u) for u in sources),
        body_md=body.strip("\n"),
        raw_md=raw,
        path=str(path),
        mtime=st.st_mtime,
    )


# ── 인덱스 빌드 ─────────────────────────────────────────────────

def _scan(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.glob("*/SKILL.md") if p.is_file())


def _version_of(paths: Iterable[Path]) -> str:
    """(파일 수, 최대 mtime, 경로 해시) — 파일 추가/삭제/수정 모두 감지."""
    paths = list(paths)
    latest = 0.0
    acc = 0
    for p in paths:
        try:
            st = p.stat()
        except OSError:
            continue
        latest = max(latest, st.st_mtime)
        # 프로세스 간 안정적인 해시 (hash() 는 PYTHONHASHSEED 로 매번 달라짐 → ETag 용으로 부적합)
        acc = zlib.crc32(p.parent.name.encode("utf-8"), acc)
    return f"{len(paths)}-{latest:.0f}-{acc:08x}"


def load_index(root: Path | str | None = None) -> LibraryIndex:
    """항상 디스크에서 새로 빌드."""
    root_p = Path(root) if root else MIRROR_DIR
    paths = _scan(root_p)
    records = []
    for p in paths:
        rec = parse_skill_md(p)
        if rec is not None:
            records.append(rec)
    records.sort(key=lambda r: r.slug)
    return LibraryIndex(
        records=tuple(records),
        version=_version_of(paths),
        root=str(root_p),
        built_at=time.time(),
    )


_CACHE: dict[str, LibraryIndex] = {}
_CACHE_CHECKED: dict[str, float] = {}
_CACHE_LOCK = threading.Lock()


def get_index(root: Path | str | None = None, *, force: bool = False) -> LibraryIndex:
    """캐시된 인덱스. 2초마다 디스크 버전 확인, 바뀌었으면 재빌드."""
    root_p = Path(root) if root else MIRROR_DIR
    key = str(root_p)
    now = time.time()
    with _CACHE_LOCK:
        cached = _CACHE.get(key)
        checked = _CACHE_CHECKED.get(key, 0.0)
        if cached is not None and not force and (now - checked) < REBUILD_THROTTLE_SEC:
            return cached
        current_version = _version_of(_scan(root_p))
        _CACHE_CHECKED[key] = now
        if cached is not None and not force and cached.version == current_version:
            return cached
    fresh = load_index(root_p)
    with _CACHE_LOCK:
        _CACHE[key] = fresh
    logger.info("라이브러리 인덱스 빌드: %d건 (version=%s)", len(fresh.records), fresh.version)
    return fresh


def is_valid_slug(slug: str) -> bool:
    return bool(slug) and len(slug) <= 120 and bool(_SLUG_RE.match(slug))
