---
name: claude-canva-mcp-integration
description: 이 스킬은 Claude AI가 Canva 기능을 활용하여 디자인 작업을 자동화할 수 있도록 MCP 서버를 연동한다. 프롬프트 하나로 다양한 디자인을 생성하고 관리할 수 있게 돕는다. Use when: ['- AI 에이전트가 디자인 콘텐츠를 직접 생성하고 관리해야 할 때', '- 기존 Canva 템플릿에 AI가 생성한 텍스트나 이미지를 자동으로 삽입할 때', '- 특정 브랜드 가이드라인에 맞춰 일관된 디자인 결과물을 얻고자 할 때']
origin: content-lab
grade: A
difficulty: 중급
category: 자동화
ai_tools: ["Claude", "Canva", "Cursor", "Claude Code"]
sources:
  - https://abounding-helmet-0e4.notion.site/Claude-Canva-33973c7b15ad81cf8f9cce23a4ae4fe7?pvs=149
---
# Claude x Canva MCP 서버 연동을 통한 AI 디자인 자동화

이 스킬은 Claude AI가 Canva 기능을 활용하여 디자인 작업을 자동화할 수 있도록 MCP 서버를 연동한다. 프롬프트 하나로 다양한 디자인을 생성하고 관리할 수 있게 돕는다. Use when: ['- AI 에이전트가 디자인 콘텐츠를 직접 생성하고 관리해야 할 때', '- 기존 Canva 템플릿에 AI가 생성한 텍스트나 이미지를 자동으로 삽입할 때', '- 특정 브랜드 가이드라인에 맞춰 일관된 디자인 결과물을 얻고자 할 때']

이 스킬은 Claude AI가 Canva 기능을 활용하여 디자인 작업을 자동화할 수 있도록 MCP 서버를 연동한다. 프롬프트 하나로 다양한 디자인을 생성하고 관리할 수 있게 돕는다. Use when: ['- AI 에이전트가 디자인 콘텐츠를 직접 생성하고 관리해야 할 때', '- 기존 Canva 템플릿에 AI가 생성한 텍스트나 이미지를 자동으로 삽입할 때', '- 특정 브랜드 가이드라인에 맞춰 일관된 디자인 결과물을 얻고자 할 때']

이 스킬은 Claude AI가 Canva 기능을 활용하여 디자인 작업을 자동화할 수 있도록 MCP 서버를 연동한다. 프롬프트 하나로 다양한 디자인을 생성하고 관리할 수 있게 돕는다. Use when: ['- AI 에이전트가 디자인 콘텐츠를 직접 생성하고 관리해야 할 때', '- 기존 Canva 템플릿에 AI가 생성한 텍스트나 이미지를 자동으로 삽입할 때', '- 특정 브랜드 가이드라인에 맞춰 일관된 디자인 결과물을 얻고자 할 때']

 등급 A · 카테고리 디자인 · 난이도 중급
> **도구** Claude, Canva, Cursor, Claude Code
> **적용 대상** 클로드코드, 공통

---

## When to use (언제 쓰는가)

['- AI 에이전트가 디자인 콘텐츠를 직접 생성하고 관리해야 할 때', '- 기존 Canva 템플릿에 AI가 생성한 텍스트나 이미지를 자동으로 삽입할 때', '- 특정 브랜드 가이드라인에 맞춰 일관된 디자인 결과물을 얻고자 할 때']

## How it works (작동 원리)

MCP(Model Context Protocol) 서버는 AI 에이전트가 외부 도구와 통신할 수 있는 표준화된 인터페이스를 제공합니다. 이 스킬은 `npx @canva/cli@latest mcp` 명령을 사용하여 로컬 환경에 Canva MCP 서버를 구성하고, 이를 Cursor, Claude Desktop, Claude Code, VS Code와 같은 MCP 클라이언트에 연결합니다. AI 에이전트는 이 서버를 통해 Canva API의 기능을 호출하여 디자인 생성, 편집, 검색 및 내보내기 작업을 수행합니다. 모든 작업은 로컬에서 이루어지며, AI는 문서 정보를 활용하여 디자인 지시를 내립니다.

