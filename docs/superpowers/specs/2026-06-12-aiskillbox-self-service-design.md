# aiskillbox 자가 운영(self-service) 업그레이드 설계

작성일: 2026-06-12 · 대상: `~/Developer/my-company/content-lab/` (aiskillbox v4.3 → v5.0)

## 1. 동기

장기적으로 Claude(나) 의 손을 거치지 않고도 사용자가 직접 aiskillbox 의
운영·튜닝·데이터 정리를 할 수 있어야 한다. 동시에 운영 중 발견된 두 가지 문제를 함께 해결한다:

- **인스타그램 피드(`/p/`) 스크랩 실패** — 로그아웃 상태 IG 의 본문 추출 한계
- **Notion 의미 중복** — 현재 dedup 이 URL 완전일치만 인식해 같은 주제·다른 URL 스킬이
  중복으로 살아남음 (예: `higgsfield-mcp-claude-ad-generation` ↔ `product-soft-sell-visual-content-generation`)

## 2. 범위와 비범위

**범위 (이 spec 에서 다룬다)**
- IG 피드 사전 차단 가드
- 의미 임베딩 기반 dedup
- 기존 ~/.claude/skills/ 146개 일괄 dedup 스캔
- 앱 내 자연어 운영·설정 채팅 (Opus 4.8)

**비범위**
- IG 쿠키 주입 기반 로그인 스크랩 (계정 정지 리스크)
- 코드 본체(`app.py`, `scripts/scraper/*`, `scripts/analyzer/*`) 의 자연어 편집 — 채팅은
  설정/룰/SKILL.md 까지만 손댄다
- Web Push / launchd plist / Cloudflare Tunnel 설정 — 본 spec 밖

## 3. 기능 단위

### 3.1 IG 피드 가드 (작업 #1)

**문제.** `instagram.com/p/...` 는 Meta 의 로그인 벽 때문에 로그아웃 상태에서는
캡션·캐러셀 본문이 ~117자 (메타 데이터만) 만 받힌다. 그 결과 Gemini 분석이 빈약한 입력으로
JSON 을 헛 생성하고 파싱 실패 → 잡 죽음. (2026-06-10 23:41 실측 케이스)

**해결.** `scripts/scraper/router.py` 의 instagram 분기 입구에서 URL 패턴 판별 후
사전 차단:

- `instagram.com/p/...` 또는 `instagram.com/reel/` 중 yt-dlp 가 실패한 경우
  → `ScrapeResult(text="", skip_reason="ig_login_wall")` 반환
- `collect.py` 가 `skip_reason` 을 보면 Gemini 호출 / Notion 등록 모두 건너뛰고
  사용자에게 한글 안내 메시지 반환:
  > "이 링크는 인스타그램 피드 포스트라 로그인 없이는 본문을 못 가져옵니다. 캡션을
  > 직접 붙여넣거나 스크린샷 → 텍스트로 변환해 등록해 주세요."

**구현 위치.**
- `scripts/scraper/router.py` (instagram 분기에 가드 추가, ~10 라인)
- `scripts/scraper/__init__.py` 의 `ScrapeResult` 데이터클래스에 `skip_reason: str | None = None` 필드 추가
- `scripts/collect.py:124` 부근에서 `skip_reason` 분기 처리

**테스트.** `python -m scripts.collect "https://www.instagram.com/p/DZPjiWcD6t2/"` →
한글 안내 메시지로 깔끔 종료, Notion 등록 X, 잡 상태 `skipped` (실패 아님).

---

### 3.2 의미 임베딩 dedup (작업 #2)

**문제.** 현재 `scripts/skill_builder/installer.py:find_existing_by_url(url)` 는 URL
완전일치만 합병. 같은 주제·다른 URL 은 신규 스킬로 등록됨. 결과:
`contextual-prompt-engineering` / `context-based-prompt-engineering` /
`context-rich-prompting` 세 개가 사실상 동일 주제로 살아있음.

**해결.** Gemini `text-embedding-004` 기반 의미 임베딩 + 코사인 유사도 dedup.

**컴포넌트.**

