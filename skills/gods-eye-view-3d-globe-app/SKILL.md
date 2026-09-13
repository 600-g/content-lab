---
name: gods-eye-view-3d-globe-app
description: 실시간 **항공기, 선박, 위성, 지진, CCTV** 등 공개 데이터를 3D 지구 위에 시각화하는 **God's Eye View** 앱 설치 및 활용 가이드
origin: content-lab
grade: A
difficulty: 초급
category: 개발
ai_tools: []
sources:
  - https://citrine-yew-bda.notion.site/God-s-Eye-View-3c9a64f5742a8161b329e0913df22800?pvs=149
---

# 3D 지구본 앱 실시간 관제

💡 실시간 **항공기, 선박, 위성, 지진, CCTV** 등 공개 데이터를 3D 지구 위에 시각화하는 **God's Eye View** 앱 설치 및 활용 가이드

## 이게 뭔가요?

**God's Eye View**는 웹 브라우저에서 실행되는 3D 지구본 애플리케이션입니다. 이 앱은 전 세계의 실시간 공개 데이터를 사진처럼 사실적인 3D 지구 위에 오버레이하여 보여줍니다. 주요 기능으로는 실시간 항공기 추적, 조종석 모드, 위성 및 ISS 궤도 시뮬레이션, 도시 CCTV 영상 투영, 지진, 화재, 선박, 교통 정보, 라디오 정보 등이 있습니다. 또한, 7가지 센서 스타일(CRT, 야간 투시경, 열화상 등)을 지원하며, 선택적으로 음성 조종 기능(유료 키 필요)도 사용할 수 있습니다.

이 앱은 특정 개인을 검색하거나 얼굴을 인식하는 기능을 포함하지 않으며, 오로지 공개된 사물, 시설, 이벤트(비행기, 배, 카메라, 지진 등)를 다루는 데 초점을 맞춥니다. 2026년 코드가 MIT 라이선스로 무료 공개되었으며, 이 가이드에서는 코딩 경험이 없는 사용자도 자신의 컴퓨터에 설치하고 활용할 수 있도록 안내합니다.


## 따라하기

### 1. Node.js 설치

