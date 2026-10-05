---
name: claude-opus-5-5-recipes-and-tips
description: **Claude Opus 5.5**를 잘 쓰는 요령 3가지와 유형별 재현 레시피 6종(3D 장면·스케치 변환·코드 영상·교육 도구·다안 비평·대형 업무), 그대로 복붙하는 화제작 프롬프트(브라우저 마인크래프트·픽셀아트 마법사)와 **Claude Code** 캐릭터 애니메이션 키트 사용법을 모은 가이드입니다.
origin: content-lab
grade: S
difficulty: 초급
category: 프롬프트
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://app.notion.com/p/Claude-Opus-5-5-100-3e51061c8a63811e89d6e69afa5899dd?pvs=39
  - https://fieldby.notion.site/5-5-10-3e5d730b3953818ead9ff0ae6badc22e?pvs=149
originals:
  - claude-opus-5-5-recipes-and-tips | Opus 5.5로 결과물 원샷 제작 | https://app.notion.com/p/Claude-Opus-5-5-100-3e51061c8a63811e89d6e69afa5899dd?pvs=39
  - claude-opus-5-5-prompt-showcase | 오퍼스5.5 프롬프트 따라하기 | https://fieldby.notion.site/5-5-10-3e5d730b3953818ead9ff0ae6badc22e?pvs=149
---

# Opus 5.5 원샷 제작 레시피

💡 **Claude Opus 5.5**는 "한 번 요청 → 스스로 확인 → 고쳐서 끝까지"가 강점입니다. 원하는 결과를 **구체적으로 한 번에** 적고, **직접 확인하게** 시키는 것이 요령이며, 아래 프롬프트를 그대로 붙여넣으면 바로 결과가 나옵니다.

## 이게 뭔가요?

Claude Opus 5.5는 앤트로픽이 2026년 9월 22일 내놓은 새 기본 모델입니다. 공개 직후 X(트위터) 등에 3D 행성, 브라우저 마인크래프트, 연필 스케치가 3D로 튀어나오는 투석기, 카메라 렌즈 3D 체험, K팝 뮤직비디오, 로블록스 격투 게임, 언리얼 엔진 액션 게임, 안티키테라 기계 게임, 코드로만 그린 픽셀 마법사, 68만 줄 코드 이전 같은 사례가 쏟아졌습니다. 이 문서는 2026년 9월 24일(출시 이틀째) 기준 공개 사례 103개와 화제작 10개를 바탕으로, 사례를 구경하는 대신 **따라 만드는 법**을 정리한 것입니다.

프롬프트는 두 종류입니다.

- **재현용 레시피 (레시피 1~6)**: 사례를 보고 따라 할 수 있게 다시 쓴 요청 문장입니다. 원작자가 쓴 문장 그대로는 아닙니다.
- **원작자 공개 프롬프트**: 제작자가 실제로 쓴 문장을 그대로 옮긴 것입니다(브라우저 마인크래프트, 픽셀아트 마법사, 애니메이션 키트 요청 예시).

### 모델 기본 정보

| 항목 | 내용 |
|---|---|
| 출시일 | 2026년 9월 22일 |
| 종합 지능 지수 (Artificial Analysis) | Opus 5.5: 58 / GPT-6 Astra: 53 |
| API 가격 (100만 토큰당) | 입력 $4 · 출력 $20 (Opus 5보다 20% 인하) |
| 생각 강도(effort) | 5단계, 기본은 medium |
| 모델 이름 (API) | claude-opus-5-5 |

### 사용 도구와 비용

- 💰 유료 필요: 클로드 앱에서는 Pro·Max·Team·Enterprise 요금제가 있어야 합니다(Pro·Max·Team은 클로드 앱과 Claude Code에서 이미 기본 모델로 켜져 있습니다). 무료 요금제는 지원하지 않습니다. 개발자는 API 종량제로 모델명 `claude-opus-5-5`를 호출합니다.
- ✅ 무료 대안: 레시피 프롬프트는 모델에 종속되지 않아 Gemini, ChatGPT 무료 버전에 그대로 넣어 시도할 수 있습니다. 다만 결과 품질과 "스스로 확인" 동작은 Opus 5.5와 다를 수 있고, 마인크래프트·픽셀 마법사 같은 고난도 결과물은 Opus 5.5의 코딩·추론 능력을 전제로 해서 다른 모델로는 같은 품질 재현이 어렵습니다.

