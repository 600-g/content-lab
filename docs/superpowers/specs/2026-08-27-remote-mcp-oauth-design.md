# aiskillbox 원격 MCP 커넥터 — OAuth 2.1 + Streamable HTTP 설계 (2026-08-27)

> 사용자 결정 (2026-08-27): **읽기 전용 3종 도구** (search_skills / get_skill / list_skills) ·
> **동적 등록 + 수동 발급 둘 다 구현하고 config 토글로 제어** · **Flask 네이티브 최소 구현**
> (authlib 등 신규 의존성 없음, 별도 서비스 분리 없음) · 연결 검증과 claude.ai 커넥터 등록까지 수행.

## 배경 / 목표

- `scripts/library/mcp_server.py` 는 **stdio 전용**이다. stdio 는 로컬 프로세스를 띄울 수 있는
  클라이언트(Claude Code, Cursor, Codex)에서만 동작한다.
- claude.ai 웹·모바일·Cowork 의 커스텀 커넥터는 **원격 MCP(공개 URL)만** 받는다. 노션 커넥터가
  열리는 이유가 이것이고, 스킬박스가 안 열리는 이유도 이것이다.
- 목표: 폰·웹 클로드 앱에서 스킬 97개를 **검색해서 꺼내 읽고, 파악하고, 그 스킬을 적용해
  결과물(md·간단한 코드)을 만들 수 있게** 한다. 자세한 코딩은 Claude Code 가 계속 담당한다.
- 스킬 97개는 전부 단일 `SKILL.md` (부속 파일 0개)로 확인됨 → `get_skill(slug)` 이 frontmatter 포함
  전문을 반환하면 스킬 활용에 필요한 전부다. 번들 파일 전송 도구가 필요 없다.
- 부수 효과: claude.ai 커넥터로 붙으면 Claude Code 에도 `mcp__claude_ai_*` 로 자동 노출되어,
  기기마다 stdio 를 등록할 필요가 사라진다.

## 비목표 (YAGNI)

- **쓰기 도구 없음.** 수집(collect)·삭제·메타 수정은 커넥터에 넣지 않는다. 수집은 순차 큐 비동기
  작업이라 job_id 반환 + 폴링 설계가 따로 필요하고, 큐레이션은 이미 CLI batch(`curate_db`)가 있다.
  도구 추가는 나중에 `TOOLS` 배열에 10줄이면 된다.
- **스코프 1개** (`skills:read`). 역할·권한 분화 없음.
- **SSE 없음.** 도구 3종이 전부 즉답형이라 스트리밍할 내용이 없다.
- **세션 상태 없음** (stateless). `Mcp-Session-Id` 발급하지 않는다.
- **폐기 전용 UI 없음.** 초대코드 삭제가 곧 폐기다 (7절).
- stdio 진입점 제거하지 않음 — 같은 `handle()` 을 공유하므로 유지 비용이 0이고, 서버가 내려가도
  로컬 stdio 경로는 계속 동작한다.

## 1. 모듈 배치

```
scripts/mcp_remote/
├── __init__.py       register_mcp_remote(app) 하나만 노출
├── oauth_store.py    logs/oauth.json 저장소 (AuthStore 패턴 복제)
├── oauth_routes.py   메타데이터 · register · authorize · token · revoke
├── transport.py      POST /mcp  Streamable HTTP → mcp_server.handle()
└── cli.py            python -m scripts.mcp_remote client create|list|delete
templates/oauth_consent.html   동의 화면
```

한 파일 한 책임. `oauth_store` 는 Flask 를 import 하지 않는다 (표준 라이브러리만 → 테스트가 앱 없이 돈다).

## 2. OAuth 저장소 — `scripts/mcp_remote/oauth_store.py` (신규, 표준 라이브러리만)

- 파일: `logs/oauth.json` (0600, logs/ 는 gitignore). atomic write (tmp + os.replace), threading.Lock,
  mtime 기반 재적재 — `auth_store.py` 와 동일 규약.
- 구조:
  ```json
  {
    "clients": { "<client_id>": {"secret_hash": "sha256…|null", "redirect_uris": ["…"],
                                 "name": "Claude", "source": "dynamic|manual", "created_at": "…"} },
    "auth_codes": { "<sha256(code)>": {"client_id","redirect_uri","code_challenge","resource",
                                       "scope","invite_code","expires_at"} },
    "tokens":  { "<sha256(access)>":  {"client_id","resource","scope","invite_code","expires_at"} },
    "refresh": { "<sha256(refresh)>": {"client_id","resource","scope","invite_code","expires_at"} }
  }
  ```
