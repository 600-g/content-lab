---
name: claude-codex-battery-menubar
description: Claude Code와 Codex의 사용량 한도를 macOS 메뉴바·Windows 트레이·Linux 터미널에 **배터리 아이콘**으로 실시간 표시해주는 오픈소스 위젯이다. `/usage` 를 매번 입력하지 않아도 잔여량과 리셋 시간을 한눈에 확인할 수 있다.
origin: content-lab
grade: S
difficulty: 중급
category: 개발
ai_tools: ["Claude", "Claude Code", "Codex"]
sources:
  - https://github.com/dennykim123/claude-codex-battery
---

# 사용량 한도를 배터리로 표시

💡 Claude Code와 Codex의 사용량 한도를 macOS 메뉴바·Windows 트레이·Linux 터미널에 **배터리 아이콘**으로 실시간 표시해주는 오픈소스 위젯이다. `/usage` 를 매번 입력하지 않아도 잔여량과 리셋 시간을 한눈에 확인할 수 있다.

## 이게 뭔가요?

`claude-codex-battery`는 **Claude Code**와 **Codex**의 사용량 한도를 macOS 메뉴바(또는 Windows 시스템 트레이, Linux 터미널)에 **배터리 아이콘**으로 표시해주는 위젯이다. `/usage` 명령을 매번 입력할 필요 없이, 메뉴바를 보는 것만으로 남은 사용량을 실시간으로 확인할 수 있다.

`C`는 Claude, `X`는 Codex를 의미하며, 각 배터리는 해당 한도 구간에서 **남은 비율(%)**을 보여준다. 초록색이면 여유 있음, 빨간색이면 거의 소진된 상태다. 클릭하면 리셋 시간까지 포함한 상세 내역이 드롭다운으로 펼쳐진다.

설치 방식은 세 가지다.
- **네이티브 앱**(macOS): 공증(notarized)된 `.app`을 더블클릭 설치, 전제조건 없음
- **SwiftBar 플러그인**: 서드파티 라이브러리 없는 단일 스크립트, `bun` 런타임 필요
- **Windows 실험적 지원 / Linux·Chromebook 터미널 배터리**: PowerShell 스크립트 또는 `ccb` CLI

Anthropic·OpenAI의 공식 사용량 API를 로컬 로그인 토큰으로 직접 호출하기 때문에 별도 API 키가 필요 없고, 사용량 데이터가 외부로 업로드되지 않는다.

✅ 무료 대안: 이 도구 자체가 무료(MIT 라이선스)이며, Claude Code·Codex 계정에 이미 로그인되어 있으면 추가 비용 없이 사용 가능하다. 단 Claude Code 또는 Codex 자체를 쓰지 않으면 표시할 데이터가 없다.

## 따라하기

### 방법 1 — macOS 네이티브 앱 (권장, 전제조건 없음)

