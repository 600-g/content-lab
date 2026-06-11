💡 이 스킬은 **Claude Code v2.1.139 신기능 `/goal` + `claude agents` Agent View** 활용 가이드로, **완료 조건 달성까지 Claude 가 자율 실행 + 여러 세션을 한 대시보드에서 동시 관리**하는 자율 워크플로우 구축법입니다.

## 이게 뭔가요?

**Claude Code v2.1.139 에 동시 출시된 두 가지 자율 워크플로우 신기능**:

**기능 / 역할**:

- **`/goal`** / Claude 가 **조건 충족 때까지** 여러 턴에 걸쳐 **자동으로 계속 작업**
- **Agent View (`claude agents`)** / 여러 Claude 세션을 한 화면에서 **모니터링·관리하는 대시보드**


공통 철학: **"Claude 에게 일을 맡기고 내가 다른 일을 하자"**.

**`/goal` vs 기존 방식**:

**방식 / 흐름**:

- **기존** / 지시 → 1턴 → 결과 확인 → 다시 지시 → 반복
- **`/goal`** / **완료 조건 설정 → Claude 가 조건 달성 때까지 자동 반복 → 완료 시 알림** ✅


**`/goal` vs 다른 자율 워크플로우 비교**:

**방식 / 다음 턴 시작 시점 / 중지 시점 / 사용 사례**:

- **`/goal`** / 이전 턴 완료 시 / 모델이 조건 충족 확인 시 / **테스트 통과·빌드 성공** 등 결과 기반
- **`/loop`** / 설정 시간 간격마다 / 사용자 중지 또는 Claude 완료 판단 / 주기적 모니터링·정기 리포트
- **Stop hook** / 이전 턴 완료 시 / 사용자 스크립트가 결정 / 고급 커스텀 자동화


💰 유료 필요: Claude Pro 이상 (Claude Code v2.1.139+)
✅ 무료 대안: `/loop` 만 사용하거나 수동 반복 — `/goal` 자체는 Pro 전용

## 따라하기

### PART 1 — `/goal` 사용법

**1. 목표 설정하기**

```bash
/goal [완료 조건 설명]
```

실전 예시:

```bash
# 예시 1: 테스트 통과 조건
/goal all tests in test/auth pass and the lint step is clean

# 예시 2: 파일 생성 조건
/goal CHANGELOG.md has an entry for every PR merged this week

# 예시 3: 안전장치 포함 (최대 20턴)
/goal all API endpoints return 200 or stop after 20 turns
```

목표 설정 후 입력창 옆에 **`◎ /goal active`** 표시.

**2. 효과적인 조건 작성 꿀팁**

⚠️ **중요**: `/goal` 평가자는 **Claude 출력(대화 내용)을 기반**으로 조건 판단. 파일을 직접 읽거나 명령 실행 X.

**좋은 조건 / 피해야 할 조건**:

- ✅ `all tests in test/auth pass` (npm test 결과 출력) / ❌ `the database is optimized` (너무 모호)
- ✅ `git status shows no uncommitted changes` / ❌ `user experience is improved` (측정 불가)
- ✅ `the build completes without errors or stop after 20 turns` (안전장치) / ❌ `the code is better`


**3. 상태 확인 / 목표 지우기**

```bash
# 현재 목표 상태 확인
/goal

# 목표 취소 (모두 동일하게 작동)
/goal clear
/goal stop
/goal off
/goal cancel
```

**4. 중단된 세션 이어서 재개**

```bash
# 활성 목표가 있던 세션 재개
claude --resume
claude --continue
```

**5. 비대화형 모드 (자동화 스크립트)**

```bash
claude -p "/goal CHANGELOG.md has an entry for every PR merged this week"
```

### `/goal` 내부 작동 원리

```
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
```

🧠 **포인트**: **작업 Claude 와 평가자 분리** → 더 객관적 판단. 진행 중 오버레이 패널에서 **경과 시간·턴 수·토큰 사용량** 실시간 확인.

### `/goal` 사용 전 확인사항

- Claude Code **v2.1.139 이상** 필요
- `disableAllHooks` 설정 시 `/goal` 작동 X
- **세션당 목표 1개만** 활성화 가능

### PART 2 — Agent View (`claude agents`)

```bash
claude agents     # Agent View 열기
# Esc 키로 닫음
```

여러 세션을 한 화면에서 모니터링.

**핵심 키보드 단축키**:

**단축키 / 동작**:

- ↑ / ↓ / 세션 목록 이동
- **Enter** / 선택 세션에 연결
- **Space** / 세션 미리보기 패널
- Shift+Enter / 디스패치하고 바로 연결
- Alt+1 ~ Alt+9 / N번째 세션 바로 연결
- ? / 전체 단축키 보기


**세션 관리**:

**단축키 / 동작**:

- **Ctrl+R** / 세션 이름 변경
- **Ctrl+T** / 세션 고정(pin)
- **Ctrl+X** / 세션 중지 (2초 내 다시 누르면 삭제)
- Ctrl+S / 그룹 기준 전환 (상태 ↔ 디렉토리)
- Ctrl+G / `$EDITOR` 에서 디스패치 프롬프트 작성


**연결(Attach)과 분리(Detach)**:

```bash
# 세션에 연결: Enter 또는 →
# 연결 해제 (Agent View로 돌아가기): ←
# 백그라운드 전환: /bg 입력 후 ←
```

**Agent View 내 새 세션 디스패치**:

**입력 / 동작**:

