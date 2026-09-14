---
name: motion-transfer-character-swap-video
description: 원본 영상의 카메라·안무·타이밍은 그대로 유지한 채 등장인물만 캐릭터 시트(2장) 또는 얼굴/장면/의상으로 역할을 나눈 이미지(3장)로 교체해 뮤직비디오·콘셉트 영상을 리메이크하는 방법. Higgsfield Genjutsu의 Motion Transfer 탭 하나로 완성된다.
origin: content-lab
grade: A
difficulty: 고급
category: 콘텐츠
ai_tools: ["도구무관"]
sources:
  - https://app.notion.com/p/3d7fd99f0e5f810a8da4e33e3c12e3cd?pvs=39
  - https://exultant-principle-9c5.notion.site/Higgsfield-Genjutsu-5-3d691cb23c4d81febdb6dccd1f17813f?pvs=149
---

# 댄스영상 캐릭터 통째로 교체하기 (합병됨)

## 이게 뭔가요?

**Higgsfield Genjutsu**는 영상 속 인물을 다른 캐릭터로 바꿔주는 AI 영상 편집 도구입니다. 안에는 두 개의 탭이 있는데, 물건 하나를 다른 물건으로 바꾸는 **Objects swap**과, 사람을 통째로 갈아끼우는 **Motion transfer**로 나뉩니다. 이 스킬이 쓰는 건 후자입니다.

원리는 단순합니다. 원본 영상이 카메라 움직임·춤 동선·타이밍·인원수·포메이션을 전부 결정하고, 참고 이미지들이 얼굴·의상·배경·색감을 결정합니다. 프롬프트는 "원본의 누구를 어떤 이미지 인물로 바꿔라"를 지정하는 역할만 합니다. 즉 동선은 그대로, 사람만 바뀌는 구조입니다.

레퍼런스를 준비하는 방식은 크게 두 가지입니다.

- **방법 A — 캐릭터 시트 2장**: 정면·측면·후면·클로즈업 4방향이 담긴 인물 이미지 2장을 쓰는 방식. 한 장에 리드 인물, 다른 한 장에 무리 전원이 될 인물을 담아 원본의 특정 의상 그룹을 통째로 그 인물로 치환한다. 캐릭터의 얼굴·체형을 정확하게 고정하고 싶을 때 유리하다.
- **방법 B — 역할 분리 이미지 3장**: 얼굴(주인공 얼굴·헤어 고정), 장면(전체 의상·주변 인물·배경·색감), 의상(치마·베일·신발 등 세부 의상)으로 이미지를 역할별로 나누는 방식. 인물뿐 아니라 배경·색감·세계관까지 통째로 바꾸고 싶을 때 유리하다.

원본으로 쓴 뮤직비디오는 상업 저작물이라 연습용으로 돌려보는 건 괜찮지만, 결과물을 그대로 공개하면 음원과 영상 저작권 문제가 생길 수 있습니다. 공개용으로 만들 때는 직접 촬영한 영상이나 이용 허락을 받은 영상으로 바꿔서 써야 합니다.

💰 유료 필요: Higgsfield Genjutsu 크레딧/구독 (15초 기준 480p 40크레딧 · 720p 104크레딧 · 1080p 144크레딧, Motion Transfer는 유료 기능)
✅ 무료 대안: 없음. 두근 무료 스택(Gemini, Leonardo AI 등)에는 동일한 모션 트랜스퍼 기능이 없다. 유사한 결과를 원한다면 ComfyUI에 AnimateDiff + ControlNet(OpenPose) 조합으로 동작을 유지한 채 인물을 리스타일링하는 파이프라인을 직접 구성해야 하지만, 난이도가 훨씬 높고 설정이 복잡하다.

### 📊 한눈에 보기

| 항목 | 내용 |
|---|---|
| 쓰는 기능 | Higgsfield Genjutsu 안의 Motion transfer 탭 |
| 넣는 것 (방법 A) | 원본 영상 1개 + 캐릭터 시트 2장 + 프롬프트 1개 |
| 넣는 것 (방법 B) | 원본 영상 1개 + 얼굴/장면/의상 이미지 3장 + 프롬프트 1개 |
| 원본 영상 길이 제한 | 4초에서 30초까지 (30초 초과 시 업로드 자체가 안 됨) |
| 레퍼런스 이미지 | 최대 30장 |
| 출력 해상도 | 1080p까지 |
| 비용 (15초 기준) | 480p 40크레딧 · 720p 104크레딧 · 1080p 144크레딧 |

