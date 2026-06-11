---
name: claude-sub-agent-pattern
description: 서브에이전트를 활용하여 메인 AI의 컨텍스트를 보호하고, 복잡하고 대규모의 작업을 병렬로 분산 처리하는 고급 패턴입니다. 토큰 비용 최적화 및 작업 흐름 관리에 필수적입니다.
origin: content-lab
grade: S
difficulty: 고급
category: 개발
ai_tools: ["Gemini", "Ollama"]
sources:
  - https://abounding-helmet-0e4.notion.site/50-300-36373c7b15ad81ccac8ded33f43886d5
---

# 클로드 서브에이전트 패턴: 컨텍스트 보호 및 병렬 작업 최적화 (합병됨)

## 두근컴퍼니 적용

두근컴퍼니의 'company-hq' 아키텍처 구현 시 핵심 패턴으로 활용됩니다. Opus 모델 사용 시 비용 폭증을 막기 위해 단순 조사/크롤링은 Sonnet 모델 지정이 필수적이며, `/compact` 등 토큰 관리 명령어를 습관화해야 합니다.

## 출처

- [https://abounding-helmet-0e4.notion.site/50-300-36373c7b15ad81ccac8ded33f43886d5](https://abounding-helmet-0e4.notion.site/50-300-36373c7b15ad81ccac8ded33f43886d5)
