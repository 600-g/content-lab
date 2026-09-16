---
name: prompts-chat-mcp-connect
description: **prompts.chat**(프롬프트 2,000개·스킬 68개·워크플로우 13개가 모인 무료 오픈소스 프롬프트 플랫폼)을 **클로드·GPT·제미나이·커서** 등 내가 쓰는 AI 도구에 **MCP**로 연결해서, "블로그 초안 프롬프트 찾아줘"처럼 말만 해도 AI가 알아서 프롬프트를 검색·적용하게 만드는 스킬입니다.
origin: content-lab
grade: S
difficulty: 중급
category: 프롬프트
ai_tools: ["Claude", "Claude Code", "GPT", "Codex", "Gemini"]
sources:
  - https://fieldby.notion.site/2-000-GPT-3d7d730b395381bb8f58fcbc532bb3e2?pvs=149
---

# 프롬프트닷챗 MCP로 연결

💡 **prompts.chat**(프롬프트 2,000개·스킬 68개·워크플로우 13개가 모인 무료 오픈소스 프롬프트 플랫폼)을 **클로드·GPT·제미나이·커서** 등 내가 쓰는 AI 도구에 **MCP**로 연결해서, "블로그 초안 프롬프트 찾아줘"처럼 말만 해도 AI가 알아서 프롬프트를 검색·적용하게 만드는 스킬입니다.

## 이게 뭔가요?

prompts.chat(프롬프트닷챗)은 프롬프트 2,000개, 스킬 68개, 워크플로우 13개가 모인 무료 오픈소스 프롬프트 플랫폼입니다. 이 자체를 MCP(Model Context Protocol) 서버로 열어 두고 있어서, 내가 쓰는 AI 도구에 주소 하나만 등록하면 그때부터 "~프롬프트 찾아줘"라는 말 한마디로 AI가 직접 검색·적용까지 해줍니다. 복사해서 붙여 넣는 과정 자체가 사라지는 게 핵심입니다.

도구별 지원 현황은 아래와 같습니다.

| 도구 | 채팅 앱 | 터미널(CLI) |
|---|---|---|
| 클로드 | ✅ 주소만 붙여넣기 (무료 계정도 1개까지) | ✅ 클로드 코드, 명령 두 줄 |
| GPT | 💰 유료 필요: 챗GPT 웹은 Plus 이상 | ✅ 코덱스, 명령 한 줄 (챗GPT 유료 계정) |
| 제미나이 | ❌ 개인용 제미나이 앱은 연결 메뉴 없음 | ✅ 무료 대안: 제미나이 CLI, 개인 구글 계정 무료 |

💰 유료 필요: 챗GPT 웹에서 커넥터를 쓰려면 Plus·Pro·Business 이상이어야 합니다. ✅ 무료 대안: 코덱스(터미널)는 챗GPT 유료 계정만 있으면 되고, 아예 무료로 쓰려면 prompts.chat 사이트에서 직접 복붙하는 방식도 남아 있습니다.

## 따라하기

### 1. 클로드 앱 — 채팅에서 주소만 붙여넣기 (가장 쉬움)

1. 왼쪽 아래 내 프로필 → **설정(Customize)** → **커넥터(Connectors)**로 들어갑니다.
2. 커넥터 옆 **+** 버튼을 누르고 **커스텀 커넥터 추가(Add custom connector)**를 선택합니다.
3. 이름은 `prompts.chat`, 주소 칸에 아래를 붙여넣고 추가(Add)를 누릅니다. 고급 설정은 비워 둡니다.

```
https://prompts.chat/api/mcp
```

4. 대화창 왼쪽 아래 **+** 버튼 → 커넥터에서 prompts.chat을 켭니다. 그다음 "블로그 초안 프롬프트 찾아줘"라고 말하면 검색해 옵니다.

무료 계정도 직접 추가하는 커넥터를 1개까지 둘 수 있으므로 prompts.chat 하나만 붙일 거면 무료로 충분합니다. Pro·Max는 개수 제한이 없습니다.

### 2. 클로드 코드 — 플러그인 두 줄 (검색 명령까지 생김)

클로드 코드를 켠 뒤 채팅창에 아래 두 줄을 차례로 입력합니다.

```
/plugin marketplace add f/prompts.chat
/plugin install prompts.chat@prompts.chat
```

