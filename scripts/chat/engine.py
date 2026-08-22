"""채팅 엔진 — tool use loop. 프로바이더 2종:

1. Anthropic Messages API (ANTHROPIC_API_KEY 있을 때) — Opus
2. Gemini 2.5 Flash function calling (기본 — 무료 1500/day, GEMINI_API_KEY 재사용)

- requests 만 사용 (SDK 의존 X).
- 모델 호출 → tool/function call 이 있으면 dispatch → 결과로 재호출. 최대 8 라운드.
- mutating 도구는 모델이 호출해도 safety 토큰이 없으면 거부되고, 그 사실이
  결과로 모델에 전달돼 모델이 사용자에게 "PIN 입력 필요" 답함.
- Gemini 는 thinking 모델 — thinkingConfig.thinkingBudget:0 필수 (없으면 사고
  토큰이 출력 예산 잠식 → 빈 응답. feedback_ollama_thinking_models.md 참조).
"""
from __future__ import annotations

import json
import logging
import os
from typing import Optional

import requests

from scripts import config_store
from scripts.chat import history, tools

logger = logging.getLogger(__name__)

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
MAX_ROUNDS = 8


def _system_prompt() -> str:
    return (
        "너는 두근컴퍼니 aiskillbox(콘텐츠랩) 의 운영 보조 에이전트다. "
        "한국어로 짧고 명확하게 답한다.\n\n"
        "역할: 사용자(두근컴퍼니 오너)의 자연어 요청을 듣고, "
        "허용된 도구만 사용해 운영 상태 조회·설정 편집·SKILL.md 수정·중복 합병·코드 수정 위임을 수행한다.\n\n"
        "규칙:\n"
        "- 코드 본체(app.py / scripts/**/*.py / static/*.js) 는 이 채팅에서 직접 수정하지 않는다. "
        "대신 스크랩 실패·버그 등 코드 수정이 필요하면 escalate_fix 도구로 로컬 Claude Code 에 위임한다. "
        "위임 전에 recent_jobs / tail_log 로 원인을 1차 진단하고, instruction 에 "
        "증상 + 의심 원인 + 검증 방법을 요약해 담아라. 실패 잡 id 는 job_id 로, 문제 URL 은 "
        "failed_url 로 함께 넘겨라 (자동 재스크랩 검증에 사용). 진행 상황은 fix_status 로 확인, "
        "완료/실패 시 사용자 폰에 Web Push 가 간다.\n"
        "- 도구가 mutating 인데 세션이 없으면 친절하게 'PIN 한 번만 입력해주세요' 안내 "
        "(PIN 값 자체는 절대 언급 금지). 이미 PIN 입력해 토큰 받은 상태면 그냥 실행.\n"
        "- 결과 보고는 한 단락 또는 짧은 bullet. 긴 dump 는 금지.\n"
        "- 비밀(.env API 키 등) 은 절대 응답 본문에 그대로 노출하지 않는다.\n"
        "- 실패/에러/고장 언급이 나오면 사용자에게 되묻기 전에 recent_jobs(limit 10) 와 tail_log 로 "
        "스스로 먼저 진단하라. 최근 실패 잡이 있으면 그것을 대상으로 진행하고, 정말 없을 때만 물어라. "
        "80% 확신이면 실행 후 보고한다.\n"
        "- '확인해볼게요' '살펴볼게요' 같은 예고만 하고 끝내는 답변 금지 — 예고할 상황이면 "
        "그 자리에서 도구를 실제로 호출해 결과까지 같은 턴에 보고하라.\n"
        "- 사용자가 모호하게 말하면 (예: '그거 합쳐줘') 후보 1-2개 제시하고 선택받기.\n"
        "- 'OO 관련 스킬 있어?' '이런 거 어떻게 해?' 같이 스킬을 찾는 질문이면 search_library 를 먼저 호출해 "
        "상위 후보(슬러그·제목·한 줄 설명)를 보여주고, 본문이 필요하면 read_skill_md 로 꺼내 요약한다. "
        "카탈로그 링크는 /catalog#<슬러그>.\n"
        "- 채팅의 핵심 목적: 사용자가 직접 클로드 코드를 열지 않고도 폰에서 운영을 끝낼 수 있게 돕는다."
    )


