---
name: claude-code-notion-mcp
description: Notion 공식 MCP 서버를 Claude Code·Cursor·VS Code·ChatGPT·Codex 등 7+ AI 도구에 연결하는 OAuth 기반 통합 가이드. `/mcp` 명령 한 줄로 노션 워크스페이스에 자연어 읽기·쓰기 권한 부여
origin: content-lab
sources:
  - https://developers.notion.com/guides/mcp/get-started-with-mcp
---

# Claude Code × Notion MCP 연동

## 이게 뭔가요?

**Notion 공식 MCP (Model Context Protocol) 서버 연결 가이드**. 한 번 OAuth 인증하면 AI 도구가 본인 노션 워크스페이스에 사용자 권한 범위 내에서 직접 읽고 쓸 수 있게 됨.

## 지원 AI 도구

| 도구 | 연결 방식 |
|---|---|
| Claude Code | `/mcp` 명령 + OAuth |
| Cursor | `.cursor/mcp.json` 프로젝트 설정 |
| VS Code (Copilot) | Command Palette → MCP: Open User Configuration |
| Claude Desktop | Settings → Connectors |
| ChatGPT | chatgpt.com/#settings/Connectors |
| Codex | `.codex/config.toml` |
| Antigravity | `mcp_config.json` (커스텀 서버 권장) |

## 따라하기

### Claude Code — 가장 간단
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

### Cursor — 프로젝트 공유
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

### 기타 도구 — URL 직접
| Transport | URL | 비고 |
|---|---|---|
| Streamable HTTP (권장) | `https://mcp.notion.com/mcp` | 모던 전송 |
| SSE (레거시) | `https://mcp.notion.com/sse` | 호환용 |

### 트러블슈팅
- **원격 MCP 미지원 도구** → `mcp-remote` 브리지 사용
- **인증 이슈** → OAuth 완료 확인 / "Clear authentication" 시도 / 워크스페이스 권한 확인

## 공식 vs OSS

| 항목 | Notion MCP (공식) | notion-mcp-server (OSS) |
|---|---|---|
| 인증 | OAuth | Bearer Token |
| 유지보수 | 활발 | **중단** |
| API | AI 에이전트 최적화 | v1 JSON API |
| 인프라 | 호스팅됨 | 본인 배포 |
| 권장 대상 | 대부분 사용자 | 헤드리스·자동화 |

## 주의사항

- **Headless 자동화 어려움** — OAuth 필수 (Bearer Token X)
- **이미지·파일 업로드 미지원** — 텍스트 콘텐츠만 (별도 Notion file upload API)
- **OAuth 권한 범위** — 인티그레이션이 연결된 페이지만 접근
- **AI가 의도 외 데이터 수정 가능** — 자동 승인 옵션 신중히
- **컨텍스트 토큰 비용** — `/context`로 모니터링

## 출처
- [Notion MCP 공식 가이드](https://developers.notion.com/guides/mcp/get-started-with-mcp)
