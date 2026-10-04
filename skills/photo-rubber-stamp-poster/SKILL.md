---
name: photo-rubber-stamp-poster
description: 사진 한 장을 **ChatGPT·Gemini** 이미지 생성에 올리고 프롬프트를 붙여넣어 **러버 스탬프 여행 포스터·크레용 그림일기 포스터·미니멀 포스터·플레이리스트 배경화면·'사랑이 잘' 앨범커버**로 바꾸는 스타일별 프롬프트 팩입니다.
origin: content-lab
grade: S
difficulty: 중급
category: 디자인
ai_tools: ["GPT", "Gemini"]
sources:
  - https://app.notion.com/p/3cb0cb665b9a80a8948eedf3973f0831?source=copy_link
  - https://fieldby.notion.site/3c9d730b395381d192fed44b806737b6?pvs=149
  - https://app.notion.com/p/3c004aeefb608081ac9bd7814df90e34?source=copy_link
  - https://fieldby.notion.site/3e3d730b39538163b41bcb0d72663ef1?pvs=149
  - https://fieldby.notion.site/3a6d730b39538184855cde596254cee5?pvs=149
  - https://fieldby.notion.site/3b8d730b3953812c868aca0d22bb954b?pvs=149
---

# 사진으로 포스터·앨범커버 만들기

💡 내 사진 한 장에 **복붙 프롬프트** 하나만 얹으면 **빈티지 스탬프 포스터·크레용 그림일기·미니멀 포스터·플레이리스트 배경화면·앨범커버**가 나옵니다. 스타일 고르는 표에서 고르고, 사진 방향에 맞는 버전을 그대로 붙여넣으면 됩니다.

## 이게 뭔가요?

사진 한 장(앨범커버는 세 장)을 이미지 생성 AI에 올리고 영문 프롬프트를 붙여넣어, 사진을 **포스터·앨범커버·배경화면**으로 바꾸는 프롬프트 모음입니다. 디자인 툴 없이 AI 챗봇 안에서 프롬프트만으로 완성합니다.

다섯 스타일 모두 같은 원칙 위에 서 있습니다.

- **원본 사진은 다시 그리지 않는다.** 인물·건축·지형·색감·조명을 그대로 보존하고, 레이아웃에 맞추는 자연스러운 크롭·배경 연장만 허용합니다. 주 피사체를 늘이거나 왜곡하지 않습니다.
- **나머지 영역에만 재해석을 얹는다.** 사진에서 가장 알아보기 쉬운 윤곽·구도·색만 뽑아 도장 판화, 크레용 손그림, 기하학 추상, 유리 카드 UI 같은 형식으로 압축합니다.
- **한 장 = 한 작품.** 여러 장을 한 번에 넣어 콜라주로 합치지 않습니다.

| 스타일 | 결과물 | 재해석 영역의 표현 |
|---|---|---|
| 러버 스탬프 여행 필드노트 | 사진 + 크림색 오래된 종이 위 2~4색 손도장 판화 + 타자기 글씨(장소명·No. 번호·키워드 3개·연도) | 장소의 특징을 압축한 작은 멀티컬러 고무도장 |
| 크레용 그림일기 | 사진 + 크라프트지 위 파스텔 크레용 손그림·종이 콜라주·타자기 문구 | 사진의 감정·분위기만 추출한 우표 같은 작은 손그림 |
| 미니멀 디자인 포스터 | 위 50% 사진 + 아래 50% 기하학 추상 | 단순 도형·평면 색·가는 선·여백 |
| 플레이리스트 배경화면 | 인물 사진 주위로 스포티파이·애플뮤직풍 반투명 음악 플레이어 카드가 떠 있는 9:16 배경화면 | 유리 질감 AR 카드 UI |
| '사랑이 잘' 앨범커버 | 두 사람 얼굴로 만든 2x2 빈티지 필름 사진 4컷 + 세로 손글씨 "사랑이 / 잘" | 원본 앨범커버의 레이아웃·톤 |

**도구:** 이미지 업로드와 이미지 생성을 함께 지원하는 **ChatGPT** 또는 **Gemini**에서 씁니다. 결과 예시는 ChatGPT 기준으로 검증된 프롬프트들입니다.

