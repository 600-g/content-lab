💡 이 스킬은 **Claude × Canva 연동 두 가지 방식**으로, **커넥터 클릭(일반 사용자)** + **MCP 서버 설정(개발자)** — Cursor·Claude Desktop·Claude Code·VS Code 어디서든 자연어로 캐러셀·SNS 그래픽·프레젠테이션을 생성하는 디자인 자동화 가이드입니다.

## 이게 뭔가요?

**Claude 채팅창에서 Canva 를 연동해 디자인 작업 + 개발 환경에서 Canva 문서 활용**. 두 방식 중 본인 상황에 맞게 선택:

| 방식 | 대상 | 설정 |
|---|---|---|
| **커넥터 클릭** | 일반 사용자 | Claude 앱 설정 → 커넥터 추가 |
| **MCP 서버** | 개발자 | Cursor·Claude Desktop·Claude Code·VS Code |

**Canva 연동으로 가능한 주요 기능**:

| 기능 | 설명 |
|---|---|
| **디자인 생성** | 프롬프트 하나로 **캐러셀·프레젠테이션·SNS 그래픽·문서** 등 생성 |
| **템플릿 자동 채우기** | 내 브랜드 템플릿에 텍스트·콘텐츠 즉시 삽입 |
| **디자인 검색 & 정리** | 기존 Canva 파일을 파일명·주제로 빠르게 검색 |
| **리사이즈 & 내보내기** | 소셜 미디어 규격 변환 + PNG·PDF 내보내기 |
| **Brand Kit 적용** | 내 폰트·색상·브랜드 보이스 자동 적용 (**Canva Pro 이상**) |

💰 유료 필요: Brand Kit 자동 적용은 Canva Pro ($14.99/월) 필요. 그 외 기능은 무료 Canva 도 OK
✅ 무료 대안: Canva 무료 + 수동 Brand Kit / 또는 다른 디자인 도구

## 따라하기

### 방식 1. 커넥터(Connector) 클릭 방식 — 일반 사용자용

Claude 앱에서 클릭 몇 번으로 Canva 계정 연결.

**🟢 Claude 에서 Canva 연결 및 사용하기**:

1. Claude 앱을 열고 **프로필 아이콘** → **설정**
2. 메뉴에서 **커넥터(Connectors)** 선택
3. 목록에서 **Canva** 찾아 누르기
4. 화면의 안내에 따라 본인 Canva 계정 연결
5. 연결 완료 후 새 채팅 시작 → 채팅창의 **설정 아이콘** 누르기
6. 커넥터 섹션에서 **Canva 활성화(켬)**

**🔴 Claude 에서 Canva 기능 끄기**:

- **일시적 비활성화** (해당 채팅에서만): 새 채팅 시작 → 설정 아이콘 → 커넥터 섹션 → Canva 비활성화
- **계정 연결 완전 해제**: 설정 → 커넥터 → Canva 항목 → 더 보기 → **연결 해제**

### 방식 2. MCP 서버 설정 방식 — 개발자용

**Canva Dev MCP (Model Context Protocol) 서버**를 구성해 Cursor·Claude Desktop 등 MCP 클라이언트에서 Canva 앱·통합 개발 지원.

#### ⚙️ 사전 준비 사항

- **git**
- **Node.js v20 이상**
- **npm**
- 호환되는 MCP 클라이언트 (Cursor·Claude Desktop·Claude Code·VS Code 등)

#### STEP 1 — MCP 클라이언트 구성

**A. Cursor** (Agent 모드에서만 사용 가능):

```bash
mkdir -p .cursor
touch .cursor/mcp.json
```

`.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "canva-dev": {
      "command": "npx",
      "args": ["-y", "@canva/cli@latest", "mcp"]
    }
  }
}
```

**B. Claude Desktop** (실 개발은 Cursor·Claude Code 권장):

설정 열기 (Windows: `Ctrl + ,` / macOS: `Cmd + ,`) → **Developer 탭** → **Edit Config** 클릭:

```json
{
  "mcpServers": {
    "canva-dev": {
      "command": "npx",
      "args": ["-y", "@canva/cli@latest", "mcp"]
    }
  }
}
```

**C. Claude Code**:

```bash
claude mcp add canva-dev -- npx -y @canva/cli@latest mcp
```

**D. VS Code** (Agent 모드에서만):

```bash
mkdir -p .vscode
touch .vscode/mcp.json
```

`.vscode/mcp.json`:

```json
{
  "servers": {
    "canva-dev": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@canva/cli@latest", "mcp"]
    }
  }
}
```

#### STEP 2 — 클라이언트 재시작

모든 구성 변경 사항 저장 → 새 설정 적용 위해 MCP 클라이언트 **완전히 종료 후 재시작**.

#### STEP 3 — 연결 확인

- **시각적 확인**: 클라이언트 UI 에서 서버 활성화 여부 확인 (Claude Desktop 의 경우 프롬프트 입력창 근처 **Search and tools** 버튼 → 목록 표시)
- **테스트 질문**: 채팅창에 다음 질문해 도구 호출 프롬프트가 뜨는지 확인:

```
"App UI Kit에는 몇 개의 컴포넌트가 있나요?"
```

💡 **중요 팁**: MCP 도구는 LLM 이 제어 → 직접 실행 X. AI 가 문서 검색하게 하려면 프롬프트에 **"App UI Kit", "Apps SDK"** 등 명확한 키워드 포함하거나 **문서 참조 직접 요청**.

#### 🛠️ 문제 해결

