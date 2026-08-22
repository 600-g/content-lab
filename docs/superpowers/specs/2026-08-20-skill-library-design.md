# aiskillbox 스킬 라이브러리 (도서관) 설계 (2026-08-20)

> 브레인스토밍 결론 (2026-08-19 세션): **SKILL.md 가 유일한 원본, 노션은 퇴역(옵션 강등),
> 소비자 4종 (Claude Code 세션 · 두근컴퍼니 에이전트 · aiskillbox 채팅 · 외부 도구) 이
> 의미+키워드 하이브리드 검색으로 본문을 꺼내 쓰고, 사람용 카탈로그 HTML 은 바탕화면
> `스킬박스고도화.zip`(두근 스킬카탈로그 킷) 템플릿으로.** 접근법 A (기존 Flask 에 붙이기) 채택.

## 목표

1. **검색해서 꺼내 쓴다** — "인스타 릴스 대본 자동화" 같은 자연어로 물으면 단어가 안 겹쳐도
   관련 스킬 본문이 나온다. 새 프로세스 0개, 유료 0원 (Gemini embedding 무료 + 기존 캐시 재활용).
2. **어디서든 붙는다** — HTTP API (두근컴퍼니 FastAPI · aiskillbox 채팅) + MCP stdio 서버
   (Claude Code · Cursor · Codex · 다른 클로드 계정, 파이썬 표준 라이브러리만으로 동작).
3. **사람도 본다** — 킷의 단일 HTML 카탈로그 (검색·출처/카테고리/등급/AI도구 필터·본문 복사·
   상세 모달). `/catalog` 로 서빙 + 정적 파일로도 뽑기.
4. **노션 퇴역** — 수집 파이프라인의 Notion 등록을 config 옵션 (`notion.register_on_collect`,
   기본 false) 으로 강등. 기존 코드/페이지는 삭제하지 않는다 (되돌리기 = 플래그 하나).

## 비목표 (YAGNI)

- `~/.claude/skills/` 전부 설치를 중단하고 MCP 검색만 쓰는 전환 — **보류**. 설치 동작은 그대로.
  (79개 description 이 세션 프롬프트를 비대하게 만드는 문제는 별건으로 다시 결정.)
- 노션 DB 삭제/아카이브, 노션 전용 정리 스크립트 제거 — 안 한다.
- 벡터 DB, 외부 검색 엔진, 인증 시스템 — 안 한다. 라이브러리 API 는 **읽기 전용 공개** (사이트 자체가 공개).
- company-hq 쪽 에이전트 도구 구현 — 이 repo 밖. 엔드포인트 문서만 제공.

## 1. 아키텍처

```
skills/*/SKILL.md (79건, git mirror — 원본)          scripts/skills/embeddings.json (77건 캐시)
   │ mtime 변경 감지 (요청마다 stat, 2초 스로틀)        │ slug → vec(3072) — dedup 용 그대로 재활용
   ▼                                                  ▼
scripts/library/index.py ─ LibraryIndex (frozen 레코드) + 키워드 BM25 + 코사인 + RRF 융합
   │
   ├─ scripts/library/routes.py  GET /api/library/search|skills|skills/<slug>|stats, GET /catalog
   │      ├─▶ 두근컴퍼니 에이전트 (HTTP, aiskillbox.600g.net)
   │      ├─▶ aiskillbox 채팅 도구 search_library (같은 프로세스, 직접 호출)
   │      └─▶ 사람 (/catalog — 킷 템플릿)
   ├─ scripts/library/mcp_server.py  stdio MCP (stdlib only) ─▶ Claude Code · Cursor · Codex · 외부 계정
   │      HTTP 우선 (AISKILLBOX_URL) → 실패 시 로컬 인덱스 직접 import 폴백
   └─ scripts/library/catalog.py  HTML 생성기 (+ CLI build-catalog → 정적 파일)
```

모든 모듈은 `scripts/library/` 패키지 안. 200~400줄 단위로 분리 (index / search / catalog / routes / mcp_server).

## 2. 컴포넌트

### 2.1 `scripts/library/index.py` — 인덱스

- `SkillRecord` (frozen dataclass): `slug, title, description, category, grade, difficulty, ai_tools,
  sources, source_types, body_md, raw_md, path, mtime`.
