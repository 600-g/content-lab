"""mcp_remote 설정 — config.json 의 mcp_remote 블록 (mtime 재적재).

재적재가 필요한 이유: dynamic_registration 토글을 서버 재시작 없이 켜고 끄기 위해서다
(최초 커넥터 연결에만 열고 바로 닫는 운영 절차).
"""
from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = PROJECT_ROOT / "config.json"

DEFAULTS = {
    "enabled": True,
    "public_base_url": "https://aiskillbox.600g.net",
    "dynamic_registration": False,
    "allowed_origins": ["https://claude.ai", "https://claude.com"],
    "access_ttl_seconds": 3600,
    "refresh_ttl_seconds": 7776000,
}

_CACHE: dict = {"mtime": None, "value": None, "path": None}
_LOCK = threading.Lock()


def load(path: Optional[Path | str] = None) -> dict:
    p = Path(path or DEFAULT_PATH)
    with _LOCK:
        try:
            m = p.stat().st_mtime
        except OSError:
            m = None
        if _CACHE["value"] is not None and _CACHE["mtime"] == m and _CACHE["path"] == str(p):
            return _CACHE["value"]
        block = {}
        if m is not None:
            try:
                raw = json.loads(p.read_text(encoding="utf-8"))
                block = raw.get("mcp_remote") or {}
            except Exception as e:  # noqa: BLE001
                logger.warning("config.json 파싱 실패 — mcp_remote 기본값 사용: %s", e)
        merged = {**DEFAULTS, **{k: v for k, v in block.items() if not k.startswith("_")}}
        merged["public_base_url"] = str(merged["public_base_url"]).rstrip("/")
        if not merged["public_base_url"].startswith("https://"):
            raise ValueError(
                "mcp_remote.public_base_url 은 https 여야 한다 — CF Tunnel 이 TLS 를 종단하므로 "
                f"http 가 새면 Claude 가 연결을 거부한다 (현재: {merged['public_base_url']!r})")
        _CACHE.update(mtime=m, value=merged, path=str(p))
        return merged


def base_url(c: Optional[dict] = None) -> str:
    return (c or load())["public_base_url"]


def abs_url(path: str, c: Optional[dict] = None) -> str:
    return base_url(c) + "/" + str(path).lstrip("/")


def resource_id(c: Optional[dict] = None) -> str:
    return abs_url("/mcp", c)


def enabled(c: Optional[dict] = None) -> bool:
    return bool((c or load())["enabled"])


def dynamic_registration(c: Optional[dict] = None) -> bool:
    return bool((c or load())["dynamic_registration"])


def allowed_origins(c: Optional[dict] = None) -> list[str]:
    return list((c or load())["allowed_origins"])


def access_ttl(c: Optional[dict] = None) -> int:
    return int((c or load())["access_ttl_seconds"])


def refresh_ttl(c: Optional[dict] = None) -> int:
    return int((c or load())["refresh_ttl_seconds"])