- **비밀은 전부 해시만 저장** (client_secret · 인가코드 · access · refresh). 저장소가 유출돼도
  그것만으로는 어떤 자격증명도 재구성되지 않는다. `auth.json` 이 기기 토큰을 해시로만 두는 판단과 동일.
- 클라이언트 이름/`client_id`/`redirect_uris` 는 평문 — CLI 조회·디버깅용.
- API: `create_client(name, redirect_uris, *, source, public=False)` → (client_id, secret|None) ·
  `verify_client(client_id, secret)` → bool · `list_clients()` · `delete_client(client_id)` ·
  `issue_code(...)` → code · `consume_code(code)` → grant|None (1회용, 소비 즉시 삭제) ·
  `issue_tokens(grant)` → (access, refresh, expires_in) · `validate_access(token, resource)` → grant|None ·
  `rotate_refresh(token)` → (access, refresh)|None · `revoke(token)` · `revoke_grants_of(client_id)`.
- `auth_codes` 는 **인가코드**다. `auth.json` 의 `codes`(초대코드)와 다른 것이라 이름을 분리했다.
- 만료 항목은 접근 시점에 지연 정리(lazy sweep) — 별도 타이머 스레드 없음.

## 3. OAuth 라우트 — `scripts/mcp_remote/oauth_routes.py` (신규)

모든 절대 URL 은 `config.json` 의 `mcp_remote.public_base_url` 에서 만든다. **헤더로 추측하지 않는다** —
CF Tunnel 이 TLS 를 종단해서 Flask 는 자기를 http 로 보고, 메타데이터에 `http://` 가 한 번 새면
Claude 가 연결을 거부한다 (11절 함정).

### 3.1 메타데이터 (게이트 예외, 무인증 공개)

- `GET /.well-known/oauth-protected-resource` 및 `/.well-known/oauth-protected-resource/mcp` (RFC 9728)
  → `{"resource": "<base>/mcp", "authorization_servers": ["<base>"], "scopes_supported": ["skills:read"]}`
- `GET /.well-known/oauth-authorization-server` (RFC 8414)
  → issuer · authorization_endpoint · token_endpoint · revocation_endpoint ·
    `code_challenge_methods_supported: ["S256"]` · `grant_types_supported: ["authorization_code","refresh_token"]` ·
    `registration_endpoint` **은 동적 등록이 켜져 있을 때만 포함**.

### 3.2 동적 등록 토글 — `POST /oauth/register` (RFC 7591)

- `config.json` → `mcp_remote.dynamic_registration` (기본 **false**).
- false 일 때: `registration_endpoint` 를 메타데이터에서 빼고 이 경로는 **404**. 인터넷에 등록 창구가
  열리지 않는다.
- true 일 때: `redirect_uris` 를 받아 클라이언트를 만들고 표준 응답(client_id/client_secret) 반환.
  등록은 로그에 남기고, 등록 시도에 무차별 대입 가드를 건다.
- **운영 절차**: 최초 연결 때만 true 로 켠다 → Claude 가 자기 콜백 URL 을 스스로 등록 → 다시 false.
  수동 발급의 최대 함정(우리가 Claude 의 `redirect_uri` 를 미리 맞춰야 함)이 사라진다.
- 수동 경로도 유지: `python -m scripts.mcp_remote client create "claude.ai" --redirect-uri <URL>` 로
  발급한 client_id/secret 을 claude.ai 커넥터 추가 화면의 [Advanced settings] 에 넣는다.

### 3.3 `GET/POST /oauth/authorize` (게이트 예외 — 자체 로그인 처리)

- **게이트를 그대로 쓸 수 없다.** 기존 `_auth_gate` 는 `redirect(f"/login?next={quote(request.path)}")`
  로 보내는데 `request.path` 는 쿼리스트링을 버린다. OAuth 파라미터가 전부 쿼리에 있으므로
  이 경로는 예외로 두고 `request.full_path` 를 보존해 직접 리다이렉트한다.
- 흐름: 파라미터 검증(client_id · redirect_uri 정확 일치 · response_type=code · PKCE S256 필수 ·
  resource) → 쿠키 `aiskillbox_auth` 없으면 `/login?next=<authorize 전문>` → 복귀 후 동의 화면
  (`templates/oauth_consent.html`: 어떤 클라이언트가 무슨 스코프를 요구하는지 명시) → [승인] POST →
  인가코드 발급(60초·1회용) → `redirect_uri?code=&state=`.
