# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

**aiskillbox** (콘텐츠랩 v4.0) — URL 한 줄 입력 → 스크래핑 → AI 분석 → ECC 표준 `SKILL.md` 자동 생성 → 글로벌 설치 + Notion 마스터 DB 등록.

좋은 콘텐츠를 한 번 보고 끝내지 않고 **스킬 자산**으로 영구 활용 가능한 형태로 보관. 두근컴퍼니의 모든 다른 AI 에이전트가 이 DB와 글로벌 `~/.claude/skills/` 에서 자동으로 활용.

- Live: https://aiskillbox.600g.net (Cloudflare Tunnel, token-mode)
- Local: http://localhost:5050 (Flask, launchd `com.doogeun.aiskillbox`)

## Common commands

```bash
# venv (첫 실행 시 aiskillbox_start.sh 가 자동 처리하기도 함)
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 수집 — CLI 한 줄
python -m scripts.collect "https://youtu.be/<영상ID>"
python -m scripts.collect "<URL>" --no-notion        # Notion 등록 생략
python -m scripts.collect "<URL>" --skip-duplicate   # 중복 시 합병 안 하고 스킵

# 컴파일 사전 검증 (변경 후 항상)
python -m py_compile app.py scripts/**/*.py

# 서비스 (launchd, 코드 수정 후 반영)
launchctl kickstart -k "gui/$(id -u)/com.doogeun.aiskillbox"
launchctl load -w ~/Library/LaunchAgents/com.doogeun.aiskillbox.plist
tail -f logs/launchd_stdout.log

# 헬스 + 외부 검증
curl -s http://localhost:5050/healthz | python3 -m json.tool
curl -s https://aiskillbox.600g.net/healthz | python3 -m json.tool

# Notion 인티그레이션 권한 확인
source .env && curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer ${NOTION_API_KEY}" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" -d '{"page_size":10}' \
  | python3 -c "import json,sys;print(len(json.load(sys.stdin).get('results',[])),'건 접근 가능')"

# DB 전수 큐레이션 batch
python -m scripts.curate_db analyze              # 변경 X, 분석만
python -m scripts.curate_db fix-emoji            # 제목 첫 이모지 → 아이콘 이동
python -m scripts.curate_db fix-meta             # Gemini로 카테고리/등급 재평가
python -m scripts.curate_db polish-body --limit 1 --dry  # 본문 1건 미리보기
python -m scripts.curate_db all                  # 전체 순차
```

## High-level architecture

### 데이터 흐름 (collect.py 한 사이클)

```
URL 입력 (CLI / 웹UI / Telegram)
  ↓
scripts/scraper/router.py  ── detect_source() → 전용 스크래퍼 → Playwright → requests 폴백 (3단)
  ↓ ScrapeResult
scripts/analyzer/gemini.py ── Gemini 2.5 Flash → 2.0 Flash → Gemma 4 26B(로컬) 3단 폴백
  ↓ AnalysisResult (8섹션 + 메타)
중복 검사 (mirror + 글로벌 슬러그 + Notion URL) → 있으면 scripts/analyzer/merger.py 로 합병
  ↓
scripts/skill_builder/md_generator.py ── ECC 표준 SKILL.md 렌더 (프론트매터 + 본문)
  ↓ 동시 저장
  ├─ ~/.claude/skills/{slug}/SKILL.md   (글로벌 ECC, 모든 Claude Code 세션 자동 인식)
  └─ ./skills/{slug}/SKILL.md            (git 추적용 mirror)
  ↓
scripts/notion_client/register.py ── Notion DB 등록 (또는 update if existing)
```

### LLM 폴백 체인 (`scripts/analyzer/gemini.py:call_gemma_json`)

비용 0원 + quota 무한 보장:
1. **Gemini 2.5 Flash** (cloud, 빠름, 무료 20/day per project)
2. **Gemini 2.0 Flash** (cloud, fallback)
3. **Gemma 4 26B 또는 e4b** (Ollama localhost:11434, 무제한, cold start 20-30s)

