---
name: higgsfield-mcp-claude-ad-generation
description: Claude에 Higgsfield MCP를 연결해 상품 페이지 URL이나 사진 한 장, 한국어 프롬프트 한 줄만으로 광고 영상·이미지를 자동 생성하는 스킬. Claude Code와 스케줄러를 더하면 매주 상품만 바꿔 넣는 완전 자동화 광고 생산 파이프라인으로 확장된다.
origin: content-lab
grade: S
difficulty: 중급
category: 콘텐츠
ai_tools: ["Claude", "Claude Code", "GPT"]
sources:
  - https://dour-tailor-5c6.notion.site/X-37861c2773b18071b093cde019e9f86e?pvs=149
  - https://aduaihiggsfield1.netlify.app/
---

# MCP로 광고영상 자동생성 (합병됨)

## 이게 뭔가요?

Claude는 원래 텍스트만 다루는 "두뇌"지만, **Higgsfield MCP** 를 연결하면 이미지·영상을 직접 만드는 "손"이 생깁니다. 브라우저를 강제로 조종하거나 외부 코드를 설치할 필요 없이, Higgsfield MCP가 Claude에게 생성 도구를 직접 쥐어줘서 모든 작업이 Claude 안에서 네이티브로 돌아갑니다.

주로 온라인 쇼핑몰(예: 올리브영)의 상품 페이지 URL을 입력하면, 해당 상품의 특징을 분석하고 스토리보드 생성, 영상 편집, 최종 결과물 저장까지 AI가 단계별로 수행합니다. 기술적인 프롬프트나 카메라 용어를 몰라도, 뭘 만들고 싶은지만 한국어로 말하면 Claude가 업종·분위기를 읽고 카메라 무빙·조명·디테일까지 알아서 설계한 뒤 Higgsfield에서 생성합니다.

**Claude Code(클코)는 선택**입니다. 일반 claude.ai 웹 채팅에서도 자동 생성 자체는 동일하게 작동하며, 결과물을 내 컴퓨터 폴더(예: `./campaign`)에 자동 저장까지 하고 싶을 때만 클코를 추가로 씁니다. 반면 Claude Desktop 앱에서 Custom Connector로 연결하고 "Cowork → Scheduled" 로 스케줄까지 걸면, 매주 URL 한 줄만 바꿔서 완전 자동화된 광고 생산 파이프라인을 운영할 수 있습니다.

💰 **유료 필요:** Higgsfield(이미지·영상 생성 시 크레딧 소모), Claude Desktop 앱 유료 플랜(Pro/Max/Team 이상, 브라우저 claude.ai는 스케줄·Custom Connector 불가), Claude Code로 자동 저장까지 쓰려면 Claude Max 권장, Chrome for Claude 연결(별도 설치)
✅ **무료 대안:** 일반 claude.ai 웹 채팅만으로도 생성 자체는 동일하게 작동합니다(로컬 폴더 자동 저장·스케줄 자동화만 빠집니다)

## 따라하기

### 1. Higgsfield MCP 연결하기

**방법 A — Higgsfield 안내 페이지에서 바로 연결 (신규, 더 간편)**
Higgsfield 시작 페이지의 "여기서 연결 시작하기" 버튼을 누르면 단계별 연결 방법이 나옵니다. 그대로 따라 하면 30초면 끝납니다. Claude Code·Codex를 쓴다면 안내 페이지의 'CLI' 탭이 더 편합니다.

**방법 B — Claude Desktop Custom Connector로 수동 연결 (스케줄 자동화를 쓰려면 이 방식 필요)**
1. Higgsfield.AI 웹사이트에 접속합니다.
2. MCP 링크를 복사합니다.
3. Claude Desktop 앱의 Connectors 메뉴로 이동합니다.
4. 새로운 Custom Connector를 추가합니다.
5. 복사한 Higgsfield MCP 링크를 붙여넣습니다. (릴스를 참고하며 연결하면 더욱 쉽습니다.)