- 💰 유료 필요: ChatGPT Plus 이상이면 이미지 생성 한도가 넉넉합니다. 얼굴 특징 유지(앨범커버)나 정확한 곡 제목 표기(배경화면)처럼 까다로운 요구일수록 상위 모델이 유리합니다.
- ✅ 무료 대안: ChatGPT 무료 버전도 횟수 제한 안에서 이미지 생성이 됩니다. **Gemini**(무료, 나노바나나)도 실행되지만 크레용 스타일은 그림이 우표처럼 작게 나오는 등 톤이 달라집니다. Bing Image Creator, Leonardo AI 등 무료·부분 유료 서비스로도 비슷한 결과를 시도할 수 있으나 얼굴 유지 정도와 품질은 떨어질 수 있습니다.

## 따라하기

### 스타일·버전 고르기

먼저 결과물을 고르고, 사진 방향과 원하는 배치에 맞는 버전을 고릅니다.

| 스타일 | 버전 | 비율 · 배치 | 어울리는 사진 / 용도 | 업로드 |
|---|---|---|---|---|
| 러버 스탬프 | ① | 가로 4:3 · 사진 왼쪽(58%) · 노트 오른쪽(42%) | 가로로 찍은 사진, 인쇄용 | 1장 |
| 러버 스탬프 | ② | 세로 3:4 · 노트 위(42%) · 사진 아래(58%) | 인스타 피드용, 가로·세로 사진 모두 대응 | 1장 |
| 러버 스탬프 | ③ | 세로 3:4 · 사진 왼쪽(58%) · 노트 오른쪽(42%) | 세로로 찍은 사진 | 1장 |
| 크레용 그림일기 | ① | 세로 3:4 · 사진 위 · 그림 아래 (1:1) | 기본형, 인스타 피드용 | 1장 |
| 크레용 그림일기 | ② | 세로 3:4 · 그림 위 · 사진 아래 (1:1) | 인물 사진(얼굴 부담이 덜한 구도) | 1장 |
| 크레용 그림일기 | ③ | 세로 3:4 · 사진 왼쪽 · 그림 오른쪽 (1:1) | 세로로 찍은 사진, 오른쪽에 문구 얹을 때 | 1장 |
| 크레용 그림일기 | ④ | 가로 4:3 · 사진 왼쪽 · 그림 오른쪽 (1:1) | 가로 포스터, 인쇄용 | 1장 |
| 미니멀 포스터 | — | 세로 3:4 · 사진 위 · 추상 아래 (1:1) | 풍경·작업물·인물, 전시 포스터 느낌 | 1장 |
| 플레이리스트 배경화면 | 밝은 버전 | 세로 9:16 · 원본 배경 유지 + 카드 4개 | 인물 사진, 폰 배경화면·프로필 | 1장 (+앨범커버 이미지 선택) |
| 플레이리스트 배경화면 | 어두운톤 버전 | 시네마틱 · 카드가 인물 앞뒤로 겹침 | 분위기 있는 인물 사진, 음악 추천 이미지 | 1장 |
| '사랑이 잘' 앨범커버 | — | 세로 4:5 (1080×1350) · 2x2 4컷 | 선명한 정면 얼굴 사진 2장(여성·남성) | 3장 |

**사진 고르는 기준 (공통)**

- 주 피사체가 명확하고 해상도가 높을수록 결과가 좋습니다. 업로드 전에 미리 보정해 두면 품질이 올라갑니다.
- 러버 스탬프는 건물·풍경·랜드마크 사진일수록 도장 그림이 잘 나오고, 인물 위주 사진은 결과 편차가 큽니다.
- 크레용 그림일기는 반려동물·풍경·카페 같은 공간 사진에도 잘 나옵니다.
- 얼굴이 중요한 스타일(앨범커버·배경화면)은 선명한 정면 사진을 씁니다.

### 공통 사용법

1. ChatGPT 또는 Gemini를 열고 사진을 **한 번에 한 장씩** 업로드합니다. 여러 장을 한 번에 넣으면 콜라주로 합쳐질 수 있습니다. 포스터 프롬프트들에도 "콜라주로 합치지 말라"는 규칙이 들어 있습니다. (예외: 앨범커버는 세 장을 정해진 순서로 올립니다.)
2. 아래 스타일 절에서 고른 버전의 프롬프트를 **전체** 복사해 사진과 함께 붙여넣습니다. 비율은 프롬프트 안에 이미 들어 있으니 따로 지정하지 않아도 됩니다. 영문 프롬프트가 인식률이 가장 좋습니다.
3. 글자를 AI 추측에 맡기기 싫으면 프롬프트 **끝에 한 줄**을 덧붙입니다 (스타일별 예시는 각 절에 있음).
4. 결과가 마음에 들 때까지 같은 프롬프트로 재생성합니다.
5. 부분만 고치고 싶으면 같은 대화에서 이어서 요청합니다. 예: "장소명 철자만 고쳐줘", "문구 철자만 고쳐줘", "그림을 조금 더 크게 그려줘", "도쿄 대신 요코하마로 바꿔줘". 이미지 전체를 다시 만들지 않고 해당 부분만 수정됩니다.

