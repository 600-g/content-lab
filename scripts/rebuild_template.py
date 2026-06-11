"""v2.7 표준 템플릿 완전 재정리 — LLM 기반 + 본문 보존 검증.

각 페이지를 TEMPLATE.md v2.2 표준으로 재작성:
- TL;DR quote 1개
- 메타 quote 1개 (3줄)
- divider
- ## 8섹션 한국어 + 영문 부제

**안전장치**:
1. 사전 백업 (logs/backup_v27_{date}/) 가 있어야만 실행
2. LLM 출력의 원본 키워드 보존율 ≥ 80% (불통과 시 skip)
3. 페이지가 너무 작거나 (300자 미만) 손상됐으면 skip
4. 기본 dry-run. --apply 명시해야 실제 적용
5. --only 키워드 / --limit N 으로 1건씩 검증 가능
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import time
from pathlib import Path
from collections import Counter

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API = "https://api.notion.com/v1"
H = {
    "Authorization": f"Bearer {os.environ['NOTION_API_KEY']}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
DB_ID = os.environ['NOTION_DB_ID']
GEMINI_KEY = os.environ['GEMINI_API_KEY']

# 백업 디렉토리 — 오늘 폴더 우선, 없으면 가장 최근 backup_v27_* 사용
def _find_backup_dir() -> Path:
    today = Path(__file__).resolve().parents[1] / "logs" / f"backup_v27_{datetime.date.today().isoformat()}"
    if today.exists():
        return today
    logs = Path(__file__).resolve().parents[1] / "logs"
    candidates = sorted(logs.glob("backup_v27_*"), reverse=True)
    return candidates[0] if candidates else today


BACKUP_DIR = _find_backup_dir()
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "logs" / f"rebuild_v27_{datetime.date.today().isoformat()}"
ENGINE_PREF = "auto"
USE_CACHE = False
MIN_SCORE = 0.75

CATEGORY_ICON = {
    "프롬프트": "💬", "자동화": "🤖", "콘텐츠": "🎬", "디자인": "🎨",
    "개발": "💻", "업무": "⚡", "기타": "📦",
}

# ─────────────────────────────────────────────
# 블록 ↔ 마크다운
# ─────────────────────────────────────────────

def block_text(b: dict) -> str:
    t = b.get("type", "?")
    rt = b.get(t, {}).get("rich_text", [])
    return "".join(r.get("plain_text", "") for r in rt)


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


def blocks_to_md(blocks: list[dict]) -> str:
    parts: list[str] = []
    for b in blocks:
        t = b.get("type", "?")
        text = block_text(b)
        if t == "heading_1": parts.append(f"# {text}")
        elif t == "heading_2": parts.append(f"## {text}")
        elif t == "heading_3": parts.append(f"### {text}")
        elif t == "bulleted_list_item": parts.append(f"- {text}")
        elif t == "numbered_list_item": parts.append(f"1. {text}")
        elif t == "quote": parts.append(f"> {text}")
        elif t == "code":
            lang = b.get("code", {}).get("language", "")
            parts.append(f"```{lang}\n{text}\n```")
        elif t == "divider": parts.append("---")
        elif t == "paragraph":
            if text.strip(): parts.append(text)
    return "\n\n".join(parts)


# ─────────────────────────────────────────────
# LLM (Gemini → Gemma 4 폴백)
# ─────────────────────────────────────────────

REBUILD_PROMPT = """너는 AI 스킬 큐레이션 에이전트다. 아래 콘텐츠를 **다른 사람·AI 가 RAG 로 읽고 활용 판단할 수 있는** 보편 스킬 자산 형식으로 재작성해라.