## 따라하기

### 원본 영상 준비 (공통)

30초를 넘으면 업로드가 안 되므로 긴 영상은 먼저 30초 안으로 잘라둡니다. 이 영상이 카메라 움직임·춤·타이밍·길이를 전부 결정하며, 프롬프트로 늘리거나 줄일 수 없습니다. 참고용 원본 영상에 복면 등 원치 않는 요소가 있다면, 그 영상을 그대로 동작 기준으로 쓰지 말고 요소를 제거한 버전이나 다른 영상을 사용해야 합니다.

### 방법 A — 캐릭터 시트 2장으로 인물 치환

1. **캐릭터 시트 2장을 만듭니다.** 한 장에는 가운데에서 리드할 인물(정면·측면·후면·얼굴 클로즈업 4방향 구성, 반드시 ONE 인물만), 다른 한 장에는 무리 전원이 될 인물을 같은 4방향 구성으로 담습니다. 한 장에 두 사람이 들어가면 얼굴이 섞이므로 반드시 인물 1명씩 분리합니다.

2. **Genjutsu를 열고 Motion transfer 탭을 고릅니다.** 물건을 바꾸는 게 아니라 사람을 통째로 갈아끼우는 작업이므로 Objects swap이 아닌 Motion transfer를 선택해야 합니다.

3. **원본 영상 1개를 업로드 슬롯에 넣습니다.** 결과물의 길이·동선·카메라워크가 여기서 확정됩니다.

4. **캐릭터 시트 2장을 순서대로 붙입니다.** 먼저 붙인 시트가 프롬프트 안의 `@[Image 1]`, 그다음이 `@[Image 2]`가 됩니다. 첫 번째 슬롯 = 가운데에서 리드할 인물, 두 번째 슬롯 = 무리 전원이 될 인물. 순서를 바꿔 붙이면 프롬프트가 지목한 인물이 통째로 뒤바뀝니다.