**연결 확인하기**
새 채팅을 열고 아래처럼 물어봅니다.
```
지금 쓸 수 있는 Higgsfield 도구들 알려줘.
```
이미지·영상 생성 도구 목록이 뜨면 연결 성공입니다. Claude Code를 쓴다면 아래처럼도 확인할 수 있습니다.
```
mcp 힉스필드 연결됐는지 확인해
```
→ "힉스필드 MCP 연결 정상" 응답이 나오면 정상입니다.

### 2. 사용 가능한 도구 목록

- `generate_image` — 제품·광고 이미지, 아바타, 패션·UGC (Nano Banana Pro 등 모델 선택)
- `generate_video` — 영상 생성 (Seedance 2.0, Kling 3.0)
- `presets_show` — 이미지→영상 프리셋
- `show_characters` — 사진 5~20장으로 학습하는, 계속 재사용 가능한 디지털 캐릭터 (약 10분 소요)
- `show_marketing_studio` — 브랜드 키트·광고 레퍼런스·프리셋으로 광고 영상 제작
- `personal_clipper_create` — 긴 유튜브 영상을 숏폼 클립으로 자동 변환 (자막·비율·개수 선택)
- `virality_predictor` — 바이럴 가능성·후킹 강도·리텐션 예측
- `show_generations` / `show_medias` / `job_display` — 과거 생성물·미디어·작업 결과 확인

### 3. 기본 형태로 생성 요청하기

새 채팅을 열고 제품 사진이나 레퍼런스 이미지를 드래그해서 올린 뒤, 만들고 싶은 걸 한국어로 적습니다.
```
방금 올린 제품 사진으로 9:16 광고 영상 5개 만들어줘. 각각 다른 사람이 등장해서 자연스럽게 후기 말하는 느낌, 8초씩.
```
결과물은 채팅에서 바로 받을 수 있고, Claude Code를 쓴다면 끝에 한 줄만 붙이면 내 컴퓨터 폴더에 자동 저장됩니다.
```
./campaign 폴더에 저장해줘
```

### 4. 상품 URL만으로 완전 자동 생성 (마스터 프롬프트)

멀티샵(예: 올리브영) 제품 페이지의 URL을 복사한 뒤, 아래 프롬프트에서 `URL 부분`만 교체해 사용합니다.

```prompt
올리브영 제품 광고를 자동으로 만들어줘. 아래 순서대로 진행해.

[1단계] Seedance 2.0 프롬프트 작성법 웹 조사
"Seedance 2.0 prompt guide" 웹 검색
6단계 공식(Subject + Action + Camera + Style + Timeline), 카메라 무브먼트 종류, 금지어(constraints) 정리
조사 결과를 영상 프롬프트에 반영할 것

[2단계] 제품 정보 수집
이 URL을 Chrome으로 접속: (여기에 멀티샵 URL 붙여넣기)
핵심 성분, 효능, 컨셉 추출, 주의점: 제품을 그대로 사용하는게 아닌 브랜드 분위기만 참고할것

[3단계] 광고 씬 이미지 생성
GPT Image 2로 광고 씬 이미지 '스토리보드 생성' - 총 9컷의 이미지 생성
9:16 비율, 청량하고 수분감 있는 컨셉(여긴 브랜드에 따라 변경하시면 됩니다!)
제품샷 / 텍스처 / 모델 사용 / 엔딩 구성

[4단계] Seedance 2 영상 생성
3단계 이미지를 start_image로 사용
1단계에서 조사한 규칙 적용
15초, 9:16, 멀티샷 9씬 구성 (싱글샷 금지)
씬별 카메라 무브먼트 명시
청량한 아쿠아 블루 톤, 슬로우모션

[5단계] 결과 저장
완성된 영상 링크를 ~/Documents/광고/ 폴더에 날짜별로 저장
어떤 제품, 어떤 프롬프트로 만들었는지 기록
```

### 5. 스케줄 걸기 (자동화 하는 방법)

