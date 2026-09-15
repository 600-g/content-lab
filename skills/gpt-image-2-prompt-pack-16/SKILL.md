---
name: gpt-image-2-prompt-pack-16
description: 이 스킬은 **GPT 이미지 2**(GPT2)로 인테리어 비포&애프터, 웹툰 스토리보드, 럭셔리 제품샷 등 16가지 고퀄리티 이미지를 만드는 **복붙형 프롬프트 모음**입니다.
origin: content-lab
grade: S
difficulty: 중급
category: 프롬프트
ai_tools: ["GPT"]
sources:
  - https://jasper-tartan-fcc.notion.site/GPT2-16-35200b4db8dc8051b4bee15a9e1bddb1?pvs=149
---

# GPT2 프롬프트16선 복붙하기

💡 이 스킬은 **GPT 이미지 2**(GPT2)로 인테리어 비포&애프터, 웹툰 스토리보드, 럭셔리 제품샷 등 16가지 고퀄리티 이미지를 만드는 **복붙형 프롬프트 모음**입니다.

## 이게 뭔가요?

**GPT 이미지 2**(GPT2, GPT Image 2)로 디자이너 없이도 퀄리티 높은 이미지를 뽑아내기 위한 프롬프트 16개를 모은 자료입니다. 각 프롬프트마다 언제 쓰면 좋은지, 어떤 결과물이 나오는지, 어떤 콘텐츠에 활용할 수 있는지가 함께 정리되어 있어서 복붙해서 바로 쓰거나 본인 스타일에 맞게 단어만 바꿔 쓸 수 있습니다.

인테리어 비포&애프터, 시대 대비 이미지, 16컷 웹툰 스토리보드, 한글 인포그래픽, 이커머스 룩북, UGC 목업, 손금 분석, 인물 프로필, 바이럴 썸네일, 럭셔리 제품 광고, 브랜드 가이드, 감성 SNS 광고, 레트로 영화 포스터, 360도 파노라마, UI 목업, 3D 교육 도해까지 실무에서 바로 쓰이는 카테고리를 전부 커버합니다.

💰 유료 필요: ChatGPT (GPT Image 2 기능)
✅ 무료 대안: Gemini, Bing Image Creator, Leonardo AI 로 프롬프트 구조를 그대로 적용해 유사 결과물 생성 가능 (단, 한글 텍스트 렌더링 정확도는 GPT2 가 가장 우수)

## 따라하기

### 1. 3가지 핵심 치트키부터 이해하기

- **구체적인 렌즈·장비 명시**: 그냥 "사진"이 아니라 `85mm f/1.8`, `Phase One XF`, `Arri Alexa` 같은 전문 장비명을 넣으면 질감이 확 달라짐
- **빛의 성질 정의**: `Bright` 대신 `Volumetric fog`, `Rim lighting`, `Golden hour backlight` 처럼 빛의 방향과 질감을 구체적으로 지정
- **질감·디테일 극대화**: `Micro-pores`, `Subsurface scattering`, `Ray-traced reflections` 같은 용어로 디테일 수준을 끌어올림

### 2. 6단계 프롬프트 공식으로 구조 잡기

GPT2 는 키워드 나열보다 구조화된 설명문을 훨씬 잘 이해합니다. 아래 순서로 작성하세요.

| 단계 | 항목 | 예시 |
|---|---|---|
| 1 | Artifact (결과물 유형) | Poster, UI Mockup, Product Shot |
| 2 | Subject (주제) | Jazz musician, Wireless earbuds |
| 3 | Scene (장면/상황) | Rainy rooftop at dusk |
| 4 | Details (디테일) | Warm light from left |
| 5 | Constraints (제약 조건) | No extra text, Sharp focus |
| 6 | Style (스타일) | Kodak film style, 35mm |

### 3. 목적에 맞는 프롬프트 골라 복붙하기

#### ① 인테리어 비포&애프터
같은 카메라 앵글·같은 창문 위치를 유지한 채 좌우로 비교되는 시네마틱 비포&애프터 이미지. "이렇게 바뀌었어요" 자기계발 콘텐츠, 인테리어 정리정돈 챌린지 인증샷, 다이어트·습관 비포애프터에 활용.

```
A dramatic side-by-side interior design transformation. Left: a messy, dark attic room with old boxes, dust, tangled cables, and cold gray light. Right: the exact same room transformed into a bright minimalist Japandi home office with warm wood desk, paper lamp, plants, clean shelving, and soft sunlight through the same window. Same camera angle, same window position, perfectly matched perspective, cinematic before-and-after contrast, photorealistic, 8K. No angle mismatch, no unrealistic furniture scale.
```

