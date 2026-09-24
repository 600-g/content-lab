---
name: crayon-diary-poster-prompt
description: 사진 한 장을 업로드하면 원본 사진과 파스텔 크레용 손그림 일러스트를 한 화면에 합친 **에디토리얼 포스터**로 바꿔주는 **이미지 생성 프롬프트 팩**입니다. 사진 방향에 맞춰 고르는 4가지 레이아웃 버전이 통째로 들어 있습니다.
origin: content-lab
grade: S
difficulty: 초급
category: 프롬프트
ai_tools: ["GPT", "Gemini"]
sources:
  - https://fieldby.notion.site/3e3d730b39538163b41bcb0d72663ef1?pvs=149
---

# 사진을 크레용 포스터로 변환

💡 사진 한 장을 업로드하면 원본 사진과 파스텔 크레용 손그림 일러스트를 한 화면에 합친 **에디토리얼 포스터**로 바꿔주는 **이미지 생성 프롬프트 팩**입니다. 사진 방향에 맞춰 고르는 4가지 레이아웃 버전이 통째로 들어 있습니다.

## 이게 뭔가요?

업로드한 사진 1장을 그대로 두고, 반대쪽 크라프트지 위에 파스텔 크레용으로 그린 작은 손그림·마스킹테이프 조각·타자기 글씨 한 줄을 얹어 "그림일기 포스터" 한 장으로 완성해주는 프롬프트입니다. 원본 인물·풍경·반려동물의 형태는 그대로 보존하면서, 반대편에는 그 사진의 감정과 분위기만 추출한 미니멀한 손그림 삽화를 배치하는 방식입니다.

**ChatGPT**의 이미지 생성 기능에서 사용하도록 설계되었으며, 사진 방향(세로/가로)과 원하는 배치(사진 위/그림 위/좌우)에 따라 총 4가지 버전 중 하나를 골라 그대로 붙여넣으면 됩니다.

💰 유료 필요: ChatGPT Plus 이상이면 이미지 생성 한도가 넉넉함
✅ 무료 대안: ChatGPT 무료 버전도 이미지 생성 가능(횟수 제한), **Gemini**(나노바나나)에서도 실행은 되지만 그림이 우표처럼 작게 나오는 등 결과 톤이 달라진다. 이 가이드의 결과물 예시는 ChatGPT 기준.

## 따라하기

1. ChatGPT를 열고 바꾸고 싶은 사진을 1장만 업로드한다 (한 번에 한 장씩 처리)
2. 아래 4가지 버전 중 사진 방향과 원하는 배치에 맞는 프롬프트 전체를 복사해 붙여넣는다
3. 결과가 마음에 들 때까지 같은 프롬프트로 재생성한다

**버전 선택 기준**
- ① 세로형 3:4, 사진 위·그림 아래 — 기본형, 인스타 피드용
- ② 세로형 3:4, 그림 위·사진 아래 — 인물 사진에 부담 없는 구도
- ③ 세로형 3:4, 사진 왼쪽·그림 오른쪽 — 세로로 찍은 사진, 오른쪽에 문구 얹을 때
- ④ 가로형 4:3, 사진 왼쪽·그림 오른쪽 — 가로 포스터, 인쇄용

### 프롬프트 ① — 세로형 3:4 (사진 위 · 그림 아래)

