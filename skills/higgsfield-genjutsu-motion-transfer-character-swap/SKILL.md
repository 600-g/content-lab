---
name: higgsfield-genjutsu-motion-transfer-character-swap
description: **Higgsfield Genjutsu Motion Transfer**로 원본 영상의 카메라 워크·안무는 그대로 두고 등장인물만 새 캐릭터로 재캐스팅하거나, **Kling 3.0 Motion Control**로 AI 인물 이미지 한 장에 원본 영상의 움직임을 복제하는 방법과 도구 선택 가이드.
origin: content-lab
grade: A
difficulty: 중급
category: 콘텐츠
ai_tools: ["GPT", "Leonardo AI", "CapCut"]
sources:
  - https://app.notion.com/p/3d7fd99f0e5f810a8da4e33e3c12e3cd?pvs=39
  - https://exultant-principle-9c5.notion.site/Higgsfield-Genjutsu-5-3d691cb23c4d81febdb6dccd1f17813f?pvs=149
  - https://yeongseon.kr/archive/3d4d86104de280fb9e40f337d6962d71.html?fbclid=PAVERFWAUYq7ZwZG9mAmZkaWQWUOky0tIFlIYUP_WiIVQubeRBOOa0h2V4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABpwnOvvdNLb7DmEDfDhYxsqwo3qVxVP8S4OOmLgGYcmkibkPC4kX_L1LDMuaL_aem_FS57y6wTmTI3bxFk25qYaQ
  - https://waiting-drug-536.notion.site/Kling-Motion-Control-3aed86104de280fdb4bcff4d311638fa?pvs=149
---

# 영상 인물 바꾸기와 동작 복제

💡 마음에 드는 **원본 영상의 움직임**을 기준으로 삼고, 그 위에 새 인물을 입힙니다. 여러 명을 한꺼번에 갈아끼우려면 **Higgsfield Genjutsu Motion Transfer**, 인물 한 명에게 동작만 입히려면 **Kling 3.0 Motion Control**을 씁니다.

## 이게 뭔가요?

AI로 영상을 처음부터 새로 생성하면 원하는 동작·카메라 앵글을 정교하게 통제하기 어렵습니다. 이 스킬은 순서를 뒤집습니다. 이미 마음에 드는 움직임(원본 영상)을 기준으로 삼고, 그 위에 인물·의상·배경 이미지를 레이어처럼 덧씌우는 구조라서 결과물의 동작 품질이 안정적입니다.

역할 분담은 어느 도구든 같습니다.

| 입력 | 결정하는 것 |
|---|---|
| 원본 영상 | 카메라 움직임·안무·타이밍·길이·인원수·동선 |
| 참조 이미지 | 새로 들어갈 인물의 얼굴·의상·배경·색감 |
| 프롬프트 (Genjutsu) | "누가 누구로 바뀌는지" 짝짓기 |

### 두 가지 도구

**Higgsfield Genjutsu**는 영상 속 인물을 다른 인물로 통째로 바꿔치기하는 AI 영상 편집 도구입니다. 힉스필드(Higgsfield)는 이미지나 스타일 레퍼런스를 기반으로 AI 영상을 생성하는 플랫폼이고, Genjutsu 안에는 두 개의 탭이 있습니다.

- **Motion Transfer**: 사람 전체를 교체 (이 스킬의 주 대상)
- **Objects swap**: 물건 하나만 교체

원본에 등장한 사람 수만큼 캐릭터가 복제돼도 각자 원래 자리와 동선은 그대로 지켜집니다. 예시로 든 원본은 GENER8ION 'STORM' 뮤직비디오의 교복 군무 장면(30초, 3840×2160)이며, 가운데 흰 셔츠를 입은 리드 한 명은 여성 캐릭터로, 검은 재킷을 입은 나머지 전원은 밀짚모자를 쓴 남성 캐릭터로 교체됐습니다.

**Kling Motion Control**은 AI가 생성한 정적인 인물 이미지에 실제 인물의 동작을 학습시켜 자연스러운 영상으로 만드는 기술입니다. AI로 만든 인물에게 특정 행동이나 춤 동작을 부여하고 싶을 때 유용합니다. GPT-2 이미지 모델로 인물 이미지를 만들고 Kling 3.0 Motion Control로 영상을 만드는 흐름이 대표적입니다.

### 어떤 방법을 언제 쓰나