### 1. 러버 스탬프 여행 필드노트 포스터

크림색 오래된 종이 질감 위에 2~4가지 색의 손도장 판화가 찍혀 있고, 장소 이름·번호·키워드 3개·연도가 타자기 서체로 인쇄된 "탐험 노트(field notes)" 스타일입니다. "필터를 씌운 사진"이 아니라 "사진 + 손으로 만든 기록물"처럼 보이는 것이 목표입니다.

프롬프트가 하는 일:

- 원본 사진 영역(58%)은 인물·건축·지형·색감·조명을 보존하고 절제된 컬러 그레이딩과 아주 미세한 필름 노이즈만 더합니다.
- 노트 영역(42%)은 따뜻한 오프화이트 오래된 종이에 넓은 여백을 남기고, 도장은 그 영역 높이의 30~38%만 차지합니다.
- 사진 구도에 따라 도장 구성을 자동으로 정합니다: 랜드마크 건축 → 외곽선·지붕·돔·탑, 산악 마을 → 계단식 색 블록, 해안 → 산 윤곽·해안선·물결, 도시 파노라마 → 스카이라인 + 대표 건물 하나, 자연 풍경 → 산·나무·길의 방향.
- 글씨는 장소 영문명 / No. 번호 / 영문 키워드 3개 / 연도 4줄로, AI가 사진을 보고 추측해 채웁니다.

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

#### 프롬프트 ② — 세로형 3:4 (노트 위 · 사진 아래)

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

#### 프롬프트 ③ — 세로형 3:4 (사진 왼쪽 · 노트 오른쪽)

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

**글씨 직접 지정:** 프롬프트 끝에 "장소는 'Seongsu, Seoul', 번호는 3, 연도는 2024로 적어줘" 같은 한 줄을 덧붙이면 반영됩니다. 시리즈로 모을 때는 "No. 002로 해줘"처럼 번호만 지정해 일관된 넘버링을 만듭니다.

### 2. 크레용 그림일기 포스터

업로드한 사진은 그대로 두고, 반대쪽 크라프트지 위에 파스텔 크레용으로 그린 작은 손그림·종이 콜라주 조각·타자기 글씨 몇 줄을 얹어 "그림일기 포스터" 한 장으로 완성합니다. 원본 인물·풍경·반려동물의 형태는 보존하고, 반대편에는 사진의 감정과 분위기만 추출한 미니멀한 삽화를 배치합니다.

프롬프트가 하는 일:

- 사진과 그림을 정확히 50:50(1:1)으로 나눕니다.
- 주 피사체를 완전한 장면이 아니라 **작은 우표 같은 모티프**로 줄이고 주변에 의도적인 여백을 넓게 둡니다.
- 원본에서 2~4가지 색을 뽑아 크리미 핑크·피치·연하늘·민트·연노랑·연라벤더 같은 맑은 파스텔로 바꿉니다. 탁한 갈색, 모란디 톤, 형광색은 피합니다.
- 영어 문구는 사진의 주제·감정·움직임에서 AI가 즉흥적으로 지어 얇은 타자기 서체로 여백에 놓습니다.

#### 프롬프트 ① — 세로형 3:4 (사진 위 · 그림 아래)

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

#### 프롬프트 ② — 세로형 3:4 (그림 위 · 사진 아래)

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

#### 프롬프트 ③ — 세로형 3:4 (사진 왼쪽 · 그림 오른쪽)

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

#### 프롬프트 ④ — 가로형 4:3 (사진 왼쪽 · 그림 오른쪽)

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

**문구 직접 지정:** 문구는 매번 달라집니다. 고정 문구를 원하면 프롬프트 끝에 `Use the phrase 'Good days ahead' as the typewriter text as` 처럼 한 줄을 덧붙입니다. AI가 지어내는 대신 지정한 문구가 종이에 찍힙니다.

### 3. 미니멀 디자인 포스터