```
Create one independent premium editorial poster for each uploaded photo. Never combine photos into a collage, grid, split-screen, or multi-photo composition. Each photo must produce one separate poster.
Use a strict 3:4 vertical layout, divided horizontally into two exactly equal 50% sections with a 1:1 height ratio.
TOP 50% — ORIGINAL PHOTO: Preserve the original photo faithfully, including subject identity, structure, pose, proportions, realistic texture, natural lighting, shadows, atmosphere, and color character. Apply only subtle high-end editorial color grading. The environment may be naturally extended when needed, but never stretch, distort, or alter the main subject.
BOTTOM 50% — HAND-DRAWN MEMORY ILLUSTRATION: Understand the photo's core theme, subject relationships, visual flow, emotion, and visual metaphor, then reinterpret it as a sparse hand-drawn pastel doodle and material-collage illustration on textured vintage paper. Do not reproduce every object. Remove irrelevant details and retain only the most recognizable contours, poses, directions, proportions, relationships, and visual memory points. The main subject should become a small stamp-like motif rather than a complete scene, while remaining immediately recognizable.
Use visible pastel crayon/chalk doodle lines with dry grain, broken pigment, slight wobble, varied thickness, imperfect edges, loose strokes, occasional cross-hatching, simple grids, and minimal smudging. Keep the drawing charmingly imperfect and handmade, but never messy or unfinished. Avoid realistic volume and smooth vector graphics.
Use restrained paper collage: paper pieces, cut-paper shapes, pastel color blocks, hand-drawn symbols, subtle layering, and natural handmade edges. Add only a very small number of relevant stars, flowers, waves, geometric marks, or everyday doodles as narrative accents. Avoid decorative clutter.
Maintain generous, intentional negative space around the small stamp-like subject. The subject may be off-center, near an edge, suspended, or partially cropped according to its natural direction, proportion, and visual weight. Balance positive and negative space, density and openness, grouping and separation, asymmetry, and visual pauses. The composition should feel sparse, deliberate, breathable, and editorial.
Use a warm kraft, recycled, handmade, or vintage paper background with realistic fibers and subtle grain. Keep it clean and tactile, without stains or artificial aging. Ensure clear contrast between background and subject so they never visually merge.
Extract 2–4 vivid, emotionally representative colors from the original photo and reinterpret them as a soft, clear pastel palette, such as creamy pink, peach, pale sky blue, mint, soft yellow, or light lavender, balanced with white or cream highlights. Keep the mood bright, warm, comforting, playful, and lively. Avoid muddy brown, dull Morandi palettes, fluorescent colors, or cheap candy-like colors.
Typography should be minimal and editorial. Freely extract a few short phrases or fragments inspired by the photo's subject, emotion, movement, memory, or visual metaphor. Use thin, airy, lightweight typewriter-style lettering with subtle irregular spacing and slight vintage print imperfections. Place typography naturally within the negative space or near the subject; never use a fixed title template.
FINAL STYLE: tactile paper texture, pastel crayon doodles, restrained material collage, a small stamp-like subject, generous intentional negative space, and relaxed editorial typography. Sophisticated, artistic, handmade, light, expressive, and breathable.
AVOID: literal object-by-object tracing, excessive detail, dense outlines, merged subject/background, overly filled compositions, realistic illustration, smooth vector graphics, excessive decoration, childish templates, 3D effects, glossy commercial design, and generic advertising-poster styling.
```

### 프롬프트 ② — 세로형 3:4 (그림 위 · 사진 아래)

```
Create one independent premium editorial poster for each uploaded photo. Never combine photos into a collage, grid, split-screen, or multi-photo composition. Each photo must produce one separate poster.
Use a strict 3:4 vertical layout, divided horizontally into two exactly equal 50% sections with a 1:1 height ratio. The hand-drawn illustration occupies the TOP half and the original photo occupies the BOTTOM half.
BOTTOM 50% — ORIGINAL PHOTO: Preserve the original photo faithfully, including subject identity, structure, pose, proportions, realistic texture, natural lighting, shadows, atmosphere, and color character. Apply only subtle high-end editorial color grading. The environment may be naturally extended when needed, but never stretch, distort, or alter the main subject.
TOP 50% — HAND-DRAWN MEMORY ILLUSTRATION: Understand the photo's core theme, subject relationships, visual flow, emotion, and visual metaphor, then reinterpret it as a sparse hand-drawn pastel doodle and material-collage illustration on textured vintage paper. Do not reproduce every object. Remove irrelevant details and retain only the most recognizable contours, poses, directions, proportions, relationships, and visual memory points. The main subject should become a small stamp-like motif rather than a complete scene, while remaining immediately recognizable.
Use visible pastel crayon/chalk doodle lines with dry grain, broken pigment, slight wobble, varied thickness, imperfect edges, loose strokes, occasional cross-hatching, simple grids, and minimal smudging. Keep the drawing charmingly imperfect and handmade, but never messy or unfinished. Avoid realistic volume and smooth vector graphics.
Use restrained paper collage: paper pieces, cut-paper shapes, pastel color blocks, hand-drawn symbols, subtle layering, and natural handmade edges. Add only a very small number of relevant stars, flowers, waves, geometric marks, or everyday doodles as narrative accents. Avoid decorative clutter.
Maintain generous, intentional negative space around the small stamp-like subject. The subject may be off-center, near an edge, suspended, or partially cropped according to its natural direction, proportion, and visual weight. Balance positive and negative space, density and openness, grouping and separation, asymmetry, and visual pauses. The composition should feel sparse, deliberate, breathable, and editorial.
Use a warm kraft, recycled, handmade, or vintage paper background with realistic fibers and subtle grain. Keep it clean and tactile, without stains or artificial aging. Ensure clear contrast between background and subject so they never visually merge.
Extract 2–4 vivid, emotionally representative colors from the original photo and reinterpret them as a soft, clear pastel palette, such as creamy pink, peach, pale sky blue, mint, soft yellow, or light lavender, balanced with white or cream highlights. Keep the mood bright, warm, comforting, playful, and lively. Avoid muddy brown, dull Morandi palettes, fluorescent colors, or cheap candy-like colors.
Typography should be minimal and editorial. Freely extract a few short phrases or fragments inspired by the photo's subject, emotion, movement, memory, or visual metaphor. Use thin, airy, lightweight typewriter-style lettering with subtle irregular spacing and slight vintage print imperfections. Place typography naturally within the negative space or near the subject; never use a fixed title template.
FINAL STYLE: tactile paper texture, pastel crayon doodles, restrained material collage, a small stamp-like subject, generous intentional negative space, and relaxed editorial typography. Sophisticated, artistic, handmade, light, expressive, and breathable.
AVOID: literal object-by-object tracing, excessive detail, dense outlines, merged subject/background, overly filled compositions, realistic illustration, smooth vector graphics, excessive decoration, childish templates, 3D effects, glossy commercial design, and generic advertising-poster styling.
```

