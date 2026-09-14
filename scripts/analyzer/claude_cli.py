"""Claude 구독(claude -p) 을 분석 프로바이더로 쓰는 얇은 래퍼 (v5.2).

왜: SKILL.md 본문은 이 파이프라인에서 품질이 가장 중요한 산출물인데, Gemini 2.5 Flash 는
프로젝트당 하루 20회 뒤 Gemma 로컬로 떨어진다 (gotcha 47 · memory project_gemini_key_shared_quota).
Max 플랜은 이미 있고(채팅·fix 러너가 쓴다) 스킬 1건이 15~30k 토큰이라 하루 10건이면 플랜의
한 자릿수 % 다. 그래서 analyze() 의 순서를 Claude → Gemini → Gemma 로 바꿨다.

두 가지 호출:
- call_claude_json(prompt, schema=)       도구 0개 + --json-schema. 순수 생성 (스킬 분석·검증 재요청)
- call_claude_read_files(prompt, files)   Read 도구 하나만 허용, 임시 폴더를 cwd 로. 슬라이드(이미지) 판독.
  영상·음성은 Claude 가 입력으로 못 받는다 — 그건 media_understand 가 계속 Gemini 로 보낸다.

운영 규칙 (chat/engine.py 와 같은 함정 — gotcha 19·20·35·49):
- `--setting-sources ""`   글로벌 CLAUDE.md/rules/스킬 로드 차단 (74k → 6k 토큰)
- `--strict-mcp-config`    사용자 MCP 서버(노션/Gmail 등) 로드 차단
- `--tools ""`             분석 호출은 도구 0개 — 모델이 Read/Bash 로 딴짓 못 하게. 판독 호출만 Read
- `--bare` 금지             OAuth(구독) 를 무시한다
- stdin 은 DEVNULL          안 주면 "no stdin data received in 3s" 를 기다린다
- 한도 도달 → 쿨다운         같은 5시간 창을 사용자의 코딩과 나눠 쓴다. 한도 메시지가 뜨면 이 프로세스에서
                           더 두드리지 않고 (config analyzer.claude_cooldown_minutes, 기본 30분) Gemini/Gemma 로
- 끄기                      env ANALYZER_CLAUDE=0 또는 config analyzer.claude_enabled=false
이 호출은 119 가드에 `sdk-cli`(자동 실행) 주체로 잡힌다 — A 경보 임계(10분 150K)는 건당 ~20k 라 여유가 있다.
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Callable, Optional

from scripts import config_store
from .prompt import GRADES, CATEGORIES, DIFFICULTIES, AI_TOOLS

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# 빈 샌드박스를 cwd 로 — 코드·.env 에 접근할 일이 없다 (도구가 없어도 습관적으로 격리)
SANDBOX = PROJECT_ROOT / "logs" / "claude_sandbox"
DEFAULT_MODEL = "claude-sonnet-5"
DEFAULT_TIMEOUT = 180
DEFAULT_COOLDOWN_MIN = 30
READ_MAX_TURNS = 12          # Read 호출 1장당 1턴 + 정리 — 슬라이드 상한 10장이면 충분
LIMIT_MARKERS = ("usage limit", "hit your limit", "rate limit", "rate_limit", "limit reached",
                 "limit exceeded", "overloaded", "429")

# analyzer/prompt.py 의 [응답 형식] 과 1:1. enum 은 프롬프트 상수에서 그대로 — 두 곳이 어긋나면
# 모델이 옳게 답해도 _validate 가 C 로 강등한다 (gotcha 48). SchemaTest 가 동기화를 지킨다.
SKILL_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "skill_name": {"type": "string", "description": "kebab-case 영문 슬러그"},
        "skill_title_ko": {"type": "string", "description": "8-15자 동사형 한국어 제목 (이모지 X)"},
        "callout": {"type": "string", "description": "이 스킬이 뭔지 1~2문장. 핵심 키워드 **굵게**"},
        "category": {"type": "string", "enum": list(CATEGORIES)},
        "grade": {"type": "string", "enum": list(GRADES)},
        "grade_reason": {"type": "string"},
        "difficulty": {"type": "string", "enum": list(DIFFICULTIES)},
        "ai_tools": {"type": "array", "items": {"type": "string", "enum": list(AI_TOOLS)}},
        "body_md": {"type": "string", "description": "본문 마크다운. callout 은 넣지 않는다"},
    },
    "required": ["skill_name", "skill_title_ko", "callout", "category", "grade",
                 "grade_reason", "difficulty", "ai_tools", "body_md"],
}

# 합병(merger) 응답 — 분석 스키마 + legacy 메타 5종(있으면 받고 없어도 통과)
MERGE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        **SKILL_SCHEMA["properties"],
        "targets": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
        "when_to_use": {"type": "string"},
        "memo": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
    "required": list(SKILL_SCHEMA["required"]),
}

Runner = Callable[..., tuple[int, str, str]]
_paused_until: float = 0.0


# ── 설정 ────────────────────────────────────────────────────────
def _cfg(key: str, default):
    return config_store.get(f"analyzer.{key}", default)


def _binary() -> Optional[str]:
    found = shutil.which("claude")
    if found:
        return found
    for cand in ("/opt/homebrew/bin/claude", os.path.expanduser("~/.local/bin/claude")):
        if os.path.exists(cand):
            return cand
    return None


def enabled() -> bool:
    env = os.getenv("ANALYZER_CLAUDE")
    if env is not None:
        return env.strip().lower() not in ("0", "false", "no", "off", "")
    return bool(_cfg("claude_enabled", True))


def model() -> str:
    return os.getenv("ANALYZER_CLAUDE_MODEL") or str(_cfg("claude_model", DEFAULT_MODEL))


def timeout_seconds() -> int:
    return int(_cfg("claude_timeout_seconds", DEFAULT_TIMEOUT))


# ── 한도 쿨다운 ──────────────────────────────────────────────────
def is_paused() -> bool:
    return time.time() < _paused_until


def reset_pause() -> None:
    global _paused_until
    _paused_until = 0.0


def note_limit(reason: str) -> None:
    global _paused_until
    minutes = int(_cfg("claude_cooldown_minutes", DEFAULT_COOLDOWN_MIN))
    _paused_until = time.time() + minutes * 60
    logger.warning("Claude 한도 감지 → %d분 쿨다운 (Gemini/Gemma 로 진행): %s", minutes, reason[:200])


def _is_limit(msg: str) -> bool:
    m = (msg or "").lower()
    return any(k in m for k in LIMIT_MARKERS)


# ── 명령줄 ──────────────────────────────────────────────────────
def _base_cmd(binary: str, *, tools: str, extra: list[str]) -> list[str]:
    return [
        binary,
        "--model", model(),
        "--setting-sources", "",
        "--strict-mcp-config",
        "--disable-slash-commands",
        "--tools", tools,
        "--output-format", "json",
        *extra,
    ]


def build_json_cmd(prompt: str, *, schema: Optional[dict] = None, binary: Optional[str] = None) -> list[str]:
    extra = ["--json-schema", json.dumps(schema, ensure_ascii=False)] if schema else []
    return _base_cmd(binary or _binary() or "claude", tools="", extra=extra) + ["-p", prompt]


def build_read_cmd(prompt: str, *, binary: Optional[str] = None, max_turns: int = READ_MAX_TURNS) -> list[str]:
    extra = ["--allowedTools", "Read", "--max-turns", str(max_turns)]
    return _base_cmd(binary or _binary() or "claude", tools="Read", extra=extra) + ["-p", prompt]


# ── 실행 ────────────────────────────────────────────────────────
def default_runner(cmd: list[str], *, cwd: str, timeout: int) -> tuple[int, str, str]:
    env = dict(os.environ)
    if "/opt/homebrew/bin" not in env.get("PATH", ""):
        env["PATH"] = "/opt/homebrew/bin:" + env.get("PATH", "")
    p = subprocess.run(
        cmd, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True,
        text=True, encoding="utf-8", errors="replace", timeout=timeout, env=env,
    )
    return p.returncode, p.stdout, p.stderr


def parse_envelope(stdout: str) -> tuple[Optional[dict], str]:
    """--output-format json 의 envelope → (dict, "") 또는 (None, 한글 사유). 실패 사유는 stdout 에 있다 (gotcha 19)."""
    raw = (stdout or "").strip()
    if not raw:
        return None, "빈 응답 (stdout empty)"
    try:
        env = json.loads(raw)
    except Exception:  # noqa: BLE001
        return None, f"envelope JSON 파싱 실패: {raw[:200]}"
    if not isinstance(env, dict):
        return None, "envelope 형식 아님"
    if env.get("is_error"):
        reason = str(env.get("result") or env.get("terminal_reason") or "unknown")
        return None, f"CLI 에러: {reason[:300]}"
    return env, ""


def _execute(cmd: list[str], *, cwd: Path, timeout: int, runner: Runner) -> Optional[dict]:
    """공통 실행 → envelope dict. 실패는 None (사유 로그). 한도 메시지면 쿨다운."""
    try:
        rc, out, err = runner(cmd, cwd=str(cwd), timeout=timeout)
    except subprocess.TimeoutExpired:
        logger.warning("claude -p 타임아웃 (%ds)", timeout)
        return None
    except Exception as e:  # noqa: BLE001
        logger.warning("claude -p 실행 실패: %s", e)
        return None
    env, perr = parse_envelope(out)
    if env is None:
        tail = (err or "").strip()[-300:]
        if _is_limit(perr) or _is_limit(tail):
            note_limit(perr or tail)
        logger.warning("claude -p 실패 (rc=%s): %s %s", rc, perr, tail)
        return None
    return env


def _ready() -> Optional[str]:
    """호출 가능하면 바이너리 경로, 아니면 None (사유는 로그)."""
    if not enabled():
        return None
    if is_paused():
        logger.info("Claude 쿨다운 중 (%.0f초 남음) — 건너뜀", _paused_until - time.time())
        return None
    binary = _binary()
    if not binary:
        logger.info("claude CLI 없음 — 건너뜀")
        return None
    return binary


def call_claude_json(prompt: str, *, schema: Optional[dict] = None, timeout: Optional[int] = None,
                     runner: Optional[Runner] = None) -> Optional[str]:
    """도구 없는 순수 생성. 반환은 JSON 텍스트 (structured_output 우선, 없으면 result 본문). 실패·비활성·쿨다운은 None."""
    binary = _ready()
    if not binary:
        return None
    SANDBOX.mkdir(parents=True, exist_ok=True)
    cmd = build_json_cmd(prompt, schema=schema, binary=binary)
    env = _execute(cmd, cwd=SANDBOX, timeout=timeout or timeout_seconds(), runner=runner or default_runner)
    if env is None:
        return None
    struct = env.get("structured_output")
    if isinstance(struct, dict) and struct:
        return json.dumps(struct, ensure_ascii=False)
    text = str(env.get("result") or "").strip()
    return text or None


def call_claude_read_files(prompt: str, files: list[tuple[str, bytes]], *, timeout: Optional[int] = None,
                           runner: Optional[Runner] = None, max_turns: int = READ_MAX_TURNS) -> Optional[str]:
    """파일들을 임시 폴더에 쓰고 그 폴더를 cwd 로 Read 도구만 허용해 읽힌다. 반환은 result 본문."""
    binary = _ready()
    if not binary:
        return None
    SANDBOX.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="read-", dir=SANDBOX))
    try:
        names: list[str] = []
        for name, data in files:
            safe = Path(name).name or "file"          # 경로 탈출 방지 — 폴더 안 이름만
            (work / safe).write_bytes(data)
            names.append(safe)
        full = (prompt + "\n\n읽을 파일 (현재 폴더, 이 순서대로 Read 도구로 열어라): " + ", ".join(names))
        cmd = build_read_cmd(full, binary=binary, max_turns=max_turns)
        env = _execute(cmd, cwd=work, timeout=timeout or timeout_seconds(), runner=runner or default_runner)
        if env is None:
            return None
        text = str(env.get("result") or "").strip()
        return text or None
    finally:
        shutil.rmtree(work, ignore_errors=True)
