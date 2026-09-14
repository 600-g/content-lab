---
name: higgsfield-genjutsu-motion-transfer-character-swap
description: Higgsfield Genjutsu의 Motion Transfer 탭에 원본 영상 1개와 참조 이미지(캐릭터 시트 2장 또는 얼굴·장면·의상 역할별 3장)를 넣고, 누가 누구로 바뀌는지 지목하는 프롬프트를 작성하면 카메라 워크·안무·타이밍은 그대로 유지한 채 등장인물만 새 캐릭터로 재캐스팅된다. 480p로 먼저 테스트한 뒤 1080p로 최종 생성하는 순서를 권장한다.
origin: content-lab
grade: A
difficulty: 중급
category: 콘텐츠
ai_tools: ["도구무관", "Leonardo AI"]
sources:
  - https://app.notion.com/p/3d7fd99f0e5f810a8da4e33e3c12e3cd?pvs=39
  - https://exultant-principle-9c5.notion.site/Higgsfield-Genjutsu-5-3d691cb23c4d81febdb6dccd1f17813f?pvs=149
---

# 영상 인물 통째로 바꾸기 (합병됨)

## 이게 뭔가요?

**Higgsfield Genjutsu**는 영상 속 인물을 다른 인물로 통째로 바꿔치기하는 AI 영상 편집 도구입니다. 안에 두 개의 탭이 있는데, 사람 전체를 교체하는 **Motion Transfer**와 물건 하나만 바꾸는 **Objects swap**으로 나뉩니다. 이번 스킬은 그중 Motion Transfer를 다룹니다.

핵심 아이디어는 이렇습니다. 원본 영상이 카메라 움직임·안무·타이밍·인원수·동선을 전부 결정하고, 참조 이미지가 새로 들어갈 인물의 얼굴·의상·배경을 결정하며, 프롬프트는 이 둘을 "누가 누구로 바뀌는지" 짝지어주는 역할만 합니다. 그래서 원본에 등장한 사람 수만큼 캐릭터가 복제돼도 각자 원래 자리와 동선은 그대로 지켜집니다. 기존에 AI로 영상을 새로 생성하면 원하는 동작·카메라 앵글을 정교하게 통제하기 어려운데, 이 방법은 이미 마음에 드는 움직임(원본 영상)을 기준으로 삼고 그 위에 인물·의상·배경 이미지를 레이어처럼 덧씌우는 구조라서 결과물의 동작 품질이 안정적입니다.

참조 이미지 구성 방식은 두 가지가 확인됩니다.
- **2장 캐릭터시트 방식**: 한 인물당 시트 1장에 정면·측면·후면·얼굴 클로즈업 4방향을 모두 담아 얼굴+의상을 한 번에 지정
- **3장 역할분담 방식**: 얼굴(Image1)·장면/의상+배경 색감(Image2)·의상 전신(Image3)으로 역할을 쪼개 각각 한 장씩 준비

어느 쪽이든 원리는 같습니다. 예시로 든 원본은 GENER8ION 'STORM' 뮤직비디오의 교복 군무 장면(30초, 3840×2160)이며, 가운데 흰 셔츠를 입은 리드 한 명은 여성 캐릭터로, 검은 재킷을 입은 나머지 전원은 밀짚모자를 쓴 남성 캐릭터로 교체됐습니다.

**한눈에 보기**

| 항목 | 내용 |
|---|---|
| 쓰는 기능 | Higgsfield Genjutsu 안의 Motion Transfer 탭 |
| 넣는 것 | 원본 영상 1개 + 참조 이미지(캐릭터 시트 2장 또는 얼굴/장면/의상 3장) + 프롬프트 1개 |
| 원본 영상 길이 제한 | 4초 ~ 30초 (넘으면 업로드 자체가 안 됨) |
| 레퍼런스 이미지 | 최대 30장 |
| 출력 해상도 | 1080p까지 |
| 비용 (15초 기준) | 480p 40크레딧 · 720p 104크레딧 · 1080p 144크레딧 |

💰 유료 필요: Higgsfield Genjutsu 구독 및 크레딧 (해상도별 크레딧 차이가 3배 이상)
✅ 무료 대안: 현재 두근 환경(Gemini, ChatGPT, CapCut, Canva 등) 도구 중 동일한 모션 트랜스퍼 기능을 대체할 무료 서비스는 확인되지 않음. 다만 캐릭터 시트를 준비해 인물을 지목하는 프롬프트 구조 자체는 다른 영상 생성 도구에도 참고 가능하며, 참조 이미지(얼굴·장면·의상) 준비는 Bing Image Creator·Leonardo AI 등 무료 이미지 생성 도구로 대체 가능