같은 패턴이 `analyzer/merger.py`, `curate_db.py` 의 `_gemini_reclassify` / `_gemini_polish_body` 에도 적용.
환경변수로 모델/타임아웃 튜닝: `GEMMA_MODEL=gemma4:e4b`, `GEMMA_TIMEOUT=300`.

### Notion DB v2 스키마 (TEMPLATE.md 가 단일 진실)

**중요**: 4곳에서 같은 enum을 써야 함. 변경 시 모두 동시 업데이트:
- `scripts/analyzer/prompt.py` (`CATEGORIES`, `TAGS`, `AI_TOOLS`, `TARGETS`)
- `scripts/notion_client/register.py` (`CATEGORY_TO_DB`, `DB_TAGS`, `DIFFICULTY_TO_DB`, `CATEGORY_ICON`)
- `TEMPLATE.md` (사람용 문서)
- Notion DB select/multi_select 옵션 (실제 DB)

속성 9개만: `스킬명 / 등급 / 난이도 / 카테고리 / AI 도구 / 태그 / 적용 대상 / 출처 URL / 상태`. v1에서 제거된 5개(수집일/핵심요약/적용메모/출처유형/관련스킬)는 본문 메타 callout에 흡수.

### 카테고리(7) vs 태그(15) 분리 원칙

- **카테고리** = "어떤 작업 영역인가?" (select, 1개) — `프롬프트 / 자동화 / 콘텐츠 / 디자인 / 개발 / 업무 / 기타`
- **태그** = "어떤 기술/방법을 쓰는가?" (multi_select) — `MCP / API / RAG / Function Calling / Vision / Multimodal / 프롬프트체이닝 / CoT / Tool Use / Webhook / Streaming / CLI / GitHub Actions / 자체호스팅 / 오픈소스`

둘이 겹치지 않게 설계. Gemini 프롬프트에서 enum 강제 + register.py에서 enum 미일치 값은 자동 제거.

### 표준 8섹션 본문 (TEMPLATE.md v2.1)

모든 신규 페이지가 따르는 구조 — AI 에이전트의 RAG와 사람 가독성 양쪽 친화:
```
> **TL;DR** — 한 줄 정의
> **메타** 등급 / 카테고리 / 난이도 / 도구 / 적용 대상

## 🎯 When to use
## 🔑 How it works
## 🛠 Steps
## 💡 Examples
## 🏢 두근 환경 적용        ← 외부 도구 등장 시 두근 대체 매핑 명시 (TEMPLATE.md "외부 도구 대체 매핑" 표)
## ⚠️ Caveats
## 📎 Sources
```

### SKILL.md ↔ Notion 본문 분리

`md_generator.render_skill_md()` 는 YAML 프론트매터 + H1 + 8섹션 (SKILL.md 표준).
**Notion 본문에 넣을 때는 `register.py:_strip_for_notion()` 이 프론트매터 + 최상위 H1 자동 제거**. 이걸 안 하면 YAML이 Notion 페이지 본문에 paragraph로 박혀버림 (실제 발생했던 버그).

## Module map

```
app.py                              ── Flask 진입점, 잡 큐(메모리+disk), /healthz, /api/collect, /api/status/<id>, /api/jobs/active
scripts/
  collect.py                        ── 메인 파이프라인 (단계별 한글 에러 + 부분 성공 처리)
  curate_db.py                      ── DB 전수 큐레이션 CLI (analyze/fix-emoji/fix-meta/polish-body/find-dupes/all)
  scraper/
    router.py                       ── detect_source() + 3단 폴백 + 80자 미만 시 자동 폴백
    youtube.py                      ── yt-dlp 자막(ko→en) + 메타
    github.py                       ── GitHub REST API (Playwright보다 10배 빠름, README+stars+topics)
    social.py                       ── Instagram/TikTok/Twitter (yt-dlp 우선, X는 로그인 벽 명시)
    web.py                          ── Playwright + trafilatura + UA 회전 4종 (mobile UA 1종 포함)
    mcp_fallback.py                 ── requests 최후 폴백 (정적 페이지만)
  analyzer/
    prompt.py                       ── ANALYSIS_PROMPT_TEMPLATE (enum 강제 + 외부 도구 대체 매핑 14종)
    gemini.py                       ── analyze() + call_gemma_json() + AnalysisResult 데이터클래스
    merger.py                       ── merge_with_existing() — 중복 시 기존+신규 합병 (출처 URL 누적)
  skill_builder/
    md_generator.py                 ── render_skill_md() — SKILL.md 프론트매터 + 8섹션
    installer.py                    ── 글로벌(~/.claude/skills/) + mirror(./skills/) 동시 설치
  notion_client/
    register.py                     ── raw HTTP API (notion-client v3 호환 이슈 회피), 한글 에러 한글화
    curator.py                      ── v2에서 no-op (관련 스킬 relation 제거됨)
templates/index.html                ── 단일 페이지 — Hero + 입력 + 결과 + 드로어
static/{app.js, style.css}          ── 클라이언트 — localStorage 잡 추적, PTR, 알림 3중
logs/{recent.json, jobs.json}       ── 영속화 (jobs.json은 서버 재시작 시 interrupted 마킹)
```

