---
name: ai-dev-environment-migration-codex
description: 이 스킬은 [Claude Code의 AI 개발 환경을] [OpenAI Codex로 효율적으로 이관하여 고급 기능을 활용]한다. Use when: ['- 기존 Claude Code 환경을 더 강력한 OpenAI Codex로 업그레이드할 때', '- AI 에이전트의 맞춤형 설정, 스킬, 서브 에이전트 등을 새 개발 환경으로 그대로 가져가고 싶을 때', '- 백그라운드 클라우드 작업, 병렬 실행, 모바일 지시, AI 코드 리뷰 등 Codex의 고급 코딩 기능을 활용하고자 할 때']
origin: content-lab
metadata:
  template_version: "v1"
  category: "개발"
  grade: "A"
  difficulty: "중급"
  targets: ["공통", "클로드코드"]
  ai_tools: ["Claude Code", "Codex", "GPT"]
  tags: ["CLI", "Tool Use", "자동화"]
  source_urls:
    - "https://abounding-helmet-0e4.notion.site/Claude-Code-Codex-35873c7b15ad81fa95a4d608d35164a3?pvs=149"
  source_type: "notion"
  collected_at: "2026-05-15"
  last_updated_at: "2026-05-15"
  merge_count: 1
---

# 📦 AI 개발 환경 (Claude Code → Codex) 마이그레이션

> **TL;DR** — 이 스킬은 [Claude Code의 AI 개발 환경을] [OpenAI Codex로 효율적으로 이관하여 고급 기능을 활용]한다.

> **메타** 등급 A · 카테고리 개발 · 난이도 중급
> **도구** Claude Code, Codex, GPT
> **적용 대상** 공통, 클로드코드

---

## 🎯 When to use (언제 쓰는가)

['- 기존 Claude Code 환경을 더 강력한 OpenAI Codex로 업그레이드할 때', '- AI 에이전트의 맞춤형 설정, 스킬, 서브 에이전트 등을 새 개발 환경으로 그대로 가져가고 싶을 때', '- 백그라운드 클라우드 작업, 병렬 실행, 모바일 지시, AI 코드 리뷰 등 Codex의 고급 코딩 기능을 활용하고자 할 때']

## 🔑 How it works (작동 원리)

OpenAI Codex의 '다른 에이전트 설정 가져오기' 기능을 활용하여 Claude Code의 설정 파일(CLAUDE.md, settings.json, Skills, Slash commands, Subagents, MCP server config, Hooks, 최근 세션 등)을 Codex 환경에 맞게 자동으로 변환하여 이주합니다. 이 과정에서 사용자의 맞춤형 AI 작업 규칙, 개인기(스킬), 보조 AI 비서(서브 에이전트) 등이 모두 새 환경으로 옮겨집니다.

## 🛠 Steps (적용 단계)

['1) Codex 앱을 실행하고 좌측 하단 Settings(설정) 메뉴로 이동합니다.', '2) General(일반) 페이지에서 [Import other agent setup(다른 에이전트 설정 가져오기)] 메뉴를 찾습니다.', '3) Import (또는 Import again) 버튼을 클릭합니다.', '4) 가져오고 싶은 항목(Instruction files, Skills, Subagents 등)을 선택한 뒤 실행합니다.', '5) 마이그레이션 완료 후 [View imported files]를 눌러 설정이 잘 들어왔는지 확인하고, 필요한 경우 AI의 도움을 받아 복잡한 설정을 마무리합니다.']

## 💡 Examples (예시)

```
| Claude Code 기존 항목       | OpenAI Codex 이동 결과 | 📝 쉬운 설명 (어떤 역할인가요?)             |
| :-------------------------- | :--------------------- | :------------------------------------------ |
| Instruction files (CLAUDE.md 등) | AGENTS.md              | AI에게 미리 알려주는 '나만의 작업 규칙과 배경지식' |
| Skills                      | Codex skills           | AI가 수행할 수 있는 구체적인 '개인기(기능)' |
| Subagents                   | Codex agents           | 특정 업무만 전담해서 처리하는 '보조 AI 비서' |
| 최근 30일 세션              | Threads / Projects     | 최근 한 달 동안 AI와 대화하고 작업했던 모든 기록 |
```

## 🏢 두근 환경 적용

["원본이 ChatGPT Plus 사용자 대상이지만, 두근컴퍼니는 'GitHub Copilot → Claude Code 또는 Codex CLI'와 같이 Codex CLI를 대안으로 고려하고 있으므로, Codex CLI 환경에서 유사한 마이그레이션 기능이 제공되는지 확인하여 활용할 수 있습니다.", '두근펫: Electron 데스크톱 앱 개발 시, 기존 Claude Code 환경에서 설정했던 개발 스킬(예: UI 컴포넌트 생성, 버그 수정 스킬) 및 서브 에이전트(예: Electron 빌드 전담)를 Codex CLI 환경으로 옮겨와 개발 효율을 높일 수 있습니다.', '클로드코드: 기존 Claude Code (CLI)에서 사용하던 AGENTS.md, 스킬, MCP 설정 등을 Codex CLI로 옮기는 데 이 가이드를 활용하여 효율적인 작업 환경 전환을 꾀할 수 있습니다.']

## ⚠️ Caveats (주의사항)

['- OpenAI Codex는 ChatGPT Plus, Pro, Business, Enterprise 사용자에게 제공되므로, 두근컴퍼니는 OpenAI의 유료 구독이 필요하거나 Codex CLI의 무료/유료 정책을 별도로 확인해야 합니다.', '- 자동 변환이 어려운 일부 복잡한 설정은 AI의 직접적인 도움을 받아야 할 수 있습니다.', '- 이주 후에도 AI 비서 권한, 외부 도구 연결 보안, Hooks 작동 여부, 플러그인 호환성 등 필수 점검 체크리스트를 확인해야 합니다.']

## 📎 Sources (출처)

- [https://abounding-helmet-0e4.notion.site/Claude-Code-Codex-35873c7b15ad81fa95a4d608d35164a3?pvs=149](https://abounding-helmet-0e4.notion.site/Claude-Code-Codex-35873c7b15ad81fa95a4d608d35164a3?pvs=149)

---

## 메타 정보

- 최초 수집: 2026-05-15
- 마지막 갱신: 2026-05-15
- 합병 횟수: 1회
- 템플릿: v1 (TEMPLATE.md)
- 자동 생성: 두근컴퍼니 콘텐츠랩 v4.0
