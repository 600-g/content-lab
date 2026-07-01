---
name: maplestory-character-prompt
description: 업로드된 사진을 바탕으로 **메이플스토리** 공식 캐릭터 스타일의 아바타를 생성하는 프롬프트입니다.
origin: content-lab
grade: S
difficulty: 초급
category: 프롬프트
ai_tools: ["GPT"]
sources:
  - https://rural-slash-4e3.notion.site/st-solrr-aa-381c2a2c7a0a80d2be19e5cc6ea02fff?pvs=149
---

# 사진으로 메이플스토리 캐릭터 생성

💡 업로드된 사진을 바탕으로 **메이플스토리** 공식 캐릭터 스타일의 아바타를 생성하는 프롬프트입니다.

## 이게 뭔가요?

이 스킬은 업로드된 사진 속 인물을 **메이플스토리(MapleStory)** 게임의 공식 캐릭터처럼 보이도록 AI 이미지 생성 도구를 활용하는 방법입니다. 영상 크리에이터 솔랄라(@solrr.aa)님이 **챗GPT**를 사용하여 직접 검증하고 공유한 프롬프트로, 사진 한 장만 있으면 전신샷을 기반으로 메이플스토리 스타일의 캐릭터 아바타를 손쉽게 만들 수 있습니다.

이 프롬프트는 매우 상세하게 작성되어 있어, 단순히 그림체를 흉내 내는 것을 넘어 메이플스토리 특유의 큰 머리와 작은 몸 비율, 표정, 의상 번역, 픽셀 아트 렌더링 방식까지 정확히 재현하도록 AI에 지시합니다. 팬아트나 일반적인 픽셀 일러스트가 아닌, 실제 게임 내 커스터마이징 화면에서 만든 듯한 결과물을 얻을 수 있도록 고안되었습니다. 한 번에 총 5가지 느낌의 캐릭터 이미지를 생성할 수 있습니다.

💰 유료 필요: **GPT-4V (ChatGPT Plus)** 또는 **Claude 3 Opus/Sonnet**과 같이 이미지 입력을 지원하는 유료 AI 모델이 필요합니다.
✅ 무료 대안: **Bing Image Creator** 등에서도 유사 시도를 해볼 수 있으나, 본 프롬프트의 디테일한 요구사항을 완벽히 구현하여 메이플스토리 특유의 느낌을 살리기는 어려울 수 있습니다.

## 따라하기

1.  변환하고 싶은 인물 사진(가급적 전신샷 추천)을 준비합니다.
2.  **ChatGPT** 등 이미지 업로드를 지원하는 AI 챗봇에 접속합니다. (예: **GPT-4V** 모델 선택)
3.  준비한 사진을 AI 챗봇에 업로드합니다.
4.  아래 프롬프트를 복사하여 붙여넣고 이미지를 생성합니다.

```
Create an avatar version of the uploaded subject in the style of an official Nexon MapleStory playable character.
The image should look as if the subject has been customized inside the real MapleStory game client. It should not look like a fan-made drawing, a generic pixel illustration, anime art, or a 3D render.
Use the uploaded photo only to understand the subject’s appearance and identity. Keep the recognizable features such as hairstyle, hair color, eye shape, facial mood, expression, main outfit colors, and one or two memorable accessories. Do not follow the original photo’s pose, body shape, height, proportions, background, camera angle, or composition.
The character must use modern official MapleStory avatar proportions: a very large head, small compact body, tiny torso, extremely short legs, small hands and feet, and a soft rounded silhouette. Do not lengthen the legs or adjust the body based on the person’s real proportions.
Place the avatar in a simple MapleStory idle standing pose, with the arms relaxed down and the hands beside the body. Use a slight front-facing quarter view, around 35–40 degrees, with both eyes visible. Avoid action poses, gestures, dramatic movement, or interaction poses.
Translate the real outfit into MapleStory-style equipment instead of copying the clothing literally. Keep the overall fashion concept, representative colors, and key accessories, but remove realistic fabric texture, folds, seams, tailoring, and tiny details.
The face should resemble an official MapleStory face preset: large rounded eyes, tiny nose, tiny mouth, and a soft cute expression. Avoid realistic facial detail, heavy anime eyelashes, or semi-realistic rendering.
The hair should feel like an official MapleStory hair item, with a large rounded silhouette, simplified volume, and no realistic individual strands.
If one human is visible, create one MapleStory character. If two humans are visible, create two separate MapleStory characters using the same base proportions. Do not merge people or add extra characters.
Only create a MapleStory-style companion pet if a real dog or cat is clearly visible in the uploaded image. Do not add pets, mascots, plush toys, creatures, or extra animals otherwise.
Render the result as an enlarged official MapleStory sprite with crisp square pixels, simple shading, limited colors, sharp pixel edges, and a nearest-neighbor scaled look. Avoid anti-aliasing, smooth gradients, painterly effects, HD pixel-art styling, or glossy illustration rendering.
Final output: 1000 x 1000, pure white background, centered composition, full body visible, balanced spacing, no floor, no shadow, no scenery, no UI, no logo, no watermark, no text, no name label, and no caption. The avatar should occupy about 72–75% of the canvas height.
The final image must look like a genuine official Nexon MapleStory playable character based on the uploaded subject. n=5
```

