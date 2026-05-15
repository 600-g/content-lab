---
name: claude-api-python-sdk-integration
description: Python 애플리케이션에서 Anthropic의 Claude API를 호출하여 메시지를 생성하고 응답을 받는 스킬입니다. Claude 언어 모델을 다양한 Python 프로젝트에 쉽게 통합할 수 있게 합니다. Use when: Python 기반 서비스나 스크립트에서 Claude AI의 언어 모델 기능을 활용하여 텍스트 생성, 분석, 대화 기능을 구현해야 할 때 트리거합니다. 특히 Claude 모델을 연동할 때 사용합니다.
origin: content-lab
metadata:
  category: "기타"
  grade: "S"
  targets: ["클로드코드", "두근컴퍼니", "공통"]
  ai_tools: ["Claude API", "Python"]
  tags: ["Claude", "Python", "API", "SDK", "AI"]
  difficulty: "초급"
  source_urls:
    - "https://github.com/anthropics/anthropic-sdk-python"
  source_type: "github"
  collected_at: "2026-05-14"
  last_updated_at: "2026-05-14"
  merge_count: 1
---

# Python용 Claude API SDK 연동

> Python 애플리케이션에서 Anthropic의 Claude API를 호출하여 메시지를 생성하고 응답을 받는 스킬입니다. Claude 언어 모델을 다양한 Python 프로젝트에 쉽게 통합할 수 있게 합니다.

**등급**: S — 두근컴퍼니는 유료 Claude Max를 사용하며, Python 초보 사용자도 쉽게 적용할 수 있는 Claude API 연동 스킬입니다. 메인 제품 company-hq에 즉시 활용 가능합니다.
**카테고리**: 기타 | **난이도**: 초급
**적용 대상**: 클로드코드, 두근컴퍼니, 공통
**누적 출처**: 1건

## When to use

Python 기반 서비스나 스크립트에서 Claude AI의 언어 모델 기능을 활용하여 텍스트 생성, 분석, 대화 기능을 구현해야 할 때 트리거합니다. 특히 Claude 모델을 연동할 때 사용합니다.

## 두근컴퍼니 적용 메모

두근컴퍼니는 유료 Claude Max를 사용하므로, 이 SDK를 활용하여 company-hq 내 멀티 에이전트의 대화 로직이나 텍스트 생성 모듈을 구현할 수 있습니다. `ANTHROPIC_API_KEY` 환경 변수 설정만 잘 안내하면 초보 사용자도 쉽게 Claude와 통신하는 에이전트를 만들 수 있습니다.

---

## 핵심 패턴
Python용 Claude SDK를 사용하여 Claude API와 연동하고, AI 모델에 메시지를 보내 응답을 받는 패턴입니다. 환경 변수를 통해 API 키를 안전하게 관리하며, `client.messages.create` 메서드를 통해 쉽게 AI와 상호작용할 수 있습니다.

## 적용 단계
1.  **Python 환경 준비**: Python 3.9 이상 버전이 설치되어 있는지 확인합니다.
2.  **SDK 설치**: 터미널 또는 명령 프롬프트에서 `pip`를 사용하여 Anthropic SDK를 설치합니다.
    ```sh
    pip install anthropic
    ```
3.  **API 키 설정**: Anthropic API 키를 `ANTHROPIC_API_KEY`라는 이름의 환경 변수로 설정합니다. 이는 보안상 중요한 단계입니다.
    *   macOS/Linux: `export ANTHROPIC_API_KEY="YOUR_API_KEY"`
    *   Windows (CMD): `set ANTHROPIC_API_KEY="YOUR_API_KEY"`
    *   Windows (PowerShell): `$env:ANTHROPIC_API_KEY="YOUR_API_KEY"`
4.  **Python 코드 작성**: SDK를 임포트하고, 클라이언트를 초기화한 후, `messages.create` 메서드를 호출하여 Claude와 상호작용합니다.

## 예시
```python
import os
from anthropic import Anthropic

# API 키는 환경 변수에서 자동으로 로드됩니다 (ANTHROPIC_API_KEY).
# client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY")) # 생략 가능

client = Anthropic() # 환경 변수가 설정되어 있다면 이처럼 간단하게 초기화 가능

message = client.messages.create(
    max_tokens=1024, # 응답으로 받을 최대 토큰 수
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude", # 사용자 메시지
        }
    ],
    model="claude-opus-4-6", # 사용할 Claude 모델 지정 (예: "claude-3-opus-20240229" 또는 "claude-opus-4-6")
)
print(message.content) # Claude의 응답 출력

# 스트리밍 예시 (더 긴 응답이나 실시간 처리에 유용)
# with client.messages.stream(
#     max_tokens=1024,
#     messages=[
#         {
#             "role": "user",
#             "content": "Tell me a long story about a brave knight.",
#         }
#     ],
#     model="claude-3-opus-20240229",
# ) as stream:
#     for text in stream.text_stream:
#         print(text, end="", flush=True)
```

## 주의사항
*   **API 키 관리**: API 키는 외부에 노출되지 않도록 환경 변수를 통해 관리하는 것이 중요합니다. 코드에 직접 포함하지 마십시오.
*   **Python 버전**: 반드시 Python 3.9 이상 환경에서 사용해야 합니다.
*   **모델 선택**: `model` 파라미터에 현재 사용 가능한 Claude 모델 이름을 정확히 지정해야 합니다. Anthropic API 문서에서 최신 모델 목록을 확인하세요.
*   **토큰 제한**: `max_tokens`는 Claude가 생성할 수 있는 응답의 최대 길이를 제한합니다. 너무 낮게 설정하면 응답이 잘릴 수 있습니다.

## 출처
*   **링크**: https://github.com/anthropics/anthropic-sdk-python
*   **저자**: Anthropic
*   **공식 문서**: https://platform.claude.com/docs/en/api/sdks/python

---

## 누적 출처

- [https://github.com/anthropics/anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python)

## 메타

- 최초 수집: 2026-05-14
- 마지막 갱신: 2026-05-14
- 합병 횟수: 1회
- 자동 생성: 두근컴퍼니 콘텐츠랩 v4.0
