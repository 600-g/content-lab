---
name: ai-30
description: 이 스킬은 **도구**와 **프롬프트**를 조합하여 반복적인 업무를 **자동화**하는 실전 가이드입니다.
origin: content-lab
grade: S
difficulty: 초급
category: 자동화
ai_tools: ["Claude", "도구무관"]
sources:
  - https://drive.google.com/file/d/1ZcmioCwiHXGU4TfNEHeokosB5Ajs3wKM/view?fbclid=PAVERFWASk3ddleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAaeaSib1FytF8FziA3TEz-Tw96epSb7kWx5pZBBQ3cSQJozZbxldaa-b493M4A_aem_7sGFNXAtXVrmQJLNdq53Sw
---

# AI 비서 30개 조합으로 업무 자동화

💡 이 스킬은 **도구**와 **프롬프트**를 조합하여 반복적인 업무를 **자동화**하는 실전 가이드입니다.

## 이게 뭔가요?
이 가이드는 **업무 자동화**를 위한 **AI 비서 30명 세팅법**을 다룹니다. 핵심 원리는 **"도구 + 도구 = 자동화"** 공식에 기반하며, 비개발자도 누구나 따라 할 수 있도록 **Claude**와 노코드 도구 조합을 활용하는 실전 가이드입니다.

이 가이드를 활용하는 방법은 복잡하게 30개를 모두 할 필요가 없습니다. 현재 가장 **귀찮은 일** 하나를 골라, 해당 카드의 **프롬프트**를 복사하여 **Claude**에 붙여넣는 것부터 시작합니다. 이 과정은 크게 세 단계로 나뉩니다.

1. **도구 연결**: 각 조합에 필요한 도구(예: Gmail, 슬랙, Google Sheets 등)를 **Claude**에 연결(MCP)해야 합니다. 이는 **"Claude가 해당 앱을 직접 만질 수 있게 권한을 주는 것"**을 의미합니다.
2. **프롬프트 붙여넣기**: 카드에 있는 **복붙 프롬프트**를 그대로 복사하여 **Claude**에 붙여넣고, **[대괄호]** 안의 내용만 자신의 상황에 맞게 수정합니다.
3. **반복으로 굳히기**: 한 번 성공적으로 자동화가 이루어지면, 끝에 **"이걸 매일 아침 9시에 자동으로 해줘"**와 같은 명령어를 추가하여 **24시간 비서**로 만듭니다.

프롬프트의 핵심 구조는 **"무엇을 / 어떤 기준으로 / 결과를 어떻게"** 세 가지를 명확히 하는 것이며, 이 구조만 갖추면 어떤 도구 조합에도 응용할 수 있습니다.

## 따라하기

### 메일 · 일정 · 기록 (01–10) 섹션 예시

**01 메일 자동 분류 (Gmail + Claude)**
*   **목표**: 받은 메일을 종류별로 자동으로 정리합니다.
*   **복붙 프롬프트**: 
    ```
    Gmail에서 오늘 받은 메일을 읽고 [업무 / 광고 / 뉴스레터 / 개인]으로 분류해서 각각 라벨을 붙여줘. 애매한 건 내가 정할게,
    목록만 먼저 보여줘.
    ```
*   **세팅 팁**: **Gmail MCP** 연결 후 성공하면, **"매일 아침 8시에 자동으로"**를 추가합니다.

**02 회의록 자동 정리 (Claude + Notion)**
*   **목표**: 회의나 자료 내용을 문서로 자동 정리합니다.
*   **복붙 프롬프트**: 
    ```
    아래 회의 내용을 [결정사항 / 담당자별 할일 / 다음 안건] 세 가지로 정리해서 Notion [회의록] 페이지에 오늘 날짜로 저장해
    줘.
    ```
*   **세팅 팁**: 녹취 텍스트를 그대로 붙여넣어도 문제없습니다.

**03 일정 자동 관리 (Claude + 캘린더)**
*   **목표**: 일정을 등록하고 리마인드까지 자동으로 처리합니다.
*   **복붙 프롬프트**: 
    ```
    "[날짜] [시간] [내용]" 일정을 Google Calendar에 등록하고 하루 전·1시간 전 알림을 설정해줘. 겹치는 일정이 있으면 먼저
    알려줘.
    ```
*   **세팅 팁**: **"이번 주 빈 시간 2시간 찾아줘"**와 같은 명령어로 스케줄 관리에도 활용 가능합니다.