| 상황 | 추천 | 이유 |
|---|---|---|
| 원본 영상 속 **여러 명**(리드 + 무리)을 각각 다른 캐릭터로 교체 | Genjutsu Motion Transfer | 인원수·동선·가림(occlusion)까지 유지하며 인물별로 지목 가능 |
| 원본의 배경·소품·조명·카메라는 **그대로 두고** 사람만 교체 | Genjutsu Motion Transfer | 장면은 원본에서, 인물만 참조 이미지에서 가져옴 |
| 표정·태도까지 세밀하게 연출 | Genjutsu Motion Transfer | 긴 프롬프트로 표정·소품·첫 프레임까지 지시 가능 |
| AI로 만든 **인물 한 명**에게 댄스·동작만 입히기 | Kling 3.0 Motion Control | 원본 동작 영상 + 인물 이미지 1장으로 끝, 프롬프트 불필요 |
| 빠르게 결과만 확인하고 싶을 때 | Kling 3.0 Motion Control | 입력 2개, 단계 3개 |
| 물건 하나만 바꾸기 | Genjutsu Objects swap | Motion Transfer가 아니라 별도 탭 |

### Genjutsu 한눈에 보기

| 항목 | 내용 |
|---|---|
| 쓰는 기능 | Higgsfield Genjutsu 안의 Motion Transfer 탭 |
| 넣는 것 | 원본 영상 1개 + 참조 이미지(캐릭터 시트 2장 또는 얼굴/장면/의상 3장) + 프롬프트 1개 |
| 원본 영상 길이 제한 | 4초 ~ 30초 (넘으면 업로드 자체가 안 됨) |
| 레퍼런스 이미지 | 최대 30장 |
| 출력 해상도 | 1080p까지 |
| 비용 (15초 기준) | 480p 40크레딧 · 720p 104크레딧 · 1080p 144크레딧 |

### 비용

- 💰 **Higgsfield Genjutsu**: 구독 및 크레딧이 필요합니다. 해상도별 크레딧 차이가 3배 이상입니다.
- 💰 **Kling Motion Control**: 원문 기준으로는 별도 유료 플랜 없이 사용 가능하다고 소개되며, CapCut 등 무료 영상 편집 툴에서 기능을 지원할 수 있습니다. 단, 특정 고도화된 AI 모델 사용 시 유료가 발생할 수 있습니다.
- ✅ **무료 대안**: Genjutsu와 동일한 모션 트랜스퍼(다인원 재캐스팅) 기능을 대체할 무료 서비스는 확인되지 않았습니다. 다만 캐릭터 시트를 준비해 인물을 지목하는 프롬프트 구조 자체는 다른 영상 생성 도구에도 참고할 수 있고, 참조 이미지(얼굴·장면·의상) 준비는 Bing Image Creator·Leonardo AI 등 무료 이미지 생성 도구로 대체할 수 있습니다. 단순 동작 입히기는 CapCut의 'AI 효과' 또는 유사 기능, Stable Diffusion 기반 영상 생성 등으로도 시도할 수 있습니다. 스타일 참조 영상이 목적이라면 CapCut, Canva 등의 무료 템플릿 기반 영상 편집도 대안이 됩니다(단, Genjutsu와 동일한 AI 생성 방식은 아님).

## 따라하기

### 0. 공통 준비: 원본 영상과 인물 이미지

1. **원본 영상을 정합니다.** 움직임의 기준이 될 영상입니다. Genjutsu는 4~30초 구간만 받으므로 긴 영상은 미리 잘라 둡니다. 결과물 길이는 원본에서 정해지며, 프롬프트로 늘리거나 줄일 수 없습니다.
2. **인물 이미지를 준비합니다.** 직접 촬영한 사진, 무료 이미지 생성 도구로 만든 이미지, 또는 아래 GPT 이미지 프롬프트로 만든 AI 인물을 씁니다. 어떤 도구든 **전신(상하체)이 잘 보이도록** 만들어야 오류 없이 자연스러운 결과가 나옵니다.

**AI 인물 이미지 만들기 (GPT-2 이미지 모델)**

여성 인물 프롬프트 예시:
```
A beautiful Korean female influencer in her 20s practicing dance in a studio, wearing trendy, hip attire reminiscent of a real idol; a full-body shot highlighting her stylish outfit and pretty face.
```

남성 인물 프롬프트 예시:
```
A handsome Korean male influencer in his 20s practicing dance in a studio, wearing trendy, stylish attire reminiscent of a real-life idol; a full-body shot highlighting his handsome face and outfit.
```

