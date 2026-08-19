---
name: claude-meta-ads-mcp-automation
description: Claude AI의 Model Context Protocol (MCP)과 Higgsfield MCP를 활용하여 메타 광고 계정을 직접 연결하고, 자연어 명령으로 바이럴 리서치, 광고 기획, 소재 제작, 캠페인 세팅, 성과 분석 및 최적화 등 광고 운영 전반을 자동화하는 스킬입니다. 마케팅 담당자의 효율성을 극대화하고 AI 기반 자동화 워크플로우를 구축합니다.
origin: content-lab
grade: S
difficulty: 중급
category: 자동화
ai_tools: ["Claude"]
sources:
  - https://ink-jay-f32.notion.site/360f2e12ad5c81b0b2faf12936955f85?pvs=149
  - https://adu-marketing-assistant.vercel.app/?fbclid=PAVERFWAS_8ptwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp4QZw6kI82IReo5sFPsD4JWsRo1HMdYx2bNPgMArMJnL3DnFvnYUd2Es2aUf_aem_NccJXC5ml8Y3kfRxb1oF1w
---

# Claude로 메타 광고 자동화 (합병됨)

## 이게 뭔가요?
이 스킬은 Claude AI와 Higgsfield MCP(Multi-Connect Plugin)를 연동하여 마케팅 업무의 복잡한 단계를 자동화하는 방법론입니다. Claude Fable 5 버전에 두 개의 커넥터를 연결하면, 바이럴 리서치, 광고 기획안 작성, 광고 소재 생성, 그리고 Meta(Facebook/Instagram) 광고 캠페인 세팅까지 채팅 인터페이스 하나로 처리할 수 있습니다. 특히, 제품 카테고리에 맞는 톤앤매너 설정과 각 단계별 최적의 MCP 활용법을 구체적으로 제시합니다. Claude의 Model Context Protocol (MCP)을 활용하여 메타 광고 계정을 직접 연결하고 자연어로 캠페인 관리, 성과 분석, 최적화 등 광고 운영 전반을 자동화합니다. 마케팅 담당자의 효율성을 극대화하고 AI 기반 자동화 워크플로우를 구축하는 핵심 스킬입니다.

*   **주요 도구:** Claude AI (Pro 플랜 권장), Higgsfield MCP (유료 플랜 필요), Meta Ads
*   **핵심 기능:** 바이럴 리서치, 광고 기획, 소재 제작, Meta 캠페인 세팅 자동화, 성과 분석 및 최적화
*   **💰 유료 필요:** Claude Pro 플랜 및 Higgsfield MCP Pro 플랜이 커넥터 기능 활성화에 필수입니다.

## 따라하기

### 1단계: Meta 광고 계정 프로페셔널 계정 전환
광고 집행을 위해서는 Meta 계정을 프로페셔널 계정으로 전환해야 합니다. 인스타그램 개인 계정이라면 프로필 → 설정 → 계정 유형 및 도구 → 프로페셔널 계정으로 전환 (무료, 1분) 과정을 따릅니다.

### 2단계: Higgsfield MCP 연결 (이미지·영상 제작용)
Claude에 이미지·영상을 만드는 기능을 추가하는 단계입니다.
1.  **Higgsfield MCP 무료 체험 링크 접속:**
    `https://higgsfield.ai/s/higgsfield-mcp-free-trial-plan-claude-fable-5-adu.aihub-Hxmist`
2.  **Higgsfield 계정 생성/로그인:** 검은 배경의 "HIGGSFIELD MCP FOR ANY AI" 페이지에서 구글 계정으로 10초 안에 가입합니다.
3.  **Higgsfield URL 복사:** 페이지 왼쪽 "1 — Copy the Higgsfield URL" 박스 안의 초록 글씨 주소 또는 상단 버튼을 클릭하여 복사합니다.
    `https://mcp.higgsfield.ai/mcp`
4.  **Claude.ai에서 Higgsfield 커넥터 연결:**
    *   새 탭에서 claude.ai를 엽니다.
    *   커넥터 목록에 Higgsfield가 보이면 **Connect** 버튼을 누릅니다.
    *   Higgsfield 로그인 창이 뜨면 로그인하고, 권한 허용 화면에서 **Allow**를 클릭합니다.
5.  **연결 확인:** 새 채팅을 열고, Higgsfield 토글을 켠 뒤 `지금 내 크레딧 얼마 남았어?` 라고 질문하여 숫자로 답하면 연결 성공입니다.

