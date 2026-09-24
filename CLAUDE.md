# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 먼저 알 것

1. **스킬의 원본은 `skills/{slug}/SKILL.md` 파일 그 자체다.** 편집 엔드포인트는 없다 — 고치려면 파일을 고친다. mtime 감지로 검색·카탈로그·MCP 에 재시작 없이 반영된다.
2. **테스트는 unittest** — `venv/bin/python -m unittest discover -s tests -t .`. ★ pytest 는 venv 에 없다. 규칙은 **네트워크 0 · 디스크 부작용 0**.
3. **코드를 고쳤으면 `launchctl kickstart -k "gui/$(id -u)/com.doogeun.aiskillbox"`.** `app.run(debug=False)` 라 자동 리로드가 없다. dev 는 `AISKILLBOX_PORT=5051 venv/bin/python app.py` (5050 은 launchd 가 쥐고 있다).
4. **사이트는 초대코드로 전체 잠금이다.** `/healthz`·`/mcp`·`/oauth/*` 외 모든 `/api/*` 는 무토큰이면 401 이 정상 — curl 은 `-H "X-Auth-Token: $TOKEN"`. 예외 목록의 단일 진실은 `scripts/auth_routes.py:_ALLOW_EXACT` (여기에 베끼지 않는다).
5. **로그는 `logs/launchd_stderr.log`** (수십 MB 무로테이션, ANSI 이스케이프 혼입). stdout 은 기동 배너뿐. 커넥터 생사 진단 1순위는 `grep -a "POST /oauth/token" logs/launchd_stderr.log | tail`.
6. **grep 할 때 `.claude/worktrees/`(v4.5 시절 전체 사본)·`venv/`·`__pycache__` 를 제외할 것** — 안 하면 옛 코드가 현행으로 잡힌다.
7. **문서보다 코드가 단일 진실인 것**: 본문 섹션(`scripts/analyzer/prompt.py:ALLOWED_HEADINGS`) · 게이트 예외(`auth_routes.py:_ALLOW_EXACT`) · MCP 도구(`scripts/library/mcp_server.py:TOOLS`) · enum(`analyzer/prompt.py` + `notion_client/register.py`). 이 문서가 목록을 들고 있던 동안 코드가 바뀐 적이 세 번이다.
8. **명령어는 전부 `venv/bin/python`** — 이 맥에 bare `python` 이 없다.

## What this is

**aiskillbox** — URL 한 줄 또는 붙여넣은 텍스트 → 스크래핑 → AI 분석 → `SKILL.md` 자동 생성 → 글로벌(`~/.claude/skills/`) + mirror(`skills/`) 설치 → **스킬 라이브러리**에 즉시 등재(검색 API · 카탈로그 · MCP). 제출은 순차 큐, 완료 시 Web Push.

- 사람이 보는 곳: https://aiskillbox.600g.net (`/catalog` 게시판, `/skill/<slug>` 게시글). Local: http://localhost:5050 (launchd `com.doogeun.aiskillbox`, Cloudflare Tunnel token-mode)
- AI 가 보는 곳: `GET /api/library/search?q=` · stdio MCP(`scripts/library/mcp_server.py`, Claude Code 용) · 원격 MCP(`POST /mcp` + OAuth 2.1, claude.ai 웹·모바일·Cowork 용). **읽기 전용 3종 도구**(`search_skills`/`get_skill`/`list_skills`).
- Notion 등록은 옵션(`config.json notion.register_on_collect`, 기본 **off**). 켤 때만 `docs/notion-migration.md`.

설계 스펙은 `docs/superpowers/specs/` (`ls` 로 확인). 릴리스 이력은 `docs/CHANGELOG.md` 와 `git log --oneline`.

## Common commands

