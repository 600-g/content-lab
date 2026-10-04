---
name: claude-code-unlimited-free
description: Claude Code 한도 안에서 더 오래·싸게 쓰는 통합 가이드. **/compact·CLAUDE.md·서브에이전트·autocompact** 로 토큰을 최대 73% 줄이고, **Headroom** 으로 요청을 압축하고, 한도가 차면 **OmniRoute·FreeLLMAPI** 무료 모델 라우터로 환승하며, **Claude-mem** 으로 세션 맥락을 잇는다.
origin: content-lab
grade: S
difficulty: 중급
category: 개발
ai_tools: ["Claude", "Claude Code", "Codex", "Gemini"]
sources:
  - https://fieldby.notion.site/3-3c7d730b395381c7b605cc88ea8b152c?pvs=149
  - https://yeongseon.kr/archive/3bfd86104de2802cbe10d6ca4aee512f.html?fbclid=PAVERFWAUDr_VwZG9mAmZkaWQWUNnqK4_WfI9gCsn3Z63HcTEKOu2EoWV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp0umc4DTXWajmYL-XeAYxIqLLiuq9aOqsLlp0RYN5F2T_M5lzkcR1nBfebKF_aem_H_7ffADoSghuOtZdWg4ixQ
  - https://abounding-helmet-0e4.notion.site/Claude-Code-Headroom-38d73c7b15ad813190abf555ad0bf667?pvs=149
  - https://waiting-drug-536.notion.site/73-34bd86104de28031b19ff79353c17b83
  - https://abounding-helmet-0e4.notion.site/50-300-36373c7b15ad81ccac8ded33f43886d5
  - https://wandering-mile-86e.notion.site/FreeLLMAPI-3e398dec8eed814d8e9cd2e698076403?pvs=149
  - https://github.com/diegosouzapw/OmniRoute?fbclid=PAVERFWAT5qhtwZG9mAmZkaWQWUNHYLf1kPOw6dg1dr2eXutgZpVf0EGV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABpygtIkWa1Avaq69_5wlE1kjoNdCyM4eJF9X0fDeS85ErLCZYU7Ab_BQEtVAR_aem_pghrJzxBaJS4VedSgGP73g
---

# 클로드 코드 한도 늘려 쓰기

💡 Claude Code 사용 한도를 아끼는 길은 네 가지입니다 — **습관·설정으로 덜 쓰기**, **Headroom 으로 요청 압축**, 한도가 차면 **OmniRoute·FreeLLMAPI 로 무료 모델 환승**, **Claude-mem·Task Observer 로 맥락과 피드백 유지**. 상황에 맞는 것부터 골라 적용하세요.

## 이게 뭔가요?

클로드 코드(Claude Code)는 터미널에서 AI에게 코딩을 시키는 유료 도구이며, 사용량에 따라 한도(rate limit)와 비용이 발생합니다. 쓰다 보면 「사용량 한도에 도달했습니다」 창을 만나거나 더 비싼 요금제를 끊어야 하는 순간이 옵니다. 이 가이드는 그 제약을 네 겹으로 완화합니다.

| 층 | 무엇을 하나 | 도구·방법 | 비용 |
|---|---|---|---|
| ① 덜 쓰기 | 명령어 습관·룰북·위임·자동 압축 임계값·작업 분할로 소모 자체를 줄임 | `/usage` `/compact` `/clear`, CLAUDE.md, 서브에이전트, autocompact, Skill 분할 | 무료 (설정만) |
| ② 압축해서 보내기 | 로그·에러·코드·RAG Chunk 를 LLM에 보내기 전에 압축 | **Headroom** (Context Compression Layer) | 무료 오픈소스 |
| ③ 다른 모델로 환승 | 한도가 차면 요청을 다른 회사의 무료 모델로 넘김 | **OmniRoute** (중계소·게이트웨이), **FreeLLMAPI** (무료 티어 모음 라우터) | 무료 오픈소스 |
| ④ 맥락·피드백 유지 | 세션이 바뀌어도 이전 작업을 기억하고, 반복 지적을 규칙으로 학습 | **Claude-mem**, **Task Observer** | 무료 오픈소스 |

💰 **유료 필요**: Claude Code 자체는 유료 서비스입니다. 나머지 도구는 모두 무료 오픈소스입니다.

이 가이드는 클로드 코드 **CLI(터미널)** 버전을 기준으로 하며, 데스크톱 앱은 일부 기능(특히 Headroom)이 지원되지 않을 수 있습니다. 처음 사용한다면 claude.ai/code 에서 시작할 수 있습니다.

### ① 덜 쓰기 — 5축 절약 패턴

Claude Code 토큰 소비를 **73%까지** 줄여 체감 작업량을 3배 이상 늘리는 패턴입니다.

| 축 | 효과 |
|---|---|
| 명령어 3종 (`/usage` `/compact` `/clear`) | 20-30% |
| CLAUDE.md 룰북 | 20-30% |
| 서브에이전트 위임 | 15-25% |
| autocompact 조정 | 10-15% |
| Skill 분할 | 5-10% |

총합 **~73%** (중복 효과 반영).

이 패턴이 특히 주목받은 배경은 2026년 5월 13일부터 7월 13일까지(PDT 기준 7/13 18:00 만료) **클로드 코드 주간 사용 한도가 50% 자동 인상**되었던 사건입니다. Anthropic-SpaceX 컴퓨트 딜 체결과 사용자 이탈 방어가 배경으로 언급되었고, 누적 세 번째 인상이었습니다: ① 5시간 한도 2배 → ② 피크 시간대 한도 제거 → ③ 주간 한도 50% 추가 인상. 적용 대상은 Pro·Max·Team·Enterprise 플랜이며 Free 플랜은 제외되었고, 별도 신청 없이 자동 적용되었습니다. `/usage` 명령어로 즉시 세션/주간 잔량을 확인할 수 있었습니다. 이 인상 기간은 이미 만료되었지만, 그 기간 동안 정리된 서브에이전트 컨텍스트 보호·병렬 작업 최적화 패턴은 한도와 무관하게 상시 유효합니다.

### ② 압축해서 보내기 — Headroom

