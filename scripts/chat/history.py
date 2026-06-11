"""채팅 메시지 + mutating 액션 영속화 (jsonl).

- chat_history.jsonl: 모든 메시지 (user/assistant/tool_use/tool_result)
- chat_audit.jsonl: mutating 도구 실행 결과만 (감사용)
"""
from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HISTORY_PATH = PROJECT_ROOT / "inbox" / "chat_history.jsonl"
AUDIT_PATH = PROJECT_ROOT / "inbox" / "chat_audit.jsonl"
_LOCK = threading.Lock()


def _append(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False)
    with _LOCK:
        with path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def log_message(role: str, content: str | list | dict, **extra) -> None:
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "role": role,
        "content": content,
    }
    rec.update(extra)
    try:
        _append(HISTORY_PATH, rec)
    except Exception as e:  # noqa: BLE001
        logger.warning("history 기록 실패: %s", e)


def log_audit(tool: str, args: dict, result: dict) -> None:
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "tool": tool,
        "args": args,
        "ok": bool(result.get("ok")),
        "summary": _summary(result),
    }
    try:
        _append(AUDIT_PATH, rec)
    except Exception as e:  # noqa: BLE001
        logger.warning("audit 기록 실패: %s", e)


def _summary(result: dict) -> str:
    if not result.get("ok"):
        return str(result.get("error", ""))[:200]
    keys = sorted(result.keys())
    return ", ".join(f"{k}={str(result[k])[:60]}" for k in keys if k != "ok")[:200]


def tail_history(limit: int = 50) -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    lines = HISTORY_PATH.read_text(encoding="utf-8").splitlines()
    out: list[dict] = []
    for ln in lines[-max(1, int(limit)):]:
        try:
            out.append(json.loads(ln))
        except Exception:  # noqa: BLE001
            continue
    return out


def tail_audit(limit: int = 50) -> list[dict]:
    if not AUDIT_PATH.exists():
        return []
    lines = AUDIT_PATH.read_text(encoding="utf-8").splitlines()
    out: list[dict] = []
    for ln in lines[-max(1, int(limit)):]:
        try:
            out.append(json.loads(ln))
        except Exception:  # noqa: BLE001
            continue
    return out
