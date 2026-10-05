---
name: phone-harness
description: 오픈소스 **phone-harness** 로 Claude Code·Codex 같은 AI 에이전트가 **실제 아이폰(맥 iPhone 미러링)·안드로이드(adb)** 를 앱 설치·탈옥 없이 직접 탭·입력·스크롤하게 만드는 설치·권한·스킬 등록·사용법 가이드입니다.
origin: content-lab
grade: S
difficulty: 중급
category: 자동화
ai_tools: ["Claude", "Claude Code", "Codex"]
sources:
  - https://github.com/ShawnPana/phone-harness
  - https://app.notion.com/p/phone-harness-3b9c601852d180209b71f3acd9e901dc?source=copy_link
originals:
  - phone-harness | AI 에이전트로 폰 제어하기 | https://github.com/ShawnPana/phone-harness
  - phone-harness-install | 아이폰 미러링 AI 에이전트 설정 | https://app.notion.com/p/phone-harness-3b9c601852d180209b71f3acd9e901dc?source=copy_link
---

# AI 에이전트로 실제 폰 조작하기

💡 **phone-harness** 를 깔면 AI 에이전트가 맥을 통해 **실제 아이폰·안드로이드 폰**의 앱을 열고, 터치하고, 글자를 입력하고, 화면을 읽습니다. 설치는 **프롬프트 한 줄**로 에이전트에게 맡기고, 사람은 **맥 권한 2개**와 폰 연결만 챙기면 됩니다.

## 이게 뭔가요?

**phone-harness** 는 AI 에이전트(Claude Code, Codex, 기타 LLM 에이전트)가 실제 스마트폰을 직접 제어하도록 만든 파이썬 기반 오픈소스 프로젝트입니다. 폰에 별도 앱을 설치하거나 루팅·탈옥할 필요가 없고, **사용자의 Mac 이 폰과의 전송 통로 역할**을 합니다.

| | iPhone | Android |
|---|---|---|
| 연결 방식 | Mac 의 **iPhone 미러링** 창 | **adb** (USB 또는 Wi-Fi) |
| 화면 읽기 | `screencapture` + Vision-framework OCR | `screencap` + 기기 자체 **접근성 트리** |
| 조작 | CGEvents (마우스·키보드 이벤트) | adb 입력 |
| 사전 준비 | 터미널 앱에 '손쉬운 사용'·'화면 기록' 권한 | '개발자 옵션' + USB 디버깅 또는 무선 디버깅 |

이렇게 하면 AI 가 사람이 폰을 만지듯 앱을 열고, 화면을 터치하고, 텍스트를 입력하고, 스크롤하며 작업을 자동화할 수 있습니다. 앱 테스트 자동화, 정보 수집, 반복적인 UI 조작을 에이전트에게 맡기고 싶은 개발자·자동화 사용자에게 맞습니다.

- 💰 유료 필요: 없음 (오픈소스)
- ✅ 무료 대안: 없음 — 이 방식으로 실제 폰을 직접 조작하는 대체 도구는 확인되지 않았습니다.

### 어떤 설치 방법을 언제 쓰나

| 상황 | 방법 | 비고 |
|---|---|---|
| Claude Code·Codex 를 쓰고 있다 (권장) | **방법 A. 에이전트에게 설치 맡기기** | 저장소 공식 안내. 클론·설치·PATH 등록·스킬 등록·온보딩까지 에이전트가 진행 |
| 에이전트 없이 직접 설치하거나, 설치 과정을 손으로 확인하고 싶다 | **방법 B. 수동 설치** | 클론·의존성 설치·권한 설정을 직접. 스킬 등록도 직접 해야 함 |

## 따라하기

### 방법 A. 에이전트에게 설치 맡기기 (권장)

1. **설치 프롬프트 붙여넣기**: Claude Code 또는 Codex 에 아래 내용을 그대로 붙여넣습니다. 에이전트가 저장소를 `~/.phone-harness` 에 클론하고, `install.md` 를 읽어 `phone-harness` 를 PATH 의 명령으로 설치한 뒤, `phone-harness skill` 출력을 본문으로 하는 에이전트 스킬 `phone-harness` 를 등록합니다. 이후 폰 작업을 시키면 에이전트가 자동으로 이 스킬을 꺼내 씁니다.

    ```text
    Set up phone-harness for me. Clone https://github.com/ShawnPana/phone-harness into ~/.phone-harness (its canonical home), read `install.md` first, install it so `phone-harness` is a command on my PATH, and register it as an agent skill named phone-harness using `phone-harness skill` as the body, so you reach for it automatically. Then read `SKILL.md` for normal usage, and always read `src/phone_harness/helpers.py` because that is where the functions are. Then read `onboarding.md` and walk me through it.
    ```