Headroom은 Claude Code가 처리하는 방대한 데이터(로그, 에러 메시지, 코드 파일, RAG Chunk 등)를 LLM에 전달하기 전 압축해 불필요한 토큰 낭비를 막는 계층입니다. 절감 효과는 작업 종류에 따라 다르게 보고됩니다.

| 작업 | 보고된 절감률 |
|---|---|
| 데이터 뭉치(로그·문서 등) 전송 | 최대 95% |
| 일반 코딩 작업 | 약 20% |
| 전체 세션 평균 | 40~50% |
| 최대 기대치로 제시된 범위 | 60~95% |

실제 절감률은 작업 환경과 입력 데이터 특성에 따라 달라집니다.

### ③ 다른 모델로 환승 — OmniRoute 와 FreeLLMAPI

두 도구 모두 내 컴퓨터에 작은 서버(라우터)를 띄우고, 클로드 코드가 Anthropic 대신 그 주소로 말을 걸게 만듭니다. 클로드 코드는 자기가 Anthropic 서버에 말을 거는 줄 알지만, 실제로는 내 컴퓨터의 라우터가 받아서 그 순간 쓸 수 있는 모델에게 넘기고 답을 다시 돌려줍니다.

비유하면 동네 카페 열 곳이 각각 「첫 잔 무료」 쿠폰을 주는 상황과 같습니다. 한 장으로는 하루도 못 버티지만, 열 장을 지갑 하나에 모아 두고 한 장이 떨어지면 다음 장을 자동으로 꺼내 주는 지갑이 있다면 매일 공짜 커피를 마실 수 있습니다. 라우터가 그 지갑입니다.

```
flowchart LR
A["클로드 코드"] -->|"http://localhost:3001"| B["FreeLLMAPI 라우터<br/>(내 컴퓨터)"]
B --> C["구글 Gemini 무료"]
B --> D["Groq · GPT-OSS 무료"]
B --> E["Cerebras · GLM 무료"]
B --> F["… 34곳"]
C & D & E & F -->|"답"| B --> A
```

**OmniRoute** 는 개발자들이 다양한 AI 모델을 더 쉽고 효율적으로 사용할 수 있도록 돕는 오픈 소스 AI 게이트웨이입니다. 단 하나의 엔드포인트를 통해 350개 이상의 AI 공급자 (90개 이상의 무료 티어 포함) 와 1200개 이상의 모델 (Kimi, Claude, GPT, Gemini, GLM, DeepSeek, MiniMax 등) 에 접근할 수 있습니다. Claude Code, Codex, Cursor, OpenCode, Cline, Copilot 등 다양한 코딩 도구와 호환되며, 450명 이상의 기여자들이 참여하고 있습니다.

- **무료 AI 게이트웨이**: 월 15억 토큰 이상의 무료 티어를 활용할 수 있습니다.
- **통합 엔드포인트**: 모든 AI 모델을 단일 `/v1` 엔드포인트로 접근
- **비용 절감**: 토큰 압축 기술 (RTK + Caveman) 로 15-95%, 최대 95% 비용 절감
- **자동 폴백**: 모델 또는 공급자가 실패할 경우 자동으로 다른 모델로 전환
- **데스크톱/PWA 지원**, **로컬 우선**(개인 정보 보호 및 보안 강화)

**FreeLLMAPI** 는 구글, Groq, Cerebras, Z.ai, NVIDIA, Mistral, Cloudflare 같은 회사들이 저마다 조금씩 주는 무료 API 티어를 내 컴퓨터의 주소 하나(`http://localhost:3001`) 뒤에 모아 둡니다. 한 회사 것만 보면 장난감 수준이지만, 전부 모으면 매달 약 74억 토큰이 됩니다.

| 항목 | 값 |
|---|---|
| 이름 | FreeLLMAPI |
| 저장소 | github.com/tashfeenahmed/freellmapi |
| 홈페이지 | freellmapi.co |
| 라이선스 | MIT (라우터 자체는 영원히 무료) |
| 2026-09-22 기준 | 스타 27,924 · 무료 제공사 34곳 · 무료 모델 엔드포인트 635개 · 월 약 74억 토큰 |

MIT 라이선스는 「가져다 쓰세요, 고쳐도 됩니다. 만든 사람 이름만 남겨 주세요」라는 가장 느슨한 약속입니다. 뒤쪽 모델은 Gemini·GPT-OSS·GLM·Kimi 등 각 회사의 무료 모델이며, 유료 필요는 없습니다(「Premium」은 카탈로그를 당일 반영해 주는 선택 사항일 뿐). 각 회사의 무료 API 키(카드 불필요)만 있으면 됩니다.

FreeLLMAPI 를 쓰기 전에 알아 둘 것 세 가지:

- **「ChatGPT」가 아니라 GPT-OSS입니다.** 목록에 있는 GPT 계열은 OpenAI가 공개한 가중치 모델 GPT-OSS 120B와 20B입니다. ChatGPT 앱이나 GPT-5 같은 유료 모델이 들어 있는 게 아닙니다. Gemini 3.5 Flash, GLM-4.7, Kimi K2.6, Grok 4.1 Fast는 이름 그대로 목록에 있습니다.
- **저장소가 스스로 「개인 실험용」이라고 적어 두었습니다.** 원문은 "This project is for personal experimentation and learning, not production." 회사 서비스에 붙이는 용도가 아닙니다.
- **무료 티어는 회사가 정한 한도가 있습니다.** 분당 요청 수, 하루 요청 수 같은 것입니다. 라우터가 한도를 세다가 막히면 다음 모델로 넘어가 주지만, 속도와 품질은 그때그때 다릅니다.

### ④ 맥락·피드백 유지 — Claude-mem 과 Task Observer

- **Claude-mem**: 이전 세션 작업 내용을 기억해 새 세션에서도 맥락을 유지시켜 줍니다. 무료 모델 환승 중에도 동일하게 작동합니다.
- **Task Observer**: 사용자가 Claude 결과물을 수정할 때마다 그 변경을 규칙으로 저장해, 같은 피드백을 반복하지 않게 해 줍니다.

## 따라하기

### 어떤 방법을 언제 쓰나

