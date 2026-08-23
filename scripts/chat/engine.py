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
import time
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
        "게시글 링크는 /skill/<슬러그>, 전체 목록은 /catalog.\n"
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


def model_label(prov: Optional[str] = None) -> str:
    """상태 표시용 모델 이름 (Opus 5 · Sonnet 5 …)."""
    prov = prov or provider()
    raw = {
        "claude_cli": str(config_store.get("chat.claude_model", "claude-opus-5")),
        "anthropic": str(config_store.get("chat.model", "claude-opus-4-8")),
        "gemini": str(config_store.get("chat.gemini_model", "gemini-2.5-flash")),
        "ollama": str(config_store.get("chat.ollama_model", "qwen3:4b")),
    }.get(prov, "")
    if not raw:
        return ""
    pretty = raw.replace("claude-", "").replace("-", " ").title()
    return pretty.replace("Opus 5", "Opus 5").replace("Sonnet 5", "Sonnet 5")


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


# ── CLI 세션 (대화 이어가기) ──────────────────────────────────
# `claude --resume <sid>` 는 CLI 가 대화 전체를 들고 있게 해준다. 효과 2가지:
#   ① 멀티턴 — 이전 사용자 메시지/도구 결과를 우리가 다시 안 보내도 모델이 기억한다
#      (전에는 매 요청이 무맥락 단발이라 "그거 다시 해줘" 같은 말이 안 통했다).
#   ② 비용/속도 — 실측 cache_read 30,792 / cache_creation 201 (fresh 는 매번 ~20,700 생성).
CLI_SESSIONS: dict[str, dict] = {}
CLI_SESSION_TTL = 6 * 3600
CLI_SESSION_MAX = 50
_CLI_SESSION_LOCK = __import__("threading").Lock()
_CONV_ID_RE = __import__("re").compile(r"^[A-Za-z0-9_-]{1,64}$")


def _conv_sid(conv_id: Optional[str]) -> Optional[str]:
    if not conv_id or not _CONV_ID_RE.match(conv_id):
        return None
    now = time.time()
    with _CLI_SESSION_LOCK:
        rec = CLI_SESSIONS.get(conv_id)
        if not rec:
            return None
        if now - rec["ts"] > CLI_SESSION_TTL:
            CLI_SESSIONS.pop(conv_id, None)
            return None
        return rec["sid"]


def _conv_remember(conv_id: Optional[str], sid: Optional[str]) -> None:
    if not conv_id or not sid or not _CONV_ID_RE.match(conv_id):
        return
    now = time.time()
    with _CLI_SESSION_LOCK:
        CLI_SESSIONS[conv_id] = {"sid": sid, "ts": now}
        if len(CLI_SESSIONS) > CLI_SESSION_MAX:
            for k in sorted(CLI_SESSIONS, key=lambda k: CLI_SESSIONS[k]["ts"])[:-CLI_SESSION_MAX]:
                CLI_SESSIONS.pop(k, None)


def forget_conversation(conv_id: Optional[str]) -> bool:
    """'새 대화' — 다음 턴부터 CLI 세션을 새로 판다."""
    if not conv_id:
        return False
    with _CLI_SESSION_LOCK:
        return CLI_SESSIONS.pop(conv_id, None) is not None


# ── 스트리밍 파서 ────────────────────────────────────────────
_JSON_ESC = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f"}


def partial_reply(buf: str) -> str:
    """미완성 JSON 조각에서 "reply" 값만큼만 뽑아낸다 (토큰 스트리밍용).

    CLI 는 structured output 을 input_json_delta 로 흘린다 —
    `{"args": {}, "reply": "안녕하` … 처럼 문자열 중간에서 끊긴다.
    """
    i = buf.find('"reply"')
    if i < 0:
        return ""
    j = buf.find(":", i + 7)
    if j < 0:
        return ""
    k = buf.find('"', j + 1)
    if k < 0:
        return ""
    out: list[str] = []
    p, n = k + 1, len(buf)
    while p < n:
        ch = buf[p]
        if ch == "\\":
            if p + 1 >= n:
                break
            nx = buf[p + 1]
            if nx == "u":
                if p + 6 > n:
                    break
                try:
                    out.append(chr(int(buf[p + 2:p + 6], 16)))
                except ValueError:
                    pass
                p += 6
                continue
            out.append(_JSON_ESC.get(nx, nx))
            p += 2
            continue
        if ch == '"':
            break
        out.append(ch)
        p += 1
    return "".join(out)


