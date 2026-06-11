---
name: dynamic-workflows
description: Claude 코드를 활용하여 **대규모 작업을 자동화**하고 **병렬 분산 및 교차 검증**하는 스킬입니다.
origin: content-lab
grade: A
difficulty: 중급
category: 자동화
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://abounding-helmet-0e4.notion.site/Dynamic-Workflows-37573c7b15ad816288b6f6a8a2788049?pvs=149
---

# 다이내믹 워크플로우 자동화

💡 Claude 코드를 활용하여 **대규모 작업을 자동화**하고 **병렬 분산 및 교차 검증**하는 스킬입니다.

## 이게 뭔가요?

다이내믹 워크플로우는 Claude가 즉석에서 JavaScript 스크립트를 작성하고, 이를 백그라운드 런타임에서 실행하여 대규모 작업을 오케스트레이션하는 기능입니다. 워크플로우는 '넓이(병렬 분산)'를 위한 도구로, 반복적인 깊이 있는 작업에서 수십~수백 개의 에이전트를 동시에 투입하여 교차 검증하는 데 최적화되어 있습니다.

작동 방식은 런타임이 스크립트를 격리 실행하며, 중간 결과는 대화 컨텍스트가 아닌 스크립트 변수에 저장됩니다. 이를 통해 Adversarial 에이전트들이 서로 결과를 검토하여 논리적 결함을 걸러내고 최종 결과물만 세션으로 반환합니다.

Claude Code v2.1.154 이상에서 사용 가능하며, Max · Team 플랜에서는 자동 활성화됩니다. Pro 및 Enterprise 플랜에서는 별도 설정을 통해 활성화해야 합니다. 

💰 유료 필요: Claude Code v2.1.154 이상 (Max, Team 플랜 외에는 별도 설정 필요)
✅ 무료 대안: 해당 기능은 Claude Code의 특정 버전 및 플랜에 종속적이므로 직접적인 무료 대안은 없습니다.

## 따라하기

**1. 환경 설정 및 활성화**

*   **전제 조건**: Claude Code v2.1.154 이상 (research preview)
*   **활성화**: 
    *   **Max · Team**: 자동 ON, 별도 설정 불필요
    *   **Pro · Enterprise**: 기본 OFF. `/config`에서 'Dynamic workflows' 토글을 켜거나, `settings.json`에 `"disableWorkflows": true`를 추가하거나, 환경 변수 `CLAUDE_CODE_DISABLE_WORKFLOWS=1` 설정을 제거해야 합니다.

**2. 워크플로우 실행**

*   **자연어 호출**: "run a workflow to..." 형식으로 입력합니다.
*   **자동 트리거**: `/effort ultracode` 와 같이 특정 명령어를 입력하여 전역 적용할 수 있습니다.
*   **번들 기능**: `/deep-research <질문>` 과 같이 특정 명령어를 사용하여 시작할 수 있습니다.

**3. 워크플로우 제어 및 관리**

*   **핵심 명령어**: `/workflows` 명령어를 사용하여 실행 목록을 확인하고, 일시정지(`p`), 중지(`x`), 저장(`s`) 등의 제어가 가능합니다.
*   **추론 강도 설정**: `/effort` 명령어로 추론 강도 및 워크플로우 모드를 설정할 수 있습니다.

**4. 워크플로우 저장 및 재사용 (스킬처럼)**

*   `/workflows` 메뉴에서 `s` 키를 눌러 현재 워크플로우를 저장합니다.
*   저장된 워크플로우는 `/이름` 슬래시 커맨드로 호출할 수 있으며, 인자 전달도 가능합니다. (예: `/triage 1024, 1025, 1030`)

**5. 워크플로우 비활성화**

*   `/config`에서 'Dynamic workflows' 토글을 OFF 합니다.
*   `settings.json` 파일에 `"disableWorkflows": true` 를 추가합니다.
*   환경 변수 `CLAUDE_CODE_DISABLE_WORKFLOWS=1` 를 설정합니다.

## 활용 예시

*   **콘텐츠 감사**: 20개 이상의 캐러셀 디자인 시스템 일관성을 일괄 점검합니다.
*   **시장 분석**: 19개 해외 유튜브 채널 트렌드를 분석하고 한글화 후보 점수를 산정합니다.
*   **데이터 검증**: 70개 이상의 가이드 문서 간 상충되는 내용을 일괄 탐지합니다.
*   **광고주 매칭**: 광고주 가이드라인과 자산을 1:1로 대조하여 자동 리포트를 생성합니다.

## 주의사항

*   **런타임 제한**: 동시 최대 16 에이전트, Run당 최대 1,000 에이전트까지 가능합니다.
*   **비용**: 일반 세션보다 토큰 소모가 큽니다. 큰 작업 전 작은 단위로 테스트하고, 단계별로 모델을 다르게 라우팅하는 전략이 필요합니다.
*   **중단**: `/workflows`에서 에이전트별 토큰을 확인하고 언제든지 중지가 가능합니다.
*   **권한 모드**: 'Default' 모드에서 'Yes, and don’t ask again'을 선택하면 해당 워크플로우는 승인 단계 없이 자동 실행됩니다. 'Auto' 모드, `ultracode`가 켜져 있거나 `Bypass permissions / claude -p / Agent SDK` 사용 시에는 권한 확인 없이 자동 실행됩니다.

## 출처

[클로드코드 Dynamic Workflows 완벽 가이드](https://abounding-helmet-0e4.notion.site/Dynamic-Workflows-37573c7b15ad816288b6f6a8a2788049?pvs=149)

## 출처

- [https://abounding-helmet-0e4.notion.site/Dynamic-Workflows-37573c7b15ad816288b6f6a8a2788049?pvs=149](https://abounding-helmet-0e4.notion.site/Dynamic-Workflows-37573c7b15ad816288b6f6a8a2788049?pvs=149)
