"""Notion DB 마스터 등록 + 중복 체크 + 한글 에러 메시지.

notion-client v3 호환성 이슈 때문에 requests로 직접 호출 (v3에서 databases.query 삭제됨).
모든 실패는 한글 사유 + 우회 안내로 반환.
"""
from __future__ import annotations

import datetime
import logging
import os
from typing import TYPE_CHECKING, Optional

import requests

if TYPE_CHECKING:
    from ..analyzer.gemini import AnalysisResult

logger = logging.getLogger(__name__)

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
TIMEOUT = 15


class NotionError(RuntimeError):
    """한글 사유 + 우회 가이드를 담은 예외."""

    def __init__(self, message_ko: str, code: str = "", hint: str = ""):
        super().__init__(message_ko)
        self.code = code
        self.hint = hint

    def to_dict(self) -> dict:
        return {"error_ko": str(self), "code": self.code, "hint": self.hint}


def _api_key() -> str | None:
    return os.getenv("NOTION_API_KEY")


def _db_id() -> str:
    return os.getenv("NOTION_DB_ID", "")


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_api_key()}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _humanize(status_code: int, body: dict, context: str) -> NotionError:
    """Notion API 오류 → 한글 사유 + 우회 가이드."""
    code = body.get("code", "")
    raw_msg = body.get("message", "")

    if status_code == 401 or code == "unauthorized":
        return NotionError(
            "Notion 인증 실패 — NOTION_API_KEY가 잘못되었거나 만료되었습니다.",
            code="unauthorized",
            hint="https://www.notion.so/my-integrations 에서 키 재확인. .env의 NOTION_API_KEY 갱신 후 LaunchAgent 재시작.",
        )
    if status_code == 404 or code == "object_not_found":
        return NotionError(
            "Notion DB에 인티그레이션 권한이 없습니다 — Connections 미연결.",
            code="no_db_connection",
            hint="Notion DB 페이지 우측 상단 ⋯ → Connections → 'aiskillbox 연동 api' 추가",
        )
    if status_code == 403 or code == "restricted_resource":
        return NotionError(
            "권한 부족 — 인티그레이션이 해당 페이지에 접근할 수 없습니다.",
            code="forbidden",
            hint="DB Connections에 인티그레이션 추가 또는 워크스페이스 관리자 권한 확인",
        )
    if status_code == 429 or code == "rate_limited":
        return NotionError(
            "Notion API 호출 한도 초과 — 잠시 후 재시도 (분당 ~3건).",
            code="rate_limited",
            hint="1분 대기 후 다시 시도",
        )
    if code == "validation_error":
        return NotionError(
            f"DB 스키마 불일치 — {raw_msg}",
            code="schema_mismatch",
            hint="Notion DB 속성(스킬명/카테고리/등급/...)이 SKILL_AGENT.md 정의와 다릅니다. DB 컬럼 확인 필요.",
        )
    return NotionError(
        f"Notion 오류 ({context}) — {raw_msg or 'unknown'}",
        code=code or f"http_{status_code}",
        hint="네트워크 또는 일시 장애. 1분 후 재시도. 지속 시 https://status.notion.so 확인",
    )


# Notion API 제약: 한 호출당 children 배열 100개 한도. 그 이상이면 chunk 분할 필수.
NOTION_CHILDREN_MAX = 100


def _append_blocks_chunked(page_id: str, blocks: list) -> None:
    """blocks 를 100개 단위로 끊어 순차 PATCH. 부분 실패 시 즉시 raise."""
    for i in range(0, len(blocks), NOTION_CHILDREN_MAX):
        chunk = blocks[i:i + NOTION_CHILDREN_MAX]
        _request(
            "PATCH", f"blocks/{page_id}/children",
            {"children": chunk},
            context=f"블록 추가 (chunk {i // NOTION_CHILDREN_MAX + 1})",
        )


