---
name: higgsfield-mcp-claude-ad-generation
description: Claude에 **Higgsfield MCP**·**Meta Ads 커넥터**를 연결해 상품 URL·사진·한국어 한 줄로 광고 영상·이미지를 만들고 메타 캠페인 세팅·성과 분석까지 자동화한다. **HyperFrames**(URL→MP4), ChatGPT Higgsfield 프리셋 66종, Claude Desktop 주간 스케줄 포함.
origin: content-lab
grade: S
difficulty: 중급
category: 자동화
ai_tools: ["Claude", "Claude Code", "GPT"]
sources:
  - https://dour-tailor-5c6.notion.site/X-37861c2773b18071b093cde019e9f86e?pvs=149
  - https://aduaihiggsfield1.netlify.app/
  - https://ink-jay-f32.notion.site/360f2e12ad5c81b0b2faf12936955f85?pvs=149
  - https://adu-marketing-assistant.vercel.app/?fbclid=PAVERFWAS_8ptwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp4QZw6kI82IReo5sFPsD4JWsRo1HMdYx2bNPgMArMJnL3DnFvnYUd2Es2aUf_aem_NccJXC5ml8Y3kfRxb1oF1w
  - https://resonant-frog-df5.notion.site/HyperFrames-Claude-3503a1a3234380b685bddfa2931f3665
  - https://abounding-helmet-0e4.notion.site/3c373c7b15ad81c2980ff1fd5eddb9e1?pvs=149
---

# AI 광고 소재 제작과 메타 운영

💡 Claude(두뇌)에 **Higgsfield MCP**(이미지·영상을 만드는 손)와 **Meta Ads 커넥터**(광고를 세팅하는 손)를 붙이면, 상품 URL이나 사진 한 장에서 시작해 **소재 제작 → 캠페인 세팅 → 성과 분석 → 주간 자동 반복**까지 채팅 하나로 돌릴 수 있습니다.

## 이게 뭔가요?

Claude는 원래 텍스트만 다루는 "두뇌"입니다. 여기에 MCP(Model Context Protocol) 커넥터를 연결하면 "손"이 생깁니다. 브라우저를 강제로 조종하거나 외부 코드를 설치할 필요 없이, 커넥터가 Claude에게 도구를 직접 쥐어줘서 모든 작업이 Claude 안에서 네이티브로 돌아갑니다.

- **Higgsfield MCP**: 이미지·영상 생성 (Nano Banana Pro, Seedance 2.0, Kling 3.0 등)
- **Meta Ads 커넥터**: Meta(Facebook/Instagram) 광고 계정에 캠페인·광고세트·소재 등록, 미리보기, 성과 조회, 예산 조정
- **Claude 기본 기능**: 웹 검색으로 바이럴 리서치, 광고 기획안·훅·UGC 대본 작성, 제품 페이지 분석

기술적인 프롬프트나 카메라 용어를 몰라도, 뭘 만들고 싶은지만 한국어로 말하면 Claude가 업종·분위기를 읽고 카메라 무빙·조명·디테일까지 설계한 뒤 Higgsfield에서 생성합니다. 예를 들어 올리브영 같은 멀티샵의 상품 페이지 URL을 주면 상품 특징 분석 → 스토리보드 생성 → 영상 생성 → 결과 저장까지 단계별로 수행합니다.

같은 목적(광고 소재 자동 제작)을 위한 길이 몇 가지 더 있습니다. 자기 웹사이트를 모션그래픽 광고로 바꾸는 **HyperFrames**(HTML → MP4 변환 프레임워크, Claude Code 슬래시 명령), ChatGPT 안에서 Higgsfield 앱을 불러 **프리셋 이름만 말해** 광고를 뽑는 방법(영상 26개 + 이미지 40개 프리셋)입니다.

### 어떤 방법을 언제 쓰나

| 내가 가진 것 / 원하는 것 | 추천 방법 | 결과물 | 따라하기 절 |
|---|---|---|---|
| 제품 사진 한 장 + "이런 느낌" 한국어 한 줄 | Claude + Higgsfield MCP 기본 요청 | 영상·이미지 여러 개 | 3-A |
| 쇼핑몰 상품 페이지 URL만 있음 | Claude + Higgsfield MCP 마스터 프롬프트 | 스토리보드 9컷 + 15초 멀티샷 영상 | 3-B |
| 시네마틱한 고퀄 컷 (업종별) | Higgsfield MCP 프로 템플릿 | 업종별 영상·이미지 | 3-C |
| 사진 한 장 + 정해진 광고 포맷(언박싱·후기·비교표 등) | ChatGPT + Higgsfield 앱 프리셋 | 프리셋형 영상·이미지 시안 | 3-D |
| **내 웹사이트** URL을 모션그래픽 광고로 | Claude Code + HyperFrames (+ Suno BGM) | HTML 기반 MP4 (릴스·틱톡·제품 소개) | 3-E |
| 기획부터 탄탄하게 (훅·대본) | Claude 기본 기능 → Higgsfield | 기획안·훅 9개·UGC 대본 → 소재 | 3-F |
| 만든 소재로 실제 메타 광고 집행·운영 | Meta Ads 커넥터 | 캠페인 세팅·미리보기·성과 분석·예산 조정 | 4 |
| 매주 같은 작업 반복 | Claude Desktop Cowork → Scheduled | 무인 주간 생산·운영 | 5 |

### 비용