1. **Cowork 클릭:** Claude Desktop 앱 상단 탭에서 "Cowork"를 클릭합니다.
2. **Scheduled 메뉴:** 왼쪽 사이드바에서 "Scheduled"를 선택합니다.
3. **New task 추가:** "+ New task"를 클릭합니다.
4. **스케줄 생성:** 채팅창에 `/schedule`을 입력하여 스케줄 생성 Skill을 실행합니다.
5. **설정 입력:**
   - **이름:** `oliveyoung-ad-weekly` (또는 원하는 이름)
   - **프롬프트:** 위 4번의 마스터 프롬프트 전체를 붙여넣습니다.
   - **주기:** 매주 (처음에는 "수동(manual)"으로 설정하여 결과를 직접 확인하는 것을 권장합니다.)
6. **Save 클릭:** 설정을 완료하고 "Save"를 클릭합니다.

운영 팁: 스케줄 작업을 열어 프롬프트 내의 URL 한 줄만 교체하면 매주 다른 제품의 광고를 생성할 수 있습니다. "Scheduled" 탭에서 프롬프트 수정·주기 변경·삭제가 가능하며, 실행은 컴퓨터가 켜져 있고 Claude Desktop 앱이 열려 있을 때 진행됩니다. 앱이 닫혀 있어도 다시 열면 예약된 작업이 실행됩니다.

### 6. (Claude Code 전용) 폴더 구조 세팅

클라이언트나 캠페인마다 폴더를 따로 두고, 각 폴더에 그 프로젝트만의 `CLAUDE.md`를 넣어두면 해당 폴더에서 채팅을 열 때 Claude가 자동으로 그 규칙을 읽습니다. 첫 작업 전에 한 번만 만들어두면 됩니다.
```
my-project/
├── CLAUDE.md      # 작업 규칙 (Claude가 매번 읽는 파일)
├── reference/     # 제품 사진·로고 등 업로드용 에셋
├── images/        # 생성된 이미지
├── videos/        # 생성된 영상
└── output/        # 최종 결과물
```

**CLAUDE.md 작업 규칙 템플릿** — 세션마다 Claude가 제일 먼저 읽는 파일입니다. 기본 모델·설정·규칙을 적어두면 매번 설명하지 않아도 됩니다.
```
# 내 Higgsfield 작업 규칙

## 모델
이미지: Nano Banana Pro (generate_image)
영상: Seedance 2.0 / Kling 3.0 (generate_video)
(샷에 맞는 모델은 Claude가 알아서 골라도 됨)

## 기본 설정
종횡비: 9:16
컷 수: 8
품질: 최고

## 작업 방식
1. reference/ 폴더의 에셋을 먼저 확인한다
2. 업종·제품에 맞는 톤으로 프롬프트를 설계한다
3. 생성 후 결과물을 날짜별 폴더에 저장한다: /output/YYYY-MM-DD/

## 규칙
- 생성 전에 종횡비·컷 수를 한 번 확인한다
- 결과물은 항상 날짜 폴더에 저장한다
- 같은 캠페인 결과는 한 폴더에 모은다
```

### 7. 작업이 중간에 끊겼을 때 이어가기

긴 작업은 가끔 중간에 멈춥니다. 진행 상황을 메모해두라고 시켜두면 새 채팅에서 한마디로 이어갈 수 있습니다.
```
어디까지 만들었는지 정리해두고, 끊기면 그 다음부터 이어서 만들어줘.
```

## 활용 예시

아래 프로 템플릿은 대괄호 안만 본인 것으로 바꾸면 바로 쓸 수 있습니다. 카메라·렌즈·조명·컬러그레이딩·모션까지 다 들어있고, 시네마틱 결과는 영어 프롬프트가 가장 정확해서 영어로 작성되어 있습니다. 길이(`8s`/`12s`)와 종횡비(`9:16`·`16:9`·`1:1`)는 용도에 맞게 숫자만 수정하면 됩니다. 참고 이미지를 함께 올리면 톤·구도 정확도가 한층 올라갑니다.

