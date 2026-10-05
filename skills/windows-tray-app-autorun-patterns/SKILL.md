---
name: windows-tray-app-autorun-patterns
description: C# **WinForms** 윈도우 상주 앱을 만드는 전 과정 — 트레이 상주·**작업 스케줄러** 자동실행·중복 실행 방지 뼈대, 오너드로우 **아이폰풍 UI**, 윈도우 없이 **mono mcs** 로 단일 exe 빌드하고 **Xvfb** 스크린샷·픽셀 측정으로 화면 검증까지 코드 조각과 함께 정리했습니다.
origin: content-lab
grade: A
difficulty: 고급
category: 개발
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://github.com/600-g/shutdown-timer
originals:
  - windows-tray-app-autorun-patterns | 윈도우 트레이 상주 앱 필수 패턴 (C#) | https://github.com/600-g/shutdown-timer
  - winforms-iphone-style-ownerdraw-ui | WinForms 아이폰풍 오너드로우 UI 기법 | https://github.com/600-g/shutdown-timer
  - winforms-mono-cross-build-linux | 리눅스에서 윈도우 exe 빌드 + 화면 검증 (mono) | https://github.com/600-g/shutdown-timer
---

# 윈도우 트레이 상주 앱 만들기

💡 **트레이 상주 뼈대**(자동실행·중복 실행·설정 저장) → **오너드로우 아이폰풍 UI** → **mono 크로스 빌드 + Xvfb 화면 검증 + DLL 0개 단일 exe** 까지, 실제 앱을 70회 넘게 다듬으며 굳힌 C# WinForms 패턴입니다.

## 이게 뭔가요?

타이머·알림·감시 도구처럼 **항상 켜져 있어야 하는 윈도우 앱**을 C# WinForms 로 만들 때 필요한 것을 한 문서로 묶었습니다. 자동 종료 타이머(종료 예약·프로그램 종료·반복 알림)를 개발하며 실제로 버그를 겪고 고친 형태 그대로이며, build 1~69 를 전부 윈도우 PC 없이 리눅스에서 빌드·검증했습니다.

세 부분으로 구성됩니다.

| 부분 | 다루는 것 | 핵심 기술 |
|---|---|---|
| 1. 상주 앱 뼈대 | UAC 없는 부팅 자동실행, 창 없이 트레이로 시작, X 버튼 = 숨김, 중복 실행 방지, 관리자 재실행, 설정 이중 저장, 알림 꺼짐 감지, 요일 반복 예약, 크래시 보고 | `schtasks`, `SetVisibleCore`, `Mutex` + `RegisterWindowMessage`, 레지스트리 |
| 2. 아이폰풍 UI | 카드·토글·스테퍼·리스트를 직접 그려 아이폰 설정 앱 같은 룩 | `TextRenderer`, `PixelOffsetMode.Half`, 더블버퍼, `GraphicsPath`, 오너드로우 ListBox |
| 3. 빌드·검증·배포 | 윈도우 없이 단일 exe 빌드, 가상 화면에 띄워 스크린샷·픽셀 측정 | `mcs -sdk:4.5 -target:winexe`, 리소스 내장, Xvfb + xdotool + ImageMagick + PIL |

### 어떤 문제에 어느 절을 보나

| 증상·목표 | 볼 곳 |
|---|---|
| 자동실행할 때마다 UAC 창이 뜬다 | 1-1 작업 스케줄러 |
| 부팅 때 창이 한 번 깜빡이며 뜬다 / 업데이트 확인이 안 돈다 | 1-2, 1-3 |
| 두 번 실행하면 앱이 두 개 뜬다 | 1-5 |
| 설정이 가끔 날아간다 / 구버전 설정 호환 | 1-7 |
| 알림이 안 보인다는 사용자 | 1-8 |
| 글자가 흐릿하다 / 1px 선이 연하다 | 2-1, 2-2, 1-11 |
| 1초마다 화면이 깜빡인다 | 2-3 |
| 리스트 스크롤바가 카드 디자인을 깬다 | 2-4, 2-5 |
| 클릭과 더블클릭이 겹친다 | 2-8 |
| 윈도우 PC 가 없다 / 맥·클라우드·CI 에서 빌드해야 한다 | 3부 전체 |
| AI 에게 UI 미세 조정을 시키고 결과를 확인하고 싶다 | 3-4, 3-5 |

윈도우 PC 없이 개발한다면 **3-1 설치와 3-2 빌드 스크립트부터** 준비해 두고 1부·2부 코드를 붙여 가며 매번 빌드·캡처로 확인하는 순서가 가장 빠릅니다.

## 따라하기

### 1부. 트레이 상주 앱 뼈대

#### 1-1. UAC 없이 부팅 자동실행 — 작업 스케줄러

시작프로그램 레지스트리는 관리자 앱이면 매번 UAC 창이 뜹니다. 작업 스케줄러를 씁니다.

```text
schtasks /create /F /TN "MyApp_600g" /TR "\"C:\경로\MyApp.exe\" --tray" /SC ONLOGON /RL HIGHEST
schtasks /query /TN "MyApp_600g"          ← 종료코드 0 이면 켜져 있음 (토글 상태 표시용)
schtasks /delete /F /TN "MyApp_600g"      ← 끄기
```

`/RL HIGHEST` 가 관리자 권한 앱을 UAC 없이 띄우는 핵심입니다. 등록 자체는 관리자 권한이 필요합니다.

#### 1-2. 자동실행 자가 치유

예전 버전이 `--tray` 없이 등록했다면 시작 시 창이 뜹니다. 앱 시작 때 `/query /V /FO LIST` 결과에 `--tray` 가 없으면 조용히 재등록합니다(`EnsureAutoRunTray`). exe 경로가 바뀐 경우도 같은 방식으로 갱신합니다.

#### 1-3. 창 없이 트레이로 시작

`--tray` 인자면 창이 한 프레임도 깜빡이지 않게 합니다.

```csharp
protected override void SetVisibleCore(bool value) {
    if (startInTray && !allowVisible) { value = false; if (!IsHandleCreated) CreateHandle(); }
    base.SetVisibleCore(value);
}
```

⚠️ 이 경우 `Shown` 이벤트가 **아예 안 옵니다** → 시작 시 해야 할 일(업데이트 확인 타이머 등)은 **생성자**에 둡니다. 숨긴 상태에서 `Show()` 하려면 `allowVisible = true` 를 먼저 설정합니다.

#### 1-4. X 버튼 = 트레이로 숨김, 완전 종료는 트레이 메뉴에서만

`OnFormClosing` 에서 `reallyExit` 플래그가 아니면 `e.Cancel = true; Hide();`. 최초 1회만 "트레이에서 계속 실행 중" 풍선을 띄웁니다.

#### 1-5. 중복 실행 방지 + 기존 창 불러오기

```csharp
bool created; mutex = new Mutex(true, "Global\\MyApp600g_SingleInstance", out created);
if (!created) { PostMessage((IntPtr)0xFFFF /*HWND_BROADCAST*/, WM_SHOWME, IntPtr.Zero, IntPtr.Zero); return; }
// 폼: WM_SHOWME = RegisterWindowMessage("MyApp600g_ShowMe");  WndProc 에서 받으면 RestoreFromTray()
```

`RegisterWindowMessage` 는 정적 생성자에서 try/catch 로 감쌉니다(mono·테스트 환경 보호 — 3부에서 mono 로 실행할 때 여기서 터지지 않게).

#### 1-6. 관리자 권한 재실행

관리자가 아니면 `Verb="runas"` 로 자기 자신을 `--noelevate` 붙여 재실행합니다. 사용자가 UAC 를 취소하면 일반 권한으로라도 계속 실행합니다(무한 루프 방지용 플래그).

#### 1-7. 설정 저장 이중화

- `HKCU\Software\MyApp` 레지스트리 + `%AppData%` 파일에 같이 저장하고, 읽을 땐 둘 다 읽어 **병합 후 저장(merge-before-save)** → 한쪽이 지워져도 복구됩니다.
- 저장 형식은 `key=v1|v2|v3` 파이프 구분 + **필드 개수로 구버전 호환**(`Split('|', 7)` 후 length 7/6/5 분기, 없는 필드는 기본값).
- 문자열 필드의 `|`·줄바꿈은 인코딩합니다.

#### 1-8. 윈도우 알림 꺼짐 감지

꺼져 있으면 트레이 풍선·토스트가 안 보입니다.

```csharp
// HKCU\Software\Microsoft\Windows\CurrentVersion\PushNotifications  ToastEnabled == 0 → 꺼짐
Process.Start(new ProcessStartInfo("ms-settings:notifications") { UseShellExecute = true });  // 설정 바로 열기
```

설정 화면에 경고 라벨을 두고, 누르면 알림 설정을 열도록 유도합니다.

#### 1-9. 요일 반복 예약 (비트마스크)

bit0=월 … bit6=일, `0x7F`=매일(기본), `0`=1회성(울리면 자동 OFF).

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

UI 에서는 월~일 토글 칩으로 보여주고, 기본은 매일, 전부 끄면 1회성으로 동작합니다.

#### 1-10. 크래시 보고

`Application.SetUnhandledExceptionMode(CatchException)` + `ThreadException`/`UnhandledException` 에서 메시지를 표시하고 로그를 남깁니다. 조용히 꺼지는 앱이 가장 나쁩니다.

#### 1-11. DPI 선명도

`Main` 첫 줄에 `SetProcessDPIAware()`(user32)를 호출합니다. 125%/150% 배율에서 윈도우가 창을 통째 확대해 뿌옇게 되는 것을 막습니다. 폰트는 **픽셀 단위**(`GraphicsUnit.Pixel`)로 만들어 크기를 일정하게 유지합니다.

### 2부. 아이폰풍 오너드로우 UI

기본 컨트롤은 최소화하고 카드·토글·스테퍼·리스트를 전부 직접 그립니다. 문제가 됐던 증상 → 원인 → 해법 순서입니다.

#### 2-1. 텍스트는 GDI `TextRenderer` 로 통일

`Graphics.DrawString`(GDI+)은 흐릿하고 글자 폭이 다릅니다. `TextRenderer.DrawText(g, text, font, rect, color, TextFormatFlags.VerticalCenter | ...)` 로 ClearType 선명하게 그립니다. (3-3 의 내장 폰트를 `AddFontMemResourceEx` 로도 등록해야 `TextRenderer` 에서 쓸 수 있습니다.)

#### 2-2. 1px 테두리가 "지워진 것처럼 연하게" 보일 때

안티앨리어싱 1px 선이 두 픽셀에 반씩 걸친 것입니다. `g.PixelOffsetMode = PixelOffsetMode.Half;` + 선 두께 1 + 색을 한 톤 진하게 합니다. 고친 뒤에는 3-5 픽셀 측정으로 한 칸인지 확인합니다.

#### 2-3. 깜빡임 제거

- 모든 커스텀 컨트롤: `SetStyle(ControlStyles.OptimizedDoubleBuffer | ControlStyles.AllPaintingInWmPaint | ControlStyles.UserPaint | ControlStyles.ResizeRedraw, true);`
- 1초 타이머로 매번 `Invalidate()` 하지 말고 **표시 내용 서명(sig) 비교**로 바뀐 경우에만 다시 그립니다.

```csharp
string sig = text + "|" + count + "|" + state;
if (sig == islandSig) return;   // 그대로면 안 그림
islandSig = sig; island.Invalidate();
```

- 무효화 영역도 전체가 아니라 바뀐 사각형만 지정합니다.

#### 2-4. ListBox 스크롤바 숨기기

`DrawMode.OwnerDrawFixed` 리스트박스를 카드보다 **오른쪽으로 넓게** 만들어 스크롤바를 카드 밖으로 밀고, `Region` 으로 카드 안쪽 폭까지만 그리게 잘라 카드 테두리를 덮지 않게 합니다(`ClipWidth`). 휠 스크롤은 그대로 동작합니다. 이 Region 은 매 Resize 때 다시 계산해야 합니다.

#### 2-5. 스크롤 위치 표시

스크롤바를 숨겼으면 항목이 넘칠 때만 오른쪽에 작은 썸(thumb) 막대를 직접 그립니다: 높이 = 보이는 비율, 위치 = `TopIndex / (Count - 보이는 수)`.

#### 2-6. 빈 목록 안내문

네이티브 리스트 위에 그리면 뭉개집니다 → 리스트를 투명(빈 Region) 처리하고 **부모 카드가** "항목 없음" 안내를 그립니다.

#### 2-7. 아이콘은 `GraphicsPath` 벡터로

이모지·SVG 는 환경마다 깨지고, mono 는 SVG·컬러 이모지 글리프를 제대로 못 그립니다. 말풍선·종·톱니를 도형으로 그리고, 켜짐/꺼짐은 **색으로만** 구분합니다(onCol/offCol).

#### 2-8. 단일클릭 vs 더블클릭 충돌

MouseDown 즉시 수정 모드 진입이 더블클릭과 겹칩니다 → **260ms 타이머**로 판별합니다.

```csharp
// MouseDown: almPendIdx = idx; almClickT.Stop(); almClickT.Start();   (Interval = 260)
// Tick:      almClickT.Stop(); if (!almDbl) SingleClick(almPendIdx); almDbl = false;
// DoubleClick: almDbl = true; almClickT.Stop(); OpenEditor(idx);
```

#### 2-9. 선택 해제 동선

리스트가 꽉 차면 빈 곳이 없어 선택을 못 풉니다 → 패널·부모의 **아무 빈 곳 클릭**에도 해제(`panel.MouseDown += delegate { ReleaseEdit(); };`)하고, 같은 항목 재클릭도 토글 해제합니다.

#### 2-10. 윈도우 표준 텍스트 조작 보강

WinForms TextBox 는 더블클릭이 단어만 선택하고 Ctrl+A 가 기본 미지원입니다.

```csharp
tb.DoubleClick += delegate { tb.SelectAll(); };
tb.KeyDown += delegate(object s, KeyEventArgs k) {
    if (k.Control && k.KeyCode == Keys.A) { tb.SelectAll(); k.SuppressKeyPress = true; k.Handled = true; } };
```

메모장형 입력은 **Enter = 저장, Shift+Enter = 줄바꿈**(KeyDown 에서 Enter && !Shift → 저장 후 SuppressKeyPress).

#### 2-11. 광학 보정

같은 크기인데 테두리 있는 버튼이 더 커 보이면 테두리 버튼을 1px 안쪽으로 줄입니다(optical inset).

#### 2-12. 다크 모드

색 리터럴 금지, 전부 `Theme.*` 토큰으로 씁니다. 별도 Form(시트·대화상자)도 같은 토큰을 써야 다크에서 흰 색이 안 남습니다.

### 3부. 윈도우 없이 빌드·화면 검증·단일 exe 배포

C# WinForms 앱을 **Mono 컴파일러 `mcs`** 로 크로스 빌드하면 윈도우 없이도 윈도우용 exe 가 나옵니다. GitHub Actions(ubuntu)·클라우드 세션·리눅스 서버 어디서나 같은 `build.sh` 로 빌드되고, 같은 exe 를 리눅스에서 `mono` 로 실행해 **Xvfb 가상 디스플레이**에 띄우면 AI 가 스크린샷을 찍어 레이아웃·정렬·색을 직접 확인할 수 있습니다.

#### 3-1. 설치 (ubuntu)

`sudo apt-get install -y mono-devel xvfb xdotool imagemagick` + `pip install pillow`

#### 3-2. 빌드 스크립트 — 리소스는 전부 exe 안에

```bash
mcs -sdk:4.5 -target:winexe -out:"MyApp.exe" \
  -r:System.Windows.Forms.dll -r:System.Drawing.dll \
  -win32res:src/app_full.res \
  -resource:src/SubR.ttf,PretendardR.ttf \
  -resource:src/SubSB.ttf,PretendardSB.ttf \
  -resource:src/AppIconEmbed.ico,AppIcon.ico \
  src/Main.cs
```

- `-target:winexe` → 콘솔 창 없는 GUI exe. `-sdk:4.5` → 윈도우 기본 탑재 .NET 4.x 에서 실행(별도 설치 불필요).
- `-win32res:*.res` → 관리자 권한 매니페스트·버전 정보·파일 아이콘. `.res` 는 한 번 만들어 두고 재사용합니다. (1-1 의 `/RL HIGHEST`, 1-6 의 관리자 재실행과 짝을 이룹니다.)
- `-resource:파일,이름` → 런타임에 `GetManifestResourceStream("이름")` 으로 꺼냅니다. **이름을 바꾸면 런타임에 못 찾습니다.**

결과는 폰트·아이콘·매니페스트가 모두 들어간 **DLL 0개 단일 exe** 입니다. 이 스크립트를 그대로 CI 의 빌드 스텝으로 쓰면 릴리스 자동화로 이어집니다(→ `self-updating-app-release-pipeline`).

#### 3-3. 내장 폰트 로드

한글 폰트는 서브셋(사용 글자만)으로 줄여 수백 KB 로 만듭니다.

```csharp
using (Stream s = Assembly.GetExecutingAssembly().GetManifestResourceStream("PretendardR.ttf")) {
    byte[] data = new byte[s.Length]; s.Read(data, 0, data.Length);
    IntPtr p = Marshal.AllocCoTaskMem(data.Length);   // 해제하지 말 것 — 폰트 수명 동안 살아 있어야 함
    Marshal.Copy(data, 0, p, data.Length);
    pfc.AddMemoryFont(p, data.Length);                  // GDI+ 용
    uint c; AddFontMemResourceEx(p, (uint)data.Length, IntPtr.Zero, out c);  // GDI(TextRenderer) 용
}
```

폰트 로드 실패 시 시스템 폰트로 폴백하도록 전부 try/catch 로 감쌉니다. 만든 `Font` 객체는 생성자에서 한 번 만들어 필드로 들고 있다가 Dispose 합니다(주의사항의 GDI 핸들 누수 참고).

#### 3-4. 가상 화면으로 실행·캡처

```bash
pkill -9 Xvfb; rm -f /tmp/.X97-lock          # 이전 잠금 파일이 남으면 "unable to open X server"
Xvfb :97 -screen 0 1280x900x24 & sleep 1
DISPLAY=:97 mono MyApp.exe & sleep 4
DISPLAY=:97 xdotool search --name "창 제목" windowactivate
DISPLAY=:97 xdotool mousemove 200 300 click 1   # 클릭·키 입력 재현
DISPLAY=:97 import -window root shot.png         # 전체 캡처 (ImageMagick)
convert shot.png -crop 300x80+40+120 +repage part.png   # 부분 확대
```

#### 3-5. 픽셀 측정

PIL 로 테두리 위치·색·간격을 숫자로 확인합니다(눈대중 금지).

```python
from PIL import Image
im = Image.open("shot.png").convert("RGB")
print([im.getpixel((x, 150)) for x in range(40, 60)])   # 1px 선이 한 칸인지 두 칸에 번졌는지
```

#### 3-6. 윈도우 실기 확인 체크리스트

리눅스·mono 에서는 아래를 검증할 수 없습니다. 로직·문자열만 확인하고 **실기(윈도우) 확인 필요 항목으로 따로 표시**한 뒤 윈도우에서 실사용 테스트로 확인합니다.

- [ ] 작업 스케줄러 등록/조회/삭제 (`schtasks`, 1-1·1-2)
- [ ] UAC·관리자 재실행 (1-6)
- [ ] 레지스트리 설정 저장·병합 (1-7)
- [ ] 윈도우 토스트 알림·알림 꺼짐 감지 (1-8)
- [ ] 실제 ClearType 렌더링 (2-1)
- [ ] 중복 실행 시 기존 창 복원 (1-5)

## 활용 예시

- **자동 종료 타이머**: 종료 예약·프로그램 종료·반복 알림을 트레이에 상주시키고, 요일 반복 칩·알림 리스트를 아이폰풍으로 그린 뒤 build 1~69 를 리눅스에서 빌드·검증.
- **그 밖의 상주 도구**: 클립보드 관리자, 폴더 감시 백업 도구, 휴식 알리미.
- **설정 화면**: 행마다 라벨 + 직접 그린 iOS 토글, 그룹은 둥근 카드.
- **알림 리스트**: 시간 큰 글씨 + 부제 + 오른쪽 토글 + 채널 아이콘(팝업/벨) 항상 표시·클릭으로 켜고 끄기.
- **요일 반복 칩**: 월~일 토글 칩, 기본 매일, 전부 끄면 1회성(1-9 비트마스크).
- **맥·클라우드만 있는 개발**: 윈도우 유틸 앱의 빌드·UI 검증까지 끝내고 윈도우에선 실사용 테스트만.
- **AI 미세 조정**: "이 버튼 1px 오른쪽으로" 같은 요청을 스크린샷+픽셀값으로 전후 비교.
- **릴리스 빌드**: GitHub Actions 에서 같은 `build.sh` 로 빌드(→ `self-updating-app-release-pipeline`).

## 💡 아이디어

- 모달 시트(`AppSheet`) 하나를 만들어 두고 안내·업데이트·진단 창을 전부 거기로 보내면, 윈도우 기본 MessageBox 가 UI 에서 튀는 문제가 해결됩니다.

## 주의사항

### 뼈대·운영

- 작업 스케줄러 등록/삭제·레지스트리·토스트는 **리눅스/mono 에서 검증 불가** → 윈도우 실기 확인 필수(3-6).
- Mutex 이름에 `Global\` 을 붙이면 다른 사용자 세션까지 한 개로 제한됩니다(의도 확인).
- `SetVisibleCore` 로 숨긴 상태에서 `Show()` 하려면 `allowVisible = true` 를 먼저.
- 종료 확인 모달("예약이 진행 중입니다")은 자동 업데이트 교체 시 건너뛰는 플래그가 필요합니다(→ `self-updating-app-release-pipeline`).

### UI

- `Fonts.Regular()` 처럼 호출마다 `new Font` 하는 헬퍼를 Paint 안에서 부르면 **GDI 핸들 누수**. 폰트는 생성자에서 만들어 필드로 들고 Dispose.
- 모달 대화상자를 비모달로 바꾸면 타이머 재진입으로 창이 겹쳐 쌓일 수 있습니다.
- 오버사이즈 리스트박스 방식은 Region 을 매 Resize 때 다시 계산해야 합니다.
- 픽셀 단위 미세 조정은 반드시 스크린샷+픽셀 측정으로 확인합니다(3-4, 3-5).

### mono 빌드·검증

- Xvfb + xdotool 로는 **한글 입력이 잘 안 들어갑니다** → 검증용 입력은 ASCII 로.
- 윈도우 전용 API(P/Invoke)는 정적 초기화에서 터지지 않게 `try { } catch { }` 로 감싸야 mono 에서 실행됩니다(예: `RegisterWindowMessage`).
- mono 는 SVG·컬러 이모지 글리프를 제대로 못 그립니다 → 아이콘은 `GraphicsPath` 로 직접 그리기(2-7).
- C# 버전은 mcs 기준입니다(람다 대신 `delegate { }` 로 통일하면 가장 안전).
- 한 줄에 선언을 여러 개 붙여 쓴 코드에 **줄 끝 `//` 주석을 끼우면 뒤 선언이 주석 처리**돼 컴파일이 실패합니다.
- `-resource:파일,이름` 의 이름을 바꾸면 런타임에 리소스를 못 찾습니다. 폰트용 메모리(`AllocCoTaskMem`)는 해제하지 마세요.

## 출처

- [https://github.com/600-g/shutdown-timer](https://github.com/600-g/shutdown-timer)

### 합쳐진 원본 문서

이 문서는 아래 3개 문서를 하나로 합쳐 새로 정리한 것입니다.

| 원본 문서 | 원래 슬러그 | 원본 출처 |
|---|---|---|
| 윈도우 트레이 상주 앱 필수 패턴 (C#) | `windows-tray-app-autorun-patterns` | [github.com](https://github.com/600-g/shutdown-timer) |
| WinForms 아이폰풍 오너드로우 UI 기법 | `winforms-iphone-style-ownerdraw-ui` | [github.com](https://github.com/600-g/shutdown-timer) |
| 리눅스에서 윈도우 exe 빌드 + 화면 검증 (mono) | `winforms-mono-cross-build-linux` | [github.com](https://github.com/600-g/shutdown-timer) |