# ── 프로바이더 선택 ──────────────────────────────────────
def _anthropic_key() -> Optional[str]:
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    return key or None


def _gemini_key() -> Optional[str]:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return key or None


def _claude_cli_available() -> bool:
    import shutil as _sh
    return bool(_sh.which("claude") or os.path.exists("/opt/homebrew/bin/claude"))


def _provider_chain() -> list[str]:
    """시도 순서. chat.provider 설정으로 단일 강제 가능.

    기본(auto): claude_cli(본계정 구독, Sonnet 5) → ollama(로컬 무료).
    Gemini 는 사용자 지시로 자동 체인에서 제외 (chat.provider=gemini 로만 강제 가능).
    """
    pref = str(config_store.get("chat.provider", "auto"))
    if pref in ("anthropic", "gemini", "ollama", "claude_cli"):
        return [pref]
    chain = []
    if _anthropic_key():
        chain.append("anthropic")
    if _claude_cli_available():
        chain.append("claude_cli")
    chain.append("ollama")  # 로컬 최후 폴백 — 가용성은 호출 시 확인
    return chain


def provider() -> str:
    """대표 프로바이더 (상태 표시용)."""
    for p in _provider_chain():
        if p == "ollama" and not _ollama_available():
            continue
        return p
    return "none"


# ── Anthropic ────────────────────────────────────────────
def _call_anthropic(messages: list[dict], system: str) -> dict:
    key = _anthropic_key()
    model = config_store.get("chat.model", "claude-opus-4-8")
    payload = {
        "model": model,
        "max_tokens": 2048,
        "system": system,
        "tools": tools.anthropic_tools(),
        "messages": messages,
    }
    headers = {
        "x-api-key": key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    r = requests.post(ANTHROPIC_URL, json=payload, headers=headers, timeout=60)
    if r.status_code >= 400:
        # 일부 환경에서 모델 alias 미지원 → 1회 폴백.
        if "model" in r.text.lower() and model != "claude-opus-4-7":
            logger.warning("model %s 거부 — claude-opus-4-7 로 폴백", model)
            payload["model"] = "claude-opus-4-7"
            r = requests.post(ANTHROPIC_URL, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    return r.json()


def _extract_text(blocks: list[dict]) -> str:
    parts = [b.get("text", "") for b in blocks if b.get("type") == "text"]
    return "\n\n".join(p for p in parts if p)


def _loop_anthropic(user_text: str, system: str, *, session_token: Optional[str],
                    tool_log: list[dict]) -> dict:
    messages: list[dict] = [{"role": "user", "content": user_text}]
    final_text = ""
    for _round in range(MAX_ROUNDS):
        resp = _call_anthropic(messages, system)
        blocks = resp.get("content", [])
        stop_reason = resp.get("stop_reason")
        text = _extract_text(blocks)
        if text:
            final_text = text

        tool_uses = [b for b in blocks if b.get("type") == "tool_use"]
        if not tool_uses:
            history.log_message("assistant", text, stop_reason=stop_reason)
            break

        messages.append({"role": "assistant", "content": blocks})
        tool_results: list[dict] = []
        for tu in tool_uses:
            name = tu.get("name", "")
            args = tu.get("input", {}) or {}
            result = _dispatch_logged(name, args, session_token, tool_log)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.get("id", ""),
                "content": json.dumps(result, ensure_ascii=False)[:8000],
                "is_error": not result.get("ok"),
            })
        messages.append({"role": "user", "content": tool_results})
        if stop_reason == "end_turn":
            break
    else:
        final_text = (final_text or "") + "\n\n(최대 호출 라운드 도달 — 더 작은 단위로 다시 요청해주세요)"
    return {"ok": True, "reply": final_text or "(빈 응답)", "tool_calls": tool_log}