## Steps (적용 단계)

1) 사전 준비: 로컬 환경에 git, Node.js (v20 이상), npm이 설치되어 있는지 확인합니다.
2) MCP 클라이언트 구성: 사용 중인 MCP 클라이언트(Cursor, Claude Desktop, Claude Code, VS Code 등)에 따라 `.cursor/mcp.json`, 설정 파일, 또는 CLI 명령어를 통해 `canva-dev` 서버를 다음과 같이 추가합니다.
```json
// .cursor/mcp.json 또는 해당 설정 파일에 추가
{
  "mcpServers": {
    "canva-dev": {
      "command": "npx",
      "args": [
        "-y",
        "@canva/cli@latest",
        "mcp"
      ]
    }
  }
}
```
```bash
# Claude Code의 경우 터미널에서 실행
claude mcp add canva-dev -- npx -y @canva/cli@latest mcp
```
3) 클라이언트 재시작: 모든 구성 변경 사항을 저장하고, 사용 중인 MCP 클라이언트를 완전히 종료한 후 재시작하여 새 설정을 적용합니다.
4) 연결 확인 및 테스트: 클라이언트 UI에서 서버 활성화 여부를 확인하고, 채팅창에 "App UI Kit에는 몇 개의 컴포넌트가 있나요?"와 같이 질문하여 도구 호출 프롬프트가 뜨는지 확인합니다.

## Examples (예시)

['*   **프롬프트:** "새로운 SNS 그래픽을 만들어줘. 주제는 \'AI 기술 동향\'이고, 캐러셀 형식으로 구성해줘."\n*   **기대 출력:** AI가 Canva MCP 서버를 통해 캐러셀 형식의 SNS 그래픽 디자인을 생성하고, 관련 템플릿에 콘텐츠를 채워 Canva 링크 또는 미리보기를 제공.\n*   **프롬프트:** "내 브랜드 키트를 사용하여 \'두근컴퍼니 여름 프로모션\' 텍스트로 프레젠테이션 템플릿을 채워줘. 폰트는 회사 기본 폰트, 색상은 브랜드 메인 색상으로 적용해줘."\n*   **기대 출력:** AI가 Canva Brand Kit 설정을 활용하여 지정된 텍스트와 브랜드 가이드라인에 맞춰 프레젠테이션 템플릿을 완성하여 제공.']

## 두근 환경 적용

- **company-hq:** AI 에이전트가 회사 홍보용 SNS 콘텐츠, 프레젠테이션, 보고서 디자인 등을 직접 생성하고 관리하는 데 활용. AI 사무실 시각화 플랫폼 내에서 디자인 요청을 처리할 수 있게 함.
- **클로드코드:** 개발 및 테스트 환경에서 AI가 Canva 디자인 기능을 활용하여 UI/UX 목업이나 콘텐츠 시안을 빠르게 생성하는 데 사용.

## ️ Caveats (주의사항)

['- MCP 도구는 LLM에 의해 제어되므로, AI가 도구를 호출하도록 명확한 키워드나 문맥을 제공해야 합니다.', '- 초기 설정은 Node.js 및 CLI 환경에 대한 기본적인 이해를 요구합니다.', "- 'Brand Kit 적용'과 같은 일부 고급 기능은 Canva Pro 이상의 유료 계정이 필요할 수 있습니다.", '- MCP 서버는 사용자의 기기에서 로컬로 작동하며 canva.dev에서 문서 정보만 가져오므로, 보안 및 개인정보 보호에 유리합니다.']

## Sources (출처)

- [https://abounding-helmet-0e4.notion.site/Claude-Canva-33973c7b15ad81cf8f9cce23a4ae4fe7?pvs=149](https://abounding-helmet-0e4.notion.site/Claude-Canva-33973c7b15ad81cf8f9cce23a4ae4fe7?pvs=149)

---

## 메타 정보

- 최초 수집: 2026-05-15
- 마지막 갱신: 2026-05-15
- 합병 횟수: 1회
- 템플릿: v1 (TEMPLATE.md)
- 자동 생성: 두근컴퍼니 콘텐츠랩 v4.0
