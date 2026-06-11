💡 이 스킬은 **Notion 공식 MCP 서버 연결 가이드**로, **Claude Code·Cursor·VS Code·ChatGPT·Codex** 등 7+ AI 도구에서 노션 워크스페이스에 자연어로 읽기·쓰기 권한을 부여하는 OAuth 기반 통합 패턴입니다.

## 이게 뭔가요?

**Notion 공식 MCP (Model Context Protocol) 서버 연결 가이드**. 한 번 OAuth 인증하면 AI 도구가 본인 노션 워크스페이스에 **사용자 권한 범위 내에서 직접 읽고 쓸 수 있게** 됨.

**MCP 가 뭔가요**:
- **Model Context Protocol** — AI 와 외부 서비스를 연결하는 표준 프로토콜
- 별도의 코드 작성 없이 노션을 **AI 의 외부 메모리·작업 공간** 으로 활용
- 한 번 연결하면 **모든 노션 작업을 자연어로** 지시 가능

**지원 AI 도구 (공식 가이드 제공)**:

| AI 도구 | 연결 방식 |
|---|---|
| **Claude Code** | `/mcp` 명령 + OAuth |
| **Cursor** | `.cursor/mcp.json` 프로젝트 설정 |
| **VS Code (GitHub Copilot)** | Command Palette → MCP: Open User Configuration |
| **Claude Desktop** | Settings → Connectors |
| **Windsurf** | 자체 가이드 |
| **ChatGPT** | chatgpt.com/#settings/Connectors |
| **Codex** | `.codex/config.toml` |
| **Antigravity** | `mcp_config.json` (커스텀 서버 권장) |

💰 유료 필요: Claude Desktop 은 Pro·Max·Team·Enterprise 만 사용 가능. ChatGPT 는 Plus 이상.
✅ 무료 대안: 오픈소스 `notion-mcp-server` (현재 유지보수 X) + Notion API 토큰

## 따라하기

### Claude Code 연결 (가장 간단)

```bash
/mcp
# OAuth 플로우 따라가면 끝
```

**Scope 옵션** (`--scope` 플래그):

| Scope | 범위 |
|---|---|
| **`--scope local`** (기본값) | 현재 프로젝트에서만 사용자 본인 |
| **`--scope project`** | 팀과 `.mcp.json` 파일로 공유 |
| **`--scope user`** | 모든 프로젝트에서 사용자 본인 |

**관리 명령어**:

```bash
/mcp        # 설치된 MCP 서버 목록 + 관리
/context    # 현재 세션 컨텍스트 토큰 사용량 + MCP 서버별 토큰
```

### Cursor 연결 (프로젝트 공유)

팀과 설정 공유하려면 프로젝트 루트에 `.cursor/mcp.json`:

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

### VS Code (Copilot) — User-level

**Command Palette** → `MCP: Open User Configuration` → 서버 설정 추가.

### Claude Desktop — Connectors

**Settings → Connectors** 에서 추가. `claude_desktop_config.json` 사용 X (Pro·Max·Team·Enterprise 만 가능).

### ChatGPT — Connectors

