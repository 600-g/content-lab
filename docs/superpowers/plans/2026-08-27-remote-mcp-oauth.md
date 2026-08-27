# aiskillbox 원격 MCP 커넥터 (OAuth 2.1 + Streamable HTTP) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** claude.ai 웹·모바일·Cowork 에서 커스텀 커넥터로 붙여 스킬 라이브러리 97건을 검색·열람할 수 있게 한다.

**Architecture:** 기존 stdio MCP 서버의 순수 디스패치 `handle(msg)` 를 그대로 재사용하고, Flask 앱에 (1) `POST /mcp` Streamable HTTP 입구와 (2) OAuth 2.1 인가서버(메타데이터·동적등록·authorize·token·revoke)를 얹는다. 신규 의존성 없음(표준 라이브러리 + 이미 쓰는 Flask). 토큰 폐기는 새 개념을 만들지 않고 기존 초대코드 존재 여부에 대한 지연 검증으로 처리한다.

**Tech Stack:** Python 3 표준 라이브러리, Flask (기존), unittest (기존), JSON 파일 저장소 (기존 `auth_store.py` 패턴)

**Spec:** `docs/superpowers/specs/2026-08-27-remote-mcp-oauth-design.md`

## Global Constraints

- **신규 의존성 0.** 표준 라이브러리 + 이미 설치된 Flask 만. `requirements.txt` 를 건드리지 않는다.
- **테스트는 네트워크 0.** 모든 테스트는 tempfile 저장소 + Flask test client. 실제 소켓 금지.
- **`handle()` 시그니처 불변.** `scripts/library/mcp_server.py:handle(msg: dict) -> Optional[dict]` 를 바꾸면 stdio 경로가 깨진다. `tests/test_mcp_server.py` 가 회귀 가드.
- **모든 절대 URL 은 `config.json` 의 `mcp_remote.public_base_url` 에서만 만든다.** CF Tunnel 이 TLS 를 종단해서 `request.url_root` 는 `http://` 를 준다. 메타데이터·`WWW-Authenticate`·issuer 에 `http://` 가 새면 Claude 가 연결을 거부한다.
- **비밀은 해시만 저장.** client_secret · 인가코드 · access · refresh 전부 `sha256` 만 `logs/oauth.json` 에 넣는다. 평문 저장은 `client_id` · `name` · `redirect_uris` 뿐.
- **스코프는 `skills:read` 하나.** 다른 값 요구 시 거부하지 않고 `skills:read` 로 좁혀 발급하고, 발급된 스코프를 토큰 응답에 명시한다.
- **리소스 식별자는 `<public_base_url>/mcp`.** authorize·token 의 `resource` 파라미터(RFC 8707)와 발급 토큰의 audience 가 이 값으로 일치해야 한다.
- **PKCE 는 S256 만.** `plain` 은 거부한다.
- 파일당 200-400줄 유지 (프로젝트 coding-style). 초과하면 책임 단위로 쪼갠다.
- 커밋 메시지 형식: `<type>: <description>` (feat/fix/refactor/docs/test/chore).

## 스펙과의 차이 (의도된 것)

스펙 1절은 `oauth_routes.py` 한 파일이었으나, 메타데이터+등록+authorize+token+revoke 를 한 파일에 담으면 400줄을 넘겨 coding-style 권장을 초과한다. 책임 경계로 둘로 쪼갠다:
- `oauth_meta.py` — discovery 표면 (`/.well-known/*`, `/oauth/register`)
- `oauth_grants.py` — grant 흐름 (`/oauth/authorize`, `/oauth/token`, `/oauth/revoke`)

또 config 접근이 4개 모듈에 흩어지므로 `config.py` 를 하나 둔다 (mtime 재적재 — 서버 재시작 없이 `dynamic_registration` 토글을 켜고 끄기 위해 필요).

## File Structure

**신규**
- `scripts/mcp_remote/__init__.py` — `register_mcp_remote(app)` 하나만 노출. 세 라우트 모듈을 배선.
- `scripts/mcp_remote/config.py` — `config.json` 의 `mcp_remote` 블록 읽기(mtime 재적재) + 절대 URL 빌더.
- `scripts/mcp_remote/oauth_store.py` — `logs/oauth.json` 저장소. Flask 를 import 하지 않는다.
- `scripts/mcp_remote/oauth_meta.py` — `/.well-known/oauth-protected-resource[/mcp]`, `/.well-known/oauth-authorization-server`, `POST /oauth/register`.
- `scripts/mcp_remote/oauth_grants.py` — `GET|POST /oauth/authorize`, `POST /oauth/token`, `POST /oauth/revoke`.
- `scripts/mcp_remote/transport.py` — `POST /mcp`, `GET /mcp` → 405.
- `scripts/mcp_remote/cli.py` — `python -m scripts.mcp_remote client create|list|delete`.
- `scripts/mcp_remote/__main__.py` — cli 진입점.
- `templates/oauth_consent.html` — 동의 화면.
- `tests/test_oauth_store.py`, `tests/test_oauth_meta.py`, `tests/test_oauth_grants.py`, `tests/test_mcp_transport.py`

**수정**
- `scripts/auth_store.py` — `has_code(code) -> bool` 추가 (지연 폐기 검증용. 기존 메서드 불변).
- `scripts/library/mcp_server.py` — `use_local_backend()` 시임 + `_FORCE_LOCAL` 분기. `handle()` 불변.
- `scripts/auth_routes.py` — 게이트 allowlist 에 `/mcp` (exact), `/oauth/`·`/.well-known/` (prefix) 추가.
- `app.py` — `register_mcp_remote(app)` 배선 1줄.
- `config.json` — `mcp_remote` 블록.

---

### Task 1: OAuth 저장소 + 초대코드 존재 확인

**Files:**
- Create: `scripts/mcp_remote/__init__.py` (빈 파일로 시작), `scripts/mcp_remote/oauth_store.py`
- Modify: `scripts/auth_store.py` (`has_code` 추가)
- Test: `tests/test_oauth_store.py`

**Interfaces:**
- Consumes: `scripts.auth_store.AuthStore` (기존)
- Produces:
  - `AuthStore.has_code(code: str) -> bool`
  - `AuthStore.code_of_token(token: str) -> Optional[str]`
  - `OAuthStore(path, *, auth_store=None)`
  - `create_client(name, redirect_uris, *, source="manual", public=False) -> tuple[str, Optional[str]]` → `(client_id, secret|None)`
  - `verify_client(client_id, secret) -> bool`
  - `get_client(client_id) -> Optional[dict]`
  - `list_clients() -> list[dict]`
  - `delete_client(client_id) -> bool`
  - `issue_code(*, client_id, redirect_uri, code_challenge, resource, scope, invite_code) -> str`
  - `consume_code(code) -> Optional[dict]` (1회용)
  - `issue_tokens(grant, *, access_ttl, refresh_ttl) -> tuple[str, str, int]`
  - `validate_access(token, *, resource) -> Optional[dict]`
  - `rotate_refresh(token, *, access_ttl, refresh_ttl) -> Optional[tuple[str, str, int]]`
  - `revoke(token) -> bool`
  - `revoke_grants_of(client_id) -> int`

- [ ] **Step 1: `has_code` 실패 테스트를 쓴다**

`tests/test_oauth_store.py` 를 만든다.

```python
"""scripts.mcp_remote.oauth_store — OAuth 저장소 (네트워크 0, 임시 디렉토리)."""
from __future__ import annotations

import shutil
import tempfile
import time
import unittest
from pathlib import Path

from scripts.auth_store import AuthStore
from scripts.mcp_remote.oauth_store import OAuthStore

RESOURCE = "https://aiskillbox.600g.net/mcp"


class HasCodeTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="oauth_store_"))
        self.auth = AuthStore(self.dir / "auth.json")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_has_code_true_after_create(self):
        code = self.auth.create_code("폰")
        self.assertTrue(self.auth.has_code(code))

    def test_has_code_false_after_delete(self):
        code = self.auth.create_code("폰")
        self.auth.delete_code(code)
        self.assertFalse(self.auth.has_code(code))

    def test_has_code_false_for_unknown(self):
        self.assertFalse(self.auth.has_code("DGN-ZZZZ-ZZZZ"))
        self.assertFalse(self.auth.has_code(""))

    def test_code_of_token_roundtrip(self):
        code = self.auth.create_code("폰")
        token = self.auth.redeem(code, device="test")
        self.assertEqual(self.auth.code_of_token(token), code)
        self.assertIsNone(self.auth.code_of_token("nope"))
        self.assertIsNone(self.auth.code_of_token(None))
```

- [ ] **Step 2: 실패를 확인한다**

Run: `venv/bin/python -m unittest tests.test_oauth_store -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.mcp_remote'`

- [ ] **Step 3: 패키지와 `has_code` 를 만든다**

```bash
mkdir -p scripts/mcp_remote
printf '"""aiskillbox 원격 MCP 커넥터 (OAuth 2.1 + Streamable HTTP)."""\n' > scripts/mcp_remote/__init__.py
```

`scripts/auth_store.py` 의 `session_count` 바로 위에 넣는다 (기존 메서드는 건드리지 않는다):

```python
    def has_code(self, code: str) -> bool:
        """초대코드가 아직 살아있는지 — OAuth grant 지연 폐기 검증용."""
        code = (code or "").strip().upper()
        if not code:
            return False
        with self._lock:
            self._load()
            return code in self._data["codes"]

    def code_of_token(self, token: Optional[str]) -> Optional[str]:
        """기기 토큰 → 그것을 발급한 초대코드. OAuth grant 에 승인 주체를 박기 위해 필요."""
        if not token:
            return None
        with self._lock:
            self._load()
            s = self._data["sessions"].get(_hash_token(str(token)))
            return s.get("code") if s else None
```

빈 `scripts/mcp_remote/oauth_store.py` 에 최소 stub 을 둬서 import 가 되게 한다:

```python
class OAuthStore:  # 다음 스텝에서 채운다
    pass
```

- [ ] **Step 4: 통과를 확인한다**

Run: `venv/bin/python -m unittest tests.test_oauth_store -v`
Expected: PASS (4건)

- [ ] **Step 5: 저장소 실패 테스트를 쓴다**

`tests/test_oauth_store.py` 에 이어 붙인다.