5. **프롬프트 입력 토글을 켜고 아래 전문을 통째로 붙여넣습니다.** 기본 프리셋만으로는 "누구를 누구로 바꿔라"를 지정할 수 없기 때문에 반드시 이 토글을 켜야 합니다.

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
Each original dark-blazer performer becomes one separate instance of this same man. Every instance follows its own corresponding source performer's movement. Preserve the number of performers, their individual trajectories, spacing, row assignments, and front-to-back o
```
(원문 프롬프트가 이 지점에서 잘려 있습니다. 실제 작업 시 나머지 지시문 — 인원수·간격·앞뒤 배치 보존, 조명·색감 유지 등 — 을 이어서 추가하면 됩니다.)

### 방법 B — 얼굴/장면/의상 역할 분리 이미지 3장으로 인물·배경 통째 교체

1. **참고 이미지 3장을 역할별로 준비합니다.**
   - **Image1 (얼굴)**: 주인공의 얼굴·헤어를 고정하는 기준 이미지. 예: 검정 단발과 빨간 립스틱이 잘 보이는 사진
   - **Image2 (장면)**: 전체 의상·주변 인물·배경·색감을 잡는 기준 이미지. 예: 주인공의 빨간 의상, 주변 인물, 배경과 색감을 함께 볼 수 있는 사진
   - **Image3 (의상)**: 세부 의상을 지정하는 기준 이미지. 예: 긴 치마·베일·검정 신발이 보이는 수녀 전신 사진 (단, 펜던트·십자가·목걸이는 제외)

   이미지마다 역할을 명확히 나누는 것이 핵심입니다. 마음에 드는 장면이 있다면 선명한 정지 화면을 참고 이미지로 써도 됩니다.

2. **Genjutsu에서 Generate now → Motion Transfer로 진입합니다.**

3. **원본 영상 1개와 이미지 3장을 업로드하고 번호를 맞춥니다.** 화면에 표시되는 이미지 번호(Image1, Image2, Image3)와 프롬프트 안의 번호를 정확히 맞춰야 합니다. 어긋나면 엉뚱한 요소가 적용됩니다.

4. **프롬프트에서 영상은 동작·카메라·타이밍의 기준, 이미지는 얼굴·의상·색감의 기준으로 각각 지정합니다.** 주변 인물은 전부 얼굴이 다른 인물로 바꾸되, 화면에서 가려졌다가 다시 나타날 때도 같은 인물처럼 보이도록 일관성 유지 지시를 넣는 것이 포인트입니다. (원문에는 실제로 사용한 프롬프트 전문이 "펼쳐서 복사" 토글 안에 접혀 있어 텍스트 추출본에는 포함되어 있지 않습니다. 정확한 프롬프트 전문은 원본 노션 페이지에서 토글을 펼쳐 직접 확인해야 합니다.)

5. **원본 영상을 `@Video1`으로, 준비한 이미지 3장을 `@Image1 → @Image2 → @Image3` 순서로 함께 첨부해 생성합니다.** 예시는 원본 영상의 처음 0~30초 구간만 사용했고, 생성 설정은 720p · 30초 · 1개였습니다.

다른 콘셉트로 응용하려면 이미지별 인물·의상·배경 설명과 영상 길이 부분만 먼저 바꿔서 시작하면 됩니다.

## 활용 예시

- 뮤직비디오 군무 장면(예: GENER8ION 'STORM' 30초, 3840×2160)을 그대로 두고 춤추는 사람만 직접 만든 캐릭터로 바꿔 30초·1280×720 결과물 제작
- 기존에 촬영해둔 댄스/퍼포먼스 영상이 있는데, 등장인물의 스타일(헤어·의상·주변 인물)만 완전히 다른 콘셉트로 바꾸고 싶을 때
- 뮤직비디오 촬영 없이 기존 레퍼런스 영상의 카메라 워크만 빌려서 완전히 다른 세계관(예: 수녀 콘셉트, SF 콘셉트 등)의 뮤직비디오를 만들고 싶을 때
- 여러 명이 등장하는 장면에서 주변 인물들의 얼굴을 전부 바꿔치기하면서도 화면에서 사라졌다 다시 나오는 인물의 일관성을 유지하고 싶을 때

## 주의사항

- 원본 뮤직비디오는 상업 저작물이므로 연습용 외에 공개용 결과물을 만들 때는 직접 촬영했거나 이용 허락을 받은 영상으로 교체해야 합니다.
- 방법 A에서 캐릭터 시트에 두 사람이 함께 들어가면 얼굴이 섞이므로 반드시 인물 1명씩 분리한 시트를 만들어야 합니다.
- 방법 B에서 이미지 3장의 역할 구분(얼굴/장면/의상)이 흐트러지면 결과물의 일관성이 떨어지므로, 각 이미지가 어떤 정보를 담당하는지 명확히 하고 업로드해야 합니다.
- 두 방법 모두 화면에 표시되는 이미지 번호와 프롬프트 안의 이미지 번호(`@[Image 1]`, `@Image1` 등)가 어긋나면 엉뚱한 요소가 적용되니 순서를 반드시 일치시켜야 합니다.
- 참고용 원본 영상에 복면 등 원치 않는 요소가 있다면 그대로 동작 기준으로 쓰지 말고 요소를 제거하거나 다른 영상으로 교체해야 합니다.
- 원본 영상은 4초~30초 사이여야 하며, 프롬프트로 길이를 늘리거나 줄일 수 없습니다.

## 출처

- [https://app.notion.com/p/3d7fd99f0e5f810a8da4e33e3c12e3cd?pvs=39](https://app.notion.com/p/3d7fd99f0e5f810a8da4e33e3c12e3cd?pvs=39)
- [https://exultant-principle-9c5.notion.site/Higgsfield-Genjutsu-5-3d691cb23c4d81febdb6dccd1f17813f?pvs=149](https://exultant-principle-9c5.notion.site/Higgsfield-Genjutsu-5-3d691cb23c4d81febdb6dccd1f17813f?pvs=149)