- 의상 스타일, 표정, 배경 등 원하는 부분만 수정해 이미지를 만들 수 있습니다.
- GPT-2 이미지 모델은 영문 프롬프트뿐 아니라 한국어 프롬프트로도 좋은 결과물을 내는 경우가 많습니다.
- Genjutsu용 캐릭터 시트를 만들 때도 같은 프롬프트를 출발점으로 삼아 정면·측면·후면·얼굴 클로즈업 4방향을 한 장에 담도록 요청하면 됩니다.

### 방법 1. Higgsfield Genjutsu Motion Transfer로 다인원 재캐스팅

#### 1-1. 참조 이미지 구성 방식 고르기

| 방식 | 구성 | 언제 |
|---|---|---|
| **2장 캐릭터시트 방식** | 한 인물당 시트 1장에 정면·측면·후면·얼굴 클로즈업 4방향을 모두 담아 얼굴+의상을 한 번에 지정 | 리드 1명 + 무리 전원처럼 인물 단위로 교체할 때 |
| **3장 역할분담 방식** | 얼굴(Image1)·장면/의상+배경 색감(Image2)·의상 전신(Image3)으로 역할을 쪼개 각각 한 장씩 | 주인공 한 명의 얼굴·의상·분위기를 따로 통제할 때 |

3장 방식의 슬롯별 역할은 다음과 같습니다.

- `Video1 — 움직임`: 참고할 원본 영상. 카메라 워크·안무·타이밍·길이를 전부 결정
- `Image1 — 얼굴`: 주인공의 얼굴·헤어가 잘 보이는 사진
- `Image2 — 장면`: 주인공의 의상·주변 인물·배경·색감을 한눈에 볼 수 있는 사진
- `Image3 — 의상`: 의상만 전신으로 보이는 사진 (원치 않는 액세서리는 미리 제외)

이미지마다 역할(얼굴/장면/의상)을 명확히 나누는 것이 핵심입니다. 복면처럼 원치 않는 요소가 남아 있는 예전 AI 생성 영상을 움직임 기준으로 재사용하지 않도록 주의합니다.

#### 1-2. Genjutsu 열기

Higgsfield Genjutsu 접속 → `Generate now` 클릭 → `Motion Transfer` 선택. 사람을 통째로 갈아끼우는 건 Motion Transfer, 물건 하나만 바꾸는 건 Objects swap이므로 반드시 Motion Transfer를 선택합니다.

강의·이벤트 등에서 받은 힉스필드 바로가기는 아래처럼 제휴/추천 링크 형태인 경우가 있습니다. 필요하면 공식 higgsfield.ai 사이트에서 직접 접속해도 됩니다.
```
higgsfield.ai (s/viral-ig-v2-ai.yeongseon-jNKMfc)
```

#### 1-3. 원본 영상 1개 업로드

이 영상이 카메라 움직임·춤·타이밍·길이를 전부 결정합니다. 원본 영상 구간(초 단위)을 정확히 맞추지 않으면 의도한 길이의 결과물이 나오지 않습니다.

#### 1-4. 참조 이미지를 순서대로 붙이고 슬롯 번호를 프롬프트와 일치시키기

화면에 표시되는 이미지 슬롯 번호(1, 2, 3...)와 프롬프트에 적을 이미지 번호를 반드시 일치시킵니다. 어긋나면 얼굴·의상·색감이 엉뚱하게 섞여 나옵니다.

- 2장 방식: 첫 번째 슬롯 = 가운데에서 리드할 인물(4방향 시트), 두 번째 슬롯 = 무리 전원이 될 인물(4방향 시트)
- 3장 방식: `Image1(얼굴) → Image2(장면) → Image3(의상)` 순으로 첨부

#### 1-5. 프롬프트 입력 토글을 켜고 전문 붙여넣기

기본 프리셋만으로는 "누구를 누구로 바꿀지"를 지정할 수 없습니다. 영상(`@Video1`)은 동작·카메라·타이밍의 기준, 이미지(`@Image1~3`)는 얼굴·의상·색감의 기준이라는 역할 구분을 지키고, 주변 인물이 화면에서 가려졌다가 다시 등장해도 같은 모습을 유지하도록 지시하는 문장을 반드시 포함합니다. 아래는 2장 캐릭터시트 방식으로 실제 사용한 프롬프트 전문입니다.