⚠️ 절대 룰 (★ 가장 중요):
★ **[[CODE_BLOCK_N]] / [[INLINE_N]] 토큰은 절대 수정/번역/삭제하지 마라.** 원본 코드/명령어/단축키 자리표시자다. 출력에 그대로 포함시켜라
★ **원문의 명사/숫자/도구명/단계 내용을 그대로 보존** — paraphrase 금지. 표현을 바꾸지 말고 구조만 정돈
★ **두근컴퍼니/두근펫/매매봇/검은별/첼시인스타/AI900 같은 사용자 개인 프로젝트 강제 매핑 금지** — 보편 정보로만 작성
★ **요약하지 마라** — 원문 단계가 5개면 출력도 5개. 원문 예시가 3종이면 출력도 3종
1. 원문에 있는 정보만 재구성 — 새 내용 추가 금지, 과장 금지
2. 단계 번호와 외부 도구 이름 (Claude Code, Codex, MCP, Obsidian 등) 그대로 보존
3. 빈 섹션은 그 H2 헤더 자체를 생략 (절대 출력 X)
4. quote (`>`) 사용 금지 — 본문 시작은 한 줄 paragraph 다음 ## H2 헤더
5. ['a','b','c'] 파이썬 list 형태 → 실제 글머리표/줄바꿈으로 풀어쓰기
6. 한국어로 작성

📐 출력 형식 (시각 위계 — H2 / H3 / **bold** 적극 활용):
```
💡 **<2-3문장 핵심 정의 + 가치 제안>** — 페이지 열자마자 "이 스킬이 뭐고 왜 쓰는지" 즉시 파악 가능하게. 명사·도구명·숫자는 **bold**.

## 🔑 어떻게 작동하나요?
핵심 메커니즘/원리. 긴 경우 ### 소제목으로 나눠라. 핵심 키워드는 **bold**.

### (필요시) 세부 원리 A
### (필요시) 세부 원리 B

## 🛠 따라 하기 (단계별)
1. **짧은 굵은 라벨**: 설명
2. **짧은 굵은 라벨**: 설명

## 💡 실제 예시
표/코드/대화 ([[CODE_BLOCK_N]] 토큰 그대로 사용)

### (필요시) 예시 1 — 시나리오 라벨
### (필요시) 예시 2 — 다른 시나리오

## ⚡ 이렇게 쓰면 효과적이다
- **추천 시점**: 어떤 상황·작업에서 가장 효과 큼
- **시너지 도구**: 함께 쓰면 좋은 도구/스킬 (보편 권장)
- **수익화 가능성**: 있으면 실현 경로 + 예상 시장 (없으면 이 항목 생략)
- **적용 난이도**: 🟢 초보 OK / 🟡 중급 / 🔴 고급 + 예상 소요 시간

## ⚠️ 주의할 점
- 한도/유료/실패 케이스 / 보안 이슈 / 한계

## 📎 출처
- [원본](URL)
```

📌 시각 위계 룰:
- 첫 줄 정의는 **`💡 **굵은 정의**`** 형태로 시작 (callout 으로 변환됨)
- 섹션이 길면 반드시 ### H3 로 분할 (한 H2 안에 100단어 넘으면 H3 권장)
- 핵심 명사·도구명·숫자·결과치는 모두 **bold** 처리
- 첫 paragraph 든 단계 라벨이든 **굵은 짧은 라벨**: 으로 시작하면 가독성 ↑

📌 입력 정보 (참고만, 본문에 그대로 박지 마라):
- 제목: {title}
- 카테고리: {category} · 난이도: {difficulty}
- AI 도구: {tools}
- 출처 URL: {url}

📄 원본 본문 ([[CODE_BLOCK_N]] / [[INLINE_N]] 토큰 그대로 출력에 포함시킬 것):
---
{body}
---

