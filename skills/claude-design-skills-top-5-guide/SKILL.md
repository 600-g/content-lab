---
name: claude-design-skills-top-5-guide
description: 밋밋한 그라데이션, 알약 모양 태그, 싸구려 느낌 모션을 개선하는 **클로드 디자인 스킬 5가지**를 설치하고 활용하는 가이드입니다.
origin: content-lab
grade: S
difficulty: 초급
category: 디자인
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://fieldby.notion.site/TOP-5-392d730b3953818184e8c0700d2d7548?pvs=149
---

# 클로드 디자인 스킬 5가지 설치

💡 밋밋한 그라데이션, 알약 모양 태그, 싸구려 느낌 모션을 개선하는 **클로드 디자인 스킬 5가지**를 설치하고 활용하는 가이드입니다.

## 이게 뭔가요?

밋밋하게 느껴지는 웹사이트 디자인, 알약 모양의 태그, 저렴해 보이는 모션 효과 등 기존 AI가 생성하는 디자인의 아쉬운 점들을 개선해주는 스킬들이 GitHub에 공개되었습니다. 에트 매거진에서 직접 검토하여 즉각적인 효과를 볼 수 있는 다섯 가지 스킬을 선별하여 설치 및 활용 가이드를 제공합니다.

이 가이드에서는 터미널을 사용하여 클로드 디자인 스킬을 설치하는 방법을 안내하며, 스킬 설치 및 설정에 약 10분 정도 소요됩니다. 터미널 사용이 어려운 사용자를 위해 웹/앱에서 ZIP 파일로 스킬을 설치하는 부록도 포함되어 있습니다.

💰 **유료 필요**: 클로드 코드 자체는 무료 프로그램이지만, 스킬을 구동하기 위한 클로드 코드 계정은 Pro 이상 유료 구독 또는 API 크레딧이 필요합니다. ✅ **무료 대안**: 무료 클로드 계정 사용자도 부록의 웹/앱 사용법을 통해 일부 스킬을 사용할 수 있습니다.

## 따라하기

아래 STEP 0부터 STEP 5까지 순서대로 따라하면 10분 안에 스킬 설치를 완료할 수 있습니다.

### STEP 0. 터미널 열기

먼저 터미널(명령어 창)을 열어야 합니다.

- **맥**: `cmd + 스페이스바` → "터미널" 입력 → 엔터
- **윈도우**: 시작 버튼 → "PowerShell" 입력 → 엔터

글자만 있는 창이 뜨면 터미널이 열린 것입니다.

### STEP 1. 클로드 코드 설치 확인

이 스킬들은 '클로드 코드(Claude Code)' 위에 설치됩니다. 이미 설치되어 있는지 확인해 보세요.

터미널에 다음 명령어를 입력하고 엔터를 누릅니다:

```
claude --version
```

버전 숫자가 표시되면 이미 설치된 것이므로 STEP 2는 건너뛰고 STEP 3으로 이동하세요. "command not found"와 같은 오류가 발생하면 STEP 2를 따라 설치를 진행합니다.

### STEP 2. 클로드 코드 설치 (설치되지 않은 경우)

클로드 코드가 설치되어 있지 않다면 아래 명령어를 터미널에 입력하여 설치합니다.

- **맥**: 
```bash
curl -fsSL https://claude.ai/install.sh | bash
```
- **윈도우 (PowerShell)**: 
```powershell
irm https://claude.ai/install.ps1 | iex
```

설치가 완료되면 터미널에 `claude`를 입력하고, 처음 실행 시 브라우저에서 클로드 계정으로 로그인합니다. 이후 `claude --version`을 다시 입력하여 버전이 표시되면 설치가 성공한 것입니다.

### STEP 3. 스킬 설치 — 한 줄씩 복붙하고 엔터

Node.js 설치 확인: 스킬 설치 명령어(npx)는 Node.js가 필요합니다. 터미널에 `node --version`을 입력하여 버전을 확인하세요. "command not found" 오류 시 nodejs.org에서 LTS 버전을 설치하고 터미널을 재시작합니다.

설치 중 영어 질문 발생 시:
- "Ok to proceed? (y)" → `y` 입력 후 엔터
- 설치 위치 선택 시 → `Claude Code`에 스페이스바로 체크 후 엔터

명령어 끝의 `-g` 옵션은 "내 컴퓨터 전체에서 쓰기"를 의미합니다.

#### ① `frontend-design` — 뻔한 디자인 탈출의 기본기

Anthropic 공식 스킬로, 색상, 글꼴, 여백 등 미적 방향을 먼저 정한 후 코딩을 시작하게 합니다.

```bash
npx skills add anthropics/skills --skill frontend-design -g
```

#### ② `taste-skill` — 디자인 취향을 다이얼처럼 조절

결과물의 분위기를 과감함, 모션, 밀도 세 가지 다이얼로 조절할 수 있습니다. 깃허브 별 5만 5천 개를 받은 검증된 스킬입니다.

```bash
npx skills add Leonxlnx/taste-skill --skill design-taste-frontend -g
```

#### ③ `playwright-mcp` — 클로드에게 "눈" 달아주기

클로드가 자신이 짠 화면을 브라우저로 직접 열어보고 스스로 수정하게 합니다. "만들고 → 보고 → 고치는" 순환을 가능하게 하여 체감 효과가 가장 큽니다.

```bash
claude mcp add playwright -s user -- npx @playwright/mcp@latest
```

#### ④ `animate` — 싸구려 느낌 모션 교정

