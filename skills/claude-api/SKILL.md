---
name: claude-api
description: Claude API로 실제 서비스형 앱을 빠르게 만드는 anthropic-quickstarts 9종 스타터와, 파이썬 스크립트·서버·자동화 파이프라인에서 Claude를 직접 호출하는 공식 anthropic-sdk-python 클라이언트를 함께 다루는 개발 스킬.
origin: content-lab
grade: S
difficulty: 중급
category: 개발
ai_tools: ["Claude"]
sources:
  - https://github.com/anthropics/anthropic-quickstarts
  - https://github.com/anthropics/anthropic-sdk-python
---

# 클로드 API로 앱 만들기 (합병됨)

## 이게 뭔가요?

Anthropic이 공식으로 운영하는 두 가지 개발 리소스를 하나로 묶은 스킬이다. 하나는 **anthropic-quickstarts** — Claude API로 배포 가능한 애플리케이션을 빠르게 시작하도록 만든 스타터 프로젝트 9종을 모아둔 모노레포(★17,664 / Fork 3,033, TypeScript, MIT 라이선스)이고, 다른 하나는 **anthropic-sdk-python** — 파이썬 코드에서 Claude API를 직접 호출할 때 쓰는 공식 클라이언트 라이브러리(★3,901 / Fork 855, MIT 라이선스, PyPI `anthropic` 패키지)다.

quickstarts는 "밑바닥부터" 시작하지 않고 검증된 뼈대 위에서 고객지원, 금융 분석, 컴퓨터/브라우저 자동화, 자율 코딩 에이전트, Managed Agents 챗봇 등 실제 서비스형 앱을 빠르게 만들 수 있게 해준다. 단순 API 호출 예시를 넘어 에이전트 패턴과 도구 사용(Tool Use) 구현에 초점을 맞춘 '프레임워크' 레벨 가이드다.

sdk-python은 Claude 웹앱이나 Claude Code CLI가 아니라 자기 파이썬 스크립트·서버·자동화 파이프라인 안에서 Claude를 코드로 직접 호출하고 싶을 때 쓴다. 대량 텍스트 배치 요약, 자체 챗봇 백엔드, 크론잡 정기 리포트 생성 등 "Claude를 앱/스크립트에 심는" 모든 작업의 출발점이다.

💰 유료 필요: 두 스킬 모두 Anthropic API 키(console.anthropic.com 발급, 사용량 기반 과금)가 필요하며, Claude Max 구독과는 별개의 과금 체계다.
✅ 무료 대안: API 크레딧이 없다면 Claude.ai 웹/앱에서 아이디어만 참고하고 실제 실행 로직은 Gemini API 무료 티어나 Ollama(Gemma 등 로컬 모델)로 옮겨 연습할 수 있다. 단, computer-use·browser-use 등 Claude 전용 툴콜 구조는 그대로 이식되지 않는다.

## 따라하기

### A. anthropic-quickstarts (앱 스타터)

1. **저장소 clone**
```
git clone https://github.com/anthropics/anthropic-quickstarts.git
cd anthropic-quickstarts
```

2. **원하는 quickstart 디렉터리로 이동** — 목적에 맞는 것을 아래 목록에서 고른다

3. **의존성 설치** (각 프로젝트 README 참고, 보통 `npm install` 또는 `pip install`)

4. **API 키를 환경변수로 설정**
```
export ANTHROPIC_API_KEY=your_api_key_here
```

5. **실행** — 각 프로젝트 README의 실행 명령(`npm run dev` 등) 그대로 따라간다

**제공되는 quickstart 9종**

