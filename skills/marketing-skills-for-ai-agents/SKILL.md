---
name: marketing-skills-for-ai-agents
description: 이 스킬은 **coreyhaines31/marketingskills** GitHub 저장소를 프로젝트에 설치해 **Claude Code·Cursor·Codex** 등 AI 에이전트에게 전환최적화·카피·SEO·광고·그로스 등 47종 마케팅 업무의 검증된 작업 순서를 학습시키는 스킬 라이브러리입니다.
origin: content-lab
grade: C
difficulty: 중급
category: 자동화
ai_tools: ["Claude", "Claude Code", "Cursor", "Codex"]
sources:
  - https://yongk.notion.site/34-39847642a71380dd9bf6e8f35ed826a4?pvs=149
---

# 마케팅 스킬 47종 설치하기

💡 이 스킬은 **coreyhaines31/marketingskills** GitHub 저장소를 프로젝트에 설치해 **Claude Code·Cursor·Codex** 등 AI 에이전트에게 전환최적화·카피·SEO·광고·그로스 등 47종 마케팅 업무의 검증된 작업 순서를 학습시키는 스킬 라이브러리입니다.

## 이게 뭔가요?

**coreyhaines31/marketingskills**는 AI 에이전트가 참고할 마케팅 전문 지식을 마크다운(.md) 파일 하나하나에 담아둔 오픈소스 라이브러리입니다. 버전은 v2.8.1, 라이선스는 MIT이며 **Claude Code**·**Cursor**·Windsurf·**Codex** 등 파일 기반으로 컨텍스트를 읽는 에이전트 환경 어디서든 동작합니다.

핵심 아이디어는 "AI 에이전트에게 미리 검증된 작업 순서를 알려주는 치트시트를 심어둔다"는 것입니다. 프로젝트 폴더에 이 스킬 파일들을 넣어두면, "랜딩페이지 전환율 올려줘" 같은 자연어 요청만으로도 에이전트가 알맞은 스킬(예: `cro`)을 스스로 골라 그 안에 정의된 프레임워크대로 작업을 수행합니다. 기술에 익숙한 마케터·창업자가 전환최적화·카피·SEO·광고·그로스를 자동화하려고 만든 프로젝트입니다.

💰 유료 필요: 없음 (저장소 자체는 무료·MIT). 단, 이를 실행할 Claude Code / Cursor / Codex 등 에이전트 도구의 사용료는 별도.
✅ 무료 대안: Claude Code 대신 Cursor 무료 티어나 로컬 Codex CLI로도 동일한 방식으로 스킬 파일을 읽혀 사용 가능.

## 따라하기

1. **저장소 설치** — GitHub `coreyhaines31/marketingskills` 저장소를 클론하거나 ZIP으로 다운로드해 프로젝트 폴더 안에 넣는다.
2. **기반 스킬부터 채우기** — 47개 스킬 전부가 가장 먼저 읽는 `product-marketing` 스킬을 열어 "이 제품이 뭐고, 타깃은 누구고, 어떻게 포지셔닝하는가"를 먼저 채운다. 이 컨텍스트 문서 품질이 나머지 46개 스킬 결과물의 품질을 좌우한다.
3. **자연어로 요청하거나 슬래시 명령으로 직접 호출** — 아래처럼 말하면 에이전트가 알맞은 스킬을 자동으로 선택해 실행한다.

| 이렇게 말하면 | 작동하는 스킬 |
|---|---|
| "이 랜딩페이지 전환율 좀 올려줘" | cro |
| "내 SaaS 홈페이지 카피 써줘" | copywriting |
| "가입 이벤트에 GA4 추적 붙여줘" | analytics |
| "5통짜리 웰컴 이메일 시퀀스 만들어줘" | emails |

직접 호출하려면 `/cro`, `/emails`, `/seo-audit`처럼 스킬 이름 앞에 `/`를 붙여 실행한다.

4. **스킬 간 연결 관계 파악** — 스킬은 서로를 참조하도록 설계되어 있다.
   - `copywriting ↔ cro ↔ ab-testing`
   - `revops ↔ sales-enablement ↔ cold-email`
   - `seo-audit ↔ schema ↔ ai-seo`
   - `customer-research → copywriting · cro · competitors`

5. **처음 쓸 때 권장 순서**
   - 기반 세팅: `product-marketing`으로 제품/타깃/포지셔닝 컨텍스트부터 채우기
   - 현황 진단: `seo-audit` / `analytics` / `customer-research`로 지금 상태 파악
   - 전환 개선: `cro` · `copywriting`으로 핵심 페이지부터 손보기
   - 트래픽 확보: 목표에 맞게 `ads` · `social` · `programmatic-seo` · `emails`
   - 검증 & 반복: `ab-testing`으로 측정하고 개선 루프 돌리기

