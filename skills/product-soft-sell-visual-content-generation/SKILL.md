---
name: product-soft-sell-visual-content-generation
description: 제품·룩북·매장 사진 한 장을 **ChatGPT(GPT-4o 이미지 생성)** 에 올리고 복붙 프롬프트를 넣으면, 원본은 그대로 둔 채 흰 손글씨 메모·화살표·체크리스트로 구매 이유를 얹은 소프트셀 브랜드 홍보 이미지를 10초 만에 만듭니다. 무료 플랜 가능.
origin: content-lab
grade: S
difficulty: 초급
category: 콘텐츠
ai_tools: ["GPT", "Gemini"]
sources:
  - https://jasper-tartan-fcc.notion.site/GPT2-35a00b4db8dc808599bbf0d4a16a627e?pvs=149
---

# 손글씨 브랜드 홍보 사진 만들기

💡 사진은 **한 픽셀도 건드리지 않고**, 그 위에 사장님이 직접 쓴 것 같은 **흰 손글씨 메모**로 "왜 사야 하는지"를 얹습니다. 할인 배너가 아니라 **신뢰와 스토리**로 파는 소프트셀 콘텐츠입니다.

## 이게 뭔가요?

ChatGPT 의 이미지 생성(GPT-4o/DALL-E)에 사진 한 장을 업로드하고, 미리 짜인 프롬프트를 그대로 붙여넣기만 하면 손글씨 메모와 체크리스트가 합성된 브랜드 홍보 사진이 완성되는 방법입니다. 자영업자·셀러가 매일 인스타그램에 올릴 콘텐츠를 10초 만에 만드는 것이 목표입니다.

- **쓰는 곳**: 매장 룩북, 메뉴 홍보, 카페 매장 홍보(빈티지 결), 제품 솔직 후기
- **잘 맞는 업종**: 화장품, 뷰티, 핸드메이드, 라이프스타일 제품, 소규모 의류 브랜드
- **언제 유용한가**: 제품 판매 중 한 장으로 끝나는 후기 콘텐츠가 필요할 때, 장문 리뷰 대신 핵심 포인트만 강조하고 싶을 때

### 감성형 손글씨와 무엇이 다른가

같은 '손글씨 합성'이라도 결이 다릅니다. 일상 사진에 감정과 맥락을 얹는 감성형 콘텐츠는 공감을 사고, 이 방법처럼 **이유와 설명**을 얹는 브랜드형 콘텐츠는 구매 이유를 보여줍니다.

| 감성형 (일상) | 브랜드형 (이 방법) |
|---|---|
| "오늘 기분 좋은 코디 ♡" | "여름 데일리 추천 / 사이즈 FREE / 신상 ♡" |
| 공감을 산다 | 구매 이유를 보여준다 |

### 브랜드 사진에 메모를 넣을 때 지킬 3가지 원칙

1. **메인 제품은 가리지 않기**: 손글씨가 아무리 좋아도 상품이 안 보이면 의미 없습니다. 제품·메뉴·룩이 항상 주인공이고 손글씨는 보조 역할입니다.
2. **문장은 짧게, 포인트는 선명하게**: 긴 설명은 잘 읽히지 않습니다. 5~14자 안에서 핵심만 전달합니다. "이래서 좋아요"보다 "데일리로 강추 ♡" 같은 짧은 결이 효과적입니다.
3. **예쁜 말보다 추천하는 이유를 적기**: "오늘 기분 좋은 코디 ♡" 대신 "여름 데일리 추천 / 사이즈 FREE / 신상 ♡"처럼 구체적인 구매 이유를 제시합니다.

### 도구와 비용

- 💰 유료 불필요 — ChatGPT 무료 플랜에서도 이미지 업로드+생성이 가능합니다(생성 횟수 제한 있음).
- ✅ 무료 대안: Gemini 이미지 생성으로도 시도할 수 있지만, 한글 손글씨 렌더링 정확도는 GPT 쪽이 더 안정적입니다.