- `load_index(root=MIRROR_DIR) -> LibraryIndex` : `skills/*/SKILL.md` 전수 파싱. frontmatter 는
  PyYAML 없이 단순 `key: value` + `- item` 파서 (현재 md_generator 가 쓰는 형태만 지원, 외부 의존 0).
  필드 누락 (v2.4 이전 11건) 은 `category="기타"`, `grade=""` 로 보정 — 인덱스에서 빼지 않는다.
- `get_index()` : 모듈 캐시. 디렉토리 스캔 비용을 막기 위해 **2초 스로틀 + 파일 수/최대 mtime 변경 시만 재빌드**.
  수집 파이프라인이 mirror 에 쓰면 다음 요청에 자동 반영 (별도 reindex 불필요).
- `source_type(url)` : `scripts/scraper.detect_source` 재사용 (youtube/instagram/github/notion/web…).

### 2.2 `scripts/library/search.py` — 하이브리드 검색

- 토크나이저: 소문자 → 영숫자/한글 토큰 분리 → **한글 토큰은 2-gram 추가** (조사/어미 변형 흡수:
  "인스타그램" 질의가 "인스타" 본문과 겹치게). 영문은 단어 그대로 + 3자 이상 prefix 는 안 함 (과매칭 방지).
- 키워드 점수: BM25 (k1=1.5, b=0.75) 를 **필드별 가중** — title×3, description×2, ai_tools/category×1.5,
  body×1. 제목에 질의 원문이 부분 문자열로 포함되면 보너스.
- 의미 점수: `embedder.embed(query)` (Gemini, 키 헤더 방식) → 캐시 벡터와 코사인. 캐시에 없는 슬러그는
  의미 점수 없음 (키워드만). 질의 임베딩 실패 (키 없음/쿼터/네트워크) → `semantic_used: false` 로
  키워드 결과만 반환. **절대 예외를 밖으로 내보내지 않는다.**
- 융합: Reciprocal Rank Fusion `Σ 1/(60+rank)` — 두 점수 스케일이 달라도 정규화 불필요. 결과에
  `kw_rank / sem_rank / score` 를 같이 실어 디버깅 가능.
- 필터: `category`, `grade` (결과 필터, 인덱스 재계산 없음). `mode=keyword` 로 의미 검색 강제 생략.
- 질의 임베딩은 **LRU 128 캐시** (같은 질문 반복 시 Gemini 재호출 X).

### 2.3 `scripts/library/catalog.py` — 카탈로그 HTML

- 킷 `catalog_template.html` 의 디자인 토큰/레이아웃/JS 엔진을 **Jinja 없이 문자열 템플릿**으로 이식
  (단일 파일 자체완결 원칙 유지, `/catalog` 와 정적 빌드가 같은 함수).
- 매핑 (킷 스펙 §2 대응표 → 우리 frontmatter):
  | 카드 요소 | 값 |
  |---|---|
  | `data-source` / 출처 뱃지 | 첫 출처 URL 의 source_type (youtube/notion/github/web/instagram…) |
  | `data-group` / 섹션 | category (7종, 고정 순서: 프롬프트/자동화/콘텐츠/디자인/개발/업무/기타) |
  | `data-grade` / 등급칩 | grade (S/A/B/C) — 킷 권고대로 확장 |
  | `data-tools` / AI도구 칩 | ai_tools (상위 10개 도구만 칩으로) |
  | `h3 > a` | title → 첫 출처 URL |
  | `code.cmd` | slug (`~/.claude/skills/<slug>`) |
  | `p.desc` | description |
  | `.date` | SKILL.md mtime (YYYY-MM-DD) |
  | `data-text` | title+slug+description+category+tools+grade+body(2000자) 소문자 — 킷 검색 인덱스 규칙 |
  | 기본 버튼 | **SKILL.md 복사** (frontmatter 포함 전문 → 다른 기기 `~/.claude/skills/<slug>/` 에 붙여넣기) |
  | 보조 버튼 | **자세히** → 모달 (본문 markdown → HTML 렌더, 출처 링크, 로컬 경로) |