| 항목 | 내용 |
|---|---|
| Higgsfield | 이미지·영상 생성 시 크레딧 소모. MCP 커넥터 기능은 Higgsfield MCP Pro 플랜이 필요하다는 안내가 있으며, 무료 체험 링크가 제공됨 |
| Claude | 커넥터 기능 활성화에는 Claude Pro 플랜 이상 권장. Custom Connector·스케줄은 Claude Desktop 앱 유료 플랜(Pro/Max/Team 이상) 필요 (브라우저 claude.ai는 스케줄·Custom Connector 불가) |
| Claude Code | 결과물을 내 컴퓨터 폴더에 자동 저장까지 쓰려면 Claude Max 권장 |
| Chrome for Claude | 상품 페이지 접속용, 별도 설치 |
| ChatGPT Higgsfield 앱 | 유료, 처음 시작하는 사용자는 3일 무료 체험 |
| Suno AI (BGM) | 무료 하루 5곡, 대량·상업용은 Suno Pro $10/월 |

✅ **무료에 가까운 대안**: Desktop 앱 없이 일반 claude.ai 웹 채팅만으로도 생성 자체는 같게 작동합니다(로컬 폴더 자동 저장·스케줄 자동화만 빠집니다). 프리셋 방식의 직접적인 무료 대안은 없으나, Canva, Leonardo AI 등 무료 이미지/영상 생성 도구로 비슷한 결과물을 만드는 것은 가능합니다(ChatGPT 안에서 즉시 생성하는 편의성은 없음).

## 따라하기

### 1. 커넥터 연결하기

#### 1-1. Higgsfield MCP 연결 (소재 제작용)

연결 방법은 세 가지이며, 쓰는 앱과 자동화 여부에 따라 고릅니다.

**방법 A — Higgsfield 안내 페이지에서 바로 연결 (가장 간편)**
Higgsfield 시작 페이지의 "여기서 연결 시작하기" 버튼을 누르면 단계별 연결 방법이 나옵니다. 그대로 따라 하면 30초면 끝납니다. Claude Code·Codex를 쓴다면 안내 페이지의 'CLI' 탭이 더 편합니다.

**방법 B — claude.ai 커넥터 목록에서 연결 (웹 채팅용)**
1. Higgsfield MCP 무료 체험 링크에 접속합니다.
   `https://higgsfield.ai/s/higgsfield-mcp-free-trial-plan-claude-fable-5-adu.aihub-Hxmist`
2. 검은 배경의 "HIGGSFIELD MCP FOR ANY AI" 페이지에서 구글 계정으로 10초 안에 가입/로그인합니다.
3. 페이지 왼쪽 "1 — Copy the Higgsfield URL" 박스 안의 초록 글씨 주소(또는 상단 버튼)를 복사합니다.
   `https://mcp.higgsfield.ai/mcp`
4. 새 탭에서 claude.ai를 열고, 커넥터 목록에 Higgsfield가 보이면 **Connect** 버튼을 누릅니다.
5. Higgsfield 로그인 창에서 로그인하고, 권한 허용 화면에서 **Allow**를 클릭합니다.

**방법 C — Claude Desktop Custom Connector로 수동 연결 (5절 스케줄 자동화를 쓰려면 이 방식 필요)**
1. Higgsfield.AI 웹사이트에 접속합니다.
2. MCP 링크(위 `https://mcp.higgsfield.ai/mcp`)를 복사합니다.
3. Claude Desktop 앱의 Connectors 메뉴로 이동합니다.
4. 새로운 Custom Connector를 추가합니다.
5. 복사한 Higgsfield MCP 링크를 붙여넣습니다.

**연결 확인하기** — 새 채팅을 열고(웹이면 Higgsfield 토글을 켜고) 아래처럼 물어봅니다. 이미지·영상 생성 도구 목록이 뜨면 성공입니다.
```
지금 쓸 수 있는 Higgsfield 도구들 알려줘.
```
크레딧이 숫자로 답해져도 성공입니다.
```
지금 내 크레딧 얼마 남았어?
```
Claude Code를 쓴다면 아래처럼 확인합니다. "힉스필드 MCP 연결 정상" 응답이 나오면 정상입니다.
```
mcp 힉스필드 연결됐는지 확인해
```

#### 1-2. Higgsfield 도구 목록

| 도구 | 용도 |
|---|---|
| `generate_image` | 제품·광고 이미지, 아바타, 패션·UGC (Nano Banana Pro 등 모델 선택) |
| `generate_video` | 영상 생성 (Seedance 2.0, Kling 3.0) |
| `presets_show` | 이미지→영상 프리셋 |
| `show_characters` | 사진 5~20장으로 학습하는, 계속 재사용 가능한 디지털 캐릭터 (약 10분 소요) |
| `show_marketing_studio` | 브랜드 키트·광고 레퍼런스·프리셋으로 광고 영상 제작 |
| `personal_clipper_create` | 긴 유튜브 영상을 숏폼 클립으로 자동 변환 (자막·비율·개수 선택) |
| `virality_predictor` | 바이럴 가능성·후킹 강도·리텐션 예측 |
| `show_generations` / `show_medias` / `job_display` | 과거 생성물·미디어·작업 결과 확인 |

#### 1-3. Meta Ads 커넥터 연결 (광고 운영용, 4절을 쓸 때만)

**사전 준비 ① 프로페셔널 계정 전환**: 인스타그램 개인 계정이라면 프로필 → 설정 → 계정 유형 및 도구 → 프로페셔널 계정으로 전환 (무료, 1분).

**연결**: Higgsfield와 방법은 같고 주소만 다릅니다.
1. Meta Ads URL: `https://mcp.facebook.com/ads`
2. claude.ai에서 **Connect**를 누르고 페이스북 로그인 후, **연결할 비즈니스/광고 계정을 선택**합니다.
3. 새 채팅에서 Meta Ads 토글을 켜고 `내 광고 계정이랑 연결된 페이스북 페이지 목록 보여줘` 라고 물어 계정이 뜨면 성공입니다. 페이지가 0개면 아래 ②를 진행합니다.