- **Customer Support Agent** — Claude의 자연어 이해·생성 능력으로 지식베이스에 접근하는 AI 고객지원 시스템 구현 ([./customer-support-agent](https://github.com/anthropics/anthropic-quickstarts/tree/main/customer-support-agent))
- **Financial Data Analyst** — 대화형 데이터 시각화와 결합해 채팅으로 금융 데이터를 분석 ([./financial-data-analyst](https://github.com/anthropics/anthropic-quickstarts/tree/main/financial-data-analyst))
- **Computer Use Demo** — Claude가 데스크톱 컴퓨터를 제어하는 환경/툴 세트, 최신 `computer_toolset_20260801` 툴셋(각 컴퓨터 액션이 이름으로 호출되는 멤버 툴 구조) 지원 ([./computer-use-demo](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo))
- **Computer Use Best Practices** — 컨테이너가 아닌 실제 macOS 데스크톱(VM 권장)에서 동작하는 교육용 레퍼런스. 명시적 툴 정의, 이미지 크기·프루닝, 프롬프트 캐싱, 서버사이드 압축, 배치 툴콜, 샌드박스 셸, 트래젝토리 기록 등 신뢰성·비용 효율을 높이는 패턴 시연 ([./computer-use-best-practices](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-best-practices))
- **Browser Use Demo** — Playwright 기반 커스텀 브라우저 툴로 웹사이트 탐색, DOM 요소 검사/조작, 콘텐츠 추출, 폼 입력을 Claude가 수행 ([./browser-use-demo](https://github.com/anthropics/anthropic-quickstarts/tree/main/browser-use-demo))
- **Autonomous Coding Agent** — Claude Agent SDK 기반 자율 코딩 에이전트. 초기화 에이전트 + 코딩 에이전트 2단계 패턴으로 여러 세션에 걸쳐 앱을 완성하며, git으로 진행상황을 저장하고 기능 목록을 순차 처리 ([./autonomous-coding](https://github.com/anthropics/anthropic-quickstarts/tree/main/autonomous-coding))
- **Managed Agents: Chat SDK** — Claude Managed Agents + Vercel Chat SDK 기반 브라우저 챗앱. 대화별 지속 세션을 유지하는 리서치 분석가가 웹 검색으로 조사하고 브리프를 토큰 단위로 스트리밍, 툴콜은 라이브 피드로 표시. Slack/Teams/Discord/Telegram/WhatsApp 어댑터만 교체하면 동일 핸들러로 동작 ([./managed-agents/chat-sdk](https://github.com/anthropics/anthropic-quickstarts/tree/main/managed-agents/chat-sdk))
- **Managed Agents with CopilotKit and AG-UI** — Claude Managed Agent 기반 개인 재무 비서 챗앱, CopilotKit으로 렌더링. 매니지드 에이전트 세션을 AG-UI 프로토콜에 연결해 이벤트 델타로 토큰 스트리밍하고, 툴콜을 인터랙티브 생성형 UI 컴포넌트로 표시 ([./managed-agents/copilot-kit-ag-ui](https://github.com/anthropics/anthropic-quickstarts/tree/main/managed-agents/copilot-kit-ag-ui))
- **Managed Agents: Knowledge Wiki** — Claude Managed Agents 기반 딜룸 지식 위키. 문서 집합을 병렬 추출 세션 → 해결(resolve) 패스 → 조정된 통합(dream) 과정을 거쳐 버전 관리되는 메모리스토어 위키로 한 번만 증류하고, 이후 반복 질문에 근거(provenance) 포함 답변을 원문 검색 대비 훨씬 적은 토큰 비용으로 제공. 실제 예제는 공개 SEC EDGAR 공시로 만든 M&A 데이터룸 ([./managed-agents/knowledge-wiki](https://github.com/anthropics/anthropic-quickstarts/tree/main/managed-agents/knowledge-wiki))

### B. anthropic-sdk-python (코드에서 직접 호출)

1. **패키지 설치** — 터미널에서 pip으로 설치한다.
```sh
pip install anthropic
```
기존에 `0.x` 버전을 쓰고 있었다면 업그레이드 전 마이그레이션 가이드(`MIGRATION.md`)를 먼저 확인한다.

2. **API 키 환경변수 등록** — [Anthropic Console](https://console.anthropic.com/)에서 발급받은 키를 환경변수 `ANTHROPIC_API_KEY`로 등록한다 (예: `.zshrc`에 `export ANTHROPIC_API_KEY=여기에_키` 추가 후 터미널 재시작).

3. **기본 호출 코드 작성** — 아래 코드를 그대로 `.py` 파일로 저장해 실행한다.
```python
import os
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),  # This is the default and can be omitted
)

message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],

    model="claude-opus-5",
)

print(message.content)
```

4. **실행 환경 확인** — Python 3.10 이상이 필요하다. `python3 --version`으로 먼저 확인한다.

5. **model 값 교체** — 위 예제의 `model="claude-opus-5"` 부분을 필요한 모델(Sonnet 5, Haiku 4.5 등)로 바꿔서 용도에 맞게 조정한다.

## 활용 예시

- 고객 문의 자동응답 시스템이 필요하다 → **Customer Support Agent**를 clone해 지식베이스만 자사 데이터로 교체
- 엑셀·CSV 재무 데이터를 채팅으로 물어보고 싶다 → **Financial Data Analyst**로 시각화 채팅 UI 구축
- Claude가 직접 화면을 보고 마우스·키보드를 조작하게 하고 싶다 → **Computer Use Demo**(컨테이너) 또는 실제 macOS 환경이면 **Computer Use Best Practices** 선택
- 여러 세션에 걸쳐 앱을 자동으로 계속 개발시키고 싶다 → **Autonomous Coding Agent**의 2-에이전트 패턴 참고
- 메신저 채널(Slack/Teams/Discord/Telegram/WhatsApp)에 리서치 어시스턴트를 붙이고 싶다 → **Managed Agents: Chat SDK**의 어댑터 교체 구조 활용
- 위 파이썬 코드를 그대로 실행하면 → 콘솔에 Claude가 생성한 응답 콘텐츠 객체가 출력된다
- `messages` 리스트에 여러 메시지를 넣고 반복문으로 감싸면 → 파일 여러 개를 순회하며 배치 요약하는 스크립트로 확장 가능
- Mac Mini에서 크론(cron)이나 launchd로 이 스크립트를 예약 실행하면 → 매일 정해진 시간에 자동으로 리포트를 생성해 파일로 저장하는 자동화 파이프라인 구성 가능

## 주의사항

- 대부분의 quickstart는 **Claude API 사용량 기반 과금**이 발생한다 — 특히 computer-use, browser-use는 스크린샷/DOM 데이터를 반복 전송하므로 토큰 소비가 크다
- Computer Use 계열은 실제 데스크톱 제어 권한을 Claude에게 부여하므로, 반드시 **VM 또는 컨테이너 격리 환경**에서 실행할 것
- 각 quickstart는 독립 프로젝트라 의존성 버전이 다를 수 있으니 루트가 아닌 **해당 하위 디렉터리 README**를 따로 확인해야 한다
- API 키는 코드에 하드코딩하지 말고 반드시 환경변수로 관리한다 (깃허브에 실수로 커밋되는 사고 방지)
- SDK는 Claude Max 구독과 무관한 별도의 API 종량 과금이므로, 반복 실행 스크립트를 만들 때는 토큰 사용량과 비용을 미리 가늠해야 한다
- 자세한 문서는 [platform.claude.com/docs/en/api/sdks/python](https://platform.claude.com/docs/en/api/sdks/python)에서 최신 API 레퍼런스를 확인한다

## 출처

- [https://github.com/anthropics/anthropic-quickstarts](https://github.com/anthropics/anthropic-quickstarts)
- [https://github.com/anthropics/anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python)
