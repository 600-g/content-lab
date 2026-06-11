---
name: pokemon-trainer-card-generator
description: AI를 활용하여 사용자를 **정통 포켓몬 트레이너 카드 스타일**로 변환하는 스킬입니다.
origin: content-lab
grade: A
difficulty: 중급
category: 디자인
ai_tools: ["GPT"]
sources:
  - https://app.notion.com/p/Chat-gpt-37686293e5b180e38f81fd76f9fb4da9?source=copy_link
---

# AI로 포켓몬 트레이너 카드 만들기

💡 AI를 활용하여 사용자를 **정통 포켓몬 트레이너 카드 스타일**로 변환하는 스킬입니다.

## 이게 뭔가요?
이 스킬은 사용자가 업로드한 인물 사진을 **공식 포켓몬 TCG(Trading Card Game) 스타일**의 트레이너 카드 이미지로 변환하는 전문적인 이미지 생성 프롬프트 가이드입니다. 단순히 스타일만 입히는 것이 아니라, 실제 포켓몬 카드에 들어가는 모든 **UI 요소(HP, 공격, 능력치, 희귀도 등)**를 포함하여 마치 실제 수집품처럼 보이게 만드는 것이 목표입니다.

핵심은 **'정체성 보존(Preserve identity exactly)'**입니다. 얼굴, 머리카락, 의상, 비율, 표정 등 원본 인물의 특징을 애니메이션 스타일로 변형시키면서도 원본의 개성을 잃지 않도록 지시하는 것이 가장 중요합니다. 또한, 트레이너와 그와 어울리는 포켓몬 파트너를 함께 배치하여 **극적인 배틀 장면**을 연출하는 것이 특징입니다.

이러한 수준의 결과물을 얻기 위해서는 단순한 텍스트 설명만으로는 부족하며, **구체적인 스타일 가이드(Style), 필수 포함 요소(Card Elements), 구도(Artwork)** 등을 매우 상세하게 지시해야 합니다. 따라서 고도화된 프롬프트 엔지니어링 능력이 요구됩니다.

💰 유료 필요: 최신 고성능 이미지 생성 AI (예: GPT-4o, Midjourney v6 이상)의 사용이 권장됩니다. 모델의 이해도가 높을수록 '정체성 보존' 규칙을 잘 따릅니다.
✅ 무료 대안: Gemini나 Leonardo AI 등에서 시도해 볼 수 있으나, **'정체성 보존'**과 **'모든 카드 요소 포함'**이라는 두 가지 까다로운 요구사항을 동시에 만족시키기 어려울 수 있습니다. 이 경우, 여러 번의 반복과 세부 조정이 필수적입니다.

## 따라하기
이 스킬은 하나의 거대한 **프롬프트 덩어리**로 구성되어 있으며, 이 전체 구조를 이미지 생성 AI에 입력하는 것이 핵심입니다. 아래는 원본에 명시된 모든 규칙과 요소를 빠짐없이 재현한 프롬프트입니다. 이 구조를 **하나의 코드 블록**으로 묶어 AI에 입력해야 합니다.

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

**주의:** 이 프롬프트는 **'업로드된 인물(uploaded person)'**을 전제로 하므로, 이미지 생성 AI가 **이미지 입력(Image Prompting)** 기능을 지원하는지 확인하고 사용해야 합니다. 텍스트만으로는 인물 사진을 기반으로 작업할 수 없습니다.

### 프롬프트 구성 요소 상세 분석
이 프롬프트는 크게 6가지 핵심 지시사항으로 나뉘어 있으며, 각 섹션의 중요도를 이해해야 합니다.

1. **주요 목표 설정**: `Transform the uploaded person...` (가장 상위에 위치하며, AI의 최종 목표를 정의합니다.)
2. **정체성 보존**: `Preserve identity exactly...` (AI가 가장 주의해야 할 제약 조건입니다. 이 부분이 무너지면 실패합니다.)
3. **스타일 정의**: `Style:` (시각적 톤앤매너를 결정합니다. 'cel shading', 'cinematic lighting' 등 구체적 용어 사용이 중요합니다.)
4. **구도 및 내용**: `Artwork:` 및 `Card Elements:` (무엇을, 어떻게 배치할지 구체적인 레이아웃을 지시합니다. 'Full TCG layout'가 핵심입니다.)
5. **파트너 선택**: `Pokémon Partner:` (사용자의 분위기에 맞는 포켓몬을 AI가 스스로 결정하도록 유도하는 예시 목록입니다.)
6. **마감 및 규칙**: `Finish:` 및 `Rules:` (최종적인 질감, 마감 처리, 그리고 반드시 지켜야 할 구도 규칙을 명시합니다.)