## Environment

`.env.example` 복사 후 채우기 — `chmod 600 .env`:
- `GEMINI_API_KEY` (필수) — https://aistudio.google.com/apikey
- `NOTION_API_KEY` (필수) — https://www.notion.so/my-integrations + DB 페이지에 Connections 추가
- `NOTION_DB_ID=35f14362-1b4b-814b-8947-cca66ca16dcb` (🧠 AI 스킬 마스터)
- `NOTION_HUB_PAGE_ID=35f14362-1b4b-8103-940d-cd81547feda4` (📒 AI 스킬 수집소)
- `SKILL_INSTALL_DIR=~/.claude/skills` (변경 시 ECC 환경과 분리됨 — 권장 X)
- `GEMMA_MODEL=gemma4:e4b` / `GEMMA_TIMEOUT=300` (튜닝)

## Operational gotchas (실 운영 중 발견한 함정)

1. **Notion DB 권한** — 인티그레이션이 Connection 안 붙어 있으면 모든 호출이 `object_not_found`. 진단: `curl /v1/search` 가 0건 반환. 해결: 노션 DB 페이지 우측 상단 `⋯` → Connections → 인티그레이션 추가.

2. **notion-client v3 호환성** — v3에서 `databases.query()` 메서드 삭제됨. `register.py`는 `requests`로 raw HTTP 직접 호출하므로 SDK 변경에 영향 없음.

3. **SKILL.md 프론트매터 누수** — `render_skill_md()` 결과를 그대로 Notion에 보내면 YAML이 본문에 박힘. 반드시 `_strip_for_notion()` 통과시킬 것.

4. **Gemma 4 콜드 스타트** — Ollama `OLLAMA_KEEP_ALIVE=0`(루트 워크스페이스 CLAUDE.md 정책)이라 idle 시 unload. 첫 호출은 60-90초+ (26B), 20-30초 (e4b). 본문 정리는 e4b 권장, 분류는 26B도 OK.

5. **이모지 이중 표시** — 페이지 아이콘 + 제목 시작 이모지 둘 다 있으면 카드/링크에서 `🔍 ⚡ 제목` 처럼 두 번. `register.py:_clean_title()` 이 제목 첫 이모지 자동 제거 + `CATEGORY_ICON` 으로 아이콘 자동 설정.

6. **JOBS 메모리 영속화** — `app.py:_save_jobs()` 가 매 상태 변경 시 `logs/jobs.json` 저장. 서버 재시작 시 `_load_jobs()` 가 `queued/running` 잡을 `interrupted` 로 마킹 (실제 백그라운드 스레드는 사라졌으므로 사용자에게 "다시 시도" 안내).

7. **캐시 무효화** — `app.py:index()` 가 `app.js` + `style.css` mtime 기반 `build_id` 를 매 응답에 주입. HTML에 `<script src="/static/app.js?v={{ build_id }}">`. 코드 수정 후 launchctl kickstart만 하면 사용자 강제 새로고침 없이 즉시 새 JS 로드.