| 모듈 | 책임 |
|---|---|
| `scripts/analyzer/embedder.py` | `embed(text: str) -> list[float]`. Gemini `text-embedding-004` 호출. 실패 시 None 반환 (dedup 스킵 → 신규 등록, 안전 폴백). |
| `scripts/skills/embeddings.json` | `{slug: {"vec": [...], "hash": "<sha256-of-callout>", "updated_at": "iso"}}` 캐시. callout 변경 시 hash 비교로 재계산. |
| `scripts/analyzer/dedup_finder.py` | `find_semantic_candidates(new_analysis) -> list[(slug, score)]`. `DEDUP_COMPONENTS` 가 지정한 필드(기본 `["callout", "ai_tools", "category"]`)를 concat → embed → 전체 cache 와 cosine. 임계값 `DEDUP_THRESHOLD`(기본 0.80) 이상 후보 top-3 반환. |

**합병 흐름 변경 (`scripts/collect.py:144` 부근).**

```text
URL 일치 합병 (기존 로직, 유지)
   ↓ 매칭 없으면
[NEW] dedup_finder.find_semantic_candidates(analysis)
   ↓ 임계값 이상 후보 있으면
   merger.merge_with_existing(existing=candidate_slug, new=analysis)  # 기존 merger 재사용
   ↓ 후보 없으면
   신규 등록
```

**튜닝 가능 항목 (config.json).**

```json
{
  "dedup": {
    "enabled": true,
    "threshold": 0.80,
    "components": ["callout", "ai_tools", "category"],
    "top_k": 3
  }
}
```

config.json 은 새로 만든다 (지금까지 .env 만 썼지만, 채팅이 편집할 비밀 아닌 운영
파라미터는 config.json 에 모은다). `app.py` 시작 시 로드, 채팅 도구가 mutate.

**임베딩 비용/한도.** Gemini `text-embedding-004` 무료 1500/일. 신규 스킬당 1 호출 +
일괄 스캔 시 146 호출 → 일일 한도 충분.

**테스트.**
- 캐시 없을 때 → 임베딩 호출 → 캐시 저장 후 재사용 검증
- 유사도 0.85+ 인 페어 있으면 merger 호출 검증
- Gemini 임베딩 실패 → 신규 등록으로 안전 폴백 검증
- `config.json` 의 threshold 변경 → 다음 호출에 즉시 반영

---

### 3.3 기존 146개 일괄 스캔 (작업 #3)

**산출.** `scripts/oneshot/scan_existing_dedup.py` 1회성 스크립트:

1. `~/.claude/skills/*/SKILL.md` 전부 파싱, callout + ai_tools + category 추출
2. 각각 임베딩 → `embeddings.json` 채움
3. 모든 페어 코사인 계산
4. 임계값 0.75 이상 페어 → `inbox/dedup_candidates.md` 리포트 (점수 내림차순)

리포트 형식:
```markdown
| 순위 | 유사도 | A | B | 비고 |
|------|--------|---|---|------|
| 1 | 0.89 | context-based-prompt-engineering | context-rich-prompting | 사실상 동일 |
| 2 | 0.85 | higgsfield-mcp-claude-ad-generation | product-soft-sell-visual-content-generation | 컨셉 겹침 |
...
```

