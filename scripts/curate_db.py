"""Notion DB 전수 큐레이션 CLI.

기능:
  analyze       — 모든 페이지 분석 리포트 (변경 X)
  fix-emoji     — 제목 시작 이모지 → 페이지 아이콘으로 이동
  fix-meta      — 카테고리/등급/난이도/태그/AI도구 재평가 (Gemini)
  polish-body   — 본문 5섹션(핵심/적용/예시/주의/출처)으로 통일 (Gemini)
  find-dupes    — 중복 후보 리스트 (변경 X)
  merge-dupes   — 중복 페이지 자동 합병
  all           — fix-emoji + fix-meta + polish-body + find-dupes 순차 실행

사용법:
  cd ~/Developer/my-company/content-lab && source venv/bin/activate
  python -m scripts.curate_db analyze
  python -m scripts.curate_db all
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:
    pass

from scripts.notion_client.register import (
    _request, _db_id, NotionError,
    CATEGORY_TO_DB, DIFFICULTY_TO_DB,
    DB_AI_TOOLS, DB_TAGS, DB_TARGETS,
)
from scripts.analyzer.prompt import CATEGORIES, GRADES, AI_TOOLS, TAGS
from scripts.analyzer.gemini import call_gemma_json

log = logging.getLogger("curate")

# 페이지 제목 시작 이모지 매칭 (BMP + 보조 평면 모두)
EMOJI_RE = re.compile(
    r'^([\U0001F000-\U0001FFFF☀-➿⌀-⏿ -⁯⬀-⯿])\s*'
)

# 카테고리별 추천 아이콘 (제목에 이모지 없을 때 폴백)
CATEGORY_ICON = {
    "프롬프트": "💬",
    "에이전트/자동화": "🤖",
    "영상/콘텐츠": "🎬",
    "디자인/이미지": "🎨",
    "코딩/개발": "💻",
    "업무효율": "⚡",
    "마케팅/SNS": "📱",
    "기타": "📦",
}


def fetch_all_pages() -> list[dict]:
    """DB의 모든 페이지 가져오기 (페이지네이션 처리)."""
    out: list[dict] = []
    cursor = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        data = _request("POST", f"databases/{_db_id()}/query", body, "전수 조회")
        out.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return out


def fetch_blocks(page_id: str) -> str:
    """페이지 본문 블록 → 마크다운 형태 텍스트."""
    md_parts: list[str] = []
    cursor = None
    while True:
        path = f"blocks/{page_id}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        data = _request("GET", path, context="블록 조회")
        for b in data.get("results", []):
            t = b.get("type")
            content = b.get(t, {})
            rt = content.get("rich_text", [])
            text = "".join(r.get("plain_text", "") for r in rt)
            if t == "heading_1":
                md_parts.append(f"# {text}")
            elif t == "heading_2":
                md_parts.append(f"## {text}")
            elif t == "heading_3":
                md_parts.append(f"### {text}")
            elif t == "bulleted_list_item":
                md_parts.append(f"- {text}")
            elif t == "numbered_list_item":
                md_parts.append(f"1. {text}")
            elif t == "paragraph":
                md_parts.append(text)
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return "\n".join(p for p in md_parts if p)


def get_title(page: dict) -> str:
    title_arr = page.get("properties", {}).get("스킬명", {}).get("title", [])
    return "".join(t.get("plain_text", "") for t in title_arr)


def get_select(page: dict, prop: str) -> str:
    p = page.get("properties", {}).get(prop, {})
    sel = p.get("select")
    return sel.get("name", "") if sel else ""


def get_multi(page: dict, prop: str) -> list[str]:
    p = page.get("properties", {}).get(prop, {})
    return [o.get("name", "") for o in p.get("multi_select", [])]


def get_url(page: dict, prop: str) -> str:
    return page.get("properties", {}).get(prop, {}).get("url", "") or ""


def get_rich_text(page: dict, prop: str) -> str:
    p = page.get("properties", {}).get(prop, {})
    rt = p.get("rich_text", [])
    return "".join(t.get("plain_text", "") for t in rt)


def split_title_emoji(title: str) -> tuple[Optional[str], str]:
    """제목에서 시작 이모지 분리. (emoji|None, rest)."""
    m = EMOJI_RE.match(title)
    if m:
        return m.group(1), title[m.end():].strip()
    return None, title.strip()


# ── 명령: analyze ────────────────────────────────────────
def cmd_analyze(pages: list[dict]) -> None:
    print(f"\n📊 전체 페이지: {len(pages)}개\n")
    print("=" * 100)

    emoji_dup = 0
    no_icon_with_title_emoji = 0
    cat_unknown = 0
    grade_unknown = 0
    diff_unknown = 0
    tags_empty = 0
    by_cat: dict[str, int] = {}
    by_grade: dict[str, int] = {}
    urls: dict[str, list[str]] = {}
    titles: dict[str, list[str]] = {}

    for p in pages:
        title = get_title(p)
        emoji, rest = split_title_emoji(title)
        icon = p.get("icon")
        cat = get_select(p, "카테고리")
        grade = get_select(p, "등급")
        diff = get_select(p, "난이도")
        tags = get_multi(p, "태그")
        url = get_url(p, "출처 URL")

        if emoji and icon:
            emoji_dup += 1
        if emoji and not icon:
            no_icon_with_title_emoji += 1

        # 카테고리 DB 옵션과 일치하는지 (역방향: DB값이 우리 코드 카테고리 7종에 있어야)
        valid_cats = set(CATEGORY_TO_DB.values())
        if cat not in valid_cats:
            cat_unknown += 1
        if not grade or grade.split("-")[0] not in GRADES:
            grade_unknown += 1
        if diff not in DIFFICULTY_TO_DB.values():
            diff_unknown += 1
        if not tags:
            tags_empty += 1

        by_cat[cat or "(없음)"] = by_cat.get(cat or "(없음)", 0) + 1
        gkey = grade.split("-")[0] if grade else "(없음)"
        by_grade[gkey] = by_grade.get(gkey, 0) + 1

        if url:
            urls.setdefault(url, []).append(title)
        norm_title = re.sub(r'[^가-힣a-zA-Z0-9]', '', rest.lower())[:18]
        if norm_title:
            titles.setdefault(norm_title, []).append(title)

    # 리포트
    print(f"🎨 이모지 중복 (제목+아이콘 둘 다): {emoji_dup}건")
    print(f"📍 제목에 이모지 + 아이콘 없음 (옮기면 됨):  {no_icon_with_title_emoji}건")
    print(f"❓ 알 수 없는 카테고리: {cat_unknown}건")
    print(f"❓ 등급 비정상:        {grade_unknown}건")
    print(f"❓ 난이도 비정상:      {diff_unknown}건")
    print(f"📋 태그 비어있음:       {tags_empty}건")

    print("\n📂 카테고리 분포:")
    for c, n in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f"   {c:24s} {n:3d}건")

    print("\n🎯 등급 분포:")
    for g, n in sorted(by_grade.items(), key=lambda x: -x[1]):
        print(f"   {g:6s} {n:3d}건")

    dup_urls = {k: v for k, v in urls.items() if len(v) > 1}
    dup_titles = {k: v for k, v in titles.items() if len(v) > 1}
    if dup_urls:
        print("\n🚨 동일 URL 중복:")
        for u, titles_list in dup_urls.items():
            print(f"   {u}")
            for t in titles_list:
                print(f"     · {t}")
    if dup_titles:
        print("\n🟡 제목 유사 (합병 후보):")
        for k, ts in dup_titles.items():
            print(f"   [{k}]")
            for t in ts:
                print(f"     · {t}")
    if not dup_urls and not dup_titles:
        print("\n✅ 명확한 중복 없음")


# ── 명령: fix-emoji ──────────────────────────────────────
def cmd_fix_emoji(pages: list[dict], dry: bool = False) -> int:
    fixed = 0
    for p in pages:
        pid = p["id"]
        title = get_title(p)
        emoji, rest = split_title_emoji(title)
        icon = p.get("icon")
        if not emoji or not rest:
            continue

        update_body: dict = {
            "properties": {
                "스킬명": {"title": [{"text": {"content": rest}}]}
            }
        }
        # 아이콘 없으면 → 제목 이모지를 아이콘으로 이동
        if not icon:
            update_body["icon"] = {"type": "emoji", "emoji": emoji}
            action = f"이모지 → 아이콘 + 제목 정리"
        else:
            action = "제목 이모지만 제거 (아이콘 유지)"

        print(f"  [{pid[:8]}] {title[:40]:<40s} → {rest[:40]:<40s} ({action})")
        if not dry:
            try:
                _request("PATCH", f"pages/{pid}", update_body, "이모지 정리")
                fixed += 1
                time.sleep(0.15)
            except NotionError as e:
                print(f"     ❌ 실패: {e}")
    print(f"\n총 {fixed}건 정리 (dry={dry})")
    return fixed


# ── 명령: fix-meta (카테고리/등급/난이도/태그/AI도구 재평가) ─
def _gemini_reclassify(title: str, summary: str, body_md: str) -> Optional[dict]:
    try:
        import google.generativeai as genai
    except ImportError:
        return None
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    genai.configure(api_key=api_key)

    cats = " / ".join(CATEGORY_TO_DB.values())
    tags_list = " / ".join(TAGS)
    tools_list = " / ".join(AI_TOOLS)
    prompt = f"""너는 두근컴퍼니의 AI 스킬 분류 검수자다.

