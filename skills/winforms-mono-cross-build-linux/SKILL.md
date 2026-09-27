---
name: winforms-mono-cross-build-linux
description: 윈도우 PC 없이 **리눅스·맥·클라우드에서 윈도우용 단일 exe(WinForms)를 빌드**하고, **가상 화면(Xvfb)으로 띄워 스크린샷·픽셀 측정까지 검증**하는 방법입니다. 폰트·아이콘·관리자 매니페스트를 exe 안에 박아 DLL 0개로 배포합니다.
origin: content-lab
grade: A
difficulty: 중급
category: 개발
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://github.com/600-g/shutdown-timer
---

# 리눅스에서 윈도우 exe 빌드 + 화면 검증 (mono)

## 이게 뭔가요?

C# WinForms 앱을 **Mono 컴파일러 `mcs`** 로 크로스 빌드하면 윈도우 없이도 윈도우용 exe 가 나옵니다. GitHub Actions(ubuntu)·클라우드 세션·리눅스 서버 어디서나 같은 `build.sh` 로 빌드됩니다. 같은 exe 를 리눅스에서 `mono` 로 실행하고 **Xvfb 가상 디스플레이**에 띄우면 AI 가 스크린샷을 찍어 레이아웃·정렬·색을 직접 확인할 수 있습니다. (자동 종료 타이머 build 1~69 를 전부 이 방식으로 만들고 검증)

## 따라하기

1. **설치** (ubuntu): `sudo apt-get install -y mono-devel xvfb xdotool imagemagick` + `pip install pillow`
2. **빌드 스크립트** — 리소스는 전부 exe 안에 박는다:
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
   - `-win32res:*.res` → 관리자 권한 매니페스트·버전 정보·파일 아이콘. `.res` 는 한 번 만들어 두고 재사용.
   - `-resource:파일,이름` → 런타임에 `GetManifestResourceStream("이름")` 으로 꺼냄. **이름을 바꾸면 런타임에 못 찾는다.**
3. **내장 폰트 로드** — 한글 폰트는 서브셋(사용 글자만)으로 줄여 수백 KB 로:
```csharp
using (Stream s = Assembly.GetExecutingAssembly().GetManifestResourceStream("PretendardR.ttf")) {
    byte[] data = new byte[s.Length]; s.Read(data, 0, data.Length);
    IntPtr p = Marshal.AllocCoTaskMem(data.Length);   // 해제하지 말 것 — 폰트 수명 동안 살아 있어야 함
    Marshal.Copy(data, 0, p, data.Length);
    pfc.AddMemoryFont(p, data.Length);                  // GDI+ 용
    uint c; AddFontMemResourceEx(p, (uint)data.Length, IntPtr.Zero, out c);  // GDI(TextRenderer) 용
}
```
   폰트 로드 실패 시 시스템 폰트로 폴백하도록 전부 try/catch.
4. **DPI 선명도** — `Main` 첫 줄에 `SetProcessDPIAware()`(user32). 125%/150% 배율에서 윈도우가 통째 확대해 뿌옇게 되는 것 방지. 폰트는 **픽셀 단위**(`GraphicsUnit.Pixel`)로 만들어 크기 일정 유지.
5. **가상 화면으로 실행·캡처**:
```bash
pkill -9 Xvfb; rm -f /tmp/.X97-lock          # 이전 잠금 파일이 남으면 "unable to open X server"
Xvfb :97 -screen 0 1280x900x24 & sleep 1
DISPLAY=:97 mono MyApp.exe & sleep 4
DISPLAY=:97 xdotool search --name "창 제목" windowactivate
DISPLAY=:97 xdotool mousemove 200 300 click 1   # 클릭·키 입력 재현
DISPLAY=:97 import -window root shot.png         # 전체 캡처 (ImageMagick)
convert shot.png -crop 300x80+40+120 +repage part.png   # 부분 확대
```
6. **픽셀 측정** — PIL 로 테두리 위치·색·간격을 숫자로 확인(눈대중 금지):
```python
from PIL import Image
im = Image.open("shot.png").convert("RGB")
print([im.getpixel((x, 150)) for x in range(40, 60)])   # 1px 선이 한 칸인지 두 칸에 번졌는지
```

## 활용 예시

- 맥·클라우드만 있는 상황에서 윈도우 유틸 앱 개발 → 빌드·UI 검증까지 끝내고 윈도우에선 실사용 테스트만.
- AI 에게 "이 버튼 1px 오른쪽으로" 같은 미세 조정을 시킬 때 스크린샷+픽셀값으로 전후 비교.
- GitHub Actions 에서 같은 `build.sh` 로 릴리스 빌드(→ `self-updating-app-release-pipeline` 스킬).

## 주의사항

- **리눅스 검증이 불가능한 영역**: 레지스트리, 윈도우 토스트 알림, `schtasks`(작업 스케줄러), UAC, 실제 ClearType 렌더링. 로직·문자열만 확인하고 **실기(윈도우) 확인 필요 항목으로 따로 표시**할 것.
- Xvfb + xdotool 로는 **한글 입력이 잘 안 들어간다** → 검증용 입력은 ASCII 로.
- 윈도우 전용 API(P/Invoke)는 정적 초기화에서 터지지 않게 `try { } catch { }` 로 감싸야 mono 에서 실행된다(예: `RegisterWindowMessage`).
- mono 는 SVG·컬러 이모지 글리프를 제대로 못 그린다 → 아이콘은 `GraphicsPath` 로 직접 그리기.
- C# 버전은 mcs 기준(람다 대신 `delegate { }` 로 통일하면 가장 안전).
- 한 줄에 선언을 여러 개 붙여 쓴 코드에 **줄 끝 `//` 주석을 끼우면 뒤 선언이 주석 처리**돼 컴파일 실패.
