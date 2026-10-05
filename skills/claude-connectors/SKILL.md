---
name: claude-connectors
description: Claude 앱·**Claude Code**에 외부 서비스를 붙이는 통합 가이드 — 공식 커넥터(Notion·Slack·Canva·Gmail·Drive·Calendar·Higgsfield), **Notion MCP**·**Canva MCP**, **Zapier MCP** 다리(Sheets·YouTube·Zoom·Telegram·Discord), 카카오 **PlayMCP** 한국형 MCP 12종까지 서비스별 연결법.
origin: content-lab
grade: S
difficulty: 중급
category: 자동화
ai_tools: ["Claude", "Claude Code", "Canva", "Cursor", "GPT", "Codex"]
sources:
  - https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149
  - https://developers.notion.com/guides/mcp/get-started-with-mcp
  - https://abounding-helmet-0e4.notion.site/Claude-Canva-33973c7b15ad81cf8f9cce23a4ae4fe7?pvs=149
  - https://playmcp.kakao.com/
originals:
  - claude-connectors | 클로드 연동 16가지 | https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149
  - claude-connectors-for-automation | 클로드에 16가지 AI 도구 연결하기 | https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149
  - claude-code-notion-mcp | Claude Code × Notion MCP 연동 | https://developers.notion.com/guides/mcp/get-started-with-mcp
  - claude-canva-mcp-integration | Claude x Canva MCP 서버 연동을 통한 AI 디자인 자동화 | https://abounding-helmet-0e4.notion.site/Claude-Canva-33973c7b15ad81cf8f9cce23a4ae4fe7?pvs=149
  - kakao-playmcp-catalog | 카카오 PlayMCP — AI에서 카톡·맵·멜론 연동 | https://playmcp.kakao.com/
---

# 클로드 외부 서비스 연결 가이드

💡 Claude 에 **공식 커넥터**·**MCP 서버**를 붙이면 Notion·Slack·Canva·Gmail 같은 앱을 채팅창에서 바로 읽고 쓰게 됩니다. 공식 커넥터가 없는 앱은 **Zapier MCP**(9,000개 앱 다리)나 카카오 **PlayMCP**(한국형 MCP 마켓)로 넓힙니다.

## 이게 뭔가요?

Claude(클로드)는 외부 서비스와 연결하는 두 가지 통로를 제공합니다.

- **공식 커넥터**: Claude 웹/데스크톱/모바일의 설정 → 커넥터(Connectors)에서 "찾아보기(Browse connectors)"로 고르거나, "커스텀 커넥터 추가(Add custom connector)"에 서버 URL 을 넣어 붙입니다. OAuth 로그인 한 번이면 끝납니다.
- **MCP(Model Context Protocol) 서버**: AI 에이전트가 외부 도구와 통신하도록 만든 표준 인터페이스입니다. Claude Code·Cursor·VS Code·ChatGPT·Codex 같은 도구에도 같은 서버를 붙일 수 있습니다. 원격(URL) 서버와, `npx` 로 내 컴퓨터에서 띄우는 로컬 서버 두 종류가 있습니다.

연결하고 나면 "회의록 페이지 새로 만들고 오늘 액션 아이템 정리해서 넣어줘" 같은 자연어 한 줄로 앱을 조작할 수 있습니다. 공식 커넥터가 없는 앱은 **Zapier MCP** 를 다리로 삼아 9,000개 이상의 앱으로 넓히고, 한국 서비스(공연·아파트·공시·다이소 재고·택배 등)는 카카오 **PlayMCP** 마켓에서 찾습니다.

강력한 기능 대부분은 Claude 유료 플랜(Pro $20/월 이상)이 필요합니다. 무료 대안으로는 Gemini·ChatGPT 등 다른 AI 도구를 기능 제한적으로 활용할 수 있습니다.

### 연결 난이도 4단계

| 단계 | 의미 | 서비스 |
|---|---|---|
| ✅ 바로 가능 | 공식 커넥터 / 전용 MCP | Higgsfield, Notion, Slack, Canva, Zapier |
| 🟡 읽기+생성까지만 | 공식 커넥터지만 수정·정리는 Zapier 로 보완 | Gmail, Google Drive, Google Calendar |
| 🟡 설정하면 가능 | Zapier MCP / 봇 토큰 설정 필요 | Google Sheets, YouTube, Zoom, Telegram, Discord |
| 🟠 제약 있음 | 조건부·직접 개발 | Instagram, 카카오톡, 네이버 |
| 🇰🇷 한국형 데이터 | 카카오 PlayMCP 마켓의 MCP 12종 | 여기어때·아파트 정보·OpenDART·다이소·띵동 등 |

## 따라하기

### 어떤 방법을 언제 쓰나