### 잘 쓰는 요령 세 가지

1. **원하는 결과를 구체적으로, 한 번에.** 사례 대부분이 한 번 요청(원샷)입니다. 대신 요청 안에 무엇이 보여야 하고 무엇을 조작할 수 있어야 하는지를 모두 적었습니다. 픽셀 마법사 프롬프트처럼 "렌더링 방식 → 캐릭터/오브젝트 규격 → 애니메이션 상태 머신 → 완성 기준" 순서로 적으면 빠짐이 없습니다.
2. **스스로 확인하게 시키기.** 3D 행성 사례(14분, $2.54)는 만든 뒤 자기 화면을 세 번 캡처해서 보고 고친 다음 멈췄습니다. 요청 끝에 "완성하면 직접 열어서 확인하고, 이상한 곳은 고쳐줘"를 붙입니다.
3. **일 시키기 전에 먼저 읽게 하기.** 앤트로픽 공식 가이드의 팁입니다. 이 모델은 일을 빨리 시작하는 편이라, 메일·문서·엑셀이 섞인 일이면 아래 한 줄을 붙입니다.

```
작업을 시작하기 전에 관련된 문서, 시트 탭, 메일을 먼저 전부 읽고 파악한 뒤 시작해줘.
```

**생각 강도(effort)**: 기본(medium)으로 충분합니다. 최대(max)로 올리면 토큰을 훨씬 많이 써서(측정값: 작업당 약 11.9만 토큰) 가격 인하 효과가 사라질 수 있으니, 어려운 일만 high로 올립니다. 마인크래프트 사례처럼 원작자가 max로 돌린 경우는 시간·비용이 크게 늘어난다는 점을 감안합니다.

## 따라하기

### 어떤 레시피를 언제 쓰나

| 만들고 싶은 것 | 쓸 프롬프트 | 어디서 | 난이도·비용 감 |
|---|---|---|---|
| 돌려보는 3D 장면·작은 게임 | 레시피 1 | claude.ai | 낮음 (3D 행성 14분, $2.54) |
| 마인크래프트급 고퀄 3D 게임 | 원작자 프롬프트 A | 클로드 앱 / API | 높음 (effort max, 약 1시간 37분, 약 $15) |
| 손그림·사진을 움직이는 결과물로 | 레시피 2 | claude.ai (이미지 첨부) | 중간 |
| 영상 AI 없이 애니메이션·뮤비 | 레시피 3 | claude.ai | 낮음 |
| 16비트 픽셀 스프라이트 애니메이션 | 원작자 프롬프트 B | 클로드 앱 | 중간 |
| 캐릭터 애니메이션 mp4 자동 제작 | 캐릭터 애니메이션 키트 | Claude Code | 준비물 필요 (Node.js·크롬·ffmpeg) |
| 수업·강의용 조작형 교재 | 레시피 4 | claude.ai | 중간 (렌즈 체험 1시간 26분, $25.66) |
| 디자인·카피 시안 여러 개 비교 | 레시피 5 | claude.ai | 낮음 |
| 대형 코드 이전·정리·버그 수정 | 레시피 6 | Claude Code | 높음 |

### 레시피 1. 브라우저에서 돌아가는 3D 장면·게임

사례: 3D 행성, 마인크래프트, 금문교

1. claude.ai에서 **Opus 5.5**를 선택합니다.
2. 아래 프롬프트로 요청합니다. 옆 창에 바로 결과가 뜹니다.
3. 마음에 안 드는 곳은 한 가지씩 말로 고칩니다. (예: "비행기를 더 크게", "밤이 되면 불 켜지게")
4. 파일로 받아 더블클릭하면 설치 없이 브라우저에서 열립니다.

