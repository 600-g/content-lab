---
name: fable-5-advanced-prompting-mastery
description: 이 스킬은 **Fable 5**의 자율 에이전트 능력을 활용하여, 복잡한 **다단계 워크플로우**를 최소한의 지시로 완성하는 고급 프롬프팅 기법입니다.
origin: content-lab
grade: S
difficulty: 고급
category: 자동화
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://adu-fable5-guide.vercel.app/?fbclid=PAVERFWASzfBJwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp3tDUQ7j-FWlcUGsIsYM7o9Z-hSYSY4JZEFSmEYEgkmd6ZEwc5It6NkxeseS_aem_5ZRvt5sOrFXdAe75h5l0VQ
---

# Fable 5로 복합 작업 흐름을 자율 설계

💡 이 스킬은 **Fable 5**의 자율 에이전트 능력을 활용하여, 복잡한 **다단계 워크플로우**를 최소한의 지시로 완성하는 고급 프롬프팅 기법입니다.

## 이게 뭔가요?
Fable 5는 이전 모델 대비 **며칠(multi-day) 단위의 자율 실행**이 가능하며, 단순한 질의응답을 넘어 복잡한 프로젝트 전체를 맡길 수 있는 수준에 도달했습니다. 이는 마치 시급이 비싼 수석 엔지니어를 기간 한정으로 빌려 쓰는 것과 같습니다. 이 모델의 핵심은 '어떻게'가 아니라 '무엇을'에 초점을 맞추어, **목표와 이유(Goal & Why)**를 명확히 제시하는 것입니다.

이 가이드는 Anthropic의 공식 가이드라인, 실사용자들의 검증 팁, 그리고 실제 테스트를 통해 도출된 **'카더라'를 걷어낸'** Fable 5 활용 설명서입니다. 특히, 이전 모델들이 단계별 지시문(Prescriptive Steps)을 요구했던 것과 달리, Fable 5는 **'파이프라인 설명 + 좋은 산출물의 모습'**만 주면 전체 전환을 스스로 처리하는 것이 가장 큰 차별점입니다.

💰 유료 필요: Claude Max (최신 기능 및 성능 활용 시)
✅ 무료 대안: Gemini 또는 GPT-4o로 유사한 복합 추론은 가능하나, 자율 루프의 신뢰도와 깊이에서 차이가 있을 수 있습니다.

## 따라하기
Fable 5의 능력을 극대화하기 위한 핵심 원칙과 고급 패턴을 단계별로 학습합니다.

### 1. 핵심 원칙 이해 및 적용
- **가장 어려운 미해결 문제에 투입**: 쉬운 작업만 시키면 모델의 잠재력을 저평가하게 됩니다. 가장 난이도가 높은 문제에 투입하는 것이 중요합니다.
- **지시의 간결화**: 이전 모델처럼 세부적인 단계별 지시(Prescriptive Steps)를 나열하는 것은 오히려 성능을 저하시킬 수 있습니다. 대신, **전체적인 목표와 이유**를 제시해야 합니다.
- **결과 중심의 사고**: 첫 문장부터 **'무슨 일이 일어났는지(what happened)'** 또는 **'무엇을 발견했는지(what did you find)'**로 시작하여, 독자가 다음 행동을 취하도록 유도해야 합니다.
- **검증 및 투명성 확보**: 모든 주장은 반드시 **'이번 세션의 도구 결과'**를 근거로 제시해야 하며, 검증되지 않은 내용은 명시적으로 '미확인'이라고 밝혀야 합니다.

### 2. 고급 프롬프트 패턴 적용
**A. 목표 기반 구조화 (G.O.A.L 프레임워크)**
복잡한 인터뷰나 요구사항 정의 시, 이 프레임워크를 활용하여 인터뷰 자체를 구조화할 수 있습니다.
*   **G**round: 기존 자산(기존 문서, 데이터)을 먼저 읽게 합니다.
*   **O**utcome: 최종적으로 도달해야 할 **완료의 모습**을 명확히 정의합니다.
*   **A**utonomy: 방법론이나 과정은 모델에게 맡깁니다.
*   **L**oop in proof: 결과에 대한 **증명(Proof)**을 요구합니다.

**B. 역할 기반 시나리오 구축 (페르소나 심사)**
다양한 관점을 요구할 때, 여러 페르소나를 지정하고 그들 간의 **상호 반박**을 유도하는 것이 효과적입니다. (예: 상업성 에디터 vs. 문장력 에디터)

**C. 자율 루프 및 에이전트 시뮬레이션**
단순한 결과물 생성을 넘어, **반복적인 프로세스**를 설계합니다. 예를 들어, 매일 아침 데이터를 수집 → 변화 상위 3개 추려 브리핑 → 원본과 대조 검증 → 결론 도출까지의 루틴을 정의하고, **종료 기준**까지 명시해야 합니다. (예: 3개 항목 검증 완료 시 종료)

### 3. 필수 명령어 및 구조화
*   **명령어 선택**: 모델에게 특정 역할을 부여할 때는 명시적으로 모델을 선택하는 것이 좋습니다. (예: `/model fable`)
*   **구조적 출력 요구**: 단순 텍스트 대신, **HTML 파일 계획/스펙** 형태로 출력을 요구하면, 인간이 다시 읽을 때 목업(Mockup)까지 보이게 되어 품질이 높아집니다.
*   **코드/구조물 보존**: 코드 블록이나 JSON 구조는 **절대 요약하거나 축소하지 않고** 원본 그대로 유지해야 합니다. (이것이 DB의 핵심 자산입니다.)

## 활용 예시

**시나리오 1: 콘텐츠 소재 고갈 방지 시스템 구축 (실전 사례)**
*   **입력**:

## 출처

- [https://adu-fable5-guide.vercel.app/?fbclid=PAVERFWASzfBJwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp3tDUQ7j-FWlcUGsIsYM7o9Z-hSYSY4JZEFSmEYEgkmd6ZEwc5It6NkxeseS_aem_5ZRvt5sOrFXdAe75h5l0VQ](https://adu-fable5-guide.vercel.app/?fbclid=PAVERFWASzfBJwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp3tDUQ7j-FWlcUGsIsYM7o9Z-hSYSY4JZEFSmEYEgkmd6ZEwc5It6NkxeseS_aem_5ZRvt5sOrFXdAe75h5l0VQ)