| 상황 | 쓸 방법 | 아래 절 |
|---|---|---|
| Claude 웹/데스크톱/모바일에서 Notion·Slack·Canva·Gmail·Drive·Calendar 를 쓰고 싶다 | 공식 커넥터 "찾아보기" | 방법 1 |
| 공식 목록에 없지만 서비스가 MCP 서버 URL 을 공개했다 (Higgsfield, Windsor.ai 등) | 커스텀 커넥터 추가 | 방법 2 |
| Claude Code·Cursor·VS Code·ChatGPT·Codex 에서 Notion 을 쓰고 싶다 | Notion 공식 원격 MCP | 방법 3 |
| Canva 앱 개발 문서를 AI 에게 참고시키며 개발하고 싶다 | Canva 로컬 MCP (`@canva/cli`) | 방법 4 |
| Google Sheets·YouTube·Zoom 처럼 공식 커넥터가 없거나 Gmail·Drive 의 수정·삭제가 필요하다 | Zapier MCP 다리 | 방법 5 |
| 텔레그램·디스코드로 메시지를 보내고 싶다 | 봇 토큰 + MCP/Zapier | 방법 6 |
| Instagram 분석, 카카오톡 알림, 네이버 캘린더·메일 | 외부 서비스·직접 개발 | 방법 7 |
| 아파트 시세·공연·공시·매장 재고 같은 한국 데이터 | 카카오 PlayMCP | 방법 8 |

### 서비스별 한눈에 보기

| 번호 | 서비스 | 연결 방법 | 할 수 있는 일 | 핵심 한계 |
|---|---|---|---|---|
| 1 | Higgsfield | 커스텀 커넥터 `https://mcp.higgsfield.ai` | AI 영상 생성 | 최대 4K·15초, 크레딧 소모 |
| 2 | Gmail | 공식 커넥터 | 읽기 + 초안 생성 | 발송·삭제·이동·라벨 불가 |
| 3 | Instagram | Windsor.ai MCP | 인사이트 조회 | 읽기 전용, 비즈니스/크리에이터 계정만 |
| 4 | Telegram | BotFather 토큰 + MCP/Zapier | 봇 메시지 전송 | 봇과 대화를 시작한 사용자/그룹만 |
| 5 | Google Drive | 공식 커넥터 | 검색·읽기·업로드·폴더 생성 | 이동·이름변경·삭제 불가 |
| 6 | 카카오톡 | Kakao Developers 메모 API (또는 PlayMCP 나챗방) | 나에게 보내기 | 타인 전송은 별도 심사 |
| 7 | 네이버 | Naver Developers 직접 개발 | 캘린더 API, 메일 IMAP/SMTP | 공식 통합 없음 |
| 8 | Notion | 공식 커넥터 / 공식 MCP | 읽기·검색·생성·업데이트 | 삭제 불가, 이미지·파일 업로드 미지원 |
| 9 | Google Calendar | 공식 커넥터 | 확인 + 새 일정 생성 | 수정·삭제는 Zapier 권장 |
| 10 | Google Sheets | Zapier MCP | 행 추가·조회 | 헤더가 미리 있어야 함 |
| 11 | Slack | 공식 커넥터 | 읽기·검색·게시·답글 | 본인 권한 채널만, 작업마다 승인 |
| 12 | Canva | 공식 커넥터 / 로컬 MCP | 검색·생성·내보내기 | 일부 기능 권한 개별 승인 |
| 13 | YouTube | Zapier MCP | 영상 찾기·업로드·썸네일·리포트 | 업로드는 전화번호 인증 필요 |
| 14 | Discord | Developer Portal 토큰 + MCP/Zapier | 채널 메시지 | 초대된 서버·권한 채널만 |
| 15 | Zoom | Zapier MCP | 회의 생성·녹화·요약 | 녹화·전사는 Zoom 유료 |
| 16 | Zapier | `mcp.zapier.com` MCP 서버 | 9,000개 앱 연결 | 호출마다 task 2개 소모 |

### 방법 1. 공식 커넥터 연결 (Notion·Slack·Canva·Gmail·Drive·Calendar)

공통 절차는 같습니다.

1. Claude 웹 → 설정 → 커넥터 (데스크톱: Customize → Connectors)
2. "찾아보기(Browse connectors)"에서 서비스 선택 → 연결(Connect)
3. 서비스 인증 화면에서 허용(Allow)
4. (데스크톱) 앱 재시작 후 채팅창 "+"에서 해당 서비스 토글 ON

서비스별 차이만 아래에 정리합니다.

#### Notion → 문서 자동 작성

1. 준비물: 유료 Claude 플랜 + Notion 계정
2. 설정: Claude 웹 → 설정 → 커넥터 (데스크톱: Customize → Connectors)
3. "찾아보기(Browse connectors)"에서 Notion 선택 → 연결(Connect)
4. 인증: Notion 인증 페이지에서 워크스페이스 선택 → 계속(Continue)
5. (데스크톱) 앱 재시작 후 채팅창 "+"에서 Notion 토글 ON
6. 예시 명령: "회의록 페이지 새로 만들고 오늘 액션 아이템 정리해서 넣어줘"
7. 한계: 읽기·검색·생성·업데이트 가능, 삭제는 불가. 처음엔 특정 페이지/DB로 범위 좁혀 연결 권장

#### Slack → 팀 메시지 자동화