```
Three.js로 HTML 파일 하나에 들어가는 3D 장면을 만들어줘.
내용: 만화풍의 작은 행성. 구름, 산, 도시 건물이 있고 자동차와 비행기가 행성 위를 돌아다녀.
조작: 마우스로 드래그하면 행성이 돌고, 스크롤하면 확대돼.
버튼 3개: 전체 보기 / 비행기 타기 / 자동차 타기.
외부 이미지 파일은 쓰지 말고 전부 코드로 그려줘.
완성하면 직접 화면을 확인하고 어색한 부분을 고친 뒤에 보여줘.
```

### 원작자 프롬프트 A. 브라우저 마인크래프트

클로드 앱 채팅창이나 API에 그대로 붙여넣습니다. 영어 원문이 원작자 문장이고, 한국어는 같은 뜻의 번역입니다.

```
Create a playable version of Minecraft in my browser. Add advanced shaders that make it look as real and beautiful as possible.
```

한국어 번역:

```
내 브라우저에서 플레이할 수 있는 마인크래프트를 만들어줘. 최대한 사실적이고 아름답게 보이도록 고급 셰이더를 넣어줘.
```

원 제작자는 effort를 최대로 설정했고, 약 1시간 37분 만에 물결·노을·횃불 그림자까지 표현된 결과물이 나왔으며 API 비용은 약 15달러였다고 밝혔습니다.

### 레시피 2. 사진·스케치를 만질 수 있는 결과물로

사례: 종이 투석기, 블록 조립 앱, iOS 앱 디자인

손으로 그린 그림이나 참고 사진을 첨부하고 요청합니다. 그림이 "설계도" 역할을 하므로 말로 설명할 내용이 줄어듭니다.

```
첨부한 연필 스케치는 투석기야. 이걸 브라우저에서 돌아가는 3D 시뮬레이션으로 만들어줘.
- 처음엔 종이 위 스케치로 시작해서, 버튼을 누르면 입체로 바뀌게
- 팔을 마우스로 당겼다 놓으면 공이 날아가고, 앞에 쌓인 블록이 무너지게
- 공 무게와 당기는 각도를 슬라이더로 바꿀 수 있게
- 몇 개가 쓰러졌는지 화면에 표시
```

참고 이미지로 앱 디자인을 뽑을 때는 이미지 여러 장 + 반복이 정석입니다. 한 사례는 참고 이미지 8장, 요청 9번, 1시간 다듬기로 완성했습니다.

### 레시피 3. 코드로 만드는 영상·음악

사례: 팝펑크 뮤비, 삶의 목적 애니메이션, 우주 여행 애니메이션

영상 생성 AI 없이 움직이는 웹페이지를 만들고 그걸 화면 녹화하는 방식입니다. 그림·움직임·소리가 모두 코드라 수정이 말 한마디로 됩니다.

```
"삶의 목적은 무엇인가"를 주제로 40초짜리 손그림풍 애니메이션을 HTML 파일 하나로 만들어줘.
대본도 네가 쓰고, 배경음악도 자바스크립트로 직접 만들어줘. 이미지·음원 파일은 쓰지 마.
재생 버튼을 누르면 처음부터 끝까지 자동으로 흘러가게 해줘.
```

완성되면 브라우저에서 재생하면서 화면 녹화(윈도우 `Win+Alt+R`, 맥 `Cmd+Shift+5`)하면 영상 파일이 됩니다.

### 원작자 프롬프트 B. 픽셀아트 마법사 애니메이션

아래 전문을 클로드 앱 채팅창에 그대로 붙여넣습니다. 결과물은 HTML 파일 하나로 완성되고, 화면 옆 미리보기 창에서 바로 움직입니다. 외부 이미지 없이 코드만으로 대기·충전·시전·회복 4단계 상태 머신이 도는 16비트풍 애니메이션이 나옵니다.

