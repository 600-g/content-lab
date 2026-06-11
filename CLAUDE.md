# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

**aiskillbox** (콘텐츠랩 v4.3) — URL 한 줄 입력 → 스크래핑 → AI 분석 → ECC 표준 `SKILL.md` 자동 생성 → 글로벌 설치 + Notion 마스터 DB 등록. 제출은 순차 큐로 비차단 처리, 완료 시 Web Push 알림.

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

# v2.3 보편 정보 템플릿 전환 워크플로 (DB 정리 — 항상 백업부터)
python -m scripts.backup_all                                    # 1) 백업 (logs/backup_v27_{date}/)
python -m scripts.audit_loss                                    # 2) 손실 점검 (백업 vs 현재 노션)
python -m scripts.audit_pages                                   # 3) 가독성/일관성 종합 점검
python -m scripts.rebuild_template --engine gemma               #    dry-run (LLM 재작성 미리보기)
python -m scripts.rebuild_template --engine gemma --apply       #    적용 (캐시 자동 사용, 100단위 chunk)
python -m scripts.rebuild_template --engine gemma --apply --use-cache  # 캐시만 사용 (LLM 재호출 X)
python -m scripts.rebuild_template --engine gemma --apply --only 옵시디언 --min-score 0.65  # 단일 + 임계값 조정
python -m scripts.recategorize --apply                          # 카테고리 재분류 + 아이콘 동기화
python -m scripts.rename_headings --apply                       # H2 헤더 한글 친화 통일
python -m scripts.demote_h2_to_h3 --apply                       # 비표준 H2 → H3 강등
python -m scripts.strip_meta_quotes --apply                     # TL;DR/메타 quote 박스 제거
python -m scripts.restore_from_backup --apply "키워드"           # 백업에서 원본 raw_blocks 복원 (LLM 변환 실패 시)
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

### 표준 본문 구조 (v2.3 보편 정보, 2026-05-18)

**v2.1 (8섹션 + TL;DR/메타 quote 박스) → v2.3 (callout + 보편 정보 + 한글 친화) 전환 완료**.

`scripts/rebuild_template.py:REBUILD_PROMPT` 가 단일 진실. 모든 페이지가 따르는 형태:

```
💡 [callout] 이 스킬은 [무엇]을 [어떻게] 하는 [도구/방법]입니다. [한 줄 가치 제안].
            (Notion callout 블록, 파란 배경 + 💡 아이콘, bold 강조)

## 🔑 어떻게 작동하나요?   ← 메커니즘/원리 (긴 경우 ### H3 분할)
## 🛠 따라 하기 (단계별)   ← numbered list (**굵은 짧은 라벨**: 설명)
## 💡 실제 예시            ← 표/코드/대화 (코드는 [[CODE_BLOCK_N]] placeholder 로 보호)
## ⚡ 이렇게 쓰면 효과적이다 ← 추천 시점 / 시너지 도구 / 수익화 가능성 / 적용 난이도 (보편 권장)
## ⚠️ 주의할 점            ← 한도/유료/실패 케이스
## 📎 출처
(필요시) ## 📌 원본 코드/명령어 (자동 보존) ← placeholder 누락된 코드 자동 rescue
```

**v2.1 → v2.3 핵심 변경**:
- `> **TL;DR** —` quote 박스 제거 → **💡 callout** 으로 시각 임팩트
- `> **메타** ...` quote 박스 제거 → DB properties 와 중복이라 폐지 (등급/카테고리/난이도/도구/대상은 우상단 properties 가 단일 진실)
- 영문 부제 (When to use / How it works / Steps / Examples / Caveats / Sources) 모두 제거 → 한글 친화 헤더만
- `## 🏢 두근 환경 적용` → `## ⚡ 이렇게 쓰면 효과적이다` (두근 프로젝트 강제 매핑 폐기 — 보편 정보로)
- bold (`**`) 적극 활용 — 핵심 명사·도구명·숫자
- 긴 섹션은 `###` H3 소제목 분할 권장

**보편 정보 원칙**: 두근컴퍼니/두근펫/매매봇/검은별/클로드코드/AI900/첼시인스타 같은 개인 프로젝트 매핑 강제 X. 다른 사용자·AI 가 RAG 로 읽고 자체 판단할 수 있게. `feedback_skill_pages_universal.md` 메모리 참조.

### 코드 보호 placeholder 패턴 (`scripts/rebuild_template.py`)

LLM 재작성 시 코드블록/인라인 코드/단축키 손실 방지:

