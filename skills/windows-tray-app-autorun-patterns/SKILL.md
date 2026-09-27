---
name: windows-tray-app-autorun-patterns
description: 윈도우 **트레이 상주 앱**에 꼭 필요한 뼈대 — UAC 없는 부팅 자동실행(작업 스케줄러), 창 없이 트레이로 시작, 중복 실행 방지 + 기존 창 불러오기, 설정 이중 저장, 윈도우 알림 꺼짐 감지, 요일 반복 예약 — 를 C# 코드 조각과 함께 정리했습니다.
origin: content-lab
grade: A
difficulty: 중급
category: 개발
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://github.com/600-g/shutdown-timer
---

# 윈도우 트레이 상주 앱 필수 패턴 (C#)

## 이게 뭔가요?

타이머·알림·감시 도구처럼 **항상 켜져 있어야 하는 윈도우 앱**의 공통 뼈대입니다. 자동 종료 타이머에서 실제로 버그를 겪고 고친 형태 그대로입니다.

## 따라하기

1. **UAC 없이 부팅 자동실행 — 작업 스케줄러** (시작프로그램 레지스트리는 관리자 앱이면 매번 UAC 창이 뜸):
```text
schtasks /create /F /TN "MyApp_600g" /TR "\"C:\경로\MyApp.exe\" --tray" /SC ONLOGON /RL HIGHEST
schtasks /query /TN "MyApp_600g"          ← 종료코드 0 이면 켜져 있음 (토글 상태 표시용)
schtasks /delete /F /TN "MyApp_600g"      ← 끄기
```
   `/RL HIGHEST` 가 관리자 권한 앱을 UAC 없이 띄우는 핵심. 등록 자체는 관리자 권한 필요.
2. **자가 치유** — 예전 버전이 `--tray` 없이 등록했다면 시작 시 창이 뜬다 → 앱 시작 때 `/query /V /FO LIST` 결과에 `--tray` 가 없으면 조용히 재등록(`EnsureAutoRunTray`). exe 경로가 바뀐 경우도 같은 방식으로 갱신.
3. **창 없이 트레이로 시작** — `--tray` 인자면 창이 한 프레임도 안 깜빡이게:
```csharp
protected override void SetVisibleCore(bool value) {
    if (startInTray && !allowVisible) { value = false; if (!IsHandleCreated) CreateHandle(); }
    base.SetVisibleCore(value);
}
```
   ⚠️ 이 경우 `Shown` 이벤트가 **아예 안 온다** → 시작 시 해야 할 일(업데이트 확인 타이머 등)은 **생성자**에.
4. **X 버튼 = 트레이로 숨김, 완전 종료는 트레이 메뉴에서만** — `OnFormClosing` 에서 `reallyExit` 플래그가 아니면 `e.Cancel = true; Hide();`. 최초 1회만 "트레이에서 계속 실행 중" 풍선.
5. **중복 실행 방지 + 기존 창 불러오기**:
```csharp
bool created; mutex = new Mutex(true, "Global\\MyApp600g_SingleInstance", out created);
if (!created) { PostMessage((IntPtr)0xFFFF /*HWND_BROADCAST*/, WM_SHOWME, IntPtr.Zero, IntPtr.Zero); return; }
// 폼: WM_SHOWME = RegisterWindowMessage("MyApp600g_ShowMe");  WndProc 에서 받으면 RestoreFromTray()
```
   `RegisterWindowMessage` 는 정적 생성자에서 try/catch (mono·테스트 환경 보호).
6. **관리자 권한 재실행** — 관리자 아니면 `Verb="runas"` 로 자기 자신을 `--noelevate` 붙여 재실행, 사용자가 UAC 를 취소하면 일반 권한으로라도 계속(무한 루프 방지용 플래그).
7. **설정 저장 이중화** — `HKCU\Software\MyApp` 레지스트리 + `%AppData%` 파일에 같이 저장, 읽을 땐 둘 다 읽어 **병합 후 저장(merge-before-save)** → 한쪽이 지워져도 복구. 저장 형식은 `key=v1|v2|v3` 파이프 구분 + **필드 개수로 구버전 호환**(`Split('|', 7)` 후 length 7/6/5 분기, 없는 필드는 기본값). 문자열 필드의 `|`·줄바꿈은 인코딩.
8. **윈도우 알림 꺼짐 감지** — 꺼져 있으면 트레이 풍선·토스트가 안 보인다:
```csharp
// HKCU\Software\Microsoft\Windows\CurrentVersion\PushNotifications  ToastEnabled == 0 → 꺼짐
Process.Start(new ProcessStartInfo("ms-settings:notifications") { UseShellExecute = true });  // 설정 바로 열기
```
   설정 화면에 경고 라벨 + 누르면 알림 설정 열기로 유도.
9. **요일 반복 예약 (비트마스크)** — bit0=월 … bit6=일, `0x7F`=매일(기본), `0`=1회성(울리면 자동 OFF):
```csharp
static int DowBit(DateTime d) { return ((int)d.DayOfWeek + 6) % 7; }
DateTime NextDailyTarget(int minutesOfDay, int mask) {
    DateTime now = DateTime.Now, cand = now.Date.AddMinutes(minutesOfDay);
    if (cand <= now) cand = cand.AddDays(1);
    for (int i = 0; i < 8; i++, cand = cand.AddDays(1))
        if (mask == 0 || (mask & 0x7F) == 0x7F || (mask & (1 << DowBit(cand))) != 0) return cand;
    return cand;
}
// 울린 뒤: mask != 0 → 다시 NextDailyTarget 로 재예약, mask == 0 → 토글 OFF
```
10. **크래시 보고** — `Application.SetUnhandledExceptionMode(CatchException)` + `ThreadException`/`UnhandledException` 에서 메시지 표시·로그. 조용히 꺼지는 앱이 가장 나쁘다.
11. **DPI** — `Main` 첫 줄 `SetProcessDPIAware()`.

## 활용 예시

- 자동 종료 타이머(종료 예약·프로그램 종료·반복 알림), 클립보드 관리자, 폴더 감시 백업 도구, 휴식 알리미.

## 주의사항

- 작업 스케줄러 등록/삭제·레지스트리·토스트는 **리눅스/mono 에서 검증 불가** → 윈도우 실기 확인 필수.
- Mutex 이름에 `Global\` 을 붙이면 다른 사용자 세션까지 한 개로 제한된다(의도 확인).
- `SetVisibleCore` 로 숨긴 상태에서 `Show()` 하려면 `allowVisible = true` 를 먼저.
- 종료 확인 모달("예약이 진행 중입니다")은 자동 업데이트 교체 시 건너뛰는 플래그가 필요하다(→ `self-updating-app-release-pipeline`).
