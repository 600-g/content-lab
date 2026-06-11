---
name: higgsfield-mcp-claude-ad-generation
description: 이 스킬은 **Claude Desktop 앱**과 **Higgsfield MCP**를 연동하여, 멀티샵의 상품 페이지 URL만 입력하면 **자동으로 광고 영상**을 생성해주는 스킬입니다.
origin: content-lab
grade: A
difficulty: 중급
category: 콘텐츠
ai_tools: ["Claude"]
sources:
  - https://dour-tailor-5c6.notion.site/X-37861c2773b18071b093cde019e9f86e?pvs=149
---

# AI로 상품 광고 영상 자동 생성

💡 이 스킬은 **Claude Desktop 앱**과 **Higgsfield MCP**를 연동하여, 멀티샵의 상품 페이지 URL만 입력하면 **자동으로 광고 영상**을 생성해주는 스킬입니다.

## 이게 뭔가요?

본 스킬은 AI 이미지 및 비디오 생성 서비스인 **Higgsfield MCP**를 **Claude Desktop 앱**에 연결하여, 특정 상품의 광고 영상을 자동으로 생성하는 워크플로우입니다. 복잡한 영상 제작 과정을 AI에게 맡길 수 있으며, 특히 Claude Desktop 앱의 커넥터 기능을 활용하여 효율성을 극대화합니다.

주로 온라인 쇼핑몰(예: 올리브영)의 상품 페이지 URL을 입력하면, 해당 상품의 특징을 분석하고, 스토리보드 생성, 영상 편집, 최종 결과물 저장까지 AI가 단계별로 수행합니다. 이를 통해 시간과 비용을 절감하며 고품질의 광고 콘텐츠를 제작할 수 있습니다. Claude Desktop 앱의 유료 플랜(Pro/Max/Team 이상)이 필수적이며, 브라우저 버전의 claude.ai로는 이용이 불가합니다.

💰 **유료 필요:** Claude Desktop 앱 (Mac/Windows) 유료 플랜 (Pro/Max/Team 이상), Higgsfield MCP 연결, Chrome for Claude 연결(별도 설치)

## 따라하기

### Higgsfield MCP 설정 워크플로우

1.  **MCP 접속:** Higgsfield.AI 웹사이트에 접속합니다.
2.  **링크 복사:** MCP 링크를 복사합니다.
3.  **Claude Connectors:** Claude Desktop 앱의 Connectors 메뉴로 이동합니다.
4.  **Custom Connector 추가:** 새로운 Custom Connector를 추가합니다.
5.  **링크 붙여넣기:** 복사한 Higgsfield MCP 링크를 붙여넣습니다. (릴스를 참고하며 연결하면 더욱 쉽습니다.)

### 광고 자동 생성 워크플로우

#### 준비물

*   **Claude Desktop 앱** (Mac/Windows) - 브라우저 claude.ai로는 불가
*   **유료 플랜** (Pro/Max/Team 이상)
*   **Higgsfield MCP 연결**
*   **Chrome for Claude 연결** (별도 설치 필요)

#### STEP 1. URL 찾기

1.  광고로 만들 제품이 있는 멀티샵(예: 올리브영) 웹사이트에 접속합니다.
2.  해당 **제품 페이지의 주소창 URL을 복사**합니다.

#### STEP 2. 마스터 프롬프트에 URL 넣기

아래 프롬프트에서 `URL 부분`만 복사한 제품 페이지 URL로 교체하여 사용합니다.

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
GPT Image 2로 광고 씬 이미지 ‘스토리보드 생성’ - 총 9컷의 이미지 생성
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

#### STEP 3. 스케줄 걸기 (자동화 하는 방법)

1.  **Cowork 클릭:** Claude Desktop 앱 상단 탭에서 "Cowork"를 클릭합니다.
2.  **Scheduled 메뉴:** 왼쪽 사이드바에서 "Scheduled"를 선택합니다.
3.  **New task 추가:** "+ New task"를 클릭합니다.
4.  **스케줄 생성:** 채팅창에 `/schedule`을 입력하여 스케줄 생성 Skill을 실행합니다.
5.  **설정 입력:**
    *   **이름:** `oliveyoung-ad-weekly` (또는 원하는 이름)
    *   **프롬프트:** STEP 2에서 작성한 마스터 프롬프트 전체를 붙여넣습니다.
    *   **주기:** 매주 (처음에는 "수동(manual)"으로 설정하여 결과를 직접 확인하는 것을 권장합니다.)
6.  **Save 클릭:** 설정을 완료하고 "Save"를 클릭합니다.

#### STEP 4. 자동화 운영

*   **매주 다른 제품 광고:** 스케줄 작업을 열어 프롬프트 내의 URL 한 줄만 교체하면 매주 다른 제품의 광고를 생성할 수 있습니다.
*   **스케줄 관리:** "Scheduled" 탭에서 프롬프트 수정, 주기 변경, 삭제가 가능합니다.
*   **실행 조건:** 컴퓨터가 켜져 있고 Claude Desktop 앱이 열려 있을 때만 실행됩니다.
*   **자동 실행:** 컴퓨터가 꺼져 있거나 앱이 닫혀 있어도, 앱을 다시 열 때 예약된 작업이 실행됩니다.

## 주의사항

*   **초기 설정:** 첫 1~2주는 "수동(manual)" 주기로 설정하여 AI가 생성하는 결과물을 직접 확인하고, 문제가 없을 경우에 자동 전환하는 것을 추천합니다.
*   **Keep awake:** 노트북이 절전 모드로 전환되지 않도록 "Keep awake" 토글을 켜두면 예약된 작업 시간을 놓치지 않고 실행할 수 있습니다.

## 출처

[힉스필드 X 클로드](https://dour-tailor-5c6.notion.site/X-37861c2773b18071b093cde019e9f86e?pvs=149)

## 출처

- [https://dour-tailor-5c6.notion.site/X-37861c2773b18071b093cde019e9f86e?pvs=149](https://dour-tailor-5c6.notion.site/X-37861c2773b18071b093cde019e9f86e?pvs=149)