#### ② 과거 vs 현재 (시대 대비)
한 장면에 두 시대를 정확히 같은 앵글로 비교하는 시각적 충격형 이미지. "예전엔 이랬는데 지금은" 카드뉴스, 성장 스토리, "10년 전 vs 지금" 비교 콘텐츠에 활용.

```
A perfect split-screen comparison of Seoul's Gwanghwamun, designed to shock viewers instantly. Left side: 1980s Seoul with grainy film stock, vintage cars, analog signs, muted colors, pedestrians in old clothing. Right side: 2080 Seoul with futuristic flying vehicles, holographic ads, sleek glass architecture, neon reflections, autonomous buses. Perfectly matching perspective, same horizon line, seamless center transition, extreme contrast between past and future, photorealistic, 8K. No mismatched angle, no distorted buildings.
```

#### ③ 웹툰 스토리보드 16컷
주인공 일관성이 유지되는 16컷 한국 웹툰. 한글 대사까지 깔끔하게 들어간 시네마틱 스토리보드. 인생 스토리 릴스·캐러셀, 공감형 콘텐츠, 브랜드 비하인드에 활용.

```
A professional 16-panel Korean webtoon storyboard with intense visual drama. Style: modern dark fantasy Korean action webtoon aesthetic. Clean line art, cinematic composition, cel-shaded coloring, highly detailed backgrounds, dramatic lighting, consistent protagonist design across all panels, clear panel separation, vertical webtoon format.
Create 16 clearly separated panels in one long vertical layout. The same protagonist must remain visually consistent throughout all panels: a young Korean male with wet black hair, sharp eyes, pale skin, dark modern clothing, standing in a rainy neon-lit Seoul street at night.
Important text rule:
Add short Korean dialogue inside clean speech bubbles only.
Use the exact Korean dialogue verbatim.
No extra random text. No unreadable text. No English text. No typo.
Keep all Korean text large, simple, and easy to read.
Panel 1: Wide establishing shot of a neon-lit Seoul street in heavy rain, wet asphalt reflections, empty ominous atmosphere. No dialogue.
Panel 2: Medium shot of the protagonist standing still in the rain, head lowered. Speech bubble: "또 시작인가."
Panel 3: Close-up of rain dripping from his face and hair. Speech bubble: "이번엔... 다르다."
Panel 4: Extreme close-up of the protagonist's eye beginning to glow blue. Small speech bubble: "뭐지?"
Panel 5: Close-up of his eye glowing intensely with blue energy. Speech bubble: "보인다."
Panel 6: His expression sharpens as he senses danger. Speech bubble: "뒤에 있어."
Panel 7: Wide shot of tall skyscrapers disappearing into the rain and darkness. No dialogue.
Panel 8: A mysterious giant shadow begins to loom behind the skyscrapers. Caption box: "그 순간, 도시가 숨을 멈췄다."
Panel 9: The shadow grows larger and more threatening, partially obscured by fog and rain. Speech bubble from protagonist: "말도 안 돼..."
Panel 10: The protagonist looks up in shock. Speech bubble: "저게 뭐야?"
Panel 11: Dramatic angle showing the scale difference between the small protagonist and the massive shadow. No dialogue.
Panel 12: Blue light gathers around the protagonist as tension rises. Speech bubble: "도망치면 끝이야."
Panel 13: Rain drops freeze mid-air around him in a supernatural moment. Caption box: "시간이 멈췄다."
Panel 14: Explosive lighting contrast, strong blue and black color clash, intense cinematic tension. Speech bubble: "이번엔 내가 막는다."
Panel 15: Close-up of the protagonist's shocked but determined face. Speech bubble: "끝까지 간다."
Panel 16: Final dramatic reveal — the giant shadow fully looming over Seoul, with the protagonist ready to confront it. Final caption box: "서울의 밤이 깨어났다."
High contrast, visually shocking, premium Korean webtoon quality, dynamic camera angles, rain effects, motion tension, atmospheric fog, explosive lighting, dramatic blue glow, scroll-stopping cinematic energy. No messy panels, no unreadable text, no inconsistent character face, no extra characters, no distorted anatomy, no random letters.
Use only 6 Korean dialogue bubbles total across the entire 16-panel webtoon. Korean text must be short, large, clean, and easy to read. Use the exact text verbatim.
```