- 섹션 안 서브그룹 (`.sub`) = 등급 (S · A · B/C). 정렬: 카테고리 고정 순서 → 등급 → 제목.
- 딥링크: `/catalog#<slug>` 진입 시 해당 카드로 스크롤 + 모달 자동 오픈 (완료 카드/채팅에서 링크용).
- **XSS 방어 (중요)**: 본문은 LLM 이 스크랩 결과에서 생성 — 악성 페이지가 `<script>` 를 심을 수 있고,
  같은 origin localStorage 에 채팅 PIN 세션 토큰이 있다.
  1. markdown 변환 전 본문의 `<`/`>` 를 이스케이프 (raw HTML 은 문자 그대로 표시, 코드블록은 무관)
  2. 모든 속성/텍스트 `html.escape(quote=True)`
  3. `<meta http-equiv="Content-Security-Policy">` 에 **nonce 기반 script-src** — 우리 엔진 `<script nonce>` 만 실행
  4. 외부 요청 0 (폰트 시스템, 이미지 없음) — CSP `default-src 'none'; style-src 'unsafe-inline'`
- CLI: `python -m scripts.library build-catalog [--out logs/catalog.html]`.

### 2.4 `scripts/library/routes.py` — Flask 엔드포인트 (읽기 전용)

| 엔드포인트 | 응답 |
|---|---|
| `GET /api/library/search?q=&k=8&category=&grade=&mode=hybrid\|keyword` | `{ok, query, mode, semantic_used, total_indexed, results:[{slug,title,description,category,grade,difficulty,ai_tools,sources,score,kw_rank,sem_rank,snippet,detail_url}]}` |
| `GET /api/library/skills?category=&grade=` | `{ok, total, items:[메타만]}` |
| `GET /api/library/skills/<slug>` (`?format=raw` → text/markdown) | `{ok, slug, meta, body_md, raw_md, path}` / 404 `{ok:false,error}` |
| `GET /api/library/stats` | `{ok, total, by_category, by_grade, embedded, last_updated}` |
| `GET /catalog`, `/catalog.html` | HTML (인덱스 버전 키로 메모리 캐시, ETag) |

- 입력 검증: `q` 2~300자 (미만 400), `k` 1~50 clamp, `category`/`grade` enum 외 값 무시.
- `Access-Control-Allow-Origin: *` (GET 만) — 공개 읽기 데이터. 에러도 JSON envelope.
- app.py: `register_library_routes(app)` 한 줄 (chat routes 와 같은 패턴).

### 2.5 `scripts/library/mcp_server.py` — MCP stdio 서버

- **표준 라이브러리만** (`json`, `sys`, `urllib`) — 다른 기기/계정에서 `python3 mcp_server.py` 만으로 동작.
- 프로토콜: JSON-RPC 2.0, newline-delimited stdio. `initialize` (protocolVersion 에코, `capabilities.tools`),
  `notifications/initialized`, `ping`, `tools/list`, `tools/call`. 모르는 메서드 → `-32601`.
- 도구 3개: `search_skills(query, k=5, category?)` · `get_skill(slug)` · `list_skills(category?, grade?)`.
  결과는 `content:[{type:"text", text}]` — search 는 사람이 읽기 좋은 요약 + slug, get 은 SKILL.md 본문 전문.
- 백엔드: `AISKILLBOX_URL` (기본 `http://localhost:5050`) HTTP 호출 → 연결 실패 시 같은 repo 의
  `scripts.library` 직접 import 폴백 (로컬 Mac 에서 서버 죽어도 키워드 검색은 됨). 둘 다 실패 → `isError:true`.
- 등록 (문서로 안내, 자동 등록 안 함):
  `claude mcp add --scope user skill-library -- python3 /Users/600mac/Developer/my-company/content-lab/scripts/library/mcp_server.py`
  외부 기기: `AISKILLBOX_URL=https://aiskillbox.600g.net` env 추가.

### 2.6 통합 (기존 코드 접점)

- `scripts/chat/tools.py`: `search_library(query, k)` 조회 도구 등록 (비 mutating). 채팅 시스템 프롬프트에
  "스킬 찾는 질문이면 search_library 먼저" 한 줄.
- `config.json`: `"notion": {"register_on_collect": false}` 추가. `app.py:_run_job` 이
  `register_notion=config_store.get("notion.register_on_collect", False)`. CLI 는 `--notion` 플래그로 강제,
  `--no-notion` 은 유지. `write_config` 허용 prefix 에 `notion.` 추가 (채팅으로 토글 가능).
