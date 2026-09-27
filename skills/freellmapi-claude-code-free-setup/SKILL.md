---
name: freellmapi-claude-code-free-setup
description: 이 스킬은 구글·Groq·Cerebras 등 여러 회사의 **무료 API 티어**를 내 컴퓨터의 **FreeLLMAPI 라우터**(localhost:3001) 하나로 모아, **클로드 코드**가 사용량 한도 걱정 없이 무료 모델로 동작하게 만드는 세팅 가이드입니다.
origin: content-lab
grade: A
difficulty: 중급
category: 개발
ai_tools: ["Claude", "Claude Code", "Gemini", "도구무관"]
sources:
  - https://wandering-mile-86e.notion.site/FreeLLMAPI-3e398dec8eed814d8e9cd2e698076403?pvs=149
---

# 클로드 코드를 무료 API로 연결

💡 이 스킬은 구글·Groq·Cerebras 등 여러 회사의 **무료 API 티어**를 내 컴퓨터의 **FreeLLMAPI 라우터**(localhost:3001) 하나로 모아, **클로드 코드**가 사용량 한도 걱정 없이 무료 모델로 동작하게 만드는 세팅 가이드입니다.

## 이게 뭔가요?

클로드 코드(Claude Code)는 터미널에서 AI에게 코딩을 시키는 도구입니다. 그런데 쓰다 보면 「사용량 한도에 도달했습니다」 창을 만나거나, 유료 요금제를 끊어야 하는 순간이 옵니다.

**FreeLLMAPI**는 그 문제를 다른 쪽에서 풉니다. 구글, Groq, Cerebras, Z.ai, NVIDIA, Mistral, Cloudflare 같은 회사들은 저마다 무료 API를 조금씩 줍니다. 한 회사 것만 보면 장난감 수준이지만, 전부 모으면 매달 약 74억 토큰이 됩니다. FreeLLMAPI는 그 무료 티어들을 내 컴퓨터의 주소 하나(`http://localhost:3001`) 뒤에 모아 두고, 클로드 코드가 그 주소로 말을 걸게 해 줍니다.

비유하면 동네 카페 열 곳이 각각 「첫 잔 무료」 쿠폰을 주는 상황과 같습니다. 한 장으로는 하루도 못 버티지만, 열 장을 지갑 하나에 모아 두고 한 장이 떨어지면 다음 장을 자동으로 꺼내 주는 지갑이 있다면 매일 공짜 커피를 마실 수 있습니다. FreeLLMAPI가 그 지갑입니다.

| 항목 | 값 |
|---|---|
| 이름 | FreeLLMAPI |
| 저장소 | github.com/tashfeenahmed/freellmapi |
| 홈페이지 | freellmapi.co |
| 라이선스 | MIT (라우터 자체는 영원히 무료) |
| 2026-09-22 기준 | 스타 27,924 · 무료 제공사 34곳 · 무료 모델 엔드포인트 635개 · 월 약 74억 토큰 |

MIT 라이선스는 「가져다 쓰세요, 고쳐도 됩니다. 만든 사람 이름만 남겨 주세요」라는 가장 느슨한 약속입니다.

- 사용 도구: **Claude Code** (터미널), 뒤쪽 모델은 Gemini·GPT-OSS·GLM·Kimi 등 각 회사의 무료 모델
- 💰 유료 필요: 없음 (라우터는 MIT 무료. 「Premium」은 카탈로그를 당일 반영해 주는 선택 사항일 뿐)
- ✅ 무료 대안: 각 회사의 무료 API 키(카드 불필요)만으로 가능

### 먼저 알고 시작할 것 세 가지

- **「ChatGPT」가 아니라 GPT-OSS입니다.** 목록에 있는 GPT 계열은 OpenAI가 공개한 가중치 모델 GPT-OSS 120B와 20B입니다. ChatGPT 앱이나 GPT-5 같은 유료 모델이 들어 있는 게 아닙니다. Gemini 3.5 Flash, GLM-4.7, Kimi K2.6, Grok 4.1 Fast는 이름 그대로 목록에 있습니다.
- **저장소가 스스로 「개인 실험용」이라고 적어 두었습니다.** 원문은 "This project is for personal experimentation and learning, not production." 회사 서비스에 붙이는 용도가 아닙니다.
- **무료 티어는 회사가 정한 한도가 있습니다.** 분당 요청 수, 하루 요청 수 같은 것입니다. FreeLLMAPI가 한도를 세다가 막히면 다음 모델로 넘어가 주지만, 속도와 품질은 그때그때 다릅니다.

### 전체 그림

