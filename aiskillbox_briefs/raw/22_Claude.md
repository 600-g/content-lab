# Claude Code 신기능 완전 정리 — /goal & Agent View 실전 가이드

- URL: https://resonant-frog-df5.notion.site/Claude-Code-goal-Agent-View-35f3a1a32343814082d5f0245cb359e5
- source_type: notion
- length: 5247 chars
- scraped_at: 2026-05-27 01:04:05
- elapsed: 5s
- ok: True
- error: 

---

📌 이 포스팅은 Claude Code 공식 문서를 기반으로 작성되었습니다. 팔로워분들과 공유하기 위한 실전 활용 가이드예요.

### 이번에 소개할 두 가지 기능

Claude Code v2.1.139에서 동시에 출시된 두 가지 강력한 신기능입니다:

/goal

— Claude가 조건을 만족할 때까지 스스로 계속 작동하게 만드는 명령어Agent View — 여러 Claude 세션을 한 화면에서 모니터링하고 관리하는 대시보드

두 기능 모두 "Claude에게 일을 맡기고 내가 다른 일을 하자"는 자율 워크플로우를 위한 기능이에요.

## PART 1 — /goal : 조건이 충족될 때까지 Claude가 혼자 달린다

### /goal 이 뭔가요?

/goal

은 완료 조건을 설정하면 Claude가 그 조건이 충족될 때까지 여러 턴에 걸쳐 자동으로 계속 작업하는 명령어입니다.기존 방식과 비교해볼게요.

기존 방식: Claude에게 지시 → Claude가 한 턴 작업 → 결과 확인 → 다시 지시 → 반복...

/goal

방식: 완료 조건 설정 → Claude가 조건 달성 때까지 자동 반복 → 완료 시 알림 ✅🔑 핵심:/goal을 쓰면 Claude가 "이게 완료됐는지" 스스로 판단하면서 작업을 이어갑니다. 개발자는 그 시간에 다른 일을 할 수 있어요.

### /goal vs 다른 자율 워크플로우 비교

방식 | 다음 턴 시작 시점 | 중지 시점 | 주요 사용 사례 |
|---|---|---|---|
/goal | 이전 턴이 완료될 때 | 모델이 조건 충족을 확인했을 때 | 테스트 통과, 빌드 성공 등 결과 기반 작업 |
/loop | 설정한 시간 간격마다 | 사용자가 중지하거나 Claude가 완료 판단 시 | 주기적 반복 작업 (모니터링, 정기 리포트) |
Stop hook | 이전 턴이 완료될 때 | 사용자 스크립트/프롬프트가 결정 | 고급 커스텀 자동화 |

💡 언제/goal을 쓸까? 결과물이 특정 조건을 만족해야 할 때 (테스트 통과, 린트 클린, 파일 생성 등)가 딱 맞아요.

### /goal 사용법 A to Z

#### 1. 목표 설정하기

/goal [완료 조건 설명]

실전 예시:

# 예시 1: 테스트 통과 조건
/goal all tests in test/auth pass and the lint step is clean
# 예시 2: 파일 생성 조건
/goal CHANGELOG.md has an entry for every PR merged this week
# 예시 3: 안전장치 포함 (최대 20턴)
/goal all API endpoints return 200 or stop after 20 turns

목표가 설정되면 입력창 옆에

◎ /goal active

표시가 뜹니다.#### 2. 효과적인 조건 작성 꿀팁

⚠️ 중요:/goal의 평가자는 Claude의 출력(대화 내용)을 기반으로 조건을 판단합니다. 파일을 직접 읽거나 명령어를 실행하지 않아요.

좋은 조건 예시:

✅ "all tests in test/auth pass"
→ Claude가 npm test를 실행하고 결과를 출력하면 평가자가 읽을 수 있음
✅ "git status shows no uncommitted changes"
→ Claude가 git status 결과를 출력에 포함시킴
✅ "the build completes without errors or stop after 20 turns"
→ 안전장치(최대 턴 수)까지 포함

피해야 할 조건 예시:

❌ "the database is optimized"
→ 너무 모호함. 평가자가 판단하기 어려움
❌ "user experience is improved"
→ 측정 불가능한 조건

#### 3. 상태 확인 / 목표 지우기

# 현재 목표 상태 확인
/goal
# 목표 취소 및 지우기 (아래 표현 모두 동일하게 작동)
/goal clear
/goal stop
/goal off
/goal cancel

#### 4. 중단된 세션 이어서 재개하기

# 활성 목표가 있던 세션 재개
claude --resume
claude --continue

#### 5. 비대화형(Non-interactive) 모드로 실행하기

터미널에서 직접 실행하거나 자동화 스크립트에 넣을 때 유용해요.

claude -p "/goal CHANGELOG.md has an entry for every PR merged this week"

### /goal 내부 작동 원리

Claude가 한 턴을 마칠 때마다 아래 과정이 일어납니다:

[Claude 작업 완료]
↓
[평가자 모델 호출 - 기본값: Claude Haiku (빠른 소형 모델)]
↓
조건 충족? ─── YES ──→ [작업 완료, 사용자에게 제어권 반환]
│
NO
↓
[Claude 다음 턴 자동 시작]
↓
(반복...)

🧠 포인트: 작업하는 Claude와 조건을 판단하는 평가자가 분리되어 있어요. 덕분에 더 객관적인 판단이 가능합니다. 진행 중에는 오버레이 패널에서 경과 시간, 턴 수, 토큰 사용량을 실시간으로 확인할 수 있어요.