1. 준비물: 유료 Claude 플랜 + Slack 워크스페이스 계정(조직은 관리자 권한 필요)
2. 설정: 커넥터 → "찾아보기"에서 Slack 선택 → 연결(Connect)
3. 인증: 워크스페이스 선택 후 허용(Allow) → 채팅창 "+"에서 Slack 토글 ON
4. 예시 명령: "#마케팅 채널 이번 주 중요한 논의 요약하고 결정사항 정리해서 올려줘"
5. 한계: 읽기·검색·게시·답글 지원, 본인 권한 범위 채널만, 각 작업은 사용자 승인 필요

#### Canva → 디자인 자동 생성

1. 준비물: 유료 Claude 플랜(Pro $20/월~) + Canva 계정
2. 설정: 커넥터 → "찾아보기"에서 Canva 검색 → 카드의 "+"(연결) 클릭
3. 인증: Canva 인증 화면에서 허용(Allow)
4. 권한 설정: "구성(Configure)"에서 'search designs', 'generate designs with AI' 등 개별 설정 → 채팅창 "+"에서 Canva 토글 ON
5. 예시 명령: "이 카피로 인스타용 카드뉴스 디자인 초안 만들고 PNG로 내보내줘"
6. 한계: 검색·생성·내보내기 지원(인라인 미리보기), AI 생성 등 일부 기능은 권한 개별 승인 필요

Canva 에 일을 시킬 때 쓸 만한 요청 예시입니다.

- **프롬프트:** "새로운 SNS 그래픽을 만들어줘. 주제는 'AI 기술 동향'이고, 캐러셀 형식으로 구성해줘."
  - **기대 출력:** Canva 를 통해 캐러셀 형식의 SNS 그래픽 디자인을 생성하고, 관련 템플릿에 콘텐츠를 채워 Canva 링크 또는 미리보기를 제공.
- **프롬프트:** "내 브랜드 키트를 사용하여 '여름 프로모션' 텍스트로 프레젠테이션 템플릿을 채워줘. 폰트는 회사 기본 폰트, 색상은 브랜드 메인 색상으로 적용해줘."
  - **기대 출력:** Canva Brand Kit 설정을 활용하여 지정된 텍스트와 브랜드 가이드라인에 맞춰 프레젠테이션 템플릿을 완성하여 제공. ('Brand Kit 적용' 같은 고급 기능은 Canva Pro 이상의 유료 계정이 필요할 수 있습니다.)

#### Gmail → 메일 읽기·초안 작성

1. 준비물: 유료 Claude 플랜 + Google 계정
2. 설정: 커넥터 → "찾아보기"에서 Gmail 선택 → 연결(Connect)
3. 인증: Google 로그인 후 권한 허용 → 채팅창 "+"에서 Gmail 토글 ON
4. 예시 명령: "지난주 거래처 메일 찾아 요약하고 회신 초안 작성해줘"
5. 한계: 읽기 + 초안 생성만. 발송·삭제·이동·라벨분류 불가, 수정 작업은 Zapier MCP 필요

#### Google Drive → 파일 검색·읽기·저장

1. 준비물: Google 계정(무료 Claude 포함 가능)
2. 설정: 커넥터 → "찾아보기"에서 Google Drive 선택 → 연결(Connect)
3. 인증: Google 로그인 후 권한 허용 → 채팅창 "+"에서 Google Drive 토글 ON
4. 예시 명령: "내 드라이브에서 '6월 보고서' 찾아 핵심 내용 정리해줘"
5. 한계: 검색·읽기·업로드·폴더생성만(텍스트만 추출), 이동·이름변경·삭제 불가, 정리는 Zapier 필요

#### Google Calendar → 일정 확인·생성

1. 준비물: 유료 Claude 플랜 + Google 계정
2. 설정: 커넥터 → "찾아보기"에서 Google Calendar 선택 → 연결(Connect)
3. 인증: Google 로그인 후 권한 허용 → 채팅창 "+"에서 Google Calendar 토글 ON
4. 예시 명령: "다음 주 빈 시간 찾아 화요일 오후에 1시간 회의 잡아줘"
5. 한계: 확인 + 새 일정 생성만 안정적, 기존 일정 수정·삭제는 Zapier 권장

### 방법 2. 커스텀 커넥터 추가 (서버 URL 이 있는 서비스)

목록에 없는 서비스라도 MCP 서버 URL 을 공개했다면 직접 붙일 수 있습니다. 대표 예가 Higgsfield 입니다. Zapier MCP 서버(방법 5)와 Windsor.ai(방법 7), PlayMCP(방법 8)도 같은 경로로 붙입니다.

#### Higgsfield → 초 고퀄 AI 영상 연동 제작

1. 준비물: Higgsfield 계정(무료 크레딧 제공), Claude PRO 모델 이상 추천
2. 설정: Claude 웹/데스크톱/모바일 → 설정(Settings) → 커넥터(Connectors) → "커스텀 커넥터 추가(Add custom connector)"
3. 이름: `Higgsfield`, 서버 URL: `https://mcp.higgsfield.ai`
4. 연결: Higgsfield 계정 로그인/인증, 필요 시 "항상 허용(Always Allow)"
5. 예시 명령: "Higgsfield로 '밤거리를 걷는 네온 고양이' 5초짜리 4K 영상 만들어줘"
6. 한계: 최대 4K·15초, 생성 시 크레딧 소모, 무료 소진 후 유료 플랜 필요

