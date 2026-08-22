"""사람용 게시판(카탈로그) + 게시글 상세 페이지 렌더링 — SKILL.md 인덱스가 원본.

- `/catalog` : 카테고리 섹션 + 칩 필터 + 검색, 카드/목록 보기 전환. 제목 클릭 = 사이트 안 게시글.
- `/skill/<slug>` : 게시글 상세 — 본문 전문·SKILL.md 복사·출처·같은 카테고리 글.
  **외부로 나가는 링크는 [원본 ↗] 하나뿐** (사이트 이탈 최소화).
- XSS 방어 (gotcha #31): 본문은 LLM 이 스크랩 결과로 만든 것 → markdown 렌더 후 allowlist
  sanitize, 모든 속성 html.escape, 엔진 스크립트만 CSP nonce.
- 정적 빌드(`build-catalog`)와 서버 응답이 같은 함수를 쓴다.
"""
from __future__ import annotations

import argparse
import collections
import html
import json
import logging
import re
import secrets
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Optional

from scripts.library import catalog_template as T
from scripts.library.index import (
    CATEGORY_ORDER,
    GRADE_ORDER,
    LibraryIndex,
    SkillRecord,
    get_index,
    load_index,
)

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = PROJECT_ROOT / "logs" / "catalog.html"
PAGE_TITLE = "두근 스킬 도서관"
DATA_TEXT_BODY_CHARS = 1500
TOOL_CHIP_MAX = 10
RELATED_MAX = 6

CATEGORY_KEYS = {
    "프롬프트": "prompt", "자동화": "automation", "콘텐츠": "content", "디자인": "design",
    "개발": "dev", "업무": "work", "기타": "etc",
}
CATEGORY_BLURB = {
    "프롬프트": "복붙해서 바로 쓰는 프롬프트 묶음과 프롬프트 설계 원리.",
    "자동화": "에이전트 · MCP · 워크플로우로 반복 업무를 없애는 스킬.",
    "콘텐츠": "영상 · SNS · 글쓰기 등 콘텐츠 제작과 기획.",
    "디자인": "이미지 생성, 일관성 유지, 시각 자산 제작.",
    "개발": "Claude Code · API · 개발 환경과 코딩 워크플로우.",
    "업무": "문서 · 분석 · 투자 · 회사 운영 같은 실무 생산성.",
    "기타": "위 분류에 딱 맞지 않는 나머지 유용한 스킬.",
}
SOURCE_LABEL = {
    "youtube": "유튜브", "notion": "노션", "github": "깃허브", "instagram": "인스타그램",
    "tiktok": "틱톡", "twitter": "X", "web": "웹",
}
GRADE_LABEL = {"S": "S · 필수", "A": "A · 추천", "B": "B · 참고", "C": "C · 보류", "": "미평가"}

# ── HTML sanitize (allowlist) ───────────────────────────────────

_ALLOWED_TAGS = {
    "p", "br", "hr", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "strong", "em", "b", "i",
    "code", "pre", "blockquote", "table", "thead", "tbody", "tr", "th", "td", "a", "del", "sup", "sub",
}
_VOID_TAGS = {"br", "hr"}
_DROP_CONTENT_TAGS = {"script", "style", "iframe", "object", "embed", "noscript", "svg", "math", "template"}
_ALLOWED_ATTRS = {"a": {"href", "title"}, "th": {"align"}, "td": {"align"}, "code": {"class"}}