1. **추출 단계** (`protect_code`): `\`\`\`...\`\`\`` 와 `` `...` `` 를 본문에서 추출 → `[[CODE_BLOCK_N]]` / `[[INLINE_N]]` 토큰으로 치환
2. **LLM 호출**: placeholder 포함된 텍스트 전달 (프롬프트에 "이 토큰은 절대 수정/번역/삭제 금지" 명시)
3. **복원 단계** (`restore_code` + `_PLACEHOLDER_RE` fuzzy): LLM 출력에서 placeholder 자리에 원본 코드 그대로 삽입. LLM 이 토큰명 변형 (`[[CON_7]]`, `[[CB_N]]`) 해도 fuzzy 매칭으로 복원
4. **누락 자동 rescue**: 매칭 실패한 placeholder 의 원본 코드 → 페이지 끝 `## 📌 원본 코드/명령어 (자동 보존)` 섹션에 자동 추가 — 데이터 손실 0

이 패턴 덕분에 LLM paraphrase 강도와 무관하게 코드/명령어/단축키는 100% 보존.

### LLM 보존율 검증 (`scripts/rebuild_template.py:preservation_score`)

- 원본 markdown 에서 한글 3자+ / 영문 5자+ 핵심 키워드 추출 (빈도 top 40)
- LLM 출력에 몇 % 보존됐는지 측정
- **임계값 기본 0.70** (`--min-score` 로 조정). 미달 시 자동 skip → 페이지 안 건드림
- 임계값 미달 페이지 → `restore_from_backup.py` 로 원본 그대로 복원 (정보 보존 우선)
- `STOPWORDS` 에 두근 개인 프로젝트명 포함 — 보편 정보 변환 시 의도적으로 빠지는 키워드는 누락 카운트 X

### SKILL.md ↔ Notion 본문 분리

`md_generator.render_skill_md()` 는 YAML 프론트매터 + H1 + 8섹션 (SKILL.md 표준).
**Notion 본문에 넣을 때는 `register.py:_strip_for_notion()` 이 프론트매터 + 최상위 H1 자동 제거**. 이걸 안 하면 YAML이 Notion 페이지 본문에 paragraph로 박혀버림 (실제 발생했던 버그).

## Module map

