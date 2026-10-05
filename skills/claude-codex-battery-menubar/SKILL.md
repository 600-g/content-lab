---
name: claude-codex-battery-menubar
description: Claude Code·Codex 사용량 한도와 작업 상태를 화면에 늘 띄워 두는 가이드. **claude-codex-battery** 로 macOS 메뉴바·Windows 트레이·Linux 터미널에 배터리 아이콘을 띄우고, **/statusline** 으로 Claude Code 하단에 폴더·브랜치·모델·컨텍스트·5시간 한도를 표시한다.
origin: content-lab
grade: S
difficulty: 초급
category: 개발
ai_tools: ["Claude", "Claude Code", "Codex"]
sources:
  - https://github.com/dennykim123/claude-codex-battery
  - https://possible-timpani-b05.notion.site/3abf67ccdbf881c2b5e9f4bf449c950c?pvs=149
originals:
  - claude-codex-battery-menubar | 사용량 한도를 배터리로 표시 | https://github.com/dennykim123/claude-codex-battery
  - claude-code-status-bar-setup | 클로드코드 상태바 세팅 가이드 | https://possible-timpani-b05.notion.site/3abf67ccdbf881c2b5e9f4bf449c950c?pvs=149
---

# 사용량과 작업 상태 상시 표시

💡 `/usage`·`/status`·`/model` 을 매번 입력하지 않아도 되도록, **메뉴바 배터리 위젯**(claude-codex-battery)으로 계정 한도를, **터미널 상태바**(`/statusline`)로 지금 세션의 폴더·브랜치·모델·컨텍스트·5시간 한도를 늘 보이게 합니다.

## 이게 뭔가요?

Claude Code 와 Codex 를 쓰다 보면 「얼마나 남았지?」를 확인하려고 `/usage` 를 치고, 지금 어느 모델·어느 브랜치인지 보려고 `/status`, `/model` 을 따로 입력하게 됩니다. 이 가이드는 그 정보를 화면 두 곳에 상시 띄워 둡니다.

| 표시 위치 | 도구 | 보이는 것 | 대상 |
|---|---|---|---|
| macOS 메뉴바 / Windows 트레이 / Linux·tmux 상태줄 | **claude-codex-battery** | Claude(`C`)·Codex(`X`) 계정 한도의 남은 비율(%) 배터리, 클릭 시 리셋 시간·상세 내역 | Claude Code 와 Codex 를 함께 쓰는 사람, 터미널 밖에서도 잔량을 보고 싶은 사람 |
| Claude Code 창 맨 아래 | **`/statusline`** (Claude Code 내장) | 현재 폴더, git 브랜치, 사용 모델, 대화 컨텍스트 %, 5시간 사용량 한도 | Claude Code 작업 중 세션 상태를 보고 싶은 사람(비개발자 포함) |

두 가지는 겹치지 않고 보완 관계입니다. 메뉴바 위젯은 **계정 단위 한도**를 앱 밖에서 보여 주고, 상태바는 **지금 이 세션**의 맥락(컨텍스트 차오름, 모델, 브랜치)을 보여 줍니다. 둘 다 켜 두면 「세션 컨텍스트는 여유 있는데 주간 한도는 빨간불」 같은 상황을 한눈에 구분할 수 있습니다.

### claude-codex-battery

`claude-codex-battery`는 **Claude Code**와 **Codex**의 사용량 한도를 macOS 메뉴바(또는 Windows 시스템 트레이, Linux 터미널)에 **배터리 아이콘**으로 표시해 주는 오픈소스 위젯입니다. `C`는 Claude, `X`는 Codex를 의미하며, 각 배터리는 해당 한도 구간에서 **남은 비율(%)**을 보여 줍니다. 초록색이면 여유 있음, 빨간색이면 거의 소진된 상태입니다. 클릭하면 리셋 시간까지 포함한 상세 내역이 드롭다운으로 펼쳐집니다.