def _request(method: str, path: str, body: dict | None = None, context: str = "") -> dict:
    url = f"{NOTION_API}/{path.lstrip('/')}"
    try:
        r = requests.request(method, url, headers=_headers(), json=body, timeout=TIMEOUT)
    except requests.Timeout:
        raise NotionError("Notion API 응답 시간 초과 (15초)", code="timeout", hint="네트워크 확인 후 재시도")
    except requests.ConnectionError as e:
        raise NotionError(f"Notion 서버 연결 실패: {e}", code="conn_error", hint="인터넷 연결 확인")

    try:
        data = r.json()
    except Exception:  # noqa: BLE001
        data = {}

    if r.status_code >= 400:
        raise _humanize(r.status_code, data, context)
    return data


def check_duplicate(source_url: str) -> Optional[str]:
    """출처 URL이 이미 등록되어 있는지 확인 (정규화 URL로 fuzzy match).

    fbclid/utm 등 트래킹 파라미터 다른 URL도 같은 페이지로 인식.
    404/401 같은 권한 문제는 None.
    """
    if not _api_key() or not _db_id():
        return None
    from ..skill_builder.installer import normalize_url
    target = normalize_url(source_url)
    try:
        # 1차: 정확 일치
        data = _request(
            "POST",
            f"databases/{_db_id()}/query",
            {
                "filter": {"property": "출처 URL", "url": {"equals": source_url}},
                "page_size": 1,
            },
            context="중복 체크",
        )
        results = data.get("results", [])
        if results:
            return results[0].get("id")

        # 2차: 정규화 URL로 fuzzy 매치 — 도메인 + path 시작 부분으로 contains
        try:
            from urllib.parse import urlsplit
            s = urlsplit(target)
            stem = f"{s.scheme}://{s.netloc}{s.path}"
            data2 = _request(
                "POST",
                f"databases/{_db_id()}/query",
                {
                    "filter": {"property": "출처 URL", "url": {"contains": stem[:80]}},
                    "page_size": 5,
                },
                context="중복 체크(fuzzy)",
            )
            for r in data2.get("results", []):
                ru = (r.get("properties", {}).get("출처 URL", {}) or {}).get("url", "")
                if normalize_url(ru) == target:
                    return r.get("id")
        except Exception:
            pass
    except NotionError as e:
        logger.info("중복 체크 스킵: %s", e)
    return None


def find_by_title(title: str) -> Optional[str]:
    """스킬명 완전 일치로 기존 페이지 검색.

    합병된 스킬인데 URL 매칭이 전부 실패한 경우의 2차 안전망 (v4.4.5).
    신규 스킬에는 쓰지 말 것 — 우연한 제목 일치로 남의 페이지를 덮을 수 있음.
    """
    if not _api_key() or not _db_id() or not title:
        return None
    clean = _clean_title(title)
    try:
        data = _request(
            "POST",
            f"databases/{_db_id()}/query",
            {
                "filter": {"property": "스킬명", "title": {"equals": clean}},
                "page_size": 1,
            },
            context="제목 중복 체크",
        )
        results = data.get("results", [])
        if results:
            return results[0].get("id")
    except NotionError as e:
        logger.info("제목 중복 체크 스킵: %s", e)
    return None


def _strip_for_notion(md: str) -> str:
    """SKILL.md 본문에서 YAML 프론트매터 + 최상위 H1(제목, Notion property에 이미 있음) 제거.

    SKILL.md 구조:
        ---
        name: ...
        description: ...
        ...
        ---
        # 아이콘 제목   ← Notion property에 이미 있으니 중복 제거
        > **TL;DR** ...   ← 여기부터 보존
    """
    # YAML 프론트매터 제거
    if md.startswith("---"):
        # 두 번째 --- 위치 찾기
        m = md.find("\n---", 3)
        if m > 0:
            md = md[m+4:].lstrip("\n")
    # 첫 줄 H1 제거 (단, # 한 개로 시작하는 것만)
    lines = md.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].startswith("# ") and not lines[0].startswith("## "):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines.pop(0)
    return "\n".join(lines)