```
Use @[Video 1](video_1) as the source for the original camera movement, framing, perspective, choreography, timing, performer count, formation, movement paths, school setting, lighting, shot structure, and duration. Recast the performers as described below while preserving the original composition and body choreography. The lead woman's facial performance is directed separately below.
REFERENCE INTERPRETATION
@[Image 1](image_1) shows multiple views of ONE adult woman.
@[Image 2](image_2) shows multiple views of ONE adult man.
Use these sheets to define each character's identity and complete outfit. Do not reproduce the reference-sheet layout, white background, or multiple views inside the video.
CHARACTER ASSIGNMENT
Replace only the original performer wearing a white long-sleeve school shirt and striped tie WITHOUT a dark blazer with the woman from @[Image 1](image_1).
At the beginning, this source performer is close to the camera with his back facing the camera, then moves into the formation. Track that same source performer throughout the video, including when partially hidden. Identify him by his original identity and trajectory, not by whoever currently occupies the center of the frame.
Match the woman's reference appearance and complete outfit: long copper-brown hair, teal halter top, denim shorts, brown belt, necklace, bracelets, and brown ankle boots. Preserve her exact reference facial structure, body proportions, and feminine appearance throughout.
Replace EVERY original dark-blazer performer with the adult man from @[Image 2](image_2), matching his face, black hair, scars, straw hat with a red band, weathered red sleeveless vest, blue cropped trousers, mustard waist sash, and brown sandals.
Each original dark-blazer performer becomes one separate instance of this same man. Every instance follows its own corresponding source performer's movement. Preserve the number of performers, their individual trajectories, spacing, row assignments, and front-to-back order.
Never exchange the two character assignments or mix their faces, hair, bodies, outfits, or accessories.
LEAD WOMAN — BODY MOTION AND BOSS PRESENCE
Transfer the original white-shirt performer's walking path, body choreography, arm and hand gestures, footwork, torso movements, head turns, head tilts, and action timing to the woman.
Do not transfer his facial expressions or facial mannerisms. @[Video 1](video_1) controls her body motion and head orientation; @[Image 1](image_1) controls her facial identity and feminine appearance.
She carries the calm authority of the woman in charge of the entire group. Her expression is cool, self-assured, and quietly intimidating, as though she already owns the room and has nothing to prove.
Express this through a steady, assessing gaze, composed brows, a relaxed jaw, and a controlled neutral mouth. Preserve the feminine facial features of @[Image 1](image_1). Her authority comes from restraint and confidence, not exaggerated aggression.
Keep subtle blinking and small, natural facial responses. Do not freeze her face. Do not add a constant smile, a cute expression, flirtatious eye contact, or an exaggerated villainous smirk.
Do not imitate the source lead's scowling, forceful jaw tension, exaggerated grimaces, lip curling, or exaggerated mouth movements. Do not reshape her face to resemble the source actor.
Preserve the source head angles and gaze targets. Convey her commanding attitude through her eyes and facial expression without adding new chin lifts, head poses, gestures, or movement.
During cigarette contact, allow the natural lip movement needed to hold or draw on the cigarette, then return to her cool, composed expression. Preserve the smoking gesture and timing without copying the source actor's surrounding facial expression.
MOTION AND VISIBILITY
Preserve each source performer's body placement, orientation, foot placement, gestures, head movements, choreography, and timing. The lead woman's facial expression follows the separate direction above.
Keep each replacement anchored to the corresponding source performer rather than moving it toward the camera or center.
Maintain the source occlusions: when a performer is hidden behind another person, the replacement remains hidden; when that performer reappears, the same replacement identity returns. Do not expose a hidden body or face to showcase the reference character.
Allow natural silhouette differences caused by the replacement body, long hair, clothing, and straw hat without shifting the performer's underlying position or movement path. Hair, fabric, and hats respond naturally to the source motion.
Every crowd performer wears the reference straw hat from their first appearance. Keep each hat attached to its own wearer and consistent through turns, bending, and partial occlusion.
FIRST-FRAME CONTINUITY
All visible targets are already fully replaced in the opening frame. Any performer revealed later is already replaced when first visible. There is no transformation sequence, delayed wardrobe change, or return to the original appearance.
CIGARETTES AND SCENE
Retain the original cigarettes and smoking actions, including their original hand or mouth attachment and timing. Preserve naturally visible smoke. Do not add cigarettes or replace them with toothpicks.
Keep the original school architecture, background, camera work, scene lighting, and props. Integrate the new bodies and outfits with natural shadows, motion blur, and ground contact consistent with the source footage.
Preserve the original audio without adding new speech, music, or sound effects. Do not infer new lip-sync or facial acting from the soundtrack.
The final result preserves the original body choreography and formation, with @[Image 1](image_1) replacing the single original white-shirt lead and @[Image 2](image_2) replacing every original dark-blazer performer. The woman retains her exact reference identity and feminine appearance while projecting the restrained confidence and quiet authority of the group's boss. Maintain photoreal live-action appearance and stable identities throughout.
```

