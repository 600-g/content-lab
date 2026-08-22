"""초대코드 / 기기 토큰 저장소 — aiskillbox 전체 잠금(v4.6)의 단일 진실.

- 파일: logs/auth.json (0600). 코드는 평문(설정창 재조회·복사용 — company-hq invite_codes.json 과
  동일 판단), 기기 토큰은 sha256 해시만 (유출 시 auth.json 만으로는 로그인 불가).
- 계정/역할 없음: 코드 1개 → 기기 N대 (redeem 마다 토큰 발급), 코드 삭제 = 해당 기기 전부 로그아웃 (cascade).
- CLI: python -m scripts.auth_store create [라벨] | list | delete <code>

설계: docs/superpowers/specs/2026-08-22-invite-auth-design.md
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import secrets
import sys
import threading
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = PROJECT_ROOT / "logs" / "auth.json"

# 혼동 문자 (I/O/0/1) 제외 — 폰으로 옮겨 적을 때 실수 방지
_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_CODE_PREFIX = "DGN"
_LAST_SEEN_THROTTLE_SEC = 60.0


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _new_code() -> str:
    part = lambda: "".join(secrets.choice(_CODE_ALPHABET) for _ in range(4))  # noqa: E731
    return f"{_CODE_PREFIX}-{part()}-{part()}"


class AuthStore:
    """auth.json 1파일 저장소. 모든 공개 메서드는 스레드 안전."""

    def __init__(self, path: Path | str = DEFAULT_PATH) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()
        self._data: dict = {"codes": {}, "sessions": {}}
        self._loaded = False
        self._last_seen_flush: dict[str, float] = {}  # token_hash -> 마지막 디스크 갱신 시각

    # ── 내부 IO ──────────────────────────────────────────────

    def _load(self) -> None:
        if self._loaded:
            return
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    self._data = {
                        "codes": dict(raw.get("codes") or {}),
                        "sessions": dict(raw.get("sessions") or {}),
                    }
            except Exception as e:  # noqa: BLE001
                logger.warning("auth.json 파싱 실패 — 빈 저장소로 시작 (bootstrap 으로 재진입): %s", e)
                self._data = {"codes": {}, "sessions": {}}
        self._loaded = True

    def _save(self) -> None:
        """반드시 self._lock 안에서 호출. atomic write + 0600."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self._data, ensure_ascii=False, indent=1), encoding="utf-8")
        os.chmod(tmp, 0o600)
        tmp.replace(self.path)

    # ── 코드 관리 ────────────────────────────────────────────

    def create_code(self, label: str = "") -> str:
        with self._lock:
            self._load()
            while True:
                code = _new_code()
                if code not in self._data["codes"]:
                    break
            self._data["codes"][code] = {"label": str(label or "").strip(), "created_at": _now()}
            self._save()
            return code

    def list_codes(self) -> list[dict]:
        with self._lock:
            self._load()
            counts: dict[str, int] = {}
            for s in self._data["sessions"].values():
                counts[s.get("code", "")] = counts.get(s.get("code", ""), 0) + 1
            return [
                {
                    "code": code,
                    "label": meta.get("label", ""),
                    "created_at": meta.get("created_at", ""),
                    "sessions": counts.get(code, 0),
                }
                for code, meta in sorted(
                    self._data["codes"].items(), key=lambda kv: kv[1].get("created_at", "")
                )
            ]

    def delete_code(self, code: str) -> int:
        """코드 삭제 + 그 코드로 발급된 세션 전부 회수. 삭제된 세션 수 반환."""
        with self._lock:
            self._load()
            if code not in self._data["codes"]:
                return 0
            del self._data["codes"][code]
            doomed = [h for h, s in self._data["sessions"].items() if s.get("code") == code]
            for h in doomed:
                del self._data["sessions"][h]
            self._save()
            return len(doomed)

    # ── 세션 ─────────────────────────────────────────────────

    def redeem(self, code: str, *, device: str = "") -> Optional[str]:
        """코드 → 기기 토큰 발급. 코드 무효면 None."""
        code = (code or "").strip().upper()
        with self._lock:
            self._load()
            if not code or code not in self._data["codes"]:
                return None
            token = secrets.token_urlsafe(32)
            self._data["sessions"][_hash_token(token)] = {
                "code": code,
                "device": str(device or "")[:120],
                "created_at": _now(),
                "last_seen": _now(),
            }
            self._save()
            return token

    def check_token(self, token: Optional[str]) -> bool:
        if not token:
            return False
        h = _hash_token(str(token))
        now = time.time()
        with self._lock:
            self._load()
            s = self._data["sessions"].get(h)
            if s is None:
                return False
            # last_seen 은 스로틀 갱신 — 요청마다 디스크 쓰기 방지
            if now - self._last_seen_flush.get(h, 0.0) > _LAST_SEEN_THROTTLE_SEC:
                s["last_seen"] = _now()
                self._last_seen_flush[h] = now
                self._save()
            return True

    def session_count(self) -> int:
        with self._lock:
            self._load()
            return len(self._data["sessions"])


_DEFAULT: Optional[AuthStore] = None
_DEFAULT_LOCK = threading.Lock()


def get_store() -> AuthStore:
    """운영용 기본 저장소 (logs/auth.json)."""
    global _DEFAULT
    with _DEFAULT_LOCK:
        if _DEFAULT is None:
            _DEFAULT = AuthStore()
        return _DEFAULT


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    store = get_store()
    if args[:1] == ["create"]:
        code = store.create_code(args[1] if len(args) > 1 else "")
        print(code)
        return 0
    if args[:1] == ["list"]:
        for row in store.list_codes():
            print(f"{row['code']}  기기 {row['sessions']}대  {row['label']}  ({row['created_at']})")
        return 0
    if args[:1] == ["delete"] and len(args) > 1:
        removed = store.delete_code(args[1])
        print(f"삭제됨 — 로그아웃된 기기 {removed}대")
        return 0
    print("사용법: python -m scripts.auth_store create [라벨] | list | delete <code>")
    return 2


if __name__ == "__main__":
    sys.exit(main())
