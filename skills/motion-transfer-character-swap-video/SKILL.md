---
name: motion-transfer-character-swap-video
description: 원본 영상의 **동선, 카메라 움직임, 타이밍**을 유지하면서, 등장인물만 원하는 **캐릭터 시트**로 교체하는 **모션 트랜스퍼** 스킬입니다.
origin: content-lab
grade: A
difficulty: 고급
category: 콘텐츠
ai_tools: ["ComfyUI", "Stable Diffusion"]
sources:
  - https://app.notion.com/p/3d7fd99f0e5f810a8da4e33e3c12e3cd?pvs=39
---

# AI로 영상 속 인물 교체하기

💡 원본 영상의 **동선, 카메라 움직임, 타이밍**을 유지하면서, 등장인물만 원하는 **캐릭터 시트**로 교체하는 **모션 트랜스퍼** 스킬입니다.

## 이게 뭔가요?
이 스킬은 **Higgsfield Genjutsu**의 **Motion transfer** 기능을 활용하여, 기존 영상의 모든 움직임과 구도를 그대로 유지한 채 등장인물만 원하는 캐릭터로 교체하는 기술입니다. 원본 영상의 군무 장면을 예시로, 춤추는 사람들의 동선과 카메라 워크는 그대로 두고, 사람만 다른 캐릭터로 갈아 끼우는 것이 핵심입니다.

이 기능을 사용하기 위해서는 **원본 영상**, **캐릭터 시트(여러 각도)**, 그리고 **매우 상세한 프롬프트**가 필요합니다. 이 과정은 단순한 이미지 생성이나 영상 편집을 넘어, 영상의 시간적 흐름과 동작의 연속성을 이해하고 제어하는 고난도 작업입니다. 💰 이 기능은 특정 AI 플랫폼의 유료 기능을 사용해야 하므로 유료가 필요할 가능성이 높습니다. ✅ 무료 대안으로는 유사한 기능을 가진 **Stable Diffusion** 기반의 **ControlNet**이나 **IP-Adapter**를 조합하여 시도해볼 수 있으나, 원본의 복잡한 동선과 타이밍을 완벽히 재현하기는 어렵습니다.

## 따라하기

이 과정은 여러 단계를 거치며, 각 단계의 순서와 내용이 매우 중요합니다. 

**준비물:**
*   **원본 영상:** 움직임, 구도, 타이밍의 기준이 되는 영상 (예: 30초 분량의 4K 뮤직비디오).
*   **캐릭터 시트 2장:** 교체할 캐릭터들의 정면, 측면, 후면, 클로즈업 등 여러 각도를 담은 시트.
*   **프롬프트:** 모든 요소를 연결하고 제어하는 상세한 텍스트 프롬프트.

**단계별 가이드:**

1.  **젠주츠 열기 및 기능 선택:** **Higgsfield Genjutsu**에 접속하여 **Motion transfer** 탭을 선택합니다. (Objects swap은 물건 교체에 사용합니다.)
2.  **원본 영상 업로드:** **원본 영상 1개**를 지정된 슬롯에 업로드합니다. 이 영상이 결과물의 길이, 카메라 움직임, 춤의 타이밍을 결정합니다. (영상 길이는 4초에서 30초 사이로 제한될 수 있습니다.)
3.  **캐릭터 시트 순서대로 붙이기:** **캐릭터 시트 2장**을 순서대로 업로드합니다. 이 순서가 프롬프트 내에서 각 캐릭터의 역할을 정의하는 기준이 됩니다. (예: 첫 번째 슬롯 = 리드 캐릭터 시트, 두 번째 슬롯 = 무리 캐릭터 시트).
4.  **프롬프트 입력:** **프롬프트 입력 토글**을 켜고, 아래의 **전문 프롬프트**를 통째로 붙여넣습니다. 이 프롬프트는 원본의 모든 요소를 유지하면서 캐릭터만 교체하도록 지시합니다.

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
Express this through a steady, assessing gaze, composed brows, a relaxed jaw, and a controlled neutral mouth.
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

### 🔧 바꿔야 할 지점

프롬프트는 매우 길기 때문에, 사용자가 자신의 소재에 맞게 수정해야 할 핵심 지점들이 있습니다. 아래 표를 참고하여 수정하는 것이 안전합니다.