프롬프트는 다음 블록으로 짜여 있어, 3장 방식이나 다른 콘셉트에 응용할 때도 같은 뼈대를 쓰면 됩니다.

| 블록 | 하는 일 |
|---|---|
| 첫 문단 | `@Video 1`이 카메라·안무·타이밍·인원·장소·길이의 기준임을 선언 |
| REFERENCE INTERPRETATION | 시트 한 장 = 한 사람임을 명시, 시트 레이아웃·흰 배경을 영상에 옮기지 말 것 |
| CHARACTER ASSIGNMENT | 원본의 누구를(옷 특징으로) 어떤 참조 인물로 바꾸는지, 첫 등장 위치로 추적 시작점 지정 |
| LEAD … BODY MOTION | 몸 동작은 원본에서, 얼굴 정체성과 표정 연출은 참조 이미지·지시문에서 |
| MOTION AND VISIBILITY | 각 인물의 위치·동선 고정, 가림(occlusion) 유지, 소품 고정 |
| FIRST-FRAME CONTINUITY | 첫 프레임부터 이미 교체 완료, 변신 장면 금지 |
| 소품·장면 | 원본 소품·배경·조명·오디오 유지 |
| 마지막 문단 | 전체 요약과 실사 톤 고정 |

#### 1-6. 내 소재에 맞게 바꿔야 할 지점

프롬프트를 그대로 붙여넣는다고 원하는 결과가 바로 나오지는 않습니다. 원본에서 바꿀 사람을 옷으로 지목하는 문장이 조금만 헐거우면 엉뚱한 사람이 바뀝니다. ★ 표시한 자리부터 손보는 순서를 권합니다.

| 프롬프트 속 문구 | 지금 뜻 | 내 것으로 바꿀 때 |
|---|---|---|
| ★ wearing a white long-sleeve school shirt and striped tie WITHOUT a dark blazer | 원본에서 바꿀 주인공을 옷으로 지목한 문장 | 가장 중요한 한 줄. 내 원본에서 그 사람만 가진 옷 특징으로 다시 쓴다. 다른 사람과 겹치는 특징을 쓰면 엉뚱한 사람이 바뀐다 |
| ★ EVERY original dark-blazer performer | 원본에서 나머지 무리를 옷으로 지목한 문장 | 내 원본에서 나머지 사람들이 공통으로 걸친 옷 특징으로 |
| ★ long copper-brown hair, teal halter top, denim shorts, brown belt, necklace, bracelets, and brown ankle boots | 시트 1 인물의 머리와 의상 전체 | 내 시트를 보고 머리색, 상의, 하의, 벨트, 액세서리, 신발까지 빠짐없이 다시 쓴다. 안 적은 것은 영상에서 사라진다 |
| ★ straw hat with a red band, weathered red sleeveless vest, blue cropped trousers, mustard waist sash, and brown sandals | 시트 2 인물의 의상 전체 | 위와 같은 요령으로 시트 2를 보고 다시 쓴다 |
| ★ @[Image 1] shows multiple views of ONE adult woman / ONE adult man | 시트마다 몇 명이 들었고 성별이 무엇인지 | 내 시트의 성별과 나이대로 바꾼다. ONE은 그대로 두어야 한다. 한 장에 두 사람이 들어 있으면 얼굴이 섞인다 |
| school setting / Keep the original school architecture | 원본이 학교라서 학교로 적은 배경 | 원본 장소로 바꾼다. 무대면 stage, 거리면 street, 체육관이면 gymnasium |
| At the beginning, this source performer is close to the camera with his back facing the camera | 주인공이 첫 프레임에 어디 있는지 | 내 원본의 첫 등장 위치와 방향을 그대로 묘사한다. 이 문장이 추적의 출발점이다 |
| LEAD WOMAN / her / she / feminine appearance | 주인공이 여성이라 붙은 표현들 | 주인공이 남성이면 문단 제목과 대명사를 전부 남성형으로 바꾼다. 한 군데라도 남으면 얼굴이 흔들린다 |
| cool, self-assured, and quietly intimidating | 주인공에게 입힌 표정과 태도 | 원하는 분위기로 바꾼다. 밝게 가려면 warm, open, easily smiling 식으로 |
| Do not add a constant smile, a cute expression, flirtatious eye contact | 원치 않는 표정을 미리 막는 문장 | 위에서 정한 분위기의 반대말로 다시 쓴다 |
| Do not imitate the source lead's scowling, forceful jaw tension, exaggerated grimaces | 원본 배우의 표정 버릇을 안 옮기게 막는 문장 | 내 원본 배우의 얼굴 버릇 중 안 가져오고 싶은 것으로 |
| cigarette / smoking gesture / Do not add cigarettes or replace them with toothpicks | 원본에 담배가 나와서 넣은 문단 | 원본에 담배가 없으면 관련 문장을 통째로 지운다. 다른 소품이면 그 소품 이름으로 |
| Every crowd performer wears the reference straw hat | 무리 전원이 쓴 소품 이름 | 시트 2에 모자가 없으면 그 자리를 다른 소품 이름으로 바꾸거나 문장을 지운다 |
| Preserve the original audio | 원본 소리를 그대로 둠 | 그대로 둔다. 소리를 새로 넣으면 입 모양이 흔들린다 |
| photoreal live-action appearance | 실사 톤으로 고정 | 애니메이션 톤이 필요하면 이 자리에서 화풍을 지정한다 |

