"""config.json 안전 read/write — 채팅 / dedup / IG 가드가 공유하는 단일 진실.

- 비밀 키 (API token 등) 는 절대 여기에 두지 않는다. 그건 .env 전용.
- 변경은 PIN 게이트 통과한 채팅 도구만. CLI 도 직접 쓰지 말 것.
- 모든 read 가 매번 디스크에서 읽지 않게 mtime 캐시.
"""
from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.json"
_LOCK = threading.Lock()
_CACHE: dict[str, Any] = {}
_CACHE_MTIME: float = 0.0


def _load() -> dict[str, Any]:
    """디스크에서 config 로드. mtime 변경 시만 다시 읽음."""
    global _CACHE, _CACHE_MTIME
    if not CONFIG_PATH.exists():
        logger.warning("config.json 없음 — 빈 dict 사용")
        return {}
    try:
        mtime = CONFIG_PATH.stat().st_mtime
        if mtime != _CACHE_MTIME or not _CACHE:
            _CACHE = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            _CACHE_MTIME = mtime
        return _CACHE
    except Exception as e:  # noqa: BLE001
        logger.error("config.json 파싱 실패: %s", e)
        return {}


def get(key_path: str, default: Any = None) -> Any:
    """점 표기로 nested 키 조회. 예: get("dedup.threshold", 0.80)."""
    with _LOCK:
        node: Any = _load()
        for part in key_path.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default
        return node


def all_config() -> dict[str, Any]:
    """전체 config 사본 반환 (mutating 도 안전)."""
    with _LOCK:
        return json.loads(json.dumps(_load()))


def patch(updates: dict[str, Any], *, allowed_prefixes: tuple[str, ...] = ()) -> dict[str, Any]:
    """점 표기 키들을 일괄 갱신. allowed_prefixes 안 경로만 허용.

    Returns: { "applied": {...}, "rejected": {...} }
    """
    global _CACHE, _CACHE_MTIME
    applied: dict[str, Any] = {}
    rejected: dict[str, str] = {}
    with _LOCK:
        data = _load()
        # _load 가 반환한 게 모듈 캐시 자체 — 깊은 복사 후 적용해 atomic 쓰기.
        new_data = json.loads(json.dumps(data))
        for key_path, value in updates.items():
            if allowed_prefixes and not any(
                key_path == p or key_path.startswith(p + ".") for p in allowed_prefixes
            ):
                rejected[key_path] = "허용되지 않은 키 경로"
                continue
            parts = key_path.split(".")
            node = new_data
            for part in parts[:-1]:
                if not isinstance(node.get(part), dict):
                    node[part] = {}
                node = node[part]
            node[parts[-1]] = value
            applied[key_path] = value

        if applied:
            CONFIG_PATH.write_text(
                json.dumps(new_data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            _CACHE = new_data
            _CACHE_MTIME = CONFIG_PATH.stat().st_mtime

    return {"applied": applied, "rejected": rejected}
