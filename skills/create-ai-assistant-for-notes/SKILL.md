---
name: create-ai-assistant-for-notes
description: Obsidian과 Claude Code를 활용하여 **흩어진 메모를 이해하고 답해주는 AI 비서**를 만드는 스킬입니다.
origin: content-lab
grade: A
difficulty: 중급
category: 자동화
ai_tools: ["Claude", "Claude Code"]
sources:
  - https://adu-llm-wiki.vercel.app/?fbclid=PAVERFWASrLkRleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAafopEyq9qrMijCCDp96qb158X29Agwno0-jPsFSwe4cSeEzyVOwtKtfzy-DHw_aem_s3d4e4EQ4Xs6x0b10NDE6A
---

# 내 모든 메모를 이해하는 AI 비서 만들기

💡 Obsidian과 Claude Code를 활용하여 **흩어진 메모를 이해하고 답해주는 AI 비서**를 만드는 스킬입니다.

## 이게 뭔가요?

흩어진 메모, 회의록, 독서 노트, 아이디어 등을 AI가 이해하고 답해주는 나만의 지식 시스템을 구축하는 방법입니다. OpenAI 창립 멤버였던 안드레 카파시가 공개한 'LLM Wiki' 패턴을 기반으로 하며, Claude Code와 Obsidian만 있으면 약 30분 안에 구축 가능합니다.

이전에는 메모 앱이 단순히 저장을 담당했다면, 이 방식을 통해 AI가 내 메모 전체를 읽고 이해하여 질문에 답해주는 '살아있는 지식 시스템'을 만들 수 있습니다.

**작동 방식:**

*   **Obsidian:** 내 모든 메모와 자료가 저장되는 저장소 역할을 합니다.
*   **Claude Code:** Obsidian 폴더를 직접 열어 읽고, 요약, 분류, 연결하여 '읽기 좋은 위키' 형태로 정리하는 AI 사서 역할을 수행합니다.

**💰 유료 필요:** Claude Pro 또는 Max 구독이 필요합니다. Obsidian, Node.js, Web Clipper는 무료입니다.

## 따라하기

**STEP 1 · Obsidian 설치 및 Vault 생성**
1.  obsidian.md에서 Obsidian을 다운로드하여 설치합니다.
2.  'Create new vault'를 눌러 새 Vault(자료 저장 폴더)를 생성하고 이름을 지정합니다 (예: MyBrain).
3.  Vault 폴더의 위치를 기억해 둡니다.

**STEP 2 · 폴더 구조 설정 (카파시 정석)**
*   `raw/`: 기사, 논문, 메모 등 원본 자료를 그대로 저장하는 폴더.
*   `raw/articles/`: 웹 클리핑 자료 저장 폴더 (선택 사항).
*   `wiki/`: AI가 정리한 읽기용 페이지가 저장되는 폴더.
*   `index.md`: 위키 전체 목차.
*   `log.md`: 작업 이력 기록.
*   `CLAUDE.md`: AI 운영 규칙 파일.

**STEP 3 · Claude Code 설치**
1.  **Node.js 설치:** nodejs.org에서 LTS 버전을 다운로드하여 설치합니다.
    *   터미널(Mac) 또는 PowerShell(Windows)에서 `node -v`를 입력하여 설치 확인.
2.  **Claude Code 설치:** 터미널 또는 PowerShell에서 다음 명령어를 실행합니다.
    ```
    npm install -g @anthropic-ai/claude-code
    ```
3.  **로그인:** 터미널에서 `claude`를 실행하고 안내에 따라 Claude 계정으로 로그인합니다.

**STEP 4 · Vault를 Claude Code로 열기**
1.  터미널에서 내 Vault 폴더로 이동합니다.
    ```
    # 예시 (실제 경로로 변경)
    cd "~/Documents/MyBrain"
    ```
2.  해당 폴더에서 `claude`를 실행합니다.