```
flowchart LR
A["클로드 코드"] -->|"http://localhost:3001"| B["FreeLLMAPI 라우터<br/>(내 컴퓨터)"]
B --> C["구글 Gemini 무료"]
B --> D["Groq · GPT-OSS 무료"]
B --> E["Cerebras · GLM 무료"]
B --> F["… 34곳"]
C & D & E & F -->|"답"| B --> A
```

클로드 코드는 자기가 Anthropic 서버에 말을 거는 줄 압니다. 실제로는 내 컴퓨터의 라우터가 받아서 그 순간 가장 상태가 좋은 무료 모델에게 넘기고, 답을 다시 클로드 코드에게 돌려줍니다.

## 따라하기

1. **설치하기 (약 5분)** — 환경에 맞는 방법 하나만 고릅니다.

   **윈도우 / 맥 — 설치 파일 하나**

   릴리스 목록에서 `.exe` 파일을 받아 실행합니다. (맥은 `.dmg`) 설치가 끝나면 작업 표시줄 트레이에 아이콘이 생기고, 대시보드가 브라우저로 열립니다. 비밀번호를 만들 필요가 없습니다. 데스크톱 앱은 숨은 로컬 계정으로 스스로 로그인합니다.

   **도커를 쓸 줄 안다면 — 한 줄**

   ```
   curl -fsSL https://freellmapi.co/install.sh | bash
   ```

   `~/freellmapi` 폴더를 만들고, 암호화 키를 만들고, 이미지를 받아서 컨테이너를 띄웁니다. 끝나면 브라우저에서 `http://localhost:3001` 을 엽니다. 도커 설치판은 이메일·비밀번호 계정을 만듭니다.

   **직접 소스로 돌리고 싶다면 (Node.js 20 이상)**

   ```
   git clone https://github.com/tashfeenahmed/freellmapi.git
   cd freellmapi
   npm install
   $ENCRYPTION_KEY = node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
   "ENCRYPTION_KEY=$ENCRYPTION_KEY`nPORT=3001" | Out-File -Encoding utf8 .env
   npm run dev
   ```

   위 소스 설치 예시의 `$ENCRYPTION_KEY = ...` 와 `Out-File` 은 윈도우 PowerShell 문법입니다.

2. **무료 API 키 받기 (약 15분)** — FreeLLMAPI는 키를 대신 만들어 주지 않습니다. 각 회사 사이트에서 무료 키를 받아 와야 합니다. 처음이라면 아래 여섯 곳이면 충분합니다. 전부 회원가입만 하면 되고 카드는 필요 없습니다.

   | 회사 | 키 받는 곳 | 뭘 주나 |
   |---|---|---|
   | 구글 | aistudio.google.com → Get API key | Gemini Flash 계열 |
   | Groq | console.groq.com → API Keys | GPT-OSS 120B/20B, Llama, Kimi K2 (매우 빠름) |
   | Cerebras | cloud.cerebras.ai → API Keys | GLM-4.7, Qwen3 (매우 빠름) |
   | OpenRouter | openrouter.ai → Keys | 「:free」가 붙은 모델 여러 개 |
   | Cloudflare | dash.cloudflare.com → Workers AI | Llama, Kimi K2.6 등 |
   | NVIDIA | build.nvidia.com → Get API Key | Nemotron, GLM, Kimi 등 |

3. **대시보드에 키 넣기** — 대시보드 위쪽 탭에서 **Keys** 를 누릅니다. 회사 이름을 고르고 방금 받은 키를 붙여 넣고 저장합니다. 여섯 번 반복합니다.

4. **성공 확인 및 통합 키 복사** — **Models** 탭으로 가면 방금 넣은 회사들의 모델이 목록에 켜집니다. 위쪽 「Monthly token budget」 띠가 여러 색으로 차 있으면 성공입니다. 색 하나가 회사 하나입니다. 그다음 Keys 탭 맨 위에 `freellmapi-…` 로 시작하는 긴 글자가 있습니다. 이게 **통합 키**입니다. 클로드 코드에는 이 키 하나만 줍니다. 회사 키들은 라우터 안에 암호화돼 있고 밖으로 나가지 않습니다.

5. **클로드 코드 연결 (약 1분)** — 터미널을 열고 한 줄 칩니다.

   ```
   npx freellmapi setup-claude --url http://localhost:3001
   ```

   이 명령이 하는 일은 셋입니다.
   - 지금 있는 클로드 코드 설정을 백업합니다 (날짜가 붙은 사본)
   - 라우터에 물어서 쓸 수 있는 모델 목록을 가져옵니다
   - 클로드 코드 설정에 `ANTHROPIC_BASE_URL=http://localhost:3001` 과 통합 키를 합쳐 넣습니다

   먼저 뭘 바꾸는지만 보고 싶으면 `--dry-run` 을 붙입니다. 아무것도 안 바꾸고 보여만 줍니다.

   설정 파일에 키를 남기기 싫으면 대신 이렇게 띄웁니다.

   ```
   npx freellmapi launch
   ```

   키를 그 순간 실행되는 클로드 코드 프로세스에만 넣어 주고, 파일에는 아무것도 남기지 않습니다.

   주소 끝에 `/v1` 을 붙이지 마세요. 클로드 코드는 뿌리 주소(`http://localhost:3001`)를 받아서 자기가 알아서 `/v1/messages` 를 붙입니다.

