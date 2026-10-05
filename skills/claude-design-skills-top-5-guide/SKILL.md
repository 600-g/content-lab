---
name: claude-design-skills-top-5-guide
description: AI 가 만든 화면이 싸 보이지 않게 — **Claude Code `/design`** 시안→코드, 디자인 스킬 5종(**frontend-design·taste-skill·playwright-mcp·animate·Figma MCP**) 설치, 이모지를 **Lucide·Phosphor** 등 무료 아이콘 세트로 교체하는 프롬프트까지.
origin: content-lab
grade: S
difficulty: 초급
category: 디자인
ai_tools: ["Claude", "Claude Code", "GPT", "Gemini"]
sources:
  - https://fieldby.notion.site/TOP-5-392d730b3953818184e8c0700d2d7548?pvs=149
  - https://every-ai-guides.vercel.app/posts/bamti-free-icon-sites-5?from=dm&fbclid=PAVERFWAUk-jhleHRuA2FlbQIxMABwZG9mAmZkaWQWUPIylD577BF_RVZaqtiuhtZmwanARnNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp8MsxXxRuNcdfhkzUnLBaTepV-M9ZugNTtYt_LV43lfdf-wJrwtCr9aemDEV_aem_DWy0zphRxiK19Q42PX1wdw
  - https://app.notion.com/p/design-3c0fd99f0e5f8102ad3ed2294e75c755?source=copy_link
originals:
  - claude-design-skills-top-5-guide | 클로드 디자인 스킬 5가지 설치 | https://fieldby.notion.site/TOP-5-392d730b3953818184e8c0700d2d7548?pvs=149
  - free-icon-sites-replace-emoji-prompt | 이모지를 무료 아이콘 세트로 교체 | https://every-ai-guides.vercel.app/posts/bamti-free-icon-sites-5?from=dm&fbclid=PAVERFWAUk-jhleHRuA2FlbQIxMABwZG9mAmZkaWQWUPIylD577BF_RVZaqtiuhtZmwanARnNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp8MsxXxRuNcdfhkzUnLBaTepV-M9ZugNTtYt_LV43lfdf-wJrwtCr9aemDEV_aem_DWy0zphRxiK19Q42PX1wdw
  - claude-code-design-skill | 화면 시안을 코드로 만드는 Claude | https://app.notion.com/p/design-3c0fd99f0e5f8102ad3ed2294e75c755?source=copy_link
---

# AI 화면 고급스럽게 만들기

💡 밋밋한 그라데이션·알약 모양 태그·싸구려 모션·제각각 **이모지 아이콘**을 걷어내는 세 가지 도구 — **`/design` 시안**, **클로드 디자인 스킬 5종**, **무료 아이콘 세트 지정 프롬프트**를 한 흐름으로 묶었습니다.

## 이게 뭔가요?

클로드에게 화면(랜딩 페이지, 카드 UI, 대시보드 등)을 맡기면 결과물이 흔히 비슷한 이유로 싸 보입니다.

- 밋밋한 그라데이션, 알약 모양의 태그, 뻔한 템플릿 느낌의 레이아웃
- 과하거나 타이밍이 어색한, 저렴해 보이는 모션 효과
- 아이콘을 따로 정해 주지 않으면 ☕·🚀·✨ 같은 **이모지**로 아이콘 자리를 채움 — 이모지는 OS·브라우저마다 모양이 다르고 색감도 제각각이라 화면 전체가 싸 보이는 원인이 됩니다 ('밤티')

이 문서는 이 문제를 단계별로 해결하는 세 가지 방법을 다룹니다.