## 따라하기

1. **원본 영상과 참조 이미지를 준비한다.** 움직임의 기준이 될 원본 영상(4~30초 구간)을 하나 정합니다. 2장 방식이면 각 인물의 4방향(정면·측면·후면·클로즈업) 캐릭터 시트를, 3장 방식이면 역할별 이미지를 준비합니다.
   - `Video1 — 움직임`: 참고할 원본 영상. 카메라 워크·안무·타이밍·길이를 전부 결정
   - `Image1 — 얼굴`: 주인공의 얼굴·헤어가 잘 보이는 사진
   - `Image2 — 장면`: 주인공의 의상·주변 인물·배경·색감을 한눈에 볼 수 있는 사진
   - `Image3 — 의상`: 의상만 전신으로 보이는 사진 (원치 않는 액세서리는 미리 제외)

   이미지마다 역할(얼굴/장면/의상)을 명확히 나누는 것이 핵심입니다. 복면처럼 원치 않는 요소가 남아있는 예전 AI 생성 영상을 움직임 기준으로 재사용하지 않도록 주의합니다.

2. **Genjutsu를 열고 Motion Transfer 탭을 고른다.** Higgsfield Genjutsu 접속 → `Generate now` 클릭 → `Motion Transfer` 선택. 사람을 통째로 갈아끼우는 건 Motion Transfer, 물건 하나만 바꾸는 건 Objects swap이므로 반드시 Motion Transfer를 선택합니다.

3. **원본 영상 1개를 업로드한다.** 이 영상이 카메라 움직임·춤·타이밍·길이를 전부 결정하며, 결과물 길이도 여기서 정해집니다. 프롬프트로 영상 길이를 늘리거나 줄일 수 없습니다.

4. **참조 이미지를 순서대로 붙이고 슬롯 번호를 프롬프트와 일치시킨다.** 화면에 표시되는 이미지 슬롯 번호(1, 2, 3...)와 프롬프트에 적을 이미지 번호를 반드시 일치시킵니다. 어긋나면 얼굴·의상·색감이 엉뚱하게 섞여 나옵니다.
   - 2장 방식: 첫 번째 슬롯 = 가운데에서 리드할 인물(4방향 시트), 두 번째 슬롯 = 무리 전원이 될 인물(4방향 시트)
   - 3장 방식: `Image1(얼굴) → Image2(장면) → Image3(의상)` 순으로 첨부

5. **프롬프트 입력 토글을 켜고 전문을 붙여넣는다.** 기본 프리셋만으로는 "누구를 누구로 바꿀지"를 지정할 수 없습니다. 영상(`@Video1`)은 동작·카메라·타이밍의 기준, 이미지(`@Image1~3`)는 얼굴·의상·색감의 기준이라는 역할 구분을 지키고, 주변 인물은 화면에서 가려졌다가 다시 등장해도 같은 모습을 유지하도록 지시하는 문장을 반드시 포함합니다. 아래는 2장 캐릭터시트 방식으로 실제 사용한 프롬프트 전문입니다.

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

6. **해상도를 고르고 생성한다.** 먼저 480p로 돌려서 인물이 제대로 갈렸는지 확인한 뒤, 맞으면 1080p로 다시 뽑는 순서를 권장합니다. 480p와 1080p는 크레딧 차이가 3배가 넘습니다. 3장 역할분담 방식의 출력 옵션 예시는 720p·30초·1개 생성입니다.

### 내 소재에 맞게 바꿔야 할 지점

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

요약하면 "원본에서 누구를 지목하는가"와 "내 참조 이미지가 어떻게 생겼는가", 이 두 가지만 정확히 갈아끼우면 나머지는 거의 그대로 재사용됩니다. 3장 역할분담 방식으로 다른 콘셉트에 응용할 때도 마찬가지로 이미지별 인물·의상·배경 설명과 영상 길이 값만 바꾸면 됩니다.

## 활용 예시