하나의 사진을 하나의 전시 포스터처럼 만드는 고급 미니멀 스타일입니다. 3:4 세로 화면을 위아래 정확히 1:1로 나눠, 위 절반은 원본 사진의 질감·자연광·색감을 유지하면서 전문 사진·아트 전시 수준으로 미세 보정하고, 아래 절반은 주 피사체의 가장 알아보기 쉬운 윤곽과 구조를 단순 도형·평면 색·가는 선·여백으로 추상화합니다. 색은 위 사진에서 뽑고, 베이지나 밝은 배경에 피사체를 가운데 두며, 짧은 영문 제목·기호·연도를 소량 넣을 수 있습니다.

```
For each photo I upload, create a separate high-end minimalist design poster individually—no multi-image collages; output each photo as a standalone piece. Overall, adopt a 3:4 vertical composition, with the upper and lower sections strictly at a 1:1 height ratio, each occupying 50% of the frame. The upper half preserves the original photo, maintaining the main structure, authentic texture, natural light and shadow, and original color atmosphere, with only subtle professional photography color grading to give it a sense of professional photography and art exhibition quality. To fit the aspect ratio, naturally extend the sky, ground, or environmental background, but do not stretch, distort, or alter the main subject. The lower half extracts the most recognizable outline and structure of the main subject from the photo, using simple geometric shapes, flat colors, fine lines, and white space for a stylized abstract expression. Avoid realistic illustrations or complex details, but preserve the subject's key features so that the original item is instantly recognizable. Color palette extracted from the upper photo, with minimal horizontal lines, vertical lines, or abstract border elements added. Overall, use a beige or light-colored background, ample white space, main subject centered, and a balanced, restrained composition. May include a small amount of concise English titles, symbols, years, or style references from international design studios, architectural posters, art exhibition posters, and high-end brand visual systems—elegant, modern, refined, artistic, avoiding vulgar clichés, cheap low-quality feel, cartoonish, electronic, or templated sensations.
```

**다듬기:** 결과가 원하는 방향이 아니면 색상 팔레트, 라인 스타일, 제목 추가 여부 같은 부분을 고쳐 다시 요청하거나 다른 사진으로 시도합니다.

### 4. 플레이리스트 배경화면

인물 사진을 스포티파이·애플뮤직 플레이리스트 화면처럼 바꿉니다. 반투명 유리 질감의 음악 플레이어 카드가 인물 주위에 떠 있는 효과입니다. 사진 구도에 맞춰 두 버전 중 하나를 고릅니다.

- **밝은 버전:** 인물과 원본 배경을 그대로 유지하고 카드 4개를 배치합니다 (오른쪽 아래 큰 카드 1, 인물 좌우 중간 카드 2, 인물 뒤 위쪽 작은 카드 1). 얼굴과 손은 가리지 않습니다.
- **어두운톤 버전:** 시네마틱 연출로, 카드가 인물 앞뒤로 겹치며 심도감을 만듭니다.

절차:

1. 인물 사진을 업로드합니다.
2. 버전을 골라 프롬프트를 붙여넣습니다.
3. 곡 정보를 바꿉니다. 밝은 버전은 카드별로 지정된 4곡을, 어두운톤 버전은 `[your songs]` 뒤의 곡 목록을 원하는 곡으로 고칩니다. **'제목 — 아티스트' 형식은 반드시 유지**해야 AI가 정확히 인식합니다.
4. 앨범 커버까지 정확히 넣고 싶으면 해당 앨범 커버 이미지를 함께 첨부합니다. 밝은 버전 프롬프트는 첨부된 앨범커버 레퍼런스를 그대로 쓰라고 지시합니다.
5. 생성 후 만족스럽지 않으면 곡 정보·카드 개수·배경 유지 여부를 고쳐 다시 생성합니다.

#### 밝은 버전 프롬프트