### 프롬프트 ③ — 세로형 3:4 (사진 왼쪽 · 그림 오른쪽)

```
Create one independent premium editorial poster for each uploaded photo. Never combine photos into a collage, grid, split-screen, or multi-photo composition. Each photo must produce one separate poster.
Use a strict 3:4 vertical layout, divided vertically into two exactly equal 50% sections with a 1:1 width ratio, without drawing an obvious dividing line.
LEFT 50% — ORIGINAL PHOTO: Preserve the original photo faithfully, including subject identity, structure, pose, proportions, realistic texture, natural lighting, shadows, atmosphere, and color character. Apply only subtle high-end editorial color grading. The environment may be naturally extended when needed, but never stretch, distort, or alter the main subject.
RIGHT 50% — HAND-DRAWN MEMORY ILLUSTRATION: Understand the photo's core theme, subject relationships, visual flow, emotion, and visual metaphor, then reinterpret it as a sparse hand-drawn pastel doodle and material-collage illustration on textured vintage paper. Do not reproduce every object. Remove irrelevant details and retain only the most recognizable contours, poses, directions, proportions, relationships, and visual memory points. The main subject should become a small stamp-like motif rather than a complete scene, while remaining immediately recognizable.
Use visible pastel crayon/chalk doodle lines with dry grain, broken pigment, slight wobble, varied thickness, imperfect edges, loose strokes, occasional cross-hatching, simple grids, and minimal smudging. Keep the drawing charmingly imperfect and handmade, but never messy or unfinished. Avoid realistic volume and smooth vector graphics.
Use restrained paper collage: paper pieces, cut-paper shapes, pastel color blocks, hand-drawn symbols, subtle layering, and natural handmade edges. Add only a very small number of relevant stars, flowers, waves, geometric marks, or everyday doodles as narrative accents. Avoid decorative clutter.
Maintain generous, intentional negative space around the small stamp-like subject. The subject may be off-center, near an edge, suspended, or partially cropped according to its natural direction, proportion, and visual weight. Balance positive and negative space, density and openness, grouping and separation, asymmetry, and visual pauses. The composition should feel sparse, deliberate, breathable, and editorial.
Use a warm kraft, recycled, handmade, or vintage paper background with realistic fibers and subtle grain. Keep it clean and tactile, without stains or artificial aging. Ensure clear contrast between background and subject so they never visually merge.
Extract 2–4 vivid, emotionally representative colors from the original photo and reinterpret them as a soft, clear pastel palette, such as creamy pink, peach, pale sky blue, mint, soft yellow, or light lavender, balanced with white or cream highlights. Keep the mood bright, warm, comforting, playful, and lively. Avoid muddy brown, dull Morandi palettes, fluorescent colors, or cheap candy-like colors.
Typography should be minimal and editorial. Freely extract a few short phrases or fragments inspired by the photo's subject, emotion, movement, memory, or visual metaphor. Use thin, airy, lightweight typewriter-style lettering with subtle irregular spacing and slight vintage print imperfections. Place typography naturally within the negative space or near the subject; never use a fixed title template.
FINAL STYLE: tactile paper texture, pastel crayon doodles, restrained material collage, a small stamp-like subject, generous intentional negative space, and relaxed editorial typography. Sophisticated, artistic, handmade, light, expressive, and breathable.
AVOID: literal object-by-object tracing, excessive detail, dense outlines, merged subject/background, overly filled compositions, realistic illustration, smooth vector graphics, excessive decoration, childish templates, 3D effects, glossy commercial design, and generic advertising-poster styling.
```

### 프롬프트 ④ — 가로형 4:3 (사진 왼쪽 · 그림 오른쪽)

