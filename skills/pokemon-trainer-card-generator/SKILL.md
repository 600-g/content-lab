---
name: pokemon-trainer-card-generator
description: 인물 사진 한 장을 **ChatGPT** 이미지 생성에 올리고 프롬프트를 붙여넣어 **포켓몬 TCG 트레이너 카드** 또는 **메이플스토리 공식 아바타** 스타일 캐릭터로 바꾸는 복붙 프롬프트 모음입니다.
origin: content-lab
grade: S
difficulty: 초급
category: 디자인
ai_tools: ["GPT"]
sources:
  - https://app.notion.com/p/Chat-gpt-37686293e5b180e38f81fd76f9fb4da9?source=copy_link
  - https://rural-slash-4e3.notion.site/st-solrr-aa-381c2a2c7a0a80d2be19e5cc6ea02fff?pvs=149
originals:
  - pokemon-trainer-card-generator | AI로 포켓몬 트레이너 카드 만들기 | https://app.notion.com/p/Chat-gpt-37686293e5b180e38f81fd76f9fb4da9?source=copy_link
  - maplestory-character-prompt | 사진으로 메이플스토리 캐릭터 생성 | https://rural-slash-4e3.notion.site/st-solrr-aa-381c2a2c7a0a80d2be19e5cc6ea02fff?pvs=149
---

# 사진으로 게임 캐릭터 만들기

💡 인물 사진에 프롬프트 하나만 붙이면 **포켓몬 트레이너 카드**나 **메이플스토리 아바타**가 됩니다. 두 프롬프트 모두 **얼굴·헤어·의상 색 같은 정체성은 지키고** 나머지는 게임 공식 스타일로 바꾸도록 설계되어 있습니다.

## 이게 뭔가요?

업로드한 인물 사진을 게임 공식 아트처럼 보이는 캐릭터 이미지로 바꾸는 이미지 생성 프롬프트 두 가지입니다. 단순히 그림체만 흉내 내는 것이 아니라, 각 게임의 레이아웃·비율·렌더링 방식까지 상세히 지시해 "실제 게임에서 나온 것 같은" 결과를 노립니다.

| | 포켓몬 트레이너 카드 | 메이플스토리 아바타 |
|---|---|---|
| 결과물 | 공식 포켓몬 TCG 풀아트 EX 카드 한 장 (트레이너 + 파트너 포켓몬 배틀 장면) | 1000 x 1000 흰 배경의 공식 메이플스토리 캐릭터 스프라이트, 한 번에 5장(`n=5`) |
| 그림체 | 애니메이션 셀 셰이딩, 시네마틱 조명, 홀로그램 포일 마감 | 큰 머리·작은 몸 비율, 크리스프한 정사각 픽셀, 니어리스트 네이버 확대 느낌 |
| 사진에서 가져가는 것 | 얼굴·머리·의상·비율·표정 전부 (애니 스타일화만 허용) | 헤어스타일·머리색·눈매·표정·대표 의상 색·액세서리 1~2개 (포즈·체형·배경은 무시) |
| 카드/화면 요소 | 이름, HP, 타입 아이콘, 희귀도, 기술·데미지, 약점·저항, 후퇴 비용, 카드 번호, 일러스트레이터, 능력치 패널 | 없음 (UI·로고·텍스트·이름표 금지) |
| 어울리는 사진 | 분위기가 뚜렷한 고화질 인물 사진 | 전신샷, 1~2명 (개·고양이가 보이면 펫도 생성) |
| 좋은 용도 | 수집품 느낌의 프로필 카드, 디지털 굿즈 | SNS 아바타, 팀원 캐릭터화, 선물 |

**공통 핵심은 정체성 보존**입니다. 포켓몬 프롬프트는 `Preserve identity exactly`, 메이플스토리 프롬프트는 "사진은 외모와 정체성을 이해하는 데만 쓰라"는 문장으로 이를 지시합니다. 이 부분이 무너지면 결과는 실패입니다.