[제목] {title}
[핵심요약] {summary}
[본문(앞 6000자)]
{body_md[:6000]}

[허용 옵션 — 정확히 일치해야 함]
- category: {cats}
- grade: S(즉시적용)/A(참고가치)/B(나중에)/C(스킵)
- difficulty: 초급 / 중급 / 고급
- targets: 두근펫 / 매매봇 / 검은별 / 클로드코드 / AI900 / 첼시인스타 / 이모티콘 / 공통
- tags: {tags_list}
- ai_tools: {tools_list}

[지시]
이 스킬의 적절한 카테고리/등급/난이도/태그/AI도구/적용대상을 다시 판정하라.
S 등급은 "지금 바로 무료로 적용 가능"한 최상위만. 모호하면 A로 보수적 판정.

[응답 JSON only — 코드블록 X]
{{
  "category": "...",
  "grade": "S",
  "difficulty": "중급",
  "targets": ["..."],
  "tags": ["..."],
  "ai_tools": ["..."]
}}
"""
    raw = ""
    try:
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"},
        )
        resp = model.generate_content(prompt)
        raw = resp.text or ""
    except Exception as e:  # noqa: BLE001
        log.warning("Gemini 재평가 실패: %s → Gemma 4 폴백", e)

    if not raw:
        raw = call_gemma_json(prompt) or ""
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:  # noqa: BLE001
        return None


def cmd_fix_meta(pages: list[dict], dry: bool = False) -> int:
    fixed = 0
    for p in pages:
        pid = p["id"]
        title = get_title(p)
        summary = get_rich_text(p, "핵심 요약")
        try:
            body = fetch_blocks(pid)
        except NotionError as e:
            print(f"  ⚠️ {title[:40]:<40s} 본문 fetch 실패: {e}")
            continue

        result = _gemini_reclassify(title, summary, body)
        if not result:
            continue

        cur_cat = get_select(p, "카테고리")
        cur_grade = get_select(p, "등급").split("-")[0]
        cur_diff = get_select(p, "난이도")

        new_cat = CATEGORY_TO_DB.get(result.get("category", ""), cur_cat)
        new_grade = result.get("grade", cur_grade)
        new_diff = DIFFICULTY_TO_DB.get(result.get("difficulty", ""), cur_diff)
        new_tags = [t for t in result.get("tags", []) if t in DB_TAGS][:10]
        new_tools = [t for t in result.get("ai_tools", []) if t in DB_AI_TOOLS][:10]
        new_targets = [t for t in result.get("targets", []) if t in DB_TARGETS][:5] or ["공통"]

        changes = []
        props_update: dict = {}
        if new_cat != cur_cat:
            changes.append(f"카테고리 {cur_cat} → {new_cat}")
            props_update["카테고리"] = {"select": {"name": new_cat}}
        grade_label = {"S": "즉시적용", "A": "참고가치", "B": "나중에", "C": "스킵"}.get(new_grade, "")
        new_grade_full = f"{new_grade}-{grade_label}" if grade_label else None
        if new_grade_full and new_grade_full.split("-")[0] != cur_grade:
            changes.append(f"등급 {cur_grade} → {new_grade}")
            props_update["등급"] = {"select": {"name": new_grade_full}}
        if new_diff != cur_diff:
            changes.append(f"난이도 {cur_diff} → {new_diff}")
            props_update["난이도"] = {"select": {"name": new_diff}}
        if set(new_tags) != set(get_multi(p, "태그")):
            changes.append(f"태그 {len(new_tags)}개")
            props_update["태그"] = {"multi_select": [{"name": t} for t in new_tags]}
        if set(new_tools) != set(get_multi(p, "AI 도구")):
            changes.append(f"AI도구 {len(new_tools)}개")
            props_update["AI 도구"] = {"multi_select": [{"name": t} for t in new_tools]}
        if set(new_targets) != set(get_multi(p, "적용 대상")):
            changes.append(f"적용대상 {','.join(new_targets)}")
            props_update["적용 대상"] = {"multi_select": [{"name": t} for t in new_targets]}

        if not changes:
            print(f"  ✓ {title[:50]:<50s} (변경 없음)")
            continue
        print(f"  → {title[:50]:<50s} | {' · '.join(changes)}")
        if not dry and props_update:
            try:
                _request("PATCH", f"pages/{pid}", {"properties": props_update}, "메타 갱신")
                fixed += 1
                time.sleep(0.3)
            except NotionError as e:
                print(f"     ❌ 실패: {e}")
    print(f"\n총 {fixed}건 메타 갱신 (dry={dry})")
    return fixed


# ── 명령: polish-body — TEMPLATE.md v1 8섹션 표준 ──────
BODY_TEMPLATE = """> **TL;DR** — {tldr}