### 방법 3. Notion 공식 MCP — Claude Code·Cursor·ChatGPT 등 여러 도구에 연결

Notion 공식 MCP 서버는 한 번 OAuth 인증하면 AI 도구가 본인 노션 워크스페이스에 사용자 권한 범위 내에서 직접 읽고 쓸 수 있게 해 줍니다. Claude 앱의 Notion 커넥터(방법 1)와 같은 서버를 다른 도구에서도 쓰는 방법입니다.

#### 지원 AI 도구

| 도구 | 연결 방식 |
|---|---|
| Claude Code | `/mcp` 명령 + OAuth |
| Cursor | `.cursor/mcp.json` 프로젝트 설정 |
| VS Code (Copilot) | Command Palette → MCP: Open User Configuration |
| Claude Desktop | Settings → Connectors |
| ChatGPT | chatgpt.com/#settings/Connectors |
| Codex | `.codex/config.toml` |
| Antigravity | `mcp_config.json` (커스텀 서버 권장) |

#### Claude Code — 가장 간단

```bash
/mcp
# OAuth 플로우 따라가면 끝
```

**Scope 옵션:**
- `--scope local` (기본) — 현재 프로젝트만
- `--scope project` — 팀과 `.mcp.json` 파일로 공유
- `--scope user` — 모든 프로젝트

**관리 명령:**
```bash
/mcp        # 설치된 MCP 서버 목록 + 관리
/context    # MCP 서버별 토큰 사용량
```

#### Cursor — 프로젝트 공유

`.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "notion": {
      "url": "https://mcp.notion.com/mcp",
      "transport": "streamable-http"
    }
  }
}
```

#### 기타 도구 — URL 직접

| Transport | URL | 비고 |
|---|---|---|
| Streamable HTTP (권장) | `https://mcp.notion.com/mcp` | 모던 전송 |
| SSE (레거시) | `https://mcp.notion.com/sse` | 호환용 |

#### 공식 서버 vs 오픈소스 서버

| 항목 | Notion MCP (공식) | notion-mcp-server (OSS) |
|---|---|---|
| 인증 | OAuth | Bearer Token |
| 유지보수 | 활발 | **중단** |
| API | AI 에이전트 최적화 | v1 JSON API |
| 인프라 | 호스팅됨 | 본인 배포 |
| 권장 대상 | 대부분 사용자 | 헤드리스·자동화 |

공식 서버는 OAuth 가 필수라 사람이 없는 헤드리스 자동화에는 맞지 않습니다. 그런 경우에만 Bearer Token 방식의 OSS 서버를 고려하되, 유지보수가 중단된 점을 감안해야 합니다.

### 방법 4. Canva 로컬 MCP 서버 (`@canva/cli`)

`npx @canva/cli@latest mcp` 명령으로 내 컴퓨터에 Canva MCP 서버(`canva-dev`)를 띄우고, Cursor·Claude Desktop·Claude Code·VS Code 같은 MCP 클라이언트에 연결하는 방법입니다. 서버는 기기에서 로컬로 작동하며 canva.dev 에서 문서 정보만 가져옵니다. 그래서 디자인 결과물을 바로 만드는 용도라기보다, AI 가 Canva 개발 문서(App UI Kit 등)를 참고해 작업하게 하는 데 맞습니다. 디자인 생성·검색·내보내기 자체가 목적이면 방법 1 의 공식 Canva 커넥터가 더 간단합니다.

1. **사전 준비**: 로컬 환경에 git, Node.js (v20 이상), npm 이 설치되어 있는지 확인합니다.
2. **MCP 클라이언트 구성**: 사용 중인 클라이언트에 따라 `.cursor/mcp.json`, 설정 파일, 또는 CLI 명령어로 `canva-dev` 서버를 추가합니다.

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

3. **클라이언트 재시작**: 구성 변경 사항을 저장하고, 사용 중인 MCP 클라이언트를 완전히 종료한 뒤 재시작해 새 설정을 적용합니다.
4. **연결 확인 및 테스트**: 클라이언트 UI 에서 서버 활성화 여부를 확인하고, 채팅창에 "App UI Kit에는 몇 개의 컴포넌트가 있나요?"처럼 질문해 도구 호출 프롬프트가 뜨는지 확인합니다.

MCP 도구는 LLM 이 판단해 호출하므로, 도구를 쓰게 하려면 "Canva", "App UI Kit" 같은 명확한 키워드나 문맥을 요청에 넣어야 합니다.

### 방법 5. Zapier MCP — 9,000개 앱으로 넓히는 다리

공식 커넥터가 없거나, 공식 커넥터가 읽기+생성까지만 되는 서비스(Gmail·Drive·Calendar)의 수정·정리 작업을 보완합니다. Google Sheets·YouTube·Zoom 은 이 절의 Zapier MCP 서버를 **먼저** 만들어야 합니다.

#### Zapier MCP 서버 만들기

