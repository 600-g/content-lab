---
name: ai-image-reference-board-generation
description: AI 이미지 생성 시 **일관성 유지**를 돕는 '레퍼런스 보드'를 만드는 스킬입니다.
origin: content-lab
grade: A
difficulty: 초급
category: 디자인
ai_tools: ["GPT"]
sources:
  - https://fieldby.notion.site/3a6d730b395381e4b56de23a839dd221?pvs=149
---

# AI 이미지 일관성 유지를 위한 레퍼런스 보드 만들기

💡 AI 이미지 생성 시 **일관성 유지**를 돕는 '레퍼런스 보드'를 만드는 스킬입니다.

## 이게 뭔가요?

레퍼런스 보드는 AI 이미지 생성 과정에서 캐릭터, 장소, 제품 등의 **일관성을 유지**하기 위해 사용되는 시각 자료입니다. 마치 영화나 애니메이션 제작팀이 사용하는 '설정 시트'와 같이, 정면, 측면, 표정, 색상 등 다양한 기준을 한 장의 이미지로 모아두어 여러 번의 이미지 생성 시에도 결과물이 동일한 세계관 안에 속하도록 합니다. 이를 통해 매번 얼굴, 옷, 배경이 바뀌는 문제를 해결하고 결과물의 통일성을 확보할 수 있습니다.

주로 ChatGPT(이미지 생성 기능)나 Gemini와 같은 AI 이미지 생성 도구에서 활용됩니다. 3:4 비율의 세로 형식으로 요청하면 시트 형태의 결과물을 얻기 용이합니다. 유료 구독이 필요한 AI 도구가 더 안정적인 결과를 제공할 수 있지만, 일부 무료 대안 도구에서도 유사한 기능을 활용할 수 있습니다.

## 따라하기

레퍼런스 보드를 만드는 과정은 크게 3단계로 나눌 수 있습니다.

1.  **기준 사진 준비**: 생성하고자 하는 캐릭터, 장소, 제품 등의 특징이 잘 나타나는 사진 한 장을 준비합니다. 인물 사진의 경우 정면이 잘 보이고 밝은 사진일수록 좋습니다.
2.  **AI 도구에 사진 첨부 및 프롬프트 입력**: ChatGPT 또는 Gemini와 같은 이미지 생성 AI에 준비한 사진을 첨부합니다. 이후 아래 설명할 보드별 프롬프트 중 원하는 것을 복사하여 사진과 함께 붙여넣습니다. 프롬프트는 세로 3:4 비율로 요청하는 것이 좋습니다.
3.  **보드 활용**: 완성된 보드 이미지를 저장합니다. 이후 동일한 인물, 장소, 제품을 다시 생성하고 싶을 때, 이전에 생성한 보드 이미지를 AI에 함께 첨부하고 "이 보드의 인물(장소/제품) 그대로 만들어줘"라고 요청하면 AI가 보드를 기준으로 삼아 일관성을 유지하며 이미지를 생성합니다.

### 보드별 프롬프트

각 보드는 특정 목적에 맞게 최적화된 프롬프트를 제공합니다. 아래 프롬프트 박스 내용을 통째로 복사하여 AI에 입력하면 됩니다.

#### 🧍 캐릭터 보드 (Character Board)

인물 한 명의 정면, 측면, 표정, 전신, 포즈 등을 한 시트에 정리합니다. 브랜드 모델이나 웹툰 주인공처럼 특정 인물의 외형을 일관되게 유지하고 싶을 때 사용합니다.