설치가 끝나면 이렇게 검색합니다. 검색어는 영어가 잘 잡힙니다.

```
/prompts.chat:prompts code review
/prompts.chat:prompts blog post --category writing
/prompts.chat:skills documentation
```

팁: 플러그인 없이 MCP만 붙이고 싶으면 터미널에서 이 한 줄이면 됩니다.

```
claude mcp add --transport http prompts-chat https://prompts.chat/api/mcp
```

### 3. GPT — 챗GPT 웹(개발자 모드) 또는 코덱스

**챗GPT 웹(💰 Plus 이상 유료)**

1. 설정 → 앱(또는 플러그인) → 고급 설정으로 들어갑니다.
2. **개발자 모드(Developer mode)**를 켭니다. Plus·Pro·Business 등 유료 플랜에서만 보입니다.
3. 커스텀 커넥터 추가를 누르고 주소 칸에 아래를 붙여넣습니다.

```
https://prompts.chat/api/mcp
```

4. 그 아래 '인증' 칸은 **OAuth가 아니라 '인증 없음'**을 골라야 합니다. (OAuth로 두면 `does not implement OAuth` 오류가 납니다.)
5. 대화창에서 그 커넥터를 켜고 "프롬프트 검색해 줘"라고 말하면 됩니다.

✅ 무료 대안: 무료 플랜은 개발자 모드가 없으므로 prompts.chat 사이트에서 골라 복붙하는 방식을 쓰면 됩니다.

**코덱스(터미널, 챗GPT 유료 계정으로 로그인)**

```
codex mcp add prompts-chat --url https://prompts.chat/api/mcp
```

이후 코덱스 안에서 "이미지 생성 프롬프트 찾아줘"처럼 말하면 알아서 검색해 옵니다. 설정은 `~/.codex/config.toml`에 저장되고 코덱스 앱·CLI·IDE 확장이 같이 씁니다. 어떤 모델을 쓰든 상관없습니다.

### 4. 제미나이 CLI — 개인 구글 계정으로 무료

개인용 제미나이 앱(브라우저·폰)에는 MCP 연결 메뉴가 없습니다. 회사용(Gemini Business·Enterprise)만 관리자가 붙일 수 있고, 개인은 CLI로 가면 됩니다. 결제나 API 키는 필요 없습니다.

1. 설치

```
brew install gemini-cli
```

홈브루가 없으면 `npm install -g @google/gemini-cli`

2. 켜고 로그인 — `gemini`라고 치면 'Sign in with Google'이 뜹니다. 평소 쓰는 개인 구글 계정으로 로그인하면 끝입니다.

```
gemini
```

3. prompts.chat 연결

```
gemini mcp add --transport http prompts-chat https://prompts.chat/api/mcp
```

4. 쓰기 — 다시 `gemini`를 켜고 "블로그 초안 프롬프트 찾아줘"라고 말하면 검색해 옵니다.

✅ 무료 한도: 개인 구글 계정은 1분에 60번, 하루 1,000번까지 가능합니다. 기본 모델은 제미나이 3 계열입니다.

### 5. 커서·윈드서프·VS Code — 설정 파일에 붙여넣기

각 도구의 MCP 설정 파일(커서는 `~/.cursor/mcp.json`)에 아래 내용을 넣습니다.

```json
{
  "mcpServers": {
    "prompts.chat": {
      "url": "https://prompts.chat/api/mcp"
    }
  }
}
```

로컬에서 돌리고 싶으면 `url` 대신 `command`를 씁니다.

```
npx -y prompts.chat mcp
```

### 6. 스킬로 꽂아 쓰기 (반복 작업용)

스킬은 SKILL.md 파일이 든 폴더입니다. 68개를 전부 받을 필요 없이, 앱 고르듯 쓸 것만 하나씩 골라 넣으면 됩니다.

1. 마음에 드는 스킬 페이지에서 폴더(SKILL.md + 부속 파일)를 내려받습니다.
2. 클로드 코드는 `~/.claude/skills/` 안에, 코덱스는 `~/.codex/skills/` 안에 폴더째 넣습니다.
3. 도구를 다시 켜면 관련 작업을 시킬 때 스킬이 자동으로 켜집니다.

팁: 클로드 코드 플러그인을 깔았다면 사이트에 안 가도 됩니다. 클로드 코드 안에서 `/prompts.chat:skills 검색어`라고 치면 스킬을 바로 찾아 가져옵니다.

