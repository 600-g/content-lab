---
name: vintage-photo-field-notes-generator
description: 원본 사진을 **빈티지 탐험 노트** 스타일의 포스터로 변환하여, 사진과 **고무도장 판화** 및 **타자기 글씨**가 결합된 독특한 결과물을 생성하는 스킬입니다.
origin: content-lab
grade: S
difficulty: 중급
category: 디자인
ai_tools: ["Gemini", "GPT"]
sources:
  - https://fieldby.notion.site/3c9d730b395381d192fed44b806737b6?pvs=149
---

# 사진을 빈티지 탐험 노트로 변환

💡 원본 사진을 **빈티지 탐험 노트** 스타일의 포스터로 변환하여, 사진과 **고무도장 판화** 및 **타자기 글씨**가 결합된 독특한 결과물을 생성하는 스킬입니다.

## 이게 뭔가요?
이 스킬은 업로드한 사진 한 장을 마치 **빈티지 탐험 노트**에 기록된 듯한 포스터 이미지로 변환하는 프롬프트 가이드입니다. 단순히 사진을 꾸미는 것을 넘어, 원본 사진의 느낌은 유지하면서도 **크림색 종이** 위에 **고무도장 판화** 스타일의 그림과 **타자기 글씨**가 추가되어 마치 실제 탐험가가 기록한 듯한 아날로그적 감성을 부여합니다.

이 프롬프트는 ChatGPT나 Gemini와 같은 텍스트 기반 AI 이미지 생성기에 사용하도록 설계되었으며, 사용자가 원하는 구도(가로형, 세로형)에 맞춰 세 가지 버전의 상세한 프롬프트를 제공합니다. 원본 사진의 디테일을 최대한 살리면서도, '탐험 노트'라는 특정 콘셉트에 맞춰 시각적 요소를 제어하는 것이 핵심입니다.

💰 유료 필요: 해당 프롬프트는 텍스트 기반의 이미지 생성 AI(Gemini, ChatGPT 등)에 입력하는 것이므로, 사용 가능한 AI 모델에 따라 비용이 발생할 수 있습니다. 하지만 기본적으로 텍스트 입력만으로 작동하므로, **Gemini**나 **ChatGPT** 등 무료 버전으로도 충분히 시도해 볼 수 있습니다. 다만, 원하는 결과물을 얻기 위해 여러 번의 재시도가 필요할 수 있습니다.

## 따라하기
이 스킬을 사용하려면, 원하는 구도에 맞는 프롬프트를 선택하여 **전체 텍스트를 복사**한 후, AI 이미지 생성기에 **사진 1장과 함께 업로드**해야 합니다. 마음에 들 때까지 같은 프롬프트를 반복하여 생성하는 것이 좋습니다.

### 버전 선택

*   **① 가로형 4:3**: 사진 왼쪽 · 노트 오른쪽 | 가로로 찍은 사진, 인쇄용
*   **② 세로형 3:4 (노트 위 · 사진 아래)**: 인스타 피드 비율. 노트가 위, 사진이 아래에 배치됩니다.
*   **③ 세로형 3:4 (사진 왼쪽 · 노트 오른쪽)**: 세로로 찍은 사진에 잘 어울리는 좌우 구도입니다.

### 프롬프트 ① — 가로형 4:3