1. **Claude Code `/design` 스킬** — 앤트로픽(Anthropic)이 2026년 8월 18일 Claude Code 에 추가한 기능입니다. 만들고 싶은 화면을 텍스트로 설명하면 여러 개의 **편집 가능한 시안**을 만들어 주고, 그중 하나를 골라 고친 뒤 **실제 코드로 구현**까지 이어 줍니다. 시안 디자인과 코드 구현을 별도 도구에서 하던 과정을 Claude Code 안에서 한 번에 처리합니다. 현재 **연구 미리보기 단계**이며 Claude Code 의 **Pro, Max, Team, Enterprise 요금제**에서 쓸 수 있습니다.
2. **클로드 디자인 스킬 5종** — GitHub 에 공개된 스킬 중 에트 매거진이 직접 검토해 즉각적인 효과를 볼 수 있는 다섯 가지를 골랐습니다. 미적 방향 설정(`frontend-design`), 취향 다이얼(`taste-skill`), 스스로 검수하는 눈(`playwright-mcp`), 모션 교정(`animate`), 피그마 시안 반영(`Figma MCP`)입니다. 터미널로 설치하면 약 10분이 걸리며, 터미널이 어려우면 웹/앱에서 ZIP 으로 일부 스킬을 설치할 수 있습니다.
3. **이모지 → 무료 아이콘 세트 교체** — 쓸 **아이콘 세트를 이름으로 딱 하나 지정**해 주면 화면 전체의 선 굵기와 모양이 한 가지로 맞춰집니다. 무료 오픈소스 아이콘 사이트 다섯 곳(Lucide, Heroicons, Phosphor, Tabler Icons, Iconify)과 바로 쓰는 프롬프트를 담았습니다. Claude, Claude Code 등 화면 코드를 만들어 주는 AI 어디서나 쓸 수 있고, 다섯 사이트 모두 무료 오픈소스라 별도 비용이 없습니다.

### 비용

- 💰 **유료 필요**: 클로드 코드 자체는 무료 프로그램이지만, 스킬을 구동하기 위한 클로드 코드 계정은 Pro 이상 유료 구독 또는 API 크레딧이 필요합니다. `/design` 은 Pro, Max, Team, Enterprise 요금제 전용이며 무료 요금제에서는 지원되지 않습니다.
- ✅ **무료 대안**: 무료 클로드 계정 사용자도 웹/앱 ZIP 업로드 방법(아래 방법 3)으로 `frontend-design`·`taste-skill`·`animate` 를 쓸 수 있습니다. 아이콘 교체 프롬프트는 Claude Max 가 없어도 Gemini·ChatGPT 무료 플랜에 같은 프롬프트를 넣어 쓸 수 있습니다.

## 따라하기

### 어떤 방법을 언제 쓰나

| 상황 | 쓸 방법 | 필요한 것 |
|---|---|---|
| 아직 화면 방향이 없다. 시안 여러 개를 보고 골라서 바로 코드로 만들고 싶다 | 방법 1. `/design` 시안 → 코드 | Claude Code 최신 버전 + Pro 이상 요금제 |
| 클로드가 만드는 화면의 기본 품질(색·글꼴·여백·모션·검수)을 늘 끌어올리고 싶다 | 방법 2. 디자인 스킬 5종 설치 (터미널) | Claude Code + Node.js, Pro 이상 또는 API 크레딧 |
| 터미널 없이 claude.ai 웹/데스크톱 앱에서 쓰고 싶다 | 방법 3. 웹/앱 ZIP 업로드 (①·②·④ 스킬만) | 무료 플랜 포함 전 플랜 |
| 이미 만든 화면에 이모지가 박혀 있다 / 새 화면에 이모지가 안 들어가게 하고 싶다 | 방법 4. 아이콘 세트 지정 프롬프트 | 어떤 AI 든 가능, 비용 0원 |
| 피그마 시안이 이미 있다 | 방법 2 의 ⑤ `Figma MCP` | 피그마 개인 액세스 토큰 |

여러 개를 함께 쓴다면 맨 아래 **추천 루틴**을 따르세요.

### 방법 1. `/design` — 설명 한 줄로 시안 받고 코드까지

#### 시작 준비: Claude Code 를 최신으로

이 기능을 쓰려면 Claude Code 를 최신 버전으로 업데이트해야 합니다. 설치 방식에 따라 업데이트 방법이 다릅니다.

- **기본 설치판**: Claude Code 를 직접 설치한 경우, 설치된 버전을 업데이트합니다.
- **Homebrew 또는 WinGet**: 해당 패키지 관리자로 설치한 경우, 관리자 도구로 업데이트합니다.

