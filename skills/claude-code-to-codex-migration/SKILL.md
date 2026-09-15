---
name: claude-code-to-codex-migration
description: 이 스킬은 **Claude Code**에서 구축한 작업 환경(Instruction 파일, Skills, Slash commands, Subagents, MCP 설정, Hooks, 세션 기록)을 **OpenAI Codex**로 클릭 한 번에 이주시키는 방법을 정리한 스킬입니다.
origin: content-lab
grade: A
difficulty: 초급
category: 개발
ai_tools: ["Claude", "Claude Code", "Codex"]
sources:
  - https://abounding-helmet-0e4.notion.site/Claude-Code-Codex-35873c7b15ad81fa95a4d608d35164a3?pvs=149
---

# Claude Code 설정 Codex로 이전

💡 이 스킬은 **Claude Code**에서 구축한 작업 환경(Instruction 파일, Skills, Slash commands, Subagents, MCP 설정, Hooks, 세션 기록)을 **OpenAI Codex**로 클릭 한 번에 이주시키는 방법을 정리한 스킬입니다.

## 이게 뭔가요?

OpenAI **Codex**에 '다른 에이전트 설정 가져오기(Import other agent setup)' 기능이 추가되면서, 기존에 **Claude Code**에서 세팅해 둔 작업 환경(Instruction 파일, Skills, Slash commands, Subagents, MCP 설정, Hooks, 최근 세션)을 거의 그대로 옮겨올 수 있게 되었습니다. 컴퓨터에 저장된 전역 설정과 프로젝트별 설정을 모두 검사해서 Codex 형식으로 자동 변환해줍니다.

Codex는 단순히 Claude Code의 대체재가 아니라 아래와 같은 고유한 장점이 있습니다.

- 💰 유료 필요: 없음 — ChatGPT Plus, Pro, Business, Enterprise 사용자는 추가 결제 없이 바로 사용 가능 (무료 사용자도 넉넉한 사용량 제공)
- **백그라운드 클라우드 작업**: 30분~몇 시간 걸리는 무거운 작업도 클라우드에서 독립 실행되어, 노트북을 덮고 퇴근해도 작업이 계속 진행됨
- **병렬 실행**: 데스크톱 앱에서 여러 작업을 동시에 지시하고 한꺼번에 결과 확인 가능
- **모바일 지시**: 이동 중 스마트폰 ChatGPT 앱에 음성/텍스트로 "이 버그 좀 고쳐줘"라고 남기면 코드 수정 및 PR 생성까지 자동 완료 (가장 최근 업데이트)
- **AI 코드 리뷰어**: GitHub PR 병합 시 AI가 직접 리뷰 코멘트를 남겨줌
- **최신 모델 탑재**: GPT-5, GPT-5-Codex 추론 모델 그대로 활용
- **샌드박스 격리**: 위험한 명령어나 시스템 접근은 자동 차단되어 기본 보안이 강력함

## 따라하기

### 1. 이주 항목 매핑표 확인하기

먼저 Claude Code의 어떤 항목이 Codex의 무엇으로 옮겨지는지 아래 표로 확인합니다.

| Claude Code 기존 항목 | OpenAI Codex 이동 결과 | 쉬운 설명 |
|---|---|---|
| Instruction files (CLAUDE.md 등) | AGENTS.md | AI에게 미리 알려주는 '나만의 작업 규칙과 배경지식' |
| settings.json / config.toml | 기본 설정 파일 | 테마, 언어, 기본 동작 등 전반적인 환경 설정 |
| Skills | Codex skills | AI가 수행할 수 있는 구체적인 '개인기(기능)' |
| Slash commands | Codex skills | `/` 를 입력해 빠르게 실행하는 단축 명령어 |
| Subagents | Codex agents | 특정 업무만 전담해서 처리하는 '보조 AI 비서' |
| MCP server config | Codex MCP config | 외부 프로그램이나 데이터베이스와 연결해주는 설정 |
| Hooks | Codex hooks | 특정 상황이 되면 자동으로 실행되도록 걸어둔 '자동화 규칙' |
| 최근 30일 세션 | Threads / Projects | 최근 한 달 동안 AI와 대화하고 작업했던 모든 기록 |

### 2. 설정 열기