```
Create a single self-contained HTML file that renders an animated pixel art wizard casting a spell, using vanilla JavaScript and Canvas 2D. No external assets, libraries, or network requests.
RENDERING
- Draw everything to an offscreen canvas at a fixed logical resolution of 128x96, then blit to a fullscreen display canvas scaled by the largest integer factor that fits the window, centered, with imageSmoothingEnabled = false and CSS image-rendering: pixelated.
- All drawing snaps to integer coordinates on the logical canvas. No sub-pixel positions, anti-aliasing, gradients, or shadowBlur.
- Fixed palette of ~24 hex colors: deep blues/purples for night sky, warm robe tones, 3-4 bright magic colors. Every pixel comes from this palette.
CHARACTER
- Build the wizard procedurally from filled rects and pixel runs, ~24x32 logical pixels: pointed hat with a bend, long beard, two-shade robe with darker outline, staff with a gem at the tip.
- Parameterize the pose (staff angle, arm raise, head tilt, robe sway). Animate parameters smoothly, then quantize to the pixel grid each frame so motion reads at an 8-12 fps pixel animation feel even though the loop runs at 60fps.
ANIMATION
- Looping state machine: IDLE (2-frame bob, beard sway) -> CHARGE (staff raises, gem flickers, sparks spiral inward) -> CAST (bright burst, projectile fires across the scene, 1-2 pixel screen shake) -> RECOVER (settle back). Ease pose parameters between keyframes.
- Pooled allocation-free particle system: preallocate and reuse. Sparks orbit the gem during CHARGE, explode outward on CAST, each particle stepping its palette index from white to magic color to dark before despawn. Snap particle positions to the grid when drawing.
- Fixed 60hz timestep update with rAF rendering. Zero object allocation inside the loop.
SCENE
- Minimal background: dark sky, a few twinkling 1px stars, moon, stone floor line. Character silhouette must read clearly.
- Subtle 1px rim light on the wizard from the gem, brightening during CHARGE and CAST.
QUALITY BAR
- Crisp pixels at any window size, seamless loop, stable 60fps, readable silhouette. Should look like a polished 16-bit sprite animation, not vector shapes scaled down.
```

한국어 (내용 이해용 번역):

```
순수 자바스크립트와 Canvas 2D로, 주문을 외우는 픽셀 아트 마법사 애니메이션을 HTML 파일 하나로 만들어줘. 외부 파일·라이브러리·네트워크 요청은 쓰지 마.
[렌더링]
- 모든 그림은 128x96 고정 해상도의 보이지 않는 캔버스(offscreen canvas)에 그린 뒤, 창에 들어가는 가장 큰 정수 배율로 키워 전체 화면 캔버스 가운데에 옮겨 그려줘. imageSmoothingEnabled = false, CSS image-rendering: pixelated를 적용해.
- 모든 그림은 논리 캔버스의 정수 좌표에 맞춰. 소수점 위치·안티앨리어싱·그라데이션·shadowBlur는 쓰지 마.
- 색은 약 24개로 고정한 팔레트만 써. 밤하늘용 짙은 파랑·보라, 따뜻한 로브 색, 밝은 마법 색 3~4개. 모든 픽셀은 이 팔레트에서만 가져와.
[캐릭터]
- 마법사는 채운 사각형과 픽셀 줄을 코드로 쌓아 약 24x32픽셀로 만들어줘. 끝이 꺾인 뾰족 모자, 긴 수염, 어두운 외곽선이 있는 두 톤 로브, 끝에 보석이 달린 지팡이.
- 자세(지팡이 각도, 팔 들기, 고개 기울기, 로브 흔들림)를 값으로 조절해. 값은 부드럽게 움직이되 매 프레임 픽셀 격자에 맞춰 끊어서, 루프는 60fps로 돌아도 8~12fps 픽셀 애니메이션처럼 보이게 해줘.
[애니메이션]
- 반복 순서: 대기(2프레임 들썩임, 수염 흔들림) → 충전(지팡이를 들고 보석이 깜빡이며 불꽃이 안쪽으로 소용돌이) → 시전(밝게 터지며 투사체가 화면을 가로질러 날아가고, 화면이 1~2픽셀 흔들림) → 회복(원래 자세로). 키프레임 사이 자세는 부드럽게 이어줘.
- 파티클은 미리 만들어 두고 재사용해. 충전 때는 불꽃이 보석 주위를 돌고, 시전 때는 바깥으로 터지며, 입자마다 흰색 → 마법 색 → 어두운 색으로 바뀐 뒤 사라지게. 그릴 때 입자 위치도 격자에 맞춰.
- 업데이트는 60Hz 고정 간격, 그리기는 requestAnimationFrame. 루프 안에서 객체를 새로 만들지 마.
[배경]
- 최소한으로: 어두운 하늘, 반짝이는 1픽셀 별 몇 개, 달, 돌바닥 선. 캐릭터 실루엣이 또렷하게 보여야 해.
- 보석에서 나오는 은은한 1픽셀 테두리 빛을 마법사에게 비추고, 충전·시전 때 더 밝아지게.
[완성 기준]
- 어떤 창 크기에서도 선명한 픽셀, 끊김 없는 반복, 안정적인 60fps, 알아보기 쉬운 실루엣. 벡터 도형을 줄인 느낌이 아니라 잘 다듬은 16비트 게임 스프라이트 애니메이션처럼 보여야 해.
```