```markdown
[EDIT INSTRUCTION] Edit the original image in a vertical 9:16 format. Preserve the original person, face, hairstyle, expression, pose, body proportions, outfit, camera angle, framing, lighting, and color exactly as-is. Preserve the entire original background exactly as-is, including its location, architecture, walls, floor, objects, colors, textures, perspective, shadows, and depth. Do not replace, redesign, extend, blur, remove, or reinterpret the background. Add exactly four floating AR music-player cards: * One oversized card in the lower-right foreground, partially cropped by the frame * One medium card on the left side of the subject * One medium card on the right side of the subject * One smaller card behind the subject in the upper background Keep the subject's face and hands unobstructed. The cards are translucent pale-blue frosted glass with rounded corners, subtle reflections, softly illuminated edges, and consistent music-player UI design. Display exactly one track on each card: "Espresso" — Sabrina Carpenter "BIRDS OF A FEATHER" — Billie Eilish "Love Me Not" — Ravyn Lenae "Daisies" — Justin Bieber Each card includes one square album cover, song title, artist name, progress bar, pause button, previous and next buttons, timestamp, and heart icon. Keep all titles and artist names correctly spelled and clearly legible. Use the supplied album-cover references exactly as provided. Do not redesign, replace, duplicate, recolor, crop incorrectly, or invent album artwork. Add only subtle pale-blue reflections from the cards onto nearby surfaces. Do not change the original environmental lighting. Do not add extra cards, extra people, new background objects, logos, random text, motion blur, or additional visual effects.
```

#### 어두운톤 버전 프롬프트

```markdown
A cinematic, dreamlike AR visual featuring a central photorealistic person surrounded by floating 3D Spotify/Apple Music interface cards. The cards orbit the subject at varying depths — some in the foreground obscuring the figure, others drifting behind. Style: Translucent frosted glass with glowing borders and rounded edges. Lighting: natural tones. Enhance the photo quality. Includes depth of field (blurred background cards) and motion accents, highlighting [your songs] player interfaces: century, rottweiler, 4 raws, phantom, mist, cali man, LV sandals.
```

### 5. '사랑이 잘' 앨범커버 (커플 4컷)

아이유·오혁의 '사랑이 잘' 앨범커버 레이아웃·비율·톤을 참고해, 두 사람의 얼굴 사진으로 따뜻한 빈티지 필름 톤의 2x2 4컷 커버를 만듭니다. 왼쪽 열은 여성, 오른쪽 열은 남성이고, 윗줄은 같은 오버사이즈 블레이저, 아랫줄은 같은 흰 프린트 티셔츠로 맞춥니다. 오른쪽 아래 여백에 세로 손글씨 "사랑이 / 잘"이 들어갑니다. 핵심은 **얼굴 특징을 그대로 유지**하는 것이라, 프롬프트에 얼굴 정체성 고정(FACE IDENTITY LOCK)과 미화 금지(ANTI-BEAUTIFICATION) 문단이 들어 있습니다.

**준비물**

- 원본 '사랑이 잘' 앨범커버 이미지 (레이아웃·비율·톤 참고용)
- 여성 얼굴 사진 1장 (정면이 잘 나온 사진 권장)
- 남성 얼굴 사진 1장

**STEP 1 · 사진 3장 지정** — 순서대로 업로드하고 역할을 맞춥니다.

- Image 1: 원본 '사랑이 잘' 앨범커버 (레이아웃, 비율, 톤 참고용)
- Image 2: 여성 얼굴 사진
- Image 3: 남성 얼굴 사진

**STEP 2 · 프롬프트 붙여넣기** — 아래 영문 프롬프트를 사진들과 함께 입력합니다. 프롬프트 안의 역슬래시(`\'`, `\"`)는 원문 표기 그대로이며 붙여넣어도 무방합니다.

