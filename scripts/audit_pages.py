"""전체 페이지 가독성/일관성 종합 점검.

체크 항목:
1. 첫 블록 = H2 (메타 quote 없음)
2. 표준 헤더 사용 (한글 친화)
3. 빈 섹션 (H2 → H2 인접)
4. 코드 language 유효성
5. 본문 길이
6. 페이지 아이콘 카테고리 매핑 일치
7. 한글/영문 혼합 헤더 잔존
"""
from __future__ import annotations

import os
import re
import sys

import requests
from dotenv import load_dotenv
from pathlib import Path
from scripts.notion_paging import query_all_pages

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API = "https://api.notion.com/v1"
H = {
    "Authorization": f"Bearer {os.environ['NOTION_API_KEY']}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
DB_ID = os.environ["NOTION_DB_ID"]

STANDARD_HEADERS = {
    "🔑 어떻게 작동하나요?",
    "🛠 따라 하기 (단계별)",
    "💡 실제 예시",
    "⚡ 이렇게 쓰면 효과적이다",
    "⚠️ 주의할 점",
    "📎 출처",
    "📌 원본 코드/명령어 (자동 보존)",  # rescue 섹션
    # 옛 헤더 (호환성)
    "🎯 어떨 때 쓰나요?",
    "🏢 두근컴퍼니에서 어떻게 활용?",
}

CATEGORY_ICON = {
    "프롬프트": "💬", "자동화": "🤖", "콘텐츠": "🎬", "디자인": "🎨",
    "개발": "💻", "업무": "⚡", "기타": "📦",
}

NOTION_CODE_LANGS = {
    "abap","arduino","bash","basic","c","clojure","coffeescript","c++","c#","css","dart",
    "diff","docker","elixir","elm","erlang","flow","fortran","f#","gherkin","glsl","go",
    "graphql","groovy","haskell","html","java","javascript","json","julia","kotlin","latex",
    "less","lisp","livescript","lua","makefile","markdown","markup","matlab","mermaid","nix",
    "notion formula","objective-c","ocaml","pascal","perl","php","plain text","powershell",
    "prolog","protobuf","python","r","reason","ruby","rust","sass","scala","scheme","scss",
    "shell","sql","swift","typescript","vb.net","verilog","vhdl","visual basic","webassembly","yaml",
}


def block_text(b: dict) -> str:
    t = b.get("type", "?")
    return "".join(r.get("plain_text", "") for r in b.get(t, {}).get("rich_text", []))


def get_all_blocks(pid: str) -> list[dict]:
    blocks = []
    cursor = None
    while True:
        path = f"{API}/blocks/{pid}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        d = requests.get(path, headers=H, timeout=30).json()
        blocks.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
    return blocks


def audit_page(p: dict) -> dict:
    pid = p["id"]
    pr = p["properties"]
    title = "".join(t["plain_text"] for t in pr.get("스킬명", {}).get("title", []))
    category = (pr.get("카테고리", {}).get("select") or {}).get("name", "")
    icon = (p.get("icon") or {}).get("emoji", "")
    expected_icon = CATEGORY_ICON.get(category, "📦")

    blocks = get_all_blocks(pid)
    issues: list[str] = []

    # 1. 첫 블록 — quote 면 메타 박스 잔존
    if blocks and blocks[0].get("type") == "quote":
        issues.append(f"❌ 첫 블록 quote (메타 박스 잔존?)")

    # 2. 헤더 표준 일치
    h2_texts: list[str] = []
    nonstandard_headers: list[str] = []
    eng_residue: list[str] = []
    for b in blocks:
        if b.get("type") != "heading_2":
            continue
        text = block_text(b).strip()
        h2_texts.append(text)
        if text not in STANDARD_HEADERS:
            nonstandard_headers.append(text)
        # 영문 부제 잔존
        if re.search(r"\((When|How|Steps|Examples|Caveats|Sources|언제 쓰는가|작동 원리|적용 단계|예시|주의사항|출처)\)", text):
            eng_residue.append(text)
    if nonstandard_headers:
        issues.append(f"⚠️ 비표준 H2 {len(nonstandard_headers)}개: {nonstandard_headers[:2]}")
    if eng_residue:
        issues.append(f"⚠️ 영문 부제 잔존: {eng_residue[:2]}")

    # 3. 빈 섹션 — H2 직후 또 H2 (또는 divider 끼고 H2)
    empty_sections = []
    for i, b in enumerate(blocks):
        if b.get("type") != "heading_2":
            continue
        # 다음 비-divider 블록
        for j in range(i + 1, len(blocks)):
            nt = blocks[j].get("type")
            if nt == "divider":
                continue
            if nt == "heading_2":
                empty_sections.append(block_text(b).strip())
            break
        else:
            # 마지막 헤더
            empty_sections.append(block_text(b).strip())
    if empty_sections:
        issues.append(f"⚠️ 빈 섹션: {empty_sections[:2]}")

    # 4. 코드블록 language
    invalid_langs = []
    for b in blocks:
        if b.get("type") != "code":
            continue
        lang = b.get("code", {}).get("language", "")
        if lang and lang not in NOTION_CODE_LANGS:
            invalid_langs.append(lang)
    if invalid_langs:
        issues.append(f"⚠️ 유효하지 않은 code language: {set(invalid_langs)}")

    # 5. 본문 길이
    total_text = "\n".join(block_text(b) for b in blocks)
    if len(total_text) < 200:
        issues.append(f"⚠️ 본문 너무 짧음 ({len(total_text)}자)")

    # 6. 아이콘 일치
    if icon != expected_icon:
        issues.append(f"⚠️ 아이콘 불일치 (현재 {icon!r} / 예상 {expected_icon!r} for {category})")

    # 7. 메타 quote 잔존 (어디든)
    meta_quote_count = 0
    for b in blocks[:10]:
        if b.get("type") == "quote":
            t = block_text(b)
            if any(kw in t for kw in ["TL;DR", "메타", "💡", "⚡", "🎯 무엇", "🤖", "S · ", "A · "]):
                meta_quote_count += 1
    if meta_quote_count > 0:
        issues.append(f"⚠️ 메타 quote 잔존 {meta_quote_count}개")

    return {
        "title": title,
        "blocks": len(blocks),
        "h2_count": len(h2_texts),
        "text_chars": len(total_text),
        "issues": issues,
        "category": category,
        "icon": icon,
        "expected_icon": expected_icon,
    }


def main() -> int:
    pages = query_all_pages(API, H, DB_ID)
    print(f"📡 {len(pages)}건 전수 검사\n")

    perfect = 0
    issues_total = 0
    for i, p in enumerate(pages, 1):
        res = audit_page(p)
        status = "✅" if not res["issues"] else "🔍"
        if not res["issues"]:
            perfect += 1
        else:
            issues_total += len(res["issues"])
        print(f"  [{i:2d}] {status} {res['title'][:45]:<45} | {res['blocks']:>3}블록 / {res['h2_count']}H2 / {res['text_chars']:>4}자")
        for issue in res["issues"]:
            print(f"        {issue}")

    print(f"\n📊 요약: 완벽 {perfect}/{len(pages)} · 총 이슈 {issues_total}건")
    return 0


if __name__ == "__main__":
    sys.exit(main())