> **메타** 등급 {grade} · 카테고리 {category} · 난이도 {difficulty}
> **도구** {tools}
> **적용 대상** {targets}

---

## 🎯 When to use (언제 쓰는가)

{when}

## 🔑 How it works (작동 원리)

{pattern}

## 🛠 Steps (적용 단계)

{steps}

## 💡 Examples (예시)

{examples}

## 🏢 두근 환경 적용

{doogeun}

## ⚠️ Caveats (주의사항)

{caveats}

## 📎 Sources (출처)

{sources}
"""


def _gemini_polish_body(
    title: str, body_md: str, source_url: str,
    grade: str = "S", category: str = "기타", difficulty: str = "중급",
    tools: list[str] | None = None, targets: list[str] | None = None,
) -> Optional[str]:
    """본문을 TEMPLATE.md v1 8섹션으로 재구성. AI + 사용자 양쪽 가독성."""
    try:
        import google.generativeai as genai
    except ImportError:
        genai = None  # type: ignore
    api_key = os.getenv("GEMINI_API_KEY")
    if genai and api_key:
        genai.configure(api_key=api_key)

    tools_str = ", ".join(tools or []) or "도구무관"
    targets_str = ", ".join(targets or []) or "공통"

    prompt = f"""너는 두근컴퍼니의 AI 스킬 큐레이터다. TEMPLATE.md v1 표준에 따라 본문 재구성.