Anthropic·OpenAI의 공식 사용량 API를 로컬 로그인 토큰으로 직접 호출하기 때문에 별도 API 키가 필요 없고, 사용량 데이터가 외부로 업로드되지 않습니다. 계정 단위 API를 조회하므로 여러 기기에서 같은 계정을 쓰면 어디서 봐도 같은 잔여량이 나옵니다.

✅ 무료 대안: 이 도구 자체가 무료(MIT 라이선스)이며, Claude Code·Codex 계정에 이미 로그인되어 있으면 추가 비용 없이 사용 가능합니다. 단 Claude Code 또는 Codex 자체를 쓰지 않으면 표시할 데이터가 없습니다.

### Claude Code 상태바

Claude Code 화면 맨 아래에 현재 폴더, git 브랜치, 사용 모델, 대화 컨텍스트 및 5시간 사용량 한도 정보를 실시간으로 보여 주는 한 줄입니다. 원래 `/status`, `/usage`, `/model` 명령어를 각각 입력해야만 알 수 있던 정보들을 한눈에 파악할 수 있게 해 주며, 코딩 경험이 없는 비개발자도 Claude Code 활용도를 높일 수 있습니다. 상태줄은 사용자의 컴퓨터에서 직접 실행되므로 Claude API 토큰을 사용하지 않고, 사용량에 전혀 영향을 주지 않습니다.

| 항목     | 내용                                     | 예시                   |
| :------- | :--------------------------------------- | :--------------------- |
| **폴더명** | 현재 작업 중인 폴더                      | 뉴스 자동화            |
| **git 브랜치** | 현재 작업 중인 브랜치                    | master                 |
| **모델명**   | 현재 사용 중인 모델                      | Opus 5                 |
| **컨텍스트** | 대화가 얼마나 채워졌는지 (토큰 사용량)   | ■■□□□□□□□□ 7%       |
| **5시간 한도** | 최근 5시간 동안 사용량을 얼마나 썼는지 | 한도 12%               |

## 따라하기

### 어떤 방법을 언제 쓰나

| 내 환경·목적 | 고를 방법 | 준비물 |
|---|---|---|
| macOS, 설치를 가장 쉽게 | 방법 1. 네이티브 앱 | 없음 (dmg 더블클릭) |
| macOS, 스크립트를 직접 읽고 감사하고 싶음·갱신 주기를 바꾸고 싶음 | 방법 2. SwiftBar 플러그인 | SwiftBar, bun |
| Windows | 방법 3. PowerShell 스크립트 (실험적) | 없음 (.NET Framework 내장 도구) |
| Linux, Chromebook(Crostini), tmux·waybar 사용자 | 방법 4. `ccb` 터미널 배터리 | bun |
| Claude Code 창 안에서 세션 상태까지 보고 싶음 (OS 무관) | 방법 5. `/statusline` 상태바 | Claude Code 만 있으면 됨 |

> 추천 조합: macOS 라면 방법 1(또는 2) + 방법 5, Windows 라면 방법 3 + 방법 5, Linux 라면 방법 4 + 방법 5.

### 방법 1. macOS 네이티브 앱 (권장, 전제조건 없음)