- 스코프는 `skills:read` 하나뿐이다. 클라이언트가 다른 값을 요구하면 거부하지 않고
  `skills:read` 로 좁혀서 발급하고(스펙 허용), 실제 발급된 스코프를 토큰 응답에 명시한다.
- `redirect_uri` 불일치·미등록 client_id 는 **리다이렉트하지 않고** 자체 오류 페이지로 끝낸다
  (오픈 리다이렉터 방지). 거부된 `redirect_uri` 는 로그에 남겨 등록 디버깅을 쉽게 한다.

### 3.4 `POST /oauth/token`

- `grant_type=authorization_code`: client 인증 → 코드 소비(1회용) → `code_verifier` 를 S256 으로
  검증 → `redirect_uri` 동일성 확인 → `resource` 확인 → access(1시간) + refresh 발급.
- `grant_type=refresh_token`: 회전 발급(옛 refresh 즉시 폐기).
- **인가코드 재사용 감지 시 그 client 의 grant 전체를 폐기** (스펙 권고).
- 표준 오류 응답 형식(`{"error": "invalid_grant", ...}`) + 401/400 코드.

### 3.5 `POST /oauth/revoke` (RFC 7009)

access·refresh 어느 쪽이든 받아 폐기. 알 수 없는 토큰도 200 (스펙).

## 4. MCP HTTP 전송 — `scripts/mcp_remote/transport.py` (신규)

`POST /mcp` 단일 엔드포인트, **stateless**.

- `Authorization: Bearer` 없음/만료/audience 불일치 → `401` +
  `WWW-Authenticate: Bearer resource_metadata="<base>/.well-known/oauth-protected-resource"`.
  이 헤더가 claude.ai 의 OAuth 흐름을 시작시키는 방아쇠다.
- 본문 = JSON-RPC 메시지 → `mcp_server.handle(msg)`.
  - id 있는 요청 → `200 application/json` 단건 응답
  - 알림·응답(id 없음) → `202 Accepted`, 본문 없음
  - 배열(배치) 입력도 각 메시지를 처리해 응답 배열 반환
- `GET /mcp` → `405` (서버 발신 스트림 미지원).
- `Origin` 헤더 검증 — 허용 목록 밖이면 403 (DNS rebinding 차단).
- `MCP-Protocol-Version` 협상은 기존 `handle()` 의 `initialize` 가 이미 처리하므로 건드리지 않는다.

## 5. 기존 코드 변경점 (4군데뿐)

1. `app.py` — 라이브러리 라우트와 같은 try/except 패턴으로 `register_mcp_remote(app)` 한 줄.
   등록이 실패하면 `/mcp` 가 404 일 뿐 구멍이 생기지 않으므로 try/except 가 안전하다
   (게이트 등록이 의도적으로 try/except 없이 된 것과는 성격이 다르다).
2. `scripts/auth_routes.py` — 게이트 예외에 `/mcp` 추가(`_ALLOW_EXACT`), `/oauth/`·`/.well-known/`
   추가(`_ALLOW_PREFIX`). 예외 경로는 전부 자체 인증을 가진다 (8절).
3. `scripts/library/mcp_server.py` — **`handle()` 시그니처 불변.** in-process 로 쓸 때 `_http_get` 이
   자기 자신(localhost:5050)을 다시 때리는 자기호출 루프가 생기므로 `use_local_backend()` 시임을
   추가해 직접 import 경로로 고정한다. 같은 프로세스라 검색 인덱스가 공유되어 이중 적재도 없다.
4. `config.json` — `mcp_remote` 블록 (6절).

## 6. 설정 — `config.json`

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

## 7. 폐기 모델 — 새 개념을 만들지 않는다

모든 grant 에 그것을 승인한 `invite_code` 를 박아두고, **토큰 검증 때마다 그 코드가 `auth.json` 에
아직 있는지 확인한다** (지연 검증). 결과:

- 초대코드 삭제 = 그 코드로 붙은 커넥터도 즉시 죽음. 기존 "코드 삭제 = 그 코드 기기 전부 로그아웃"
  cascade 와 정확히 같은 멘탈 모델이 된다.
- `auth_store` ↔ `oauth_store` 순환 import 나 삭제 훅 배선이 필요 없다 (oauth_store 가 auth_store 를
  단방향으로 읽기만 한다).
- 폐기 전용 UI 를 만들 필요가 없다.

## 8. 보안 경계