**사전 준비 ② 광고용 페이스북 페이지 만들기**: 광고는 페이스북 "페이지" 명의로만 집행할 수 있습니다. 개인 프로필만 있으면 소재 등록 단계에서 막힙니다.
1. 새 페이스북 페이지를 만듭니다. 광고 관리 용도로만 쓰며 프로필 꾸미기나 친구 추가는 필요 없습니다. 가입 직후 이메일 인증만 완료합니다.
2. 페이지 설정 → 연결된 계정 → Instagram에서 인스타그램 계정을 연결합니다. (프로필 사진만 같게 넣어도 광고에 지장 없습니다.)
3. 새 채팅에서 `내 광고 계정이랑 연결된 페이스북 페이지 목록 보여줘` 를 다시 물어 방금 만든 페이지가 뜨면 셋업 완료입니다.

### 2. 작업 기준 고정하기

#### 2-1. 브랜드 기준 입력 (모든 방법 공통)

새 작업을 시작할 때마다 브랜드 기준을 먼저 알려두면 소재·카피·캠페인 전체의 톤이 흔들리지 않습니다.
```
지금부터 내 브랜드 기준으로 일해줘. 브랜드명: [브랜드명]. 파는 것: [제품/서비스 한 줄]. 고객: [예: 30대 직장인 여성]. 톤: [예: 친근하지만 과장 없음]. 절대 금지: 과장 표현(최고·유일·100%), 경쟁사 비방. 이 기준을 앞으로 모든 소재·카피·캠페인에 적용해.
```

#### 2-2. (Claude Code) 폴더 구조와 CLAUDE.md

클라이언트나 캠페인마다 폴더를 따로 두고, 각 폴더에 그 프로젝트만의 `CLAUDE.md`를 넣어두면 해당 폴더에서 채팅을 열 때 Claude가 자동으로 그 규칙을 읽습니다. 첫 작업 전에 한 번만 만들어두면 됩니다.
```
my-project/
├── CLAUDE.md      # 작업 규칙 (Claude가 매번 읽는 파일)
├── reference/     # 제품 사진·로고 등 업로드용 에셋
├── images/        # 생성된 이미지
├── videos/        # 생성된 영상
└── output/        # 최종 결과물
```

**CLAUDE.md 작업 규칙 템플릿** — 세션마다 Claude가 제일 먼저 읽는 파일입니다. 기본 모델·설정·규칙을 적어두면 매번 설명하지 않아도 됩니다. 2-1의 브랜드 기준 문장을 여기에 같이 넣어두면 더 편합니다.
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

### 3. 광고 소재 만들기

#### 3-A. 사진 한 장 + 한국어 한 줄 (Higgsfield MCP)

새 채팅을 열고 제품 사진이나 레퍼런스 이미지를 드래그해서 올린 뒤, 만들고 싶은 걸 한국어로 적습니다.
```
방금 올린 제품 사진으로 9:16 광고 영상 5개 만들어줘. 각각 다른 사람이 등장해서 자연스럽게 후기 말하는 느낌, 8초씩.
```
결과물은 채팅에서 바로 받을 수 있고, Claude Code를 쓴다면 끝에 한 줄만 붙이면 내 컴퓨터 폴더에 자동 저장됩니다.
```
./campaign 폴더에 저장해줘
```

#### 3-B. 상품 URL만으로 완전 자동 생성 (마스터 프롬프트)

멀티샵(예: 올리브영) 제품 페이지의 URL을 복사한 뒤, 아래 프롬프트에서 `URL 부분`만 교체해 씁니다. 2단계는 Chrome으로 페이지에 접속하므로 Chrome for Claude 연결이 필요합니다. 3단계의 컨셉 문구(청량·수분감)와 4단계의 톤(아쿠아 블루)은 브랜드에 맞게 바꿉니다.
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

이 프롬프트가 하는 일을 정리하면 다음과 같습니다.

| 단계 | 하는 일 | 바꿀 곳 |
|---|---|---|
| 1 | 영상 모델 프롬프트 규칙(6단계 공식·카메라 무브먼트·금지어)을 먼저 조사 | 다른 모델을 쓰면 검색어 |
| 2 | 상품 페이지에서 성분·효능·컨셉 추출 (제품 그대로 X, 분위기만 참고) | URL |
| 3 | 9컷 스토리보드 이미지 (제품샷/텍스처/모델 사용/엔딩) | 컨셉 문구 |
| 4 | 스토리보드를 start_image로 15초 9:16 멀티샷 영상 | 톤·속도 |
| 5 | 날짜별 폴더에 영상 링크와 사용 프롬프트 기록 | 저장 경로 |

#### 3-C. 업종별 프로 템플릿 (Higgsfield MCP)

대괄호 안만 본인 것으로 바꾸면 바로 쓸 수 있습니다. 카메라·렌즈·조명·컬러그레이딩·모션까지 다 들어 있고, 시네마틱 결과는 영어 프롬프트가 가장 정확해서 영어로 되어 있습니다. 길이(`8s`/`12s`)와 종횡비(`9:16`·`16:9`·`1:1`)는 용도에 맞게 숫자만 수정합니다. 참고 이미지를 함께 올리면 톤·구도 정확도가 한층 올라갑니다.

