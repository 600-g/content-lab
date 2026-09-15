---
name: photo-rubber-stamp-poster
description: 사진을 업로드하고 3가지 구도(가로 4:3, 세로 위/아래, 세로 좌/우) 프롬프트 중 하나를 선택해 붙여넣으면, 원본 사진과 빈티지 러버 스탬프 판화 일러스트·타자기 텍스트가 결합된 "여행 필드노트" 포스터가 생성됩니다. 장소명·번호·연도를 직접 지정하거나 오탈자만 재수정 요청할 수도 있습니다.
origin: content-lab
grade: S
difficulty: 중급
category: 디자인
ai_tools: ["GPT", "Gemini"]
sources:
  - https://app.notion.com/p/3cb0cb665b9a80a8948eedf3973f0831?source=copy_link
  - https://fieldby.notion.site/3c9d730b395381d192fed44b806737b6?pvs=149
---

# 사진 빈티지 스탬프 포스터로 만들기 (합병됨)

## 이게 뭔가요?

사진을 업로드하고 원하는 프롬프트를 복사해 AI에게 전달하면, **사진의 특징을 담은 빈티지 러버 스탬프 포스터**를 생성해주는 스킬입니다. ChatGPT나 Gemini와 같은 AI 챗봇을 활용해, 업로드한 사진을 기반으로 독특한 러버 스탬프 스타일의 포스터를 제작합니다. 사진의 주요 특징을 추출해 빈티지한 러버 스탬프 디자인으로 재해석하며, 여행 기록, 디자인 프로젝트 등에 활용할 수 있습니다.

핵심은 **사진을 다시 그리거나 왜곡하지 않는다**는 점입니다. 원본 사진 영역은 인물·건축·지형·색감·조명을 그대로 보존하고, 나머지 여백 영역에만 위치의 특징을 압축한 소형 도장 그림을 얹습니다. 완성물은 크림색 오래된 종이 질감 위에 2~4가지 색의 손도장 판화가 찍혀 있고, 장소 이름·번호·키워드 3개·연도가 타자기 서체로 함께 인쇄된 "탐험 노트(field notes)" 스타일 포스터입니다. "필터를 씌운 사진"이 아니라 "사진 + 손으로 만든 기록물"처럼 보이는 것이 목표입니다.

이 스킬은 주로 **ChatGPT** 또는 **Gemini**와 같은 이미지 분석 및 생성 기능이 있는 AI 도구에서 활용됩니다. 별도의 유료 툴 없이 AI 챗봇 내에서 프롬프트 엔지니어링만으로 구현할 수 있습니다.
✅ 무료 대안: Gemini(무료 버전) 또는 ChatGPT 무료 플랜의 이미지 생성 기능으로도 시도 가능

## 따라하기

### 1. 사진 준비 및 AI 챗봇 접속
1. **메인 오브젝트가 명확한 사진**을 준비합니다. 사진의 퀄리티가 결과물에 큰 영향을 미칩니다.
2. ChatGPT 또는 Gemini와 같이 **이미지 업로드 및 프롬프트 입력이 가능한 AI 챗봇**에 접속합니다.
3. 사진은 **한 번에 한 장씩만** 업로드합니다. 여러 장을 한 번에 넣으면 콜라주로 합쳐질 수 있습니다.

### 2. 구도 선택
아래 3가지 버전 중 원하는 구도를 골라 프롬프트 **전체**를 복사한 후, 준비한 사진과 함께 AI 챗봇에 입력합니다.

- **① 가로형 4:3** — 사진 왼쪽·노트 오른쪽. 가로로 찍은 사진, 인쇄용에 적합
- **② 세로형 3:4** — 노트 위·사진 아래. 인스타 피드용, 가로·세로 사진 모두 대응
- **③ 세로형 3:4** — 사진 왼쪽·노트 오른쪽. 세로로 찍은 사진에 적합

#### 프롬프트 ① — 가로형 4:3 (사진 왼쪽 · 노트 오른쪽)

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

#### 프롬프트 ② — 세로형 3:4 (일러스트가 상단 · 사진이 하단)

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

#### 프롬프트 ③ — 세로형 3:4 (사진이 좌측 · 일러스트가 우측)

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

