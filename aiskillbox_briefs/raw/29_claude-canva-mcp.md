# Claude x Canva MCP 연동

- URL: https://abounding-helmet-0e4.notion.site/Claude-Canva-33973c7b15ad81cf8f9cce23a4ae4fe7?pvs=149
- source_type: notion
- length: 3085 chars
- elapsed: 6s
- ok: True

---

### 🖌️ 일반 사용자용: Claude × Canva 디자인 연동

Claude 채팅창에서 Canva를 연동하여 디자인 작업을 수행하거나, 개발 환경에서 Canva 문서를 활용할 수 있습니다. 필요에 따라 아래의 커넥터 클릭 방식 또는 MCP 서버 설정 방식 중 하나를 선택해 진행해 주세요.

#### 📌 주요 기능

디자인 생성: 프롬프트 하나로 캐러셀, 프레젠테이션, SNS 그래픽, 문서 등 생성

템플릿 자동 채우기: 내 브랜드 템플릿에 텍스트와 콘텐츠를 즉시 삽입

디자인 검색 & 정리: 기존 Canva 파일을 파일명이나 주제로 빠르게 검색

리사이즈 & 내보내기: 소셜 미디어 규격으로 변환하거나 PNG, PDF 형식으로 내보내기

Brand Kit 적용: 내 폰트, 색상, 브랜드 보이스 자동 적용 (Canva Pro 이상)

#### 🔗 참고 문서

### 1. 커넥터(Connector) 클릭 방식 연동

Claude 앱 내에서 클릭 몇 번으로 간단하게 Canva 계정을 연결하고 사용하는 직관적인 방법입니다.

#### 🟢 Claude에서 Canva 연결 및 사용하기

Claude 앱을 열고 프로필 아이콘을 눌러 설정으로 이동합니다.

메뉴에서 커넥터(Connectors)를 선택합니다.

목록에서 Canva를 찾아 누릅니다.

화면의 안내에 따라 본인의 Canva 계정을 연결합니다.

연결이 완료되면 새 채팅을 시작하고 채팅창의 설정 아이콘을 누릅니다.

커넥터 섹션에서 Canva를 활성화(켬) 합니다.

#### 🔴 Claude에서 Canva 기능 끄기

상황에 따라 일시적으로 기능을 끄거나, 계정 연결을 완전히 해제할 수 있습니다.

일시적으로 비활성화 (해당 채팅에서만):

새 채팅을 시작하고 설정 아이콘을 선택합니다.

커넥터 섹션에서 Canva를 비활성화(끔) 합니다.

계정 연결 완전히 해제하기:

설정 > 커넥터 메뉴로 이동합니다.

Canva 항목에서 '더 보기'를 선택합니다.

연결 해제를 선택한 후 확인을 누릅니다.

### 2. MCP 서버 설정 방식 연동

Canva Dev MCP(Model Context Protocol) 서버를 구성하여, 선호하는 MCP 클라이언트(Cursor, Claude Desktop 등)에서 Canva 앱 및 통합 개발 지원을 받는 방법입니다.

#### ⚙️ 사전 준비 사항

이 방식을 사용하려면 로컬 환경에 다음 도구들이 설치되어 있어야 합니다.

git

Node.js

v20 이상npm

호환되는 MCP 클라이언트 (Cursor, Claude Desktop 등)

#### 🚀 Step 1: MCP 클라이언트 구성

사용 중인 환경에 맞춰 아래의 설정을 적용하세요.

#### A. Cursor

참고: Cursor에서 MCP 도구는 Agent 모드에서만 사용할 수 있습니다.

프로젝트 디렉토리에 설정 폴더와 파일을 생성합니다.

mkdir -p .cursor
touch .cursor/mcp.json

.cursor/mcp.json

파일에 다음 구성을 추가합니다.
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

#### B. Claude Desktop

참고: 실질적인 개발 및 피드백 루프를 위해서는 Claude Desktop보다 Cursor나 Claude Code 사용을 권장합니다.

Claude Desktop 설정을 엽니다. (Windows:

Ctrl + ,

/ macOS: Command + ,

)
Developer 탭으로 이동합니다.

Edit Config를 클릭하고 다음 구성을 추가합니다.

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

#### C. Claude Code

터미널에서 다음 명령어를 실행하여 서버를 추가합니다.

claude mcp add canva-dev -- npx -y @canva/cli@latest mcp

#### D. VS Code

참고: MCP 도구는 Agent 모드에서만 사용할 수 있습니다.

워크스페이스에 VS Code 설정 폴더와 파일을 생성합니다.

mkdir -p .vscode
touch .vscode/mcp.json

.vscode/mcp.json

파일에 다음 내용을 추가합니다.
{
"servers": {
"canva-dev": {
"type": "stdio",
"command": "npx",
"args": [
"-y",
"@canva/cli@latest",
"mcp"
]
}
}
}

#### 🔄 Step 2: 클라이언트 재시작

모든 구성 변경 사항을 저장합니다.

새 설정을 적용하기 위해 사용 중인 MCP 클라이언트를 완전히 종료한 후 재시작합니다.

#### 🔍 Step 3: 연결 확인

시각적 확인: 클라이언트 UI 내에서 서버가 활성화되었는지 확인합니다. (예: Claude Desktop의 경우 프롬프트 입력창 근처의 'Search and tools' 버튼 클릭 시 목록에 표시됨)

테스트 질문: 채팅창에 다음과 같이 질문하여 도구 호출 프롬프트가 뜨는지 확인합니다.

"App UI Kit에는 몇 개의 컴포넌트가 있나요?"

💡 중요 팁: MCP 도구는 LLM이 제어하므로 직접 실행할 수 없습니다. AI가 문서를 검색하게 하려면 프롬프트에 "App UI Kit", "Apps SDK" 등 명확한 키워드를 포함하거나 문서를 참조해 달라고 직접 요청하세요.

#### 🛠️ 문제 해결

도구를 찾지 못할 때: Step 1의 구성 코드가 정확한지 확인하고 클라이언트를 재시작하세요.

답변이 부정확할 때: 새 채팅 세션을 열어 컨텍스트를 초기화하고, 원하는 Canva 공식 문서 키워드를 더 구체적으로 포함하여 질문해 보세요.

#### 🔒 보안 및 개인정보

해당 MCP 서버는 사용자의 기기에서 로컬로 작동하며

canva.dev

에서 문서 정보만 가져옵니다. 사용자의 코드나 프롬프트는 연결된 AI 에이전트 외의 다른 곳으로 전송되지 않습니다.앞으로 더 많은 AI 인사이트와 트렌드는?

@sebia.ai 팔로우하고 함께 앞서 나가요!