### /goal 사용 전 필수 확인사항

Claude Code 최신 버전 필요 (v2.1.139 이상)

disableAllHooks

설정이 되어 있으면 /goal

이 작동하지 않음세션당 목표는 1개만 활성화 가능

## PART 2 — Agent View : 여러 Claude를 한 화면에서 관리하기

### Agent View가 뭔가요?

claude agents

명령어로 열리는 Claude Code 세션 전체 모니터링 대시보드입니다.실행 중인 세션, 내 입력을 기다리는 세션, 완료된 세션을 한눈에 파악하고 직접 제어할 수 있어요.

💡 쉽게 말하면: Claude 여러 개를 동시에 돌리면서 "어느 Claude가 막혔는지, 어느 Claude가 잘 달리고 있는지" 대시보드로 확인하는 기능이에요.

### Agent View 시작하기

claude agents

Esc 키로 닫을 수 있어요.

### 핵심 키보드 단축키

#### 기본 탐색

단축키 | 동작 |
|---|---|
↑ / ↓ | 세션 목록에서 이동 |
Enter | 선택한 세션에 연결(attach) |
Space | 세션 미리보기(peek) 패널 열기/닫기 |
Shift+Enter | 디스패치하고 바로 연결 |
→ | 선택한 세션에 연결 |
Alt+1 ~ Alt+9 | N번째 세션에 바로 연결 |
Esc | 미리보기 닫기 / 입력 초기화 / 종료 |
? | 전체 단축키 목록 보기 |

#### 세션 관리

단축키 | 동작 |
|---|---|
Ctrl+R | 세션 이름 변경 |
Ctrl+T | 세션 고정(pin) / 고정 해제 |
Ctrl+X | 세션 중지 (2초 내 다시 누르면 삭제) |
Shift+↑ / Shift+↓ | 세션 순서 변경 |
Ctrl+S | 그룹 기준 전환 (상태 기준 ↔ 디렉토리 기준) |
Ctrl+G | $EDITOR 에서 디스패치 프롬프트 작성 |

### 세션 연결(Attach)과 분리(Detach)

# 세션에 연결: Enter 또는 →
# 연결 해제 (Agent View로 돌아가기): ←
# 백그라운드로 전환: /bg 입력 후 ←

### 새 세션 디스패치(실행) 방법

#### Agent View 내에서

입력 방식 | 동작 |
|---|---|
[프롬프트] • Enter | 일반 세션 실행 |
<agent-name> <prompt> | 커스텀 서브에이전트로 실행 |
@<agent-name> | 프롬프트 어디서든 특정 에이전트 지정 |
@<repo> | 특정 레포지토리 경로에서 세션 실행 |
/<skill> | 스킬을 프롬프트로 사용해 디스패치 |
#<PR번호> 또는 PR URL | 해당 PR 작업 세션 선택 |
Shift+Enter | 디스패치하고 즉시 연결 |

#### 터미널 쉘에서 직접 실행

# 백그라운드로 세션 실행
claude --bg "리팩토링 작업 진행해줘"
# 특정 세션에 연결
claude attach <session-id>

### 세션 필터링

세션이 많아질수록 유용한 기능입니다.

필터 | 표시 내용 |
|---|---|
a:<에이전트이름> | 해당 에이전트를 실행 중인 세션만 표시 |
s:<상태> | 특정 상태의 세션만 표시 |
s:blocked | 🚨 내 입력을 기다리는 세션만 표시 |
#<PR번호> 또는 PR URL | 해당 PR 작업 중인 세션 |

🎯 실무 팁:s:blocked필터가 가장 자주 씁니다. Claude 여러 개 돌릴 때 "지금 당장 내가 봐야 할 세션"만 빠르게 추려줘요.

### 터미널에서 사용하는 쉘 명령어 모음

# Agent View 열기
claude agents
# 특정 세션에 연결
claude attach <session-id>
# 세션의 최근 출력 로그 확인
claude logs <session-id>
# 세션 중지
claude stop <session-id>
claude kill <session-id> # 동일한 명령어
# 중지된 세션을 대화 내용 유지하며 재시작
claude respawn <session-id>
# 중지된 모든 세션 한 번에 재시작
claude respawn --all
# 목록에서 세션 제거
claude rm <session-id>

### /goal + Agent View 함께 쓰는 법

이 두 기능은 함께 쓸 때 시너지가 극대화됩니다.

1. claude agents 로 Agent View 열기
2. 여러 세션 디스패치 (각각 다른 작업)
3. 각 세션에 /goal 설정
예) 세션 A: /goal all unit tests pass
세션 B: /goal API docs are generated
세션 C: /goal migration script runs without errors
4. s:blocked 필터로 내 응답이 필요한 세션만 확인
5. 완료된 세션은 Space로 결과 미리보기

🔥 실무 적용 예: 코드 리뷰, 테스트 수정, 문서 생성을 각각 별도 Claude 세션에/goal로 맡기고, Agent View에서s:blocked만 모니터링하면 됩니다.

### 한눈에 정리

기능 | 명령어 | 핵심 가치 |
|---|---|---|
목표 기반 자동 실행 | /goal [조건] | Claude가 조건 달성까지 혼자 달림 |
목표 취소 | /goal clear | 언제든 중단 가능 |
전체 세션 대시보드 | claude agents | 여러 Claude 한눈에 관리 |
막힌 세션만 필터 | s:blocked | 내가 봐야 할 것만 추려냄 |
세션 재시작 | claude respawn <id> | 대화 유지하며 재실행 |

📌 참고 공식 문서