def cli_normalize(obj: dict) -> tuple[str, str, dict]:
    """structured output → (reply, tool, args). 모델의 스키마 이탈을 흡수한다.

    실측된 이탈 3종:
      ① {"args": {"reply": "..."}}        — reply 를 args 안에 넣음 (답변이 통째로 유실됐다)
      ② {"reply": "...", "tool": "StructuredOutput"} — tool 칸에 출력도구 이름을 적음
      ③ {"tool": "recent_jobs", "limit": 3}          — 인자를 args 없이 top-level 로
    """
    if not isinstance(obj, dict):
        return "", "", {}
    reply = str(obj.get("reply") or "").strip()
    tool = str(obj.get("tool") or "").strip()
    args = dict(obj["args"]) if isinstance(obj.get("args"), dict) else {}
    if not reply and isinstance(args.get("reply"), str):
        reply = args.pop("reply").strip()
    if not tool and isinstance(args.get("tool"), str):
        tool = args.pop("tool").strip()
    if tool and not args:
        args = {k: v for k, v in obj.items() if k not in ("reply", "tool", "args")}
    if tool and tool not in tools.REGISTRY:
        if tool != "StructuredOutput":
            logger.info("claude_cli 미등록 도구 무시: %s", tool)
        tool = ""
    return reply, tool, args


def _cli_base_cmd(claude_bin: str, model: str, system_full: str, schema_str: str) -> list[str]:
    return [
        claude_bin,
        "--model", model,
        # 한도 도달/모델 거부 시 CLI 가 알아서 낮은 티어로 — 채팅이 죽지 않는다.
        "--fallback-model", str(config_store.get("chat.claude_fallback_model", "claude-sonnet-5")),
        "--setting-sources", "",   # 글로벌 설정/스킬 로드 차단 — 속도 + 한도 절약 (필수)
        "--strict-mcp-config",     # 사용자 MCP 서버(노션/Gmail 등) 로드 차단 — 무관한 도구 오염 방지
        "--disable-slash-commands",
        "--append-system-prompt", system_full,
        "--output-format", "stream-json",
        "--include-partial-messages",
        "--verbose",
        "--json-schema", schema_str,
    ]


def _cli_run_round(cmd: list[str], user_turn: str, *, env: dict, resume_sid: Optional[str],
                   on_delta=None) -> dict:
    """CLI 1라운드 실행 (stream-json). {structured, err, sid, streamed}."""
    import subprocess
    import threading

    full = list(cmd)
    if resume_sid:
        full = [full[0], "--resume", resume_sid] + full[1:]
    full += ["-p", user_turn]

    proc = subprocess.Popen(
        full, cwd=str(CLI_SANDBOX), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace", env=env, bufsize=1,
    )
    killer = threading.Timer(CLI_ROUND_TIMEOUT, proc.kill)
    killer.start()

    sid: Optional[str] = None
    structured: Optional[dict] = None
    err = ""
    buf = ""          # input_json_delta 누적
    sent = ""         # 이미 사용자에게 흘려보낸 reply 접두사
    plain: list[str] = []   # 스키마 밖 순수 text delta (드묾)
    try:
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            t = ev.get("type")
            if t == "system" and ev.get("subtype") == "init":
                sid = ev.get("session_id") or sid
            elif t == "stream_event":
                inner = ev.get("event") or {}
                if inner.get("type") == "content_block_delta":
                    d = inner.get("delta") or {}
                    if d.get("type") == "input_json_delta":
                        buf += d.get("partial_json") or ""
                        if on_delta:
                            grown = partial_reply(buf)
                            if grown.startswith(sent) and len(grown) > len(sent):
                                on_delta(grown[len(sent):])
                                sent = grown
                    elif d.get("type") == "text_delta":
                        chunk = d.get("text") or ""
                        plain.append(chunk)
                        if on_delta and chunk:
                            on_delta(chunk)
                            sent += chunk
            elif t == "result":
                sid = ev.get("session_id") or sid
                if ev.get("is_error"):
                    err = str(ev.get("result") or ev.get("terminal_reason") or "unknown")[:300]
                so = ev.get("structured_output")
                if isinstance(so, dict):
                    structured = so
                elif isinstance(ev.get("result"), str):
                    try:
                        parsed = json.loads(ev["result"])
                        if isinstance(parsed, dict):
                            structured = parsed
                    except Exception:  # noqa: BLE001
                        pass
        proc.wait(timeout=10)
    finally:
        killer.cancel()
        if proc.poll() is None:
            proc.kill()

    if structured is None and not err:
        tail = (proc.stderr.read() or "").strip()[-300:] if proc.stderr else ""
        if proc.returncode and proc.returncode != 0:
            err = f"claude CLI 종료 코드 {proc.returncode}: {tail or '(출력 없음)'}"
        elif plain:
            structured = {"reply": "".join(plain)}
        else:
            err = f"structured_output 없음 {tail}".strip()
    return {"structured": structured, "err": err, "sid": sid, "streamed": sent,
            "plain": "".join(plain).strip()}


