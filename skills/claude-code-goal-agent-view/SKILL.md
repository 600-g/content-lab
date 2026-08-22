---
name: claude-code-goal-agent-view
description: Claude Code v2.1.139의 /goal 자율 실행 + claude agents Agent View 대시보드를 활용해 완료 조건 달성까지 Claude가 자동으로 반복 실행하고 여러 세션을 한 화면에서 모니터링하는 자율 워크플로우 가이드
origin: content-lab
sources:
  - https://resonant-frog-df5.notion.site/Claude-Code-goal-Agent-View-35f3a1a32343814082d5f0245cb359e5
---

# Claude Code 자율실행 모드 (/goal + Agent View)

## 이게 뭔가요?

Claude Code v2.1.139에 동시 출시된 자율 워크플로우 신기능:

- **`/goal`** — 조건 충족까지 여러 턴 자동 반복
- **Agent View (`claude agents`)** — 여러 세션 통합 모니터링 대시보드

철학: "Claude에게 일을 맡기고 내가 다른 일을 하자"

## 따라하기

### PART 1 — `/goal` 사용법

**목표 설정:**
```bash
/goal all tests in test/auth pass and the lint step is clean
/goal CHANGELOG.md has an entry for every PR merged this week
/goal all API endpoints return 200 or stop after 20 turns
```

목표 활성 시 입력창 옆 `◎ /goal active` 표시.

**효과적인 조건 작성 원칙:**
- ✅ 객관적 검증 가능: `all tests pass`, `git status shows no uncommitted changes`
- ✅ 안전장치 포함: `or stop after 20 turns`
- ❌ 모호한 조건 금지: "the code is better", "database is optimized"

**상태 확인 / 취소:**
```bash
/goal              # 상태 확인
/goal clear        # 취소 (stop / off / cancel 동일)
claude --resume    # 중단 세션 재개
```

**비대화형 자동화:**
```bash
claude -p "/goal CHANGELOG.md has entry for every PR merged this week"
```

### PART 2 — Agent View

```bash
claude agents      # 열기 (Esc로 닫음)
```

**핵심 키:**
- Enter / → : 세션 연결
- ← : 분리 (Agent View 복귀)
- Space : 미리보기
- Alt+1~9 : N번째 세션 바로 연결
- Ctrl+R : 세션 이름 변경
- Ctrl+T : 세션 pin
- Ctrl+X : 세션 중지 (2초 내 재클릭 시 삭제)

**세션 필터링:**
- `s:blocked` — 🚨 **내 입력 기다리는 세션만** (실무 최다 사용)
- `a:<에이전트>` — 특정 에이전트 세션
- `#<PR번호>` — PR 관련 세션

**터미널 명령:**
```bash
claude --bg "리팩토링 진행해줘"
claude attach <session-id>
claude logs <session-id>
claude respawn <session-id>
claude respawn --all
```

### 조합 활용
```
1. claude agents → Agent View
2. 여러 세션 디스패치
3. 각 세션에 /goal 설정
4. s:blocked 필터로 응답 필요 세션만 확인
```

## 주의사항

- Claude Code v2.1.139 이상 필수
- 세션당 목표 1개만
- 모호한 조건 = 무한 루프 위험 → 안전장치(턴 수 제한) 필수
- 평가자는 **출력만 봄** — 파일/시스템 상태 자동 체크 X
- `disableAllHooks` 설정 시 `/goal` 작동 X
- 동시 10+ 세션은 RAM 16GB+ 권장

## 출처
- [Claude Code /goal + Agent View 가이드](https://resonant-frog-df5.notion.site/Claude-Code-goal-Agent-View-35f3a1a32343814082d5f0245cb359e5)
