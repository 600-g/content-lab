# 두근컴퍼니 AI 스킬 표준 템플릿 v2

> 이 문서는 모든 스킬 페이지의 **단일 진실**(single source of truth)입니다.
> Notion DB · `~/.claude/skills/` · 큐레이션 batch 모두 이 형식을 따릅니다.

---

## 설계 원칙

1. **DB 속성은 핵심 분류만** — 본문 v1 메타 callout과 중복 X
2. **카테고리 vs 태그 명확히 분리** — 카테고리 = "작업 영역", 태그 = "기술/방법"
3. **첫 줄에 TL;DR** — 사람 0.5초 + AI semantic RAG 최적
4. **메타 callout** — 등급/카테고리/도구/적용대상을 본문 첫 줄에 한 번 더
5. **고정 8섹션 헤더** — 영문 키 + 한국어 라벨
6. **코드/명령어는 코드블록**
7. **두근 환경 적용 섹션 필수** (프로젝트별 매핑)
8. **광고/홍보/잡담 제거** — 핵심만

---

## Notion DB 속성 (9개, 슬림 v2)

| 속성 | 타입 | 용도 | enum |
|------|------|------|------|
| 스킬명 | title | 필수, 이모지 X | — |
| **등급** | select | 우선순위 | S-즉시적용 / A-참고가치 / B-나중에 / C-스킵 |
| **난이도** | select | 적용 비용 | 🟢 초보OK / 🟡 중급 / 🔴 고급 |
| **카테고리** | select | 작업 영역 (1개) | 아래 7종 |
| **AI 도구** | multi_select | 사용 도구 | 아래 14종 |
| **태그** | multi_select | 기술/방법 (검색용) | 아래 15종 |
| **적용 대상** | multi_select | 두근 프로젝트 매핑 | 아래 8종 |
| 출처 URL | url | 중복 체크 + 검증 (자동) | — |
| 상태 | select | 진행 흐름 | 신규 / 적용완료 / 검토중 / 폐기 |
| 마지막 업데이트 | last_edited_time | 자동 | — |

**제거된 속성 (v1에서 → v2):** 수집일, 핵심 요약, 적용 메모, 출처 유형, 관련 스킬
→ 모두 본문 v1 템플릿 안에 있어서 중복.

---

## 카테고리 (7종, "작업 영역")

```
프롬프트 · 자동화 · 콘텐츠 · 디자인 · 개발 · 업무 · 기타
```

**원칙**: "어떤 작업/영역인가?" — 1개만 선택 (board view 그룹핑용)

- **프롬프트** — 프롬프트 엔지니어링, 시스템 프롬프트 설계
- **자동화** — AI 에이전트, 워크플로우, 작업 자동화
- **콘텐츠** — 영상/이미지/텍스트 콘텐츠 생성, SNS
- **디자인** — UI/UX, 캐릭터, 시각 디자인
- **개발** — 코딩, 앱 구축, 배포
- **업무** — 문서 작성, 회의록, 일정, 의사결정
- **기타** — 위 분류에 안 맞는 것

---

## 태그 (15종, "기술/방법")

```
MCP · API · RAG · Function Calling · Vision · Multimodal
프롬프트체이닝 · CoT · Tool Use · Webhook · Streaming
CLI · GitHub Actions · 자체호스팅 · 오픈소스
```

**원칙**: "어떤 기술/방법을 쓰는가?" — 여러 개 가능 (검색 키워드용)

- **MCP** — Model Context Protocol 서버/클라이언트
- **API** — REST API, GraphQL 직접 호출
- **RAG** — Retrieval-Augmented Generation
- **Function Calling** — LLM이 함수 호출
- **Vision** — 이미지 인식/분석
- **Multimodal** — 텍스트+이미지/비디오/오디오
- **프롬프트체이닝** — 단계별 프롬프트 연결
- **CoT** — Chain of Thought 추론
- **Tool Use** — Claude/GPT의 tool use 패턴
- **Webhook** — 이벤트 기반 트리거
- **Streaming** — 스트리밍 응답 처리
- **CLI** — 터미널 명령줄 도구
- **GitHub Actions** — CI/CD 자동화
- **자체호스팅** — 로컬/사설 서버 운영
- **오픈소스** — 오픈소스 도구/모델 활용

**카테고리와 태그가 안 겹치는지 검증**: "프롬프트" 카테고리 + "프롬프트체이닝" 태그는 OK (서로 다른 차원). "자동화" 카테고리 + "MCP" 태그도 OK.

---

## AI 도구 (14종, multi_select)