2. **온보딩 따라가기**: 에이전트가 `onboarding.md` 를 바탕으로 필요한 설정을 하나씩 안내합니다. 이때 사람이 직접 해야 하는 일은 아래 "폰 연결·권한 설정" 절입니다.
3. **연결 확인**: 아래 명령으로 설정이 올바른지 점검합니다.

    ```bash
    phone-harness --doctor
    ```

4. **기본 플랫폼 지정**: 주로 쓸 폰 종류를 정합니다.

    ```bash
    phone-harness config set platform ios
    ```

    ```bash
    phone-harness config set platform android
    ```

### 방법 B. 수동 설치

1. **저장소 클론**: 터미널에서 실행합니다.

    ```bash
    git clone https://github.com/ShawnPana/phone-harness.git
    ```

2. **디렉터리 이동**:

    ```bash
    cd phone-harness
    ```

3. **의존성 설치**:

    ```bash
    pip install -r requirements.txt
    ```

4. 저장소의 `install.md` 를 열어 `phone-harness` 명령이 PATH 에 잡히도록 마무리합니다. 사용법은 `SKILL.md`, 호출 가능한 함수 목록은 `src/phone_harness/helpers.py` 에 있습니다.
5. 아래 "폰 연결·권한 설정"을 마친 뒤 `phone-harness --doctor` 로 확인하고, `phone-harness config set platform ios` 또는 `android` 로 기본 플랫폼을 지정합니다.
6. 에이전트가 자동으로 쓰게 하려면 "에이전트 스킬로 등록하기"를 진행합니다.

### 폰 연결·권한 설정 (사람이 직접)

#### iPhone

1. Mac 에서 **iPhone 미러링** 을 켜고 폰을 연결합니다.
2. **시스템 설정(System Settings)** → **개인정보 보호 및 보안(Privacy & Security)** 을 엽니다.
3. **화면 기록(Screen Recording)** 에서 phone-harness 를 실행하는 프로그램(터미널, VS Code 등 코드를 돌리는 앱)을 찾아 허용(On)합니다. 재시동을 요구할 수 있습니다.
4. **손쉬운 사용(Accessibility)** 에서도 같은 프로그램을 허용합니다. 화면 기록은 '보기', 손쉬운 사용은 '조작'에 필요합니다.
5. 폰이 잠겨 있으면 물리적으로 잠금을 풀어 둡니다.

#### Android

1. 폰에서 **개발자 옵션**을 활성화합니다.
2. **USB 디버깅**으로 케이블 연결하거나, **무선 디버깅**을 설정합니다.
3. PIN·패턴 잠금은 에이전트가 풀 수 없으니 사용자가 직접 해제합니다.

### 에이전트 스킬로 등록하기

방법 A 의 프롬프트를 썼다면 `phone-harness skill` 출력을 본문으로 하는 스킬이 이미 등록돼 있으니 건너뜁니다. 수동으로 Codex 에 등록할 때는 스킬 이름·설명·실행 명령을 담은 설정 파일을 만들고 Codex 에 추가합니다. 아래는 그 **형태 예시**이며, 실제 파일명·진입점·인자 형식은 저장소의 `install.md`·`SKILL.md` 와 사용 중인 Codex 버전에 맞춰 바꿔야 합니다.

1. **스킬 설정 파일**: phone-harness 디렉터리에 Codex 스킬용 설정 파일(예: `codex_skill.json` 또는 `phone_harness_skill.py`)을 만듭니다.
2. **명령어 정의**:

    ```json
    {
      "name": "phone_harness",
      "description": "AI agent to control iPhone via mirroring on Mac",
      "command": "python /path/to/phone-harness/main.py --action <action> --args <args>"
    }
    ```

    - `/path/to/phone-harness/` 는 실제 설치 경로로 바꿉니다.
    - `--action` 과 `--args` 는 AI 가 수행할 작업과 인자를 넘기는 자리입니다.
3. **Codex 에 등록**: 스킬 디렉터리에 넣거나 CLI 로 등록합니다 (명령은 Codex 버전에 따라 다를 수 있습니다).

    ```bash
    codex add skill /path/to/your/skill/file.json
    ```

### 써보기

**스크립트로 직접 호출** — 에이전트가 내부적으로 하는 일과 같습니다. 메모 앱을 열고 "New Note" 를 탭한 뒤 "hello from the harness" 를 입력하고, 화면에서 읽은 텍스트 중 처음 10개를 출력합니다.

```bash
./phone-harness <<'PY'
open_app("Notes")
tap_text("New Note")
type_text("hello from the harness")
print([o["text"] for o in ocr()][:10])
PY
```

**자연어로 시키기** — 스킬 등록 후에는 에이전트에게 말로 요청하면 됩니다.

| 입력 프롬프트 | 에이전트가 내부적으로 하는 호출 (예시) |
|---|---|
| “아이폰에서 카카오톡 앱을 열어줘.” | `phone_harness --action open_app --args {"app_name": "KakaoTalk"}` |
| “아이폰 화면을 아래로 2번 스크롤해줘.” | `phone_harness --action scroll --args {"direction": "down", "times": 2}` |
| “아이폰의 검색창에 ‘AI 스킬 백과사전’이라고 입력해줘.” | `phone_harness --action type_text --args {"text": "AI 스킬 백과사전"}` |

