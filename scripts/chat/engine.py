"""Anthropic Messages API (Opus 4.8) 직접 호출 + tool use loop.

- requests 만 사용 (anthropic SDK 의존 X — venv 새로 깔 필요 없음).
- 모델 호출 → tool_use 가 있으면 dispatch → tool_result 로 재호출. 최대 8 라운드.
- mutating 도구는 모델이 호출해도 safety 토큰이 없으면 거부되고, 그 사실이
  tool_result 로 모델에 전달돼 모델이 사용자에게 "PIN 입력 필요" 답함.
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Optional

import requests

from scripts import config_store
from scripts.chat import history, tools

logger = logging.getLogger(__name__)

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
MAX_ROUNDS = 8
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _system_prompt() -> str:
    return (
        "너는 두근컴퍼니 aiskillbox(콘텐츠랩) 의 운영 보조 에이전트다. "
        "한국어로 짧고 명확하게 답한다.\n\n"
        "역할: 사용자(두근컴퍼니 오너)의 자연어 요청을 듣고, "
        "허용된 도구만 사용해 운영 상태 조회·설정 편집·SKILL.md 수정·중복 합병을 수행한다.\n\n"
        "규칙:\n"
        "- 절대 손대지 않는다: app.py / scripts/scraper/* / scripts/analyzer/(gemini.py,merger.py,prompt.py) / "
        "scripts/skill_builder/* / scripts/notion_client/* — 이건 코드 본체라 사용자에게 "
        "'클로드 코드에서 직접 수정 필요' 라고 안내.\n"
        "- 도구가 mutating 인데 세션이 없으면 친절하게 'PIN(0910) 한 번만 입력해주세요' 안내. "
        "이미 PIN 입력해 토큰 받은 상태면 그냥 실행.\n"
        "- 결과 보고는 한 단락 또는 짧은 bullet. 긴 dump 는 금지.\n"
        "- 비밀(.env API 키 등) 은 절대 응답 본문에 그대로 노출하지 않는다.\n"
        "- 사용자가 모호하게 말하면 (예: '그거 합쳐줘') 후보 1-2개 제시하고 선택받기.\n"
        "- 채팅의 핵심 목적: 사용자가 나(클로드) 의 손을 거치지 않고도 직접 운영을 끝낼 수 있게 돕는다."
    )


def _ensure_key() -> Optional[str]:
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return None
    return key


def _call_anthropic(messages: list[dict], system: str) -> dict:
    """Anthropic Messages API 단일 호출."""
    key = _ensure_key()
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY 미설정 — .env 에 추가 후 재기동")
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
        # 일부 환경에서 모델 alias 가 4-7 만 통과할 수 있음 → 1회 폴백.
        if "model" in r.text.lower() and model != "claude-opus-4-7":
            logger.warning("model %s 거부 — claude-opus-4-7 로 폴백", model)
            payload["model"] = "claude-opus-4-7"
            r = requests.post(ANTHROPIC_URL, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    return r.json()


def _extract_text(blocks: list[dict]) -> str:
    parts = [b.get("text", "") for b in blocks if b.get("type") == "text"]
    return "\n\n".join(p for p in parts if p)


def chat_turn(user_text: str, *, session_token: Optional[str]) -> dict:
    """1 사용자 메시지 → tool loop → 최종 응답 dict.

    Returns:
        {
          "ok": True,
          "reply": "<assistant text>",
          "tool_calls": [{"name", "args", "result_summary", "ok"}],
          "session_token": <변경 가능성: 도구가 새로 토큰 발급한 경우>,
        }
    """
    if not user_text or not user_text.strip():
        return {"ok": False, "error": "빈 메시지"}
    max_chars = int(config_store.get("chat.max_input_chars", 12000))
    if len(user_text) > max_chars:
        return {"ok": False, "error": f"입력이 너무 깁니다 ({len(user_text)} > {max_chars}자)"}
    if not _ensure_key():
        return {
            "ok": False,
            "error": "ANTHROPIC_API_KEY 미설정",
            "hint": ".env 에 ANTHROPIC_API_KEY=sk-ant-... 추가 후 설정 모달에서 [재기동] 하세요.",
        }

    system = _system_prompt()
    messages: list[dict] = [
        {"role": "user", "content": user_text},
    ]
    history.log_message("user", user_text)

    tool_log: list[dict] = []
    final_text = ""

    for round_i in range(MAX_ROUNDS):
        try:
            resp = _call_anthropic(messages, system)
        except requests.HTTPError as e:
            body = ""
            try:
                body = e.response.text[:400]
            except Exception:  # noqa: BLE001
                pass
            history.log_message("assistant", f"API 오류: {e}\n{body}", ok=False)
            return {"ok": False, "error": f"Anthropic API 오류: {e}", "body": body}
        except Exception as e:  # noqa: BLE001
            history.log_message("assistant", f"호출 실패: {e}", ok=False)
            return {"ok": False, "error": str(e)}

        blocks = resp.get("content", [])
        stop_reason = resp.get("stop_reason")
        text = _extract_text(blocks)
        if text:
            final_text = text  # 마지막 텍스트가 최종.

        tool_uses = [b for b in blocks if b.get("type") == "tool_use"]
        if not tool_uses:
            # 모델이 응답 종료.
            history.log_message("assistant", text, stop_reason=stop_reason)
            break

        # 모델 응답을 messages 에 그대로 보존.
        messages.append({"role": "assistant", "content": blocks})

        tool_results: list[dict] = []
        for tu in tool_uses:
            name = tu.get("name", "")
            args = tu.get("input", {}) or {}
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

    return {
        "ok": True,
        "reply": final_text or "(빈 응답)",
        "tool_calls": tool_log,
    }


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