| 증상 | 해결 |
|---|---|
| 도구를 찾지 못함 | Step 1 구성 코드 정확성 확인 + 클라이언트 재시작 |
| 답변이 부정확함 | 새 채팅 세션 → 컨텍스트 초기화 + Canva 공식 문서 키워드 구체적으로 |

#### 🔒 보안 및 개인정보

MCP 서버는 **사용자의 기기에서 로컬로 작동**하며 `canva.dev` 에서 **문서 정보만** 가져옴. 사용자의 코드·프롬프트는 연결된 AI 에이전트 외 다른 곳으로 **전송 X**.

### 활용 — 자연어로 디자인 의뢰하기

**프롬프트 예시**:

```
캐러셀 만들어줘.
주제: AI 시대 개인 브랜딩 전략 5가지
- 슬라이드 10장
- 1080×1080 정사각형
- 톤: 미니멀, 핑크/베이지 그라데이션
- 각 슬라이드: 큰 헤드라인 + 본문 2-3줄 + 작은 번호
- 나의 Brand Kit 적용 (폰트 Pretendard, 컬러 #FF6B9D)
```

```
지난 달 인스타 캐러셀 중 "AI 활용법" 주제의 것 찾아줘.
1080×1920 인스타 스토리 크기로 리사이즈하고
새 시리즈로 정리해줘.
```

## 활용 예시

- **1인 콘텐츠 크리에이터 — 매일 캐러셀 자동화** — Claude 와 캐러셀 주제만 채팅 → 자동 생성 + Brand Kit 자동 적용. 매일 10분에 콘텐츠 1개
- **마케팅 팀 — 캠페인 디자인 자동화** — Claude 에 캠페인 브리프 입력 → 카드뉴스·배너·SNS 그래픽 한 번에. 디자인 외주 비용 절감
- **PM·기획자 — 본인이 직접 제안서 디자인** — 디자이너 없이 본인이 자연어로 제안서·발표자료 생성. 기획자가 프로토타입까지 자체 진행
- **개발자 — 디자인 시스템 reference** — MCP 서버 방식으로 Cursor 에서 Canva 디자인 패턴·컴포넌트 참조하며 코드 작성
- **광고 대행사 — 클라이언트별 디자인 양산** — 클라이언트별 Brand Kit 등록 → 매주 자동 디자인 생성. 1인이 10+ 클라이언트
- **이커머스 — 상세페이지 디자인** — 신상 출시 시 상품 사진 + 카피만 → Canva 상세페이지 자동 생성 → 스마트스토어 자동 업로드
- **교육 콘텐츠 — 강의 슬라이드 자동화** — 강의 노트 → Canva 프레젠테이션 자동 생성. 강사 부담 ↓
- **B2B SaaS — 마케팅 리소스 양산** — 매주 새 기능 출시 시 Twitter·LinkedIn·블로그·이메일용 그래픽 한 번에

## 💡 아이디어

- **Canva 디자인 자동화 SaaS** — Brand Kit + 캠페인 주제 → 자동 디자인 생성 → 슬랙·이메일 푸시 → 월 $20-50/seat
- **에이전시용 Canva + Claude 패키지** — 클라이언트 N개 동시 운영 도구. Brand Kit 격리 + 자동 양산 + 자동 업로드 → 월 $100/seat
- **사내 디자인 표준화 컨설팅** — 회사 Brand Kit 정립 + Claude 연동 + 사내 디자인 가이드 → 컨설팅 패키지 $3,000-10,000
- **Canva 템플릿 마켓플레이스** — 직군별·업종별 Canva 템플릿 100+ 종 → Claude 연동 안내 가이드 포함 → $10-30/팩
- **AI 디자인 강의** — 4시간 강의 패키지: 커넥터 + MCP + 실전 워크플로우 ($100-200/회)
- **Canva 사용자 그룹 운영** — 본인 도시·업종 Canva + Claude 사용자 그룹 운영 → 매월 워크숍 → 광고 수익

## 주의사항

- **Cursor·VS Code MCP 도구는 Agent 모드에서만** — 일반 채팅 모드에서는 동작 X. 명시적으로 Agent 모드 활성화 필요
- **Brand Kit 자동 적용은 Canva Pro 필요** — 무료 플랜은 수동 적용. Brand Kit 자주 쓰면 Pro 권장 ($14.99/월)
- **MCP 도구는 LLM 이 제어** — 직접 명령 실행 X. **명확한 키워드 + 문서 참조 요청**으로 호출 유도
- **Claude Desktop 보다 Cursor·Claude Code 권장** (개발자) — 피드백 루프가 더 좋음
- **저작권 — Canva 무료 이미지 라이선스 확인** — 일부 이미지·폰트는 Canva Pro 필수. 상업 사용 시 라이선스 표시
- **MCP 서버 보안** — `canva.dev` 문서만 가져오는 read-only 서버. 다른 외부 데이터 전송 X. 사내망 사용 시 IT 부서 확인
- **Brand Kit 자동 적용 후 검수** — AI 가 자동 적용한 색상·폰트가 본인 브랜드 톤에 맞는지 첫 5개는 사람 검수
- **Canva 자체 한도** — 무료 플랜은 디자인 수·내보내기 횟수 제한. 본격 양산 시 Pro 권장

## 출처

- [Claude × Canva 디자인 연동 (Notion)](https://abounding-helmet-0e4.notion.site/Claude-Canva-33973c7b15ad81cf8f9cce23a4ae4fe7)
- 제작·운영: @sebia.ai
