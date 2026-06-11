---
name: claude-opus-4-8-features
description: Claude Opus 4.8은 **코딩, 추론, 컴퓨터 조작, 지식 업무** 등 전반적인 성능을 개선하고, **Dynamic Workflows, Ultracode, /deep-research** 등의 새로운 Claude Code 기능을 도입한 **AI 모델**입니다.
origin: content-lab
grade: A
difficulty: 중급
category: 업무
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://resonant-frog-df5.notion.site/Claude-Opus-4-8-3783a1a3234380f0b5b4e646e6f65ec9?pvs=149
---

# Claude Opus 4.8 성능 및 기능 업데이트

💡 Claude Opus 4.8은 **코딩, 추론, 컴퓨터 조작, 지식 업무** 등 전반적인 성능을 개선하고, **Dynamic Workflows, Ultracode, /deep-research** 등의 새로운 Claude Code 기능을 도입한 **AI 모델**입니다.

## 이게 뭔가요?
Claude Opus 4.8은 이전 모델인 Opus 4.7을 기반으로 성능과 기능이 개선된 최신 AI 모델입니다. Anthropic은 Opus 4.8이 이전 모델보다 완만하지만 체감할 수 있는 개선을 이루었다고 설명하며, 특히 코딩, 추론, 컴퓨터 조작, 지식 업무 평가 점수 향상에 중점을 두었습니다. 또한, Claude Code와 같은 제품 기능에서도 Dynamic Workflows, Ultracode, /deep-research와 같은 새로운 기능들이 추가되었습니다.

이 스킬은 Claude Opus 4.8 모델의 전반적인 성능 향상과 Claude Code 제품의 새로운 기능들을 소개하고, 각각의 기능이 어떻게 작동하며 어떤 이점을 제공하는지 상세히 설명합니다. 일반 Claude 웹 사용자, Claude Code 사용자, API 개발자 등 사용자 유형별로 체감할 수 있는 변화도 함께 다룹니다.

💰 **유료 필요**: Claude Opus 4.8 모델 및 Claude Code의 고급 기능 사용을 위해서는 유료 요금제 구독 또는 API 사용이 필요합니다.
✅ **무료 대안**: Opus 4.8의 기본적인 성능 향상은 무료 버전에서도 일부 체감될 수 있으나, Dynamic Workflows와 같은 신규 Claude Code 기능은 유료 사용자에게 제공됩니다.

## 따라하기
### 1. Opus 4.8 성능 향상 확인
Opus 4.8은 다양한 평가 항목에서 Opus 4.7 대비 점수가 향상되었습니다. 주요 평가 항목별 성능 변화는 다음과 같습니다:

*   **SWE-Bench Pro (코드 작성)**: 64.3% → 69.2% (+4.9%p)
*   **Terminal-Bench 2.1 (터미널 작업)**: 66.1% → 74.6% (+8.5%p)
*   **Humanity’s Last Exam (추론)**: 46.9% → 49.8% (+2.9%p)
*   **OSWorld-Verified (컴퓨터 조작)**: 82.3% → 83.4% (+1.1%p)
*   **GDPval-AA (지식 업무)**: 1,753 → 1,890 (+137)
*   **Finance Agent v2 (금융 분석)**: 51.5% → 53.9% (+2.4%p)

**참고**: Terminal-Bench 2.1 점수에서는 GPT-5.5가 Opus 4.8보다 높은 점수를 기록했으며, 모든 벤치마크에서 GPT-5.5를 앞섰다고 설명하는 것은 정확하지 않습니다.

### 2. 답변 신뢰성 및 코드 검토 능력 개선
Opus 4.8은 다음과 같은 정직성 측면에서 개선되었습니다:

*   자신의 작업에서 불확실한 부분을 더 자주 표시
*   충분한 근거가 없는 주장을 할 가능성 감소
*   자신이 작성한 코드의 결함을 발견하고도 말하지 않고 넘어갈 가능성 감소 (Opus 4.7 대비 약 4배 낮음)

### 3. 장시간 작업 및 도구 사용 개선
*   장시간 진행되는 에이전트 코딩 안정성 향상
*   긴 대화와 긴 작업 맥락 처리 능력 개선
*   작업 중 컨텍스트 압축 후 원래 작업을 이어가는 능력 향상
*   작업에 필요한 도구 호출을 건너뛰는 경우 감소

### 4. Effort Control 기능 활용 (Claude 웹/Cowork)
Claude 웹과 Cowork에서 모델 선택 화면에 Effort를 조절하는 기능이 새로 추가되었습니다. Effort는 Claude가 작업에 사용하는 추론 자원을 조절하는 기능으로, 낮으면 빠른 응답과 적은 사용량을, 높으면 깊은 추론과 많은 토큰 사용을 의미합니다.

