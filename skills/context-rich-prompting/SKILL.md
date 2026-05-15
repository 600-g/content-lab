---
name: context-rich-prompting
description: AI에게 일반적인 역할을 부여하기보다, 구체적인 상황과 맥락을 제공하여 답변 품질을 즉시 향상시키는 프롬프트 작성 원리입니다. Use when: - AI의 답변이 너무 일반적이거나 기대에 못 미칠 때 - 특정 상황에 맞춰진 구체적이고 실용적인 답변이 필요할 때 - AI 활용의 효율성을 극대화하고 싶을 때
origin: content-lab
metadata:
  template_version: "v2.2"
  category: "프롬프트"
  grade: "S"
  difficulty: "초급"
  targets: ["공통"]
  ai_tools: ["Claude", "GPT", "Gemini", "Ollama", "Claude Code", "도구무관"]
  tags: ["MCP", "프롬프트체이닝", "CoT"]
  source_urls:
    - "https://drive.google.com/file/d/1VyKG8kkBxKlnroB3sXFhEQB9deLApp_l/view"
  source_type: "web"
  collected_at: "2026-05-15"
  last_updated_at: "2026-05-15"
  merge_count: 1
---

# 💬 역할 대신 맥락을 제공하는 프롬프트

> **💡 AI에게 일반적인 역할을 부여하기보다, 구체적인 상황과 맥락을 제공하여 답변 품질을 즉시 향상시키는 프롬프트 작성 원리입니다.**
>
> **S** · 프롬프트 · 초급
> 🤖 Claude · GPT · Gemini · Ollama · Claude Code · 도구무관 → 🎯 공통

## 🎯 언제 쓰나

- AI의 답변이 너무 일반적이거나 기대에 못 미칠 때
- 특정 상황에 맞춰진 구체적이고 실용적인 답변이 필요할 때
- AI 활용의 효율성을 극대화하고 싶을 때

## 🔑 원리

AI는 방대한 데이터로 이미 학습되어 있어 역할 지정이 지식 수준을 바꾸지 못합니다. 대신, '상황(Context)', '목적(Goal)', '독자(Audience)', '형식(Format)', '제약(Constraint)'의 5가지 구성 요소를 프롬프트에 구체적으로 명시함으로써 AI가 답변의 맥락, 수준, 방향을 정확히 파악하여 최적화된 결과물을 생성하도록 유도합니다. 역할보다 맥락이 10배 강하다는 핵심 법칙에 기반합니다.

## 🛠 단계

1) AI에게 '넌 전문가야' 대신 '나는 지금 이런 상황이야'라고 구체적으로 설명한다.
2) 다음 템플릿을 사용하여 현재 상황, 목표, 제약, 독자를 명시한다.
```
나는 [직업/역할]이야.
현재 상황: [구체적인 현재 상태]
목표: [원하는 결과]
제약: [불가능한 것 / 조건]
위 상황에서 [질문]을 도와줘.
이 조건에 맞지 않는 답변은 필요 없어.
```
3) 독자(Audience)를 명시하여 AI가 언어 수준, 비유, 전제 지식, 톤을 조정하도록 유도한다.

## 💡 예시

**약한 프롬프트:**
`넌 마케팅 전문가야. 인스타 마케팅 방법 알려줘.`
**강한 프롬프트 (상황/맥락 기반):**
`나는 월 예산 50만원의 로컬 카페 사장이야. 인스타 팔로워 200명. 이전에 일반 음식 사진만 올렸고 효과가 없었어. 지금 당장 할 수 있는 무료 전략 3가지를 각각 구체적인 행동 단계로 알려줘.`

**약한 프롬프트:**
`넌 창업 전문가야. 사업 아이디어 평가해줘.`
**강한 프롬프트 (상황/맥락 기반):**
`나는 직장을 다니면서 주말에만 작업하는 1인 창업자야. 초기 자본은 500만원이고 제조업은 불가능해. 아래 아이디어가 이 조건에서 현실적인지 평가해줘. 실패 가능성도 솔직하게 말해줘.`

## 🏢 두근컴퍼니 적용

- 메인 제품 company-hq의 AI 에이전트 프롬프트에 이 원리를 적용하여 더 정확하고 상황에 맞는 답변을 유도합니다.
- Claude Max, Gemini API, Gemma 등 모든 AI 도구 활용 시 프롬프트 작성의 기본 원칙으로 적용하여 답변 품질을 극대화합니다.
- 두근펫, 매매봇, 검은별, 클로드코드, AI900 등 모든 프로젝트의 프롬프트 및 MCP(Multi-agent Collaboration Protocol) 설계에 활용하여 각 프로젝트의 특수성에 맞는 AI 행동을 정의합니다.
- 특히 사용자가 초보 코딩 실력을 가지고 있어, AI가 초보자 수준에 맞춰 친절하고 구체적인 단계를 제공하도록 독자(Audience) 명시를 적극 활용합니다.

## 📎 출처

- [https://drive.google.com/file/d/1VyKG8kkBxKlnroB3sXFhEQB9deLApp_l/view](https://drive.google.com/file/d/1VyKG8kkBxKlnroB3sXFhEQB9deLApp_l/view)


---

<details>
<summary>📋 메타 정보</summary>

- 최초 수집: `2026-05-15` · 마지막 갱신: `2026-05-15` · 합병: 1회
- 템플릿: v2.2 · slug: `context-rich-prompting`
- 자동 생성: 두근컴퍼니 콘텐츠랩

</details>