```
Claude · GPT · Gemini · Midjourney · Leonardo AI · CapCut · Canva
Cursor · Codex · ComfyUI · Stable Diffusion · Ollama · Claude Code · 도구무관
```

---

## 적용 대상 (8종, multi_select)

```
두근펫 · 매매봇 · 검은별 · 클로드코드 · AI900 · 첼시인스타 · 이모티콘 · 공통
```

---

## 표준 본문 8섹션 (TEMPLATE v1과 동일, 변경 없음)

````markdown
> **TL;DR** — 이 스킬은 [언제] [무엇을] 한다. (한 줄, 2문장 이내)

> **메타** 등급 S · 카테고리 자동화 · 난이도 🟡 중급
> **도구** Claude Code, Notion MCP
> **적용 대상** 클로드코드, 두근컴퍼니

---

## 🎯 When to use (언제 쓰는가)
- 트리거 조건 1
- 트리거 조건 2

## 🔑 How it works (작동 원리)
핵심 패턴/공식/메커니즘. 코드는 ```코드블록```

## 🛠 Steps (적용 단계)
1. 첫 단계
2. 두 번째 단계

## 💡 Examples (예시)
실제 입력→출력. 표 가능.

## 🏢 두근 환경 적용
(필수 1) **외부 도구 대체** — 원본이 두근 안 쓰는 도구 사용 시 두근 환경 대체안 명시
  - 예: "Cursor 대신 → Claude Code + Continue 확장으로 동일"
  - 예: "Midjourney 대신 → Bing DALL-E 3 무료"
(필수 2) **프로젝트 매핑** — 두근펫/매매봇/검은별/첼시인스타/콘텐츠 중 관련
  - 예: "**매매봇**: 시황 자동 분석 → 텔레그램 알림"

## ⚠️ Caveats (주의사항)
한도/유료/실패 케이스

## 📎 Sources (출처)
- 원본: [제목](URL) (저자, 날짜)
````

---

## 페이지 아이콘 매핑 (카테고리 7개로 단순화)

| 카테고리 | 아이콘 |
|---|---|
| 프롬프트 | 💬 |
| 자동화 | 🤖 |
| 콘텐츠 | 🎬 |
| 디자인 | 🎨 |
| 개발 | 💻 |
| 업무 | ⚡ |
| 기타 | 📦 |

→ 페이지 제목에는 이모지 없음. 아이콘만 1개.

---

## 외부 도구 대체 매핑 (두근 환경)

원본 스킬이 두근이 안 쓰는 외부 도구를 사용하면 **반드시** 본문 "🏢 두근 환경 적용" 섹션에 대체 도구 + 적용법 명시.

| 외부 도구 | 두근 대체 | 적용법 |
|---|---|---|
| Cursor | Claude Code + VSCode + Continue 확장 | Claude Max 포함, CLI 기반 |
| GitHub Copilot | Claude Code / Codex CLI | 자동 완성 + 채팅 |
| ChatGPT Plus | Gemini 무료 + Claude Max | 대용량(Gemini) + 코딩(Claude) |
| Midjourney | Bing DALL-E 3 / Leonardo AI 무료 | 무료, 무제한 (한도 내) |
| Replit / Vercel | Mac Mini M4 + CF Tunnel | 자체 호스팅, 0원 |
| Notion AI | Notion MCP + Claude Code | 무료, 본인 데이터 |
| Runway / Pika | Pixelle 오픈소스 + Gemini 이미지 | Mac Mini 로컬 |
| Zapier / Make | Claude Code + GitHub Actions | 무료, 무제한 |
| Perplexity | Gemini + Claude (Web Search MCP) | 무료 |
| v0.dev | Claude Artifacts | Claude Max 포함 |
| ElevenLabs | 로컬 TTS + CapCut | 무료 |
| DeepL | Gemini / Claude 번역 | 무료 + 정확도 ↑ |
| Linear / Jira | Notion DB + Cursor 룰 | 본인 워크플로우 |
| Figma AI | Claude Design | Claude Max 포함 |

새 도구 발견 시 이 표에 추가 → 자동 분석 시 즉시 대체안 제시.

---

## 변경 이력

| 날짜 | 버전 | 변경 |
|------|------|------|
| 2026-05-15 | v1.0 | 최초 정의. 8섹션 표준 |
| 2026-05-15 | v2.0 | DB 속성 15→9개 슬림화. 카테고리 8→7개 단순화. 태그 17→15개 기술/방법 키워드로 재정의 |
| 2026-05-15 | v2.1 | 외부 도구 대체 매핑 14종 정의. doogeun 섹션 작성 가이드 강화 |
