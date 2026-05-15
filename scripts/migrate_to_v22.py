"""Notion DB 전체 페이지를 v2.2 가독성 형식으로 마이그레이션.

변환 규칙 (LLM 없이 단순 매핑):
1. YAML 프론트매터 제거 (--- 사이 블록)
2. 최상위 H1 제거 (Notion 제목 property와 중복)
3. 영문 헤더 → 한국어 헤더 (## When to use → ## 🎯 언제 쓰나)
4. "(해당 없음)" 등 placeholder 줄 + 그 헤더 섹션 제거
5. 메타 callout 한 묶음 추가 (등급/카테고리/도구/적용 대상)
"""
from __future__ import annotations

import os
import re
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API = "https://api.notion.com/v1"
H = {
    "Authorization": f"Bearer {os.environ['NOTION_API_KEY']}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
DB_ID = os.environ['NOTION_DB_ID']

# 헤더 매핑 — 옛 → v2.2
HEADER_MAP = {
    # v1/v2.1 영문 헤더
    "## ⚡ TL;DR": None,  # 본문에서 제거 (메타 callout으로 흡수)
    "## 🎯 When to use (언제 쓰는가)": "## 🎯 언제 쓰나",
    "## 🎯 When to use": "## 🎯 언제 쓰나",
    "## 🔑 How it works (작동 원리)": "## 🔑 원리",
    "## 🔑 How it works": "## 🔑 원리",
    "## 🔑 핵심 패턴": "## 🔑 원리",
    "## 🛠 Steps (적용 단계)": "## 🛠 단계",
    "## 🛠 Steps": "## 🛠 단계",
    "## 🛠 적용 단계": "## 🛠 단계",
    "## 💡 Examples (예시)": "## 💡 예시",
    "## 💡 Examples": "## 💡 예시",
    "## 🏢 두근 환경 적용": "## 🏢 두근컴퍼니 적용",
    "## 🏢 두근컴퍼니 환경 적용": "## 🏢 두근컴퍼니 적용",
    "## ⚠️ Caveats (주의사항)": "## ⚠️ 주의",
    "## ⚠️ Caveats": "## ⚠️ 주의",
    "## ⚠️ 주의사항": "## ⚠️ 주의",
    "## 📎 Sources (출처)": "## 📎 출처",
    "## 📎 Sources": "## 📎 출처",
    # 사용자 직접 작성 헤더
    "## 핵심 요약": None,  # 메타 callout으로 흡수
    "## 상세 내용": "## 🔑 원리",
    "## 적용 방법": "## 🛠 단계",
    "## 💡 아이디어 & 활용": "## 🏢 두근컴퍼니 적용",
    "## 출처": "## 📎 출처",
    "## 핵심 원칙": "## 🔑 원리",
    "## 보너스: [MEMORY.md](http://MEMORY.md) 활용법": "## 💡 예시",
}

# 메타 정보 섹션 제거 패턴 (v2.1에서 추가됐던 것)
META_INFO_RE = re.compile(
    r'## 메타 정보.*?(?=\n## |\Z)', re.DOTALL
)

# "(해당 없음)" 줄 (빈 섹션 표시)
EMPTY_MARKERS = ["(해당 없음)", "(없음)", "(없음.)", "(해당없음)", "(N/A)"]


def fetch_page_with_blocks(page_id: str) -> dict:
    """페이지 properties + 모든 블록을 fetch."""
    p = requests.get(f"{API}/pages/{page_id}", headers=H, timeout=20).json()
    blocks = []
    cursor = None
    while True:
        path = f"{API}/blocks/{page_id}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        d = requests.get(path, headers=H, timeout=20).json()
        blocks.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
    return {"page": p, "blocks": blocks}


def blocks_to_markdown(blocks: list) -> str:
    """Notion 블록 → 마크다운."""
    lines: list[str] = []
    for b in blocks:
        t = b.get("type", "?")
        c = b.get(t, {})
        rt = c.get("rich_text", [])
        text = "".join(r.get("plain_text", "") for r in rt)
        if t == "heading_1":
            lines.append(f"# {text}")
        elif t == "heading_2":
            lines.append(f"## {text}")
        elif t == "heading_3":
            lines.append(f"### {text}")
        elif t == "bulleted_list_item":
            lines.append(f"- {text}")
        elif t == "numbered_list_item":
            lines.append(f"1. {text}")
        elif t == "quote":
            lines.append(f"> {text}")
        elif t == "code":
            lang = c.get("language", "")
            lines.append(f"```{lang}\n{text}\n```")
        elif t == "divider":
            lines.append("---")
        elif t == "paragraph":
            if text.strip():
                lines.append(text)
        elif t == "table":
            lines.append("<!-- table 블록 생략 (보존 어려움) -->")
        else:
            if text.strip():
                lines.append(text)
    return "\n\n".join(lines)


def md_to_blocks(md: str) -> list[dict]:
    """마크다운 → Notion 블록 (단순)."""
    blocks: list[dict] = []
    in_code = False
    code_lang = ""
    code_buf: list[str] = []
    for line in md.splitlines():
        if line.strip().startswith("```"):
            if in_code:
                blocks.append({
                    "object": "block", "type": "code",
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
        block: dict
        if s.startswith("> "):
            block = _b("quote", s[2:])
        elif s.startswith("# "):
            block = _b("heading_1", s[2:])
        elif s.startswith("## "):
            block = _b("heading_2", s[3:])
        elif s.startswith("### "):
            block = _b("heading_3", s[4:])
        elif s.startswith(("- ", "* ")):
            block = _b("bulleted_list_item", s[2:])
        elif re.match(r"^\d+\.\s", s):
            block = _b("numbered_list_item", re.sub(r"^\d+\.\s", "", s))
        elif s == "---":
            block = {"object": "block", "type": "divider", "divider": {}}
        else:
            block = _b("paragraph", s[:1900])
        blocks.append(block)
        if len(blocks) >= 95:
            break
    return blocks


def _b(btype: str, text: str) -> dict:
    return {
        "object": "block", "type": btype,
        btype: {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def transform(md: str, meta: dict) -> str:
    """v2.2 변환."""
    # 1. YAML 프론트매터 제거
    if md.lstrip().startswith("---"):
        m = re.search(r"^\s*---\n.*?\n---\s*\n", md, re.DOTALL)
        if m:
            md = md[m.end():]
    # 2. 첫 H1 제거
    md = re.sub(r"^\s*#\s+[^\n]+\n", "", md, count=1)
    # 3. 메타 정보 섹션 제거
    md = META_INFO_RE.sub("", md)
    # 4. 헤더 매핑 — None이면 그 섹션 자체 제거
    lines = md.split("\n")
    out_lines: list[str] = []
    skip_until_next_h2 = False
    for line in lines:
        stripped = line.strip()
        # 매핑 대상 헤더?
        mapped = HEADER_MAP.get(stripped)
        if stripped in HEADER_MAP:
            if mapped is None:
                skip_until_next_h2 = True
                continue
            else:
                skip_until_next_h2 = False
                out_lines.append(mapped)
                continue
        # 다음 H2가 나오면 skip 종료
        if skip_until_next_h2 and stripped.startswith("## "):
            skip_until_next_h2 = False
            out_lines.append(line)
            continue
        if skip_until_next_h2:
            continue
        # "(해당 없음)" 마커가 있는 줄 → 그 섹션 통째로 제거
        if any(m in stripped for m in EMPTY_MARKERS):
            # 직전 헤더(##)도 제거
            while out_lines and not out_lines[-1].startswith("## ") and out_lines[-1].strip() == "":
                out_lines.pop()
            if out_lines and out_lines[-1].startswith("## "):
                out_lines.pop()
            continue
        out_lines.append(line)
    body = "\n".join(out_lines).strip()

    # 5. 메타 callout 위에 prepend
    grade = meta.get("grade", "S").split("-")[0]
    cat = meta.get("cat", "기타")
    diff = meta.get("diff", "🟡 중급")
    tools = " · ".join(meta.get("tools", [])[:5]) or "도구무관"
    targets = " · ".join(meta.get("targets", [])[:5]) or "공통"
    title = meta.get("title", "")

    # TL;DR 추출 — 본문 첫 paragraph 또는 핵심 요약 첫 줄
    tldr = ""
    for line in body.split("\n"):
        s = line.strip()
        if s and not s.startswith(("#", "-", "*", ">", "1.", "2.", "3.")):
            tldr = s[:200]
            break

    meta_block = (
        f"> **💡 {tldr or title}**\n"
        f">\n"
        f"> **{grade}** · {cat} · {diff}\n"
        f"> 🤖 {tools} → 🎯 {targets}\n\n"
    )

    # 본문에서 위 tldr 줄 제거 (메타 callout과 중복)
    if tldr:
        body = body.replace(tldr, "", 1).strip()
        # 연속 빈 줄 정리
        body = re.sub(r"\n{3,}", "\n\n", body)

    return meta_block + body


def replace_blocks(page_id: str, new_blocks: list[dict]) -> bool:
    """기존 블록 모두 삭제 + 새 블록 추가."""
    # 기존 블록 ID 수집
    cursor = None
    old_ids: list[str] = []
    while True:
        path = f"{API}/blocks/{page_id}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        d = requests.get(path, headers=H, timeout=20).json()
        old_ids.extend(b["id"] for b in d.get("results", []))
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")

    # 삭제 (best effort)
    for bid in old_ids:
        try:
            requests.delete(f"{API}/blocks/{bid}", headers=H, timeout=15)
        except Exception:
            pass
        time.sleep(0.05)

    # 새 블록 추가 (100개씩 batch)
    for i in range(0, len(new_blocks), 100):
        chunk = new_blocks[i:i+100]
        r = requests.patch(
            f"{API}/blocks/{page_id}/children",
            headers=H,
            json={"children": chunk},
            timeout=30,
        )
        if r.status_code >= 400:
            print(f"     ❌ 블록 추가 실패: {r.status_code} {r.text[:120]}")
            return False
        time.sleep(0.2)
    return True


def main(target_ids: list[str] | None = None) -> int:
    # 18건 조회
    r = requests.post(f"{API}/databases/{DB_ID}/query", headers=H, json={
        "sorts": [{"property": "마지막 업데이트", "direction": "ascending"}],
        "page_size": 50,
    }).json()
    pages = r.get("results", [])
    print(f"📡 총 {len(pages)}건 발견\n")

    fixed = 0
    failed = 0
    for i, p in enumerate(pages, 1):
        pid = p["id"]
        if target_ids and pid not in target_ids:
            continue
        pr = p["properties"]
        title = "".join(t["plain_text"] for t in pr.get("스킬명", {}).get("title", []))
        cat = (pr.get("카테고리", {}).get("select") or {}).get("name", "")
        grade = (pr.get("등급", {}).get("select") or {}).get("name", "")
        diff = (pr.get("난이도", {}).get("select") or {}).get("name", "")
        tools = [t["name"] for t in pr.get("AI 도구", {}).get("multi_select", [])]
        targets = [t["name"] for t in pr.get("적용 대상", {}).get("multi_select", [])]
        meta = {
            "title": title, "cat": cat, "grade": grade, "diff": diff,
            "tools": tools, "targets": targets,
        }

        print(f"[{i:2d}/{len(pages)}] {title[:45]}")
        try:
            data = fetch_page_with_blocks(pid)
            md = blocks_to_markdown(data["blocks"])
            new_md = transform(md, meta)
            new_blocks = md_to_blocks(new_md)
            print(f"          블록 {len(data['blocks'])} → {len(new_blocks)} (md {len(md)} → {len(new_md)}자)")
            ok = replace_blocks(pid, new_blocks)
            if ok:
                fixed += 1
                print(f"          ✅ 적용\n")
            else:
                failed += 1
                print(f"          ❌ 실패\n")
        except Exception as e:
            failed += 1
            print(f"          ❌ 예외: {e}\n")
        time.sleep(0.5)

    print(f"\n총 {fixed}건 마이그레이션 성공, {failed}건 실패")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    target_ids = sys.argv[1:] if len(sys.argv) > 1 else None
    sys.exit(main(target_ids))