```
Use the uploaded photos as fixed identity references: Image 2 = the WOMAN\'s face identity, Image 3 = the MAN\'s face identity. Use Image 1 only as the LAYOUT + RATIO + TONE reference: a tight 2x2 grid of four individually printed vintage photographs on a warm cream film-toned ground, with the vertical hand-brushed Korean text \"사랑이 / 잘\" on the lower-right margin. Take the grid structure, proportions, print texture, and tone from Image 1 — not any faces. Create a vertical 4:5 (1080×1350) album-cover composition: four vintage warm-toned portrait prints in a tight 2x2 grid with slim even gutters. The outer ground is a warm yellowed cream film paper; each print has subtle individual tonal variation as if separately developed, with faint glossy photo-paper edges. Vertical calligraphy \"사랑이 / 잘\" on the lower-right margin. Woman occupies the LEFT column (top-left, bottom-left); man occupies the RIGHT column (top-right, bottom-right). ── FACE IDENTITY LOCK (ABSOLUTE HIGHEST PRIORITY — overrides all other layers if any conflict) ── The faces from Image 2 (woman) and Image 3 (man) are the single most important element of this render. Reproduce them as a strict 1:1 identity match — the exact same real individuals, instantly recognizable as the people in the uploaded photos, in every frame. Preserve ALL of the following from each source photo, unchanged: overall face shape, width, and length; jawline and chin; cheekbones; forehead and hairline; eye shape, size, spacing, eyelid crease, iris color; eyebrow shape and thickness; nose shape, bridge, tip, nostrils; lip shape and thickness, mouth width, philtrum; exact hairstyle, length, parting, texture, color; skin tone and undertone; age; and any distinctive marks (moles, freckles, dimples, ear shape). Keep the true, natural spacing and proportions between all features. Only head ANGLE and EXPRESSION may change. This is the SAME face from a different angle, never reinterpreted, morphed, or blended. Do not blend the woman\'s and man\'s identities. ── ANTI-BEAUTIFICATION (CRITICAL for the WOMAN) ── Do NOT beautify, idealize, or \"prettify\" the woman\'s face. Specifically: - do NOT enlarge her eyes, sharpen or slim her jaw, narrow her nose, or smooth her face into a generic pretty K-pop / idol face - do NOT make her look younger, thinner-faced, or more symmetrical than the source - KEEP her real, natural facial asymmetry, her exact eye size and shape, her real nose width, her actual face width and cheek fullness, and any imperfections or unique features exactly as in Image 2 - her likeness to the source photo matters more than making her attractive; a less \"beautiful\" but accurate face is correct, a prettier but different face is WRONG Apply the same faithfulness to the man, but the woman\'s anti-beautification is the top constraint of this render. ── FRAMING & SCALE ── Each portrait is a tight upper-body crop from roughly mid-chest up, minimal headroom, close portrait distance against a warm beige studio wall with a soft shadow gradient. Consistent crop scale and camera distance across all four. ── LIGHTING ── Directional soft side key light with gentle modeling shadows on one side of each face and along the neck/hand, warm and low-contrast — not flat frontal lighting. The key light must never wash out or smooth away the woman\'s real features — identity stays fully readable through the lighting. ── WARDROBE LOCK ── TOP ROW (both): the SAME oversized tailored blazer over a plain white tee — a coordinated his-and-hers set. BOTTOM ROW (both): the SAME white vintage band/photo-print t-shirt — a coordinated set. ── FRAME CONTENT ── TOP-LEFT (woman): oversized blazer over white tee, seated, head turned sharply to the side looking off-frame, calm expression, side key light. TOP-RIGHT (man): the same blazer over white tee, one open hand raised covering part of the face, head slightly bowed. The hand does NOT distort the facial features — keep Image 3 identity intact around the hand. BOTTOM-LEFT (woman): white band-print tee, facing straight toward the camera in a direct frontal head-on pose, calm neutral expression. This is the woman\'s identity-anchor frame — her frontal face here must match Image 2 as closely as possible, with her real, un-beautified features. BOTTOM-RIGHT (man): the same tee, head tilted fully back, eyes softly closed, chin up, relaxed low-angle pose, neck in soft shadow. Keep Image 3 bone structure recognizable. ── CONTINUITY ── Consistent facial identity, warm vintage tone, side lighting, camera distance, crop scale, and beige backdrop across all four prints. The woman is the same person in both left frames; the man the same in both right frames. Top row shares one blazer look, bottom row one printed-tee look. No duplicated people, no extra frames. ── STYLE ── Authentic vintage warm golden-cream film photography, visible fine film grain, faded low-contrast tonal range with lifted milky blacks and soft creamy blown highlights, warm honey/amber skin tones, muted desaturated yellow-green cast, soft directional studio lighting, natural candid expressions, analog imperfections and slight softness, realistic skin and hair texture. Four tightly packed individually-developed prints with slim even gutters, straight alignment, centered 2x2 composition on warm cream ground. Vertical hand-brushed matte-black \"사랑이 / 잘\" on the lower-right margin. ── AVOID ── Beautifying, idealizing, slimming, de-aging, enlarging eyes, narrowing the nose, sharpening the jaw, over-smoothing, or making the woman\'s face more symmetrical or prettier than Image 2 — this is the primary failure to avoid. Also: any face morphing or reinterpretation; generic idealized K-pop face; blending the two identities or mixing in a third person; loss of likeness under lighting or pose; flat frontal lighting; pure white or cool background; loose wide crops with excess headroom; mismatched outfits within a row; duplicated people or limbs; cool/neutral tone; warped or garbled \"사랑이 잘\" text; wide gaps between frames; extra frames or photo strips; added logos, dates, decorations, or carousel overlay. 4:5 (1080×1350), 8K,
```

