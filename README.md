# 두근컴퍼니 콘텐츠랩 v4.9

URL(또는 붙여넣은 텍스트) → 스크래핑 → AI 분석 → ECC 표준 SKILL.md 생성 → 글로벌 설치 → **스킬 라이브러리(검색 API · MCP · 카탈로그)** 에 즉시 등재. (Notion DB 등록은 v4.5 부터 옵션)

좋은 콘텐츠를 한 번 보고 끝내지 않고, **스킬 자산**으로 영구 활용 가능한 형태로 보관한다.

---

## 빠른 시작

```bash
cd ~/Developer/my-company/content-lab

# 1. venv + 의존성
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 2. .env 설정
cp .env.example .env
# .env 열고 GEMINI_API_KEY + NOTION_API_KEY 입력

# 3. 첫 수집
python -m scripts.collect "https://youtu.be/<영상ID>"
```

JSON 결과가 stdout에 출력되고, 글로벌 `~/.claude/skills/<slug>/SKILL.md` + mirror `skills/<slug>/SKILL.md` 생성. mirror 에 저장되는 순간 라이브러리 검색/카탈로그에 잡힌다 (재인덱스 불필요).

---

## 사용 예시

```bash
# YouTube 영상
python -m scripts.collect "https://www.youtube.com/watch?v=XYZ"

# 인스타그램 포스트
python -m scripts.collect "https://www.instagram.com/p/ABC/"

# Notion 공개 페이지
python -m scripts.collect "https://example.notion.site/skill-doc"

# GitHub 레포
python -m scripts.collect "https://github.com/user/repo"

# Notion 등록 (v4.5 기본 off — config.json notion.register_on_collect) 강제 on/off
python -m scripts.collect "<URL>" --notion
python -m scripts.collect "<URL>" --no-notion

# 기존 슬러그 덮어쓰기
python -m scripts.collect "<URL>" --overwrite

# 텍스트 직접 입력 (v4.9) — 스크랩이 안 되는 출처용. 최소 200자
#   ChatGPT 공유·GPT 링크, 인스타 피드, 로그인 벽 뉴스레터, 워크스페이스 전용 노션
python -m scripts.collect --text-file ./본문.md --title "제목"
pbpaste | python -m scripts.collect --text -

# 본문만 손으로 옮겼고 원본 링크는 남기고 싶을 때 — 그 URL 이 출처가 된다
python -m scripts.collect "https://chatgpt.com/share/abc" --text-file ./본문.md
```

웹 UI 는 메인 폼의 **[✍️ 텍스트] 탭**에서 같은 일을 한다. 링크 입력칸에 본문을 붙여넣어도
자동으로 텍스트 탭으로 넘어간다.

---

## 결과 위치

| 위치 | 용도 |
|------|------|
| `~/.claude/skills/<slug>/SKILL.md` | 모든 Claude Code 세션이 자동 활성화 후보로 인식 |
| `content-lab/skills/<slug>/SKILL.md` | Git 추적용 mirror — **라이브러리 원본** (검색 인덱스·카탈로그·MCP 가 여기서 읽음) |
| `https://aiskillbox.600g.net/catalog` | 사람용 게시판 (검색·필터·카드/목록 전환). 제목 클릭 = 사이트 안 게시글 `/skill/<slug>` |
| `GET /api/library/search?q=…` | 에이전트용 하이브리드 검색 API (두근컴퍼니 FastAPI, aiskillbox 채팅 `search_library`) |
| MCP `skill-library` | Claude Code · Cursor · Codex · 다른 클로드 계정 — 아래 "스킬 라이브러리" 참고 |
| Notion DB | (옵션) `config.json` `notion.register_on_collect: true` 일 때만 등록 |

---

## 로그인 (v4.6 — 초대코드 전체 잠금)

사이트 전체가 초대코드 로그인 필요 (`/login`, `/healthz` 만 공개). 코드 한 번 입력하면 그 기기는 영구 자동로그인.

```bash
# 첫 진입 (또는 전 기기 로그아웃 복구): 브라우저 /login → "관리자 첫 등록" 에 ADMIN_PIN
# → 자동 로그인 + 첫 초대코드 발급 (다른 기기용으로 복사)

# 터미널에서 코드 관리
python -m scripts.auth_store create "폰"     # 발급
python -m scripts.auth_store list             # 목록 (기기 수 포함)
python -m scripts.auth_store delete DGN-....  # 삭제 = 그 코드 기기 전부 로그아웃

# 에이전트/외부 MCP: redeem 응답의 token 을 env 로
#   claude mcp add ... -e AISKILLBOX_URL=https://aiskillbox.600g.net -e AISKILLBOX_TOKEN=<token>
# (이 Mac 의 MCP 는 토큰 없어도 로컬 인덱스 폴백으로 검색 동작)
```

설정창(⚙️, PIN)에도 초대코드 발급/삭제 UI 가 있어요.

## 운영 채팅 — v4.8 (Opus 5 · 실시간)

우측 하단 💬 버튼. 자연어로 운영 상태 조회·설정 편집·SKILL.md 수정·코드 수정 위임까지 폰에서 끝낸다.