# Notion code block 허용 언어 enum (주요 항목만 — 모르는 건 plain text 폴백)
_NOTION_CODE_LANGS = {
    "abap","abc","agda","arduino","ascii art","assembly","bash","basic","bnf","c","c#",
    "c++","clojure","coffeescript","coq","css","dart","dhall","diff","docker","ebnf",
    "elixir","elm","erlang","f#","flow","fortran","gherkin","glsl","go","graphql",
    "groovy","haskell","hcl","html","idris","java","javascript","json","julia","kotlin",
    "latex","less","lisp","livescript","llvm ir","lua","makefile","markdown","markup",
    "matlab","mathematica","mermaid","nix","notion formula","objective-c","ocaml","pascal",
    "perl","php","plain text","powershell","prolog","protobuf","purescript","python",
    "r","racket","reason","ruby","rust","sass","scala","scheme","scss","shell","smalltalk",
    "solidity","sql","swift","toml","typescript","vb.net","verilog","vhdl","visual basic",
    "webassembly","xml","yaml","java/c/c++/c#",
}
_LANG_ALIASES = {
    "sh": "shell", "zsh": "shell", "fish": "shell", "ksh": "shell",
    "py": "python", "python3": "python",
    "js": "javascript", "jsx": "javascript",
    "ts": "typescript", "tsx": "typescript",
    "yml": "yaml",
    "tex": "latex",
    "dockerfile": "docker",
    "md": "markdown",
    "console": "shell",
    "tsv": "plain text", "csv": "plain text", "text": "plain text",
    "": "plain text",
}


def _norm_code_lang(lang: str) -> str:
    """노션 enum 강제. 모르는 언어 → plain text."""
    lang = (lang or "").strip().lower()
    lang = _LANG_ALIASES.get(lang, lang)
    return lang if lang in _NOTION_CODE_LANGS else "plain text"


def _markdown_to_blocks(md: str) -> list[dict]:
    """간단 마크다운 → Notion 블록. SKILL.md 프론트매터 자동 제거."""
    md = _strip_for_notion(md)
    blocks = []
    in_code = False
    code_lang = ""
    code_buf: list[str] = []
    for line in md.splitlines():
        # 코드블록 처리
        if line.strip().startswith("```"):
            if in_code:
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": "\n".join(code_buf)[:1900]}}],
                        "language": _norm_code_lang(code_lang),
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
        # v2.6: 💡 로 시작하는 단락 → Notion callout 블록 (blue_background, 인라인 서식 적용)
        if s.startswith("💡 "):
            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": _rich_text(s[2:].strip()[:1900]),
                    "icon": {"type": "emoji", "emoji": "💡"},
                    "color": "blue_background",
                },
            })
            continue
        # 인용/quote (메타 박스 폐기됐지만 호환용)
        if s.startswith("> "):
            blocks.append(_block("quote", s[2:]))
            continue
        if s.startswith("# "):
            blocks.append(_block("heading_1", s[2:]))
        elif s.startswith("## "):
            blocks.append(_block("heading_2", s[3:]))
        elif s.startswith("### "):
            blocks.append(_block("heading_3", s[4:]))
        elif s.startswith(("- ", "* ")):
            blocks.append(_block("bulleted_list_item", s[2:]))
        elif s and s[0].isdigit() and s[1:3] in (". ", ".\t"):
            blocks.append(_block("numbered_list_item", s[3:]))
        elif s == "---":
            blocks.append({"object": "block", "type": "divider", "divider": {}})
        else:
            blocks.append(_block("paragraph", s[:1900]))
        # page_replacer.append_blocks() 가 100-block/request 제한을 chunk 분할로 처리하므로
        # 여기서 임의 cap 을 두지 않는다. 풍부한 본문 보존 우선.
    return blocks


import re as _re_inline

# 마크다운 인라인 서식 파서 — Notion rich_text annotations 적용
# 우선순위: code(`) > bold(**) > link([](url)) > italic(*)
_INLINE_PATTERNS = [
    ("code",   _re_inline.compile(r"`([^`\n]+)`")),
    ("bold",   _re_inline.compile(r"\*\*([^*\n]+)\*\*")),
    ("link",   _re_inline.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)")),
    ("italic", _re_inline.compile(r"(?<![\*\w])\*([^*\n]+)\*(?![\*\w])")),
]