### 3단계: Meta Ads 커넥터 연결 (광고 세팅용)
Claude에 광고를 세팅하는 기능을 추가하는 단계입니다. Higgsfield와 방법은 동일하나 주소만 다릅니다.
1.  **Meta Ads URL:**
    `https://mcp.facebook.com/ads`
2.  **Claude.ai에서 Meta Ads 커넥터 연결:**
    *   **Connect**를 누르고 페이스북 로그인 후, **연결할 비즈니스/광고 계정을 선택**합니다.
3.  **연결 확인:** 새 채팅에서 Meta Ads 토글을 켜고 `내 광고 계정이랑 연결된 페이스북 페이지 목록 보여줘` 라고 질문하여 계정이 뜨면 성공입니다. (페이지가 0개면 4단계 진행)

### 4단계: Meta 광고용 페이스북 페이지 생성 및 연결
광고는 페이스북 "페이지" 명의로만 집행 가능합니다. 개인 프로필만 있으면 소재 등록 단계에서 막힙니다. 
1.  **새 페이스북 페이지 생성:** 광고 관리 용도로만 사용하며, 프로필 꾸미기나 친구 추가는 필요 없습니다. 가입 직후 이메일 인증만 완료합니다.
2.  **Instagram 계정 연결:** 페이지 설정 → 연결된 계정 → Instagram에서 인스타그램 계정을 연결합니다. (프로필 사진만 동일하게 넣어도 광고에 지장 없습니다.)
3.  **Meta Ads 커넥터 재확인:** 새 채팅에서 `내 광고 계정이랑 연결된 페이스북 페이지 목록 보여줘` 라고 질문하여 방금 만든 페이지가 목록에 뜨면 셋업 완료입니다.

### 5단계: Claude에게 브랜드 정보 입력 및 기본 설정
매번 새 작업 시작 시 다음과 같은 형식으로 Claude에게 브랜드 기준을 설정합니다.
```
지금부터 내 브랜드 기준으로 일해줘. 브랜드명: [브랜드명]. 파는 것: [제품/서비스 한 줄]. 고객: [예: 30대 직장인 여성]. 톤: [예: 친근하지만 과장 없음]. 절대 금지: 과장 표현(최고·유일·100%), 경쟁사 비방. 이 기준을 앞으로 모든 소재·카피·캠페인에 적용해.
```

### 6단계: 광고 소재 및 캠페인 제작 프롬프트 예시
아래 프롬프트들은 Claude에게 특정 작업을 지시할 때 사용합니다. 각 프롬프트에는 어떤 MCP(손)를 사용하는지 태그와 함께 명시되어 있습니다.

#### 6-1. 바이럴 리서치, 기획안, 소재 제작, 캠페인 세팅 (종합)
```
첨부한 제품 사진 봐. ①먼저 웹 검색으로 이 카테고리에서 요즘 바이럴 되는 광고랑 릴스 훅을 직접 찾아서 정리해줘. ②그걸 바탕으로 광고 기획안부터 만들어 — 훅은 패턴 깨기·시청자 직접 호명·문제 먼저 던지기 세 방식으로 9개. ③소재 톤은 [클린 스튜디오]로 가줘 (내 카테고리에 맞는 톤은 위 05 톤 가이드에서 골라 이 자리에 넣기). CTA는 딱 하나만. ④이 기준으로 힉스필드로 소재 5개 만들고 훅 강도 점수 매겨줘. ⑤제일 좋은 걸로 메타 광고 계정에 하루 2만원짜리 테스트 캠페인 세팅해놔. 타겟은 한국 25~44. 전부 일시정지 상태로, 집행은 하지 말고 내 확인 받고 해.
```

#### 6-2. 소재 톤 변경 (Higgsfield)
```
기획안은 그대로 두고 힉스필드로 소재만 5개 다시 뽑아줘. 이번엔 [톤을 클린 스튜디오로 / 배경을 더 밝게 / 인물을 넣어서 / 텍스트 여백 크게] 해줘.
```

#### 6-3. 트래픽 캠페인 세팅 (Meta Ads)
```
방금 만든 소재 중 1등으로 메타 광고 계정에 트래픽 캠페인 세팅해줘. 일 예산 2만원. 캠페인 → 광고세트(한국 25~44) → 소재 등록 → 광고까지. 전부 일시정지 상태로 만들고 실행은 하지 마.
```

#### 6-4. 광고 미리보기 (Meta Ads)
```
방금 만든 광고 인스타그램 릴스 지면으로 미리보기 보여줘. 피드 지면도.
```

#### 6-5. 캠페인 실행
```
미리보기 확인했어. 캠페인 실행해줘.
```