**제품 정보형 광고 (자막 포함)** — 제품 사진 + 제품명·가격·핵심 효과를 자막으로 박는 정보형 광고.
```
첨부한 제품 사진으로 광고 영상 만들어줘.
- 제품명: [제품명]
- 가격: [가격]
- 핵심 효과: [효과1] / [효과2] / [효과3]
- 톤: [캐주얼 / 럭셔리 / 발랄]
제품명과 가격은 화면에 깔끔하고 잘 보이는 자막으로 넣고, 효과는 짧고 강한 카피로 비주얼에 맞춰 하나씩 띄워줘. 자막은 한국어로. 시네마틱 조명, 9:16, 12초. ./campaign 에 저장.
```
💡 자막 텍스트가 많으면 `generate_image`(Nano Banana Pro)로 글자가 깔끔한 이미지 광고를 먼저 뽑은 뒤 영상화해도 좋습니다.

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

**피트니스 다이내믹** — 로우앵글 트래킹 + 하드 라이트 + 차가운 디새추레이션.
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

**웹사이트 히어로 배경 (루프)** — 루프 가능한 추상 그라데이션, 텍스트 가독성을 위해 포컬포인트 없이.
```
Abstract website hero background loop. Slow-drifting liquid gradient mesh in brand colors, soft volumetric light blooms, seamless loop with no hard focal point so overlaid text stays readable, subtle organic motion, gentle film grain. 16:9, 10s, loopable.
```

#### 3-D. ChatGPT에서 Higgsfield 프리셋으로 만들기

별도 사이트로 이동하지 않고 ChatGPT 안에서 Higgsfield 앱을 불러, 사진을 올리고 프리셋 이름만 말하면 광고 영상·이미지 시안이 나옵니다. 빠르면 몇 초 안에 결과가 나옵니다.

1. ChatGPT 사이드바에서 앱 목록을 엽니다.
2. 'Higgsfield'를 검색해 추가합니다. 한 번 추가하면 다음부터는 대화창에서 바로 불러 쓸 수 있습니다.
3. 사진을 올리고 원하는 프리셋 이름을 **말로** 지정합니다(버튼을 찾아 누르는 방식이 아님). 아래 목록의 이름을 그대로 쓰면 됩니다.

**프리셋 사용 예시**
- "이 헤드폰 Product Showcase 16:9로 만들어줘"
- "이 헤드폰 UGC 광고 영상으로 만들어줘"
- "이 헤드폰 Hyper Motion으로 만들어줘"
- "이 헤드폰 Product Shot으로 만들어줘. 여름 해변 캠페인 컷으로."

**비율 지정**: 인스타 피드(4:5), 릴스/숏폼(9:16), 유튜브/상세페이지(16:9) 등 원하는 비율을 말로 지정합니다.

**이름이 정확하지 않아도 됩니다**: 프리셋 이름이 기억나지 않으면 만들고 싶은 광고 내용을 말로 설명해도 인식해 생성하기도 합니다(예: Product Shot 대신 "제품을 정면으로 보여줘"). 다만 정확한 이름을 쓰면 의도에 더 맞는 결과가 나옵니다.

**정해진 틀이 없을 때**: 원하는 장면이 목록에 없으면 `Wild Card` 프리셋으로 장면을 직접 설명합니다.

**🎥 영상 프리셋 26개 (크게 다섯 갈래)**

| 갈래 | 프리셋 | 설명 |
|---|---|---|
| 사람이 나와서 말하는 것 (8) | UGC | 실사용자가 찍은 것처럼 보이는 기본형 |
| | Selfie Testimonial | 셀카 각도로 찍은 후기 |
| | Direct-to-Camera | 카메라 정면을 보고 말하는 톤 |
| | This Gadget Saved Me | "이거 덕분에 편해졌다" 추천형 |
| | Secret Hack Reveal | 몰랐던 사용법을 알려주는 구성 |
| | UGC Addiction | 손에서 못 놓는 모습 강조 |
| | Couple Sharing At Home | 집에서 둘이 같이 쓰는 장면 |
| | Tutorial | 순서대로 알려주는 사용법 |
| 열어보고 착용하는 것 (7) | Unboxing | 기본 언박싱 |
| | Unboxing ASMR | 소리를 살린 언박싱 |
| | Reboxing | 거꾸로 다시 포장하며 보여주기 |
| | Unboxing Virtual Try-On | 열고 바로 착용까지 한 번에 |
| | UGC Virtual Try On | 착용해본 후기 톤 |
| | Pro Virtual Try On | 더 정교한 가상 착용 |
| | Virtual Try-On Sneakers | 신발 전용 착용 |
| 제품만 나오는 것 (6) | Product Showcase | 제품을 정면으로 소개 |
| | TV Spot | TV 광고에 가까운 톤 |
| | Hyper Motion | 빠르게 훑는 접사 모션 |
| | Camera POV | 내가 보는 시점으로 |
| | Giant Figure | 크기를 키워 압도적으로 |
| | Mystery Box | 뭔지 모르게 열어 보이기 |
| 변화를 보여주는 것 (4) | Before and After | 쓰기 전과 후 |
| | Mess to Fresh | 엉망인 상태에서 깔끔하게 |
| | Crush Test | 부숴보는 내구성 테스트 |
| | Classic Meets Modern | 예전 것과 지금 것을 섞기 |
| 정해진 틀이 없는 것 (1) | Wild Card | 원하는 장면을 직접 설명해서 만들기 |

**🖼️ 이미지 광고 프리셋 40개 (상세페이지·피드 광고에 가까움)**