- **실시간 스트리밍** — 답이 토큰 단위로 흐르고, 도구 실행(`recent_jobs` 등)이 진행 중에 그대로 보인다. [중지] 로 언제든 끊기.
- **대화를 기억한다** — "아까 그거 다시", "그럼 그건 왜 실패했어?" 처럼 이어 말해도 된다. 맥락을 비우려면 [새 대화].
- **모델** — 본계정 구독(claude CLI)의 **Opus 5**. 한도에 걸리면 CLI 가 Sonnet 5 로 자동 강등, 그마저 안 되면 로컬 Ollama.
- **쓰기 명령은 PIN 1회** — 설정 변경·스킬 수정·코드 위임 등 mutating 도구만 해당. 30분 세션.

```bash
# 모델 바꾸기 (config.json)
"chat": { "claude_model": "claude-opus-5", "claude_fallback_model": "claude-sonnet-5" }
```

## 스킬 라이브러리 (도서관) — v4.5

SKILL.md 가 유일한 원본. 노션 없이 "검색해서 꺼내 쓰는" 세 가지 입구:

```bash
# 1) 사람 — 게시판 (카테고리·검색·카드/목록 전환). 제목 클릭 = 사이트 안 게시글
open https://aiskillbox.600g.net/catalog            # 목록
open https://aiskillbox.600g.net/skill/<슬러그>      # 게시글 상세 (본문 전문 + SKILL.md 복사)
python -m scripts.library build-catalog --out logs/catalog.html   # 정적 목록 단일 HTML (~360KB)

# 2) 에이전트 — HTTP (키워드 BM25 + Gemini 임베딩 코사인 → RRF 융합)
curl -s "http://localhost:5050/api/library/search?q=인스타+릴스+대본&k=5" | python3 -m json.tool
curl -s "http://localhost:5050/api/library/skills/<slug>?format=raw"      # SKILL.md 전문
curl -s "http://localhost:5050/api/library/skills?category=자동화&grade=S"  # 목록(메타)
curl -s "http://localhost:5050/api/library/stats"

# 3) MCP — Claude Code (이 Mac)
claude mcp add --scope user skill-library -- python3 /Users/600mac/Developer/my-company/content-lab/scripts/library/mcp_server.py
#    외부 기기/다른 계정 (HTTP 만 사용, 표준 라이브러리라 venv 불필요)
claude mcp add --scope user skill-library -e AISKILLBOX_URL=https://aiskillbox.600g.net -- python3 /path/to/mcp_server.py
#    도구: search_skills(query,k,category) · get_skill(slug) · list_skills(category,grade)

# 터미널 검색
python -m scripts.library search "토큰 절약" -k 5
python -m scripts.library stats
```

- 의미 검색은 `scripts/skills/embeddings.json`(dedup 용 캐시) 를 재활용. Gemini 키/쿼터가 없으면 자동으로 키워드만 (`semantic_used:false`).
- aiskillbox 채팅에 "OO 스킬 있어?" 라고 물으면 `search_library` 도구가 먼저 돈다.
- Notion 등록을 다시 켜려면 `config.json` → `"notion": {"register_on_collect": true}` (채팅 `write_config` 로도 가능).

---

## 의존성

| 패키지 | 용도 |
|--------|------|
| playwright | JS 렌더링 (IG/TikTok/Notion 등) |
| yt-dlp | YouTube 자막/메타 |
| google-generativeai | Gemini 분석 |
| notion-client | Notion DB 등록 |
| beautifulsoup4 + requests | 정적 HTML 폴백 |

---

## 환경 변수

`.env.example` 복사 후 채우기:
- `GEMINI_API_KEY` — https://aistudio.google.com/apikey (필수)
- `NOTION_API_KEY` — https://www.notion.so/my-integrations (필수)
- `NOTION_DB_ID` — 두근 스킬 DB UUID (이미 세팅됨)

NOTION_API_KEY 발급 후 **DB 페이지 → Connections → 인티그레이션 추가** 잊지 말 것 (안 하면 401).

---

## 트러블슈팅

### `playwright._impl._errors.Error: BrowserType.launch: Executable doesn't exist`
```bash
playwright install chromium
```

### `yt-dlp: command not found`
```bash
brew install yt-dlp
```

### Gemini 429 (quota exceeded)
무료 1500/day 초과. 다음 날 리셋. 다급하면 GEMINI_API_KEY 다른 계정 키로 임시 교체.

### Notion 401
DB Connections에 인티그레이션 안 붙임. https://www.notion.so/my-integrations 에서 만든 인티그레이션을 DB 페이지에서 추가.

### Playwright가 빈 페이지 반환 (IG/TikTok 로그인 벽)
`mcp_fallback.py` 가 requests로 우회 시도. 그래도 실패하면 Claude Code 세션에서 exa/firecrawl MCP로 재시도. 로그인 필요한 콘텐츠는 수동 텍스트 입력 우회 권장.

---

## 두근컴퍼니 안에서의 위치

- CPO 또는 사용자가 콘텐츠랩 채팅창에 URL을 던지면 콘텐츠랩 에이전트가 위 CLI 실행
- 생성된 SKILL.md는 모든 두근컴퍼니 에이전트(`~/.claude/skills/` 자동 인식)에 즉시 노출
- MD 메이커 (`agent-6d883e`)가 신규 에이전트 만들 때 이 스킬 DB에서 검색해서 페르소나에 통합

---

## 변경 로그

자세한 내용은 `CLAUDE.md` 의 [변경 로그] 섹션 참조.
