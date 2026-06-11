---
name: contextual-prompt-engineering
description: AI에게 '넌 전문가야' 대신 '나는 이런 상황이고, 이 독자를 위해, 이런 제약 안에서 답변해줘'라고 구체적인 맥락을 제공하여 답변 품질을 극대화한다. Use when: - 일반적이고 추상적인 AI 답변에 불만족할 때 - 특정 상황, 대상, 제약을 고려한 현실적인 AI 조언이 필요할 때 - AI의 잠재력을 최대한 활용하여 고품질의 결과물을 얻고 싶을 때
origin: content-lab
grade: A
difficulty: 중급
category: 기타
ai_tools: []
sources:
  - (unknown)
---

# 맥락 기반 프롬프트 엔지니어링 (상황, 독자, 제약 활용)

AI에게 '넌 전문가야' 대신 '나는 이런 상황이고, 이 독자를 위해, 이런 제약 안에서 답변해줘'라고 구체적인 맥락을 제공하여 답변 품질을 극대화한다. Use when: - 일반적이고 추상적인 AI 답변에 불만족할 때 - 특정 상황, 대상, 제약을 고려한 현실적인 AI 조언이 필요할 때 - AI의 잠재력을 최대한 활용하여 고품질의 결과물을 얻고 싶을 때

AI에게 '넌 전문가야' 대신 '나는 이런 상황이고, 이 독자를 위해, 이런 제약 안에서 답변해줘'라고 구체적인 맥락을 제공하여 답변 품질을 극대화한다. Use when: - 일반적이고 추상적인 AI 답변에 불만족할 때 - 특정 상황, 대상, 제약을 고려한 현실적인 AI 조언이 필요할 때 - AI의 잠재력을 최대한 활용하여 고품질의 결과물을 얻고 싶을 때

AI에게 '넌 전문가야' 대신 '나는 이런 상황이고, 이 독자를 위해, 이런 제약 안에서 답변해줘'라고 구체적인 맥락을 제공하여 답변 품질을 극대화한다. Use when: - 일반적이고 추상적인 AI 답변에 불만족할 때 - 특정 상황, 대상, 제약을 고려한 현실적인 AI 조언이 필요할 때 - AI의 잠재력을 최대한 활용하여 고품질의 결과물을 얻고 싶을 때

> **💡 AI에게 '넌 전문가야' 대신 '나는 이런 상황이고, 이 독자를 위해, 이런 제약 안에서 답변해줘'라고 구체적인 맥락을 제공하여 답변 품질을 극대화한다.**
>
> 🤖 Claude · GPT · Gemini · Ollama · 도구무관 → 🎯 공통

## 언제 쓰나

- 일반적이고 추상적인 AI 답변에 불만족할 때
- 특정 상황, 대상, 제약을 고려한 현실적인 AI 조언이 필요할 때
- AI의 잠재력을 최대한 활용하여 고품질의 결과물을 얻고 싶을 때

## 원리

AI는 이미 방대한 지식을 학습하고 있지만, 그 지식을 어떤 맥락에서, 어떤 수준으로, 어떤 형식으로 답변해야 할지 모르면 범용적인 결과를 내놓는다. 이 스킬은 AI에게 사용자의 현재 상황(Context), 답변을 받을 대상(Audience), 그리고 불가능하거나 필요한 조건(Constraint)을 명확히 알려줌으로써, AI가 자신의 지식을 사용자의 특정 요구에 맞춰 최적화된 형태로 제공하도록 유도한다. 핵심은 역할(Role) 지정보다 맥락(Context) 지정이 답변 품질에 10배 더 큰 영향을 미친다는 원리이다.

## 단계

- 1) **상황(Context) 지정:** 내가 처한 구체적인 상황, 현재 상태, 목표, 불가능한 조건 등을 명확히 설명한다.
- 2) **독자(Audience) 명시:** 답변을 받아볼 대상(독자)이 누구인지, 그들의 특징, 배경, 관련 경험 수준 등을 알려준다.
- 3) **제약 조건(Constraint) 추가:** 예산, 시간, 인원, 도구, 경험 등 현실적인 한계나 조건을 먼저 제시하여 AI가 실행 가능한 답변을 하도록 유도한다.

## 예시

{'약한 프롬프트': '```json\n{\n  "input": "넌 마케팅 전문가야. 인스타 마케팅 방법 알려줘."\n}\n```', '강한 프롬프트': '```json\n{\n  "input": "나는 월 예산 50만원의 로컬 카페 사장이야. 인스타 팔로워 200명. 이전에 일반 음식 사진만 올렸고 효과가 없었어. 지금 당장 할 수 있는 무료 전략 3가지를 각각 구체적인 행동 단계로 알려줘."\n}\n```'}

## 두근컴퍼니 적용

- Claude Max, Gemini 등 모든 AI 도구 사용 시 프롬프트에 구체적인 상황, 독자, 제약 조건을 포함하여 고품질 답변 유도.
- company-hq 내 AI 에이전트의 프롬프트 작성 시, 사용자 의도와 상황을 명확히 반영하도록 스킬 적용.
- 두근펫, 매매봇, 검은별, 첼시인스타 등 프로젝트별 AI 활용 시, 해당 프로젝트의 특성과 제약을 프롬프트에 명시하여 최적화된 결과 도출.

## ️ 주의

- 단순히 '넌 전문가야'와 같은 역할 지정 프롬프트는 AI의 지식을 변화시키지 못하며, 범용적이고 비현실적인 답변을 초래할 수 있다.
- 맥락 정보가 부족하면 AI는 이상적인 조건을 가정하여 현실과 동떨어진 답변을 줄 수 있다.

## 출처

- [https://drive.google.com/file/d/1VyKG8kkBxKlnroB3sXFhEQB9deLApp_l/view?fbclid=PAVERFWARzvMlleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAac9ReryTj2M2HecWc75nuN_1QNHYVheaZ7NCDQG1DaCdbZawL3NQf2QoIPCVw_aem_PZS53-BUbxksGQHRXQziBw](https://drive.google.com/file/d/1VyKG8kkBxKlnroB3sXFhEQB9deLApp_l/view?fbclid=PAVERFWARzvMlleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAac9ReryTj2M2HecWc75nuN_1QNHYVheaZ7NCDQG1DaCdbZawL3NQf2QoIPCVw_aem_PZS53-BUbxksGQHRXQziBw)

---

<details>
<summary>📋 메타 정보</summary>

- 최초 수집: `2026-05-15` · 마지막 갱신: `2026-05-15` · 합병: 1회
- 템플릿: v2.2 · slug: `contextual-prompt-engineering`
- 자동 생성: 두근컴퍼니 콘텐츠랩

</details>
