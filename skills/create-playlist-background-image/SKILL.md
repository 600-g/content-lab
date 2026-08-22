---
name: create-playlist-background-image
description: AI 이미지 생성 도구를 활용하여 **자신의 사진**을 스포티파이·애플뮤직 스타일의 **투명한 음악 플레이어 카드**가 떠다니는 배경화면으로 만드는 스킬입니다.
origin: content-lab
grade: A
difficulty: 초급
category: 디자인
ai_tools: ["Claude", "GPT"]
sources:
  - https://fieldby.notion.site/3b8d730b3953812c868aca0d22bb954b?pvs=149
---

# 사진으로 플레이리스트 배경화면 만들기

💡 AI 이미지 생성 도구를 활용하여 **자신의 사진**을 스포티파이·애플뮤직 스타일의 **투명한 음악 플레이어 카드**가 떠다니는 배경화면으로 만드는 스킬입니다.

## 이게 뭔가요?

이 스킬은 개인 사진 한 장을 스포티파이, 애플뮤직과 같은 음악 스트리밍 서비스의 플레이리스트 배경화면처럼 바꿔주는 이미지 생성 AI 프롬프트 가이드입니다. 마치 투명한 음악 플레이어 카드가 유리처럼 떠다니는 듯한 효과를 연출할 수 있습니다.

사진 편집 및 생성이 가능한 AI 도구(예: ChatGPT, Claude 등)에 제공된 프롬프트를 붙여넣고, 원하는 사진과 곡 정보만 수정하면 됩니다. 복잡한 디자인 툴을 사용하지 않고도 개성 있는 배경화면을 만들 수 있다는 장점이 있습니다.

💰 **유료 필요**: 고품질의 이미지 생성을 위해서는 유료 AI 모델(예: Claude Max, GPT-4) 사용이 권장됩니다. ✅ **무료 대안**: Gemini, Bing Image Creator, Leonardo AI 등 무료 또는 부분 유료 서비스로도 유사한 결과물 생성이 가능합니다.

## 따라하기

1.  **이미지 생성 AI 도구 준비**: 인물 사진 편집 및 생성이 가능한 AI 도구에 접속합니다.
2.  **사진 업로드**: 생성할 배경화면의 기반이 될 개인 사진을 AI 도구에 업로드합니다.
3.  **프롬프트 선택 및 붙여넣기**: 사진의 구도에 맞는 아래 프롬프트 버전 중 하나를 선택하여 복사한 후, AI 도구의 프롬프트 입력란에 붙여넣습니다.
    *   **밝은 버전 프롬프트**: 인물과 배경을 그대로 유지하면서 4개의 투명한 카드 배치
    *   **어두운톤 버전 프롬프트**: 시네마틱 연출, 카드가 인물 앞뒤로 겹치는 깊이감 있는 디자인
4.  **곡 정보 수정**: 프롬프트 내 `[your songs]` 또는 각 카드에 지정된 곡 제목과 아티스트를 원하는 곡으로 변경합니다. '제목 — 아티스트' 형식은 반드시 유지해야 합니다. 앨범 커버 이미지까지 정확하게 반영하고 싶다면, 해당 앨범 커버 이미지를 AI 도구에 함께 첨부하여 요청할 수 있습니다.
5.  **생성**: AI 도구의 생성 기능을 실행하여 결과물을 확인합니다.
6.  **결과물 확인 및 재수정**: 생성된 이미지를 확인하고, 만족스럽지 않다면 곡 정보, 카드 개수, 배경 유지 여부 등 프롬프트의 해당 부분을 수정하여 다시 생성합니다.

### 밝은 버전 프롬프트