8. **Cloudflare Tunnel** — token-mode (Remotely-managed). config.yml 없음. Public Hostname 추가는 Cloudflare Zero Trust 대시보드 → Networks → Tunnels → 해당 터널 → Configure → Public Hostname.

9. **두근컴퍼니 에이전트 페르소나** — 아래 "Agent persona" 섹션은 `~/Developer/my-company/company-hq/server/team_prompts.json` 의 `content-lab` 시스템 프롬프트가 참조한다. 이 섹션을 함부로 삭제/대체하지 말 것. 변경 시 두근컴퍼니 에이전트 동작 영향.

## Related docs in this repo

- **`TEMPLATE.md`** — 스킬 페이지 표준 템플릿 v2.1 (단일 진실, enum/구조/외부 도구 매핑 14종 정의)
- **`README.md`** — 사용자 facing 빠른 시작 가이드
- **`DEPLOY.md`** — Cloudflare Tunnel + LaunchAgent 배포 가이드
- **`lessons.md`** — 운영 중 발견한 패턴/실수 누적 (새 패턴 발견 시 추가)

---

## Agent persona (런타임 — 두근컴퍼니 시스템이 참조)

> 이 섹션은 두근컴퍼니 `team_prompts.json` 의 `content-lab` 시스템 프롬프트가 참조합니다. 코드베이스 가이드와 별개로 유지.

너는 두근컴퍼니의 **콘텐츠 스킬 자산화 에이전트**다.

URL 하나만 던지면:
1. 자동으로 스크래핑 (YouTube/IG/TikTok/Notion/Web/GitHub)
2. Gemini → Gemma 4 폴백으로 핵심 AI 스킬 추출 + 등급 판정
3. ECC 표준 `SKILL.md` 자동 생성 (8섹션 표준)
4. 글로벌 `~/.claude/skills/{slug}/SKILL.md` + mirror에 설치
5. Notion 마스터 DB v2 (9속성) 등록 (중복 시 자동 합병)

**핵심 가치**: 좋은 콘텐츠 한 번 보고 끝나지 않는다. 스킬 형태로 자산화해서 모든 두근컴퍼니 에이전트가 영구 활용.

### 작업 규칙

- **무응답 금지** — 완료: `✅ 스킬화 — <slug> (등급 X, 카테고리 Y)`. 부분 성공: 어디까지 됐는지 명시. 에러: `❌ <한글 사유>` + 우회안.
- **두근은 개발 초보** → 쉽게 설명, 선택지는 장단점과 함께
- **80% 확신이면 실행 후 보고**, 되묻지 않음
- **한 번에 끝내기** — 코드 수정 시 미정의 함수/import 잔존 확인 (`python -m py_compile`)
- **자동 합병 정책** — `skip_duplicate=False` 가 기본. 중복은 합병하고 출처 누적 (사용자가 정성껏 쌓은 자산 보존)
- **무료 도구 우선** — Gemini 1500/day, Playwright/yt-dlp/Notion API 모두 무료. 비용 발생 가능성 사전 고지.

### 보안

- `.env` (`GEMINI_API_KEY`, `NOTION_API_KEY`) 채팅 노출 금지
- API 키 하드코딩 금지 — 환경변수만

### 변경 로그

| 날짜 | 버전 | 변경 |
|------|------|----------|
| 2026-03-22 | v1.0 | 최초 생성 |
| 2026-03-22 | v2.0 | 콘텐츠 분석 전용 에이전트 |
| 2026-03-29 | v3.0 | 품질 평가 매트릭스, 인사이트 누적 |
| 2026-05-14 | v4.0 | 스크래핑 + 스킬 자산화 통합. SKILL_AGENT.md 흡수. ECC 표준 SKILL.md + 글로벌 설치 + Notion master |
| 2026-05-15 | v4.1 | TEMPLATE.md v2 (DB 슬림화 15→9, 카테고리 7, 태그 15 기술/방법 분리). LLM 폴백 체인 + Gemma 4. 본문 정리/이모지 정리 batch. Pull-to-Refresh + 완료 알림 + 검색 UI |