## 활용 예시

*   **친구의 사진으로 특별한 프로필 이미지 만들기:**
    *   **입력:** 친구의 개성이 담긴 전신 사진 한 장과 위 프롬프트
    *   **결과:** 친구의 특징을 살리면서 메이플스토리 특유의 아기자기한 매력이 더해진 캐릭터 이미지 5개 생성. 친구에게 특별한 선물이 될 수 있습니다.

*   **SNS 아바타로 활용:**
    *   **입력:** 본인의 개성 있는 사진과 위 프롬프트
    *   **결과:** 실제 메이플스토리 게임에 나올 법한 나만의 아바타 생성. 개인 브랜드나 SNS 프로필 사진으로 활용하여 독특한 개성을 표현할 수 있습니다.

*   **팀원들의 메이플스토리화:**
    *   **입력:** 팀원들 각자의 사진과 위 프롬프트
    *   **결과:** 팀원 모두를 메이플스토리 스타일 캐릭터로 변환하여, 재미있는 팀 로고나 이벤트 홍보를 위한 일러스트로 활용할 수 있습니다.

## 💡 아이디어

*   **커미션 서비스 운영:** 사용자 사진을 받아 메이플스토리 스타일 캐릭터를 만들어주는 커미션 서비스를 운영하여 수익을 창출할 수 있습니다.
*   **캐릭터 굿즈 제작:** 생성된 캐릭터 이미지를 활용하여 폰케이스, 스티커, 티셔츠 등 다양한 굿즈를 제작하고 판매하여 부가 수익을 얻을 수 있습니다.
*   **콘텐츠 마케팅:** 메이플스토리 팬덤을 타겟으로 하는 콘텐츠(예: '나만의 메이플스토리 캐릭터 만들기 챌린지')를 기획하여 바이럴 마케팅 효과를 창출하고 커뮤니티를 활성화할 수 있습니다.

## 주의사항

*   **저작권:** 생성된 이미지의 저작권 및 상업적 이용 가능 여부는 사용하는 AI 도구의 정책과 메이플스토리 IP 사용 가이드라인을 반드시 확인해야 합니다.
*   **사진 품질:** 원본 사진의 품질(특히 전신샷 여부, 인물 특징의 선명도)이 생성되는 캐릭터의 유사성과 완성도에 큰 영향을 미칩니다. 가급적 선명한 사진을 사용하세요.
*   **AI 도구의 해석:** 프롬프트가 매우 상세하지만, AI 도구마다 이미지 해석 방식에 차이가 있어 동일한 프롬프트라도 결과물의 퀄리티나 디테일이 다를 수 있습니다.

## 출처

[메이플st 캐릭터 프롬프트 @solrr.aa](https://rural-slash-4e3.notion.site/st-solrr-aa-381c2a2c7a0a80d2be19e5cc6ea02fff?pvs=149)

## 출처

- [https://rural-slash-4e3.notion.site/st-solrr-aa-381c2a2c7a0a80d2be19e5cc6ea02fff?pvs=149](https://rural-slash-4e3.notion.site/st-solrr-aa-381c2a2c7a0a80d2be19e5cc6ea02fff?pvs=149)