```markdown
[EDIT INSTRUCTION] Edit the original image in a vertical 9:16 format. Preserve the original person, face, hairstyle, expression, pose, body proportions, outfit, camera angle, framing, lighting, and color exactly as-is. Preserve the entire original background exactly as-is, including its location, architecture, walls, floor, objects, colors, textures, perspective, shadows, and depth. Do not replace, redesign, extend, blur, remove, or reinterpret the background. Add exactly four floating AR music-player cards: * One oversized card in the lower-right foreground, partially cropped by the frame * One medium card on the left side of the subject * One medium card on the right side of the subject * One smaller card behind the subject in the upper background Keep the subject's face and hands unobstructed. The cards are translucent pale-blue frosted glass with rounded corners, subtle reflections, softly illuminated edges, and consistent music-player UI design. Display exactly one track on each card: "Espresso" — Sabrina Carpenter "BIRDS OF A FEATHER" — Billie Eilish "Love Me Not" — Ravyn Lenae "Daisies" — Justin Bieber Each card includes one square album cover, song title, artist name, progress bar, pause button, previous and next buttons, timestamp, and heart icon. Keep all titles and artist names correctly spelled and clearly legible. Use the supplied album-cover references exactly as provided. Do not redesign, replace, duplicate, recolor, crop incorrectly, or invent album artwork. Add only subtle pale-blue reflections from the cards onto nearby surfaces. Do not change the original environmental lighting. Do not add extra cards, extra people, new background objects, logos, random text, motion blur, or additional visual effects.
```

### 어두운톤 버전 프롬프트

```markdown
A cinematic, dreamlike AR visual featuring a central photorealistic person surrounded by floating 3D Spotify/Apple Music interface cards. The cards orbit the subject at varying depths — some in the foreground obscuring the figure, others drifting behind. Style: Translucent frosted glass with glowing borders and rounded edges. Lighting: natural tones. Enhance the photo quality. Includes depth of field (blurred background cards) and motion accents, highlighting [your songs] player interfaces: century, rottweiler, 4 raws, phantom, mist, cali man, LV sandals.
```

## 활용 예시

1.  **개인 프로필 배경화면**: 자신의 셀카 사진을 이용하여, 좋아하는 곡들과 함께 개인 SNS 프로필에 사용할 독특한 배경화면을 제작합니다. (예: 밝은 버전 프롬프트 사용, 곡은 'Dynamite — BTS', 'Levitating — Dua Lipa' 등으로 변경)
2.  **음악 추천 카드**: 친구에게 음악을 추천해 줄 때, 추천하는 곡의 플레이리스트 카드와 함께 자신의 사진을 배경으로 삽입하여 시각적인 재미를 더합니다. (예: 어두운톤 버전 프롬프트 사용, 곡은 'Blinding Lights — The Weeknd', 'Save Your Tears — The Weeknd' 등으로 변경)
3.  **프로젝트 홍보 이미지**: 자신의 사진이 포함된 프로젝트나 이벤트 홍보 시, 이벤트 테마에 맞는 곡들을 플레이리스트 카드로 넣어 시선을 끄는 홍보 이미지를 만듭니다.

## 💡 아이디어

*   **맞춤형 굿즈 제작**: 제작된 플레이리스트 배경화면 이미지를 활용하여 폰 케이스, 머그컵 등 개인 맞춤 굿즈 제작에 활용할 수 있습니다.
*   **챌린지 이벤트**: 특정 곡이나 아티스트를 주제로 사용자들이 자신만의 플레이리스트 배경화면을 만들어 공유하는 SNS 챌린지 이벤트를 기획할 수 있습니다.

## 주의사항

*   **배경 보존**: 밝은 버전 프롬프트 사용 시, 원본 배경을 유지하려면 프롬프트에 `Preserve the entire original background exactly as-is` 문구가 포함되어 있는지 반드시 확인해야 합니다. 이 문구가 누락되면 AI가 임의로 배경을 수정하거나 제거할 수 있습니다.
*   **카드 개수**: 밝은 버전 프롬프트는 4개의 카드가 안정적인 구도를 제공합니다. 카드 개수를 임의로 늘릴 경우 인물의 얼굴이나 손이 가려질 수 있으니 주의해야 합니다.
*   **곡 형식**: 곡 제목과 아티스트는 반드시 '제목 — 아티스트' 형식을 유지해야 AI가 정확하게 인식합니다.

## 출처

[내 사진을 플레이리스트 배경화면으로 만드는 프롬프트 가이드](https://fieldby.notion.site/3b8d730b3953812c868aca0d22bb954b?pvs=149)

## 출처

- [https://fieldby.notion.site/3b8d730b3953812c868aca0d22bb954b?pvs=149](https://fieldby.notion.site/3b8d730b3953812c868aca0d22bb954b?pvs=149)