### 캐릭터 애니메이션 키트 (Claude Code)

스토리보드 구성부터 mp4 출력까지 자동화된 클로드 캐릭터 애니메이션 제작 키트입니다. GitHub에서 키트를 내려받아 Claude Code에서 열고, 원하는 장면을 말로 요청합니다.

1. 사전 준비: Node.js·크롬·ffmpeg를 설치합니다. 그래픽카드가 없으면 수채화 효과 렌더링이 느려집니다.
2. 키트 폴더를 Claude Code에서 엽니다.
3. 아래처럼 가이드 문서를 먼저 읽게 한 뒤 장면을 요청합니다.

요청 예시 (English 원문):

```
Read ANIMATION_GUIDE.md, then make a 15-second video of Clawd trying to catch a butterfly.
```

한국어:

```
ANIMATION_GUIDE.md를 먼저 읽고, 나비를 잡으려는 클로드 캐릭터의 15초 영상을 만들어줘.
```

### 레시피 4. 설명하기 어려운 걸 "만져보는 교재"로

사례: 카메라 초점 교육 도구 — 초점 링을 돌리면 렌즈 속 유리알이 움직이는 3D 체험 사이트 (1시간 26분, $25.66)

강의·수업·상담 자료에 가장 바로 쓸 수 있는 유형입니다. "설명해줘" 대신 "설명하는 도구를 만들어줘"라고 요청합니다.

```
카메라 초점이 어떻게 맞는지 중학생도 이해할 수 있게, 직접 조작해보는 인터랙티브 교육 도구를 만들어줘.
- 렌즈를 돌리면 초점면이 앞뒤로 움직이는 게 보이게
- 조리개를 바꾸면 배경이 얼마나 흐려지는지 바로 보이게
- 화면 한쪽에 지금 무슨 일이 일어나는지 한두 문장으로 설명
```

### 레시피 5. 여러 안을 만들고 스스로 비평하게 하기

사례: 개인 웹사이트 리디자인

한 번에 정답 하나를 달라고 하지 말고 "여러 안 → 스스로 평가 → 좋은 안 다듬기"를 시키면 결과가 확 좋아집니다. 디자인·카피·기획서 모두 적용됩니다.

```
내 웹사이트(주소 또는 첨부 파일)를 리디자인할 거야. 원하는 분위기는 "차분하고, 손글씨 느낌이 살짝 있는"이야.
1. 서로 확실히 다른 방향으로 5개 안을 만들어줘
2. 각 안을 내가 말한 분위기 기준으로 스스로 평가해서 점수와 이유를 적어줘
3. 점수가 제일 높은 2개를 골라 한 번 더 다듬어줘
```

