"""중복 페이지 통폐합 스크립트.

대표 페이지를 하나 고르고, 나머지 페이지의 유니크 정보를 LLM 으로 추출해서
대표에 append + 소스 URL 통합. 나머지는 Notion archive + 로컬 SKILL.md 정리.

사용:
    python -m scripts.merge_duplicates --plan /tmp/merge_plan.json
    python -m scripts.merge_duplicates --plan /tmp/merge_plan.json --apply

plan 파일 형식:
    [
      {"group_name":"AI 루프",
       "representative":"39914362-1b4b-....",
       "members":["39914362-...", "39814362-...", ...]},
      ...
    ]
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

SKILLS_GLOBAL = Path(os.path.expanduser("~/.claude/skills"))
SKILLS_MIRROR = Path(__file__).resolve().parents[1] / "skills"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {os.environ['NOTION_API_KEY']}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _load_env() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _fetch_page(pid: str) -> dict:
    r = requests.get(f"{NOTION_API}/pages/{pid}", headers=_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def _fetch_children(bid: str) -> list[dict]:
    """모든 자식 블록 (페이징)."""
    out: list[dict] = []
    start: Optional[str] = None
    while True:
        params = {"page_size": 100}
        if start:
            params["start_cursor"] = start
        r = requests.get(
            f"{NOTION_API}/blocks/{bid}/children",
            headers=_headers(),
            params=params,
            timeout=30,
        )
        r.raise_for_status()
        d = r.json()
        out.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        start = d.get("next_cursor")
    return out


def _block_to_md(b: dict, depth: int = 0) -> str:
    t = b.get("type", "")
    node = b.get(t) or {}
    rt = node.get("rich_text") or []
    text = "".join(a.get("plain_text", "") for a in rt if isinstance(a, dict))
    pref = "  " * depth
    if t == "heading_1":
        return f"# {text}"
    if t == "heading_2":
        return f"## {text}"
    if t == "heading_3":
        return f"### {text}"
    if t == "bulleted_list_item":
        return f"{pref}- {text}"
    if t == "numbered_list_item":
        return f"{pref}1. {text}"
    if t == "code":
        lang = node.get("language", "")
        return f"```{lang}\n{text}\n```"
    if t == "quote":
        return f"> {text}"
    if t == "callout":
        icon = ((node.get("icon") or {}).get("emoji")) or "💡"
        return f"> {icon} {text}"
    if t == "divider":
        return "---"
    return text


def _page_markdown(pid: str) -> str:
    blocks = _fetch_children(pid)
    lines = []
    for b in blocks:
        s = _block_to_md(b)
        if s.strip():
            lines.append(s)
        if b.get("has_children") and b["type"] not in ("column_list", "column"):
            child_lines = []
            try:
                for cb in _fetch_children(b["id"]):
                    cs = _block_to_md(cb, depth=1)
                    if cs.strip():
                        child_lines.append(cs)
            except Exception:  # noqa: BLE001
                pass
            lines.extend(child_lines)
    return "\n\n".join(lines)


def _page_title(page: dict) -> str:
    for _, pv in (page.get("properties") or {}).items():
        if pv.get("type") == "title":
            return "".join(a.get("plain_text", "") for a in pv.get("title", []))
    return ""


def _page_url(page: dict) -> str:
    pv = (page.get("properties") or {}).get("출처 URL") or {}
    if pv.get("type") == "url":
        return pv.get("url") or ""
    return "".join(a.get("plain_text", "") for a in pv.get("rich_text", []))


def _extract_unique_with_gemma(rep_md: str, other_md: str, other_title: str) -> str:
    """대표 본문에 없는 유니크 정보만 Gemma 로 추출."""
    from scripts.analyzer.gemini import call_gemma_json

    prompt = f"""너는 문서 통폐합 도우미다. 아래 두 문서를 비교하고, "보조" 에만 있는 유니크한 정보만 markdown 으로 뽑아라.

**추출 대상**:
- 대표에 없는 실무 팁 / 주의사항 / 단계 세부 설명
- 다른 사용 예시나 시나리오 (같은 예시는 제외)
- 코드 블록 / 명령어 / 프롬프트 스니펫 (대표에 이미 있으면 제외)
- 대표에서 다루지 않은 도구 이름·링크·수치

**제외 대상**:
- 대표와 같은 개념·같은 문장의 다른 표현 (paraphrase 는 제외)
- 페이지 메타·헤더·"이 스킬은..." 같은 소개문
- 인사말·마무리멘트