```bash
# venv 는 aiskillbox_start.sh 가 첫 실행 때 만든다. 손으로 할 때만:
python3 -m venv venv && venv/bin/pip install -r requirements.txt && venv/bin/playwright install chromium

# 수집
venv/bin/python -m scripts.collect "https://youtu.be/<id>"
venv/bin/python -m scripts.collect "<URL>" --skip-duplicate          # 중복 시 합병 안 하고 스킵
venv/bin/python -m scripts.collect --text-file ./본문.md --title "제목"   # 스크랩 불가 출처 (최소 200자)
pbpaste | venv/bin/python -m scripts.collect --text -

# 컴파일 사전 검증 (변경 후 항상). bash 는 ** 를 재귀 확장하지 않는다 — find 로.
find scripts -name '*.py' -not -path '*/__pycache__/*' -print0 | xargs -0 venv/bin/python -m py_compile app.py

# 서비스
launchctl kickstart -k "gui/$(id -u)/com.doogeun.aiskillbox"
launchctl load -w ~/Library/LaunchAgents/com.doogeun.aiskillbox.plist
grep -a "AI 분석 완료\|Claude 한도\|Jina" logs/launchd_stderr.log | tail -20   # tail -f 보다 이게 기본 (수십 MB)

# 테스트 — unittest 전용 (★ pytest 없음). 네트워크 0 · 수 초
venv/bin/python -m unittest discover -s tests -t .
venv/bin/python -m unittest tests.test_mcp_transport -v
venv/bin/python -m unittest tests.test_mcp_transport.TransportTest.test_bad_token_is_401

# 라이브러리 — 토큰부터 발급 (게이트 안이라 없으면 401)
TOKEN=$(venv/bin/python -c 'from scripts.auth_store import get_store;s=get_store();print(s.redeem(s.create_code("로컬 작업")))')
curl -s -H "X-Auth-Token: $TOKEN" "localhost:5050/api/library/search?q=인스타+릴스&k=5" | python3 -m json.tool
curl -s -H "X-Auth-Token: $TOKEN" "localhost:5050/api/library/skills/<slug>?format=raw"
venv/bin/python -m scripts.library search "토큰 절약" -k 5     # ★ .env 를 안 읽는다 — venv 활성화 없이 돌리면 키워드만 (gotcha 42)
venv/bin/python -m scripts.library stats
venv/bin/python -m scripts.library build-catalog --out logs/catalog.html
venv/bin/python -m scripts.library.repair sources            # 이중 출처 점검 (dry-run) · --apply 로 수선. mirror + 글로벌 동시, 멱등
venv/bin/python -m scripts.library.regrade                   # 등급 재판정 — dry-run 기본, --apply --recategorize 로 적용
venv/bin/python -m scripts.library.consolidate --dry-run <keeper> <absorbed>   # ⚠️ 이건 반대로 적용이 기본이다 — 먼저 --dry-run
venv/bin/python -m scripts.library.consolidate <keeper> <absorbed>             #    absorbed 를 즉시 rmtree (백업 logs/backup_consolidate_*)

# stdio MCP 를 Claude Code 에 붙일 때 — 토큰 없으면 401 → 로컬 인덱스로 조용히 폴백한다 (결과는 나오니 눈치채기 어렵다)
claude mcp add --scope user skill-library -e AISKILLBOX_TOKEN="$TOKEN" -- python3 ~/Developer/my-company/content-lab/scripts/library/mcp_server.py
#   외부 기기는 -e AISKILLBOX_URL=https://aiskillbox.600g.net 추가. 폴백 여부는 검색 결과 헤더("의미검색 포함" 이면 정상)

# 초대코드 (삭제 = 그 코드로 붙은 기기·커넥터 전부 즉시 로그아웃)
venv/bin/python -m scripts.auth_store create "폰" && venv/bin/python -m scripts.auth_store list
# 전 기기 로그아웃 복구: /login → "관리자 첫 등록" 에 ADMIN_PIN

# 원격 MCP 커넥터 (claude.ai)
venv/bin/python -m scripts.mcp_remote client list
grep -a "POST /oauth/token" logs/launchd_stderr.log | tail -5              # ★ 생사 1순위 — 갱신이 오면 살아있다
grep -a "POST /mcp" logs/launchd_stderr.log | grep -a '" 401 ' | tail -5   # 401 뒤에 /oauth/token 이 안 오면 진짜 단절, 요청 자체가 없으면 idle
venv/bin/python -m scripts.mcp_remote client create "Claude" \
  --redirect-uri https://claude.ai/api/mcp/auth_callback --redirect-uri https://claude.com/api/mcp/auth_callback
#   ★ dynamic_registration 은 켜지 말 것 — 켜는 동안 누구나 등록 가능, 상한 없음. 위 수동 발급이 정식 경로.
#     secret 은 이때 한 번만 보인다 → claude.ai 커넥터 추가 화면 [고급 설정] 에 넣는다.

# 헬스 (version 은 app.py 하드코딩 — grep -n '"version"' app.py 로 확인, 릴리스마다 손으로 올린다)
curl -s localhost:5050/healthz | python3 -m json.tool

# 푸시 확인 — 스킬과 코드의 유일본이 이 맥에 있다
git status --short && git log --oneline origin/main..HEAD
```

## High-level architecture

### 요청 조립과 게이트

게이트는 `before_request` **하나**(`auth_routes.py`)라 등록 순서와 무관하게 전 라우트에 걸린다. `/catalog`·`/skill/<slug>`·`/api/library/*` 는 **전부 게이트 안**이다 (`library/routes.py` 의 docstring "공개 API" 는 v4.6 이전 stale). chat/library/mcp_remote 는 try/except 로 등록하지만 **`register_auth` 만 의도적으로 무보호** — 게이트 실패 시 무보호로 뜨는 대신 기동 실패(healthz 죽음 → 112 감지)가 낫다.

### 데이터 흐름 (collect.py 한 사이클)

```
URL (CLI / 웹 / Telegram)                      텍스트 붙여넣기 (웹 [✍️ 텍스트] 탭 / CLI --text)
  ↓                                              ↓
scripts/scraper/router.py                      scripts/scraper/plain_text.py (스크랩 생략, paste://<sha16>)
  IG embed 선행 → 사전차단 2종 → 전용 스크래퍼 → Playwright×2 → requests → Jina 4단
  각 결과를 pick_best() 로 겨룬다 (임계 미달 ≠ 부재, gotcha 38). MIN_TEXT_LEN=500 (env SCRAPER_MIN_TEXT_LEN)
  ↓ ScrapeResult
scripts/analyzer/media_understand.py ── meta["media"] 가 있을 때만. 영상 → Gemini Files API, 슬라이드 → Claude(Read) → Gemini, 유튜브 → URL
  ↓ (500자 게이트는 이 뒤)
scripts/analyzer/gemini.py:analyze ── Claude Sonnet 5(claude -p) → Gemini Flash → Flash Lite → Gemma(로컬)
  ↓ AnalysisResult
중복 5단 사다리 (collect.py ~380-431) — 순서가 곧 안전장치, 오합병 사고 3건의 방어가 전부 여기 있다:
  ① 글로벌 슬러그 + _lab_origin 가드(非 content-lab 이면 _next_free_slug 로 회피)
  ② mirror 슬러그  ③ _sources_contain 미스면 GENERIC_SLUGS 차단 + _confirm_semantic_merge LLM 게이트
  ④ mirror frontmatter sources 일치(installer.py — 본문 스캔 아님)  ⑤ 임베딩 dedup + 같은 LLM 게이트
  → 있으면 analyzer/merger.py 합병
  ↓
scripts/skill_builder/md_generator.py ── frontmatter 6키 + 자유 본문. 본문 속 `## 출처` 는 _strip_source_section 이 뗀다 (출처는 frontmatter sources 가 단일 진실)
  ├─ ~/.claude/skills/{slug}/SKILL.md   (글로벌 ECC)
  └─ ./skills/{slug}/SKILL.md            (mirror = 라이브러리 원본. 저장 즉시 검색·카탈로그·MCP 에 반영)
  ↓ (config notion.register_on_collect=true 일 때만) notion_client/register.py
  ↓ (등록 성공 시에만) scripts/sync_hub.py — best-effort