### 3. 결과물 확인 및 수정
AI가 생성한 결과물을 확인합니다. 원하는 결과가 나오지 않았다면, 텍스트 수정(예: 장소명 변경) 또는 프롬프트 조정을 통해 다시 시도합니다. 결과가 마음에 들 때까지 같은 프롬프트로 재생성을 반복해도 됩니다.

## 활용 예시

**시나리오 1: 여행 기록 포스터 제작**
- 입력: 프랑스 파리의 에펠탑 사진 + 프롬프트 ②
- 결과: 사진 하단에는 에펠탑의 실제 모습이, 상단에는 에펠탑 실루엣이 담긴 빈티지 스탬프와 함께 'Paris', 'Eiffel Tower', 'France', '2023' 등의 텍스트가 새겨진 포스터 생성

**시나리오 2: 특정 장소의 건축적 특징을 살린 디자인**
- 입력: 이탈리아 콜로세움의 측면 사진 + 프롬프트 ③
- 결과: 사진 좌측에는 콜로세움 원본 이미지가, 우측에는 콜로세움 외곽선과 'Rome', 'Colosseum', 'Ancient', 'Italy', '2022' 텍스트가 포함된 스탬프 디자인 생성

**시나리오 3: 자연 풍경의 핵심 요소 강조**
- 입력: 스위스 알프스의 산악 지대 사진 + 프롬프트 ②
- 결과: 하단에는 알프스 풍경, 상단에는 산맥의 윤곽선과 'Alps', 'Switzerland', 'Nature', '2024' 텍스트가 담긴 스탬프 포스터 생성

**시나리오 4: 시리즈 넘버링**
- 여러 장의 사진을 시리즈로 모으고 싶을 때: 프롬프트 끝에 "No. 002로 해줘"처럼 번호를 직접 지정하면 일관된 넘버링의 시리즈 제작 가능

**시나리오 5: 텍스트만 재수정**
- 결과 글씨의 장소명 철자가 틀렸을 때: 이어서 "장소명 철자만 고쳐줘"라고 요청하면 이미지 재생성 없이 텍스트만 수정 가능

**시나리오 6: 장소·번호·연도 직접 지정**
- AI 추측에 맡기지 않고 직접 지정하고 싶을 때: 프롬프트 끝에 "장소는 'Seongsu, Seoul', 번호는 3, 연도는 2024로 적어줘" 한 줄을 덧붙이면 반영됨

## 💡 아이디어
- **개인화된 굿즈 제작:** 직접 찍은 사진으로 나만의 엽서, 스티커, 에코백 등을 제작할 수 있습니다.
- **디자인 프로젝트:** 웹사이트 배너, 소셜 미디어 콘텐츠 등에 독특한 시각적 요소를 추가하여 개성을 더할 수 있습니다.
- **콘텐츠 제작:** 블로그나 여행 기록 앱에서 각 장소의 분위기를 살린 썸네일이나 삽화로 활용 가능합니다.

## 주의사항
- **사진 선택:** 메인이 되는 오브젝트가 명확하고, 이미지의 해상도가 높을수록 좋은 결과물을 얻을 수 있습니다. 건물·풍경·랜드마크 사진일수록 도장 그림이 잘 나오고, 인물 위주 사진은 결과 품질 편차가 큽니다.
- **텍스트 정확도:** 노트에 찍히는 글씨는 장소 이름·No. 번호·키워드 3개·연도 4줄로 구성되며, 모두 AI가 사진을 보고 추측하므로 일상 사진의 경우 장소를 엉뚱하게 표기할 수 있습니다. 원하는 내용이 아닐 경우 구체적으로 수정 요청해야 합니다(예: "도쿄 대신 요코하마로 바꿔줘").
- **업로드 방식:** 사진은 한 번에 한 장씩만 업로드해야 합니다. 여러 장을 한 번에 넣으면 콜라주로 합쳐질 수 있습니다.
- **보정된 사진 활용:** AI에 업로드하기 전, 사진을 미리 보정하면 결과물의 퀄리티를 높일 수 있습니다.

## 출처

- [https://app.notion.com/p/3cb0cb665b9a80a8948eedf3973f0831?source=copy_link](https://app.notion.com/p/3cb0cb665b9a80a8948eedf3973f0831?source=copy_link)
- [https://fieldby.notion.site/3c9d730b395381d192fed44b806737b6?pvs=149](https://fieldby.notion.site/3c9d730b395381d192fed44b806737b6?pvs=149)
