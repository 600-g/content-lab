---
name: vintage-field-notes-poster-prompt
description: 이 스킬은 사진 한 장을 **크림색 종이 위 고무도장 판화 그림 + 타자기 글씨**가 찍힌 빈티지 '탐험 노트' 포스터로 바꿔주는 **이미지 생성 프롬프트**입니다. 원본 사진은 그대로 유지하면서 옆(또는 위아래)에 위치·랜드마크를 압축한 손도장 일러스트가 추가됩니다.
origin: content-lab
grade: S
difficulty: 초급
category: 디자인
ai_tools: ["GPT", "Gemini"]
sources:
  - https://fieldby.notion.site/3c9d730b395381d192fed44b806737b6?pvs=149
---

# 사진을 빈티지 탐험노트로 변환

💡 이 스킬은 사진 한 장을 **크림색 종이 위 고무도장 판화 그림 + 타자기 글씨**가 찍힌 빈티지 '탐험 노트' 포스터로 바꿔주는 **이미지 생성 프롬프트**입니다. 원본 사진은 그대로 유지하면서 옆(또는 위아래)에 위치·랜드마크를 압축한 손도장 일러스트가 추가됩니다.

## 이게 뭔가요?

여행 사진이나 풍경·건축 사진 한 장을 업로드하면, 원본 사진은 그대로 살리면서 옆(또는 위아래)에 "고무도장으로 찍은 듯한" 빈티지 판화 그림과 타자기 글씨를 합성해주는 이미지 생성 프롬프트입니다. 완성물은 크림색 오래된 종이 질감 위에 2~4가지 색의 손도장 판화가 찍혀 있고, 장소 이름·번호·키워드 3개·연도가 타자기 서체로 함께 인쇄된 "탐험 노트" 스타일 포스터입니다.

핵심은 사진을 다시 그리거나 왜곡하지 않는다는 점입니다. 원본 사진 영역은 인물·건축·지형·색감·조명을 그대로 보존하고, 나머지 여백 영역에만 위치의 특징을 압축한 소형 도장 그림을 얹습니다. 그래서 "필터를 씌운 사진"이 아니라 "사진 + 손으로 만든 기록물"처럼 보이는 것이 목표입니다.

**ChatGPT**나 **Gemini**의 이미지 업로드·생성 기능만 있으면 바로 사용할 수 있고, 별도 유료 결제 없이 두 도구의 무료/기본 티어에서도 시도해볼 수 있습니다.
✅ 무료 대안: Gemini(무료 버전) 또는 ChatGPT 무료 플랜의 이미지 생성 기능으로 가능

## 따라하기

1. **ChatGPT** 또는 **Gemini**를 열고 바꾸고 싶은 사진 1장을 업로드합니다 (한 번에 한 장씩 처리).
2. 아래 3가지 버전 중 원하는 구도를 골라 프롬프트 **전체**를 복사해 붙여넣습니다.
3. 결과가 마음에 들 때까지 같은 프롬프트로 재생성을 반복합니다.

구도 선택 기준:
- **① 가로형 4:3** — 사진 왼쪽·노트 오른쪽. 가로로 찍은 사진, 인쇄용에 적합
- **② 세로형 3:4** — 노트 위·사진 아래. 인스타 피드용, 가로·세로 사진 모두 대응
- **③ 세로형 3:4** — 사진 왼쪽·노트 오른쪽. 세로로 찍은 사진에 적합

### 프롬프트 ① — 가로형 4:3 (사진 왼쪽 · 노트 오른쪽)

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

- 여행지에서 찍은 건축물·풍경 사진을 업로드 → 세 가지 구도 중 하나로 크림색 종이 위 손도장 판화가 곁들여진 포스터 완성. 인쇄해서 여행 기록집이나 액자용으로 사용 가능
- 여러 장의 사진을 시리즈로 모으고 싶을 때: 프롬프트 끝에 "No. 002로 해줘"처럼 번호를 직접 지정하면 일관된 넘버링의 시리즈 제작 가능
- 결과 글씨의 장소명 철자가 틀렸을 때: 이어서 "장소명 철자만 고쳐줘"라고 요청하면 재생성 없이 텍스트만 수정 가능
- 장소·번호·연도를 AI 추측에 맡기지 않고 직접 지정하고 싶을 때: 프롬프트 끝에 "장소는 'Seongsu, Seoul', 번호는 3, 연도는 2024로 적어줘" 한 줄을 덧붙이면 반영됨

## 주의사항

- 건물·풍경·랜드마크 사진일수록 도장 그림이 잘 나오고, 인물 위주 사진은 결과 품질 편차가 큽니다.
- 노트에 찍히는 글씨는 4줄로 구성됩니다 — 장소 이름 · No. 번호 · 키워드 3개 · 연도. 모두 AI가 사진을 보고 추측하므로, 일상 사진의 경우 장소를 엉뚱하게 표기할 수 있습니다.
- 사진은 한 번에 한 장씩만 업로드해야 합니다. 여러 장을 한 번에 넣으면 콜라주로 합쳐질 수 있습니다.

## 출처

- [https://fieldby.notion.site/3c9d730b395381d192fed44b806737b6?pvs=149](https://fieldby.notion.site/3c9d730b395381d192fed44b806737b6?pvs=149)