#### 6-6. 성과 분석 및 소재 피로도 관리 (Meta Ads)
```
메타 광고 계정에서 지난 7일 성과를 표로 정리해줘. 광고마다 CTR 추세·빈도·CPM 추세를 보고 "CTR 하락 + 7일 빈도 3.5 초과 + CPM 상승" 세 개가 겹치는 소재는 피로 판정하고 꺼줘. 애매한 건 끄지 말고 이유랑 같이 보고만 해.
```

#### 6-7. 예산 증액 (Meta Ads)
```
메타에서 제일 성과 좋은 캠페인 예산 20% 올려줘. 다음 증액은 최소 이틀 뒤에 다시 검토하자. 일 5만원은 넘기지 말고.
```

#### 6-8. 주간 루틴 (종합)
```
이번 주 루틴 돌리자. ①메타에서 지난주 광고 성과 정리하고 ②피로해진 소재 골라내고 ③성과 좋은 소재의 훅을 변형해서 힉스필드로 새 소재 3개 뽑고 ④새 소재로 메타에 캠페인 세팅해놔. 일시정지 상태로. 정리되면 이번 주에 뭘 실행할지 추천해줘.
```

#### 6-9. UGC 광고 대본 제작 (Claude 기본 기능)
```
이 제품으로 25초 UGC 광고 대본 써줘. 구조는 훅(0~3초) → 문제(3~10초) → 해결·시연(10~20초) → CTA(마지막 5초). 훅은 ①패턴 깨기(예상 밖 장면) ②시청자 직접 호명 ③문제 먼저 던지기, 세 방식으로 각 3개씩 총 9개 뽑고 제일 센 걸로 대본 완성해. CTA는 딱 1개만.
```

#### 6-10. 소재 컨셉 제안 (Meta Ads)
```
메타 광고 계
```

## 활용 예시

*   **메타 광고 운영의 수동 작업 시간을 절약하고 싶을 때:** 자연어 명령만으로 캠페인 생성, 예산 조정, 성과 분석까지 가능합니다.
*   **자연어 명령으로 광고 캠페인 생성, 성과 분석, 문제 진단을 자동화하고 싶을 때:** "지난주 성과 분석해서 CTR 하락 소재 꺼줘"와 같은 명령어로 즉각적인 액션이 가능합니다.
*   **AI를 활용한 마케팅 자동화 및 효율성 개선 솔루션 구축을 원할 때:** Claude AI와 MCP 연동을 통해 자체적인 AI 마케팅 에이전트를 구축할 수 있습니다.

## 💡 아이디어

*   **클로드코드 개발의 핵심 패턴으로 확장:** MCP 및 API 연동은 클로드코드 개발의 핵심 패턴이므로, 메타 광고 외 다른 외부 서비스 연동에도 이 패턴을 적용하여 자동화 범위를 확장할 수 있습니다.
*   **맞춤형 AI 마케팅 에이전트 구축:** 브랜드의 특성과 목표에 맞춰 Claude AI의 응답 방식을 세밀하게 조정하여, 단순 자동화를 넘어선 고도화된 맞춤형 AI 마케팅 에이전트를 구축할 수 있습니다.

## 주의사항

*   **유료 플랜 필수:** Claude Pro 플랜 및 Higgsfield MCP Pro 플랜이 커넥터 기능 활성화에 필수적입니다.
*   **Meta 광고 계정 정책 준수:** Meta 광고 정책을 준수하며 광고를 집행해야 합니다.
*   **데이터 보안:** 개인 정보 및 광고 계정 정보 보호에 유의해야 합니다.

## 출처

- [https://ink-jay-f32.notion.site/360f2e12ad5c81b0b2faf12936955f85?pvs=149](https://ink-jay-f32.notion.site/360f2e12ad5c81b0b2faf12936955f85?pvs=149)
- [https://adu-marketing-assistant.vercel.app/?fbclid=PAVERFWAS_8ptwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp4QZw6kI82IReo5sFPsD4JWsRo1HMdYx2bNPgMArMJnL3DnFvnYUd2Es2aUf_aem_NccJXC5ml8Y3kfRxb1oF1w](https://adu-marketing-assistant.vercel.app/?fbclid=PAVERFWAS_8ptwZG9mAmV4dG4DYWVtAjEwAHNydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp4QZw6kI82IReo5sFPsD4JWsRo1HMdYx2bNPgMArMJnL3DnFvnYUd2Es2aUf_aem_NccJXC5ml8Y3kfRxb1oF1w)