| 상황 | 먼저 쓸 방법 | 이유 |
|---|---|---|
| 아직 한도에 안 걸렸지만 늘 빠듯하다 | 방법 1. 5축 절약 | 설정만으로 소모를 줄이고, 다른 방법과 함께 써도 충돌이 없음 |
| 로그·문서·대형 소스를 자주 통째로 넘긴다 | 방법 2. Headroom | 데이터 뭉치일수록 압축 효과가 큼(최대 95%) |
| 지금 한도가 찼는데 작업을 이어가야 한다 | 방법 3. OmniRoute (`omniroute launch`) 또는 방법 4. FreeLLMAPI (`npx freellmapi launch`) | 그 실행 창만 무료 모델로 돌림. 한도가 풀리면 다시 `claude` |
| 여러 회사 무료 키를 모아 꾸준히 무료로 굴리고 싶다 | 방법 4. FreeLLMAPI | 무료 제공사 34곳·월 약 74억 토큰을 한 주소로 묶음, 대시보드에서 모델 순서 지정 |
| Claude Code 외에 Codex·Cursor·Aider 등도 한 엔드포인트로 쓰고 싶다 | 방법 3. OmniRoute | 350개+ 공급자, `omniroute run <도구>` 와 `/v1` 엔드포인트 |
| 며칠짜리 프로젝트에서 세션을 자주 새로 연다 | 방법 5. Claude-mem | 새 세션에 이전 작업 요약이 자동 표시 |
| 같은 수정 지시를 매번 반복한다 | 방법 5. Task Observer | 수정 패턴을 규칙으로 학습 |

> 조합 원칙: 방법 1·5는 무엇과도 함께 쓸 수 있습니다. 방법 2(압축)와 방법 3·4(환승)는 모두 클로드 앞단에 끼어드는 도구이므로 **한 번에 하나만** 앞단에 두는 것이 좋습니다. 방법 3과 4도 둘 다 라우터이므로 하나를 고르세요.

### 0. 준비물 확인

설치는 모두 터미널(맥: 터미널, 윈도우: PowerShell)에서 진행됩니다. 코딩 지식은 필요 없으며, 안내된 명령어를 복사해 붙여넣고 엔터만 누르면 됩니다.

설치 전 Node.js와 Python이 설치되어 있는지 확인합니다. (FreeLLMAPI 를 소스로 돌릴 때는 Node.js 20 이상이 필요합니다.)

```bash
node --version
python3 --version
```

만일을 대비해 설정 파일을 백업합니다. 파일이 없다는 메시지가 나와도 무시하고 진행하면 됩니다.

```bash
cp ~/.claude/settings.json ~/.claude/settings.backup.json
cp ~/.claude.json ~/.claude.backup.json
```

### 방법 1. 5축 절약 패턴 — 설정과 습관

#### 축 1. 핵심 명령어 3종

**`/usage`** — 작업 전후 습관
```
주간 사용량 + 세션 사용량 + 리셋 시간 확인
"이번 주 30% 남았네" 같은 자기 통제
```

**`/compact`** — 긴 작업 도중
```
채팅 요약 → 오래된 데이터 드롭 (문맥은 유지)
1시간 작업 중 30분 시점에 1회 실행 권장
```

**`/clear`** — 작업 전환 시
```
완전히 깨끗한 세션 시작
서로 무관한 작업 사이엔 반드시 /clear
```

#### 축 2. CLAUDE.md 룰북

프로젝트 루트 또는 `~/.claude/CLAUDE.md`:
```markdown
# Response Style
- 응답 간결하게. 불필요한 서문·요약 금지.
- 한 줄로 끝날 답변은 한 줄로만.
- 코드만 요청 시 부연 설명 생략.

# Output Limits
- Bash output이 길면 head, tail, jq로 자를 것.
- 테스트 로그는 마지막 20줄만 분석.
- 파일 1000줄 넘으면 청크 분할.

# Workflow
- 대규모 조사·분석은 서브에이전트에 위임.
- 메인 컨텍스트는 지휘·검토만.
- 단순 검색은 메인에서 직접.

# Token Saving
- 코드 변경 후 변경된 부분만 (diff 형태).
- 100줄 이상 새 파일은 미리 확인.
- 명시하지 않은 추가 기능 자발 추가 X.
```

클로드가 매 요청마다 이 규칙을 먼저 읽어 불필요한 출력 토큰을 줄여 줍니다. 토큰 절감 효과는 프로젝트 규모와 작업 패턴에 따라 달라질 수 있습니다.

#### 축 3. 서브에이전트 위임 패턴

**기본 원칙:**
- 격리 작업 — 서브에이전트는 격리된 컨텍스트에서 작업
- 결과만 반환 — 진행 과정은 숨기고 최종 결과만 메인으로 반환해 메인 컨텍스트 보호
- 파일로 저장 — 3개 이상 병렬 시 각 결과를 개별 파일로 저장하고, 메인은 "파일 경로 + 한 줄 요약"만 전달받도록 구성

**🚨 Opus 비용 함정:** 서브에이전트는 부모 모델을 상속합니다. Opus 모델에서 서브에이전트를 5개 병렬로 돌리면 Opus 토큰 비용이 **5배**로 폭증합니다. 단순 조사·크롤링은 반드시 명시적으로 `--model sonnet` 또는 `--model haiku`를 지정해 위임하세요.

**위임 기준:**
- ✅ 위임 추천: 다중 모듈 조사 / 병렬 코드 리뷰 / 대규모 리팩토링 / 문서 양산
- ❌ 위임 비추천: 단일 검색 / 짧은 Lookup / 순차 의존성이 있는 작업 / 1-2턴 작업

#### 축 4. autocompact 임계값

기본 임계값(약 95%)을 낮춰 컨텍스트가 꽉 차기 전에 미리 압축하도록 설정합니다. `~/.claude/settings.json`:
```json
{
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "70"
  }
}
```

| 작업 유형 | 권장 |
|---|---|
| 일반 | 60~75% |
| 큰 컨텍스트 유지 | 85% |
| 디버깅 | 90% (압축 늦게) |

