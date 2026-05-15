# 두근컴퍼니 콘텐츠랩 v4.0

URL → 스크래핑 → AI 분석 → ECC 표준 SKILL.md 생성 → 글로벌 설치 + Notion DB 등록.

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

JSON 결과가 stdout에 출력되고, 글로벌 `~/.claude/skills/<slug>/SKILL.md` 생성 + Notion DB에 새 페이지 등록됨.

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

# Notion 등록 없이 로컬만
python -m scripts.collect "<URL>" --no-notion

# 기존 슬러그 덮어쓰기
python -m scripts.collect "<URL>" --overwrite
```

---

## 결과 위치

| 위치 | 용도 |
|------|------|
| `~/.claude/skills/<slug>/SKILL.md` | 모든 Claude Code 세션이 자동 활성화 후보로 인식 |
| `content-lab/skills/<slug>/SKILL.md` | Git 추적용 mirror (백업 + 협업) |
| Notion DB | 모바일에서도 조회, 마스터 카탈로그 |

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