요약하면 "원본에서 누구를 지목하는가"와 "내 참조 이미지가 어떻게 생겼는가", 이 두 가지만 정확히 갈아끼우면 나머지는 거의 그대로 재사용됩니다. 3장 역할분담 방식으로 다른 콘셉트에 응용할 때도 이미지별 인물·의상·배경 설명과 영상 길이 값만 바꾸면 됩니다. 이때 `@[Image 1]`(얼굴)·`@[Image 2]`(장면·색감)·`@[Image 3]`(의상)처럼 프롬프트 안에서도 이미지마다 역할을 한 가지씩만 맡깁니다.

#### 1-7. 해상도를 고르고 생성

먼저 480p로 돌려서 인물이 제대로 갈렸는지 확인한 뒤, 맞으면 1080p로 다시 뽑는 순서를 권장합니다. 480p와 1080p는 크레딧 차이가 3배가 넘습니다(15초 기준 40 vs 144크레딧). 3장 역할분담 방식의 출력 옵션 예시는 720p·30초·1개 생성입니다.

### 방법 2. Kling 3.0 Motion Control로 인물 한 명에 동작 복제

1. **Kling Motion Control 접속**: 메뉴에서 `비디오` → `클링 3.0 모션 컨트롤`을 클릭합니다.
2. **영상 및 이미지 입력**: 좌측에는 **원본 동작 영상**을, 우측에는 **0단계에서 만든 인물 이미지**를 넣습니다.
3. **결과 확인**: 시스템이 원본 영상의 동작을 분석해 우측 이미지에 적용하고 새로운 영상을 생성합니다.

💡 원본 이미지를 생성할 때 **전신(상하체)이 잘 보이도록** 만들어야 Kling Motion Control에서 오류가 나지 않고 결과가 자연스럽습니다. 복잡하거나 미묘한 표정·동작은 한계가 있으니, 결과물은 편집 툴에서 후처리해 다듬습니다.

### 결과 점검 체크리스트

- [ ] 지목한 인물만 바뀌었고, 나머지는 의도대로 교체(또는 유지)됐다
- [ ] 시트에 있던 모자·신발·액세서리가 영상에 모두 남아 있다
- [ ] 가려졌다가 다시 나온 인물이 같은 얼굴로 돌아왔다
- [ ] 첫 프레임부터 교체가 완료돼 있고 변신 장면이 없다
- [ ] 원본 오디오·배경·소품이 유지됐다
- [ ] (Kling) 손·발 등 전신이 깨지지 않았다
- [ ] 저해상도 테스트 통과 후에만 고해상도로 재생성했다

### 트러블슈팅