사용자가 리포트 검토 → **채팅으로** "리포트 3번, 7번 합병해줘" 식으로 실행 (작업 #4 와 연계).

**비범위.** 자동 합병 X. 사용자 검토 필수.

---

### 3.4 자가 운영 채팅 (작업 #4, 메인)

**요구.** 앱 우측 하단 플로팅 채팅 → 자연어로 운영 명령 + 설정·룰·SKILL.md 편집.
PIN 0910 + 30분 세션. Opus 4.8 단일 모델.

#### 3.4.1 UI

- 우측 하단 플로팅 버튼 💬 (모바일은 풀스크린, 데스크탑은 우측 사이드패널 360px)
- 메시지 로그 + 입력창
- 응답에 "계획: N단계 · 영향파일: M개" 카드 + [diff 보기] [적용] [취소] 버튼
- 적용 시 PIN 입력 모달 (세션 토큰 없는 경우 한정, 한 번 입력 → 30분 유지)
- 응답 영역 하단에 "최근 실행" 로그 패널 (마지막 5건, 시간·도구·결과 한 줄씩)

#### 3.4.2 백엔드

**디렉토리: `scripts/chat/`**

| 파일 | 책임 |
|---|---|
| `engine.py` | `claude-opus-4-8` 직접 호출. anthropic SDK + `.env:ANTHROPIC_API_KEY`. 시스템 프롬프트는 화이트리스트 도구 목록 + 금지 파일 목록 + 두근컴퍼니 톤. 응답은 SSE 스트리밍. |
| `tools.py` | Anthropic tool use 정의 (아래 표). |
| `safety.py` | PIN 검증 + 30분 세션 토큰. 기존 `app.py:_PIN_GUARD` 재활용. mutating 도구 호출 직전에 토큰 검사. |
| `history.py` | `inbox/chat_history.jsonl` (전체) + `inbox/chat_audit.jsonl` (mutating 만) 영속화. |

**도구 화이트리스트 (Anthropic tool_use schema).**

| 도구 | 종류 | 동작 |
|---|---|---|
| `run_op_command(cmd: enum)` | mutating | 사전 정의된 명령만 실행: `restart_server`, `reinstall_skills`, `kickstart_aiskillbox`, `tail_log`, `gemini_quota_status`. |
| `read_config()` | safe | `config.json` 전체 반환 |
| `write_config(patch: dict)` | mutating | `config.json` 의 `dedup.*`, `ig_block.*` 키만 패치 가능. 다른 키는 거부. |
| `read_skill_md(slug: str)` | safe | `~/.claude/skills/{slug}/SKILL.md` 반환 |
| `edit_skill_md(slug: str, new_body: str)` | mutating | SKILL.md 만. 프론트매터 보존. mirror(`./skills/`) 동시 갱신. |
| `merge_skills(slug_a: str, slug_b: str)` | mutating | `merger.merge_with_existing` 재호출. 결과는 slug_a 에 합쳐지고 slug_b 는 mirror 만 archive 폴더로 이동. |
| `rebuild_embeddings(slugs: list[str] \| "*")` | mutating | embeddings.json 무효화 + 재계산. |
| `recent_jobs(limit: int)` | safe | `logs/jobs.json` 의 최근 잡 요약 |
| `dedup_report()` | safe | `inbox/dedup_candidates.md` 그대로 반환 (작업 #3 결과 조회) |

**금지 (시스템 프롬프트에 명시).** `app.py`, `scripts/scraper/*`, `scripts/analyzer/*`,
`scripts/notion_client/*`, `scripts/skill_builder/*` 의 코드 자체는 손대지 않는다.
요청이 오면 채팅이 한글로 거부:
> "이 작업은 코드 본체 수정이 필요합니다. 클로드 코드에서 직접 진행해 주세요."

**시스템 프롬프트 스켈레톤.**
- 첫 단락: 역할(aiskillbox 운영 보조), 사용자(두근컴퍼니 오너), 톤(한국어, 짧고 명확)
- 도구 카탈로그: 위 표 그대로
- 금지: 위 목록 + 비밀 키 절대 노출 금지 (.env, API 키 raw 값 전송 X)
- 응답 규약: 계획 → diff 미리보기 → 사용자 [적용] 클릭 후에만 실제 mutating 실행

#### 3.4.3 API

| 엔드포인트 | 동작 |
|---|---|
| `POST /api/chat/message` | body `{text, session_token?}` → Opus 호출 → SSE 로 텍스트 청크 + tool_use plan 스트리밍. plan 은 `plan_id` 발급 후 임시 보관 (30분 TTL). |
| `POST /api/chat/apply` | body `{plan_id, pin?}` → PIN 미설정/만료면 401 + `need_pin: true`. 검증 통과 시 plan 의 mutating tool 들 순차 실행. 각 단계 결과 SSE. |
| `GET /api/chat/history` | 최근 50개 메시지 |
| `GET /api/chat/audit` | 최근 50개 mutating 액션 |

세션 토큰: HttpOnly 쿠키 `chat_session=<random32>`. 만료 30분. 갱신은 mutating 도구
호출 시 자동 연장.

#### 3.4.4 PIN 통합

`.env:ADMIN_PIN=0910` (이미 적용 완료, 2026-06-12). 채팅의 mutating 게이트는 기존
`app.py:_check_pin()` 재사용 → 별도 PIN 키 추가 X. 즉 설정 모달과 채팅이 같은 PIN.

#### 3.4.5 영속화

- `inbox/chat_history.jsonl` — 모든 메시지 (user/assistant/tool_use/tool_result)
- `inbox/chat_audit.jsonl` — mutating 실행 결과만 (`{ts, tool, args, ok, summary}`)
- 둘 다 일자별 롤링 (`chat_history_2026-06.jsonl`)
- `.gitignore` 에 추가

#### 3.4.6 토큰 비용 가이드

Opus 4.8 직접 호출이라 토큰 비용 발생. 하루 50회 평균 대화 가정 시 입력 ~250k +
출력 ~50k → 일 약 $10 추정. 채팅 사이드패널 상단에 "이번 달 토큰" 표시 (간단한
세션 카운터, 정확도보단 의식용).

---

## 4. 데이터 마이그레이션

- `config.json` 신규 생성, 기본값 적재
- `embeddings.json` 첫 일괄 스캔 (작업 #3) 으로 채움
- 기존 `.env`, `logs/jobs.json`, `logs/push_subscriptions.json` 영향 없음
- Notion DB 스키마 변경 없음

## 5. 보안

- ANTHROPIC_API_KEY 는 `.env` 에만, 응답 본문에 절대 노출 X
- 채팅 도구는 모두 화이트리스트. 임의 `exec()` / `eval()` / shell 명령 X
- `run_op_command` 의 cmd 는 enum 강제, 임의 문자열 거부
- diff 미리보기를 사용자에게 보여주고 [적용] 클릭 받기 전에는 어떤 mutating 도 일어나지 않음
- 30분 세션 만료 + 5회 PIN 실패 시 5분 잠금 (기존 정책 그대로)
- 외부 PR 등록 / 패스워드 변경 / 사용자 추가 같은 권한 escalation 도구는 화이트리스트에 X

## 6. 단계별 작업 순서

본 spec 승인 후 `writing-plans` 스킬로 세부 작업 분해. 큰 흐름은:

1. IG 피드 가드 (`router.py` + `collect.py`, ~30 라인) — 30분
2. `config.json` 도입 + 로더 (`app.py` 부팅 시) — 30분
3. 의미 임베딩 인프라 (`embedder.py`, `dedup_finder.py`, `embeddings.json`) — 1.5시간
4. 일괄 스캔 + 리포트 (`oneshot/scan_existing_dedup.py`) — 30분
5. 채팅 백엔드 (`scripts/chat/*`, `/api/chat/*`) — 4시간
6. 채팅 프론트 (`templates/index.html`, `static/app.js`, `static/style.css`) — 3시간
7. E2E 검증 (PIN 미설정 / 잠금 / 도구별 happy path / 금지 도구 시도) — 1시간

총 추정: ~11 시간 (단일 작업자 기준).

## 7. 성공 기준

- 인스타그램 `/p/` URL 등록 시도 시 즉시 친절한 한글 메시지로 종료, Notion 오염 X
- 신규 URL 등록 시 의미 dedup 이 작동해 같은 주제 페이지가 자동 합병됨
- 일괄 스캔 리포트가 `contextual-prompt-engineering` 군집을 후보로 잡음
- 채팅에서 "dedup 임계값 0.85 로 올려줘" → diff 미리보기 → PIN → 적용 → 즉시 다음
  스크랩에 반영
- 채팅이 `app.py` 수정 요청을 받았을 때 명확히 거부

## 8. 의도적 비결정사항

- 채팅 UI 다크모드 — 현재 사이트가 다크 전제이므로 별도 토글 X
- 채팅 모바일 폼팩터 정확한 폭/높이 — 구현 단계에서 결정
- Opus 4.8 fallback (4.7 / Sonnet 4.6) — 1차 구현 후 운영 데이터 보고 추가

## 9. 변경 이력

| 일자 | 변경 |
|---|---|
| 2026-06-12 | 최초 작성 |