[스킬 제목] {title}
[원본 출처] {source_url}
[기존 본문]
{body_md[:15000]}

[목표]
이 본문을 두 종류 독자에게 모두 잘 읽히도록 재구성:
1. **AI 에이전트** — 섹션 헤더 고정, 짧은 문장, 코드/표 그대로, 메타 명시
2. **일반 사용자(두근)** — 한눈에 핵심, 단계별 적용, 두근 환경 매핑

[표준 8섹션 — JSON으로 응답]
{{
  "tldr": "이 스킬은 [언제] [무엇을] 한다. 2문장 이내. (TL;DR 한 줄)",
  "when": "🎯 When to use — bullet 3개 이내. '- 이런 상황일 때' 형식",
  "pattern": "🔑 How it works — 작동 원리/공식/메커니즘. 명령어는 ```코드블록```",
  "steps": "🛠 Steps — 1) 2) 3) 번호 단계. 두근(초보)도 따라할 수 있게",
  "examples": "💡 Examples — 실제 입력→출력. 표/코드 가능",
  "doogeun": "🏢 두근 환경 적용 — 두근펫/매매봇/검은별/콘텐츠 중 관련 프로젝트별 매핑. 최소 1개",
  "caveats": "⚠️ Caveats — 한도/유료/실패 케이스. bullet",
  "sources": "📎 Sources — 원본 링크 + 저자/날짜"
}}

