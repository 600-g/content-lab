# aiskillbox 초대코드 로그인 (v4.6) + 노션 /p/ 오탐 수정 설계 (2026-08-22)

> 사용자 결정 (2026-08-22): **전체 잠금** (수집 UI + 카탈로그 + 검색 API 전부 로그인 필요) ·
> **코드 → 기기 토큰** (계정 없음, 코드 하나로 여러 기기, 코드 삭제 = cascade 로그아웃) ·
> **노션 app.notion.com/p/ 오탐도 같이 수정**. 두근컴퍼니 멀티유저 베타의 초대코드 패턴 축소 이식.

## 배경 / 목표

- aiskillbox 는 `aiskillbox.600g.net` 으로 공개인데 앱 자체 인증이 없다. `/api/collect` 는 완전 무인증 —
  누구든 URL 을 던져 LLM 쿼터를 태우고 dedup/합병으로 데이터를 오염시킬 수 있다. 설정/채팅만 PIN.
- v4.5 카탈로그·검색 API 는 수집 본문 전문을 서빙하므로, "내 자산 도서관" 성격상 초대 있어야 입장.
- 오너 UX: 코드 한 번 입력 → 그 기기 영구 자동로그인.

## 비목표 (YAGNI)

- 계정/역할/capability 없음 (두근컴퍼니식 사용자 DB 아님). 기기 = 익명 세션.
- 세션 만료 없음 (회수는 코드 삭제로만). OAuth/비밀번호 없음.
- company-hq 쪽 코드 변경 없음 (토큰 env 계약만 문서화).

## 1. 인증 저장소 — `scripts/auth_store.py` (신규, 표준 라이브러리만)

- 파일: `logs/auth.json` (0600, logs/ 는 gitignore). atomic write (tmp + os.replace), threading.Lock.
- 구조:
  ```json
  {
    "codes":    { "<code>": {"label": "폰", "created_at": "..."} },
    "sessions": { "<sha256(token)>": {"code": "<code>", "device": "...", "created_at": "...", "last_seen": "..."} }
  }
  ```
- **코드는 평문 저장** (설정창에서 재조회·복사 필요 — company-hq invite_codes.json 과 동일 판단, 0600 + 회수 가능).
  **토큰은 해시만 저장** (bearer 자격증명 — 유출면 auth.json 만으로 로그인 불가).
- 코드 형식: `DGN-XXXX-XXXX` (secrets, 대문자/숫자, 혼동 문자 I/O/0/1 제외).
- API: `create_code(label)` → code · `list_codes()` → [{code,label,created_at,sessions}] ·
  `delete_code(code)` → 삭제된 세션 수 (cascade) · `redeem(code, device)` → token | None ·
  `check_token(token)` → bool (last_seen 은 60초 스로틀로 갱신 — 요청마다 디스크 쓰기 방지).
- CLI: `python -m scripts.auth_store create [라벨] | list | delete <code>` (터미널 관리용).

## 2. 게이트 + 라우트 — `scripts/auth_routes.py` (신규)

`register_auth(app, pin_ok=..., request_pin=...)` 하나로 등록 (pin_ok 는 app.py 의 기존 `_pin_ok` 주입 —
무차별 대입 잠금 로직 재사용, 테스트에서는 가짜 주입).

### before_request 게이트
- 통과 (allowlist): `OPTIONS` 메서드(CORS preflight) · `/login` · `/api/auth/redeem` · `/api/auth/bootstrap`
  · `/healthz`(112 모니터·데일리 리포트가 사용) · `/static/*`(로그인 페이지 CSS/JS/아이콘) · `/sw.js`.
- 인증: 쿠키 `aiskillbox_auth` **또는** 헤더 `X-Auth-Token` → `auth_store.check_token`.
- 미인증: `/api/*` → 401 `{ok:false, error:"로그인 필요", need_login:true}` · 페이지 → `302 /login?next=<path>`.

### 엔드포인트
| | |
|---|---|
| `POST /api/auth/redeem {code, device?}` | 코드 검증 → 토큰 발급 + `Set-Cookie: aiskillbox_auth` (HttpOnly, SameSite=Lax, Max-Age 400일). 응답에 token 도 포함 (MCP/에이전트가 복사해 env 로 쓰는 용도). 실패 401. 무차별 대입: PIN 가드와 동일한 5회/5분 잠금 (자체 카운터) |
| `POST /api/auth/bootstrap {pin, device?}` | **첫 등록/복구** — ADMIN_PIN 검증(주입된 pin_ok → 기존 잠금 공유) → 코드 자동 생성("owner") + 즉시 redeem → 쿠키 + {code, token} 반환. 코드가 하나도 없어도 오너는 PIN 만으로 진입 가능 (닭-달걀 해소) |
| `GET/POST/DELETE /api/auth/codes[/<code>]` | 코드 목록/발급/삭제(cascade). 로그인 + **X-Admin-Pin 헤더** 이중 게이트 (설정 API 와 동일 규약) |
| `GET /login` | 로그인 페이지 렌더 (아래 §3) |

