# Codex Pet — AI 펫 제작

- URL: https://resonant-frog-df5.notion.site/Codex-Pet-AI-35c3a1a3234381fb9b8bd2ca7adb8d29
- source_type: notion
- length: 3967 chars
- elapsed: 7s
- ok: True

---

💡 댓글 다신 팔로워분들께 드리는 Codex Pet 실전 활용 가이드입니다!

### Codex Pet이란?

OpenAI Codex 데스크톱 앱에 내장된 플로팅 AI 동반자 UI입니다. 단순히 귀여운 장식이 아니라, Codex가 지금 무엇을 하고 있는지 직관적으로 알려주는 실용적인 기능이에요.

기존에는 Codex에게 코딩을 시키면 몇 분씩 기다리며 이런 고민을 했죠:

지금 생각 중인가?

내 답변을 기다리며 멈춰 있는 건가?

이미 완료하고 리뷰를 기다리는 중인가?

Codex Pet은 작은 동물의 행동 상태로 이 문제를 해결합니다.

### 펫의 3가지 핵심 상태

상태 | 표시 의미 | 실무 활용 팁 |
|---|---|---|
🏃 Running (달리는 중) | Codex가 현재 작업 진행 중 | 다른 업무로 전환해도 OK |
⏳ Waiting (대기 중) | 사용자 입력/응답을 기다리는 중 | 빠르게 확인하고 입력 필요 |
✅ Review (검토 대기) | 작업 완료, 리뷰 요청 상태 | 결과물 확인 타이밍 |

🎯 멀티태스킹 환경에서 특히 효과적입니다. 창을 일일이 전환하지 않아도 펫 상태만 보면 작업 흐름을 파악할 수 있어요.

### ⚠️ 시작 전 사전 준비

#### 1. Codex Desktop 앱 설치 필수

Codex Pet은 Codex Desktop 앱에서만 작동합니다. CLI(터미널) 버전에서는 사용 불가합니다. 아래 방법으로 Desktop 앱을 설치하세요:

JavaScript

# 방법 1: npm 설치 후 데스크톱 앱 실행
npm i -g @openai/codex
codex app
# 방법 2: Homebrew (macOS)
brew install --cask codex

혹은 Codex App 페이지에서 직접 다운로드.

#### 2. 구독 플랜 필요 확인

Codex Desktop 사용은 ChatGPT 유료 구독이 있어야 합니다.

플랜 | Codex 사용 가능 |
|---|---|
Free / Go | 한시적 무료 제공 중 |
Plus | ✅ 사용 가능 |
Pro $100 | ✅ 2x 활용 (2026.05.31까지 프로모) |
Pro $200 | ✅ 최대 활용 |
Business / Enterprise / Edu | ✅ 사용 가능 |

💡 포인트: 현재 임시적으로 Free 플랜도 사용 가능하지만, 정식 서비스는 유료 구독 필요입니다.

### Step 1 — Codex Pet 활성화하기

#### 기본 설정 (3단계)

JavaScript

1단계: 최신 버전 Codex로 업데이트 (Pets 기능 포함 버전 필요)
2단계: 입력창에 /pet 입력
또는 Settings → Appearance → Pets 이동
3단계: 원하는 내장 펫 선택 또는 커스텀 펫 설치

#### 내장 펫 빠르게 켜기/끄기

JavaScript

/pet

입력창에

/pet

을 입력하면 펫이 토글됩니다.### Step 2 — 커스텀 펫 만들기 (hatch-pet)

기본 제공 펫 외에, 나만의 캐릭터를 직접 만들 수 있습니다.

#### hatch-pet 스킬 설치 (신규 시)

hatch-pet은 openai/skills 리포지토리의 공식 스킬입니다.

하단 명령어로 설치하거나, GitHub 링크에서 직접 확인할 수 있어요.

JavaScript

# 1. Codex 입력창에서 스킬 설치
$skill-installer hatch-pet
# 2. 스킬 리로드: Cmd+K (macOS) / Ctrl+K (Windows)
→ "Force Reload Skills" 선택
# 3. 펫 생성 시작
$hatch-pet create a new pet inspired by my recent projects

#### hatch-pet 명령어 사용법

JavaScript