## 따라하기

### 공통 사용법

1. 챗GPT에 사진 1장 업로드
2. 만들고 싶은 카테고리 프롬프트 복사
3. 챗GPT에 그대로 붙여넣기
4. 대기 → 완성

### 어떤 프롬프트를 쓰나

| 사진 종류 | 쓸 프롬프트 | 결과물의 느낌 |
|---|---|---|
| 제품 단독 사진 (화장품·핸드메이드·생활용품) | A. 제품 솔직 후기 | 사장님이 제품 옆에 남긴 손글씨 노트 |
| 모델 착용 사진 (의류·잡화) | B. 매장 룩북 (OOTD) | 작은 디자이너의 룩북 한 페이지 + 폴라로이드 디테일 컷 |
| 메뉴·카페 매장 사진 | A 를 응용 (아래 "응용" 참고) | 사장님 추천 메모가 붙은 매장 홍보 |

두 프롬프트 모두 브랜드명 자리에 placeholder 인 `리더인` / `리더인 스튜디오` 를 씁니다. 실제 사용할 때는 프롬프트 안의 이 이름을 **내 가게 이름으로 모두 바꿔** 붙여넣으세요.

### A. 제품 솔직 후기 프롬프트

```
[CRITICAL BASE RULES - DO NOT VIOLATE]
- Preserve the original product photo EXACTLY as it is.
- Do NOT crop, change aspect ratio, or alter composition.
- Do NOT change brightness, color tone, contrast, or saturation.
- Maintain original resolution and sharpness.
- Keep all visible elements identical: product, packaging, background, props.
- Do NOT add new products or change details.

[BRAND PURPOSE]
This is a WARM, SOFT-SELL PRODUCT PROMOTION for small brand owners or sellers. The owner shares their product with personal pride — like recommending a favorite to a friend. NOT a Smart Store discount banner. NOT a casual user review. The feel: a small brand owner's handwritten note next to their product. The goal: Make viewers think "이 브랜드 감성 좋다" → "한번 써보고 싶다" through TRUST and STORYTELLING, not through aggressive SALE messaging.

[BRAND NAME REFERENCE]
Use "리더인" as the placeholder brand name throughout. For example: "리더인 코스메틱" / "리더인 라이프" / just "리더인" (Use exactly: 리더인 — do NOT invent other names)

[CONCEPT]
Soft brand storytelling + product highlights + warm reasons to try + gentle purchase guide. Should feel like a small brand owner's lookbook page, NOT a Smart Store promotion image.

[OVERLAY STYLE]
Add white hand-drawn doodles and handwritten Korean notes. The mood: TRUSTWORTHY + WARM + PERSONAL. Like a brand owner introducing their product to a friend.

[VISUAL ELEMENTS]
- Lightly trace key product edges (cap, label, body)
- 5~7 thin arrows pointing to features
- Highlight ONE main USP with soft DOTTED CIRCLE
- Soft ★ ratings (use sparingly, max 3 places)
- Gentle ♡ accents

[KOREAN HANDWRITTEN TEXT]
- Use ONLY natural Korean
- Total: 9~12 short annotations
- Each annotation: 4~14 Korean characters
- Tone: warm, sincere, brand-storytelling

[ANNOTATION CATEGORIES]
1️⃣ ITEM NAME (top, soft handwriting):
- "리더인 — 데일리 세럼"
- "리더인 코스메틱"
- "리더인 — 오늘의 추천"
- "리더인 라이프 — 신제품"
→ Place clearly at top, NO bold sticker

2️⃣ KEY FEATURES (with arrows, warm tone):
- "민감성 피부 OK"
- "EWG 그린 등급"
- "비건 인증 ♡"
- "한국 제조"
- "올인원 케어"
- "끈적임 없어요"
- "데일리로 부담 없이"

3️⃣ STORY / BRAND TOUCH (warm, personal):
- "직접 써보고 만든 제품"
- "사장님이 자신있는 ★"
- "오랜 연구 끝에"
- "정성 담은 한 병"
- "꾸준히 사랑받는 ♡"

4️⃣ NEW / RESTOCK ANNOUNCEMENT (subtle, max 1):
Choose AT MOST 1:
- "이번 주 신제품 ♡"
- "재입고 안내"
- "기다려주신 분들께"
- "리뷰로 사랑받은 ★"
- "새로운 라인 출시"
→ Soft handwriting style, NOT bold red sticker

5️⃣ TARGET / WHO IT'S FOR:
- "20-30대 데일리 케어"
- "민감성 피부 추천"
- "선물용으로도 좋아요"
- "초보자도 쉽게"
- "이런 분들께 추천해요"

6️⃣ STAR RATINGS (sparingly, max 3):
- "사용감 ★★★★★"
- "디자인 ★★★★☆"
- "재구매율 ★★★★★"
→ Use as small accents, not as main marketing tool

7️⃣ TRUST INDICATORS (soft, warm):
- "리뷰 천 개 넘어요 ♡"
- "재구매율 높아요 ★"
- "사랑받는 베스트"
→ Use AT MOST 1, in soft handwriting

8️⃣ GENTLE PURCHASE GUIDE (bottom area):
- "💬 DM으로 문의 환영"
- "📦 스마트스토어: 리더인"
- "🔗 프로필 링크"
→ Soft icons, no 🛒💰🔥

[CHECKBOX BOX - Right side, soft design]
Title: "추천 포인트"
Example A (Standard):
♡ 사용감 부드러움
♡ 디자인 만족
♡ 데일리로 OK
♡ 재구매 의향 ★
Example B (Brand-trust focus):
♡ 사장님 자신 있는 ★
♡ 리뷰 사랑받는
♡ 민감성 OK
♡ 선물용으로도 ♡
Example C (With seasonal):
♡ 이번 주 신제품
♡ 사장님 추천 ★
♡ 데일리 케어
♡ DM 문의 환영

[MAIN VERDICT - Inside soft dotted box]
Choose ONE warm message:
```