```
app.py                              ── Flask 진입점. 순차 잡 큐(단일 워커 스레드 + queue.Queue),
                                        /healthz, /api/collect, /api/status/<id>, /api/jobs/active,
                                        /api/push/*, /api/settings*, /sw.js (루트 스코프 SW 서빙)
scripts/
  collect.py                        ── 메인 파이프라인 (단계별 한글 에러 + 부분 성공 처리)
  push.py                           ── Web Push — VAPID 로드 + 구독 저장(logs/push_subscriptions.json) + send_push (죽은 구독 자동 정리)
  settings_store.py                 ── .env 안전 읽기/쓰기 (주석·순서 보존). 설정 창 PIN 보호 API 가 사용
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
  # DB 정리/마이그레이션 (2026-05-18 추가) — 모두 dry-run 기본, --apply 명시 필요
  backup_all.py                     ── 전체 페이지 raw_blocks JSON + markdown 백업 (logs/backup_v27_{date}/)
  rebuild_template.py               ── 코어. LLM (Gemma 26B / Gemini) 으로 v2.3 보편 정보 재작성 + 코드 보호 placeholder + 보존율 검증 + 페이지 끝 rescue 섹션. --use-cache 옵션으로 LLM 재호출 생략
  restore_from_backup.py            ── 백업 raw_blocks 그대로 페이지에 복원 (LLM 변환 실패 시 안전망). null 필드 제거 필수
  recategorize.py                   ── LLM 으로 카테고리 자동 분류 + 페이지 아이콘 동기화
  rename_headings.py                ── H2 헤더 텍스트 정규화 (영문 부제 제거, 한글 친화로 통일)
  demote_h2_to_h3.py                ── 표준 8섹션 외 H2 → H3 강등 (LLM 출력에서 sub-section 이 H2 로 박힌 경우)
  strip_meta_quotes.py              ── 첫 heading 이전 quote + divider 일괄 제거 (v2.1 → v2.3 메타 박스 폐기)
  fix_visual.py                     ── 정적 cleanup (list dump / 빈 paragraph / HTML 잔재 / 빈 quote / 중복 quote / 빈 헤더 제거)
  audit_pages.py                    ── 가독성/일관성 종합 점검 (표준 헤더 / 빈 섹션 / code language / 아이콘 매핑)
  audit_loss.py                     ── 백업 vs 현재 노션 — 코드/명령어/단축키 손실 검사 (false positive 보정: rich_text annotations.code 처리)
templates/index.html                ── 단일 페이지 — Hero + 입력 + 작업 큐 리스트 + 설정 모달 + 드로어
static/{app.js, style.css}          ── 클라이언트 — 비차단 제출, 다중 잡 큐 UI, PIN 설정창, Web Push 구독
static/sw.js                        ── 서비스워커 — push/notificationclick 핸들러 (백그라운드 알림)
logs/{recent.json, jobs.json}       ── 영속화 (running 잡은 재시작 시 interrupted, queued 잡은 재투입)
logs/push_subscriptions.json        ── Web Push 구독 (브라우저 PushSubscription JSON 목록, gitignore)
logs/backup_v{25,26,27}_{date}/     ── 단계별 백업. v27 은 raw_blocks JSON 포함 (복원용)
logs/rebuild_v27_{date}/            ── LLM 재작성 결과 markdown 캐시 ({pid}__{slug}.md). --use-cache 시 재사용
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

6. **JOBS 메모리 영속화 + 순차 큐** — `app.py:_save_jobs()` 가 매 상태 변경 시 `logs/jobs.json` 저장. 잡은 **단일 워커 스레드**가 `queue.Queue` 에서 하나씩 꺼내 순차 처리 (동시 실행 X — Gemma 26B 동시 호출로 인한 메모리 압박 방지). 서버 재시작 시 `_load_jobs()` 가 `running` 잡은 `interrupted` 마킹, `queued` 잡은 그대로 두고 `_requeue_pending()` 가 큐에 재투입 (started_at 순). `/api/collect` 는 큐에 넣고 즉시 반환 — 클라이언트 입력칸이 바로 비고 다음 URL 을 계속 넣을 수 있음.

7. **캐시 무효화** — `app.py:index()` 가 `app.js` + `style.css` mtime 기반 `build_id` 를 매 응답에 주입. HTML에 `<script src="/static/app.js?v={{ build_id }}">`. 코드 수정 후 launchctl kickstart만 하면 사용자 강제 새로고침 없이 즉시 새 JS 로드.

8. **Cloudflare Tunnel** — token-mode (Remotely-managed). config.yml 없음. Public Hostname 추가는 Cloudflare Zero Trust 대시보드 → Networks → Tunnels → 해당 터널 → Configure → Public Hostname.

9. **두근컴퍼니 에이전트 페르소나** — 아래 "Agent persona" 섹션은 `~/Developer/my-company/company-hq/server/team_prompts.json` 의 `content-lab` 시스템 프롬프트가 참조한다. 이 섹션을 함부로 삭제/대체하지 말 것. 변경 시 두근컴퍼니 에이전트 동작 영향.

10. **Notion API write 시 `null` 필드 제거 필수** — 페이지 fetch (read) 응답에는 `paragraph.icon: null` 같은 필드가 들어있는데 API write 가 이걸 reject (`should be an object or undefined`). `restore_from_backup.py:_strip_nulls()` 가 재귀적으로 None 제거 후 PATCH. raw_blocks 백업 그대로 보내면 안 됨.

11. **Notion code block language enum 매핑** — `code.language` 는 Notion 이 정한 enum 안에서만 허용. LLM 이 임의 언어 (예: `text`, `tsv`, `console`) 출력하면 reject. `rebuild_template.py:NOTION_CODE_LANGS` + `_LANG_ALIASES` + `_normalize_code_lang()` 가 안전하게 매핑 (모르면 `plain text`).

12. **Notion 인티그레이션 권한은 페이지별** — 마스터 DB 에 Connection 추가했어도 같은 워크스페이스 다른 페이지에는 자동 상속 안 됨. 외부 page id 가 `2e91...` 같이 다른 prefix 면 별도 권한 추가 필요. 또는 Playwright 로 public share view scrape.

13. **Notion page id prefix 충돌** — 같은 DB row 페이지들은 첫 8자 같음 (`35f14362-...`). 백업 파일명에 `pid[:8]` 만 쓰면 모든 파일이 같은 prefix → glob 매칭이 첫 1개만 반환 → **다른 페이지 본문이 잘못된 페이지에 박힘** (실 발생 버그). `backup_all.py` 와 `rebuild_template.py` 는 항상 **전체 32자** 사용.

14. **delete 후 append 패턴의 위험** — `rebuild_template.py:replace_h2_with_h3` 와 페이지 children 교체 시: `delete_all_children()` 다음 `append_blocks()`. 만약 append 가 validation 으로 실패하면 **페이지가 통째로 비어버림**. → `restore_from_backup.py` 즉시 실행으로 복원. append 실패 사유는 보통 (10), (11) 케이스.

15. **LLM 보편 정보 변환 한계** — 본문이 짧거나 광고성/특수 표현 위주 페이지는 보존율 0.40 미만으로 떨어짐 (실 사례: "클로드 MCP 메타 광고 자동화" 36%). 무리하게 변환하면 정보 손실 큼. 임계값 미달 페이지는 자동 skip → `restore_from_backup.py` 로 원본 보존 처리.

16. **노션 DB row 는 사이드바에 펼쳐 보임** — 노션 UI 가 "허브 페이지 → DB → row 페이지" 트리를 사이드바에 자동 expand. 사용자가 "외부 페이지 여러 개 생긴" 줄 오해할 수 있음. 실제 구조는 `허브 1 + DB 1 + DB.rows = 페이지 수`. `/v1/search` 결과로 검증 가능.

17. **Web Push 는 HTTPS + 서비스워커 필수** — `new Notification()` 은 페이지가 떠 있을 때만 동작 → 백그라운드면 알림이 멈춤. 진짜 백그라운드 알림은 VAPID 키쌍(`.env`) + `static/sw.js` + 서버 발송(`scripts/push.py`). `/sw.js` 는 **루트 스코프**로 서빙해야 `/` 전체를 제어 (`Service-Worker-Allowed: /` 헤더). **iOS 는 홈화면에 추가한 PWA (16.4+) 에서만** Web Push 동작 — Safari 탭에서는 `Notification` 자체가 없음. 권한 요청은 반드시 사용자 제스처(제출/버튼) 안에서.

18. **설정 창 PIN 보호** — aiskillbox 는 `aiskillbox.600g.net` 으로 공개되고 앱 자체 인증이 없다. API 키 편집 엔드포인트(`/api/settings*`)는 `.env` 의 `ADMIN_PIN` 으로 보호 — `X-Admin-Pin` 헤더, `hmac.compare_digest` 상수시간 비교, 5회 실패 시 5분 잠금. 키 값은 응답에서 항상 마스킹(`settings_store.mask`). 새 비밀/공개 엔드포인트 추가 시 같은 PIN 게이트를 반드시 통과시킬 것.

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
| 2026-05-25 | v2.4 템플릿 | **폼 규칙화 폐지** — 본문 7섹션 강제 X, 원본의 자연스러운 결대로 자유 형식 (`body_md`). **속성 가지치기**: Notion DB 9속성 → 6속성 (스킬명/카테고리/등급/난이도/AI 도구/출처). 태그·적용대상·상태·날짜·tldr quote 박스·메타 stripe·30초 핵심 박스·이모지 아이콘 prefix 전부 제거. **강한 제목 + 💡 1줄**로 5초 안에 "각이 잡히게". `scripts/convert_v24.py` 로 디스크 22건 + Notion DB 일괄 정렬. `prompt.py` v2.4 (8-15자 동사형 제목, body_md 자유 형식). `md_generator.py` lean (frontmatter flat 6키 + # 제목 + 💡 + body + ## 출처). |
| 2026-05-23 | v4.3 | **순차 잡 큐** — 요청마다 스레드 생성 → 단일 워커 + `queue.Queue` 순차 처리. 제출 즉시 입력칸 비움 + 비차단(다음 URL 계속 입력 가능) + 다중 잡 큐 UI. **Web Push** — VAPID + `static/sw.js` + `scripts/push.py`, 앱 백그라운드여도 완료 알림. **설정 창** — PIN(`ADMIN_PIN`) 보호 API 키 편집 UI (`scripts/settings_store.py`, `/api/settings*`). Gemma 폴백 버그 수정 (`call_gemma_json` think:false + num_ctx 16384 — JSON 필드 누락 root cause). `mcp_fallback.py` ImportError 수정 (`_extract_text` → `_bs4_extract`). |
| 2026-05-18 | v4.2 | **v2.3 보편 정보 템플릿** 전환. TL;DR/메타 quote 박스 폐기 (DB properties 중복) → 💡 callout. 영문 부제 제거 → 한글 친화 헤더 (어떨 때 쓰나요? / 어떻게 작동하나요? / 따라 하기 / 실제 예시 / 이렇게 쓰면 효과적이다 / 주의할 점 / 출처). 두근 프로젝트 강제 매핑 폐기 → 보편 정보로 정리. 코드 보호 placeholder 패턴 (`[[CODE_BLOCK_N]]` / `[[INLINE_N]]` + fuzzy restore + 페이지 끝 rescue 섹션). 보존율 검증 (한글 3+ / 영문 5+ 핵심 키워드 빈도). DB 정리 스크립트 11종 추가 (backup_all/rebuild_template/restore_from_backup/recategorize/rename_headings/demote_h2_to_h3/strip_meta_quotes/fix_visual/audit_pages/audit_loss). 카테고리 재분류 (LLM 자동) + 페이지 아이콘 동기화 |