### 이런 문제가 생기면

| 증상 | 원인·해결 |
|---|---|
| 에이전트가 아이폰 화면을 못 읽거나 조작을 못 함 | 맥 **화면 기록**·**손쉬운 사용** 권한이 코드를 실행하는 앱(터미널·VS Code 등)에 안 켜진 경우. 시스템 설정을 다시 확인하고, 켠 뒤 해당 앱을 재시작 |
| 앱 실행 실패 | 폰에 앱이 없거나 앱 이름이 정확하지 않음. 폰에 설치된 앱의 정확한 이름(예: `KakaoTalk`)으로 다시 시도 |
| 미러링 연결이 불안정 | 아이폰과 맥이 같은 Wi-Fi 에 있는지, 블루투스가 켜져 있는지 확인하고 재연결 |
| 무엇이 문제인지 모르겠음 | `phone-harness --doctor` 로 점검 |
| 아이콘 버튼을 못 누름 | OCR 은 글자만 인식. 텍스트가 없는 아이콘은 별도 이미지 인식이 필요할 수 있음 |
| 안드로이드에서 한글이 안 써짐 | adb `input text` 는 ASCII 문자만 지원 |

## 활용 예시

- **메모 자동 작성**: 위 스크립트처럼 메모 앱을 열어 새 메모를 만들고 내용을 입력한 뒤, 화면 OCR 결과로 제대로 들어갔는지 확인합니다.
- **앱 실행·탐색**: “카카오톡 열고 아래로 두 번 스크롤해줘”처럼 앱 실행과 스크롤을 이어서 시킵니다.
- **검색 입력**: 앱의 검색창에 문구를 입력해 결과 화면을 OCR 로 읽어 오게 합니다.
- **실기기 앱 테스트**: 개발 중인 앱의 UI 흐름을 실제 폰에서 반복 실행하고, 화면 텍스트로 결과를 검증합니다.
- **정보 수집**: 앱 안에서만 보이는 정보를 화면을 넘기며 읽어 정리하게 합니다.

## 💡 아이디어

- **AI 개인 비서 강화**: 알람 설정, 특정 앱 알림 확인, 간단한 정보 검색 같은 일상적인 폰 조작을 에이전트가 대신 처리합니다.
- **모바일 앱 테스트 자동화**: 실제 기기에서 UI 테스트를 자동으로 돌리고, 발견된 문제를 AI 가 리포트로 정리하게 만듭니다.
- **접근성 보조 도구**: 시각 장애가 있는 사용자를 위해 음성 명령만으로 폰의 특정 기능을 AI 가 대신 수행하도록 맞춤 설정합니다.

## 주의사항

**iPhone**
- 한 세션에서 폰 **한 대만** 제어할 수 있습니다.
- 물리적인 잠금 해제가 필요할 수 있습니다.
- OCR 은 텍스트만 인식하므로, 아이콘 형태의 버튼은 별도 이미지 인식이 필요할 수 있습니다.

**Android**
- 접근성 트리를 읽는 데 시간이 조금 걸릴 수 있습니다.
- `input text` 는 ASCII 문자만 지원하며, 복잡한 키 조합 입력은 제한적입니다.
- PIN 또는 패턴 잠금 해제는 사용자가 직접 해야 합니다.

**공통**
- 멀티터치(핀치 줌 등), 카메라/Face ID 관련 기능, DRM 보호 비디오는 지원하지 않습니다.
- 초기 연결과 인증(미러링 연결, 디버깅 허용, 맥 권한 부여)은 사용자가 직접 해야 합니다.
- 에이전트가 실제 폰을 조작하므로, 결제·송금·메시지 발송처럼 되돌리기 어려운 동작은 맡기기 전에 범위를 분명히 정해 두는 편이 안전합니다.

## 출처

- [https://github.com/ShawnPana/phone-harness](https://github.com/ShawnPana/phone-harness)
- [https://app.notion.com/p/phone-harness-3b9c601852d180209b71f3acd9e901dc?source=copy_link](https://app.notion.com/p/phone-harness-3b9c601852d180209b71f3acd9e901dc?source=copy_link)

### 합쳐진 원본 문서

이 문서는 아래 2개 문서를 하나로 합쳐 새로 정리한 것입니다.

| 원본 문서 | 원래 슬러그 | 원본 출처 |
|---|---|---|
| AI 에이전트로 폰 제어하기 | `phone-harness` | [github.com](https://github.com/ShawnPana/phone-harness) |
| 아이폰 미러링 AI 에이전트 설정 | `phone-harness-install` | [app.notion.com](https://app.notion.com/p/phone-harness-3b9c601852d180209b71f3acd9e901dc?source=copy_link) |
