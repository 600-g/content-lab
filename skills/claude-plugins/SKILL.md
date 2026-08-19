---
name: claude-plugins
description: 클로드의 성능을 극대화하는 **6가지 무료 깃허브 도구**를 소개합니다. 복사·붙여넣기만으로 즉시 적용 가능합니다.
origin: content-lab
grade: S
difficulty: 초급
category: 업무
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://adu-github-picks.vercel.app/?fbclid=PAVERFWATdWHtwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp7ycc2kxliZp1IHlUgwDv3xsJB1IHkMf4JViHgx9_v9zjtikGiGa2gNENg2O_aem_FNen8P-jpFaciFvHrtjF0A
---

# 클로드 플러그인으로 AI 성능 높이기

💡 클로드의 성능을 극대화하는 **6가지 무료 깃허브 도구**를 소개합니다. 복사·붙여넣기만으로 즉시 적용 가능합니다.

## 이게 뭔가요?
같은 클로드를 사용하더라도 설정에 따라 성능 차이가 크게 발생합니다. 이 글에서는 클로드의 성능을 향상시키기 위해 전 세계 사용자들이 다듬어온 공개된 깃허브 설정을 소개합니다. 특히 별 10만 개 이상을 받은 검증된 설정과 복사·붙여넣기 수준으로 바로 적용 가능한 것들만 추려 6가지 무료 도구를 제시합니다. 이 도구들은 클로드 코드의 채팅 입력창에 명령어를 붙여넣는 것만으로 설치 및 활용이 가능합니다.


## 따라하기

### 01. CLAUDE.md: 카르파시 4원칙

- **난이도:** 파일 한 장 넣기
- **효과:** 클로드의 작업 방식 변화 (AI 코딩의 고질병 개선)
- **설명:** 테슬라 AI 총괄 출신 안드레 카파시가 제안한 4가지 원칙을 담은 텍스트 파일입니다. 이 파일을 작업 폴더에 넣으면 클로드 코드가 자동으로 해당 폴더의 모든 작업에 적용하여, AI가 멋대로 가정하거나 복잡하게 만드는 버릇을 제어합니다.

```
https://github.com/multica-ai/andrej-karpathy-skills 저장소에 있는 CLAUDE.md 파일 내용을 가져와서 지금 폴더에 CLAUDE.md로 저장해줘. 이미 CLAUDE.md가 있으면 맨 아래에 이어 붙여줘.
```

### 02. 문서 스킬 (Document Skills): 파일 자동 생성 및 편집

- **난이도:** 명령어 두 줄
- **효과:** 결과물이 채팅 밖으로 — 파일로 나옴
- **설명:** 클로드를 만든 앤트로픽이 제공하는 공식 스킬로, PPT, 엑셀, 워드, PDF 파일을 클로드가 직접 만들거나 기존 파일을 수정할 수 있게 합니다.

```
https://github.com/anthropics/skills 저장소에서 문서 스킬(document-skills)을 플러그인으로 설치해줘.
/plugin install document-skills@anthropic-agent-skills
```

### 03. Superpowers: 계획 수립 및 검토 강화

- **난이도:** 명령어 한 줄
- **효과:** 만들기 전에 계획부터 밟음
- **설명:** 이 플러그인은 클로드에게 작업을 지시했을 때, 바로 결과물을 내놓기보다 설계 검토 → 계획 → 구현 → 스스로 리뷰의 단계를 거치도록 하여 결과물의 완성도를 높입니다.

```
https://github.com/obra/superpowers 이 저장소의 superpowers 플러그인을 설치해줘.
/plugin install superpowers@claude-plugins-official
```

### 04. 질문하는 스킬 (Matt Pocock Skills): 요구사항 구체화

- **난이도:** 명령어 두 줄
- **효과:** 클로드가 사용자에게 질문하기 시작함
- **설명:** 유명 개발 강사가 공개한 스킬로, 작업 시작 전 클로드가 사용자에게 요구사항을 자세히 묻고, 사용자의 계획에 대한 피드백을 제공하여 더 정확한 결과물을 얻도록 돕습니다.

```
https://github.com/mattpocock/skills 이 저장소의 스킬을 플러그인으로 설치해줘. 설치가 끝나면 초기 설정(/setup-matt-pocock-skills)까지 진행해줘.
/plugin install mattpocock-skills
/setup-matt-pocock-skills
```

### 05. The Agency: 직군별 AI 에이전트 활용

- **난이도:** 붙여넣기 한 번
- **효과:** 혼자인데 검토해줄 팀이 생긴 효과 (개발 지식 불필요)
- **설명:** 마케팅, 영업, 재무, 디자인 등 다양한 직군의 AI 에이전트 230개 이상을 제공합니다. 특정 역할을 지정하여 해당 직군의 관점에서 답변을 받을 수 있습니다.

```
https://github.com/msitarzewski/agency-agents 저장소를 받아서 설치 스크립트(scripts/install.sh)를 실행해줘. 설치 대상은 클로드 코드로 선택해줘.
```

