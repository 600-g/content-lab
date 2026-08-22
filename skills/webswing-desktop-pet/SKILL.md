---
name: webswing-desktop-pet
description: 열려 있는 **창 위에서 거미줄을 타고 날아다니는** 데스크톱 펫 스킬입니다.
origin: content-lab
grade: A
difficulty: 중급
category: 기타
ai_tools: []
sources:
  - https://joowonkoh.com/playground/webswing?fbclid=PAVERFWATld71wZG9mAmZkaWQWUMKVlajuz_FkwWfv_CISbvn90Q6JbGV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABpwFYoSVao__eu75-GVkCux6sksglj8gGLC7o0yO9YPThstkhxKZJqptaidC7_aem_UXMcK1WEfr1r-QfyfwYCIg
---

# 창 사이를 나는 데스크톱 펫

💡 열려 있는 **창 위에서 거미줄을 타고 날아다니는** 데스크톱 펫 스킬입니다.

## 이게 뭔가요?

**WebSwing**은 실제 열려 있는 창의 모서리에 거미줄을 걸고 그 위를 날아다니는 독특한 데스크톱 펫 애플리케이션입니다. 맥과 윈도우 모두에서 사용할 수 있으며, 사용자의 행동에 따라 반응하는 귀여운 특징을 가지고 있습니다.

평소에는 알아서 창 사이를 돌아다니거나 창 위를 걸어 다닙니다. 사용자가 타자를 치면 거미줄을 타고 올라가고, 클릭한 위치에는 거미줄을 쏘기도 합니다. 필요 없을 때는 눈만 남기고 사라지게 할 수도 있어 사용자 경험을 방해하지 않습니다.

WebSwing은 배경화면 위에 투명한 레이어를 띄워 그 위에서 히어로(펫)가 움직이는 방식으로 작동합니다. 거미줄이 걸리는 지점은 단순히 그림이 아니라 **현재 활성화된 창의 윗변**입니다. 따라서 크롬과 같은 창을 옮기면 펫이 매달릴 자리도 함께 움직이며, 창을 닫으면 해당 발판이 사라집니다.

💰 **유료 정보:** WebSwing은 무료로 제공되는 애플리케이션입니다. 별도의 유료 결제나 구독이 필요하지 않습니다.

## 따라하기

**macOS 설치 및 설정**

1.  **다운로드 및 압축 해제:** WebSwing.zip 파일을 다운로드하여 압축을 해제하면 `WebSwing.app` 파일이 나옵니다.
2.  **응용 프로그램 폴더로 이동:** `WebSwing.app` 파일을 '응용 프로그램' 폴더로 옮깁니다. (다운로드 폴더에 그대로 두면 실수로 삭제할 위험이 있습니다.)
3.  **실행:** `WebSwing.app`을 더블클릭하여 실행합니다. macOS에서 애플 공증을 받은 앱이므로 경고 없이 바로 열립니다.
4.  **메뉴 막대 아이콘 확인:** 실행 후에는 Dock에 아이콘이 나타나지 않으며, 화면 오른쪽 상단 메뉴 막대에 거미줄 모양 아이콘이 생성됩니다. 모드 전환 및 종료는 이 메뉴를 통해 할 수 있습니다.

**Windows 설치 및 설정**