```
Please create a separate "Rubber Stamp Travel Field Notes Poster" for each photo I upload, outputting each photo individually without collage or multi-image combinations.
Overall, use a 4:3 landscape composition, dividing the frame into left and right regions, but without drawing an obvious dividing line.
The left side takes up about 58% of the frame, faithfully preserving the original photo. Accurately maintain the main subject identity, terrain, architecture, plants, people, spatial relationships, natural lighting and shadows, authentic textures, and the original color atmosphere; apply only restrained art publication-level photo color grading, and add extremely subtle, fine-grained film noise. For layout adaptation, natural cropping is allowed, but do not stretch, distort, shift, replace, or redraw the main subject.
The right side takes up about 42% of the frame, using a warm off-white aged paper as the background. The paper features subtle fibers, natural grain, light usage marks, and a matte texture, while preserving large areas of unprinted paper whitespace, making the blank space an essential part of the layout.
Analyze the original photo and extract the most location-distinctive subject outlines, architectural structures, terrain contours, plant forms, roads, shorelines, or other key visual relationships, compressing them into a small multi-color rubber stamp image.
Do not replicate every single element from the photo item by item. Retain only the minimal information necessary to instantly recognize the original location, subject, and scene relationships. Remove crowds, vehicles, dense windows, repetitive buildings, fragmented vegetation, decorative elements, and irrelevant backgrounds.
The stamp is positioned in the lower-middle of the right-side paper area, occupying only about 30%–38% of the right region's height, with ample whitespace preserved around it. The stamp must not be enlarged into a standard illustration, full landscape painting, or brand logo.
Determine the stamp's organization based on the original photo's composition:
- Iconic architecture: Retain the most distinctive outer contours, roofs, domes, arches, towers, or main structures.
- Mountain settlements: Compress buildings into a few terraced color blocks aligned along the terrain.
- Coastal scenery: Retain mountain contours, settlement layers, shorelines, and sparse intermittent water ripples.
- City panoramas: Retain the main skyline, one iconic building, and one or two layers of distant mountains.
- Natural landscapes: Retain primary mountain forms, trees, shorelines, or road orientations.
- Foreground occlusions: If narratively important in the original photo, retain as foreground stamp outlines.
Extract 2–4 spot inks from the original photo. Prioritize desaturated colors like carbon black, deep green, brick red, ochre yellow, slate blue, or taupe brown, but do not force a fixed palette. Preserve the most distinctive color character from the original photo, allowing only a small area of color for visual emphasis.
Render each color as a separately hand-stamped effect:
Authentic rubber stamp carving texture, hand-engraved marks, uneven line widths, contour notches, fractured edges, dry ink shortages, paper show-through, granular ink, uneven pressure, partial ghosting, and about 1–2 mm of subtle misregistration.
Allow natural misalignment between color layers; edges must not be digitally smoothed. The print should resemble a real carved stamp pressed onto aged paper, not a filtered photo, smooth vector illustration, or line-art logo.
Generate text based on the photo's location, theme, and visual imagery:
Location English name
No. Number
Three short English keywords
Gregorian calendar year
Place the text below or adjacent to the stamp in the whitespace, using a small, restrained, slightly mechanically imperfect typewriter font. The typography should evoke a traveler's field record, not an ad headline. Ensure all text is spelled accurately, without adding irrelevant slogans, brands, or decorative copy.
The overall vibe is like field notes kept by an architect, travel writer, or natural observer: quiet, restrained, tactilely real, regionally specific, with handmade imperfections and a collectible feel. The photo handles the on-site record; the stamp captures the most recognizable fragments of memory.
Avoid: Obvious central dividing lines, circular seals, Chinese red stamps, postage stamp perforations, wax seals, sticker collages, tourist souvenir templates, smooth vector logos, generic city icons, full replication of all architecture, dense detailing, childlike craftiness, cartoon style, 3D rendering, plastic textures, glossy digital gradients, oversaturation, excessive text, decorative clutter, and redrawing or altering the left-side original photo.
```

### 프롬프트 ② — 세로형 3:4 (노트 위 · 사진 아래)