**자주 생기는 문제**

| 증상 | 해결 |
|---|---|
| 얼굴이 예쁘게 미화돼요 | 프롬프트의 `ANTI-BEAUTIFICATION` 문단을 지우지 마세요. 원본 얼굴을 그대로 지키는 핵심 장치입니다. |
| 비율이 달라요 | `4:5 (1080×1350)` 세로 비율로 고정하세요. |
| '사랑이 잘' 글씨가 깨져요 | 세로 손글씨 타이포로 우측 하단에 배치되도록 강조하고, 다른 텍스트·로고는 넣지 마세요. |
| 얼굴이 뭉개져요 | 원본 얼굴 사진을 선명한 정면으로 바꿔 다시 시도하세요. |

### 결과 점검과 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| 여러 사진이 한 장에 합쳐짐 | 한 번에 여러 장 업로드 | 한 장씩 업로드 (앨범커버만 예외) |
| 장소명·문구가 엉뚱함 | 글씨를 AI가 사진을 보고 추측함 (일상 사진일수록 빗나감) | 프롬프트 끝에 장소·번호·연도·문구를 지정하거나, "도쿄 대신 요코하마로 바꿔줘"처럼 구체적으로 수정 요청 |
| 철자가 틀림 | 이미지 속 텍스트 생성 오류 | "철자만 고쳐줘"로 텍스트만 재수정 |
| 크레용 그림이 우표처럼 너무 작음 | Gemini에서 실행 시 톤 차이 | ChatGPT에서 실행하거나 "그림을 조금 더 크게 그려줘" |
| 배경이 바뀌거나 사라짐 (배경화면) | 배경 보존 문구 누락 | 밝은 버전에 `Preserve the entire original background exactly as-is` 문구가 있는지 확인 |
| 카드가 얼굴·손을 가림 (배경화면) | 카드 수를 늘림 | 밝은 버전은 4개가 안정적인 구도이니 그대로 유지 |
| 곡 제목이 틀리게 나옴 | 형식 깨짐 | '제목 — 아티스트' 형식 유지, 필요하면 앨범커버 이미지 첨부 |
| 원하는 결과와 거리가 멂 | AI 해석 차이, 도구·버전별 성능 차이 | 같은 프롬프트로 재생성하거나 해당 부분만 고쳐 재요청, 다른 사진으로 시도 |

## 활용 예시

**러버 스탬프 — 여행 기록 포스터**
- 입력: 프랑스 파리의 에펠탑 사진 + 프롬프트 ②
- 결과: 사진 하단에는 에펠탑의 실제 모습이, 상단에는 에펠탑 실루엣이 담긴 빈티지 스탬프와 함께 'Paris', 'Eiffel Tower', 'France', '2023' 등의 텍스트가 새겨진 포스터

**러버 스탬프 — 건축적 특징을 살린 디자인**
- 입력: 이탈리아 콜로세움의 측면 사진 + 프롬프트 ③
- 결과: 사진 좌측에는 콜로세움 원본 이미지가, 우측에는 콜로세움 외곽선과 'Rome', 'Colosseum', 'Ancient', 'Italy', '2022' 텍스트가 포함된 스탬프 디자인

**러버 스탬프 — 자연 풍경의 핵심 요소 강조**
- 입력: 스위스 알프스의 산악 지대 사진 + 프롬프트 ②
- 결과: 하단에는 알프스 풍경, 상단에는 산맥의 윤곽선과 'Alps', 'Switzerland', 'Nature', '2024' 텍스트가 담긴 스탬프 포스터

**크레용 그림일기 — 인물·반려동물 사진**
- 인물 사진은 얼굴 부담이 덜한 ② 버전(그림 위·사진 아래)으로 시도합니다. 반려동물·풍경·카페 사진은 ① 기본형으로 충분합니다.

**미니멀 포스터**
- 개인 사진 앨범: 여행지 풍경 사진 → 상단은 실제 풍경, 하단은 풍경의 핵심 요소를 추상화한 미니멀 포스터
- 프로젝트 포트폴리오: 디자인 작업물 이미지 → 원본 디자인의 색감과 형태를 살린 예술적인 포스터
- 소셜 미디어 콘텐츠: 인물 사진 → 인물의 특징을 살린 모던하고 감각적인 인물 포스터