```python
class OAuthStoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="oauth_store_"))
        self.auth = AuthStore(self.dir / "auth.json")
        self.code = self.auth.create_code("테스트")
        self.st = OAuthStore(self.dir / "oauth.json", auth_store=self.auth)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _grant(self):
        return {"client_id": "c1", "resource": RESOURCE,
                "scope": "skills:read", "invite_code": self.code}

    def test_client_roundtrip(self):
        cid, secret = self.st.create_client("Claude", ["https://claude.ai/cb"])
        self.assertTrue(cid and secret)
        self.assertTrue(self.st.verify_client(cid, secret))
        self.assertFalse(self.st.verify_client(cid, "wrong"))
        self.assertEqual(self.st.get_client(cid)["redirect_uris"], ["https://claude.ai/cb"])

    def test_client_secret_never_stored_plaintext(self):
        cid, secret = self.st.create_client("Claude", ["https://claude.ai/cb"])
        raw = (self.dir / "oauth.json").read_text(encoding="utf-8")
        self.assertNotIn(secret, raw)
        self.assertIn(cid, raw)

    def test_public_client_has_no_secret(self):
        cid, secret = self.st.create_client("Pub", ["https://claude.ai/cb"], public=True)
        self.assertIsNone(secret)
        self.assertTrue(self.st.verify_client(cid, None))

    def test_code_is_single_use(self):
        code = self.st.issue_code(client_id="c1", redirect_uri="https://claude.ai/cb",
                                  code_challenge="chal", resource=RESOURCE,
                                  scope="skills:read", invite_code=self.code)
        first = self.st.consume_code(code)
        self.assertEqual(first["client_id"], "c1")
        self.assertIsNone(self.st.consume_code(code))

    def test_code_expires(self):
        code = self.st.issue_code(client_id="c1", redirect_uri="https://claude.ai/cb",
                                  code_challenge="chal", resource=RESOURCE,
                                  scope="skills:read", invite_code=self.code, ttl=-1)
        self.assertIsNone(self.st.consume_code(code))

    def test_access_token_validates(self):
        access, refresh, ttl = self.st.issue_tokens(self._grant(), access_ttl=60, refresh_ttl=600)
        self.assertEqual(ttl, 60)
        self.assertIsNotNone(self.st.validate_access(access, resource=RESOURCE))

    def test_access_token_rejects_wrong_resource(self):
        access, _, _ = self.st.issue_tokens(self._grant(), access_ttl=60, refresh_ttl=600)
        self.assertIsNone(self.st.validate_access(access, resource="https://evil.example/mcp"))

    def test_access_token_expires(self):
        access, _, _ = self.st.issue_tokens(self._grant(), access_ttl=-1, refresh_ttl=600)
        self.assertIsNone(self.st.validate_access(access, resource=RESOURCE))

    def test_deleting_invite_code_kills_token(self):
        access, _, _ = self.st.issue_tokens(self._grant(), access_ttl=60, refresh_ttl=600)
        self.assertIsNotNone(self.st.validate_access(access, resource=RESOURCE))
        self.auth.delete_code(self.code)
        self.assertIsNone(self.st.validate_access(access, resource=RESOURCE))

    def test_refresh_rotates_and_old_dies(self):
        _, refresh, _ = self.st.issue_tokens(self._grant(), access_ttl=60, refresh_ttl=600)
        rotated = self.st.rotate_refresh(refresh, access_ttl=60, refresh_ttl=600)
        self.assertIsNotNone(rotated)
        new_access, new_refresh, _ = rotated
        self.assertNotEqual(refresh, new_refresh)
        self.assertIsNotNone(self.st.validate_access(new_access, resource=RESOURCE))
        self.assertIsNone(self.st.rotate_refresh(refresh, access_ttl=60, refresh_ttl=600))

    def test_revoke_grants_of_client(self):
        a1, _, _ = self.st.issue_tokens(self._grant(), access_ttl=60, refresh_ttl=600)
        n = self.st.revoke_grants_of("c1")
        self.assertGreaterEqual(n, 1)
        self.assertIsNone(self.st.validate_access(a1, resource=RESOURCE))

    def test_reloads_when_file_changes_on_disk(self):
        cid, secret = self.st.create_client("Claude", ["https://claude.ai/cb"])
        other = OAuthStore(self.dir / "oauth.json", auth_store=self.auth)
        other.delete_client(cid)
        self.assertFalse(self.st.verify_client(cid, secret))
```

- [ ] **Step 6: 실패를 확인한다**

Run: `venv/bin/python -m unittest tests.test_oauth_store -v`
Expected: FAIL — `AttributeError: 'OAuthStore' object has no attribute 'create_client'`

- [ ] **Step 7: 저장소를 구현한다**

`scripts/mcp_remote/oauth_store.py` 전체를 쓴다. `auth_store.py` 의 규약(0600, tmp+os.replace 원자적 쓰기, `threading.Lock`, mtime 재적재)을 그대로 따른다.

```python
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

    def consume_code(self, code: str) -> Optional[dict]:
        """1회용 — 존재하면 삭제하고 반환. 만료면 None (삭제는 함)."""
        if not code:
            return None
        with self._lock:
            self._load()
            g = self._data["auth_codes"].pop(_h(code), None)
            if g is not None:
                self._save()
            if g is None or g.get("expires_at", 0) < time.time():
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

    def rotate_refresh(self, token: str, *, access_ttl: int,
                       refresh_ttl: int) -> Optional[tuple[str, str, int]]:
        g = self._valid("refresh", token, resource=None)
        if g is None:
            return None
        with self._lock:
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
```

- [ ] **Step 8: 통과를 확인한다**

Run: `venv/bin/python -m unittest tests.test_oauth_store -v`
Expected: PASS (전체). 실패하면 실패한 테스트 하나만 보고 고친다.

- [ ] **Step 9: 기존 테스트 회귀를 확인한다**

Run: `venv/bin/python -m unittest discover -s tests -t . 2>&1 | tail -5`
Expected: OK — `auth_store.py` 수정이 기존 테스트를 깨지 않았는지 확인.

- [ ] **Step 10: 커밋**

```bash
git add scripts/mcp_remote/__init__.py scripts/mcp_remote/oauth_store.py scripts/auth_store.py tests/test_oauth_store.py
git commit -m "feat(mcp-remote): OAuth 저장소 + 초대코드 지연 폐기 검증"
```

---

### Task 2: in-process 백엔드 시임 (자기호출 루프 차단)

`transport.py` 가 같은 프로세스 안에서 `mcp_server` 를 부르면 `_http_get` 이 자기 서버(localhost:5050)를 다시 때리고, v4.6 게이트에 막혀 401 을 받는다. 로컬 인덱스 직접 경로로 고정하는 시임을 넣는다.

**Files:**
- Modify: `scripts/library/mcp_server.py`
- Test: `tests/test_mcp_server.py` (기존 파일에 추가)

**Interfaces:**
- Consumes: `scripts.library.mcp_server.backend_search/backend_get/backend_list` (기존)
- Produces: `use_local_backend() -> None` — 호출 후 모든 `backend_*` 가 HTTP 를 건너뛰고 `"inproc"` 모드로 응답한다. `handle()` 시그니처는 불변.

- [ ] **Step 1: 실패 테스트를 쓴다**

`tests/test_mcp_server.py` 끝에 추가한다. 실제 소켓을 쓰지 않고, HTTP 경로를 타면 즉시 터지게 `_http_get` 을 지뢰로 바꿔서 확인한다.

```python
class LocalBackendSeamTest(unittest.TestCase):
    """use_local_backend() 이후에는 _http_get 이 절대 호출되지 않아야 한다."""

    def setUp(self):
        from scripts.library import mcp_server as ms
        self.ms = ms
        self.root = make_mirror()
        self._saved_force = getattr(ms, "_FORCE_LOCAL", False)
        self._saved_http = ms._http_get
        self._saved_root = ms.LOCAL_ROOT
        ms.LOCAL_ROOT = str(self.root)

        def landmine(*a, **kw):
            raise AssertionError("in-process 모드인데 HTTP 백엔드를 호출했다")

        ms._http_get = landmine

    def tearDown(self):
        self.ms._http_get = self._saved_http
        self.ms._FORCE_LOCAL = self._saved_force
        self.ms.LOCAL_ROOT = self._saved_root
        shutil.rmtree(self.root, ignore_errors=True)

    def test_search_uses_local_index(self):
        self.ms.use_local_backend()
        res, mode = self.ms.backend_search("릴스", 3, "")
        self.assertEqual(mode, "inproc")
        self.assertIn("results", res)

    def test_get_uses_local_index(self):
        self.ms.use_local_backend()
        raw, mode = self.ms.backend_get("instagram-reels-script-automation")
        self.assertEqual(mode, "inproc")
        self.assertIn("---", raw)

    def test_list_uses_local_index(self):
        self.ms.use_local_backend()
        items, mode = self.ms.backend_list("", "")
        self.assertEqual(mode, "inproc")
        self.assertTrue(items)

    def test_inproc_mode_has_no_fallback_warning(self):
        """'서버 미응답' 문구가 사용자에게 새면 안 된다 — 정상 경로다."""
        self.assertEqual(self.ms._mode_tag("inproc"), "")
```

> `tests/test_mcp_server.py` 는 이미 `shutil` 과 `from tests.fixtures import SKILLS, make_mirror` 를 import 하고 있다 (확인함). `make_mirror()` 는 임시 루트 `Path` **하나**를 반환하고 정리는 호출자 몫이다.

- [ ] **Step 2: 실패를 확인한다**

Run: `venv/bin/python -m unittest tests.test_mcp_server -v`
Expected: FAIL — `AttributeError: module 'scripts.library.mcp_server' has no attribute 'use_local_backend'`

- [ ] **Step 3: 시임을 구현한다**

`scripts/library/mcp_server.py` 의 `MAX_K = 20` 아래에 플래그를 둔다:

```python
_FORCE_LOCAL = False


def use_local_backend() -> None:
    """같은 프로세스 안(Flask transport)에서 쓸 때 HTTP 백엔드를 건너뛴다.

    안 하면 _http_get 이 자기 서버를 다시 때리고 v4.6 게이트에 막혀 401 을 받는다.
    같은 프로세스라 scripts.library 인덱스를 공유하므로 이중 적재도 없다.
    """
    global _FORCE_LOCAL
    _FORCE_LOCAL = True
```

세 `backend_*` 함수 맨 앞에 각각 분기를 넣는다:

```python
def backend_search(query: str, k: int, category: str) -> tuple[dict, str]:
    if _FORCE_LOCAL:
        return _local_search(query, k, category), "inproc"
    try:
```

```python
def backend_get(slug: str) -> tuple[Optional[str], str]:
    if _FORCE_LOCAL:
        return _local_get_raw(slug), "inproc"
    try:
```