아직 설치하지 않았다면 방법 2 의 STEP 1~2 로 먼저 설치합니다. 업데이트 후에도 `/design` 명령이 보이지 않으면 관련 도움말을 참고해야 할 수 있습니다.

#### 핵심 워크플로: 세 단계면 끝

1. **`/design` 뒤에 만들고 싶은 화면을 적는다**
   채팅 입력창에 `/design` 을 입력하고, 이어서 만들고 싶은 화면 설명을 씁니다.
   예시: `/design 클로드 코드를 위한 새로운 채팅 입력창`
2. **시안을 고르고, 그 자리에서 고친다**
   설명을 바탕으로 여러 개의 편집 가능한 시안이 생성됩니다. 시안을 직접 보면서 버튼 위치나 문구 등을 수정할 수 있습니다. 공식 문서에서는 이를 "editable artboards"라고 부르며, 화면 요소를 직접 조작해 원하는 디자인을 만듭니다.
3. **"이 안으로 만들어 줘" 한마디로 구현을 맡긴다**
   마음에 드는 시안을 확정한 뒤 "이 안으로 만들어 줘"처럼 요청하면 Claude Code 가 그 디자인을 바탕으로 실제 코드를 생성합니다.

시안 단계에서 "아이콘은 Lucide 만, 이모지 금지"처럼 방법 4 의 조건을 함께 적어 두면 구현 결과에서 다시 고칠 일이 줄어듭니다.

### 방법 2. 디자인 스킬 5종 설치 (터미널, 약 10분)

STEP 0 부터 STEP 5 까지 순서대로 따라 하면 10분 안에 설치가 끝납니다.

#### STEP 0. 터미널 열기

- **맥**: `cmd + 스페이스바` → "터미널" 입력 → 엔터
- **윈도우**: 시작 버튼 → "PowerShell" 입력 → 엔터

글자만 있는 창이 뜨면 터미널이 열린 것입니다.

#### STEP 1. 클로드 코드 설치 확인

이 스킬들은 '클로드 코드(Claude Code)' 위에 설치됩니다. 터미널에 다음 명령어를 입력하고 엔터를 누릅니다.

```
claude --version
```

버전 숫자가 표시되면 이미 설치된 것이므로 STEP 2 는 건너뛰고 STEP 3 으로 갑니다. "command not found"와 같은 오류가 나면 STEP 2 로 설치합니다.

#### STEP 2. 클로드 코드 설치 (설치되지 않은 경우)

- **맥**:
```bash
curl -fsSL https://claude.ai/install.sh | bash
```
- **윈도우 (PowerShell)**:
```powershell
irm https://claude.ai/install.ps1 | iex
```

설치가 끝나면 터미널에 `claude` 를 입력하고, 처음 실행할 때 브라우저에서 클로드 계정으로 로그인합니다. 이후 `claude --version` 을 다시 입력해 버전이 표시되면 성공입니다.

#### STEP 3. 스킬 설치 — 한 줄씩 복붙하고 엔터

먼저 **Node.js 설치 확인**: 스킬 설치 명령어(npx)는 Node.js 가 필요합니다. 터미널에 `node --version` 을 입력해 버전을 확인하세요. "command not found" 오류가 나면 nodejs.org 에서 LTS 버전을 설치하고 터미널을 재시작합니다.

설치 중 영어 질문이 나오면:
- "Ok to proceed? (y)" → `y` 입력 후 엔터
- 설치 위치 선택 시 → `Claude Code` 에 스페이스바로 체크 후 엔터

명령어 끝의 `-g` 옵션은 "내 컴퓨터 전체에서 쓰기"를 뜻합니다.

| 번호 | 스킬 | 해결하는 문제 | 슬래시 호출 |
|---|---|---|---|
| ① | `frontend-design` | 뻔한 디자인 — 미적 방향을 먼저 정하게 함 | 있음 (`/frontend-design`) |
| ② | `taste-skill` (`design-taste-frontend`) | 분위기 조절 — 과감함·모션·밀도 다이얼 | 있음 |
| ③ | `playwright-mcp` | 만들고 확인을 안 함 — 브라우저로 직접 열어 스스로 수정 | 없음 (자동 인식) |
| ④ | `animate` | 싸구려 모션 — 짧고 절제된 타이밍 | 있음 |
| ⑤ | `Figma MCP` | 시안과 다른 코드 — 피그마 값을 그대로 읽음 | 없음 (자동 인식) |