**제품 정보형 광고 (자막 포함)** — 제품 사진 + 제품명·가격·핵심 효과를 자막으로 박는 정보형 광고.
```
첨부한 제품 사진으로 광고 영상 만들어줘.
- 제품명: [제품명]
- 가격: [가격]
- 핵심 효과: [효과1] / [효과2] / [효과3]
- 톤: [캐주얼 / 럭셔리 / 발랄]
제품명과 가격은 화면에 깔끔하고 잘 보이는 자막으로 넣고, 효과는 짧고 강한 카피로 비주얼에 맞춰 하나씩 띄워줘. 자막은 한국어로. 시네마틱 조명, 9:16, 12초. ./campaign 에 저장.
```
💡 자막 텍스트가 많으면 `generate_image`(Nano Banana Pro)로 글자 깔끔한 이미지 광고를 먼저 뽑은 뒤 영상화해도 좋습니다.

**UGC 후기 스타일** — 자연광 핸드헬드의 진짜 후기 같은 톤, 화질·연기 디테일은 광고급.
```
Vertical handheld UGC-style ad. A natural, relatable presenter holds [PRODUCT] toward the lens in a sun-lit apartment, speaking candidly to camera. Soft window key light, gentle handheld sway, 35mm look, shallow depth of field, true-to-life warm color, authentic skin tones, no over-polished CGI feel. 9:16, 8s. Generate 5 variations with different presenters and rooms. Save to ./campaign.
```

**럭셔리 히어로 컷** — 단일 광원 + 연무 + 티얼&앰버 그레이딩의 슬로우 오비탈.
```
Cinematic product hero film of [PRODUCT] on a matte stone pedestal. Slow 180-degree orbital dolly, 50mm lens, shallow depth of field, single dramatic key light with soft negative fill, volumetric haze, premium teal-and-amber grade, 24fps with natural motion blur, fine dust particles drifting in the light beam. 9:16, 12s. No text overlays.
```

**푸드 매크로** — 라떼 푸어링 매크로 클로즈업, 모닝 사이드라이트, 60fps 슬로모.
```
Appetizing food-commercial shot. A barista pours latte art into a ceramic cup, extreme macro close-up, 100mm macro lens, rising steam, soft morning side-light through a window, creamy bokeh background, warm cozy palette, 60fps slow motion, glossy condensation detail. 9:16, 10s.
```

**피트니스 다이내믹** — 로우앵글 트래킹 + 하드 라이트 + 차가운 데새추레이션.
```
High-energy fitness ad. An athlete mid-workout in a raw concrete loft gym, dynamic low-angle tracking shot following the movement, hard directional key light with deep contrast shadows, cool desaturated grade with crushed blacks, visible sweat and muscle detail, motivated whip-pans, fast rhythm. 9:16, 10s.
```

**부동산 워크스루** — 짐벌 글라이드 워크스루, 골든아워, 24mm 와이드.
```
Luxury real estate walkthrough of a modern penthouse. Smooth gimbal glide from the entry through floor-to-ceiling windows at golden hour, 24mm wide lens, balanced exposure between the interior and the city skyline, clean neutral architectural color, gentle parallax, elegant slow pace. 16:9, 15s.
```

**스킨케어 매크로** — 세럼 드롭 매크로 + 뷰티디시 조명 + 120fps 울트라 슬로모.
```
Premium skincare commercial. A dropper releases a single serum drop in extreme macro, the bead forming and spreading over smooth skin texture, soft beauty-dish lighting with gentle highlights, clinical clean white-and-blush palette, 120fps ultra slow motion, glossy reflective surface. 9:16, 8s.
```

**패션 에디토리얼** — 아나모픽 워킹 샷, 브루탈리스트 코리더, 필름 그레인 그레이딩.
```
Editorial fashion lookbook. A model walks toward camera through a brutalist concrete corridor wearing [OUTFIT], anamorphic 35mm lens with subtle horizontal flares, soft overcast natural light, muted film-stock grade with fine grain, confident slow stride, gentle dolly-back. 16:9, 12s.
```

