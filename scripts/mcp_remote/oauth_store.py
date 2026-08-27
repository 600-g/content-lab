"""OAuth 2.1 인가서버 저장소 — logs/oauth.json (표준 라이브러리만, Flask 미의존).

auth_store.py 와 같은 규약: 0600 · atomic write · threading.Lock · mtime 재적재.
비밀(client_secret · 인가코드 · access · refresh)은 sha256 만 저장한다.

폐기: 모든 grant 에 승인한 invite_code 를 박아두고, 검증 때마다 그 코드가 auth.json 에
아직 있는지 본다 (지연 폐기). 초대코드 삭제 = 그 코드로 붙은 커넥터도 즉시 끊김.

설계: docs/superpowers/specs/2026-08-27-remote-mcp-oauth-design.md
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import secrets
import threading
import time
from pathlib import Path
from typing import Optional

from scripts import auth_store as auth_store_mod

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = PROJECT_ROOT / "logs" / "oauth.json"
CODE_TTL_SECONDS = 60
_EMPTY = {"clients": {}, "auth_codes": {}, "tokens": {}, "refresh": {}, "spent_codes": {}}


def _h(value: str) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


class OAuthStore:
    """oauth.json 1파일 저장소. 모든 공개 메서드는 스레드 안전."""

    def __init__(self, path: Path | str = DEFAULT_PATH, *, auth_store=None) -> None:
        self.path = Path(path)
        self._lock = threading.RLock()
        self._data = json.loads(json.dumps(_EMPTY))
        self._mtime: Optional[float] = None
        self._auth = auth_store  # None 이면 첫 사용 시 기본 저장소

    # ── 내부 ────────────────────────────────────────────────

    def _auth_store(self):
        if self._auth is None:
            self._auth = auth_store_mod.get_store()
        return self._auth

    def _disk_mtime(self) -> Optional[float]:
        try:
            return self.path.stat().st_mtime
        except OSError:
            return None

    def _load(self) -> None:
        m = self._disk_mtime()
        if m is not None and m == self._mtime:
            return
        if m is None:
            self._data = json.loads(json.dumps(_EMPTY))
            self._mtime = None
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("최상위가 dict 가 아님")
            for k, v in _EMPTY.items():
                raw.setdefault(k, json.loads(json.dumps(v)))
            self._data = raw
        except Exception as e:  # noqa: BLE001
            logger.warning("oauth.json 파싱 실패 — 빈 저장소로 시작: %s", e)
            self._data = json.loads(json.dumps(_EMPTY))
        self._mtime = m

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self._data, ensure_ascii=False, indent=1), encoding="utf-8")
        os.chmod(tmp, 0o600)
        os.replace(tmp, self.path)
        self._mtime = self._disk_mtime()

    def _sweep(self) -> None:
        """만료 항목 지연 정리 — 타이머 스레드 없음."""
        now = time.time()
        for bucket in ("auth_codes", "tokens", "refresh", "spent_codes"):
            dead = [k for k, v in self._data[bucket].items() if v.get("expires_at", 0) < now]
            for k in dead:
                del self._data[bucket][k]

    # ── 클라이언트 ───────────────────────────────────────────

    def create_client(self, name: str, redirect_uris: list[str], *,
                      source: str = "manual", public: bool = False) -> tuple[str, Optional[str]]:
        client_id = "cli_" + secrets.token_urlsafe(16)
        secret = None if public else secrets.token_urlsafe(32)
        with self._lock:
            self._load()
            self._data["clients"][client_id] = {
                "secret_hash": None if secret is None else _h(secret),
                "redirect_uris": [str(u) for u in redirect_uris],
                "name": str(name or "")[:120],
                "source": source,
                "created_at": _now(),
            }
            self._save()
        return client_id, secret

    def get_client(self, client_id: str) -> Optional[dict]:
        with self._lock:
            self._load()
            c = self._data["clients"].get(str(client_id))
            return json.loads(json.dumps(c)) if c else None

    def verify_client(self, client_id: str, secret: Optional[str]) -> bool:
        c = self.get_client(client_id)
        if c is None:
            return False
        if c["secret_hash"] is None:
            return True  # public 클라이언트 — PKCE 가 인증을 대신한다
        if not secret:
            return False
        return secrets.compare_digest(c["secret_hash"], _h(secret))

    def list_clients(self) -> list[dict]:
        with self._lock:
            self._load()
            return [
                {"client_id": cid, "name": c.get("name", ""), "source": c.get("source", ""),
                 "redirect_uris": c.get("redirect_uris", []), "created_at": c.get("created_at", "")}
                for cid, c in sorted(self._data["clients"].items(),
                                     key=lambda kv: kv[1].get("created_at", ""))
            ]

    def delete_client(self, client_id: str) -> bool:
        with self._lock:
            self._load()
            if str(client_id) not in self._data["clients"]:
                return False
            del self._data["clients"][str(client_id)]
            self._save()
        self.revoke_grants_of(client_id)
        return True

    # ── 인가코드 ─────────────────────────────────────────────

    def issue_code(self, *, client_id: str, redirect_uri: str, code_challenge: str,
                   resource: str, scope: str, invite_code: str,
                   ttl: int = CODE_TTL_SECONDS) -> str:
        code = secrets.token_urlsafe(32)
        with self._lock:
            self._load()
            self._sweep()
            self._data["auth_codes"][_h(code)] = {
                "client_id": client_id, "redirect_uri": redirect_uri,
                "code_challenge": code_challenge, "resource": resource,
                "scope": scope, "invite_code": invite_code,
                "expires_at": time.time() + ttl, "created_at": _now(),
            }
            self._save()
        return code

    def consume_code(self, code: str, *, client_id: Optional[str] = None) -> Optional[dict]:
        """1회용 — 존재하면 삭제하고 반환. 만료면 None (삭제는 함).

        client_id 를 주면 **소유자가 일치할 때만** 삭제한다. 불일치면 코드를 건드리지 않고
        None — 남의 코드를 파괴해 정당한 교환을 막는 무흔적 DoS 를 차단한다.
        """
        if not code:
            return None
        with self._lock:
            self._load()
            h = _h(code)
            g = self._data["auth_codes"].get(h)
            if g is None:
                return None
            if client_id is not None and g.get("client_id") != client_id:
                return None   # 소유자 불일치 — pop 하지 않는다
            del self._data["auth_codes"][h]
            self._save()
            if g.get("expires_at", 0) < time.time():
                return None
            return g

    def code_was_seen(self, code: str) -> bool:
        """이미 소비된 코드인지 — 재사용 감지용 (소비 이력 해시 보관)."""
        with self._lock:
            self._load()
            return _h(code) in self._data.get("spent_codes", {})

    def mark_code_spent(self, code: str, client_id: str) -> None:
        with self._lock:
            self._load()
            self._data.setdefault("spent_codes", {})[_h(code)] = {
                "client_id": client_id, "expires_at": time.time() + 600}
            self._save()

    # ── 토큰 ────────────────────────────────────────────────

    def issue_tokens(self, grant: dict, *, access_ttl: int, refresh_ttl: int) -> tuple[str, str, int]:
        access = secrets.token_urlsafe(32)
        refresh = secrets.token_urlsafe(32)
        base = {"client_id": grant["client_id"], "resource": grant["resource"],
                "scope": grant.get("scope", "skills:read"),
                "invite_code": grant["invite_code"], "created_at": _now()}
        with self._lock:
            self._load()
            self._sweep()
            self._data["tokens"][_h(access)] = {**base, "expires_at": time.time() + access_ttl}
            self._data["refresh"][_h(refresh)] = {**base, "expires_at": time.time() + refresh_ttl}
            self._save()
        return access, refresh, access_ttl

    def _valid(self, bucket: str, token: str, *, resource: Optional[str]) -> Optional[dict]:
        if not token:
            return None
        with self._lock:
            self._load()
            g = self._data[bucket].get(_h(token))
            if g is None or g.get("expires_at", 0) < time.time():
                return None
            if resource is not None and g.get("resource") != resource:
                return None
            if not self._auth_store().has_code(g.get("invite_code", "")):
                return None  # 지연 폐기 — 초대코드가 사라지면 grant 도 죽는다
            return json.loads(json.dumps(g))

    def validate_access(self, token: str, *, resource: str) -> Optional[dict]:
        return self._valid("tokens", token, resource=resource)

    def rotate_refresh(self, token: str, *, access_ttl: int, refresh_ttl: int,
                       client_id: Optional[str] = None) -> Optional[tuple[str, str, int]]:
        with self._lock:          # RLock — _valid/issue_tokens 재진입 안전
            g = self._valid("refresh", token, resource=None)
            if g is None:
                return None
            if client_id is not None and g.get("client_id") != client_id:
                return None   # RFC 6749 §6 — refresh 토큰은 발급받은 클라이언트에만
            self._load()
            self._data["refresh"].pop(_h(token), None)
            self._save()
            return self.issue_tokens(g, access_ttl=access_ttl, refresh_ttl=refresh_ttl)

    def revoke(self, token: str) -> bool:
        with self._lock:
            self._load()
            hit = False
            for bucket in ("tokens", "refresh"):
                if self._data[bucket].pop(_h(token), None) is not None:
                    hit = True
            if hit:
                self._save()
            return hit

    def revoke_grants_of(self, client_id: str) -> int:
        with self._lock:
            self._load()
            n = 0
            for bucket in ("tokens", "refresh", "auth_codes"):
                dead = [k for k, v in self._data[bucket].items() if v.get("client_id") == client_id]
                for k in dead:
                    del self._data[bucket][k]
                n += len(dead)
            if n:
                self._save()
            return n


_DEFAULT: Optional[OAuthStore] = None
_DEFAULT_LOCK = threading.Lock()


def get_store() -> OAuthStore:
    """운영용 기본 저장소 (logs/oauth.json)."""
    global _DEFAULT
    with _DEFAULT_LOCK:
        if _DEFAULT is None:
            _DEFAULT = OAuthStore()
        return _DEFAULT
