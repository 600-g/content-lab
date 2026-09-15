---
name: phone-harness-install
description: 이 스킬은 **AI 에이전트가 실제 아이폰을 조작**하여 앱 실행, 터치, 입력, 스크롤 등 **자동화된 작업**을 수행하도록 설정하는 가이드입니다.
origin: content-lab
grade: A
difficulty: 초급
category: 자동화
ai_tools: ["Codex"]
sources:
  - https://app.notion.com/p/phone-harness-3b9c601852d180209b71f3acd9e901dc?source=copy_link
---

# 아이폰 미러링 AI 에이전트 설정

💡 이 스킬은 **AI 에이전트가 실제 아이폰을 조작**하여 앱 실행, 터치, 입력, 스크롤 등 **자동화된 작업**을 수행하도록 설정하는 가이드입니다.

## 이게 뭔가요?

‘phone-harness’는 AI 에이전트가 사용자의 맥(Mac) 환경에서 아이폰 미러링 창을 보면서 실제 아이폰을 직접 조작할 수 있게 해주는 도구입니다. 이를 통해 AI는 아이폰의 앱을 열고, 화면을 터치하며, 텍스트를 입력하고, 화면을 스크롤하는 등 사용자와 동일한 방식으로 아이폰을 제어할 수 있습니다. 이 가이드는 처음 사용하는 사용자도 쉽게 따라 할 수 있도록 ‘phone-harness’의 설치 및 설정 과정을 상세하게 안내합니다.

주로 AI 개발자나 자동화에 관심 있는 사용자들이 AI 에이전트에게 아이폰 기반의 작업을 위임하고자 할 때 사용됩니다. 예를 들어, 특정 앱의 테스트 자동화, 정보 수집, 혹은 반복적인 UI 조작 등을 AI에게 맡길 수 있습니다.

💰 유료 필요: 없음
✅ 무료 대안: 없음 (이와 같은 방식으로 아이폰을 직접 조작하는 무료 도구는 현재 없습니다.)

## 따라하기

### Step 1. 설치하기

1.  **GitHub 저장소 클론**: 터미널을 열고 아래 명령어를 실행하여 ‘phone-harness’ 저장소를 클론합니다.
    ```bash
    git clone https://github.com/ShawnPana/phone-harness.git
    ```
2.  **디렉토리 이동**: 클론된 디렉토리로 이동합니다.
    ```bash
    cd phone-harness
    ```
3.  **의존성 설치**: 필요한 파이썬 패키지를 설치합니다.
    ```bash
    pip install -r requirements.txt
    ```

### Step 2. 맥 권한 켜기

AI 에이전트가 맥 화면을 인식하고 상호작용하기 위해서는 화면 녹화 및 제어 권한이 필요합니다. 다음 단계를 따라 권한을 설정해주세요.

1.  **시스템 설정 열기**: 맥의 `시스템 설정(System Settings)`을 엽니다.
2.  **개인정보 보호 및 보안**: 왼쪽 사이드바에서 `개인정보 보호 및 보안(Privacy & Security)`을 선택합니다.
3.  **화면 기록**: `스크린 타임(Screen Time)` 아래에 있는 `화면 기록(Screen Recording)` 항목을 찾습니다.
4.  **권한 부여**: `화면 기록` 설정에서 ‘phone-harness’와 관련된 애플리케이션 (예: 터미널, VS Code 등 코드를 실행하는 프로그램)을 찾아 허용(On)으로 변경합니다. 필요한 경우 재시동을 요청할 수 있습니다.
5.  **실행 제어**: 만약 ‘phone-harness’가 직접적인 제어 권한을 요구한다면, `시스템 설정 > 개인정보 보호 및 보안 > 손쉬운 사용(Accessibility)`에서도 관련 항목을 찾아 허용해야 할 수 있습니다.

### Step 3. 코덱스 스킬로 등록하기

‘phone-harness’를 코덱스(Codex) 스킬로 등록하는 과정입니다. 코덱스는 AI가 외부 도구나 API를 호출할 수 있도록 돕는 프레임워크입니다. (참고: 코덱스 사용법은 해당 프레임워크의 문서를 참조하세요.)