# ── Gemini function calling ──────────────────────────────
def _to_gemini_schema(schema: dict) -> dict:
    """Anthropic input_schema(JSON Schema) → Gemini Schema. 미지원 키 제거."""
    out: dict = {}
    for k, v in (schema or {}).items():
        if k == "type":
            out["type"] = str(v).upper()
        elif k == "properties" and isinstance(v, dict):
            out["properties"] = {pk: _to_gemini_schema(pv) for pk, pv in v.items()}
        elif k == "items" and isinstance(v, dict):
            out["items"] = _to_gemini_schema(v)
        elif k in ("required", "description", "enum"):
            out[k] = v
        # minimum/maximum 등은 Gemini Schema 미지원 — 드롭
    return out


def _gemini_tools() -> list[dict]:
    decls = []
    for s in tools.REGISTRY.values():
        d: dict = {"name": s.name, "description": s.description}
        props = (s.input_schema or {}).get("properties") or {}
        if props:
            d["parameters"] = _to_gemini_schema(s.input_schema)
        decls.append(d)
    return [{"functionDeclarations": decls}]


def _call_gemini(contents: list[dict], system: str, *, use_tools: bool = True,
                 thinking_off: bool = True) -> dict:
    key = _gemini_key()
    models = [
        str(config_store.get("chat.gemini_model", "gemini-2.5-flash")),
        "gemini-2.5-flash-lite",  # 별도 무료 쿼터 버킷 — 2.5-flash 20/day 소진 시 주력
        "gemini-2.0-flash",
    ]
    payload: dict = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system}]},
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
        },
    }
    if use_tools:
        payload["tools"] = _gemini_tools()
    if thinking_off:
        # 사고 토큰이 출력 예산 잠식 방지. 단, functionResponse 이후 라운드에선
        # budget 0 이 출력 0토큰(빈 content)을 만들 수 있어 마무리 호출은 thinking_off=False.
        payload["generationConfig"]["thinkingConfig"] = {"thinkingBudget": 0}
    last_err: Exception | None = None
    for model in models:
        body = dict(payload)
        if not model.startswith("gemini-2.5"):
            # 2.0 은 thinkingConfig 미지원 — 제거
            gc = dict(body["generationConfig"])
            gc.pop("thinkingConfig", None)
            body["generationConfig"] = gc
        try:
            r = requests.post(
                GEMINI_URL.format(model=model),
                headers={"x-goog-api-key": key},  # 쿼리 파라미터 금지 — 에러 로그에 키 노출됨
                json=body, timeout=60,
            )
            if r.status_code == 429:
                last_err = RuntimeError(f"{model} quota 초과")
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last_err = e
            logger.warning("Gemini %s 실패 — 다음 모델 폴백: %s", model, e)
    raise RuntimeError(f"Gemini 호출 실패: {last_err}")