1. 준비물: Zapier 계정(무료 포함, 호출 1회당 task 2개 차감) + MCP 추가 가능한 유료 Claude 플랜
2. MCP 서버 생성: `mcp.zapier.com` → "+ New MCP Server" → Claude 선택 → 서버 이름 입력 → "Create MCP Server"
3. 도구 추가: "Configure" 탭 → "+ Add tool" → 앱 검색 → 액션 선택(또는 "Add all tools") → 계정 인증 → Save
4. Claude 연결: "Connect" 탭의 서버 URL 복사 → Claude 설정에서 새 커넥터로 추가
5. 예시 명령: "내 Zapier에 연결된 앱들로 지금 뭘 할 수 있는지 알려줘"
6. 한계: 서버 URL=비밀번호(유출 주의), 호출마다 task 2개 소모, 추가한 액션만 사용 가능

이후 앱을 늘릴 때는 같은 서버의 "Configure" 탭에서 도구만 추가하면 됩니다. Claude 쪽 커넥터를 다시 만들 필요는 없습니다.

#### Google Sheets → 숫자 자동 집계

1. 준비물: Zapier MCP 서버 완료 + Google 계정
2. 설정: Zapier MCP 서버 "Configure" 탭 → "+ Add tool" → "Google Sheets" 검색
3. 액션 선택: "Create Spreadsheet Row"(여러 행은 "Create Multiple Spreadsheet Rows"), 읽기 필요 시 "Lookup Spreadsheet Row"도 추가
4. Google 계정 인증 → 대상 시트/워크시트 지정 후 Save
5. 예시 명령: "오늘 리드 3명을 'Leads' 시트에 이름·이메일·날짜로 한 줄씩 추가해줘"
6. 한계: 추가 행은 헤더 바로 아래 삽입, 헤더(컬럼)가 미리 정의돼 있어야 매핑 가능

#### YouTube → 채널 자동 관리

1. 준비물: Zapier MCP 서버 완료 + YouTube(Google) 채널 + (업로드 시) 채널 전화번호 인증 설정
2. 설정: "Configure" 탭 → "+ Add tool" → "YouTube" 검색
3. 액션 선택: Find Video, Upload Video, Update Video Thumbnail, Get Report 등, 계정 인증 후 Save
4. 예시 명령: "내 채널 최근 30일 조회수 리포트 가져오고, 새 영상 'AI 카드뉴스 만들기' 업로드해줘"
5. 한계: 업로드·썸네일은 전화번호 인증 필요, 비공개 분석("Get Report")은 본인 소유 채널만

#### Zoom → 회의록 자동 정리

1. 준비물: Zapier MCP 서버 완료 + Zoom 계정 + (녹화·전사는) Zoom 유료(Pro 이상, 자동 전사 트리거는 Business 이상)
2. 설정: "Configure" 탭 → "+ Add tool" → "Zoom" 검색
3. 액션 선택: Create Meeting, Find Recording and Download, Get Meeting Summary 등, OAuth 인증 후 Save
4. 예시 명령: "내일 3시 '주간 회의' 만들고, 지난 회의 클라우드 녹화 전사본 가져와 요약해줘"
5. 한계: 클라우드 녹화·전사는 Zoom 유료 필수(무료는 로컬녹화라 불가), 본인이 호스트인 미팅만

### 방법 6. 봇 토큰 연결 (Telegram·Discord)

봇을 만들어 토큰을 받고, 그 토큰을 MCP 서버 설정이나 Zapier 연동에 넣는 방식입니다. 토큰은 봇의 열쇠이므로 유출되면 즉시 재발급해야 합니다.

#### Telegram → 나만의 비서

1. 준비물: Telegram 계정 + BotFather 봇 토큰 + MCP/Zapier 설정
2. 봇 생성: Telegram @BotFather → /newbot → 봇 이름·사용자명 입력, 발급된 HTTP API 토큰 복사
3. 연동: 토큰을 텔레그램 MCP 서버 설정 또는 Zapier Telegram 연동에 입력 → Claude 연결
4. 예시 명령: "내 텔레그램 봇으로 '오늘 카드뉴스 업로드 완료' 메시지 보내줘"
5. 한계: 봇과 먼저 대화를 시작한 사용자/봇이 속한 그룹에만 전송 가능, 토큰 유출 시 봇 탈취

#### Discord → 커뮤니티 봇

1. 준비물: Discord 계정 + 관리 권한 서버 + Developer Portal 봇 토큰
2. 봇 생성: Discord Developer Portal → New Application → 이름 입력 → Create → Bot 탭 → Reset Token으로 토큰 발급/복사
3. 봇 초대: Installation 탭 → Guild Install → Scopes에 `bot` 추가 + 권한 지정 → 생성된 Install Link로 봇 초대
4. 연동: 토큰을 MCP/Zapier Discord 연동에 입력
5. 예시 명령: "디스코드 #공지 채널에 '신규 카드뉴스 발행됨' 올려줘"
6. 한계: 초대된 서버·권한 채널만, 토큰 유출 시 재발급 필요, 일부 동작은 Privileged Intents 필요

### 방법 7. 제약 있는 서비스 (Instagram·카카오톡·네이버)

#### Instagram → 계정 분석 (조회만)