1.  **스킬 설정 파일**: ‘phone-harness’ 디렉토리 내에 코덱스 스킬로 등록하기 위한 설정 파일(예: `codex_skill.json` 또는 `phone_harness_skill.py`)을 생성하거나 수정합니다. 이 파일에는 스킬의 이름, 설명, 실행 명령어 등이 포함됩니다.
2.  **명령어 정의**: 코덱스가 ‘phone-harness’를 실행할 수 있도록 명령어(Command)를 정의합니다. 예를 들어, 다음과 같은 형태가 될 수 있습니다.
    ```json
    {
      "name": "phone_harness",
      "description": "AI agent to control iPhone via mirroring on Mac",
      "command": "python /path/to/phone-harness/main.py --action <action> --args <args>"
    }
    ```
    *  `/path/to/phone-harness/` 는 실제 ‘phone-harness’가 설치된 경로로 변경해야 합니다.
    *  `--action` 과 `--args` 는 AI가 수행할 작업과 그 인자를 전달하는 방식입니다.
3.  **코덱스에 등록**: 정의된 스킬 설정 파일을 코덱스 프레임워크의 스킬 디렉토리에 추가하거나, 코덱스 CLI를 사용하여 등록합니다.
    ```bash
    codex add skill /path/to/your/skill/file.json
    ```
    (코덱스 등록 명령어는 실제 사용 중인 코덱스 버전에 따라 다를 수 있습니다.)

### Step 4. 이렇게 써보세요

코덱스 프롬프트에서 ‘phone-harness’ 스킬을 호출하여 아이폰 조작을 요청하는 예시입니다.

**예시 1: 특정 앱 실행하기**

*   **입력 프롬프트**: “아이폰에서 카카오톡 앱을 열어줘.”
*   **코덱스 호출 (내부적으로)**: `phone_harness --action open_app --args {"app_name": "KakaoTalk"}`

**예시 2: 화면 스크롤하기**

*   **입력 프롬프트**: “아이폰 화면을 아래로 2번 스크롤해줘.”
*   **코덱스 호출 (내부적으로)**: `phone_harness --action scroll --args {"direction": "down", "times": 2}`

**예시 3: 텍스트 입력하기**

*   **입력 프롬프트**: “아이폰의 검색창에 ‘AI 스킬 백과사전’이라고 입력해줘.”
*   **코덱스 호출 (내부적으로)**: `phone_harness --action type_text --args {"text": "AI 스킬 백과사전"}`

## 이런 문제가 생기면

*   **권한 오류**: 맥에서 화면 기록 또는 제어 권한이 제대로 설정되지 않은 경우, AI 에이전트가 아이폰 화면을 인식하지 못하거나 조작할 수 없습니다. 시스템 설정을 다시 확인하고 관련 프로그램에 권한을 부여했는지 검토하세요.
*   **앱 실행 실패**: 아이폰에 해당 앱이 설치되어 있지 않거나, 앱 이름이 정확하지 않은 경우 실행에 실패할 수 있습니다. 아이폰에 설치된 앱의 정확한 이름을 확인 후 다시 시도하세요.
*   **미러링 연결 문제**: 아이폰과 맥 간의 미러링 연결이 불안정하면 ‘phone-harness’ 작동에 문제가 발생할 수 있습니다. 두 기기가 동일한 Wi-Fi 네트워크에 연결되어 있는지, 블루투스가 켜져 있는지 확인하고, 필요하다면 재연결을 시도하세요.

매일 업데이트 되는 AI 뉴스와 트렌드가 더 궁금하다면?
@ai_freaks.kr 팔로우하고 소식 놓치지 마세요!

## 출처

[‘phone-harness’ 설치 가이드](https://app.notion.com/p/phone-harness-3b9c601852d180209b71f3acd9e901dc?source=copy_link)

## 출처

- [https://app.notion.com/p/phone-harness-3b9c601852d180209b71f3acd9e901dc?source=copy_link](https://app.notion.com/p/phone-harness-3b9c601852d180209b71f3acd9e901dc?source=copy_link)