1. GitHub [Releases](https://github.com/dennykim123/claude-codex-battery/releases) 페이지에서 `ClaudeCodexBattery-vX.Y.Z.dmg` 를 다운로드한다.
2. dmg 를 열고 `ClaudeCodexBattery.app` 을 **Applications** 폴더로 드래그한다.
3. 앱을 실행한다 — 서명·공증이 되어 있어 더블클릭으로 바로 실행되며, 최초 실행 시 로그인 시 자동 시작 여부를 물어본다.
4. 설정에서 언어(영어·한국어·日本語·简体中文·繁體中文·Español)와 **Settings → Cat**(픽셀 마스코트, 번아웃 시 감정 표현) 등을 조정할 수 있다.

### 방법 2 — SwiftBar 플러그인 (단일 스크립트, 감사 용이)

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

완전히 끄고 싶다면:

```bash
launchctl bootout gui/$(id -u)/com.dennykim.claude-codex-battery && osascript -e 'quit app "SwiftBar"'
```

**수동 설치**를 원하면:

```bash
mkdir -p ~/.swiftbar-plugins
# rewrite shebang to your bun path, then copy:
sed "1s|.*|#!$(command -v bun)|" claude-codex-usage.2m.js > ~/.swiftbar-plugins/claude-codex-usage.2m.js
chmod +x ~/.swiftbar-plugins/claude-codex-usage.2m.js
defaults write com.ameba.SwiftBar PluginDirectory -string ~/.swiftbar-plugins
open -a SwiftBar
```

SwiftBar 플러그인 필요 사항:

| | 필수? | 설치 |
|---|---|---|
| macOS | ✅ | — |
| SwiftBar | ✅ | `brew install swiftbar` |
| bun | ✅ | `curl -fsSL https://bun.sh/install \| bash` |
| Claude Code | ✅ (C 배터리용) | 이 Mac에 로그인만 되어 있으면 됨 |
| Codex CLI | 선택 | X 배터리용, 없으면 Claude만 표시 |
| ccusage | 선택 | 드롭다운에 비용·토큰·모델별 내역 추가 |

### 방법 3 — Windows (실험적)

```powershell
cd windows
.\install.ps1
```

.NET Framework 내장 도구로 컴파일되며 Node.js·패키지 매니저·Visual Studio 설치가 필요 없다. 자세한 내용은 저장소 내 `windows/README.md` 참고.

### 방법 4 — Linux & Chromebook (터미널 배터리)

Claude Code가 Linux 컨테이너에서 동작하는 Chromebook Crostini에서도 그대로 사용 가능하다. `bun` 필요.

```bash
git clone https://github.com/dennykim123/claude-codex-battery.git
cd claude-codex-battery
./ccb            # full gauges with reset countdowns
./ccb --statusline   # one compact ANSI line
./ccb --tmux         # tmux status-right format
./ccb --json         # waybar custom-module JSON
```

tmux 상태바에 넣으려면:

```
set -g status-right '#(~/claude-codex-battery/ccb --tmux)'
```
(`status-interval 120` 함께 설정)

Chromebook에서 앱처럼 쓰고 싶다면:

```bash
./install-linux.sh
```

백그라운드 서버와 함께 ChromeOS 런처에 "Claude Codex Battery" 아이콘이 등록되어, 클릭 한 번으로 Linux 컨테이너를 부팅하며 배터리 창이 열린다.

브라우저 창 형태로 쓰고 싶다면 `./ccb --serve` 로 로컬 서버(포트 41414)를 띄운 뒤 Chrome에서 열고 ⋮ → *Save and share* → *Install page as app* 으로 독립 창을 만들 수 있다.

## 활용 예시

- Claude Max 요금제로 Claude Code를 하루 종일 쓰는 경우, 메뉴바에서 `C` 배터리가 빨간색으로 바뀌는 순간 작업 강도를 조절 → 5시간 세션 한도 초과로 작업이 끊기는 상황을 사전에 방지
- 여러 대의 Mac에서 같은 Claude Code 계정을 쓰는 경우, 계정 단위 사용량 API를 조회하므로 어느 기기에서 봐도 동일한 잔여량이 표시됨 → 팀/개인 다중 기기 환경에서 중복 확인 불필요
- Codex CLI 사용자가 `ccusage` 를 함께 설치하면 드롭다운에서 `today by model · $55 total` 같은 형태로 오늘 사용한 비용을 모델별로 바로 확인 가능

## 주의사항

- 이 위젯은 **본인 계정의** 사용량만 보여준다. Claude Code 또는 Codex CLI에 로그인되어 있지 않으면 표시할 데이터 자체가 없다.
- Claude 토큰은 macOS Keychain(`Claude Code-credentials` 항목)에서, Codex 토큰은 `~/.codex/auth.json` 에서 읽으며, 각각 `api.anthropic.com` / `chatgpt.com` 으로만 전송된다. Keychain 접근 시 뜨는 최초 권한 프롬프트는 **Always Allow**를 눌러야 매 새로고침마다 재확인창이 뜨지 않는다.
- Keychain 접근 자체를 원치 않으면 `touch ~/.claude/swiftbar/.no-live` 로 라이브 조회를 끄고 로컬 캐시 파일만 읽게 할 수 있다.
- SwiftBar 플러그인은 2분(`.2m.`)마다 갱신되며, 파일명의 `.2m.` 부분을 `.1m.`, `.30s.` 등으로 바꾸면 갱신 주기를 조절할 수 있다.
- 업데이트 확인은 하루 최대 1회, `VERSION` 파일에 대한 가벼운 요청으로 이루어지며 이 요청을 원치 않으면 스크립트 하단의 `getUpdateInfo()` 호출을 주석 처리하면 된다.

## 출처

[dennykim123/claude-codex-battery](https://github.com/dennykim123/claude-codex-battery)

## 출처

- [https://github.com/dennykim123/claude-codex-battery](https://github.com/dennykim123/claude-codex-battery)
