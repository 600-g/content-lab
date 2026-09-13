---
name: phone-harness
description: AI 에이전트가 **실제 스마트폰을 제어**할 수 있게 해주는 파이썬 기반의 오픈소스 도구입니다. **iPhone** 및 **Android** 기기를 지원하며, 별도 앱 설치 없이 Mac에서 직접 조작합니다.
origin: content-lab
grade: A
difficulty: 중급
category: 자동화
ai_tools: ["Claude", "Claude Code", "Codex"]
sources:
  - https://github.com/ShawnPana/phone-harness
---

# AI 에이전트로 폰 제어하기

💡 AI 에이전트가 **실제 스마트폰을 제어**할 수 있게 해주는 파이썬 기반의 오픈소스 도구입니다. **iPhone** 및 **Android** 기기를 지원하며, 별도 앱 설치 없이 Mac에서 직접 조작합니다.

## 이게 뭔가요?

**Phone Harness**는 AI 에이전트(Claude Code, Codex, LLM 등)가 실제 스마트폰을 직접 제어할 수 있도록 설계된 파이썬 기반의 오픈소스 프로젝트입니다. 별도의 앱 설치나 루팅/탈옥 없이, Mac 환경에서 iPhone은 'iPhone 미러링' 창을 통해, Android는 adb(USB 또는 Wi-Fi)를 통해 연결됩니다. 사용자의 Mac이 전화기의 전체 전송 역할을 수행하며, iPhone의 경우 `screencapture`와 Vision-framework OCR로 화면을 인식하고 CGEvents로 조작하며, Android는 `screencap`과 기기 자체의 접근성 트리를 활용하여 정확한 텍스트 인식 및 조작을 수행합니다. 이를 통해 AI는 마치 사용자가 직접 휴대폰을 다루는 것처럼 앱을 열고, 텍스트를 입력하고, 화면을 탐색하는 등의 작업을 자동화할 수 있습니다.

💰 유료 필요: 해당 없음
✅ 무료 대안: 없음 (기능의 특수성상 대체 도구 부재)

## 따라하기

1.  **Phone Harness 설치 및 설정**: 
    Claude Code 또는 Codex 프롬프트에 아래 내용을 붙여넣어 설치를 자동화합니다.
    ```text
    Set up phone-harness for me. Clone https://github.com/ShawnPana/phone-harness into ~/.phone-harness (its canonical home), read `install.md` first, install it so `phone-harness` is a command on my PATH, and register it as an agent skill named phone-harness using `phone-harness skill` as the body, so you reach for it automatically. Then read `SKILL.md` for normal usage, and always read `src/phone_harness/helpers.py` because that is where the functions are. Then read `onboarding.md` and walk me through it.
    ```

2.  **초기 설정 진행**: 
    AI 에이전트가 `onboarding.md` 파일을 기반으로 사용자에게 필요한 설정을 안내합니다.
    *   **iPhone**: Mac의 'iPhone 미러링' 기능을 활성화하고, 터미널 앱에 '손쉬운 사용' 및 '화면 기록' 권한을 부여합니다. (macOS 시스템 설정 → 개인 정보 보호 및 보안)
    *   **Android**: '개발자 옵션'을 활성화하고, USB 연결 또는 무선 디버깅 설정을 완료합니다.

3.  **연결 확인**: 
    `phone-harness --doctor` 명령어를 실행하여 설정이 올바르게 되었는지 확인합니다.

4.  **기본 플랫폼 설정**: 
    `phone-harness config set platform ios` 또는 `phone-harness config set platform android` 명령어로 사용할 기본 플랫폼을 설정합니다.

## 활용 예시

AI 에이전트가 Phone Harness를 사용하여 휴대폰에서 작업을 수행하는 예시입니다.

```bash
./phone-harness <<'PY'
open_app("Notes")
tap_text("New Note")
type_text("hello from the harness")
print([o["text"] for o in ocr()][:10])
PY
```

위 코드는 "Notes" 앱을 열고, "New Note" 버튼을 탭한 후, "hello from the harness"라는 텍스트를 입력하고, 화면에 표시된 텍스트 중 처음 10개를 출력하는 과정을 보여줍니다.

## 💡 아이디어

*   **AI 기반 개인 비서 강화**: AI가 사용자의 일상적인 휴대폰 조작(예: 알람 설정, 특정 앱 알림 확인, 간단한 정보 검색)을 자동으로 수행하여 개인 비서 역할을 더욱 강화할 수 있습니다.
*   **모바일 앱 테스트 자동화**: 개발자들은 Phone Harness를 활용하여 실제 기기에서의 앱 UI 테스트 과정을 자동화하고, 발견된 문제점을 AI가 자동으로 리포트하도록 구축할 수 있습니다.
*   **접근성 향상 도구**: 시각 장애가 있는 사용자들을 위해, 음성 명령만으로 휴대폰의 특정 기능을 AI가 대신 수행해주도록 맞춤 설정하는 보조 도구로 활용될 수 있습니다.

## 주의사항

*   **iPhone**: 현재 세션에서 하나의 전화기만 제어 가능합니다. 물리적인 전화기 잠금 해제가 필요할 수 있습니다. OCR은 텍스트만 인식하며, 아이콘 형태의 버튼은 별도의 이미지 인식이 필요할 수 있습니다.
*   **Android**: 접근성 트리를 읽는 데 시간이 다소 소요될 수 있습니다. `input text`는 ASCII 문자만 지원하며, 복잡한 키 조합 입력은 제한적입니다. PIN 또는 패턴 잠금 해제는 사용자의 직접적인 개입이 필요합니다.
*   **공통**: 멀티터치(핀치 줌 등), 카메라/Face ID 관련 기능, DRM 보호 비디오는 지원하지 않습니다. 초기 연결 및 인증 과정은 사용자가 직접 수행해야 합니다.

## 출처

[ShawnPana/phone-harness](https://github.com/ShawnPana/phone-harness)

## 출처

- [https://github.com/ShawnPana/phone-harness](https://github.com/ShawnPana/phone-harness)