시작값은 **70~75%** 사이에서 잡고, 1주 사용 후 본인 패턴에 맞게 조정하세요. 50% 이하로 내리면 압축이 너무 잦아 역효과가 납니다.

#### 축 5. Skill 분할

대규모 리팩토링을 통째로 맡기지 말고 5개 단위 작업으로 분할합니다:
```
1차: "auth 모듈만 리팩토링" + /goal lint clean and tests pass
   ↓ /clear
2차: "API 모듈만 리팩토링" + /goal
   ↓ /clear
...
```

#### 7일 점진적 도입

| 일차 | 작업 |
|---|---|
| Day 1 | `/usage` 매 작업 전후 습관화 |
| Day 2 | `CLAUDE.md` 룰북 적용 |
| Day 3 | autocompact 70~75% 설정 |
| Day 4 | 첫 서브에이전트 위임 (단순 조사부터) |
| Day 5 | `/compact` 적극 활용 |
| Day 6 | 큰 작업 5개 단위 분할 |
| Day 7 | 본인 패턴 분석 + 룰북 개인화 |

#### 한도 인상 이벤트 대응 체크리스트

2026-05-13~07-13 한시적 50% 인상(현재는 만료되어 원래 한도로 복귀) 때 정리된 체크리스트입니다. 유사한 이벤트가 다시 생기면 그대로 재사용합니다.
- CLAUDE.md 템플릿 적용 완료
- autocompact 70~75% override 설정 완료 (`~/.claude/settings.json`)
- 토큰 소모가 큰 '대규모 리팩터링 및 마이그레이션' 작업을 인상 기간으로 일정 재조정
- 서브에이전트 패턴 워크플로우 실무 정착
- 주 1회 `/usage` 명령어로 토큰 소모 패턴 점검 및 학습

### 방법 2. Headroom — 요청 압축

1. **설치 (pip 방식, 권장)**
   ```bash
   pip3 install "headroom-ai[all]"
   ```
   `pip` 명령어가 작동하지 않으면 `pip3`를 사용합니다. Node/TypeScript 환경에서는 다음처럼도 설치할 수 있지만, 실행 명령어가 자동 생성되지 않으므로 실제 CLI 실행에는 pip3 방식이 안전합니다.
   ```bash
   npm install headroom-ai
   ```
   더 짧은 패키지명으로 안내되는 경우도 있으니, 설치 전 실제 배포된 패키지명을 확인하세요.
   ```bash
   pip install headroom
   ```

2. **압축 모드로 켜기** — 이제부터 `claude` 대신 아래 형태로 실행하면 압축 기능이 활성화됩니다.
   ```bash
   headroom wrap claude
   ```
   일반화하면 다음과 같이 임의의 실행 명령어를 감쌀 수 있습니다.
   ```bash
   headroom wrap [실행할_명령어]
   ```
   이 명령으로 실행된 창에서만 압축이 작동하며, 터미널 창을 닫으면 압축도 중단됩니다. 처음 실행 시 Serena라는 코드 탐색 보조 도구가 함께 설치·등록됩니다.

3. **상태 확인**
   ```bash
   headroom doctor
   ```

4. **토큰 절감 현황 확인**
   ```bash
   headroom dashboard
   ```

5. **원래대로 돌리기**
   ```bash
   headroom unwrap claude
   ```

처음에는 작은 프로젝트나 덜 민감한 데이터로 압축 품질을 시험해 보고 범위를 넓히세요.

### 방법 3. OmniRoute — 무료 모델 환승 게이트웨이

1. **설치** — npm을 사용하여 전역으로 설치합니다.
   ```bash
   npm install -g omniroute
   ```
   짧게 쓰면 다음과 같습니다.
   ```bash
   npm i -g omniroute
   ```
   맥에서 `permission denied` 또는 `EACCES` 오류 발생 시 관리자 권한으로 실행합니다.
   ```bash
   sudo npm install -g omniroute
   ```

2. **서버 켜기**
   ```bash
   omniroute
   ```
   `localhost:20128` 에서 API 서버가 시작됩니다. 이 창은 켜둔 채로 유지하고, 이후 작업은 새 터미널 창에서 진행합니다.

3. **무료 제공사 연결** — 브라우저에서 `http://localhost:20128`로 접속해 OmniRoute 대시보드에서 사용할 무료 제공사를 선택·연결합니다. 처음 접속 시 관리자 비밀번호 설정이 필요할 수 있습니다. (`auto` 모델처럼 기본 무료 백엔드를 쓰는 경우에는 API 키나 별도 설정 없이 바로 쓸 수 있다고 안내됩니다.)

4. **상태 확인**
   ```bash
   omniroute status
   ```

5. **환승 모드로 클로드 실행** — 한도 도달 시 일반 `claude` 대신 다음 명령어를 사용합니다.
   ```bash
   omniroute launch
   ```
   평소에는 `claude`, 한도에 도달했을 때만 `omniroute launch`를 사용합니다. 서버 창은 계속 켜두어야 합니다.

6. **모델을 지정해 CLI 도구 실행** — `omniroute run` 으로 Claude Code 외의 코딩 CLI 도구도 OmniRoute를 통해 실행할 수 있습니다.
   ```bash
   # Claude Code 실행 (GPT-5.4 모델 사용)
   omniroute run claude --model openai/gpt-5.4

   # Codex CLI 실행 (GLM-5.2 모델 사용)
   omniroute run codex --model glm/glm-5.2

   # Aider 실행 (GLM-5.2 모델 사용)
   omniroute run aider --model glm/glm-5.2 -- --message "reply OK"
   ```

7. **IDE·OpenAI 호환 도구 연결** — Cursor, Cline 같은 도구나 OpenAI API 호환 클라이언트는 API 엔드포인트를 `http://localhost:20128/v1` 으로 설정합니다. 모델 ID를 `auto` 또는 `auto/coding` 으로 주면 OmniRoute가 최적의 무료 또는 저비용 모델을 자동으로 고릅니다. 특정 무료 백엔드를 직접 호출할 수도 있습니다 (예: `oc/...` 는 OpenCode Free, `felo/...` 는 Felo).
   ```bash
   curl http://localhost:20128/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"auto","messages":[{"role":"user","content":"Hello!"}]}'
   ```
   위 curl 에 답이 오면 게이트웨이가 정상 동작하는 것입니다.

