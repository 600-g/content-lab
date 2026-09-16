---
name: agency-agents-seven-orchestrator
description: GitHub 저장소 **agency-agents** 에 든 264개 AI 에이전트 md 파일 중 **지휘자 1명 + 실무자 6명**만 골라 Claude Code 에 설치하고, 목표 한 줄로 나머지를 자동 호출하게 만드는 스킬입니다.
origin: content-lab
grade: S
difficulty: 중급
category: 자동화
ai_tools: ["Claude", "Claude Code", "Cursor", "Codex", "Gemini"]
sources:
  - https://wandering-mile-86e.notion.site/AI-264-3db98dec8eed819ebfa8ed6359d56248?pvs=149
---

# AI 에이전트 7명 설치하기

💡 GitHub 저장소 **agency-agents** 에 든 264개 AI 에이전트 md 파일 중 **지휘자 1명 + 실무자 6명**만 골라 Claude Code 에 설치하고, 목표 한 줄로 나머지를 자동 호출하게 만드는 스킬입니다.

## 이게 뭔가요?

GitHub 에 **agency-agents** 라는 저장소(별 15만 개, MIT 라이선스)가 있습니다. 회사 일에 써도 되는 오픈소스입니다. 이 저장소 안에는 AI 직원이 264명 들어 있는데, 직원 한 명 = 마크다운 파일 하나입니다. 파일에는 이름·성격·일하는 순서가 적혀 있고, 이 파일을 Claude Code 같은 AI 코딩 도구에 붙이면 그 역할대로 일하는 "에이전트"가 됩니다.

문제는 264명을 다 깔면 매번 "이번엔 누굴 부르지"를 내가 직접 골라야 해서 느려진다는 점입니다. 그래서 딱 **일곱 명만** 고릅니다. 그중 한 명(지휘자, agents-orchestrator)에게 나머지 여섯 명을 맡기면, 내가 여섯 명을 하나씩 부르는 대신 지휘자 한 명에게만 목표를 말하면 됩니다.

흐름을 그림으로 보면 이렇습니다.

```
flowchart TD
ME["나<br/>목표 한 줄만 적는다"] --> O["agents-orchestrator<br/>«비서실장» · 7번째"]
O --> A["Frontend Developer<br/>화면을 만든다"]
O --> B["UI Designer<br/>색·글자·부품 규칙"]
O --> C["Reality Checker<br/>증거 없으면 «아직 아님»"]
O --> D["AI Code Auditor<br/>비밀키·뚫린 구멍 찾기"]
O --> E["Reddit Community Builder<br/>손님 모인 곳에 글"]
O --> F["Ad Creative Strategist<br/>광고 문구 쓰고 시험"]
```

핵심은 화살표 방향입니다. 264명 중 일곱만 깔면 되고, 그 일곱 중에서도 먼저 깔 것은 지휘자입니다. 저장소·설치 스크립트·앱 전부 무료입니다. ✅ 무료 대안: 이 스킬 전체가 추가 결제 없이 GitHub 저장소만으로 완결됩니다. Claude Code 외에 Cursor·Codex·Gemini CLI·Copilot 에도 붙일 수 있습니다.

## 따라하기

### 1. 일곱 명 — 파일 위치 확인

| 순서 | 하는 일 | 이름 | 파일 위치 |
|---|---|---|---|
| 1 | 부린다 — 목표 하나를 받아 나머지를 지휘 | Agents Orchestrator | `specialized/agents-orchestrator.md` |
| 2 | 만든다 — 눌러 볼 수 있는 화면 | Frontend Developer | `engineering/engineering-frontend-developer.md` |
| 3 | 만든다 — 색·글자·부품 규칙 | UI Designer | `design/design-ui-designer.md` |
| 4 | 지킨다 — 증거 없으면 「아직 아님」 | Reality Checker | `testing/testing-reality-checker.md` |
| 5 | 지킨다 — 박힌 비밀키·뚫린 구멍 찾기 | AI-Generated Code Security Auditor | `security/security-ai-generated-code-auditor.md` |
| 6 | 알린다 — 손님이 모인 게시판에 글 | Reddit Community Builder | `marketing/marketing-reddit-community-builder.md` |
| 7 | 알린다 — 광고 문구 쓰고 시험 | Ad Creative Strategist | `paid-media/paid-media-creative-strategist.md` |

1번부터 까세요. 지휘자가 있어야 나머지 여섯이 "내가 부르는 직원"이 아니라 "알아서 불려 오는 직원"이 됩니다.

### 2. 설치 — 세 가지 길 중 하나 선택

**길 1 · 앱에서 클릭 (제일 쉬움)**