1. GitHub [Releases](https://github.com/dennykim123/claude-codex-battery/releases) 페이지에서 `ClaudeCodexBattery-vX.Y.Z.dmg` 를 다운로드합니다.
2. dmg 를 열고 `ClaudeCodexBattery.app` 을 **Applications** 폴더로 드래그합니다.
3. 앱을 실행합니다 — 서명·공증(notarized)이 되어 있어 더블클릭으로 바로 실행되며, 최초 실행 시 로그인 시 자동 시작 여부를 물어봅니다.
4. 설정에서 언어(영어·한국어·日本語·简体中文·繁體中文·Español)와 **Settings → Cat**(픽셀 마스코트, 번아웃 시 감정 표현) 등을 조정할 수 있습니다.
5. Keychain 접근 권한 프롬프트가 뜨면 **Always Allow** 를 누릅니다(아래 주의사항 참고).

### 방법 2. SwiftBar 플러그인 (서드파티 라이브러리 없는 단일 스크립트, 감사 용이)

**필요 사항**

| | 필수? | 설치 |
|---|---|---|
| macOS | ✅ | — |
| SwiftBar | ✅ | `brew install swiftbar` |
| bun | ✅ | `curl -fsSL https://bun.sh/install \| bash` |
| Claude Code | ✅ (C 배터리용) | 이 Mac에 로그인만 되어 있으면 됨 |
| Codex CLI | 선택 | X 배터리용, 없으면 Claude만 표시 |
| ccusage | 선택 | 드롭다운에 비용·토큰·모델별 내역 추가 |

**자동 설치**

```bash
git clone https://github.com/dennykim123/claude-codex-battery.git
cd claude-codex-battery
./install.sh
```

`install.sh` 가 자동으로 수행하는 작업:

1. **bun**과 **SwiftBar**가 설치되어 있는지 확인 (없으면 설치 방법 안내)
2. 플러그인을 `~/.swiftbar-plugins/` 로 복사하면서 shebang을 로컬 bun 경로로 재작성 (SwiftBar가 최소 PATH로 플러그인을 실행하므로 절대경로 shebang 필요)
3. SwiftBar가 해당 플러그인 폴더를 바라보도록 설정 후 실행
4. launchd **KeepAlive** 에이전트를 설치해 재부팅·슬립·SwiftBar 크래시 후에도 자동 복구되게 함

**수동 설치**를 원하면:

```bash
mkdir -p ~/.swiftbar-plugins
# rewrite shebang to your bun path, then copy:
sed "1s|.*|#!$(command -v bun)|" claude-codex-usage.2m.js > ~/.swiftbar-plugins/claude-codex-usage.2m.js
chmod +x ~/.swiftbar-plugins/claude-codex-usage.2m.js
defaults write com.ameba.SwiftBar PluginDirectory -string ~/.swiftbar-plugins
open -a SwiftBar
```

**갱신 주기 바꾸기** — 플러그인은 2분(`.2m.`)마다 갱신됩니다. 파일명의 `.2m.` 부분을 `.1m.`, `.30s.` 등으로 바꾸면 갱신 주기를 조절할 수 있습니다.

**완전히 끄기**

```bash
launchctl bootout gui/$(id -u)/com.dennykim.claude-codex-battery && osascript -e 'quit app "SwiftBar"'
```

KeepAlive 에이전트가 깔려 있으므로 SwiftBar 만 종료하면 다시 살아납니다. 끌 때는 위 명령처럼 에이전트부터 내립니다.

### 방법 3. Windows (실험적)

```powershell
cd windows
.\install.ps1
```

.NET Framework 내장 도구로 컴파일되며 Node.js·패키지 매니저·Visual Studio 설치가 필요 없습니다. 자세한 내용은 저장소 내 `windows/README.md` 를 참고합니다.

### 방법 4. Linux & Chromebook (터미널 배터리 `ccb`)

Claude Code가 Linux 컨테이너에서 동작하는 Chromebook Crostini에서도 그대로 사용 가능합니다. `bun` 이 필요합니다.

```bash
git clone https://github.com/dennykim123/claude-codex-battery.git
cd claude-codex-battery
./ccb            # full gauges with reset countdowns
./ccb --statusline   # one compact ANSI line
./ccb --tmux         # tmux status-right format
./ccb --json         # waybar custom-module JSON
```

| 옵션 | 쓰임 |
|---|---|
| (없음) | 리셋 카운트다운이 포함된 전체 게이지 |
| `--statusline` | 한 줄짜리 ANSI 요약 |
| `--tmux` | tmux `status-right` 형식 |
| `--json` | waybar 커스텀 모듈용 JSON |
| `--serve` | 로컬 서버(포트 41414)로 브라우저 창 표시 |

tmux 상태바에 넣으려면:

```
set -g status-right '#(~/claude-codex-battery/ccb --tmux)'
```
(`status-interval 120` 함께 설정)

Chromebook에서 앱처럼 쓰고 싶다면:

```bash
./install-linux.sh
```

백그라운드 서버와 함께 ChromeOS 런처에 "Claude Codex Battery" 아이콘이 등록되어, 클릭 한 번으로 Linux 컨테이너를 부팅하며 배터리 창이 열립니다.

브라우저 창 형태로 쓰고 싶다면 `./ccb --serve` 로 로컬 서버(포트 41414)를 띄운 뒤 Chrome에서 열고 ⋮ → *Save and share* → *Install page as app* 으로 독립 창을 만들 수 있습니다.

### 방법 5. Claude Code 상태바 (`/statusline`)

#### 1단계 · 어디에 입력하는지 확인

Claude Code 창에 직접 입력합니다. 터미널이 아닙니다.

*   **터미널:** `PS C:\Users\...>` 또는 `이름@맥북 ~ %` 와 같이 시작합니다.
*   **클로드코드:** `>` 만 보이며, `for agents` 와 같은 안내 메시지가 하단에 표시됩니다.

**클로드코드 켜는 법**

1.  터미널을 엽니다.
2.  작업할 폴더로 이동합니다.
3.  `claude` 를 입력하고 실행합니다.

`Welcome back` 메시지가 뜨면 성공입니다.

#### 2단계 · 운영체제에 맞는 프롬프트 붙여넣기

**Windows 사용자** — Claude Code 창에 다음 명령어를 붙여넣으세요:

```
/statusline 현재 폴더명,
git 브랜치, 모델명,
컨텍스트 % 프로그레스바,
5시간 사용량 한도를 한 줄로 보여줘.
PowerShell로 만들어줘
```

`PowerShell로 만들어줘` 를 반드시 포함해야 합니다. 이 지시가 없으면 bash로 생성되는데, bash는 `jq` 라는 프로그램을 별도 설치해야만 데이터를 제대로 읽을 수 있습니다. PowerShell은 Windows에 기본 내장되어 있어 별도 설치 없이 바로 작동합니다.

**Mac 사용자** — Claude Code 창에 다음 명령어를 붙여넣으세요:

```
/statusline 현재 폴더명, git 브랜치, 모델명, 컨텍스트 % 프로그레스바, 5시간 사용량 한도를 한 줄로 보여줘.
Python으로 만들어줘
```

Mac에서도 `Python으로 만들어줘` 를 붙이는 것이 안전합니다. Mac에는 `jq`가 기본으로 없기 때문에 bash로 생성 시 상태줄이 비어 보일 수 있습니다. Python으로 생성하면 이 문제를 방지할 수 있습니다.

#### 3단계 · 승인하고 첫 메시지 보내기

1.  파일을 만들어도 되냐는 질문에 `승인` 합니다.
2.  설정이 완료되면, Claude Code에게 아무 말이나 건네보세요 (예: `안녕`).

그때부터 화면 아래에 상태줄이 나타나기 시작합니다. 한 번 설정하면 Claude Code를 껐다 켜거나 다른 폴더로 이동해도 계속 유지됩니다(사용자별 설정 파일에 저장). 단 설정은 현재 컴퓨터에 저장되므로, 다른 컴퓨터(예: PC에서 설정 후 노트북)에서는 다시 설정해야 합니다.

#### 4단계 · 마음에 안 들면 말로 고치기

색상이나 표시되는 항목을 자유롭게 변경할 수 있습니다. Claude Code에게 직접 요청합니다.

*   **색상 변경:** `상태줄 색이 너무 어두워. 5개 항목 전부 밝게 바꿔줘`
*   **프로그레스바 형식 변경:** `컨텍스트 바를 채운 칸은 ■, 빈 칸은 □ 로 바꿔줘`
*   **항목 이름 변경:** `5h 를 한도 로 바꿔줘`
*   **항목 제거:** `git 브랜치는 빼줘`
*   **줄바꿈:** `너무 길어. 두 줄로 나눠줘`

#### 끄고 싶으면

```
/statusline delete
```

이 명령어를 실행하면 설정 파일에서 상태줄 관련 항목이 삭제됩니다. 상태바에는 별도의 on/off 스위치가 없으며, 다시 켜려면 2단계의 프롬프트를 다시 입력합니다.

### 트러블슈팅

| 증상 | 원인·해결 |
|---|---|
| 메뉴바에 `C` 배터리가 안 나옴 | 이 Mac 의 Claude Code 에 로그인되어 있는지 확인 (본인 계정 데이터만 표시) |
| `X` 배터리가 안 나옴 | Codex CLI 가 없거나 로그인 안 됨 → 없으면 Claude 만 표시되는 것이 정상 |
| 새로고침마다 Keychain 확인창이 뜸 | 최초 권한 프롬프트에서 **Always Allow** 선택 |
| SwiftBar 플러그인이 비어 있거나 실행 안 됨 | SwiftBar 는 최소 PATH 로 실행하므로 shebang 이 bun 절대경로여야 함 → `install.sh` 재실행 또는 수동 설치의 `sed` 줄 재실행 |
| SwiftBar 를 꺼도 다시 켜짐 | KeepAlive 에이전트 때문 → `launchctl bootout ...` 명령으로 끄기 |
| 드롭다운에 비용·모델별 내역이 없음 | `ccusage` 설치 (선택 사항) |
| 상태바를 설정했는데 아무것도 안 보임 | Claude Code를 껐다 켜거나, 아무 말이나 한 번 더 걸어보기 |
| 껐다 켜도 상태바가 안 보임 | 설정 파일이 제대로 저장되지 않았을 수 있음 → 프롬프트를 다시 입력 |
| 상태바에서 5시간 한도만 안 보임 | `jq` 프로그램이 없거나 제대로 설치되지 않음 (Mac bash 사용자) → Python/PowerShell 로 다시 생성 |
| git 브랜치만 안 보임 | 해당 폴더가 git으로 관리되지 않거나, git 정보 파싱 문제 |
| 한글 폴더인데 브랜치만 안 나옴 | 인코딩 문제일 수 있음 → Claude Code의 터미널 환경 설정 확인 |
| 상태줄은 있는데 값이 다 비어 있음 | Claude Code가 정상적으로 실행되지 않았거나 정보 수집 실패 → Claude Code 재시작 |
| 글자가 네모나 물음표로 깨짐 | 폰트 문제 또는 터미널이 한국어를 제대로 지원하지 못함 → 터미널 설정 확인 또는 다른 터미널 에뮬레이터 사용 |

## 활용 예시

- Claude Max 요금제로 Claude Code를 하루 종일 쓰는 경우, 메뉴바에서 `C` 배터리가 빨간색으로 바뀌는 순간 작업 강도를 조절 → 5시간 세션 한도 초과로 작업이 끊기는 상황을 사전에 방지합니다.
- 여러 대의 Mac에서 같은 Claude Code 계정을 쓰는 경우, 계정 단위 사용량 API를 조회하므로 어느 기기에서 봐도 동일한 잔여량이 표시됩니다 → 팀/개인 다중 기기 환경에서 중복 확인이 필요 없습니다.
- Codex CLI 사용자가 `ccusage` 를 함께 설치하면 드롭다운에서 `today by model · $55 total` 같은 형태로 오늘 사용한 비용을 모델별로 바로 확인할 수 있습니다.
- 긴 작업 중 상태바의 컨텍스트 프로그레스바가 차오르는 것을 보고 적절한 시점에 대화를 정리하거나 새로 시작할 타이밍을 잡습니다.
- 여러 폴더·브랜치를 오가며 작업할 때 상태바의 폴더명·git 브랜치를 보고 엉뚱한 곳에서 작업하는 실수를 줄입니다. 모델명 표시로 지금 어떤 모델이 답하고 있는지도 바로 확인합니다.
- Linux 서버나 Chromebook 에서 tmux 로 작업할 때 `ccb --tmux` 를 `status-right` 에 넣어, 터미널 하단에 Claude·Codex 잔량을 함께 띄워 둡니다.

## 💡 아이디어

- 메뉴바 위젯(계정 주간·5시간 한도) + Claude Code 상태바(세션 컨텍스트·모델·브랜치)를 동시에 켜 두면, 「한도 때문에 멈춰야 하는지」와 「세션을 정리해야 하는지」를 따로 판단할 수 있습니다.
- waybar 사용자라면 `ccb --json` 을 커스텀 모듈에 연결해 데스크톱 상단바에 배터리를 띄울 수 있습니다.
- 상태바 항목은 말로 고칠 수 있으므로, 처음엔 5개 항목으로 시작해 자주 안 보는 항목은 빼고 두 줄로 나누는 식으로 자기 화면에 맞게 다듬어 갑니다.

## 주의사항

- 메뉴바 위젯은 **본인 계정의** 사용량만 보여 줍니다. Claude Code 또는 Codex CLI에 로그인되어 있지 않으면 표시할 데이터 자체가 없습니다.
- Claude 토큰은 macOS Keychain(`Claude Code-credentials` 항목)에서, Codex 토큰은 `~/.codex/auth.json` 에서 읽으며, 각각 `api.anthropic.com` / `chatgpt.com` 으로만 전송됩니다. Keychain 접근 시 뜨는 최초 권한 프롬프트는 **Always Allow**를 눌러야 매 새로고침마다 재확인창이 뜨지 않습니다.
- Keychain 접근 자체를 원치 않으면 `touch ~/.claude/swiftbar/.no-live` 로 라이브 조회를 끄고 로컬 캐시 파일만 읽게 할 수 있습니다.
- SwiftBar 플러그인은 2분(`.2m.`)마다 갱신되며, 파일명의 `.2m.` 부분을 `.1m.`, `.30s.` 등으로 바꾸면 갱신 주기를 조절할 수 있습니다.
- 업데이트 확인은 하루 최대 1회, `VERSION` 파일에 대한 가벼운 요청으로 이루어지며 이 요청을 원치 않으면 스크립트 하단의 `getUpdateInfo()` 호출을 주석 처리하면 됩니다.
- Windows 지원은 실험적입니다.
- `/statusline` 프롬프트는 반드시 Claude Code 창(`>` 프롬프트)에 입력합니다. 터미널에 치면 동작하지 않습니다.
- Windows 는 `PowerShell로 만들어줘`, Mac 은 `Python으로 만들어줘` 를 꼭 붙입니다. bash 로 만들어지면 `jq` 가 없어서 상태줄이 비거나 5시간 한도가 안 보일 수 있습니다.
- 상태바 설정은 기기별로 저장됩니다. 다른 컴퓨터에서는 다시 설정해야 합니다.
- 상태줄은 로컬에서 실행되므로 Claude API 토큰을 쓰지 않습니다. 켜 둔다고 한도가 줄지 않습니다.

## 출처

- [https://github.com/dennykim123/claude-codex-battery](https://github.com/dennykim123/claude-codex-battery)
- [https://possible-timpani-b05.notion.site/3abf67ccdbf881c2b5e9f4bf449c950c?pvs=149](https://possible-timpani-b05.notion.site/3abf67ccdbf881c2b5e9f4bf449c950c?pvs=149)

### 합쳐진 원본 문서

이 문서는 아래 2개 문서를 하나로 합쳐 새로 정리한 것입니다.

| 원본 문서 | 원래 슬러그 | 원본 출처 |
|---|---|---|
| 사용량 한도를 배터리로 표시 | `claude-codex-battery-menubar` | [github.com](https://github.com/dennykim123/claude-codex-battery) |
| 클로드코드 상태바 세팅 가이드 | `claude-code-status-bar-setup` | [possible-timpani-b05.notion.site](https://possible-timpani-b05.notion.site/3abf67ccdbf881c2b5e9f4bf449c950c?pvs=149) |