### 방법 4. FreeLLMAPI — 무료 API 티어 모음 라우터

1. **설치하기 (약 5분)** — 환경에 맞는 방법 하나만 고릅니다.

   **윈도우 / 맥 — 설치 파일 하나**

   릴리스 목록에서 `.exe` 파일을 받아 실행합니다. (맥은 `.dmg`) 설치가 끝나면 작업 표시줄 트레이에 아이콘이 생기고, 대시보드가 브라우저로 열립니다. 비밀번호를 만들 필요가 없습니다. 데스크톱 앱은 숨은 로컬 계정으로 스스로 로그인합니다.

   **도커를 쓸 줄 안다면 — 한 줄**

   ```
   curl -fsSL https://freellmapi.co/install.sh | bash
   ```

   `~/freellmapi` 폴더를 만들고, 암호화 키를 만들고, 이미지를 받아서 컨테이너를 띄웁니다. 끝나면 브라우저에서 `http://localhost:3001` 을 엽니다. 도커 설치판은 이메일·비밀번호 계정을 만듭니다.

   **직접 소스로 돌리고 싶다면 (Node.js 20 이상)**

   ```
   git clone https://github.com/tashfeenahmed/freellmapi.git
   cd freellmapi
   npm install
   $ENCRYPTION_KEY = node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
   "ENCRYPTION_KEY=$ENCRYPTION_KEY`nPORT=3001" | Out-File -Encoding utf8 .env
   npm run dev
   ```

   위 예시의 `$ENCRYPTION_KEY = ...` 와 `Out-File` 은 윈도우 PowerShell 문법입니다. 맥·리눅스 셸에서는 같은 내용(`ENCRYPTION_KEY=<32바이트 hex>` 와 `PORT=3001` 두 줄)을 `.env` 파일에 직접 적어 넣으면 됩니다.

2. **무료 API 키 받기 (약 15분)** — FreeLLMAPI는 키를 대신 만들어 주지 않습니다. 각 회사 사이트에서 무료 키를 받아 와야 합니다. 처음이라면 아래 여섯 곳이면 충분합니다. 전부 회원가입만 하면 되고 카드는 필요 없습니다.

   | 회사 | 키 받는 곳 | 뭘 주나 |
   |---|---|---|
   | 구글 | aistudio.google.com → Get API key | Gemini Flash 계열 |
   | Groq | console.groq.com → API Keys | GPT-OSS 120B/20B, Llama, Kimi K2 (매우 빠름) |
   | Cerebras | cloud.cerebras.ai → API Keys | GLM-4.7, Qwen3 (매우 빠름) |
   | OpenRouter | openrouter.ai → Keys | 「:free」가 붙은 모델 여러 개 |
   | Cloudflare | dash.cloudflare.com → Workers AI | Llama, Kimi K2.6 등 |
   | NVIDIA | build.nvidia.com → Get API Key | Nemotron, GLM, Kimi 등 |

3. **대시보드에 키 넣기** — 대시보드 위쪽 탭에서 **Keys** 를 누릅니다. 회사 이름을 고르고 방금 받은 키를 붙여 넣고 저장합니다. 여섯 번 반복합니다.

4. **성공 확인 및 통합 키 복사** — **Models** 탭으로 가면 방금 넣은 회사들의 모델이 목록에 켜집니다. 위쪽 「Monthly token budget」 띠가 여러 색으로 차 있으면 성공입니다. 색 하나가 회사 하나입니다. 그다음 Keys 탭 맨 위에 `freellmapi-…` 로 시작하는 긴 글자가 있습니다. 이게 **통합 키**입니다. 클로드 코드에는 이 키 하나만 줍니다. 회사 키들은 라우터 안에 암호화돼 있고 밖으로 나가지 않습니다.

5. **클로드 코드 연결 (약 1분)** — 터미널을 열고 한 줄 칩니다.

   ```
   npx freellmapi setup-claude --url http://localhost:3001
   ```

   이 명령이 하는 일은 셋입니다.
   - 지금 있는 클로드 코드 설정을 백업합니다 (날짜가 붙은 사본)
   - 라우터에 물어서 쓸 수 있는 모델 목록을 가져옵니다
   - 클로드 코드 설정에 `ANTHROPIC_BASE_URL=http://localhost:3001` 과 통합 키를 합쳐 넣습니다

   먼저 뭘 바꾸는지만 보고 싶으면 `--dry-run` 을 붙입니다. 아무것도 안 바꾸고 보여만 줍니다.

   설정 파일에 키를 남기기 싫으면(또는 한도가 찬 날만 무료로 돌리고 싶으면) 대신 이렇게 띄웁니다.

   ```
   npx freellmapi launch
   ```

   키를 그 순간 실행되는 클로드 코드 프로세스에만 넣어 주고, 파일에는 아무것도 남기지 않습니다.

   주소 끝에 `/v1` 을 붙이지 마세요. 클로드 코드는 뿌리 주소(`http://localhost:3001`)를 받아서 자기가 알아서 `/v1/messages` 를 붙입니다. (OmniRoute 의 `/v1` 엔드포인트는 OpenAI 호환 도구용이라 경우가 다릅니다.)

6. **모델이 바뀔 때 인수인계 메모 켜기** — 한 모델이 한도에 걸리면 라우터가 다음 모델로 넘깁니다. 이때 대화가 끊긴 것처럼 새 모델이 처음부터 다시 묻는 일이 생길 수 있습니다. 그걸 막으려면 라우터 폴더의 `.env` 파일에 아래 한 줄을 넣고 라우터를 다시 켭니다.

   ```
   FREELLMAPI_CONTEXT_HANDOFF=on_model_switch
   ```

   이러면 모델이 바뀌는 순간 라우터가 새 모델에게 짧은 인수인계 메모를 먼저 건넵니다. 내용은 대략 「너는 다른 모델이 하던 대화를 이어받는 중이다. 처음부터 다시 시작하거나 이미 정한 것을 다시 묻지 마라」 입니다. 대화 기록은 라우터 메모리에 3시간 동안 남고, 디스크에는 저장되지 않습니다. 같은 대화는 기본으로 30분 동안 같은 모델에 머뭅니다. 메모는 그 30분 안에 어쩔 수 없이 바뀔 때만 쓰입니다.