Agency Agents 앱을 받습니다 → https://github.com/msitarzewski/agency-agents-app/releases/latest (맥 13 이상 · 윈도 x64/ARM64 · 리눅스 x86_64 전부 지원)

맥은 터미널에서도 설치됩니다.

```
brew tap msitarzewski/agency-agents
brew install --cask agency-agents
```

앱을 열고 왼쪽 **Tools** 에서 Claude Code 가 잡혀 있는지 확인합니다. (Cursor · Codex · Gemini CLI · Copilot 도 지원)

왼쪽 **Agents** 에서 위 표의 이름을 검색 → 오른쪽 상세 패널에서 파일 내용을 읽고 → **Install** 을 누릅니다. Global 로 깔면 모든 프로젝트에서, Project 로 깔면 그 폴더에서만 불립니다. 표 순서대로 일곱 번 반복하면 끝입니다. 앱이 파일을 알아서 최신으로 맞춰 줍니다.

**길 2 · 저장소를 받아 스크립트로 (전체 설치)**

```
git clone https://github.com/msitarzewski/agency-agents.git
cd agency-agents
./scripts/install.sh --tool claude-code
```

이 명령은 264명 전부를 까는 것이라, 일곱만 두려면 아래 "길 3"처럼 파일을 골라 복사하는 편이 낫습니다.

**길 3 · 파일 일곱 개만 손으로 복사**

Claude Code 는 `~/.claude/agents/` 폴더의 md 파일을 직원으로 씁니다. 위 표의 파일 일곱 개만 그 폴더에 넣으면 됩니다.

```
# 저장소를 받은 폴더 안에서
mkdir -p ~/.claude/agents
cp specialized/agents-orchestrator.md \
engineering/engineering-frontend-developer.md \
design/design-ui-designer.md \
testing/testing-reality-checker.md \
security/security-ai-generated-code-auditor.md \
marketing/marketing-reddit-community-builder.md \
paid-media/paid-media-creative-strategist.md \
~/.claude/agents/
```

윈도 PowerShell 이면 `~/.claude/agents/` 대신 `$env:USERPROFILE\.claude\agents\` 를 씁니다.

### 3. 지휘자에게 목표 문장 던지기

Claude Code 를 열고 목표를 한 줄로 씁니다. 문장 안에 직원 이름을 넣으면 그 직원이 불려 옵니다. (아래 "활용 예시" 참고)

## 활용 예시

### 예시 1 · 작은 웹앱 만들기

```
agents-orchestrator 를 써서 「오늘 할 일을 적고 지우는 웹앱」을 기획부터 배포 직전까지 만들어 줘. 화면은 frontend-developer 와 ui-designer, 검사는 reality-checker 와 ai-generated-code-auditor 에게 맡겨.
```

→ 지휘자가 화면 제작은 Frontend Developer·UI Designer 에게, 검증은 Reality Checker·AI Code Auditor 에게 자동으로 분배합니다.

### 예시 2 · 이미 있는 코드 손보기

```
agents-orchestrator 를 써서 이 저장소의 로그인 화면을 고쳐 줘. 고치기 전에 ai-generated-code-auditor 가 비밀키·권한 구멍을 먼저 보고, 끝나면 reality-checker 가 증거를 달아 판정해.
```

→ 수정 전 보안 감사 → 수정 → 증거 기반 검증까지 순서대로 자동 진행됩니다.

### 예시 3 · 만든 걸 알리기

```
agents-orchestrator 를 써서 이 앱을 알릴 준비를 해 줘. reddit-community-builder 는 어느 게시판에 무슨 글을 올릴지, ad-creative-strategist 는 광고 문구 세 벌을 써.
```

→ 커뮤니티 홍보 글 초안과 광고 카피 3종이 동시에 나옵니다.

## 주의사항

- 목표는 한 줄, 결과물은 하나로 적습니다. 두 개를 시키면 지휘자도 헷갈립니다.
- Reality Checker 가 "아직 아님"이라고 답하면 실패가 아니라 검사관이 정상적으로 일한 겁니다. 증거를 채우라는 신호입니다.
- 일곱으로 부족해지면 그때 264명 중 한 명씩 더 깝니다. 처음부터 다 깔지 않습니다.

## 출처

[AI 직원 264명 중 일곱만 뽑기 — 파일 위치 · 설치 순서 · 목표 문장](https://wandering-mile-86e.notion.site/AI-264-3db98dec8eed819ebfa8ed6359d56248?pvs=149)

## 출처

- [https://wandering-mile-86e.notion.site/AI-264-3db98dec8eed819ebfa8ed6359d56248?pvs=149](https://wandering-mile-86e.notion.site/AI-264-3db98dec8eed819ebfa8ed6359d56248?pvs=149)
