---
name: claude-code-token-saving
description: Claude Code 토큰 73% 절약 통합 패턴 — /usage /compact /clear 명령 + CLAUDE.md 룰북 + 서브에이전트 위임 + autocompact 조정 + Skill 분할의 5축 전략으로 주간 한도 안에서 작업량을 3배 늘리는 실전 가이드
origin: content-lab
sources:
  - https://waiting-drug-536.notion.site/73-34bd86104de28031b19ff79353c17b83
---

# Claude Code 토큰 절약 치트시트

## 이게 뭔가요?

Claude Code 토큰 소비를 73%까지 줄여 작업량을 3배 이상 늘리는 5축 절약 통합 패턴.

| 축 | 효과 |
|---|---|
| 명령어 3종 (`/usage` `/compact` `/clear`) | 20-30% |
| CLAUDE.md 룰북 | 20-30% |
| 서브에이전트 위임 | 15-25% |
| autocompact 조정 | 10-15% |
| Skill 분할 | 5-10% |

총합 **~73%** (중복 효과 반영).

## 따라하기

### 축 1. 핵심 명령어 3종

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

### 축 2. CLAUDE.md 룰북

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
- 대규모 조사·분석은 서브에이전트 위임.
- 메인 컨텍스트는 지휘·검토만.
- 단순 검색은 메인에서 직접.

# Token Saving
- 코드 변경 후 변경된 부분만 (diff 형태).
- 100줄 이상 새 파일은 미리 확인.
- 명시하지 않은 추가 기능 자발 추가 X.
```

### 축 3. 서브에이전트 위임 패턴

**기본 원칙:**
- 격리 작업 — 서브에이전트는 격리된 컨텍스트
- 결과만 반환 — 진행 과정 숨김
- 파일로 저장 — 3개 이상 병렬 시 각 결과 개별 파일

**🚨 Opus 비용 함정:**
- 서브에이전트는 부모 모델 상속 → Opus 5개 병렬 = **비용 5배**
- 해결: 단순 조사·크롤링은 명시적 `--model sonnet` 또는 `--model haiku`

**위임 기준:**
- ✅ 다중 모듈 조사 / 병렬 코드 리뷰 / 대규모 리팩토링 / 문서 양산
- ❌ 단일 검색 / 짧은 Lookup / 순차 의존성 / 1-2턴 작업

### 축 4. autocompact 임계값

`~/.claude/settings.json`:
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

시작: **70%** → 1주 사용 후 조정.

### 축 5. Skill 분할

대규모 리팩토링 X → **5개 단위 작업**으로 분할:
```
1차: "auth 모듈만 리팩토링" + /goal lint clean and tests pass
   ↓ /clear
2차: "API 모듈만 리팩토링" + /goal
   ↓ /clear
...
```

## 7일 점진적 도입

| 일차 | 작업 |
|---|---|
| Day 1 | `/usage` 매 작업 전후 습관화 |
| Day 2 | `CLAUDE.md` 룰북 적용 |
| Day 3 | autocompact 70% 설정 |
| Day 4 | 첫 서브에이전트 위임 (단순 조사부터) |
| Day 5 | `/compact` 적극 활용 |
| Day 6 | 큰 작업 5개 단위 분할 |
| Day 7 | 본인 패턴 분석 + 룰북 개인화 |

## 주의사항

- CLAUDE.md 룰북 과도 X — "1줄로만" 강한 규제는 품질 저하
- `/clear`는 복구 불가 — 작업 전환 시에만
- 서브에이전트 Opus 폭주 = 5배 비용 → 반드시 모델 명시
- autocompact 50% 이하 역효과 — 작업 흐름 끊김
- 장시간 압축된 세션은 환각 가능성 ↑ — 중요 작업은 새 세션

## 출처
- [클로드코드 토큰 73% 절약](https://waiting-drug-536.notion.site/73-34bd86104de28031b19ff79353c17b83)