def _rich_text(s: str) -> list[dict]:
    """마크다운 인라인 서식 → Notion rich_text 배열."""
    if not s:
        return [{"type": "text", "text": {"content": ""}}]
    # 모든 패턴의 매치를 위치별로 수집
    matches = []
    for kind, regex in _INLINE_PATTERNS:
        for m in regex.finditer(s):
            matches.append((m.start(), m.end(), kind, m))
    # 우선순위 충돌 — 시작 위치 정렬 + 겹침은 먼저 잡힌 것 우선 (code > bold > link > italic)
    matches.sort(key=lambda x: (x[0], _INLINE_PATTERNS.index(next(p for p in _INLINE_PATTERNS if p[0] == x[2]))))
    accepted = []
    last_end = 0
    for start, end, kind, m in matches:
        if start < last_end:
            continue  # 이미 처리된 영역과 겹침
        accepted.append((start, end, kind, m))
        last_end = end
    accepted.sort(key=lambda x: x[0])

    result: list[dict] = []
    cursor = 0
    for start, end, kind, m in accepted:
        if start > cursor:
            result.append({"type": "text", "text": {"content": s[cursor:start]}})
        if kind == "code":
            result.append({"type": "text", "text": {"content": m.group(1)},
                          "annotations": {"code": True}})
        elif kind == "bold":
            result.append({"type": "text", "text": {"content": m.group(1)},
                          "annotations": {"bold": True}})
        elif kind == "link":
            url_val = m.group(2)
            if url_val.startswith(("http://", "https://", "mailto:")):
                result.append({"type": "text",
                              "text": {"content": m.group(1), "link": {"url": url_val}}})
            else:
                # 상대경로/빈 URL — 노션 거부 → plain 으로 폴백
                result.append({"type": "text",
                              "text": {"content": f"[{m.group(1)}]({url_val})"}})
        elif kind == "italic":
            result.append({"type": "text", "text": {"content": m.group(1)},
                          "annotations": {"italic": True}})
        cursor = end
    if cursor < len(s):
        result.append({"type": "text", "text": {"content": s[cursor:]}})
    return result or [{"type": "text", "text": {"content": s}}]


# Notion API: 블록 하나의 rich_text 배열은 최대 100개 요소.
# 인라인 서식(**굵게**/`코드`)이 많은 긴 문단은 이 한도를 쉽게 넘고, 넘으면 그 블록만이 아니라
# 페이지 등록 요청 전체가 400 으로 죽는다 (실사고 2026-08-10: heading_2 에 119개 → 노션 누락).
NOTION_RICH_TEXT_MAX = 100
# 헤딩은 길어질 이유가 없다. 본문이 통째로 헤딩에 들어온 이상 케이스를 여기서 끊는다.
NOTION_HEADING_MAX_CHARS = 200


def _block(btype: str, text: str) -> dict:
    if btype.startswith("heading_") and len(text) > NOTION_HEADING_MAX_CHARS:
        logger.warning(
            "%s 텍스트 %d자 → %d자로 절단 (본문이 헤딩으로 붙은 이상 케이스)",
            btype, len(text), NOTION_HEADING_MAX_CHARS,
        )
        text = text[:NOTION_HEADING_MAX_CHARS].rstrip() + "…"
    rt = _rich_text(text)
    if len(rt) > NOTION_RICH_TEXT_MAX:
        logger.warning("%s rich_text %d개 → %d개로 병합", btype, len(rt), NOTION_RICH_TEXT_MAX)
        keep = rt[: NOTION_RICH_TEXT_MAX - 1]
        tail = "".join(r.get("text", {}).get("content", "") for r in rt[NOTION_RICH_TEXT_MAX - 1:])
        keep.append({"type": "text", "text": {"content": tail[:1900]}})
        rt = keep
    return {
        "object": "block",
        "type": btype,
        btype: {"rich_text": rt},
    }


def _grade_label(g: str) -> str:
    return {"S": "즉시적용", "A": "참고가치", "B": "나중에", "C": "스킵"}.get(g, "")