```text
Create a dense, professional CHARACTER DESIGN BOARD as a single vertical reference sheet for the person in the attached photo.
Background: warm beige textured art paper (soft cream, not white, not black). Section titles and thin divider lines in terracotta orange. Clean monospace labels.
CRITICAL: keep the EXACT same person from the photo in every panel — same face, same hairstyle, same outfit, same skin tone.
Add a small 'CHARACTER PROFILE' text box (name, age, hair, eyes, wardrobe, vibe) at the top.
Panels:
01 - VIEWS: front, 3/4 left, side profile, back
02 - EXPRESSIONS: neutral, subtle smile, serious, soft laugh
03 - DETAILS (MACRO): eyes, lips, hair texture, hands
04 - FULL BODY: one full-length standing shot
05 - POSES: standing, walking, sitting, leaning
06 - COLOR PALETTE: skin tone, hair, wardrobe swatches with hex codes
Consistent studio lighting, editorial photo style, 3:4 vertical.
```

**💡 바꿔 쓰기**: 'CHARACTER PROFILE' 항목의 내용을 원하는 설정으로 변경하여 다른 인물에게도 동일한 구조를 적용할 수 있습니다.

#### 🤸 포즈 보드 (Pose Board)

같은 인물의 기본 자세, 걷기, 앉기, 제스처 등을 다양한 각도로 모아 보여줍니다. 캐릭터의 '움직임'을 일관되게 표현하고자 할 때 유용합니다.

```text
Create a POSE BOARD / motion reference kit as a single vertical sheet for the person in the attached photo.
Warm beige paper background, terracotta section titles, monospace labels.
CRITICAL: keep the same person, same outfit, same body in every panel.
Panels:
01 - BASE POSES: relaxed stand, A-pose, contrapposto, hands on hips
02 - ANGLE COVERAGE: front, 3/4 left, side, back
03 - WALK SEQUENCE: step 1, 2, 3, 4
04 - LOW POSES: sitting, crouching, kneeling
05 - GESTURES: arms crossed, hand to face, reaching
06 - COLOR PALETTE: skin tones, hair, clothing swatches with hex codes
Full-body figures, neutral studio lighting, 3:4 vertical.
```

**💡 바꿔 쓰기**: 각 패널의 포즈 이름을 원하는 동작(예: jumping, dancing)으로 변경하여 필요한 자세만 추출할 수 있습니다.

#### 📱 오브젝트 보드 (Object Board)

제품이나 사물 하나를 여러 각도, 재질, 조명, 디테일별로 보여줍니다. 제품 상세컷이나 광고 소재 제작 시 활용됩니다.

```text
Create a product OBJECT BOARD as a single vertical reference sheet for the product in the attached photo.
Warm beige paper background, terracotta section titles, monospace labels.
CRITICAL: keep the exact same product — same shape, material, and color — in every panel.
Add a small 'OBJECT PROFILE' box (type, material, finish, key feature, vibe) at top.
Panels:
01 - VIEWS: front, back, side, 3/4 angle
02 - MATERIAL / FINISH: close-ups of the key surfaces and parts
03 - LIGHTING: studio, soft, dramatic, backlit
04 - HERO SHOT: one large glamour shot
05 - DETAILS: macro close-ups of small parts
06 - COLOR PALETTE: main body, accent, highlight swatches with hex codes
Clean product-photography style, 3:4 vertical.
```

**💡 바꿔 쓰기**: 패션, 가구, 음식 등 어떤 종류의 사물이든 원본 사진만 변경하면 동일한 구조로 보드를 생성할 수 있습니다.

#### 🏙 장소 보드 (Location Board)

하나의 장소를 시간대, 날씨, 앵글별로 정리하여 배경의 톤이 달라지는 문제를 해결합니다. 같은 배경을 여러 분위기로 유지하고 싶을 때 사용합니다.

```text
Create a LOCATION BOARD as a single vertical reference sheet for the place in the attached photo.
Warm beige paper background, terracotta section titles, monospace labels.
CRITICAL: keep the exact same location and its key elements in every panel.
Add a small 'LOCATION PROFILE' box (type, setting, key elements, mood, vibe) at top.
Panels:
01 - TIME OF DAY: morning, midday, golden hour, night
02 - WEATHER: sunny, overcast, rainy, misty
03 - VIEWPOINTS: wide, low angle, close, from across
04 - DETAILS (MACRO): textures and small elements
05 - HERO SHOT: one signature framing
06 - COLOR PALETTE: dominant color swatches with hex codes
Filmic photo style, 3:4 vertical.
```

