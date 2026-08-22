---
name: claude-code-headroom
description: 이 스킬은 **Claude Code** 사용 시 입력 토큰을 미리 압축하여 **비용을 절감**하는 **Headroom** 사용법을 안내하는 스킬입니다.
origin: content-lab
grade: A
difficulty: 초급
category: 개발
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://abounding-helmet-0e4.notion.site/Claude-Code-Headroom-38d73c7b15ad813190abf555ad0bf667?pvs=149
---

# Claude Code 토큰 비용 절감

💡 이 스킬은 **Claude Code** 사용 시 입력 토큰을 미리 압축하여 **비용을 절감**하는 **Headroom** 사용법을 안내하는 스킬입니다.

## 이게 뭔가요?

Claude Code는 AI 에이전트가 처리하는 방대한 양의 데이터(로그, 에러 메시지, 코드 파일, RAG Chunk 등)를 LLM에 전달하기 전에 미리 압축하여 불필요한 토큰 낭비를 막아주는 **Context Compression Layer(맥락 압축 계층)**입니다.

주로 Claude Code와 같이 입력 토큰의 양에 따라 비용이 발생하는 LLM 서비스 앞에서 활용됩니다. Headroom을 사용하면 AI가 모든 정보를 그대로 읽는 대신, 핵심적인 정보만을 필터링하여 전달함으로써 **60~95%의 토큰 절감 효과**를 기대할 수 있습니다 (작업 종류 및 입력 파일에 따라 상이).

기존에는 파일/로그 등이 그대로 Claude Code에 전달되어 불필요한 토큰 낭비가 발생했지만, Headroom을 적용하면 파일/로그를 Headroom에서 압축/정리한 후 Claude Code에 전달하여 비용을 최적화할 수 있습니다.

💰 **유료 필요**: Claude Code 자체는 유료 서비스이며, Headroom은 이 비용 최적화를 위한 도구입니다.

## 따라하기

Headroom을 설치하고 Claude Code에 적용하는 방법은 다음과 같습니다.

1.  **Headroom 전체 패키지 설치**
    터미널을 열고 아래 명령어를 실행하여 Headroom 전체 패키지를 설치합니다. Node/TypeScript 환경에서는 `npm install headroom-ai`를 사용합니다.
    ```bash
    pip install "headroom-ai[all]"
    ```

2.  **Claude Code에 Headroom 래핑 적용**
    설치가 완료되면 `headroom wrap claude` 명령어를 사용하여 Claude Code에 Headroom 래핑을 적용합니다.
    ```bash
    headroom wrap claude
    ```

3.  **토큰 절감 현황 확인 (대시보드 실행)**
    Headroom의 토큰 절감 현황을 확인하기 위해 대시보드를 실행합니다.
    ```bash
    headroom dashboard
    ```

## 활용 예시

*   **대규모 로그 파일 분석**: 서비스 운영 중 발생하는 방대한 양의 로그 파일 전체를 Claude Code에 입력하는 대신, Headroom으로 압축하여 필요한 핵심 에러 정보만 전달함으로써 분석 시간과 비용을 절감합니다.
*   **복잡한 코드베이스 디버깅**: 수백 페이지에 달하는 소스 코드 전체를 Claude Code에 한 번에 입력하는 대신, Headroom을 통해 관련 함수나 에러 발생 지점 근처의 코드로 압축하여 전달합니다.
*   **RAG 시스템에서의 정보 검색**: Retrieval-Augmented Generation (RAG) 시스템에서 검색된 여러 문서 Chunk들을 그대로 LLM에 전달하면 토큰이 과도하게 소모될 수 있습니다. Headroom을 사용하여 관련성 높은 정보만 추출하고 압축하여 전달함으로써 비용 효율성을 높입니다.

## 주의사항

*   **절감률은 절대적인 수치가 아닙니다**: 공식 문서에서 제시하는 60–95% 절감률은 최대 기대치이며, 실제 작업 환경 및 입력 데이터의 특성에 따라 절감률은 달라질 수 있습니다.
*   **점진적인 도입을 권장합니다**: 중요한 코드나 핵심적인 에러 로그를 압축하는 과정에서 맥락이 유실될 가능성이 있습니다. 처음에는 작은 프로젝트나 덜 민감한 데이터로 Headroom의 압축 성능을 테스트해 보는 것이 좋습니다.
*   **팀 단위 적용 시 분리 운영**: 여러 사용자가 함께 Headroom을 사용하는 팀 환경에서는 개인의 로컬 설정과 팀 공용 설정을 명확히 분리하여 운영하는 것이 예상치 못한 문제를 방지하는 데 도움이 됩니다.

## 출처

[Claude Code 토큰 줄이는 Headroom 가이드](https://abounding-helmet-0e4.notion.site/Claude-Code-Headroom-38d73c7b15ad813190abf555ad0bf667?pvs=149)

## 출처

- [https://abounding-helmet-0e4.notion.site/Claude-Code-Headroom-38d73c7b15ad813190abf555ad0bf667?pvs=149](https://abounding-helmet-0e4.notion.site/Claude-Code-Headroom-38d73c7b15ad813190abf555ad0bf667?pvs=149)