1. 준비물: Facebook 페이지에 연결된 인스타 비즈니스/크리에이터 계정 + Windsor.ai 계정
2. 설정: `onboard.windsor.ai` → 데이터 소스 "Instagram Insights" 선택 → Facebook 인증, 인스타 프로필 선택
3. 연동: Claude에서 Windsor.ai 커넥터(MCP) 연결 → 권한 "항상 허용"
4. 예시 명령: "최근 14일간 공유율이 가장 높았던 릴스 알려줘"
5. 한계: 읽기 전용(분석)만, 게시·수정·댓글·DM 불가, 개인 계정 불가, Windsor.ai는 외부 유료 서비스

#### 카카오톡 → 나에게 알림 (메모 API)

내 채팅방으로 메시지를 보내는 것만 필요하다면 방법 8 의 PlayMCP **카카오톡 나챗방** MCP 가 훨씬 간단합니다. 직접 자동화 파이프라인을 만들 때 아래 메모 API 를 씁니다.

1. 준비물: 카카오 계정 + Kakao Developers 앱 + REST API 키 + 카카오 로그인 OAuth(talk_message 동의)
2. 설정: `developers.kakao.com` → 내 애플리케이션 → 애플리케이션 추가 → [요약 정보]에서 앱 키 확인, [카카오 로그인] 활성화 및 Redirect URI 등록, [동의항목]에서 "카카오톡 메시지 전송(talk_message)" 설정
3. 연동: OAuth로 access token 발급 → `POST https://kapi.kakao.com/v2/api/talk/memo/default/send` 호출
4. 예시 명령: "오늘 할 일 요약본을 내 카카오톡으로 보내줘" (자동화는 Make의 Kakao 모듈로)
5. 한계: 나에게 보내기(메모)만 가능, 친구/타인 전송은 별도 심사·승인 필요, 공식 커넥터 없음

#### 네이버 → 일정·메일 (직접 개발 필요)

1. 준비물: 네이버 계정 + Naver Developers 앱 + Client ID/Secret + 네이버 로그인 access token
2. 설정: `developers.naver.com` → Application → 애플리케이션 등록 → 사용 API "네이버 로그인" 선택, 서비스 URL·Callback URL 등록
3. 연동: 발급된 Client ID/Secret 확인, OAuth로 token 발급 후 캘린더 API 직접 호출 / 메일은 IMAP·SMTP 사용
4. 예시 명령: "다음 주 회의를 네이버 캘린더에 추가해줘" (직접 만든 연동 스크립트/MCP 필요)
5. 한계: 원클릭 커넥터·공식 통합 없음, 개발자가 OAuth·API 직접 구현, 메일은 REST API 없어 IMAP/SMTP만, 비개발자는 구글 캘린더 권장

네이버 검색(웹·뉴스·블로그·쇼핑·지식iN·검색 트렌드)만 필요하다면 방법 8 의 **네이버 검색 mcp** 로 개발 없이 해결됩니다.

### 방법 8. 카카오 PlayMCP — 한국형 MCP 마켓

카카오가 운영하는 PlayMCP 마켓플레이스는 한국 시장 특화 MCP 서버를 모아 둔 곳입니다. 글로벌 MCP 로는 접근하기 어려운 한국 데이터(공연·아파트·금감원 공시 등)를 AI 채팅창에서 자연어로 바로 씁니다.

#### MCP 카탈로그 12종

**🎭 문화·여가**

| MCP | 운영자 | 핵심 기능 |
|---|---|---|
| 팝업스토어 MCP | 오덕후 | 지역·브랜드·카테고리별 팝업 필터링 + 후기 |
| ArtBridge | 한태진 | KOPIS 20만+ 공연, 9개 장르 |
| 여기어때 | 여기어때 | 실시간 숙소 검색 + 객실별 상세 |

**🍎 정보·검색**

| MCP | 운영자 | 핵심 기능 |
|---|---|---|
| 애플 탐색기 | Apple | Apple Newsroom + App Store 검색 + 차트 |
| 네이버 검색 mcp | isnow890 | 웹·뉴스·블로그·쇼핑·이미지·지식iN·검색 트렌드 |
| OpenDART | 김다윤 | 금감원 DART API, 한국 상장 114,000+ 기업 공시 |
| 미국 주식 정보 | gino.im | Yahoo Finance 기반 매수·매도·뉴스 |

**🏠 부동산·생활**

| MCP | 운영자 | 핵심 기능 |
|---|---|---|
| 아파트 정보 | Kakao | 지역 단위 아파트 단지 + 가격 |
| 다이소 MCP | hmmhmmhm | 다이소·올리브영·메가박스·CGV·CU·GS25·이마트24·세븐일레븐 매장·재고 |
| 띵동 (택배 추적기) | 신성수 | 실시간 배송 + 세관 + 사기 이력 조회 + URL 안전 검사 |

**🤖 카카오·생산성**

| MCP | 운영자 | 핵심 기능 |
|---|---|---|
| 카카오톡 나챗방 | Kakao | "~라고 나챗방에 보내줘" → 자동 전송 |
| 투두메이트 | todo mate | 할 일 목록·완료·추가·알림·카테고리 |

#### 사용 시작 (3단계)