**STEP 5 · 카파시 설계도 적용 (지름길)**
1.  아래 주소에서 카파시의 LLM Wiki 설계도를 복사합니다:
    [https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
2.  Claude Code(`claude` 실행 후)에 복사한 내용을 붙여넣고 다음과 같이 요청합니다:
    ```
    이 설계도를 그대로 내 세컨드 브레인으로 구현해줘. - CLAUDE.md 규칙 파일을 만들고 - index.md와 log.md를 만들고 - raw, wiki 폴더 구조를 잡아줘 - 첫 ingest 예시를 한 번 보여줘 앞으로 모든 작업은 이 규칙을 따른다. 한국어로 해줘.
    ```
3.  AI의 제안을 허용하고 폴더 및 파일 생성을 확인합니다.

**STEP 6 · 자료 넣기 (ingest)**
1.  **직접 넣기:** 마크다운(.md) 형식으로 저장된 메모나 문서를 `raw/` 폴더에 넣습니다.
2.  **웹에서 줍기:** Obsidian Web Clipper를 설치하여 웹 기사를 `raw/articles/`에 저장합니다.
3.  자료를 넣은 후, Claude Code가 실행 중인 상태에서 다음 명령어를 입력합니다.
    ```
    › ingest
    ```
    AI가 자동으로 자료를 요약, 엔티티 추출, 개념 분류, 링크 연결, 목차 및 이력 갱신을 수행합니다.

**핵심 동작 ① ingest:** `raw/`에 자료를 넣고 `› ingest` 명령 시, AI가 요약, 엔티티 추출, 개념 분류/연결, 목차/이력 갱신을 자동으로 수행합니다.

**핵심 동작 ② query:** 정리된 위키(`wiki/` 폴더)에 평소 말투로 질문합니다. AI는 흩어진 정보를 모아 새로운 정리본을 만들어 줍니다.
    *   예: "예전에 적었던 AI 관련 아이디어 전부 찾아서 정리해줘."

**핵심 동작 ③ lint:** AI에게 위키 점검을 요청하여 오래된 주장, 모순, 끊긴 링크 등을 찾아 수정합니다.
    ```
    › 위키를 점검(lint)해줘. 오래된 주장, 서로 모순되는 내용, 끊긴 링크, 외톨이 페이지, 약한 연결을 찾아서 알려줘.
    ```

**두 가지 원칙:**
1.  **위키가 자산, 채팅은 창구:** 가치 있는 결과는 반드시 위키 페이지로 저장합니다.
2.  **꾸준히, 작게 처리:** 매일 정해진 시간에 ingest를 수행하여 시스템 과부하를 방지합니다.

## 활용 예시

*   **직장인:** 회의록, 업무 메모를 `raw/`에 모아 "이번 주 내 할 일", "지난 분기 결정사항" 등을 질문하여 주간 보고 초안 작성에 활용합니다.
*   **크리에이터:** 아이디어, 레퍼런스를 `raw/`에 저장하고 "이번 달 콘텐츠 소재 후보", "예전 인기 글 패턴" 등을 질문하여 기획에 활용합니다.
*   **공부하는 사람:** 강의 노트, 책 요약을 `raw/`에 넣고 "이 개념 관련 내 메모 전부", "시험 범위 핵심만" 등을 질문하여 학습 자료를 정리합니다.

## 주의사항

*   **민감 정보 금지:** 비밀번호, 주민등록번호 등 민감한 정보는 Vault에 저장하지 않습니다.
*   **원본(raw) 보존:** AI가 `raw/` 폴더의 원본 파일을 임의로 수정하지 않도록 주의합니다. `ingest` 시 AI가 `raw/`를 바꾸려 하면 거부합니다.
*   **백업 필수:** Vault 폴더를 클라우드에 동기화하거나 주기적으로 복사하여 백업합니다.
*   **처음엔 사본으로:** 중요한 자료는 복사본으로 먼저 연습한 뒤 적용합니다.

## 출처

[내 모든 메모를 이해하고 답해주는 AI 비서 만들기](https://adu-llm-wiki.vercel.app/?fbclid=PAVERFWASrLkRleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTAAafopEyq9qrMijCCDp96qb158X29Agwno0-jPsFSwe4cSeEzyVOwtKtfzy-DHw_aem_s3d4e4EQ4Xs6x0b10NDE6A)

## 출처

- [https://adu-llm-wiki.vercel.app/?fbclid=PAVERFWASrLkRleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAafopEyq9qrMijCCDp96qb158X29Agwno0-jPsFSwe4cSeEzyVOwtKtfzy-DHw_aem_s3d4e4EQ4Xs6x0b10NDE6A](https://adu-llm-wiki.vercel.app/?fbclid=PAVERFWASrLkRleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAafopEyq9qrMijCCDp96qb158X29Agwno0-jPsFSwe4cSeEzyVOwtKtfzy-DHw_aem_s3d4e4EQ4Xs6x0b10NDE6A)