| 갈래 | 프리셋 | 설명 |
|---|---|---|
| 후기와 반응 (10) | Customer Quote | 고객 한마디를 크게 |
| | Star Review | 별점이 붙은 후기 |
| | Trusted Review | 신뢰도를 강조한 리뷰 인용 |
| | Social Proof | 사용자 수 같은 인기 지표 |
| | Social Comment | SNS 댓글처럼 보이는 형태 |
| | Highlighted Comment | 댓글 하나를 크게 강조 |
| | Reaction Quote | 반응을 그대로 옮긴 형태 |
| | Customer Story | 한 사람의 사연 중심 |
| | Media Mentions | 언론에 언급된 것처럼 |
| | Press Screenshot | 기사 화면 캡처 느낌 |
| 기능과 혜택 설명 (8) | Key Features | 핵심 기능 정리 |
| | Benefits | 좋은 점 나열 |
| | Benefits Checklist | 체크 표시로 정리한 혜택 |
| | Callout Notes | 부위마다 선을 빼서 설명 |
| | Product in Action | 실제로 쓰는 장면 |
| | Whiteboard Explainer | 손으로 그린 듯한 설명 |
| | Behind the Product | 만들어진 과정 이야기 |
| | Personal Note | 손편지 같은 톤 |
| 비교하고 전환시키는 것 (5) | Comparison Table | 다른 제품과 나란히 비교표 |
| | Then vs Now | 예전과 지금 |
| | Unexpected Twist | 예상을 뒤집는 구성 |
| | Why We're Different | 다른 점을 정면으로 |
| | Product Spotlight | 제품 하나만 강하게 |
| 가격을 말하는 것 (2) | Special Offer | 할인이나 특가 |
| | Bundle Deal | 묶음 구성 |
| 숫자를 보여주는 것 (3) | Stat Surround | 수치를 제품 주위에 배치 (레이아웃 두 가지) |
| | Lifestyle with Numbers | 일상 장면 위에 수치 |
| 카피가 주인공인 것 (7) | Headline | 큰 제목 한 줄 |
| | Bold Statement | 강하게 선언하는 문장 |
| | Hero Statement | 대표 문구를 중앙에 |
| | Mystery Hook | 궁금하게 만드는 문장 |
| | Highlighted Hook | 형광펜으로 그은 듯한 강조 |
| | Scroll Break | 스크롤을 멈추게 하는 컷 |
| | Magazine Style | 잡지 지면 레이아웃 |
| 플랫폼 화면을 흉내내는 것 (5) | Organic Post | 광고가 아닌 일반 게시물처럼 |
| | Trending Post | 인기 게시물 톤 |
| | App Screenshot | 앱 화면처럼 |
| | UGC Side-by-Side | 사용자 컷을 나란히 |
| | Color Block | 색면으로 나눈 디자인 |

목록은 2024년 8월 기준이며, 프리셋은 계속 추가·업데이트될 수 있습니다. 처리 시간은 프리셋마다 다릅니다(예: `Product Showcase` 46초, `Hero Statement` 1분 16초). 오래 걸린다고 오류는 아니니 기다립니다. 사진 한 장으로 여러 프리셋을 돌려볼 수 있어 새로 찍을 필요가 없습니다.

#### 3-E. 내 웹사이트 URL → 광고 영상 (HyperFrames + Claude Code)

HyperFrames는 HTML → MP4 자동 변환 프레임워크입니다. Claude에게 웹사이트 URL을 주면 디자인 분석부터 영상 완성까지 자동으로 진행합니다.

| 종류 | 길이 | 포맷 |
|---|---|---|
| 인스타 릴스/스토리 | 10~15초 | 1080 × 1920 세로 |
| 틱톡 광고 | 10~15초 | 1080 × 1920 세로 |
| 제품 소개 영상 | 30~60초 | 1920 × 1080 가로 |
| 브랜드 광고 | 15~30초 | 원하는 포맷 |

**STEP 1. HyperFrames 셋업** — Claude에게 한 줄:
```
HyperFrames 깃헙 레포 [URL] 를 내 프로젝트에 설치하고 셋업해줘.
Claude Code 슬래시 명령으로 /website-to-hyperframes 가 동작하도록.
```

**STEP 2. Claude Code에서 한 줄 명령** — Claude가 프리뷰 URL을 돌려주면 브라우저에서 확인합니다.
```
/website-to-hyperframes https://원하는사이트.com 15초짜리 인스타 광고 만들어줘
```

**STEP 3. 상세 프롬프트 (제품 정보 포함)**
```
/hyperframes 사용해서 영상 만들어줘.

제품 : claudeasy
설명 : 개발을 몰라도 자동화를 만들어주는 웹앱.
핵심 기능 : 200개 넘는 하네스 임베드, 오케스트레이션이 알아서 대답,
          깃헙 트렌드 실시간 모니터링.
타겟 : 비전공자 / 클로드 초보.
길이 : 15초.
프로젝트 path: [본인 프로젝트 경로]
```

**STEP 4. MP4 저장** — Claude가 만들어준 웹페이지에서 Export → 다운로드.

**STEP 5. Suno AI BGM (선택)** — 사이트: https://suno.com (무료 하루 5곡)

BGM 프롬프트 예:
```
cinematic ambient, minimal piano, no vocals, soft, premium feel, 30 seconds
upbeat electronic, corporate, motivational, no lyrics, clean
J-pop rock, anime opening, energetic, female vocal, refreshing, 1 minute
```

활용 팁: 1막(도입)·2막(전개)·3막(CTA)별로 다른 BGM으로 분위기를 전환합니다.

#### 3-F. 기획부터 탄탄하게: 훅·대본 → 소재

소재를 바로 뽑기 전에 Claude 기본 기능으로 기획을 먼저 세우면 성과가 안정적입니다.

**UGC 광고 대본 (Claude 기본 기능)**
```
이 제품으로 25초 UGC 광고 대본 써줘. 구조는 훅(0~3초) → 문제(3~10초) → 해결·시연(10~20초) → CTA(마지막 5초). 훅은 ①패턴 깨기(예상 밖 장면) ②시청자 직접 호명 ③문제 먼저 던지기, 세 방식으로 각 3개씩 총 9개 뽑고 제일 센 걸로 대본 완성해. CTA는 딱 1개만.
```