7. **잘 되는지 확인하기** — 클로드 코드를 켜고 아무 말이나 시킵니다. 대시보드 **Analytics** 탭을 엽니다. 방금 요청이 어느 회사의 어느 모델로 갔는지 줄이 하나 생깁니다. 답이 안 오거나 느리면 Models 탭의 「Router pressure」 를 봅니다. 최근 30분 동안 막힌 모델과 쉬는 중인 모델이 여기 보입니다.

8. **어려운 작업은 큰 모델 우선** — Models 탭에서 GPT-OSS 120B나 GLM-4.7 을 위쪽으로 끌어 올려 두면 복잡한 요청이 그 큰 모델부터 배정됩니다. 모델 카탈로그는 https://freellmapi.co/models.html 에서 볼 수 있습니다.

### 방법 5. 세션 맥락과 반복 피드백 유지

#### Claude-mem — 세션 기억

1. **설치**
   ```bash
   npx claude-mem install
   ```
   중간에 질문이 나오면 엔터로 기본값을 선택합니다. 클로드 코드 화면 내에서는 다음 명령으로도 설치할 수 있습니다.
   ```bash
   /plugin marketplace add thedotmack/claude-mem
   /plugin install claude-mem
   ```

2. **재시작** — 설치 후 클로드 코드를 완전히 종료했다가 다시 시작해야 기억 기능이 활성화됩니다. 재시작 후 새 세션을 열면 이전 작업 요약이 자동으로 나타나며, OmniRoute 환승 모드에서도 동일하게 작동합니다.

#### Task Observer — 반복 피드백 학습

1. **설치**
   ```bash
   git clone [Task Observer 저장소 URL]
   cd task-observer
   ```
   정확한 Git 저장소 URL이 원문에 명시되어 있지 않으므로, 실제 사용 시 해당 저장소를 직접 찾아야 합니다.

2. **사용** — 사용자가 Claude 결과물을 수정할 때마다 그 변경 사항을 기록하고 규칙으로 저장해, 향후 유사한 상황에서 AI가 처음부터 더 나은 결과를 생성하도록 돕습니다. `references` 폴더를 삭제하면 성능이 저하될 수 있으니 유지해야 합니다. 패턴을 학습하는 데 시간이 걸려 초기에는 효과가 작게 느껴질 수 있습니다.

### 전체 설치 확인

```bash
omniroute status
headroom doctor
```

| 도구 | 정상 신호 |
|---|---|
| OmniRoute | `omniroute status` 에 서버 상태 표시 |
| Headroom | `headroom doctor` 에 체크 표시 |
| Claude-mem | 클로드 코드 내에서 `/plugin` 입력 시 목록에 `claude-mem` 이 보임 |
| FreeLLMAPI | Models 탭 「Monthly token budget」 띠가 여러 색으로 차 있고, Analytics 탭에 요청 줄이 생김 |
| 5축 설정 | `/usage` 로 세션/주간 잔량 확인, `~/.claude/settings.json` 에 `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` 존재 |

### 트러블슈팅

| 증상 | 확인할 것 |
|---|---|
| `npm install -g` 에서 `permission denied` / `EACCES` (맥) | `sudo npm install -g omniroute` 로 재설치 |
| `pip` 명령이 없다고 나옴 | `pip3` 로 바꿔 실행 |
| npm 으로 Headroom 을 깔았는데 `headroom` 명령이 없음 | npm 판은 실행 명령어가 자동 생성되지 않음 → `pip3 install "headroom-ai[all]"` |
| 압축이 갑자기 안 됨 | `headroom wrap claude` 로 연 창을 닫으면 압축도 중단됨 → 다시 wrap 으로 실행 |
| `omniroute launch` 가 응답 없음 | `omniroute` 서버 창이 켜져 있는지, `omniroute status` 확인 |
| FreeLLMAPI 연결 후 클로드 코드가 오류 | 주소 끝에 `/v1` 을 붙이지 않았는지 확인 (`http://localhost:3001` 만) |
| FreeLLMAPI 답이 안 오거나 느림 | Models 탭 「Router pressure」 에서 최근 30분 막힌 모델·쉬는 모델 확인, 키를 더 넣거나 순서 조정 |
| 모델이 바뀌자 처음부터 다시 물음 | `.env` 에 `FREELLMAPI_CONTEXT_HANDOFF=on_model_switch` 추가 후 라우터 재시작 |
| Claude-mem 요약이 안 뜸 | 클로드 코드를 완전히 종료 후 재시작 |
| 설정이 꼬였음 | 0단계에서 만든 `settings.backup.json` / `.claude.backup.json` 으로 되돌리기 (FreeLLMAPI `setup-claude` 는 날짜가 붙은 백업도 따로 남김) |

## 활용 예시