```

### LLM 폴백 — 분석과 채팅이 **반대 방향**이다

- **분석(`analyzer/gemini.py:analyze` · `claude_cli.py`)**: Claude Sonnet 5(`claude -p`, 구독·과금 X) → Gemini 2.5 Flash(20/day, company-hq 와 키 공유) → Flash Lite(20/day) → Gemma 4(Ollama, 무제한, cold start 20-90s). 한도 메시지 → 30분 쿨다운(`analyzer.claude_cooldown_minutes`). 스위치 `config.json analyzer.claude_enabled`(mtime 재적재) · 긴급 env `ANALYZER_CLAUDE=0`. 어느 LLM 이 만들었는지는 잡 summary `stages.analyze.provider`.
- **채팅(`chat/engine.py`)**: `.env` 에 `ANTHROPIC_API_KEY` 가 있으면 **anthropic(과금 API, opus-4-8) 이 먼저** → claude_cli(구독, opus-5) → ollama. **delta 스트리밍·`--resume` 대화 기억은 claude_cli 전용** — anthropic 이 잡히면 status/tool/done 만 흐르고 앞 턴을 기억하지 못한다. 구독 강제는 `config.json chat.provider="claude_cli"`.
- 같은 폴백 패턴이 `analyzer/merger.py` 와 `library/regrade.py` 에도 있다 (`library/consolidate.py` 는 merger 를 경유). 등급 rubric 은 `analyzer/prompt.py` 와 `library/regrade.py` 두 곳에 **같은 문장** — 어긋나면 안 된다.

### 검색·인덱싱 — 캐시가 4겹이다

- **인덱스**(`library/index.py`): `skills/*/SKILL.md` → frozen 레코드. 무효화 키는 `f"{파일수}-{mtime 초}-{슬러그 디렉터리명 crc32}"` — **본문 내용은 키에 없다.** `cp -p` 복원이나 같은 초 안의 연속 수정은 감지되지 않는다 → `get_index(force=True)` 또는 재기동.
- **검색**(`library/search.py`): 한글 2-gram BM25(title×3/desc×2/meta×1.5/body×1) + `scripts/skills/embeddings.json` 코사인 + RRF 융합. 임베딩 실패는 키워드만으로 강등되고 응답 `semantic_skip_reason` 에 사유가 실린다.
- **질의 임베딩은 `@lru_cache`** — **실패(None)도 캐시된다.** 키를 고쳐도 같은 검색어로는 프로세스 수명 내내 키워드만이다. 검증은 다른 검색어로 하거나 재기동.
- **임베딩 호출은 Gemini 쿼터 게이트 밖이다.** `logs/gemini_quota.json` 게이트는 generateContent 전용. 사이트·MCP·채팅 검색이 **질의마다 embedContent 1콜**을 공유 키로 태운다 (`embedder.py` 는 429 면 WARNING 한 줄 + None).

### 원격 MCP ↔ stdio MCP — 같은 핸들러다

`mcp_remote/transport.py` 가 등록 시점에 `mcp_server.use_local_backend()` 로 `_FORCE_LOCAL` 을 세우고, `POST /mcp` 는 stdio 와 **같은 `handle()`** 을 재사용한다. **도구를 하나 추가하면 로컬 stdio MCP 와 claude.ai 커넥터에 동시에 노출된다** — "로컬에만" 은 없다. 도구 목록의 단일 진실은 `mcp_server.py:TOOLS`.

- `AISKILLBOX_URL` 이 없으면(현재 `.env` 에 없음) 검색 결과 텍스트의 `{BASE_URL}/skill/<slug>` 가 **localhost** 로 나간다 — 폰에서 링크를 눌러 보기 전엔 안 드러난다.
- `config.json mcp_remote.enabled` 만 핫리로드 예외 — `enabled=false` 면 **라우트를 아예 안 만든다**(모듈 레벨 1회). off→on 은 kickstart. `dynamic_registration`·`allowed_origins`·TTL 은 요청마다 다시 읽힌다.
- `register_mcp_remote(app)` 는 `app.py` 가 모듈 레벨에서 **1회** 호출 — 그 1회가 FailGuard 지역화의 전제다(여러 번 부르면 잠금이 리셋된다).
- **모든 절대 URL 은 `config.json mcp_remote.public_base_url` 에서만** 만든다. CF Tunnel 이 TLS 를 종단해 Flask 는 자기를 http 로 보므로 `request.url_root` 를 쓰면 `http://` 가 새고 Claude 가 연결을 거부한다. `load()` 가 https 아닌 값을 캐시 갱신 전에 `ValueError` 로 거부한다 (gotcha 46).

### 원격 MCP 커넥터가 끊기는 이유 (전수)

커넥터는 **액세스 토큰 1시간 / 리프레시 토큰 90일** 로 돈다. 90일은 카운트다운이 아니라 **"90일 연속 미사용" 타이머**다 — `rotate_refresh` 가 갱신 때마다 리프레시를 새로 발급하며 만료를 다시 90일 뒤로 민다. 절대 상한은 없다. 이 TTL(`config.json mcp_remote.refresh_ttl_seconds`)이 하는 일은 "방치된 커넥터를 언제 끊을까" 하나뿐이니 늘릴 이유가 없다. 진단은 항상 `grep -a "POST /oauth/token" logs/launchd_stderr.log | tail` 부터. **갱신 요청이 오고 있으면 커넥터는 살아있다.**

| # | 원인 | 증상 | 대응 |
|---|---|---|---|
| 1 | **초대코드 삭제** (설계된 폐기 경로) | 즉시 전부 401. `client list` 엔 남아있음 | 의도한 것. 되살리려면 재연결 |
| 2 | **`client delete`** | 즉시 401, `client list` 에서 사라짐 | 재발급 후 재연결 |
| 3 | **90일 연속 미사용** | 조용히 401 | 재연결. 실사용 중엔 해당 없음 |
| 4 | **claude.ai 가 갱신을 멈춤** — 만료 액세스 토큰으로 1~2회 401 만 받고 `/oauth/token` 을 안 침 | 서버·터널·초대코드·리프레시 다 정상인데 401 반복, 갱신 요청 **뚝 끊김** | 401 챌린지의 `error="invalid_token"`(RFC 6750) 누락이 원인이었고 2026-09-14 수정 후 401 은 0건. 재발 시 `mcp_health.py` 가 `AUTH_STUCK` 으로 잡아 자가 복구(헤더 회귀면 재시작 + 만료 토큰 청소) → 실패 시에만 알림. 그래도 안 되면 claude.ai 설정에서 재연결 |
| 5 | **커넥터를 지웠다가 재추가** | 추가 화면에서 실패 | `dynamic_registration:false` 라 `/oauth/register` 가 404. 위의 수동 발급 경로로 |
| 6 | **FailGuard 잠금** | 올바른 secret 인데 429 | client_id 당 5회 실패 → 300초. 기다리면 풀림 |
| 7 | **서버/터널 다운** | 401 아니라 502·타임아웃 | `claude_112.sh` 가 자동 복구 |

**4번이 위험한 이유**: 모든 헬스체크를 통과한다 (2026-09-03 → 09-05 이틀 방치). 감시는 `~/claude_guard/mcp_health.py` 가 한다 (`claude_112.sh` 5번 항목이 7분마다 호출, 2026-09-24 재작성). 종전의 "액세스 토큰 N시간째 갱신 없음" 기준은 **고장이 아니라 안 쓴 것**을 재고 있었다 — claude.ai 는 커넥터를 쓸 때만 갱신하므로 자거나 다른 일 하면 무조건 걸렸고, 매일 오던 "재연결 필요" 가 전부 오탐이었다. 지금 판정은 `GRANT_EXPIRED`(사람이 재연결) → `AUTH_STUCK`(**`/mcp` 401 연속 + 뒤따르는 `/oauth/token`·200 없음** — 챌린지 헤더 자가점검·만료 토큰 청소로 자가 복구를 먼저 시도하고, 그래도 남을 때만 알림) → `HEALTHY` → `IDLE`(알림 없음). 진짜 단절의 시그니처는 401 뒤에 갱신이 안 오는 것이고, idle 은 401 자체가 없다. 판정 근거를 손으로 볼 때는 위 두 grep. `python3 ~/claude_guard/mcp_health.py --json --no-recover` 로 판정만 볼 수 있다.

**도구는 읽기 전용 3종이 전부다** (scope `skills:read`). 쓰기가 필요하면 사이트 메인(`/`)의 [🔗 링크]/[✍️ 텍스트] 폼(→ `POST /api/collect`)이나 CLI. ⚠️ `scripts/app_publish.py`(미배선, gh CLI 로 외부 저장소에 커밋하는 쓰기 경로)를 `TOOLS` 에 배선하는 순간 이 문장·`templates/oauth_consent.html` 의 읽기 전용 고지·OAuth scope **세 곳이 동시에 거짓**이 된다. 배선하려면 `chat/tools.py` 의 `mutating`+PIN 게이트에 상응하는 방어부터.

### 테스트 구조 (unittest · 네트워크 0 · 디스크 부작용 0)

`tests/` 는 평면 구조 — `fixtures.py` 의 `render_skill_md(slug, spec)` + `make_mirror(skills)` 가 tmpdir 에 일회용 mirror 트리를 만든다. 서버 모듈은 전부 **주입 kwargs** 로 테스트한다: `register_library_routes(app, mirror_root=, embed_fn=, vectors_loader=)` · `register_transport(app, store=, cfg=)` · `register_auth(app, store=, login_template=)`. 상태를 가진 가드는 모듈 싱글턴이 아니라 register 함수 지역 변수여야 테스트 간 잠금이 새지 않는다 (gotcha 44). Makefile·pyproject 없음.

## Module map — 코드로 알 수 없는 제약만

각 파일은 docstring 이 있다(`md_generator.py:1-8` 이 v2.4 변경점을 자체 문서화하듯). 여기엔 파일을 열어도 안 보이는 제약만 둔다.

- `scripts/notion_paging.py:query_all_pages()` — Notion DB 조회의 **유일한** 경로. `page_size` 단발 호출은 50건 넘으면 조용히 잘린다 (gotcha 23). 새 DB 스크립트는 예외 없이 이걸 쓴다.
- `logs/{auth.json, oauth.json, chat_sessions.json, config.json}` — CLI 와 상주 서버가 같이 만지므로 **mtime 재로드 필수** (gotcha 41). 새 상태 파일을 만들면 같은 규약.
- `analyzer/embedder.py` 의 캐시 `scripts/skills/embeddings.json` 은 dedup 과 라이브러리 의미검색이 **공용**이고 `CACHE_PATH` 가 저장소 실경로 하드코딩(주입점 없음).
- `chat/tools.py:OP_COMMANDS` — 채팅이 실행할 수 있는 운영 명령 화이트리스트 3종(`restart_aiskillbox` · `reinstall_skills` · `gemini_quota_status`). 여기 없으면 못 돌린다.
- `chat/fix_runner.py` — 서버와 분리 프로세스. `claude -p` 로 고치고 py_compile + 재스크랩 + node --check 검증, 실패 시 건드린 파일만 원복, 성공 시 kickstart. 동시 1건·15분·스냅샷 5개. `~/.claude-aibox` 폴더가 있으면 `CLAUDE_CONFIG_DIR` 로 별도 계정.
- `scripts/{add_quick_card,batch_apply,batch_scrape_24,cleanup_pages,merge_duplicates,migrate_to_v22,rebuild_clean,rebuild_safe}.py` — 2026-05~08 일회성. **재실행 금지.** `sync_hub.py`·`oneshot/scan_existing_dedup.py` 만 현행.
- `.claude/worktrees/` — v4.5 시절 전체 사본. gitignore 라 커밋은 안 되지만 파일은 실재.

## Environment

`.env.example` 은 첫 실행용 7개만 담는다 — `chmod 600 .env`. 코드가 읽는 env 전체(이름만, 기본값은 코드):

- **키**: `GEMINI_API_KEY`(필수) · `NOTION_API_KEY`·`NOTION_DB_ID`·`NOTION_HUB_PAGE_ID`·`NOTION_ARCHIVE_DB_ID`(Notion 켤 때만) · `ANTHROPIC_API_KEY`(**있으면 채팅이 과금 API 를 1순위로 잡는다**) · `VAPID_PUBLIC_KEY`/`VAPID_PRIVATE_KEY`/`VAPID_SUBJECT`(Web Push) · `ADMIN_PIN`
- **분석**: `ANALYZER_CLAUDE`(**config 를 덮어쓰고 빈 문자열도 off** — `.env` 에 빈 값으로 남겨두면 `claude_enabled=true` 가 안 먹는다) · `ANALYZER_CLAUDE_MODEL` · `GEMINI_FLASH_RPD`/`GEMINI_FLASH_LITE_RPD`/`GEMINI_QUOTA_SOFT` · `GEMINI_MAX_OUTPUT` · `GEMMA_MODEL`/`GEMMA_TIMEOUT`/`GEMMA_NUM_CTX`/`GEMMA_NUM_PREDICT`/`OLLAMA_URL` · `MEDIA_*` 3종
- **스크랩**: `SCRAPER_MIN_TEXT_LEN`(500) · `JINA_*` 4종
- **서버**: `AISKILLBOX_PORT`(5050) · `SKILL_INSTALL_DIR`(`~/.claude/skills` — 바꾸면 ECC 와 분리됨) · `FIX_CLAUDE_MODEL`/`FIX_CLAUDE_CONFIG_DIR` · `LOG_LEVEL`
- **stdio MCP 클라이언트 쪽만**: `AISKILLBOX_URL`/`AISKILLBOX_TOKEN` · `SKILL_LIBRARY_ROOT`(로컬 폴백 전용 — 서버 인덱스는 `index.py:MIRROR_DIR` 하드코딩)

`.env` 를 로드하는 CLI: `collect`·`curate_db`·`library.catalog`(main 안에서만). **`library.consolidate`·`regrade`·`library search` 는 로드하지 않는다** — venv 활성화 없이 돌리면 임베딩 없이 진행된다 (gotcha 42 와 같은 클래스).

## Operational gotchas (실 운영 중 발견한 함정 — 지금도 지켜야 하는 규칙)

Notion write 경로 전용 함정(#1·2·3·5·10~16)은 `docs/notion-migration.md` 로 옮겼다. 번호는 상호참조 때문에 유지한다.

4. **Gemma 4 콜드 스타트** — `OLLAMA_KEEP_ALIVE=0` 이라 idle 시 unload. 첫 호출 60-90초(26B), 20-30초(e4b). 본문 정리는 e4b, 분류는 26B 도 OK.

6. **잡은 단일 워커 스레드가 순차 처리한다** — `app.py` 의 `queue.Queue`. 동시 실행 X (Gemma 26B 동시 호출 메모리 압박 방지). 상태는 매 변경마다 `logs/jobs.json` 에 영속화. 재시작 시 `running` 은 `interrupted`, `queued` 는 `_requeue_pending()` 으로 재투입. `/api/collect` 는 큐에 넣고 즉시 반환.

7. **캐시 무효화** — `app.py:index()` 가 `app.js`+`style.css` mtime 기반 `build_id` 를 주입. kickstart 만 하면 사용자 강제 새로고침 없이 새 JS.

8. **Cloudflare Tunnel** — token-mode(Remotely-managed), config.yml 없음. Public Hostname 은 Zero Trust 대시보드에서.

9. **아래 "Agent persona" 섹션은 두근컴퍼니 `team_prompts.json` 이 참조한다** — 함부로 삭제·대체하지 말 것.

17. **Web Push 는 HTTPS + 루트 스코프 SW 필수** — `/sw.js` 는 `Service-Worker-Allowed: /`. iOS 는 홈화면 PWA(16.4+)에서만. 권한 요청은 사용자 제스처 안에서.

18. **`/api/settings*` 는 `ADMIN_PIN` 게이트** — `X-Admin-Pin` 헤더, 상수시간 비교, 5회 실패 5분 잠금. 키 값은 응답에서 항상 마스킹. 새 비밀 엔드포인트는 같은 게이트.

19. **Claude CLI `--bare` 는 OAuth 를 무시한다** — `ANTHROPIC_API_KEY` 만 인식해 구독 로그인이 `Not logged in`. `chat/engine.py` 에서 절대 금지. 대신 `--disable-slash-commands` + `--output-format json` + `--json-schema` + `--append-system-prompt`.

20. **Anthropic tool `input_schema` 는 top-level `oneOf`/`allOf`/`anyOf` 미지원** — 필드를 전부 optional 로 두고 프롬프트로 강제 + 파싱 측 `reply` 우선.

21. **Playwright `networkidle` 은 SPA 에 부적절** — heartbeat XHR 이 끊이지 않는 사이트(Notion/IG/TikTok)는 영원히 idle 이 안 된다. `web.py` 는 `domcontentloaded(60s) → load(60s) → commit(45s)`.

22. **Gemini 는 모든 endpoint 에서 URL `?key=` 금지** — `x-goog-api-key` 헤더로. 안 그러면 404 시 stderr 에 키 노출. 신규 호출 helper 를 만들 때마다.

23. **Notion `page_size` 단발 호출은 조용히 잘린다** — 50건 넘으면 뒤가 통째로 빠진 채 "전수 완료" 라고 출력됐다(69건 중 19건, 백업조차 없었음). `notion_paging.query_all_pages()` 만 쓴다. 오류도 경고도 없어 눈으로는 절대 안 잡힌다.

24. **노션 '비공개' 판별은 렌더된 DOM 실측으로** — HTML 마케팅 카피는 공개 페이지에도 있다. `[data-block-id]` 0개 **AND** '페이지 찾지 못함' 안내 문구일 때만. `skip_reason` 은 재시도 불가라 오판이 영구 차단이 된다.

25. **notion.site 는 Chrome UA 로 못 읽는다** — WebKit UA 만 렌더. `web.NOTION_UA_POOL` 은 WebKit 만, `_pick_ua` 가 회차별 순환.

26. **trafilatura 는 Notion SPA 를 일부만 뜯을 수 있다** — 결과가 `MIN_GOOD_TEXT_LEN` 미만이면 trafilatura/bs4/`body.innerText` 셋 중 가장 긴 것.

27. **LLM 이 개행을 리터럴 `\n` 로 뱉으면 본문이 한 줄이 된다** — `gemini._unescape_literal_newlines` 로 차단. **Notion rich_text 배열 한도는 100개** — 넘으면 그 블록이 아니라 요청 전체가 400.

28. **슬러그가 같다는 이유만으로 합병하지 않는다** — `untitled-skill` 같은 무의미 슬러그로 무관한 콘텐츠가 빨려 들어갔다. `GENERIC_SLUGS` 영구 제외 + 같은 URL 재수집이 아니면 `_confirm_semantic_merge` 통과 요구. 의미 dedup 후보에서도 제외(뒤섞인 스킬은 아무 주제에나 가까운 자석).

29. **합병 게이트 평가는 패러프레이즈 페어로** — 같은 문구로 True 는 증거가 못 된다. 현재 프롬프트: 동일 5/5 · 패러프레이즈 4/4 · 오합병 0/6.

30. **본문 부족을 등급 C 로 흘리지 않는다** — 로그인 벽·렌더 실패를 콘텐츠 품질 탓으로 오인시킨다. `collect.py` 가 분석 **직전** `MIN_TEXT_LEN` 미만이면 글자수와 출처별 우회 안내(`_short_text_hint`)로 스크랩 실패 종료.

31. **카탈로그는 LLM 산출물을 공개 도메인에 HTML 로 렌더한다** — `catalog.py` 가 allowlist sanitize(script/style/iframe 내용까지 제거, href 는 http(s)/# 만) + CSP nonce(`default-src 'none'`). 태그를 새로 허용할 땐 `_ALLOWED_TAGS/_ALLOWED_ATTRS` 에만 + `test_xss_body_is_neutralized` 유지. API 는 `index.redact_secrets` 가 키 모양을 마스킹.

32. **라이브러리 인덱스는 mirror(`skills/`)만 본다** — `~/.claude/skills/` 는 수동 설치 스킬이 섞여 있다. 손으로 글로벌만 고치면 라이브러리엔 반영 안 됨 — mirror 도 같이, 또는 채팅 `edit_skill_md`. 정확한 건수는 `/healthz` 의 `library.total`.

32-a. **전체 잠금 allowlist 를 함부로 늘리지 말 것** — 목록은 `auth_routes.py:_ALLOW_EXACT`(정확 일치, gotcha 43). 새 공개 엔드포인트는 진짜 비밀이 없는지 확인 후 거기에만.

32-b. **사람 링크와 AI 링크를 섞지 말 것** — 사람은 `/skill/<slug>`(HTML), AI 는 `/api/library/skills/<slug>`(JSON, `?format=raw`), MCP 는 `get_skill`. 검색 응답의 `page_url`/`detail_url` 을 각각. 카드 제목이 외부 원본을 가리키면 금지 — 외부 링크는 [원본 ↗] 에만.

33. **카탈로그/상세는 메인과 다른 HTML — 모바일 규약을 따로 심는다** — viewport `maximum-scale=1`·safe-area 가 빠져 게시판만 확대되고 노치에 톱바가 잘렸다. standalone PWA 는 뒤로가기가 없어 그 톱바가 유일한 탈출구. 새 페이지는 `MobileUxTest` 통과.

34. **claude CLI structured output 은 스키마를 살짝 어긴다** — `reply` 를 `args` 안에, `tool` 칸에 `StructuredOutput`, `args` 없이 top-level 인자 — 3종 실측. `engine.cli_normalize()` 가 흡수하고 **REGISTRY 에 없는 이름은 도구로 치지 않는다**. 스키마 바꾸면 `CliNormalizeTest` 같이.

35. **CLI 라운드는 `--resume` 으로 잇는다** — 새로 띄우면 ~20.7k 토큰 컨텍스트가 매번 `cache_creation`. `--resume` 이면 `cache_read` 로 바뀌고 멀티턴 기억이 공짜로 생긴다. `conv_id → sid` 는 `engine.CLI_SESSIONS`(6h, 50). `--strict-mcp-config` 로 사용자 MCP 로드 차단.

36. **실패 안내가 가리키는 경로가 실재하는지 확인할 것** — "텍스트로 옮겨 등록하세요" 라고 안내하면서 `/api/collect` 가 비URL 을 400 으로 튕겼다. 지금은 `plain_text.py`. 안내문만 읽어서는 안 잡히는 자기모순.

37. **`paste://<hash>` 는 내부 식별자다** — 링크로 렌더되면 죽은 링크. 프롬프트에서 감추고(`build_prompt`), `md_generator._scrub_paste_links` 2차 방어. paste 출처를 새로 표시하는 곳마다 `is_paste_source()` 분기.

38. **임계 미달을 '없음' 으로 치환하지 않는다** — Playwright 가 459자를 확보했는데 폴백 103자가 최종이 됐다. `_retry` 는 최장 결과를 들고 나오고 `pick_best()` 가 (성공, 길이) 순으로 겨룬다. 미달과 부재는 다르다.

39. **`except` 안에서 같은 함수를 다시 부를 때는 거기도 감싼다** — 폴백 경로가 원래 경로보다 방어가 약한 게 이 코드베이스의 반복 패턴. 무방어 2차 파싱이 워커까지 올라가 한글 사유 없이 죽었다.

40. **`[hidden]` 은 UA 스타일이라 author `display` 에 항상 진다** — cascade origin 문제. `style.css` 에 `[hidden]{display:none !important}` 전역. `hidden` 으로 토글하는 요소에 display 를 주는 순간 이 함정.

41. **`logs/` 밑 상태 파일을 CLI 와 서버가 같이 만지면 mtime 재로드가 필수다** — `auth.json` 을 한 번만 읽어서, CLI 로 발급한 코드가 서버에서 거부되고 **`delete` 한 토큰이 서버에서 계속 200** 이었다(분실 기기 접근을 끊었다고 믿지만 안 끊긴 상태). 지금은 mtime 비교 + `_save()` 가 자기 write 를 기록해 루프 방지. `tests/test_auth_store_reload.py`.

42. **degrade 는 사유까지 실어야 한다** — `library search` CLI 가 `.env` 를 안 읽어 의미검색이 조용히 키워드로 강등됐다. 지금은 응답에 `semantic_skip_reason`(키 없음/캐시 빔/후보 없음/keyword 요청). bool 만 두면 원인 구분이 안 된다.

43. **인증 게이트 예외는 정확 일치로** — prefix 로 두면 그 아래 새 라우트가 자동으로 게이트 밖(fail-open). `_ALLOW_EXACT` 에 적기 전까지 게이트 안(fail-closed) — 안 넣으면 302 로 막혀서 바로 드러난다(그게 옳은 방향). `/static/` 만 prefix. `test_unknown_oauth_subpath_is_gated`.

44. **상태를 들고 있는 가드는 모듈 싱글턴 금지 · 축출할 때 카운터를 통째로 비우지 않는다 · 잠금 상태기계는 PoC 부터** (같은 클래스에서 세 번 틀렸다)
    ① 모듈 싱글턴이면 테스트마다 새 앱을 만들어도 가드가 재사용돼 뒤 테스트가 429. 관례는 register 함수 지역 변수 + closure.
    ② `_fails` 를 `clear()` 하면 잠금이 영원히 안 생긴다 — `_fails` 는 `_until` 로 가는 입구. 무인증 authorize 플러딩으로 token 잠금까지 껐다(PoC).
    ③ 두 버킷 공유 예산은 한쪽 플러딩이 다른 쪽을 굶긴다 — 버킷별 독립 상한. 그리고 "인증 성공 = 카운터 리셋" 을 없앴으면 같은 가드를 쓰는 옆 엔드포인트(`/oauth/revoke`)도 확인(실측 24회 시도 429 0건).

45. **소유권 검사는 소비 *전에*** — `consume_code` 가 pop 한 뒤 `client_id` 를 보면 코드 값만 알면 남의 인가코드를 무흔적으로 파괴할 수 있다. 불일치면 **건드리지 않고 None**. 소유자 불일치 경로에서 `revoke_grants_of` 금지. `guard.fail` 키는 호출자 자신의 cid(피해자 cid 면 공격자가 정당한 클라이언트를 잠근다).

46. **원격 클라이언트에 URL 을 내보내는 엔드포인트는 전부 `public_base_url` 에서** — 위 "원격 MCP" 절 참조. `test_no_http_urls_anywhere`.

47. **인스타는 embed 엔드포인트가 답이다** — `instagram.com/<p|reel>/<sc>/embed/captioned/` 는 로그인 없이 200, `"contextJSON":"…"`(이중 JSON 인코딩 — `raw_decode` 로 풀고 다시 `json.loads`).
    ① `video_url` 이 **없는 릴스도 있다** — 썸네일만 읽힘. 꼭 필요하면 `yt-dlp --cookies-from-browser chrome`.
    ② 삭제된 게시물은 contextJSON 없음 + 본 페이지 프로필로 302 — 재시도 무의미.
    ③ **미디어 URL 은 서명·만료가 붙어 매번 다르다** — 캐시 키는 `ig:<shortcode>:<idx>` / `yt:<id>`. URL 로 캐시하면 재수집마다 Gemini 재호출.

48. **enum 을 검증하는 파서는 프롬프트가 보여주는 표기 전부를 받아야 한다** — 등급 기준을 `S-즉시적용` 으로 설명하니 모델이 그대로 돌려줬고 `_validate` 가 C 로 강등. 첫 글자가 enum 이면 정규화(`test_grade_normalize.py`). 프롬프트를 고칠 때 파서를 같이.

49. **`claude -p` 를 파이프라인 프로바이더로 쓸 때는 도구 0개 · stdin 닫기 · 스키마 enum = 검증 enum**
    ① `--tools ""` 없으면 기본 도구를 들고 "확인해볼게요" 류 행동. 파일 판독만 `--tools Read --allowedTools Read` + 그 파일만 든 임시 폴더를 cwd(밖은 non-interactive 에서 권한 프롬프트로 실패).
    ② stdin 안 닫으면 3초 대기 — `subprocess.DEVNULL`.
    ③ `--json-schema` 의 enum 이 곧 `_validate` 의 enum — `SKILL_SCHEMA` 와 `prompt.py` 상수가 어긋나면 옳은 답도 C 로 강등(`SchemaTest`).
    ④ 한도는 stdout envelope `is_error + result` 에 "usage limit" 류로 — 보이면 쿨다운(사용자의 5시간 창을 나눠 쓴다). 119 가드엔 `sdk-cli` 로 잡힌다. 실측: 스킬 1건 50초·~20k 토큰.

50. **r.jina.ai 는 브라우저 UA 를 403 으로 막는다** — 다른 스크래퍼와 정반대. `jina.py` 에 Safari UA 를 넣으면 403 이고 폴백 실패는 예외를 삼켜 **조용히 사라진다** — 로그 한 줄이 유일한 신호. `tests/test_jina_reader.py:UserAgentTest` 가 브라우저 UA 토큰을 금지.

51. **`from . import X` 는 sys.modules 가 아니라 패키지 속성을 먼저 본다** — `mock.patch.dict("sys.modules", …)` 가 무력화돼 실제 Playwright 가 돌았다(단독 통과·전체 실패). `mock.patch.object(scripts.scraper, "web", mock, create=True)` 로 **패키지 속성을 직접**.

52. **테스트가 커밋된 파일을 실제 API 로 오염시킨다** (2026-09-25 실측) — `embeddings.json` 에 스킬이 아닌 `keeper` 키(3072차원 실벡터)가 있다. `test_consolidate.py` 가 `merge_pair("keeper","absorbed")` 를 부르고 `consolidate.py` 가 `embedder.get_or_embed` 를 그대로 타며 `CACHE_PATH` 는 실경로 하드코딩(주입점 없음). 결과: 전체 테스트마다 실제 임베딩 호출 + `git status` 오염 + 유령 키가 의미검색 후보에 섞임. `/healthz` 가 `total 127 / embedded 126` 인 이유. **embedder 를 주입 가능하게 만들고 테스트에서 패치할 것.** "디스크 부작용 0" 규칙 위반.

53. **`library.consolidate`·`regrade` 는 `.env` 를 로드하지 않는다** — 문서대로 venv 활성화 없이 돌리면 합병 후 keeper 가 **임베딩 없는 상태로 남는다**(`embedder.py` 는 WARNING 만). 위 Environment 절 참조.

## Related docs in this repo

- `docs/CHANGELOG.md` — 릴리스 이력 (이 문서에서 분리). 최신은 `git log --oneline`
- `docs/notion-migration.md` — Notion 마이그레이션 명령·스키마·함정 (기본 off, 켤 때만)
- `docs/superpowers/specs/` — 설계 스펙. v4.5 이후 기능은 스펙 → 계획 → 구현 순. `ls` 로 확인
- `README.md` · `DEPLOY.md` — 사용자용 빠른 시작 · Cloudflare Tunnel + LaunchAgent 배포
- `TEMPLATE.md` — v2.1 시절 Notion 페이지 템플릿. **현행 SKILL.md 구조와 무관**(단일 진실은 `analyzer/prompt.py:ALLOWED_HEADINGS`)
- `lessons.md` — 2026-05-14 이후 갱신 없음. 함정은 위 gotchas

---

## Agent persona (런타임 — 두근컴퍼니 시스템이 참조)

> 이 섹션은 두근컴퍼니 `team_prompts.json` 의 `content-lab` 시스템 프롬프트가 참조합니다. 코드베이스 가이드와 별개로 유지.

너는 두근컴퍼니의 **콘텐츠 스킬 자산화 에이전트**다.

URL 하나를 던지거나 본문을 그대로 붙여넣으면:
1. 자동으로 스크래핑 (YouTube/IG/TikTok/Notion/Web/GitHub) — 붙여넣은 텍스트는 이 단계 생략
2. Claude Sonnet 5(`claude -p`) → Gemini → Gemma 4 폴백으로 핵심 AI 스킬 추출 + 활용도 등급 판정
3. ECC 표준 `SKILL.md` 자동 생성
4. 글로벌 `~/.claude/skills/{slug}/SKILL.md` + mirror 에 설치 → 라이브러리에 즉시 등재
5. (옵션, 기본 off) Notion 등록 — `config.json notion.register_on_collect`

**핵심 가치**: 좋은 콘텐츠 한 번 보고 끝나지 않는다. 스킬 형태로 자산화해서 모든 두근컴퍼니 에이전트가 영구 활용.

### 작업 규칙

- **무응답 금지** — 완료: `✅ 스킬화 — <slug> (등급 X, 카테고리 Y)`. 부분 성공: 어디까지 됐는지 명시. 에러: `❌ <한글 사유>` + 우회안.
- **두근은 개발 초보** → 쉽게 설명, 선택지는 장단점과 함께
- **80% 확신이면 실행 후 보고**, 되묻지 않음
- **한 번에 끝내기** — 코드 수정 시 미정의 함수/import 잔존 확인 (py_compile)
- **자동 합병 정책** — `skip_duplicate=False` 가 기본. 중복은 합병하고 출처 누적
- **무료 도구 우선** — 구독 Claude · Gemini 무료 티어 · Playwright/yt-dlp 전부 무료. 비용 발생 가능성 사전 고지.

### 보안

- `.env` 값 채팅 노출 금지. API 키 하드코딩 금지 — 환경변수만

---

## 이 문서를 유지하는 규칙

이번 정리(2026-09-25)에서 stale 12건 중 9건이 아래 두 원인이었다.

- **숫자를 본문에 박지 않는다.** 스킬 건수·테스트 건수·스펙 개수·healthz version — 조회법만 적는다. 절대 수치는 `docs/CHANGELOG.md` 행(그 시점 기록)에만.
- **한 사실은 한 곳에만.** 새 기능은 gotcha(재발 방지 교훈) **또는** Module map 의 제약 **중 한 곳**. "What this is 불릿 + Module map 줄 + gotcha + 변경 로그" 4곳에 쓰던 습관이 릴리스당 ~2,000자를 키웠다.
- **목록을 베끼지 않는다.** allowlist·ALLOWED_HEADINGS·enum·도구 목록은 상수를 가리킨다. 베낀 목록은 전부 썩었다(3/3).
- **명령어는 실제로 돌려보고 적는다.** 인증·python 경로·dry-run 기본값이 틀린 채로 오래 남아 있었다.