```
Create one independent premium editorial poster for each uploaded photo. Never combine photos into a collage, grid, split-screen, or multi-photo composition. Each photo must produce one separate poster.
Use a strict 4:3 horizontal (landscape) layout, divided vertically into two exactly equal 50% sections with a 1:1 width ratio, without drawing an obvious dividing line.
LEFT 50% — ORIGINAL PHOTO: Preserve the original photo faithfully, including subject identity, structure, pose, proportions, realistic texture, natural lighting, shadows, atmosphere, and color character. Apply only subtle high-end editorial color grading. The environment may be naturally extended when needed, but never stretch, distort, or alter the main subject.
RIGHT 50% — HAND-DRAWN MEMORY ILLUSTRATION: Understand the photo's core theme, subject relationships, visual flow, emotion, and visual metaphor, then reinterpret it as a sparse hand-drawn pastel doodle and material-collage illustration on textured vintage paper. Do not reproduce every object. Remove irrelevant details and retain only the most recognizable contours, poses, directions, proportions, relationships, and visual memory points. The main subject should become a small stamp-like motif rather than a complete scene, while remaining immediately recognizable.
Use visible pastel crayon/chalk doodle lines with dry grain, broken pigment, slight wobble, varied thickness, imperfect edges, loose strokes, occasional cross-hatching, simple grids, and minimal smudging. Keep the drawing charmingly imperfect and handmade, but never messy or unfinished. Avoid realistic volume and smooth vector graphics.
Use restrained paper collage: paper pieces, cut-paper shapes, pastel color blocks, hand-drawn symbols, subtle layering, and natural handmade edges. Add only a very small number of relevant stars, flowers, waves, geometric marks, or everyday doodles as narrative accents. Avoid decorative clutter.
Maintain generous, intentional negative space around the small stamp-like subject. The subject may be off-center, near an edge, suspended, or partially cropped according to its natural direction, proportion, and visual weight. Balance positive and negative space, density and openness, grouping and separation, asymmetry, and visual pauses. The composition should feel sparse, deliberate, breathable, and editorial.
Use a warm kraft, recycled, handmade, or vintage paper background with realistic fibers and subtle grain. Keep it clean and tactile, without stains or artificial aging. Ensure clear contrast between background and subject so they never visually merge.
Extract 2–4 vivid, emotionally representative colors from the original photo and reinterpret them as a soft, clear pastel palette, such as creamy pink, peach, pale sky blue, mint, soft yellow, or light lavender, balanced with white or cream highlights. Keep the mood bright, warm, comforting, playful, and lively. Avoid muddy brown, dull Morandi palettes, fluorescent colors, or cheap candy-like colors.
Typography should be minimal and editorial. Freely extract a few short phrases or fragments inspired by the photo's subject, emotion, movement, memory, or visual metaphor. Use thin, airy, lightweight typewriter-style lettering with subtle irregular spacing and slight vintage print imperfections. Place typography naturally within the negative space or near the subject; never use a fixed title template.
FINAL STYLE: tactile paper texture, pastel crayon doodles, restrained material collage, a small stamp-like subject, generous intentional negative space, and relaxed editorial typography. Sophisticated, artistic, handmade, light, expressive, and breathable.
AVOID: literal object-by-object tracing, excessive detail, dense outlines, merged subject/background, overly filled compositions, realistic illustration, smooth vector graphics, excessive decoration, childish templates, 3D effects, glossy commercial design, and generic advertising-poster styling.
```

## 활용 예시

- 반려동물, 풍경, 카페 같은 공간 사진에도 잘 나온다
- 인물 사진은 얼굴 부담이 덜한 ② 버전(그림 위·사진 아래)으로 시도
- 원하는 문구가 있다면 프롬프트 끝에 한 줄만 덧붙이면 된다: `Use the phrase 'Good days ahead' as the typewriter text as` 처럼 작성 → AI가 지어내는 대신 지정한 문구가 종이에 찍힌다
- 결과가 마음에 안 들면 → 이어서 "문구 철자만 고쳐줘" 또는 "그림을 조금 더 크게 그려줘"라고 재요청하면 같은 대화 안에서 수정된다

## 주의사항

- 프롬프트 자체에 "사진 여러 장을 하나의 콜라주로 합치지 말라"는 규칙이 명시되어 있으므로, 사진은 반드시 한 번에 한 장씩만 업로드한다
- 종이에 찍히는 영어 문구는 AI가 사진을 보고 즉흥적으로 짓기 때문에 매번 달라진다. 고정 문구를 원하면 반드시 프롬프트 끝에 지정 문구를 추가해야 한다
- **Gemini**(나노바나나)에서도 실행되지만 그림이 작은 우표처럼 나오는 등 톤이 달라진다. 이 가이드의 결과물은 ChatGPT 기준으로 작성되었다

## 출처

- [https://fieldby.notion.site/3e3d730b39538163b41bcb0d72663ef1?pvs=149](https://fieldby.notion.site/3e3d730b39538163b41bcb0d72663ef1?pvs=149)