def _loop_gemini(user_text: str, system: str, *, session_token: Optional[str],
                 tool_log: list[dict]) -> dict:
    contents: list[dict] = [{"role": "user", "parts": [{"text": user_text}]}]
    final_text = ""
    for _round in range(MAX_ROUNDS):
        data = _call_gemini(contents, system)
        cands = data.get("candidates") or []
        parts = ((cands[0].get("content") or {}).get("parts") or []) if cands else []
        texts = [p["text"] for p in parts if isinstance(p, dict) and p.get("text")]
        fcalls = [p["functionCall"] for p in parts if isinstance(p, dict) and p.get("functionCall")]
        if texts:
            final_text = "\n".join(texts).strip()

        if not fcalls:
            history.log_message("assistant", final_text, provider="gemini")
            break

        contents.append({"role": "model", "parts": parts})
        resp_parts = []
        for fc in fcalls:
            name = fc.get("name", "")
            args = fc.get("args") or {}
            result = _dispatch_logged(name, args, session_token, tool_log)
            resp_parts.append({
                "functionResponse": {"name": name, "response": {"result": result}},
            })
        contents.append({"role": "user", "parts": resp_parts})
    else:
        final_text = (final_text or "") + "\n\n(최대 호출 라운드 도달 — 더 작은 단위로 다시 요청해주세요)"

    # 워크어라운드: 도구는 실행했는데 최종 텍스트가 빈 경우 (thinkingBudget:0 +
    # functionResponse 조합에서 출력 0토큰 이슈) — thinking 허용 + 도구 없이 마무리 요청.
    if not final_text and tool_log:
        contents.append({"role": "user", "parts": [{
            "text": "위 도구 결과를 바탕으로 사용자 질문에 한국어로 간결하게 최종 답변만 작성해라.",
        }]})
        data = _call_gemini(contents, system, use_tools=False, thinking_off=False)
        cands = data.get("candidates") or []
        parts = ((cands[0].get("content") or {}).get("parts") or []) if cands else []
        final_text = "\n".join(p["text"] for p in parts if isinstance(p, dict) and p.get("text")).strip()
        history.log_message("assistant", final_text, provider="gemini")

    return {"ok": True, "reply": final_text or "(빈 응답)", "tool_calls": tool_log}


# ── Claude CLI (본계정 구독 — 기본 프로바이더) ────────────
# claude -p (Sonnet 5) 를 라운드마다 호출. 도구는 JSON 프로토콜로 우리 REGISTRY 만 허용
# → 기존 화이트리스트 + PIN 게이트 그대로 유지. cwd 는 빈 샌드박스 (코드/.env 접근 차단).
#
# 핵심 CLI 옵션 (v4.4.3, 2026-07-31 도입):
#   --output-format json    → stdout 이 envelope JSON. structured_output 필드에 스키마 준수 dict.
#   --json-schema '<oneOf>' → tool 호출 또는 reply 강제 (모델이 임의 자연어 못 뱉게).
#   --disable-slash-commands→ CLI 가 자체 스킬/슬래시 커맨드 못 로드하게.
#   --append-system-prompt  → system prompt 를 정식 채널로 (프롬프트 본문에 섞지 않음).
#   -p "<user turn>"        → 순수 사용자 턴만. 이전 대화는 transcript 로 -p 안에 요약해 넘긴다
#                             (CLI 는 세션 없이 매번 fresh — round 간 상태는 우리가 관리).
# `--bare` 는 OAuth/keychain 을 무시하고 ANTHROPIC_API_KEY 만 인식 → 본계정 구독 사용 불가라 금지.
#   --setting-sources ""    → 글로벌 CLAUDE.md/rules/스킬 목록 로드 차단. 미지정 시 라운드당
#                             ~74k 토큰이 시스템 컨텍스트로 붙어 25초+ 지연 + 사용 한도 잠식
#                             (v4.4.4 계측: 74,133 → 6,023 토큰, 25s → 2.7s).
CLI_ROUND_TIMEOUT = 180
PROJECT_ROOT_CHAT = __import__("pathlib").Path(__file__).resolve().parents[2]
CLI_SANDBOX = PROJECT_ROOT_CHAT / "logs" / "chat_sandbox"

# structured output 강제 스키마 — tool 호출 또는 reply 중 정확히 하나.
# Anthropic tool input_schema 는 top-level oneOf/anyOf/allOf 미지원 → 세 필드 모두
# optional 로 두고 프롬프트로 "reply 또는 tool+args 둘 중 하나만" 강제. 파싱 측에서
# reply 우선 처리해서 모델이 둘 다 넣어도 안전.
_CLI_SCHEMA = {
    "type": "object",
    "properties": {
        "reply": {
            "type": "string",
            "description": "최종 답변 (한국어). 도구 호출 없이 사용자에게 직접 답할 때만 채운다.",
        },
        "tool": {
            "type": "string",
            "description": "호출할 도구 이름. 도구 호출이 필요할 때 채우고, 그때는 reply 를 비운다.",
        },
        "args": {
            "type": "object",
            "description": "도구 인자 dict. tool 을 채웠을 때만.",
        },
    },
}