| 증상 | 원인일 가능성이 높은 곳 | 고치는 법 |
|---|---|---|
| 엉뚱한 사람이 바뀐다 | 옷 지목 문장이 다른 사람과 겹치는 특징을 쓰고 있음 | 그 사람만 가진 옷 특징으로 다시 쓰고, 첫 등장 위치 문장을 보강 |
| 시트에 있던 모자나 신발이 사라진다 | 프롬프트에 해당 소품을 명시적으로 적지 않음 | 머리부터 신발까지 빠짐없이 나열 |
| 뒤에 가려졌다 나온 사람이 다른 얼굴로 나온다 | occlusion(가림) 관련 문장이 빠졌거나 약함 | MOTION AND VISIBILITY 블록의 가림 유지 문장을 그대로 유지·강화 |
| 얼굴·의상·색감이 엉뚱하게 섞인다 | 슬롯 번호와 프롬프트의 이미지 번호가 어긋남 | 붙인 순서와 `@[Image N]` 번호를 다시 맞춤 |
| 얼굴이 두 사람 섞인 것처럼 나온다 | 한 장의 시트에 두 사람이 들어 있음 / 성별 대명사가 섞임 | 시트 1장 = 1명, 대명사·문단 제목을 한 성별로 통일 |
| 원치 않는 액세서리·복면이 따라 나온다 | 참조 이미지나 움직임 기준 영상에 그 요소가 남아 있음 | 참조 이미지를 다시 고르고, 예전 AI 생성 영상을 움직임 기준으로 쓰지 않음 |
| 결과 길이가 다르다 | 원본 영상 구간을 정확히 자르지 않음 | 원본을 원하는 길이(4~30초)로 정확히 잘라 재업로드 |
| (Kling) 오류가 나거나 동작이 어색하다 | 인물 이미지에 전신이 다 보이지 않음 | 상하체 전신이 보이도록 이미지를 다시 생성 |

## 활용 예시

- **뮤직비디오 군무 재캐스팅** (Genjutsu): 상업 뮤직비디오 대신 직접 촬영한 군무 영상 30초를 올리고, 리드 1명 + 나머지 전원용 캐릭터 시트 2장만 준비하면 → 동일한 안무·동선을 유지한 채 오리지널 캐릭터가 주인공인 영상으로 재탄생합니다.
- **브랜드 광고 리스킨** (Genjutsu): 광고 모델이 나온 짧은 영상을 원본으로 쓰고, 브랜드 마스코트 캐릭터 시트를 준비해 프롬프트의 옷 지목 문구만 마스코트 특징으로 바꾸면 → 같은 카메라 워크와 타이밍으로 마스코트가 등장하는 광고 컷을 만듭니다.
- **코스프레/버추얼 캐릭터 댄스 영상** (Genjutsu): 안무 챌린지 영상 하나를 원본으로 두고, 버추얼 캐릭터 시트(정면·측면·후면·클로즈업 4방향)를 만들어 넣으면 → 실제 촬영 없이 버추얼 캐릭터가 같은 안무를 추는 영상이 완성됩니다.
- **세계관/컨셉 변경 영상** (Genjutsu 3장 방식): 같은 원본 영상에 의상 이미지(Image3)만 바꿔 넣으면 → 수녀 컨셉 대신 SF·판타지 등 다른 컨셉의 영상을 같은 동작으로 재생성합니다.
- **배경 인물 일괄 교체** (Genjutsu): 프롬프트에 "주변 인물은 전부 다른 얼굴의 ○○으로 바꾸고 재등장 시에도 동일 인물 유지" 문장을 넣으면 → 엑스트라까지 일관된 새 캐릭터로 채워진 장면을 얻습니다.
- **댄스 챌린지 영상 제작** (Kling): 인기 댄스 챌린지 영상의 동작을 AI 인물에게 입혀 자신만의 스타일로 재해석한 댄스 영상을 만듭니다.
- **가상 아이돌 프로모션** (Kling): AI로 생성한 가상 아이돌의 데뷔 영상이나 퍼포먼스 영상을 만들어 공개합니다.
- **패션 인플루언서 콘텐츠** (Kling): AI 인물이 최신 유행 의상을 입고 워킹하거나 포즈를 취하는 영상으로 패션 트렌드를 보여줍니다.

## 💡 아이디어

- **개인화된 AI 아바타**: 사용자가 자신의 사진이나 원하는 인물 사진을 올리면 그 인물이 특정 동작을 수행하는 영상을 만들어 주는 서비스.
- **교육용 콘텐츠**: 운동 동작, 악기 연주법 같은 특정 동작을 AI 인물이 시연하는 영상을 만들어 학습 효과를 높입니다.
- **커머스 제품 홍보**: 의류나 액세서리를 AI 모델이 착용한 영상을 만들어 온라인 쇼핑몰에서 활용합니다.
- **2단계 조합**: Kling으로 인물 한 명의 동작 영상을 먼저 만들어 보고 마음에 드는 캐릭터가 정해지면, 그 캐릭터의 4방향 시트를 만들어 Genjutsu로 다인원 장면에 투입합니다.