- **뮤직비디오 군무 재캐스팅**: 상업 뮤직비디오 대신 직접 촬영한 군무 영상 30초를 올리고, 리드 1명 + 나머지 전원용 캐릭터 시트 2장만 준비하면 → 동일한 안무·동선을 유지한 채 오리지널 캐릭터가 주인공인 영상으로 재탄생
- **브랜드 광고 리스킨**: 광고 모델이 나온 짧은 영상을 원본으로 쓰고, 브랜드 마스코트 캐릭터 시트를 준비해 프롬프트의 옷 지목 문구만 마스코트 특징으로 바꾸면 → 동일한 카메라 워크와 타이밍을 유지한 채 마스코트가 등장하는 광고 컷 제작
- **코스프레/버추얼 캐릭터 댄스 영상**: 안무 챌린지 영상 하나를 원본으로 두고, 버추얼 캐릭터 시트(정면·측면·후면·클로즈업 4방향)를 만들어 넣으면 → 실제 촬영 없이 버추얼 캐릭터가 같은 안무를 추는 영상 완성
- **세계관/컨셉 변경 영상**: 동일한 원본 영상에 의상 이미지(Image3)만 바꿔 넣으면 → 수녀 컨셉 대신 SF·판타지 등 다른 컨셉의 영상을 같은 동작으로 재생성
- **배경 인물 일괄 교체**: 프롬프트에 "주변 인물은 전부 다른 얼굴의 ○○으로 바꾸고 재등장 시에도 동일 인물 유지" 문장을 넣으면 → 엑스트라까지 일관된 새 캐릭터로 채워진 장면을 얻을 수 있음

## 주의사항

- **원본 영상 길이는 4초~30초로 고정**. 30초를 넘으면 업로드 자체가 안 되므로 긴 영상은 먼저 30초 안으로 잘라야 한다.
- **저작권 문제**: 상업 뮤직비디오를 예시로 쓸 경우 연습용으로 돌려보는 건 괜찮지만, 결과물을 그대로 공개 배포하면 음원·영상 저작권 문제가 생길 수 있다. 공개용으로 만들 때는 직접 촬영한 영상이나 이용 허락을 받은 영상으로 바꿔야 한다.
- **시트/이미지 순서 실수**: 참조 이미지를 붙이는 순서가 프롬프트의 `@[Image 1]`, `@[Image 2]`(또는 `@Image1~3`) 지목 순서를 그대로 결정한다. 순서를 바꿔 붙이거나 슬롯 번호와 프롬프트 번호가 어긋나면 얼굴·의상·색감이 엉뚱하게 섞이거나 지목한 인물이 통째로 뒤바뀐다.
- **참조 이미지 속 원치 않는 요소**: 펜던트·십자가 등 원치 않는 액세서리가 참조 이미지에 남아 있으면 결과물에도 그대로 반영된다. 의상 참고 이미지는 원치 않는 요소를 미리 제외하고 촬영/선별해야 한다. 복면 등 가려진 부분이 있는 예전 AI 생성 영상을 움직임 기준 영상으로 재사용하면 원치 않는 요소가 새 영상에도 섞여 들어갈 수 있다.
- **원본 영상 구간(초 단위)**을 정확히 맞추지 않으면 의도한 길이의 결과물이 나오지 않는다.
- 자주 막히는 문제 3가지
  - 엉뚱한 사람이 바뀐다 → 옷 지목 문장이 다른 사람과 겹치는 특징을 쓰고 있을 가능성이 높다
  - 시트에 있던 모자나 신발이 영상에서 사라진다 → 프롬프트에 해당 소품을 명시적으로 적지 않았을 가능성이 높다
  - 뒤에 가려졌다 나온 사람이 다른 얼굴로 나온다 → occlusion(가림) 관련 문장이 빠졌거나 약하게 적혀 있을 가능성이 높다
- 480p로 먼저 테스트하고 맞으면 1080p로 재생성하는 순서를 권장한다. 해상도별 크레딧 차이가 3배 이상이라 1080p로 바로 돌리면 실패 시 크레딧 낭비가 크다.

## 출처

- [https://app.notion.com/p/3d7fd99f0e5f810a8da4e33e3c12e3cd?pvs=39](https://app.notion.com/p/3d7fd99f0e5f810a8da4e33e3c12e3cd?pvs=39)
- [https://exultant-principle-9c5.notion.site/Higgsfield-Genjutsu-5-3d691cb23c4d81febdb6dccd1f17813f?pvs=149](https://exultant-principle-9c5.notion.site/Higgsfield-Genjutsu-5-3d691cb23c4d81febdb6dccd1f17813f?pvs=149)