```python
def backend_list(category: str, grade: str) -> tuple[list[dict], str]:
    if _FORCE_LOCAL:
        return _local_list(category, grade), "inproc"
    try:
```

`_mode_tag` 를 고쳐 `inproc` 도 정상 경로로 취급한다 (안 그러면 "서버 미응답" 문구가 사용자에게 샌다):

```python
def _mode_tag(mode: str) -> str:
    return "" if mode in ("http", "inproc") else " (로컬 인덱스 폴백 — aiskillbox 서버 미응답)"
```

- [ ] **Step 4: 통과를 확인한다**

Run: `venv/bin/python -m unittest tests.test_mcp_server -v`
Expected: PASS. 기존 테스트가 전부 함께 통과해야 한다 (`handle()` 불변 회귀 가드).

- [ ] **Step 5: 커밋**

```bash
git add scripts/library/mcp_server.py tests/test_mcp_server.py
git commit -m "feat(mcp): in-process 백엔드 시임 — 자기호출 루프 차단"
```

---

### Task 3: 설정 모듈 + 무차별 대입 가드

**Files:**
- Create: `scripts/mcp_remote/config.py`, `scripts/mcp_remote/guard.py`
- Modify: `config.json`
- Test: `tests/test_mcp_remote_config.py`, `tests/test_mcp_remote_guard.py`

**Interfaces:**
- Produces:
  - `load(path=None) -> dict` — 기본값 병합, mtime 재적재
  - `base_url() -> str` — 끝 슬래시 없음
  - `abs_url(path: str) -> str`
  - `resource_id() -> str` — `<base>/mcp`
  - `enabled() -> bool`, `dynamic_registration() -> bool`, `allowed_origins() -> list[str]`
  - `access_ttl() -> int`, `refresh_ttl() -> int`
  - `guard.FailGuard(max_fails=5, lock_seconds=300, clock=time.time)` —
    `check(key) -> Optional[str]` (잠겼으면 사유) · `fail(key) -> None` · `ok(key) -> None`

- [ ] **Step 1: 실패 테스트를 쓴다**

```python
"""scripts.mcp_remote.config — 설정 로드 + 절대 URL 빌더 (네트워크 0)."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.mcp_remote import config as cfg


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="mcp_cfg_"))
        self.path = self.dir / "config.json"

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _write(self, block):
        self.path.write_text(json.dumps({"mcp_remote": block}), encoding="utf-8")

    def test_defaults_when_block_missing(self):
        self.path.write_text(json.dumps({}), encoding="utf-8")
        c = cfg.load(self.path)
        self.assertFalse(c["dynamic_registration"])
        self.assertEqual(c["access_ttl_seconds"], 3600)

    def test_trailing_slash_stripped(self):
        self._write({"public_base_url": "https://x.example/"})
        self.assertEqual(cfg.load(self.path)["public_base_url"], "https://x.example")

    def test_abs_url_and_resource_id(self):
        self._write({"public_base_url": "https://x.example"})
        c = cfg.load(self.path)
        self.assertEqual(cfg.abs_url("/oauth/token", c), "https://x.example/oauth/token")
        self.assertEqual(cfg.resource_id(c), "https://x.example/mcp")

    def test_http_base_url_is_rejected(self):
        """CF Tunnel 함정 — http 가 새면 Claude 가 연결을 거부한다."""
        self._write({"public_base_url": "http://x.example"})
        with self.assertRaises(ValueError):
            cfg.load(self.path)

    def test_reloads_when_file_changes(self):
        self._write({"dynamic_registration": False})
        self.assertFalse(cfg.load(self.path)["dynamic_registration"])
        self._write({"dynamic_registration": True})
        import os, time
        os.utime(self.path, (time.time() + 2, time.time() + 2))
        self.assertTrue(cfg.load(self.path)["dynamic_registration"])
```

- [ ] **Step 2: 실패를 확인한다**

Run: `venv/bin/python -m unittest tests.test_mcp_remote_config -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.mcp_remote.config'`

- [ ] **Step 3: 구현한다**

`scripts/mcp_remote/config.py`:

```python
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
```

- [ ] **Step 4: 통과를 확인한다**

Run: `venv/bin/python -m unittest tests.test_mcp_remote_config -v`
Expected: PASS (5건)

- [ ] **Step 5: `config.json` 에 블록을 넣는다**

`chat` 블록 뒤에 추가한다 (JSON 이라 앞 블록 끝에 쉼표 필요):

```json
  "mcp_remote": {
    "enabled": true,
    "public_base_url": "https://aiskillbox.600g.net",
    "dynamic_registration": false,
    "allowed_origins": ["https://claude.ai", "https://claude.com"],
    "access_ttl_seconds": 3600,
    "refresh_ttl_seconds": 7776000,
    "_note": "dynamic_registration 은 최초 커넥터 연결 때만 true 로 켰다가 되돌린다. public_base_url 은 반드시 https — CF Tunnel 이 TLS 를 종단해서 헤더 추측은 http 를 준다."
  }
```

- [ ] **Step 6: JSON 유효성 + 로드를 확인한다**

```bash
python3 -c "import json; json.load(open('config.json')); print('JSON OK')"
venv/bin/python -c "from scripts.mcp_remote import config; print(config.resource_id())"
```
Expected: `JSON OK` 와 `https://aiskillbox.600g.net/mcp`

- [ ] **Step 7: 가드 실패 테스트를 쓴다**

`tests/test_mcp_remote_guard.py`:

```python
"""scripts.mcp_remote.guard — 무차별 대입 가드 (시계 주입, 네트워크 0)."""
from __future__ import annotations

import unittest

from scripts.mcp_remote.guard import FailGuard


class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def advance(self, sec):
        self.t += sec


class FailGuardTest(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.g = FailGuard(max_fails=5, lock_seconds=300, clock=self.clock)

    def test_four_failures_do_not_lock(self):
        for _ in range(4):
            self.g.fail("c1")
        self.assertIsNone(self.g.check("c1"))

    def test_fifth_failure_locks(self):
        for _ in range(5):
            self.g.fail("c1")
        msg = self.g.check("c1")
        self.assertIsNotNone(msg)
        self.assertIn("초", msg)

    def test_lock_expires(self):
        for _ in range(5):
            self.g.fail("c1")
        self.clock.advance(301)
        self.assertIsNone(self.g.check("c1"))

    def test_success_resets_counter(self):
        for _ in range(4):
            self.g.fail("c1")
        self.g.ok("c1")
        self.g.fail("c1")
        self.assertIsNone(self.g.check("c1"))

    def test_keys_are_independent(self):
        for _ in range(5):
            self.g.fail("c1")
        self.assertIsNotNone(self.g.check("c1"))
        self.assertIsNone(self.g.check("c2"))
```

- [ ] **Step 8: 실패를 확인한다**

Run: `venv/bin/python -m unittest tests.test_mcp_remote_guard -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.mcp_remote.guard'`

- [ ] **Step 9: 가드를 구현한다**

`scripts/mcp_remote/guard.py`:

```python
"""무차별 대입 가드 — auth_routes._RedeemGuard 와 같은 파라미터 (5회 실패 → 5분 잠금).

다른 모듈의 private 를 끌어다 쓰지 않고 같은 규칙을 복제한다. 대신 키별 추적을 더한다:
한 client_id 가 잠겨도 다른 클라이언트는 영향받지 않는다.
"""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional


class FailGuard:
    def __init__(self, *, max_fails: int = 5, lock_seconds: int = 300,
                 clock: Callable[[], float] = time.time) -> None:
        self._max = max_fails
        self._lock_sec = lock_seconds
        self._clock = clock
        self._mu = threading.Lock()
        self._fails: dict[str, int] = {}
        self._until: dict[str, float] = {}

    def check(self, key: str = "global") -> Optional[str]:
        """잠겨 있으면 사용자에게 보여줄 사유, 아니면 None."""
        with self._mu:
            wait = int(self._until.get(key, 0.0) - self._clock())
            return f"시도 잠김 — {wait}초 후 재시도" if wait > 0 else None

    def fail(self, key: str = "global") -> None:
        with self._mu:
            c = self._fails.get(key, 0) + 1
            if c >= self._max:
                self._until[key] = self._clock() + self._lock_sec
                self._fails[key] = 0
            else:
                self._fails[key] = c

    def ok(self, key: str = "global") -> None:
        with self._mu:
            self._fails.pop(key, None)
            self._until.pop(key, None)
```

- [ ] **Step 10: 통과를 확인한다**

Run: `venv/bin/python -m unittest tests.test_mcp_remote_guard -v`
Expected: PASS (5건)

- [ ] **Step 11: 커밋**

```bash
git add scripts/mcp_remote/config.py scripts/mcp_remote/guard.py config.json tests/test_mcp_remote_config.py tests/test_mcp_remote_guard.py
git commit -m "feat(mcp-remote): 설정 모듈 + 무차별 대입 가드"
```

---

### Task 4: Streamable HTTP 전송 (`POST /mcp`)

**Files:**
- Create: `scripts/mcp_remote/transport.py`
- Test: `tests/test_mcp_transport.py`

**Interfaces:**
- Consumes: `oauth_store.OAuthStore.validate_access`, `config.resource_id/abs_url/allowed_origins`, `mcp_server.handle/use_local_backend`
- Produces: `register_transport(app, *, store=None, cfg=None) -> None` — `POST /mcp`, `GET /mcp`

- [ ] **Step 1: 실패 테스트를 쓴다**