응답은 반드시 JSON:
{{
  "additions": "## 📌 [{other_title}] 에서 보강\\n\\n<추출한 유니크 정보 markdown. 없으면 빈 문자열>",
  "has_content": true/false
}}

## 대표 본문
{rep_md[:6000]}

## 보조 본문 (제목: {other_title})
{other_md[:6000]}
"""

    try:
        raw = call_gemma_json(prompt, temperature=0.2)
        if not raw:
            return ""
        # partial JSON 보호 — 우리가 만든 _extract_json 활용
        from scripts.analyzer.gemini import _extract_json
        d = _extract_json(raw)
        if not isinstance(d, dict):
            return ""
        if d.get("has_content") is False:
            return ""
        return d.get("additions", "") or ""
    except Exception as e:  # noqa: BLE001
        logger.warning("LLM 유니크 추출 실패 (%s), 스킵", e)
        return ""


def _append_markdown_as_blocks(pid: str, md: str) -> None:
    """markdown 을 간단히 heading/paragraph/code/list 블록으로 변환해서 append."""
    if not md.strip():
        return
    blocks: list[dict] = []
    in_code = False
    code_buf: list[str] = []
    code_lang = ""
    for line in md.splitlines():
        if line.startswith("```"):
            if in_code:
                blocks.append({
                    "object": "block", "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": "\n".join(code_buf)[:2000]}}],
                        "language": code_lang or "plain text",
                    },
                })
                in_code = False; code_buf = []; code_lang = ""
            else:
                in_code = True
                code_lang = line[3:].strip() or "plain text"
            continue
        if in_code:
            code_buf.append(line)
            continue
        s = line.rstrip()
        if not s:
            continue
        if s.startswith("### "):
            blocks.append({"object":"block","type":"heading_3","heading_3":{"rich_text":[{"type":"text","text":{"content":s[4:][:1900]}}]}})
        elif s.startswith("## "):
            blocks.append({"object":"block","type":"heading_2","heading_2":{"rich_text":[{"type":"text","text":{"content":s[3:][:1900]}}]}})
        elif s.startswith("# "):
            blocks.append({"object":"block","type":"heading_2","heading_2":{"rich_text":[{"type":"text","text":{"content":s[2:][:1900]}}]}})
        elif s.lstrip().startswith("- "):
            blocks.append({"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":[{"type":"text","text":{"content":s.lstrip()[2:][:1900]}}]}})
        elif s.lstrip().startswith(("1.","2.","3.","4.","5.","6.","7.","8.","9.")):
            content = s.lstrip()
            idx = content.find(".")
            blocks.append({"object":"block","type":"numbered_list_item","numbered_list_item":{"rich_text":[{"type":"text","text":{"content":content[idx+1:].lstrip()[:1900]}}]}})
        elif s.startswith("> "):
            blocks.append({"object":"block","type":"quote","quote":{"rich_text":[{"type":"text","text":{"content":s[2:][:1900]}}]}})
        else:
            blocks.append({"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":s[:1900]}}]}})
    if in_code and code_buf:
        blocks.append({
            "object":"block","type":"code",
            "code":{"rich_text":[{"type":"text","text":{"content":"\n".join(code_buf)[:2000]}}], "language": code_lang or "plain text"},
        })
    if not blocks:
        return
    # append 100 단위
    for i in range(0, len(blocks), 100):
        chunk = blocks[i:i+100]
        r = requests.patch(f"{NOTION_API}/blocks/{pid}/children", headers=_headers(), json={"children": chunk}, timeout=60)
        if r.status_code >= 400:
            logger.error("append 실패 %s: %s", r.status_code, r.text[:200])
        r.raise_for_status()


def _archive_page(pid: str) -> None:
    r = requests.patch(f"{NOTION_API}/pages/{pid}", headers=_headers(), json={"archived": True}, timeout=30)
    if r.status_code >= 400:
        logger.error("archive 실패 %s: %s", pid[:8], r.text[:200])
    r.raise_for_status()


def _slug_from_page(page: dict) -> str:
    # 프론트매터/파일에서 얻기 힘드니 title 로 매핑. 대신 로컬 SKILL.md 스캔.
    title = _page_title(page)
    url = _page_url(page)
    for base in (SKILLS_GLOBAL, SKILLS_MIRROR):
        if not base.exists(): continue
        for d in base.iterdir():
            if not d.is_dir(): continue
            md = d / "SKILL.md"
            if not md.exists(): continue
            try:
                txt = md.read_text(encoding="utf-8")
            except Exception:  # noqa: BLE001
                continue
            if url and url[:60] in txt:
                return d.name
    return ""


def merge_group(group: dict, apply: bool) -> dict:
    rep_id = group["representative"]
    members = [m for m in group["members"] if m != rep_id]
    rep_page = _fetch_page(rep_id)
    rep_title = _page_title(rep_page)
    rep_md = _page_markdown(rep_id)
    logger.info("그룹 '%s' — 대표 [%s] '%s' 본문 %d자", group.get("group_name",""), rep_id[:8], rep_title, len(rep_md))

    additions: list[str] = []
    archive_ids: list[str] = []
    sources: list[tuple[str, str]] = []  # (title, url)

    for pid in members:
        p = _fetch_page(pid)
        t = _page_title(p); u = _page_url(p)
        md = _page_markdown(pid)
        logger.info("  보조 [%s] '%s' 본문 %d자 — 유니크 추출 중...", pid[:8], t, len(md))
        add = _extract_unique_with_gemma(rep_md, md, t)
        if add.strip():
            additions.append(add)
            logger.info("    → 유니크 %d자", len(add))
        else:
            logger.info("    → 유니크 없음")
        sources.append((t, u))
        archive_ids.append(pid)

    # 대표 페이지에 추가할 markdown 조립
    tail = ""
    if additions:
        tail += "\n\n---\n\n## 📌 유사 페이지에서 보강된 자료\n\n" + "\n\n".join(additions)
    if sources:
        tail += "\n\n---\n\n## 🔗 병합된 원본 출처\n\n"
        for st, su in sources:
            if su:
                tail += f"- [{st}]({su})\n"
            else:
                tail += f"- {st}\n"

    if not apply:
        return {
            "group_name": group.get("group_name",""),
            "representative": rep_id,
            "would_archive": archive_ids,
            "additions_chars": sum(len(a) for a in additions),
            "sources_count": len(sources),
            "tail_preview": tail[:600],
        }

    # 실제 적용
    if tail.strip():
        _append_markdown_as_blocks(rep_id, tail)
        logger.info("  대표 페이지 append 완료 (%d자)", len(tail))
    time.sleep(0.5)

    # 나머지 archive
    for pid in archive_ids:
        try:
            _archive_page(pid)
            logger.info("  archive [%s]", pid[:8])
        except Exception as e:  # noqa: BLE001
            logger.error("  archive 실패 [%s]: %s", pid[:8], e)

    # 로컬 SKILL.md 정리 — 대표는 유지, 나머지 slug 폴더는 .archived 로 rename
    rep_slug = _slug_from_page(rep_page)
    for pid in archive_ids:
        p = _fetch_page(pid)
        slug = _slug_from_page(p)
        if not slug or slug == rep_slug:
            continue
        for base in (SKILLS_GLOBAL, SKILLS_MIRROR):
            d = base / slug
            if d.exists() and d.is_dir():
                dest = base / f"{slug}.archived"
                try:
                    if dest.exists():
                        shutil.rmtree(dest)
                    d.rename(dest)
                    logger.info("  로컬 %s → %s.archived", d, slug)
                except Exception as e:  # noqa: BLE001
                    logger.warning("  로컬 rename 실패 %s: %s", d, e)

    return {
        "group_name": group.get("group_name",""),
        "representative": rep_id,
        "archived": archive_ids,
        "additions_chars": sum(len(a) for a in additions),
        "sources_count": len(sources),
    }


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    parser = argparse.ArgumentParser(description="중복 페이지 통폐합")
    parser.add_argument("--plan", required=True, help="병합 계획 JSON 파일")
    parser.add_argument("--apply", action="store_true", help="실제 적용 (기본 dry-run)")
    args = parser.parse_args()

    _load_env()
    plan = json.load(open(args.plan, encoding="utf-8"))
    results = []
    for group in plan:
        try:
            r = merge_group(group, apply=args.apply)
        except Exception as e:  # noqa: BLE001
            logger.exception("그룹 실패: %s", group.get("group_name",""))
            r = {"group_name": group.get("group_name",""), "error": str(e)}
        results.append(r)

    print("\n=== 결과 ===")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