> 원문 프롬프트는 `[MAIN VERDICT]` 의 "Choose ONE warm message:" 에서 끝납니다. 붙여넣을 때 이 줄 아래에 점선 박스에 넣고 싶은 따뜻한 한 줄 메시지(4~14자)를 직접 한두 개 적어 주면 결과가 더 안정적입니다. 적지 않으면 GPT 가 위 카테고리 문구를 참고해 스스로 고릅니다.

**결과를 보고 고칠 때**

- 체크박스는 Example A(기본) / B(브랜드 신뢰) / C(시즌) 중 하나만 남기면 의도가 더 선명해집니다.
- 제품 특성이 다르면 2️⃣ KEY FEATURES 목록을 내 제품의 실제 특징으로 바꿉니다. 사실이 아닌 인증·등급 문구(예: "EWG 그린 등급", "비건 인증 ♡")는 반드시 지웁니다.

### B. 매장 룩북 프롬프트 (OOTD — 쇼핑몰 운영자)

```
[CRITICAL BASE RULES - DO NOT VIOLATE]
- Preserve the original photo EXACTLY as it is.
- Do NOT crop, change aspect ratio, or alter composition.
- Do NOT change brightness, color tone, contrast, or saturation.
- Maintain original resolution and sharpness.
- Keep all visible elements identical: person, outfit, background, lighting.
- Do NOT add new people, objects, or background elements.

[BRAND PURPOSE]
This is a SOFT-SELL FASHION LOOKBOOK for small clothing brand owners. The owner shares the outfit with personal recommendation tone — like a friend showing you what they made. NOT aggressive ad-style. NOT a personal diary either. The feel: a small fashion brand owner's hand-curated lookbook content. The goal: Make viewers think "이 옷 어디서 사지?" through TRUST and STYLE, not through aggressive sale messaging.

[BRAND NAME REFERENCE]
Use "리더인 스튜디오" as the placeholder shop name throughout the content. (Use exactly: 리더인 스튜디오 — do NOT invent other names like "어반시크 스튜디오")

[CONCEPT]
Soft fashion lookbook + personal styling notes + warm sizing/fit guide + gentle CTA. Should feel like flipping through a small designer's lookbook, NOT a discount flyer or aggressive ad.

[COMPOSITION - CORE STRUCTURE]
1) MAIN SHOT: Person stays as central focus
2) DETAIL FRAMES: 3 to 4 zoomed-in detail crops as polaroid-style
- Each frame: garment detail with handwritten note about FIT/MATERIAL/STYLING
- Slightly tilted (3~10 degrees), white borders
3) CONNECTION LINES: Thin dashed lines or curved arrows from main shot to frames
4) GENTLE CTA: Bottom area with soft purchase guide

[PEN STYLE]
- White gel pen handwriting
- Slightly rough, hand-drawn feel
- Variable line thickness, no perfectly straight lines
- Korean characters MUST be sharp and readable

[KOREAN HANDWRITTEN TEXT]
- Use ONLY natural Korean (no English, no Japanese)
- Total: 12~15 short annotations
- Each line: 4~14 Korean characters
- Tone: warm, personal, like a small brand owner sharing a favorite piece

[ANNOTATION CATEGORIES]
1️⃣ ITEM NAME (top of each detail frame, soft tag style):
- "스트라이프 니트 티"
- "코튼 숏팬츠"
- "라탄 토트백"
- "린넨 셔츠"
- "오버핏 카디건"
→ Just the item name. No price tag, no SALE markers.

2️⃣ MATERIAL / FIT NOTES (with arrows, warm and informative):
- "여름용 얇은 니트"
- "통기성 좋은 면 100%"
- "비침 없는 두께감"
- "부드러운 소재감 ♡"
- "여유있는 핏"
- "키 큰 분도 OK"

3️⃣ SIZING GUIDE (near body shot, gentle):
- "모델 키 165 / S 착용"
- "정사이즈 추천"
- "55-77 사이즈 가능"
- "한 사이즈 업도 좋아요"

4️⃣ STYLING / WHO IT'S FOR (warm recommendation):
- "데일리룩으로 좋아요"
- "오피스룩에도 OK"
- "여름 출근룩 추천"
- "가벼운 외출에 ♡"
- "이런 분들께 추천해요"
```