| 프롬프트 속 문구 | 지금 뜻 | 내 것으로 바꿀 때 | 
| :--- | :--- | :--- | 
| ★ wearing a white long-sleeve school shirt and striped tie WITHOUT a dark blazer | 원본에서 바꿀 주인공을 옷으로 지목한 문장 | 가장 중요한 한 줄. 내 원본에서 그 사람만 가진 옷 특징으로 다시 씁니다. 다른 사람과 겹치는 특징을 쓰면 엉뚱한 사람이 바뀝니다 | 
| ★ EVERY original dark-blazer performer | 원본에서 나머지 무리를 옷으로 지목한 문장 | 내 원본에서 나머지 사람들이 공통으로 걸친 옷 특징으로 | 
| ★ long copper-brown hair, teal halter top, denim shorts, brown belt, necklace, bracelets, and brown ankle boots | 시트 1 인물의 머리와 의상 전체 | 내 시트를 보고 머리색, 상의, 하의, 벨트, 액세서리, 신발까지 빠짐없이 다시 씁니다. 안 적은 것은 영상에서 사라집니다 | 
| ★ straw hat with a red band, weathered red sleeveless vest, blue cropped trousers, mustard waist sash, and brown sandals | 시트 2 인물의 의상 전체 | 위와 같은 요령으로 시트 2를 보고 다시 씁니다 | 
| ★ @[Image 1] shows multiple views of ONE adult woman / ONE adult man | 시트마다 몇 명이 들었고 성별이 무엇인지 | 내 시트의 성별과 나이대로. ONE 은 그대로 두세요. 한 장에 두 사람이 들어 있으면 얼굴이 섞입니다 | 
| school setting / Keep the original school architecture | 원본이 학교라서 학교로 적은 배경 | 원본 장소로. 무대면 stage, 거리면 street, 체육관이면 gymnasium | 
| At the beginning, this source performer is close to the camera with his back facing the camera | 주인공이 첫 프레임에 어디 있는지 | 내 원본의 첫 등장 위치와 방향을 그대로 묘사합니다. 이 문장이 추적의 출발점이에요 | 
| LEAD WOMAN / her / she / feminine appearance | 주인공이 여성이라 붙은 표현들 | 주인공이 남성이면 문단 제목과 대명사를 전부 남성형으로 바꿉니다. 한 군데라도 남으면 얼굴이 흔들립니다 | 
| cool, self-assured, and quietly intimidating | 주인공에게 입힌 표정과 태도 | 원하는 분위기로. 밝게 가려면 warm, open, easily smiling 식으로 | 
| Do not add a constant smile, a cute expression, flirtatious eye contact | 원치 않는 표정을 미리 막는 문장 | 위에서 정한 분위기의 반대말로 다시 씁니다 | 
| Do not imitate the source lead's scowling, forceful jaw tension, exaggerated grimaces | 원본 배우의 표정 버릇을 안 옮기게 막는 문장 | 내 원본 배우의 얼굴 버릇 중 안 가져오고 싶은 것으로 | 
| cigarette / smoking gesture / Do not add cigarettes or replace them with toothpicks | 원본에 담배가 나와서 넣은 문단 | 원본에 담배가 없으면 관련 문장을 통째로 지웁니다. 다른 소품이면 그 소품 이름으로 | 
| Every crowd performer wears the reference straw hat | 무리 전원이 쓴 소품 이름 | 시트 2에 모자가 없으면 그 자리를 다른 소품 이름으로 바꾸거나 문장을 지웁니다 | 
| Preserve the original audio | 원본 소리를 그대로 둠 | 그대로 둡니다. 소리를 새로 넣으면 입 모양이 흔들립니다 | 
| photoreal live-action appearance | 실사 톤으로 고정 | 애니메이션 톤이 필요하면 이 자리에서 화풍을 지정합니다 | 

**핵심 요약:** 원본에서 **누구를 지목하는지**, **내 시트가 어떻게 생겼는지**, 이 두 가지만 정확히 갈아끼우면 나머지는 거의 그대로 재사용됩니다.

## 활용 예시

**시나리오:** K-POP 아이돌 그룹의 뮤직비디오를 활용하여, 특정 멤버의 얼굴과 의상으로 교체하고 싶을 때.

**입력:**
1.  **원본 영상:** K-POP 뮤직비디오의 군무 장면 (동선, 구도 유지).
2.  **캐릭터 시트 1:** 교체할 멤버 A의 시트.
3.  **캐릭터 시트 2:** 교체할 멤버 B의 시트.
4.  **프롬프트:** 위에서 제시된 프롬프트의 **'CHARACTER ASSIGNMENT'**와 **'LEAD WOMAN'** 부분을 멤버 A와 B의 특징에 맞게 수정하고, **'school setting'** 부분을 **'stage setting'** 등으로 변경합니다.

**결과:**
원본 영상의 모든 군무와 카메라 움직임이 유지되면서, 모든 출연자가 멤버 A와 B의 외모와 의상으로 완벽하게 교체된 고품질의 영상이 생성됩니다.

## 💡 아이디어

*   **패션 화보 영상 제작:** 특정 브랜드의 의상을 입은 모델들의 움직임을 원본 영상에 합성하여, 가상의 화보 영상을 만들 수 있습니다. (예: 특정 브랜드의 의상을 입은 가상 인물들이 걷는 장면).
*   **게임 캐릭터 애니메이션:** 게임 속 캐릭터의 움직임을 실제 배우의 동작에 합성하여, 홍보 영상이나 티저 영상을 제작할 수 있습니다.

## 주의사항

*   **프롬프트의 중요성:** 프롬프트의 수정이 가장 중요하며, 원본의 지시사항(예: 'Do not add a constant smile')을 빠뜨리면 의도치 않은 결과가 나올 수 있습니다.
*   **저작권 문제:** 원본 영상이 상업 저작물인 경우, 결과물을 공개적으로 사용하기 전에 반드시 저작권 문제를 확인해야 합니다.
*   **영상 길이 제한:** 원본 영상이 30초를 넘으면 처리가 안 될 수 있으니, 긴 영상은 미리 30초 이내로 잘라야 합니다.

## 출처
[Notion | Where teams and agents work together](https://app.notion.com/p/3d7fd99f0e5f810a8da4e33e3c12e3cd?pvs=39)

## 출처

- [https://app.notion.com/p/3d7fd99f0e5f810a8da4e33e3c12e3cd?pvs=39](https://app.notion.com/p/3d7fd99f0e5f810a8da4e33e3c12e3cd?pvs=39)