#### ④ 디자인 인포그래픽 (한글 완벽 렌더링)
한글이 정확하게 박혀서 자료로 바로 쓸 수 있는 정보 포스터. 강의자료·워크북 표지, 보고서 요약, 전시 패널 디자인에 활용.

```
generate an image that only gpt image 2 can do, showing its full power. A scientific poster about black holes, written in 한국어로 작성. 고딕체로 작성. Premium, minimalist infographic poster style. Featuring multiple distinct 3D scientific illustrations of black holes, event horizons, and gravitational lensing. Clean Swiss design layout. Accurate Korean text throughout including section titles and explanations. Typography: Modern Korean Gothic sans-serif. Soft pastel color palette with deep space accents. 8K resolution.
```

#### ⑤ 이커머스 패션 룩북
원단 질감까지 살아있는 하이엔드 에디토리얼 패션 컷. 스마트스토어·인스타 마켓 메인 이미지, 의류 브랜드 룩북, 패션 콘텐츠 표지에 활용.

```
A high-end editorial fashion shot for a luxury brand. A model wearing a minimalist beige linen suit, captured on a Phase One XF camera. Soft, diffused top-down studio lighting. Sharp focus on fabric texture (linen weave). Minimalist, neutral grey background. 8k resolution, commercial grade.
```

#### ⑥ 리얼 UGC 목업
스마트폰으로 막 찍은 것처럼 보이는, 광고 같지 않은 광고. 인스타 스폰서 콘텐츠, 카페·식음료 협찬 콘텐츠, "내돈내산" 느낌의 후기 콘텐츠에 활용.

```
A candid, slightly shaky smartphone photo (UGC style) of a hand holding a sleek black coffee tumbler in a bustling sunlit park. Natural lens flare, intentional slight motion blur, authentic skin texture with micro-pores. Captured on iPhone 15 Pro, unedited raw look.
```

#### ⑦ 초정밀 손금/사주 분석용
손바닥의 잔주름까지 다 보이는 초고화질 매크로 사진. 운세·사주 콘텐츠 카드뉴스, 자기탐구 콘텐츠, 점성술·타로 릴스 표지에 활용.

```
Extreme macro photography of a human palm, top-down view. 100mm macro lens. Hyper-detailed skin texture, every fine line and crease is sharp and clear. Soft side-lighting to create depth in the palm lines. Scientific, clinical quality. Neutral color grading.
```

#### ⑧ 시네마틱 인물 프로필
영화 한 장면 같은 분위기의 전문가 인물 사진. 강사·전문가 프로필, 책 띠지·강의 페이지 표지, 링크드인·홈페이지 메인에 활용.

```
Cinematic close-up portrait of a tech founder. Lighting: 'Rembrandt lighting' with a warm rim light. Background: Blurred modern office with blue and amber bokeh. Shot on Arri Alexa, 50mm prime lens. Realistic skin imperfections, focused gaze. Moody, professional atmosphere.
```

#### ⑨ 바이럴 썸네일
한글 텍스트가 정확히 박힌, 시선을 강제로 멈추게 하는 썸네일. 유튜브 썸네일, 인스타 릴스 표지, 강의 후킹 영상 표지에 활용.

```
High-impact YouTube thumbnail for a tech review. A glowing, futuristic smartphone floating in the center with ray-traced reflections. Background: Dynamic speed lines and sparks. Bold, 3D extruded text overlay: '역대급 성능!' in vibrant yellow. High contrast, HDR.
```

#### ⑩ 럭셔리 제품 광고
조명과 질감으로 분위기를 압도하는 시네마틱 제품샷. 럭셔리 브랜드 광고, 제품 상세페이지 메인, 인스타 광고 캠페인에 활용.

```
A luxury perfume bottle placed on a wet, dark volcanic rock. Cinematic lighting with a single 'God ray' hitting the glass. Realistic water droplets with refractive properties. Deep shadows, moody emerald green color grading. 8k, Unreal Engine render style.
```

#### ⑪ 브랜드 가이드
로고·컬러팔레트·타이포·문구류가 깔끔하게 정리된 브랜드 시트. 신규 브랜드 런칭 자료, 브랜드 제안서 표지, 포트폴리오 정리에 활용.

```
A comprehensive brand identity showcase for a tech startup named 'NEO'. Layout: A clean grid showing a minimalist logo, a specific color palette (Deep Navy, Electric Lime), and typography samples. Realistic stationery mockups (business cards, letterhead) arranged neatly.
```

#### ⑫ 감성 SNS 광고
물·꽃잎·자연광이 어우러진 몽환적 분위기의 광고 컷. 인스타 피드 광고, 뷰티 브랜드 콘텐츠, 웰니스·라이프스타일 콘텐츠에 활용.