- 💰 유료 필요: 이미지 입력(이미지 업로드)을 지원하는 고성능 이미지 생성 모델이 필요합니다. ChatGPT Plus(GPT-4o·GPT-4V)가 권장되며, 모델의 이해도가 높을수록 정체성 보존 규칙을 잘 따릅니다. Midjourney v6 이상도 포켓몬 카드에 권장되고, 이미지 입력이 되는 Claude 3 Opus/Sonnet도 언급됩니다.
- ✅ 무료 대안: Gemini, Leonardo AI, Bing Image Creator 등에서 시도해 볼 수 있으나, 정체성 보존과 세부 요구사항(카드 요소 전부, 메이플 특유의 픽셀 렌더링)을 동시에 만족시키기 어려워 여러 번의 반복과 세부 조정이 필요합니다.

메이플스토리 프롬프트는 영상 크리에이터 솔랄라(@solrr.aa)님이 ChatGPT로 직접 검증해 공유한 것입니다.

## 따라하기

### 공통 절차

1. 변환할 인물 사진을 준비합니다. 고화질에 인물 특징이 선명할수록 좋고, 메이플스토리는 가급적 **전신샷**을 씁니다.
2. **이미지 업로드를 지원하는** AI 챗봇(예: ChatGPT)에 접속합니다. 두 프롬프트 모두 "uploaded person / uploaded subject"를 전제로 하므로 텍스트만 입력하는 모드로는 작동하지 않습니다.
3. 사진을 업로드합니다.
4. 아래에서 원하는 프롬프트를 **하나의 코드 블록 전체 그대로** 복사해 붙여넣고 생성합니다.
5. 결과를 보고 필요한 부분만 고쳐 재생성합니다 (각 절의 "조정 포인트" 참고).

### 1. 포켓몬 트레이너 카드

인물을 공식 포켓몬 TCG 스타일의 트레이너 카드로 바꿉니다. HP·기술·능력치·희귀도 같은 실제 카드 UI 요소를 모두 넣어 수집품처럼 보이게 하고, 인물 분위기에 맞는 포켓몬 파트너와 함께 극적인 배틀 장면을 연출합니다.

```
Transform the uploaded person into an authentic Pokémon Trainer trading card in the official Pokémon TCG style.

Preserve identity exactly (face, hair, outfit, proportions, expression). Do not alter appearance beyond anime stylization.

Style:
Official Pokémon anime / TCG art, clean linework, bright cel shading, cinematic lighting, dynamic pose, colorful energy effects, highly detailed full-art EX card.

Artwork:
Trainer + matching Pokémon together in a dramatic battle scene with glowing aura, motion effects, and cinematic composition.

Card Elements:
Full TCG layout including name, HP, type icon, rarity, attacks with energy icons + damage, weakness/resistance, retreat cost, card number, illustrator credit, and stat panel (Bond, Strategy, Speed, etc.).

Pokémon Partner:
Automatically choose one that matches the subject’s vibe.
Examples: • calm / mysterious → Umbreon, Mewtwo • playful / energetic → Pikachu, Greninja • elegant / stylish → Gardevoir, Milotic • adventurous / bold → Dragonite, Arcanine

Finish:
Holographic foil, metallic highlights, glossy texture, ultra-rare collectible look.

Background:
Simple real-world setting (mall, street, concrete), softly blurred for depth.

Rules:
Single card composition, no splits, readable UI, trainer, and Pokémon together.
```

#### 프롬프트 구조 이해하기

프롬프트는 6가지 지시로 나뉩니다. 고칠 때는 해당 섹션만 건드립니다.

1. **주요 목표 설정**: `Transform the uploaded person...` — 가장 위에서 AI의 최종 목표를 정의합니다.
2. **정체성 보존**: `Preserve identity exactly...` — AI가 가장 주의해야 할 제약 조건입니다. 이 부분이 무너지면 실패합니다.
3. **스타일 정의**: `Style:` — 시각적 톤앤매너를 결정합니다. 'cel shading', 'cinematic lighting' 같은 구체적 용어가 중요합니다.
4. **구도 및 내용**: `Artwork:` 및 `Card Elements:` — 무엇을 어떻게 배치할지 지시합니다. 'Full TCG layout'이 핵심입니다.
5. **파트너 선택**: `Pokémon Partner:` — 인물 분위기에 맞는 포켓몬을 AI가 스스로 고르도록 유도하는 예시 목록입니다.
6. **마감 및 규칙**: `Finish:` 및 `Rules:` — 최종 질감·마감과 반드시 지킬 구도 규칙입니다.