def _loop_claude_cli(user_text: str, system: str, *, session_token: Optional[str],
                     tool_log: list[dict], conv_id: Optional[str] = None,
                     on_event=None) -> dict:
    import shutil as _sh
    claude_bin = _sh.which("claude") or "/opt/homebrew/bin/claude"
    model = str(config_store.get("chat.claude_model", "claude-opus-5"))
    CLI_SANDBOX.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    if "/opt/homebrew/bin" not in env.get("PATH", ""):
        env["PATH"] = "/opt/homebrew/bin:" + env.get("PATH", "")

    def emit(ev: dict) -> None:
        if on_event:
            try:
                on_event(ev)
            except Exception:  # noqa: BLE001
                pass

    tool_directive = (
        "너는 aiskillbox 운영 채팅 API 다. 자연어 설명·확인 예고·과정 서술 모두 금지. "
        "매 턴 정확히 다음 두 형태 중 하나로만 응답한다 (동시에 채우지 마라):\n"
        '  A) 도구 호출이 필요할 때 → {"tool": "<이름>", "args": {...}}  (reply 는 비운다)\n'
        '  B) 사용자에게 직접 답할 때 → {"reply": "<한국어 답변>"}  (tool·args 는 비운다)\n'
        '"tool" 에는 아래 목록의 이름만 넣는다 — 답변만 할 때는 tool/args 를 아예 넣지 마라.\n'
        "\n사용 가능한 도구 (이 목록 밖 도구/명령 사용 금지):\n"
        f"{_cli_tool_catalog()}\n"
        "\n원칙:\n"
        "- 상태/실패/설정 질문은 답 예고하지 말고 즉시 조회 도구 호출 (recent_jobs / tail_log / "
        "  fix_status / get_settings 등).\n"
        "- 코드 수정이 필요하면 escalate_fix 호출. 그 전에 recent_jobs 로 실패 잡 확인 필수.\n"
        "- mutating 도구 호출 실패 사유가 'PIN' / '세션' 이면 그 즉시 reply 로 'PIN 1회 입력 필요' 만 짧게 안내.\n"
        "- 이전 턴 대화를 기억하고 있다 — 사용자가 '아까 그거' 라고 하면 되묻지 말고 맥락에서 이어가라.\n"
        "- reply 는 한국어로 3-4문장 이하. 긴 dump 금지."
    )
    system_full = system + "\n\n" + tool_directive
    schema_str = json.dumps(_CLI_SCHEMA, ensure_ascii=False)
    cmd = _cli_base_cmd(claude_bin, model, system_full, schema_str)

    sid = _conv_sid(conv_id)
    turn = user_text if sid else (
        "아래는 사용자의 요청이다. 스키마 준수 JSON 오브젝트 하나만 반환하라.\n\n"
        f"[사용자] {user_text}"
    )
    final_text = ""

    for _round in range(MAX_ROUNDS):
        emit({"type": "status", "text": "생각 중…" if _round == 0 else "이어서 정리 중…"})
        res = _cli_run_round(cmd, turn, env=env, resume_sid=sid, on_delta=(
            (lambda t: emit({"type": "delta", "text": t})) if on_event else None))
        if res["err"] and res["structured"] is None and sid and "session" in res["err"].lower():
            # 세션 파일이 사라졌거나 손상 — 맥락 없이 1회 재시도
            logger.warning("claude_cli resume 실패 — 새 세션으로 재시도: %s", res["err"])
            _conv_remember(conv_id, None)
            with _CLI_SESSION_LOCK:
                CLI_SESSIONS.pop(conv_id or "", None)
            sid = None
            if res["streamed"]:
                emit({"type": "reset"})
            res = _cli_run_round(cmd, turn, env=env, resume_sid=None, on_delta=(
                (lambda t: emit({"type": "delta", "text": t})) if on_event else None))

        sid = res["sid"] or sid
        _conv_remember(conv_id, sid)

        if res["structured"] is None:
            raise RuntimeError(res["err"] or "claude CLI 응답 없음")

        reply, name, args = cli_normalize(res["structured"])
        # 스키마 대신 일반 텍스트 블록으로 답한 라운드도 살린다.
        if not reply and not name and res.get("plain"):
            reply = res["plain"]
        # reply 우선 — 모델이 둘 다 채워도 답이 있으면 그게 최종.
        if reply and not name:
            final_text = reply
            history.log_message("assistant", final_text, provider="claude_cli")
            break
        if not name:
            logger.warning("claude_cli round %d 응답 필드 누락 obj=%s",
                           _round, json.dumps(res["structured"], ensure_ascii=False)[:500])
            final_text = reply or "(응답 필드 누락 — 다시 말씀해 주세요)"
            break

        if res["streamed"]:
            emit({"type": "reset"})   # 도구 라운드였다 — 흘린 조각 취소
        emit({"type": "tool", "phase": "start", "name": name})
        result = _dispatch_logged(name, args, session_token, tool_log)
        emit({"type": "tool", "phase": "end", "name": name,
              "ok": bool(result.get("ok")), "summary": _short_summary(result)})
        turn = (
            f"[도구 결과] {name} → "
            f"{json.dumps(result, ensure_ascii=False)[:6000]}\n\n"
            "이 결과를 바탕으로 다음 스키마 준수 JSON 하나만 반환하라 "
            "(추가 도구가 필요하면 tool, 끝났으면 reply)."
        )
    else:
        final_text = (final_text or "") + "\n\n(최대 호출 라운드 도달 — 더 작은 단위로 다시 요청해주세요)"
    return {"ok": True, "reply": final_text or "(빈 응답)", "tool_calls": tool_log,
            "conv_id": conv_id}


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