## 활용 예시
**시나리오 1: 전문적인 프로필 카드 생성**
*   **입력 (프롬프트)**: 위에서 복사한 전체 프롬프트와 함께, 변환하고자 하는 인물의 고화질 사진을 첨부합니다.
*   **기대 결과**: 인물의 특징을 유지하면서, 마치 포켓몬 트레이너가 되어 배틀하는 듯한, **홀로그램 질감**이 느껴지는 고해상도 카드 이미지가 생성됩니다. 카드 하단에는 가상의 'Bond'나 'Strategy' 같은 능력치 패널이 채워져 있을 것입니다.

**시나리오 2: 특정 분위기 강조 (예: 신비로운 분위기)**
*   **입력 (프롬프트)**: 전체 프롬프트를 사용하되, `Pokémon Partner` 부분의 예시를 수정합니다. (예: `• calm / mysterious → Umbreon, Mewtwo`를 강조하며, 트레이너의 분위기 설명에 '신비롭고 차분한 느낌'을 추가합니다.)
*   **기대 결과**: Umbreon이나 Mewtwo와 같은 어둡고 신비로운 포켓몬이 등장하며, 전체적인 조명과 색감이 차분하고 신비로운 톤으로 맞춰질 가능성이 높습니다.

**시나리오 3: 포켓몬 파트너 변경 시도**
*   **입력 (프롬프트)**: 전체 프롬프트를 사용하되, `Pokémon Partner` 섹션의 예시를 **'playful / energetic → Pikachu, Greninja'**로 고정하고, 트레이너의 포즈를 '역동적이고 활기찬 포즈'로 구체화합니다.
*   **기대 결과**: 피카츄나 그레니지 같은 밝고 에너제틱한 포켓몬과 함께, 배경과 조명까지 활기찬 느낌으로 연출된 카드가 나올 확률이 높습니다.

## 💡 아이디어
이 스킬은 단순한 이미지 생성을 넘어 **'개인화된 디지털 굿즈 제작'**이라는 측면에서 수익화가 가능합니다. 사용자들에게 자신의 사진을 받아 위 프롬프트를 통해 **'디지털 포켓몬 카드 세트'**를 제작해주고 유료로 판매할 수 있습니다. 또한, 특정 테마(예: '직장인 버전', '학생 버전')에 맞춰 프롬프트의 **'Card Elements'** 부분을 수정하여 판매하는 것도 좋은 아이디어가 될 수 있습니다. (예: '직장인 버전'이라면 능력치 패널에 '업무 효율', '커뮤니케이션 스킬' 등을 넣도록 지시 추가)

## 주의사항
1. **'정체성 보존'의 한계**: AI는 텍스트 기반의 지시를 따르지만, 실제 사람의 미묘한 개성까지 100% 보존하는 것은 현재 기술의 한계일 수 있습니다. 여러 번의 시도가 필요합니다.
2. **AI 도구의 선택**: 이 프롬프트는 **'이미지 입력(Image Prompting)'** 기능이 필수적이므로, 텍스트만 입력하는 AI 모델(예: 기본 ChatGPT)로는 작동하지 않습니다. 반드시 이미지 업로드 기능이 있는 모델을 사용해야 합니다.
3. **프롬프트 길이**: 프롬프트 자체가 매우 길고 복잡하기 때문에, 일부 AI 모델은 처리 과정에서 일부 규칙을 무시할 수 있습니다. 따라서 **가장 중요한 규칙(1. 정체성 보존, 2. TCG 레이아웃)**을 별도로 강조하는 것이 좋습니다.

## 출처
[Notion | Where teams and agents work together](https://app.notion.com/p/Chat-gpt-37686293e5b180e38f81fd76f9fb4da9?source=copy_link)

## 출처

- [https://app.notion.com/p/Chat-gpt-37686293e5b180e38f81fd76f9fb4da9?source=copy_link](https://app.notion.com/p/Chat-gpt-37686293e5b180e38f81fd76f9fb4da9?source=copy_link)