AI가 만든 애니메이션의 속도와 타이밍을 조절하여 짧고 절제된 고급스러운 모션을 적용합니다.

```bash
npx skills add delphi-ai/animate-skill --skill animate -g
```

#### ⑤ `Figma MCP` — 피그마 시안을 그대로 코드로

피그마 시안의 색상, 간격, 글꼴 정보를 클로드가 직접 읽어와 시안과 거의 똑같은 코드를 생성합니다. 피그마 개인 액세스 토큰이 필요합니다.

```bash
claude mcp add figma -s user -- npx figma-developer-mcp --figma-api-key=[피그마토큰] --stdio
```

*(주의: `[피그마토큰]` 부분에 발급받은 피그마 개인 액세스 토큰을 붙여넣으세요. 토큰 발급 방법은 원문 참조)*

### STEP 4. 잘 깔렸는지 확인

터미널에 `claude`를 입력하여 클로드 코드를 실행한 뒤, "지금 내가 쓸 수 있는 디자인 스킬이나 도구, 뭐가 있어?"라고 질문하여 설치한 스킬 이름이 답변에 나오는지 확인합니다. 이름이 나오지 않으면 터미널을 완전히 껐다 켠 후 다시 시도하세요.

### STEP 5. 실전 사용법 — 이렇게 시키면 됩니다

스킬은 자동으로 발동되거나, 직접 호출할 수 있습니다. 직접 호출을 추천합니다.

- **자동 발동**: "랜딩페이지 만들어줘"와 같이 요청하면 클로드가 관련 스킬을 알아서 적용합니다.
- **직접 호출 (추천)**: 문장에 스킬 이름을 넣거나 `/스킬이름` 형태로 명령하면 100% 발동됩니다. (예: `/frontend-design`)

**나만의 명령어 만들기**: 긴 스킬 이름을 외울 필요 없이, 클로드에게 나만의 단축 명령어를 만들어 달라고 요청할 수 있습니다.

예시: "내가 `/디자인`이라고 치면 `frontend-design` 스킬과 `animate` 스킬을 같이 적용해서 작업하도록, 나만의 명령어로 만들어줘"

**스킬별 사용 예시**:

- **`frontend-design`**: "`frontend-design` 스킬 써서 우리 브랜드 소개 랜딩페이지 만들어줘. 뻔한 템플릿 느낌 말고, 방향을 과감하게 잡아서."
- **`taste-skill`**: "`design-taste-frontend` 스킬 써서, 지금 디자인에서 밀도는 그대로 두고 과감함만 한 단계 올려줘."
- **`playwright-mcp`**: "방금 만든 페이지를 브라우저로 직접 열어서 확인하고, 어색한 부분을 스스로 찾아서 고쳐줘."
- **`animate`**: "`animate` 스킬 써서 버튼이랑 카드에 자연스러운 등장 애니메이션 넣어줘. 과하지 않게."
- **`Figma MCP`**: "[피그마 파일 링크] 이 시안 그대로 코드로 만들어줘. 간격이랑 색상 최대한 똑같이."

`playwright-mcp`와 `Figma MCP`는 슬래시 호출이 없으며, 해당 도구가 필요한 작업을 요청하면 클로드가 알아서 인식합니다.

### ⭐ 추천 루틴 — 이 순서로 쌓으세요

1. `frontend-design` 또는 `taste-skill`로 기본기를 잡습니다.
2. `animate`로 모션을 다듬습니다.
3. `playwright-mcp`로 클로드가 결과물을 직접 검수하게 합니다.
4. 피그마 시안이 있다면 `Figma MCP`를 추가합니다.

## 📎 부록. 클로드 웹/앱에서 쓰는 법 — ①·②·④ 스킬만

터미널 없이 claude.ai 웹 또는 데스크톱 앱을 사용하는 경우, ZIP 파일로 스킬을 업로드하여 사용할 수 있습니다. (무료 플랜 포함 전 플랜에서 사용 가능)

1.  **ZIP 내려받기**: 각 스킬의 GitHub 페이지에서 "Code" → "Download ZIP"을 눌러 다운로드합니다.
    *   `frontend-design`: [https://github.com/anthropics/skills](https://github.com/anthropics/skills)
    *   `taste-skill`: [https://github.com/Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)
    *   `animate`: [https://github.com/delphi-ai/animate-skill](https://github.com/delphi-ai/animate-skill)
2.  **스킬 폴더만 다시 압축**: 다운로드한 ZIP 압축 해제 후, `SKILL.md` 파일이 포함된 스킬 폴더만 선택하여 새 ZIP 파일로 압축합니다.
3.  **클로드에 업로드**: `claude.ai` 접속 → 설정(Settings) → Customize → Skills → "+" → "Upload a skill" 선택 후 방금 만든 ZIP 파일을 업로드합니다.
4.  **켜져 있는지 확인**: 설정에서 코드 실행(Code execution) 기능이 활성화되어 있는지 확인합니다. 이후 채팅에서 "랜딩페이지 하나 만들어줘"라고 요청하면 업로드한 스킬이 적용됩니다.

*참고: `playwright-mcp`와 `Figma MCP`는 웹 버전에서 직접적인 지원이 어렵습니다. 데스크톱 앱의 확장 기능으로 구현 가능하지만 설정이 복잡하므로, 클로드 코드 CLI 환경에서의 사용을 권장합니다.*

## 출처

- [https://fieldby.notion.site/TOP-5-392d730b3953818184e8c0700d2d7548?pvs=149](https://fieldby.notion.site/TOP-5-392d730b3953818184e8c0700d2d7548?pvs=149)