##### ① `frontend-design` — 뻔한 디자인 탈출의 기본기

Anthropic 공식 스킬로, 색상·글꼴·여백 등 미적 방향을 먼저 정한 뒤 코딩을 시작하게 합니다.

```bash
npx skills add anthropics/skills --skill frontend-design -g
```

##### ② `taste-skill` — 디자인 취향을 다이얼처럼 조절

결과물의 분위기를 과감함, 모션, 밀도 세 가지 다이얼로 조절합니다. 깃허브 별 5만 5천 개를 받은 검증된 스킬입니다.

```bash
npx skills add Leonxlnx/taste-skill --skill design-taste-frontend -g
```

##### ③ `playwright-mcp` — 클로드에게 "눈" 달아주기

클로드가 자신이 짠 화면을 브라우저로 직접 열어 보고 스스로 수정하게 합니다. "만들고 → 보고 → 고치는" 순환이 가능해져 체감 효과가 가장 큽니다.

```bash
claude mcp add playwright -s user -- npx @playwright/mcp@latest
```

##### ④ `animate` — 싸구려 느낌 모션 교정

AI 가 만든 애니메이션의 속도와 타이밍을 조절해 짧고 절제된 고급스러운 모션을 적용합니다.

```bash
npx skills add delphi-ai/animate-skill --skill animate -g
```

##### ⑤ `Figma MCP` — 피그마 시안을 그대로 코드로

피그마 시안의 색상·간격·글꼴 정보를 클로드가 직접 읽어 와 시안과 거의 똑같은 코드를 만듭니다. 피그마 개인 액세스 토큰이 필요합니다.

```bash
claude mcp add figma -s user -- npx figma-developer-mcp --figma-api-key=[피그마토큰] --stdio
```

*(`[피그마토큰]` 부분에 발급받은 피그마 개인 액세스 토큰을 붙여넣으세요. 토큰 발급 방법은 출처 원문 참조)*

#### STEP 4. 잘 깔렸는지 확인

터미널에 `claude` 를 입력해 클로드 코드를 실행한 뒤, "지금 내가 쓸 수 있는 디자인 스킬이나 도구, 뭐가 있어?"라고 물어 설치한 스킬 이름이 답변에 나오는지 확인합니다. 이름이 나오지 않으면 터미널을 완전히 껐다 켠 뒤 다시 시도하세요.

#### STEP 5. 실전 사용법 — 이렇게 시키면 됩니다

스킬은 자동으로 발동되거나 직접 호출할 수 있습니다. 직접 호출을 추천합니다.

- **자동 발동**: "랜딩페이지 만들어줘"처럼 요청하면 클로드가 관련 스킬을 알아서 적용합니다.
- **직접 호출 (추천)**: 문장에 스킬 이름을 넣거나 `/스킬이름` 형태로 명령하면 100% 발동됩니다. (예: `/frontend-design`)

`playwright-mcp` 와 `Figma MCP` 는 슬래시 호출이 없으며, 해당 도구가 필요한 작업을 요청하면 클로드가 알아서 인식합니다.

**나만의 명령어 만들기**: 긴 스킬 이름을 외울 필요 없이, 클로드에게 단축 명령어를 만들어 달라고 요청할 수 있습니다.

예시: "내가 `/디자인`이라고 치면 `frontend-design` 스킬과 `animate` 스킬을 같이 적용해서 작업하도록, 나만의 명령어로 만들어줘"

**스킬별 사용 예시**:

