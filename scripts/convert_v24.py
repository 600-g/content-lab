"""v2.2/v2.3 SKILL.md → v2.4 일괄 변환.

사용:
    python -m scripts.convert_v24 --dry        # 미리보기
    python -m scripts.convert_v24 --apply      # 디스크 22건 실제 변환
    python -m scripts.convert_v24 --apply --notion  # + Notion DB 의 폐기 속성 비우기

원칙:
- 본문 내용은 보존 (사용자 지시 — "내용은 유지").
- 폼 규칙 잔재(메타 quote 박스, 30초 핵심, role stripe, 푸터 메타)만 제거.
- frontmatter 를 v2.4 flat 키로 정리. 폐기 키(tags/targets/날짜/template_version) 제거.
- 미러도 같이 동기화.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GLOBAL_SKILLS = Path.home() / ".claude" / "skills"
MIRROR_SKILLS = PROJECT_ROOT / "skills"

NOTION_API = "https://api.notion.com/v1"
NOTION_DB_ID = os.getenv("NOTION_DB_ID", "")
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


# ── frontmatter 파싱 (v2.2 nested metadata) ───────────────
_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """SKILL.md 텍스트 → (frontmatter dict, body str).

    v2.2 nested `metadata:` + v2.4 flat 키 + 들여쓰기 리스트(sources) 모두 지원.
    """
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    raw_fm, body = m.group(1), text[m.end():]
    fm: dict = {"_raw": raw_fm}
    lines = raw_fm.splitlines()
    i = 0
    while i < len(lines):
        s = lines[i].rstrip()
        if not s or s.startswith("#") or s.startswith(" "):
            i += 1; continue
        m2 = re.match(r"^([a-zA-Z_]+):\s*(.*)$", s)
        if not m2:
            i += 1; continue
        key, val = m2.group(1), m2.group(2).strip()
        # inline list  ai_tools: ["A", "B"]
        if val.startswith("[") and val.endswith("]"):
            inside = val[1:-1].strip()
            fm[key] = [x.strip().strip('"').strip("'") for x in inside.split(",") if x.strip()]
            i += 1; continue
        # block list  sources:\n  - url1\n  - url2
        if val == "" and i + 1 < len(lines) and lines[i + 1].lstrip().startswith("-"):
            items = []
            j = i + 1
            while j < len(lines) and lines[j].lstrip().startswith("-"):
                items.append(lines[j].lstrip()[1:].strip().strip('"').strip("'"))
                j += 1
            fm[key] = items
            i = j; continue
        # 스칼라
        fm[key] = val.strip('"').strip("'")
        i += 1
    # metadata 블록 (v2.2 nested)
    md_m = re.search(r"^metadata:\s*\n((?:  .*\n?)+)", raw_fm, re.M)
    if md_m:
        meta_block = md_m.group(1)
        fm["metadata"] = {}
        # 단순 key: value
        for line in meta_block.splitlines():
            ln = line.strip()
            mk = re.match(r"^([a-zA-Z_]+):\s*(.*)$", ln)
            if mk:
                v = mk.group(2).strip()
                # 리스트 [a, b]
                if v.startswith("[") and v.endswith("]"):
                    inside = v[1:-1].strip()
                    items = [x.strip().strip('"').strip("'") for x in inside.split(",") if x.strip()]
                    fm["metadata"][mk.group(1)] = items
                else:
                    fm["metadata"][mk.group(1)] = v.strip('"').strip("'")
        # source_urls: 별도 (들여쓰기 리스트)
        urls_m = re.search(r"^  source_urls:\s*\n((?:    -.*\n?)+)", raw_fm, re.M)
        if urls_m:
            fm["metadata"]["source_urls"] = [
                ln.strip()[2:].strip().strip('"').strip("'")
                for ln in urls_m.group(1).splitlines() if ln.strip().startswith("-")
            ]
    return fm, body


# ── 본문 메타 폼 제거 ────────────────────────────────────
_RE_30S = re.compile(r"^>\s*\*\*⚡\s*30초\s*핵심\*\*.*?(?:\n>.*)*\n?", re.M)
_RE_TLDR = re.compile(r"^>\s*\*\*TL;DR\*\*.*$\n?", re.M)
_RE_META_QUOTE = re.compile(r"^>\s*\*\*메타\*\*.*?(?:\n>\s*\*\*(?:도구|적용 대상)\*\*.*)*\n?", re.M)
_RE_ROLE_STRIPE = re.compile(r"^>\s*\*\*[SABC]\*\*\s*·.*$\n?", re.M)
_RE_FOOTER_META = re.compile(r"^>\s*📋\s*\*수집.*?\*\s*$\n?", re.M)
_RE_DIVIDER_ORPHAN = re.compile(r"\n\n---\n\n(?=#)", re.M)  # 메타 박스 뒤 외톨이 ---
# v2.5 — 헤더 이모지 prefix 제거 (가독성). H1/H2/H3 모두
_RE_H_EMOJI = re.compile(r"^(#+)\s+[\U0001F300-\U0001FAFF☀-➿⌀-⏿]+\s*", re.M)
# 본문 첫 줄 💡 callout → 자연 문장
_RE_CALLOUT_LIGHTBULB = re.compile(r"^💡\s+", re.M)


def strip_form_blocks(body: str) -> str:
    """메타 quote / 30초 핵심 / role stripe / 푸터 메타 제거. 본문은 보존.
    v2.5 추가: 헤더 이모지 prefix 제거 + 💡 콜아웃 prefix 제거."""
    body = _RE_30S.sub("", body)
    body = _RE_TLDR.sub("", body)
    body = _RE_META_QUOTE.sub("", body)
    body = _RE_ROLE_STRIPE.sub("", body)
    body = _RE_FOOTER_META.sub("", body)
    body = _RE_H_EMOJI.sub(r"\1 ", body)            # `## 🎯 언제 쓰나` → `## 언제 쓰나`
    body = _RE_CALLOUT_LIGHTBULB.sub("", body)     # `💡 1줄...` → `1줄...`
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip() + "\n"


def extract_tldr(body: str, fm_description: str) -> str:
    """30초 핵심 박스에서 '🎯 무엇 — ...' 추출, 없으면 frontmatter description."""
    m = re.search(r"🎯\s*\*\*무엇\*\*\s*—\s*([^\n]+)", body)
    if m:
        return m.group(1).strip().rstrip(".") + "."
    if fm_description:
        return fm_description.strip()
    return ""


def extract_title(body: str) -> str:
    """H1 추출 + 선행 이모지/아이콘 prefix 제거 (예: '# ⚡ AI 이커머스 비서' → 'AI 이커머스 비서')."""
    m = re.search(r"^#\s+(.+?)$", body, re.M)
    if not m:
        return ""
    title = m.group(1).strip()
    # 끝의 '· 🔀 합병됨' 같은 배지 제거
    title = re.sub(r"\s*·\s*🔀\s*합병됨\s*$", "", title)
    # 시작 이모지 1-2개 제거 (한글/영문 시작 전까지)
    title = re.sub(r"^[\U0001F300-\U0001FAFF☀-➿⌀-⏿]+\s*", "", title)
    return title.strip()


# ── v2.4 SKILL.md 재조립 ────────────────────────────────
def to_v24(text: str) -> tuple[str, dict]:
    """기존 SKILL.md 텍스트 → v2.4 텍스트. 변환 요약 정보도 반환."""
    fm, body = parse_frontmatter(text)
    meta = fm.get("metadata", {})

    title = extract_title(body)
    tldr = extract_tldr(body, fm.get("description", ""))

    # H1 + 첫 메타 박스들 제거
    body_clean = strip_form_blocks(body)
    # 기존 H1 / 첫 stripe 제거 (재구성)
    body_clean = re.sub(r"^#\s+.+?\n", "", body_clean, count=1)
    # 본문이 빈 줄로 시작하면 정리
    body_clean = body_clean.lstrip("\n")

    # frontmatter 재구성 — v2.2 nested 우선 + v2.4 flat fallback
    def _g(k, default):
        v = meta.get(k)
        if v in (None, ""):
            v = fm.get(k)
        return v if v not in (None, "") else default

    grade = _g("grade", "A")
    difficulty = _g("difficulty", "중급")
    category = _g("category", "기타")
    ai_tools = _g("ai_tools", []) or []
    if not isinstance(ai_tools, list):
        ai_tools = []
    sources = fm.get("sources") or meta.get("source_urls") or []
    if not isinstance(sources, list):
        sources = []

    description = (fm.get("description") or tldr).replace("\n", " ").strip()
    if len(description) > 280:
        description = description[:277] + "..."

    tools_yaml = ", ".join(f'"{t}"' for t in ai_tools)
    sources_yaml = "\n".join(f"  - {u}" for u in sources) or "  - (unknown)"

    new_fm = f"""---