1. **마켓플레이스 접속**: `https://playmcp.kakao.com/` → 원하는 MCP 선택
2. **MCP 클라이언트에 연결**
   - **Claude Desktop**: 설정 → MCP 서버 추가 → URL 붙여넣기 (방법 2 의 커스텀 커넥터 경로)
   - **카카오 i 오픈빌더**: 자연어로 활성화
3. **자연어로 사용**

```
"관악구 25평 아파트 시세 알려줘" (아파트 정보)
"지난주 코스피 시총 상위 10개 공시 요약" (OpenDART)
"신촌 근처 다이소에 텀블러 있어?" (다이소 MCP)
"내일 명동 갈 거야, 4성급 호텔 추천" (여기어때)
"이번 주말 연극 추천" (ArtBridge)
"내 택배 어디까지 왔어?" (띵동)
```

### 연결 후 공통 점검

1. 채팅창 "+" 메뉴(데스크톱·웹) 또는 `/mcp`(Claude Code)에서 해당 서버가 켜져 있는지 확인합니다.
2. "내 Zapier에 연결된 앱들로 지금 뭘 할 수 있는지 알려줘"처럼 사용 가능한 도구를 물어봐 도구 목록이 나오는지 봅니다.
3. 처음에는 읽기 작업으로 테스트하고, 쓰기·게시 작업은 승인 창을 확인하며 진행합니다.
4. Claude Code 에서는 `/context` 로 MCP 서버별 토큰 사용량을 확인하고, 안 쓰는 서버는 끕니다.

### 트러블슈팅

| 증상 | 확인할 것 |
|---|---|
| 도구가 채팅에서 안 보인다 | 데스크톱은 앱 재시작 후 "+" 에서 토글 ON. 로컬 MCP(방법 4)는 클라이언트를 완전히 종료 후 재시작 |
| 인증 오류 | OAuth 완료 확인 / "Clear authentication" 시도 / 워크스페이스 권한 확인 |
| 원격 MCP 를 지원하지 않는 도구 | `mcp-remote` 브리지 사용 |
| 일부 페이지만 보인다 (Notion) | OAuth 권한 범위 — 인티그레이션이 연결된 페이지만 접근 가능 |
| 도구를 부르지 않고 대답만 한다 | 요청에 서비스 이름·도구 관련 키워드를 넣어 명확히 지시 |
| Gmail 발송·Drive 이동이 안 된다 | 공식 커넥터 한계 — Zapier MCP(방법 5)로 보완 |
| Sheets 행이 엉뚱한 칸에 들어간다 | 헤더(컬럼)가 미리 정의돼 있는지 확인 |
| `npx` 실행 오류 (방법 4) | Node.js v20 이상·npm·git 설치 여부 확인 |
| PlayMCP 결과가 비어 있다 | 공공데이터 기반 MCP 는 사용량 한도로 일시 미조회 가능 — 잠시 뒤 재시도 |

## 활용 예시

1. **업무 보고 자동화**: Notion + Slack 커넥터를 함께 사용해 "주간 회의록을 Notion에 저장하고 주요 결정사항을 Slack #general 채널에 공유해줘"로 업무 효율 증대
2. **콘텐츠 제작 자동화**: Higgsfield 커넥터로 "'AI 활용법' 주제로 30초짜리 홍보 영상 만들어줘"라고 요청하면 Claude가 영상을 생성
3. **데이터 관리**: Google Sheets + Zapier를 연동해 "오늘 접수된 신규 고객 5명의 정보를 '고객 리드' 시트에 자동으로 추가해줘"로 데이터베이스 관리 간소화
4. **카드뉴스 발행 알림**: Canva 커넥터로 "이 카피로 인스타용 카드뉴스 디자인 초안 만들고 PNG로 내보내줘" → 텔레그램 봇으로 "'오늘 카드뉴스 업로드 완료' 메시지 보내줘" → 디스코드 #공지 채널에 "신규 카드뉴스 발행됨" 게시
5. **개발 중 노션 문서 참조**: Claude Code 에 Notion MCP 를 `--scope project` 로 붙여 `.mcp.json` 을 팀과 공유하고, 기획서 페이지를 읽어 구현 작업에 바로 반영

### PlayMCP 조합 활용 예

- **데이트 코스** — ArtBridge(공연) + 여기어때(카페·숙소) + 팝업스토어 통합 추천
- **주식 스크리닝** — OpenDART(재무) + 미국 주식 정보(뉴스) → 조건별 종목 자동 선별
- **부동산 매수** — 아파트 정보 + 네이버 검색(학군) 통합 분석
- **콘텐츠 트렌드 리포트** — 네이버 데이터랩 + 팝업스토어 + Apple → 매주 자동

## 💡 아이디어