class _Sanitizer(HTMLParser):
    """allowlist 밖 태그는 벗기고(텍스트는 유지), script/style 류는 내용까지 버린다."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self._drop_depth = 0
        self._open: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if self._drop_depth:
            if tag in _DROP_CONTENT_TAGS and tag not in _VOID_TAGS:
                self._drop_depth += 1
            return
        if tag in _DROP_CONTENT_TAGS:
            self._drop_depth = 1
            return
        if tag not in _ALLOWED_TAGS:
            return
        kept: list[str] = []
        allowed = _ALLOWED_ATTRS.get(tag, set())
        for name, value in attrs:
            name = name.lower()
            if name not in allowed or value is None:
                continue
            if name == "href":
                v = value.strip()
                low = v.lower()
                if not (low.startswith("http://") or low.startswith("https://") or low.startswith("#")):
                    continue
                kept.append(f'href="{html.escape(v, quote=True)}"')
                kept.append('target="_blank"')
                kept.append('rel="noopener noreferrer"')
                continue
            kept.append(f'{name}="{html.escape(value, quote=True)}"')
        attr_s = (" " + " ".join(kept)) if kept else ""
        self.out.append(f"<{tag}{attr_s}>")
        if tag not in _VOID_TAGS:
            self._open.append(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._drop_depth:
            if tag in _DROP_CONTENT_TAGS:
                self._drop_depth -= 1
            return
        if tag in _ALLOWED_TAGS and tag not in _VOID_TAGS and tag in self._open:
            # 닫는 태그 균형 — 가장 최근 같은 태그까지 닫는다
            while self._open:
                t = self._open.pop()
                self.out.append(f"</{t}>")
                if t == tag:
                    break

    def handle_data(self, data: str) -> None:
        if self._drop_depth:
            return
        self.out.append(html.escape(data, quote=False))

    def result(self) -> str:
        while self._open:
            self.out.append(f"</{self._open.pop()}>")
        return "".join(self.out)


def sanitize_html(fragment: str) -> str:
    p = _Sanitizer()
    p.feed(fragment or "")
    p.close()
    return p.result()


def render_markdown(md_text: str) -> str:
    """markdown → sanitize 된 HTML. markdown 패키지 없으면 <pre> 이스케이프 폴백."""
    try:
        import markdown  # type: ignore
        raw_html = markdown.markdown(md_text or "", extensions=["tables", "fenced_code", "sane_lists"])
    except Exception as e:  # noqa: BLE001
        logger.warning("markdown 렌더 실패 — pre 폴백: %s", e)
        raw_html = "<pre>" + html.escape(md_text or "") + "</pre>"
    return sanitize_html(raw_html)


# ── 헬퍼 ────────────────────────────────────────────────────────

def category_key(category: str) -> str:
    return CATEGORY_KEYS.get(category, "etc")


def tool_key(tool: str) -> str:
    return "".join(ch if (ch.isalnum() or ch in "._") else "_" for ch in tool.strip().lower()) or "etc"


def post_url(slug: str) -> str:
    return f"/skill/{slug}"


def _esc(s: str) -> str:
    return html.escape(s or "", quote=True)


_MD_MARK_RE = re.compile(r"\*\*|__|`")
_CALLOUT_RE = re.compile(r"^💡\s*(.+?)\s*$", re.M)


def plain_text(s: str) -> str:
    """설명 한 줄에서 마크다운 강조 기호(** __ `) 제거 — 카드/칩 같은 비-마크다운 자리용."""
    return _MD_MARK_RE.sub("", s or "").strip()


def _data_text(r: SkillRecord) -> str:
    parts = [r.title, r.slug, r.slug.replace("-", " "), plain_text(r.description), r.category, r.grade,
             r.difficulty, " ".join(r.ai_tools), r.body_md[:DATA_TEXT_BODY_CHARS]]
    text = " ".join(p for p in parts if p).lower()
    return " ".join(text.split())


def _grade_badge(grade: str) -> str:
    return f'<span class="grade g-{_esc(grade)}">{_esc(grade or "—")}</span>'


def _source_badge(src_type: str) -> str:
    return f'<span class="src s-{_esc(src_type)}">{_esc(SOURCE_LABEL.get(src_type, src_type))}</span>'


def _origin_button(r: SkillRecord, cls: str = "btn ext") -> str:
    """유일한 외부 이탈 링크 — 출처가 없으면 버튼 자체를 안 만든다."""
    if not r.sources:
        return ""
    return (f'<a class="{cls}" href="{_esc(r.sources[0])}" target="_blank" '
            f'rel="noopener noreferrer">원본 ↗</a>')


def _body_without_title(r: SkillRecord) -> tuple[str, str]:
    """(callout 한 줄, H1·callout 제거한 본문) — 상세 페이지에서 callout 은 따로 강조."""
    lines = r.body_md.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    body = "\n".join(lines).strip("\n")
    m = _CALLOUT_RE.search(body)
    callout = ""
    if m:
        callout = m.group(1).strip()
        body = body[:m.start()] + body[m.end():]
    return callout, body.strip("\n")


# ── 카탈로그(게시판 목록) ────────────────────────────────────────

def _render_card(r: SkillRecord, i: int) -> str:
    src_type = r.source_types[0] if r.source_types else "web"
    tools_s = " · ".join(r.ai_tools) if r.ai_tools else "도구 미지정"
    meta_line = f"{r.difficulty + ' · ' if r.difficulty else ''}{tools_s}"
    url = post_url(r.slug)
    return (
        f'<article class="card" style="--i:{i}" id="{_esc(r.slug)}" data-group="{category_key(r.category)}" '
        f'data-grade="{_esc(r.grade)}" data-source="{_esc(src_type)}" '
        f'data-tools="{_esc(" ".join(tool_key(t) for t in r.ai_tools))}" '
        f'data-date="{_esc(r.updated_date)}" data-text="{_esc(_data_text(r))}">\n'
        f'  <div class="chead">{_grade_badge(r.grade)}{_source_badge(src_type)}'
        f'<span class="date">{_esc(r.updated_date)}</span></div>\n'
        f'  <h3><a class="tlink" href="{_esc(url)}">{_esc(r.title)}</a></h3>\n'
        f'  <p class="desc">{_esc(plain_text(r.description))}</p>\n'
        f'  <p class="cmeta">{_esc(meta_line)}</p>\n'
        f'  <div class="acts">\n'
        f'    <a class="btn primary" href="{_esc(url)}">읽기</a>\n'
        f'    {_origin_button(r)}\n'
        f'  </div>\n'
        f'</article>\n'
    )


def _grade_sort_key(g: str) -> int:
    return GRADE_ORDER.index(g) if g in GRADE_ORDER else len(GRADE_ORDER)


def _render_sections(records: Iterable[SkillRecord]) -> str:
    by_cat: dict[str, list[SkillRecord]] = collections.defaultdict(list)
    for r in records:
        by_cat[r.category].append(r)
    order = [c for c in CATEGORY_ORDER if c in by_cat] + sorted(c for c in by_cat if c not in CATEGORY_ORDER)
    out: list[str] = []
    for n, cat in enumerate(order, start=1):
        recs = sorted(by_cat[cat], key=lambda r: (_grade_sort_key(r.grade), r.title))
        subs: dict[str, list[SkillRecord]] = collections.OrderedDict()
        for r in recs:
            subs.setdefault(r.grade, []).append(r)
        sub_html = []
        for grade, items in subs.items():
            cards = "".join(_render_card(r, i) for i, r in enumerate(items))
            sub_html.append(
                f'<div class="sub"><div class="shead">{_esc(GRADE_LABEL.get(grade, grade))}</div>'
                f'<div class="grid">\n{cards}</div></div>'
            )
        out.append(
            f'<section class="domain" data-group="{category_key(cat)}">\n'
            f'  <div class="dhead"><span class="num">{n:02d}</span><h2>{_esc(cat)}</h2>'
            f'<span class="cnt">{len(recs)}</span></div>\n'
            f'  <p class="dblurb">{_esc(CATEGORY_BLURB.get(cat, ""))}</p>\n'
            + "\n".join(sub_html) + "\n</section>\n"
        )
    return "\n".join(out)


def _chips(items: Iterable[tuple[str, str]], cls: str, attr: str) -> str:
    return "".join(f'<button class="{cls}" data-{attr}="{_esc(k)}">{_esc(label)}</button>' for k, label in items)


def render_catalog(index: LibraryIndex, *, nonce: str | None = None) -> str:
    """인덱스 → 게시판 HTML (자체완결)."""
    nonce = nonce or secrets.token_urlsafe(16)
    recs = index.records
    stats = index.stats()
    src_counter: collections.Counter[str] = collections.Counter(
        r.source_types[0] if r.source_types else "web" for r in recs
    )
    source_chips = _chips(
        ((s, f"{SOURCE_LABEL.get(s, s)} {c}") for s, c in src_counter.most_common()), "schip", "src",
    )
    cats_present = [c for c in CATEGORY_ORDER if stats["by_category"].get(c)]
    category_chips = _chips(((category_key(c), f"{c} {stats['by_category'][c]}") for c in cats_present), "chip", "dom")
    grades_present = [g for g in GRADE_ORDER if stats["by_grade"].get(g)]
    grade_chips = _chips(((g, f"{g} {stats['by_grade'][g]}") for g in grades_present), "gchip", "grade")
    tool_chips = _chips(
        ((tool_key(t), f"{t} {c}") for t, c in stats["top_tools"][:TOOL_CHIP_MAX]), "tchip", "tool",
    )
    last = stats["last_updated"]
    last_short = f"{last[5:7]}.{last[8:10]}" if len(last) >= 10 else "-"
    return T.CATALOG_PAGE.format(
        csp=T.CSP.format(nonce=nonce),
        fonts=T.FONT_LINKS,
        nonce=nonce,
        title=_esc(PAGE_TITLE),
        css=T.BASE_CSS + T.CATALOG_CSS,
        js=T.CATALOG_JS,
        generated_kst=time.strftime("%Y-%m-%d %H:%M"),
        total=len(recs),
        n_categories=len(cats_present),
        last_updated_short=_esc(last_short),
        source_chips=source_chips,
        category_chips=category_chips,
        grade_chips=grade_chips,
        tool_chips=tool_chips,
        sections=_render_sections(recs),
    )


# ── 게시글 상세 ─────────────────────────────────────────────────

def _related_html(rec: SkillRecord, index: LibraryIndex) -> str:
    siblings = [
        r for r in index.filter(category=rec.category)
        if r.slug != rec.slug
    ]
    siblings.sort(key=lambda r: (_grade_sort_key(r.grade), r.title))
    items = siblings[:RELATED_MAX]
    rows = "".join(
        f'<li><a href="{_esc(post_url(r.slug))}">{_grade_badge(r.grade)}'
        f'<span class="rt">{_esc(r.title)}</span></a></li>'
        for r in items
    ) or ('<li><a href="/catalog"><span class="rt">이 카테고리엔 아직 다른 글이 없어요 — '
          '전체 목록 보기</span></a></li>')
    return (
        f'<section class="psec"><h2>같은 카테고리 · {_esc(rec.category)}</h2>'
        f'<ul class="related">{rows}</ul></section>'
    )


def render_skill_page(rec: SkillRecord, index: LibraryIndex, *, nonce: str | None = None) -> str:
    """게시글 상세 HTML. 외부 링크는 [원본 ↗] 과 출처 목록뿐."""
    nonce = nonce or secrets.token_urlsafe(16)
    callout, body = _body_without_title(rec)
    src_type = rec.source_types[0] if rec.source_types else "web"
    chips = [_grade_badge(rec.grade), _source_badge(src_type),
             f'<span class="tag">{_esc(rec.category)}</span>']
    if rec.difficulty:
        chips.append(f'<span class="tag">{_esc(rec.difficulty)}</span>')
    chips += [f'<span class="tag">{_esc(t)}</span>' for t in rec.ai_tools]
    chips.append(f'<span class="date">{_esc(rec.updated_date)}</span>')
    sources_html = "".join(
        f'<a href="{_esc(u)}" target="_blank" rel="noopener noreferrer">{_esc(u)}</a>' for u in rec.sources
    ) or '<span class="tag">출처 정보 없음</span>'
    return T.SKILL_PAGE.format(
        csp=T.CSP.format(nonce=nonce),
        fonts=T.FONT_LINKS,
        nonce=nonce,
        title=_esc(rec.title),
        slug=_esc(rec.slug),
        meta_chips="".join(chips),
        origin_button=_origin_button(rec, cls="btn"),
        callout=(f'<div class="callout">{_esc(plain_text(callout))}</div>' if callout else ""),
        body_html=render_markdown(body),
        sources_html=sources_html,
        related_html=_related_html(rec, index),
        raw_md=_esc(rec.raw_md),
        css=T.BASE_CSS + T.PAGE_CSS,
        js=T.PAGE_JS,
    )


# ── 정적 빌드 / CLI ─────────────────────────────────────────────

def build_catalog_file(out: Path | str = DEFAULT_OUT, *, root: Path | str | None = None) -> dict:
    """정적 catalog.html 생성. {ok, path, count, bytes}."""
    idx = load_index(root) if root else get_index(force=True)
    html_text = render_catalog(idx)
    out_p = Path(out)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_p.with_suffix(out_p.suffix + ".tmp")
    tmp.write_text(html_text, encoding="utf-8")
    tmp.replace(out_p)
    return {"ok": True, "path": str(out_p), "count": len(idx.records), "bytes": len(html_text.encode("utf-8"))}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="스킬 라이브러리 CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build-catalog", help="정적 catalog.html 생성")
    b.add_argument("--out", default=str(DEFAULT_OUT))
    b.add_argument("--root", default=None, help="SKILL.md mirror 루트 (기본 skills/)")
    s = sub.add_parser("search", help="터미널에서 검색")
    s.add_argument("query")
    s.add_argument("-k", type=int, default=8)
    s.add_argument("--mode", default="hybrid", choices=["hybrid", "keyword"])
    sub.add_parser("stats", help="인덱스 통계")
    args = parser.parse_args(argv)
    if args.cmd == "build-catalog":
        res = build_catalog_file(args.out, root=args.root)
        print(json.dumps(res, ensure_ascii=False))
        return 0
    if args.cmd == "search":
        from scripts.library.search import search
        res = search(args.query, k=args.k, mode=args.mode)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res.get("ok") else 1
    if args.cmd == "stats":
        print(json.dumps(get_index(force=True).stats(), ensure_ascii=False, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
