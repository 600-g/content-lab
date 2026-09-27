---
name: winforms-iphone-style-ownerdraw-ui
description: 투박한 윈도우 기본 컨트롤 대신 **오너드로우(직접 그리기)로 아이폰풍 WinForms UI**를 만드는 실전 기법 모음입니다. 깜빡임 제거, 1px 테두리 선명화, 스크롤바 숨기기, 벡터 아이콘, 단일/더블클릭 구분, 윈도우 표준 텍스트 조작까지 다룹니다.
origin: content-lab
grade: A
difficulty: 고급
category: 디자인
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://github.com/600-g/shutdown-timer
---

# WinForms 아이폰풍 오너드로우 UI 기법

## 이게 뭔가요?

자동 종료 타이머를 70회 넘게 다듬으며 굳힌 **WinForms 커스텀 페인트 요령**입니다. 기본 컨트롤은 최소화하고, 카드·토글·스테퍼·리스트를 전부 직접 그려 아이폰 설정 앱 같은 룩을 냅니다. 문제가 됐던 증상 → 원인 → 해법 순서로 정리했습니다.

## 따라하기

1. **텍스트는 GDI `TextRenderer` 로 통일** — `Graphics.DrawString`(GDI+)은 흐릿하고 글자 폭이 다르다. `TextRenderer.DrawText(g, text, font, rect, color, TextFormatFlags.VerticalCenter | ...)` 로 ClearType 선명하게.
2. **1px 테두리가 "지워진 것처럼 연하게" 보일 때** — 안티앨리어싱 1px 선이 두 픽셀에 반씩 걸친 것. `g.PixelOffsetMode = PixelOffsetMode.Half;` + 선 두께 1 + 색을 한 톤 진하게.
3. **깜빡임 제거**
   - 모든 커스텀 컨트롤: `SetStyle(ControlStyles.OptimizedDoubleBuffer | ControlStyles.AllPaintingInWmPaint | ControlStyles.UserPaint | ControlStyles.ResizeRedraw, true);`
   - 1초 타이머로 매번 `Invalidate()` 하지 말 것 → **표시 내용 서명(sig) 비교**로 바뀐 경우에만 다시 그림:
```csharp
string sig = text + "|" + count + "|" + state;
if (sig == islandSig) return;   // 그대로면 안 그림
islandSig = sig; island.Invalidate();
```
   - 무효화 영역도 전체가 아니라 바뀐 사각형만.
4. **ListBox 스크롤바 숨기기** — `DrawMode.OwnerDrawFixed` 리스트박스를 카드보다 **오른쪽으로 넓게** 만들어 스크롤바를 카드 밖으로 밀고, `Region` 으로 카드 안쪽 폭까지만 그리게 잘라 카드 테두리를 덮지 않게(`ClipWidth`). 휠 스크롤은 그대로 동작.
5. **스크롤 위치 표시** — 스크롤바를 숨겼으면 항목이 넘칠 때만 오른쪽에 작은 썸(thumb) 막대를 직접 그림: 높이 = 보이는 비율, 위치 = `TopIndex / (Count - 보이는 수)`.
6. **빈 목록 안내문** — 네이티브 리스트 위에 그리면 뭉개진다 → 리스트를 투명(빈 Region) 처리하고 **부모 카드가** "항목 없음" 안내를 그림.
7. **아이콘은 `GraphicsPath` 벡터로** — 이모지·SVG 는 환경마다 깨짐. 말풍선·종·톱니를 도형으로 그리고, 켜짐/꺼짐은 **색으로만** 구분(onCol/offCol).
8. **단일클릭 vs 더블클릭 충돌** — MouseDown 즉시 수정 모드 진입이 더블클릭과 겹침 → **260ms 타이머**로 판별:
```csharp
// MouseDown: almPendIdx = idx; almClickT.Stop(); almClickT.Start();   (Interval = 260)
// Tick:      almClickT.Stop(); if (!almDbl) SingleClick(almPendIdx); almDbl = false;
// DoubleClick: almDbl = true; almClickT.Stop(); OpenEditor(idx);
```
9. **선택 해제 동선** — 리스트가 꽉 차면 빈 곳이 없어 선택을 못 푼다 → 패널·부모의 **아무 빈 곳 클릭**에도 해제(`panel.MouseDown += delegate { ReleaseEdit(); };`), 같은 항목 재클릭도 토글 해제.
10. **윈도우 표준 텍스트 조작 보강** — WinForms TextBox 는 더블클릭이 단어만, Ctrl+A 가 기본 미지원:
```csharp
tb.DoubleClick += delegate { tb.SelectAll(); };
tb.KeyDown += delegate(object s, KeyEventArgs k) {
    if (k.Control && k.KeyCode == Keys.A) { tb.SelectAll(); k.SuppressKeyPress = true; k.Handled = true; } };
```
    메모장형 입력은 **Enter = 저장, Shift+Enter = 줄바꿈**(KeyDown 에서 Enter && !Shift → 저장 후 SuppressKeyPress).
11. **광학 보정** — 같은 크기인데 테두리 있는 버튼이 더 커 보이면 테두리 버튼을 1px 안쪽으로(optical inset).
12. **다크 모드** — 색 리터럴 금지, 전부 `Theme.*` 토큰. 별도 Form(시트·대화상자)도 같은 토큰을 써야 다크에서 흰 색이 안 남는다.

## 활용 예시

- 설정 화면: 행마다 라벨 + 직접 그린 iOS 토글, 그룹은 둥근 카드.
- 알림 리스트: 시간 큰 글씨 + 부제 + 오른쪽 토글 + 채널 아이콘(팝업/벨) 항상 표시·클릭으로 켜고 끄기.
- 요일 반복 칩: 월~일 토글 칩, 기본 매일, 전부 끄면 1회성.

## 💡 아이디어

- 모달 시트(`AppSheet`) 하나를 만들어 두고 안내·업데이트·진단 창을 전부 거기로 — 윈도우 기본 MessageBox 가 UI 에서 튀는 문제 해결.

## 주의사항

- `Fonts.Regular()` 처럼 호출마다 `new Font` 하는 헬퍼를 Paint 안에서 부르면 **GDI 핸들 누수**. 폰트는 생성자에서 만들어 필드로 들고 Dispose.
- 모달 대화상자를 비모달로 바꾸면 타이머 재진입으로 창이 겹쳐 쌓일 수 있다.
- 오버사이즈 리스트박스 방식은 Region 을 매 Resize 때 다시 계산해야 한다.
- 픽셀 단위 미세 조정은 반드시 스크린샷+픽셀 측정으로 확인(→ `winforms-mono-cross-build-linux`).