```python
"""scripts.mcp_remote.transport — POST /mcp Streamable HTTP (Flask test client, 네트워크 0)."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from flask import Flask

from scripts.auth_store import AuthStore
from scripts.mcp_remote.oauth_store import OAuthStore
from scripts.mcp_remote.transport import register_transport

BASE = "https://aiskillbox.600g.net"
RESOURCE = BASE + "/mcp"
CFG = {"enabled": True, "public_base_url": BASE, "dynamic_registration": False,
       "allowed_origins": ["https://claude.ai"], "access_ttl_seconds": 3600,
       "refresh_ttl_seconds": 7776000}


class TransportTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="mcp_tr_"))
        self.auth = AuthStore(self.dir / "auth.json")
        self.code = self.auth.create_code("테스트")
        self.st = OAuthStore(self.dir / "oauth.json", auth_store=self.auth)
        self.access, _, _ = self.st.issue_tokens(
            {"client_id": "c1", "resource": RESOURCE, "scope": "skills:read",
             "invite_code": self.code}, access_ttl=600, refresh_ttl=600)
        app = Flask(__name__)
        app.config["TESTING"] = True
        register_transport(app, store=self.st, cfg=CFG)
        self.c = app.test_client()

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _post(self, body, token=None, origin="https://claude.ai"):
        h = {"Content-Type": "application/json"}
        if token:
            h["Authorization"] = "Bearer " + token
        if origin:
            h["Origin"] = origin
        return self.c.post("/mcp", json=body, headers=h)

    def test_no_token_is_401_with_resource_metadata_header(self):
        r = self._post({"jsonrpc": "2.0", "id": 1, "method": "ping"})
        self.assertEqual(r.status_code, 401)
        www = r.headers.get("WWW-Authenticate", "")
        self.assertIn("Bearer", www)
        self.assertIn("/.well-known/oauth-protected-resource", www)
        self.assertIn("https://", www)
        self.assertNotIn("http://", www)

    def test_bad_token_is_401(self):
        r = self._post({"jsonrpc": "2.0", "id": 1, "method": "ping"}, token="nope")
        self.assertEqual(r.status_code, 401)

    def test_revoked_invite_code_is_401(self):
        self.auth.delete_code(self.code)
        r = self._post({"jsonrpc": "2.0", "id": 1, "method": "ping"}, token=self.access)
        self.assertEqual(r.status_code, 401)

    def test_initialize_roundtrip(self):
        r = self._post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                        "params": {"protocolVersion": "2025-06-18"}}, token=self.access)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers["Content-Type"].split(";")[0], "application/json")
        body = r.get_json()
        self.assertEqual(body["id"], 1)
        self.assertEqual(body["result"]["serverInfo"]["name"], "skill-library")

    def test_tools_list_has_three_read_tools(self):
        r = self._post({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, token=self.access)
        names = {t["name"] for t in r.get_json()["result"]["tools"]}
        self.assertEqual(names, {"search_skills", "get_skill", "list_skills"})

    def test_notification_returns_202_no_body(self):
        r = self._post({"jsonrpc": "2.0", "method": "notifications/initialized"}, token=self.access)
        self.assertEqual(r.status_code, 202)
        self.assertEqual(r.get_data(), b"")

    def test_get_is_405(self):
        r = self.c.get("/mcp", headers={"Authorization": "Bearer " + self.access})
        self.assertEqual(r.status_code, 405)

    def test_bad_origin_is_403(self):
        r = self._post({"jsonrpc": "2.0", "id": 1, "method": "ping"},
                       token=self.access, origin="https://evil.example")
        self.assertEqual(r.status_code, 403)

    def test_missing_origin_is_allowed(self):
        """curl·서버간 호출은 Origin 이 없다 — 브라우저만 강제한다."""
        r = self._post({"jsonrpc": "2.0", "id": 1, "method": "ping"},
                       token=self.access, origin=None)
        self.assertEqual(r.status_code, 200)

    def test_batch_request(self):
        r = self._post([{"jsonrpc": "2.0", "id": 1, "method": "ping"},
                        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}], token=self.access)
        body = r.get_json()
        self.assertEqual(len(body), 2)
        self.assertEqual({m["id"] for m in body}, {1, 2})

    def test_malformed_json_is_jsonrpc_parse_error(self):
        r = self.c.post("/mcp", data="{not json",
                        headers={"Content-Type": "application/json",
                                 "Authorization": "Bearer " + self.access})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["error"]["code"], -32700)
```

- [ ] **Step 2: 실패를 확인한다**

Run: `venv/bin/python -m unittest tests.test_mcp_transport -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.mcp_remote.transport'`

- [ ] **Step 3: 구현한다**

`scripts/mcp_remote/transport.py`:

```python
"""MCP Streamable HTTP 전송 — POST /mcp (stateless).

기존 stdio 서버의 순수 디스패치 mcp_server.handle(msg) 를 그대로 재사용한다.
SSE 미지원(도구 3종이 전부 즉답형), 세션 ID 미발급(stateless).

설계: docs/superpowers/specs/2026-08-27-remote-mcp-oauth-design.md
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from flask import Flask, Response, jsonify, request

from scripts.library import mcp_server
from scripts.mcp_remote import config as mcp_config
from scripts.mcp_remote import oauth_store as store_mod

logger = logging.getLogger(__name__)

PROTECTED_RESOURCE_PATH = "/.well-known/oauth-protected-resource"


def _rpc_error(req_id, code: int, message: str, status: int):
    return jsonify({"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": code, "message": message}}), status


def register_transport(app: Flask, *, store=None, cfg: Optional[dict] = None) -> None:
    """store/cfg 는 테스트 주입용 — 운영에서는 기본값(None)."""
    mcp_server.use_local_backend()   # 자기호출 루프 차단 (Task 2)

    def _cfg() -> dict:
        return cfg if cfg is not None else mcp_config.load()

    def _store():
        return store if store is not None else store_mod.get_store()

    def _challenge() -> str:
        url = mcp_config.abs_url(PROTECTED_RESOURCE_PATH, _cfg())
        return f'Bearer resource_metadata="{url}"'

    def _unauthorized(msg: str):
        resp = jsonify({"error": "invalid_token", "error_description": msg})
        resp.status_code = 401
        resp.headers["WWW-Authenticate"] = _challenge()
        return resp

    def _origin_ok(c: dict) -> bool:
        origin = request.headers.get("Origin")
        if not origin:
            return True   # curl·서버간 호출 — 브라우저가 아니면 Origin 이 없다
        return origin in mcp_config.allowed_origins(c)

    @app.post("/mcp")
    def mcp_endpoint():
        c = _cfg()
        if not mcp_config.enabled(c):
            return jsonify({"error": "disabled"}), 404
        if not _origin_ok(c):
            return jsonify({"error": "origin_not_allowed"}), 403

        auth = request.headers.get("Authorization", "")
        token = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
        if not token:
            return _unauthorized("Bearer 토큰이 필요합니다")
        grant = _store().validate_access(token, resource=mcp_config.resource_id(c))
        if grant is None:
            return _unauthorized("토큰이 유효하지 않거나 만료되었습니다")

        raw = request.get_data(as_text=True)
        try:
            payload = json.loads(raw) if raw.strip() else None
        except json.JSONDecodeError as e:
            return _rpc_error(None, -32700, f"Parse error: {e.msg}", 400)
        if payload is None:
            return _rpc_error(None, -32600, "Invalid Request", 400)

        batch = isinstance(payload, list)
        messages = payload if batch else [payload]
        if not messages or any(not isinstance(m, dict) for m in messages):
            return _rpc_error(None, -32600, "Invalid Request", 400)

        responses = []
        for msg in messages:
            try:
                resp = mcp_server.handle(msg)
            except Exception as e:  # noqa: BLE001
                logger.warning("handle 예외: %r", e)
                resp = {"jsonrpc": "2.0", "id": msg.get("id"),
                        "error": {"code": -32603, "message": f"Internal error: {e}"}}
            if resp is not None:
                responses.append(resp)

        if not responses:
            return Response(status=202)   # 알림만 있는 요청
        body = responses if batch else responses[0]
        return app.response_class(
            json.dumps(body, ensure_ascii=False), status=200,
            mimetype="application/json")

    @app.get("/mcp")
    def mcp_get_not_supported():
        resp = jsonify({"error": "method_not_allowed",
                        "error_description": "서버 발신 SSE 스트림은 지원하지 않습니다 — POST 를 쓰세요"})
        resp.status_code = 405
        resp.headers["Allow"] = "POST"
        return resp
```

- [ ] **Step 4: 통과를 확인한다**

Run: `venv/bin/python -m unittest tests.test_mcp_transport -v`
Expected: PASS (11건)

> `test_tools_list_has_three_read_tools` 가 실패하면 `mcp_server.TOOLS` 의 실제 도구 이름을 확인해 테스트를 맞춘다 (구현이 아니라 테스트가 틀린 경우다).

- [ ] **Step 5: 커밋**

```bash
git add scripts/mcp_remote/transport.py tests/test_mcp_transport.py
git commit -m "feat(mcp-remote): Streamable HTTP 전송 POST /mcp"
```

---

### Task 5: OAuth 메타데이터 + 동적 등록 토글

**Files:**
- Create: `scripts/mcp_remote/oauth_meta.py`
- Test: `tests/test_oauth_meta.py`

**Interfaces:**
- Produces: `register_oauth_meta(app, *, store=None, cfg=None) -> None`
  — `GET /.well-known/oauth-protected-resource`, `GET /.well-known/oauth-protected-resource/mcp`, `GET /.well-known/oauth-authorization-server`, `POST /oauth/register`

- [ ] **Step 1: 실패 테스트를 쓴다**