```
A dreamy, soft-focus Instagram ad for a premium skincare serum. A glass bottle partially submerged in clear, rippling water with floating white flower petals. Lighting: Soft morning sunlight through a window (caustics effect). Text: 'PURE GLOW' in elegant serif.
```

#### ⑬ 레트로 영화 포스터
80년대 영화 포스터 감성의 그라피티 같은 작품. 90s·2000s 콘텐츠 시리즈, 레트로 카드뉴스 표지, 향수 자극 콘텐츠에 활용.

```
Retro 80s synthwave movie poster. Title: 'CYBER CITY' in glowing neon chrome. Illustration style: Hand-painted airbrush look. Vibrant purple and cyan color palette. Grainy VHS texture, cinematic composition with a lone hero overlooking a futuristic metropolis.
```

#### ⑭ 360도 파노라마
이음새 없이 매끄럽게 펼쳐진 광활한 파노라마 이미지. 여행·공간 콘텐츠, 가상 투어·메타버스 콘텐츠, 공간 브랜딩 자료에 활용.

```
An equirectangular 360-degree panorama of a futuristic Mars colony interior. Seamless stitching, high-tech glass domes showing the red planet outside. Soft interior LED lighting. Photorealistic, 8k, immersive perspective.
```

#### ⑮ 고퀄 UI 목업
실제 출시된 앱 같은 고퀄리티 UI 디자인 시안. 앱 런칭 페이지, 서비스 소개 자료, IR·투자 제안서에 활용.

```
A high-fidelity UI/UX mockup of a fitness app displayed on a bezel-less smartphone. Style: Glassmorphism with frosted glass effects. Vibrant gradient backgrounds, clean data visualizations (rings and charts). Realistic hand holding the phone in a lifestyle setting.
```

#### ⑯ 3D 교육용 도해
교과서급 퀄리티의 3D 단면도. 한글·영문 라벨까지 정확히 들어감. 교육 콘텐츠·강의자료, 의학·과학 정보 콘텐츠, 전자책 내지 일러스트에 활용.

```
A detailed 3D medical illustration of the human heart. Cross-section view with translucent layers showing internal valves. Labeled in clean English and Korean: 'Left Atrium (좌심방)', 'Aorta (대동맥)'. Studio lighting on a clean white background. Textbook quality.
```

## 활용 예시

- 인테리어 정리정돈 챌린지를 진행 중이라면 ① 프롬프트의 Left/Right 문구를 실제 방 상태로 바꿔 넣으면 → 같은 앵글의 비포&애프터 카드뉴스가 바로 나옴
- 강의 오프닝 릴스를 만들 때 ③ 웹툰 스토리보드 프롬프트에서 대사만 본인 스토리로 교체하면 → 16컷 한글 대사 웹툰이 한 번에 생성됨
- 스마트스토어 메인 이미지가 필요할 때 ⑤ 룩북 프롬프트의 의상·배경 색만 바꾸면 → 커머셜급 패션 컷을 별도 촬영 없이 확보 가능

## 주의사항

- **한글 텍스트 깨짐 방지**: 큰따옴표로 감싸고 `verbatim`(글자 그대로) 키워드를 붙일 것. 예: `Text: "역대급 성능!" verbatim`
- **부정 프롬프트**: 원치 않는 요소는 `No [요소]` 형식으로 명확히 제외. 예: `No watermarks`, `No distorted hands`, `No extra text`
- **인물 일관성 유지**: 연속으로 같은 인물을 만들 땐 `Keep the character's facial features identical to the previous image` 추가
- **결과물 수정 요청**: 사진작가에게 말하듯 구체적으로. 예: `Make the lighting more dramatic`, `Change the camera angle to low-angle`, `Add more contrast to the shadows`
- **이미지 참조 활용**: 기존 이미지를 업로드한 뒤 `이 이미지의 스타일을 유지하면서 [새로운 주제]를 그려줘` 형태로 요청

## 출처

[GPT2 이미지 프롬프트 16선](https://jasper-tartan-fcc.notion.site/GPT2-16-35200b4db8dc8051b4bee15a9e1bddb1?pvs=149)

## 출처

- [https://jasper-tartan-fcc.notion.site/GPT2-16-35200b4db8dc8051b4bee15a9e1bddb1?pvs=149](https://jasper-tartan-fcc.notion.site/GPT2-16-35200b4db8dc8051b4bee15a9e1bddb1?pvs=149)