> 원문 프롬프트는 4️⃣ 카테고리에서 끝납니다. `[COMPOSITION]` 의 4) GENTLE CTA 를 확실히 넣고 싶다면, A 프롬프트의 8️⃣ GENTLE PURCHASE GUIDE 블록(DM 문의·스마트스토어·프로필 링크)을 이 프롬프트 끝에 이어 붙이세요. 이때 `리더인` 은 `리더인 스튜디오`(또는 내 가게 이름)로 맞춥니다.

**결과를 보고 고칠 때**

- 3️⃣ SIZING GUIDE 의 모델 키·착용 사이즈는 실제 촬영 정보로 바꿉니다. 틀린 사이즈 정보는 반품·문의로 돌아옵니다.
- 디테일 프레임이 인물을 가리면 "Place detail frames in empty background areas, never over the person" 같은 한 줄을 덧붙여 다시 요청합니다.

### 응용: 메뉴·카페 매장 사진

메뉴·카페 매장 홍보용 전용 프롬프트는 이 문서에 실려 있지 않습니다. A 프롬프트를 바탕으로 다음만 바꿔 쓰면 같은 결을 낼 수 있습니다.

1. `[CRITICAL BASE RULES]` 의 `product, packaging, background, props` 를 사진에 실제로 있는 요소(메뉴, 그릇, 매장 인테리어 등)로 바꿉니다.
2. `[ANNOTATION CATEGORIES]` 의 화장품 문구를 "사장님 추천", "오늘의 추천 메뉴 ♡", "신선한 재료 사용" 같은 매장 문구로 바꿉니다.
3. 빈티지 결을 원하면 `[OVERLAY STYLE]` 의 분위기 설명에 원하는 무드를 덧붙입니다.