# TEMPLATE v2 (2026-05-15) — 카테고리 7개 단순화 매핑
# v1 8종 + 옛 표기 모두 → v2 7종으로 정리
CATEGORY_TO_DB = {
    # v2 표준
    "프롬프트": "프롬프트",
    "자동화": "자동화",
    "콘텐츠": "콘텐츠",
    "디자인": "디자인",
    "개발": "개발",
    "업무": "업무",
    "기타": "기타",
    # v1 호환 (점진적 마이그레이션)
    "에이전트·자동화": "자동화",
    "에이전트/자동화": "자동화",
    "영상·콘텐츠": "콘텐츠",
    "영상/콘텐츠": "콘텐츠",
    "디자인·이미지": "디자인",
    "디자인/이미지": "디자인",
    "코딩·개발": "개발",
    "코딩/개발": "개발",
    "업무효율": "업무",
    "마케팅·SNS": "콘텐츠",
    "마케팅/SNS": "콘텐츠",
}

DIFFICULTY_TO_DB = {
    "초급": "🟢 초보OK",
    "초보": "🟢 초보OK",
    "🟢 초보OK": "🟢 초보OK",
    "중급": "🟡 중급",
    "🟡 중급": "🟡 중급",
    "고급": "🔴 고급",
    "🔴 고급": "🔴 고급",
}

SOURCE_TYPE_TO_DB = {
    "youtube": "유튜브",
    "github": "GitHub",
    "notion": "노션",
    "web": "웹",
    "instagram": "웹",
    "tiktok": "웹",
    "twitter": "웹",
}

# v2 카테고리 7개 → 페이지 아이콘 매핑
CATEGORY_ICON = {
    "프롬프트": "💬",
    "자동화": "🤖",
    "콘텐츠": "🎬",
    "디자인": "🎨",
    "개발": "💻",
    "업무": "⚡",
    "기타": "📦",
}

# 제목 시작 이모지 자동 제거용
# 주의: 이전 정규식의 ` -⁯` 는 U+0020~U+206F 로 파싱돼 ASCII 알파벳까지 삼키는 버그가 있었음
# (예: "AI 활용..." → "I 활용..."). 이모지 유니코드 블록만 명시적으로 나열.
import re as _re
_TITLE_EMOJI_RE = _re.compile(
    r'^(?:'
    r'[\U0001F300-\U0001FAFF]'       # main emoji planes (symbols/pictographs/faces)
    r'|[☀-➿]'              # misc symbols + dingbats
    r'|[⌀-⏿]'              # misc technical
    r'|[⬀-⯿]'              # misc symbols and arrows
    r'|[←-⇿]'              # arrows
    r'|[︀-️]'              # variation selectors
    r'|\U0001F1E6-\U0001F1FF'        # regional indicators (flags)
    r')\s*'
)


def _clean_title(title: str) -> str:
    """제목에서 시작 이모지 제거 (페이지 아이콘과 중복 방지)."""
    return _TITLE_EMOJI_RE.sub("", title).strip()

# DB에 존재하는 옵션만 (없으면 무시)
DB_AI_TOOLS = {
    "Claude", "GPT", "Gemini", "Midjourney", "Leonardo AI", "CapCut", "Canva",
    "Cursor", "Codex", "ComfyUI", "Stable Diffusion", "Ollama", "Claude Code", "도구무관",
}
DB_TAGS = {
    # v2 표준 — 기술/방법 키워드 (15종, 카테고리와 안 겹침)
    "MCP", "API", "RAG", "Function Calling", "Vision", "Multimodal",
    "프롬프트체이닝", "CoT", "Tool Use", "Webhook", "Streaming",
    "CLI", "GitHub Actions", "자체호스팅", "오픈소스",
}
DB_TARGETS = {"두근펫", "매매봇", "검은별", "클로드코드", "AI900", "첼시인스타", "이모티콘", "공통"}