def _cli_tool_catalog() -> str:
    lines = []
    for s in tools.REGISTRY.values():
        props = (s.input_schema or {}).get("properties") or {}
        args = ", ".join(f"{k}:{(v or {}).get('type', 'any')}" for k, v in props.items()) or "인자 없음"
        gate = " [PIN 필요]" if s.mutating else ""
        lines.append(f"- {s.name}({args}){gate} — {s.description}")
    return "\n".join(lines)


def _cli_parse_envelope(stdout: str) -> tuple[dict | None, str]:
    """--output-format json 의 envelope 파싱. Returns (structured, human_error).

    성공 시: (structured_output dict, "")
    실패 시: (None, 한글 에러 요약) — 로그인 문제·quota·model reject 등을 사용자에게 그대로 노출.
    """
    raw = (stdout or "").strip()
    if not raw:
        return None, "빈 응답 (CLI stdout empty)"
    try:
        env = json.loads(raw)
    except Exception:  # noqa: BLE001
        return None, f"envelope JSON 파싱 실패: {raw[:200]}"
    if env.get("is_error"):
        reason = str(env.get("result") or env.get("terminal_reason") or "unknown")
        return None, f"CLI 에러: {reason[:300]}"
    struct = env.get("structured_output")
    if isinstance(struct, dict):
        return struct, ""
    # 스키마 강제됐어도 fallback: result 문자열 안에 JSON 이 문자열로 들어있음.
    result = env.get("result")
    if isinstance(result, str):
        try:
            parsed = json.loads(result)
            if isinstance(parsed, dict):
                return parsed, ""
        except Exception:  # noqa: BLE001
            pass
    return None, f"structured_output 없음: {json.dumps(env)[:300]}"