#### 조정 포인트

- **분위기 강조:** `Pokémon Partner` 예시 중 원하는 줄(예: `• calm / mysterious → Umbreon, Mewtwo`)을 강조하고, 트레이너 분위기 설명에 '신비롭고 차분한 느낌'을 추가합니다.
- **파트너 고정:** `Pokémon Partner` 예시를 **'playful / energetic → Pikachu, Greninja'**로 고정하고 트레이너 포즈를 '역동적이고 활기찬 포즈'로 구체화합니다.
- **능력치 패널 테마:** `Card Elements`의 stat panel 항목을 바꿉니다. 예를 들어 '직장인 버전'이면 능력치 패널에 '업무 효율', '커뮤니케이션 스킬' 등을 넣도록 지시를 추가합니다.
- **규칙이 무시될 때:** 프롬프트가 길어 일부 규칙이 빠질 수 있습니다. 가장 중요한 두 규칙(1. 정체성 보존, 2. TCG 레이아웃)을 따로 한 번 더 강조해 재요청합니다.

### 2. 메이플스토리 아바타

인물을 실제 메이플스토리 게임 클라이언트의 커스터마이징 화면에서 만든 것 같은 공식 캐릭터로 바꿉니다. 팬아트나 일반 픽셀 일러스트, 애니 그림, 3D 렌더처럼 보이지 않도록 지시합니다.

프롬프트가 하는 일:

- **비율:** 아주 큰 머리, 작고 둥근 몸, 아주 짧은 다리. 실제 체형에 맞춰 다리를 늘리지 않습니다.
- **포즈:** 팔을 내린 기본 대기 자세, 35~40도 정도의 살짝 비스듬한 정면, 두 눈이 보이게.
- **의상:** 실제 옷을 그대로 베끼지 않고 메이플 장비 스타일로 번역합니다. 대표 색과 액세서리만 유지합니다.
- **얼굴·헤어:** 공식 얼굴 프리셋(큰 둥근 눈, 작은 코와 입)과 공식 헤어 아이템 같은 둥근 실루엣.
- **인원:** 사람 1명이면 캐릭터 1개, 2명이면 같은 비율로 2개. 개나 고양이가 실제로 보일 때만 펫을 만듭니다.
- **출력:** 1000 x 1000, 순백 배경, 전신, 캐릭터가 캔버스 높이의 약 72~75%. 바닥·그림자·배경·UI·로고·텍스트 없음. 끝의 `n=5`로 한 번에 5가지 느낌을 생성합니다.

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

#### 조정 포인트

- **닮지 않았을 때:** 전신이 나오고 얼굴·헤어가 선명한 사진으로 바꿉니다. 원본 사진의 품질이 유사성과 완성도에 가장 큰 영향을 줍니다.
- **여러 명 사진:** 두 명까지는 각각 별도 캐릭터로 만들어집니다. 사람들을 합치거나 캐릭터를 추가하지 말라는 지시가 이미 들어 있습니다.

## 활용 예시

**포켓몬 — 전문적인 프로필 카드**
- 입력: 위 포켓몬 프롬프트 전체 + 변환할 인물의 고화질 사진
- 기대 결과: 인물 특징을 유지한 채 포켓몬 트레이너가 되어 배틀하는 듯한, **홀로그램 질감**의 고해상도 카드. 카드 하단에는 가상의 'Bond'나 'Strategy' 같은 능력치 패널이 채워집니다.

**포켓몬 — 신비로운 분위기 강조**
- 입력: 전체 프롬프트 + `• calm / mysterious → Umbreon, Mewtwo` 강조, 트레이너 분위기에 '신비롭고 차분한 느낌' 추가
- 기대 결과: Umbreon이나 Mewtwo 같은 어둡고 신비로운 포켓몬이 등장하고, 조명과 색감이 차분하고 신비로운 톤으로 맞춰질 가능성이 높습니다.

**포켓몬 — 파트너 변경**
- 입력: 전체 프롬프트 + 파트너 예시를 'playful / energetic → Pikachu, Greninja'로 고정, 포즈를 '역동적이고 활기찬 포즈'로 구체화
- 기대 결과: 피카츄나 Greninja 같은 밝고 에너제틱한 포켓몬과 함께 배경·조명까지 활기찬 카드가 나올 확률이 높습니다.