**이커머스 제품 세트 (스튜디오 6컷)** — 스튜디오 3점 조명, 다양한 앵글 6컷, 하이엔드 이커머스 룩.
```
High-end studio product photography, 6 images of [PRODUCT] on a seamless gradient backdrop. Three-point lighting with a soft key and crisp rim light, varied angles (3/4 hero, top-down flat lay, dramatic side-light, macro detail, low hero, floating product), true color, crisp controlled reflections, premium e-commerce finish. 1:1.
```

**인스타 캐러셀 (7장)** — 톤·라이트 통일, 히어로+라이프스타일+디테일 믹스, 헤드라인 여백 확보.
```
Cohesive 7-slide Instagram carousel for [BRAND]. Consistent color palette and lighting across every frame, a mix of product hero, lifestyle context, and macro detail shots, generous negative space reserved for headline text, refined editorial-minimal composition. 1:1.
```

**이벤트 포스터** — 다크 차콜 + 브러시드 골드, 카피 공간 확보, 럭셔리 미니멀.
```
Vertical event poster design. Minimal luxury layout, dark charcoal background with brushed-gold accents, a single strong central focal visual, clean reserved space at top and bottom for serif typography, subtle film grain and a soft vignette, refined high-end mood. 2:3.
```

**웹사이트 히어로 배경 (루프)** — 루프 가능 추상 그라데이션, 텍스트 가독성 위해 포컬포인트 없이.
```
Abstract website hero background loop. Slow-drifting liquid gradient mesh in brand colors, soft volumetric light blooms, seamless loop with no hard focal point so overlaid text stays readable, subtle organic motion, gentle film grain. 16:9, 10s, loopable.
```

## 💡 아이디어

- 클라이언트별 폴더 + 전용 `CLAUDE.md`를 미리 세팅해두면, 광고 대행 워크플로우에서 캠페인 착수와 동시에 톤·규칙이 고정되어 결과물 일관성이 유지됩니다.
- `show_characters`로 학습시킨 디지털 캐릭터를 브랜드 전속 모델처럼 여러 캠페인에 재사용하면 매번 새 모델을 섭외하지 않아도 됩니다.
- `virality_predictor`로 생성 직후 바이럴 가능성을 예측해, 업로드 전에 후킹 강도가 낮은 컷을 걸러낼 수 있습니다.
- 스케줄 자동화와 캐릭터 재사용을 결합하면, 매주 URL만 바꿔 넣어도 같은 모델이 등장하는 시리즈형 광고를 무인으로 생산할 수 있습니다.

## 주의사항

- **초기 설정:** 첫 1~2주는 "수동(manual)" 주기로 설정하여 AI가 생성하는 결과물을 직접 확인하고, 문제가 없을 경우에 자동 전환하는 것을 추천합니다.
- **Keep awake:** 노트북이 절전 모드로 전환되지 않도록 "Keep awake" 토글을 켜두면 예약된 작업 시간을 놓치지 않고 실행할 수 있습니다.
- Higgsfield 결과물은 파일명이 정돈되지 않으므로 `/output/YYYY-MM-DD/` 형태의 날짜 폴더로 모으는 것이 안전합니다.
- 시네마틱한 결과를 원하면 한국어보다 영어 프롬프트가 더 정확하게 반영됩니다.
- 연결이 끊기면 안내 페이지에서 `＋`로 링크를 다시 추가하면 됩니다.
- 브라우저 버전 claude.ai로는 Custom Connector·스케줄 자동화 기능을 쓸 수 없어 Claude Desktop 앱이 필요합니다.

## 출처

- [https://dour-tailor-5c6.notion.site/X-37861c2773b18071b093cde019e9f86e?pvs=149](https://dour-tailor-5c6.notion.site/X-37861c2773b18071b093cde019e9f86e?pvs=149)
- [https://aduaihiggsfield1.netlify.app/](https://aduaihiggsfield1.netlify.app/)