def _loop_claude_cli(user_text: str, system: str, *, session_token: Optional[str],
                     tool_log: list[dict]) -> dict:
    import shutil as _sh
    import subprocess
    claude_bin = _sh.which("claude") or "/opt/homebrew/bin/claude"
    model = str(config_store.get("chat.claude_model", "claude-sonnet-5"))
    CLI_SANDBOX.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    if "/opt/homebrew/bin" not in env.get("PATH", ""):
        env["PATH"] = "/opt/homebrew/bin:" + env.get("PATH", "")

    tool_directive = (
        "너는 aiskillbox 운영 채팅 API 다. 자연어 설명·확인 예고·과정 서술 모두 금지. "
        "매 턴 정확히 다음 두 형태 중 하나로만 응답한다 (동시에 채우지 마라):\n"
        '  A) 도구 호출이 필요할 때 → {"tool": "<이름>", "args": {...}}  (reply 는 비운다)\n'
        '  B) 사용자에게 직접 답할 때 → {"reply": "<한국어 답변>"}  (tool·args 는 비운다)\n'
        "\n사용 가능한 도구 (이 목록 밖 도구/명령 사용 금지):\n"
        f"{_cli_tool_catalog()}\n"
        "\n원칙:\n"
        "- 상태/실패/설정 질문은 답 예고하지 말고 즉시 조회 도구 호출 (recent_jobs / tail_log / "
        "  fix_status / get_settings 등).\n"
        "- 코드 수정이 필요하면 escalate_fix 호출. 그 전에 recent_jobs 로 실패 잡 확인 필수.\n"
        "- mutating 도구 호출 실패 사유가 'PIN' / '세션' 이면 그 즉시 reply 로 'PIN 1회 입력 필요' 만 짧게 안내.\n"
        "- reply 는 한국어로 3-4문장 이하. 긴 dump 금지."
    )
    system_full = system + "\n\n" + tool_directive

    transcript: list[str] = [f"[사용자] {user_text}"]
    final_text = ""
    schema_str = json.dumps(_CLI_SCHEMA, ensure_ascii=False)

    cmd = [
        claude_bin,
        "--model", model,
        "--setting-sources", "",  # 글로벌 설정/스킬 로드 차단 — 속도 + 한도 절약 (필수)
        "--disable-slash-commands",
        "--append-system-prompt", system_full,
        "--output-format", "json",
        "--json-schema", schema_str,
    ]

    def _run_once(user_turn: str):
        return subprocess.run(
            cmd + ["-p", user_turn],
            cwd=str(CLI_SANDBOX), capture_output=True, text=True,
            timeout=CLI_ROUND_TIMEOUT, env=env,
        )

    for _round in range(MAX_ROUNDS):
        user_turn = (
            "이전 대화/도구 기록 (context):\n"
            + "\n".join(transcript)
            + "\n\n지금 스키마 준수 JSON 오브젝트 하나만 반환하라."
        )
        r = _run_once(user_turn)
        if r.returncode != 0:
            # 일시 오류(네트워크 등) 대비 1회 재시도. 한도 도달이면 재시도해도 같지만 비용 낮음.
            r = _run_once(user_turn)
        if r.returncode != 0:
            # 실패 사유는 stderr 가 아니라 stdout envelope 에 있는 경우가 대부분
            # (예: 사용 한도 도달). 둘 다 수집해 정확한 사유를 위로 올린다.
            stderr = (r.stderr or "").strip()[-400:]
            stdout_tail = (r.stdout or "").strip()[-400:]
            reason = stderr or stdout_tail or "(출력 없음)"
            try:
                env_json = json.loads((r.stdout or "").strip())
                reason = str(env_json.get("result") or env_json.get("terminal_reason") or reason)[:400]
            except Exception:  # noqa: BLE001
                pass
            raise RuntimeError(f"claude CLI 종료 코드 {r.returncode}: {reason}")

        obj, err = _cli_parse_envelope(r.stdout)
        if obj is None:
            logger.warning("claude_cli round %d 파싱 실패: %s", _round, err)
            final_text = f"(CLI 응답 파싱 실패 — {err})"
            break

        reply = str(obj.get("reply") or "").strip()
        name = str(obj.get("tool") or "").strip()
        # 도구 이름 없고 reply 만 있으면 최종 답변. 둘 다 채운 경우도 reply 우선 처리
        # (스키마 강제가 top-level oneOf 를 못 쓰므로 방어).
        if reply and not name:
            final_text = reply
            history.log_message("assistant", final_text, provider="claude_cli")
            break

        if not name:
            logger.warning("claude_cli round %d 응답 필드 누락 obj=%s",
                           _round, json.dumps(obj, ensure_ascii=False)[:500])
            final_text = reply or "(응답 필드 누락 — 재시도 필요)"
            break

        args = obj.get("args") or {}
        if not isinstance(args, dict):
            args = {}

        result = _dispatch_logged(name, args, session_token, tool_log)
        transcript.append(f'[도구 호출] {name}({json.dumps(args, ensure_ascii=False)[:500]})')
        transcript.append(f"[도구 결과] {json.dumps(result, ensure_ascii=False)[:6000]}")
    else:
        final_text = (final_text or "") + "\n\n(최대 호출 라운드 도달 — 더 작은 단위로 다시 요청해주세요)"
    return {"ok": True, "reply": final_text or "(빈 응답)", "tool_calls": tool_log}


# ── Ollama (로컬, 무제한 — 최후 폴백) ────────────────────
OLLAMA_URL = "http://localhost:11434"


def _ollama_available() -> bool:
    try:
        return requests.get(f"{OLLAMA_URL}/api/tags", timeout=2).status_code == 200
    except Exception:  # noqa: BLE001
        return False


def _ollama_tools() -> list[dict]:
    return [
        {"type": "function", "function": {
            "name": s.name,
            "description": s.description,
            "parameters": s.input_schema,
        }}
        for s in tools.REGISTRY.values()
    ]