## 3. UI

- `templates/login.html` (신규, 픽셀 스타일 — style.css 재사용): 코드 입력 1칸 + [입장] →
  `/api/auth/redeem` → 성공 시 `next`(기본 `/`) 로 이동. 하단 접이식 "관리자 첫 등록" → PIN 입력 →
  `/api/auth/bootstrap` → 발급된 코드를 화면에 1회 표시(다른 기기용으로 복사 안내) 후 이동.
  IME Enter 이중 전송 가드 (chat.js 패턴).
- 설정창 (index.html + app.js, PIN 인증 뷰 안): "초대코드" 섹션 — 목록(코드·라벨·기기 수·[복사][삭제]) +
  [+ 새 코드] (라벨 입력). 삭제 확인 문구에 "이 코드로 로그인한 기기 N대가 로그아웃됩니다".

## 4. 에이전트 / MCP / CORS

- MCP `scripts/library/mcp_server.py`: env `AISKILLBOX_TOKEN` 있으면 모든 HTTP 요청에 `X-Auth-Token` 헤더.
  **401 응답이면 로컬 인덱스 폴백** (이 Mac 에선 토큰 없이도 계속 동작). 등록 예:
  `claude mcp add ... -e AISKILLBOX_URL=https://aiskillbox.600g.net -e AISKILLBOX_TOKEN=<redeem 응답의 token>`
- library CORS: `Access-Control-Allow-Headers: X-Auth-Token` 추가 (preflight 는 게이트 allowlist 의 OPTIONS 로 통과).
- 두근컴퍼니 에이전트(server-side fetch): `.env` 에 `AISKILLBOX_TOKEN` 넣고 헤더로 전달 — company-hq 쪽 작업은 별건.

## 5. 노션 `app.notion.com/p/` 오탐 수정

- 원인 (2026-08-21 분석 확정): `router.py:_notion_workspace_guard` 가 `app.notion.com` 도메인이면 무조건
  `notion_workspace_only` 사전 차단. 노션이 "링크 복사"를 `app.notion.com/p/<id>` **공개 공유 링크**로
  발급하기 시작하면서 (비로그인 렌더 실측: 본문 블록 57/5개, 2,119/1,939자) 가정이 깨짐.
- 수정: URL path 가 `/p/` 로 시작하면 가드 통과 → 일반 notion 스크랩 경로 (진짜 비공개는 v4.4.6 의
  DOM 실측 판별 `[data-block-id]` 0 + 안내 문구가 잡음). `/p/` 아닌 app.notion.com 경로는 기존대로 차단.
- 검증: 가드 단위 테스트 + 실패했던 프롬왓 링크 2건 scrape-only 실측 (수집 등록은 라이브 적용 후).

## 6. 에러 처리 / 엣지

- `auth.json` 파싱 실패 → 빈 저장소로 시작 + 경고 (bootstrap 으로 재진입 가능 — 잠김 사고 없음).
- ADMIN_PIN 미설정 → bootstrap 이 그 사유를 그대로 안내 (기존 `_pin_ok` 메시지).
- 카탈로그 딥링크 `#slug` 는 fragment 라 서버에 안 옴 — redirect 후 브라우저가 fragment 유지 (next 는 path만).
- redeem/bootstrap 실패 응답은 코드 존재 여부를 구분하지 않는 단일 문구 (코드 존재 탐지 방지).

## 7. 테스트 (unittest, 네트워크 0)

- `tests/test_auth_store.py`: 발급/목록/삭제 cascade/redeem/check, auth.json 에 토큰 원문 부재(해시만),
  파일 0600, 깨진 JSON 복구.
- `tests/test_auth_routes.py`: 미인증 API 401 · 페이지 302(/login?next=…) · allowlist 통과(login/healthz/static/OPTIONS) ·
  redeem 성공 → 쿠키로 통과 · 헤더 X-Auth-Token 통과 · bootstrap(PIN 성공/실패/잠금) · codes CRUD PIN 게이트 ·
  코드 삭제 후 해당 토큰 즉시 401.
- `tests/test_notion_guard.py`: `/p/` 통과 · 워크스페이스 경로 차단 · notion.site 무관.
- 실구동 스모크: 임시 포트 — 무인증 / → 302, /api/library/search → 401, bootstrap → 쿠키 → 전부 200, MCP 토큰 헤더.

## 8. 적용 (라이브)

`worktree-skill-library` 브랜치 (v4.5 위). merge + kickstart 후 첫 접속 → /login → "관리자 첫 등록(PIN)" →
자동 로그인 + 첫 코드 발급. 이후 다른 기기는 그 코드로 입장.