```python
"""scripts.mcp_remote.oauth_meta — discovery 메타데이터 + 동적 등록 (네트워크 0)."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from flask import Flask

from scripts.auth_store import AuthStore
from scripts.mcp_remote.oauth_meta import register_oauth_meta
from scripts.mcp_remote.oauth_store import OAuthStore

BASE = "https://aiskillbox.600g.net"


def _cfg(dcr: bool):
    return {"enabled": True, "public_base_url": BASE, "dynamic_registration": dcr,
            "allowed_origins": ["https://claude.ai"], "access_ttl_seconds": 3600,
            "refresh_ttl_seconds": 7776000}


class MetaTest(unittest.TestCase):
    def _client(self, dcr=False):
        self.dir = Path(tempfile.mkdtemp(prefix="oauth_meta_"))
        self.auth = AuthStore(self.dir / "auth.json")
        self.st = OAuthStore(self.dir / "oauth.json", auth_store=self.auth)
        app = Flask(__name__)
        app.config["TESTING"] = True
        register_oauth_meta(app, store=self.st, cfg=_cfg(dcr))
        return app.test_client()

    def tearDown(self):
        shutil.rmtree(getattr(self, "dir", Path(tempfile.gettempdir())), ignore_errors=True)

    def test_protected_resource_metadata(self):
        r = self._client().get("/.well-known/oauth-protected-resource")
        self.assertEqual(r.status_code, 200)
        b = r.get_json()
        self.assertEqual(b["resource"], BASE + "/mcp")
        self.assertEqual(b["authorization_servers"], [BASE])
        self.assertIn("skills:read", b["scopes_supported"])

    def test_protected_resource_path_variant(self):
        r = self._client().get("/.well-known/oauth-protected-resource/mcp")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["resource"], BASE + "/mcp")

    def test_as_metadata_shape(self):
        b = self._client().get("/.well-known/oauth-authorization-server").get_json()
        self.assertEqual(b["issuer"], BASE)
        self.assertEqual(b["authorization_endpoint"], BASE + "/oauth/authorize")
        self.assertEqual(b["token_endpoint"], BASE + "/oauth/token")
        self.assertEqual(b["code_challenge_methods_supported"], ["S256"])
        self.assertIn("authorization_code", b["grant_types_supported"])
        self.assertIn("refresh_token", b["grant_types_supported"])

    def test_no_http_urls_anywhere(self):
        """CF Tunnel 함정 회귀 가드."""
        import json as _json
        for path in ("/.well-known/oauth-protected-resource",
                     "/.well-known/oauth-authorization-server"):
            raw = _json.dumps(self._client().get(path).get_json())
            self.assertNotIn("http://", raw, path)

    def test_registration_endpoint_absent_when_toggle_off(self):
        b = self._client(dcr=False).get("/.well-known/oauth-authorization-server").get_json()
        self.assertNotIn("registration_endpoint", b)

    def test_registration_endpoint_present_when_toggle_on(self):
        b = self._client(dcr=True).get("/.well-known/oauth-authorization-server").get_json()
        self.assertEqual(b["registration_endpoint"], BASE + "/oauth/register")

    def test_register_is_404_when_toggle_off(self):
        r = self._client(dcr=False).post("/oauth/register",
                                         json={"redirect_uris": ["https://claude.ai/cb"]})
        self.assertEqual(r.status_code, 404)

    def test_register_creates_client_when_toggle_on(self):
        c = self._client(dcr=True)
        r = c.post("/oauth/register", json={"redirect_uris": ["https://claude.ai/cb"],
                                            "client_name": "Claude"})
        self.assertEqual(r.status_code, 201)
        b = r.get_json()
        self.assertTrue(b["client_id"])
        self.assertEqual(b["redirect_uris"], ["https://claude.ai/cb"])
        self.assertEqual(self.st.get_client(b["client_id"])["source"], "dynamic")

    def test_register_rejects_missing_redirect_uris(self):
        r = self._client(dcr=True).post("/oauth/register", json={"client_name": "X"})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["error"], "invalid_redirect_uri")

    def test_register_rejects_non_https_redirect(self):
        r = self._client(dcr=True).post("/oauth/register",
                                        json={"redirect_uris": ["http://evil.example/cb"]})
        self.assertEqual(r.status_code, 400)

    def test_register_locks_after_repeated_failures(self):
        c = self._client(dcr=True)
        for _ in range(5):
            c.post("/oauth/register", json={})
        r = c.post("/oauth/register", json={"redirect_uris": ["https://claude.ai/cb"]})
        self.assertEqual(r.status_code, 429)
```

- [ ] **Step 2: 실패를 확인한다**

Run: `venv/bin/python -m unittest tests.test_oauth_meta -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: 구현한다**

`scripts/mcp_remote/oauth_meta.py`:

```python
"""OAuth discovery 메타데이터 (RFC 9728 / RFC 8414) + 동적 등록 (RFC 7591).

동적 등록은 config 토글이다. 꺼져 있으면 registration_endpoint 를 메타데이터에서 빼고
/oauth/register 는 404 — 인터넷에 등록 창구가 열리지 않는다.
운영: 최초 커넥터 연결 때만 켜서 Claude 가 자기 redirect_uri 를 등록하게 하고 다시 끈다.
"""
from __future__ import annotations

import logging
from typing import Optional
from urllib.parse import urlparse

from flask import Flask, jsonify, request

from scripts.mcp_remote import config as mcp_config
from scripts.mcp_remote import oauth_store as store_mod
from scripts.mcp_remote.guard import FailGuard

logger = logging.getLogger(__name__)

SCOPE = "skills:read"
MAX_REDIRECT_URIS = 8
_GUARD = FailGuard()


def _https_uri(u: str) -> bool:
    try:
        p = urlparse(str(u))
    except Exception:  # noqa: BLE001
        return False
    return p.scheme == "https" and bool(p.netloc)


def register_oauth_meta(app: Flask, *, store=None, cfg: Optional[dict] = None) -> None:
    def _cfg() -> dict:
        return cfg if cfg is not None else mcp_config.load()

    def _store():
        return store if store is not None else store_mod.get_store()

    def _protected_resource():
        c = _cfg()
        return jsonify({
            "resource": mcp_config.resource_id(c),
            "authorization_servers": [mcp_config.base_url(c)],
            "scopes_supported": [SCOPE],
            "bearer_methods_supported": ["header"],
        })

    app.add_url_rule("/.well-known/oauth-protected-resource", "mcp_protected_resource",
                     _protected_resource, methods=["GET"])
    app.add_url_rule("/.well-known/oauth-protected-resource/mcp", "mcp_protected_resource_path",
                     _protected_resource, methods=["GET"])

    @app.get("/.well-known/oauth-authorization-server")
    def as_metadata():
        c = _cfg()
        meta = {
            "issuer": mcp_config.base_url(c),
            "authorization_endpoint": mcp_config.abs_url("/oauth/authorize", c),
            "token_endpoint": mcp_config.abs_url("/oauth/token", c),
            "revocation_endpoint": mcp_config.abs_url("/oauth/revoke", c),
            "scopes_supported": [SCOPE],
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "code_challenge_methods_supported": ["S256"],
            "token_endpoint_auth_methods_supported": ["client_secret_post", "none"],
        }
        if mcp_config.dynamic_registration(c):
            meta["registration_endpoint"] = mcp_config.abs_url("/oauth/register", c)
        return jsonify(meta)

    @app.post("/oauth/register")
    def register_client():
        c = _cfg()
        if not mcp_config.dynamic_registration(c):
            return jsonify({"error": "not_found"}), 404
        locked = _GUARD.check("register")
        if locked:
            return jsonify({"error": "too_many_requests", "error_description": locked}), 429
        body = request.get_json(silent=True) or {}
        uris = body.get("redirect_uris")
        if not isinstance(uris, list) or not uris or len(uris) > MAX_REDIRECT_URIS:
            _GUARD.fail("register")
            return jsonify({"error": "invalid_redirect_uri",
                            "error_description": "redirect_uris 배열이 필요합니다"}), 400
        if not all(_https_uri(u) for u in uris):
            _GUARD.fail("register")
            return jsonify({"error": "invalid_redirect_uri",
                            "error_description": "redirect_uri 는 https 절대 URL 이어야 합니다"}), 400
        name = str(body.get("client_name") or "unnamed")[:120]
        client_id, secret = _store().create_client(name, [str(u) for u in uris], source="dynamic")
        logger.info("동적 등록: %s (%s) redirect_uris=%s", name, client_id, uris)
        out = {"client_id": client_id, "client_name": name, "redirect_uris": [str(u) for u in uris],
               "grant_types": ["authorization_code", "refresh_token"],
               "response_types": ["code"], "token_endpoint_auth_method": "client_secret_post",
               "scope": SCOPE}
        if secret:
            out["client_secret"] = secret
        return jsonify(out), 201
```

- [ ] **Step 4: 통과를 확인한다**

Run: `venv/bin/python -m unittest tests.test_oauth_meta -v`
Expected: PASS (11건)

- [ ] **Step 5: 커밋**

```bash
git add scripts/mcp_remote/oauth_meta.py tests/test_oauth_meta.py
git commit -m "feat(mcp-remote): OAuth 메타데이터 + 동적 등록 토글"
```

---

### Task 6: authorize + token + revoke + 동의 화면

**Files:**
- Create: `scripts/mcp_remote/oauth_grants.py`, `templates/oauth_consent.html`
- Test: `tests/test_oauth_grants.py`

**Interfaces:**
- Consumes: `OAuthStore` 전체, `config`, `scripts.auth_routes.COOKIE_NAME`
- Produces: `register_oauth_grants(app, *, store=None, auth=None, cfg=None, consent_template="oauth_consent.html") -> None`

- [ ] **Step 1: 실패 테스트를 쓴다**

```python
"""scripts.mcp_remote.oauth_grants — authorize/token/revoke (Flask test client, 네트워크 0)."""
from __future__ import annotations

import base64
import hashlib
import shutil
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from flask import Flask

from scripts.auth_routes import COOKIE_NAME
from scripts.auth_store import AuthStore
from scripts.mcp_remote.oauth_grants import register_oauth_grants
from scripts.mcp_remote.oauth_store import OAuthStore

BASE = "https://aiskillbox.600g.net"
RESOURCE = BASE + "/mcp"
REDIRECT = "https://claude.ai/api/mcp/auth_callback"
VERIFIER = "a" * 64


def _challenge(verifier: str) -> str:
    d = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(d).rstrip(b"=").decode("ascii")


CFG = {"enabled": True, "public_base_url": BASE, "dynamic_registration": False,
       "allowed_origins": ["https://claude.ai"], "access_ttl_seconds": 3600,
       "refresh_ttl_seconds": 7776000}


class GrantsTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="oauth_grants_"))
        self.auth = AuthStore(self.dir / "auth.json")
        self.code = self.auth.create_code("테스트")
        self.token = self.auth.redeem(self.code, device="test")
        self.st = OAuthStore(self.dir / "oauth.json", auth_store=self.auth)
        self.cid, self.secret = self.st.create_client("Claude", [REDIRECT])
        app = Flask(__name__)
        app.config["TESTING"] = True
        register_oauth_grants(app, store=self.st, auth=self.auth, cfg=CFG,
                              consent_template=None)
        self.c = app.test_client()

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _authorize_qs(self, **over):
        q = {"response_type": "code", "client_id": self.cid, "redirect_uri": REDIRECT,
             "code_challenge": _challenge(VERIFIER), "code_challenge_method": "S256",
             "state": "xyz", "resource": RESOURCE, "scope": "skills:read"}
        q.update(over)
        return "&".join(f"{k}={v}" for k, v in q.items() if v is not None)

    def _login(self):
        self.c.set_cookie(COOKIE_NAME, self.token)   # Flask 3.x 시그니처

    def _get_code(self):
        self._login()
        r = self.c.post("/oauth/authorize?" + self._authorize_qs(), data={"approve": "yes"})
        self.assertEqual(r.status_code, 302)
        return parse_qs(urlparse(r.headers["Location"]).query)["code"][0]

    # ── authorize ──

    def test_unauthenticated_redirects_to_login_preserving_query(self):
        r = self.c.get("/oauth/authorize?" + self._authorize_qs())
        self.assertEqual(r.status_code, 302)
        loc = r.headers["Location"]
        self.assertIn("/login", loc)
        self.assertIn("code_challenge", loc)   # 쿼리스트링이 살아있어야 한다
        self.assertIn("state", loc)

    def test_authenticated_shows_consent(self):
        self._login()
        r = self.c.get("/oauth/authorize?" + self._authorize_qs())
        self.assertEqual(r.status_code, 200)

    def test_approve_issues_code_with_state(self):
        self._login()
        r = self.c.post("/oauth/authorize?" + self._authorize_qs(), data={"approve": "yes"})
        self.assertEqual(r.status_code, 302)
        q = parse_qs(urlparse(r.headers["Location"]).query)
        self.assertTrue(q["code"][0])
        self.assertEqual(q["state"][0], "xyz")

    def test_deny_redirects_with_access_denied(self):
        self._login()
        r = self.c.post("/oauth/authorize?" + self._authorize_qs(), data={})
        q = parse_qs(urlparse(r.headers["Location"]).query)
        self.assertEqual(q["error"][0], "access_denied")

    def test_redirect_uri_mismatch_does_not_redirect(self):
        self._login()
        r = self.c.get("/oauth/authorize?" + self._authorize_qs(
            redirect_uri="https://evil.example/cb"))
        self.assertEqual(r.status_code, 400)
        self.assertNotIn("Location", r.headers)   # 오픈 리다이렉터 방지

    def test_unknown_client_does_not_redirect(self):
        self._login()
        r = self.c.get("/oauth/authorize?" + self._authorize_qs(client_id="nope"))
        self.assertEqual(r.status_code, 400)
        self.assertNotIn("Location", r.headers)

    def test_plain_pkce_is_rejected(self):
        self._login()
        r = self.c.get("/oauth/authorize?" + self._authorize_qs(code_challenge_method="plain"))
        self.assertEqual(r.status_code, 400)

    def test_missing_pkce_is_rejected(self):
        self._login()
        r = self.c.get("/oauth/authorize?" + self._authorize_qs(code_challenge=None))
        self.assertEqual(r.status_code, 400)

    # ── token ──

    def test_token_exchange_succeeds(self):
        code = self._get_code()
        r = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE})
        self.assertEqual(r.status_code, 200)
        b = r.get_json()
        self.assertEqual(b["token_type"], "Bearer")
        self.assertEqual(b["scope"], "skills:read")
        self.assertTrue(b["access_token"] and b["refresh_token"])
        self.assertIsNotNone(self.st.validate_access(b["access_token"], resource=RESOURCE))

    def test_token_rejects_wrong_verifier(self):
        code = self._get_code()
        r = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": "b" * 64, "resource": RESOURCE})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["error"], "invalid_grant")

    def test_token_rejects_bad_client_secret(self):
        code = self._get_code()
        r = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": "wrong",
            "code_verifier": VERIFIER, "resource": RESOURCE})
        self.assertEqual(r.status_code, 401)

    def test_token_locks_after_repeated_bad_secrets(self):
        for _ in range(5):
            self.c.post("/oauth/token", data={"grant_type": "authorization_code",
                                              "client_id": self.cid, "client_secret": "wrong"})
        r = self.c.post("/oauth/token", data={"grant_type": "authorization_code",
                                              "client_id": self.cid,
                                              "client_secret": self.secret})
        self.assertEqual(r.status_code, 429)

    def test_code_reuse_revokes_all_grants_of_client(self):
        code = self._get_code()
        ok = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE}).get_json()
        again = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE})
        self.assertEqual(again.status_code, 400)
        self.assertIsNone(self.st.validate_access(ok["access_token"], resource=RESOURCE))

    def test_refresh_rotates(self):
        code = self._get_code()
        first = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE}).get_json()
        r = self.c.post("/oauth/token", data={
            "grant_type": "refresh_token", "refresh_token": first["refresh_token"],
            "client_id": self.cid, "client_secret": self.secret})
        self.assertEqual(r.status_code, 200)
        self.assertNotEqual(r.get_json()["refresh_token"], first["refresh_token"])

    def test_scope_narrowed_to_skills_read(self):
        self._login()
        r = self.c.post("/oauth/authorize?" + self._authorize_qs(scope="admin:all"),
                        data={"approve": "yes"})
        code = parse_qs(urlparse(r.headers["Location"]).query)["code"][0]
        b = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE}).get_json()
        self.assertEqual(b["scope"], "skills:read")

    # ── revoke ──

    def test_revoke_kills_token_and_returns_200_for_unknown(self):
        code = self._get_code()
        b = self.c.post("/oauth/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": self.cid, "client_secret": self.secret,
            "code_verifier": VERIFIER, "resource": RESOURCE}).get_json()
        r = self.c.post("/oauth/revoke", data={"token": b["access_token"],
                                               "client_id": self.cid,
                                               "client_secret": self.secret})
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(self.st.validate_access(b["access_token"], resource=RESOURCE))
        r2 = self.c.post("/oauth/revoke", data={"token": "unknown",
                                                "client_id": self.cid,
                                                "client_secret": self.secret})
        self.assertEqual(r2.status_code, 200)
```

- [ ] **Step 2: 실패를 확인한다**

Run: `venv/bin/python -m unittest tests.test_oauth_grants -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: 동의 화면 템플릿을 만든다**