def _ollama_payload(model: str, messages: list[dict], *, with_tools: bool = True) -> dict:
    payload: dict = {
        "model": model, "messages": messages,
        "stream": False,
        "options": {"num_ctx": 16384},
    }
    if with_tools:
        payload["tools"] = _ollama_tools()
    # think 파라미터는 thinking 모델(qwen3/deepseek-r1)만 지원 — qwen2.5/gemma 에 보내면 400.
    if model.startswith(("qwen3", "deepseek-r1")):
        payload["think"] = False  # 미설정 시 빈 응답 함정
    return payload


def _loop_ollama(user_text: str, system: str, *, session_token: Optional[str],
                 tool_log: list[dict]) -> dict:
    # 기본 qwen2.5:14b — tool calling 지원 + 비 thinking (영어 사고과정 dump 없음) + 한국어 준수.
    # 구 기본값 qwen3:4b 는 think:false 여도 영어 reasoning 을 답변 본문에 그대로 뱉는 사고 다발.
    model = str(config_store.get("chat.ollama_model", "qwen2.5:14b"))
    messages: list[dict] = [
        {"role": "system", "content": system + "\n\n반드시 한국어로만 답한다. 영어 문장 금지. "
         "사고 과정/분석 과정을 절대 출력하지 말고 최종 답변만 출력한다."},
        {"role": "user", "content": user_text},
    ]
    final_text = ""
    for _round in range(MAX_ROUNDS):
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=_ollama_payload(model, messages),
            timeout=300,  # 콜드 스타트 (OLLAMA_KEEP_ALIVE=0) 고려
        )
        r.raise_for_status()
        msg = (r.json() or {}).get("message") or {}
        if msg.get("content"):
            final_text = str(msg["content"]).strip()
        tcs = msg.get("tool_calls") or []
        if not tcs:
            history.log_message("assistant", final_text, provider="ollama")
            break
        messages.append(msg)
        for tc in tcs:
            fn = tc.get("function") or {}
            name = fn.get("name", "")
            args = fn.get("arguments") or {}
            if not isinstance(args, dict):
                try:
                    args = json.loads(args)
                except Exception:  # noqa: BLE001
                    args = {}
            result = _dispatch_logged(name, args, session_token, tool_log)
            messages.append({
                "role": "tool",
                "tool_name": name,
                "content": json.dumps(result, ensure_ascii=False)[:8000],
            })
    else:
        final_text = (final_text or "") + "\n\n(최대 호출 라운드 도달 — 더 작은 단위로 다시 요청해주세요)"

    # 한국어 가드 — 소형 로컬 모델이 영어 reasoning 을 본문에 뱉은 경우 1회 재정리.
    import re as _re
    if final_text and not _re.search(r"[가-힣]", final_text):
        try:
            fix_messages = messages + [
                {"role": "assistant", "content": final_text},
                {"role": "user", "content": "위 내용을 사용자용 최종 답변으로 한국어 2-4문장으로만 다시 써라. "
                 "분석 과정·영어 문장 금지."},
            ]
            r2 = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json=_ollama_payload(model, fix_messages, with_tools=False),
                timeout=300,
            )
            r2.raise_for_status()
            fixed = str(((r2.json() or {}).get("message") or {}).get("content") or "").strip()
            if fixed and _re.search(r"[가-힣]", fixed):
                final_text = fixed
        except Exception as e:  # noqa: BLE001
            logger.warning("ollama 한국어 재정리 실패 — 원문 유지: %s", e)

    return {"ok": True, "reply": final_text or "(빈 응답)", "tool_calls": tool_log}


# ── 공통 ─────────────────────────────────────────────────
def _dispatch_logged(name: str, args: dict, session_token: Optional[str],
                     tool_log: list[dict]) -> dict:
    result = tools.dispatch(name, args, session_token=session_token)
    tool_log.append({
        "name": name,
        "args": args,
        "ok": bool(result.get("ok")),
        "summary": _short_summary(result),
    })
    spec = tools.REGISTRY.get(name)
    if spec and spec.mutating:
        history.log_audit(name, args, result)
    return result