- **한도 도달 시 작업 이어가기**: 평소 `claude`로 작업하다가 한도 메시지가 뜨면 새 터미널에서 `omniroute` 서버를 켜고 `omniroute launch`로 이어가고, 한도가 풀리면 다시 `claude`로 돌아갑니다. FreeLLMAPI 를 쓴다면 `npx freellmapi launch` 로 띄우면 설정 파일은 그대로 두고 그 프로세스만 무료 모델로 동작합니다.
- **긴 디버깅 세션**: 컨텍스트가 늘어질 때 `/compact` 를 실행하면 스레드 문맥은 유지한 채 오래된 로그만 드롭되어 이어서 작업할 수 있습니다.
- **작업 전환**: 새 기능 개발로 넘어갈 때 `/clear` 로 세션을 초기화해 이전 디버깅 로그가 불필요한 토큰을 소모하는 것을 막습니다.
- **여러 모듈 동시 조사**: Sonnet 모델을 지정한 서브에이전트 3개를 병렬로 실행하고 각 결과를 파일로 저장합니다. 메인 컨텍스트는 "파일 경로 + 한 줄 요약"만 받아 오염 없이 검토합니다.
- **멀티 에이전트 구조의 팀 운영**: 단순 조사/크롤링 작업에는 Opus 대신 Sonnet 모델을 명시 지정해 서브에이전트 비용 폭증을 막고, `/compact` 등 토큰 관리 명령어를 팀 전체 습관으로 정착시킵니다.
- **대규모 로그/코드 압축 분석**: 방대한 로그 파일이나 수백 페이지 소스 코드 전체를 그대로 넣는 대신 `headroom wrap claude`로 실행해 핵심 정보만 압축 전달하고, `headroom dashboard`로 절감량을 확인합니다.
- **RAG 청크 절감**: RAG 시스템에서 검색된 여러 문서 Chunk를 그대로 전달하면 토큰이 과도하게 소모되는데, Headroom으로 관련성 높은 정보만 추출·압축해 비용을 낮춥니다.
- **연습용 Python 스크립트 실험**: 코딩 초보가 부담 없이 여러 번 시켜 볼 때, FreeLLMAPI 에 연결한 클로드 코드에 「간단한 파일 정리 스크립트 만들어줘」 라고 입력하면 Analytics 탭에서 어느 회사의 어느 모델이 답했는지 줄로 확인됩니다.
- **IDE 코딩 지원**: VS Code의 Claude Code 또는 Cursor IDE에서 OmniRoute를 API 엔드포인트로 설정하여, 무료 티어의 다양한 모델로 코드 자동 완성, 버그 수정, 코드 설명 등을 받습니다.
- **AI 챗봇 연동**: 기존에 쓰던 OpenAI API 호환 챗봇 클라이언트(예: LiteLLM)를 OmniRoute 로컬 엔드포인트(`http://localhost:20128/v1`)로 지시해 무료 또는 저비용 모델로 챗봇을 운영합니다.
- **빠른 프로토타이핑**: 새 AI 기능을 개발할 때 OmniRoute로 여러 최신 모델을 빠르게 테스트·비교합니다. `auto` 모델 ID는 최적의 모델을 찾아 주므로 모델 선택 시간을 줄여 줍니다.
- **장시간 프로젝트 맥락 유지**: 며칠에 걸친 프로젝트에서 세션을 다시 열 때마다 Claude-mem이 이전 작업을 요약해 보여줘 "어제 하던 작업 이어서 해줘" 같은 요청도 맥락을 이해하고 처리합니다.
- **반복 수정 코드 생성**: 개발자가 특정 스타일이나 로직을 반복 수정하는 패턴을 Task Observer가 학습해, 다음 코드 생성 시 처음부터 더 만족스러운 결과를 받아 추가 토큰 소모를 줄입니다.
- **긴 문서 요약 재작성**: 긴 보고서를 요약할 때 Headroom이 원본 압축으로 토큰을 줄이고, 사용자가 특정 관점을 반복 요청하면 Task Observer가 이를 학습해 다음 요약에 반영합니다.

## 💡 아이디어

- 5축 절약을 기본으로 깔고, Claude-mem 으로 맥락을 잇고, 한도가 찬 날만 라우터로 환승하는 3단 운영으로 개인 프로젝트의 개발 속도와 프로토타이핑 시간을 단축할 수 있습니다.
- 정기적인 코드 리뷰나 신기술 학습 보조 도구로 Claude Code를 쓰되, 압축·맥락 유지 도구를 함께 활용해 대규모 프로젝트에서도 지속적인 학습·개발을 지원받을 수 있습니다.
- Headroom과 Task Observer를 결합하면 개인 맞춤형 프롬프트 엔지니어링 도구를 만들 수 있습니다. Task Observer가 사용자의 코딩 스타일·자주 하는 질문 유형·선호 결과물 형식을 학습하고, Headroom이 이를 바탕으로 Claude에 전달되는 프롬프트를 최적화해 토큰은 최소화하면서 결과 정확도는 높이는 방식입니다.
- **팀 공유 게이트웨이**: OmniRoute를 팀 서버에 구축하고, 팀원들이 공유 API 키나 계정을 사용하지 않고 각자의 환경에서 OmniRoute 엔드포인트만 바라보도록 설정해 AI 리소스 사용을 효율화하고 비용을 관리할 수 있습니다.
- **성능 모니터링**: OmniRoute의 로깅·분석 기능이나 FreeLLMAPI 의 Analytics 탭으로 모델별 응답 속도, 토큰 사용량, 비용 등을 모니터링하고 자기 작업에 맞는 모델 순서를 찾을 수 있습니다.

## 주의사항

**도구 조합**
- OmniRoute(또는 FreeLLMAPI)와 Headroom은 클로드 앞단에서 같은 자리를 차지(환승 vs 압축)하므로 하나만 선택해 사용하는 것이 좋습니다.
- 본 가이드는 클로드 코드 CLI 버전 기준이며, 데스크톱 앱은 특히 Headroom 기능이 제한될 수 있습니다.

**절약 설정**
- CLAUDE.md 룰북 과도 적용 X — "1줄로만" 같은 강한 규제는 답변 품질 저하로 이어질 수 있습니다.
- `/clear`는 복구 불가 — 반드시 작업 전환 시에만 사용합니다.
- 서브에이전트 Opus 병렬 실행 = 서브에이전트 수만큼 비용 곱연산 폭증 → 단순 조사는 반드시 모델을 명시합니다.
- autocompact 50% 이하는 역효과 — 압축이 너무 잦아 작업 흐름이 끊깁니다.
- 장시간 압축된 세션은 환각 가능성이 높아집니다 — 중요 작업은 새 세션에서 진행합니다.
- 2026-05-13~07-13(PDT 7/13 18:00 만료) 한도 50% 인상은 Free 플랜 제외였고, 현재는 이미 원래 한도로 복귀한 상태입니다. 관련 체크리스트는 유사 이벤트 재발 시 참고용입니다.