- 게이트 예외 경로는 **전부 자체 인증을 가진다**: `/mcp` = Bearer, `/oauth/token` = client secret + PKCE,
  `/oauth/authorize` = 쿠키 + 명시적 동의, `/.well-known/*` = 공개 메타데이터(비밀 없음),
  `/oauth/register` = 토글 off 면 존재하지 않음.
- PKCE S256 **필수** (plain 거부). `resource` (RFC 8707) 를 검증해 토큰을 `<base>/mcp` 에 바인딩 —
  토큰이 새도 다른 리소스에 재사용 불가.
- 인가코드 60초·1회용, 재사용 감지 시 grant 전체 폐기. refresh 회전 + 재사용 감지.
- `/oauth/token`·`/oauth/authorize`·`/oauth/register` 에 기존 `_RedeemGuard` 와 같은 파라미터
  (5회 실패 → 5분 잠금) 의 무차별 대입 가드.
- 오픈 리다이렉터 방지: `redirect_uri` 는 등록값과 **정확 일치**만 허용, 불일치 시 리다이렉트 안 함.
- 도구가 읽기 전용 3종이라 최악의 경우에도 피해 상한이 "스킬 조회" 다.

## 9. 테스트 (기존 관례: unittest, 네트워크 0)

- `tests/test_oauth_store.py` — 클라이언트 생성/검증, 코드 1회용·만료, 토큰 해시 저장 확인,
  refresh 회전, **초대코드 삭제 시 지연 폐기**, 만료 지연 정리.
- `tests/test_oauth_routes.py` — 메타데이터 형태와 https 절대 URL, 토글 on/off 시
  `registration_endpoint` 유무 + `/oauth/register` 404, PKCE 정답/오답, `redirect_uri` 불일치 거부,
  resource 바인딩, authorize 미로그인 시 next 에 쿼리 보존, 인가코드 재사용 시 grant 폐기.
- `tests/test_mcp_transport.py` — initialize / tools/list / tools/call 왕복, 무토큰 401 +
  `WWW-Authenticate` 헤더 내용, 알림 202, GET 405, Origin 거부, 배치 요청.
- `tests/test_mcp_server.py` — 기존 테스트가 그대로 통과하는지 회귀 (`handle()` 불변 확인).

## 10. 연결 절차 (운영)

1. `python -m py_compile` + `venv/bin/python -m unittest discover -s tests -t .`
2. `launchctl kickstart -k "gui/$(id -u)/com.doogeun.aiskillbox"`
3. 서버 검증 (브라우저 없이 curl): `POST /mcp` 무토큰 → 401 + 헤더 확인 → 메타데이터 2종 →
   테스트 클라이언트 발급 → PKCE 토큰 교환 → `tools/list` + `search_skills` 실호출.
4. `dynamic_registration: true` 로 전환 → claude.ai 설정 → 커넥터 → 커스텀 커넥터 추가에
   `https://aiskillbox.600g.net/mcp` → OAuth 동의(초대코드) → 연결.
5. 등록된 `redirect_uri` 를 CLI 로 확인한 뒤 `dynamic_registration: false` 로 복귀.
6. 클로드 앱에서 스킬 검색 → SKILL.md 수신 → 스킬 적용해 md 산출까지 실사용 확인.

## 11. 함정 노트 (구현 시 반드시 지킬 것)

- **http 누출**: CF Tunnel 이 TLS 를 종단하므로 `request.url_root` 는 `http://` 를 준다. 메타데이터·
  `WWW-Authenticate`·issuer 의 모든 절대 URL 은 `public_base_url` 에서만 만든다.
- **자기호출 루프**: in-process transport 에서 `mcp_server` 가 HTTP 백엔드를 쓰면 자기 서버를 다시
  때리고, 게이트에 막혀 401 을 받는다. 반드시 `use_local_backend()`.
- **쿼리 유실**: 게이트의 `next` 는 `request.path` 기반이라 OAuth 파라미터를 버린다. authorize 는
  게이트 예외 + `full_path` 보존.
- **등록 순서는 함정이 아니다**: `app.py` 에서 게이트가 마지막에 등록되지만, 라우트 등록 순서는
  `before_request` 게이트 동작에 영향을 주지 않는다. `/mcp` 가 통과하는 유일한 조건은 **게이트
  allowlist 에 경로가 들어가 있는 것**이다. 연결이 안 될 때 등록 순서를 의심하지 말 것.
- **초대코드 없는 상태**: 코드가 하나도 없으면 authorize 에서 로그인 불가 →
  `/login` 의 "관리자 첫 등록(PIN)" 으로 먼저 코드를 만든다.