def chat_turn(user_text: str, *, session_token: Optional[str],
              conv_id: Optional[str] = None, on_event=None) -> dict:
    """1 사용자 메시지 → tool loop → 최종 응답 dict.

    conv_id  : 대화 스레드 id — claude_cli 가 `--resume` 으로 맥락을 이어간다.
    on_event : 스트리밍 콜백 (status/delta/tool/reset). None 이면 기존 동작 그대로.
    """
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
            kw = {"session_token": session_token, "tool_log": tool_log}
            if prov == "claude_cli":
                kw.update({"conv_id": conv_id, "on_event": on_event})
            result = loops[prov](user_text, system, **kw)
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


# ── 실시간 스트리밍 ──────────────────────────────────────────
def chat_stream(user_text: str, *, session_token: Optional[str] = None,
                conv_id: Optional[str] = None):
    """chat_turn 을 백그라운드로 돌리며 진행 이벤트를 순서대로 흘린다 (SSE 용).

    이벤트: status(단계) · delta(응답 토큰) · reset(흘린 조각 취소) ·
            tool(도구 시작/끝) · done(최종) · error · ping(연결 유지).
    """
    import queue
    import threading

    q: "queue.Queue" = queue.Queue()

    def on_event(ev: dict) -> None:
        q.put(ev)

    def run() -> None:
        try:
            res = chat_turn(user_text, session_token=session_token,
                            conv_id=conv_id, on_event=on_event)
            if res.get("ok"):
                q.put({"type": "done", "reply": res.get("reply", ""),
                       "tool_calls": res.get("tool_calls") or [],
                       "provider": res.get("provider", "")})
            else:
                q.put({"type": "error", "message": res.get("error", "응답 실패"),
                       "hint": res.get("hint", "")})
        except Exception as e:  # noqa: BLE001
            logger.exception("chat_stream 실패")
            q.put({"type": "error", "message": str(e)})
        finally:
            q.put(None)

    threading.Thread(target=run, daemon=True).start()
    while True:
        try:
            ev = q.get(timeout=10)
        except Exception:  # noqa: BLE001  (queue.Empty)
            yield {"type": "ping"}     # CF 터널/프록시 버퍼링 방지용 하트비트
            continue
        if ev is None:
            break
        yield ev