```
Please create a separate "Rubber Stamp Travel Field Notes Poster" for each photo I upload, outputting each photo individually without collage or multi-image combinations.
Overall, use a 3:4 portrait (vertical) composition, dividing the frame into top and bottom regions, but without drawing an obvious dividing line.
The bottom section takes up about 58% of the frame height, faithfully preserving the original photo. Accurately maintain the main subject identity, terrain, architecture, plants, people, spatial relationships, natural lighting and shadows, authentic textures, and the original color atmosphere; apply only restrained art publication-level photo color grading, and add extremely subtle, fine-grained film noise. For layout adaptation, natural cropping is allowed, but do not stretch, distort, shift, replace, or redraw the main subject.
The top section takes up about 42% of the frame height, using a warm off-white aged paper as the background. The paper features subtle fibers, natural grain, light usage marks, and a matte texture, while preserving large areas of unprinted paper whitespace, making the blank space an essential part of the layout.
Analyze the original photo and extract the most location-distinctive subject outlines, architectural structures, terrain contours, plant forms, roads, shorelines, or other key visual relationships, compressing them into a small multi-color rubber stamp image.
Do not replicate every single element from the photo item by item. Retain only the minimal information necessary to instantly recognize the original location, subject, and scene relationships. Remove crowds, vehicles, dense windows, repetitive buildings, fragmented vegetation, decorative elements, and irrelevant backgrounds.
The stamp is positioned in the center of the top paper area, occupying only about 30%–38% of the top region's height, with ample whitespace preserved around it. The stamp must not be enlarged into a standard illustration, full landscape painting, or brand logo.
Determine the stamp's organization based on the original photo's composition:
- Iconic architecture: Retain the most distinctive outer contours, roofs, domes, arches, towers, or main structures.
- Mountain settlements: Compress buildings into a few terraced color blocks aligned along the terrain.
- Coastal scenery: Retain mountain contours, settlement layers, shorelines, and sparse intermittent water ripples.
- City panoramas: Retain the main skyline, one iconic building, and one or two layers of distant mountains.
- Natural landscapes: Retain primary mountain forms, trees, shorelines, or road orientations.
- Foreground occlusions: If narratively important in the original photo, retain as foreground stamp outlines.
Extract 2–4 spot inks from the original photo. Prioritize desaturated colors like carbon black, deep green, brick red, ochre yellow, slate blue, or taupe brown, but do not force a fixed palette. Preserve the most distinctive color character from the original photo, allowing only a small area of color for visual emphasis.
Render each color as a separately hand-stamped effect:
Authentic rubber stamp carving texture, hand-engraved marks, uneven line widths, contour notches, fractured edges, dry ink shortages, paper show-through, granular ink, uneven pressure, partial ghosting, and about 1–2 mm of subtle misregistration.
Allow natural misalignment between color layers; edges must not be digitally smoothed. The print should resemble a real carved stamp pressed onto aged paper, not a filtered photo, smooth vector illustration, or line-art logo.
Generate text based on the photo's location, theme, and visual imagery:
Location English name
No. Number
Three short English keywords
Gregorian calendar year
Place the text below or adjacent to the stamp in the whitespace, using a small, restrained, slightly mechanically imperfect typewriter font. The typography should evoke a traveler's field record, not an ad headline. Ensure all text is spelled accurately, without adding irrelevant slogans, brands, or decorative copy.
The overall vibe is like field notes kept by an architect, travel writer, or natural observer: quiet, restrained, tactilely real, regionally specific, with handmade imperfections and a collectible feel. The photo handles the on-site record; the stamp captures the most recognizable fragments of memory.
Avoid: Obvious central dividing lines, circular seals, Chinese red stamps, postage stamp perforations, wax seals, sticker collages, tourist souvenir templates, smooth vector logos, generic city icons, full replication of all architecture, dense detailing, childlike craftiness, cartoon style, 3D rendering, plastic textures, glossy digital gradients, oversaturation, excessive text, decorative clutter, and redrawing or altering the bottom original photo.
```

### 프롬프트 ③ — 세로형 3:4 (사진 왼쪽 · 노트 오른쪽)