**플레이리스트 배경화면**
- 개인 프로필 배경화면: 셀카 + 밝은 버전, 곡은 'Dynamite — BTS', 'Levitating — Dua Lipa' 등으로 변경
- 음악 추천 카드: 친구에게 곡을 추천할 때 어두운톤 버전, 곡은 'Blinding Lights — The Weeknd', 'Save Your Tears — The Weeknd' 등으로 변경
- 프로젝트·이벤트 홍보: 테마에 맞는 곡들을 카드로 넣어 시선을 끄는 홍보 이미지

**'사랑이 잘' 앨범커버**
- 커플 사진 두 장으로 기념일용 4컷 앨범커버를 만들어 SNS 프로필이나 선물로 씁니다.

## 💡 아이디어

- **개인 굿즈:** 결과 이미지로 엽서, 스티커, 에코백, 폰케이스, 머그컵을 만듭니다.
- **시리즈 컬렉션:** 러버 스탬프 포스터에 No. 번호를 이어 매겨 여행지별 필드노트 시리즈를 만듭니다.
- **디자인 소재:** 웹사이트 배너, 블로그·여행 기록 앱의 썸네일이나 삽화로 장소의 분위기를 살립니다.
- **온라인 갤러리:** 개인 웹사이트나 포트폴리오 플랫폼에 포스터를 모아 나만의 갤러리를 꾸밉니다.
- **인쇄·액자 연동:** 생성된 디자인을 바로 인쇄하고 액자로 만들어주는 서비스와 묶어 원스톱으로 제공합니다.
- **SNS 챌린지:** 특정 곡이나 아티스트를 주제로 각자 플레이리스트 배경화면을 만들어 공유하는 챌린지를 기획합니다.

## 주의사항

- **원본 보존 문구를 지우지 마세요.** 각 프롬프트의 원본 사진 보존 지시(redraw 금지, `Preserve ... exactly as-is`, `ANTI-BEAUTIFICATION`)가 품질의 핵심입니다. 빠지면 AI가 사진이나 얼굴을 임의로 다시 그립니다.
- **글씨는 AI 추측입니다.** 러버 스탬프의 장소명·번호·키워드·연도, 크레용의 영어 문구는 AI가 사진을 보고 짓기 때문에 매번 달라지고 틀릴 수 있습니다. 고정하려면 프롬프트 끝에 직접 지정합니다.
- **도구별 차이:** 같은 프롬프트라도 AI 도구와 버전에 따라 결과가 다릅니다. 크레용 스타일은 Gemini에서 그림이 작게 나오는 등 톤이 달라지며, 예시 결과는 ChatGPT 기준입니다. 프롬프트가 길고 세밀해 AI가 의도와 다르게 해석할 수 있으니 여러 번 시도할 각오를 합니다.
- **저작권·초상권:** 원본 사진의 저작권을 확인하고, AI 생성물을 상업적으로 쓸 때는 도구 정책을 확인합니다. 앨범커버는 실제 앨범 디자인을 참고하므로 개인 소장·비상업 용도로 쓰고, 다른 사람의 얼굴 사진은 당사자 동의를 받아 사용합니다.

## 출처

- [https://app.notion.com/p/3cb0cb665b9a80a8948eedf3973f0831?source=copy_link](https://app.notion.com/p/3cb0cb665b9a80a8948eedf3973f0831?source=copy_link)
- [https://fieldby.notion.site/3c9d730b395381d192fed44b806737b6?pvs=149](https://fieldby.notion.site/3c9d730b395381d192fed44b806737b6?pvs=149)
- [https://app.notion.com/p/3c004aeefb608081ac9bd7814df90e34?source=copy_link](https://app.notion.com/p/3c004aeefb608081ac9bd7814df90e34?source=copy_link)
- [https://fieldby.notion.site/3e3d730b39538163b41bcb0d72663ef1?pvs=149](https://fieldby.notion.site/3e3d730b39538163b41bcb0d72663ef1?pvs=149)
- [https://fieldby.notion.site/3a6d730b39538184855cde596254cee5?pvs=149](https://fieldby.notion.site/3a6d730b39538184855cde596254cee5?pvs=149)
- [https://fieldby.notion.site/3b8d730b3953812c868aca0d22bb954b?pvs=149](https://fieldby.notion.site/3b8d730b3953812c868aca0d22bb954b?pvs=149)