1.  [nodejs.org](https://nodejs.org/)에서 Windows Installer(.msi)를 다운로드합니다. LTS 최신 버전을 권장합니다.
2.  설치 과정에서 "다음"만 계속 누르면 됩니다.
3.  설치 후 컴퓨터를 **반드시 재시작**합니다. (재시작하지 않으면 다음 단계에서 명령어가 인식되지 않을 수 있습니다.)

### 2. 명령 프롬프트 열기

1.  `PowerShell` 대신 **명령 프롬프트(cmd)**를 사용합니다. `PowerShell`은 보안 정책으로 인해 `npm` 관련 오류가 발생할 수 있습니다.
2.  `⊞` (윈도우 키)를 누른 후 `cmd`를 입력하고 검색 결과의 "명령 프롬프트"를 클릭합니다.
3.  **확인:** 명령 프롬프트 창에 아래 두 줄을 각각 입력하고 엔터를 누릅니다.
    ```bash
    node -v
    npm -v
    ```
    버전 번호 (예: `v24.14.0`, `v26.8.1`)가 표시되면 성공입니다.

### 3. 코드 다운로드, 설치 및 실행

1.  아래 코드를 **통째로 복사**하여 명령 프롬프트에 붙여넣고 엔터를 누릅니다:
    ```bash
mkdir C:\gev 2>nul & cd /d C:\gev
curl -L -o gev.zip https://github.com/bilawalsidhu/gods-eye-view/archive/refs/heads/main.zip
tar -xf gev.zip
move gods-eye-view-main gods-eye-view
cd gods-eye-view
    ```
2.  API 키 없이 일단 실행해볼 `.env` 파일을 생성합니다:
    ```bash
echo GOOGLE_MAPS_API_KEY=>.env
echo OPENSKY_AUTH_MODE=anon>>.env
    ```
3.  설치 및 실행합니다. 설치에는 3~8분 정도 소요됩니다:
    ```bash
npm install
    ```
    *   `npm warn` 메시지나 `X high severity vulnerabilities` 문구는 정상이며 무시해도 됩니다.
    *   **절대 `npm audit fix`를 실행하지 마세요.** 버전이 깨질 수 있습니다.
4.  설치가 완료되면 이어서 실행합니다:
    ```bash
npm run dev -- --host localhost --port 4173
    ```
    화면에 `Local: http://localhost:4173/` 줄이 보이고 커서가 멈춰있다면 정상 작동 중입니다. **이 창은 앱이 켜져 있는 동안 계속 열어두어야 합니다.**
5.  크롬(또는 다른 브라우저) 주소창에 `http://localhost:4173`을 입력하여 접속합니다.

**다음에 다시 실행할 때:**

```bash
cd /d C:\gev\gods-eye-view
npm run dev -- --host localhost --port 4173
```

**앱을 끌 때:** 실행 창을 클릭한 후 `Ctrl + C`를 누릅니다.


## 처음 5분 — 뭐부터 눌러볼까

1.  앱 실행 후 뜨는 첫 화면 팝업에서 **LIVE CONTACTS**를 클릭하면 실시간 비행기 정보가 화면에 표시됩니다. 아무 비행기나 클릭하면 해당 비행기에 카메라가 고정되고 정보 카드가 뜹니다.
2.  `C` 키 또는 **COCKPIT** 버튼을 누르면 선택한 비행기의 조종석 시점으로 전환됩니다.
3.  키보드 숫자 `1`~`7` 키를 눌러 CRT, 야간 투시경(NVG), 열화상(FLIR) 등 다양한 화면 스타일로 전환할 수 있습니다.
4.  `H` 키는 HUD 표시, `D` 키는 탐지 박스 표시, `Esc` 키는 시점에서 빠져나옵니다.
5.  **Satellites**를 켜고 ISS(국제 우주 정거장)를 클릭하면 궤도를 따라 함께 이동합니다.
6.  탐색이 끝나면 **Reset Globe** 버튼으로 전체 지구본 화면으로 복귀합니다.

**한글 번역:**

앱 자체는 한글을 지원하지 않지만, 크롬 자동 번역 기능을 켜면 됩니다. 접속 시 나타나는 "한국어로 번역" 배너를 그대로 사용하면 일부 버튼 이름이 어색하게 번역될 수 있지만 전반적인 사용에 무리가 없습니다.


## CCTV 보는 법

1.  화면이 잘려 보인다면 `Ctrl` + `-` 키로 브라우저 배율을 낮춥니다.
2.  오른쪽 패널에서 **CCTV**를 클릭해 펼칩니다.
3.  `CCTV OFF` 버튼을 `CCTV ON`으로 바꾸면 카메라 로딩이 시작됩니다.
4.  **NEAREST**는 가장 가까운 카메라를 찾고, **FOCUS**는 해당 카메라 시점으로 이동합니다.
5.  영상이 3D 도시 위에 실제로 투영됩니다.
6.  **COVERAGE**를 켜면 카메라 시야 범위가 입체적으로 표시됩니다.
7.  `PREV` / `NEXT`로 카메라를 넘기거나, **AUTO HOP**을 켜면 카메라를 자동으로 순회합니다.

*   **참고:** 현재 CCTV는 오스틴(텍사스), 캘리포니아, 런던 지역에만 약 800대가 있으며, 다른 도시나 한국에서는 CCTV를 켜도 영상이 보이지 않는 것이 정상입니다. 검색창에 `Austin`, `London` 등을 입력하여 해당 지역으로 이동한 후 다시 시도해보세요.


## 비용 — 뭘 조심해야 하나

현재 상태(구글 API 키 미입력)에서는 **모든 기능이 무료**입니다. 구글 API 키를 입력하지 않으면 구글이나 OpenAI에 요청 자체가 발생하지 않아 비용이 청구되지 않습니다.

| 항목              | 구분     | 얻는 것                           | 비용                                   |
| :---------------- | :------- | :-------------------------------- | :------------------------------------- |
| Google Map Tiles  | 🔴 유료  | 사진 기반 3D 지구본               | 월 1,000회 무료, 초과 시 1,000회당 약 $6 |
| OpenAI Realtime   | 🔴 유료  | 음성 조종 + AI 요약               | 1분당 약 40~140원, 세션당 $5 상한      |
| Cesium ion        | 🟡 무료 가입 | Bing 위성사진 + 3D 지형           | 카드 등록 없이 무료                    |
| TomTom            | 🟡 무료 가입 | 실제 교통 정체 (시뮬레이션 대체)  | 하루 약 5만 요청 무료                  |
| AISStream/NASA FIRMS/OpenSky | 🟡 무료 가입 | 선박 / 산불 / 항공기 여유분       | 카드 등록 없이 무료                    |
| 비행기·위성·지진·CCTV·라디오 등 대부분 | 🟢 가입 불필요 | 즉시 사용                         | 0원                                    |


## 무료 키 2개 추가하기 (Cesium ion + TomTom)

화질과 데이터 정확도를 크게 높일 수 있는 Cesium ion과 TomTom 무료 키를 등록하는 방법입니다. 카드 등록 없이 사용 가능합니다.

### 1. Cesium ion — 위성사진 지구본

1.  [cesium.com/ion/signup](https://cesium.com/ion/signup) 에서 무료 가입합니다.
2.  로그인 후 **Access Tokens** 탭으로 이동합니다.
3.  **Default Token** 문자열을 복사합니다.

### 2. TomTom — 실제 교통 정체

1.  [developer.tomtom.com](https://developer.tomtom.com/) 에서 회원가입 후 로그인합니다.
2.  **Dashboard** → **My Keys**로 이동합니다.
3.  기본 생성된 키 문자열을 복사합니다.

### 3. 앱에 적용하기

1.  터미널 창에서 `Ctrl` + `C`를 눌러 서버를 중지합니다 (Y 입력 시 저장).
2.  같은 창에 `notepad .env`를 입력하고 엔터를 눌러 메모장을 엽니다.
3.  파일 맨 아래에 아래 두 줄을 추가하고 저장 (`Ctrl`+`S`)합니다:
    ```
    CESIUM_ION_TOKEN=복사한_Cesium_토큰
    TOMTOM_API_KEY=복사한_TomTom_키
    ```
4.  서버를 다시 시작합니다:
    ```bash
npm run dev -- --host localhost --port 4173
    ```
5.  브라우저를 새로고침(`F5`)합니다.

*   **확인:** 지도 선택 칩에서 **Bing Aerial**이 활성화되면 성공입니다. **Traffic**을 켜고 도심으로 8km 이하까지 내려가면 흰 점 대신 실제 색깔로 표시되는 교통 정체를 볼 수 있습니다.


## 주의사항

*   **콘텐츠 소재 사용 시:** 코드는 MIT 라이선스로 자유롭게 사용 가능하지만, GitHub README의 GIF 및 이미지는 저작자 소유이므로 직접 실행하여 녹화한 화면만 사용해야 합니다. 화면 하단의 Google, Cesium, TomTom 저작자 표시는 크롭하지 마세요.
*   **데이터 라이선스:** 주 데이터 소스인 OpenSky(항공기)는 비상업 라이선스이며, 해저케이블 지도는 비상업 전용(CC BY-NC-SA)입니다. 유료 협찬, 광고 콘텐츠에는 이러한 요소들이 보이지 않도록 주의하는 것이 안전합니다.
*   **오용 방지:** "해킹"이나 "감시 툴"과 같이 포장하지 마세요. 이 프로젝트는 의도적으로 특정 개인 추적이나 얼굴 인식 기능을 배제하고 있으며, 모든 데이터는 공개된 정보만을 활용합니다.
*   **오류:** `npm` 관련 권한 오류(`UnauthorizedAccess`), `port 4173 is already in use` 오류(`Port 4173 is already in use`), 비행기나 위성 사진이 보이지 않는 경우 등은 설정 오류나 네트워크 문제일 수 있습니다.


## 출처

[God's Eye View](https://citrine-yew-bda.notion.site/God-s-Eye-View-3c9a64f5742a8161b329e0913df22800?pvs=149)

## 출처

- [https://citrine-yew-bda.notion.site/God-s-Eye-View-3c9a64f5742a8161b329e0913df22800?pvs=149](https://citrine-yew-bda.notion.site/God-s-Eye-View-3c9a64f5742a8161b329e0913df22800?pvs=149)