```
Please create a separate "Rubber Stamp Travel Field Notes Poster" for each photo I upload, outputting each photo individually without collage or multi-image combinations.
Overall, use a 3:4 portrait (vertical) composition, dividing the frame into left and right regions, but without drawing an obvious dividing line.
The left side takes up about 58% of the frame width, faithfully preserving the original photo. Accurately maintain the main subject identity, terrain, architecture, plants, people, spatial relationships, natural lighting and shadows, authentic textures, and the original color atmosphere; apply only restrained art publication-level photo color grading, and add extremely subtle, fine-grained film noise. For layout adaptation, natural cropping is allowed, but do not stretch, distort, shift, replace, or redraw the main subject.
The right side takes up about 42% of the frame width, using a warm off-white aged paper as the background. The paper features subtle fibers, natural grain, light usage marks, and a matte texture, while preserving large areas of unprinted paper whitespace, making the blank space an essential part of the layout.
Analyze the original photo and extract the most location-distinctive subject outlines, architectural structures, terrain contours, plant forms, roads, shorelines, or other key visual relationships, compressing them into a small multi-color rubber stamp image.
Do not replicate every single element from the photo item by item. Retain only the minimal information necessary to instantly recognize the original location, subject, and scene relationships. Remove crowds, vehicles, dense windows, repetitive buildings, fragmented vegetation, decorative elements, and irrelevant backgrounds.
The stamp is positioned in the lower-middle of the right-side paper area, occupying only about 30%–38% of the right region's height, with ample whitespace preserved around it. The stamp must not be enlarged into a standard illustration, full landscape painting, or brand logo.
Determine the stamp's organization based on the original photo's composition:
- Iconic architecture: Retain the most distinctive outer contours, roofs, domes, arches, towers, or main structures.
- Mountain settlements: Compress buildings into a few terraced color blocks aligned along the terrain.
- Coastal scenery: Retain mountain contours, settlement layers, shorelines, and sparse intermittent water ripples.
- City panoramas: Retain the main skyline, one iconic building, and one or two layers of distant mountains.
- Natural landscapes: Retain primary mountain forms, trees, shorelines, or road orientations.
- Foreground occlusions: If narratively important in the original photo, retain as foreground stamp outlines.
Extract 2–4 spot inks from the original photo. Prioritize desaturated colors like carbon black, deep green, brick red, ochre yellow, slate blue, or taupe brown, but do not force a fixed palette. Preserve the most distinctive color character from the original photo, allowing only a small area of color for visual emphasis.
Render each color as a separately hand-stamped effect:
Authentic rubber stamp carving texture, hand-engraved marks, uneven line widths, contour notches, fractured edges, dry ink shortages, paper show-through, granular ink, uneven pressure, partial ghosting, and about 1–2 mm of subtle misregistration.
Allow natural misalignment between color layers; edges must not be digitally smoothed. The print should resemble a real carved stamp pressed onto aged paper, not a filtered photo, smooth vector illustration, or line-art logo.
Generate text based on the photo's location, theme, and visual imagery:
Location English name
No. Number
Three short English keywords
Gregorian calendar year
Place the text below or adjacent to the stamp in the whitespace, using a small, restrained, slightly mechanically imperfect typewriter font. The typography should evoke a traveler's field record, not an ad headline. Ensure all text is spelled accurately, without adding irrelevant slogans, brands, or decorative copy.
The overall vibe is like field notes kept by an architect, travel writer, or natural observer: quiet, restrained, tactilely real, regionally specific, with handmade imperfections and a collectible feel. The photo handles the on-site record; the stamp captures the most recognizable fragments of memory.
Avoid: Obvious central dividing lines, circular seals, Chinese red stamps, postage stamp perforations, wax seals, sticker collages, tourist souvenir templates, smooth vector logos, generic city icons, full replication of all architecture, dense detailing, childlike craftiness, cartoon style, 3D rendering, plastic textures, glossy digital gradients, oversaturation, excessive text, decorative clutter, and redrawing or altering the left-side original photo.
```

## 활용 예시

- **시나리오 1: 유럽 여행 사진 처리 (가로형 4:3 사용)**
  *   **입력**: 유럽의 오래된 거리 풍경 사진 1장 업로드 + 프롬프트 ① 복사/붙여넣기
  *   **결과**: 사진의 왼쪽 절반은 원본 사진의 느낌을 유지하고, 오른쪽 절반에는 크림색 종이 배경 위에 해당 지역의 특징적인 건축물 윤곽이 **고무도장**으로 찍히고, 아래에는 'Paris, France', 'No. 001', 'Eiffel, Seine, Art', '2023'과 같은 **타자기 텍스트**가 기록된 포스터가 생성됩니다.

- **시나리오 2: 인스타그램 피드용 (세로형 3:4, 노트 위)**
  *   **입력**: 자연 풍경 사진 1장 업로드 + 프롬프트 ② 복사/붙여넣기
  *   **결과**: 사진이 아래쪽에 배치되고, 상단에는 노트 배경과 함께 풍경의 주요 지형지물(산맥, 해안선 등)이 **스탬프**로 압축되어 찍히며, 그 아래에 여행 기록 텍스트가 배치된 세로형 이미지가 생성됩니다.

- **시나리오 3: 특정 정보 강제 지정 (프롬프트 ③ 사용)**
  *   **입력**: 특정 장소의 사진 1장 업로드 + 프롬프트 ③ 복사/붙여넣기 + **추가 요청**:

## 출처

- [https://fieldby.notion.site/3c9d730b395381d192fed44b806737b6?pvs=149](https://fieldby.notion.site/3c9d730b395381d192fed44b806737b6?pvs=149)