## 활용 예시

- **제품 후기**: 고객이 올린 제품 사진에 "정말 만족해요", "민감성 피부에도 순해요 ♡" 같은 손글씨 후기를 더해 신뢰도를 높입니다.
- **룩북**: 모델 착용 사진에 상품명, 소재, 사이즈, 코디 추천 이유를 손글씨로 넣어 쇼핑몰 룩북 콘텐츠를 만듭니다.
- **카페 메뉴**: 매장·메뉴 사진에 "사장님 추천", "오늘의 추천 메뉴 ♡", "신선한 재료 사용" 등의 문구를 넣어 홍보 효과를 높입니다.
- **핸드메이드 제품**: 만든 사람의 손길이 느껴지는 사진에 "정성 담아 만들었어요", "세상에 하나뿐인 ♡" 등을 더해 감성적인 스토리텔링을 강화합니다.
- **리테일 숍**: 매장 전경이나 디스플레이 사진에 "오랜 연구 끝에", "리뷰 천 개 넘어요 ♡" 같은 문구로 브랜드 신뢰와 고객 경험을 강조합니다.

## 💡 아이디어

- **시즌별 프로모션**: "이번 주 신제품 ♡", "여름맞이 특가", "가을 신상 입고" 등 시즌 문구로 최신성을 강조합니다.
- **사용자 참여 유도**: "DM으로 문의 환영", "프로필 링크 클릭", "궁금한 점은 댓글로!" 같은 CTA 로 고객과의 소통 창구를 엽니다.
- **재입고 알림**: "재입고 완료!", "기다려주신 분들께"처럼 품절됐던 인기 상품의 재입고 소식을 알려 구매 전환을 높입니다.
- **타깃 맞춤형 추천**: "2030 데일리 케어", "민감성 피부 추천", "초보자도 쉽게" 등 대상을 명시해 구매 결정을 돕습니다.

## 주의사항

- **원본 사진의 저작권**: 원본 사진의 저작권과 초상권 침해 여부를 반드시 확인합니다. 고객이 올린 사진은 사용 허락을 받은 뒤 씁니다.
- **기본 규칙 유지**: 원하는 결과를 얻으려면 프롬프트 지시를 정확히 따르게 하는 것이 중요합니다. 특히 `[CRITICAL BASE RULES - DO NOT VIOLATE]` 부분은 빼거나 줄이지 않습니다. 이 블록이 원본 사진의 구도·색감 보존을 담당합니다.
- **정보 과부하 방지**: 텍스트나 그래픽이 너무 많으면 오히려 가독성이 떨어집니다. 프롬프트가 정한 개수(후기 9~12개, 룩북 12~15개)와 4~14자 길이를 넘기지 않습니다.
- **결과물 검토**: AI 결과물은 항상 완벽하지 않습니다. 한글 오탈자, 상품을 가린 메모, 바뀐 색감이 없는지 확인하고 필요하면 다시 생성합니다.
- **사실만 적기**: 예시 문구 속 인증·리뷰 수·재구매율 같은 표현은 placeholder 입니다. 내 제품에 해당하지 않는 문구가 결과물에 남지 않게 합니다.

## 출처

- [https://jasper-tartan-fcc.notion.site/GPT2-35a00b4db8dc808599bbf0d4a16a627e?pvs=149](https://jasper-tartan-fcc.notion.site/GPT2-35a00b4db8dc808599bbf0d4a16a627e?pvs=149)