Codex 앱을 실행하고 좌측 하단의 **Settings(설정)** 메뉴로 들어갑니다.

### 3. 메뉴 찾기

**General(일반)** 페이지에서 **[Import other agent setup(다른 에이전트 설정 가져오기)]** 항목을 찾습니다.

### 4. 가져오기 실행

**Import** (또는 이미 한 번 실행한 적이 있다면 **Import again**) 버튼을 클릭합니다.

### 5. 항목 선택

앞서 확인한 8가지 항목(Instruction files, settings, Skills, Slash commands, Subagents, MCP config, Hooks, 최근 세션) 중 가져오고 싶은 것만 체크한 뒤 실행합니다.

### 6. 결과 확인

마이그레이션이 완료되면 **[View imported files]**를 눌러 내 설정이 잘 들어왔는지 확인합니다.

> 💡 꿀팁: 자동 변환이 어려운 일부 복잡한 설정은 앱이 알려주며, **'Continue in Codex'** 버튼을 누르면 AI가 대화를 통해 나머지 변환을 직접 도와줍니다.

### 7. 이주 후 필수 점검 체크리스트

자동 이주가 끝나면 아래 항목들이 의도대로 작동하는지 반드시 확인합니다.

- AI 비서(에이전트)와 스킬들이 파일에 접근하거나 수정할 수 있는 권한 및 제한 범위 확인
- 외부 도구와 연결(MCP 서버)할 때 필요한 비밀번호(인증), 환경변수 등의 보안 설정이 풀리지 않았는지 체크
- 특정 조건에서 자동 실행되는 규칙(Hook)이 Codex 환경에서도 똑같이 작동하는지 테스트
- 클로드 전용으로 설치했던 플러그인이나 마켓플레이스 항목 중 따로 다시 설치해야 할 것이 있는지 확인
- 프롬프트(명령어) 안에 파일 경로나 변수를 빈칸으로 비워둔 템플릿이 정상적으로 텍스트를 불러오는지 확인
- 슬래시(`/`)를 활용한 단축 명령어가 기존과 동일하게 입력되고 작동하는지 점검

## 활용 예시

- Claude Code에서 몇 달간 쌓아온 `CLAUDE.md` 규칙 파일과 커스텀 Slash commands가 있는 경우 → Import 실행 → `AGENTS.md`와 Codex skills로 자동 변환되어 새 도구에서도 동일한 작업 규칙을 즉시 사용
- 여러 개의 Subagent(코드 리뷰용, 문서 작성용 등)를 운영 중이던 경우 → Import 시 Subagents 항목 체크 → Codex agents로 옮겨져 역할 분담 구조를 그대로 유지
- Slack, Notion 등과 연결한 MCP 서버 설정이 있는 경우 → Import 후 반드시 인증/환경변수가 노출되지 않았는지 재확인 → 문제 없으면 외부 도구 연동을 Codex에서도 이어서 사용

## 💡 아이디어

- 이주가 5분 이내로 끝나므로, 굳이 하나만 택하지 않고 Claude Code와 Codex를 병행 사용하며 동일 작업(속도·정확도·MCP 안정성·과거 기록 검색 편의성)을 비교해보고 자신의 업무 스타일에 더 맞는 쪽으로 정착하는 방식을 추천

## 주의사항

- MCP 서버 관련 인증 정보나 환경변수는 이주 과정에서 보안 설정이 풀릴 수 있으므로 반드시 재확인 필요
- Hooks(자동 실행 규칙)는 Codex 환경에서 동일하게 작동하지 않을 수 있어 별도 테스트 필수
- Claude 전용 플러그인/마켓플레이스 항목은 자동 이주 대상이 아니므로 필요 시 Codex에서 별도 설치 필요

## 출처

[Claude Code → Codex 이주 가이드](https://abounding-helmet-0e4.notion.site/Claude-Code-Codex-35873c7b15ad81fa95a4d608d35164a3?pvs=149)

## 출처

- [https://abounding-helmet-0e4.notion.site/Claude-Code-Codex-35873c7b15ad81fa95a4d608d35164a3?pvs=149](https://abounding-helmet-0e4.notion.site/Claude-Code-Codex-35873c7b15ad81fa95a4d608d35164a3?pvs=149)