6. **모델이 바뀔 때 인수인계 메모 켜기** — 한 모델이 한도에 걸리면 라우터가 다음 모델로 넘깁니다. 이때 대화가 끊긴 것처럼 새 모델이 처음부터 다시 묻는 일이 생길 수 있습니다. 그걸 막으려면 라우터 폴더의 `.env` 파일에 아래 한 줄을 넣고 라우터를 다시 켭니다.

   ```
   FREELLMAPI_CONTEXT_HANDOFF=on_model_switch
   ```

   이러면 모델이 바뀌는 순간 라우터가 새 모델에게 짧은 인수인계 메모를 먼저 건넵니다. 내용은 대략 「너는 다른 모델이 하던 대화를 이어받는 중이다. 처음부터 다시 시작하거나 이미 정한 것을 다시 묻지 마라」 입니다. 대화 기록은 라우터 메모리에 3시간 동안 남고, 디스크에는 저장되지 않습니다. 같은 대화는 기본으로 30분 동안 같은 모델에 머뭅니다. 메모는 그 30분 안에 어쩔 수 없이 바뀔 때만 쓰입니다.

7. **잘 되는지 확인하기** — 클로드 코드를 켜고 아무 말이나 시킵니다. 대시보드 **Analytics** 탭을 엽니다. 방금 요청이 어느 회사의 어느 모델로 갔는지 줄이 하나 생깁니다. 답이 안 오거나 느리면 Models 탭의 「Router pressure」 를 봅니다. 최근 30분 동안 막힌 모델과 쉬는 중인 모델이 여기 보입니다.

## 활용 예시

- **Claude Max 한도가 찼을 때 이어 쓰기**: 유료 한도에 걸린 날, 터미널에서 `npx freellmapi launch` 로 클로드 코드를 띄우면 → 설정 파일은 그대로 두고 그 프로세스만 무료 모델로 동작합니다.
- **연습용 Python 스크립트 실험**: 코딩 초보가 부담 없이 여러 번 시켜 볼 때, 클로드 코드에 「간단한 파일 정리 스크립트 만들어줘」 라고 입력하면 → Analytics 탭에서 어느 회사의 어느 모델이 답했는지 줄로 확인됩니다.
- **어려운 코드는 큰 모델로 고정**: Models 탭에서 GPT-OSS 120B나 GLM-4.7 을 위쪽으로 끌어 올려 두면 → 복잡한 요청이 그 큰 모델부터 배정됩니다.

## 주의사항

- 무료 티어는 회사 마음입니다. 어느 날 한도가 줄거나 모델이 사라질 수 있습니다. 라우터가 하루 두 번 카탈로그를 받아서 스스로 고치지만, 무료판은 새 모델이 30일 늦게 들어옵니다. (유료 「Premium」은 카탈로그를 당일 반영해 주는 것뿐이고, 라우터 자체는 계속 무료입니다.)
- 회사 서비스에 붙이지 마세요. 저장소가 스스로 「개인 실험용」이라고 적어 두었습니다.
- 키는 내 컴퓨터에만 있습니다. 라우터가 밖으로 보내는 건 각 회사에 보내는 요청뿐입니다. 다만 각 회사의 무료 티어 약관은 각자 확인하세요.
- 모델마다 실력이 다릅니다. 어려운 코드는 GPT-OSS 120B나 GLM-4.7 같은 큰 모델이 잡히도록 Models 탭에서 순서를 위로 끌어 올려 두면 편합니다.
- 주소 끝에 `/v1` 을 붙이면 안 됩니다. `http://localhost:3001` 뿌리 주소만 씁니다.
- 참고: 모델 카탈로그 https://freellmapi.co/models.html

## 출처

- [https://wandering-mile-86e.notion.site/FreeLLMAPI-3e398dec8eed814d8e9cd2e698076403?pvs=149](https://wandering-mile-86e.notion.site/FreeLLMAPI-3e398dec8eed814d8e9cd2e698076403?pvs=149)