### 06. ECC (Enhanced Contextual Conversation): 작업 기억 및 연속성

- **난이도:** 명령어 두 줄
- **효과:** 어제 하던 일을 기억함
- **설명:** 전문 에이전트, 스킬, 명령어를 통합 제공하며, 세션이 끝나도 작업 요약을 저장하여 다음 작업에 이어서 활용할 수 있게 합니다. 계획, 실행, 검토, 기억까지 포함하는 종합 패키지입니다.

```
https://github.com/affaan-m/ECC 이 저장소를 플러그인으로 설치해줘.
/plugin marketplace add https://github.com/affaan-m/ECC
/plugin install ecc@ecc
```

## 활용 예시

1. **CLAUDE.md 활용:**
   - **입력:** (CLAUDE.md 파일 내용을 작업 폴더에 저장)
   - **시나리오:** "이 문서에서 오타만 고쳐줘. 다른 건 건드리지 말고."
   - **결과:** 명확하게 오타만 수정하며, 불필요한 의역이나 추가 작업 없이 요청된 범위만 처리합니다.

2. **문서 스킬 활용:**
   - **입력:** "아래 회의 내용을 보고용 PPT 파일로 만들어줘. 표지 포함 5장 이내로. (회의록 내용 붙여넣기)"
   - **결과:** 클로드가 직접 PPT 파일을 생성하여 제공합니다.

3. **Superpowers 활용:**
   - **입력:** "우리 가게 예약 안내 페이지 하나 만들어줘."
   - **결과:** 클로드가 바로 코드를 생성하는 대신, 어떤 손님이 보는 페이지인지, 어떤 정보가 들어가야 하는지 먼저 질문하고 계획을 세운 뒤 결과물을 생성합니다.

4. **질문하는 스킬 활용:**
   - **입력:** `/grill-me 다음 달에 스마트스토어를 열려고 해. 첫 달은 광고 없이 인스타로만 모객하고 상품은 3개로 시작할 생각이야.`
   - **결과:** 클로드가 "스마트스토어에서 판매할 상품은 무엇인가요?", "타겟 고객층은 누구인가요?" 등 구체적인 질문을 던져 계획을 구체화하도록 돕습니다.

5. **The Agency 활용:**
   - **입력:** "틱톡 전략가 에이전트 관점으로 이 릴스 아이디어 3개를 검토해줘. 어떤 게 제일 가능성 있는지 이유랑 같이. (아이디어 붙여넣기)"
   - **결과:** 틱톡 전략가의 관점에서 각 아이디어의 장단점과 성공 가능성을 분석하여 제시합니다.

6. **ECC 활용:**
   - **입력:** `/ecc:plan 다음 주에 올릴 콘텐츠 5개 계획 짜기`
   - **결과:** 다음 주 콘텐츠 5개에 대한 상세한 계획을 수립하고, 추후 `/ecc:continue` 와 같은 명령어로 이어서 작업을 진행할 수 있습니다.

## 💡 아이디어

- **콘텐츠 제작 자동화:** The Agency의 "콘텐츠 크리에이터" 에이전트를 활용하여 블로그 게시물, 소셜 미디어 콘텐츠 등 다양한 형식의 초안을 자동으로 생성하고, Superpowers를 통해 계획 및 검토 단계를 거쳐 완성도를 높일 수 있습니다.
- **맞춤형 학습 도구:** 질문하는 스킬의 `/teach` 명령어를 활용하여 특정 주제에 대한 심층 학습 자료를 생성하고, ECC를 통해 학습 과정을 기록하고 이어갈 수 있습니다.

## 주의사항

- **중복 설치 주의:** 여러 스킬 팩을 동시에 설치하면 충돌이 발생할 수 있으므로, 처음에는 상황에 맞는 하나를 선택하여 사용하고 점진적으로 추가하는 것이 좋습니다.
- **유료 플랜:** ECC의 Pro 플랜은 유료 옵션이 있으므로, 무료 버전을 충분히 활용한 후 필요에 따라 고려할 수 있습니다.
- **대화 속도:** 일부 스킬은 계획 및 검토 단계를 추가하므로, 빠른 답변이 필요한 간단한 작업에는 오히려 시간이 더 소요될 수 있습니다.

## 출처

[클로드 성능을 바꾸는 깃허브 무료 도구 6개](https://adu-github-picks.vercel.app/)

## 출처

- [https://adu-github-picks.vercel.app/?fbclid=PAVERFWATdWHtwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp7ycc2kxliZp1IHlUgwDv3xsJB1IHkMf4JViHgx9_v9zjtikGiGa2gNENg2O_aem_FNen8P-jpFaciFvHrtjF0A](https://adu-github-picks.vercel.app/?fbclid=PAVERFWATdWHtwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp7ycc2kxliZp1IHlUgwDv3xsJB1IHkMf4JViHgx9_v9zjtikGiGa2gNENg2O_aem_FNen8P-jpFaciFvHrtjF0A)