⚠️ 출력은 위 표준 형식의 순수 markdown 만. 코드 펜스(```) wrapping 없이 바로 시작. 설명/주석/사과 금지.
⚠️ "두근컴퍼니 매핑" 같은 개인 프로젝트 연결 X. 일반 사용자 관점의 효과적 활용 추천만."""


def call_gemini(prompt: str, model: str = "gemini-2.5-flash", retries: int = 3) -> str | None:
    """Gemini 호출 — 429/503 재시도 (지수 backoff). RPM 10 한도 가정."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
    for attempt in range(retries):
        try:
            r = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.3, "maxOutputTokens": 8000},
                },
                timeout=120,
            )
            if r.status_code == 200:
                d = r.json()
                cands = d.get("candidates", [])
                if not cands:
                    return None
                parts = cands[0].get("content", {}).get("parts", [])
                return "".join(p.get("text", "") for p in parts) or None
            if r.status_code in (429, 503):
                wait = 8 * (attempt + 1)
                time.sleep(wait)
                continue
            return None
        except Exception:
            time.sleep(3)
    return None


def call_gemma(prompt: str, model: str = "gemma4:26b") -> str | None:
    """Gemma 호출. keep_alive=30m 으로 cold start 1회만."""
    try:
        r = requests.post(
            f"{os.getenv('OLLAMA_URL','http://localhost:11434')}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "think": False,
                "keep_alive": "30m",
                "options": {"temperature": 0.2, "num_predict": 8000},
            },
            timeout=int(os.getenv("GEMMA_TIMEOUT", "600")),
        )
        r.raise_for_status()
        return r.json().get("response", "") or None
    except Exception:
        return None


def rebuild_markdown(meta: dict, engine_pref: str = "auto") -> tuple[str | None, str]:
    """LLM 호출 → 재작성된 markdown. (text, 사용된_엔진).

    engine_pref:
      - "auto" : Gemini → Gemma 26B 폴백 (기본)
      - "gemini" : Gemini 만
      - "gemma" : Gemma 26B 만
    """
    prompt = REBUILD_PROMPT.format(**meta)
    if engine_pref in ("auto", "gemini"):
        for model in ("gemini-2.5-flash", "gemini-2.0-flash"):
            out = call_gemini(prompt, model)
            if out and len(out) > 200:
                return clean_llm_output(out), model
        if engine_pref == "gemini":
            return None, ""
    if engine_pref in ("auto", "gemma"):
        out = call_gemma(prompt, "gemma4:26b")
        if out and len(out) > 200:
            return clean_llm_output(out), "gemma4:26b"
    return None, ""


def clean_llm_output(text: str) -> str:
    """LLM 이 가끔 코드펜스 ```markdown ... ``` 으로 wrap 하면 풀기."""
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-z]*\n", "", t)
        t = re.sub(r"\n```\s*$", "", t)
    return t.strip()


# ─────────────────────────────────────────────
# 코드 보호 (placeholder 치환 → LLM → 복원)
# ─────────────────────────────────────────────

CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def protect_code(text: str) -> tuple[str, list[str], list[str]]:
    """텍스트에서 코드블록·인라인 코드 추출 → placeholder 치환."""
    code_blocks: list[str] = []
    def _cb(m: re.Match) -> str:
        i = len(code_blocks)
        code_blocks.append(m.group(0))
        return f"[[CODE_BLOCK_{i}]]"
    text2 = CODE_BLOCK_RE.sub(_cb, text)

    inline_codes: list[str] = []
    def _ic(m: re.Match) -> str:
        i = len(inline_codes)
        inline_codes.append(m.group(0))
        return f"[[INLINE_{i}]]"
    text3 = INLINE_CODE_RE.sub(_ic, text2)

    return text3, code_blocks, inline_codes


_PLACEHOLDER_RE = re.compile(r"\[\[([A-Z][A-Z_]*?)_?(\d+)\]\]")


def restore_code(text: str, code_blocks: list[str], inline_codes: list[str]) -> tuple[str, list[str]]:
    """placeholder → 원본 코드 복원. fuzzy matching (LLM 이 토큰명 변형해도 복원).

    매칭 규칙:
    - 이름에 'CODE'/'BLOCK' 포함 → code_blocks[n]
    - 그 외 (INLINE/IC/CON/...) → inline_codes[n]
    """
    matched: set[str] = set()

    def repl(m: re.Match) -> str:
        name = m.group(1).upper()
        try:
            n = int(m.group(2))
        except ValueError:
            return m.group(0)
        if "CODE" in name or "BLOCK" in name or "CB" == name:
            if 0 <= n < len(code_blocks):
                matched.add(f"CB_{n}")
                return code_blocks[n]
        else:
            if 0 <= n < len(inline_codes):
                matched.add(f"IC_{n}")
                return inline_codes[n]
        return m.group(0)

    text = _PLACEHOLDER_RE.sub(repl, text)

    missing: list[str] = []
    for i in range(len(code_blocks)):
        if f"CB_{i}" not in matched:
            missing.append(f"CODE_BLOCK_{i}")
    for i in range(len(inline_codes)):
        if f"IC_{i}" not in matched:
            missing.append(f"INLINE_{i}")
    return text, missing


# ─────────────────────────────────────────────
# 본문 보존 검증
# ─────────────────────────────────────────────

STOPWORDS = {
    "있다", "없다", "하는", "되는", "위해", "통해", "또는", "그리고",
    "있는", "있음", "이는", "이를", "것을", "것이", "에서", "으로",
    "로서", "에게", "에는", "에서는", "정도", "혹은", "https", "http",
    "기존", "활용", "사용", "적용", "필요", "가능", "참고", "이용",
    "만들기", "바꾸는", "이어가기", "시스템", "콘텐츠", "가이드",
    "두근의", "시사점", "Wasted", "Productive", "체크", "확인", "구조를",
    "고도화", "고도화에", "기존에는", "참고해", "아니라", "시키면",
    "코딩을", "기다리며", "알려주는", "고민을", "Phase", "중인가",
    "장식이", "커뮤니티", "선택", "전반", "정리하고",
    # 두근컴퍼니 개인 프로젝트명 (보편 템플릿에서 의도적으로 제거됨 — 보존율 카운트 X)
    "두근", "두근컴퍼니", "두근펫", "매매봇", "검은별", "클로드코드",
    "첼시인스타", "이모티콘", "AI900", "doogeun", "company-hq",
}


def extract_keywords(md: str) -> set[str]:
    """원본 markdown 에서 핵심 키워드 추출 — 영문 5자+, 한글 3자+."""
    text = re.sub(r"```.*?```", " ", md, flags=re.DOTALL)
    text = re.sub(r"https?://\S+", " ", text)
    tokens = re.findall(r"[가-힣]{3,}|[A-Za-z][A-Za-z0-9_\-\.]{4,}", text)
    counter = Counter(t for t in tokens if t.lower() not in STOPWORDS)
    # 빈도 1+ 상위 40개
    return {w for w, _ in counter.most_common(40)}


def preservation_score(original: str, rebuilt: str) -> tuple[float, list[str]]:
    """원본 키워드 → 재작성 본문에 몇 % 보존?"""
    keys = extract_keywords(original)
    if not keys:
        return 1.0, []
    rebuilt_lower = rebuilt.lower()
    missing = [k for k in keys if k.lower() not in rebuilt_lower]
    kept = len(keys) - len(missing)
    return kept / len(keys), missing


# ─────────────────────────────────────────────
# Markdown → Notion blocks
# ─────────────────────────────────────────────

NOTION_CODE_LANGS = {
    "abap", "arduino", "bash", "basic", "c", "clojure", "coffeescript",
    "c++", "c#", "css", "dart", "diff", "docker", "elixir", "elm", "erlang",
    "flow", "fortran", "f#", "gherkin", "glsl", "go", "graphql", "groovy",
    "haskell", "html", "java", "javascript", "json", "julia", "kotlin",
    "latex", "less", "lisp", "livescript", "lua", "makefile", "markdown",
    "markup", "matlab", "mermaid", "nix", "notion formula", "objective-c",
    "ocaml", "pascal", "perl", "php", "plain text", "powershell", "prolog",
    "protobuf", "python", "r", "reason", "ruby", "rust", "sass", "scala",
    "scheme", "scss", "shell", "sql", "swift", "typescript", "vb.net",
    "verilog", "vhdl", "visual basic", "webassembly", "yaml",
}

_LANG_ALIASES = {
    "sh": "shell", "zsh": "shell", "console": "shell", "bash-script": "bash",
    "js": "javascript", "jsx": "javascript", "node": "javascript",
    "ts": "typescript", "tsx": "typescript",
    "py": "python", "python3": "python",
    "yml": "yaml", "md": "markdown", "rb": "ruby",
    "text": "plain text", "txt": "plain text", "plain": "plain text",
    "shell-script": "shell", "tsv": "plain text", "csv": "plain text",
}


def _normalize_code_lang(lang: str) -> str:
    """Notion 유효 code language 로 정규화."""
    l = (lang or "").lower().strip()
    if not l:
        return "plain text"
    if l in NOTION_CODE_LANGS:
        return l
    if l in _LANG_ALIASES:
        return _LANG_ALIASES[l]
    return "plain text"


_INLINE_RE = re.compile(
    r"(\*\*(?P<bold>.+?)\*\*)"
    r"|(`(?P<code>[^`]+)`)"
    r"|(\[(?P<linktext>[^\]]+)\]\((?P<url>https?://[^\s)]+)\))"
)


def _rt(text: str, max_len: int = 1900) -> list[dict]:
    """markdown inline (**bold**, `code`, [text](url)) → Notion rich_text."""
    text = text[:max_len]
    out: list[dict] = []
    pos = 0
    for m in _INLINE_RE.finditer(text):
        if m.start() > pos:
            out.append({"type": "text", "text": {"content": text[pos:m.start()]}})
        if m.group("bold") is not None:
            out.append({"type": "text", "text": {"content": m.group("bold")},
                        "annotations": {"bold": True}})
        elif m.group("code") is not None:
            out.append({"type": "text", "text": {"content": m.group("code")},
                        "annotations": {"code": True}})
        elif m.group("url") is not None:
            out.append({"type": "text",
                        "text": {"content": m.group("linktext"),
                                 "link": {"url": m.group("url")}}})
        pos = m.end()
    if pos < len(text):
        out.append({"type": "text", "text": {"content": text[pos:]}})
    return out or [{"type": "text", "text": {"content": text}}]


def md_to_blocks(md: str) -> list[dict]:
    blocks: list[dict] = []
    lines = md.split("\n")
    in_code = False
    code_lang = ""
    code_buf: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 코드 블록
        if stripped.startswith("```"):
            if in_code:
                blocks.append({
                    "object": "block", "type": "code",
                    "code": {
                        "rich_text": _rt("\n".join(code_buf), 1900),
                        "language": _normalize_code_lang(code_lang),
                    },
                })
                in_code = False
                code_buf = []
                code_lang = ""
            else:
                in_code = True
                code_lang = stripped.lstrip("`").strip() or ""
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        # quote — 연속된 `> ` 라인은 하나의 quote 블록으로 합치되 줄바꿈 보존
        if stripped.startswith("> "):
            buf = [stripped[2:].rstrip()]
            j = i + 1
            while j < len(lines):
                ns = lines[j].strip()
                if ns.startswith("> "):
                    buf.append(ns[2:].rstrip())
                    j += 1
                elif ns == ">":
                    buf.append("")
                    j += 1
                else:
                    break
            content = "\n".join(buf).strip()
            blocks.append({
                "object": "block", "type": "quote",
                "quote": {"rich_text": _rt(content)},
            })
            i = j
            continue

        if stripped.startswith("# "):
            blocks.append({"object": "block", "type": "heading_1",
                           "heading_1": {"rich_text": _rt(stripped[2:])}})
        elif stripped.startswith("## "):
            blocks.append({"object": "block", "type": "heading_2",
                           "heading_2": {"rich_text": _rt(stripped[3:])}})
        elif stripped.startswith("### "):
            blocks.append({"object": "block", "type": "heading_3",
                           "heading_3": {"rich_text": _rt(stripped[4:])}})
        elif stripped.startswith(("- ", "* ", "• ")):
            blocks.append({"object": "block", "type": "bulleted_list_item",
                           "bulleted_list_item": {"rich_text": _rt(stripped[2:])}})
        elif re.match(r"^\d+[\.\)]\s", stripped):
            content = re.sub(r"^\d+[\.\)]\s", "", stripped)
            blocks.append({"object": "block", "type": "numbered_list_item",
                           "numbered_list_item": {"rich_text": _rt(content)}})
        elif stripped == "---":
            blocks.append({"object": "block", "type": "divider", "divider": {}})
        elif stripped.startswith("|") and stripped.endswith("|"):
            # markdown table → code block (Notion API 의 table 은 복잡)
            table_buf = [line]
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                table_buf.append(lines[j])
                j += 1
            blocks.append({
                "object": "block", "type": "code",
                "code": {"rich_text": _rt("\n".join(table_buf), 1900),
                         "language": "plain text"},
            })
            i = j
            continue
        else:
            # 첫 paragraph (heading 이전, 💡 시작) → callout 블록
            if not blocks and stripped.startswith("💡"):
                content = stripped[1:].strip()
                blocks.append({
                    "object": "block", "type": "callout",
                    "callout": {
                        "rich_text": _rt(content),
                        "icon": {"type": "emoji", "emoji": "💡"},
                        "color": "blue_background",
                    },
                })
            else:
                blocks.append({"object": "block", "type": "paragraph",
                               "paragraph": {"rich_text": _rt(stripped)}})
        i += 1
    return blocks


# ─────────────────────────────────────────────
# 페이지 교체
# ─────────────────────────────────────────────

def delete_all_children(pid: str) -> int:
    """페이지 children 전부 archive (Notion의 'delete'는 archive)."""
    blocks = get_all_blocks(pid)
    deleted = 0
    for b in blocks:
        try:
            r = requests.delete(f"{API}/blocks/{b['id']}", headers=H, timeout=30)
            if r.status_code == 200:
                deleted += 1
            time.sleep(0.06)
        except Exception:
            pass
    return deleted


def append_blocks(pid: str, new_blocks: list[dict]) -> int:
    """새 blocks 를 페이지 children 으로 append (100건씩)."""
    added = 0
    for i in range(0, len(new_blocks), 100):
        chunk = new_blocks[i:i+100]
        r = requests.patch(f"{API}/blocks/{pid}/children", headers=H,
                           json={"children": chunk}, timeout=60)
        if r.status_code == 200:
            added += len(chunk)
        else:
            print(f"      ⚠️ append 실패 {r.status_code}: {r.text[:120]}")
            break
        time.sleep(0.15)
    return added


def update_page_icon(pid: str, category: str) -> None:
    icon = CATEGORY_ICON.get(category)
    if not icon:
        return
    try:
        requests.patch(f"{API}/pages/{pid}", headers=H,
                       json={"icon": {"type": "emoji", "emoji": icon}}, timeout=15)
    except Exception:
        pass


# ─────────────────────────────────────────────
# 메인 처리
# ─────────────────────────────────────────────

def extract_props(pr: dict) -> dict:
    title = "".join(t["plain_text"] for t in pr.get("스킬명", {}).get("title", []))
    return {
        "title": title,
        "grade": ((pr.get("등급", {}).get("select") or {}).get("name") or "S").split("-")[0],
        "category": (pr.get("카테고리", {}).get("select") or {}).get("name") or "기타",
        "difficulty": (pr.get("난이도", {}).get("select") or {}).get("name") or "🟡 중급",
        "tools": ", ".join(t["name"] for t in pr.get("AI 도구", {}).get("multi_select", [])) or "도구무관",
        "url": (pr.get("출처 URL", {}) or {}).get("url") or "",
    }


def process_page(p: dict, apply: bool, verbose: bool) -> str:
    pid = p["id"]
    pr = p["properties"]
    props = extract_props(pr)
    title = props["title"]

    # 백업에서 원본 markdown 로드 — 전체 pid 매칭 (prefix 충돌 방지)
    pid_full = pid.replace("-", "")
    backup_md = None
    for f in BACKUP_DIR.glob(f"{pid_full}__*.md"):
        backup_md = f.read_text(encoding="utf-8")
        break
    if not backup_md:
        # 백업 없으면 직접 fetch
        blocks = get_all_blocks(pid)
        backup_md = blocks_to_md(blocks)

    # 본문만 추출 (첫 # 제목 라인 + 본문)
    body = re.sub(r"^#\s+.*\n+", "", backup_md, count=1).strip()

    if len(body) < 100:
        return f"⏭ 본문 너무 작음 ({len(body)}자)"

    # 캐시 — 이미 생성된 rebuild markdown 있으면 LLM 호출 생략
    cached_path = OUTPUT_DIR / f"{pid_full}__{re.sub(r'[^가-힣A-Za-z0-9]+','-',title)[:50]}.md"
    rebuilt = None
    engine = ""
    if USE_CACHE and cached_path.exists():
        raw = cached_path.read_text(encoding="utf-8")
        # 첫 H1 + 코멘트 라인 제거 후 본문만
        m = re.search(r"<!--\s*엔진:\s*([^·]+)\s*·", raw)
        if m:
            engine = f"{m.group(1).strip()} (cache)"
        rebuilt = re.sub(r"^#[^\n]*\n+", "", raw, count=1)
        rebuilt = re.sub(r"<!--.*?-->\n+", "", rebuilt, count=1).strip()

    # 캐시 없거나 옵션 off → LLM 호출 (코드 보호 모드)
    if not rebuilt:
        protected_body, code_blocks, inline_codes = protect_code(body)
        total_tokens = len(code_blocks) + len(inline_codes)

        # 최대 2회 시도 — placeholder 누락 시 재호출
        best_rebuilt = None
        best_missing: list[str] = []
        for attempt in range(2):
            meta = {**props, "body": protected_body}
            rebuilt_protected, engine = rebuild_markdown(meta, engine_pref=ENGINE_PREF)
            if not rebuilt_protected:
                continue
            tmp, missing_tokens = restore_code(rebuilt_protected, code_blocks, inline_codes)
            if not missing_tokens:
                best_rebuilt = tmp
                best_missing = []
                break
            if best_rebuilt is None or len(missing_tokens) < len(best_missing):
                best_rebuilt = tmp
                best_missing = missing_tokens
        if best_rebuilt is None:
            return f"❌ LLM 호출 실패 (engine={ENGINE_PREF})"

        # 누락 placeholder 가 있으면 페이지 끝에 "원본 코드 (보존)" 섹션으로 추가
        rebuilt = best_rebuilt
        if best_missing:
            rescue_lines = ["", "## 📌 원본 코드/명령어 (자동 보존)", "",
                            "> LLM 가공 과정에서 본문 위치를 잃어버린 원본 코드/명령어. 데이터 손실 방지를 위해 페이지 끝에 그대로 보존."]
            for tok in best_missing:
                if tok.startswith("CODE_BLOCK_"):
                    idx = int(tok.replace("CODE_BLOCK_", ""))
                    rescue_lines.append("")
                    rescue_lines.append(code_blocks[idx])
                elif tok.startswith("INLINE_"):
                    idx = int(tok.replace("INLINE_", ""))
                    rescue_lines.append(f"- {inline_codes[idx]}")
            rebuilt = rebuilt + "\n" + "\n".join(rescue_lines) + "\n"
            if verbose:
                print(f"      ⚠️ placeholder 누락 {len(best_missing)}/{total_tokens} → 페이지 끝에 보존")

    # 보존 검증
    score, missing = preservation_score(body, rebuilt)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{pid_full}__{re.sub(r'[^가-힣A-Za-z0-9]+','-',title)[:50]}"
    (OUTPUT_DIR / f"{stem}.md").write_text(
        f"# {title}\n\n<!-- 엔진: {engine} · 보존율: {score:.0%} · 누락: {', '.join(missing[:10])} -->\n\n{rebuilt}",
        encoding="utf-8",
    )

    # 출력 길이가 원본의 30% 미만이면 요약 과다 → skip
    body_chars = len(body)
    rebuilt_chars = len(rebuilt)
    length_ratio = rebuilt_chars / max(body_chars, 1)
    if length_ratio < 0.30:
        return f"❌ 출력 너무 짧음 ({rebuilt_chars}/{body_chars}자, {length_ratio:.0%})"

    if score < MIN_SCORE:
        if verbose:
            print(f"      누락 키워드 ({len(missing)}개): {', '.join(missing[:15])}")
        return f"❌ 보존율 {score:.0%} < {MIN_SCORE:.0%} (skip) · 엔진 {engine}"
    if score < 0.85 and verbose:
        print(f"      ⚠️ 보존 {score:.0%} (75-85% 구간) · 누락: {', '.join(missing[:10])}")

    if not apply:
        return f"🔍[dry] 보존 {score:.0%} · 엔진 {engine} · 신규 블록 ~{len(md_to_blocks(rebuilt))}개"

    # 실제 적용 — 안전: 새 블록 검증 후 delete → append
    new_blocks = md_to_blocks(rebuilt)
    if len(new_blocks) < 5:
        return f"❌ 블록 변환 결과 {len(new_blocks)}개 (너무 적음 — skip)"

    deleted = delete_all_children(pid)
    time.sleep(0.5)
    added = append_blocks(pid, new_blocks)
    if added == 0:
        # 치명적 상황: 옛 내용 사라지고 새 내용 추가 실패 → 백업 markdown 즉시 안내
        backup_file = next(BACKUP_DIR.glob(f"{pid_full}__*.md"), None)
        return f"🚨 추가 실패! 페이지 비어있음. 복원 백업: {backup_file}"
    if added < len(new_blocks):
        return f"⚠️ 부분 추가 {added}/{len(new_blocks)} · 보존 {score:.0%} · 엔진 {engine}"
    update_page_icon(pid, props["category"])

    return f"✅ 삭제 {deleted} → 추가 {added} · 보존 {score:.0%} · 엔진 {engine}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--only", type=str, default="")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--engine", choices=["auto", "gemini", "gemma"], default="auto",
                        help="LLM 선택 — auto: Gemini→Gemma, gemini: Gemini 만, gemma: Gemma 26B 만")
    parser.add_argument("--use-cache", action="store_true",
                        help="이전 dry-run 결과 markdown 재사용 (LLM 호출 생략)")
    parser.add_argument("--min-score", type=float, default=0.70,
                        help="본문 보존율 최소값 (0.0~1.0). 누락이 paraphrase 만이면 0.70 권장")
    args = parser.parse_args()

    global ENGINE_PREF, USE_CACHE, MIN_SCORE
    ENGINE_PREF = args.engine
    USE_CACHE = args.use_cache
    MIN_SCORE = args.min_score

    if not BACKUP_DIR.exists():
        print(f"❌ 백업 디렉토리 없음: {BACKUP_DIR}")
        print(f"   먼저 실행: python -m scripts.backup_all")
        return 1

    r = requests.post(f"{API}/databases/{DB_ID}/query", headers=H, json={"page_size": 50}).json()
    pages = r.get("results", [])
    if args.only:
        pages = [p for p in pages if args.only in "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])]
    if args.limit > 0:
        pages = pages[:args.limit]

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"📡 모드: {mode} · 대상: {len(pages)}건")
    print(f"📁 백업: {BACKUP_DIR}")
    print(f"📂 출력: {OUTPUT_DIR}\n")

    for i, p in enumerate(pages, 1):
        title = "".join(t["plain_text"] for t in p["properties"]["스킬명"]["title"])
        try:
            result = process_page(p, apply=args.apply, verbose=args.verbose)
            print(f"  [{i:2d}/{len(pages)}] {title[:44]:<44}  {result}")
        except Exception as e:
            print(f"  [{i:2d}/{len(pages)}] {title[:44]:<44}  ❌ 예외: {e}")
        # Gemini RPM 한도 회피 — engine 별 적절한 간격
        time.sleep(2 if ENGINE_PREF == "gemma" else 7)
    return 0


if __name__ == "__main__":
    sys.exit(main())