### 스킬 카탈로그 (47개)

**기반**
- `product-marketing` — 제품·타깃·포지셔닝 컨텍스트 문서 작성 (가장 먼저 세팅)

**전환 최적화 (CRO)**
- `cro` 랜딩페이지·폼 전환율 최적화 / `signup` 가입·등록·체험 활성화 흐름 개선 / `onboarding` 온보딩·활성화·첫 사용 경험 / `popups` 팝업·모달·배너 최적화 / `paywalls` 앱 내 페이월·업그레이드 화면

**콘텐츠 & 카피**
- `copywriting` 페이지 카피 작성·개선 / `copy-editing` 기존 카피 편집·리프레시 / `emails` 자동화 이메일 시퀀스 / `cold-email` B2B 콜드 이메일 / `sms` SMS/MMS 마케팅 / `social` 소셜 콘텐츠 제작·전략 / `image` AI 이미지 생성 / `video` AI/프로그래매틱 영상 / `content-strategy` 콘텐츠 전략·주제 선정

**SEO & 검색 노출**
- `seo-audit` 기술·온페이지 SEO 점검 / `ai-seo` AEO·GEO·LLMO 최적화 / `programmatic-seo` 템플릿+데이터로 페이지 대량 생성 / `site-architecture` 구조·내비·URL 설계 / `competitors` 비교·대안 페이지 제작 / `schema` 구조화 데이터 마크업 / `aso` 앱스토어 리스팅 최적화

**유료 광고 & 배포**
- `ads` 구글·메타·링크드인 광고 캠페인 / `ad-creative` 광고 크리에이티브 대량 생성

**측정 & 테스트**
- `analytics` 이벤트 추적 세팅(GA4 등) / `ab-testing` A/B 테스트·실험 설계

**리텐션 & 로열티**
- `churn-prevention` 이탈 방지·세이브 오퍼 / `referrals` 추천·제휴 프로그램 / `community-marketing` 커뮤니티 구축 / `lead-magnets` 리드 마그넷 제작

**그로스 엔지니어링**
- `free-tools` 무료 도구·계산기 기획 / `co-marketing` 코마케팅 파트너 발굴 / `marketing-loops` 자동 마케팅 루프 / `directory-submissions` 디렉토리 등록

**세일즈 & RevOps**
- `prospecting` 잠재고객 발굴·리스트 구축 / `revops` 매출 운영·스코어링·라우팅 / `sales-enablement` 세일즈 덱·반론 대응

**전략 & 수익화**
- `pricing` 가격·패키징 전략 / `offers` 오퍼 설계·가치 프레이밍 / `launch` 출시/발표 전략 / `marketing-plan` AARRR 기반 종합 계획 / `marketing-ideas` 140개 SaaS 마케팅 아이디어 뱅크 / `marketing-psychology` 마케팅 심리학·행동과학 / `marketing-council` 가상 자문단 관점 / `customer-research` 고객 리서치 수행·종합 / `competitor-profiling` 경쟁사 URL 기반 프로파일링 / `public-relations` PR·언론 아웃리치

## 활용 예시

- 신규 SaaS 프로젝트 폴더에 저장소를 설치하고 `product-marketing`을 먼저 채운 뒤 "내 SaaS 홈페이지 카피 써줘"라고 입력 → 에이전트가 `copywriting` 스킬을 자동 선택해 포지셔닝 컨텍스트에 맞는 카피 초안을 생성.
- "가입 이벤트에 GA4 추적 붙여줘"라고 요청 → `analytics` 스킬이 실행되며 이벤트 추적 세팅 절차를 안내.
- `/seo-audit`을 직접 호출 → 기술·온페이지 SEO 점검 체크리스트를 즉시 실행.

## 💡 아이디어

- 두근컴퍼니 콘텐츠 프로젝트에도 동일한 패턴(스킬 마크다운 + 기반 컨텍스트 문서 우선 세팅)을 적용해 자체 마케팅 스킬 라이브러리를 만들 수 있음 — 기존 스킬 라이브러리 프로젝트([[project_skill_library]])와 구조가 유사해 참고할 가치가 있음.

## 주의사항

- 이 카탈로그에는 각 스킬의 실제 프롬프트 원문(.md 파일 내용)은 포함되어 있지 않다. 실제 사용을 위해서는 GitHub 저장소를 직접 설치해 파일을 확인해야 한다.
- `product-marketing` 컨텍스트 문서를 채우지 않고 바로 다른 스킬을 호출하면 결과 품질이 크게 떨어진다.

## 출처

- [https://yongk.notion.site/34-39847642a71380dd9bf6e8f35ed826a4?pvs=149](https://yongk.notion.site/34-39847642a71380dd9bf6e8f35ed826a4?pvs=149)