def _short_summary(result: dict) -> str:
    if not result.get("ok"):
        return f"❌ {str(result.get('error', ''))[:120]}"
    parts = []
    for k, v in result.items():
        if k == "ok":
            continue
        s = str(v)
        if len(s) > 80:
            s = s[:77] + "…"
        parts.append(f"{k}={s}")
        if sum(len(p) for p in parts) > 200:
            break
    return ", ".join(parts)


def chat_turn(user_text: str, *, session_token: Optional[str]) -> dict:
    """1 사용자 메시지 → tool loop → 최종 응답 dict."""
    if not user_text or not user_text.strip():
        return {"ok": False, "error": "빈 메시지"}
    max_chars = int(config_store.get("chat.max_input_chars", 12000))
    if len(user_text) > max_chars:
        return {"ok": False, "error": f"입력이 너무 깁니다 ({len(user_text)} > {max_chars}자)"}

    system = _system_prompt()
    history.log_message("user", user_text)
    tool_log: list[dict] = []
    loops = {"anthropic": _loop_anthropic, "claude_cli": _loop_claude_cli,
             "gemini": _loop_gemini, "ollama": _loop_ollama}

    last_err = "LLM 프로바이더 없음"
    claude_failed = False
    for prov in _provider_chain():
        if prov == "ollama" and not _ollama_available():
            last_err = "Ollama 미기동 (localhost:11434)"
            continue
        try:
            result = loops[prov](user_text, system, session_token=session_token, tool_log=tool_log)
            result["provider"] = prov
            # 폴백 투명화 — Claude 실패 후 로컬 모델이 답한 경우 품질 저하 사유를 명시.
            if prov == "ollama" and claude_failed and result.get("reply"):
                limit_hit = "limit" in last_err.lower() or "한도" in last_err
                why = "Claude 사용 한도 도달" if limit_hit else "Claude CLI 일시 오류"
                result["reply"] = (
                    f"⚠️ {why} — 로컬 보조 모델이 대신 답했어요 (품질 낮을 수 있음).\n\n"
                    + result["reply"]
                )
            return result
        except Exception as e:  # noqa: BLE001
            body = ""
            if isinstance(e, requests.HTTPError):
                try:
                    body = e.response.text[:300]
                except Exception:  # noqa: BLE001
                    pass
            last_err = f"{prov}: {e} {body}".strip()
            if prov == "claude_cli":
                claude_failed = True
            logger.warning("chat provider %s 실패: %s", prov, last_err)
            # 이미 도구가 실행됐다면 다른 프로바이더로 재시도하지 않는다 (중복 실행 방지).
            if tool_log:
                break

    history.log_message("assistant", f"호출 실패: {last_err}", ok=False)
    hints = []
    if "limit" in last_err.lower() and ("claude" in last_err.lower()):
        hints.append("Claude 사용 한도 도달 — 한도 리셋 후 자동 회복됩니다 (메뉴바 배터리 위젯에서 리셋 시각 확인).")
    elif "claude_cli" in last_err or "claude CLI" in last_err:
        hints.append(
            "Claude CLI 실패 — 터미널에서 `claude --version` / `claude -p 'ok'` 로 "
            "본계정 로그인 상태를 확인하세요."
        )
    if "Ollama" in last_err or "ollama" in last_err:
        hints.append("Ollama 데몬(:11434) 미기동 — `ollama list` 로 확인.")
    if "gemini" in last_err.lower() and "quota" in last_err.lower():
        hints.append(
            "Gemini quota 초과 — chat.provider 설정이 gemini 로 강제돼 있을 수 있어요. "
            "auto 로 되돌리면 claude_cli 로 폴백됩니다."
        )
    return {
        "ok": False,
        "error": f"채팅 응답 실패 — {last_err}",
        "hint": " / ".join(hints) if hints else "잠시 후 다시 시도하거나 채팅창에서 상태를 확인해 주세요.",
    }