[chatgpt.com/#settings/Connectors](https://chatgpt.com/#settings/Connectors) 접속 (로그인 필요).

### Codex — Project-level

`.codex/config.toml` 에 서버 설정 추가 (Cursor 와 동일 형식).

### Antigravity — 커스텀 서버 권장

Antigravity MCP 갤러리의 사전 설정된 "Notion" 커넥터는 **deprecated `notion-mcp-server` 패키지** 사용. 커스텀 MCP 서버로 직접 연결 권장.

### 기타 도구 — URL 직접 사용

목록에 없는 도구도 MCP 지원하면 다음 URL 사용 가능:

| Transport | URL | 비고 |
|---|---|---|
| **Streamable HTTP** (권장) | `https://mcp.notion.com/mcp` | 모던 전송, 광범위 지원 |
| **SSE** (Server-Sent Events) | `https://mcp.notion.com/sse` | 레거시 호환 |

### Notion 앱에서 직접 연결 (대안)

AI 도구 직접 설정 대신 **Notion 안에서 연결 시작** 가능.

### 트러블슈팅

**도구가 원격 MCP 서버 미지원** — `mcp-remote` 브리지 사용:

```
일부 MCP 클라이언트는 로컬 stdio 서버만 지원.
mcp-remote 브리지로 Notion MCP 연결 가능.
최후의 수단: 오픈소스 MCP 서버 로컬 실행 (유지보수 X).
```

**인증 이슈**:
- OAuth 플로우 완료 확인
- 도구의 MCP 설정에서 "Clear authentication" 또는 "Disconnect" 시도
- Notion 워크스페이스 권한 확인

### Notion MCP vs 오픈소스 `notion-mcp-server`

| 항목 | Notion MCP (공식) | notion-mcp-server (OSS) |
|---|---|---|
| **인증** | OAuth | Bearer Token |
| **유지보수** | 활발히 유지 | **유지보수 중단** |
| **API** | AI 에이전트 최적화 도구 | v1 JSON API |
| **인프라** | 호스팅됨 (설정 불필요) | **본인이 배포 관리** |
| **권장 대상** | 대부분 사용자 | 헤드리스·자동화 워크플로우 |

💡 **대부분 사용자**: 공식 Notion MCP 권장.

## 활용 예시

- **개인 — 노션을 외부 두뇌화** — Claude Code 에 `/mcp` → "오늘 일정 정리해서 노션 저장" 같은 자연어 명령. 노션 페이지 직접 클릭 0회
- **개발팀 — 프로젝트 노션 자동 동기화** — `.cursor/mcp.json` 으로 팀원 모두 동일 설정 공유. PR 메인 머지 시 자동 노션 페이지 업데이트
- **PM — 회의 후속 액션 자동화** — 슬랙 미팅 록 → Claude 가 노션 페이지에 액션 아이템 자동 정리. 회의록 정리 시간 80% 절감
- **컨설턴트 — 클라이언트별 노션 워크스페이스 통합 관리** — `--scope local` 로 클라이언트별 별도 OAuth → 컨텍스트 격리. 1인이 10+ 클라이언트
- **콘텐츠 크리에이터** — 아이디어 캡처 → 노션 → AI 자동 정리·태깅·연관 콘텐츠 추천
- **연구자·작가** — Notion 의 모든 노트를 AI 의 RAG 베이스로 활용. "내 노트 중에 X 주제 관련된 것 정리해줘"
- **HR / 팀 리더** — 신입 온보딩 시 노션 가이드를 AI 가 자연어로 안내. 1:1 가이드 부담 감소

## 💡 아이디어

- **Notion MCP 자동 백업 봇** — 노션 워크스페이스 일일 자동 백업 + 변경 알림 → 월 $5
- **다중 AI 도구 통합 대시보드** — Claude·Cursor·ChatGPT 모두에서 같은 노션 데이터 접근 → 통합 모니터링 SaaS
- **노션 + AI 강의 콘텐츠** — Notion MCP 활용법 4시간 강의 패키지 → $100-200
- **사내 노션 표준화 컨설팅** — 회사 노션 워크스페이스 + AI 도구 연동 설계 컨설팅 → $1,000-3,000/회
- **Headless 자동화용 OSS MCP 호스팅 SaaS** — 유지보수 중단된 OSS MCP 를 활발히 유지하는 호스팅 서비스 → 월 $20
- **노션 변경 이력 자동 분석** — AI 가 워크스페이스 변경 패턴 분석 → "이 페이지 자주 수정됨, 정리 권장" 인사이트 제공

## 주의사항

- **Headless 자동화 어려움** — Notion MCP 는 **OAuth 필수 (Bearer Token X)**. 사용자 손이 가지 않는 완전 자동화는 별도 OSS 솔루션 필요
- **이미지·파일 업로드 미지원** — 현재 Notion MCP 는 텍스트 콘텐츠만. 이미지·파일은 별도 [Notion file upload API](https://developers.notion.com/docs/working-with-files) 사용
- **OAuth 권한 범위 — Connections 권한 점검** — 인티그레이션이 연결된 페이지만 접근 가능. 새 페이지 추가 시 Connection 확인 필요
- **공식 vs OSS — 둘 다 유지 비추천 영역** — `notion-mcp-server` 유지보수 중단, 공식만 권장
- **AI 가 의도 외 데이터 수정 가능** — MCP 는 강력. **수행 작업 사전 검토 권장**. 자동 승인 옵션 켜기 신중히
- **컨텍스트 토큰 비용** — Notion MCP 활성화 시 매 세션 토큰 일부 소비. `/context` 로 모니터링 권장
- **Notion 워크스페이스 권한** — 본인의 노션 권한 범위 내에서만 작동. 다른 팀원 워크스페이스 접근 X

## 출처

- [Connecting to Notion MCP — Notion Docs](https://developers.notion.com/guides/mcp/get-started-with-mcp)
- 전체 문서 인덱스: [https://developers.notion.com/llms.txt](https://developers.notion.com/llms.txt)