def _properties(result: "AnalysisResult", source_url: str, source_type: str) -> dict:
    """v2.4: 6개 핵심 속성만 (태그·적용대상·상태 폐기).

    유지: 스킬명 / 카테고리(어떤 류) / 등급 / 난이도 / AI 도구(어떤 툴) / 출처 URL.
    """
    category = CATEGORY_TO_DB.get(result.category, "기타")
    difficulty = DIFFICULTY_TO_DB.get(result.difficulty, "🟡 중급")
    ai_tools = [t for t in result.ai_tools if t in DB_AI_TOOLS][:10]
    clean_title = _clean_title(result.skill_title_ko)

    return {
        "스킬명": {"title": [{"text": {"content": clean_title}}]},
        "카테고리": {"select": {"name": category}},
        "등급": {"select": {"name": f"{result.grade}-{_grade_label(result.grade)}"}},
        "난이도": {"select": {"name": difficulty}},
        "AI 도구": {"multi_select": [{"name": t} for t in ai_tools]},
        "출처 URL": {"url": source_url},
    }


def register_skill(
    result: "AnalysisResult",
    source_url: str,
    source_type: str,
    skill_md_content: str,
    existing_page_id: Optional[str] = None,
) -> dict:
    """Notion DB에 등록/갱신.

    반환:
        {"ok": True, "page_id": "...", "action": "created" | "updated"}
        {"ok": False, "error_ko": "...", "code": "...", "hint": "..."}
    """
    if not _api_key() or not _db_id():
        return {
            "ok": False,
            "error_ko": "Notion 환경변수 미설정",
            "code": "no_config",
            "hint": ".env에 NOTION_API_KEY + NOTION_DB_ID 설정",
        }

    if result.grade == "C":
        return {"ok": False, "error_ko": "등급 C — Notion 등록 안 함", "code": "grade_c", "hint": ""}

    properties = _properties(result, source_url, source_type)
    blocks = _markdown_to_blocks(skill_md_content)

    try:
        if existing_page_id:
            # 기존 페이지 갱신
            _request("PATCH", f"pages/{existing_page_id}",
                     {"properties": properties}, context="페이지 속성 갱신")
            # 기존 블록 삭제 (best-effort)
            try:
                children = _request("GET", f"blocks/{existing_page_id}/children", context="블록 조회")
                for child in children.get("results", []):
                    try:
                        _request("DELETE", f"blocks/{child['id']}", context="블록 삭제")
                    except NotionError:
                        pass
            except NotionError as e:
                logger.warning("기존 블록 정리 실패 (계속): %s", e)
            # 새 블록 추가 — Notion API 는 한 호출당 children 100개 한도, chunk 분할.
            _append_blocks_chunked(existing_page_id, blocks)
            logger.info("Notion 페이지 갱신 완료: %s (블록 %d)", existing_page_id, len(blocks))
            return {"ok": True, "page_id": existing_page_id, "action": "updated"}

        # 카테고리에 맞는 아이콘 자동 설정 (제목은 이미 텍스트만)
        category_value = properties.get("카테고리", {}).get("select", {}).get("name", "기타")
        icon_emoji = CATEGORY_ICON.get(category_value, "📦")

        # children 100개 한도 — 첫 100개로 페이지 생성, 나머지는 PATCH 로 append.
        first_chunk = blocks[:NOTION_CHILDREN_MAX]
        rest = blocks[NOTION_CHILDREN_MAX:]
        data = _request("POST", "pages", {
            "parent": {"database_id": _db_id()},
            "icon": {"type": "emoji", "emoji": icon_emoji},
            "properties": properties,
            "children": first_chunk,
        }, context="페이지 생성")
        page_id = data.get("id", "")
        if rest and page_id:
            _append_blocks_chunked(page_id, rest)
        logger.info(
            "Notion 신규 등록 완료: %s (아이콘 %s, 블록 %d)",
            page_id, icon_emoji, len(blocks),
        )
        return {"ok": True, "page_id": page_id, "action": "created"}

    except NotionError as e:
        logger.error("Notion 등록 실패: %s (hint=%s)", e, e.hint)
        return {"ok": False, **e.to_dict()}
    except Exception as e:  # noqa: BLE001
        logger.exception("Notion 예기치 못한 오류")
        return {
            "ok": False,
            "error_ko": f"Notion 알 수 없는 오류: {e}",
            "code": "unknown",
            "hint": "logs/launchd_stderr.log 확인",
        }