`templates/oauth_consent.html`:

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>스킬 라이브러리 연결 승인</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", sans-serif;
           background: #0f1115; color: #e6e8ec; display: grid; place-items: center;
           min-height: 100vh; margin: 0; padding: 1.5rem; }
    .card { max-width: 26rem; width: 100%; background: #171a21; border: 1px solid #262b36;
            border-radius: 14px; padding: 1.75rem; }
    h1 { font-size: 1.15rem; margin: 0 0 1rem; }
    .who { font-weight: 600; color: #7dd3fc; }
    ul { padding-left: 1.1rem; line-height: 1.7; color: #aab2c0; }
    .row { display: flex; gap: .6rem; margin-top: 1.5rem; }
    button { flex: 1; padding: .8rem; border-radius: 9px; border: 0; font-size: .95rem;
             font-weight: 600; cursor: pointer; }
    .ok { background: #2563eb; color: #fff; }
    .no { background: #262b36; color: #aab2c0; }
    .fine { margin-top: 1rem; font-size: .78rem; color: #6b7280; line-height: 1.6; }
  </style>
</head>
<body>
  <div class="card">
    <h1><span class="who">{{ client_name }}</span> 이(가) 스킬 라이브러리 접근을 요청합니다</h1>
    <ul>
      <li>스킬 검색 및 목록 조회</li>
      <li>SKILL.md 본문 읽기</li>
    </ul>
    <form method="post" action="{{ action }}">
      <div class="row">
        <button class="no" type="submit" name="deny" value="1">거부</button>
        <button class="ok" type="submit" name="approve" value="yes">승인</button>
      </div>
    </form>
    <p class="fine">읽기 전용입니다 — 수집·삭제·수정 권한은 포함되지 않습니다.
       연결을 끊으려면 이 기기의 초대코드를 삭제하세요.</p>
  </div>
</body>
</html>
```

- [ ] **Step 4: 구현한다**

`scripts/mcp_remote/oauth_grants.py`:

```python
"""OAuth 2.1 grant 흐름 — authorize / token / revoke.

authorize 가 게이트 예외인 이유: 기존 _auth_gate 의 next 는 request.path 기반이라
쿼리스트링을 버린다. OAuth 파라미터가 전부 쿼리에 있으므로 여기서 full_path 를 보존해
직접 /login 으로 보낸다.
"""
from __future__ import annotations

import base64
import hashlib
import logging
import secrets
from typing import Optional
from urllib.parse import quote, urlencode

from flask import Flask, jsonify, redirect, render_template, request

from scripts import auth_store as auth_store_mod
from scripts.auth_routes import COOKIE_NAME
from scripts.mcp_remote import config as mcp_config
from scripts.mcp_remote import oauth_store as store_mod
from scripts.mcp_remote.guard import FailGuard

logger = logging.getLogger(__name__)

SCOPE = "skills:read"
LOGIN_PATH = "/login"
_GUARD = FailGuard()


def _pkce_ok(verifier: str, challenge: str) -> bool:
    if not verifier or not challenge:
        return False
    digest = hashlib.sha256(str(verifier).encode("ascii")).digest()
    computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return secrets.compare_digest(computed, str(challenge))


def _err_page(message: str, status: int = 400):
    """리다이렉트하지 않는 오류 — 오픈 리다이렉터 방지. 잠금(429)에도 쓴다."""
    return (f"<!doctype html><meta charset='utf-8'>"
            f"<p style='font-family:sans-serif;padding:2rem'>연결 실패: {message}</p>"), status


def register_oauth_grants(app: Flask, *, store=None, auth=None, cfg: Optional[dict] = None,
                          consent_template: Optional[str] = "oauth_consent.html") -> None:
    """store/auth/cfg/consent_template 은 테스트 주입용."""

    def _cfg() -> dict:
        return cfg if cfg is not None else mcp_config.load()

    def _store():
        return store if store is not None else store_mod.get_store()

    def _auth():
        return auth if auth is not None else auth_store_mod.get_store()

    def _client_from_form():
        cid = request.form.get("client_id", "")
        secret = request.form.get("client_secret") or None
        return cid, secret

    # ── authorize ────────────────────────────────────────────

    def _validate_authorize(c: dict):
        """(client, params) 또는 (None, 오류응답)."""
        q = request.args
        locked = _GUARD.check(q.get("client_id", "") or "anon")
        if locked:
            return None, _err_page(locked, 429)
        client = _store().get_client(q.get("client_id", ""))
        if client is None:
            _GUARD.fail(q.get("client_id", "") or "anon")
            logger.warning("authorize: 미등록 client_id=%r", q.get("client_id"))
            return None, _err_page("등록되지 않은 클라이언트입니다")
        redirect_uri = q.get("redirect_uri", "")
        if redirect_uri not in client["redirect_uris"]:
            _GUARD.fail(q.get("client_id", ""))
            logger.warning("authorize: redirect_uri 불일치 요청=%r 등록=%r",
                           redirect_uri, client["redirect_uris"])
            return None, _err_page("redirect_uri 가 등록값과 일치하지 않습니다")
        if q.get("response_type") != "code":
            return None, _err_page("response_type 은 code 여야 합니다")
        if q.get("code_challenge_method", "S256") != "S256" or not q.get("code_challenge"):
            return None, _err_page("PKCE S256 이 필요합니다")
        resource = q.get("resource") or mcp_config.resource_id(c)
        if resource != mcp_config.resource_id(c):
            return None, _err_page("resource 가 이 서버와 일치하지 않습니다")
        return client, {"redirect_uri": redirect_uri, "state": q.get("state", ""),
                        "code_challenge": q.get("code_challenge"), "resource": resource}

    def _invite_code_of_request() -> Optional[str]:
        """로그인 쿠키 → 그 세션을 발급한 초대코드 (grant 에 승인 주체로 박는다)."""
        token = request.cookies.get(COOKIE_NAME, "")
        if not token or not _auth().check_token(token):
            return None
        return _auth().code_of_token(token)   # Task 1 에서 추가함

    @app.get("/oauth/authorize")
    def oauth_authorize_get():
        c = _cfg()
        client, out = _validate_authorize(c)
        if client is None:
            return out
        if _invite_code_of_request() is None:
            nxt = quote(request.full_path.rstrip("?"), safe="")
            return redirect(f"{LOGIN_PATH}?next={nxt}")
        if consent_template is None:
            return "CONSENT", 200
        return render_template(consent_template, client_name=client["name"],
                               action=request.full_path.rstrip("?"))

    @app.post("/oauth/authorize")
    def oauth_authorize_post():
        c = _cfg()
        client, out = _validate_authorize(c)
        if client is None:
            return out
        invite = _invite_code_of_request()
        if invite is None:
            nxt = quote(request.full_path.rstrip("?"), safe="")
            return redirect(f"{LOGIN_PATH}?next={nxt}")
        params = out
        if request.form.get("approve") != "yes":
            q = {"error": "access_denied"}
            if params["state"]:
                q["state"] = params["state"]
            return redirect(params["redirect_uri"] + "?" + urlencode(q))
        code = _store().issue_code(
            client_id=request.args.get("client_id", ""), redirect_uri=params["redirect_uri"],
            code_challenge=params["code_challenge"], resource=params["resource"],
            scope=SCOPE, invite_code=invite)
        q = {"code": code}
        if params["state"]:
            q["state"] = params["state"]
        return redirect(params["redirect_uri"] + "?" + urlencode(q))

    # ── token ────────────────────────────────────────────────

    @app.post("/oauth/token")
    def oauth_token():
        c = _cfg()
        st = _store()
        cid, secret = _client_from_form()
        locked = _GUARD.check(cid or "anon")
        if locked:
            return jsonify({"error": "too_many_requests", "error_description": locked}), 429
        if not st.verify_client(cid, secret):
            _GUARD.fail(cid or "anon")
            return jsonify({"error": "invalid_client"}), 401
        _GUARD.ok(cid)
        grant_type = request.form.get("grant_type", "")

        if grant_type == "authorization_code":
            code = request.form.get("code", "")
            if st.code_was_seen(code):
                n = st.revoke_grants_of(cid)
                logger.warning("인가코드 재사용 감지 — client=%s grant %d건 폐기", cid, n)
                return jsonify({"error": "invalid_grant",
                                "error_description": "인가코드 재사용"}), 400
            g = st.consume_code(code)
            if g is None or g["client_id"] != cid:
                return jsonify({"error": "invalid_grant"}), 400
            st.mark_code_spent(code, cid)
            if g["redirect_uri"] != request.form.get("redirect_uri", ""):
                return jsonify({"error": "invalid_grant",
                                "error_description": "redirect_uri 불일치"}), 400
            if not _pkce_ok(request.form.get("code_verifier", ""), g["code_challenge"]):
                return jsonify({"error": "invalid_grant",
                                "error_description": "PKCE 검증 실패"}), 400
            req_resource = request.form.get("resource") or g["resource"]
            if req_resource != g["resource"]:
                return jsonify({"error": "invalid_target"}), 400
            access, refresh, ttl = st.issue_tokens(
                g, access_ttl=mcp_config.access_ttl(c), refresh_ttl=mcp_config.refresh_ttl(c))

        elif grant_type == "refresh_token":
            rotated = st.rotate_refresh(request.form.get("refresh_token", ""),
                                        access_ttl=mcp_config.access_ttl(c),
                                        refresh_ttl=mcp_config.refresh_ttl(c))
            if rotated is None:
                return jsonify({"error": "invalid_grant"}), 400
            access, refresh, ttl = rotated

        else:
            return jsonify({"error": "unsupported_grant_type"}), 400

        return jsonify({"access_token": access, "token_type": "Bearer", "expires_in": ttl,
                        "refresh_token": refresh, "scope": SCOPE})

    # ── revoke ───────────────────────────────────────────────

    @app.post("/oauth/revoke")
    def oauth_revoke():
        cid, secret = _client_from_form()
        if not _store().verify_client(cid, secret):
            return jsonify({"error": "invalid_client"}), 401
        _store().revoke(request.form.get("token", ""))
        return "", 200   # RFC 7009 — 알 수 없는 토큰도 200
```

- [ ] **Step 5: 통과를 확인한다**

Run: `venv/bin/python -m unittest tests.test_oauth_grants -v`
Expected: PASS (18건)

- [ ] **Step 6: 전체 회귀를 확인한다**

Run: `venv/bin/python -m unittest discover -s tests -t . 2>&1 | tail -5`
Expected: OK

- [ ] **Step 7: 커밋**

```bash
git add scripts/mcp_remote/oauth_grants.py templates/oauth_consent.html tests/test_oauth_grants.py
git commit -m "feat(mcp-remote): authorize/token/revoke + 동의 화면"
```

---

### Task 7: 앱 배선 + 게이트 예외 + CLI

**Files:**
- Create: `scripts/mcp_remote/cli.py`, `scripts/mcp_remote/__main__.py`
- Modify: `scripts/mcp_remote/__init__.py`, `scripts/auth_routes.py`, `app.py`
- Test: `tests/test_auth_routes.py` (게이트 예외 케이스 추가)

**Interfaces:**
- Produces: `scripts.mcp_remote.register_mcp_remote(app) -> None` — meta + grants + transport 를 한 번에 등록

- [ ] **Step 1: 게이트 예외 실패 테스트를 쓴다**

`tests/test_auth_routes.py` 의 기존 `AuthRoutesTest.setUp` 안 라우트 정의부에 아래를 추가한다:

```python
        @app.post("/mcp")
        def mcp():
            return jsonify({"ok": True})

        @app.get("/.well-known/oauth-authorization-server")
        def as_meta():
            return jsonify({"ok": True})

        @app.get("/oauth/authorize")
        def oauth_authorize():
            return "AUTHORIZE"
```

그리고 테스트 메서드를 추가한다:

```python
    def test_mcp_bypasses_gate(self):
        """/mcp 는 자체 Bearer 인증을 가지므로 게이트를 통과해야 한다."""
        r = self.client.post("/mcp", json={})
        self.assertEqual(r.status_code, 200)

    def test_well_known_bypasses_gate(self):
        r = self.client.get("/.well-known/oauth-authorization-server")
        self.assertEqual(r.status_code, 200)

    def test_oauth_path_bypasses_gate(self):
        r = self.client.get("/oauth/authorize")
        self.assertEqual(r.status_code, 200)

    def test_unrelated_path_still_gated(self):
        """예외 추가가 게이트를 넓히지 않았는지 — 회귀 가드."""
        r = self.client.get("/catalog")
        self.assertEqual(r.status_code, 302)
```

> 기존 `AuthRoutesTest` 는 test client 를 `self.client` 로 둔다 (확인함).

- [ ] **Step 2: 실패를 확인한다**

Run: `venv/bin/python -m unittest tests.test_auth_routes -v`
Expected: FAIL — `/mcp`, `/.well-known/...`, `/oauth/authorize` 가 302 로 리다이렉트됨

- [ ] **Step 3: 게이트 예외를 추가한다**

`scripts/auth_routes.py` 상단 상수를 고친다:

```python
# 게이트 없이 통과하는 경로 (정확 일치 or prefix)
# 여기 있는 경로는 전부 자체 인증을 가진다: /mcp=Bearer, /oauth/token=client secret+PKCE,
# /oauth/authorize=쿠키+동의, /.well-known/*=비밀 없는 공개 메타데이터.
_ALLOW_EXACT = {LOGIN_PATH, "/api/auth/redeem", "/api/auth/bootstrap", "/healthz", "/sw.js",
                "/favicon.ico", "/mcp"}
_ALLOW_PREFIX = ("/static/", "/oauth/", "/.well-known/")
```

- [ ] **Step 4: 통과를 확인한다**

Run: `venv/bin/python -m unittest tests.test_auth_routes -v`
Expected: PASS (기존 + 신규 4건)

- [ ] **Step 5: 배선과 CLI 를 만든다**

`scripts/mcp_remote/__init__.py`:

```python
"""aiskillbox 원격 MCP 커넥터 (OAuth 2.1 + Streamable HTTP).

app.py 가 register_mcp_remote(app) 한 줄로 등록한다.
설계: docs/superpowers/specs/2026-08-27-remote-mcp-oauth-design.md
"""
from __future__ import annotations

import logging

from flask import Flask

logger = logging.getLogger(__name__)


def register_mcp_remote(app: Flask) -> None:
    from scripts.mcp_remote import config as mcp_config
    from scripts.mcp_remote.oauth_grants import register_oauth_grants
    from scripts.mcp_remote.oauth_meta import register_oauth_meta
    from scripts.mcp_remote.transport import register_transport

    c = mcp_config.load()
    if not mcp_config.enabled(c):
        logger.info("mcp_remote 비활성 (config.json mcp_remote.enabled=false)")
        return
    register_oauth_meta(app)
    register_oauth_grants(app)
    register_transport(app)
    logger.info("원격 MCP 커넥터 등록 — resource=%s dcr=%s",
                mcp_config.resource_id(c), mcp_config.dynamic_registration(c))
```

`scripts/mcp_remote/cli.py`:

```python
"""python -m scripts.mcp_remote client create|list|delete — 수동 클라이언트 발급.

동적 등록을 끈 채로 커넥터를 붙일 때 쓴다. 발급된 client_id/secret 을 claude.ai
커넥터 추가 화면의 [Advanced settings] 에 넣는다. secret 은 이때 한 번만 보인다.
"""
from __future__ import annotations

import sys

from scripts.mcp_remote.oauth_store import get_store

USAGE = "사용법: python -m scripts.mcp_remote client create <이름> --redirect-uri <URL> [...] | list | delete <client_id>"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 2 or args[0] != "client":
        print(USAGE)
        return 1
    st = get_store()
    action = args[1]

    if action == "list":
        rows = st.list_clients()
        if not rows:
            print("등록된 클라이언트 없음")
            return 0
        for r in rows:
            print(f"{r['client_id']}  {r['name']:<20} [{r['source']}]  {r['created_at']}")
            for u in r["redirect_uris"]:
                print(f"    ↳ {u}")
        return 0

    if action == "create":
        rest = args[2:]
        name = rest[0] if rest and not rest[0].startswith("--") else "manual"
        uris = [rest[i + 1] for i, a in enumerate(rest) if a == "--redirect-uri" and i + 1 < len(rest)]
        if not uris:
            print("--redirect-uri 가 최소 하나 필요합니다")
            print(USAGE)
            return 1
        cid, secret = st.create_client(name, uris, source="manual")
        print(f"client_id     : {cid}")
        print(f"client_secret : {secret}   ← 지금만 보입니다. 저장해두세요")
        for u in uris:
            print(f"redirect_uri  : {u}")
        return 0

    if action == "delete":
        if len(args) < 3:
            print(USAGE)
            return 1
        ok = st.delete_client(args[2])
        print("삭제됨 (관련 토큰도 폐기)" if ok else "그런 client_id 없음")
        return 0 if ok else 1

    print(USAGE)
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

`scripts/mcp_remote/__main__.py`:

```python
import sys

from scripts.mcp_remote.cli import main

sys.exit(main())
```

- [ ] **Step 6: `app.py` 에 배선한다**

`app.py` 의 라이브러리 라우트 등록 블록 바로 뒤, `register_auth` 앞에 넣는다:

```python
# ── 원격 MCP 커넥터 (/mcp + OAuth 2.1) ────────────────────
# 등록 실패 시 /mcp 가 404 일 뿐 게이트에 구멍이 생기지 않으므로 try/except 가 안전하다.
try:
    from scripts.mcp_remote import register_mcp_remote
    register_mcp_remote(app)
except Exception as _mcp_err:  # noqa: BLE001
    log.warning("원격 MCP 커넥터 등록 실패 — /mcp 비활성: %s", _mcp_err)
```

- [ ] **Step 7: 컴파일 + 전체 테스트 + 기동을 확인한다**

```bash
python -m py_compile app.py scripts/mcp_remote/*.py scripts/auth_store.py scripts/auth_routes.py scripts/library/mcp_server.py
venv/bin/python -m unittest discover -s tests -t . 2>&1 | tail -5
launchctl kickstart -k "gui/$(id -u)/com.doogeun.aiskillbox"
sleep 3 && curl -s http://localhost:5050/healthz | python3 -m json.tool | head -5
```
Expected: 컴파일 오류 없음, 테스트 OK, healthz 응답.

- [ ] **Step 8: 로컬 엔드투엔드를 확인한다**

```bash
# 401 + 챌린지 헤더
curl -s -i -X POST http://localhost:5050/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"ping"}' | head -12

# 메타데이터 2종 — https 절대 URL 이어야 한다
curl -s http://localhost:5050/.well-known/oauth-protected-resource | python3 -m json.tool
curl -s http://localhost:5050/.well-known/oauth-authorization-server | python3 -m json.tool

# 동적 등록이 꺼져 있는지 (404 여야 정상)
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:5050/oauth/register \
  -H 'Content-Type: application/json' -d '{"redirect_uris":["https://claude.ai/cb"]}'
```
Expected: 401 + `WWW-Authenticate: Bearer resource_metadata="https://aiskillbox.600g.net/..."`, 메타데이터에 `http://` 없음, register 는 `404`.

- [ ] **Step 9: 커밋**

```bash
git add scripts/mcp_remote/ scripts/auth_routes.py app.py tests/test_auth_routes.py
git commit -m "feat(mcp-remote): 앱 배선 + 게이트 예외 + 클라이언트 CLI"
```

---

### Task 8: 실연결 + 문서

**Files:**
- Modify: `CLAUDE.md`, `README.md`

- [ ] **Step 0: 초대코드가 있는지 확인한다**

```bash
venv/bin/python -m scripts.auth_store list
```
코드가 하나도 없으면 authorize 단계에서 로그인할 수 없다. `venv/bin/python -m scripts.auth_store create "클로드앱"` 으로 하나 만들거나, `/login` 의 "관리자 첫 등록(PIN)" 으로 진입한다.

- [ ] **Step 1: PKCE 왕복을 실제로 돌려본다**

스크래치에 스크립트를 두고(레포에 커밋하지 않는다) 인가코드→토큰→`tools/call` 까지 한 번에 확인한다. `AISKILLBOX_COOKIE` 는 브라우저에서 꺼낸 `aiskillbox_auth` 값이다.

```bash
python3 - <<'PY'
import base64, hashlib, json, secrets, urllib.parse, urllib.request, os
BASE = "http://localhost:5050"
v = secrets.token_urlsafe(48)
ch = base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b"=").decode()
print("verifier :", v)
print("challenge:", ch)
print("authorize:", BASE + "/oauth/authorize?" + urllib.parse.urlencode({
    "response_type": "code", "client_id": os.environ["CID"],
    "redirect_uri": os.environ["REDIRECT"], "code_challenge": ch,
    "code_challenge_method": "S256", "state": "test",
    "resource": "https://aiskillbox.600g.net/mcp", "scope": "skills:read"}))
PY
```

브라우저로 authorize URL 을 열어 승인하고, 리다이렉트된 주소에서 `code` 를 꺼내 교환한다:

```bash
curl -s -X POST http://localhost:5050/oauth/token \
  -d grant_type=authorization_code -d code="$CODE" -d redirect_uri="$REDIRECT" \
  -d client_id="$CID" -d client_secret="$SECRET" -d code_verifier="$VERIFIER" \
  -d resource="https://aiskillbox.600g.net/mcp" | python3 -m json.tool
```

받은 access token 으로 도구를 실호출한다:

```bash
curl -s -X POST http://localhost:5050/mcp -H "Authorization: Bearer $ACCESS" \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 -m json.tool | head -20

curl -s -X POST http://localhost:5050/mcp -H "Authorization: Bearer $ACCESS" \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"search_skills","arguments":{"query":"토큰 절약","k":3}}}' \
  | python3 -m json.tool | head -30
```
Expected: 도구 3종 목록, 그리고 검색 결과 텍스트. `(로컬 인덱스 폴백 — 서버 미응답)` 문구가 **보이면 안 된다** (Task 2 의 `inproc` 태그가 제대로 걸렸는지 확인).

- [ ] **Step 2: 공개 URL 로 같은 확인을 한다**

```bash
curl -s -i -X POST https://aiskillbox.600g.net/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"ping"}' | head -12
curl -s https://aiskillbox.600g.net/.well-known/oauth-protected-resource | python3 -m json.tool
```
Expected: 401 + 챌린지, 메타데이터 정상. CF 가 막으면 여기서 멈추고 보고한다.

- [ ] **Step 3: 동적 등록을 잠깐 켠다**

```bash
python3 - <<'PY'
import json, pathlib
p = pathlib.Path("config.json"); d = json.loads(p.read_text(encoding="utf-8"))
d["mcp_remote"]["dynamic_registration"] = True
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("dynamic_registration = True")
PY
curl -s https://aiskillbox.600g.net/.well-known/oauth-authorization-server \
  | python3 -c "import json,sys; print('registration_endpoint' in json.load(sys.stdin))"
```
Expected: `True` (config 는 mtime 재적재라 서버 재시작 불필요)

- [ ] **Step 4: claude.ai 에 커넥터를 붙인다**

claude.ai → 설정 → 커넥터 → 커스텀 커넥터 추가 → `https://aiskillbox.600g.net/mcp` → OAuth 동의(초대코드 입력 → 승인) → 연결 확인.

- [ ] **Step 5: 등록 결과를 확인하고 토글을 되돌린다**

```bash
venv/bin/python -m scripts.mcp_remote client list
python3 - <<'PY'
import json, pathlib
p = pathlib.Path("config.json"); d = json.loads(p.read_text(encoding="utf-8"))
d["mcp_remote"]["dynamic_registration"] = False
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("dynamic_registration = False")
PY
curl -s -o /dev/null -w '%{http_code}\n' -X POST https://aiskillbox.600g.net/oauth/register \
  -H 'Content-Type: application/json' -d '{"redirect_uris":["https://x.example/cb"]}'
```
Expected: `client list` 에 Claude 가 자기 redirect_uri 와 함께 보이고, 되돌린 뒤 register 는 `404`.

- [ ] **Step 6: 클로드 앱에서 실사용을 확인한다**

폰 또는 웹 클로드에서: 스킬 검색 → `get_skill` 로 본문 수신 → **그 스킬을 적용해 md 산출**까지 한 번 돌려본다. 이게 이 작업의 최종 수용 기준이다.

- [ ] **Step 7: 문서를 갱신한다**

`CLAUDE.md` 의 "Common commands" 에 추가한다:

```bash
# 원격 MCP 커넥터 (claude.ai 웹/모바일/Cowork)
curl -s https://aiskillbox.600g.net/.well-known/oauth-protected-resource | python3 -m json.tool
venv/bin/python -m scripts.mcp_remote client list          # 붙어있는 커넥터
venv/bin/python -m scripts.mcp_remote client delete <id>   # 커넥터 끊기
#   커넥터 연결 = 초대코드에 묶임 → 초대코드 삭제하면 커넥터도 즉시 끊긴다
#   새 커넥터 붙일 때만 config.json mcp_remote.dynamic_registration 을 true 로 켰다가 되돌린다
```

`CLAUDE.md` 상단 "What this is" 에 한 줄 추가한다:

```
- **원격 MCP (v5.0)**: `POST /mcp` (Streamable HTTP) + OAuth 2.1 인가서버. claude.ai 웹·모바일·Cowork 에 커스텀 커넥터로 붙는다. 읽기 전용 3종 도구. 설계: `docs/superpowers/specs/2026-08-27-remote-mcp-oauth-design.md`
```

- [ ] **Step 8: 커밋**

```bash
git add CLAUDE.md README.md
git commit -m "docs: 원격 MCP 커넥터 운영 명령 + 연결 절차"
```

---

## 실행 순서 요약

| Task | 산출물 | 의존 |
|---|---|---|
| 1 | OAuth 저장소 + `has_code` | — |
| 2 | in-process 백엔드 시임 | — |
| 3 | 설정 모듈 + 무차별 대입 가드 | — |
| 4 | `POST /mcp` 전송 | 1, 2, 3 |
| 5 | 메타데이터 + 동적 등록 | 1, 3 |
| 6 | authorize/token/revoke | 1, 3 |
| 7 | 배선 + 게이트 예외 + CLI | 4, 5, 6 |
| 8 | 실연결 + 문서 | 7 |

Task 1·2·3 은 서로 독립이라 병렬 가능하다.