*   **낮은 Effort**: 빠르게 응답하고 사용량을 적게 소비
*   **높은 Effort**: 더 깊게 추론하고 더 많은 토큰을 사용

환경에 따라 **low, medium, high, extra (xhigh), max** 단계를 사용할 수 있습니다.

### 5. Claude Code의 Dynamic Workflows 활용
Dynamic Workflows는 하나의 큰 작업을 여러 개의 작은 작업으로 나누고, 여러 서브에이전트에게 분배한 뒤 결과를 검증하고 통합하는 기능입니다.

**실행 과정 예시 (프로젝트 보안 문제 찾기)**:
1.  전체 작업을 여러 보안 영역으로 분리
2.  각 영역 담당 서브에이전트 실행
3.  발견된 문제 별도 에이전트가 검토
4.  검증된 결과만 정리
5.  하나의 최종 보고서로 통합

**활용 사례**: 프로젝트 전체 버그 검사, 대규모 보안 감사, 수백 개 파일 마이그레이션, 프레임워크/API 교체, 여러 출처 교차 검증 조사 등

**스크립트 기반 제어**: Dynamic Workflow에서는 Claude가 작업에 맞는 JavaScript 스크립트를 생성하고, 이 스크립트가 에이전트 실행 순서, 병렬 처리, 반복 작업, 조건 분기 등을 관리합니다.

**제한**: 동시에 실행 가능한 에이전트 최대 16개, 한 번의 Workflow에서 생성 가능한 총 에이전트 최대 1,000개

**이용 가능 환경**: Claude Code 2.1.154 이상, Claude 유료 요금제, Anthropic API, Amazon Bedrock, Google Cloud Vertex AI, Microsoft Foundry

### 6. Claude Code의 Ultracode 설정
Ultracode는 Claude Code의 실행 설정으로, 모델의 Effort를 `xhigh`로 설정하고 중요한 작업에서 Dynamic Workflow를 자동으로 구성합니다.

*   **설정 방법**: `/effort ultracode` 명령 사용
*   **작동 방식**: Ultracode 활성화 시 Claude가 중요한 작업마다 Dynamic Workflow 필요 여부를 판단하여 실행합니다. 하나의 요청도 프로젝트 구조 분석, 코드 수정, 결과 검증 등으로 나눌 수 있습니다.
*   **주의**: Ultracode는 현재 Claude Code 세션에만 적용되며, 일반적인 낮은 Effort 설정보다 더 많은 토큰을 사용하고 작업 시간이 길어질 수 있습니다.

### 7. Claude Code의 /deep-research 기능 사용
`/deep-research`는 Dynamic Workflows 기반의 내장 기능으로, 질문을 여러 검색 방향으로 분리하여 병렬 검색, 출처 수집, 교차 검증, 인용 보고서 작성을 수행합니다.

*   **실행 방법**: `/deep-research 조사할 질문`
*   **요구사항**: WebSearch 도구 사용 가능해야 함

**참고**: `/deep-research`는 Opus 4.8 모델 자체의 기능이 아니라 Claude Code의 신규 내장 Workflow입니다.

### 8. API 대화 중 System 메시지 변경 (API 개발자 대상)
Opus 4.8의 Messages API는 대화의 `messages` 배열 중간에 `system` 역할의 메시지를 삽입할 수 있습니다. 이를 통해 에이전트가 긴 작업을 수행하는 도중 전체 프롬프트 재전송 없이 지침을 변경할 수 있습니다.

*   **이점**: Prompt Cache 유지, 반복 에이전트 작업 입력 비용 절감

### 9. Fast Mode 활용 및 가격 변화
Fast Mode는 Opus 모델을 더 빠른 출력 속도로 사용하는 기능입니다. Opus 4.8 Fast Mode는 최대 2.5배 빠른 초당 출력 토큰 속도를 제공하며, Opus 4.7 Fast Mode 가격의 3분의 1로 인하되었습니다.

*   **Opus 4.8 Fast Mode 가격**: 입력 100만 토큰당 10달러, 출력 100만 토큰당 50달러
*   **참고**: 일반 Opus 4.8 모드 대비 토큰 단가는 두 배입니다.

## 활용 예시
### 1. 대규모 코드베이스 보안 감사 (Claude Code)
**시나리오**: 수백 개의 파일로 구성된 프로젝트의 모든 잠재적 보안 취약점을 자동으로 검사하고 보고서를 생성하고 싶습니다.

**방법**: Claude Code에서 `/effort ultracode`를 설정하고, `/deep-research: 프로젝트 전체의 보안 취약점을 감사해줘.` 와 같이 프롬프트합니다. Dynamic Workflows와 `/deep-research` 기능이 자동으로 활성화되어 여러 에이전트가 병렬로 코드 분석, 취약점 탐지, 관련 정보 검색 및 교차 검증을 수행한 후 최종 보고서를 생성합니다.