**소재 톤만 바꿔 다시 뽑기 (Higgsfield)**
```
기획안은 그대로 두고 힉스필드로 소재만 5개 다시 뽑아줘. 이번엔 [톤을 클린 스튜디오로 / 배경을 더 밝게 / 인물을 넣어서 / 텍스트 여백 크게] 해줘.
```

톤은 제품 카테고리에 맞게 고릅니다(예: [클린 스튜디오]). 4-2의 종합 프롬프트는 리서치 → 기획안 → 소재 → 캠페인 세팅까지 한 번에 돕니다.

### 4. 메타 광고 운영 (Meta Ads 커넥터)

각 프롬프트 앞의 괄호는 어떤 커넥터(손)를 쓰는지 표시합니다. 프롬프트를 보낼 때 해당 커넥터 토글이 켜져 있어야 합니다.

#### 4-1. 안전 원칙

- 캠페인은 항상 **일시정지 상태로** 만들게 하고, 미리보기를 확인한 뒤 따로 "실행"을 지시합니다.
- 예산 상한(예: 일 5만원)과 증액 간격(예: 최소 이틀)을 프롬프트에 박아둡니다.
- 애매한 판정은 끄지 말고 이유와 함께 보고만 하게 합니다.

#### 4-2. 리서치 → 기획 → 소재 → 캠페인 세팅 (종합, Higgsfield + Meta Ads)
```
첨부한 제품 사진 봐. ①먼저 웹 검색으로 이 카테고리에서 요즘 바이럴 되는 광고랑 릴스 훅을 직접 찾아서 정리해줘. ②그걸 바탕으로 광고 기획안부터 만들어 — 훅은 패턴 깨기·시청자 직접 호명·문제 먼저 던지기 세 방식으로 9개. ③소재 톤은 [클린 스튜디오]로 가줘 (내 카테고리에 맞는 톤은 위 05 톤 가이드에서 골라 이 자리에 넣기). CTA는 딱 하나만. ④이 기준으로 힉스필드로 소재 5개 만들고 훅 강도 점수 매겨줘. ⑤제일 좋은 걸로 메타 광고 계정에 하루 2만원짜리 테스트 캠페인 세팅해놔. 타겟은 한국 25~44. 전부 일시정지 상태로, 집행은 하지 말고 내 확인 받고 해.
```

#### 4-3. 트래픽 캠페인 세팅 (Meta Ads)
```
방금 만든 소재 중 1등으로 메타 광고 계정에 트래픽 캠페인 세팅해줘. 일 예산 2만원. 캠페인 → 광고세트(한국 25~44) → 소재 등록 → 광고까지. 전부 일시정지 상태로 만들고 실행은 하지 마.
```

#### 4-4. 광고 미리보기 (Meta Ads)
```
방금 만든 광고 인스타그램 릴스 지면으로 미리보기 보여줘. 피드 지면도.
```

#### 4-5. 캠페인 실행 (Meta Ads)
```
미리보기 확인했어. 캠페인 실행해줘.
```

#### 4-6. 성과 분석 및 소재 피로도 관리 (Meta Ads)
```
메타 광고 계정에서 지난 7일 성과를 표로 정리해줘. 광고마다 CTR 추세·빈도·CPM 추세를 보고 "CTR 하락 + 7일 빈도 3.5 초과 + CPM 상승" 세 개가 겹치는 소재는 피로 판정하고 꺼줘. 애매한 건 끄지 말고 이유랑 같이 보고만 해.
```

#### 4-7. 예산 증액 (Meta Ads)
```
메타에서 제일 성과 좋은 캠페인 예산 20% 올려줘. 다음 증액은 최소 이틀 뒤에 다시 검토하자. 일 5만원은 넘기지 말고.
```

#### 4-8. 소재 컨셉 제안 (Meta Ads)

원문 프롬프트가 아래에서 끊겨 있습니다. 4-6의 성과표를 바탕으로 다음 소재 컨셉을 제안받는 용도로, 뒷부분은 직접 이어 써서 씁니다.
```
메타 광고 계
```

### 5. 주간 자동화 파이프라인

#### 5-1. 주간 루틴 프롬프트 (Meta Ads + Higgsfield)

성과 정리 → 피로 소재 제거 → 잘 된 훅 변형으로 새 소재 → 일시정지 상태 세팅 → 이번 주 실행 추천까지 한 번에 돕니다.
```
이번 주 루틴 돌리자. ①메타에서 지난주 광고 성과 정리하고 ②피로해진 소재 골라내고 ③성과 좋은 소재의 훅을 변형해서 힉스필드로 새 소재 3개 뽑고 ④새 소재로 메타에 캠페인 세팅해놔. 일시정지 상태로. 정리되면 이번 주에 뭘 실행할지 추천해줘.
```

소재 생산만 매주 돌리고 싶다면 3-B 마스터 프롬프트를, 운영까지 돌리려면 위 루틴 프롬프트를 스케줄에 넣습니다.

#### 5-2. 스케줄 걸기 (Claude Desktop)

1. **Cowork 클릭:** Claude Desktop 앱 상단 탭에서 "Cowork"를 클릭합니다.
2. **Scheduled 메뉴:** 왼쪽 사이드바에서 "Scheduled"를 선택합니다.
3. **New task 추가:** "+ New task"를 클릭합니다.
4. **스케줄 생성:** 채팅창에 `/schedule`을 입력해 스케줄 생성 Skill을 실행합니다.
5. **설정 입력:**
   - **이름:** `oliveyoung-ad-weekly` (또는 원하는 이름)
   - **프롬프트:** 3-B 마스터 프롬프트 전체(또는 5-1 주간 루틴)를 붙여넣습니다.
   - **주기:** 매주 (처음에는 "수동(manual)"으로 설정해 결과를 직접 확인하는 것을 권장합니다.)