## 주의사항

- **원본 영상 길이는 4초~30초로 고정**(Genjutsu)입니다. 30초를 넘으면 업로드 자체가 안 되므로 긴 영상은 먼저 30초 안으로 잘라야 합니다.
- **저작권**: 상업 뮤직비디오를 예시로 연습용으로 돌려보는 건 괜찮지만, 결과물을 그대로 공개 배포하면 음원·영상 저작권 문제가 생길 수 있습니다. 공개용은 직접 촬영한 영상이나 이용 허락을 받은 영상으로 바꿔야 합니다.
- **시트/이미지 순서 실수**: 참조 이미지를 붙이는 순서가 프롬프트의 `@[Image 1]`, `@[Image 2]`(또는 `@Image1~3`) 지목 순서를 그대로 결정합니다. 순서를 바꿔 붙이거나 슬롯 번호와 프롬프트 번호가 어긋나면 얼굴·의상·색감이 섞이거나 지목한 인물이 통째로 뒤바뀝니다.
- **참조 이미지 속 원치 않는 요소**: 펜던트·십자가 등 원치 않는 액세서리가 참조 이미지에 남아 있으면 결과물에도 그대로 반영됩니다. 의상 참고 이미지는 원치 않는 요소를 미리 빼고 촬영/선별해야 합니다. 복면 등 가려진 부분이 있는 예전 AI 생성 영상을 움직임 기준으로 재사용하면 원치 않는 요소가 새 영상에 섞여 들어갈 수 있습니다.
- **크레딧 관리**: 480p로 먼저 테스트하고 맞으면 1080p로 재생성합니다. 해상도별 크레딧 차이가 3배 이상이라 1080p로 바로 돌리면 실패 시 낭비가 큽니다.
- **전신 이미지 필수**(Kling): 전신이 명확하게 드러나지 않으면 후속 영상 생성에서 오류가 나기 쉽습니다.
- **표현 한계**: 복잡하거나 미묘한 표정·동작 표현에는 한계가 있을 수 있으니 편집 툴 후처리를 염두에 둡니다.
- **강의·추천 링크**: 힉스필드 바로가기가 제휴/추천 링크(`s/viral-ig-v2-ai.yeongseon-jNKMfc`) 형태로 배포되는 경우가 있습니다. 강의 소개 페이지에 붙은 오픈카톡방·카페 링크는 도구 사용법과 무관하며, 상세 조작법은 공식 사이트나 별도 가이드북에서 확인합니다.

## 출처

- [https://app.notion.com/p/3d7fd99f0e5f810a8da4e33e3c12e3cd?pvs=39](https://app.notion.com/p/3d7fd99f0e5f810a8da4e33e3c12e3cd?pvs=39)
- [https://exultant-principle-9c5.notion.site/Higgsfield-Genjutsu-5-3d691cb23c4d81febdb6dccd1f17813f?pvs=149](https://exultant-principle-9c5.notion.site/Higgsfield-Genjutsu-5-3d691cb23c4d81febdb6dccd1f17813f?pvs=149)
- [https://yeongseon.kr/archive/3d4d86104de280fb9e40f337d6962d71.html?fbclid=PAVERFWAUYq7ZwZG9mAmZkaWQWUOky0tIFlIYUP_WiIVQubeRBOOa0h2V4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABpwnOvvdNLb7DmEDfDhYxsqwo3qVxVP8S4OOmLgGYcmkibkPC4kX_L1LDMuaL_aem_FS57y6wTmTI3bxFk25qYaQ](https://yeongseon.kr/archive/3d4d86104de280fb9e40f337d6962d71.html?fbclid=PAVERFWAUYq7ZwZG9mAmZkaWQWUOky0tIFlIYUP_WiIVQubeRBOOa0h2V4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABpwnOvvdNLb7DmEDfDhYxsqwo3qVxVP8S4OOmLgGYcmkibkPC4kX_L1LDMuaL_aem_FS57y6wTmTI3bxFk25qYaQ)
- [https://waiting-drug-536.notion.site/Kling-Motion-Control-3aed86104de280fdb4bcff4d311638fa?pvs=149](https://waiting-drug-536.notion.site/Kling-Motion-Control-3aed86104de280fdb4bcff4d311638fa?pvs=149)