**💡 바꿔 쓰기**: 실내, 자연, 도시 등 어떤 공간이든 원본 사진만 바꿔 넣으면 적용 가능합니다.

#### 🦀 크리처 보드 (Creature Board)

가상의 캐릭터나 마스코트를 각도, 성장 단계, 행동별로 정리합니다. 캐릭터 IP 제작 시 설정집을 굳히는 데 활용됩니다.

```text
Create a CREATURE DESIGN BOARD as a single vertical reference sheet for the creature in the attached photo.
Warm beige paper background, terracotta section titles, monospace labels.
CRITICAL: keep the exact same creature — same shape, colors, and features — in every panel.
Add a small 'CREATURE PROFILE' box (species, size, color, features, temperament) at top.
Panels:
01 - VIEWS: front, 3/4, side, back
02 - GROWTH STAGES: hatchling, juvenile, sub-adult, adult
03 - ANATOMY (MACRO): eyes, texture, limbs, underside
04 - BEHAVIOR: resting, walking, alert, moving
05 - SCALE: the creature next to a human silhouette
06 - COLOR PALETTE: body, accent, shadow swatches with hex codes
Soft 3D-render character-design style, 3:4 vertical.
```

**💡 바꿔 쓰기**: 동물, 몬스터, 로봇 등 어떤 종류의 캐릭터든 참고 이미지 변경만으로 적용할 수 있습니다.

#### 🎬 샷 보드 (Shot Board)

하나의 사진을 와이드 샷부터 클로즈업까지 12개의 콘티 컷으로 펼칩니다. 릴스나 영상 콘티를 사진 한 장에서 시작할 때 유용합니다.

```text
Create a SHOT LIST BOARD as a single vertical sheet turning the attached photo into a 12-shot storyboard.
Warm beige paper background, terracotta labels.
CRITICAL: keep the exact same person, wardrobe, scene, and lighting across all 12 frames.
Add a small header box (scene, setting, light, mood) at top.
Twelve numbered frames in a 3-column grid:
01 WIDE ESTABLISHING, 02 LONG SHOT, 03 FULL SHOT, 04 MEDIUM WIDE, 05 MEDIUM, 06 MEDIUM CLOSE, 07 CLOSE-UP, 08 EXTREME CLOSE, 09 OVER-THE-SHOULDER, 10 LOW ANGLE, 11 HIGH ANGLE, 12 WIDE FINAL
Consistent cinematic color grade, 3:4 vertical.
```

**💡 바꿔 쓰기**: 샷 이름을 원하는 컷으로 변경하여 자신만의 콘티 구성을 만들 수 있습니다.

### 💡 자주 묻는 질문

*   **Q. 프롬프트를 한국어로 바꿔도 되나요?**
    영어로 입력하는 것이 가장 안정적이지만, 한국어로 번역하여 사용해도 대체로 작동합니다. 결과가 일관되지 않으면 영어 원문으로 다시 시도해 보세요.
*   **Q. 인물이 원본과 다르게 나와요.**
    정면이 또렷하고 밝은 사진을 사용하고, 프롬프트 내 "keep the EXACT same person"과 같은 문장을 반드시 포함하세요.
*   **Q. 어떤 AI 도구를 사용하나요?**
    이미지 생성이 가능한 ChatGPT나 Gemini를 사용하면 됩니다. 세로 3:4 비율로 요청하는 것이 시트 형태의 결과물에 유리합니다.

## 출처

[레퍼런스 보드 프롬프트 가이드](https://fieldby.notion.site/3a6d730b395381e4b56de23a839dd221?pvs=149)

## 출처

- [https://fieldby.notion.site/3a6d730b395381e4b56de23a839dd221?pvs=149](https://fieldby.notion.site/3a6d730b395381e4b56de23a839dd221?pvs=149)