### 2. 복잡한 금융 보고서 작성 (Claude 웹/API)
**시나리오**: 여러 금융 데이터를 분석하고 복잡한 보고서를 작성해야 하며, 응답 속도와 추론 깊이 사이의 균형을 맞추고 싶습니다.

**방법**: Claude 웹 인터페이스에서 Opus 4.8 모델을 선택하고, Effort Control 슬라이더를 'high' 또는 'extra'로 조절하여 깊이 있는 분석을 수행하도록 합니다. API 사용 시에는 Effort 설정을 조절하거나, 덜 중요한 작업에는 Fast Mode를 사용하여 비용 효율성을 높일 수 있습니다.

### 3. API 연동 중 실시간 지침 변경 (API 개발자)
**시나리오**: 사용자의 입력에 따라 AI 에이전트의 작동 방식을 동적으로 변경해야 하는 서비스를 개발 중입니다.

**방법**: Opus 4.8의 Messages API를 사용하여 대화 중간에 `system` 역할의 메시지를 삽입합니다. 예를 들어, 사용자가 특정 기능을 요청하면 `system` 메시지를 통해 해당 기능 실행에 필요한 지침이나 제약 조건(예: 토큰 예산, 실행 환경 정보)을 실시간으로 업데이트할 수 있습니다.

## 💡 아이디어
### 1. 개인 맞춤형 코딩 도우미 개발
Opus 4.8의 향상된 코딩 능력과 Claude Code의 Dynamic Workflows를 결합하여, 사용자의 코딩 스타일, 자주 사용하는 라이브러리, 프로젝트 구조 등을 학습하여 맞춤형 코드 제안, 리팩토링, 버그 수정 자동화를 제공하는 개인화된 코딩 도우미를 개발할 수 있습니다. Ultracode 설정은 대규모 리팩토링이나 복잡한 기능 구현 시 자동화 수준을 높이는 데 활용될 수 있습니다.

### 2. 실시간 시장 분석 및 보고서 자동 생성 서비스
`/deep-research` 기능과 Opus 4.8의 금융 분석 능력을 결합하여, 특정 금융 상품이나 시장 동향에 대한 실시간 데이터를 수집하고, 여러 출처를 교차 검증하여 심층 분석 보고서를 자동으로 생성하는 서비스를 구축할 수 있습니다. Dynamic Workflows를 통해 데이터 수집, 분석, 보고서 작성 단계를 분산하여 효율성을 극대화할 수 있습니다.

## 주의사항
### 1. Dynamic Workflows 및 Ultracode의 토큰 사용량
Dynamic Workflows와 Ultracode는 여러 에이전트를 실행하므로 일반적인 Claude Code 대화보다 **의미 있게 많은 토큰을 사용할 수 있습니다.** Anthropic은 평균 사용량 증가 배수를 공개하지 않았으므로, 비용 예측 시 주의가 필요합니다. `/workflows` 화면에서 각 에이전트의 토큰 사용량을 확인하여 비용을 관리할 수 있습니다.

### 2. Fast Mode의 토큰 가격
Fast Mode는 출력 속도를 높이지만, **일반 모드보다 토큰 단가가 두 배입니다.** 빠른 응답이 필수적인 경우에만 사용하는 것이 비용 효율적입니다.

### 3. GPT-5.5와의 벤치마크 비교
Opus 4.8이 모든 벤치마크에서 GPT-5.5를 앞섰다고 주장하는 것은 **정확하지 않습니다.** Terminal-Bench 2.1 등 일부 항목에서는 GPT-5.5가 더 높은 점수를 기록했습니다. 벤치마크 결과 해석 시 신중해야 합니다.

### 4. 새로운 토크나이저 관련 토큰 사용량
Opus 4.7부터 사용된 새로운 토크나이저는 이전 모델 대비 같은 텍스트에 대해 최대 35% 더 많은 토큰을 사용할 수 있습니다. Opus 4.8도 이 토크나이저를 사용하므로, Opus 4.7 이전 모델과 비교 시 토큰 사용량 증가가 있을 수 있습니다. Opus 4.8과 Opus 4.7 간의 토큰 사용량 차이는 이 토크나이저 자체의 영향보다는 Effort 설정 등 다른 요인에 더 영향을 받습니다.

## 출처
[Claude Opus 4.8, 무엇이 달라졌을까?](https://resonant-frog-df5.notion.site/Claude-Opus-4-8-3783a1a3234380f0b5b4e646e6f65ec9?pvs=149)

## 출처

- [https://resonant-frog-df5.notion.site/Claude-Opus-4-8-3783a1a3234380f0b5b4e646e6f65ec9?pvs=149](https://resonant-frog-df5.notion.site/Claude-Opus-4-8-3783a1a3234380f0b5b4e646e6f65ec9?pvs=149)