- **`frontend-design`**: "`frontend-design` 스킬 써서 우리 브랜드 소개 랜딩페이지 만들어줘. 뻔한 템플릿 느낌 말고, 방향을 과감하게 잡아서."
- **`taste-skill`**: "`design-taste-frontend` 스킬 써서, 지금 디자인에서 밀도는 그대로 두고 과감함만 한 단계 올려줘."
- **`playwright-mcp`**: "방금 만든 페이지를 브라우저로 직접 열어서 확인하고, 어색한 부분을 스스로 찾아서 고쳐줘."
- **`animate`**: "`animate` 스킬 써서 버튼이랑 카드에 자연스러운 등장 애니메이션 넣어줘. 과하지 않게."
- **`Figma MCP`**: "[피그마 파일 링크] 이 시안 그대로 코드로 만들어줘. 간격이랑 색상 최대한 똑같이."

### 방법 3. 클로드 웹/앱에서 쓰는 법 — ①·②·④ 스킬만

터미널 없이 claude.ai 웹 또는 데스크톱 앱을 쓴다면 ZIP 파일로 스킬을 업로드합니다. (무료 플랜 포함 전 플랜에서 사용 가능)

1. **ZIP 내려받기**: 각 스킬의 GitHub 페이지에서 "Code" → "Download ZIP"을 눌러 받습니다.
   - `frontend-design`: [https://github.com/anthropics/skills](https://github.com/anthropics/skills)
   - `taste-skill`: [https://github.com/Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)
   - `animate`: [https://github.com/delphi-ai/animate-skill](https://github.com/delphi-ai/animate-skill)
2. **스킬 폴더만 다시 압축**: 받은 ZIP 을 풀고, `SKILL.md` 파일이 들어 있는 스킬 폴더만 골라 새 ZIP 파일로 압축합니다.
3. **클로드에 업로드**: `claude.ai` 접속 → 설정(Settings) → Customize → Skills → "+" → "Upload a skill" 선택 후 방금 만든 ZIP 파일을 업로드합니다.
4. **켜져 있는지 확인**: 설정에서 코드 실행(Code execution) 기능이 켜져 있는지 확인합니다. 이후 채팅에서 "랜딩페이지 하나 만들어줘"라고 요청하면 업로드한 스킬이 적용됩니다.

*참고: `playwright-mcp` 와 `Figma MCP` 는 웹 버전에서 직접 지원이 어렵습니다. 데스크톱 앱의 확장 기능으로 구현할 수는 있지만 설정이 복잡하므로 클로드 코드 CLI 환경을 권장합니다.*

### 방법 4. 이모지를 무료 아이콘 세트로 교체 (약 10분)

#### STEP 1 · 3분 — 만들 화면에 맞는 아이콘 세트를 고른다

| 사이트 | 이럴 때 | 특징 |
|---|---|---|
| Lucide | 무난하고 깔끔한 기본 세트가 필요할 때 | 아이콘 1,856개(검색창 표시 기준). 색·크기·선 굵기를 바꿀 수 있음. ISC 라이선스 |
| Heroicons | 테일윈드 CSS로 만든 화면일 때 | Tailwind CSS 제작팀이 만든 316개. Outline·Solid·Mini·Micro 네 가지 스타일. MIT 라이선스 |
| Phosphor | 굵기를 화면 분위기에 맞추고 싶을 때 | 9,072개. Thin·Light·Regular·Bold·Fill·Duotone 여섯 굵기. MIT 라이선스 |
| Tabler Icons | 개수가 많고 상업용으로 쓸 세트가 필요할 때 | 6,220개. 무료 오픈소스 플랜에 MIT License·Personal & Commercial License 표기 |
| Iconify | 여러 세트를 한 번에 찾아보고 싶을 때 | 222개 아이콘 세트, 30만 개가 넘는 오픈소스 아이콘을 한곳에서 검색. 라이선스는 세트마다 다름 |

위 표에서 세트를 **하나만** 고릅니다. 잘 모르겠다면 Lucide 가 무난합니다. (라이선스와 아이콘 개수는 2026년 9월 25일 각 공식 페이지 기준)

#### STEP 2 · 3분 — 세트 이름과 아이콘 이름을 확인한다

1. 고른 사이트에서 필요한 아이콘을 검색합니다. `coffee`, `truck`, `shield-check` 처럼 영문 이름이 나옵니다.
2. 이 이름을 두세 개만 적어 둡니다. 이름을 알려 주면 클로드가 같은 세트에서 정확히 골라 씁니다.
3. Iconify 에서 찾은 아이콘은 **세트 이름과 라이선스를 함께** 확인합니다.

#### STEP 3 · 5분 — 프롬프트로 이모지를 아이콘 세트로 바꾼다

**이미 만든 화면이 있을 때** — 아래 프롬프트를 그대로 넣습니다. 아이콘 이름은 STEP 2 에서 적어 둔 것으로 바꿉니다.

```
방금 만든 화면에서 이모지로 된 아이콘을 전부 Lucide 아이콘으로 바꿔줘.
- 기능 카드: coffee, truck, leaf, star
- 버튼 안 화살표: arrow-right
아이콘은 한 세트만 쓰고, 크기와 선 굵기(stroke width)는 화면 전체에서 똑같이 맞춰줘. 본문과 버튼 글자에는 이모지를 넣지 마.
```

**처음부터 새 화면을 만들 때** — `[우리 서비스 한 줄 설명]` 자리에 서비스 설명을 넣습니다.

```
[우리 서비스 한 줄 설명]의 랜딩 페이지를 만들어줘. 아이콘은 Phosphor의 Regular 굵기만 쓰고, 이모지는 화면 어디에도 쓰지 마. 아이콘마다 어떤 이름을 썼는지 마지막에 목록으로 알려줘.
```

성공하면 화면의 이모지가 사라지고 같은 굵기의 선 아이콘으로 통일됩니다. 두 번째 프롬프트는 마지막에 사용한 아이콘 이름 목록도 함께 받아 검수하기 편합니다.

### ⭐ 추천 루틴 — 이 순서로 쌓으세요

1. 방향이 없다면 `/design` 으로 시안 여러 개를 보고 하나를 골라 고친 뒤 "이 안으로 만들어 줘"로 구현합니다. 피그마 시안이 있다면 대신 `Figma MCP` 로 시작합니다.
2. `frontend-design` 또는 `taste-skill` 로 색·글꼴·여백 기본기를 잡습니다.
3. 아이콘 세트를 하나 지정해 이모지를 걷어냅니다 (방법 4).
4. `animate` 로 모션을 다듬습니다.
5. `playwright-mcp` 로 클로드가 결과물을 브라우저에서 직접 검수하고 고치게 합니다.

### 마무리 점검 체크리스트

- [ ] 화면 어디에도 이모지가 아이콘 대신 쓰이지 않았다 (본문·버튼 글자 포함)
- [ ] 아이콘은 한 세트, 한 굵기로 통일됐다
- [ ] 색·글꼴·여백이 정해진 방향을 따른다 (`frontend-design` / `taste-skill`)
- [ ] 모션이 짧고 절제됐다 (`animate`)
- [ ] 브라우저로 실제 화면을 열어 어색한 부분을 확인했다 (`playwright-mcp`)
- [ ] 피그마 시안이 있다면 간격·색상이 시안과 일치한다 (`Figma MCP`)
- [ ] Iconify 등에서 가져온 아이콘의 라이선스를 확인했다

### 트러블슈팅

| 증상 | 해결 |
|---|---|
| `claude --version` 에 "command not found" | 방법 2 STEP 2 로 클로드 코드 설치 |
| `npx` 명령이 안 된다 | `node --version` 확인 → nodejs.org 에서 LTS 설치 후 터미널 재시작 |
| 설치했는데 스킬 이름이 안 나온다 | 터미널을 완전히 껐다 켠 뒤 STEP 4 질문 다시 |
| 스킬이 적용됐는지 모르겠다 | 문장에 스킬 이름을 넣거나 `/스킬이름` 으로 직접 호출 |
| `/design` 이 보이지 않는다 | Claude Code 최신 버전 업데이트, 요금제(Pro·Max·Team·Enterprise) 확인, 그래도 없으면 관련 도움말 참고 |
| 웹에 업로드한 스킬이 안 먹는다 | ZIP 안에 `SKILL.md` 가 든 스킬 폴더만 있는지, 코드 실행(Code execution)이 켜져 있는지 확인 |
| 아이콘을 바꿨는데도 어수선하다 | 세트가 섞였는지 확인하고 하나로 통일, 크기·선 굵기(stroke width)를 화면 전체에서 맞추도록 다시 요청 |

## 활용 예시

- **채팅 입력창 재설계**: `/design 클로드 코드를 위한 새로운 채팅 입력창, 사용자 경험을 개선하여 버튼 위치를 조정하고 텍스트 입력 영역을 넓힌다.` 입력 → 여러 시안이 나오고, 수정한 뒤 최종 코드를 받습니다.
- **대시보드 UI 생성**: `/design 월간 판매 실적을 보여주는 심플한 웹 대시보드. 좌측에는 필터링 옵션을, 우측에는 차트와 주요 지표를 배치한다.` 처럼 구체적인 요구사항을 전달해 맞춤형 UI 를 만듭니다.
- **브랜드 랜딩페이지 끌어올리기**: "`frontend-design` 스킬 써서 우리 브랜드 소개 랜딩페이지 만들어줘. 뻔한 템플릿 느낌 말고, 방향을 과감하게 잡아서." → "`animate` 스킬 써서 버튼이랑 카드에 자연스러운 등장 애니메이션 넣어줘. 과하지 않게." → "방금 만든 페이지를 브라우저로 직접 열어서 확인하고, 어색한 부분을 스스로 찾아서 고쳐줘."
- **기존 화면 아이콘 정리**: 클로드가 만든 카페 소개 페이지에 ☕🚚🌿⭐ 이모지가 카드마다 박혀 있다 → 방법 4 의 첫 번째 프롬프트 입력 → `coffee`, `truck`, `leaf`, `star` Lucide 아이콘으로 바뀌고 버튼 화살표도 `arrow-right` 로 통일됩니다.
- **처음부터 이모지 없는 화면**: 서비스 한 줄 설명과 함께 방법 4 의 두 번째 프롬프트 입력 → Phosphor Regular 굵기 아이콘만 쓴 랜딩 페이지가 나오고, 마지막에 아이콘별 사용 이름 목록이 붙습니다.
- **테일윈드 화면**: 테일윈드 CSS 로 만든 화면이라면 프롬프트의 세트 이름만 `Heroicons` 로 바꾸고 스타일(Outline 등)을 함께 지정합니다.
- **피그마 시안 구현**: "[피그마 파일 링크] 이 시안 그대로 코드로 만들어줘. 간격이랑 색상 최대한 똑같이."

## 💡 아이디어

- **나만의 `/디자인` 명령**: `frontend-design` + `animate` 를 묶은 단축 명령에 "아이콘은 Lucide 만, 이모지 금지" 조건까지 넣어 두면 한 번에 기본기·모션·아이콘이 정리됩니다.
- **CLAUDE.md 에 규칙 고정**: 프로젝트마다 사용할 아이콘 세트와 굵기를 CLAUDE.md 에 한 줄로 적어 두면 매번 프롬프트에 쓰지 않아도 같은 스타일이 유지됩니다.
- **스타트업 MVP 제작 가속화**: `/design` 으로 아이디어를 빠르게 시각화하고 프로토타입 코드까지 만들어 개발 속도를 높입니다.
- **개인 프로젝트 디자인 시스템 구축**: 자신만의 디자인 규칙을 Claude Code 에 알려 두고 일관된 디자인 시스템을 적용한 코드를 계속 생성합니다.
- **외주·판매용 결과물 마무리**: 랜딩 페이지·블로그 썸네일·상세페이지 목업의 마지막 단계로 아이콘 교체 + `playwright-mcp` 검수를 넣어 완성도를 올립니다.

## 주의사항

- **`/design` 은 연구 미리보기 단계**: 개발 초기 단계라 예상치 못한 오류가 나거나 불안정할 수 있습니다. Claude Code 공식 문서에 전용 페이지가 아직 없을 수 있어, 상세 기능이나 사용량 계산 등에 대한 정보가 제한적입니다.
- **요금제 제한**: `/design` 은 Pro, Max, Team, Enterprise 요금제에서만 쓸 수 있고, 터미널로 설치한 스킬도 Pro 이상 유료 구독 또는 API 크레딧이 필요합니다. 웹/앱 ZIP 업로드는 무료 플랜에서도 되지만 ①·②·④ 스킬만 가능합니다.
- **Figma 토큰 관리**: `--figma-api-key=[피그마토큰]` 에 넣는 개인 액세스 토큰은 비밀번호처럼 다룹니다.
- **아이콘 세트는 하나만**: 한 화면에 여러 세트를 섞으면 선 굵기가 달라져 다시 어수선해 보입니다.
- **아이콘만으로는 부족**: 아이콘만 바꿔도 인상이 크게 달라지지만 **색·글꼴·여백**은 따로 다듬어야 합니다 (`frontend-design`·`taste-skill` 로 보완).
- **라이선스 확인**: 아이콘 라이선스와 개수는 2026년 9월 25일 각 공식 페이지를 직접 열어 본 내용 기준이며 이후 달라질 수 있습니다. Iconify 의 개별 세트는 라이선스가 서로 다르니 쓰기 전에 세트 페이지에서 확인하세요.
- **공식 참고 자료**: Lucide(아이콘 검색), Heroicons(Tailwind CSS 제작팀 아이콘), Phosphor(여섯 굵기 아이콘), Tabler Icons(MIT 라이선스 아이콘), Iconify(아이콘 세트 통합 검색) 각 공식 사이트.

## 출처

- [https://fieldby.notion.site/TOP-5-392d730b3953818184e8c0700d2d7548?pvs=149](https://fieldby.notion.site/TOP-5-392d730b3953818184e8c0700d2d7548?pvs=149)
- [https://every-ai-guides.vercel.app/posts/bamti-free-icon-sites-5?from=dm&fbclid=PAVERFWAUk-jhleHRuA2FlbQIxMABwZG9mAmZkaWQWUPIylD577BF_RVZaqtiuhtZmwanARnNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp8MsxXxRuNcdfhkzUnLBaTepV-M9ZugNTtYt_LV43lfdf-wJrwtCr9aemDEV_aem_DWy0zphRxiK19Q42PX1wdw](https://every-ai-guides.vercel.app/posts/bamti-free-icon-sites-5?from=dm&fbclid=PAVERFWAUk-jhleHRuA2FlbQIxMABwZG9mAmZkaWQWUPIylD577BF_RVZaqtiuhtZmwanARnNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp8MsxXxRuNcdfhkzUnLBaTepV-M9ZugNTtYt_LV43lfdf-wJrwtCr9aemDEV_aem_DWy0zphRxiK19Q42PX1wdw)
- [https://app.notion.com/p/design-3c0fd99f0e5f8102ad3ed2294e75c755?source=copy_link](https://app.notion.com/p/design-3c0fd99f0e5f8102ad3ed2294e75c755?source=copy_link)

### 합쳐진 원본 문서

이 문서는 아래 3개 문서를 하나로 합쳐 새로 정리한 것입니다.

| 원본 문서 | 원래 슬러그 | 원본 출처 |
|---|---|---|
| 클로드 디자인 스킬 5가지 설치 | `claude-design-skills-top-5-guide` | [fieldby.notion.site](https://fieldby.notion.site/TOP-5-392d730b3953818184e8c0700d2d7548?pvs=149) |
| 이모지를 무료 아이콘 세트로 교체 | `free-icon-sites-replace-emoji-prompt` | [every-ai-guides.vercel.app](https://every-ai-guides.vercel.app/posts/bamti-free-icon-sites-5?from=dm&fbclid=PAVERFWAUk-jhleHRuA2FlbQIxMABwZG9mAmZkaWQWUPIylD577BF_RVZaqtiuhtZmwanARnNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp8MsxXxRuNcdfhkzUnLBaTepV-M9ZugNTtYt_LV43lfdf-wJrwtCr9aemDEV_aem_DWy0zphRxiK19Q42PX1wdw) |
| 화면 시안을 코드로 만드는 Claude | `claude-code-design-skill` | [app.notion.com](https://app.notion.com/p/design-3c0fd99f0e5f8102ad3ed2294e75c755?source=copy_link) |