- `templates/index.html` / `static/app.js`: 상단 Notion 칩 → **📚 카탈로그** 칩 (`/catalog`), 드로어에
  카탈로그 링크 카드, 완료 카드/최근 목록의 Notion 링크 자리에 `📚 카탈로그 #slug` 링크
  (notion_web_url 있으면 Notion 링크도 같이). Notion 섹션/헬스 행은 `notion_enabled` 일 때만.
- `app.py:index()` 가 `notion_enabled`, `catalog_url` 템플릿 변수 전달.

## 3. 데이터 흐름

1. 수집 완료 → `mirror_skill()` 이 `skills/<slug>/SKILL.md` 갱신 → 다음 `/api/library/*` 요청에서
   mtime 변경 감지 → 인덱스 재빌드 (79건 ≈ 수십 ms) → 즉시 검색 가능. 임베딩은 수집 시 이미
   `get_or_embed(slug, …)` 로 캐시에 들어감 (기존 동작).
2. 질의 → 토큰화 → BM25 순위 / (가능하면) 질의 임베딩 → 코사인 순위 → RRF → 필터 → top-k.
3. 카탈로그: 인덱스 버전(파일 수+최대 mtime) 이 바뀌면 HTML 재생성, 아니면 캐시 응답.

## 4. 에러 처리

- 인덱스 파싱 실패 파일 → 경고 로그 + 그 파일만 제외 (전체 실패 금지).
- 임베딩 실패 → 키워드 결과 + `semantic_used:false` (조용히 품질만 낮아지는 게 아니라 응답에 표시).
- 캐시 벡터 차원 불일치 (모델 변경) → 해당 항목 무시 + 경고 1회.
- MCP: JSON 파싱 실패 라인 → `-32700` 응답 후 계속; 도구 예외 → `isError:true` 텍스트.
- 존재하지 않는 slug → 404 JSON. 경로 탐색 방지: slug 는 `[a-z0-9\-_.]+` 만 허용.

## 5. 테스트 (unittest, `venv/bin/python -m unittest discover tests`)

- `tests/test_library_index.py` — frontmatter 파싱(누락 필드 보정, sources 리스트), 토크나이저 2-gram,
  BM25 제목 가중(제목 일치 문서가 본문 일치보다 상위), RRF 융합(키워드만/의미만/둘 다), 필터.
  임시 디렉토리에 SKILL.md 픽스처 3~4건 생성 — 실제 mirror 에 의존 안 함.
- `tests/test_library_catalog.py` — 카드 수/섹션 순서, `<script>alert` 본문이 이스케이프돼 실행 태그가 없음,
  nonce 가 CSP 와 script 에 동일하게 박힘, 딥링크용 `id="<slug>"`.
- `tests/test_library_routes.py` — Flask test client: search 200/400, skills/<slug> 200/404, raw 포맷,
  CORS 헤더, /catalog 200 + text/html.
- `tests/test_mcp_server.py` — subprocess 로 서버 띄워 initialize → tools/list → tools/call(list_skills,
  로컬 폴백 모드, `AISKILLBOX_URL=http://127.0.0.1:9` 로 HTTP 강제 실패) 왕복 검증.
- 실구동 스모크: 임시 포트로 `app.py` 띄워 `/catalog`, `/api/library/search?q=인스타` 실측.

## 6. 리스크 / 주의

- 공개 도메인에서 SKILL.md 전문이 읽힌다 — 이미 `~/.claude/skills` 에 있는 공개 수집물이라 비밀 없음.
  단 **frontmatter/본문에 키가 섞여 들어간 적 없는지** 서빙 전 `_redact_secrets` 패턴으로 한 번 거른다.
- 의미 검색은 캐시 벡터가 "제목+callout+도구+카테고리" 로 만든 것 — 본문 세부는 키워드가 보완.
  필요하면 나중에 본문 임베딩으로 교체 (캐시 키 동일, `rebuild_embeddings` 재사용).
- 카탈로그 HTML 은 79건 × 본문 렌더 ≈ 수백 KB — 첫 로딩만. 이미지 없음. 수백 건까지 문제없음 (킷 실측).
- Notion 기본 off 는 **행동 변경** — 변경 로그와 README 에 명시, 되돌리기는 `notion.register_on_collect: true`.