- **개인 맞춤형 뉴스레터 생성**: 관심 키워드를 입력하면 Gmail 또는 RSS 피드(Zapier 연동)로 관련 기사를 수집하고 Claude가 요약해 Telegram이나 Email로 보내주는 시스템 구축
- **AI 영상 콘텐츠 제작 파이프라인**: Higgsfield로 영상을 생성하고, YouTube(Zapier)로 직접 업로드하며, Canva로 썸네일을 제작하는 일련의 과정을 Claude에게 맡기는 워크플로우 설계
- **브랜드 일관 디자인**: Canva Brand Kit 을 지정해 두고 SNS 그래픽·프레젠테이션을 같은 폰트·색상으로 반복 생성
- **나만의 생활 비서**: 투두메이트(할 일) + 띵동(택배) + 카카오톡 나챗방(알림)을 묶어 "오늘 할 일과 택배 현황을 나챗방에 보내줘" 한 줄로 아침 브리핑

## 주의사항

### 비용·플랜

- 대부분의 강력한 기능은 Claude 유료 플랜(Pro $20/월 이상) 필요
- Zapier 는 호출 1회당 task 2개가 차감됩니다. 무료 플랜이라도 자주 쓰면 금방 소진됩니다
- Higgsfield 는 생성할 때마다 크레딧이 소모되고, Instagram 분석용 Windsor.ai 는 외부 유료 서비스입니다
- Zoom 클라우드 녹화·전사는 Zoom 유료(Pro 이상, 자동 전사 트리거는 Business 이상), Canva Brand Kit 같은 고급 기능은 Canva Pro 이상이 필요할 수 있습니다

### 보안·권한

- Zapier MCP 서버 URL 은 비밀번호처럼 다뤄야 하며 유출에 주의
- Telegram·Discord 봇 토큰이 유출되면 봇을 탈취당합니다. 유출 즉시 재발급하세요
- AI 가 의도하지 않은 데이터를 수정할 수 있으니 자동 승인("항상 허용") 옵션은 신중히 켜고, 처음엔 특정 페이지/DB 처럼 범위를 좁혀 연결합니다
- 로컬 MCP 서버(Canva `@canva/cli`)는 사용자 기기에서 작동하고 canva.dev 에서 문서 정보만 가져오므로 보안·개인정보 측면에서 유리합니다

### 기능 한계

- Google Sheets·YouTube·Zoom 은 Zapier MCP 서버를 먼저 설정해야 작동
- Notion 은 삭제 불가, 이미지·파일 업로드 미지원(텍스트 콘텐츠만 — 별도 Notion file upload API 필요). 공식 MCP 는 OAuth 필수라 헤드리스 자동화가 어렵습니다
- 일부 서비스(예: Instagram Insights)는 외부 유료 서비스 연동이 필요하거나 특정 계정 유형(비즈니스/크리에이터)만 지원
- 카카오톡 메시지 전송은 공식 커넥터가 없으며, 일반 사용자는 개인 메모(나에게 보내기) 외에 타인에게 메시지를 보내는 것이 사실상 불가능
- MCP 서버가 많을수록 컨텍스트 토큰 비용이 늘어납니다. Claude Code 에서는 `/context` 로 모니터링하세요

### PlayMCP 사용 시

- **사용량 한도** — 일부 MCP 는 공공데이터 기반이라 일시적으로 조회되지 않을 수 있습니다
- **데이터 시점 차** — 실시간이 아닌 데이터인지 확인이 필요합니다
- **공식 인증 X** — Apple 탐색기 등 일부는 개인이 운영합니다
- **개인정보** — 띵동 사기 이력 조회 시 본인 명의 외 조회는 법적 이슈가 있을 수 있습니다
- **카카오톡 나챗방 자동 메시지** — 스팸 주의
- **DART 데이터** — 자동 추출 데이터로 투자 결정을 내릴 때는 사람이 최종 검증해야 합니다

## 출처

- [https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149](https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149)
- [https://developers.notion.com/guides/mcp/get-started-with-mcp](https://developers.notion.com/guides/mcp/get-started-with-mcp)
- [https://abounding-helmet-0e4.notion.site/Claude-Canva-33973c7b15ad81cf8f9cce23a4ae4fe7?pvs=149](https://abounding-helmet-0e4.notion.site/Claude-Canva-33973c7b15ad81cf8f9cce23a4ae4fe7?pvs=149)
- [https://playmcp.kakao.com/](https://playmcp.kakao.com/)

### 합쳐진 원본 문서

이 문서는 아래 5개 문서를 하나로 합쳐 새로 정리한 것입니다.

| 원본 문서 | 원래 슬러그 | 원본 출처 |
|---|---|---|
| 클로드 연동 16가지 | `claude-connectors` | [yongk.notion.site](https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149) |
| 클로드에 16가지 AI 도구 연결하기 | `claude-connectors-for-automation` | [yongk.notion.site](https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149) |
| Claude Code × Notion MCP 연동 | `claude-code-notion-mcp` | [developers.notion.com](https://developers.notion.com/guides/mcp/get-started-with-mcp) |
| Claude x Canva MCP 서버 연동을 통한 AI 디자인 자동화 | `claude-canva-mcp-integration` | [abounding-helmet-0e4.notion.site](https://abounding-helmet-0e4.notion.site/Claude-Canva-33973c7b15ad81cf8f9cce23a4ae4fe7?pvs=149) |
| 카카오 PlayMCP — AI에서 카톡·맵·멜론 연동 | `kakao-playmcp-catalog` | [playmcp.kakao.com](https://playmcp.kakao.com/) |