### 레시피 6. 크고 긴 업무 맡기기

사례: 68만 줄 코드 이전, PR 40개 정리, 밤새 버그 수정

**Claude Code**에서 하는 일입니다. 단계를 나누고, 단계마다 검사를 통과해야 다음으로 넘어가게 하는 것이 요령입니다. 메일·문서가 섞인 일이면 앞의 "먼저 전부 읽고 시작해줘" 한 줄을 함께 붙입니다.

```
이 작업을 단계로 나눠서 진행해줘.
각 단계가 끝날 때마다 테스트를 돌려서 통과한 것을 확인한 뒤에만 다음 단계로 넘어가.
막히는 곳이 있으면 멈추지 말고, 무엇이 왜 막혔는지 정리해서 마지막에 한꺼번에 알려줘.
```

### 설치 없이 먼저 체험해보기

카메라 렌즈 초점 3D 체험 사이트와 안티키테라 기계 게임은 원본 게시물의 데모 링크를 누르면 설치·로그인 없이 브라우저에서 바로 실행됩니다. 안티키테라 게임은 키보드 조작이라 PC 환경을 권합니다. 직접 만들기 전에 결과 수준을 감 잡는 용도로 좋습니다.

## 활용 예시

- **수업·강의 자료**: 레시피 4에서 주제만 바꿔 "중학생도 이해할 수 있게 직접 조작해보는 인터랙티브 교육 도구를 만들어줘"라고 요청합니다. 결과는 HTML 파일 하나이며 더블클릭으로 열립니다.
- **손그림 아이디어 시각화**: 연필 스케치를 사진으로 찍어 첨부하고 레시피 2를 쓰면 버튼과 슬라이더가 달린 브라우저 시뮬레이션이 나옵니다.
- **디자인·카피 시안 고르기**: 레시피 5의 "웹사이트" 자리에 블로그 소개문이나 썸네일 문구를 넣으면 5개 안, 점수와 이유, 상위 2개의 다듬은 버전을 받습니다.
- **고퀄 데모 재현**: 원작자 프롬프트 A를 그대로 넣으면 물결·노을·횃불 그림자가 표현된 브라우저용 마인크래프트가, 프롬프트 B를 넣으면 4단계 상태 머신 픽셀 마법사가 HTML 파일 하나로 나옵니다.
- **짧은 캐릭터 클립**: 애니메이션 키트에서 "나비를 잡으려는 15초 영상"의 장면 설명만 바꿔 SNS용 캐릭터 클립을 뽑습니다.

## 💡 아이디어

- **픽셀 마법사 프롬프트를 틀로 재활용**: "렌더링 방식 → 캐릭터 규격 → 애니메이션 상태 머신 → 완성 기준" 구조를 그대로 두고 캐릭터 부분만 바꾸면 자기 마스코트나 다른 캐릭터의 픽셀 애니메이션을 만들 수 있습니다.
- **코드 영상 → 숏폼**: 레시피 3은 영상 생성 AI 없이 만드는 방식이라, 화면 녹화 후 CapCut으로 편집하면 숏폼 소재로 이어갈 수 있습니다.
- **인터랙티브 교재 확장**: 레시피 4 결과물은 강의·상담 보조 자료나 전자책 부록으로 확장할 수 있습니다.
- **대형 작업 기본 지시문**: 레시피 6의 "단계별 테스트 통과 후 진행" 문구를 Claude Code로 운영하는 프로젝트의 기본 지시문에 넣어 큰 리팩터링마다 재사용합니다.
- **홍보 영상 자동화**: 애니메이션 키트는 스토리보드부터 mp4 출력까지 자동화돼 있어 짧은 SNS 홍보 영상 제작에 응용할 수 있습니다.

## 주의사항

