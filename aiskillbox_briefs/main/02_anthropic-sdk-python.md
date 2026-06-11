💡 이 스킬은 **Anthropic 공식 Python SDK** (`pip install anthropic`)로, Claude API 를 Python 애플리케이션에서 호출하는 가장 단순하고 빠른 방법을 제공합니다.

## 이게 뭔가요?

**Anthropic 이 직접 관리하는 공식 Python SDK** (PyPI: `anthropic`, GitHub stars 3.5k · forks 691, MIT License). Python 코드 5줄로 Claude API 메시지 호출이 가능하며, **streaming · async · tool use · vision** 등 Claude 의 모든 핵심 기능을 한 라이브러리로 다룹니다.

요구사항: **Python 3.9 이상**.

💰 유료 필요: Claude API 키 (`console.anthropic.com` 에서 발급, 신규 가입 시 무료 크레딧 $5 제공)
✅ 무료 대안: Claude Max 구독자는 API 크레딧으로 충당 가능. Gemini 무료 API + 별도 SDK 도 호환 인터페이스가 비슷해 학습용으로 가능

## 따라하기

1. **설치**

   ```sh
   pip install anthropic
   ```

2. **환경변수 설정**

   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

3. **기본 메시지 호출 — 5줄로 시작**

   ```python
   import os
   from anthropic import Anthropic

   client = Anthropic(
       api_key=os.environ.get("ANTHROPIC_API_KEY"),  # 기본값, 생략 가능
   )

   message = client.messages.create(
       max_tokens=1024,
       messages=[
           {
               "role": "user",
               "content": "Hello, Claude",
           }
       ],
       model="claude-opus-4-6",
   )
   print(message.content)
   ```

4. **고급 기능 활용** — 공식 문서의 추가 가이드 참고
   - `api.md` — 전체 API 레퍼런스
   - `helpers.md` — 유틸리티 헬퍼
   - `tools.md` — Tool Use 통합
   - 공식 문서: [platform.claude.com/docs/en/api/sdks/python](https://platform.claude.com/docs/en/api/sdks/python)

## 활용 예시

- **개인 챗봇·자동화 스크립트** — 5줄 예제에 자신만의 시스템 프롬프트만 추가하면 Slack 봇 / 디스코드 봇 / 이메일 자동 분류 봇이 즉시 동작
- **데이터 분석 도우미** — pandas DataFrame 요약본을 Claude 에 보내 자연어로 인사이트 추출. 분석가 보조 도구로 활용
- **콘텐츠 제작 파이프라인** — `streaming=True` 로 긴 글을 실시간 생성, 블로그 자동화 / 뉴스레터 초안 작성 도구 구축
- **이미지 분석 (Vision)** — 제품 사진 업로드 → 자동 설명 생성으로 이커머스 상품 등록 자동화
- **사내 RAG 시스템** — Tool Use 로 자사 DB 조회 함수 등록 → 사내 지식 검색 챗봇 1주일 만에 출시

## 💡 아이디어

- **저렴한 1인 SaaS** — 무료 크레딧 + Claude Max 로 시작해서 사용자에게 월 $5–10 받는 미세 자동화 도구(이메일 분류·요약·번역) 출시
- **개발자 학습 교재** — 5줄 예제를 시작점으로 streaming, tool use, vision 까지 단계적으로 익히는 부트캠프 커리큘럼

## 주의사항

- 모델 이름(`claude-opus-4-6` 등)은 **API 사양에 따라 주기적으로 업데이트** — 최신 모델 ID 는 공식 문서 확인 필수
- API 키는 **환경변수**로만 관리 (코드에 하드코딩 금지)
- 무료 크레딧 소진 시 자동 과금 안 됨 → 결제 수단 등록 필요

## 출처

- [anthropics/anthropic-sdk-python (GitHub)](https://github.com/anthropics/anthropic-sdk-python)
- [공식 Python SDK 문서](https://platform.claude.com/docs/en/api/sdks/python)
- 최신 버전: v0.104.1 (2026-05-22)