6. **Save 클릭:** 설정을 마치고 "Save"를 클릭합니다.

운영 팁: 스케줄 작업을 열어 프롬프트 안의 URL 한 줄만 교체하면 매주 다른 제품의 광고를 생성할 수 있습니다. "Scheduled" 탭에서 프롬프트 수정·주기 변경·삭제가 가능하며, 실행은 컴퓨터가 켜져 있고 Claude Desktop 앱이 열려 있을 때 진행됩니다. 앱이 닫혀 있어도 다시 열면 예약된 작업이 실행됩니다.

#### 5-3. 작업이 중간에 끊겼을 때 이어가기

긴 작업은 가끔 중간에 멈춥니다. 진행 상황을 메모해두라고 시켜두면 새 채팅에서 한마디로 이어갈 수 있습니다.
```
어디까지 만들었는지 정리해두고, 끊기면 그 다음부터 이어서 만들어줘.
```

### 6. 운영 체크리스트

- [ ] Higgsfield 연결 확인(도구 목록·크레딧 응답)
- [ ] (운영 시) 프로페셔널 계정 전환 + 광고용 페이스북 페이지 + Meta Ads 커넥터에서 페이지 목록 확인
- [ ] 브랜드 기준(금지 표현 포함) 입력 또는 CLAUDE.md에 고정
- [ ] 첫 5개 소재는 사람이 톤 검수, 세로 영상은 실제 앱 화면에서 미리보기
- [ ] 캠페인은 일시정지 상태로 생성 → 미리보기 → 실행 지시
- [ ] 예산 상한·증액 간격 명시
- [ ] 결과물은 `/output/YYYY-MM-DD/` 날짜 폴더에 정리
- [ ] 스케줄은 첫 1~2주 수동(manual) → 문제 없으면 매주로 전환, Keep awake 켜기

### 7. 트러블슈팅

| 증상 | 확인할 것 |
|---|---|
| Higgsfield 도구가 안 보인다 | 새 채팅에서 커넥터 토글이 켜져 있는지, 연결이 끊겼으면 안내 페이지에서 `＋`로 링크를 다시 추가 |
| 브라우저 claude.ai에서 Custom Connector·스케줄 메뉴가 없다 | 브라우저 버전에서는 쓸 수 없음. Claude Desktop 앱 유료 플랜 필요 |
| 상품 URL을 못 읽는다 | Chrome for Claude 연결(별도 설치) 여부 |
| 소재 등록 단계에서 막힌다 | 페이스북 "페이지"가 광고 계정에 연결돼 있는지 (개인 프로필만으로는 불가) |
| 페이지 목록이 0개 | 1-3의 광고용 페이스북 페이지 만들기 진행 |
| 예약 작업이 안 돌았다 | 컴퓨터 절전 여부(Keep awake), Desktop 앱 실행 여부 — 앱을 다시 열면 실행됨 |
| 결과물 파일명이 뒤죽박죽 | 날짜 폴더 저장 규칙을 프롬프트·CLAUDE.md에 명시 |
| 프리셋 이름으로 검색이 안 된다 (웹사이트) | ChatGPT 앱과 웹사이트의 프리셋 이름이 다를 수 있음. 앱에서 부르는 이름으로 통일 |
| 시네마틱 느낌이 약하다 | 영어 프롬프트(3-C 템플릿) 사용, 참고 이미지 첨부 |
| 생성이 오래 걸린다 | 프리셋·모델마다 1분 이상 걸릴 수 있음, 오류 아님 |

## 활용 예시

- **쇼핑몰 신상품 주간 광고**: 매주 신상품 상세페이지 URL 한 줄만 바꿔 넣은 3-B 마스터 프롬프트를 스케줄로 돌리면 → 9컷 스토리보드와 15초 세로 광고가 날짜 폴더에 쌓입니다.
- **메타 광고 운영 시간 절약**: "지난주 성과 분석해서 CTR 하락 소재 꺼줘" 같은 자연어 명령만으로 캠페인 생성, 예산 조정, 성과 분석, 문제 진단까지 즉시 실행합니다.
- **업종별 고퀄 컷**: 카페는 푸드 매크로, 헬스장은 피트니스 다이내믹, 부동산은 워크스루 템플릿으로 대괄호만 바꿔 바로 생성합니다.
- **상세페이지·피드 이미지 일괄 제작**: 제품 사진 한 장으로 ChatGPT Higgsfield 프리셋 Key Features·Star Review·Comparison Table을 연달아 돌려 상세페이지 상단 이미지와 피드 광고 세트를 만듭니다.
- **SaaS·웹앱 홍보 영상**: 내 서비스 URL을 `/website-to-hyperframes`로 넘겨 15초 릴스 광고를 만들고, Suno로 Instrumental BGM을 붙입니다.
- **A/B 테스트**: 훅 9개(패턴 깨기·직접 호명·문제 먼저)로 소재 5개를 만들고 훅 강도 점수를 매긴 뒤, 1등과 2등을 각각 일시정지 상태 캠페인으로 세팅해 비교합니다.
- **자체 AI 마케팅 에이전트**: Claude와 MCP 연동으로 리서치·기획·제작·운영을 한 대화에서 처리하는 맞춤형 마케팅 에이전트를 구축합니다.

## 💡 아이디어