1.  **.NET 9 데스크톱 런타임 설치:** WebSwing은 .NET 9 런타임을 필요로 합니다. 먼저 아래 링크에서 .NET 9 데스크톱 런타임 (x64) 설치 파일을 받아 설치합니다. (약 60MB)
    *   [.\NET 9 데스크톱 런타임 (x64) 바로 받기](https://download.visualstudio.microsoft.com/download/pr/27020197/e0b97f6f674903001b6f517505873843/windowsdesktop.runtime.net9.x64.exe)
2.  **WebSwing 파일 다운로드:** 런타임 설치 후, 아래 링크에서 WebSwing (Windows) 파일을 다운로드합니다. (126KB)
    *   [WebSwing (Windows) 내려받기](https://github.com/joowonkoh/webswing/releases/download/v1.0.2/WebSwing.zip)
3.  **압축 해제 및 폴더 유지:** 다운로드한 zip 파일의 압축을 풀고, `WebSwing.exe` 파일과 함께 `DLL` 및 `Resources` 폴더가 같은 위치에 있도록 유지합니다. `WebSwing.exe` 혼자서는 실행되지 않습니다.
4.  **실행:** `WebSwing.exe`를 실행합니다. Windows SmartScreen에서 보안 경고가 표시될 수 있습니다. '추가 정보'를 클릭하고 '실행'을 선택하면 이후에는 경고 없이 실행됩니다.
5.  **알림 영역 아이콘 확인:** 실행 후, Windows 작업 표시줄 오른쪽 알림 영역(시계 옆 '^' 아이콘)에 거미줄 모양 아이콘이 나타납니다. Windows 11에서는 기본적으로 숨겨져 있을 수 있으므로, 꺼내서 작업 표시줄에 고정하면 편리합니다.

**주요 기능 및 조작법 (macOS & Windows 공통)**

*   **펫 모드 (기본):**
    *   알아서 창 사이를 스윙하고, 창 위를 걸어 다닙니다.
    *   가끔 사용자의 커서 쪽으로 날아옵니다.
    *   화면의 아무 곳이나 클릭하면 해당 지점에 거미줄을 쏘고 올라갑니다.
*   **타자 모드 (`⌘⇧T` / `Ctrl+Shift+T`):**
    *   화면 아래에서 대기하다가 사용자가 타자를 치면 거미줄을 던지고 올라갑니다.
    *   타자를 멈추면 천천히 내려옵니다. 내려오는 중 다시 타자를 치면 그 자리에서 즉시 다시 올라갑니다.
    *   바닥에 닿으면 거미줄이 사라집니다.
    *   어느 앱에서 타자를 치든 반응합니다.
    *   빠르게 오래 칠수록 더 높이 올라가며, 한 문장 정도 치면 화면 꼭대기까지 도달할 수 있습니다.
*   **게임 모드 (`⌘⇧S` / `Ctrl+Shift+S`):**
    *   사용자가 직접 펫을 조종할 수 있습니다.
    *   점수나 목표는 없습니다.
    *   바닥에서 놓으면 떨어지고, 올라가는 중에 놓으면 날아갑니다. 타이밍이 중요합니다.
    *   **게임 모드 조작:**
        *   `Space / 클릭`: 커서 방향으로 거미줄 발사 / 떼면 발사 중지
        *   `A · D`: 좌우 조종, 스윙에 힘 싣기
        *   `S`: 줄 감기 (끝까지 감으면 창턱 위로 올라섬)
        *   `W`: 점프
        *   `Esc`: 원래 모드로 복귀
*   **숨기기 / 다시 부르기 (`⌘⇧H` / `Ctrl+Shift+H`):**
    *   화면 맨 아래로 내려가 눈만 남기고 나머지는 투명해집니다.
    *   다시 실행하거나 메뉴의 '눈' 아이콘을 클릭하면 원래대로 돌아와, 이전에 사용하던 모드를 그대로 이어서 진행합니다.
    *   회의 화면 공유 직전 등에 유용합니다.

**추가 설정 (메뉴 막대/트레이 메뉴)**

*   **Size:** 펫의 크기를 Tiny(0.5x)부터 Large(1.5x)까지 5단계로 조절할 수 있습니다. 크기 변경 시 그림뿐만 아니라 물리적인 크기도 함께 조절되어 창턱에 발이 제대로 닿도록 유지됩니다.
*   **Display (Windows) / Monitor (macOS):**
    *   **macOS:** 어느 화면에 펫이 살지 선택할 수 있습니다. 화면 사이를 건너다니지는 못합니다.
    *   **Windows:** 기본적으로 모든 모니터를 하나의 연속된 화면처럼 인식하여 건너다닐 수 있습니다. 특정 모니터만 선택하여 그 화면에서만 동작하도록 설정할 수도 있습니다. (발표나 작업 중인 화면에 끼어들지 않게 할 때 유용)
    *   화면을 변경하면 현재 진행 중이던 동작(스윙 등)은 끊어지고 새 화면에서 다시 시작됩니다.
*   **Wander Along the Bottom (Windows):** 타자 모드에서 바닥에 있을 때, 펫이 어슬렁거릴지 아니면 내린 자리에 그대로 서 있을지를 설정할 수 있습니다. 이 설정은 다음 실행 시에도 기억됩니다.

**알려진 한계점**

*   **메인 디스플레이 동작:** macOS 버전은 메인 디스플레이에서만 정상적으로 동작하며, 외장 모니터에서는 지원되지 않습니다.
*   **전체 화면 앱:** 전체 화면으로 실행된 앱 위에서는 창 정보를 읽을 수 없어 펫이 화면 바닥에서만 동작합니다.

## 활용 예시

*   **업무 집중력 향상:** 지루할 수 있는 코딩이나 문서 작업 중 귀여운 펫이 창 위를 돌아다니거나 스윙하는 모습을 보며 잠시 휴식을 취하고 집중력을 환기할 수 있습니다.
*   **개인화된 데스크톱 경험:** 자신만의 개성 있는 바탕화면을 꾸미고 싶을 때, WebSwing 펫을 통해 역동적이고 재미있는 요소를 추가하여 컴퓨터 사용 경험을 더욱 즐겁게 만들 수 있습니다.
*   **발표 준비:** 화면 공유 직전, `⌘⇧H` (또는 `Ctrl+Shift+H`) 단축키를 눌러 펫을 잠시 눈만 남기고 숨겨서 깔끔한 화면을 유지할 수 있습니다.

## 출처

*   [WebSwing — 창 사이를 날아다니는 데스크톱 펫 (맥 · 윈도우)](https://joowonkoh.com/playground/webswing?fbclid=PAVERFWATld71wZG9mAmZkaWQWUMKVlajuz_FkwWfv_CISbvn90Q6JbGV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQ1NTABpwFYoSVao__eu75-GVkCux6sksglj8gGLC7o0yO9YPThstkhxKZJqptaidC7_aem_UXMcK1WEfr1r-QfyfwYCIg)


## 출처

- [https://joowonkoh.com/playground/webswing?fbclid=PAVERFWATld71wZG9mAmZkaWQWUMKVlajuz_FkwWfv_CISbvn90Q6JbGV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABpwFYoSVao__eu75-GVkCux6sksglj8gGLC7o0yO9YPThstkhxKZJqptaidC7_aem_UXMcK1WEfr1r-QfyfwYCIg](https://joowonkoh.com/playground/webswing?fbclid=PAVERFWATld71wZG9mAmZkaWQWUMKVlajuz_FkwWfv_CISbvn90Q6JbGV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABpwFYoSVao__eu75-GVkCux6sksglj8gGLC7o0yO9YPThstkhxKZJqptaidC7_aem_UXMcK1WEfr1r-QfyfwYCIg)
