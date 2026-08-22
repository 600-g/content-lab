#!/usr/bin/env python3
"""스킬 라이브러리 MCP 서버 (stdio, JSON-RPC 2.0 newline-delimited) — 표준 라이브러리만 사용.

Claude Code · Cursor · Codex · 다른 클로드 계정 등 MCP 클라이언트가 aiskillbox 스킬 라이브러리를
검색하고 SKILL.md 본문을 꺼내 쓰게 한다. 어떤 python3 로도 실행 가능 (venv 불필요).

등록 (Claude Code):
  claude mcp add --scope user skill-library -- python3 /Users/600mac/Developer/my-company/content-lab/scripts/library/mcp_server.py
외부 기기:
  AISKILLBOX_URL=https://aiskillbox.600g.net 환경변수 추가 (claude mcp add -e AISKILLBOX_URL=...)

백엔드: AISKILLBOX_URL (기본 http://localhost:5050) HTTP → 연결 실패 **또는 라이브러리 API 미배포
서버(비 JSON 404 — 구버전 aiskillbox 의 Flask HTML 404)** 시 같은 repo 의 scripts.library 직접
import (로컬 Mac 에서 서버가 내려가도 키워드 검색은 동작). 둘 다 실패 → isError.

stdout 은 JSON-RPC 전용 — 로그는 전부 stderr.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Optional

SERVER_NAME = "skill-library"
SERVER_VERSION = "1.0.0"
DEFAULT_PROTOCOL = "2025-06-18"
SUPPORTED_PROTOCOLS = {"2025-06-18", "2025-03-26", "2024-11-05"}
BASE_URL = os.environ.get("AISKILLBOX_URL", "http://localhost:5050").rstrip("/")
HTTP_TIMEOUT = float(os.environ.get("AISKILLBOX_TIMEOUT", "8"))
LOCAL_ROOT = os.environ.get("SKILL_LIBRARY_ROOT") or None   # 테스트/커스텀 mirror 루트
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAX_K = 20

TOOLS = [
    {
        "name": "search_skills",
        "description": (
            "두근 스킬 라이브러리(SKILL.md 자산)를 자연어로 검색합니다 — 키워드+의미 하이브리드. "
            "작업 중 '이런 스킬/프롬프트/워크플로우 있나?' 싶을 때 먼저 호출. "
            "결과: slug·제목·한 줄 설명·등급·카테고리·스니펫. 본문은 get_skill(slug)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "자연어 질의 (2자 이상, 한국어/영어)"},
                "k": {"type": "integer", "minimum": 1, "maximum": MAX_K, "description": "결과 수 (기본 5)"},
                "category": {
                    "type": "string",
                    "description": "선택 필터: 프롬프트|자동화|콘텐츠|디자인|개발|업무|기타",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_skill",
        "description": "슬러그로 SKILL.md 전문(frontmatter 포함 마크다운)을 가져옵니다. 컨텍스트에 그대로 넣어 쓰세요.",
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string", "description": "search_skills 결과의 slug"}},
            "required": ["slug"],
        },
    },
    {
        "name": "list_skills",
        "description": "라이브러리 전체(또는 카테고리/등급 필터) 목록 — slug·제목·등급·카테고리 한 줄씩.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "프롬프트|자동화|콘텐츠|디자인|개발|업무|기타"},
                "grade": {"type": "string", "description": "S|A|B|C"},
            },
            "required": [],
        },
    },
]


def _log(msg: str) -> None:
    sys.stderr.write(f"[skill-library-mcp] {msg}\n")
    sys.stderr.flush()


# ── 백엔드 ──────────────────────────────────────────────────────

class BackendError(Exception):
    pass


def _http_get(path: str, params: dict | None = None) -> dict:
    qs = ("?" + urllib.parse.urlencode({k: v for k, v in (params or {}).items() if v not in (None, "")})) if params else ""
    headers = {"Accept": "application/json", "User-Agent": "skill-library-mcp/1.0"}
    # v4.6 전체 잠금 — 초대코드로 발급받은 기기 토큰을 env 로 전달
    token = os.environ.get("AISKILLBOX_TOKEN", "").strip()
    if token:
        headers["X-Auth-Token"] = token
    req = urllib.request.Request(BASE_URL + path + qs, headers=headers)
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


_LOCAL: dict[str, Any] = {}


def _local():
    """로컬 폴백 — scripts.library 지연 import (같은 repo 에서만 가능)."""
    if "mod" in _LOCAL:
        return _LOCAL["mod"]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from scripts.library import index as lib_index  # noqa: WPS433
        from scripts.library import search as lib_search  # noqa: WPS433
    except Exception as e:  # noqa: BLE001
        raise BackendError(f"HTTP 백엔드 연결 실패 + 로컬 인덱스 import 불가: {e}") from e
    _LOCAL["mod"] = (lib_index, lib_search)
    return _LOCAL["mod"]


def _http_error_json(e: urllib.error.HTTPError) -> Optional[dict]:
    """HTTPError 본문이 라이브러리 API 의 JSON envelope 면 dict, 아니면 None.

    None = 라이브러리 라우트가 없는 서버 (구버전 aiskillbox 의 Flask HTML 404 등)
    → 호출부가 로컬 인덱스 폴백을 탄다. JSON 으로 응답했다면 API 는 배포돼 있는 것.

    예외: 401(로그인 필요) 은 JSON 이어도 None — AISKILLBOX_TOKEN 미설정/회수 기기는
    이 Mac 의 로컬 인덱스 폴백으로 계속 동작한다 (v4.6 전체 잠금).
    """
    if e.code == 401:
        _log("HTTP 401 (초대코드 토큰 필요 — AISKILLBOX_TOKEN env) → 로컬 인덱스 폴백")
        return None
    try:
        data = json.loads(e.read().decode("utf-8"))
    except Exception:  # noqa: BLE001
        return None
    return data if isinstance(data, dict) else None


def _local_search(query: str, k: int, category: str) -> dict:
    lib_index, lib_search = _local()
    idx = lib_index.get_index(LOCAL_ROOT)
    return lib_search.search(query, k=k, category=category or None, index=idx)


def _local_get_raw(slug: str) -> Optional[str]:
    lib_index, _ = _local()
    rec = lib_index.get_index(LOCAL_ROOT).get(slug)
    return rec.raw_md if rec else None


def _local_list(category: str, grade: str) -> list[dict]:
    lib_index, _ = _local()
    idx = lib_index.get_index(LOCAL_ROOT)
    items = idx.filter(category=category or None, grade=(grade or "").upper() or None)
    return [r.meta() for r in items]


def backend_search(query: str, k: int, category: str) -> tuple[dict, str]:
    try:
        return _http_get("/api/library/search", {"q": query, "k": k, "category": category}), "http"
    except urllib.error.HTTPError as e:
        data = _http_error_json(e)
        if data is not None:
            return data, "http"
        _log(f"HTTP {e.code} 비 JSON 응답 (라이브러리 API 미배포 서버) → 로컬 인덱스 폴백")
        return _local_search(query, k, category), "local"
    except Exception as e:  # noqa: BLE001
        _log(f"HTTP 실패({e.__class__.__name__}) → 로컬 인덱스 폴백")
        return _local_search(query, k, category), "local"


def backend_get(slug: str) -> tuple[Optional[str], str]:
    try:
        data = _http_get(f"/api/library/skills/{urllib.parse.quote(slug)}")
        return data.get("raw_md"), "http"
    except urllib.error.HTTPError as e:
        data = _http_error_json(e)
        if data is not None:
            if e.code == 404:
                return None, "http"  # 라이브러리 API 의 정상 404 — 스킬 없음
            raise BackendError(f"HTTP {e.code}: {data.get('error') or ''}".rstrip(": ")) from e
        _log(f"HTTP {e.code} 비 JSON 응답 (라이브러리 API 미배포 서버) → 로컬 인덱스 폴백")
        return _local_get_raw(slug), "local"
    except Exception as e:  # noqa: BLE001
        _log(f"HTTP 실패({e.__class__.__name__}) → 로컬 인덱스 폴백")
        return _local_get_raw(slug), "local"


def backend_list(category: str, grade: str) -> tuple[list[dict], str]:
    try:
        data = _http_get("/api/library/skills", {"category": category, "grade": grade})
        return data.get("items", []), "http"
    except urllib.error.HTTPError as e:
        data = _http_error_json(e)
        if data is not None:
            raise BackendError(f"HTTP {e.code}: {data.get('error') or ''}".rstrip(": ")) from e
        _log(f"HTTP {e.code} 비 JSON 응답 (라이브러리 API 미배포 서버) → 로컬 인덱스 폴백")
        return _local_list(category, grade), "local"
    except Exception as e:  # noqa: BLE001
        _log(f"HTTP 실패({e.__class__.__name__}) → 로컬 인덱스 폴백")
        return _local_list(category, grade), "local"


# ── 포맷 ────────────────────────────────────────────────────────

def _mode_tag(mode: str) -> str:
    return "" if mode == "http" else " (로컬 인덱스 폴백 — aiskillbox 서버 미응답)"


def fmt_search(res: dict, mode: str) -> str:
    if not res.get("ok"):
        raise BackendError(res.get("error", "검색 실패"))
    lines = [
        f"🔎 '{res.get('query')}' — {len(res.get('results', []))}건 / 인덱스 {res.get('total_indexed')}건"
        f"{' · 의미검색 포함' if res.get('semantic_used') else ' · 키워드만'}{_mode_tag(mode)}"
    ]
    for i, r in enumerate(res.get("results", []), start=1):
        lines.append(
            f"\n{i}. {r.get('title')}  [{r.get('slug')}]\n"
            f"   등급 {r.get('grade') or '-'} · {r.get('category')} · {', '.join(r.get('ai_tools') or []) or '도구 미지정'}\n"
            f"   {r.get('description', '')}\n"
            + (f"   ↳ {r.get('snippet')}\n" if r.get("snippet") else "")
            + f"   get_skill(\"{r.get('slug')}\") 로 본문 · 사람용 게시글 {BASE_URL}/skill/{r.get('slug')}"
        )
    if not res.get("results"):
        lines.append("\n결과 없음 — 다른 표현으로 다시 검색하거나 list_skills 로 목록을 보세요.")
    return "\n".join(lines)


def fmt_list(items: list[dict], mode: str) -> str:
    lines = [f"📚 스킬 {len(items)}건{_mode_tag(mode)}"]
    for r in items:
        lines.append(f"- [{r.get('slug')}] {r.get('title')} — 등급 {r.get('grade') or '-'} · {r.get('category')}")
    return "\n".join(lines)


# ── 도구 실행 ────────────────────────────────────────────────────

def _clamp_k(v: Any) -> int:
    try:
        return max(1, min(MAX_K, int(v)))
    except (TypeError, ValueError):
        return 5


def call_tool(name: str, args: dict) -> tuple[str, bool]:
    """(text, is_error)."""
    try:
        if name == "search_skills":
            query = str(args.get("query", "")).strip()
            if len(query) < 2:
                return "query 는 2자 이상이어야 합니다.", True
            res, mode = backend_search(query, _clamp_k(args.get("k", 5)), str(args.get("category", "") or ""))
            return fmt_search(res, mode), False
        if name == "get_skill":
            slug = str(args.get("slug", "")).strip()
            if not slug or "/" in slug or ".." in slug:
                return "slug 가 비었거나 잘못됐습니다.", True
            raw, mode = backend_get(slug)
            if raw is None:
                return f"스킬 없음: {slug} — search_skills 로 먼저 찾아보세요.", True
            return raw + _mode_tag(mode), False
        if name == "list_skills":
            items, mode = backend_list(str(args.get("category", "") or ""), str(args.get("grade", "") or ""))
            return fmt_list(items, mode), False
        return f"알 수 없는 도구: {name}", True
    except BackendError as e:
        return f"백엔드 오류: {e}", True
    except Exception as e:  # noqa: BLE001
        _log(f"tool {name} 예외: {e!r}")
        return f"도구 실행 실패: {e}", True


# ── JSON-RPC 디스패치 ─────────────────────────────────────────────

def _ok(req_id: Any, result: Any) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _err(req_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def handle(msg: dict) -> Optional[dict]:
    method = msg.get("method")
    req_id = msg.get("id")
    params = msg.get("params") or {}
    is_notification = "id" not in msg
    if method == "initialize":
        requested = str(params.get("protocolVersion") or DEFAULT_PROTOCOL)
        proto = requested if requested in SUPPORTED_PROTOCOLS else DEFAULT_PROTOCOL
        return _ok(req_id, {
            "protocolVersion": proto,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "instructions": (
                "두근컴퍼니 스킬 라이브러리. 작업 전에 search_skills 로 관련 SKILL.md 가 있는지 확인하고, "
                "있으면 get_skill 로 본문을 가져와 그대로 따르세요."
            ),
        })
    if is_notification:
        return None  # notifications/initialized, notifications/cancelled 등 — 응답 없음
    if method == "ping":
        return _ok(req_id, {})
    if method == "tools/list":
        return _ok(req_id, {"tools": TOOLS})
    if method == "tools/call":
        name = str(params.get("name", ""))
        args = params.get("arguments") or {}
        if not isinstance(args, dict):
            args = {}
        text, is_error = call_tool(name, args)
        return _ok(req_id, {"content": [{"type": "text", "text": text}], "isError": is_error})
    return _err(req_id, -32601, f"Method not found: {method}")


def main() -> int:
    _log(f"시작 — backend={BASE_URL} (로컬 폴백 root={LOCAL_ROOT or PROJECT_ROOT / 'skills'})")
    out = sys.stdout
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            out.write(json.dumps(_err(None, -32700, f"Parse error: {e.msg}")) + "\n")
            out.flush()
            continue
        if not isinstance(msg, dict):
            out.write(json.dumps(_err(None, -32600, "Invalid Request")) + "\n")
            out.flush()
            continue
        try:
            resp = handle(msg)
        except Exception as e:  # noqa: BLE001
            _log(f"handle 예외: {e!r}")
            resp = _err(msg.get("id"), -32603, f"Internal error: {e}")
        if resp is not None:
            out.write(json.dumps(resp, ensure_ascii=False) + "\n")
            out.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