- **요금제**: 클로드 앱에서 쓰려면 Pro·Max·Team·Enterprise가 필요하고 무료 요금제는 지원하지 않습니다. API는 모델명 `claude-opus-5-5`로 호출합니다.
- **effort는 medium부터**: max는 작업당 약 11.9만 토큰을 써서 가격 인하 효과가 사라질 수 있습니다. 어려운 일만 high로 올립니다.
- **수치는 원작자 환경 기준**: 마인크래프트(약 1시간 37분, 약 $15)·렌즈 체험(1시간 26분, $25.66) 같은 시간·비용은 원 제작자가 API를 직접 호출한 경우입니다. 클로드 앱에서 실행하면 소요 시간과 품질이 달라질 수 있습니다.
- **데모는 최고 결과입니다**: 실력 좋은 사람이 뽑은 결과이고, 몇 번 시도했는지·어떤 도구를 붙였는지가 제각각이라 똑같이 한 번에 나온다는 보장은 없습니다.
- **출시 직후 정보**: 나온 지 이틀 된 시점의 자료라 개인 실무 후기는 적습니다. 업무 사례 상당수가 앤트로픽 발표 자료에 실린 고객사 인용이라, 회사가 고른 좋은 사례라는 점을 감안해야 합니다.
- **"Astra를 넘었다"에는 조건이 있습니다**: 종합 지수(58 vs 53)는 제3자 측정이지만, 코딩 시험 하나(Terminal-Bench)만 같은 설정으로 비교하면 거의 동점입니다.
- **일부 요청은 이전 모델로 넘어갑니다**: 보안·생물학 관련으로 분류된 요청은 앤트로픽이 조용히 이전 모델(Opus 4.8·Opus 5)로 보냅니다.
- **K팝 뮤직비디오 사례의 지시문**은 제작자 개인 도구(시댄스 2.5, 일레븐랩스 등)와 유료 API를 전제로 한 것이라 참고용으로만 보세요.
- **애니메이션 키트 준비물**: Node.js·크롬·ffmpeg 설치가 필요하고, 그래픽카드가 없으면 수채화 효과 렌더링이 느립니다.
- **원본 사례 링크**: 원문에는 사례 103개(업무·실무 44개, 게임 19개, 3D 월드·장면 16개, 영상·음악·애니메이션 20개, 교육·실험 4개)의 링크 모음이 있고, 원작자가 프롬프트를 공개한 사례는 📝로 표시돼 있습니다. 이 문서에는 링크 목록이 포함되지 않았으니 개별 사례·데모 링크는 원문 페이지에서 확인합니다.
- **원문이 참고한 출처**: 앤트로픽 공식 발표(anthropic.com/claude-opus-5-5), 공식 프롬프팅 가이드(platform.claude.com), Artificial Analysis(종합 지능 지수), Kingy.ai(Astra 비교 설정 차이 분석), The New Stack(이전 모델로 넘어가는 요청), blendermcp.org(Blender 연결 가이드).

## 출처

- [https://app.notion.com/p/Claude-Opus-5-5-100-3e51061c8a63811e89d6e69afa5899dd?pvs=39](https://app.notion.com/p/Claude-Opus-5-5-100-3e51061c8a63811e89d6e69afa5899dd?pvs=39)
- [https://fieldby.notion.site/5-5-10-3e5d730b3953818ead9ff0ae6badc22e?pvs=149](https://fieldby.notion.site/5-5-10-3e5d730b3953818ead9ff0ae6badc22e?pvs=149)

### 합쳐진 원본 문서

이 문서는 아래 2개 문서를 하나로 합쳐 새로 정리한 것입니다.

| 원본 문서 | 원래 슬러그 | 원본 출처 |
|---|---|---|
| Opus 5.5로 결과물 원샷 제작 | `claude-opus-5-5-recipes-and-tips` | [app.notion.com](https://app.notion.com/p/Claude-Opus-5-5-100-3e51061c8a63811e89d6e69afa5899dd?pvs=39) |
| 오퍼스5.5 프롬프트 따라하기 | `claude-opus-5-5-prompt-showcase` | [fieldby.notion.site](https://fieldby.notion.site/5-5-10-3e5d730b3953818ead9ff0ae6badc22e?pvs=149) |