# 기본 형식
$hatch-pet [원하는 캐릭터 설명]
# 예시 1: 코드 스타일 기반
$hatch-pet 내 최근 코드 스타일(주로 Rust)을 기반으로 펫을 부화시켜줘
→ 게(Crab) 캐릭터가 생성될 가능성이 높습니다
# 예시 2: 구체적인 캐릭터 지정
$hatch-pet 실험실 가운을 입은 카피바라를 만들어줘
# 예시 3: 사진 기반 생성
$hatch-pet 이 사진 속 고양이를 Codex 펫으로 만들어줘
(사진 첨부)
# 예시 4: 상태 반응 지정
$hatch-pet 작은 픽셀 스타일의 검은 고양이, 노란 눈, 코딩할 때 졸다가 완료되면 반짝이는 느낌의 Codex pet 만들어줘

### Step 3 — 커스텀 펫 제작 전체 흐름

① 콘셉트 정하기

펫은 작은 크기로 표시되므로 단순하고 알아보기 쉬운 디자인이 좋습니다.

픽셀 스타일 추천

외곽선 두껍게

디테일 최소화

② hatch-pet 명령어로 생성 요청

위 명령어 예시를 참고해서 Codex에 요청합니다.

③ 기준 이미지(Base Image) 확인

생성된 기준 이미지가 모든 애니메이션의 원본이 됩니다.

④ 애니메이션 상태 설정 (hatch-pet 스킬이 다 해줌, 내가 할 필요 없음!)

상태 이름 | 동작 의미 |
|---|---|
idle | 평소 대기 |
running-right | 오른쪽 이동 |
running-left | 왼쪽 이동 |
waving | 완료 반응 |
jumping | 강조 |
failed | 오류 발생 |
waiting | 입력 대기 |
running | 작업 진행 중 |
review | 검토 요청 |

⑤ 스프라이트시트 생성 (Codex가 다 해줌, 내가 할 필요 없음!)

항목 | 조건 |
|---|---|
전체 크기 | 1536 × 1872 |
셀 크기 | 192 × 208 |
구조 | 8 × 9 |
형식 | WebP |
배경 | 투명 |

⑥ 파일 구성(Codex가 다 해줌, 내가 할 필요 없음!)

JavaScript

~/.codex/pets/[펫이름]/spritesheet.webp
~/.codex/pets/[펫이름]/pet.json

⑦ pet.json 작성 (Codex가 다 해줌, 내가 할 필요 없음!)

JSON

{
"id": "your-pet-name",
"displayName": "펫 표시 이름",
"description": "상태 반응 설명",
"spritesheetPath": "spritesheet.webp"
}

⑧ Codex에 적용

설치 경로:

~/.codex/pets/[펫이름]

설정값:

custom:[펫이름]

앱 재실행 후

/pet

명령어로 확인### 적용 확인 체크리스트

앱을 재실행했나요?

~/.codex/pets/[이름]/

폴더가 존재하나요?pet.json

파일이 있나요?파일명이 정확히

spritesheet.webp

인가요?설정값이

custom:[이름]

형식인가요?### 성향별 추천 전략

나의 상황 | 추천 방법 |
|---|---|
기본부터 시작하고 싶다 | /pet 으로 내장 펫 먼저 활성화 |
개성 있는 펫을 원한다 | $hatch-pet 으로 커스텀 생성 |
집중력이 방해될 것 같다 | 일단 끄고 사용, 핵심 기능에 영향 없음 |
Claude Code도 함께 쓴다 | Codex에는 Pets, Claude Code에는 MCP Buddy 설치 |

### 실사용자 평가 (5점 만점)

평가 항목 | 평균 점수 | 핵심 피드백 |
|---|---|---|
상태 인지 효율성 | ⭐ 4.6 | "진행률 표시줄보다 직관적" |
멀티태스킹 도움 | ⭐ 4.4 | "어떤 작업이 대기 중인지 바로 파악" |
커스터마이징 만족도 | ⭐ 4.7 | "나만의 캐릭터를 키우는 소속감" |
장기 사용 의향 | ⭐ 4.1 | "없으면 허전할 것 같다" |

### 마무리

Codex Pet의 핵심 가치는 "지금 AI가 뭔 하고 있지?" 라는 멀티태스킹 상황의 인지 부담을 줄여주는 데 있습니다. 작은 동물의 행동 하나로 작업 흐름을 파악하고, 나만의 캐릭터로 개성도 더할 수 있어요.

완성까지 전체 흐름 요약:

콘셉트 → hatch-pet 생성 → 기준 이미지 → 애니메이션 → 수정 → 스프라이트 → json → 설치 → 설정 → 확인 ✅

📌 참고 자료