**04 어디서나 지시 (텔레그램 + Claude)**
*   **목표**: 외부(텔레그램)에서도 메시지 한 줄로 업무 지시가 가능하게 합니다.
*   **복붙 프롬프트**: 
    ```
    앞으로 내가 텔레그램으로 보내는 메시지를 업무 지시로 받아 처리하고, 완료되면 결과를 텔레그램으로 다시 보내줘.
    ```
*   **세팅 팁**: 컴퓨터를 켜 둔 채 외출하면 스마트폰으로 모든 업무 지시가 가능합니다.

**05 웹 정보 자동 수집 (Playwright + Claude)**
*   **목표**: 특정 웹사이트의 정보를 긁어와 자동 요약합니다.
*   **복붙 프롬프트**: 
    ```
    [사이트 URL]에 접속해서 [제목 / 가격 / 내용 등]을 수집해서 정리해줘. 여러 페이지면 [N]페이지까지 순서대로.
    ```
*   **세팅 팁**: **Playwright MCP** 설정을 통해 API 없이 어떤 사이트든 정보 수집이 가능합니다.

## 활용 예시

- **시나리오 1 (이메일 관리)**: 매일 아침 받은 메일함을 **Claude**에 연결하고, **"오늘 받은 메일 중 [업무] 관련 메일만 모아서 요약하고, 미처리된 건 목록만 보여줘"**라고 지시하면, 분류와 요약이 동시에 이루어집니다.
- **시나리오 2 (회의록 정리)**: 회의 녹취록 전체를 복사하여 **Claude**에 붙여넣고 **"이 내용을 바탕으로 [결정사항], [담당자별 할일], [다음 안건]을 표로 정리하고, 각 할 일에 마감일을 지정해줘"**라고 요청하면 구조화된 결과물을 얻을 수 있습니다.
- **시나리오 3 (웹 정보 수집)**: 특정 경쟁사 웹사이트 URL을 지정하고 **"이 사이트의 최신 가격 정보와 주요 특징 3가지를 수집해서 비교표로 만들어줘"**라고 요청하면, **Playwright**를 통해 데이터를 수집하고 정리합니다.

## 💡 아이디어

이 구조를 활용하여 **'주간 보고서 자동 생성'**과 같은 고도화된 자동화 워크플로우를 만들 수 있습니다. 예를 들어, 매주 월요일 아침에 **Gmail**에서 지난주 주요 업무 메일을 수집하고, **Notion**에 저장된 회의록과 결합하여 **'주간 성과 보고서 초안'**을 자동으로 작성하도록 프롬프트를 설계할 수 있습니다. 이는 단순 반복 업무를 넘어 지식 자산화 단계로 나아가는 핵심 과정입니다.

## 주의사항

*   **프롬프트의 핵심**: **"무엇을 / 어떤 기준으로 / 결과를 어떻게"** 이 세 가지 요소가 명확해야 합니다. 이 중 하나라도 모호하면 AI의 결과물도 모호해집니다.
*   **도구 연결 권한**: **MCP** 연결 시, **Claude**에게 부여하는 권한 범위를 명확히 인지하고, 불필요한 접근 권한은 주지 않도록 주의해야 합니다.
*   **반복 테스트**: 자동화 설정을 한 번에 완벽하게 기대하기보다, **'한 번 잘 되면'**이라는 마인드로 작은 성공부터 반복하며 시스템을 굳히는 것이 중요합니다.

## 출처
[비서30명_세팅법.pdf](https://drive.google.com/file/d/1ZcmioCwiHXGU4TfNEHeokosB5Ajs3wKM/view?fbclid=PAVERFWASk3ddleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAaeaSib1FytF8FziA3TEz-Tw96epSb7kWx5pZBBQ3cSQJozZbxldaa-b493M4A_aem_7sGFNXAtXVrmQJLNdq53Sw

## 출처

- [https://drive.google.com/file/d/1ZcmioCwiHXGU4TfNEHeokosB5Ajs3wKM/view?fbclid=PAVERFWASk3ddleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAaeaSib1FytF8FziA3TEz-Tw96epSb7kWx5pZBBQ3cSQJozZbxldaa-b493M4A_aem_7sGFNXAtXVrmQJLNdq53Sw](https://drive.google.com/file/d/1ZcmioCwiHXGU4TfNEHeokosB5Ajs3wKM/view?fbclid=PAVERFWASk3ddleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAaeaSib1FytF8FziA3TEz-Tw96epSb7kWx5pZBBQ3cSQJozZbxldaa-b493M4A_aem_7sGFNXAtXVrmQJLNdq53Sw)