참고로 워크플로우(프롬프트 여러 개를 순서대로 묶은 13개 묶음)는 연결로 불러오는 게 아니라 사이트에서 보고 복사해 쓰는 방식이라 참고용입니다.

## 활용 예시

**① 검색해서 골라 쓰기 (제일 기본)**
"prompts.chat에서 링크드인 자기소개 프롬프트 찾아줘"라고 말하면 → AI가 prompts.chat에 검색을 보내고 제목·설명이 붙은 후보 몇 개를 보여줍니다. 예: 'LinkedIn About Section Writer — 3 Professional Styles'. "2번으로 해줘"라고 고르면 → AI가 그 프롬프트 전문을 가져와 바로 그 역할로 변신합니다. 이제 "나는 콘텐츠 마케터 5년 차야, 자기소개 써줘"라고 내 내용만 던지면 → 그 프롬프트 방식대로 결과가 나옵니다.

**② 작업만 시키면 알아서 꺼내 쓰기 (터미널 에이전트)**
클로드 코드·코덱스·제미나이 CLI에서는 "이 블로그 글 초안 잡아줘"라고만 시켜도 → 에이전트가 필요하다고 판단할 때 prompts.chat에서 맞는 프롬프트를 스스로 검색해 쓰고 결과만 줍니다. 꼭 쓰게 하고 싶으면 "prompts.chat 프롬프트 참고해서"라고 한마디 붙이면 확실해집니다.

**③ 검색 팁**
"이미지 생성용으로만 찾아줘"처럼 종류(TEXT/IMAGE/SKILL)를 지정할 수 있습니다. 영어 단어로 검색하는 게 잘 잡히고('copywriter', 'translator', 'midjourney'), 'instagram caption'이 1건뿐이면 'social media', 'copywriting'처럼 단어를 넓혀보면 됩니다.

**프롬프트 구조 예시** — prompts.chat에 등록된 프롬프트는 대부분 '역할 + 할 일 + 빈칸' 구조입니다.

```
You are an expert in ${learning_topic}, a long-term tutor, practical coach, and knowledge-system designer. I have already clarified my learning goals, scope, target depth, and resources. Your task is to guide me through a complete...
```

`${learning_topic}` 같은 빈칸이 있으면 AI가 "어떤 주제요?"라고 묻거나 내가 말한 내용으로 알아서 채우므로, 한 프롬프트를 여러 주제에 돌려 쓸 수 있습니다.

## 💡 아이디어

프롬프트 데이터는 CC0(저작권 포기)라 자유롭게 쓸 수 있고, 사내용 비공개 prompts.chat은 아래 한 줄로 직접 띄울 수 있습니다.

```
npx prompts.chat new my-prompt-library
```

## 주의사항

- 챗GPT 웹은 무료 플랜에 개발자 모드가 아예 없어 커넥터 연결이 불가능합니다. Plus 이상만 가능합니다.
- 챗GPT 웹 인증 설정에서 OAuth를 선택하면 `does not implement OAuth` 오류가 나므로 반드시 '인증 없음'을 골라야 합니다.
- 검색은 제목·본문의 단어를 맞추는 방식이라 한국어나 '멋진 글'처럼 두루뭉술한 표현은 잘 안 잡힙니다. 영어 키워드로 검색하세요.
- 제미나이 CLI 무료 한도는 1분에 60번, 하루 1,000번입니다.
- 연결했는데 검색이 안 되면 도구를 완전히 껐다 켜보고, 그래도 안 되면 "prompts.chat MCP로 code review 프롬프트 검색해 줘"처럼 도구 이름을 콕 집어 말하면 됩니다.
- 프롬프트 검색·가져오기는 로그인 없이 되지만, 내 프롬프트를 저장하려면 무료 계정 API 키가 필요합니다.

## 출처

[프롬프트 2,000개 GPT·클로드에 꽂는 법 — 도구별 연결 가이드](https://fieldby.notion.site/2-000-GPT-3d7d730b395381bb8f58fcbc532bb3e2?pvs=149)

## 출처

- [https://fieldby.notion.site/2-000-GPT-3d7d730b395381bb8f58fcbc532bb3e2?pvs=149](https://fieldby.notion.site/2-000-GPT-3d7d730b395381bb8f58fcbc532bb3e2?pvs=149)