- `[프롬프트]` + Enter / 일반 세션
- `<agent-name> <prompt>` / 커스텀 서브에이전트
- `@<agent-name>` / 프롬프트 어디서든 특정 에이전트 지정
- `@<repo>` / 특정 레포 경로에서 세션
- `/<skill>` / 스킬을 프롬프트로 사용
- `#<PR번호>` 또는 PR URL / 해당 PR 작업 세션


**터미널 직접 명령**:

```bash
claude agents                          # Agent View 열기
claude --bg "리팩토링 진행해줘"           # 백그라운드 세션
claude attach <session-id>             # 세션 연결
claude logs <session-id>               # 최근 출력 로그
claude stop <session-id>               # 세션 중지
claude respawn <session-id>            # 대화 유지하며 재시작
claude respawn --all                   # 중지된 모든 세션 재시작
claude rm <session-id>                 # 목록에서 제거
```

**세션 필터링** (세션 많아질수록 핵심):

**필터 / 표시**:

- `a:<에이전트이름>` / 해당 에이전트 실행 세션
- `s:<상태>` / 특정 상태 세션
- **`s:blocked`** / 🚨 **내 입력 기다리는 세션만**
- `#<PR번호>` / 해당 PR 작업 중인 세션


🎯 **실무 팁**: `s:blocked` 가 가장 자주 씀. 여러 세션 돌릴 때 **"지금 당장 봐야 할 세션"만 추려줌**.

### `/goal` + Agent View 함께 쓰기

```
1. claude agents → Agent View 열기
2. 여러 세션 디스패치 (각각 다른 작업)
3. 각 세션에 /goal 설정
   - 세션 A: /goal all unit tests pass
   - 세션 B: /goal API docs are generated
   - 세션 C: /goal migration script runs without errors
4. s:blocked 필터로 응답 필요 세션만 확인
5. 완료 세션은 Space 로 결과 미리보기
```

🔥 **실무 적용 예**: 코드 리뷰·테스트 수정·문서 생성을 **각각 별도 세션 + /goal** 로 맡기고, Agent View 에서 `s:blocked` 만 모니터링.

## 활용 예시

- **시니어 개발자 — 야간 자동 리팩토링** — 퇴근 전 3개 세션에 `/goal` 설정 (테스트 통과·린트 클린·문서 자동 생성). 다음날 출근 시 모두 완료. 워라밸·생산성 동시 확보
- **테스트 자동화 — TDD 사이클 자동 완주** — `/goal all tests pass and coverage > 80%` 로 RED → GREEN → REFACTOR 자동 사이클 완주
- **데브옵스 — 마이그레이션 자동 검증** — `/goal migration runs without errors and rollback test passes` 로 마이그레이션 안전성 자동 검증
- **AI 강사 — 학생 실습 자동 채점** — 각 학생 PR 에 `/goal lint clean and tests pass` 자동 평가. 1인이 50명 강의 가능
- **오픈소스 메인테이너 — 컨트리뷰터 PR 빠른 검토** — 새 PR 들어오면 `/goal` + Agent View `#<PR번호>` 필터로 일괄 점검
- **연구자 — 실험 반복** — 같은 코드 파라미터 5종 변경 동시 실행. Agent View 로 결과 한눈에 비교
- **컨설턴트 — 클라이언트 다중 운영** — 클라이언트 A·B·C 작업 별도 세션 → `s:blocked` 만 알림 → 막힌 곳만 응답

## 💡 아이디어

- **Agent View 모니터링 SaaS** — 외부 대시보드에서 본인 Claude 세션들 통합 모니터링 + 슬랙·텔레그램 알림 → 월 $10
- **`/goal` 라이브러리** — 직군별·작업별 검증된 goal 조건 100개 모음 → 카테고리별 $20-30
- **AI 자율 작업 큐 시스템** — 회사 내 Claude 세션 풀 관리 + 우선순위 자동 할당 → 엔터프라이즈 $500-1000/월
- **PR 자동 처리 봇** — `/goal` 기반으로 새 PR 마다 자동 lint·test·doc 처리. 메인테이너 부담 90% 절감
- **Claude Code 학습 코스** — `/goal` + Agent View 활용법 4시간 강의 ($100-200)
- **자율 실행 시간 통계** — 사용자의 자율 작업 패턴 분석 → 어떤 작업에 자율 실행 효과적인지 인사이트 제공

## 주의사항

- **Claude Code v2.1.139 이상 필수** — 구버전은 `/goal` 미지원
- **세션당 1개 목표만** — 동시 여러 goal 설정 불가
- **조건이 모호하면 무한 루프** — "코드 품질 향상" 같은 측정 불가 조건 피하기. 항상 **객관적 검증 가능한 조건** + **안전장치 (`or stop after 20 turns`)**
- **평가자는 출력만 본다** — 파일·시스템 상태를 자동 체크 X. Claude 가 결과를 **출력에 명시적으로 포함**해야 평가자가 판단 가능
- **disableAllHooks 와 충돌** — Hook 비활성화 설정 시 `/goal` 작동 X
- **자율 실행 비용 관리** — 무한 루프 가능성. 안전장치 턴 수 제한 항상 권장
- **AgentView 멀티 세션은 메모리 부담** — 동시 10+ 세션 운영 시 노트북 RAM 16GB 이상 권장

## 출처

- [Claude Code 신기능 완전 정리 — /goal & Agent View 실전 가이드 (Notion)](https://resonant-frog-df5.notion.site/Claude-Code-goal-Agent-View-35f3a1a32343814082d5f0245cb359e5)
- 원본: Claude Code 공식 문서 기반