**메이플스토리 — 친구 선물용 프로필**
- 입력: 친구의 개성이 담긴 전신 사진 + 메이플 프롬프트
- 결과: 친구의 특징을 살리면서 메이플스토리 특유의 아기자기한 매력이 더해진 캐릭터 이미지 5개

**메이플스토리 — SNS 아바타**
- 입력: 본인의 개성 있는 사진 + 메이플 프롬프트
- 결과: 실제 게임에 나올 법한 나만의 아바타. 개인 브랜드나 SNS 프로필 사진으로 씁니다.

**메이플스토리 — 팀원 캐릭터화**
- 입력: 팀원 각자의 사진 + 메이플 프롬프트
- 결과: 팀원 모두를 같은 스타일 캐릭터로 바꿔 팀 로고나 이벤트 홍보 일러스트로 활용합니다.

## 💡 아이디어

- **디지털 굿즈·커미션:** 사진을 받아 '디지털 포켓몬 카드 세트'나 메이플스토리 캐릭터를 만들어주는 커미션을 운영합니다. 포켓몬 카드는 '직장인 버전', '학생 버전'처럼 `Card Elements` 테마를 바꾼 상품으로 나눌 수 있습니다.
- **실물 굿즈:** 캐릭터 이미지로 폰케이스, 스티커, 티셔츠 등을 만듭니다.
- **챌린지 콘텐츠:** '나만의 메이플스토리 캐릭터 만들기 챌린지'처럼 팬덤을 겨냥한 참여형 콘텐츠로 바이럴과 커뮤니티 활성화를 노립니다.
- **세트 구성:** 같은 사진으로 포켓몬 카드와 메이플 아바타를 함께 만들어 한 사람의 '게임 캐릭터 세트'로 묶습니다.

## 주의사항

- **정체성 보존의 한계:** AI가 실제 사람의 미묘한 개성까지 100% 보존하기는 어렵습니다. 여러 번 시도할 각오를 하고, 선명한 사진을 씁니다.
- **이미지 입력 필수:** 두 프롬프트 모두 이미지 업로드가 되는 모델에서만 작동합니다. 텍스트만 입력하는 모델로는 인물 사진 기반 작업이 불가능합니다.
- **긴 프롬프트:** 프롬프트가 길고 복잡해 일부 모델은 규칙 일부를 무시할 수 있습니다. 가장 중요한 규칙을 별도로 강조해 재요청합니다.
- **도구별 차이:** 같은 프롬프트라도 AI 도구마다 이미지 해석 방식이 달라 퀄리티와 디테일이 다릅니다.
- **저작권·IP:** 포켓몬과 메이플스토리는 모두 상표·IP가 있는 게임입니다. 생성 이미지의 저작권과 상업적 이용 가능 여부는 사용하는 AI 도구의 정책과 각 IP의 사용 가이드라인을 반드시 확인합니다. 다른 사람의 사진은 당사자 동의를 받아 씁니다.

## 출처

- [https://app.notion.com/p/Chat-gpt-37686293e5b180e38f81fd76f9fb4da9?source=copy_link](https://app.notion.com/p/Chat-gpt-37686293e5b180e38f81fd76f9fb4da9?source=copy_link)
- [https://rural-slash-4e3.notion.site/st-solrr-aa-381c2a2c7a0a80d2be19e5cc6ea02fff?pvs=149](https://rural-slash-4e3.notion.site/st-solrr-aa-381c2a2c7a0a80d2be19e5cc6ea02fff?pvs=149)

### 합쳐진 원본 문서

이 문서는 아래 2개 문서를 하나로 합쳐 새로 정리한 것입니다.

| 원본 문서 | 원래 슬러그 | 원본 출처 |
|---|---|---|
| AI로 포켓몬 트레이너 카드 만들기 | `pokemon-trainer-card-generator` | [app.notion.com](https://app.notion.com/p/Chat-gpt-37686293e5b180e38f81fd76f9fb4da9?source=copy_link) |
| 사진으로 메이플스토리 캐릭터 생성 | `maplestory-character-prompt` | [rural-slash-4e3.notion.site](https://rural-slash-4e3.notion.site/st-solrr-aa-381c2a2c7a0a80d2be19e5cc6ea02fff?pvs=149) |