**압축(Headroom)**
- 절감률(60~95%, 최대 95%/약 20%/40~50% 등, OmniRoute 압축의 15-95% 포함)은 절대 수치가 아닌 최대 기대치이며 실제 작업 환경에 따라 달라집니다.
- 중요한 코드나 핵심 에러 로그를 압축하는 과정에서 맥락이 유실될 수 있으니, 처음에는 작은 프로젝트나 덜 민감한 데이터로 테스트합니다.
- 숫자가 중요한 데이터(금융 정보 등)는 압축 시 정밀도가 보장되지 않을 수 있습니다.
- 팀 단위로 쓸 때는 개인 로컬 설정과 팀 공용 설정을 분리 운영해야 예상치 못한 문제를 막을 수 있습니다.
- 터미널 창이 닫히면 압축이 중단됩니다.

**무료 모델 환승(OmniRoute·FreeLLMAPI)**
- 무료 모델로 환승하면 요청 내용이 해당 제3자 서버로 전송됩니다. 민감한 정보·중요한 코드는 보내지 마세요. 각 회사의 무료 티어 약관도 각자 확인하세요.
- FreeLLMAPI 의 키는 내 컴퓨터에만 있고, 라우터가 밖으로 보내는 건 각 회사에 보내는 요청뿐입니다. OmniRoute 도 로컬에서 실행되므로 외부 노출에 주의하고, 중요한 키 정보는 `.env` 파일 등으로 안전하게 관리합니다.
- 무료 티어는 회사 마음입니다. 제공 토큰에 한계가 있고, 어느 날 한도가 줄거나 모델이 사라질 수 있습니다. FreeLLMAPI 는 하루 두 번 카탈로그를 받아 스스로 고치지만, 무료판은 새 모델이 30일 늦게 들어옵니다(유료 「Premium」은 카탈로그를 당일 반영해 주는 것뿐이고, 라우터 자체는 계속 무료입니다). 대규모 사용 시에는 유료 모델 사용을 고려합니다.
- 무료 모델은 상용 유료 모델에 비해 성능·안정성이 떨어질 수 있고 모델마다 실력이 다릅니다. 어려운 코드는 GPT-OSS 120B나 GLM-4.7 같은 큰 모델이 잡히도록 순서를 올려 둡니다.
- 회사 서비스에 붙이지 마세요. FreeLLMAPI 저장소가 스스로 「개인 실험용」이라고 적어 두었습니다.
- FreeLLMAPI 를 클로드 코드에 연결할 때 주소 끝에 `/v1` 을 붙이면 안 됩니다. `http://localhost:3001` 뿌리 주소만 씁니다.

**맥락 유지(Claude-mem·Task Observer)**
- Claude-mem 은 설치 후 클로드 코드를 완전히 재시작해야 활성화됩니다.
- Task Observer는 `references` 폴더 데이터로 성능을 최적화하므로 이 폴더를 불필요하게 삭제하면 효과가 감소합니다.
- Task Observer는 사용자 패턴을 학습하는 데 시간이 걸려 초기에는 큰 효과를 못 느낄 수 있지만 꾸준히 쓰면 성능이 향상됩니다.

**더 볼 자료**
- Claude AI가 처음이거나 도구 설정이 낯설다면 claude-mem(Claude 모델의 기억력 향상), claude-code-setup(Claude 코딩 환경 설정), OmniRoute(라우팅 최적화) 문서와 "[에이나우] 클로드 토큰 아끼는 2가지 설치 가이드북"을 먼저 참고하는 것이 좋습니다.

## 출처

- [https://fieldby.notion.site/3-3c7d730b395381c7b605cc88ea8b152c?pvs=149](https://fieldby.notion.site/3-3c7d730b395381c7b605cc88ea8b152c?pvs=149)
- [https://yeongseon.kr/archive/3bfd86104de2802cbe10d6ca4aee512f.html?fbclid=PAVERFWAUDr_VwZG9mAmZkaWQWUNnqK4_WfI9gCsn3Z63HcTEKOu2EoWV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp0umc4DTXWajmYL-XeAYxIqLLiuq9aOqsLlp0RYN5F2T_M5lzkcR1nBfebKF_aem_H_7ffADoSghuOtZdWg4ixQ](https://yeongseon.kr/archive/3bfd86104de2802cbe10d6ca4aee512f.html?fbclid=PAVERFWAUDr_VwZG9mAmZkaWQWUNnqK4_WfI9gCsn3Z63HcTEKOu2EoWV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp0umc4DTXWajmYL-XeAYxIqLLiuq9aOqsLlp0RYN5F2T_M5lzkcR1nBfebKF_aem_H_7ffADoSghuOtZdWg4ixQ)
- [https://abounding-helmet-0e4.notion.site/Claude-Code-Headroom-38d73c7b15ad813190abf555ad0bf667?pvs=149](https://abounding-helmet-0e4.notion.site/Claude-Code-Headroom-38d73c7b15ad813190abf555ad0bf667?pvs=149)
- [https://waiting-drug-536.notion.site/73-34bd86104de28031b19ff79353c17b83](https://waiting-drug-536.notion.site/73-34bd86104de28031b19ff79353c17b83)
- [https://abounding-helmet-0e4.notion.site/50-300-36373c7b15ad81ccac8ded33f43886d5](https://abounding-helmet-0e4.notion.site/50-300-36373c7b15ad81ccac8ded33f43886d5)
- [https://wandering-mile-86e.notion.site/FreeLLMAPI-3e398dec8eed814d8e9cd2e698076403?pvs=149](https://wandering-mile-86e.notion.site/FreeLLMAPI-3e398dec8eed814d8e9cd2e698076403?pvs=149)
- [https://github.com/diegosouzapw/OmniRoute?fbclid=PAVERFWAT5qhtwZG9mAmZkaWQWUNHYLf1kPOw6dg1dr2eXutgZpVf0EGV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABpygtIkWa1Avaq69_5wlE1kjoNdCyM4eJF9X0fDeS85ErLCZYU7Ab_BQEtVAR_aem_pghrJzxBaJS4VedSgGP73g](https://github.com/diegosouzapw/OmniRoute?fbclid=PAVERFWAT5qhtwZG9mAmZkaWQWUNHYLf1kPOw6dg1dr2eXutgZpVf0EGV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABpygtIkWa1Avaq69_5wlE1kjoNdCyM4eJF9X0fDeS85ErLCZYU7Ab_BQEtVAR_aem_pghrJzxBaJS4VedSgGP73g)