[규칙]
- 광고/홍보/외부 도구 추천은 제거
- 두근컴퍼니 환경(Claude Max, Gemini 무료, Mac Mini M4)에 맞게
- 모든 섹션은 한국어, 마크다운 자유 사용 (## ### - 1. ```)
- 비어있는 섹션은 "(해당 없음)" 으로 표시 — 빈 문자열 X
- 사용자가 정성껏 쓴 표·예시·이모지 분류는 최대한 보존

JSON only — 코드블록 없이.
"""
    raw = ""
    try:
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"},
        )
        resp = model.generate_content(prompt)
        raw = resp.text or ""
    except Exception as e:  # noqa: BLE001
        log.warning("Gemini polish 실패: %s → Gemma 4 폴백", e)

    if not raw:
        raw = call_gemma_json(prompt) or ""
    if not raw:
        return None
    try:
        data = json.loads(raw)
        return BODY_TEMPLATE.format(
            tldr=data.get("tldr", "(없음)"),
            grade=grade,
            category=category,
            difficulty=difficulty,
            tools=tools_str,
            targets=targets_str,
            when=data.get("when", "(해당 없음)"),
            pattern=data.get("pattern", "(해당 없음)"),
            steps=data.get("steps", "(해당 없음)"),
            examples=data.get("examples", "(해당 없음)"),
            doogeun=data.get("doogeun", "(해당 없음)"),
            caveats=data.get("caveats", "(해당 없음)"),
            sources=data.get("sources", source_url),
        )
    except Exception as e:  # noqa: BLE001
        log.warning("polish JSON 파싱 실패: %s", e)
        return None


def _md_to_blocks(md: str) -> list[dict]:
    """간단 마크다운 → Notion 블록."""
    blocks = []
    in_code = False
    code_lang = ""
    code_buf: list[str] = []
    for line in md.splitlines():
        if line.strip().startswith("```"):
            if in_code:
                # close
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": "\n".join(code_buf)[:1900]}}],
                        "language": code_lang or "plain text",
                    },
                })
                in_code = False
                code_buf = []
                code_lang = ""
            else:
                in_code = True
                code_lang = line.strip().lstrip("`").strip() or ""
            continue
        if in_code:
            code_buf.append(line)
            continue
        s = line.strip()
        if not s:
            continue
        if s.startswith("# "):
            blocks.append(_b("heading_1", s[2:]))
        elif s.startswith("## "):
            blocks.append(_b("heading_2", s[3:]))
        elif s.startswith("### "):
            blocks.append(_b("heading_3", s[4:]))
        elif re.match(r"^\d+\.\s", s):
            blocks.append(_b("numbered_list_item", re.sub(r"^\d+\.\s", "", s)))
        elif s.startswith(("- ", "* ")):
            blocks.append(_b("bulleted_list_item", s[2:]))
        else:
            blocks.append(_b("paragraph", s[:1900]))
        if len(blocks) >= 95:
            break
    return blocks


def _b(btype: str, text: str) -> dict:
    return {
        "object": "block",
        "type": btype,
        btype: {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def cmd_polish_body(pages: list[dict], dry: bool = False) -> int:
    """모든 페이지 본문을 TEMPLATE.md v1 8섹션으로 재구성."""
    fixed = 0
    for p in pages:
        pid = p["id"]
        title = get_title(p)
        url = get_url(p, "출처 URL")
        grade = get_select(p, "등급").split("-")[0] or "S"
        category = get_select(p, "카테고리") or "기타"
        difficulty = get_select(p, "난이도") or "🟡 중급"
        tools = get_multi(p, "AI 도구")
        targets = get_multi(p, "적용 대상")
        try:
            body = fetch_blocks(pid)
        except NotionError as e:
            print(f"  ⚠️ {title[:40]:<40s} 본문 fetch 실패: {e}")
            continue
        if len(body) < 100:
            print(f"  ✓ {title[:50]:<50s} (본문 짧음, 스킵)")
            continue

        new_body = _gemini_polish_body(
            title, body, url,
            grade=grade, category=category, difficulty=difficulty,
            tools=tools, targets=targets,
        )
        if not new_body:
            print(f"  ❌ {title[:50]:<50s} Gemini 응답 실패")
            continue

        print(f"  → {title[:50]:<50s} ({len(body)} → {len(new_body)}자)")
        if dry:
            continue
        # 기존 블록 삭제 → 새 블록 추가
        try:
            children = _request("GET", f"blocks/{pid}/children?page_size=100", context="블록 조회")
            for c in children.get("results", []):
                try:
                    _request("DELETE", f"blocks/{c['id']}", context="블록 삭제")
                except NotionError:
                    pass
            _request("PATCH", f"blocks/{pid}/children",
                     {"children": _md_to_blocks(new_body)}, "본문 재구성")
            fixed += 1
            time.sleep(0.5)
        except NotionError as e:
            print(f"     ❌ 실패: {e}")
    print(f"\n총 {fixed}건 본문 재구성 (dry={dry})")
    return fixed


# ── 명령: find-dupes ─────────────────────────────────────
def cmd_find_dupes(pages: list[dict]) -> None:
    """URL/제목 기반 중복 후보 리스트."""
    urls: dict[str, list[dict]] = {}
    titles: dict[str, list[dict]] = {}
    for p in pages:
        url = get_url(p, "출처 URL")
        title = get_title(p)
        _, rest = split_title_emoji(title)
        norm = re.sub(r'[^가-힣a-zA-Z0-9]', '', rest.lower())[:20]
        if url:
            urls.setdefault(url, []).append(p)
        if norm:
            titles.setdefault(norm, []).append(p)

    dup_urls = {k: v for k, v in urls.items() if len(v) > 1}
    dup_titles = {k: v for k, v in titles.items() if len(v) > 1}

    if dup_urls:
        print("\n🚨 같은 URL을 가진 중복:")
        for u, lst in dup_urls.items():
            print(f"  URL: {u}")
            for p in lst:
                print(f"    · {p['id'][:8]} | {get_title(p)}")
    if dup_titles:
        print("\n🟡 제목 유사 중복 후보:")
        for k, lst in dup_titles.items():
            print(f"  [{k}]")
            for p in lst:
                print(f"    · {p['id'][:8]} | {get_title(p)}")
    if not dup_urls and not dup_titles:
        print("\n✅ 중복 없음")


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = argparse.ArgumentParser(description="Notion DB 전수 큐레이션")
    parser.add_argument(
        "command",
        choices=["analyze", "fix-emoji", "fix-meta", "polish-body", "find-dupes", "all"],
    )
    parser.add_argument("--dry", action="store_true", help="실제 변경 없이 분석만")
    parser.add_argument("--limit", type=int, default=0, help="처리할 페이지 수 제한 (0=전체)")
    args = parser.parse_args()

    print("📡 DB 전체 페이지 조회 중...")
    try:
        pages = fetch_all_pages()
    except NotionError as e:
        print(f"❌ 조회 실패: {e}")
        print(f"💡 {e.hint}")
        return 1
    print(f"✓ {len(pages)}건 로드\n")

    if args.limit > 0:
        pages = pages[:args.limit]
        print(f"⚠️ --limit {args.limit} 적용 → {len(pages)}건만 처리\n")

    if args.command == "analyze":
        cmd_analyze(pages)
    elif args.command == "fix-emoji":
        cmd_fix_emoji(pages, dry=args.dry)
    elif args.command == "fix-meta":
        cmd_fix_meta(pages, dry=args.dry)
    elif args.command == "polish-body":
        cmd_polish_body(pages, dry=args.dry)
    elif args.command == "find-dupes":
        cmd_find_dupes(pages)
    elif args.command == "all":
        print("─" * 60); print("1단계: 분석"); print("─" * 60)
        cmd_analyze(pages)
        print("\n" + "─" * 60); print("2단계: 이모지 정리"); print("─" * 60)
        cmd_fix_emoji(pages, dry=args.dry)
        print("\n" + "─" * 60); print("3단계: 카테고리/등급 재평가"); print("─" * 60)
        cmd_fix_meta(pages, dry=args.dry)
        print("\n" + "─" * 60); print("4단계: 본문 8섹션 통일"); print("─" * 60)
        cmd_polish_body(pages, dry=args.dry)
        print("\n" + "─" * 60); print("5단계: 중복 점검"); print("─" * 60)
        cmd_find_dupes(pages)
    return 0


if __name__ == "__main__":
    sys.exit(main())