- 클라이언트별 폴더 + 전용 `CLAUDE.md`를 미리 세팅해두면, 광고 대행 워크플로우에서 캠페인 착수와 동시에 톤·규칙이 고정되어 결과물 일관성이 유지됩니다.
- `show_characters`로 학습시킨 디지털 캐릭터를 브랜드 전속 모델처럼 여러 캠페인에 재사용하면 매번 새 모델을 섭외하지 않아도 됩니다.
- `virality_predictor`로 생성 직후 바이럴 가능성을 예측해, 업로드 전에 후킹 강도가 낮은 컷을 걸러냅니다.
- 스케줄 자동화와 캐릭터 재사용을 결합하면, 매주 URL만 바꿔 넣어도 같은 모델이 등장하는 시리즈형 광고를 무인으로 생산할 수 있습니다.
- `personal_clipper_create`로 긴 유튜브 영상을 숏폼 클립으로 잘라 광고 소재 후보로 씁니다.
- MCP·API 연동은 Claude Code 개발의 핵심 패턴이므로, 메타 광고 외 다른 외부 서비스 연동에도 같은 패턴을 적용해 자동화 범위를 넓힐 수 있습니다.
- 촬영이 어렵거나 예산이 부족한 개인 사업자·스타트업은 사진 몇 장만으로 상세페이지 이미지, 광고 영상, 브랜드 소개 영상까지 빠르게 만들 수 있습니다.

## 주의사항

- **집행 전 사람 확인**: 캠페인은 항상 일시정지 상태로 만들고 미리보기 확인 후 실행합니다. 예산 상한을 프롬프트에 명시합니다.
- **스케줄 초기 설정**: 첫 1~2주는 "수동(manual)" 주기로 결과를 직접 확인하고, 문제가 없을 때 자동으로 전환합니다.
- **Keep awake**: 노트북이 절전 모드로 넘어가지 않도록 "Keep awake" 토글을 켜두면 예약 시간을 놓치지 않습니다.
- **파일 정리**: Higgsfield 결과물은 파일명이 정돈되지 않으므로 `/output/YYYY-MM-DD/` 형태의 날짜 폴더로 모으는 것이 안전합니다.
- **프롬프트 언어**: 시네마틱한 결과를 원하면 한국어보다 영어 프롬프트가 더 정확하게 반영됩니다.
- **연결 끊김**: 연결이 끊기면 안내 페이지에서 `＋`로 링크를 다시 추가합니다.
- **앱 제약**: 브라우저 버전 claude.ai로는 Custom Connector·스케줄 자동화를 쓸 수 없어 Claude Desktop 앱이 필요합니다. HyperFrames 셋업은 Claude Code 권한이 필요합니다.
- **저작권·제품 표현**: HyperFrames는 본인 웹사이트만 사용합니다(타사 URL로 광고 제작 X). 상품 페이지 분석 시에도 제품을 그대로 쓰지 말고 브랜드 분위기만 참고하게 합니다.
- **과장·허위 수치**: 브랜드 기준에 과장 표현(최고·유일·100%)과 경쟁사 비방 금지를 넣어둡니다. `Product Spotlight` 프리셋은 이미지 하단에 스펙·성능 수치 막대를 자동 생성하는데, 이 숫자가 실제 제품 정보와 다를 수 있으니 잘라내고 씁니다.
- **프리셋 이름 차이**: ChatGPT 앱의 프리셋 이름과 웹사이트 검색 이름이 다를 수 있습니다(예: `Reboxing`, `Crush Test`는 웹에서 찾기 어려울 수 있음). 앱에서 부르는 이름으로 통일합니다.
- **검수**: AI 생성 영상은 톤 검수가 필수입니다. 첫 5개는 사람이 검수하고, 1080×1920 세로 영상은 실제 앱 미리보기로 확인합니다.
- **Suno**: 무료 5곡/일 한도, 대량은 Suno Pro $10/월. 한국어 발음이 어색하니 영어 가사 또는 Instrumental을 권장하며, 무료는 상업 사용이 제한되므로 광고용은 Pro 라이선스를 확인합니다.
- **정책·보안**: Meta 광고 정책을 준수해 집행하고, 개인 정보와 광고 계정 정보 보호에 유의합니다.

## 출처

- [https://dour-tailor-5c6.notion.site/X-37861c2773b18071b093cde019e9f86e?pvs=149](https://dour-tailor-5c6.notion.site/X-37861c2773b18071b093cde019e9f86e?pvs=149)
- [https://aduaihiggsfield1.netlify.app/](https://aduaihiggsfield1.netlify.app/)
- [https://ink-jay-f32.notion.site/360f2e12ad5c81b0b2faf12936955f85?pvs=149](https://ink-jay-f32.notion.site/360f2e12ad5c81b0b2faf12936955f85?pvs=149)
- [https://adu-marketing-assistant.vercel.app/?fbclid=PAVERFWAS_8ptwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp4QZw6kI82IReo5sFPsD4JWsRo1HMdYx2bNPgMArMJnL3DnFvnYUd2Es2aUf_aem_NccJXC5ml8Y3kfRxb1oF1w](https://adu-marketing-assistant.vercel.app/?fbclid=PAVERFWAS_8ptwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp4QZw6kI82IReo5sFPsD4JWsRo1HMdYx2bNPgMArMJnL3DnFvnYUd2Es2aUf_aem_NccJXC5ml8Y3kfRxb1oF1w)
- [https://resonant-frog-df5.notion.site/HyperFrames-Claude-3503a1a3234380b685bddfa2931f3665](https://resonant-frog-df5.notion.site/HyperFrames-Claude-3503a1a3234380b685bddfa2931f3665)
- [https://abounding-helmet-0e4.notion.site/3c373c7b15ad81c2980ff1fd5eddb9e1?pvs=149](https://abounding-helmet-0e4.notion.site/3c373c7b15ad81c2980ff1fd5eddb9e1?pvs=149)