name: {fm.get("name", "")}
description: {description}
origin: content-lab
grade: {grade}
difficulty: {difficulty}
category: {category}
ai_tools: [{tools_yaml}]
sources:
{sources_yaml}
---
"""

    # v2.5: 💡 prefix 제거 — 자연 문장 한두 줄로 시작
    intro = f"\n{tldr}\n" if tldr else ""
    new_text = f"{new_fm}\n# {title}\n{intro}\n{body_clean.rstrip()}\n"
    return new_text, {
        "name": fm.get("name", ""),
        "title": title,
        "tldr_extracted": bool(tldr),
        "grade": grade,
        "category": category,
        "source_count": len(sources),
        "before_bytes": len(text),
        "after_bytes": len(new_text),
    }


# ── Notion 정리 ─────────────────────────────────────────
def notion_db_pages() -> list[dict]:
    """DB row 페이지 전수 조회 (간이 — 100건 한 번)."""
    if not NOTION_API_KEY or not NOTION_DB_ID:
        return []
    r = requests.post(
        f"{NOTION_API}/databases/{NOTION_DB_ID}/query",
        headers=NOTION_HEADERS, json={"page_size": 100}, timeout=20,
    )
    r.raise_for_status()
    return r.json().get("results", [])


def notion_clear_legacy(page_id: str) -> bool:
    """폐기 속성(태그/적용대상) 비우기. '상태' 는 select 라 그대로 둠."""
    body = {
        "properties": {
            "태그": {"multi_select": []},
            "적용 대상": {"multi_select": []},
        }
    }
    try:
        r = requests.patch(
            f"{NOTION_API}/pages/{page_id}",
            headers=NOTION_HEADERS, json=body, timeout=20,
        )
        return r.status_code in (200, 201)
    except Exception:  # noqa: BLE001
        return False


# ── Notion 본문 정리 (v2.5) ─────────────────────────────
_FORM_QUOTE_PATTERNS = (
    "30초 핵심", "TL;DR", "**메타**", "**도구**", "**적용 대상**",
    "📋 *수집", "📋 수집",
    # 30초 핵심 박스의 분리 줄들 (Notion 이 quote 안의 각 줄을 별 quote 로 박는 경우)
    "🎯 **무엇**", "⏰ **언제**", "🛠 **시작**", "🏢 **두근 적용**",
    "🎯 무엇 —", "⏰ 언제 —", "🛠 시작 —", "🏢 두근 적용 —",
)
_RE_FORM_STRIPE = re.compile(r"^\*\*[SABC]\*\*\s*·")
_RE_HDR_EMOJI = re.compile(r"^[\U0001F300-\U0001FAFF☀-➿⌀-⏿]+\s*")


def _is_form_quote(plain: str) -> bool:
    """폼 메타 quote 인지 판별 (사용자 콘텐츠 quote 와 구분)."""
    p = plain.strip()
    if any(pat in p for pat in _FORM_QUOTE_PATTERNS):
        return True
    if _RE_FORM_STRIPE.match(p):
        return True
    return False


def _strip_h_emoji(text: str) -> str:
    return _RE_HDR_EMOJI.sub("", text).strip()


import time as _time  # 레이트 제한 sleep 용


def notion_clean_body(page_id: str) -> dict:
    """페이지 children blocks 정리.
    - quote 블록 중 폼 메타 패턴인 것만 삭제 (사용자 인용은 보존)
    - heading_1/2/3 의 이모지 prefix 제거 → 평문 헤더로
    """
    stats = {"quotes_deleted": 0, "headings_cleaned": 0}
    cursor = None
    while True:
        url = f"{NOTION_API}/blocks/{page_id}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        try:
            r = requests.get(url, headers=NOTION_HEADERS, timeout=20)
            if r.status_code != 200:
                return stats
            d = r.json()
        except Exception:  # noqa: BLE001
            return stats
        for block in d.get("results", []):
            btype = block.get("type")
            bid = block.get("id")
            if btype == "quote":
                texts = block.get("quote", {}).get("rich_text", [])
                plain = "".join(t.get("plain_text", "") for t in texts)
                if _is_form_quote(plain):
                    try:
                        requests.delete(f"{NOTION_API}/blocks/{bid}",
                                        headers=NOTION_HEADERS, timeout=10)
                        stats["quotes_deleted"] += 1
                    except Exception:  # noqa: BLE001
                        pass
                    _time.sleep(0.35)
            elif btype == "paragraph":
                # 빈 / `>` 만 있는 paragraph (메타 박스 잔재) 삭제
                texts = block.get("paragraph", {}).get("rich_text", [])
                plain = "".join(t.get("plain_text", "") for t in texts).strip()
                if plain in ("", ">", "> ", "---"):
                    try:
                        requests.delete(f"{NOTION_API}/blocks/{bid}",
                                        headers=NOTION_HEADERS, timeout=10)
                        stats["quotes_deleted"] += 1  # 같은 카운터로 묶음
                    except Exception:  # noqa: BLE001
                        pass
                    _time.sleep(0.35)
            elif btype in ("heading_1", "heading_2", "heading_3"):
                blob = block.get(btype, {})
                texts = blob.get("rich_text", [])
                if not texts:
                    continue
                plain = "".join(t.get("plain_text", "") for t in texts)
                new_plain = _strip_h_emoji(plain)
                if new_plain and new_plain != plain:
                    new_rt = [{"type": "text", "text": {"content": new_plain}}]
                    try:
                        requests.patch(
                            f"{NOTION_API}/blocks/{bid}",
                            headers=NOTION_HEADERS,
                            json={btype: {"rich_text": new_rt}},
                            timeout=10,
                        )
                        stats["headings_cleaned"] += 1
                    except Exception:  # noqa: BLE001
                        pass
                    _time.sleep(0.35)
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
    return stats


# ── 실행 ────────────────────────────────────────────────
def find_content_lab_files() -> list[Path]:
    """origin: content-lab 인 SKILL.md 전수 (글로벌)."""
    out = []
    for f in GLOBAL_SKILLS.glob("*/SKILL.md"):
        head = f.read_text(encoding="utf-8", errors="ignore")[:600]
        if "origin: content-lab" in head:
            out.append(f)
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="실제 디스크 쓰기")
    ap.add_argument("--notion", action="store_true", help="Notion 폐기 속성도 정리")
    ap.add_argument("--dry", action="store_true", help="미리보기 (기본)")
    args = ap.parse_args()
    apply = args.apply and not args.dry

    files = find_content_lab_files()
    print(f"대상: {len(files)}건 (origin=content-lab)\n")

    summaries = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        try:
            new_text, info = to_v24(text)
        except Exception as e:  # noqa: BLE001
            print(f"  ❌ {f.parent.name}: {e}")
            continue
        info["delta"] = info["after_bytes"] - info["before_bytes"]
        summaries.append(info)
        mark = "✏️ 변환" if apply else "👀 미리보기"
        print(f"  {mark}  {info['name']:<45} {info['grade']:<2} {info['category']:<6}  Δ{info['delta']:+5}B")
        if apply:
            f.write_text(new_text, encoding="utf-8")
            # mirror 동기화
            mirror = MIRROR_SKILLS / f.parent.name / "SKILL.md"
            if mirror.exists():
                mirror.write_text(new_text, encoding="utf-8")

    total_delta = sum(s["delta"] for s in summaries)
    print(f"\n총 변환 {len(summaries)}건, 누적 바이트 변화: {total_delta:+}")

    if args.notion and apply:
        print(f"\nNotion 정리...")
        pages = notion_db_pages()
        cleaned = 0
        total_q = 0
        total_h = 0
        for p in pages:
            if notion_clear_legacy(p["id"]):
                cleaned += 1
            # 본문 폼 정리
            bs = notion_clean_body(p["id"])
            total_q += bs["quotes_deleted"]
            total_h += bs["headings_cleaned"]
            title_prop = p.get("properties", {}).get("스킬명", {}).get("title", [])
            name = "".join(t.get("plain_text", "") for t in title_prop)[:40]
            if bs["quotes_deleted"] or bs["headings_cleaned"]:
                print(f"  {name:<40}  quote -{bs['quotes_deleted']}  heading 정리 {bs['headings_cleaned']}")
        print(f"  속성 정리: {cleaned}/{len(pages)}건 / 폼 quote 삭제: {total_q} / 이모지 헤더 정리: {total_h}건")


if __name__ == "__main__":
    main()
